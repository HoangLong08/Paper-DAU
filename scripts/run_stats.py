"""E6 — THỐNG KÊ. Đơn vị = **BỆNH NHÂN** (lô cũ làm sai). → results/stats/ · Hình 2

    python scripts/run_stats.py --config configs/exp_smoke.yaml
    python scripts/run_stats.py --config configs/exp_main.yaml

Ba bậc tự do KHOÁ TRƯỚC (A4e): **k primary = 4** · **decoding primary = `brightest`** ·
**thuật toán reference = `DP-exact`**. MỘT primary endpoint cho MỖI mệnh đề.

**FAMILY cho Holm (A4e — trước đó "Holm" là một từ trống, ~4.620 test khả dĩ):**

| Family | Nội dung | Hiệu chỉnh |
|---|---|---|
| **A** | superiority (P4): U-Net vs oracle level-set | 1 test ⇒ không cần |
| **B** | trend (P3 primary + secondary) | **Holm TRONG family** |
| **C** | equivalence (TOST, tại MỘT k primary) | ⚠️ TOST là **intersection–union test** ⇒ **KHÔNG hiệu chỉnh** |
| **D** | mọi thứ còn lại | **EXPLORATORY** — effect size + CI, **không dùng p-value để claim** |

**Bẫy đã gỡ:**
* **A4d — `zero_method="pratt"`** (mặc định của `src.eval.stats`). `scipy` mặc định
  `'wilcox'` **LOẠI BỎ các cặp hiệu = 0** — mà theo P1 các cặp-0 (hai thuật toán ⇒ mask
  giống hệt) **chính là kết quả của bài**; nó còn tự sinh "significance" giả — đúng cái
  tội bài đang tố cáo. Mọi bảng so sánh cặp **BẮT BUỘC** in `n_zero / n_total`:
  *"trên X/n bệnh nhân, QIGOA và PSO cho ra mask GIỐNG HỆT NHAU"* = cả bài gói trong một
  phân số.
* **A4c — KHÔNG báo "TOST pass/fail"**: báo **90% CI** của hiệu theo cặp + **`delta_ach`**
  (bound nhỏ nhất còn giữ tương đương ở α=0,05) ⇒ *"Equivalence holds for any SESOI ≥
  delta_ach = X"*. Phân tích này **không bao giờ fail**. **Bayesian ROPE là PRIMARY**;
  TOST là frequentist companion. Báo cả hierarchy 3 bound, luôn luôn.
* **A4a — P3 primary KHÔNG phải Spearman gộp** (n=7 ⇒ decision rule tự mâu thuẫn; quan hệ
  là chữ U ngược ⇒ rank correlation là dụng cụ SAI; trung bình-theo-k trước rồi tương quan
  là **aggregation fallacy** che giấu chính Simpson's paradox bài muốn phơi bày).
  Primary = **one-sample Wilcoxon trên Δᵢ per-patient**, n = số bệnh nhân.
* **A4b — P2c decoupling test:** `Spearman(relative_gap_fitness, |ΔDice vs DP|)` ⇒ dự đoán
  ≈ 0. Nếu mạnh & dương ⇒ fitness *thực sự* là proxy tốt cho Dice ⇒ luận điểm Goodhart yếu
  đi. P2c biến "circularity" từ lỗ hổng thành KẾT QUẢ.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as sps

from _common import (
    ROOT,
    _banner,
    data_source,
    load_config,
    parse_args,
    read_results_csv,
    resolve_output_dir,
    section,
    set_all_seeds,
    write_readme,
    write_run_manifest,
)
from src.eval.stats import (
    bayesian_signed_rank,
    bootstrap_ci,
    friedman_nemenyi,
    one_sample_wilcoxon_delta,
    tost,
    wilcoxon_signed,
)

FAM_A, FAM_B, FAM_C, FAM_D = "A-superiority", "B-trend", "C-equivalence", "D-exploratory"


# --------------------------------------------------------------------------- #
def load_raw(path: Path) -> pd.DataFrame:
    df = read_results_csv(path)
    df["include_zero_bg"] = df["include_zero_bg"].astype(str).str.lower()
    for c in ("dice", "psnr", "ssim", "relative_gap", "hd95", "k"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def per_patient(df, target, bg, rule, k, method, metric="dice") -> pd.Series:
    """MỘT giá trị / bệnh nhân (median qua seed) — đơn vị thống kê là BỆNH NHÂN."""
    m = df[(df["target"] == target) & (df["include_zero_bg"] == bg)
           & (df["decode_rule"] == rule) & (df["k"] == k) & (df["method"] == method)]
    if m.empty:
        return pd.Series(dtype=float)
    return m.groupby("patient_id")[metric].median()


def paired(a: pd.Series, b: pd.Series):
    """Ghép cặp trên CÙNG tập bệnh nhân (A3 — nếu không, Wilcoxon paired vô nghĩa)."""
    idx = a.index.intersection(b.index)
    return a.loc[idx].to_numpy(), b.loc[idx].to_numpy(), list(idx)


def holm(pvals):
    """Holm–Bonferroni TRONG một family. Trả p đã hiệu chỉnh, giữ nguyên thứ tự."""
    n = len(pvals)
    order = np.argsort(pvals)
    adj = np.empty(n, dtype=float)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, (n - rank) * pvals[i])
        adj[i] = min(1.0, running)
    return adj


def _dump(df: pd.DataFrame, path: Path, cfg: dict, script: str) -> Path:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        for line in _banner(script, cfg):
            fh.write(line + "\n")
        df.to_csv(fh, index=False)
    return path


# --------------------------------------------------------------------------- #
def main() -> int:
    args = parse_args(__doc__.splitlines()[0]).parse_args()
    cfg, cfg_hash = load_config(args.config)
    scfg = section(cfg, "stats")
    out_dir = resolve_output_dir(scfg, args.output, "results/stats")

    st = cfg.get("stats") or {}
    k_primary = int(st.get("k_primary", scfg.get("k_primary", 4)))
    rule = str(st.get("decoding_primary", "brightest"))
    ref = str(st.get("reference_method", "DP-exact"))
    sesoi = float(st.get("sesoi", 0.01))
    hierarchy = [float(x) for x in (st.get("sesoi_hierarchy") or [sesoi])]
    rope = tuple(float(x) for x in (st.get("rope") or (-sesoi, sesoi)))
    nboot = int((cfg.get("metrics") or {}).get("bootstrap_n", 10000))
    nbayes = int(st.get("bayes_samples", 20000))
    set_all_seeds(int((cfg.get("seeds") or [0])[0]))

    main_dir = ROOT / (scfg.get("main_dir") or cfg.get("output_dir") or "results/main")
    raw_path = main_dir / "raw.csv"
    if not raw_path.exists():
        raise SystemExit(f"[E6] không thấy {raw_path} — chạy run_main_grid.py trước.")
    df = load_raw(raw_path)
    ph = int(data_source(cfg) == "synthetic")
    t0 = time.perf_counter()

    targets = sorted(df["target"].dropna().unique())
    bgs = [b for b in sorted(df["include_zero_bg"].unique()) if b in ("true", "false")]
    methods = [m for m in sorted(df["method"].unique()) if m != ref]
    outputs = []

    # ===================================================================== #
    # FAMILY C — equivalence: Dice(algo) − Dice(DP-exact), tại k primary
    # (P2b — "đồng tiền lâm sàng", chân chống-circularity)
    # ===================================================================== #
    pair_rows, tost_rows, bayes_rows = [], [], []
    for target in targets:
        for bg in bgs:
            a_ref = per_patient(df, target, bg, rule, k_primary, ref)
            if a_ref.empty:
                continue
            for m in methods:
                a_m = per_patient(df, target, bg, rule, k_primary, m)
                if a_m.empty:
                    continue
                x, y, ids = paired(a_m, a_ref)
                if len(x) < 2:
                    continue
                d = x - y
                w = wilcoxon_signed(d)          # A4d — pratt, giữ cặp-0
                lo, hi = bootstrap_ci(d, stat=np.median, n=nboot)
                pair_rows.append({
                    "family": FAM_C, "target": target, "include_zero_bg": bg,
                    "k": k_primary, "decode_rule": rule, "metric": "dice",
                    "method": m, "reference": ref, "n_patients": len(x),
                    "median_diff": float(np.median(d)), "mean_diff": float(np.mean(d)),
                    "ci_low": lo, "ci_high": hi,
                    "wilcoxon_stat": w["stat"], "p": w["p"],
                    "rank_biserial": w["rank_biserial"],
                    # A4d — con số "X/n bệnh nhân cho mask GIỐNG HỆT" = cả bài trong 1 phân số
                    "n_zero": w["n_zero"], "n_total": w["n_total"],
                    "zero_frac": w["n_zero"] / w["n_total"] if w["n_total"] else np.nan,
                    "holm_note": "TOST = intersection-union test ⇒ KHÔNG hiệu chỉnh (A4e)",
                    "placeholder": ph,
                })
                t = tost(d, -hierarchy[0], hierarchy[0])
                row = {"family": FAM_C, "target": target, "include_zero_bg": bg,
                       "k": k_primary, "decode_rule": rule, "method": m, "reference": ref,
                       "n_patients": len(x), "mean_diff": float(np.mean(d)),
                       "ci90_low": t["ci90_low"], "ci90_high": t["ci90_high"],
                       # A4c mục 3 — LUÔN là một con số; "TOST fail" không tồn tại
                       "delta_ach": t["delta_ach"],
                       "equivalence_holds_for_any_sesoi_ge": t["delta_ach"],
                       "placeholder": ph}
                for b in hierarchy:             # A4c mục 2 — báo cáo CẢ BA bound, luôn luôn
                    row[f"tost_p_delta{b:g}"] = tost(d, -b, b)["p"]
                tost_rows.append(row)

                bz = bayesian_signed_rank(d, rope=rope, n_samples=nbayes, seed=0)
                bayes_rows.append({
                    "family": FAM_C, "target": target, "include_zero_bg": bg,
                    "k": k_primary, "decode_rule": rule, "method": m, "reference": ref,
                    "n_patients": len(x), "rope_low": rope[0], "rope_high": rope[1],
                    "p_left": bz["p_left"], "p_rope": bz["p_rope"], "p_right": bz["p_right"],
                    "primary": True,            # A4c mục 4 — Bayes ROPE là PRIMARY
                    "placeholder": ph,
                })
    outputs += [_dump(pd.DataFrame(pair_rows), out_dir / "pairwise.csv", cfg, "run_stats.py"),
                _dump(pd.DataFrame(tost_rows), out_dir / "tost.csv", cfg, "run_stats.py"),
                _dump(pd.DataFrame(bayes_rows), out_dir / "bayes.csv", cfg, "run_stats.py")]

    # ===================================================================== #
    # Friedman + Nemenyi + CD  → Hình 2 (Demšar 2006)
    # ===================================================================== #
    cd_rows = []
    for target in targets:
        for bg in bgs:
            data = {}
            for m in [ref] + methods:
                s = per_patient(df, target, bg, rule, k_primary, m)
                if not s.empty:
                    data[m] = s
            if len(data) < 3:
                continue
            common = set.intersection(*(set(s.index) for s in data.values()))
            if len(common) < 3:
                continue
            common = sorted(common)
            # hạng TĂNG DẦN ⇒ để "hạng thấp = tốt" trên Dice, đảo dấu (Dice cao = tốt)
            fr = friedman_nemenyi({m: -s.loc[common].to_numpy() for m, s in data.items()})
            for m, r in fr["ranks"].items():
                cd_rows.append({
                    "target": target, "include_zero_bg": bg, "k": k_primary,
                    "decode_rule": rule, "metric": "dice(neg-ranked: low rank = better)",
                    "method": m, "avg_rank": r, "cd": fr["cd"],
                    "friedman_stat": fr["friedman_stat"], "friedman_p": fr["friedman_p"],
                    "n_patients": len(common), "n_methods": len(data),
                    "family": FAM_D, "placeholder": ph,
                })
    outputs.append(_dump(pd.DataFrame(cd_rows), out_dir / "cd.csv", cfg, "run_stats.py"))

    # ===================================================================== #
    # FAMILY B — P3 (A4a): Δᵢ = Diceᵢ(k*_Dice) − Diceᵢ(k*_PSNR), one-sample Wilcoxon
    # ===================================================================== #
    p3_rows = []
    for target in targets:
        for bg in bgs:
            sub = df[(df["target"] == target) & (df["include_zero_bg"] == bg)
                     & (df["decode_rule"] == rule) & (df["method"] == ref)]
            if sub.empty:
                continue
            piv_d = sub.pivot_table(index="patient_id", columns="k", values="dice",
                                    aggfunc="median")
            piv_p = sub.pivot_table(index="patient_id", columns="k", values="psnr",
                                    aggfunc="median")
            ks = [c for c in piv_d.columns if c in piv_p.columns and c > 0]
            if len(ks) < 2:
                continue
            piv_d, piv_p = piv_d[ks], piv_p[ks]

            # PRIMARY (A4a): k* per-patient theo từng thước đo; cả hai đều là argmax
            # per-patient ⇒ so sánh công bằng. Headline = CHI PHÍ có đơn vị lâm sàng.
            k_dice = piv_d.idxmax(axis=1)
            k_psnr = piv_p.idxmax(axis=1)
            delta = np.array([piv_d.loc[i, k_dice[i]] - piv_d.loc[i, k_psnr[i]]
                              for i in piv_d.index])
            r = one_sample_wilcoxon_delta(delta, sesoi)
            p3_rows.append({
                "family": FAM_B, "analysis": "P3-primary: Dice(k*_Dice) - Dice(k*_PSNR)",
                "target": target, "include_zero_bg": bg, "decode_rule": rule,
                "reference": ref, "n": r["n"], "median_delta": r["median"], "p": r["p"],
                "rank_biserial": r["rank_biserial"], "ci_low": r["ci_low"],
                "ci_high": r["ci_high"], "sesoi": r["sesoi"],
                "n_zero": r["n_zero"], "n_total": r["n_total"],
                "success": r.get("success"),
                "mode_k_psnr": int(pd.Series(k_psnr).mode().iloc[0]),
                "mode_k_dice": int(pd.Series(k_dice).mode().iloc[0]),
                "placeholder": ph,
            })

            # SECONDARY (A4a): Spearman ρᵢ per-patient trên các k ⇒ one-sample Wilcoxon.
            # (Aggregate Spearman(k,Dice) chỉ là HÌNH MÔ TẢ — đã BỎ khỏi decision rule.)
            rhos = []
            for i in piv_d.index:
                v = piv_d.loc[i].to_numpy(dtype=float)
                if np.all(np.isfinite(v)) and np.unique(v).size > 1:
                    rhos.append(sps.spearmanr(np.array(ks, dtype=float), v).statistic)
            if len(rhos) >= 2:
                w = wilcoxon_signed(np.array(rhos))
                lo, hi = bootstrap_ci(np.array(rhos), stat=np.median, n=nboot)
                p3_rows.append({
                    "family": FAM_B, "analysis": "P3-secondary: per-patient Spearman(k, Dice)",
                    "target": target, "include_zero_bg": bg, "decode_rule": rule,
                    "reference": ref, "n": len(rhos), "median_delta": float(np.median(rhos)),
                    "p": w["p"], "rank_biserial": w["rank_biserial"],
                    "ci_low": lo, "ci_high": hi, "sesoi": -0.5,
                    "n_zero": w["n_zero"], "n_total": w["n_total"],
                    "success": bool(np.median(rhos) < -0.5 and w["p"] < 0.05),
                    "placeholder": ph,
                })
    p3 = pd.DataFrame(p3_rows)
    if not p3.empty:                       # Holm TRONG family B (A4e)
        p3["p_holm"] = holm(p3["p"].fillna(1.0).to_numpy())
    outputs.append(_dump(p3, out_dir / "p3_delta.csv", cfg, "run_stats.py"))

    # ===================================================================== #
    # P2c — decoupling test (A4b): Spearman(gap_fitness, |ΔDice vs DP|) ⇒ dự đoán ≈ 0
    # ===================================================================== #
    p2c_rows = []
    for target in targets:
        for bg in bgs:
            for k in sorted(x for x in df["k"].dropna().unique() if x > 0):
                a_ref = per_patient(df, target, bg, rule, k, ref)
                if a_ref.empty:
                    continue
                gaps, ddice = [], []
                for m in methods:
                    sub = df[(df["target"] == target) & (df["include_zero_bg"] == bg)
                             & (df["decode_rule"] == rule) & (df["k"] == k)
                             & (df["method"] == m)]
                    if sub.empty:
                        continue
                    for pid, g in sub.groupby("patient_id"):
                        if pid not in a_ref.index:
                            continue
                        gp = g["relative_gap"].median()
                        dd = abs(g["dice"].median() - a_ref.loc[pid])
                        if np.isfinite(gp) and np.isfinite(dd):
                            gaps.append(gp)
                            ddice.append(dd)
                if len(gaps) >= 3 and np.unique(gaps).size > 1 and np.unique(ddice).size > 1:
                    r = sps.spearmanr(gaps, ddice)
                    p2c_rows.append({
                        "family": FAM_D, "analysis": "P2c decoupling", "target": target,
                        "include_zero_bg": bg, "k": int(k), "decode_rule": rule,
                        "n_obs": len(gaps), "spearman_rho": float(r.statistic),
                        "p": float(r.pvalue),
                        "prediction": "rho ~ 0 (fitness gap KHÔNG dịch thành ΔDice); "
                                      "rho mạnh & dương ⇒ luận điểm Goodhart yếu đi",
                        "placeholder": ph,
                    })
    outputs.append(_dump(pd.DataFrame(p2c_rows), out_dir / "p2c_decoupling.csv", cfg,
                         "run_stats.py"))

    # ===================================================================== #
    # FAMILY A — superiority (P4): U-Net vs oracle level-set (1 test, không hiệu chỉnh)
    # ===================================================================== #
    fam_a = []
    ceil_p = ROOT / "results" / "ceiling" / "raw.csv"
    unet_p = ROOT / "results" / "unet" / "raw.csv"
    if scfg.get("ceiling_dir"):
        ceil_p = ROOT / scfg["ceiling_dir"] / "raw.csv"
    if scfg.get("unet_dir"):
        unet_p = ROOT / scfg["unet_dir"] / "raw.csv"
    if ceil_p.exists() and unet_p.exists():
        cdf, udf = read_results_csv(ceil_p), read_results_csv(unet_p)
        for target in sorted(set(udf["target"]) & set(cdf["target"])):
            u = udf[udf["target"] == target].groupby("patient_id")["dice"].median()
            o = cdf[(cdf["target"] == target) & (cdf["method"] == "oracle_levelset")]
            if o.empty:
                continue
            o = o.groupby("patient_id")["dice"].median()
            x, y, ids = paired(u, o)
            if len(x) < 2:
                continue
            d = x - y
            w = wilcoxon_signed(d)
            lo, hi = bootstrap_ci(d, stat=np.median, n=nboot)
            fam_a.append({
                "family": FAM_A, "analysis": "P4: Dice(2D-UNet) - Dice(oracle_levelset)",
                "target": target, "n_patients": len(x), "median_diff": float(np.median(d)),
                "ci_low": lo, "ci_high": hi, "p": w["p"],
                "rank_biserial": w["rank_biserial"],
                "n_zero": w["n_zero"], "n_total": w["n_total"],
                "reference_class": "C: uses test-time ground truth (oracle = unreachable "
                                   "upper bound, NOT a method)",
                "holm": "1 test ⇒ không hiệu chỉnh (A4e)",
                "fallback_if_not_superior": "KHÔNG rút về 'thresholding chạm trần của chính "
                                            "nó' (= François & Tinarrage đã in ⇒ zero "
                                            "novelty). Headline: 'Trần CAO — thất bại KHÔNG "
                                            "do giới hạn biểu diễn mà do BÀI TOÁN CHỌN "
                                            "NGƯỠNG' (A2).",
                "placeholder": ph,
            })
    else:
        print(f"[E6] bỏ qua Family A (cần {ceil_p} + {unet_p}).")
    outputs.append(_dump(pd.DataFrame(fam_a), out_dir / "family_a_superiority.csv", cfg,
                         "run_stats.py"))

    elapsed = time.perf_counter() - t0
    write_run_manifest(
        out_dir, cfg, cfg_hash, args.config, outputs,
        extra={"experiment": "E6 statistics", "unit": "patient",
               "k_primary": k_primary, "decoding_primary": rule, "reference_method": ref,
               "sesoi": sesoi, "sesoi_hierarchy": hierarchy, "rope": list(rope),
               "zero_method": "pratt (A4d)",
               "families": {"A": "superiority (1 test, no correction)",
                            "B": "trend (Holm within family)",
                            "C": "equivalence TOST (intersection-union ⇒ NO correction)",
                            "D": "exploratory (effect size + CI, no p-claims)"},
               "elapsed_s": round(elapsed, 3)},
    )
    write_readme(
        out_dir, cfg, "E6 — thống kê (đơn vị: BỆNH NHÂN)",
        "| file | family | nội dung |\n|---|---|---|\n"
        "| `pairwise.csv` | C/D | Wilcoxon **pratt** + rank-biserial + **`n_zero/n_total`** |\n"
        "| `tost.csv` | C | 90% CI + **`delta_ach`** + 3 bound hierarchy — KHÔNG pass/fail |\n"
        "| `bayes.csv` | C | Bayesian signed-rank + ROPE — **PRIMARY** |\n"
        "| `cd.csv` | D | Friedman + Nemenyi + CD → Hình 2 |\n"
        "| `p3_delta.csv` | B | Δᵢ per-patient (primary) + Spearman per-patient (secondary), Holm trong family |\n"
        "| `p2c_decoupling.csv` | D | Spearman(gap_fitness, \\|ΔDice\\|) — dự đoán ≈ 0 |\n"
        "| `family_a_superiority.csv` | A | U-Net vs oracle level-set (1 test) |\n\n"
        f"Khoá: k primary = **{k_primary}** · decoding primary = **`{rule}`** · reference = "
        f"**`{ref}`** · SESOI = **{sesoi}** · ROPE = **{list(rope)}**.\n\n"
        "**Cách đọc (A4c):** *đừng* đọc \"TOST pass/fail\", đọc **`delta_ach`** — "
        "*\"Equivalence holds for any SESOI ≥ delta_ach\"*. Bayesian ROPE là primary.\n\n"
        "⚠️ **A3 caveat cho P3:** `k*` per-patient trong primary là một lựa chọn **oracle** "
        "cho CẢ HAI thước đo (đúng như A4a viết) ⇒ nó đo *chi phí của việc chọn k bằng "
        "PSNR*, KHÔNG phải hiệu năng của một pipeline triển khai được. Nếu bản thảo dùng "
        "\"chọn k\" như một **phương pháp**, nó là loại B ⇒ phải chấm **out-of-fold**.",
    )
    print(f"\n[E6] xong {elapsed:.1f}s → {out_dir}")
    for p in outputs:
        print(f"  - {Path(p).name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

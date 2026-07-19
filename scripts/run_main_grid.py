"""E2 — LƯỚI CHÍNH equal-NFE: bệnh nhân × k × phương pháp × seed.  → Bảng III · Hình 2 · Hình 3

    python scripts/run_main_grid.py --config configs/exp_smoke.yaml            # < 60 s, [PLACEHOLDER]
    python scripts/run_main_grid.py --config configs/exp_main.yaml --resume    # lưới thật

⛔ KHÔNG chạy lưới thật trước khi (1) `run_exact_check.py` PASS và (2) bốn thí nghiệm
rủi ro của Tuần 1 sống sót (prereg §6/A10). Xem scripts/README.md.

Ghi ra `results/<exp>/raw.csv` (long-format: MỘT hàng cho mỗi
(bệnh nhân, target, include_zero_bg, k, phương pháp, seed, decode_rule)):

  * `relative_gap` = (f_DP − f_algo)/|f_DP| · `hit` = gap < tol  → **P2a**
  * `nfe` (assert = budget, ±0) · `runtime_s` · độ phức tạp báo ở bảng, KHÔNG claim
    tốc độ từ wall-clock (A0)
  * Dice / HD95 / NSD(+τ sensitivity) / `n_components` / `empty_mask`  → **kết quả**
  * PSNR / SSIM trên ảnh tái tạo  → **bằng chứng cho P3**, không phải kết quả
  * `mask_hash`  → **MASK-IDENTITY RATE** (headline A0): *"trên X% ô, mọi metaheuristic
    sinh ra binary mask giống hệt nhau từng byte"* — không cần kiểm định, không phản bác được.

Resume-được (§5 Kaggle): checkpoint sau MỖI ô (image, k, algo, seed), histogram cache
`.npy`, `--resume` bỏ qua ô đã có trong raw.csv.
"""

from __future__ import annotations

import multiprocessing as mp
import os
import sys
import time

import numpy as np
import pandas as pd

from _common import (
    CLASS_A,
    NA_BG,
    NA_K,
    NA_SEED,
    CsvAppender,
    classical_masks,
    data_source,
    decode_rows,
    done_keys,
    hist_cached,
    iter_slices,
    key_of,
    load_config,
    make_fitness,
    mask_metrics,
    metrics_cfg,
    parse_args,
    raw_fields,
    read_results_csv,
    reconstruct,
    resolve_output_dir,
    run_optimizer_cell,
    section,
    set_all_seeds,
    target_arrays,
    write_readme,
    write_run_manifest,
)
from src.decode.decoding import mask_hash
from src.eval.metrics import psnr, ssim
from src.solvers.exact_dp import relative_gap, solve_exact

KEY_COLS = ["patient_id", "target", "include_zero_bg", "k", "method", "seed"]
EXACT = "DP-exact"


def _cell_common(cfg, sl, target, bg, k, method, seed, img, thr, f_val, f_exact, tol):
    """Phần chung của một ô (trước khi tách theo decode_rule)."""
    rec = reconstruct(img, thr) if thr else None
    gap = relative_gap(f_exact, f_val) if (f_exact is not None and f_val is not None) else np.nan
    return {
        "patient_id": sl.patient_id,
        "target": target,
        "include_zero_bg": str(bool(bg)).lower() if bg is not NA_BG else NA_BG,
        "k": k,
        "method": method,
        "method_class": CLASS_A,   # E2 chỉ chứa loại A (unsupervised per-image) + DP
        "seed": seed,
        "thresholds": "|".join(map(str, thr)) if thr else "",
        "fitness": f_val,
        "f_exact": f_exact,
        "relative_gap": gap,
        "hit": int(gap < tol) if gap == gap else "",
        "psnr": psnr(img, rec) if rec is not None else np.nan,
        "ssim": ssim(img, rec) if rec is not None else np.nan,
        "data_source": data_source(cfg),
        "placeholder": int(data_source(cfg) == "synthetic"),
    }


def _patient_rows(task):
    """Toàn bộ công việc của MỘT bệnh nhân → (rows, n_cells). KHÔNG ghi file.

    Tách ra để đường tuần tự (--workers 1) và đường song song dùng CHUNG một thân
    duy nhất — nếu nhân đôi code, hai đường sẽ trôi dạt và số của paper phụ thuộc vào
    cờ dòng lệnh (đúng loại lỗi mà scripts/README §"Interface gaps" cảnh báo).

    An toàn song song: một ô chỉ phụ thuộc (histogram, k, seed, budget, hp) vì
    `_common.run_optimizer_cell` gọi `set_all_seeds(seed)` ngay đầu mỗi ô ⇒ độc lập
    thứ tự chạy. Ghi CSV vẫn do tiến trình cha làm (một người ghi duy nhất).
    """
    sl, done_p, ctx = task
    cfg, scfg = ctx["cfg"], ctx["scfg"]
    rules, labelmap_all = ctx["rules"], ctx["labelmap_all"]
    lm_primary_only, lm_methods = ctx["lm_primary_only"], ctx["lm_methods"]
    k_primary, seeds, algos = ctx["k_primary"], ctx["seeds"], ctx["algos"]
    budget, hp, tol, cache_dir = ctx["budget"], ctx["hp"], ctx["tol"], ctx["cache_dir"]

    rows, n_cells = [], 0
    for target in ctx["targets"]:
        img, gt = target_arrays(sl, target)

        # ---- baseline cổ điển (loại A; không phụ thuộc k lẫn histogram-bg) --
        if scfg.get("include_classical", False):
            for name, mask in classical_masks(
                    img, scfg.get("classical") or [], scfg).items():
                row_key = {"patient_id": sl.patient_id, "target": target,
                           "include_zero_bg": NA_BG, "k": NA_K,
                           "method": name, "seed": NA_SEED}
                if key_of(row_key, KEY_COLS) in done_p:
                    continue
                rows.append({
                    **row_key, "method_class": CLASS_A, "decode_rule": "native",
                    "decode_horn": "native", "thresholds": "",
                    "fitness": "", "f_exact": "", "relative_gap": "", "hit": "",
                    "nfe": "", "budget": "", "runtime_s": "",
                    "psnr": "", "ssim": "",
                    "mask_hash": mask_hash(mask),
                    **mask_metrics(mask, gt, ctx["mcfg"]),
                    "data_source": data_source(cfg),
                    "placeholder": int(data_source(cfg) == "synthetic"),
                })

        for bg in ctx["bgs"]:
            hist = hist_cached(cache_dir, sl, target, bool(bg))
            if hist.sum() <= 0:
                print(f"[SKIP] {sl.patient_id}/{target}/bg={bg}: histogram rỗng")
                continue
            fit = make_fitness(hist, str(scfg.get("fitness", "kapur")))

            for k in ctx["k_list"]:
                # reference optimum (Menotti 2015 — KHÔNG phải đóng góp của ta)
                thr_ex, f_ex = solve_exact(fit, k)
                lm = (labelmap_all
                      if labelmap_all and (not lm_primary_only or k == k_primary)
                      else [])

                # ---- DP-exact (tất định ⇒ seed = -1) -----------------
                row_key = {"patient_id": sl.patient_id, "target": target,
                           "include_zero_bg": str(bool(bg)).lower(), "k": k,
                           "method": EXACT, "seed": NA_SEED}
                if key_of(row_key, KEY_COLS) not in done_p:
                    t0 = time.perf_counter()
                    _ = solve_exact(fit, k)      # đo lại để có runtime sạch
                    dt = time.perf_counter() - t0
                    base = _cell_common(cfg, sl, target, bg, k, EXACT, NA_SEED,
                                        img, list(thr_ex), float(f_ex), float(f_ex), tol)
                    base.update({"nfe": "", "budget": "", "runtime_s": dt})
                    lm_dp = lm if (lm_methods is None or EXACT in lm_methods) else []
                    rows.extend(decode_rows(base, img, gt, list(thr_ex), scfg, rules, lm_dp))
                    n_cells += 1

                # ---- metaheuristic × seed ----------------------------
                for algo in algos:
                    use_lm = lm if (lm_methods is None or algo in lm_methods) else []
                    for seed in seeds:
                        row_key = {"patient_id": sl.patient_id, "target": target,
                                   "include_zero_bg": str(bool(bg)).lower(), "k": k,
                                   "method": algo, "seed": seed}
                        if key_of(row_key, KEY_COLS) in done_p:
                            continue
                        res = run_optimizer_cell(algo, fit, k, seed, budget, hp)
                        base = _cell_common(cfg, sl, target, bg, k, algo, seed, img,
                                            res["thresholds"], res["fitness"],
                                            float(f_ex), tol)
                        base.update({"nfe": res["nfe"], "budget": budget,
                                     "runtime_s": res["runtime_s"]})
                        lm_here = use_lm if seed == seeds[0] or not lm_primary_only else []
                        rows.extend(decode_rows(base, img, gt, res["thresholds"],
                                                scfg, rules, lm_here))
                        n_cells += 1
    return rows, n_cells


def main() -> int:
    _p = parse_args(__doc__.splitlines()[0])
    _p.add_argument(
        "--k-subset",
        type=str,
        default=None,
        help="chỉ chạy các k này, VD '2,3,4'. E2 (~20h) vượt giới hạn session Kaggle "
             "12h ⇒ chia stage theo k qua nhiều session, rồi merge (docs/huong-dan-setup-kaggle.md §4)",
    )
    _p.add_argument(
        "--workers",
        type=int,
        default=0,
        help="số tiến trình song song, chia việc theo BỆNH NHÂN. 0 (MẶC ĐỊNH) = dùng hết "
             "os.cpu_count(); đặt 1 để quay về đường chạy tuần tự nguyên bản. Mặc định là "
             "auto vì notebook Kaggle gọi script này KHÔNG kèm cờ, mà chạy 1 luồng ở n=369 "
             "tốn ~114h CPU. Đổi mặc định KHÔNG đổi số: "
             "BIT-EXACT với tuần tự: mỗi ô gọi set_all_seeds(seed) "
             "riêng (_common.run_optimizer_cell) nên kết quả KHÔNG phụ thuộc thứ tự chạy; "
             "Pool.imap giữ nguyên thứ tự bệnh nhân ⇒ raw.csv giống hệt (trừ cột runtime_s, "
             "vốn là wall-clock). 0 hoặc âm ⇒ dùng os.cpu_count().",
    )
    args = _p.parse_args()
    cfg, cfg_hash = load_config(args.config)
    scfg = section(cfg, "main")
    out_dir = resolve_output_dir(scfg, args.output, "results/main")
    raw_path = out_dir / "raw.csv"

    mcfg = metrics_cfg(scfg)
    dcfg = scfg.get("decoding") or {}
    rules = list(dcfg.get("rules", ["brightest"]))
    labelmap_all = list(dcfg.get("labelmap") or [])
    lm_primary_only = bool(dcfg.get("labelmap_primary_only", True))
    lm_methods = dcfg.get("labelmap_methods")  # None ⇒ mọi phương pháp

    targets = list(scfg.get("targets", ["wt_flair"]))
    bgs = scfg.get("include_zero_bg", [True])
    bgs = [bgs] if isinstance(bgs, bool) else list(bgs)
    k_list = [int(k) for k in scfg.get("k_list", [2])]
    if args.k_subset:
        requested = [int(x) for x in args.k_subset.split(",") if x.strip()]
        unknown = sorted(set(requested) - set(k_list))
        if unknown:
            raise SystemExit(
                f"--k-subset {unknown} không có trong k_list của config ({k_list}). "
                "Chia stage chỉ được chọn TẬP CON của lưới đã preregister, không mở rộng nó."
            )
        k_list = [k for k in k_list if k in requested]
    # k_primary là hằng số thiết kế đã preregister (A4e), không suy ra từ subset của stage.
    k_primary = int(scfg.get("k_primary", k_list[0]))
    seeds = [int(s) for s in scfg.get("seeds", [0])]
    budget = int(scfg.get("budget", 1000))
    hp = dict(scfg.get("hyperparams") or {})
    algos = list(scfg.get("optimizers") or [])
    tol = float((scfg.get("stats") or {}).get("hit_gap_tol", 1e-4))
    cache_dir = out_dir / "cache"
    if scfg.get("cache_dir"):
        from _common import ROOT

        cache_dir = ROOT / scfg["cache_dir"]

    fields = raw_fields(mcfg)
    done = done_keys(raw_path, KEY_COLS, args.resume)
    n_cells = 0
    t_start = time.perf_counter()

    ctx = {
        "cfg": cfg, "scfg": scfg, "mcfg": mcfg, "targets": targets, "bgs": bgs,
        "k_list": k_list, "k_primary": k_primary, "seeds": seeds, "budget": budget,
        "hp": hp, "algos": algos, "tol": tol, "cache_dir": cache_dir, "rules": rules,
        "labelmap_all": labelmap_all, "lm_primary_only": lm_primary_only,
        "lm_methods": lm_methods,
    }
    workers = int(args.workers) or (os.cpu_count() or 1)
    if workers < 0:
        workers = os.cpu_count() or 1

    def _tasks():
        """Sinh task theo bệnh nhân; lọc sẵn done-keys của riêng bệnh nhân đó
        (gửi cả tập `done` cho mỗi worker sẽ pickle thừa hàng trăm nghìn khoá)."""
        for sl in iter_slices(scfg):
            yield (sl, {t for t in done if t[0] == sl.patient_id}, ctx)

    with CsvAppender(raw_path, fields, "run_main_grid.py", cfg, resume=args.resume,
                     note="long-format: 1 row per (patient, target, bg, k, method, seed, "
                          "decode_rule). k=-1 / seed=-1 / include_zero_bg=na ⇒ not applicable."
                     ) as w:
        if workers <= 1:
            results = (_patient_rows(t) for t in _tasks())
        else:
            # imap (KHÔNG imap_unordered) ⇒ giữ nguyên thứ tự bệnh nhân ⇒ raw.csv
            # giống hệt bản tuần tự, không chỉ tương đương về nội dung.
            print(f"[E2] chạy song song {workers} tiến trình (chia theo bệnh nhân); "
                  f"ghi CSV vẫn tuần tự ở tiến trình cha.")
            pool = mp.Pool(processes=workers)
            results = pool.imap(_patient_rows, _tasks(), chunksize=1)

        try:
            for rows, n in results:
                for r in rows:
                    w.write(r)
                w.flush()       # checkpoint sau MỖI bệnh nhân (§5 Kaggle #3)
                n_cells += n
        finally:
            if workers > 1:
                pool.close()
                pool.join()

    elapsed = time.perf_counter() - t_start
    summary_path, ident_path = summarise(raw_path, out_dir, scfg, cfg, algos)

    write_run_manifest(
        out_dir, cfg, cfg_hash, args.config, [raw_path, summary_path, ident_path],
        extra={"experiment": "E2 main grid", "n_cells_computed": n_cells,
               "budget": budget, "k_list": k_list, "seeds": seeds, "optimizers": algos,
               "decoding_rules": rules, "labelmap_decoders": labelmap_all,
               "elapsed_s": round(elapsed, 3)},
    )
    print(f"\n[E2] {n_cells} ô mới, {elapsed:.1f}s → {raw_path}")
    print(f"[E2] summary → {summary_path}\n[E2] mask-identity → {ident_path}")
    return 0


# --------------------------------------------------------------------------- #
# summary.csv + mask_identity.csv
# --------------------------------------------------------------------------- #
def summarise(raw_path, out_dir, scfg, cfg, algos):
    """Tổng hợp raw.csv → summary.csv + mask_identity.csv (không gõ số tay)."""
    from src.eval.stats import bootstrap_ci

    df = read_results_csv(raw_path)

    # Lớp phòng vệ: raw.csv là append-only nên một lần --resume trượt khoá sẽ để lại
    # dòng LẶP. Các bản sao bit-identical (đã kiểm 2026-07-19) nên bỏ trùng là vô hại,
    # nhưng KHÔNG bỏ trùng thì median/CI bị đếm hai lần ⇒ số sai vào Bảng III.
    full_key = KEY_COLS + ["decode_rule"]
    if all(c in df.columns for c in full_key):
        n_before = len(df)
        df = df.drop_duplicates(full_key, keep="first")
        if n_before != len(df):
            print(f"[summarise] BỎ TRÙNG {n_before - len(df)} dòng lặp khoá "
                  f"(còn {len(df)}). Nguyên nhân gốc: --resume trượt khoá; "
                  f"đã vá ở read_results_csv.", flush=True)

    mcfg = metrics_cfg(scfg)
    nboot = int(mcfg.get("bootstrap_n", 10000))

    # A7 — mean±std là cách trình bày SAI cho Dice (chặn [0,1], lệch, thường bimodal).
    # Khoá: median [IQR] + 95% bootstrap CI.
    rows = []
    gcols = ["target", "include_zero_bg", "k", "method", "decode_rule"]
    for keys, g in df.groupby(gcols, dropna=False):
        d = pd.to_numeric(g["dice"], errors="coerce").dropna().to_numpy()
        lo, hi = bootstrap_ci(d, stat=np.median, n=nboot) if d.size else (np.nan, np.nan)
        gap = pd.to_numeric(g["relative_gap"], errors="coerce").dropna()
        hit = pd.to_numeric(g["hit"], errors="coerce").dropna()
        rows.append({
            **dict(zip(gcols, keys)),
            "n_rows": len(g),
            "n_patients": g["patient_id"].nunique(),
            "dice_median": np.median(d) if d.size else np.nan,
            "dice_q1": np.percentile(d, 25) if d.size else np.nan,
            "dice_q3": np.percentile(d, 75) if d.size else np.nan,
            "dice_ci_low": lo, "dice_ci_high": hi,
            "hd95_median": pd.to_numeric(g["hd95"], errors="coerce").median(),
            "nsd_median": pd.to_numeric(g["nsd"], errors="coerce").median(),
            "n_components_median": pd.to_numeric(g["n_components"], errors="coerce").median(),
            # A7 — empty-mask rate là KẾT QUẢ ĐỘC LẬP (bằng chứng cho P3), không được giấu
            "empty_mask_rate": pd.to_numeric(g["empty_mask"], errors="coerce").mean(),
            "psnr_median": pd.to_numeric(g["psnr"], errors="coerce").median(),
            "ssim_median": pd.to_numeric(g["ssim"], errors="coerce").median(),
            "relative_gap_mean": gap.mean() if len(gap) else np.nan,
            "relative_gap_std": gap.std(ddof=1) if len(gap) > 1 else np.nan,
            "hit_rate": hit.mean() if len(hit) else np.nan,
            "nfe_mean": pd.to_numeric(g["nfe"], errors="coerce").mean(),
            "runtime_s_mean": pd.to_numeric(g["runtime_s"], errors="coerce").mean(),
            "placeholder": int(data_source(cfg) == "synthetic"),
        })
    summary = pd.DataFrame(rows).sort_values(gcols)
    summary_path = out_dir / "summary.csv"
    _write_with_banner(summary, summary_path, cfg, "run_main_grid.py::summarise")

    # ---- MASK-IDENTITY RATE (headline A0) ---------------------------------- #
    meta = [a for a in algos if a in set(df["method"])]
    sub = df[df["method"].isin(meta)]
    ident = []
    if not sub.empty:
        for keys, g in sub.groupby(["target", "include_zero_bg", "k", "decode_rule"],
                                   dropna=False):
            per_cell = g.groupby(["patient_id", "seed"])["mask_hash"].nunique()
            n_meth = g.groupby(["patient_id", "seed"])["method"].nunique()
            valid = per_cell[n_meth >= 2]
            ident.append({
                "target": keys[0], "include_zero_bg": keys[1], "k": keys[2],
                "decode_rule": keys[3],
                "n_groups": int(valid.size),
                "n_methods_compared": int(n_meth.max()) if len(n_meth) else 0,
                # tỷ lệ ô (bệnh nhân, seed) mà MỌI metaheuristic cho mask GIỐNG HỆT
                "mask_identity_rate": float((valid == 1).mean()) if valid.size else np.nan,
                "distinct_masks_median": float(valid.median()) if valid.size else np.nan,
                "placeholder": int(data_source(cfg) == "synthetic"),
            })
    ident_path = out_dir / "mask_identity.csv"
    _write_with_banner(pd.DataFrame(ident), ident_path, cfg,
                       "run_main_grid.py::summarise (A0 headline)")

    write_readme(
        out_dir, cfg, "E2 — lưới chính equal-NFE",
        "| file | nội dung |\n|---|---|\n"
        "| `raw.csv` | 1 hàng / (bệnh nhân, target, bg, k, method, seed, decode_rule) |\n"
        "| `summary.csv` | median [IQR] + 95% bootstrap CI của Dice (A7), gap, hit-rate, "
        "NFE, runtime, **empty-mask rate**, PSNR/SSIM |\n"
        "| `mask_identity.csv` | **A0 headline** — % ô mà MỌI metaheuristic sinh mask "
        "giống hệt từng byte |\n\n"
        "Quy ước sentinel: `k = -1`, `seed = -1`, `include_zero_bg = na` ⇒ không áp dụng "
        "(baseline cổ điển không có k; DP-exact tất định nên không có seed).\n\n"
        "⚠️ `runtime_s` KHÔNG được dùng để claim tốc độ — đồng tiền chính là **NFE + độ "
        "phức tạp** (A0). ⚠️ PSNR/SSIM là **bằng chứng cho P3**, không phải kết quả.",
    )
    return summary_path, ident_path


def _write_with_banner(df: pd.DataFrame, path, cfg, script: str) -> None:
    from _common import _banner

    with open(path, "w", newline="", encoding="utf-8") as fh:
        for line in _banner(script, cfg):
            fh.write(line + "\n")
        df.to_csv(fh, index=False)


if __name__ == "__main__":
    sys.exit(main())

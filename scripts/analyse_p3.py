"""P3 — phân tích ROBUSTNESS theo decoding rule (tái lập B4 ở n=368).

    python scripts/analyse_p3.py --config configs/exp_main.yaml

Vì sao script này tồn tại (đọc trước khi diễn giải số):
  • `results/stats/p3_delta.csv` (run_stats.py) chỉ tính ở decode_rule PRIMARY
    (`brightest`, prereg A4e — rule ta KIỂM TRA, không phải rule ta quy kết).
  • Nhưng prereg §6/B4 `[SCREENING]` đã cảnh báo: **dấu của Spearman(k, Dice) LẬT
    theo decoding rule**, và bắt buộc **tái lập ở n=368 TRƯỚC KHI VIẾT**. Nếu tương
    quan âm chỉ tồn tại dưới một rule ⇒ headline "metrics are anti-correlated" SAI,
    và bài thật ra chỉ nói "một decoding rule có bias theo k" — nhỏ hơn nhiều.
  • Script này chạy đúng phép kiểm đó + hai kiểm tra prereg còn nợ:
    (3) PSNR có đơn điệu tăng theo k không (lập luận Lloyd–Max, §6/A4a "chứng minh,
        đừng tương quan"), và (4) tỉ lệ mask rỗng theo k (prereg dòng 386 — phải báo
        cáo như KẾT QUẢ ĐỘC LẬP, kể cả khi nó âm).

Đơn vị phân tích = BỆNH NHÂN. Dùng method=DP-exact (tối ưu toàn cục thật) để loại
hoàn toàn nhiễu optimizer: mọi khác biệt còn lại KHÔNG thể đổ cho metaheuristic.

Sinh ra (results/stats/):
    p3_by_rule.csv          — Δᵢ = Dice(k*_Dice) − Dice(k*_PSNR), tách theo rule
    p3_spearman_by_rule.csv — Spearman(k, Dice) từng BN, tách theo rule (B4)
    p3_psnr_monotone.csv    — PSNR trung bình theo k (chứng cứ Lloyd–Max)
    p3_empty_mask_by_k.csv  — tỉ lệ mask rỗng theo k
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, wilcoxon

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from _common import (  # noqa: E402
    load_config,
    parse_args,
    read_results_csv,
    resolve_output_dir,
    section,
    write_run_manifest,
)

HORN1 = ("brightest", "upper_union", "otsu_pick", "morph")
REFERENCE = "DP-exact"
BOOT = 10000
SEED = 0


def _boot_ci(x: np.ndarray, n: int = BOOT) -> tuple[float, float]:
    rng = np.random.default_rng(SEED)
    med = [np.median(rng.choice(x, x.size, replace=True)) for _ in range(n)]
    return tuple(np.percentile(med, [2.5, 97.5]))


def _delta_by_rule(d: pd.DataFrame, sesoi: float) -> pd.DataFrame:
    """P3-primary (prereg A4a) nhưng lặp qua TỪNG decoding rule."""
    out = []
    for (tg, bg), g0 in d.groupby(["target", "include_zero_bg"]):
        for rule, g in g0.groupby("decode_rule"):
            deltas, k_psnr, k_dice = [], [], []
            for _pid, gp in g.groupby("patient_id"):
                a = gp.groupby("k")[["dice", "psnr"]].mean().dropna()
                if len(a) < 5:          # cần đủ trục k mới nói được chuyện chọn k
                    continue
                kp, kd = a.psnr.idxmax(), a.dice.idxmax()
                deltas.append(a.dice[kd] - a.dice[kp])
                k_psnr.append(kp)
                k_dice.append(kd)
            deltas = np.asarray(deltas, dtype=float)
            if deltas.size < 10:
                continue
            p = float(wilcoxon(deltas).pvalue) if np.any(deltas != 0) else np.nan
            lo, hi = _boot_ci(deltas)
            out.append({
                "target": tg, "include_zero_bg": bg, "decode_rule": rule,
                "reference": REFERENCE, "n": deltas.size,
                "median_delta": float(np.median(deltas)), "mean_delta": float(deltas.mean()),
                "ci_low": lo, "ci_high": hi, "p": p, "sesoi": sesoi,
                "n_zero": int((deltas == 0).sum()),
                "mode_k_psnr": int(pd.Series(k_psnr).mode()[0]),
                "mode_k_dice": int(pd.Series(k_dice).mode()[0]),
                # thành công = ĐÚNG luật đã khoá ở prereg A4a (median > SESOI,
                # p < 0,05, CI không chứa SESOI). KHÔNG hạ ngưỡng cho khớp số.
                "success": bool(np.median(deltas) > sesoi and p < 0.05 and lo > sesoi),
            })
    return pd.DataFrame(out)


def _spearman_by_rule(d: pd.DataFrame) -> pd.DataFrame:
    """B4 — Spearman(k, Dice) TỪNG bệnh nhân, tách theo rule. 7 điểm k mỗi BN."""
    out = []
    for (tg, bg), g0 in d.groupby(["target", "include_zero_bg"]):
        for rule, g in g0.groupby("decode_rule"):
            rho = []
            for _pid, gp in g.groupby("patient_id"):
                s = gp.groupby("k").dice.mean()
                if s.notna().sum() >= 5 and s.nunique() > 1:
                    r = spearmanr(s.index.values, s.values).correlation
                    if np.isfinite(r):
                        rho.append(r)
            rho = np.asarray(rho, dtype=float)
            if rho.size < 10:
                continue
            lo, hi = _boot_ci(rho)
            out.append({
                "target": tg, "include_zero_bg": bg, "decode_rule": rule,
                "n": rho.size, "median_rho": float(np.median(rho)),
                "mean_rho": float(rho.mean()), "ci_low": lo, "ci_high": hi,
                "frac_negative": float((rho < 0).mean()),
                "p": float(wilcoxon(rho).pvalue),
                # ngưỡng GỐC của §1/P3 — giữ nguyên để cho thấy nó THẤT BẠI,
                # không phải để cứu. Prereg A4a đã hạ nó xuống SECONDARY.
                "success_orig_rule": bool(np.median(rho) < -0.5),
            })
    return pd.DataFrame(out)


def main() -> int:
    args = parse_args(__doc__.splitlines()[0]).parse_args()
    cfg, cfg_hash = load_config(args.config)
    scfg = section(cfg, "stats")
    out_dir = resolve_output_dir(scfg, args.output, "results/stats")
    sesoi = float(scfg.get("sesoi", 0.01))

    raw = ROOT / scfg.get("main_dir", "results/main") / "raw.csv"
    if not raw.exists():
        raise SystemExit(f"Không thấy {raw} — chạy run_main_grid.py trước.")
    df = read_results_csv(raw)
    df["k"] = pd.to_numeric(df["k"], errors="coerce")
    for c in ("dice", "psnr"):
        df[c] = pd.to_numeric(df[c], errors="coerce")

    ref = df[(df.method == REFERENCE) & (df.k > 0)].copy()
    ref["k"] = ref.k.astype(int)
    horn1 = ref[ref.decode_rule.isin(HORN1)]

    delta = _delta_by_rule(horn1, sesoi)
    spear = _spearman_by_rule(horn1)

    # (3) Lloyd–Max: PSNR là hàm của sai số lượng tử hoá ⇒ phải TĂNG theo k.
    native = ref[ref.decode_rule == "native"]
    psnr_src = native if len(native) else ref
    piv = psnr_src.groupby(["target", "include_zero_bg", "k"]).psnr.mean().unstack()
    piv["monotone_increasing"] = piv.apply(
        lambda r: bool(np.all(np.diff(r.dropna().values) > 0)), axis=1)
    mono = piv.reset_index()

    # (4) prereg dòng 386 — báo cáo kể cả khi ÂM (không có mask rỗng).
    empty = pd.DataFrame()
    if "empty_mask" in df.columns:
        h = df[(df.k > 0) & (df.decode_rule.isin(HORN1))].copy()
        h["k"] = h.k.astype(int)
        h["empty_mask"] = pd.to_numeric(h.empty_mask, errors="coerce")
        empty = (h.groupby(["target", "decode_rule", "k"]).empty_mask.mean()
                 .unstack().reset_index())

    paths = []
    for name, frame in (("p3_by_rule", delta), ("p3_spearman_by_rule", spear),
                        ("p3_psnr_monotone", mono), ("p3_empty_mask_by_k", empty)):
        if frame is None or frame.empty:
            continue
        p = out_dir / f"{name}.csv"
        frame.to_csv(p, index=False)
        paths.append(p)
        print(f"  → {p.relative_to(ROOT)}  ({len(frame)} dòng)")

    write_run_manifest(
        out_dir, cfg, cfg_hash, args.config, paths,
        extra={"experiment": "P3 robustness theo decoding rule (tái lập prereg B4)",
               "reference_method": REFERENCE, "decode_rules": list(HORN1),
               "sesoi": sesoi, "bootstrap_n": BOOT, "unit": "patient"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

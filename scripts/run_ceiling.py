"""E4 — THANG BẬC TRẦN: oracle ladder + baseline cổ điển + P5 (nested CV). → Bảng V · Hình 4

    python scripts/run_ceiling.py --config configs/exp_smoke.yaml            # plumbing
    python scripts/run_ceiling.py --config configs/exp_ceiling.yaml --resume

Ba nhóm hàng, mỗi hàng mang cột `method_class` — **nhãn này phải xuất hiện ở MỌI bảng/hình**:

  * **loại C — `uses test-time ground truth`**: `oracle_single` (trần của decoding "lớp
    sáng nhất") ⊆ `oracle_interval` (trần của mọi band LIÊN TIẾP) ⊆ `oracle_levelset`
    (**TRẦN ĐÚNG** — tập mức xám tuỳ ý, O(L log L)).
    ⛔ Oracle **KHÔNG phải "phương pháp"** — nó là cận trên không đạt được.
    ⛔ CẤM câu *"we establish the ceiling"* (François & Tinarrage, JMIV 68:20, 2026 đã in
       trần 0,83±0,18 trên BraTS FLAIR). Ta claim **phân rã** trần, không claim trần.
    ⛔ CẤM ship `oracle_levelset` như *"Theorem 1 (ours)"* — Lipton, Elkan &
       Narayanaswamy (arXiv:1402.1892, 2014) + RankSEG (JMLR 2023) sở hữu định lý.
       **CLAIM ỨNG DỤNG, KHÔNG CLAIM TOÁN HỌC.**
  * **loại A — unsupervised per-image**: Otsu / Li / Triangle / k-means / GMM.
  * **loại B — CÓ HỌC ⇒ CHỈ out-of-fold**: **P5**, ngưỡng 1-tham-số (phân vị `q` của
    CHÍNH ảnh đó).

**P5 — chống leakage (A3, lỗi DUY NHẤT có thể bị reject vì LIÊM CHÍNH):**
`q*` được fit trên **outer-train fold**, **ĐÓNG BĂNG**, rồi chấm **out-of-fold**. Mỗi bệnh
nhân cho ĐÚNG MỘT giá trị out-of-fold ⇒ Wilcoxon paired / Friedman / TOST mới có định
nghĩa. `qstar.csv` **công bố cả 5 giá trị `q*`** (ổn định giữa các fold ⇒ finding mạnh)
kèm learning curve theo cỡ tập fit. Chuẩn hoá cường độ là **per-image** (loader A3) —
dùng thống kê toàn dataset = preprocessing leak.

**Fallback khoá trước khi thấy số (A10 mục 2):** nếu P5 THUA metaheuristic ⇒ đóng góp
dương rơi về *ceiling decomposition + công cụ chẩn đoán O(L log L) + checklist giao thức*.
Ba thứ đó phải đủ đứng một mình — và đó là lý do E4 chạy ở TUẦN 2, không phải tuần 3.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from _common import (
    CLASS_A,
    CLASS_B,
    CLASS_C,
    NA_BG,
    NA_K,
    NA_SEED,
    ROOT,
    CsvAppender,
    _banner,
    classical_masks,
    data_source,
    done_keys,
    iter_slices,
    key_of,
    load_config,
    mask_metrics,
    metrics_cfg,
    parse_args,
    read_results_csv,
    resolve_output_dir,
    section,
    set_all_seeds,
    target_arrays,
    write_readme,
    write_run_manifest,
)
from src.decode.decoding import mask_hash, oracle_interval, oracle_levelset, oracle_single

KEY_COLS = ["patient_id", "target", "include_zero_bg", "method"]
ORACLES = {
    "oracle_single": oracle_single,
    "oracle_interval": oracle_interval,
    "oracle_levelset": oracle_levelset,
}


# --------------------------------------------------------------------------- #
# P5 — ngưỡng 1-tham-số (per-image percentile)
# --------------------------------------------------------------------------- #
def p5_mask(img, q: float, include_zero_bg: bool) -> np.ndarray:
    """mask = img >= percentile_q(img).  MỘT tham số, per-image (A3 — không dùng
    thống kê toàn dataset).

    `include_zero_bg=False` ⇒ phân vị tính trên pixel > 0 (bỏ nền skull-strip), khớp
    đúng biến thể histogram bỏ-nền của A5c.
    """
    a = np.asarray(img)
    pool = a[a > 0] if not include_zero_bg else a
    if pool.size == 0:
        return np.zeros(a.shape, dtype=bool)
    return a >= np.percentile(pool, q)


def fit_qstar(train, target, q_grid, include_zero_bg: bool):
    """Chọn q* cực đại hoá Dice TRUNG BÌNH trên outer-train. Trả (q*, dice_train)."""
    from src.eval.metrics import dice

    best_q, best_d = float(q_grid[0]), -1.0
    for q in q_grid:
        ds = []
        for sl in train:
            img, gt = target_arrays(sl, target)
            ds.append(dice(p5_mask(img, float(q), include_zero_bg), gt))
        m = float(np.mean(ds)) if ds else 0.0
        if m > best_d:
            best_d, best_q = m, float(q)
    return best_q, best_d


def load_folds(scfg, slices):
    """{fold: [patient_id...]} test-fold ở CẤP BỆNH NHÂN (A3).

    Ưu tiên `data/splits/fold_{i}.json` (artefact commit vào repo). Nếu chưa có (VD
    smoke synthetic) ⇒ chia vòng tròn tất định — CHỈ hợp lệ cho smoke.
    """
    d = scfg.get("data") or {}
    splits_dir = Path(d.get("splits_dir", "data/splits"))
    if not splits_dir.is_absolute():
        splits_dir = ROOT / splits_dir
    n_folds = int(scfg.get("n_folds", 5))
    files = sorted(splits_dir.glob("fold_*.json"))
    if files:
        folds = {}
        for f in files:
            info = json.loads(f.read_text(encoding="utf-8"))
            folds[int(info["fold"])] = {"test": list(info["test"]),
                                        "train": list(info["train"]) + list(info["val"])}
        return folds
    print(f"[WARN] không có {splits_dir}/fold_*.json — chia vòng tròn tất định "
          f"({n_folds} fold). CHỈ hợp lệ cho smoke; lưới thật PHẢI dùng split đã commit "
          f"(A3: phân tầng grade × tertile thể tích WT).")
    ids = [s.patient_id for s in slices]
    folds = {}
    for i in range(n_folds):
        test = [p for j, p in enumerate(ids) if j % n_folds == i]
        folds[i] = {"test": test, "train": [p for p in ids if p not in test]}
    return folds


def main() -> int:
    _p = parse_args(__doc__.splitlines()[0])
    _p.add_argument(
        "--stage",
        choices=("all", "oracles", "p5_nested_cv"),
        default="all",
        help="'p5_nested_cv' chạy RIÊNG bậc-5 (~1h) cho thí nghiệm rủi ro Tuần-1 "
             "(prereg §6/A10 #2: bài có đóng góp dương không?) mà không tốn oracle scan; "
             "'oracles' chạy riêng thang trần; 'all' (mặc định) chạy cả hai",
    )
    args = _p.parse_args()
    cfg, cfg_hash = load_config(args.config)
    scfg = section(cfg, "ceiling")
    out_dir = resolve_output_dir(scfg, args.output, "results/ceiling")
    raw_path, q_path = out_dir / "raw.csv", out_dir / "qstar.csv"

    mcfg = metrics_cfg(scfg)
    targets = list(scfg.get("targets", ["wt_flair"]))
    bgs = scfg.get("include_zero_bg", [True])
    bgs = [bgs] if isinstance(bgs, bool) else list(bgs)
    oracles = list(scfg.get("oracles") or list(ORACLES))
    q_grid = np.linspace(float(scfg.get("q_grid_start", 80.0)),
                         float(scfg.get("q_grid_stop", 99.9)),
                         int(scfg.get("q_grid_num", 100)))
    lc_sizes = [int(s) for s in (scfg.get("learning_curve_sizes") or [0])]
    seed0 = int((scfg.get("seeds") or [0])[0])
    set_all_seeds(seed0)

    fields = (["patient_id", "target", "include_zero_bg", "method", "method_class",
               "fold", "params", "dice", "hd95", "nsd"]
              + [f"nsd_tau{float(t):g}" for t in (mcfg.get("nsd_tau_sensitivity") or [])]
              + ["n_components", "empty_mask", "mask_hash", "data_source", "placeholder"])

    slices = list(iter_slices(scfg))
    by_id = {s.patient_id: s for s in slices}
    folds = load_folds(scfg, slices)
    done = done_keys(raw_path, KEY_COLS, args.resume)
    ph = int(data_source(cfg) == "synthetic")
    qrows, n_rows = [], 0
    t_start = time.perf_counter()

    with CsvAppender(raw_path, fields, "run_ceiling.py", cfg, resume=args.resume,
                     note="method_class: C = uses test-time ground truth (oracle = an "
                          "UNREACHABLE upper bound, NOT a method); B = learned, "
                          "out-of-fold only; A = unsupervised per-image.") as w:
        for target in targets:
            # ---- loại C: oracle ladder (không phụ thuộc histogram-bg) --------
            for name in (oracles if args.stage in ("all", "oracles") else []):
                for sl in slices:
                    rk = {"patient_id": sl.patient_id, "target": target,
                          "include_zero_bg": NA_BG, "method": name}
                    if key_of(rk, KEY_COLS) in done:
                        continue
                    img, gt = target_arrays(sl, target)
                    res = ORACLES[name](img, gt)
                    mask, params = res[0], (res[2] if len(res) > 2 else "levelset")
                    w.write({**rk, "method_class": CLASS_C, "fold": NA_SEED,
                             "params": str(params), "mask_hash": mask_hash(mask),
                             **mask_metrics(mask, gt, mcfg),
                             "data_source": data_source(cfg), "placeholder": ph})
                    n_rows += 1
                w.flush()

            # ---- loại A: baseline cổ điển ------------------------------------
            if scfg.get("include_classical", False):
                for sl in slices:
                    img, gt = target_arrays(sl, target)
                    masks = classical_masks(img, scfg.get("classical") or [], scfg)
                    for name, mask in masks.items():
                        rk = {"patient_id": sl.patient_id, "target": target,
                              "include_zero_bg": NA_BG, "method": name}
                        if key_of(rk, KEY_COLS) in done:
                            continue
                        w.write({**rk, "method_class": CLASS_A, "fold": NA_SEED,
                                 "params": "", "mask_hash": mask_hash(mask),
                                 **mask_metrics(mask, gt, mcfg),
                                 "data_source": data_source(cfg), "placeholder": ph})
                        n_rows += 1
                w.flush()

            # ---- loại B: P5 — nested CV, out-of-fold ONLY (A3) ---------------
            for bg in (bgs if args.stage in ("all", "p5_nested_cv") else []):
                for fold, split in sorted(folds.items()):
                    train = [by_id[p] for p in split["train"] if p in by_id]
                    test = [by_id[p] for p in split["test"] if p in by_id]
                    if not train or not test:
                        continue
                    for size in lc_sizes:
                        sub = train if size in (0, None) else train[:min(size, len(train))]
                        qstar, dtrain = fit_qstar(sub, target, q_grid, bool(bg))
                        # q* ĐÓNG BĂNG tại đây; test fold chưa từng được nhìn.
                        tag = "P5-percentile" if size in (0, None) else f"P5-percentile@n{size}"
                        test_d = []
                        for sl in test:
                            rk = {"patient_id": sl.patient_id, "target": target,
                                  "include_zero_bg": str(bool(bg)).lower(), "method": tag}
                            img, gt = target_arrays(sl, target)
                            mask = p5_mask(img, qstar, bool(bg))
                            mm = mask_metrics(mask, gt, mcfg)
                            test_d.append(mm["dice"])
                            if key_of(rk, KEY_COLS) in done:
                                continue
                            w.write({**rk, "method_class": CLASS_B, "fold": fold,
                                     "params": f"q={qstar:.4f}", "mask_hash": mask_hash(mask),
                                     **mm, "data_source": data_source(cfg), "placeholder": ph})
                            n_rows += 1
                        w.flush()
                        qrows.append({
                            "target": target, "include_zero_bg": str(bool(bg)).lower(),
                            "fold": fold, "fit_size": len(sub), "label": tag,
                            "q_star": qstar, "train_dice_mean": dtrain,
                            "n_train": len(sub), "n_test": len(test),
                            "test_dice_median": float(np.median(test_d)) if test_d else np.nan,
                            "placeholder": ph,
                        })

    qdf = pd.DataFrame(qrows)
    _write_banner_csv(qdf, q_path, cfg, "run_ceiling.py (P5 q* — nested CV, A3)")
    summary_path = _summarise(raw_path, out_dir, scfg, cfg)

    elapsed = time.perf_counter() - t_start
    write_run_manifest(
        out_dir, cfg, cfg_hash, args.config, [raw_path, q_path, summary_path],
        extra={"experiment": "E4 ceiling ladder + P5", "oracles": oracles,
               "n_folds": len(folds), "q_grid": [float(q_grid[0]), float(q_grid[-1]),
                                                 len(q_grid)],
               "learning_curve_sizes": lc_sizes, "n_rows": n_rows,
               "p5_protocol": "nested CV, patient-level, q* fitted on outer-train, "
                              "frozen, evaluated out-of-fold (prereg A3)",
               "elapsed_s": round(elapsed, 3)},
    )
    write_readme(
        out_dir, cfg, "E4 — ceiling ladder + P5 (Bảng V · Hình 4)",
        "| file | nội dung |\n|---|---|\n"
        "| `raw.csv` | 1 hàng / (bệnh nhân, target, bg, method) — cột `method_class` |\n"
        "| `qstar.csv` | **5 giá trị q\\*** (một/fold) + learning curve theo cỡ tập fit |\n"
        "| `summary.csv` | median [IQR] + 95% bootstrap CI theo bậc |\n\n"
        "🔴 **Oracle = loại C, `uses test-time ground truth`** — KHÔNG phải phương pháp, "
        "là cận trên không đạt được. Nhãn này phải in ở MỌI bảng/hình.\n"
        "🔴 **P5 = loại B** — chỉ đọc số **out-of-fold**. `q*` fit trên outer-train và đóng "
        "băng trước khi chạm test fold (A3).\n"
        "⛔ CẤM \"we establish the ceiling\" (François & Tinarrage, JMIV 2026) · CẤM claim "
        "định lý level-set (Lipton et al. 2014 / RankSEG 2023) — claim **ứng dụng**.",
    )
    print(f"\n[E4] {n_rows} hàng, {elapsed:.1f}s → {raw_path}")
    print(f"[E4] q* → {q_path}\n[E4] summary → {summary_path}")
    if not qdf.empty:
        print("\n[E4] q* theo fold (A3 — công bố cả 5):")
        print(qdf[qdf["label"] == "P5-percentile"][
            ["target", "include_zero_bg", "fold", "q_star", "test_dice_median"]
        ].to_string(index=False))
    return 0


def _summarise(raw_path, out_dir, scfg, cfg):
    from src.eval.stats import bootstrap_ci

    df = read_results_csv(raw_path)
    nboot = int(metrics_cfg(scfg).get("bootstrap_n", 10000))
    rows = []
    for keys, g in df.groupby(["target", "include_zero_bg", "method", "method_class"],
                              dropna=False):
        d = pd.to_numeric(g["dice"], errors="coerce").dropna().to_numpy()
        lo, hi = bootstrap_ci(d, stat=np.median, n=nboot) if d.size else (np.nan, np.nan)
        rows.append({
            "target": keys[0], "include_zero_bg": keys[1], "method": keys[2],
            "method_class": keys[3], "n_patients": g["patient_id"].nunique(),
            "dice_median": np.median(d) if d.size else np.nan,
            "dice_q1": np.percentile(d, 25) if d.size else np.nan,
            "dice_q3": np.percentile(d, 75) if d.size else np.nan,
            "dice_ci_low": lo, "dice_ci_high": hi,
            "hd95_median": pd.to_numeric(g["hd95"], errors="coerce").median(),
            "nsd_median": pd.to_numeric(g["nsd"], errors="coerce").median(),
            "n_components_median": pd.to_numeric(g["n_components"], errors="coerce").median(),
            "empty_mask_rate": pd.to_numeric(g["empty_mask"], errors="coerce").mean(),
            "placeholder": int(data_source(cfg) == "synthetic"),
        })
    out = pd.DataFrame(rows).sort_values(["target", "method_class", "dice_median"])
    path = out_dir / "summary.csv"
    _write_banner_csv(out, path, cfg, "run_ceiling.py::_summarise")
    return path


def _write_banner_csv(df, path, cfg, script):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        for line in _banner(script, cfg):
            fh.write(line + "\n")
        df.to_csv(fh, index=False)


if __name__ == "__main__":
    sys.exit(main())

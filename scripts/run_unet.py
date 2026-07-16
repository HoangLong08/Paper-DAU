"""E4 — 2D U-Net (GPU), baseline DL CÔNG BẰNG: cùng input = 1 lát FLAIR. → bậc 8 của Hình 4

    python scripts/run_unet.py --config configs/exp_smoke.yaml            # CPU, synthetic
    python scripts/run_unet.py --config configs/exp_unet.yaml --resume    # 5 fold × 3 seed, GPU

**A3 — U-Net là loại B ⇒ CHỈ chấm out-of-fold.** `train_unet_cv` train trên TẤT CẢ lát có
u của bệnh nhân outer-train (hàng nghìn lát) và chọn epoch bằng inner-val; `infer_unet`
chấm trên ĐÚNG 1 lát chỉ định của bệnh nhân **held-out** — cùng lát mà thresholding thấy.
*"Cùng input" là ràng buộc lúc INFERENCE, không phải lúc TRAIN* — nếu train trên 1 lát/BN
thì kết quả P4, dù dương hay âm, đều KHÔNG diễn giải được (confound thiếu dữ liệu).

Mỗi bệnh nhân ⇒ ĐÚNG MỘT giá trị out-of-fold trên CÙNG tập bệnh nhân với các bậc khác
⇒ Wilcoxon paired / Friedman / TOST mới có định nghĩa (A3).

❌ **KHÔNG train nnU-Net** — 3D full-res × 5 fold = nhiều ngày GPU; Kaggle: 30 GPU-h/tuần,
session ≤ 12 h. Số nnU-Net chỉ **trích từ văn liệu** (config `literature_reference`) và
phải dán nhãn *"reference from literature, not run by us, different input protocol"*.

**Fallback P4 khoá trước khi thấy số (A2):** nếu U-Net KHÔNG vượt trần, headline **KHÔNG**
rút về *"thresholding chạm trần của chính nó"* (= đúng thứ François & Tinarrage đã in ⇒
zero novelty). Headline đổi thành: *"Trần CAO — thất bại của thresholding KHÔNG do giới
hạn biểu diễn, mà do BÀI TOÁN CHỌN NGƯỠNG; và không cỗ máy metaheuristic nào chạm tới
bài toán chọn đó."*
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from _common import (
    CLASS_B,
    NA_BG,
    ROOT,
    CsvAppender,
    _banner,
    data_root,
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
from run_ceiling import load_folds
from src.baselines.unet2d import infer_unet, train_unet_cv
from src.decode.decoding import mask_hash

KEY_COLS = ["patient_id", "target", "fold", "seed"]
METHOD = "2D-UNet"


def main() -> int:
    args = parse_args(__doc__.splitlines()[0]).parse_args()
    cfg, cfg_hash = load_config(args.config)
    scfg = section(cfg, "unet")
    out_dir = resolve_output_dir(scfg, args.output, "results/unet")
    raw_path = out_dir / "raw.csv"

    mcfg = metrics_cfg(scfg)
    targets = list(scfg.get("targets", ["wt_flair"]))
    folds = [int(f) for f in scfg.get("folds", [0])]
    seeds = [int(s) for s in scfg.get("seeds", [0])]
    ucfg = dict(scfg.get("cfg") or {})
    ucfg.setdefault("out_dir", str(out_dir / "checkpoints"))
    smoke = bool(ucfg.get("smoke", False))

    d = scfg.get("data") or {}
    cohort_csv = ROOT / d.get("cohort_csv", "data/splits/brats_cohort.csv")
    splits_dir = ROOT / d.get("splits_dir", "data/splits")
    brats_root = data_root(scfg)

    slices = list(iter_slices(scfg))
    by_id = {s.patient_id: s for s in slices}
    fold_map = load_folds(scfg, slices)

    fields = (["patient_id", "target", "method", "method_class", "fold", "seed",
               "checkpoint", "dice", "hd95", "nsd"]
              + [f"nsd_tau{float(t):g}" for t in (mcfg.get("nsd_tau_sensitivity") or [])]
              + ["n_components", "empty_mask", "mask_hash", "data_source", "placeholder"])
    done = done_keys(raw_path, KEY_COLS, args.resume)
    ph = int(data_source(cfg) == "synthetic")
    n_rows = 0
    t_start = time.perf_counter()

    with CsvAppender(raw_path, fields, "run_unet.py", cfg, resume=args.resume,
                     note="A3: class B (learned) — OUT-OF-FOLD ONLY. Trained on all "
                          "tumour slices of outer-train patients; scored on the single "
                          "designated slice of held-out patients ('same input' is an "
                          "INFERENCE constraint).") as w:
        for target in targets:
            for fold in folds:
                for seed in seeds:
                    set_all_seeds(seed)
                    test_ids = fold_map.get(fold, {}).get("test", [])
                    if not smoke and not test_ids:
                        print(f"[SKIP] fold {fold}: không có danh sách test")
                        continue
                    pending = [p for p in (test_ids or list(by_id))
                               if key_of({"patient_id": p, "target": target,
                                          "fold": fold, "seed": seed}, KEY_COLS) not in done]
                    if not pending:
                        continue

                    print(f"[E4/U-Net] train fold={fold} seed={seed} "
                          f"(smoke={smoke}, device={ucfg.get('device')}) ...")
                    ckpt = train_unet_cv(cohort_csv, splits_dir, brats_root,
                                         fold=fold, seed=seed, cfg=ucfg)

                    for pid in pending:
                        sl = by_id.get(pid)
                        if sl is None:
                            print(f"[SKIP] {pid}: không nạp được lát")
                            continue
                        _img, gt = target_arrays(sl, target)
                        mask = infer_unet(ckpt, sl)   # ĐÚNG 1 lát của BN held-out
                        w.write({"patient_id": pid, "target": target, "method": METHOD,
                                 "method_class": CLASS_B, "fold": fold, "seed": seed,
                                 "checkpoint": str(ckpt), "mask_hash": mask_hash(mask),
                                 **mask_metrics(mask, gt, mcfg),
                                 "data_source": data_source(cfg), "placeholder": ph})
                        n_rows += 1
                    w.flush()

    summary_path = _summarise(raw_path, out_dir, scfg, cfg)
    elapsed = time.perf_counter() - t_start
    write_run_manifest(
        out_dir, cfg, cfg_hash, args.config, [raw_path, summary_path],
        extra={"experiment": "E4 2D U-Net", "folds": folds, "seeds": seeds,
               "unet_cfg": ucfg, "n_rows": n_rows,
               "protocol": "class B — out-of-fold only; train on all tumour slices of "
                           "outer-train patients, infer on the single designated slice "
                           "of held-out patients (prereg A3)",
               "nnunet": "NOT trained — literature reference only "
                         "(Isensee et al., arXiv:2011.00848)",
               "elapsed_s": round(elapsed, 3)},
    )
    lit = scfg.get("literature_reference") or {}
    write_readme(
        out_dir, cfg, "E4 — 2D U-Net (bậc 8 của Hình 4)",
        f"5 fold × ≥3 seed, out-of-fold only (A3). Fold chạy: {folds}, seed: {seeds}.\n\n"
        "**Cùng input** = 1 lát FLAIR lúc **inference**; train dùng mọi lát có u của bệnh "
        "nhân outer-train ⇒ vô hiệu hoá phản biện *\"anh so 2D đơn-modality với 3D "
        "đa-modality\"* mà không tạo confound thiếu dữ liệu.\n\n"
        + (f"**Tham chiếu văn liệu (KHÔNG chạy):** {lit.get('name')} — WT Dice "
           f"{lit.get('wt_dice_val')} val / {lit.get('wt_dice_test')} test "
           f"({lit.get('source')}). Nhãn bắt buộc: *{lit.get('label')}*. Dùng làm "
           f"**context**, KHÔNG phải baseline so trực tiếp.\n" if lit else ""),
    )
    print(f"\n[E4/U-Net] {n_rows} hàng, {elapsed:.1f}s → {raw_path}\n"
          f"[E4/U-Net] summary → {summary_path}")
    return 0


def _summarise(raw_path, out_dir, scfg, cfg):
    from src.eval.stats import bootstrap_ci

    df = read_results_csv(raw_path)
    nboot = int(metrics_cfg(scfg).get("bootstrap_n", 10000))
    rows = []
    if not df.empty:
        # Mỗi bệnh nhân: gộp qua seed (median) ⇒ ĐÚNG MỘT giá trị out-of-fold/bệnh nhân.
        per_patient = df.groupby(["target", "patient_id"])["dice"].median().reset_index()
        for target, g in per_patient.groupby("target"):
            d = g["dice"].to_numpy()
            lo, hi = bootstrap_ci(d, stat=np.median, n=nboot)
            sub = df[df["target"] == target]
            rows.append({
                "target": target, "method": METHOD, "method_class": CLASS_B,
                "n_patients": g["patient_id"].nunique(),
                "n_folds": sub["fold"].nunique(), "n_seeds": sub["seed"].nunique(),
                "dice_median": float(np.median(d)),
                "dice_q1": float(np.percentile(d, 25)),
                "dice_q3": float(np.percentile(d, 75)),
                "dice_ci_low": lo, "dice_ci_high": hi,
                "hd95_median": pd.to_numeric(sub["hd95"], errors="coerce").median(),
                "nsd_median": pd.to_numeric(sub["nsd"], errors="coerce").median(),
                "empty_mask_rate": pd.to_numeric(sub["empty_mask"], errors="coerce").mean(),
                "placeholder": int(data_source(cfg) == "synthetic"),
            })
    path = out_dir / "summary.csv"
    with open(path, "w", newline="", encoding="utf-8") as fh:
        for line in _banner("run_unet.py::_summarise", cfg):
            fh.write(line + "\n")
        pd.DataFrame(rows).to_csv(fh, index=False)
    return path


if __name__ == "__main__":
    sys.exit(main())

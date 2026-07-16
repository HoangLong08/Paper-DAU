"""E0 — cohort manifest + split cấp BỆNH NHÂN (chạy TRƯỚC mọi thí nghiệm dùng fold).

    python scripts/make_splits.py --config configs/exp_main.yaml
    → data/splits/brats_cohort.csv · data/splits/fold_{0..4}.json · run-manifest.json

Vì sao script này tồn tại (A3):
    `run_ceiling.py::load_folds` ưu tiên `data/splits/fold_*.json`; KHÔNG có file đó
    nó rơi về **chia vòng tròn** kèm [WARN] — hợp lệ cho smoke, **KHÔNG** hợp lệ cho
    P5. P5 là loại B (CÓ HỌC) ⇒ chỉ được đánh giá out-of-fold trên split phân tầng
    grade × tertile thể tích WT. Chạy P5 trên split vòng tròn = đánh giá một đóng góp
    dương bằng đúng thứ kỷ luật mà bài này đi tố cáo người khác vi phạm.

Tất định: `make_splits` chạy cùng `seed` cho ra cùng fold (tests/test_data.py). Không
có bước ngẫu nhiên nào ngoài `seed` của config.
"""

from __future__ import annotations

import sys
from pathlib import Path

from _common import (  # noqa: E402  (_common đặt ROOT lên sys.path)
    ROOT,
    data_root,
    data_source,
    load_config,
    parse_args,
)

from src.data.brats_loader import build_cohort, make_splits  # noqa: E402
from src.manifest import write_manifest  # noqa: E402


def _abs(p, default: str) -> Path:
    path = Path(p or default)
    return path if path.is_absolute() else ROOT / path


def main() -> int:
    _p = parse_args(__doc__.splitlines()[0])
    _p.add_argument(
        "--seed",
        type=int,
        default=0,
        help="seed của StratifiedKFold (mặc định 0 — split là artefact TẤT ĐỊNH, "
             "không phải một trong 5 seed thí nghiệm)",
    )
    args = _p.parse_args()
    cfg, cfg_hash = load_config(args.config)

    src = data_source(cfg)
    if src != "brats":
        print(f"[BỎ QUA] data.source = {src!r} (không phải 'brats') — split cấp bệnh "
              f"nhân chỉ áp dụng cho BraTS. Smoke synthetic không cần file này.")
        return 0

    d = cfg.get("data") or {}
    root = data_root(cfg)
    if root is None:
        print("[LỖI] Không thấy dữ liệu BraTS. Kiểm tra data.root_kaggle / "
              "data.root_local trong config (Kaggle: /kaggle/input/...).", file=sys.stderr)
        return 1

    cohort_csv = _abs(d.get("cohort_csv"), "data/splits/brats_cohort.csv")
    splits_dir = _abs(args.output or d.get("splits_dir"), "data/splits")
    splits_dir.mkdir(parents=True, exist_ok=True)
    n_folds = int(cfg.get("n_folds", 5))

    if cohort_csv.exists() and args.resume:
        print(f"[RESUME] Đã có {cohort_csv} — bỏ qua build_cohort.")
    else:
        cohort_csv.parent.mkdir(parents=True, exist_ok=True)
        print(f"Quét cohort từ {root} … (369 ca — vài phút, đọc NIfTI)")
        df = build_cohort(root, cohort_csv)
        print(f"  → {cohort_csv}  (n = {len(df)} ca)")

    print(f"Chia {n_folds} fold ở CẤP BỆNH NHÂN, phân tầng grade × tertile thể tích WT "
          f"(A3), seed = {args.seed} …")
    make_splits(cohort_csv, splits_dir, n_folds=n_folds, seed=args.seed)

    folds = sorted(splits_dir.glob("fold_*.json"))
    for f in folds:
        print("  →", f.relative_to(ROOT) if f.is_relative_to(ROOT) else f)
    if not folds:
        print("[LỖI] make_splits không sinh fold_*.json.", file=sys.stderr)
        return 1

    write_manifest(
        splits_dir / "run-manifest.json",
        config_hash=cfg_hash,
        seeds=[args.seed],
        dataset_version=str(d.get("version", "")),
        extra={
            "script": "scripts/make_splits.py",
            "n_folds": n_folds,
            "split_unit": "patient",
            "stratified_by": "grade x WT-volume tertile (A3)",
            "cohort_csv": str(cohort_csv),
            "output_paths": [str(cohort_csv), *[str(f) for f in folds]],
        },
    )

    print(f"\nXONG. {len(folds)} fold + cohort đã sẵn sàng ⇒ run_ceiling.py sẽ dùng "
          f"split này thay vì rơi về chia vòng tròn.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""BraTS 2020 loader + cohort/split builder — MODULE A (data).

Reproducibility & integrity decisions baked in here (see docs/preregistration.md §6):

* **A3 — per-image intensity normalisation.** Each 2D slice is clipped to its own
  [1, 99] percentiles and rescaled to uint8 [0, 255]. We NEVER use dataset-wide
  statistics (mean/std/percentiles over the cohort) — that would be a preprocessing
  leak. FLAIR and T1ce are normalised independently.
* **A3 — patient-level splits.** `make_splits` partitions at the *patient* level
  (never the slice level), stratified by grade (HGG/LGG) × WT-volume tertile, so that
  paired Wilcoxon / Friedman / TOST across patients are well defined and no patient
  leaks between train and test.
* **A8 — use ALL 369 training cases**, not a 150-case subset. The oracle runs on the
  histogram (~ms/image), so there is no compute reason to sacrifice sample size.

Public interface (imported by other modules):
    Slice                      dataclass carrying one axial slice + masks
    load_brats_slice(dir)      -> Slice
    build_cohort(root, csv)    -> pandas.DataFrame
    make_splits(csv, out_dir)  -> writes data/splits/fold_{0..4}.json
    iter_cohort(csv, root)     -> Iterator[Slice]

`nibabel` is imported lazily so this module can be imported (and the synthetic /
split / LGG code paths exercised) even where nibabel is not installed. Install with
`pip install nibabel` before touching real BraTS volumes.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterator, List, Optional

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------- #
# Named constants (no magic numbers scattered through the code)
# --------------------------------------------------------------------------- #
NUM_LEVELS: int = 256          # L = 256 gray levels; images are uint8 [0, 255]
CLIP_LOW_PCT: float = 1.0      # A3: per-image lower percentile for intensity clip
CLIP_HIGH_PCT: float = 99.0    # A3: per-image upper percentile for intensity clip
AXIAL_AXIS: int = 2            # BraTS volumes are (H, W, Z); axial index runs on axis 2

# BraTS segmentation label convention (labels 1, 2, 4; label 3 unused)
SEG_LABEL_NECROTIC: int = 1    # NCR/NET
SEG_LABEL_EDEMA: int = 2       # ED
SEG_LABEL_ENHANCING: int = 4   # ET

N_FOLDS_DEFAULT: int = 5
N_WT_TERTILES: int = 3         # A3 stratification: WT-volume tertiles

_BRATS_PATIENT_GLOB = "BraTS20_Training_*"


# --------------------------------------------------------------------------- #
# Data container (shared interface contract)
# --------------------------------------------------------------------------- #
@dataclass
class Slice:
    """One axial slice of a case, with the masks other modules need.

    Attributes
    ----------
    patient_id : str    e.g. "BraTS20_Training_042"
    flair      : np.ndarray  uint8 (H, W), per-image normalised FLAIR
    wt_mask    : np.ndarray  bool  (H, W), Whole Tumor = seg > 0
    t1ce       : np.ndarray  uint8 (H, W), per-image normalised T1ce
    et_mask    : np.ndarray  bool  (H, W), Enhancing Tumor = seg == 4
    grade      : str    "HGG" | "LGG" | "UNK"
    slice_idx  : int    axial index chosen (max-WT-area rule)
    """

    patient_id: str
    flair: np.ndarray
    wt_mask: np.ndarray
    t1ce: np.ndarray
    et_mask: np.ndarray
    grade: str
    slice_idx: int


# --------------------------------------------------------------------------- #
# Intensity normalisation (A3 — per image, no dataset statistics)
# --------------------------------------------------------------------------- #
def normalize_to_uint8(img: np.ndarray) -> np.ndarray:
    """Clip to this image's own [1, 99] percentiles, rescale to uint8 [0, 255].

    A3: percentiles are computed *within this single image* only. Using cohort-wide
    statistics would be a preprocessing leak, so it is deliberately not done here.
    """
    img = np.asarray(img, dtype=np.float64)
    lo = np.percentile(img, CLIP_LOW_PCT)
    hi = np.percentile(img, CLIP_HIGH_PCT)
    if hi <= lo:
        # Degenerate (near-constant) slice: return all zeros rather than divide by 0.
        return np.zeros(img.shape, dtype=np.uint8)
    clipped = np.clip(img, lo, hi)
    scaled = (clipped - lo) / (hi - lo)  # -> [0, 1]
    return np.round(scaled * (NUM_LEVELS - 1)).astype(np.uint8)


# --------------------------------------------------------------------------- #
# Filesystem helpers
# --------------------------------------------------------------------------- #
def _find_modality(patient_dir: Path, suffix: str) -> Path:
    """Locate a modality file (e.g. '_flair') allowing .nii and .nii.gz."""
    for pat in (f"*{suffix}.nii", f"*{suffix}.nii.gz"):
        hits = sorted(patient_dir.glob(pat))
        if hits:
            return hits[0]
    raise FileNotFoundError(f"No '*{suffix}.nii[.gz]' under {patient_dir}")


def _load_volume(path: Path) -> np.ndarray:
    """Load a NIfTI volume as a numpy array (nibabel imported lazily)."""
    try:
        import nibabel as nib
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise ImportError(
            "nibabel is required to read BraTS .nii volumes. "
            "Install it with `pip install nibabel`."
        ) from exc
    return np.asanyarray(nib.load(str(path)).dataobj)


def _pick_max_wt_slice(seg: np.ndarray) -> int:
    """Fixed, pre-declared slice rule: the axial slice with the largest WT area.

    WT = seg > 0. Ties resolved by lowest index (np.argmax). The SAME index is used
    for FLAIR and T1ce so their histograms and the masks are spatially consistent.
    """
    wt = seg > 0
    per_slice_area = wt.sum(axis=tuple(a for a in range(seg.ndim) if a != AXIAL_AXIS))
    return int(np.argmax(per_slice_area))


# --------------------------------------------------------------------------- #
# name_mapping.csv (grade lookup)
# --------------------------------------------------------------------------- #
def _find_name_mapping(start: Path) -> Optional[Path]:
    """Search `start` and its parents for name_mapping.csv."""
    for base in [start, *start.parents]:
        cand = base / "name_mapping.csv"
        if cand.exists():
            return cand
    return None


def _load_grade_map(name_mapping_csv: Optional[Path]) -> Dict[str, str]:
    """Return {patient_id -> 'HGG'|'LGG'} from BraTS name_mapping.csv, or {}."""
    if name_mapping_csv is None or not name_mapping_csv.exists():
        return {}
    df = pd.read_csv(name_mapping_csv)
    id_col = next(
        (c for c in df.columns if "BraTS_2020_subject_ID" in c or "subject_ID" in c),
        None,
    )
    grade_col = next((c for c in df.columns if c.strip().lower() == "grade"), None)
    if id_col is None or grade_col is None:
        return {}
    return {
        str(r[id_col]).strip(): str(r[grade_col]).strip()
        for _, r in df.iterrows()
        if isinstance(r[id_col], str) or not pd.isna(r[id_col])
    }


# --------------------------------------------------------------------------- #
# Public: single-case loader
# --------------------------------------------------------------------------- #
def load_brats_slice(patient_dir: Path, normalize: bool = True) -> Slice:
    """Load the max-WT axial slice of one BraTS case as a :class:`Slice`.

    Masks (A8 label convention):
        WT = seg > 0 ; ET = seg == 4 ; (TC = (seg==1)|(seg==4), not stored but trivial).
    Intensities are per-image normalised (A3) when `normalize=True`.
    """
    patient_dir = Path(patient_dir)
    patient_id = patient_dir.name

    flair_vol = _load_volume(_find_modality(patient_dir, "_flair"))
    t1ce_vol = _load_volume(_find_modality(patient_dir, "_t1ce"))
    seg_vol = _load_volume(_find_modality(patient_dir, "_seg"))

    z = _pick_max_wt_slice(seg_vol)
    flair2d = np.take(flair_vol, z, axis=AXIAL_AXIS)
    t1ce2d = np.take(t1ce_vol, z, axis=AXIAL_AXIS)
    seg2d = np.take(seg_vol, z, axis=AXIAL_AXIS)

    wt_mask = seg2d > 0
    et_mask = seg2d == SEG_LABEL_ENHANCING

    if normalize:
        flair2d = normalize_to_uint8(flair2d)
        t1ce2d = normalize_to_uint8(t1ce2d)
    else:
        flair2d = flair2d.astype(np.uint8)
        t1ce2d = t1ce2d.astype(np.uint8)

    grade = _load_grade_map(_find_name_mapping(patient_dir)).get(patient_id, "UNK")

    return Slice(
        patient_id=patient_id,
        flair=flair2d,
        wt_mask=np.ascontiguousarray(wt_mask, dtype=bool),
        t1ce=t1ce2d,
        et_mask=np.ascontiguousarray(et_mask, dtype=bool),
        grade=grade,
        slice_idx=z,
    )


# --------------------------------------------------------------------------- #
# Public: cohort builder (A8 — scan ALL 369 cases)
# --------------------------------------------------------------------------- #
def _sha256_of(arr: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(arr).tobytes()).hexdigest()


def build_cohort(brats_root: Path, out_csv: Path) -> pd.DataFrame:
    """Scan the whole training directory and write the cohort manifest CSV.

    A8: every case under `brats_root` matching ``BraTS20_Training_*`` is included
    (target n = 369). Columns: patient_id, slice_idx, wt_area, grade, sha256, split.
    `sha256` is the hash of the chosen FLAIR slice (post-normalisation) for provenance;
    `split` is left empty here — it is filled by :func:`make_splits`.
    """
    brats_root = Path(brats_root)
    out_csv = Path(out_csv)
    patient_dirs = sorted(
        d for d in brats_root.glob(_BRATS_PATIENT_GLOB) if d.is_dir()
    )
    if not patient_dirs:
        raise FileNotFoundError(
            f"No '{_BRATS_PATIENT_GLOB}' directories under {brats_root}"
        )

    grade_map = _load_grade_map(_find_name_mapping(brats_root))

    rows: List[dict] = []
    for pdir in patient_dirs:
        try:
            s = load_brats_slice(pdir, normalize=True)
        except FileNotFoundError:
            # Skip incomplete cases but do not silently fabricate anything.
            continue
        rows.append(
            {
                "patient_id": s.patient_id,
                "slice_idx": s.slice_idx,
                "wt_area": int(s.wt_mask.sum()),
                "grade": grade_map.get(s.patient_id, s.grade),
                "sha256": _sha256_of(s.flair),
                "split": "",
            }
        )

    df = pd.DataFrame(
        rows, columns=["patient_id", "slice_idx", "wt_area", "grade", "sha256", "split"]
    )
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    return df


# --------------------------------------------------------------------------- #
# Public: patient-level stratified 5-fold splits (A3)
# --------------------------------------------------------------------------- #
def _wt_tertile_labels(wt_area: np.ndarray) -> np.ndarray:
    """Assign each patient a WT-volume tertile index in {0, 1, 2} (rank-based)."""
    order = np.argsort(np.argsort(wt_area, kind="stable"), kind="stable")
    n = len(wt_area)
    # Rank-based tertiles are robust to ties and identical values.
    return np.minimum((order * N_WT_TERTILES) // max(n, 1), N_WT_TERTILES - 1)


def make_splits(
    cohort_csv: Path, out_dir: Path, n_folds: int = N_FOLDS_DEFAULT, seed: int = 0
) -> None:
    """Write patient-level stratified CV splits to ``data/splits/fold_{i}.json``.

    A3: the split unit is the PATIENT. Stratification is by grade (HGG/LGG) ×
    WT-volume tertile. Each fold has one held-out *test* fold; the rest is train,
    from which one inner fold is peeled off as *val* (for early stopping / epoch
    selection). Deterministic given `seed`. Also writes a copy of the cohort with a
    `split` column (the outer test-fold index per patient) to
    ``out_dir/brats_cohort.csv``.
    """
    from sklearn.model_selection import StratifiedKFold

    cohort_csv = Path(cohort_csv)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(cohort_csv)
    df = df.sort_values("patient_id", kind="stable").reset_index(drop=True)
    patient_ids = df["patient_id"].astype(str).to_numpy()

    grade = df["grade"].astype(str).fillna("UNK").to_numpy()
    tertile = _wt_tertile_labels(df["wt_area"].to_numpy())
    strata = np.array([f"{g}_{t}" for g, t in zip(grade, tertile)])

    # Collapse any stratum too small for n_folds into a shared bucket so
    # StratifiedKFold stays valid without dropping patients.
    counts = pd.Series(strata).value_counts()
    rare = set(counts[counts < n_folds].index)
    strata = np.array(["_RARE_" if s in rare else s for s in strata])

    outer = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=seed)
    idx_all = np.arange(len(df))

    # Record the outer test-fold index per patient for the cohort CSV.
    test_fold_of = np.full(len(df), -1, dtype=int)

    for fold, (train_val_idx, test_idx) in enumerate(outer.split(idx_all, strata)):
        test_fold_of[test_idx] = fold

        # Peel one inner fold off train_val as validation (stratified, deterministic).
        tv_strata = strata[train_val_idx]
        inner = StratifiedKFold(
            n_splits=n_folds, shuffle=True, random_state=seed + 1000 + fold
        )
        inner_train_rel, inner_val_rel = next(inner.split(train_val_idx, tv_strata))
        train_idx = train_val_idx[inner_train_rel]
        val_idx = train_val_idx[inner_val_rel]

        payload = {
            "fold": fold,
            "seed": seed,
            "n_folds": n_folds,
            "split_unit": "patient",
            "stratify": "grade x WT-volume-tertile",
            "train": sorted(patient_ids[train_idx].tolist()),
            "val": sorted(patient_ids[val_idx].tolist()),
            "test": sorted(patient_ids[test_idx].tolist()),
        }
        with open(out_dir / f"fold_{fold}.json", "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)

    df_out = df.copy()
    df_out["split"] = test_fold_of
    df_out.to_csv(out_dir / "brats_cohort.csv", index=False)


# --------------------------------------------------------------------------- #
# Public: cohort iterator
# --------------------------------------------------------------------------- #
def iter_cohort(cohort_csv: Path, brats_root: Path) -> Iterator[Slice]:
    """Yield a :class:`Slice` for every patient listed in the cohort CSV."""
    brats_root = Path(brats_root)
    df = pd.read_csv(cohort_csv)
    for pid in df["patient_id"].astype(str):
        yield load_brats_slice(brats_root / pid, normalize=True)

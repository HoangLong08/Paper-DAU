"""BraTS slice loader. Designed for Kaggle BraTS2020/2023 dataset layout.

We work with 2D axial slices from FLAIR modality (best contrast for tumor).
Ground-truth labels are merged into a binary tumor / not-tumor mask for
segmentation metrics (Dice, IoU) — multilevel thresholding cannot produce
the 3-class BraTS labels reliably, so we evaluate on the union.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Tuple
import numpy as np


@dataclass
class Slice:
    image_id: str           # patient + slice index
    image: np.ndarray       # 2D uint8 [H, W]
    mask: np.ndarray        # 2D uint8 {0,1} (whole tumor)
    modality: str = "FLAIR"


def _normalize_uint8(arr: np.ndarray) -> np.ndarray:
    a = arr.astype(np.float32)
    lo, hi = np.percentile(a[a > 0], [1, 99]) if (a > 0).any() else (0.0, 1.0)
    if hi <= lo:
        hi = lo + 1.0
    a = np.clip((a - lo) / (hi - lo), 0, 1) * 255.0
    return a.astype(np.uint8)


def load_nifti(path: str) -> np.ndarray:
    import nibabel as nib
    return nib.load(path).get_fdata()


def iter_brats_patients(root: str) -> Iterable[Path]:
    root = Path(root)
    for p in sorted(root.glob("*/")):
        if p.is_dir():
            yield p


def _find_modality(folder: Path, key: str) -> Path | None:
    candidates = list(folder.glob(f"*{key}*.nii*")) + list(folder.glob(f"*{key.lower()}*.nii*"))
    return candidates[0] if candidates else None


def load_slices_from_patient(folder: Path, modality: str = "flair",
                              min_tumor_pixels: int = 200,
                              max_slices_per_patient: int = 3) -> List[Slice]:
    """Picks the most informative axial slices (largest tumor area)."""
    flair_p = _find_modality(folder, modality)
    seg_p = _find_modality(folder, "seg")
    if flair_p is None or seg_p is None:
        return []
    vol = load_nifti(str(flair_p))
    seg = load_nifti(str(seg_p))
    if vol.shape != seg.shape:
        return []
    # axial = last axis in standard BraTS orientation
    areas = (seg > 0).sum(axis=(0, 1))
    valid = np.where(areas >= min_tumor_pixels)[0]
    if valid.size == 0:
        return []
    # pick top-k by area
    top = valid[np.argsort(-areas[valid])[:max_slices_per_patient]]
    out: List[Slice] = []
    pid = folder.name
    for z in top:
        img = _normalize_uint8(vol[..., z])
        msk = (seg[..., z] > 0).astype(np.uint8)
        out.append(Slice(image_id=f"{pid}_z{int(z)}", image=img, mask=msk, modality=modality.upper()))
    return out


def load_brats_dataset(root: str, n_patients: int = 20,
                        modality: str = "flair",
                        max_slices_per_patient: int = 3) -> List[Slice]:
    out: List[Slice] = []
    for folder in iter_brats_patients(root):
        slices = load_slices_from_patient(folder, modality, max_slices_per_patient=max_slices_per_patient)
        if not slices:
            continue
        out.extend(slices)
        if len({s.image_id.rsplit("_z", 1)[0] for s in out}) >= n_patients:
            break
    return out

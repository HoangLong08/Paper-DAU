"""LGG (Buda et al.) TIFF loader — E7 external-validation candidate.

===================================  A8 WARNINGS  ============================
1. **CHANNEL TRAP.** The Kaggle `mateuszbuda/lgg-mri-segmentation` images are
   **3-channel TIFFs** with channels ordered
   ``(0) pre-contrast, (1) FLAIR, (2) post-contrast``.
   The FLAIR band this study needs is the **MIDDLE channel, index 1** — NOT a
   grayscale mean and NOT channel 0. Taking the wrong channel corrupts the
   histogram and therefore every Kapur/DP threshold downstream. This is unit-tested
   in ``tests/test_lgg_loader.py``.

2. **COHORT-OVERLAP / MISREPRESENTATION RISK.** Buda et al. = 110 TCGA-LGG patients
   (TCIA). BraTS 2020 already absorbed **108 TCGA-LGG cases from the same
   collection**. So "different site / different scanner" may in fact be the **same
   patients**. Before ANY use of the phrase "external validation":
     - load BraTS ``name_mapping.csv`` (it maps BraTS_2020 IDs ↔ TCGA IDs),
     - cross-reference and **report the overlap count as a number**, then choose:
         (a) drop the overlapping patients; or
         (b) keep them but call it *"annotation/preprocessing replication on an
             overlapping cohort"*; or
         (c) do external validation along the TASK axis instead (tune on WT/FLAIR,
             test on ET/T1ce) — cheapest and strongest (aligns with A2).
   Calling it external validation when the patients overlap, and a BraTS reviewer
   catches it, reads as MISREPRESENTATION, not a design flaw.

3. **E7 = zero-shot.** Do NOT re-tune the 1-parameter threshold on LGG; re-tuning
   would stop it being external validation (preregistration §6/A3).
=============================================================================

This module only *reads* the data into the shared :class:`Slice` container. The
overlap check above is a human/analysis step and is deliberately NOT auto-bypassed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterator, List

import numpy as np

from src.data.brats_loader import Slice, normalize_to_uint8

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #
FLAIR_CHANNEL_INDEX: int = 1        # A8: FLAIR is the MIDDLE band of the 3-ch TIFF
PRECONTRAST_CHANNEL_INDEX: int = 0
POSTCONTRAST_CHANNEL_INDEX: int = 2  # used as a T1ce analogue for interface parity
MASK_SUFFIX: str = "_mask"
_EXPECTED_CHANNELS: int = 3


def _read_tiff(path: Path) -> np.ndarray:
    """Read a TIFF as an (H, W[, C]) array (tifffile preferred, PIL fallback)."""
    try:
        import tifffile

        return np.asarray(tifffile.imread(str(path)))
    except ImportError:  # pragma: no cover - fallback path
        from PIL import Image

        return np.asarray(Image.open(str(path)))


def _flair_channel(img: np.ndarray) -> np.ndarray:
    """Extract the FLAIR band (index 1) from a 3-channel LGG TIFF.

    A8 channel trap: we assert the array is 3-channel and select index 1 explicitly.
    A single-channel image is passed through (already FLAIR-only), but a 2-channel or
    other unexpected shape raises rather than silently guessing.
    """
    if img.ndim == 2:
        return img
    if img.ndim == 3 and img.shape[-1] == _EXPECTED_CHANNELS:
        return img[..., FLAIR_CHANNEL_INDEX]
    if img.ndim == 3 and img.shape[0] == _EXPECTED_CHANNELS:
        # channel-first layout
        return img[FLAIR_CHANNEL_INDEX, ...]
    raise ValueError(
        f"Unexpected LGG TIFF shape {img.shape}; expected 3-channel "
        f"(pre-contrast/FLAIR/post-contrast)."
    )


def _channel(img: np.ndarray, index: int) -> np.ndarray:
    if img.ndim == 2:
        return img
    if img.ndim == 3 and img.shape[-1] == _EXPECTED_CHANNELS:
        return img[..., index]
    if img.ndim == 3 and img.shape[0] == _EXPECTED_CHANNELS:
        return img[index, ...]
    raise ValueError(f"Unexpected LGG TIFF shape {img.shape}")


def load_lgg_slice(image_path: Path, normalize: bool = True) -> Slice:
    """Load one LGG TIFF (+ its ``*_mask.tif``) as a :class:`Slice`.

    - ``flair``   = FLAIR band (channel 1), per-image normalised (A3) to uint8.
    - ``wt_mask`` = tumour mask (from ``<name>_mask.tif``), boolean.
    - ``t1ce``    = post-contrast band (channel 2) for interface parity; LGG has no
      ET label, so ``et_mask`` is all-False. grade is fixed "LGG".
    """
    image_path = Path(image_path)
    img = _read_tiff(image_path)

    flair2d = _flair_channel(img)
    t1ce2d = _channel(img, POSTCONTRAST_CHANNEL_INDEX)

    mask_path = image_path.with_name(
        image_path.stem + MASK_SUFFIX + image_path.suffix
    )
    if mask_path.exists():
        mask_raw = _read_tiff(mask_path)
        if mask_raw.ndim == 3:
            mask_raw = mask_raw[..., 0] if mask_raw.shape[-1] <= 4 else mask_raw[0]
        wt_mask = np.asarray(mask_raw) > 0
    else:
        wt_mask = np.zeros(flair2d.shape[:2], dtype=bool)

    if normalize:
        flair2d = normalize_to_uint8(flair2d)
        t1ce2d = normalize_to_uint8(t1ce2d)
    else:
        flair2d = flair2d.astype(np.uint8)
        t1ce2d = t1ce2d.astype(np.uint8)

    return Slice(
        patient_id=image_path.stem,
        flair=flair2d,
        wt_mask=np.ascontiguousarray(wt_mask, dtype=bool),
        t1ce=t1ce2d,
        et_mask=np.zeros(flair2d.shape[:2], dtype=bool),
        grade="LGG",
        slice_idx=0,
    )


def iter_lgg(lgg_root: Path, tumor_only: bool = True) -> Iterator[Slice]:
    """Yield :class:`Slice` for LGG TIFFs under `lgg_root` (skips ``*_mask.tif``).

    With ``tumor_only=True`` only slices whose mask has >0 tumour pixels are yielded
    (the natural unit for a Dice-based external check). Remember: E7 is zero-shot —
    do not re-tune anything on these slices.
    """
    lgg_root = Path(lgg_root)
    paths: List[Path] = sorted(
        p
        for p in lgg_root.rglob("*.tif")
        if MASK_SUFFIX not in p.stem
    )
    for p in paths:
        s = load_lgg_slice(p)
        if tumor_only and not s.wt_mask.any():
            continue
        yield s

"""Synthetic brain phantom — smoke-test fixture only.

INTEGRITY: numbers produced from these phantoms are [PLACEHOLDER] and must NEVER
appear in the paper as results (CLAUDE.md §2 IRON RULE 1/3). The phantom exists so
that every downstream module can run end-to-end (< 60 s) before real BraTS is mounted.

The phantom mimics a skull-stripped slice: ~65% zero-intensity background, a few
concentric regions of increasing intensity (edema/tissue analogues), and one bright
"tumour" blob that defines the WT/ET masks.
"""

from __future__ import annotations

import numpy as np

from src.data.brats_loader import NUM_LEVELS, Slice

# --------------------------------------------------------------------------- #
# Phantom geometry / intensity constants
# --------------------------------------------------------------------------- #
PHANTOM_SIZE: int = 240              # match BraTS in-plane size (H = W = 240)
BRAIN_RADIUS_FRAC: float = 0.33      # brain disk radius -> ~65% zero background
TUMOR_RADIUS_FRAC: float = 0.09      # tumour blob radius
TUMOR_OFFSET_FRAC: float = 0.12      # tumour centre offset from image centre (stays in brain)
_MAXV: int = NUM_LEVELS - 1          # 255


def _disk(size: int, cy: float, cx: float, r: float) -> np.ndarray:
    yy, xx = np.ogrid[:size, :size]
    return (yy - cy) ** 2 + (xx - cx) ** 2 <= r ** 2


def synthetic_slice(seed: int) -> Slice:
    """Return a valid :class:`Slice` phantom deterministic in `seed`.

    Guarantees: uint8 images in [0, 255], boolean masks, WT area > 0, ~65% zero
    background (skull-stripped look). ET is a bright sub-core of WT.
    """
    rng = np.random.default_rng(seed)
    s = PHANTOM_SIZE
    c = s / 2.0

    brain = _disk(s, c, c, BRAIN_RADIUS_FRAC * s)

    # FLAIR: graded tissue intensities inside the brain, zero outside.
    flair = np.zeros((s, s), dtype=np.float64)
    flair[brain] = 55.0
    flair[_disk(s, c, c, 0.24 * s)] = 95.0     # inner tissue ring
    flair[_disk(s, c, c, 0.14 * s)] = 135.0    # deeper structure

    # Tumour blob (offset from centre): bright on FLAIR (edema-like WT).
    ty = c + TUMOR_OFFSET_FRAC * s
    tx = c - TUMOR_OFFSET_FRAC * s
    wt = _disk(s, ty, tx, TUMOR_RADIUS_FRAC * s)
    flair[wt] = 220.0

    # Enhancing core: a small bright sub-region of WT (analogue of ET, seg==4).
    et = _disk(s, ty, tx, 0.045 * s)
    flair[wt & ~et] = 200.0

    # T1ce: darker overall, but the enhancing core is the brightest thing present.
    t1ce = np.zeros((s, s), dtype=np.float64)
    t1ce[brain] = 40.0
    t1ce[_disk(s, c, c, 0.24 * s)] = 70.0
    t1ce[wt] = 110.0
    t1ce[et] = 235.0

    # Mild texture so histograms are non-degenerate (does not cross class boundaries).
    flair[brain] += rng.normal(0.0, 3.0, size=flair.shape)[brain]
    t1ce[brain] += rng.normal(0.0, 3.0, size=t1ce.shape)[brain]

    flair_u8 = np.clip(np.round(flair), 0, _MAXV).astype(np.uint8)
    t1ce_u8 = np.clip(np.round(t1ce), 0, _MAXV).astype(np.uint8)

    return Slice(
        patient_id=f"SYNTH_{seed:03d}",
        flair=flair_u8,
        wt_mask=np.ascontiguousarray(wt, dtype=bool),
        t1ce=t1ce_u8,
        et_mask=np.ascontiguousarray(et, dtype=bool),
        grade="UNK",
        slice_idx=0,
    )

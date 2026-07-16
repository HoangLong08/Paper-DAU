"""MODULE A (data) — BraTS 2020 loading, cohort building, patient-level splits.

Re-exports the shared data interface so callers may do either
``from src.data import load_brats_slice`` or
``from src.data.brats_loader import load_brats_slice``.
"""

from src.data.brats_loader import (
    Slice,
    build_cohort,
    iter_cohort,
    load_brats_slice,
    make_splits,
    normalize_to_uint8,
)
from src.data.lgg_loader import iter_lgg, load_lgg_slice
from src.data.synthetic import synthetic_slice

__all__ = [
    "Slice",
    "load_brats_slice",
    "build_cohort",
    "make_splits",
    "iter_cohort",
    "normalize_to_uint8",
    "synthetic_slice",
    "load_lgg_slice",
    "iter_lgg",
]

"""Smoke tests for MODULE A: synthetic phantom validity + split integrity (A3).

- ``synthetic_slice`` must return a well-formed Slice (uint8 images, bool masks, WT>0).
- ``normalize_to_uint8`` must be per-image and in range (A3).
- ``make_splits`` must not leak patients between train/val/test (A3).
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

from src.data.brats_loader import Slice, make_splits, normalize_to_uint8
from src.data.synthetic import synthetic_slice


# --------------------------------------------------------------------------- #
# Synthetic phantom
# --------------------------------------------------------------------------- #
def test_synthetic_slice_is_valid():
    s = synthetic_slice(0)
    assert isinstance(s, Slice)
    assert s.flair.dtype == np.uint8 and s.t1ce.dtype == np.uint8
    assert s.flair.max() <= 255 and s.flair.min() >= 0
    assert s.wt_mask.dtype == bool and s.et_mask.dtype == bool
    assert s.wt_mask.shape == s.flair.shape == s.t1ce.shape == s.et_mask.shape
    assert s.wt_mask.sum() > 0, "WT area must be > 0"
    # ET is a sub-core of WT.
    assert np.all(s.et_mask <= s.wt_mask)
    # Skull-stripped look: majority of pixels are zero background.
    assert (s.flair == 0).mean() > 0.5


def test_synthetic_slice_deterministic():
    a = synthetic_slice(7)
    b = synthetic_slice(7)
    assert np.array_equal(a.flair, b.flair)
    assert np.array_equal(a.wt_mask, b.wt_mask)


# --------------------------------------------------------------------------- #
# Per-image normalisation (A3)
# --------------------------------------------------------------------------- #
def test_normalize_is_per_image_and_uint8():
    rng = np.random.default_rng(0)
    img = rng.normal(500, 120, size=(64, 64))
    out = normalize_to_uint8(img)
    assert out.dtype == np.uint8
    assert out.min() >= 0 and out.max() <= 255
    # A near-constant image must not blow up (guard against divide-by-zero).
    flat = normalize_to_uint8(np.full((8, 8), 42.0))
    assert flat.dtype == np.uint8 and flat.max() == 0


# --------------------------------------------------------------------------- #
# Patient-level split integrity (A3)
# --------------------------------------------------------------------------- #
def _fake_cohort(tmp_path, n=120, seed=0):
    rng = np.random.default_rng(seed)
    grades = rng.choice(["HGG", "LGG"], size=n, p=[0.75, 0.25])
    rows = []
    for i in range(n):
        rows.append(
            {
                "patient_id": f"BraTS20_Training_{i:03d}",
                "slice_idx": int(rng.integers(40, 120)),
                "wt_area": int(rng.integers(200, 8000)),
                "grade": grades[i],
                "sha256": f"{i:064x}",
                "split": "",
            }
        )
    csv = tmp_path / "cohort.csv"
    pd.DataFrame(rows).to_csv(csv, index=False)
    return csv, n


def test_make_splits_no_patient_leakage(tmp_path):
    csv, n = _fake_cohort(tmp_path)
    out_dir = tmp_path / "splits"
    make_splits(csv, out_dir, n_folds=5, seed=0)

    all_test = []
    for fold in range(5):
        payload = json.loads((out_dir / f"fold_{fold}.json").read_text())
        train = set(payload["train"])
        val = set(payload["val"])
        test = set(payload["test"])
        # No overlap within a fold.
        assert train.isdisjoint(test), f"fold {fold}: train/test overlap"
        assert train.isdisjoint(val), f"fold {fold}: train/val overlap"
        assert val.isdisjoint(test), f"fold {fold}: val/test overlap"
        # The three partitions cover every patient exactly once.
        assert len(train | val | test) == n
        all_test.append(test)

    # Every patient is in exactly one test fold (a valid CV partition).
    union = set().union(*all_test)
    assert len(union) == n
    assert sum(len(t) for t in all_test) == n, "test folds must be disjoint"


def test_make_splits_deterministic(tmp_path):
    csv, _ = _fake_cohort(tmp_path)
    a, b = tmp_path / "a", tmp_path / "b"
    make_splits(csv, a, n_folds=5, seed=0)
    make_splits(csv, b, n_folds=5, seed=0)
    for fold in range(5):
        assert (a / f"fold_{fold}.json").read_text() == (
            b / f"fold_{fold}.json"
        ).read_text()


def test_make_splits_writes_cohort_csv(tmp_path):
    csv, n = _fake_cohort(tmp_path)
    out_dir = tmp_path / "splits"
    make_splits(csv, out_dir, n_folds=5, seed=0)
    cohort = pd.read_csv(out_dir / "brats_cohort.csv")
    assert len(cohort) == n
    # Every patient assigned to a real outer test fold in [0, 4].
    assert cohort["split"].between(0, 4).all()

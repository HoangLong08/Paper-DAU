"""A8 channel-trap unit test for the LGG loader.

Builds a synthetic 3-channel TIFF where the FLAIR band (index 1) is intentionally
distinct from the pre-/post-contrast bands, then asserts the loader returns exactly
that band. Guards against the "grabbed the wrong channel" bug that would silently
corrupt every downstream histogram/threshold.
"""

from __future__ import annotations

import numpy as np
import pytest

tifffile = pytest.importorskip("tifffile")

from src.data.lgg_loader import FLAIR_CHANNEL_INDEX, load_lgg_slice


def _make_lgg_tiff(tmp_path):
    h, w = 32, 32
    pre = np.full((h, w), 10, dtype=np.uint8)     # channel 0
    flair = np.full((h, w), 200, dtype=np.uint8)  # channel 1 — the one we want
    post = np.full((h, w), 60, dtype=np.uint8)    # channel 2
    # Make FLAIR spatially unmistakable: a bright square only in the FLAIR band.
    flair[8:24, 8:24] = 255
    img = np.stack([pre, flair, post], axis=-1)   # (H, W, 3)

    img_path = tmp_path / "case_1.tif"
    tifffile.imwrite(str(img_path), img)

    mask = np.zeros((h, w), dtype=np.uint8)
    mask[10:20, 10:20] = 255
    tifffile.imwrite(str(tmp_path / "case_1_mask.tif"), mask)
    return img_path, flair, mask


def test_flair_channel_index_is_one():
    assert FLAIR_CHANNEL_INDEX == 1, "A8: FLAIR must be the middle channel"


def test_loader_picks_flair_channel(tmp_path):
    img_path, flair_expected, _ = _make_lgg_tiff(tmp_path)
    s = load_lgg_slice(img_path, normalize=False)

    # The returned FLAIR must equal channel 1, NOT channel 0 or 2.
    assert s.flair.shape == flair_expected.shape
    assert np.array_equal(s.flair, flair_expected), (
        "A8 channel trap: loader did not return the FLAIR band (index 1)"
    )
    # Sanity: it must differ from the pre-contrast band it could be confused with.
    assert not np.all(s.flair == 10)


def test_loader_reads_mask_and_metadata(tmp_path):
    img_path, _, mask = _make_lgg_tiff(tmp_path)
    s = load_lgg_slice(img_path, normalize=True)

    assert s.wt_mask.dtype == bool
    assert s.wt_mask.sum() == int((mask > 0).sum()) > 0
    assert s.flair.dtype == np.uint8
    assert s.et_mask.dtype == bool and not s.et_mask.any()  # LGG has no ET label
    assert s.grade == "LGG"


def test_channelfirst_layout_also_works(tmp_path):
    # Some TIFF writers store (C, H, W); loader must still pick FLAIR.
    h, w = 16, 16
    img = np.stack(
        [np.full((h, w), 10, np.uint8),
         np.full((h, w), 200, np.uint8),
         np.full((h, w), 60, np.uint8)],
        axis=0,
    )  # (3, H, W)
    p = tmp_path / "cf_1.tif"
    tifffile.imwrite(str(p), img)
    s = load_lgg_slice(p, normalize=False)
    assert np.all(s.flair == 200)

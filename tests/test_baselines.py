"""Tests for MODULE F — classical baselines, 2D U-Net shape, and run manifest.

Skips gracefully where an optional dependency (skimage / sklearn / torch) is not
installed, so the suite still runs on a minimal environment.
"""

from __future__ import annotations

import json

import numpy as np
import pytest


# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #
def _two_region_image(size: int = 64, bg: int = 30, fg: int = 210):
    """Dark background with a bright central square — a cleanly separable
    two-region image so every class-A baseline should recover the bright square."""
    img = np.full((size, size), bg, dtype=np.uint8)
    a, b = size // 4, 3 * size // 4
    img[a:b, a:b] = fg
    true_fg = np.zeros((size, size), dtype=bool)
    true_fg[a:b, a:b] = True
    return img, true_fg


def _iou(a: np.ndarray, b: np.ndarray) -> float:
    inter = np.logical_and(a, b).sum()
    union = np.logical_or(a, b).sum()
    return float(inter / union) if union else 1.0


# --------------------------------------------------------------------------- #
# Classical baselines: bool mask, right shape, recovers the bright region
# --------------------------------------------------------------------------- #
def test_threshold_baselines_recover_bright_region():
    pytest.importorskip("skimage")
    from src.baselines.classical import (
        otsu_threshold, li_threshold, triangle_threshold,
    )

    img, true_fg = _two_region_image()
    for fn in (otsu_threshold, li_threshold, triangle_threshold):
        mask = fn(img)
        assert mask.dtype == np.bool_, f"{fn.__name__} must return bool"
        assert mask.shape == img.shape, f"{fn.__name__} shape mismatch"
        assert _iou(mask, true_fg) > 0.9, f"{fn.__name__} failed to recover region"


def test_clustering_baselines_recover_bright_region():
    pytest.importorskip("sklearn")
    from src.baselines.classical import kmeans_segment, gmm_segment

    img, true_fg = _two_region_image()
    for fn in (kmeans_segment, gmm_segment):
        mask = fn(img)
        assert mask.dtype == np.bool_, f"{fn.__name__} must return bool"
        assert mask.shape == img.shape, f"{fn.__name__} shape mismatch"
        assert _iou(mask, true_fg) > 0.9, f"{fn.__name__} failed to recover region"


def test_constant_image_returns_empty_mask():
    pytest.importorskip("skimage")
    pytest.importorskip("sklearn")
    from src.baselines.classical import (
        otsu_threshold, li_threshold, triangle_threshold,
        kmeans_segment, gmm_segment,
    )

    const = np.full((32, 32), 100, dtype=np.uint8)
    for fn in (otsu_threshold, li_threshold, triangle_threshold,
               kmeans_segment, gmm_segment):
        mask = fn(const)
        assert mask.dtype == np.bool_
        assert mask.shape == const.shape
        assert not mask.any(), f"{fn.__name__} should be all-background on constant"


def test_clustering_is_deterministic():
    """A class-A method must be a pure function of its image (pinned RNG)."""
    pytest.importorskip("sklearn")
    from src.baselines.classical import kmeans_segment, gmm_segment

    img, _ = _two_region_image()
    assert np.array_equal(kmeans_segment(img), kmeans_segment(img))
    assert np.array_equal(gmm_segment(img), gmm_segment(img))


# --------------------------------------------------------------------------- #
# 2D U-Net: forward-pass shape (1,1,H,W) -> (1,1,H,W)
# --------------------------------------------------------------------------- #
def test_unet_forward_shape():
    torch = pytest.importorskip("torch")
    from src.baselines.unet2d import UNet2D

    model = UNet2D(base_channels=8).eval()
    x = torch.randn(1, 1, 64, 64)
    with torch.no_grad():
        y = model(x)
    assert y.shape == (1, 1, 64, 64)
    assert float(y.min()) >= 0.0 and float(y.max()) <= 1.0, "output must be sigmoid"


def test_unet_smoke_train_and_infer(tmp_path):
    """CPU-smoke: nested-CV plumbing (train -> checkpoint -> infer) runs with no
    GPU and no BraTS mounted. Structural only — not a paper number."""
    torch = pytest.importorskip("torch")  # noqa: F841
    from dataclasses import dataclass

    from src.baselines.unet2d import train_unet_cv, infer_unet

    cfg = {
        "smoke": True,
        "epochs": 2,
        "batch_size": 4,
        "base_channels": 8,
        "out_dir": str(tmp_path / "ckpts"),
        "smoke_image_size": 64,
    }
    ckpt = train_unet_cv(
        cohort_csv=None, splits_dir=None, brats_root=None,
        fold=0, seed=0, cfg=cfg,
    )
    assert ckpt and __import__("os").path.exists(ckpt)

    @dataclass
    class _FakeSlice:
        flair: np.ndarray

    sl = _FakeSlice(flair=np.random.randint(0, 256, (72, 80), dtype=np.uint8))
    mask = infer_unet(ckpt, sl)
    assert mask.dtype == np.bool_
    assert mask.shape == (72, 80), "infer must return the slice's native shape"


# --------------------------------------------------------------------------- #
# Manifest
# --------------------------------------------------------------------------- #
def test_write_manifest_has_required_keys(tmp_path):
    from src.manifest import write_manifest

    out = tmp_path / "run-manifest.json"
    result = write_manifest(
        out,
        config_hash="abc123",
        seeds=[0, 1, 2, 3, 4],
        dataset_version="brats20-v1",
        extra={"experiment": "unet_cv", "output_paths": ["results/unet/m.csv"]},
    )

    assert out.exists()
    with open(out, "r", encoding="utf-8") as fh:
        loaded = json.load(fh)

    required = {
        "git_commit", "config_hash", "seeds", "dataset_version",
        "lib_versions", "timestamp", "output_paths", "extra",
    }
    assert required.issubset(loaded.keys())
    assert loaded == result
    assert loaded["seeds"] == [0, 1, 2, 3, 4]
    assert loaded["config_hash"] == "abc123"
    assert loaded["dataset_version"] == "brats20-v1"
    assert loaded["output_paths"] == ["results/unet/m.csv"]  # promoted from extra
    assert isinstance(loaded["lib_versions"], dict)
    assert "numpy" in loaded["lib_versions"], "numpy version must be recorded"
    assert "experiment" in loaded["extra"]


def test_write_manifest_seed_scalar_and_defaults(tmp_path):
    from src.manifest import write_manifest

    out = tmp_path / "m.json"
    result = write_manifest(out, seeds=7)
    assert result["seeds"] == [7]
    # output_paths defaults to the manifest path itself when not supplied.
    assert result["output_paths"] == [str(out)]

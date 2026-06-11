"""Threshold segmentation and synthetic fallback dataset (for sanity tests)."""
from __future__ import annotations
import numpy as np


def apply_thresholds(image: np.ndarray, thresholds: np.ndarray) -> np.ndarray:
    """Label each pixel by which class it falls into."""
    t = np.sort(np.unique(np.asarray(thresholds, dtype=np.int64)))
    return np.digitize(image, t).astype(np.uint8)


def segmentation_to_binary(seg: np.ndarray, tumor_class: int | None = None) -> np.ndarray:
    """Convert multi-class threshold output to a binary tumor mask.

    Heuristic: the brightest class on FLAIR corresponds to the tumor (hyper-
    intense lesion). If `tumor_class` is provided, use that label.
    """
    if tumor_class is None:
        tumor_class = int(seg.max())
    return (seg == tumor_class).astype(np.uint8)


def synthetic_brain_image(rng: np.random.Generator, size: int = 192) -> tuple[np.ndarray, np.ndarray]:
    """Fallback synthetic test image with a bright 'tumor' blob — for unit tests
    when BraTS data isn't available."""
    H = W = size
    img = np.zeros((H, W), dtype=np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    # gray brain blob
    cx, cy = W // 2, H // 2
    brain = ((xx - cx) ** 2 / (W * 0.45) ** 2 + (yy - cy) ** 2 / (H * 0.45) ** 2) < 1
    img[brain] = 120 + rng.normal(0, 8, size=brain.sum())
    # tumor: bright eccentric blob
    tx, ty = cx + rng.integers(-20, 20), cy + rng.integers(-20, 20)
    tumor = ((xx - tx) ** 2 + (yy - ty) ** 2) < (size * 0.07) ** 2
    img[tumor] = 220 + rng.normal(0, 5, size=tumor.sum())
    img = np.clip(img, 0, 255).astype(np.uint8)
    mask = tumor.astype(np.uint8)
    return img, mask

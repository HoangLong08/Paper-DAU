"""Kapur's entropy objective for multilevel thresholding.

Reference: Kapur, Sahoo, Wong (1985), "A new method for gray-level
picture thresholding using the entropy of the histogram."
"""
from __future__ import annotations
import numpy as np


def compute_histogram(image: np.ndarray, levels: int = 256) -> np.ndarray:
    img = image.astype(np.int64).ravel()
    hist = np.bincount(img, minlength=levels).astype(np.float64)
    total = hist.sum()
    if total <= 0:
        return np.zeros(levels, dtype=np.float64)
    return hist / total


def kapur_entropy(prob: np.ndarray, thresholds: np.ndarray) -> float:
    """Kapur entropy for a probability histogram and a sorted threshold vector.

    `thresholds` are integer cut points in [1, L-1]. They partition the
    intensity range into k+1 classes.
    """
    L = prob.shape[0]
    t = np.asarray(thresholds, dtype=np.int64)
    t = np.clip(t, 1, L - 1)
    t = np.sort(np.unique(t))
    if t.size == 0:
        return -np.inf
    edges = np.concatenate(([0], t, [L]))
    eps = 1e-12
    total_entropy = 0.0
    for i in range(edges.size - 1):
        lo, hi = edges[i], edges[i + 1]
        p_class = prob[lo:hi]
        w = p_class.sum()
        if w <= eps:
            continue
        # normalize within the class
        p_norm = p_class / w
        p_norm = p_norm[p_norm > eps]
        if p_norm.size == 0:
            continue
        h = -np.sum(p_norm * np.log(p_norm))
        total_entropy += h
    return float(total_entropy)


def make_kapur_objective(image: np.ndarray, levels: int = 256):
    """Returns a callable f(x) -> entropy where x is a length-k threshold vector
    of real numbers (will be rounded and clipped). Maximization.
    """
    prob = compute_histogram(image, levels=levels)

    def f(x: np.ndarray) -> float:
        if x.ndim == 1:
            t = np.round(x).astype(np.int64)
            return kapur_entropy(prob, t)
        # batch evaluation
        out = np.empty(x.shape[0], dtype=np.float64)
        for i in range(x.shape[0]):
            out[i] = kapur_entropy(prob, np.round(x[i]).astype(np.int64))
        return out

    return f, prob

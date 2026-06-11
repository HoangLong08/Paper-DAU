"""Otsu between-class variance for multilevel thresholding (ablation)."""
from __future__ import annotations
import numpy as np
from .kapur import compute_histogram


def otsu_variance(prob: np.ndarray, thresholds: np.ndarray) -> float:
    L = prob.shape[0]
    t = np.asarray(thresholds, dtype=np.int64)
    t = np.clip(t, 1, L - 1)
    t = np.sort(np.unique(t))
    if t.size == 0:
        return -np.inf
    edges = np.concatenate(([0], t, [L]))
    intensities = np.arange(L, dtype=np.float64)
    global_mean = float(np.sum(intensities * prob))
    var_b = 0.0
    for i in range(edges.size - 1):
        lo, hi = edges[i], edges[i + 1]
        w = prob[lo:hi].sum()
        if w <= 1e-12:
            continue
        mu = float(np.sum(intensities[lo:hi] * prob[lo:hi]) / w)
        var_b += w * (mu - global_mean) ** 2
    return float(var_b)


def make_otsu_objective(image: np.ndarray, levels: int = 256):
    prob = compute_histogram(image, levels=levels)

    def f(x: np.ndarray) -> float:
        if x.ndim == 1:
            return otsu_variance(prob, np.round(x).astype(np.int64))
        out = np.empty(x.shape[0], dtype=np.float64)
        for i in range(x.shape[0]):
            out[i] = otsu_variance(prob, np.round(x[i]).astype(np.int64))
        return out

    return f, prob

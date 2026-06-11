"""Tsallis entropy multilevel-thresholding objective.

Reference: de Albuquerque et al. (2004), "Image thresholding using Tsallis
entropy." The non-extensive parameter q controls landscape smoothness: q=1
recovers Shannon, q > 1 sharpens around the histogram mode (harder, more
multimodal optimization landscape).
"""
from __future__ import annotations
import numpy as np
from .kapur import compute_histogram


def tsallis_entropy(prob: np.ndarray, thresholds: np.ndarray, q: float = 0.5) -> float:
    L = prob.shape[0]
    t = np.asarray(thresholds, dtype=np.int64)
    t = np.clip(t, 1, L - 1)
    t = np.sort(np.unique(t))
    if t.size == 0:
        return -np.inf
    edges = np.concatenate(([0], t, [L]))
    eps = 1e-12
    weights = []
    s_per_class = []
    for i in range(edges.size - 1):
        lo, hi = edges[i], edges[i + 1]
        p_class = prob[lo:hi]
        w = p_class.sum()
        if w <= eps:
            weights.append(0.0); s_per_class.append(0.0); continue
        p_norm = p_class / w
        s_q = (1.0 - np.sum(p_norm ** q)) / (q - 1.0 + eps) if abs(q - 1.0) > 1e-9 \
              else -np.sum(p_norm * np.log(p_norm + eps))
        weights.append(float(w))
        s_per_class.append(float(s_q))
    # Non-extensive composition rule for q != 1
    if abs(q - 1.0) > 1e-9:
        total = sum(s_per_class) + (1.0 - q) * sum(
            s_per_class[i] * s_per_class[j]
            for i in range(len(s_per_class)) for j in range(i + 1, len(s_per_class))
        )
    else:
        total = sum(s_per_class)
    return float(total)


def make_tsallis_objective(image: np.ndarray, q: float = 0.5, levels: int = 256):
    prob = compute_histogram(image, levels=levels)

    def f(x: np.ndarray) -> float:
        if x.ndim == 1:
            return tsallis_entropy(prob, np.round(x).astype(np.int64), q=q)
        out = np.empty(x.shape[0], dtype=np.float64)
        for i in range(x.shape[0]):
            out[i] = tsallis_entropy(prob, np.round(x[i]).astype(np.int64), q=q)
        return out

    return f, prob

"""Shared helpers: Levy flight, opposition-based learning, clipping."""
from __future__ import annotations
import numpy as np
from scipy.special import gamma


def levy_flight(dim: int, beta: float = 1.5, rng: np.random.Generator | None = None) -> np.ndarray:
    """Mantegna's algorithm for Levy flight step."""
    rng = rng or np.random.default_rng()
    sigma_u = (gamma(1 + beta) * np.sin(np.pi * beta / 2) /
               (gamma((1 + beta) / 2) * beta * 2 ** ((beta - 1) / 2))) ** (1 / beta)
    u = rng.normal(0.0, sigma_u, size=dim)
    v = rng.normal(0.0, 1.0, size=dim)
    return u / (np.abs(v) ** (1 / beta) + 1e-12)


def opposition(x: np.ndarray, lb: np.ndarray, ub: np.ndarray) -> np.ndarray:
    """Opposition-based learning: x' = lb + ub - x."""
    return lb + ub - x


def clip_repair(x: np.ndarray, lb: np.ndarray, ub: np.ndarray) -> np.ndarray:
    return np.minimum(np.maximum(x, lb), ub)


def sanitize_thresholds(x: np.ndarray, lb: np.ndarray, ub: np.ndarray) -> np.ndarray:
    """Clip, round, sort, and de-duplicate threshold vectors (preserves shape).

    If duplicates collapse, re-spread within bounds.
    """
    x = clip_repair(x, lb, ub)
    if x.ndim == 1:
        return _sanitize_one(x, lb, ub)
    out = np.empty_like(x)
    for i in range(x.shape[0]):
        out[i] = _sanitize_one(x[i], lb, ub)
    return out


def _sanitize_one(v: np.ndarray, lb: np.ndarray, ub: np.ndarray) -> np.ndarray:
    v_int = np.round(v).astype(np.int64)
    v_int = np.sort(v_int)
    # de-duplicate by pushing up
    for i in range(1, v_int.size):
        if v_int[i] <= v_int[i - 1]:
            v_int[i] = v_int[i - 1] + 1
    # if exceeded upper bound, push down from the top
    if v_int[-1] > ub[-1]:
        v_int[-1] = int(ub[-1])
        for i in range(v_int.size - 2, -1, -1):
            if v_int[i] >= v_int[i + 1]:
                v_int[i] = v_int[i + 1] - 1
    v_int = np.clip(v_int, lb.astype(np.int64), ub.astype(np.int64))
    return v_int.astype(np.float64)

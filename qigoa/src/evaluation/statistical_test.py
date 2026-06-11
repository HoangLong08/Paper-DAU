"""Wilcoxon signed-rank (pairwise) and Friedman + Holm post-hoc.

We test QIGOA vs each baseline on the per-image best fitness vector across runs.
"""
from __future__ import annotations
from typing import Dict, List, Tuple
import numpy as np
from scipy import stats


def wilcoxon_vs_baselines(qigoa_scores: np.ndarray,
                           baseline_scores: Dict[str, np.ndarray],
                           alternative: str = "greater") -> Dict[str, dict]:
    """Pairwise Wilcoxon test of QIGOA vs each baseline.

    `qigoa_scores` and each `baseline_scores[name]` must be 1-D arrays of equal
    length (same images / same runs aligned).
    """
    out = {}
    for name, b in baseline_scores.items():
        diff = qigoa_scores - b
        if np.all(diff == 0):
            out[name] = {"statistic": 0.0, "p_value": 1.0, "significant": False, "win": 0, "tie": len(diff), "lose": 0}
            continue
        try:
            stat, p = stats.wilcoxon(qigoa_scores, b, alternative=alternative, zero_method="zsplit")
        except ValueError:
            stat, p = float("nan"), 1.0
        win = int((diff > 0).sum())
        lose = int((diff < 0).sum())
        tie = int((diff == 0).sum())
        out[name] = {"statistic": float(stat), "p_value": float(p),
                     "significant": bool(p < 0.05), "win": win, "tie": tie, "lose": lose}
    return out


def friedman_with_holm(all_scores: Dict[str, np.ndarray]) -> Tuple[float, float, Dict[str, float]]:
    """Friedman omnibus test + Holm-corrected pairwise comparison to the best
    mean-rank method.

    Returns (statistic, p_value, holm_p_values_by_algo).
    """
    names = list(all_scores.keys())
    matrix = np.stack([all_scores[n] for n in names], axis=1)  # (n_problems, n_algos)
    stat, p = stats.friedmanchisquare(*matrix.T)
    # ranks per problem (1 = best, larger fitness -> lower rank)
    ranks = np.apply_along_axis(lambda row: stats.rankdata(-row, method="average"), 1, matrix)
    mean_ranks = ranks.mean(axis=0)
    control = int(np.argmin(mean_ranks))
    n_problems, n_algos = matrix.shape
    se = np.sqrt(n_algos * (n_algos + 1) / (6.0 * n_problems))
    z = {names[i]: (mean_ranks[i] - mean_ranks[control]) / se for i in range(n_algos)}
    raw_p = {n: 2 * (1 - stats.norm.cdf(abs(z_val))) for n, z_val in z.items()}
    # Holm correction
    pairs = sorted([(n, raw_p[n]) for n in names if n != names[control]], key=lambda kv: kv[1])
    holm = {names[control]: 0.0}
    m = len(pairs)
    for i, (n, p_val) in enumerate(pairs):
        holm[n] = min(1.0, (m - i) * p_val)
    return float(stat), float(p), holm

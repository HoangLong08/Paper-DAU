"""Standard Grasshopper Optimization Algorithm (Saremi, Mirjalili, Lewis 2017)."""
from __future__ import annotations
import time
import numpy as np
from .base import BaseOptimizer, OptResult
from ..utils.helpers import sanitize_thresholds


def _s(r: np.ndarray, f: float = 0.5, l: float = 1.5) -> np.ndarray:
    """Social-force function."""
    return f * np.exp(-r / l) - np.exp(-r)


class GOA(BaseOptimizer):
    name = "GOA"

    def __init__(self, dim, lb, ub, pop_size=30, max_iter=100, seed=None,
                 c_max: float = 1.0, c_min: float = 1e-5,
                 f_intensity: float = 0.5, l_scale: float = 1.5):
        super().__init__(dim, lb, ub, pop_size, max_iter, seed)
        self.c_max, self.c_min = c_max, c_min
        self.f_intensity, self.l_scale = f_intensity, l_scale

    def _social(self, pop: np.ndarray, c: float) -> np.ndarray:
        N, dim = pop.shape
        new = np.zeros_like(pop)
        ub_lb = (self.ub - self.lb) / 2.0
        for i in range(N):
            diff = pop - pop[i]  # (N, dim)
            dist = np.linalg.norm(diff, axis=1, keepdims=True) + 1e-12
            unit = diff / dist
            s_vals = _s(dist.squeeze(-1), self.f_intensity, self.l_scale)
            # exclude self
            s_vals[i] = 0.0
            contrib = (c * ub_lb[None, :] * s_vals[:, None] * unit).sum(axis=0)
            new[i] = c * contrib
        return new

    def optimize(self, fitness):
        t0 = time.perf_counter()
        pop = self._init_pop()
        fit = self._evaluate(fitness, pop)
        g_idx = int(np.argmax(fit))
        target = pop[g_idx].copy()
        target_f = float(fit[g_idx])
        history = [target_f]

        for t in range(self.max_iter):
            c = self.c_max - (t + 1) * (self.c_max - self.c_min) / self.max_iter
            social = self._social(pop, c)
            new_pop = social + target  # eq. (3) in the paper
            pop = sanitize_thresholds(new_pop, self.lb, self.ub)
            fit = self._evaluate(fitness, pop)
            j = int(np.argmax(fit))
            if fit[j] > target_f:
                target_f = float(fit[j])
                target = pop[j].copy()
            history.append(target_f)

        return OptResult(best_x=target, best_fitness=target_f, history=history,
                         runtime_s=time.perf_counter() - t0,
                         n_evals=self.n_evals, name=self.name)

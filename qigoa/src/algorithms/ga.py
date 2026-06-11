"""Real-coded Genetic Algorithm with tournament selection, BLX-alpha crossover,
Gaussian mutation. Maximization."""
from __future__ import annotations
import time
import numpy as np
from .base import BaseOptimizer, OptResult
from ..utils.helpers import sanitize_thresholds


class GA(BaseOptimizer):
    name = "GA"

    def __init__(self, dim, lb, ub, pop_size=30, max_iter=100, seed=None,
                 cx_prob: float = 0.9, mut_prob: float = 0.1,
                 tournament_k: int = 3, blx_alpha: float = 0.5):
        super().__init__(dim, lb, ub, pop_size, max_iter, seed)
        self.cx_prob = cx_prob
        self.mut_prob = mut_prob
        self.tournament_k = tournament_k
        self.blx_alpha = blx_alpha

    def _tournament(self, fit: np.ndarray) -> int:
        idx = self.rng.integers(0, self.pop_size, size=self.tournament_k)
        return int(idx[np.argmax(fit[idx])])

    def _blx(self, p1: np.ndarray, p2: np.ndarray) -> np.ndarray:
        lo = np.minimum(p1, p2)
        hi = np.maximum(p1, p2)
        d = hi - lo
        child = self.rng.uniform(lo - self.blx_alpha * d, hi + self.blx_alpha * d)
        return child

    def optimize(self, fitness):
        t0 = time.perf_counter()
        pop = self._init_pop()
        fit = self._evaluate(fitness, pop)
        best_idx = int(np.argmax(fit))
        best_x = pop[best_idx].copy()
        best_f = float(fit[best_idx])
        history = [best_f]

        span = self.ub - self.lb
        for _ in range(self.max_iter):
            new_pop = np.empty_like(pop)
            new_pop[0] = best_x  # elitism
            for i in range(1, self.pop_size):
                i1 = self._tournament(fit)
                i2 = self._tournament(fit)
                if self.rng.random() < self.cx_prob:
                    child = self._blx(pop[i1], pop[i2])
                else:
                    child = pop[i1].copy()
                # Gaussian mutation
                mask = self.rng.random(self.dim) < self.mut_prob
                if mask.any():
                    child[mask] += self.rng.normal(0.0, 0.1 * span[mask])
                new_pop[i] = child
            pop = sanitize_thresholds(new_pop, self.lb, self.ub)
            fit = self._evaluate(fitness, pop)
            j = int(np.argmax(fit))
            if fit[j] > best_f:
                best_f = float(fit[j])
                best_x = pop[j].copy()
            history.append(best_f)

        return OptResult(best_x=best_x, best_fitness=best_f, history=history,
                         runtime_s=time.perf_counter() - t0,
                         n_evals=self.n_evals, name=self.name)

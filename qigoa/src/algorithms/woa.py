"""Whale Optimization Algorithm (Mirjalili & Lewis 2016)."""
from __future__ import annotations
import time
import numpy as np
from .base import BaseOptimizer, OptResult
from ..utils.helpers import sanitize_thresholds


class WOA(BaseOptimizer):
    name = "WOA"

    def __init__(self, dim, lb, ub, pop_size=30, max_iter=100, seed=None, b: float = 1.0):
        super().__init__(dim, lb, ub, pop_size, max_iter, seed)
        self.b = b

    def optimize(self, fitness):
        t0 = time.perf_counter()
        pop = self._init_pop()
        fit = self._evaluate(fitness, pop)
        g_idx = int(np.argmax(fit))
        best = pop[g_idx].copy()
        best_f = float(fit[g_idx])
        history = [best_f]

        for t in range(self.max_iter):
            a = 2.0 - 2.0 * t / max(1, self.max_iter - 1)
            for i in range(self.pop_size):
                r1, r2 = self.rng.random(), self.rng.random()
                A = 2 * a * r1 - a
                C = 2 * r2
                p = self.rng.random()
                if p < 0.5:
                    if abs(A) < 1:
                        D = np.abs(C * best - pop[i])
                        pop[i] = best - A * D
                    else:
                        rand_idx = self.rng.integers(0, self.pop_size)
                        x_rand = pop[rand_idx]
                        D = np.abs(C * x_rand - pop[i])
                        pop[i] = x_rand - A * D
                else:
                    l = self.rng.uniform(-1, 1)
                    D = np.abs(best - pop[i])
                    pop[i] = D * np.exp(self.b * l) * np.cos(2 * np.pi * l) + best
            pop = sanitize_thresholds(pop, self.lb, self.ub)
            fit = self._evaluate(fitness, pop)
            j = int(np.argmax(fit))
            if fit[j] > best_f:
                best_f = float(fit[j])
                best = pop[j].copy()
            history.append(best_f)

        return OptResult(best_x=best, best_fitness=best_f, history=history,
                         runtime_s=time.perf_counter() - t0,
                         n_evals=self.n_evals, name=self.name)

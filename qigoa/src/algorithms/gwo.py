"""Grey Wolf Optimizer (Mirjalili, Mirjalili, Lewis 2014)."""
from __future__ import annotations
import time
import numpy as np
from .base import BaseOptimizer, OptResult
from ..utils.helpers import sanitize_thresholds


class GWO(BaseOptimizer):
    name = "GWO"

    def optimize(self, fitness):
        t0 = time.perf_counter()
        pop = self._init_pop()
        fit = self._evaluate(fitness, pop)
        order = np.argsort(-fit)
        alpha, beta, delta = pop[order[0]].copy(), pop[order[1]].copy(), pop[order[2]].copy()
        f_a, f_b, f_d = float(fit[order[0]]), float(fit[order[1]]), float(fit[order[2]])
        history = [f_a]

        for t in range(self.max_iter):
            a = 2.0 - 2.0 * t / max(1, self.max_iter - 1)
            for i in range(self.pop_size):
                x = pop[i]
                A1, A2, A3 = (2 * a * self.rng.random(self.dim) - a for _ in range(3))
                C1, C2, C3 = (2 * self.rng.random(self.dim) for _ in range(3))
                X1 = alpha - A1 * np.abs(C1 * alpha - x)
                X2 = beta - A2 * np.abs(C2 * beta - x)
                X3 = delta - A3 * np.abs(C3 * delta - x)
                pop[i] = (X1 + X2 + X3) / 3.0
            pop = sanitize_thresholds(pop, self.lb, self.ub)
            fit = self._evaluate(fitness, pop)
            for i in range(self.pop_size):
                v = fit[i]
                if v > f_a:
                    f_d, delta = f_b, beta.copy()
                    f_b, beta = f_a, alpha.copy()
                    f_a, alpha = float(v), pop[i].copy()
                elif v > f_b:
                    f_d, delta = f_b, beta.copy()
                    f_b, beta = float(v), pop[i].copy()
                elif v > f_d:
                    f_d, delta = float(v), pop[i].copy()
            history.append(f_a)

        return OptResult(best_x=alpha, best_fitness=f_a, history=history,
                         runtime_s=time.perf_counter() - t0,
                         n_evals=self.n_evals, name=self.name)

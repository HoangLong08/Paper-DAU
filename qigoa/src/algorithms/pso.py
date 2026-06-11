"""Standard PSO with inertia weight (Shi & Eberhart 1998). Maximization."""
from __future__ import annotations
import time
import numpy as np
from .base import BaseOptimizer, OptResult
from ..utils.helpers import sanitize_thresholds


class PSO(BaseOptimizer):
    name = "PSO"

    def __init__(self, dim, lb, ub, pop_size=30, max_iter=100, seed=None,
                 w_max: float = 0.9, w_min: float = 0.4,
                 c1: float = 2.0, c2: float = 2.0, v_clip: float = 0.2):
        super().__init__(dim, lb, ub, pop_size, max_iter, seed)
        self.w_max, self.w_min = w_max, w_min
        self.c1, self.c2 = c1, c2
        self.v_clip = v_clip

    def optimize(self, fitness):
        t0 = time.perf_counter()
        pop = self._init_pop()
        fit = self._evaluate(fitness, pop)
        pbest = pop.copy()
        pbest_f = fit.copy()
        g_idx = int(np.argmax(pbest_f))
        gbest = pbest[g_idx].copy()
        gbest_f = float(pbest_f[g_idx])
        history = [gbest_f]

        span = self.ub - self.lb
        v_max = self.v_clip * span
        vel = self.rng.uniform(-v_max, v_max, size=pop.shape)

        for t in range(self.max_iter):
            w = self.w_max - (self.w_max - self.w_min) * (t / max(1, self.max_iter - 1))
            r1 = self.rng.random(pop.shape)
            r2 = self.rng.random(pop.shape)
            vel = w * vel + self.c1 * r1 * (pbest - pop) + self.c2 * r2 * (gbest - pop)
            vel = np.clip(vel, -v_max, v_max)
            pop = sanitize_thresholds(pop + vel, self.lb, self.ub)
            fit = self._evaluate(fitness, pop)
            improved = fit > pbest_f
            pbest[improved] = pop[improved]
            pbest_f[improved] = fit[improved]
            g_idx = int(np.argmax(pbest_f))
            if pbest_f[g_idx] > gbest_f:
                gbest_f = float(pbest_f[g_idx])
                gbest = pbest[g_idx].copy()
            history.append(gbest_f)

        return OptResult(best_x=gbest, best_fitness=gbest_f, history=history,
                         runtime_s=time.perf_counter() - t0,
                         n_evals=self.n_evals, name=self.name)

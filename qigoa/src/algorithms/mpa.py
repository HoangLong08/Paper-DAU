"""Marine Predators Algorithm (Faramarzi, Heidarinejad, Mirjalili, Gandomi 2020).

Three-phase strategy with Brownian/Levy steps. Maximization here.
"""
from __future__ import annotations
import time
import numpy as np
from .base import BaseOptimizer, OptResult
from ..utils.helpers import sanitize_thresholds, levy_flight


class MPA(BaseOptimizer):
    name = "MPA"

    def __init__(self, dim, lb, ub, pop_size=30, max_iter=100, seed=None,
                 P: float = 0.5, FADs: float = 0.2):
        super().__init__(dim, lb, ub, pop_size, max_iter, seed)
        self.P = P
        self.FADs = FADs

    def _brownian(self, shape):
        return self.rng.normal(0.0, 1.0, size=shape)

    def _levy(self, shape):
        out = np.empty(shape)
        for i in range(shape[0]):
            out[i] = levy_flight(shape[1], rng=self.rng)
        return out

    def optimize(self, fitness):
        t0 = time.perf_counter()
        prey = self._init_pop()
        fit = self._evaluate(fitness, prey)
        g_idx = int(np.argmax(fit))
        elite_row = prey[g_idx].copy()
        best = elite_row.copy()
        best_f = float(fit[g_idx])
        history = [best_f]

        for t in range(self.max_iter):
            elite = np.tile(elite_row, (self.pop_size, 1))
            CF = (1 - t / self.max_iter) ** (2 * t / self.max_iter)
            R = self.rng.random(prey.shape)
            if t < self.max_iter / 3:
                RB = self._brownian(prey.shape)
                stepsize = RB * (elite - RB * prey)
                prey = prey + self.P * R * stepsize
            elif t < 2 * self.max_iter / 3:
                RL = self._levy(prey.shape)
                RB = self._brownian(prey.shape)
                # first half: levy
                half = self.pop_size // 2
                stepsize_l = RL[:half] * (elite[:half] - RL[:half] * prey[:half])
                prey[:half] = prey[:half] + self.P * R[:half] * stepsize_l
                stepsize_b = RB[half:] * (RB[half:] * elite[half:] - prey[half:])
                prey[half:] = elite[half:] + self.P * CF * stepsize_b
            else:
                RL = self._levy(prey.shape)
                stepsize = RL * (RL * elite - prey)
                prey = elite + self.P * CF * stepsize

            # FADs effect
            if self.rng.random() < self.FADs:
                U = (self.rng.random(prey.shape) < self.FADs).astype(np.float64)
                prey = prey + CF * ((self.lb + self.rng.random(prey.shape) * (self.ub - self.lb)) * U)
            else:
                r = self.rng.random()
                idx1 = self.rng.permutation(self.pop_size)
                idx2 = self.rng.permutation(self.pop_size)
                prey = prey + (self.FADs * (1 - r) + r) * (prey[idx1] - prey[idx2])

            prey = sanitize_thresholds(prey, self.lb, self.ub)
            fit = self._evaluate(fitness, prey)
            j = int(np.argmax(fit))
            if fit[j] > best_f:
                best_f = float(fit[j])
                best = prey[j].copy()
                elite_row = best.copy()
            history.append(best_f)

        return OptResult(best_x=best, best_fitness=best_f, history=history,
                         runtime_s=time.perf_counter() - t0,
                         n_evals=self.n_evals, name=self.name)

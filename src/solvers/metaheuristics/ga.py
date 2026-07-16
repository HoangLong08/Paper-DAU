"""Genetic Algorithm (GA) — real-coded, cho multilevel thresholding.

Baseline metaheuristic kinh điển. Chọn lọc giải đấu (tournament) + lai ghép số
học (arithmetic crossover) + đột biến Gauss + elitism. Mọi lượt chấm điểm đi qua
``self.evaluate`` ⇒ đếm vào NFE. Vòng thế hệ không tự kết thúc; dừng bởi
``BudgetExhausted``.

Tham chiếu: Holland, *Adaptation in Natural and Artificial Systems* (1975);
real-coded GA — Deb & Agrawal, *Complex Systems* 9 (1995).
"""

from __future__ import annotations

import numpy as np

from src.solvers.metaheuristics.base import Optimizer

DEFAULT_POP = 30
DEFAULT_MUT_RATE = 0.1          # xác suất đột biến mỗi con
DEFAULT_MUT_FRAC = 0.10         # độ lệch Gauss = frac × span
DEFAULT_TOURNAMENT = 3          # cỡ giải đấu


class GA(Optimizer):
    name = "GA"

    def _tournament(self, pop: np.ndarray, fit: np.ndarray, tsize: int) -> np.ndarray:
        idx = self.rng.integers(0, len(pop), size=tsize)
        winner = idx[int(np.argmax(fit[idx]))]
        return pop[winner].copy()

    def _search(self) -> None:
        n = int(self.hp.get("pop", DEFAULT_POP))
        mut_rate = float(self.hp.get("mut_rate", DEFAULT_MUT_RATE))
        mut_scale = float(self.hp.get("mut_frac", DEFAULT_MUT_FRAC)) * self.span
        tsize = int(self.hp.get("tournament", DEFAULT_TOURNAMENT))

        pop = self._rand_pop(n)
        fit = np.array([self.evaluate(pop[i]) for i in range(n)])

        while True:                        # dừng duy nhất bởi BudgetExhausted
            elite = pop[int(np.argmax(fit))].copy()
            children = [elite]             # elitism: giữ cá thể tốt nhất
            while len(children) < n:
                p1 = self._tournament(pop, fit, tsize)
                p2 = self._tournament(pop, fit, tsize)
                a = self.rng.random()
                child = a * p1 + (1.0 - a) * p2
                if self.rng.random() < mut_rate:
                    child = child + self.rng.normal(0.0, mut_scale, size=self.k)
                children.append(self._clip(child))

            new_pop = np.asarray(children[:n])
            new_fit = np.array([self.evaluate(new_pop[i]) for i in range(n)])
            pop, fit = new_pop, new_fit

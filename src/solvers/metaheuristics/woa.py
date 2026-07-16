"""Whale Optimization Algorithm (WOA) — cho multilevel thresholding.

Bao vây con mồi (encircling) + tấn công lưới bong bóng theo đường xoắn ốc
(bubble-net spiral) + tìm kiếm ngẫu nhiên khi ``|A| >= 1``. Hệ số ``a`` giảm
2→0 theo tiến độ tiêu ngân sách. Mọi lượt chấm điểm qua ``self.evaluate``. Dừng
bởi ``BudgetExhausted``.

Tham chiếu: Mirjalili & Lewis, *Advances in Engineering Software* 95:51–67
(2016), ``10.1016/j.advengsoft.2016.01.008``.
"""

from __future__ import annotations

import numpy as np

from src.solvers.metaheuristics.base import Optimizer

DEFAULT_POP = 30
A_START = 2.0                  # hệ số bao vây (2→0)
SPIRAL_B = 1.0                 # hằng hình dạng xoắn ốc logarit


class WOA(Optimizer):
    name = "WOA"

    def _search(self) -> None:
        n = int(self.hp.get("pop", DEFAULT_POP))
        b = float(self.hp.get("spiral_b", SPIRAL_B))

        pop = self._rand_pop(n)
        fit = np.array([self.evaluate(pop[i]) for i in range(n)])

        while True:                        # dừng duy nhất bởi BudgetExhausted
            progress = self._used / self.budget
            a = A_START * (1.0 - progress)          # 2 → 0
            best = self._incumbent_vec()

            for i in range(n):
                r1 = self.rng.random(self.k)
                r2 = self.rng.random(self.k)
                A = 2.0 * a * r1 - a
                C = 2.0 * r2
                p = self.rng.random()

                if p < 0.5:
                    if np.mean(np.abs(A)) < 1.0:
                        # bao vây con mồi tốt nhất
                        D = np.abs(C * best - pop[i])
                        cand = best - A * D
                    else:
                        # khám phá: bám một cá thể ngẫu nhiên
                        rand_i = int(self.rng.integers(0, n))
                        D = np.abs(C * pop[rand_i] - pop[i])
                        cand = pop[rand_i] - A * D
                else:
                    # tấn công lưới bong bóng: xoắn ốc logarit quanh best
                    dist = np.abs(best - pop[i])
                    ell = self.rng.uniform(-1.0, 1.0, size=self.k)
                    cand = dist * np.exp(b * ell) * np.cos(2.0 * np.pi * ell) + best

                pop[i] = self._clip(cand)
                fit[i] = self.evaluate(pop[i])

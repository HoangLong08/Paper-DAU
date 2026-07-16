"""Grey Wolf Optimizer (GWO) — cho multilevel thresholding.

Ba con sói dẫn đầu (alpha/beta/delta) kéo bầy; hệ số ``a`` giảm 2→0 theo tiến
độ tiêu ngân sách (thay cho ``t/max_iter`` vì ta điều khiển bằng NFE budget chứ
không bằng số vòng lặp). Mọi lượt chấm điểm qua ``self.evaluate``. Dừng bởi
``BudgetExhausted``.

Tham chiếu: Mirjalili, Mirjalili & Lewis, *Advances in Engineering Software*
69:46–61 (2014), ``10.1016/j.advengsoft.2013.12.007``.
"""

from __future__ import annotations

import numpy as np

from src.solvers.metaheuristics.base import Optimizer

DEFAULT_POP = 30
A_START = 2.0                  # hệ số điều khiển khám phá/khai thác (2→0)


class GWO(Optimizer):
    name = "GWO"

    def _search(self) -> None:
        n = int(self.hp.get("pop", DEFAULT_POP))

        pop = self._rand_pop(n)
        fit = np.array([self.evaluate(pop[i]) for i in range(n)])

        def top3(pop_, fit_):
            order = np.argsort(fit_)[::-1]
            return (
                pop_[order[0]].copy(), float(fit_[order[0]]),
                pop_[order[1]].copy(), float(fit_[order[1]]),
                pop_[order[2]].copy(), float(fit_[order[2]]),
            )

        a_pos, a_f, b_pos, b_f, d_pos, d_f = top3(pop, fit)

        while True:                        # dừng duy nhất bởi BudgetExhausted
            progress = self._used / self.budget
            a = A_START * (1.0 - progress)

            for i in range(n):
                new_i = np.zeros(self.k)
                for leader in (a_pos, b_pos, d_pos):
                    r1 = self.rng.random(self.k)
                    r2 = self.rng.random(self.k)
                    A = 2.0 * a * r1 - a
                    C = 2.0 * r2
                    D = np.abs(C * leader - pop[i])
                    new_i += leader - A * D
                pop[i] = self._clip(new_i / 3.0)
                f = self.evaluate(pop[i])

                # cập nhật thứ hạng alpha/beta/delta
                if f > a_f:
                    d_pos, d_f = b_pos, b_f
                    b_pos, b_f = a_pos, a_f
                    a_pos, a_f = pop[i].copy(), f
                elif f > b_f:
                    d_pos, d_f = b_pos, b_f
                    b_pos, b_f = pop[i].copy(), f
                elif f > d_f:
                    d_pos, d_f = pop[i].copy(), f

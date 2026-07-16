"""Marine Predators Algorithm (MPA) — cho multilevel thresholding.

Ba pha (chuyển động Brown ở pha đầu, hỗn hợp Brown+Lévy ở giữa, Lévy ở pha
cuối) + hiệu ứng FADs (Fish Aggregating Devices) để thoát tối ưu cục bộ. Pha
được chọn theo tiến độ tiêu ngân sách (thay cho ``Iter/Max_Iter``). Mọi lượt
chấm điểm — kể cả bước FADs — qua ``self.evaluate``. Dừng bởi ``BudgetExhausted``.

Tham chiếu: Faramarzi, Heidarinejad, Mirjalili & Gandomi, *Expert Systems with
Applications* 152:113377 (2020), ``10.1016/j.eswa.2020.113377``.
"""

from __future__ import annotations

import numpy as np

from src.solvers.metaheuristics.base import Optimizer

DEFAULT_POP = 25
P_CONST = 0.5                  # hằng số bước (Faramarzi et al. 2020)
FADS_RATE = 0.2               # xác suất hiệu ứng FADs
LEVY_SCALE = 0.05             # tỉ lệ bước Lévy


class MPA(Optimizer):
    name = "MPA"

    def _cf(self, progress: float) -> float:
        """Hệ số điều khiển kích thước bước thích ứng CF (Faramarzi et al. 2020)."""
        return (1.0 - progress) ** (2.0 * progress)

    def _search(self) -> None:
        n = int(self.hp.get("pop", DEFAULT_POP))
        p_const = float(self.hp.get("p_const", P_CONST))
        fads = float(self.hp.get("fads", FADS_RATE))
        levy_scale = float(self.hp.get("levy_scale", LEVY_SCALE))

        pop = self._rand_pop(n)
        fit = np.array([self.evaluate(pop[i]) for i in range(n)])

        while True:                        # dừng duy nhất bởi BudgetExhausted
            progress = self._used / self.budget
            elite = self._incumbent_vec()
            cf = self._cf(progress)

            for i in range(n):
                RB = self.rng.normal(0.0, 1.0, size=self.k)          # Brown
                RL = levy_scale * self._levy(self.k)                 # Lévy
                R = self.rng.random(self.k)

                if progress < 1.0 / 3.0:                             # pha 1: khám phá
                    step = RB * (elite - RB * pop[i])
                    cand = pop[i] + p_const * R * step
                elif progress < 2.0 / 3.0:                          # pha 2: chuyển tiếp
                    if i < n // 2:
                        step = RL * (elite - RL * pop[i])
                        cand = pop[i] + p_const * R * step
                    else:
                        step = RB * (RB * elite - pop[i])
                        cand = elite + p_const * cf * step
                else:                                               # pha 3: khai thác
                    step = RL * (RL * elite - pop[i])
                    cand = elite + p_const * cf * step

                pop[i] = self._clip(cand)
                fit[i] = self.evaluate(pop[i])

            # Hiệu ứng FADs — mọi lượt vẫn đếm vào NFE
            for i in range(n):
                if self.rng.random() < fads:
                    U = (self.rng.random(self.k) < fads).astype(float)
                    rand = self.lb + self.rng.random(self.k) * self.span
                    cand = pop[i] + cf * rand * U
                else:
                    r = self.rng.random()
                    i1, i2 = self.rng.integers(0, n, size=2)
                    cand = pop[i] + (fads * (1.0 - r) + r) * (pop[i1] - pop[i2])
                pop[i] = self._clip(cand)
                fit[i] = self.evaluate(pop[i])

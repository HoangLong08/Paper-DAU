"""Particle Swarm Optimization (PSO) — cho multilevel thresholding.

Baseline metaheuristic kinh điển và là **đối chứng chính của QIGOA** trong
ablation E3/§7 (QIEA ≡ EDA ⇒ QIGOA ≈ PSO về hành vi; xem qigoa.py). Inertia +
thành phần nhận thức (pbest) + xã hội (gbest). Mọi lượt chấm điểm qua
``self.evaluate``. Vòng lặp dừng bởi ``BudgetExhausted``.

Tham chiếu: Kennedy & Eberhart, *Proc. ICNN* (1995); trọng số quán tính —
Shi & Eberhart, *Proc. IEEE CEC* (1998).
"""

from __future__ import annotations

import numpy as np

from src.solvers.metaheuristics.base import Optimizer

DEFAULT_POP = 30
DEFAULT_W = 0.7                 # trọng số quán tính
DEFAULT_C1 = 1.5               # hệ số nhận thức (pbest)
DEFAULT_C2 = 1.5               # hệ số xã hội (gbest)
DEFAULT_VMAX_FRAC = 0.2        # trần vận tốc = frac × span


class PSO(Optimizer):
    name = "PSO"

    def _search(self) -> None:
        n = int(self.hp.get("pop", DEFAULT_POP))
        w = float(self.hp.get("w", DEFAULT_W))
        c1 = float(self.hp.get("c1", DEFAULT_C1))
        c2 = float(self.hp.get("c2", DEFAULT_C2))
        vmax = float(self.hp.get("vmax_frac", DEFAULT_VMAX_FRAC)) * self.span

        pos = self._rand_pop(n)
        vel = self.rng.uniform(-vmax, vmax, size=(n, self.k))
        fit = np.array([self.evaluate(pos[i]) for i in range(n)])

        pbest = pos.copy()
        pbest_f = fit.copy()
        g = int(np.argmax(fit))
        gbest = pos[g].copy()
        gbest_f = float(fit[g])

        while True:                        # dừng duy nhất bởi BudgetExhausted
            for i in range(n):
                r1 = self.rng.random(self.k)
                r2 = self.rng.random(self.k)
                vel[i] = (
                    w * vel[i]
                    + c1 * r1 * (pbest[i] - pos[i])
                    + c2 * r2 * (gbest - pos[i])
                )
                vel[i] = np.clip(vel[i], -vmax, vmax)
                pos[i] = self._clip(pos[i] + vel[i])
                f = self.evaluate(pos[i])
                if f > pbest_f[i]:
                    pbest[i] = pos[i].copy()
                    pbest_f[i] = f
                    if f > gbest_f:
                        gbest = pos[i].copy()
                        gbest_f = f

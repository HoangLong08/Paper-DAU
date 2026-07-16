"""Grasshopper Optimization Algorithm (GOA) — bản có LỖI cố ý (baseline lỗi).

⚠️ ĐÂY LÀ MỘT BASELINE HỎNG, GIỮ NGUYÊN CÓ CHỦ ĐÍCH (docs/ke-hoach-trien-khai.md
§E2; docs/preregistration.md §6/A6). Lô cũ có "GOA" với hit-rate tới nghiệm tốt
nhất = 0% ở mọi k≥3. Ta tái tạo đúng chế độ hỏng đó để làm **bài học phương pháp
luận**: một implementation lỗi sinh ra "significance" giả trên cả 10 cấu hình.

Cơ chế lỗi (khớp một bug phổ biến ngoài đời): lực xã hội GOA dùng hàm
``s(r) = f·e^{-r/l} − e^{-r}`` vốn CHỈ có nghĩa khi khoảng cách ``r`` được chuẩn
hoá về ``[1, 4]``. Bản này **KHÔNG chuẩn hoá** — nạp thẳng khoảng cách cỡ pixel
(0..255) vào ``s(·)`` ⇒ ``s(r) ≈ 0`` (bão hoà) ⇒ lực xã hội triệt tiêu ⇒ toàn
bầy co sập về incumbent ⇒ hội tụ non, càng tệ khi số chiều k tăng.

Bản SỬA ĐÚNG: goa_fixed.py (``GOAFixed``).

Tham chiếu thuật toán: Saremi, Mirjalili & Lewis, *Advances in Engineering
Software* 105:30–47 (2017), ``10.1016/j.advengsoft.2017.01.004``.
Định vị GOA ≡ biến thể PSO: Harandi et al., *ANTS 2024*, LNCS 84–97,
``10.1007/978-3-031-70932-6_7``.
"""

from __future__ import annotations

import numpy as np

from src.solvers.metaheuristics.base import Optimizer

DEFAULT_POP = 30
DEFAULT_C_MAX = 1.0            # hệ số vùng thoải mái (comfort zone) lớn nhất
DEFAULT_C_MIN = 0.00004       # nhỏ nhất (Saremi et al. 2017)


class GOA(Optimizer):
    name = "GOA"

    #: chuẩn hoá khoảng cách về [1,4]? False = bản LỖI. Bản fixed override True.
    NORMALIZE_DISTANCE: bool = False

    def _search(self) -> None:
        n = int(self.hp.get("pop", DEFAULT_POP))
        c_max = float(self.hp.get("c_max", DEFAULT_C_MAX))
        c_min = float(self.hp.get("c_min", DEFAULT_C_MIN))

        pop = self._rand_pop(n)
        fit = np.array([self.evaluate(pop[i]) for i in range(n)])

        while True:                        # dừng duy nhất bởi BudgetExhausted
            # hệ số c giảm tuyến tính theo tiến độ tiêu ngân sách
            progress = self._used / self.budget
            c = c_max - progress * (c_max - c_min)
            target = self._incumbent_vec()  # T_d = vị trí tốt nhất

            new = np.empty_like(pop)
            for i in range(n):
                social = self._goa_social(pop, i, c, normalize=self.NORMALIZE_DISTANCE)
                new[i] = self._clip(c * social + target)

            for i in range(n):
                fit[i] = self.evaluate(new[i])
            pop = new

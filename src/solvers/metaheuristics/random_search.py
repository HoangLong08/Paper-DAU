"""Random search — lấy mẫu ngẫu nhiên đều trong ngân sách NFE.

Baseline QUAN TRỌNG NHẤT về mặt lập luận (docs/ke-hoach-trien-khai.md §E4,
bậc 1): nếu random search ở **cùng NFE** ngang các metaheuristic tinh vi, thì
"lợi thế thuật toán" trên bài toán này là ảo — đòn chí mạng cho luận đề.

Không có cơ chế học: mỗi lượt sinh một vector ngưỡng ngẫu nhiên mới và chấm
điểm. Incumbent do ``evaluate`` giữ (base.py). Chạy tới khi ``BudgetExhausted``.
"""

from __future__ import annotations

from src.solvers.metaheuristics.base import Optimizer


class RandomSearch(Optimizer):
    name = "random"

    def _search(self) -> None:
        while True:                       # dừng duy nhất bởi BudgetExhausted
            self.evaluate(self._rand_vec())

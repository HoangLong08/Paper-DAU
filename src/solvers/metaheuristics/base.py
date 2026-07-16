"""Lớp nền cho MỌI metaheuristic — HARD NFE BUDGET + cổng cứng liêm chính.

Đây là module quan trọng nhất về mặt liêm chính của MODULE C. Lô thí nghiệm
cũ (commit ``c4fe108``) chết vì đúng file này: QIGOA tiêu 8.563 NFE trong khi
baseline chỉ 7.550 (thừa 13,4%) — memetic/OBL/Lévy KHÔNG được đếm vào ngân sách.

Ba bất biến (docs/preregistration.md §6/A5, docs/ke-hoach-trien-khai.md §1):

  1. ``evaluate()`` là **CỔNG DUY NHẤT** tới hàm mục tiêu. Không thuật toán nào
     được gọi ``objective()`` trực tiếp; MỌI lượt đánh giá (kể cả init, OBL,
     Lévy, memetic refinement) đi qua đây ⇒ **đếm vào NFE**.
  2. ``evaluate()`` **cập nhật incumbent NGAY TẠI CHỖ** (sửa bug A5d): trước
     đây thuật toán cập nhật ``best_x`` SAU khi ``evaluate()`` trả về, nên khi
     ``BudgetExhausted`` bắn giữa generation, cải thiện dở dang bị vứt âm thầm
     — mỗi thuật toán mất một lượng khác nhau ⇒ thiên lệch không kiểm soát.
  3. ``run()`` **assert** ``used == budget`` (±0). Mọi thuật toán phải TIÊU HẾT
     ngân sách (chạy tới ``BudgetExhausted``), không dừng sớm. Assert fail ⇒
     LƯỚI VÔ HIỆU. Đây là cổng của ``tests/test_nfe_budget.py``.

Hệ quả thiết kế: mọi ``_search()`` chạy vòng lặp **không tự kết thúc**
(``while True``); điểm dừng duy nhất là ``BudgetExhausted`` do ``evaluate()``
ném ra đúng tại lượt thứ ``budget + 1``. Nhờ vậy ``used`` luôn bằng ``budget``
CHÍNH XÁC cho MỌI thuật toán, kể cả QIGOA bật đủ mọi thành phần.
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from typing import Callable

import numpy as np

# --- Hằng số miền bài toán -------------------------------------------------
DEFAULT_L: int = 256          # số mức xám (ảnh 8-bit)
THRESH_MIN: int = 1           # ngưỡng nhỏ nhất hợp lệ
# ngưỡng lớn nhất = L - 1 (tính theo self.L trong __init__)


class BudgetExhausted(Exception):
    """Ném ra khi cạn ngân sách NFE. Thuật toán PHẢI dừng, trả best-so-far.

    KHÔNG được ``try/except`` nuốt exception này bên trong ``_search()`` —
    nó phải lan ra tới ``run()`` để cổng ``assert used == budget`` có nghĩa.
    """


class Optimizer(ABC):
    """Giao diện chung cho mọi metaheuristic (hợp đồng MODULE C).

    Parameters
    ----------
    objective : Callable[[np.ndarray], float]
        Hàm mục tiêu cần **MAXIMIZE** (VD ``KapurFitness.__call__`` của MODULE B).
        Nhận vector ngưỡng INT đã hợp lệ hoá, trả một float. MODULE C KHÔNG cài
        fitness — chỉ nhận qua tham số này.
    k : int
        Số ngưỡng cần tìm.
    seed : int
        Seed cho bộ sinh số ngẫu nhiên numpy (tất định, per-instance).
    budget : int
        Ngân sách NFE TUYỆT ĐỐI (số lần gọi ``objective`` tối đa).
    L : int, default 256
        Số mức xám; ngưỡng nằm trong ``[THRESH_MIN, L - 1]``.
    **hp
        Siêu tham số riêng của từng thuật toán (pop size, w, c1... ).
    """

    name: str = "optimizer"

    def __init__(
        self,
        objective: Callable[[np.ndarray], float],
        k: int,
        seed: int,
        budget: int,
        L: int = DEFAULT_L,
        **hp,
    ) -> None:
        if k < 1:
            raise ValueError(f"k phải >= 1, nhận {k}")
        if budget < 1:
            raise ValueError(f"budget phải >= 1, nhận {budget}")
        self.objective = objective
        self.k = int(k)
        self.seed = int(seed)
        self.budget = int(budget)
        self.L = int(L)
        self.hp = hp

        self.lb: float = float(THRESH_MIN)       # cận dưới thực = 1.0
        self.ub: float = float(self.L - 1)       # cận trên thực = 255.0
        if self.ub - self.lb + 1 < self.k:
            raise ValueError(
                f"không đủ {self.k} mức xám phân biệt trong [{THRESH_MIN}, {self.L - 1}]"
            )

        # Seed numpy (per-instance Generator ⇒ tất định, không đụng global state).
        self.rng: np.random.Generator = np.random.default_rng(self.seed)

        self._used: int = 0
        self.best_x: np.ndarray | None = None
        self.best_f: float = -math.inf

    # ------------------------------------------------------------------ #
    # Cổng đánh giá — trái tim của kỷ luật NFE                            #
    # ------------------------------------------------------------------ #
    def evaluate(self, x) -> float:
        """CỔNG DUY NHẤT tới hàm mục tiêu.

        (a) hết ngân sách ⇒ raise ``BudgetExhausted``;
        (b) tăng bộ đếm NFE;
        (c) hợp lệ hoá x → k ngưỡng INT phân biệt rồi chấm điểm;
        (d) **cập nhật incumbent NGAY nếu cải thiện** (sửa A5d).
        """
        if self._used >= self.budget:
            raise BudgetExhausted
        self._used += 1
        xr = self._repair(x)
        f = float(self.objective(xr))
        if f > self.best_f:
            self.best_f = f
            self.best_x = xr
        return f

    def _repair(self, x) -> np.ndarray:
        """Ánh xạ vector thực → k ngưỡng INT hợp lệ: sorted, unique, phân biệt.

        (i) làm tròn + clamp về ``[lb, ub]``; (ii) lấy unique (đã sorted);
        (iii) nếu trùng khiến < k phần tử, dịch/điền thêm mức xám chưa dùng cho
        đủ ĐÚNG k ngưỡng phân biệt. Luôn tồn tại nghiệm vì ``ub - lb + 1 >= k``.
        """
        lo, hi = int(self.lb), int(self.ub)
        v = np.clip(np.rint(np.asarray(x, dtype=float).ravel()), lo, hi).astype(int)
        uniq = np.unique(v)  # sorted tăng dần, đã bỏ trùng

        if len(uniq) >= self.k:
            return uniq[: self.k].copy()

        # Thiếu ngưỡng phân biệt → điền từ các mức xám chưa dùng.
        present = set(int(t) for t in uniq)
        result = list(int(t) for t in uniq)
        cand = lo
        while len(result) < self.k and cand <= hi:
            if cand not in present:
                present.add(cand)
                result.append(cand)
            cand += 1
        result.sort()
        return np.asarray(result[: self.k], dtype=int)

    # ------------------------------------------------------------------ #
    # Vòng đời                                                            #
    # ------------------------------------------------------------------ #
    @abstractmethod
    def _search(self) -> None:
        """Vòng tìm kiếm. PHẢI gọi ``self.evaluate`` cho MỌI lượt đánh giá và
        chạy tới khi ``BudgetExhausted`` (vòng lặp không tự kết thúc)."""

    def run(self) -> tuple[np.ndarray, float, int]:
        """Chạy tới cạn ngân sách; trả ``(best_x, best_f, used)``.

        ``best_x`` là ``np.ndarray`` gồm k ngưỡng INT sorted-unique trong
        ``[1, L-1]``. Assert ``used == budget`` là cổng cứng chống ăn gian NFE.
        """
        try:
            self._search()
        except BudgetExhausted:
            pass
        assert self._used == self.budget, (
            f"{self.name} dùng {self._used}/{self.budget} NFE — LƯỚI VÔ HIỆU"
        )
        return self.best_x, self.best_f, self._used

    # ------------------------------------------------------------------ #
    # Tiện ích dùng chung cho các thuật toán con                          #
    # ------------------------------------------------------------------ #
    @property
    def span(self) -> float:
        """Bề rộng miền tìm kiếm ``ub - lb``."""
        return self.ub - self.lb

    def _rand_vec(self) -> np.ndarray:
        """Một vector k ngưỡng thực ngẫu nhiên đều trong ``[lb, ub]``."""
        return self.rng.uniform(self.lb, self.ub, size=self.k)

    def _rand_pop(self, n: int) -> np.ndarray:
        """Quần thể ``n × k`` vị trí thực ngẫu nhiên đều trong ``[lb, ub]``."""
        return self.rng.uniform(self.lb, self.ub, size=(n, self.k))

    def _clip(self, x: np.ndarray) -> np.ndarray:
        """Ép vector thực về trong biên ``[lb, ub]`` (chưa làm tròn)."""
        return np.clip(x, self.lb, self.ub)

    def _incumbent_vec(self) -> np.ndarray:
        """Incumbent hiện tại dưới dạng vector thực (target cho leader-based)."""
        return self.best_x.astype(float)

    def _levy(self, size: int, beta: float = 1.5) -> np.ndarray:
        """Bước Lévy theo thuật toán Mantegna (Mantegna, Phys. Rev. E 49, 1994).

        Dùng bởi WOA/MPA/QIGOA. Trả ``size`` mẫu heavy-tailed ~ Lévy(beta).
        """
        num = math.gamma(1.0 + beta) * math.sin(math.pi * beta / 2.0)
        den = math.gamma((1.0 + beta) / 2.0) * beta * 2.0 ** ((beta - 1.0) / 2.0)
        sigma = (num / den) ** (1.0 / beta)
        u = self.rng.normal(0.0, sigma, size=size)
        v = self.rng.normal(0.0, 1.0, size=size)
        return u / np.abs(v) ** (1.0 / beta)

    @staticmethod
    def _s_func(r: np.ndarray, f: float = 0.5, l: float = 1.5) -> np.ndarray:
        """Hàm cường độ lực xã hội của GOA (Saremi, Mirjalili & Lewis, Adv. Eng.
        Softw. 105:30–47, 2017, eq. 2.3): ``s(r) = f·e^{-r/l} − e^{-r}``.

        ⚠️ Chỉ có ý nghĩa khi ``r`` đã chuẩn hoá về ``[1, 4]`` — đây chính là
        chỗ bản GOA "hỏng" (goa.py) làm sai và bản GOA-fixed (goa_fixed.py) sửa.
        """
        return f * np.exp(-r / l) - np.exp(-r)

    def _goa_social(self, pop: np.ndarray, i: int, c: float, normalize: bool) -> np.ndarray:
        """Tổng lực xã hội tác động lên cá thể ``i`` theo GOA (Saremi et al. 2017,
        eq. 2.7).

        normalize=True  → chuẩn hoá khoảng cách về ``[1, 4]`` (ĐÚNG).
        normalize=False → dùng khoảng cách thô cỡ pixel (0..255); khi đó
                          ``s(r) ≈ 0`` (bão hoà) ⇒ lực xã hội triệt tiêu ⇒ bầy
                          co sập về incumbent ⇒ hội tụ non, tệ dần khi k>2.
                          Đây là baseline LỖI cố ý (bài học phương pháp luận).
        """
        xi = pop[i]
        total = np.zeros(self.k)
        span = self.span
        for j in range(len(pop)):
            if j == i:
                continue
            diff = pop[j] - xi
            dist = np.abs(diff)
            unit = diff / (dist + 1e-12)
            if normalize:
                r = 1.0 + 3.0 * dist / span          # → [1, 4]
            else:
                r = dist                              # thô ⇒ s(r) bão hoà về 0
            total += c * (span * 0.5) * self._s_func(r) * unit
        return total

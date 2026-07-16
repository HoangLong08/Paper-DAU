"""Otsu multilevel thresholding — fitness cộng-tính-theo-khoảng (dùng cho baseline).

Otsu (1979) chọn ngưỡng cực đại hoá **phương sai giữa lớp** (between-class variance):

    σ_B²(t_1,...,t_k) = Σ_{lớp}  w · (μ − μ_T)²  =  ( Σ_{lớp} w·μ² )  −  μ_T².

`μ_T²` là hằng số (không phụ thuộc ngưỡng) ⇒ argmax của σ_B² **trùng** argmax của
`Σ w·μ²`. Đại lượng `w·μ² = (Σ p_i·i)² / w` là **cộng tính theo khoảng**, nên áp
dụng đúng cùng bộ giải DP như Kapur.

Quy ước trả về của `__call__`: trả tiêu chí cộng tính `Σ w·μ²` (KHÔNG trừ hằng số
μ_T²) để `fitness(thresholds) == giá trị solve_exact/solve_bruteforce` một cách CHÍNH
XÁC. Đây là *cùng argmax* với between-class variance; chênh nhau đúng hằng số μ_T².

Otsu ở đây chỉ dùng làm baseline / kiểm tra chéo DP — KHÔNG phải nhân vật của bài.
"""

from __future__ import annotations

import numpy as np

from src.fitness.kapur import L_DEFAULT, _validate_thresholds


class OtsuFitness:
    """Fitness Otsu (between-class variance criterion) từ histogram xác suất len 256.

    Prefix-sum moment bậc 0 và bậc 1 cho phép `interval_variance(lo, hi)` O(1):
        w = Σ_{i=lo..hi} p_i
        m = Σ_{i=lo..hi} i·p_i
        đóng góp = w·μ² = m² / w        (lớp rỗng w = 0 ⇒ 0)
    """

    def __init__(self, hist: np.ndarray):
        hist = np.asarray(hist, dtype=np.float64).ravel()
        if hist.shape[0] != L_DEFAULT:
            raise ValueError(f"hist phải dài {L_DEFAULT}, nhận {hist.shape[0]}")
        if np.any(hist < 0):
            raise ValueError("hist chứa xác suất âm")
        self.hist = hist
        self.L = L_DEFAULT
        idx = np.arange(L_DEFAULT, dtype=np.float64)
        self._M0 = np.concatenate(([0.0], np.cumsum(hist)))          # Σ p
        self._M1 = np.concatenate(([0.0], np.cumsum(idx * hist)))    # Σ i·p

    # -- giao diện CHUNG cho bộ giải DP --------------------------------------
    def interval_score(self, lo: int, hi: int) -> float:
        """Alias chung mà solver DP dùng (= interval_variance)."""
        return self.interval_variance(lo, hi)

    def interval_variance(self, lo: int, hi: int) -> float:
        """Đóng góp between-class của lớp [lo..hi] = w·μ² = m²/w. Lớp rỗng ⇒ 0.0."""
        if hi < lo:
            return 0.0
        w = self._M0[hi + 1] - self._M0[lo]
        if w <= 0.0:
            return 0.0
        m = self._M1[hi + 1] - self._M1[lo]
        return float((m * m) / w)

    # -- tổng objective -------------------------------------------------------
    def __call__(self, thresholds) -> float:
        """Tiêu chí Otsu `Σ w·μ²` (MAXIMIZE) — cùng argmax với between-class variance.

        `thresholds` = k ngưỡng int trong [1,255]; phân [0,255] thành k+1 lớp như Kapur.
        """
        thr = _validate_thresholds(thresholds, self.L)
        bounds = [0, *thr, self.L]
        return float(
            sum(
                self.interval_variance(bounds[i], bounds[i + 1] - 1)
                for i in range(len(bounds) - 1)
            )
        )

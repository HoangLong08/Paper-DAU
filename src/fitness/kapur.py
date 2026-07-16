"""Kapur (maximum-entropy) multilevel thresholding — fitness cộng-tính-theo-khoảng.

Kapur et al. (1985) chọn k ngưỡng chia dải xám [0, L-1] thành k+1 lớp sao cho
**tổng entropy của các lớp** là cực đại. Tổng entropy là *cộng tính theo khoảng*:

    H_total(t_1, ..., t_k) = Σ_{lớp}  H(lớp),

nên có thể tính bằng prefix-sum (mỗi khoảng O(1)) và tối ưu toàn cục bằng DP
(src/solvers/exact_dp.py). Đây KHÔNG phải đóng góp của bài — chỉ là *reference
optimum* để đo khoảng cách của metaheuristic.

Quy ước (khoá trước khi chạy — docs/preregistration.md §6/A5c):
  * `0·log 0 := 0` (bin xác suất 0 đóng góp 0 vào entropy).
  * **Lớp rỗng** (tổng xác suất = 0) đóng góp **0** entropy.
  * `include_zero_bg` (build_histogram): CÓ tính pixel cường-độ-0 (nền skull-strip
    ~65% của lát BraTS) vào histogram HAY KHÔNG. Lựa chọn này **đổi hoàn toàn**
    ngưỡng tối ưu, Dice, và mọi PSNR/SSIM ⇒ phải hỗ trợ và báo cáo CẢ HAI.
  * Log tự nhiên (cơ số e). Sai khác cơ số chỉ là hằng số nhân ⇒ không đổi argmax.
"""

from __future__ import annotations

import numpy as np

L_DEFAULT = 256


def build_histogram(img_uint8, include_zero_bg: bool = True) -> np.ndarray:
    """Đếm tần suất 256 bins của ảnh uint8 và chuẩn hoá thành phân phối xác suất.

    Trả về mảng `hist` dài 256, `hist.sum() == 1.0` (trừ trường hợp suy biến dưới).

    Tham số
    -------
    img_uint8 : array-like
        Ảnh cường độ, giá trị trong [0, 255]. Được ép về uint8.
    include_zero_bg : bool, mặc định True
        * True  — tính CẢ pixel cường-độ-0 vào histogram (mọi 256 bin).
        * False — LOẠI bin 0 (nền skull-stripped) rồi chuẩn hoá lại trên [1..255].
          Đây là biến thể "bỏ nền" — đổi hoàn toàn ngưỡng tối ưu (A5c).

    Ghi chú liêm chính: nếu ảnh (sau khi bỏ nền) rỗng hoàn toàn, trả histogram toàn 0
    (KHÔNG bịa phân phối) — caller phải xử lý lớp rỗng.
    """
    arr = np.asarray(img_uint8)
    if arr.dtype != np.uint8:
        # Ép an toàn: clip về [0,255] rồi ép kiểu, không làm tròn ngầm gây lệch bin.
        arr = np.clip(np.rint(arr), 0, 255).astype(np.uint8)
    counts = np.bincount(arr.ravel(), minlength=L_DEFAULT).astype(np.float64)
    if counts.shape[0] != L_DEFAULT:
        counts = counts[:L_DEFAULT]
    if not include_zero_bg:
        counts[0] = 0.0
    total = counts.sum()
    if total <= 0.0:
        # Không có pixel nào ⇒ không chuẩn hoá được. Trả về toàn 0, gắn cờ suy biến.
        return counts
    return counts / total


class KapurFitness:
    """Fitness Kapur từ một histogram xác suất len 256.

    Prefix-sum cho phép `interval_entropy(lo, hi)` chạy O(1)/khoảng:
        w = Σ_{i=lo..hi} p_i
        S = Σ_{i=lo..hi} p_i·log(p_i)            (0·log0 := 0)
        H = log(w) − S/w                          (= −Σ (p_i/w)·log(p_i/w))
    Lớp rỗng (w = 0) ⇒ H = 0.
    """

    def __init__(self, hist: np.ndarray):
        hist = np.asarray(hist, dtype=np.float64).ravel()
        if hist.shape[0] != L_DEFAULT:
            raise ValueError(f"hist phải dài {L_DEFAULT}, nhận {hist.shape[0]}")
        if np.any(hist < 0):
            raise ValueError("hist chứa xác suất âm")
        self.hist = hist
        self.L = L_DEFAULT
        # p·log(p) với quy ước 0·log0 = 0.
        with np.errstate(divide="ignore", invalid="ignore"):
            plogp = np.where(hist > 0, hist * np.log(hist), 0.0)
        # Prefix-sum độ dài L+1: P[i] = Σ_{j<i} hist[j], Q[i] = Σ_{j<i} plogp[j].
        self._P = np.concatenate(([0.0], np.cumsum(hist)))
        self._Q = np.concatenate(([0.0], np.cumsum(plogp)))

    # -- giao diện CHUNG cho bộ giải DP --------------------------------------
    def interval_score(self, lo: int, hi: int) -> float:
        """Alias chung mà solver DP dùng (= interval_entropy)."""
        return self.interval_entropy(lo, hi)

    def interval_entropy(self, lo: int, hi: int) -> float:
        """Kapur entropy của lớp gồm các bin [lo..hi] (bao gồm cả hai đầu).

        Quy ước 0·log0 := 0; lớp rỗng (Σp = 0) trả 0.0.
        """
        if hi < lo:
            return 0.0
        w = self._P[hi + 1] - self._P[lo]
        if w <= 0.0:
            return 0.0
        s = self._Q[hi + 1] - self._Q[lo]
        return float(np.log(w) - s / w)

    # -- tổng objective -------------------------------------------------------
    def __call__(self, thresholds) -> float:
        """Tổng entropy Kapur (MAXIMIZE). `thresholds` = k ngưỡng int trong [1,255].

        k ngưỡng chia [0,255] thành k+1 lớp:
            lớp 0     = [0,       t_1 - 1]
            lớp j     = [t_j,     t_{j+1} - 1]
            lớp cuối  = [t_k,     255]
        """
        thr = _validate_thresholds(thresholds, self.L)
        bounds = [0, *thr, self.L]
        return float(
            sum(
                self.interval_entropy(bounds[i], bounds[i + 1] - 1)
                for i in range(len(bounds) - 1)
            )
        )


def _validate_thresholds(thresholds, L: int) -> list[int]:
    thr = [int(t) for t in thresholds]
    if any(t < 1 or t > L - 1 for t in thr):
        raise ValueError(f"ngưỡng phải nằm trong [1,{L - 1}]: {thr}")
    if any(thr[i] >= thr[i + 1] for i in range(len(thr) - 1)):
        raise ValueError(f"ngưỡng phải tăng ngặt (sorted, không trùng): {thr}")
    return thr

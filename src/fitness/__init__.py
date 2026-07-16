"""Hàm mục tiêu cộng-tính-theo-khoảng cho multilevel thresholding.

Mọi fitness ở đây phơi ra một giao diện CHUNG để bộ giải chính xác (DP) dùng lại:

    fitness.interval_score(lo, hi) -> float   # điểm của lớp gồm các bin [lo..hi]
    fitness(thresholds)            -> float    # tổng điểm (MAXIMIZE)
    fitness.hist                   -> np.ndarray(len=256)  # histogram xác suất

Nhờ tính cộng-tính-theo-khoảng (total = Σ interval_score(lo_j, hi_j)) mà quy hoạch
động cho nghiệm tối ưu toàn cục trong O(k·L²) (xem src/solvers/exact_dp.py).
"""

from src.fitness.kapur import KapurFitness, build_histogram
from src.fitness.otsu import OtsuFitness

__all__ = ["KapurFitness", "OtsuFitness", "build_histogram"]

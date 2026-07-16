"""Bộ giải cho multilevel thresholding.

  * exact_dp.solve_exact       — nghiệm tối ưu TOÀN CỤC bằng quy hoạch động O(k·L²).
  * exhaustive.solve_bruteforce — vét cạn (k<=3), dùng làm reference cho unit test.

Cả hai trả nghiệm **canonical duy nhất** (A5a): khi nhiều tập ngưỡng cho cùng phân
hoạch/giá trị, snap về mức xám thấp nhất.
"""

from src.solvers.exact_dp import canonicalize, solve_exact
from src.solvers.exhaustive import solve_bruteforce

__all__ = ["solve_exact", "solve_bruteforce", "canonicalize"]

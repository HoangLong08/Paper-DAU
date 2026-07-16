"""Vét cạn multilevel thresholding — reference tối ưu cho unit test (k <= 3).

Chỉ dùng để KIỂM CHỨNG solve_exact (src/solvers/exact_dp.py) trên cỡ nhỏ. KHÔNG dùng
trong thí nghiệm chính (chi phí C(L-1, k) không khả thi khi k lớn).

Tối ưu tốc độ (giữ nguyên tính đúng): vì dịch một ngưỡng qua dải bin xác-suất-0 KHÔNG
đổi giá trị mục tiêu, giá trị tối ưu TOÀN CỤC luôn đạt được tại các *biên của bin có
xác suất > 0*. Do đó chỉ cần vét cạn trên tập ứng viên đó, rồi canonicalise (A5a). Nếu
mọi bin đều > 0, tập ứng viên = toàn [1, L-1] ⇒ vét cạn đầy đủ, vẫn đúng.
"""

from __future__ import annotations

import math
from itertools import combinations

from src.solvers.exact_dp import TOL, canonicalize


def _candidate_thresholds(hist, L: int) -> list[int]:
    """Tập ngưỡng ứng viên = biên (trước/sau) của mọi bin xác suất > 0, trong [1,L-1].

    Bao đủ mọi vị trí ngưỡng có thể ĐỔI phân hoạch pixel ⇒ vét cạn trên tập này tìm
    đúng giá trị tối ưu toàn cục. Ứng viên tối thiểu {1} luôn có mặt để phủ trường hợp
    đặt ngưỡng dưới toàn bộ khối lượng.
    """
    cands = {1}
    for v in range(L):
        if hist[v] > 0.0:
            if 1 <= v <= L - 1:
                cands.add(v)          # tách bin v khỏi bin v-1
            if 1 <= v + 1 <= L - 1:
                cands.add(v + 1)      # tách bin v khỏi bin v+1
    return sorted(cands)


def solve_bruteforce(fitness, k: int, L: int = 256):
    """Vét cạn nghiệm tối ưu (k <= 3 khuyến nghị) — reference cho test.

    Trả về (thresholds_canonical, f) giống hình dạng solve_exact. Nghiệm được chọn là
    tổ hợp ĐẠT tối ưu có thứ tự-từ-điển nhỏ nhất (lexicographic-min) rồi canonicalise,
    khớp đúng quy tắc canonical của solve_exact ⇒ hai bên trùng khít.
    """
    if k < 1:
        raise ValueError("k phải >= 1")
    if k > L - 1:
        raise ValueError(f"k={k} vượt số ngưỡng khả thi tối đa L-1={L - 1}")

    score = fitness.interval_score
    cands = _candidate_thresholds(fitness.hist, L)
    if len(cands) < k:
        raise ValueError(
            f"không đủ ngưỡng ứng viên ({len(cands)}) cho k={k} — histogram quá thưa"
        )

    def value(combo) -> float:
        bounds = (0, *combo, L)
        return sum(
            score(bounds[i], bounds[i + 1] - 1) for i in range(len(bounds) - 1)
        )

    # combinations trả theo thứ tự từ điển tăng dần ⇒ tổ hợp đầu tiên đạt max = lex-min.
    best_val = -math.inf
    best_combo = None
    for combo in combinations(cands, k):
        v = value(combo)
        if v > best_val + TOL:  # cải thiện thực sự ⇒ cập nhật; hoà ⇒ giữ (lex nhỏ hơn)
            best_val = v
            best_combo = combo

    thr = canonicalize(best_combo, fitness.hist)
    f = fitness(thr)
    return thr, f

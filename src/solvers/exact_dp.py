"""Nghiệm tối ưu TOÀN CỤC cho multilevel thresholding bằng quy hoạch động — O(k·L²).

⚠️ ĐÂY KHÔNG PHẢI ĐÓNG GÓP CỦA BÀI. Exact DP cho multilevel thresholding có
tính-cộng-tính-theo-khoảng đã có từ lâu; ta chỉ DÙNG nó làm *reference optimum* để
đo khoảng cách của metaheuristic. Cite trang trọng ở Abstract:
  * Luessi, Eichmann, Schmidt & Fessler, "Framework for efficient optimal
    multilevel image thresholding", J. Electronic Imaging 18(1):013004 (2009).
  * Merzban & Elbayoumi, "Efficient solution of Otsu multilevel image
    thresholding: A comparative study", Expert Systems with Applications
    116:299-309 (2019).
  * Menotti, Najman & de A. Araújo, "Efficient Polynomial Implementation of
    Several Multithresholding Methods...", LNCS/CIARP 2015, pp. 350-357.

Tính tổng quát: solver áp dụng cho BẤT KỲ fitness cộng-tính-theo-khoảng nào phơi ra
`fitness.interval_score(lo, hi)` và `fitness.hist` (xem src/fitness/). Kapur và Otsu
đều thoả.

Bài toán
--------
k ngưỡng int t_1 < ... < t_k trong [1, L-1] chia [0, L-1] thành k+1 lớp:
    lớp 0    = [0,   t_1-1]
    lớp j    = [t_j, t_{j+1}-1]
    lớp cuối = [t_k, L-1]
Cực đại Σ_lớp interval_score(lo_lớp, hi_lớp).

Quy hoạch động (suffix form)
----------------------------
    h[c][s] = giá trị tối ưu khi chia dải [s, L) thành đúng c lớp.
    h[1][s] = score(s, L-1)
    h[c][s] = max_{s' ∈ [s+1, L-(c-1)]}  score(s, s'-1) + h[c-1][s']
Nghiệm = h[k+1][0]; truy vết TỪ ĐẦU chọn ngưỡng nhỏ nhất tại mỗi bước ⇒ vector ngưỡng
nhỏ nhất theo thứ tự từ điển (lexicographic-min), rồi canonicalise (A5a).

⚠️ A5a — CANONICALISE. Lát BraTS đã skull-strip ⇒ ~65% pixel ở cường độ 0 và nhiều
mức xám RỖNG. Dưới quy ước 0·log0 := 0, dịch một ngưỡng qua một dải bin xác-suất-0
KHÔNG đổi giá trị mục tiêu ⇒ **argmax không duy nhất** ⇒ nhiều tập ngưỡng, nhiều mask,
nhiều Dice. Để nghiệm TẤT ĐỊNH và tái lập được, ta chọn nghiệm CANONICAL: snap mỗi
ngưỡng xuống mức xám thấp nhất mà KHÔNG đổi phân hoạch pixel (tức khi bin ngay dưới có
xác suất 0). Cùng một quy tắc canonical áp cho cả solve_bruteforce ⇒ hai bên trùng khít.

⚠️ A5b — relative_gap ÂM (metaheuristic "vượt" DP) hầu như LUÔN do LỆCH TẬP KHẢ THI
(ngưỡng liên tục/làm tròn/trùng, hoặc quy ước 0log0 / lớp rỗng / có-hay-không tính nền
khác nhau), **KHÔNG phải bug DP**. Bước debug ĐẦU TIÊN = audit quy ước, không phải sửa
DP. DP ở đây đã qua cổng cứng tests/test_exact_dp.py (bit-exact vs vét cạn).
"""

from __future__ import annotations

import math

NEG_INF = -math.inf
TOL = 1e-9  # dung sai so khớp giá trị tối ưu (chống nhiễu dấu phẩy động khi truy vết)


def canonicalize(thresholds, hist) -> tuple[int, ...]:
    """Snap ngưỡng xuống mức xám thấp nhất mà KHÔNG đổi phân hoạch pixel (A5a).

    Với mỗi ngưỡng t (bin trên cùng của lớp dưới là t-1): nếu `hist[t-1] == 0` thì
    dịch t xuống 1 giữ nguyên mask VÀ giá trị mục tiêu (bin rỗng không thuộc pixel nào,
    không đóng góp entropy/variance). Dừng khi chạm bin có xác suất > 0 hoặc chạm sàn
    lớp (t = ngưỡng trước + 1). Trả nghiệm canonical duy nhất.
    """
    thr = [int(t) for t in thresholds]
    prev = 0
    for i in range(len(thr)):
        t = thr[i]
        while t > prev + 1 and hist[t - 1] == 0.0:
            t -= 1
        thr[i] = t
        prev = t
    return tuple(thr)


def solve_exact(fitness, k: int, L: int = 256):
    """Nghiệm tối ưu toàn cục bằng DP O(k·L²).

    Tham số
    -------
    fitness : object cộng-tính-theo-khoảng
        Phải có `fitness.interval_score(lo, hi) -> float` và `fitness.hist` (len L).
    k : int   — số ngưỡng (1 <= k <= L-1).
    L : int   — số mức xám (mặc định 256).

    Trả về
    ------
    (thresholds, f) : tuple[tuple[int,...], float]
        `thresholds` = k ngưỡng int tối ưu, CANONICAL (A5a), tăng ngặt.
        `f` = giá trị mục tiêu tại nghiệm đó (= fitness(thresholds)).
    """
    if k < 1:
        raise ValueError("k phải >= 1")
    if k > L - 1:
        raise ValueError(f"k={k} vượt số ngưỡng khả thi tối đa L-1={L - 1}")

    score = fitness.interval_score

    # h[c][s] = tối ưu chia [s, L) thành c lớp.
    h = [[NEG_INF] * (L + 1) for _ in range(k + 2)]

    # c = 1: cả [s, L-1] là một lớp.
    for s in range(L):
        h[1][s] = score(s, L - 1)

    # c >= 2.
    for c in range(2, k + 2):
        row_prev = h[c - 1]
        row_cur = h[c]
        # cần đủ chỗ cho c lớp trong [s, L): L - s >= c  ⇒  s <= L - c.
        for s in range(0, L - c + 1):
            best = NEG_INF
            # lớp đầu = [s, s'-1]; c-1 lớp còn lại trong [s', L): cần s' <= L-(c-1).
            for sp in range(s + 1, L - (c - 1) + 1):
                val = score(s, sp - 1) + row_prev[sp]
                if val > best:
                    best = val
            row_cur[s] = best

    # Truy vết TỪ ĐẦU: tại mỗi bước chọn ngưỡng NHỎ NHẤT đạt tối ưu ⇒ lexicographic-min.
    thresholds: list[int] = []
    cur = 0
    target = h[k + 1][0]
    for rem in range(k + 1, 1, -1):  # rem = số lớp còn lại (k+1, k, ..., 2) → k ngưỡng
        row_prev = h[rem - 1]
        found = False
        for sp in range(cur + 1, L - (rem - 1) + 1):
            if abs(score(cur, sp - 1) + row_prev[sp] - target) <= TOL:
                thresholds.append(sp)
                cur = sp
                target = row_prev[sp]
                found = True
                break
        if not found:  # pragma: no cover — chỉ xảy ra nếu bảng DP hỏng
            raise RuntimeError("Truy vết DP thất bại — bảng h[][] không nhất quán")

    thr = canonicalize(thresholds, fitness.hist)
    f = fitness(thr)
    return thr, f


def relative_gap(f_ref: float, f_alg: float) -> float:
    """Khoảng cách tương đối tới nghiệm tối ưu tham chiếu: (f_ref − f_alg) / |f_ref|.

    > 0 : thuật toán KÉM hơn DP (bình thường).
    < 0 : thuật toán "vượt" DP — xem A5b: hầu như LUÔN do lệch tập khả thi, KHÔNG phải
          bug DP. Kiểm quy ước (ngưỡng liên tục/làm tròn/trùng, 0log0, lớp rỗng, có
          tính nền hay không) TRƯỚC khi nghi ngờ solver này.
    """
    denom = abs(f_ref) if f_ref != 0.0 else 1.0
    return (f_ref - f_alg) / denom

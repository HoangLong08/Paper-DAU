"""CỔNG CỨNG (docs/preregistration.md §6/A5a) cho bộ giải chính xác.

Nếu bất kỳ test nào ở đây FAIL ⇒ **toàn bộ pipeline vô hiệu**: mọi kết luận về P2
(khoảng cách metaheuristic → nghiệm tối ưu) dựng trên tính đúng đắn của solve_exact.

Kiểm định (>=20 histogram, k=2 và k=3):
  1. |f_DP − f_brute| <= 1e-9  (giá trị mục tiêu trùng).
  2. Phân hoạch cảm sinh GIỐNG HỆT sau canonicalise — so sánh nhãn lớp từng bin
     (= mask khi tính cả bội pixel) VÀ mask trên các bin có pixel thật.
  3. include_zero_bg True vs False cho ra ngưỡng KHÁC nhau (A5c) — ghi nhận + một ca
     dựng sẵn để chắc chắn nhánh khác biệt thực sự được thực thi.

Chạy: `pytest tests/test_exact_dp.py -v`  (hoặc `python tests/test_exact_dp.py`).
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.fitness.kapur import KapurFitness, build_histogram  # noqa: E402
from src.fitness.otsu import OtsuFitness  # noqa: E402
from src.solvers.exact_dp import solve_exact  # noqa: E402
from src.solvers.exhaustive import solve_bruteforce  # noqa: E402

L = 256
N_IMAGES = 24  # >= 20 theo yêu cầu cổng cứng
KS = (2, 3)


# --------------------------------------------------------------------------- #
# Nguồn dữ liệu: ưu tiên src.data.synthetic (module A) nếu có; else sparse random
# --------------------------------------------------------------------------- #
def _make_sparse_histograms(n: int, seed: int = 20260716):
    """Sinh n histogram xác suất THƯA (ít mức xám khác 0) có seed cố định.

    Thưa vì (a) khớp thực tế BraTS skull-strip (nhiều bin rỗng), (b) kích hoạt đúng
    tình huống suy biến argmax mà A5a phải xử lý, (c) giữ vét cạn k=3 khả thi.
    Không có src.data.synthetic ⇒ đây là fallback được yêu cầu trong đặc tả.
    """
    rng = np.random.default_rng(seed)
    hists = []
    for _ in range(n):
        n_levels = int(rng.integers(6, 28))  # ít mức xám khác 0
        levels = rng.choice(np.arange(L), size=n_levels, replace=False)
        counts = np.zeros(L, dtype=np.float64)
        counts[levels] = rng.integers(1, 500, size=n_levels).astype(np.float64)
        # ~60-70% khối lượng dồn về bin 0 (nền skull-strip) cho hiện thực + suy biến.
        counts[0] += counts.sum() * rng.uniform(1.2, 2.5)
        hists.append(counts / counts.sum())
    return hists


def _load_histograms(n: int):
    """Trả về danh sách (name, hist). Thử src.data.synthetic trước, else fallback."""
    try:
        from src.data import synthetic  # type: ignore

        for fn_name in ("phantom_histograms", "make_histograms", "histograms"):
            fn = getattr(synthetic, fn_name, None)
            if callable(fn):
                hs = fn(n)
                return [(f"synthetic[{i}]", np.asarray(h, dtype=np.float64))
                        for i, h in enumerate(hs)]
    except Exception:
        pass
    return [(f"sparse[{i}]", h) for i, h in enumerate(_make_sparse_histograms(n))]


def _labels(thresholds, L: int = L) -> np.ndarray:
    """Nhãn lớp của TỪNG bin [0..L-1] cho một tập ngưỡng (= mask cảm sinh theo bin)."""
    return np.searchsorted(np.asarray(thresholds), np.arange(L), side="right")


# --------------------------------------------------------------------------- #
# CỔNG CỨNG chính: DP == vét cạn (giá trị + phân hoạch), Kapur & Otsu, k=2,3
# --------------------------------------------------------------------------- #
def _check_dp_matches_bruteforce(fitness_cls, name_tag: str):
    data = _load_histograms(N_IMAGES)
    assert len(data) >= 20, "cổng cứng đòi >= 20 histogram"
    for name, hist in data:
        fit = fitness_cls(hist)
        nz = hist > 0.0  # các bin có pixel thật ⇒ mask lâm sàng chỉ quan tâm chỗ này
        for k in KS:
            thr_dp, f_dp = solve_exact(fit, k, L)
            thr_bf, f_bf = solve_bruteforce(fit, k, L)

            # (1) giá trị mục tiêu trùng trong 1e-9
            assert abs(f_dp - f_bf) <= 1e-9, (
                f"{name_tag} {name} k={k}: |f_DP-f_brute|={abs(f_dp - f_bf):.3e} "
                f"(DP={f_dp!r} brute={f_bf!r})"
            )

            # (2a) ngưỡng canonical trùng khít
            assert tuple(thr_dp) == tuple(thr_bf), (
                f"{name_tag} {name} k={k}: ngưỡng lệch DP={thr_dp} brute={thr_bf}"
            )

            # (2b) phân hoạch cảm sinh giống hệt — nhãn từng bin + mask trên bin thật
            lab_dp, lab_bf = _labels(thr_dp), _labels(thr_bf)
            assert np.array_equal(lab_dp, lab_bf), (
                f"{name_tag} {name} k={k}: phân hoạch theo bin khác nhau"
            )
            assert np.array_equal(lab_dp[nz], lab_bf[nz]), (
                f"{name_tag} {name} k={k}: mask trên bin có pixel khác nhau"
            )

            # sanity: ngưỡng hợp lệ, tăng ngặt, trong [1,255]
            assert all(1 <= t <= L - 1 for t in thr_dp)
            assert all(thr_dp[i] < thr_dp[i + 1] for i in range(len(thr_dp) - 1))


def test_dp_matches_bruteforce_kapur():
    """DP khớp vét cạn cho KAPUR (nhân vật chính) — k=2,3, >=20 histogram."""
    _check_dp_matches_bruteforce(KapurFitness, "KAPUR")


def test_dp_matches_bruteforce_otsu():
    """DP khớp vét cạn cho OTSU (baseline) — cùng solver DP tổng quát."""
    _check_dp_matches_bruteforce(OtsuFitness, "OTSU")


# --------------------------------------------------------------------------- #
# A5c: include_zero_bg True vs False ⇒ ngưỡng KHÁC (ghi nhận, không assert bằng nhau)
# --------------------------------------------------------------------------- #
def _brats_like_image(seed: int = 7) -> np.ndarray:
    """Ảnh giả kiểu lát BraTS skull-strip: ~65% pixel nền cường-độ-0 + vài mô sáng."""
    rng = np.random.default_rng(seed)
    img = np.zeros(64 * 64, dtype=np.int64)
    n = img.size
    n_fg = int(0.35 * n)
    fg_idx = rng.choice(n, size=n_fg, replace=False)
    # ba đám mô: xám thấp, xám trung, u sáng
    tissue = rng.choice([40, 90, 150, 210], size=n_fg, p=[0.4, 0.3, 0.2, 0.1])
    img[fg_idx] = tissue + rng.integers(-8, 9, size=n_fg)
    return np.clip(img, 0, 255).astype(np.uint8)


def test_include_zero_bg_changes_optimum():
    """A5c: tính hay không tính nền cường-độ-0 ĐỔI ngưỡng tối ưu — phải chạy CẢ HAI."""
    img = _brats_like_image()

    hist_with = build_histogram(img, include_zero_bg=True)
    hist_without = build_histogram(img, include_zero_bg=False)

    assert abs(hist_with.sum() - 1.0) < 1e-12
    assert abs(hist_without.sum() - 1.0) < 1e-12
    assert hist_without[0] == 0.0, "bỏ nền ⇒ bin 0 phải bằng 0"
    assert hist_with[0] > 0.0, "ảnh có nền ⇒ bin 0 > 0"

    for k in KS:
        thr_with, _ = solve_exact(KapurFitness(hist_with), k, L)
        thr_without, _ = solve_exact(KapurFitness(hist_without), k, L)
        # Ghi nhận (A5c): con số hai nhánh khác nhau — bằng chứng lựa chọn nền quan trọng.
        print(f"[A5c] k={k}: include_zero_bg=True -> {thr_with} | False -> {thr_without}")

    # Với ảnh có ~65% nền, ít nhất MỘT k phải cho ngưỡng khác nhau (không assert cụ thể k nào).
    diffs = []
    for k in KS:
        tw, _ = solve_exact(KapurFitness(hist_with), k, L)
        to, _ = solve_exact(KapurFitness(hist_without), k, L)
        diffs.append(tuple(tw) != tuple(to))
    assert any(diffs), "kỳ vọng include_zero_bg đổi ngưỡng cho ít nhất một k"


def test_build_histogram_basic():
    """build_histogram: len 256, chuẩn hoá, đếm đúng."""
    img = np.array([0, 0, 0, 128, 255], dtype=np.uint8)
    h = build_histogram(img, include_zero_bg=True)
    assert h.shape == (256,)
    assert abs(h.sum() - 1.0) < 1e-12
    assert abs(h[0] - 3 / 5) < 1e-12
    assert abs(h[128] - 1 / 5) < 1e-12
    assert abs(h[255] - 1 / 5) < 1e-12
    h2 = build_histogram(img, include_zero_bg=False)
    assert h2[0] == 0.0
    assert abs(h2[128] - 1 / 2) < 1e-12  # chuẩn hoá lại trên 2 pixel còn lại


if __name__ == "__main__":
    test_build_histogram_basic()
    print("[ok] build_histogram")
    test_dp_matches_bruteforce_kapur()
    print("[ok] DP == bruteforce (Kapur, k=2,3, >=20 histogram)")
    test_dp_matches_bruteforce_otsu()
    print("[ok] DP == bruteforce (Otsu, k=2,3, >=20 histogram)")
    test_include_zero_bg_changes_optimum()
    print("[ok] include_zero_bg True vs False đổi ngưỡng (A5c)")
    print("\nTẤT CẢ CỔNG CỨNG PASS.")

"""Kiểm định MODULE E — metrics + stats (docs/preregistration.md §6/A4 + A7).

Nguyên tắc LIÊM CHÍNH: mọi con số kỳ vọng ở đây là **đáp án tính tay biết trước** hoặc
một tính chất bất biến (tổng xác suất = 1, CI lo ≤ hi, ...). Không có số minh hoạ.

Chạy:  ``pytest tests/test_metrics.py -v``  hoặc  ``python tests/test_metrics.py``.
"""

from __future__ import annotations

import math
import os
import sys

import numpy as np
import pytest

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from src.eval.metrics import (  # noqa: E402
    dice,
    empty_mask_rate,
    hd95,
    n_connected_components,
    nsd,
)
from src.eval.stats import (  # noqa: E402
    bayesian_signed_rank,
    bootstrap_ci,
    friedman_nemenyi,
    one_sample_wilcoxon_delta,
    tost,
    wilcoxon_signed,
)


# ======================================================================= #
# METRICS — Dice (đáp án tính tay)
# ======================================================================= #
def _square(shape, r0, r1, c0, c1) -> np.ndarray:
    """Mask bool: hình chữ nhật [r0:r1, c0:c1) True trên nền ``shape``."""
    m = np.zeros(shape, dtype=bool)
    m[r0:r1, c0:c1] = True
    return m


def test_dice_two_overlapping_squares_hand_calc():
    """Hai hình vuông 4x4 chồng nhau ở cột 2..3 ⇒ Dice = 2·8/(16+16) = 0.5 (tính tay)."""
    gt = _square((8, 8), 0, 4, 0, 4)     # 16 px
    pred = _square((8, 8), 0, 4, 2, 6)   # 16 px, chồng cột {2,3} × 4 hàng = 8 px
    assert int(gt.sum()) == 16 and int(pred.sum()) == 16
    assert int(np.logical_and(gt, pred).sum()) == 8
    assert dice(pred, gt) == pytest.approx(0.5)


def test_dice_identical_is_one():
    gt = _square((8, 8), 1, 5, 1, 5)
    assert dice(gt.copy(), gt) == pytest.approx(1.0)


def test_dice_both_empty_is_one():
    """A7: cả hai rỗng ⇒ Dice = 1.0."""
    z = np.zeros((8, 8), dtype=bool)
    assert dice(z, z.copy()) == 1.0


def test_dice_gt_empty_pred_nonempty_is_zero():
    """A7: GT rỗng & pred không rỗng ⇒ Dice = 0.0 (theo công thức)."""
    gt = np.zeros((8, 8), dtype=bool)
    pred = _square((8, 8), 0, 2, 0, 2)
    assert dice(pred, gt) == 0.0
    # đối xứng: GT không rỗng & pred rỗng ⇒ 0.0
    assert dice(gt, pred) == 0.0


# ======================================================================= #
# METRICS — HD95 (đáp án tính tay + quy ước rỗng A7)
# ======================================================================= #
def test_hd95_identical_is_zero():
    gt = _square((16, 16), 3, 9, 3, 9)
    assert hd95(gt.copy(), gt) == pytest.approx(0.0, abs=1e-9)


def test_hd95_two_single_pixels_exact():
    """Hai mask 1-pixel cách nhau 3 cột ⇒ mọi khoảng cách mặt = 3 ⇒ HD95 = 3.0 (tính tay)."""
    a = np.zeros((8, 8), dtype=bool)
    b = np.zeros((8, 8), dtype=bool)
    a[0, 0] = True
    b[0, 3] = True
    assert hd95(a, b, spacing=(1.0, 1.0)) == pytest.approx(3.0, abs=1e-9)
    # spacing theo cột = 2 ⇒ khoảng cách 3·2 = 6.0
    assert hd95(a, b, spacing=(1.0, 2.0)) == pytest.approx(6.0, abs=1e-9)


def test_hd95_pred_empty_returns_penalty_diagonal():
    """A7: GT≠rỗng & pred rỗng ⇒ HD95 = hình phạt = đường chéo ảnh theo spacing."""
    gt = _square((10, 20), 2, 6, 2, 6)
    pred = np.zeros((10, 20), dtype=bool)
    expected = math.sqrt((10 * 1.0) ** 2 + (20 * 1.0) ** 2)
    assert hd95(pred, gt, spacing=(1.0, 1.0)) == pytest.approx(expected, abs=1e-9)
    # ghi đè hình phạt tường minh
    assert hd95(pred, gt, empty_penalty=999.0) == 999.0


def test_hd95_both_empty_is_zero():
    z = np.zeros((10, 10), dtype=bool)
    assert hd95(z, z.copy()) == 0.0


def test_hd95_symmetric():
    a = _square((16, 16), 2, 8, 2, 8)
    b = _square((16, 16), 4, 10, 4, 10)
    assert hd95(a, b) == pytest.approx(hd95(b, a), abs=1e-9)


# ======================================================================= #
# METRICS — NSD (quy ước rỗng + tolerance)
# ======================================================================= #
def test_nsd_identical_is_one():
    gt = _square((16, 16), 3, 9, 3, 9)
    assert nsd(gt.copy(), gt, tau_mm=2.0) == pytest.approx(1.0)


def test_nsd_far_pixels_tolerance():
    """Hai pixel cách 3 mm: τ=1 ⇒ NSD=0 (không mặt nào trong dung sai); τ=5 ⇒ NSD=1."""
    a = np.zeros((8, 8), dtype=bool)
    b = np.zeros((8, 8), dtype=bool)
    a[0, 0] = True
    b[0, 3] = True
    assert nsd(a, b, tau_mm=1.0) == pytest.approx(0.0)
    assert nsd(a, b, tau_mm=5.0) == pytest.approx(1.0)


def test_nsd_both_empty_is_one_one_empty_is_zero():
    z = np.zeros((8, 8), dtype=bool)
    nonempty = _square((8, 8), 0, 2, 0, 2)
    assert nsd(z, z.copy()) == 1.0
    assert nsd(nonempty, z) == 0.0
    assert nsd(z, nonempty) == 0.0


# ======================================================================= #
# METRICS — connected components + empty_mask_rate (A7)
# ======================================================================= #
def test_n_connected_components_three_blobs():
    """A7: mask 3 cục rời nhau ⇒ 3 thành phần liên thông."""
    m = np.zeros((10, 30), dtype=bool)
    m[1:3, 1:3] = True     # cục 1
    m[5:7, 10:12] = True   # cục 2
    m[1:3, 20:22] = True   # cục 3
    assert n_connected_components(m) == 3


def test_n_connected_components_empty_is_zero():
    assert n_connected_components(np.zeros((5, 5), dtype=bool)) == 0


def test_empty_mask_rate():
    """A7: tỷ lệ mask rỗng — 2/5 rỗng ⇒ 0.4."""
    full = _square((6, 6), 0, 2, 0, 2)
    empty = np.zeros((6, 6), dtype=bool)
    masks = [full, empty, full.copy(), empty.copy(), full.copy()]
    assert empty_mask_rate(masks) == pytest.approx(2 / 5)
    assert empty_mask_rate([]) == 0.0


# ======================================================================= #
# METRICS — PSNR / SSIM (wrapper skimage — bỏ qua nếu thiếu skimage)
# ======================================================================= #
def test_psnr_ssim_skimage_wrappers():
    pytest.importorskip("skimage")
    from src.eval.metrics import psnr, ssim

    rng = np.random.default_rng(0)
    img = rng.integers(0, 256, size=(32, 32)).astype(np.uint8)
    # ảnh giống hệt ⇒ PSNR = +inf, SSIM = 1.0
    assert math.isinf(psnr(img, img.copy()))
    assert ssim(img, img.copy()) == pytest.approx(1.0, abs=1e-9)
    # ảnh khác ⇒ PSNR hữu hạn, SSIM < 1
    noisy = np.clip(img.astype(int) + rng.integers(-30, 31, img.shape), 0, 255).astype(np.uint8)
    assert math.isfinite(psnr(img, noisy))
    assert ssim(img, noisy) < 1.0


# ======================================================================= #
# STATS — Wilcoxon signed (A4d: pratt KHÔNG loại cặp-0)
# ======================================================================= #
def test_wilcoxon_pratt_keeps_zero_pairs():
    """A4d: pratt giữ cặp hiệu = 0 — n_zero báo đúng, n_total = toàn bộ mẫu."""
    x = np.array([0.10, 0.20, 0.30, 0.40, 0.50, 0.60])
    y = np.array([0.10, 0.20, 0.30, 0.10, 0.20, 0.30])  # 3 cặp đầu hiệu = 0
    res = wilcoxon_signed(x, y, zero_method="pratt")
    assert res["n_total"] == 6
    assert res["n_zero"] == 3
    # rank-biserial dương (mọi hiệu khác 0 đều dương)
    assert res["rank_biserial"] == pytest.approx(1.0)
    assert 0.0 <= res["p"] <= 1.0


def test_wilcoxon_all_zero_is_safe():
    """Mọi hiệu = 0 (hai thuật toán ⇒ mask giống hệt tuyệt đối) ⇒ không crash, p=1."""
    d = np.zeros(10)
    res = wilcoxon_signed(d)
    assert res["n_zero"] == 10 and res["n_total"] == 10
    assert res["p"] == 1.0 and res["rank_biserial"] == 0.0


def test_wilcoxon_x_is_diff_when_y_none():
    d = np.array([0.05, -0.02, 0.03, 0.0, 0.04])
    res = wilcoxon_signed(d)
    assert res["n_total"] == 5 and res["n_zero"] == 1


# ======================================================================= #
# STATS — Friedman + Nemenyi (§3)
# ======================================================================= #
def test_friedman_nemenyi_basic():
    rng = np.random.default_rng(1)
    N = 30
    data = {
        "A": rng.normal(0.60, 0.05, N),
        "B": rng.normal(0.65, 0.05, N),
        "C": rng.normal(0.55, 0.05, N),
    }
    res = friedman_nemenyi(data)
    assert set(res["ranks"].keys()) == {"A", "B", "C"}
    assert 0.0 <= res["friedman_p"] <= 1.0
    assert res["cd"] > 0.0
    # 3 phương pháp ⇒ C(3,2) = 3 cặp Nemenyi
    assert len(res["nemenyi"]) == 3
    for pair, info in res["nemenyi"].items():
        assert info["rank_diff"] >= 0.0
        assert isinstance(info["significant"], bool)


def test_friedman_unequal_length_raises():
    with pytest.raises(ValueError):
        friedman_nemenyi({"A": [1, 2, 3], "B": [1, 2, 3], "C": [1, 2]})


def test_friedman_needs_three_methods():
    """Friedman là omnibus ≥ 3 nhóm; k=2 ⇒ báo lỗi rõ (dùng wilcoxon_signed thay thế)."""
    with pytest.raises(ValueError):
        friedman_nemenyi({"A": [1, 2, 3, 4], "B": [2, 3, 4, 5]})


# ======================================================================= #
# STATS — TOST (A4c: luôn trả delta_ach hợp lệ, không "fail")
# ======================================================================= #
def test_tost_returns_valid_delta_ach():
    rng = np.random.default_rng(2)
    diff = rng.normal(0.0, 0.02, 150)  # hiệu quanh 0
    res = tost(diff, low=-0.01, high=0.01)
    assert res["delta_ach"] > 0.0 and math.isfinite(res["delta_ach"])
    assert res["ci90_low"] < res["ci90_high"]
    assert 0.0 <= res["p"] <= 1.0
    # delta_ach = max(|ci90_low|, |ci90_high|) theo định nghĩa A4c
    assert res["delta_ach"] == pytest.approx(
        max(abs(res["ci90_low"]), abs(res["ci90_high"]))
    )


def test_tost_tight_data_is_equivalent():
    """Hiệu cực nhỏ, phương sai bé ⇒ delta_ach nhỏ ⇒ tương đương ở bound 0.01."""
    diff = np.full(100, 0.001) + np.random.default_rng(3).normal(0, 1e-4, 100)
    res = tost(diff, low=-0.01, high=0.01)
    assert res["delta_ach"] < 0.01
    assert res["p"] < 0.05  # tương đương ở α=0.05 với bound ±0.01


# ======================================================================= #
# STATS — Bayesian signed-rank + ROPE (A4c: tổng xác suất = 1)
# ======================================================================= #
def test_bayesian_rope_probabilities_sum_to_one():
    rng = np.random.default_rng(4)
    diff = rng.normal(0.0, 0.02, 60)
    res = bayesian_signed_rank(diff, rope=(-0.01, 0.01), n_samples=4000, seed=0)
    total = res["p_left"] + res["p_rope"] + res["p_right"]
    assert total == pytest.approx(1.0, abs=1e-9)
    for key in ("p_left", "p_rope", "p_right"):
        assert 0.0 <= res[key] <= 1.0


def test_bayesian_rope_detects_equivalence_with_zeros():
    """Nhiều hiệu = 0 (mask giống hệt) ⇒ khối lượng dồn về ROPE ⇒ p_rope lớn nhất."""
    diff = np.concatenate([np.zeros(40), np.random.default_rng(5).normal(0, 0.003, 20)])
    res = bayesian_signed_rank(diff, rope=(-0.01, 0.01), n_samples=4000, seed=1)
    assert res["p_rope"] > res["p_left"] and res["p_rope"] > res["p_right"]


# ======================================================================= #
# STATS — one-sample Wilcoxon Δ (A4a: P3 primary)
# ======================================================================= #
def test_one_sample_wilcoxon_delta_success_path():
    """Δ tập trung quanh 0.05 > SESOI=0.01 ⇒ cả ba tiêu chí thành công đúng."""
    rng = np.random.default_rng(6)
    delta = rng.normal(0.05, 0.02, 150)
    res = one_sample_wilcoxon_delta(delta, sesoi=0.01)
    assert res["n"] == 150
    assert res["median"] > 0.01
    assert res["p"] < 0.05
    assert res["ci_low"] > 0.01  # CI không chứa SESOI (nằm hẳn trên)
    assert res["success"] is True


def test_one_sample_wilcoxon_delta_null_path():
    """Δ quanh 0 ⇒ không đạt SESOI ⇒ success = False (trung thực khi mệnh đề sai)."""
    rng = np.random.default_rng(7)
    delta = rng.normal(0.0, 0.02, 150)
    res = one_sample_wilcoxon_delta(delta, sesoi=0.01)
    assert res["success"] is False


# ======================================================================= #
# STATS — bootstrap CI (A7: median [IQR] + 95% bootstrap CI)
# ======================================================================= #
def test_bootstrap_ci_brackets_median():
    rng = np.random.default_rng(8)
    vals = rng.normal(0.7, 0.1, 200)
    lo, hi = bootstrap_ci(vals, stat=np.median, n=2000, seed=0)
    assert lo <= hi
    assert lo <= np.median(vals) <= hi


def test_bootstrap_ci_edge_cases():
    assert bootstrap_ci([], n=100) == pytest.approx((float("nan"), float("nan")), nan_ok=True)
    lo, hi = bootstrap_ci([0.42], n=100)
    assert lo == 0.42 and hi == 0.42


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))

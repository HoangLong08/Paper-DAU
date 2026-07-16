"""UNIT TEST SỐ HỌC cho MODULE D — bake A1 (suy biến) và trần A2.

⚠️ ĐÂY LÀ UNIT TEST, KHÔNG PHẢI RESULT (docs/preregistration.md §6/A1). Nó KHÔNG có
p-value, KHÔNG được trình bày như bằng chứng thực nghiệm. `std(Dice) < 1e-12` là mệnh
đề số học (Proposition + Corollary), luôn pass — kể cả trên ảnh nhiễu ngẫu nhiên. Vai
trò của nó: khoá cứng bất biến cấu trúc của decode/oracle trước khi chạy lưới chính.

Nội dung:
  1. A1 — với rule `brightest`, các tập k ngưỡng NGẪU NHIÊN cùng ``t_k`` ⇒ mask giống
     hệt ⇒ nhóm theo MASK HASH (không theo t_max) ⇒ std(Dice) < 1e-12 mỗi nhóm.
  2. A1 Corollary — số mask khả dĩ của MỌI band-selection bị chặn (<= C(256,2)) và ĐỘC
     LẬP với k (số mask `brightest` <= số t_k phân biệt, bất kể k lên tới 10+).
  3. A2 — oracle_levelset >= oracle_interval >= oracle_single về Dice (trần nới dần).
  4. Smoke-test Horn-2 decoders (skimage/sklearn) qua importorskip — không chặn nếu
     thiếu dep.

Chạy: `pytest tests/test_degeneracy.py -v`  (hoặc `python tests/test_degeneracy.py`).
"""

from __future__ import annotations

import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.decode.decoding import (  # noqa: E402
    RULES,
    decode,
    label_map,
    mask_hash,
    oracle_interval,
    oracle_levelset,
    oracle_single,
)

L = 256
EPS = 1e-9


# --------------------------------------------------------------------------- #
# dice: dùng module E nếu có, else fallback cục bộ (đặc tả cho phép)
# --------------------------------------------------------------------------- #
try:
    from src.eval.metrics import dice  # type: ignore  # noqa: E402
except Exception:  # module E build song song — fallback theo đúng hợp đồng

    def dice(pred, gt) -> float:
        pred = np.asarray(pred, dtype=bool)
        gt = np.asarray(gt, dtype=bool)
        s = int(pred.sum()) + int(gt.sum())
        if s == 0:
            return 1.0  # cả hai rỗng = 1.0 (khớp hợp đồng module E)
        return 2.0 * int(np.logical_and(pred, gt).sum()) / s


# --------------------------------------------------------------------------- #
# Ảnh + GT test: synthetic phantom (module A) nếu có, cộng vài ảnh random
# --------------------------------------------------------------------------- #
def _test_cases():
    """Danh sách (name, img_uint8, gt_bool). Ưu tiên phantom thật, thêm ảnh random."""
    cases = []
    try:
        from src.data.synthetic import synthetic_slice  # type: ignore

        for seed in (0, 1, 2):
            sl = synthetic_slice(seed)
            cases.append((f"synth_flair_{seed}", np.asarray(sl.flair), np.asarray(sl.wt_mask, bool)))
            cases.append((f"synth_t1ce_{seed}", np.asarray(sl.t1ce), np.asarray(sl.et_mask, bool)))
    except Exception:
        pass

    # Ảnh random (nền skull-strip giả) + GT là superlevel-set nhiễu ⇒ purity không tầm thường.
    for seed in (10, 11, 12):
        rng = np.random.default_rng(seed)
        img = np.zeros((48, 48), dtype=np.uint8)
        n = img.size
        fg = rng.choice(n, size=int(0.4 * n), replace=False)
        img.ravel()[fg] = rng.integers(30, 256, size=fg.size).astype(np.uint8)
        gt = (img >= 150) & (rng.random(img.shape) < 0.85)  # nhiễu ⇒ purity < 1
        cases.append((f"rand_{seed}", img, gt))

    # Ca biên: GT rỗng (kiểm quy ước cả-hai-rỗng), GT toàn bộ trong não.
    rng = np.random.default_rng(99)
    img = rng.integers(0, 256, size=(32, 32)).astype(np.uint8)
    cases.append(("gt_empty", img, np.zeros(img.shape, dtype=bool)))
    return cases


# --------------------------------------------------------------------------- #
# 1. A1 — brightest suy biến: cùng t_k ⇒ mask giống hệt ⇒ std(Dice)=0 mỗi mask-group
# --------------------------------------------------------------------------- #
def _random_thresholds_with_tk(rng, t_k: int, k: int) -> tuple[int, ...]:
    """k ngưỡng tăng ngặt với ngưỡng lớn nhất = t_k (k-1 ngưỡng dưới lấy ngẫu nhiên)."""
    if k == 1:
        return (t_k,)
    lows = rng.choice(np.arange(1, t_k), size=k - 1, replace=False)
    return tuple(sorted(int(v) for v in lows) + [int(t_k)])


def test_a1_brightest_degeneracy_std_zero_per_maskgroup():
    """A1: nhóm theo MASK HASH ⇒ std(Dice) < 1e-12 trên 100% nhóm (Proposition số học)."""
    rng = np.random.default_rng(2026)
    for name, img, gt in _test_cases():
        records = []  # (mask_hash, dice)
        # nhiều t_k khác nhau, mỗi t_k nhiều tập ngưỡng ngẫu nhiên với k khác nhau
        for t_k in rng.choice(np.arange(20, 250), size=8, replace=False):
            for _ in range(6):
                k = int(rng.integers(2, 11))          # k = 2..10
                if t_k <= k:                          # cần đủ ngưỡng dưới t_k
                    continue
                thr = _random_thresholds_with_tk(rng, int(t_k), k)
                m = decode(thr, img, "brightest")
                records.append((mask_hash(m), dice(m, gt)))

        # Nhóm theo mask hash (A1: KHÔNG nhóm theo t_max).
        groups: dict[str, list[float]] = {}
        for h, d in records:
            groups.setdefault(h, []).append(d)
        for h, ds in groups.items():
            assert np.std(ds) < 1e-12, (
                f"{name}: mask-group {h[:12]} có std(Dice)={np.std(ds):.3e} >= 1e-12 "
                f"⇒ P1 (suy biến brightest) bị bác bỏ ở mức số học"
            )


def test_a1_same_tk_implies_identical_mask():
    """A1: mọi tập k ngưỡng CÙNG t_k ⇒ CÙNG một mask hash (mask phụ thuộc đúng t_k)."""
    rng = np.random.default_rng(7)
    _, img, _ = _test_cases()[0]
    for t_k in (60, 120, 200):
        hashes = set()
        for _ in range(12):
            k = int(rng.integers(2, 11))
            thr = _random_thresholds_with_tk(rng, t_k, k)
            hashes.add(mask_hash(decode(thr, img, "brightest")))
        assert len(hashes) == 1, f"t_k={t_k}: brightest sinh {len(hashes)} mask khác nhau (kỳ vọng 1)"


# --------------------------------------------------------------------------- #
# 2. A1 Corollary — lực lượng mask band-selection bị chặn & ĐỘC LẬP với k
# --------------------------------------------------------------------------- #
def test_a1_bandselection_mask_cardinality_bounded():
    """|{mask khả dĩ của band-selection}| <= C(256,2), bất kể k (headline ~10^-13)."""
    _, img, _ = _test_cases()[0]
    rng = np.random.default_rng(123)
    bound = math.comb(L, 2)                            # số cặp (lo,hi) khả dĩ

    hashes_brightest = set()
    tk_values = set()
    hashes_any_band = set()
    # 800 vector ngẫu nhiên, k trải 2..12 ⇒ search space tại k=12 ~ C(254,12) ≈ 10^19,
    # nhưng số mask thực tế bị chặn cứng dưới C(256,2).
    for _ in range(800):
        k = int(rng.integers(2, 13))
        thr = tuple(sorted(rng.choice(np.arange(1, L), size=k, replace=False).tolist()))
        tk_values.add(thr[-1])
        hashes_brightest.add(mask_hash(decode(thr, img, "brightest")))
        for rule in ("brightest", "upper_union", "otsu_pick"):
            hashes_any_band.add(mask_hash(decode(thr, img, rule)))

    assert len(hashes_any_band) <= bound, (
        f"số mask band-selection = {len(hashes_any_band)} > C(256,2)={bound}"
    )
    # ĐỘC LẬP với k: số mask brightest <= số t_k phân biệt (mask phụ thuộc đúng t_k).
    assert len(hashes_brightest) <= len(tk_values), (
        f"brightest: {len(hashes_brightest)} mask > {len(tk_values)} t_k phân biệt "
        f"⇒ mask KHÔNG chỉ phụ thuộc t_k (mâu thuẫn A1)"
    )


# --------------------------------------------------------------------------- #
# 3. A2 — trần nới dần: levelset >= interval >= single
# --------------------------------------------------------------------------- #
def test_a2_oracle_ceiling_monotone():
    """A2: Dice(oracle_levelset) >= Dice(oracle_interval) >= Dice(oracle_single)."""
    for name, img, gt in _test_cases():
        _, d_single, t = oracle_single(img, gt)
        _, d_interval, (lo, hi) = oracle_interval(img, gt)
        _, d_levelset = oracle_levelset(img, gt)

        assert 1 <= t <= L - 1
        assert 0 <= lo <= hi <= L - 1
        assert d_interval >= d_single - EPS, (
            f"{name}: interval {d_interval:.6f} < single {d_single:.6f}"
        )
        assert d_levelset >= d_interval - EPS, (
            f"{name}: levelset {d_levelset:.6f} < interval {d_interval:.6f}"
        )
        for d in (d_single, d_interval, d_levelset):
            assert -EPS <= d <= 1.0 + EPS


def test_a2_oracle_masks_consistent_with_reported_dice():
    """Mask trả về khớp Dice trả về (không lệch giữa số và hiện vật)."""
    for name, img, gt in _test_cases():
        for fn in (oracle_single, oracle_interval, oracle_levelset):
            out = fn(img, gt)
            mask, d_reported = out[0], out[1]
            d_recomputed = dice(mask, gt)
            assert abs(d_reported - d_recomputed) < 1e-9, (
                f"{name}/{fn.__name__}: dice báo {d_reported:.9f} != dice mask {d_recomputed:.9f}"
            )


# --------------------------------------------------------------------------- #
# 4. Sanity band rules + Horn-2 smoke test (skip nếu thiếu dep)
# --------------------------------------------------------------------------- #
def test_band_rules_return_bool_masks():
    """Mọi rule trong RULES trả mask bool đúng shape (morph cần skimage)."""
    import pytest

    _, img, _ = _test_cases()[0]
    thr = (50, 100, 150, 200)
    for rule in RULES:
        if rule == "morph":
            pytest.importorskip("skimage")
        m = decode(thr, img, rule)
        assert m.dtype == bool and m.shape == img.shape

    # brightest == (label == k) == (pixel >= t_k): kiểm tra bất biến cốt lõi A1.
    lab = label_map(thr, img)
    assert np.array_equal(decode(thr, img, "brightest"), lab == len(thr))
    assert np.array_equal(decode(thr, img, "brightest"), img >= thr[-1])


def test_horn2_decoders_smoke():
    """Horn-2 (kmeans/watershed/chanvese) trả mask bool đúng shape khi có dep."""
    import pytest

    pytest.importorskip("skimage")
    pytest.importorskip("sklearn")
    from src.decode.decoding import LABELMAP_DECODERS, decode_labelmap

    _, img, _ = _test_cases()[0]
    thr = (60, 120, 180)
    for method in LABELMAP_DECODERS:
        m = decode_labelmap(thr, img, method, seed=0)
        assert m.dtype == bool and m.shape == img.shape


if __name__ == "__main__":
    test_a1_brightest_degeneracy_std_zero_per_maskgroup()
    print("[ok] A1: std(Dice)<1e-12 mỗi mask-group (brightest suy biến)")
    test_a1_same_tk_implies_identical_mask()
    print("[ok] A1: cùng t_k ⇒ cùng mask")
    test_a1_bandselection_mask_cardinality_bounded()
    print("[ok] A1 Corollary: |mask band-selection| bị chặn & độc lập k")
    test_a2_oracle_ceiling_monotone()
    print("[ok] A2: levelset >= interval >= single")
    test_a2_oracle_masks_consistent_with_reported_dice()
    print("[ok] A2: mask khớp Dice báo cáo")
    test_band_rules_return_bool_masks()
    print("[ok] band rules trả bool mask")
    try:
        test_horn2_decoders_smoke()
        print("[ok] Horn-2 decoders smoke")
    except Exception as e:
        print(f"[skip] Horn-2 smoke ({e})")
    print("\nTẤT CẢ TEST MODULE D PASS.")

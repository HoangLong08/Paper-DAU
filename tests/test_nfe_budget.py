"""CỔNG CỨNG NFE (docs/preregistration.md §6/A5; ke-hoach §1, §E2).

Lô cũ (commit ``c4fe108``) chết vì QIGOA tiêu 8.563 NFE trong khi baseline chỉ
7.550 (thừa 13,4%): memetic/OBL/Lévy KHÔNG được đếm. Test này là hàng rào chống
tái phạm — nó phải PASS trước khi được phép chạy lưới chính.

Kiểm 3 điều cho MỌI optimizer (GA, PSO, GOA, GOA-fixed, GWO, WOA, MPA, QIGOA,
random) với một objective giả có nghiệm biết trước:
  1. ``used == budget`` CHÍNH XÁC (±0) — kể cả QIGOA bật đủ memetic+OBL+Lévy.
  2. ``best_x`` là ``np.ndarray`` INT, sorted, unique, đúng ``k`` phần tử,
     nằm trong ``[1, 255]``.
  3. Đơn điệu ngân sách: budget khác nhau ⇒ ``used`` bằng đúng budget đó.

Chạy trực tiếp không cần pytest:  ``python tests/test_nfe_budget.py``
Hoặc qua pytest:                  ``pytest tests/test_nfe_budget.py``

Test này KHÔNG cần MODULE B (fitness thật): objective giả là hàm bậc hai có
nghiệm tối ưu tại ``target`` — đủ để lái tìm kiếm và kiểm định dạng đầu ra.
"""

from __future__ import annotations

import os
import sys

import numpy as np

# Cho phép chạy trực tiếp từ thư mục repo (thêm gốc repo vào sys.path).
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from src.solvers.metaheuristics import (  # noqa: E402
    GA,
    GOA,
    GWO,
    MPA,
    PSO,
    QIGOA,
    WOA,
    GOAFixed,
    RandomSearch,
)

L = 256
THRESH_MIN, THRESH_MAX = 1, L - 1

# Mọi lớp optimizer cần đi qua cổng (khớp danh sách lưới chính E2).
OPTIMIZER_CLASSES = [GA, PSO, GOA, GOAFixed, GWO, WOA, MPA, QIGOA, RandomSearch]


def make_objective(k: int):
    """Objective giả cần MAXIMIZE, nghiệm tối ưu biết trước tại ``target``.

    ``f(x) = −Σ (x − target)²`` ⇒ đạt cực đại (=0) khi x = target. Tất định,
    không ngẫu nhiên — phù hợp làm objective kiểm thử (hợp đồng MODULE C)."""
    target = np.linspace(40, 210, k)

    def objective(x: np.ndarray) -> float:
        x = np.asarray(x, dtype=float)
        return float(-np.sum((x - target) ** 2))

    return objective


def _check_output_shape(best_x: np.ndarray, k: int) -> None:
    assert isinstance(best_x, np.ndarray), f"best_x phải là np.ndarray, nhận {type(best_x)}"
    assert np.issubdtype(best_x.dtype, np.integer), f"best_x phải INT, nhận {best_x.dtype}"
    assert best_x.shape == (k,), f"best_x phải có đúng {k} phần tử, nhận shape {best_x.shape}"
    # sorted tăng dần & phân biệt (unique)
    assert np.all(np.diff(best_x) > 0), f"best_x phải sorted & unique, nhận {best_x.tolist()}"
    assert best_x.min() >= THRESH_MIN and best_x.max() <= THRESH_MAX, (
        f"best_x phải nằm trong [{THRESH_MIN}, {THRESH_MAX}], nhận {best_x.tolist()}"
    )


# --------------------------------------------------------------------------- #
# 1. Cổng NFE: used == budget CHÍNH XÁC cho MỌI thuật toán                     #
# --------------------------------------------------------------------------- #
def test_all_optimizers_exhaust_exact_budget():
    k, budget, seed = 3, 500, 0
    for cls in OPTIMIZER_CLASSES:
        opt = cls(objective=make_objective(k), k=k, seed=seed, budget=budget, L=L)
        best_x, best_f, used = opt.run()
        assert used == budget, f"{cls.name}: used={used} != budget={budget} (±0 BẮT BUỘC)"
        _check_output_shape(best_x, k)
        assert np.isfinite(best_f), f"{cls.name}: best_f không hữu hạn ({best_f})"


# --------------------------------------------------------------------------- #
# 2. QIGOA bật ĐỦ memetic+OBL+Lévy+quantum vẫn tiêu ĐÚNG budget (không tràn)   #
#    ← đây là chỗ lô cũ ăn gian 13,4%                                          #
# --------------------------------------------------------------------------- #
def test_qigoa_full_components_exact_budget():
    k, budget, seed = 3, 500, 1
    opt = QIGOA(
        objective=make_objective(k),
        k=k,
        seed=seed,
        budget=budget,
        L=L,
        quantum=True,
        memetic=True,
        obl=True,
        levy=True,
    )
    best_x, _, used = opt.run()
    assert used == budget, f"QIGOA-full: used={used} != budget={budget} — TRÀN NFE (bug A5)"
    _check_output_shape(best_x, k)


def test_qigoa_ablation_variants_exact_budget():
    """Mọi biến thể ablation E3 (tắt từng thành phần) đều tiêu đúng budget."""
    k, budget = 4, 400
    variants = {
        "full": dict(quantum=True, memetic=True, obl=True, levy=True),
        "-quantum": dict(quantum=False, memetic=True, obl=True, levy=True),
        "-memetic": dict(quantum=True, memetic=False, obl=True, levy=True),
        "-obl": dict(quantum=True, memetic=True, obl=False, levy=True),
        "-levy": dict(quantum=True, memetic=True, obl=True, levy=False),
        "bare": dict(quantum=True, memetic=False, obl=False, levy=False),
    }
    for label, hp in variants.items():
        opt = QIGOA(objective=make_objective(k), k=k, seed=2, budget=budget, L=L, **hp)
        best_x, _, used = opt.run()
        assert used == budget, f"QIGOA[{label}]: used={used} != budget={budget}"
        _check_output_shape(best_x, k)


# --------------------------------------------------------------------------- #
# 3. Đầu ra hợp lệ trên nhiều k (gồm k=2 và k cao)                             #
# --------------------------------------------------------------------------- #
def test_output_valid_across_k():
    budget = 300
    for k in (2, 3, 5, 8):
        for cls in OPTIMIZER_CLASSES:
            opt = cls(objective=make_objective(k), k=k, seed=7, budget=budget, L=L)
            best_x, _, used = opt.run()
            assert used == budget, f"{cls.name} @k={k}: used={used} != {budget}"
            _check_output_shape(best_x, k)


# --------------------------------------------------------------------------- #
# 4. Ngân sách khác nhau ⇒ used bằng đúng budget đó (đơn điệu, không lệch)     #
# --------------------------------------------------------------------------- #
def test_budget_is_respected_for_various_sizes():
    k = 3
    for budget in (50, 137, 500, 1000):
        for cls in (QIGOA, GA, RandomSearch):
            opt = cls(objective=make_objective(k), k=k, seed=3, budget=budget, L=L)
            _, _, used = opt.run()
            assert used == budget, f"{cls.name}: budget={budget} nhưng used={used}"


# --------------------------------------------------------------------------- #
# 5. Determinism: cùng seed ⇒ cùng kết quả                                     #
# --------------------------------------------------------------------------- #
def test_determinism_same_seed():
    k, budget = 3, 400
    for cls in OPTIMIZER_CLASSES:
        r1 = cls(objective=make_objective(k), k=k, seed=42, budget=budget, L=L).run()
        r2 = cls(objective=make_objective(k), k=k, seed=42, budget=budget, L=L).run()
        assert np.array_equal(r1[0], r2[0]) and r1[1] == r2[1], (
            f"{cls.name}: không tất định với cùng seed"
        )


def _run_all():
    tests = [
        test_all_optimizers_exhaust_exact_budget,
        test_qigoa_full_components_exact_budget,
        test_qigoa_ablation_variants_exact_budget,
        test_output_valid_across_k,
        test_budget_is_respected_for_various_sizes,
        test_determinism_same_seed,
    ]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"[PASS] {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"[FAIL] {t.__name__}: {e}")
    print("-" * 60)
    if failed:
        print(f"{failed}/{len(tests)} test THẤT BẠI")
        return 1
    print(f"TẤT CẢ {len(tests)} test PASS — cổng NFE thông.")
    return 0


if __name__ == "__main__":
    # Console Windows mặc định cp1252 không mã hoá được tiếng Việt → ép UTF-8.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(_run_all())

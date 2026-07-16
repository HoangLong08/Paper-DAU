"""MODULE C — họ metaheuristic dưới HARD NFE BUDGET.

Tất cả kế thừa ``Optimizer`` (base.py) và chỉ khác nhau ở ``_search()``. Cổng
cứng ``tests/test_nfe_budget.py`` bảo đảm MỌI thuật toán tiêu ĐÚNG cùng số NFE
(±0) — điều lô cũ (commit ``c4fe108``) làm sai và là lý do lô đó bị vứt.

Hợp đồng import (docs/ke-hoach-trien-khai.md §1):
    from src.solvers.metaheuristics.qigoa import QIGOA
"""

from src.solvers.metaheuristics.base import BudgetExhausted, Optimizer
from src.solvers.metaheuristics.ga import GA
from src.solvers.metaheuristics.pso import PSO
from src.solvers.metaheuristics.goa import GOA
from src.solvers.metaheuristics.goa_fixed import GOAFixed
from src.solvers.metaheuristics.gwo import GWO
from src.solvers.metaheuristics.woa import WOA
from src.solvers.metaheuristics.mpa import MPA
from src.solvers.metaheuristics.qigoa import QIGOA
from src.solvers.metaheuristics.random_search import RandomSearch

#: Đăng ký tên → lớp, dùng bởi script chạy lưới và test cổng cứng.
OPTIMIZERS: dict[str, type[Optimizer]] = {
    GA.name: GA,
    PSO.name: PSO,
    GOA.name: GOA,
    GOAFixed.name: GOAFixed,
    GWO.name: GWO,
    WOA.name: WOA,
    MPA.name: MPA,
    QIGOA.name: QIGOA,
    RandomSearch.name: RandomSearch,
}

__all__ = [
    "Optimizer",
    "BudgetExhausted",
    "GA",
    "PSO",
    "GOA",
    "GOAFixed",
    "GWO",
    "WOA",
    "MPA",
    "QIGOA",
    "RandomSearch",
    "OPTIMIZERS",
]

"""Base class for population-based optimizers, maximization convention."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, List, Optional
import time
import numpy as np

from ..utils.helpers import sanitize_thresholds


@dataclass
class OptResult:
    best_x: np.ndarray
    best_fitness: float
    history: List[float] = field(default_factory=list)
    runtime_s: float = 0.0
    n_evals: int = 0
    name: str = ""


class BaseOptimizer:
    name: str = "base"

    def __init__(self, dim: int, lb, ub, pop_size: int = 30,
                 max_iter: int = 100, seed: Optional[int] = None):
        self.dim = int(dim)
        self.lb = np.full(self.dim, lb, dtype=np.float64) if np.isscalar(lb) else np.asarray(lb, dtype=np.float64)
        self.ub = np.full(self.dim, ub, dtype=np.float64) if np.isscalar(ub) else np.asarray(ub, dtype=np.float64)
        self.pop_size = int(pop_size)
        self.max_iter = int(max_iter)
        self.rng = np.random.default_rng(seed)
        self.n_evals = 0

    def _init_pop(self) -> np.ndarray:
        x = self.rng.uniform(self.lb, self.ub, size=(self.pop_size, self.dim))
        return sanitize_thresholds(x, self.lb, self.ub)

    def _evaluate(self, f: Callable[[np.ndarray], float], pop: np.ndarray) -> np.ndarray:
        out = np.empty(pop.shape[0], dtype=np.float64)
        for i in range(pop.shape[0]):
            out[i] = f(pop[i])
        self.n_evals += pop.shape[0]
        return out

    def optimize(self, fitness: Callable[[np.ndarray], float]) -> OptResult:
        raise NotImplementedError

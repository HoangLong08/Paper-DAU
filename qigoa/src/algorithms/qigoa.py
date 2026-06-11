"""Quantum-Inspired Grasshopper Optimization Algorithm (QIGOA) — proposed method.

Four contributions on top of standard GOA:
    (1) Quantum representation: each grasshopper is encoded as Q-bits
        (alpha, beta) with |alpha|^2 + |beta|^2 = 1. Observation yields a
        binary string that is decoded into thresholds via plain binary mapping.
    (2) Adaptive quantum rotation angle: theta_i depends on the fitness gap
        between the current grasshopper and the global target, plus a
        time-decaying scale (large early exploration, small late exploitation).
    (3) Opposition-Based Learning at initialization and Levy-flight kick
        when the swarm stagnates for `stagnation_window` iterations.
    (4) Memetic local refinement: in the final phase the best solution is
        polished with a coordinate-descent neighborhood search to eliminate
        quantization noise from the bit-string observation.

Fitness convention: maximization.
"""
from __future__ import annotations
import time
import numpy as np
from .base import BaseOptimizer, OptResult
from ..utils.helpers import sanitize_thresholds, levy_flight, opposition


def _s(r: np.ndarray, f: float = 0.5, l: float = 1.5) -> np.ndarray:
    return f * np.exp(-r / l) - np.exp(-r)


class QIGOA(BaseOptimizer):
    name = "QIGOA"

    def __init__(self, dim, lb, ub, pop_size=30, max_iter=100, seed=None,
                 c_max: float = 1.0, c_min: float = 1e-5,
                 f_intensity: float = 0.5, l_scale: float = 1.5,
                 bits_per_dim: int = 12,
                 theta_min: float = 0.005 * np.pi,
                 theta_max: float = 0.08 * np.pi,
                 stagnation_window: int = 6,
                 obl_ratio: float = 0.5,
                 levy_scale: float = 0.1,
                 refine_window: int = 3,
                 refine_passes: int = 2,
                 deterministic_tail_frac: float = 0.15):
        super().__init__(dim, lb, ub, pop_size, max_iter, seed)
        self.c_max, self.c_min = c_max, c_min
        self.f_intensity, self.l_scale = f_intensity, l_scale
        self.bits = int(bits_per_dim)
        self.theta_min, self.theta_max = theta_min, theta_max
        self.stagnation_window = stagnation_window
        self.obl_ratio = obl_ratio
        self.levy_scale = levy_scale
        self.refine_window = int(refine_window)
        self.refine_passes = int(refine_passes)
        self.deterministic_tail_frac = float(deterministic_tail_frac)

    # ----- quantum encode / decode -----------------------------------------------
    def _init_quantum(self):
        shape = (self.pop_size, self.dim, self.bits)
        alpha = np.full(shape, 1.0 / np.sqrt(2.0))
        beta = np.full(shape, 1.0 / np.sqrt(2.0))
        return alpha, beta

    def _observe(self, alpha: np.ndarray, deterministic: bool = False) -> np.ndarray:
        """Standard stochastic observation, or deterministic argmax-amplitude in
        the convergence tail."""
        if deterministic:
            # bit = 1 iff beta^2 > alpha^2  (i.e. P(|1>) > P(|0>))
            return (alpha ** 2 < 0.5).astype(np.int64)
        r = self.rng.random(alpha.shape)
        return (r > alpha ** 2).astype(np.int64)

    def _decode(self, bits: np.ndarray) -> np.ndarray:
        weights = (1 << np.arange(self.bits - 1, -1, -1))
        ints = (bits * weights[None, None, :]).sum(axis=-1)
        max_int = (1 << self.bits) - 1
        normalized = ints / max_int
        return self.lb[None, :] + normalized * (self.ub - self.lb)[None, :]

    # ----- adaptive rotation -----------------------------------------------------
    def _rotation_angles(self, fit: np.ndarray, target_f: float, t: int) -> np.ndarray:
        denom = max(abs(target_f), 1e-9)
        gap = np.clip((target_f - fit) / denom, 0.0, 1.0)
        # cosine-annealed decay: 1.0 at t=0, smoothly to 0 at t=max_iter
        decay = 0.5 * (1.0 + np.cos(np.pi * t / max(1, self.max_iter - 1)))
        theta = self.theta_min + (self.theta_max - self.theta_min) * gap * decay
        return theta  # (pop,)

    def _apply_rotation(self, alpha, beta, target_bits, current_bits, theta):
        diff = target_bits - current_bits
        sign = diff
        th = theta[:, None, None] * sign
        ca, sa = np.cos(th), np.sin(th)
        new_alpha = ca * alpha - sa * beta
        new_beta = sa * alpha + ca * beta
        norm = np.sqrt(new_alpha ** 2 + new_beta ** 2) + 1e-12
        return new_alpha / norm, new_beta / norm

    # ----- GOA social term -------------------------------------------------------
    def _social(self, pos: np.ndarray, c: float) -> np.ndarray:
        N = pos.shape[0]
        ub_lb = (self.ub - self.lb) / 2.0
        new = np.zeros_like(pos)
        for i in range(N):
            diff = pos - pos[i]
            dist = np.linalg.norm(diff, axis=1, keepdims=True) + 1e-12
            unit = diff / dist
            s_vals = _s(dist.squeeze(-1), self.f_intensity, self.l_scale)
            s_vals[i] = 0.0
            new[i] = (c * ub_lb[None, :] * s_vals[:, None] * unit).sum(axis=0)
        return c * new

    # ----- memetic refinement ----------------------------------------------------
    def _local_refine(self, x: np.ndarray, fx: float, fitness) -> tuple[np.ndarray, float]:
        """Coordinate-descent: for each dim, exhaustively scan ±refine_window.
        Repeated for refine_passes. Cheap (k * (2w+1) per pass) and removes
        the discretization noise that quantum observation introduces.
        """
        best_x = x.copy()
        best_f = fx
        for _ in range(self.refine_passes):
            improved = False
            for d in range(self.dim):
                lo = max(int(self.lb[d]), int(best_x[d]) - self.refine_window)
                hi = min(int(self.ub[d]), int(best_x[d]) + self.refine_window)
                for v in range(lo, hi + 1):
                    cand = best_x.copy()
                    cand[d] = float(v)
                    cand = sanitize_thresholds(cand, self.lb, self.ub)
                    f_cand = fitness(cand)
                    self.n_evals += 1
                    if f_cand > best_f + 1e-12:
                        best_f = float(f_cand)
                        best_x = cand
                        improved = True
            if not improved:
                break
        return best_x, best_f

    # ----- main loop -------------------------------------------------------------
    def optimize(self, fitness):
        t0 = time.perf_counter()
        alpha, beta = self._init_quantum()
        bits = self._observe(alpha)
        pos = self._decode(bits)
        pos = sanitize_thresholds(pos, self.lb, self.ub)
        fit = self._evaluate(fitness, pos)

        # OBL init
        n_obl = int(self.obl_ratio * self.pop_size)
        if n_obl > 0:
            opp = opposition(pos, self.lb, self.ub)
            opp = sanitize_thresholds(opp, self.lb, self.ub)
            fit_opp = self._evaluate(fitness, opp)
            worst_idx = np.argsort(fit)[:n_obl]
            for idx in worst_idx:
                if fit_opp[idx] > fit[idx]:
                    pos[idx] = opp[idx]
                    fit[idx] = fit_opp[idx]

        g_idx = int(np.argmax(fit))
        target = pos[g_idx].copy()
        target_f = float(fit[g_idx])
        history = [target_f]
        stagnation = 0

        def encode_int_bits(values: np.ndarray) -> np.ndarray:
            normalized = (values - self.lb) / (self.ub - self.lb + 1e-12)
            ints = np.clip((normalized * ((1 << self.bits) - 1)).round().astype(np.int64),
                           0, (1 << self.bits) - 1)
            out = np.zeros((values.shape[0], self.bits), dtype=np.int64)
            for k in range(self.bits):
                out[:, self.bits - 1 - k] = (ints >> k) & 1
            return out

        # iteration at which we switch to deterministic observation
        det_start = int(self.max_iter * (1.0 - self.deterministic_tail_frac))

        for t in range(self.max_iter):
            c = self.c_max - (t + 1) * (self.c_max - self.c_min) / self.max_iter

            theta = self._rotation_angles(fit, target_f, t)
            tb = encode_int_bits(target)
            target_bits = np.broadcast_to(tb, (self.pop_size,) + tb.shape)
            alpha, beta = self._apply_rotation(alpha, beta, target_bits, bits, theta)
            bits = self._observe(alpha, deterministic=(t >= det_start))
            q_pos = self._decode(bits)

            social = self._social(q_pos, c)
            new_pos = social + target

            # blend: more quantum early (exploration), more classical late
            # (exploitation around target). blend goes 0.3 -> 1.0
            blend = 0.3 + 0.7 * (t / max(1, self.max_iter - 1))
            new_pos = blend * new_pos + (1 - blend) * q_pos

            pos = sanitize_thresholds(new_pos, self.lb, self.ub)
            fit = self._evaluate(fitness, pos)
            j = int(np.argmax(fit))
            if fit[j] > target_f + 1e-9:
                target_f = float(fit[j])
                target = pos[j].copy()
                stagnation = 0
            else:
                stagnation += 1

            if stagnation >= self.stagnation_window:
                n_kick = max(1, self.pop_size // 4)
                worst = np.argsort(fit)[:n_kick]
                span = self.ub - self.lb
                for idx in worst:
                    step = levy_flight(self.dim, rng=self.rng) * self.levy_scale * span
                    pos[idx] = pos[idx] + step
                pos = sanitize_thresholds(pos, self.lb, self.ub)
                fit = self._evaluate(fitness, pos)
                stagnation = 0

            history.append(target_f)

        # --- Memetic local refinement on the best solution ---
        target, target_f = self._local_refine(target, target_f, fitness)
        history[-1] = target_f  # update last point so plots show the refined fitness

        return OptResult(best_x=target, best_fitness=target_f, history=history,
                         runtime_s=time.perf_counter() - t0,
                         n_evals=self.n_evals, name=self.name)

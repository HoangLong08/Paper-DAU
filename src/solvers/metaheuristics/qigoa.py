"""QIGOA — Quantum-Inspired Grasshopper Optimization Algorithm.

Đề gốc của thầy Hảo. QIGOA = GOA + biểu diễn Q-bit + rotation gate (cập nhật
XÁC SUẤT kiểu EDA) + (tuỳ chọn) OBL init / Lévy flight / memetic refinement.

────────────────────────────────────────────────────────────────────────────
⚠️ ĐỊNH VỊ TRUNG THỰC (docs/preregistration.md §5, §6/A6; CLAUDE.md §2 IRON
RULE 6). TUYỆT ĐỐI **KHÔNG** claim "quantum advantage" ở bất cứ đâu. Q-bit +
rotation gate của QIEA đã được chứng minh là **tương đương một EDA** (Estimation
of Distribution Algorithm) khi chạy trên phần cứng cổ điển. Ở đây nó là *"a
probabilistic (EDA-style) update rule"*, không hơn.
────────────────────────────────────────────────────────────────────────────

Cite TỪNG phương trình về một nguồn công bố CÓ TÊN (A6):

  * Biểu diễn Q-bit (biên độ α,β; xác suất |β|²) và **rotation gate** cập nhật
    góc θ:  Han & Kim, "Quantum-inspired evolutionary algorithm for a class of
    combinatorial optimization", *IEEE Trans. Evolutionary Computation* 6(6):
    580–593 (2002), ``10.1109/TEVC.2002.804320``.
  * QIEA ≡ EDA (cập nhật xác suất, KHÔNG có ưu thế lượng tử trên phần cứng cổ
    điển): Platel, Schliebs & Kasabov, "Quantum-Inspired Evolutionary Algorithm:
    A Multimodel EDA", *IEEE Trans. Evolutionary Computation* 13(6):1218–1232
    (2009), ``10.1109/TEVC.2008.2003010``.
  * Nền GOA (lực xã hội s(r), hệ số comfort-zone c): Saremi, Mirjalili & Lewis,
    *Advances in Engineering Software* 105:30–47 (2017),
    ``10.1016/j.advengsoft.2017.01.004``.
  * Opposition-Based Learning (OBL) init: Tizhoosh, *Proc. CIMCA/IAWTIC* (2005).
  * Lévy flight (Mantegna): Mantegna, *Physical Review E* 49(5):4677 (1994).

★ KỶ LUẬT NFE (docs/preregistration.md §6/A5 — chỗ lô cũ ăn gian 13,4%):
  MỌI thành phần (OBL, sampling Q-bit, Lévy, memetic) gọi ``self.evaluate`` ⇒
  ĐẾM VÀO NGÂN SÁCH. Không có ngoại lệ. Nhờ vòng lặp không tự kết thúc + cổng
  ``evaluate``, QIGOA-full tiêu ĐÚNG ``budget`` NFE (±0) như mọi thuật toán khác.

Cờ ablation (E3 — bật/tắt từng thành phần, giữ mọi hp khác y hệt):
  ``quantum`` (Q-bit + rotation gate) · ``obl`` · ``levy`` · ``memetic``.
  Mặc định tất cả True = "QIGOA-full".
"""

from __future__ import annotations

import numpy as np

from src.solvers.metaheuristics.base import Optimizer

DEFAULT_POP = 30
DEFAULT_C_MAX = 1.0            # comfort-zone lớn nhất (GOA)
DEFAULT_C_MIN = 0.00004       # comfort-zone nhỏ nhất (GOA)
DEFAULT_ROT_STEP = 0.05       # bước xoay Δθ của rotation gate (× π)
DEFAULT_LEVY_SCALE = 0.01     # tỉ lệ bước Lévy


class QIGOA(Optimizer):
    name = "QIGOA"

    # ---- ánh xạ Q-bit ↔ ngưỡng ------------------------------------------ #
    def _theta_to_center(self, theta: np.ndarray) -> np.ndarray:
        """Xác suất |β|² = sin²θ (Han & Kim 2002) → tâm ngưỡng trong [lb, ub]."""
        return self.lb + np.sin(theta) ** 2 * self.span

    def _vec_to_theta(self, vec: np.ndarray) -> np.ndarray:
        """Ngưỡng thực → góc θ tương ứng (nghịch đảo _theta_to_center)."""
        p = np.clip((np.asarray(vec, float) - self.lb) / self.span, 0.0, 1.0)
        return np.arcsin(np.sqrt(p))

    def _memetic(self, base_vec: np.ndarray) -> None:
        """Tinh chỉnh cục bộ (memetic) quanh incumbent: thử dịch ±1 mỗi chiều.

        Mỗi lượt thử gọi ``self.evaluate`` ⇒ ĐẾM VÀO NFE. Incumbent tự cập nhật
        trong ``evaluate`` nếu tốt hơn (base.py A5d)."""
        cur = np.asarray(base_vec, dtype=float)
        for d in range(self.k):
            for delta in (-1.0, 1.0):
                cand = cur.copy()
                cand[d] += delta
                self.evaluate(cand)          # đếm NFE; cập nhật best nếu cải thiện

    def _search(self) -> None:
        n = int(self.hp.get("pop", DEFAULT_POP))
        c_max = float(self.hp.get("c_max", DEFAULT_C_MAX))
        c_min = float(self.hp.get("c_min", DEFAULT_C_MIN))
        d_theta = float(self.hp.get("rot_step", DEFAULT_ROT_STEP)) * np.pi
        levy_scale = float(self.hp.get("levy_scale", DEFAULT_LEVY_SCALE))

        use_quantum = bool(self.hp.get("quantum", True))
        use_obl = bool(self.hp.get("obl", True))
        use_levy = bool(self.hp.get("levy", True))
        use_memetic = bool(self.hp.get("memetic", True))

        # --- Khởi tạo (+ OBL) — mọi lượt đánh giá đếm NFE (A5) ------------- #
        pop = self._rand_pop(n)
        fit = np.array([self.evaluate(pop[i]) for i in range(n)])
        if use_obl:
            # Opposition-Based Learning: điểm đối lập x' = lb + ub − x (Tizhoosh 2005)
            opp = self.lb + self.ub - pop
            opp_fit = np.array([self.evaluate(opp[i]) for i in range(n)])
            allp = np.vstack([pop, opp])
            allf = np.concatenate([fit, opp_fit])
            keep = np.argsort(allf)[::-1][:n]
            pop, fit = allp[keep].copy(), allf[keep].copy()

        # Góc Q-bit θ per-chiều, khởi từ incumbent (Han & Kim 2002).
        theta = self._vec_to_theta(self._incumbent_vec())

        while True:                          # dừng duy nhất bởi BudgetExhausted
            progress = self._used / self.budget
            c = c_max - progress * (c_max - c_min)
            target = self._incumbent_vec()

            # --- Sinh quần thể mới ---------------------------------------- #
            new = np.empty_like(pop)
            if use_quantum:
                # Lấy mẫu từ mô hình Q-bit (EDA-style; Platel et al. 2009):
                # tâm = sin²θ ánh xạ vào miền, độ tản = c·½·span.
                center = self._theta_to_center(theta)
                spread = c * 0.5 * self.span
                for i in range(n):
                    cand = center + self.rng.normal(0.0, 1.0, size=self.k) * spread
                    new[i] = self._clip(cand)
            else:
                # −quantum: rơi về cập nhật xã hội GOA cài ĐÚNG (chuẩn hoá [1,4]).
                for i in range(n):
                    social = self._goa_social(pop, i, c, normalize=True)
                    new[i] = self._clip(c * social + target)

            for i in range(n):
                fit[i] = self.evaluate(new[i])
            pop = new

            # --- Lévy flight (thăm dò heavy-tailed) — đếm NFE ------------- #
            if use_levy:
                best = self._incumbent_vec()
                for i in range(n):
                    step = levy_scale * self._levy(self.k) * (pop[i] - best)
                    self.evaluate(self._clip(pop[i] + step))

            # --- Rotation gate: xoay θ về phía incumbent (Han & Kim 2002) -- #
            if use_quantum:
                target_theta = self._vec_to_theta(self._incumbent_vec())
                theta = theta + d_theta * np.sign(target_theta - theta)
                theta = np.clip(theta, 0.0, np.pi / 2.0)

            # --- Memetic refinement quanh incumbent — đếm NFE ------------- #
            if use_memetic:
                self._memetic(self._incumbent_vec())

"""Thống kê cho pipeline QIGOA Reality-Check (docs/preregistration.md §6/A4 + §3).

Tầng này vận hành các decision rule đã khoá. Nó CHỨA đúng những con dao mà A4 chỉ ra
sẽ tự cắt bài nếu dùng ẩu:

  * A4d — ``scipy.stats.wilcoxon`` mặc định ``zero_method="wilcox"`` VỨT các cặp bằng 0.
    Nhưng theo P1, hai thuật toán tìm cùng ``t_k`` ⇒ mask GIỐNG HỆT ⇒ hiệu = 0 CHÍNH XÁC,
    và các cặp-0 đó CHÍNH LÀ kết quả của bài. ⇒ ta KHOÁ ``zero_method="pratt"`` và LUÔN
    báo cáo ``n_zero / n_total``. Con số "trên X/150 bệnh nhân hai thuật toán cho mask
    giống hệt" là cả bài gói trong một phân số.
  * A4c — "p > 0,05" KHÔNG chứng minh tương đương. Equivalence hợp pháp:
      - PRIMARY  : Bayesian signed-rank + ROPE (Benavoli et al., JMLR 18(77):1–36, 2017)
                   — không có khái niệm "fail", xử lý spike-tại-0 tự nhiên.
      - COMPANION: TOST ↔ 90% CI của hiệu theo cặp, + ``delta_ach`` = equivalence bound
                   NHỎ NHẤT còn giữ tương đương ở α=0,05 ⇒ LUÔN trả một con số, không "fail".
  * A4a — P3 primary: one-sample Wilcoxon trên Δᵢ per-patient (n lớn) + rank-biserial +
    bootstrap BCa CI. Rank correlation aggregate bị hạ xuống hình mô tả (quan hệ chữ-U-ngược
    + aggregation fallacy làm nó thành dụng cụ SAI).
  * §3 — omnibus Friedman + post-hoc Nemenyi + Critical Difference (Demšar, JMLR 7:1–30, 2006).

Effect size LUÔN đi kèm p-value (CLAUDE.md §3: "nêu effect size, không chỉ p-value").
"""

from __future__ import annotations

import math

import numpy as np
from scipy import stats

# Bảng q_0.05 của Nemenyi (Demšar 2006, Table 5b) — đã chia sẵn cho √2, dùng trực tiếp
# trong công thức CD = q · sqrt(k(k+1)/(6N)). Index = số phương pháp k (2..10).
_NEMENYI_Q05 = {
    2: 1.960, 3: 2.343, 4: 2.569, 5: 2.728, 6: 2.850,
    7: 2.949, 8: 3.031, 9: 3.102, 10: 3.164,
}


# --------------------------------------------------------------------------- #
# A4d — Wilcoxon signed-rank giữ cặp-0 (pratt) + rank-biserial + n_zero/n_total
# --------------------------------------------------------------------------- #
def wilcoxon_signed(x, y=None, zero_method: str = "pratt") -> dict:
    """Wilcoxon signed-rank test — MẶC ĐỊNH ``zero_method="pratt"`` (A4d).

    🔴 KHÔNG dùng "wilcox" (mặc định của scipy): nó LOẠI các cặp hiệu = 0, mà theo P1
    các cặp-0 (hai thuật toán ⇒ mask giống hệt ⇒ hiệu = 0) chính là kết quả của bài.
    "pratt" giữ cặp-0 khi xếp hạng |d| rồi bỏ chúng khỏi tổng thống kê — không vứt mẫu.

    Tham số
    -------
    x, y : nếu có ``y`` ⇒ so sánh cặp trên ``d = x − y``; nếu ``y=None`` ⇒ ``x`` đã là hiệu.
    zero_method : chuyển thẳng cho scipy; giữ mặc định "pratt" trừ khi có lý do rõ.

    Trả về dict:
      * stat          — thống kê Wilcoxon (scipy).
      * p             — p-value hai phía.
      * n_zero        — số cặp có hiệu = 0 CHÍNH XÁC (BÁO CÁO trong MỌI bảng — A4d).
      * n_total       — tổng số cặp.
      * rank_biserial — effect size rank-biserial ∈ [−1, 1] = (W⁺ − W⁻)/(W⁺ + W⁻).
    """
    d = np.asarray(x, dtype=np.float64)
    if y is not None:
        d = d - np.asarray(y, dtype=np.float64)
    d = d.ravel()
    n_total = int(d.size)
    n_zero = int(np.sum(d == 0.0))

    # rank-biserial (pratt): xếp hạng |d| GỒM cả cặp-0, tổng hạng theo dấu.
    absd = np.abs(d)
    ranks = stats.rankdata(absd)
    w_pos = float(ranks[d > 0].sum())
    w_neg = float(ranks[d < 0].sum())
    denom = w_pos + w_neg
    rank_biserial = (w_pos - w_neg) / denom if denom > 0 else 0.0

    if denom == 0:  # mọi hiệu bằng 0 ⇒ hai phương pháp cho ra mask giống hệt tuyệt đối
        return {
            "stat": 0.0, "p": 1.0, "n_zero": n_zero, "n_total": n_total,
            "rank_biserial": 0.0,
        }

    try:
        res = stats.wilcoxon(d, zero_method=zero_method)
        stat, p = float(res.statistic), float(res.pvalue)
    except Exception:  # pragma: no cover - phòng ca suy biến scipy
        stat, p = float(min(w_pos, w_neg)), 1.0

    return {
        "stat": stat, "p": p, "n_zero": n_zero, "n_total": n_total,
        "rank_biserial": float(rank_biserial),
    }


# --------------------------------------------------------------------------- #
# §3 — Friedman + post-hoc Nemenyi + Critical Difference (Demšar 2006)
# --------------------------------------------------------------------------- #
def friedman_nemenyi(data_by_method: dict) -> dict:
    """Friedman omnibus + post-hoc Nemenyi + Critical Difference cho CD-diagram.

    Tham số
    -------
    data_by_method : dict {tên_phương_pháp: array length N (khối/bệnh nhân)}.
        Mọi array phải cùng độ dài N (đo trên CÙNG tập bệnh nhân — nested CV, A3).

    Quy ước hạng: xếp hạng TĂNG DẦN trong mỗi khối (giá trị nhỏ ⇒ hạng nhỏ). Caller tự
    định hướng metric để "hạng thấp = tốt" nếu muốn đọc CD-diagram theo chiều thường lệ.

    Trả về dict:
      * friedman_stat, friedman_p — thống kê & p omnibus (``scipy.stats.friedmanchisquare``).
      * ranks   — dict {method: mean rank}.
      * cd      — Critical Difference ở α=0,05 (Demšar 2006): q·sqrt(k(k+1)/(6N)).
      * nemenyi — dict {(m_i, m_j): {"rank_diff", "significant", "p"}}.
                  significant = |ΔR| > cd ; p qua phân phối studentized-range nếu tính được.
    """
    methods = list(data_by_method.keys())
    k = len(methods)
    if k < 3:
        # Friedman là omnibus ≥ 3 nhóm (scipy cũng đòi vậy); k=2 ⇒ dùng wilcoxon_signed.
        raise ValueError("Friedman cần >= 3 phương pháp (k=2 ⇒ dùng wilcoxon_signed)")
    arrays = [np.asarray(data_by_method[m], dtype=np.float64).ravel() for m in methods]
    N = arrays[0].size
    if any(a.size != N for a in arrays):
        raise ValueError("mọi phương pháp phải cùng số khối N (paired trên cùng bệnh nhân)")
    if N < 2:
        raise ValueError("Friedman cần >= 2 khối")

    # ma trận N x k, xếp hạng trong mỗi hàng (khối).
    M = np.column_stack(arrays)
    block_ranks = np.apply_along_axis(stats.rankdata, 1, M)  # N x k
    mean_ranks = block_ranks.mean(axis=0)
    ranks = {m: float(r) for m, r in zip(methods, mean_ranks)}

    fr = stats.friedmanchisquare(*arrays)
    friedman_stat, friedman_p = float(fr.statistic), float(fr.pvalue)

    q = _NEMENYI_Q05.get(k)
    if q is None:  # k > 10: lấy từ phân phối studentized-range (chia √2)
        try:
            q = float(stats.studentized_range.ppf(0.95, k, np.inf) / math.sqrt(2.0))
        except Exception:  # pragma: no cover
            q = _NEMENYI_Q05[10]
    se = math.sqrt(k * (k + 1) / (6.0 * N))
    cd = float(q * se)

    nemenyi: dict = {}
    for i in range(k):
        for j in range(i + 1, k):
            diff = abs(mean_ranks[i] - mean_ranks[j])
            p_ij = None
            try:
                # q-stat = ΔR / sqrt(k(k+1)/(12N)); p qua studentized-range.
                qstat = diff / math.sqrt(k * (k + 1) / (12.0 * N))
                p_ij = float(stats.studentized_range.sf(qstat, k, np.inf))
                p_ij = min(1.0, max(0.0, p_ij))
            except Exception:  # pragma: no cover
                p_ij = None
            nemenyi[(methods[i], methods[j])] = {
                "rank_diff": float(diff),
                "significant": bool(diff > cd),
                "p": p_ij,
            }

    return {
        "friedman_stat": friedman_stat,
        "friedman_p": friedman_p,
        "ranks": ranks,
        "cd": cd,
        "nemenyi": nemenyi,
    }


# --------------------------------------------------------------------------- #
# A4c — TOST equivalence ↔ 90% CI + delta_ach (LUÔN trả số, KHÔNG "fail")
# --------------------------------------------------------------------------- #
def tost(diff, low, high) -> dict:
    """Two One-Sided Tests cho tương đương, báo cáo theo cách A4c (không "pass/fail").

    Với hiệu theo cặp ``diff`` (vd Dice(algo) − Dice(DP-exact) cấp bệnh nhân) và biên
    tương đương (low, high):

      * ``p``          = p-value TOST = max(p_lower, p_upper) — tương đương ở α nếu p < α.
      * ``ci90_low/high`` = 90% CI của mean(diff) (TOST ở α=0,05 ↔ 90% CI ⊂ (low, high)).
      * ``delta_ach``  = equivalence bound ĐỐI XỨNG NHỎ NHẤT còn giữ tương đương ở α=0,05
        = max(|ci90_low|, |ci90_high|). ⇒ "Equivalence holds for any SESOI ≥ delta_ach."
        LUÔN là một con số hữu hạn ⇒ rủi ro FATAL "TOST fail" biến mất (A4c mục 3).

    Hỗ trợ hierarchy 3 bound (A4c mục 2): gọi hàm ba lần với Δ₁=0,01 / Δ₂ (inter-rater) /
    Δ₃=0,05; ``delta_ach`` độc lập với bound truyền vào nên chỉ cần đọc một lần.
    """
    d = np.asarray(diff, dtype=np.float64).ravel()
    n = d.size
    if n < 2:
        raise ValueError("TOST cần >= 2 quan sát")
    m = float(d.mean())
    sd = float(d.std(ddof=1))
    se = sd / math.sqrt(n)

    if se == 0.0:  # mọi hiệu bằng nhau tuyệt đối ⇒ tương đương chặt tại đúng điểm m
        p = 0.0 if (low < m < high) else 1.0
        return {"p": p, "ci90_low": m, "ci90_high": m, "delta_ach": abs(m)}

    df = n - 1
    t_upper = (m - low) / se       # H0: mean <= low  (test mean > low)
    t_lower = (m - high) / se      # H0: mean >= high (test mean < high)
    p_lower = float(stats.t.sf(t_upper, df))   # phía trên của low
    p_upper = float(stats.t.cdf(t_lower, df))  # phía dưới của high
    p = max(p_lower, p_upper)

    tcrit = float(stats.t.ppf(0.95, df))  # 90% CI ⇒ 0,95 mỗi đuôi
    ci90_low = m - tcrit * se
    ci90_high = m + tcrit * se
    delta_ach = max(abs(ci90_low), abs(ci90_high))

    return {
        "p": float(p),
        "ci90_low": float(ci90_low),
        "ci90_high": float(ci90_high),
        "delta_ach": float(delta_ach),
    }


# --------------------------------------------------------------------------- #
# A4c — Bayesian signed-rank + ROPE (Benavoli et al. 2017) — PRIMARY equivalence
# --------------------------------------------------------------------------- #
def bayesian_signed_rank(
    diff, rope=(-0.01, 0.01), n_samples: int = 20000, seed: int = 0, prior_strength: float = 1.0,
) -> dict:
    """Bayesian signed-rank test với ROPE (Benavoli et al., JMLR 2017) — PRIMARY (A4c).

    Không có khái niệm "fail"; xử lý spike-tại-0 (mask giống hệt ⇒ hiệu = 0) tự nhiên
    qua một pseudo-quan-sát Dirac tại 0 với trọng số ``prior_strength``.

    Implementation (có tên — A7): prior Dirichlet-process (Benavoli 2017 §2). Mỗi mẫu
    Monte-Carlo rút trọng số ``w ~ Dirichlet(prior_strength, 1, …, 1)`` trên {0} ∪ {diffᵢ}.
    Thống kê signed-rank xét trung bình cặp (vᵢ + vⱼ)/2 ∀ i ≤ j; phân loại từng cặp vào
    left / rope / right theo ROPE, rồi tính khối lượng ``Σ wᵢ wⱼ 1[(vᵢ+vⱼ)/2 ∈ vùng]``.
    Mỗi mẫu chọn vùng có khối lượng LỚN NHẤT làm "thắng"; xác suất trả về = tỷ lệ mẫu
    mỗi vùng thắng ⇒ ``p_left + p_rope + p_right = 1``.

    Trả về dict {p_left, p_rope, p_right} (tổng = 1). ``rope=(low, high)`` = vùng tương đương.
    """
    d = np.asarray(diff, dtype=np.float64).ravel()
    low, high = float(rope[0]), float(rope[1])

    # {0} (pseudo, prior) ∪ dữ liệu.  concentration: [prior_strength, 1, 1, ...].
    vals = np.concatenate([[0.0], d])
    m = vals.size
    conc = np.concatenate([[float(prior_strength)], np.ones(d.size)])

    # Phân loại vùng của trung bình cặp — CỐ ĐỊNH theo dữ liệu (không phụ thuộc w).
    pair_mean = (vals[:, None] + vals[None, :]) / 2.0  # m x m, đối xứng
    left = (pair_mean < low).astype(np.float64)
    right = (pair_mean > high).astype(np.float64)
    inrope = ((pair_mean >= low) & (pair_mean <= high)).astype(np.float64)

    rng = np.random.default_rng(seed)
    # w ~ Dirichlet(conc): rút Gamma(conc,1) rồi chuẩn hoá. W: n_samples x m.
    g = rng.gamma(shape=conc, scale=1.0, size=(n_samples, m))
    W = g / g.sum(axis=1, keepdims=True)

    # khối lượng mỗi vùng cho từng mẫu = wᵀ M w (dạng bậc hai).
    mass_left = np.einsum("si,ij,sj->s", W, left, W)
    mass_rope = np.einsum("si,ij,sj->s", W, inrope, W)
    mass_right = np.einsum("si,ij,sj->s", W, right, W)

    masses = np.column_stack([mass_left, mass_rope, mass_right])
    winners = np.argmax(masses, axis=1)  # 0=left, 1=rope, 2=right
    p_left = float(np.mean(winners == 0))
    p_rope = float(np.mean(winners == 1))
    p_right = float(np.mean(winners == 2))
    return {"p_left": p_left, "p_rope": p_rope, "p_right": p_right}


# --------------------------------------------------------------------------- #
# A4a — one-sample Wilcoxon trên Δᵢ per-patient (P3 primary)
# --------------------------------------------------------------------------- #
def one_sample_wilcoxon_delta(delta, sesoi) -> dict:
    """PRIMARY cho P3 (A4a): Δᵢ = Diceᵢ(k*_Dice) − Diceᵢ(k*_PSNR) per-patient.

    One-sample Wilcoxon trên {Δᵢ} (H0: median = 0) với ``zero_method="pratt"`` (A4d),
    + rank-biserial + bootstrap BCa CI của median (over patients).

    Headline = một CHI PHÍ có đơn vị lâm sàng: "chọn k bằng PSNR như văn liệu khiến bệnh
    nhân mất median Δ Dice."

    Thành công (A4a — cả ba phải đúng):
      1. median(Δ) > sesoi,
      2. p < 0,05,
      3. CI 95% KHÔNG chứa ``sesoi``.

    Trả về dict: n, median, p, rank_biserial, ci_low, ci_high, sesoi, success
    (+ ba cờ thành phần success_median / success_p / success_ci).
    """
    d = np.asarray(delta, dtype=np.float64).ravel()
    n = int(d.size)
    med = float(np.median(d)) if n > 0 else float("nan")

    w = wilcoxon_signed(d, zero_method="pratt")
    p = w["p"]
    rank_biserial = w["rank_biserial"]

    ci_low, ci_high = bootstrap_ci(d, stat=np.median, ci=95)

    success_median = med > sesoi
    success_p = p < 0.05
    success_ci = not (ci_low <= sesoi <= ci_high)  # CI không chứa SESOI
    success = bool(success_median and success_p and success_ci)

    return {
        "n": n,
        "median": med,
        "p": float(p),
        "rank_biserial": float(rank_biserial),
        "ci_low": float(ci_low),
        "ci_high": float(ci_high),
        "sesoi": float(sesoi),
        "n_zero": w["n_zero"],
        "n_total": w["n_total"],
        "success_median": bool(success_median),
        "success_p": bool(success_p),
        "success_ci": bool(success_ci),
        "success": success,
    }


# --------------------------------------------------------------------------- #
# Bootstrap CI — BCa (median [IQR] + 95% bootstrap CI là chuẩn trình bày Dice, A7)
# --------------------------------------------------------------------------- #
def bootstrap_ci(values, stat=np.median, n: int = 10000, seed: int = 0, ci: float = 95):
    """Bootstrap CI cho một thống kê (mặc định median) — BCa, fallback percentile.

    BCa (bias-corrected and accelerated, Efron 1987): hiệu chỉnh bias qua z₀ và độ lệch
    qua gia tốc ``a`` (jackknife) ⇒ CI chính xác hơn percentile cho thống kê lệch như
    median của Dice (A7: "median [IQR] + 95% bootstrap CI"). Khi z₀/a suy biến (mọi
    resample cho cùng giá trị, hoặc jackknife bằng phẳng) ⇒ lùi về percentile bootstrap.

    Trả về (lo, hi). Danh sách rỗng ⇒ (nan, nan); một phần tử ⇒ (v, v) (không bịa CI).
    """
    v = np.asarray(values, dtype=np.float64).ravel()
    v = v[~np.isnan(v)]
    m = v.size
    if m == 0:
        return (float("nan"), float("nan"))
    if m == 1:
        return (float(v[0]), float(v[0]))

    alpha = (1.0 - ci / 100.0) / 2.0
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, m, size=(n, m))
    resamples = v[idx]
    try:
        boot = np.asarray(stat(resamples, axis=1), dtype=np.float64)
    except TypeError:  # stat không nhận axis
        boot = np.array([float(stat(v[i])) for i in idx], dtype=np.float64)

    def _percentile_ci():
        return (
            float(np.percentile(boot, 100.0 * alpha)),
            float(np.percentile(boot, 100.0 * (1.0 - alpha))),
        )

    theta_hat = float(stat(v))
    # z0: hiệu chỉnh bias.
    prop = (np.sum(boot < theta_hat) + 0.5 * np.sum(boot == theta_hat)) / n
    if prop <= 0.0 or prop >= 1.0:
        return _percentile_ci()
    z0 = float(stats.norm.ppf(prop))

    # gia tốc a qua jackknife leave-one-out.
    jack = np.array([float(stat(np.delete(v, i))) for i in range(m)], dtype=np.float64)
    jbar = jack.mean()
    diff = jbar - jack
    denom = 6.0 * (np.sum(diff ** 2) ** 1.5)
    if denom == 0.0:
        return _percentile_ci()
    a_acc = float(np.sum(diff ** 3) / denom)

    z_lo = float(stats.norm.ppf(alpha))
    z_hi = float(stats.norm.ppf(1.0 - alpha))

    def _adjust(z):
        denom_z = 1.0 - a_acc * (z0 + z)
        if denom_z == 0.0:
            return None
        return float(stats.norm.cdf(z0 + (z0 + z) / denom_z))

    a1 = _adjust(z_lo)
    a2 = _adjust(z_hi)
    if a1 is None or a2 is None or not (0.0 < a1 < 1.0) or not (0.0 < a2 < 1.0) or a1 >= a2:
        return _percentile_ci()

    return (
        float(np.percentile(boot, 100.0 * a1)),
        float(np.percentile(boot, 100.0 * a2)),
    )

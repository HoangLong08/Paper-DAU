"""MODULE D — decoding (vector ngưỡng → binary mask) + oracle (trần Dice).

Đây là cột sống thực nghiệm của **P1** (thế lưỡng nan suy biến) và **P4** (trần đúng).
Đọc `docs/preregistration.md` §6/A1 và §6/A2 — code dưới đây bake chính xác hai amendment
đó. Mọi phát biểu về trần/decoding phải khớp từng chữ với chúng.

---------------------------------------------------------------------------
⚠️ A1 — P1 LÀ THẾ LƯỠNG NAN, KHÔNG PHẢI QUY KẾT (đọc trước khi sửa)
---------------------------------------------------------------------------
Quy tắc "lớp sáng nhất" (`brightest`, tức `label == k` ⇔ `pixel >= t_k`) **KHÔNG TÌM
THẤY TRONG VĂN LIỆU** — nó là **code cũ của chính chúng ta**. TUYỆT ĐỐI không viết
code, comment, hay docstring nào quy kết *"văn liệu decode bằng lớp sáng nhất [refs]"*
— đó là xuyên tạc công trình được trích dẫn ⇒ vi phạm IRON RULE 2 (CLAUDE.md §2), nặng
hơn cả rủi ro bị reject.

`brightest` ở đây là rule ta **KIỂM TRA** (một khả năng — "Horn 1"), không phải rule ta
**quy kết** cho ai. P1 được kiểm bằng cả hai sừng:

  * Horn 1 — band-selection (mọi hàm trong :data:`RULES`): mask chỉ phụ thuộc **nhiều
    nhất 2** ngưỡng (với `brightest`: đúng 1, là `t_k`) ⇒ k−1 ngưỡng là biến giả, và
    toàn bộ máy Q-bit/rotation-gate/Lévy/memetic đang tối ưu biến không ảnh hưởng output.
  * Horn 2 — label-map segmenter (mọi hàm trong :data:`LABELMAP_DECODERS`): mask do
    **segmenter hạ nguồn** tạo ra ⇒ tầng thresholding CHƯA TỪNG được ablate ⇒ claim
    nhân quả "optimizer tốt hơn ⇒ mask tốt hơn" là CHƯA ĐƯỢC KIỂM.

Metric quyết định của P1 nhóm theo **MASK HASH** (:func:`mask_hash`), KHÔNG theo `t_max`
— vì `otsu_pick` tạo đường phụ thuộc thật `{t_1..t_k} → chỉ số band → mask`, nhóm theo
band đã chọn sẽ "conditioning away" chính hiện tượng cần đo.

---------------------------------------------------------------------------
⚠️ A2 — TRẦN ĐÚNG là oracle level-set, KHÔNG phải oracle-1-khoảng
---------------------------------------------------------------------------
* :func:`oracle_single`   — trần của decoding "lớp sáng nhất" (một superlevel-set).
* :func:`oracle_interval` — trần của MỌI band-selection LIÊN TIẾP — nhưng **KHÔNG** phải
  trần tuyệt đối (decoder chọn lớp KHÔNG liên tiếp vượt nó).
* :func:`oracle_levelset` — **TRẦN ĐÚNG**: oracle trên tập mức xám tuỳ ý
  ``S ⊆ {0..L-1}``, dạng tổng quát nhất của *mọi* decoder chỉ-dùng-cường-độ.

  Đây là một linear-fractional 0/1 program; nghiệm tối ưu LUÔN là superlevel-set của
  **purity** ``r_v = g_v / n_v`` ⇒ sắp mức xám theo ``r_v`` giảm dần, quét prefix, lấy
  max ⇒ nghiệm CHÍNH XÁC trong ``O(L log L)``.

  ⛔ KHÔNG claim đây là định lý của mình. Đã có chủ:
    - Lipton, Elkan & Narayanaswamy, "Thresholding Classifiers to Maximize F1 Score",
      arXiv:1402.1892 (ECML-PKDD 2014) — "the optimal threshold is half the optimal F1".
    - Dai & Li, "RankSEG", JMLR 2023.
  Dice = F1; purity = posterior đã calibrate ⇒ **CLAIM ỨNG DỤNG, KHÔNG CLAIM TOÁN HỌC**.

  ⛔ CẤM TUYỆT ĐỐI câu "we establish the ceiling": François & Tinarrage (J. Math. Imaging
  & Vision 68, 20, 2026, doi:10.1007/s10851-026-01300-1) đã in trần 0.83±0.18 trên BraTS
  FLAIR. Ta claim **phân rã** trần, không claim thiết lập trần.

Quy ước chung (khớp module A/B/C): L=256; ảnh uint8 [0,255]; k ngưỡng int [1,255] tăng
ngặt phân [0,255] thành k+1 lớp — lớp 0 = [0, t_1-1], lớp j = [t_j, t_{j+1}-1], lớp cuối
k = [t_k, 255]. Nhãn lớp = số ngưỡng ``<= v`` (``np.searchsorted(thr, v, side="right")``).
"""

from __future__ import annotations

import hashlib

import numpy as np

L = 256

#: Band-selection decoders (Horn-1). Mỗi rule chọn MỘT dải lớp liên tiếp ⇒ mask phụ
#: thuộc <= 2 ngưỡng bất kể k. `primary decoding rule = "brightest"` (prereg §6/A4e).
RULES = ("brightest", "upper_union", "otsu_pick", "morph")

#: Label-map decoders (Horn-2, A1). Tiêu thụ TOÀN BỘ label map bằng một segmenter hạ
#: nguồn ⇒ mask do segmenter tạo, không phải do một ngưỡng đơn lẻ.
LABELMAP_DECODERS = ("kmeans", "watershed", "chanvese")


# --------------------------------------------------------------------------- #
# Label map
# --------------------------------------------------------------------------- #
def label_map(thresholds, img_uint8) -> np.ndarray:
    """Gán mỗi pixel nhãn lớp 0..k theo k ngưỡng (khớp quy ước module A/B/C).

    Nhãn của pixel cường độ ``v`` = số ngưỡng ``<= v`` = ``searchsorted(thr, v, 'right')``.
    ⇒ lớp 0 = [0, t_1-1], lớp j = [t_j, t_{j+1}-1], lớp cuối k = [t_k, 255].

    ``thresholds`` được sắp tăng phòng hờ; giá trị lặp tạo lớp rỗng (không lỗi).
    """
    img = np.asarray(img_uint8)
    thr = np.asarray(sorted(int(t) for t in thresholds), dtype=np.int64)
    if thr.size == 0:
        return np.zeros(img.shape, dtype=np.int64)
    return np.searchsorted(thr, img, side="right").astype(np.int64)


# --------------------------------------------------------------------------- #
# Horn-1: band-selection decoders
# --------------------------------------------------------------------------- #
def _otsu_1d(values: np.ndarray) -> float:
    """Ngưỡng Otsu (between-class variance cực đại) trên một mảng giá trị 1D.

    Numpy thuần (không phụ thuộc skimage) ⇒ `otsu_pick` là rule lõi, luôn chạy được.
    Trả về ngưỡng ``c`` sao cho nhóm ``values > c`` là "foreground".
    """
    vals = np.asarray(values).ravel()
    lo, hi = int(vals.min()), int(vals.max())
    if hi <= lo:
        return float(lo)
    hist = np.bincount((vals - lo).astype(np.int64), minlength=hi - lo + 1).astype(np.float64)
    p = hist / hist.sum()
    levels = np.arange(lo, hi + 1, dtype=np.float64)
    w0 = np.cumsum(p)
    w1 = 1.0 - w0
    mu = np.cumsum(p * levels)
    mu_t = mu[-1]
    denom = w0 * w1
    with np.errstate(divide="ignore", invalid="ignore"):
        sigma_b = np.where(denom > 0, (mu_t * w0 - mu) ** 2 / denom, 0.0)
    idx = int(np.argmax(sigma_b))
    return float(levels[idx])


def decode(thresholds, img_uint8, rule: str, **kw) -> np.ndarray:
    """Horn-1 — ánh xạ vector k ngưỡng → binary mask bằng một quy tắc chọn-dải-lớp.

    Mọi rule ở đây chọn một dải lớp liên tiếp ⇒ mask phụ thuộc <= 2 ngưỡng (A1).

    rule
    ----
    "brightest"   : lớp sáng nhất, ``label == k`` ⇔ ``pixel >= t_k`` (phụ thuộc ĐÚNG 1
                    ngưỡng). ĐÂY LÀ rule ta KIỂM TRA, KHÔNG phải rule ta quy kết cho văn
                    liệu (A1). Rule primary của preregistration (§6/A4e).
    "upper_union" : hợp các lớp trên cùng, ``pixel >= t_j`` với j quét; mặc định
                    ``j = ngưỡng giữa`` (1-based), override qua ``j=<int>``.
    "otsu_pick"   : chọn lớp bằng ngưỡng Otsu hai tầng TRÊN LABEL MAP (Otsu trên nhãn lớp
                    ⇒ tách nhóm lớp sáng/tối, foreground = nhóm lớp sáng). Rule này tạo
                    đường phụ thuộc thật ``{t_1..t_k} → band → mask`` (lý do A1 nhóm theo
                    mask hash chứ không theo t_max).
    "morph"       : "brightest" + hậu xử lý hình thái (opening→closing) + giữ thành phần
                    liên thông LỚN NHẤT (cần scikit-image).

    Trả về mask bool cùng shape ảnh.
    """
    if rule not in RULES:
        raise ValueError(f"rule không hợp lệ: {rule!r} — chọn trong {RULES}")

    img = np.asarray(img_uint8)
    thr = sorted(int(t) for t in thresholds)
    k = len(thr)
    lab = label_map(thr, img)

    if rule == "brightest":
        # label == k  <=>  pixel >= t_k. Phụ thuộc ĐÚNG 1 ngưỡng (A1, Horn-1).
        return lab == k if k > 0 else np.ones(img.shape, dtype=bool)

    if rule == "upper_union":
        if k == 0:
            return np.ones(img.shape, dtype=bool)
        j = int(kw.get("j", (k + 1) // 2))          # 1-based; mặc định ngưỡng giữa
        j = max(1, min(j, k))
        return img >= thr[j - 1]                     # = (label >= j)

    if rule == "otsu_pick":
        if k == 0:
            return np.ones(img.shape, dtype=bool)
        # Otsu trên chính label map (giá trị 0..k) ⇒ cắt tại một chỉ số lớp `c`,
        # foreground = các lớp > c (nhóm lớp sáng). Nếu chỉ 1 lớp hiện diện ⇒ brightest.
        present = np.unique(lab)
        if present.size < 2:
            return lab == k
        cut = _otsu_1d(lab)
        mask = lab > cut
        if not mask.any():                           # phòng suy biến ⇒ lùi về brightest
            mask = lab == k
        return mask

    # rule == "morph"
    base = (lab == k) if k > 0 else np.ones(img.shape, dtype=bool)
    return _morph_postprocess(base, **kw)


def _morph_postprocess(mask: np.ndarray, radius: int = 2, **_) -> np.ndarray:
    """Opening→closing (disk bán kính `radius`) + giữ thành phần liên thông lớn nhất.

    Cần scikit-image; import trễ để module vẫn nạp được khi chưa cài skimage (chỉ
    `morph`/Horn-2 mới đòi dep — band rule khác và oracle là numpy thuần).
    """
    from skimage.measure import label as cc_label
    from skimage.morphology import binary_closing, binary_opening, disk

    m = np.asarray(mask, dtype=bool)
    if not m.any():
        return m
    se = disk(radius)
    m = binary_closing(binary_opening(m, se), se)
    if not m.any():
        return m
    lab = cc_label(m)
    sizes = np.bincount(lab.ravel())
    sizes[0] = 0                                     # bỏ nền
    if sizes.max() == 0:
        return np.zeros_like(m)
    return lab == int(np.argmax(sizes))


# --------------------------------------------------------------------------- #
# Horn-2: label-map segmenters (tiêu thụ TOÀN BỘ label map)
# --------------------------------------------------------------------------- #
def decode_labelmap(thresholds, img_uint8, method: str, **kw) -> np.ndarray:
    """Horn-2 (A1) — decode bằng một segmenter hạ nguồn tiêu thụ TOÀN BỘ label map.

    Ở sừng này của thế lưỡng nan, mask do **segmenter** tạo, không phải do một ngưỡng.

    method
    ------
    "kmeans"    : KMeans trên cường độ với k+1 cụm (khởi tạo từ trung bình cường độ mỗi
                  lớp của label map) rồi chọn cụm SÁNG NHẤT. Cần scikit-learn.
    "watershed" : watershed trên gradient ảnh, markers lấy từ label map (nền = lớp 0,
                  foreground seed = lớp sáng nhất k); mask = vùng nảy từ seed sáng. Cần
                  scikit-image.
    "chanvese"  : Chan–Vese khởi tạo từ vùng sáng (lớp k) của label map; chọn pha phủ
                  vùng khởi tạo. Cần scikit-image.

    Trả về mask bool cùng shape ảnh.
    """
    if method not in LABELMAP_DECODERS:
        raise ValueError(f"method không hợp lệ: {method!r} — chọn trong {LABELMAP_DECODERS}")
    img = np.asarray(img_uint8)
    thr = sorted(int(t) for t in thresholds)
    k = len(thr)
    lab = label_map(thr, img)

    if method == "kmeans":
        return _decode_kmeans(img, lab, k, seed=int(kw.get("seed", 0)))
    if method == "watershed":
        return _decode_watershed(img, lab, k)
    return _decode_chanvese(img, lab, k, **kw)      # chanvese


def _decode_kmeans(img, lab, k, seed=0) -> np.ndarray:
    from sklearn.cluster import KMeans

    vals = img.reshape(-1, 1).astype(np.float64)
    uniq = np.unique(vals)
    n_clusters = int(min(k + 1, uniq.size))
    if n_clusters <= 1:
        return np.zeros(img.shape, dtype=bool)      # ảnh gần hằng ⇒ không có cụm sáng riêng

    # Khởi tạo tâm cụm từ trung bình cường độ mỗi lớp của label map ⇒ "tiêu thụ label map".
    means = []
    for c in range(k + 1):
        sel = lab.ravel() == c
        if sel.any():
            means.append(float(vals[sel].mean()))
    means = np.array(sorted(set(round(m, 6) for m in means)))
    if means.size >= n_clusters:
        pick = np.linspace(0, means.size - 1, n_clusters).round().astype(int)
        init = means[np.unique(pick)][:n_clusters].reshape(-1, 1)
        if init.shape[0] == n_clusters:
            km = KMeans(n_clusters=n_clusters, init=init, n_init=1, random_state=seed)
        else:
            km = KMeans(n_clusters=n_clusters, init="k-means++", n_init=10, random_state=seed)
    else:
        km = KMeans(n_clusters=n_clusters, init="k-means++", n_init=10, random_state=seed)

    labels = km.fit_predict(vals)
    brightest_cluster = int(np.argmax(km.cluster_centers_.ravel()))
    return (labels == brightest_cluster).reshape(img.shape)


def _decode_watershed(img, lab, k) -> np.ndarray:
    from skimage.filters import sobel
    from skimage.segmentation import watershed

    elevation = sobel(img.astype(np.float64))
    markers = np.zeros(img.shape, dtype=np.int32)
    markers[lab == 0] = 1                            # nền (lớp tối nhất)
    top = k                                          # lớp sáng nhất hiện diện
    while top > 0 and not np.any(lab == top):
        top -= 1
    if top == 0:
        return np.zeros(img.shape, dtype=bool)       # không có lớp sáng tách biệt
    markers[lab == top] = 2                          # foreground seed (lớp sáng nhất)
    ws = watershed(elevation, markers)
    return ws == 2


def _decode_chanvese(img, lab, k, max_num_iter: int = 100, **_) -> np.ndarray:
    from skimage.segmentation import chan_vese

    init = (lab == k) if k > 0 else np.ones(img.shape, dtype=bool)
    if not init.any():
        return np.zeros(img.shape, dtype=bool)
    rng = float(img.max()) - float(img.min())
    norm = (img.astype(np.float64) - float(img.min())) / (rng if rng > 0 else 1.0)
    cv = chan_vese(
        norm,
        mu=0.25,
        init_level_set=init.astype(np.float64),
        max_num_iter=max_num_iter,
        extended_output=False,
    )
    cv = np.asarray(cv, dtype=bool)
    # Chan–Vese không cố định pha nào là foreground ⇒ chọn pha phủ vùng khởi tạo nhiều hơn.
    if np.logical_and(cv, init).sum() >= np.logical_and(~cv, init).sum():
        return cv
    return ~cv


# --------------------------------------------------------------------------- #
# Oracle (A2) — trần Dice nới dần: single <= interval <= levelset
# --------------------------------------------------------------------------- #
def _level_counts(img_uint8, gt_mask):
    """(n_v, g_v, |G|): số pixel / số pixel-GT tại mỗi mức xám v∈[0,255], và |GT|."""
    img = np.asarray(img_uint8)
    gt = np.asarray(gt_mask, dtype=bool)
    flat = img.ravel()
    gtf = gt.ravel()
    n_v = np.bincount(flat, minlength=L).astype(np.int64)[:L]
    g_v = np.bincount(flat[gtf], minlength=L).astype(np.int64)[:L]
    return n_v, g_v, int(gtf.sum())


def oracle_single(img_uint8, gt_mask):
    """Vét cạn 254 ngưỡng: mask = ``pixel >= t``, chọn Dice cao nhất (A2).

    Trần của decoding "lớp sáng nhất". Trả ``(mask, dice, t)``. O(L) qua suffix-sum.
    """
    img = np.asarray(img_uint8)
    n_v, g_v, G = _level_counts(img, gt_mask)
    suf_n = np.cumsum(n_v[::-1])[::-1]               # suf_n[t] = Σ_{v>=t} n_v
    suf_g = np.cumsum(g_v[::-1])[::-1]
    ts = np.arange(1, L)                             # ngưỡng khả dĩ [1,255]
    tp = suf_g[1:L].astype(np.float64)
    sz = suf_n[1:L].astype(np.float64)
    den = sz + G
    with np.errstate(divide="ignore", invalid="ignore"):
        dice = np.where(den > 0, 2.0 * tp / den, 1.0)  # den==0 ⇒ pred&GT đều rỗng ⇒ 1.0
    i = int(np.argmax(dice))
    t = int(ts[i])
    mask = img >= t
    return mask, float(dice[i]), t


def oracle_interval(img_uint8, gt_mask):
    """Vét cạn mọi cặp (lo,hi): mask = ``lo <= pixel <= hi``, chọn Dice cao nhất (A2).

    Trần của MỌI band-selection LIÊN TIẾP — nhưng KHÔNG phải trần tuyệt đối (tập lớp
    KHÔNG liên tiếp vượt nó; xem A2 và :func:`oracle_levelset`). Trả ``(mask, dice, (lo,hi))``.
    """
    img = np.asarray(img_uint8)
    n_v, g_v, G = _level_counts(img, gt_mask)
    cum_n = np.concatenate([[0], np.cumsum(n_v)]).astype(np.float64)   # cum[v+1]=Σ_{0..v}
    cum_g = np.concatenate([[0], np.cumsum(g_v)]).astype(np.float64)

    best_dice, best_lo, best_hi = -1.0, 1, L - 1
    for lo in range(L):
        his = np.arange(lo, L)
        tp = cum_g[his + 1] - cum_g[lo]
        sz = cum_n[his + 1] - cum_n[lo]
        den = sz + G
        with np.errstate(divide="ignore", invalid="ignore"):
            dice = np.where(den > 0, 2.0 * tp / den, 1.0)
        j = int(np.argmax(dice))
        if dice[j] > best_dice:
            best_dice, best_lo, best_hi = float(dice[j]), lo, int(his[j])
    mask = (img >= best_lo) & (img <= best_hi)
    return mask, best_dice, (best_lo, best_hi)


def oracle_levelset(img_uint8, gt_mask):
    """TRẦN ĐÚNG (A2): oracle trên tập mức xám tuỳ ý S ⊆ {0..255}, O(L log L).

    Linear-fractional 0/1 program ``max_S 2·Σ_{v∈S} g_v / (Σ_{v∈S} n_v + |G|)``. Nghiệm
    tối ưu luôn là superlevel-set của purity ``r_v = g_v/n_v`` ⇒ sắp mức theo r_v giảm
    dần, quét prefix, lấy max.

    ⛔ KHÔNG claim toán học là của mình — Lipton, Elkan & Narayanaswamy (arXiv:1402.1892,
    2014) + RankSEG (Dai & Li, JMLR 2023) sở hữu định lý. CLAIM ỨNG DỤNG. Và CẤM câu "we
    establish the ceiling" (François & Tinarrage, JMIV 2026, đã in trần 0.83 trên BraTS).

    Trả ``(mask, dice)``. Trần này >= oracle_interval >= oracle_single về Dice.
    """
    img = np.asarray(img_uint8)
    n_v, g_v, G = _level_counts(img, gt_mask)
    levels = np.where(n_v > 0)[0]

    best_dice = 1.0 if G == 0 else 0.0               # ứng viên tập RỖNG (pred rỗng)
    sel_levels = np.empty(0, dtype=np.int64)

    if levels.size > 0:
        r = g_v[levels].astype(np.float64) / n_v[levels].astype(np.float64)   # purity
        order = np.argsort(-r, kind="stable")        # purity giảm dần
        sorted_levels = levels[order]
        cg = np.cumsum(g_v[sorted_levels]).astype(np.float64)
        cn = np.cumsum(n_v[sorted_levels]).astype(np.float64)
        den = cn + G
        with np.errstate(divide="ignore", invalid="ignore"):
            dice_prefix = np.where(den > 0, 2.0 * cg / den, 1.0)
        j = int(np.argmax(dice_prefix))
        if dice_prefix[j] >= best_dice:
            best_dice = float(dice_prefix[j])
            sel_levels = sorted_levels[: j + 1]

    if sel_levels.size == 0:
        mask = np.zeros(img.shape, dtype=bool)
    else:
        mask = np.isin(img, sel_levels)
    return mask, best_dice


# --------------------------------------------------------------------------- #
# Mask identity (A1 headline: "X/n bệnh nhân cho mask GIỐNG HỆT byte-for-byte")
# --------------------------------------------------------------------------- #
def mask_hash(mask) -> str:
    """SHA-256 hex của mask bool đã pack bit (:func:`numpy.packbits`).

    Định danh mask ổn định, byte-for-byte — nền của MASK-IDENTITY RATE (prereg §6/A0) và
    của metric quyết định P1 (nhóm theo mask hash, KHÔNG theo t_max — A1). Shape được
    băm cùng để hai mask khác shape không bao giờ đụng độ.
    """
    m = np.ascontiguousarray(np.asarray(mask, dtype=bool))
    h = hashlib.sha256()
    h.update(np.asarray(m.shape, dtype=np.int64).tobytes())
    h.update(np.packbits(m.ravel()).tobytes())
    return h.hexdigest()

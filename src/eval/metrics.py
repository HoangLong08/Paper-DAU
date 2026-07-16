"""Trắc lượng segmentation cho pipeline QIGOA Reality-Check (docs/preregistration.md §6/A7).

Đây là tầng ĐO. Vì bài đi tố cáo dòng văn liệu đo sai (PSNR/SSIM/FSIM tự chế, không
Dice, không ground truth), MỌI quy ước ở đây phải khoá trước khi chạy và MỌI
implementation phải có TÊN — cấm implementation vô danh (A7, lặp lại tội "FSIM tự chế"
của lô cũ commit c4fe108).

Bộ metric khoá (A7):
  * dice                  — overlap chính, median [IQR] là cách trình bày chuẩn.
  * hd95                  — sai số biên; mask rỗng xử lý bằng HÌNH PHẠT CỐ ĐỊNH đã khai.
  * nsd (τ = 2 mm)        — Normalized Surface Dice, primary tolerance 2 mm.
  * n_connected_components— "output thresholding có N cục; khối u có 1" (bằng chứng lâm sàng).
  * empty_mask_rate       — tỷ lệ mask rỗng theo k (KẾT QUẢ ĐỘC LẬP cho P3, A7).
  * psnr / ssim           — wrapper MỎNG quanh skimage.metrics (bằng chứng cho P3,
                            KHÔNG phải kết quả; KHÔNG tự chế — A7).

ĐÃ BỎ (A7):
  * IoU  — song ánh đơn điệu với Dice (IoU = D/(2−D)) ⇒ không thêm một bit thông tin.
  * FSIM — lô cũ "tự thú not the full FSIM"; không dùng lại.

Quy ước rỗng (A7 — KHOÁ, ba cách xử lý khác nhau = ba bài báo khác nhau):
  * Dice:  cả hai rỗng ⇒ 1.0 ; GT≠rỗng & pred rỗng ⇒ 0.0 (theo công thức, intersection=0).
  * HD95:  cả hai rỗng ⇒ 0.0 ; đúng một bên rỗng ⇒ ``empty_penalty``
           (mặc định = đường chéo ảnh theo spacing = sqrt((H·sy)² + (W·sx)²)).
           🔴 CẤM âm thầm loại ca mask rỗng khỏi thống kê HD95 (selection bias có lợi
           cho thresholding ở k lớn ⇒ phá P3). Báo cáo empty_mask_rate riêng thay vì bỏ.
  * NSD:   cả hai rỗng ⇒ 1.0 ; đúng một bên rỗng ⇒ 0.0.

Backend khoảng-cách-biên (A7 — nêu TÊN implementation):
  * hd95 / nsd ưu tiên ``medpy`` hoặc ``surface_distance`` nếu import được; nếu KHÔNG,
    dùng fallback tự cài có tên **"boundary-EDT percentile (medpy-style)"**: trích biên
    bằng ``scipy.ndimage.binary_erosion`` rồi lấy khoảng cách mặt đối xứng qua
    ``scipy.ndimage.distance_transform_edt(sampling=spacing)``. spacing = (sy, sx) theo
    trục mảng (hàng, cột); BraTS in-plane 1 mm isotropic ⇒ spacing mặc định (1.0, 1.0).
"""

from __future__ import annotations

import math

import numpy as np
from scipy import ndimage

# --------------------------------------------------------------------------- #
# Backend HD95/NSD: ưu tiên lib chuẩn, else fallback boundary-EDT có tên rõ.
# --------------------------------------------------------------------------- #
try:  # pragma: no cover - phụ thuộc môi trường
    from medpy.metric.binary import hd95 as _medpy_hd95  # type: ignore

    _HD_BACKEND = "medpy"
except Exception:  # pragma: no cover
    _medpy_hd95 = None
    _HD_BACKEND = "boundary-EDT (self)"


def _as_bool(mask) -> np.ndarray:
    """Ép mask về ndarray bool (LIÊM CHÍNH: không diễn giải ngầm ngưỡng khác 0)."""
    m = np.asarray(mask)
    if m.dtype != np.bool_:
        m = m.astype(bool)
    return m


def _image_diagonal(shape, spacing) -> float:
    """Đường chéo ảnh theo spacing = sqrt(Σ (dim_i · spacing_i)²) — hình phạt HD95 mặc định (A7)."""
    spacing = _match_spacing(spacing, len(shape))
    return float(math.sqrt(sum((d * s) ** 2 for d, s in zip(shape, spacing))))


def _match_spacing(spacing, ndim) -> tuple[float, ...]:
    """Chuẩn hoá spacing thành tuple độ dài ndim (scalar ⇒ lặp lại)."""
    if np.isscalar(spacing):
        return tuple(float(spacing) for _ in range(ndim))
    sp = tuple(float(s) for s in spacing)
    if len(sp) != ndim:
        raise ValueError(f"spacing {sp} không khớp số chiều mask ({ndim})")
    return sp


# --------------------------------------------------------------------------- #
# Dice
# --------------------------------------------------------------------------- #
def dice(pred, gt) -> float:
    """Dice similarity coefficient = 2·|pred ∩ gt| / (|pred| + |gt|).

    Quy ước rỗng (A7 — KHOÁ):
      * cả hai rỗng ⇒ **1.0** (không có gì để phân đoạn, và ta cũng không phân đoạn gì).
      * GT≠rỗng & pred rỗng ⇒ **0.0** (theo đúng công thức: giao = 0, mẫu = |gt| > 0).
      * pred≠rỗng & GT rỗng ⇒ **0.0** (đối xứng).
    """
    p = _as_bool(pred)
    g = _as_bool(gt)
    ps, gs = int(p.sum()), int(g.sum())
    if ps == 0 and gs == 0:
        return 1.0
    inter = int(np.logical_and(p, g).sum())
    return float(2.0 * inter / (ps + gs))


# --------------------------------------------------------------------------- #
# Khoảng cách biên (surface) dùng chung cho HD95 & NSD — fallback boundary-EDT.
# --------------------------------------------------------------------------- #
def _surface(mask: np.ndarray) -> np.ndarray:
    """Biên của mask = voxel thuộc mask nhưng có ít nhất một hàng xóm nền.

    Dùng ``binary_erosion`` với ``border_value=0`` (voxel chạm mép ảnh là biên).
    Kết nối trực giao (mặc định) — đủ cho định nghĩa mặt trong lưới đều.
    """
    if not mask.any():
        return np.zeros_like(mask, dtype=bool)
    eroded = ndimage.binary_erosion(mask, border_value=0)
    return mask & ~eroded


def _symmetric_surface_distances(pred: np.ndarray, gt: np.ndarray, spacing):
    """(d_pred→gt, d_gt→pred): khoảng cách từ mỗi voxel biên sang mặt đối diện.

    Implementation "boundary-EDT (self)": EDT của phần bù mặt cho khoảng cách tới
    mặt gần nhất, lấy mẫu tại các voxel biên. Đây là công thức khoảng-cách-mặt kiểu
    medpy. spacing truyền vào ``distance_transform_edt`` qua ``sampling``.
    """
    sp = _match_spacing(spacing, pred.ndim)
    surf_p = _surface(pred)
    surf_g = _surface(gt)
    # distance_transform_edt: khoảng cách tới voxel-0 gần nhất ⇒ đảo mặt (~surf) để
    # nền = 0, mặt = "chướng ngại". dt tại một điểm = khoảng cách tới mặt gần nhất.
    dt_to_g = ndimage.distance_transform_edt(~surf_g, sampling=sp)
    dt_to_p = ndimage.distance_transform_edt(~surf_p, sampling=sp)
    d_pg = dt_to_g[surf_p]
    d_gp = dt_to_p[surf_g]
    return d_pg, d_gp


def hd95(pred, gt, spacing=(1.0, 1.0), empty_penalty: float | None = None) -> float:
    """95th-percentile Hausdorff distance (đối xứng), đơn vị = mm theo ``spacing``.

    Backend: ``medpy.metric.binary.hd95`` nếu import được; nếu không, fallback tự cài
    **"boundary-EDT percentile (medpy-style)"** (xem module docstring & _symmetric_surface_distances).

    Quy ước rỗng (A7 — KHOÁ, ghi số cụ thể, KHÔNG loại ca rỗng khỏi thống kê):
      * cả hai rỗng ⇒ **0.0**.
      * đúng một bên rỗng ⇒ **empty_penalty**. Mặc định = ĐƯỜNG CHÉO ảnh theo spacing
        = sqrt((H·sy)² + (W·sx)²) — hình phạt cố định, hữu hạn, đã khai báo.

    Tham số
    -------
    spacing : (sy, sx) khoảng cách voxel theo trục (hàng, cột). BraTS in-plane 1 mm iso.
    empty_penalty : ghi đè hình phạt mask rỗng; None ⇒ dùng đường chéo ảnh.
    """
    p = _as_bool(pred)
    g = _as_bool(gt)
    pe, ge = p.any(), g.any()

    if not pe and not ge:
        return 0.0
    if pe != ge:  # đúng một bên rỗng
        if empty_penalty is not None:
            return float(empty_penalty)
        return _image_diagonal(g.shape, spacing)

    if _medpy_hd95 is not None:  # pragma: no cover - chỉ khi có medpy
        sp = _match_spacing(spacing, p.ndim)
        return float(_medpy_hd95(p, g, voxelspacing=sp))

    d_pg, d_gp = _symmetric_surface_distances(p, g, spacing)
    alld = np.concatenate([d_pg, d_gp])
    if alld.size == 0:  # pragma: no cover - không xảy ra khi cả hai non-empty
        return 0.0
    return float(np.percentile(alld, 95))


def nsd(pred, gt, tau_mm: float = 2.0, spacing=(1.0, 1.0)) -> float:
    """Normalized Surface Dice ở dung sai τ (A7: τ = 2 mm PRIMARY; sensitivity {1,3,5}).

    NSD = (|biên pred trong τ của biên gt| + |biên gt trong τ của biên pred|)
          / (|biên pred| + |biên gt|).

    Implementation: xấp xỉ đếm-voxel-biên "boundary-EDT (self)" — cùng backend với hd95.
    (surface_distance của DeepMind ước lượng theo diện-tích-mặt; ở đây đếm voxel biên,
    đủ nhất quán cho lưới đều và có TÊN rõ ràng — A7.)

    Quy ước rỗng: cả hai rỗng ⇒ 1.0 ; đúng một bên rỗng ⇒ 0.0.
    spacing = (sy, sx) mm; BraTS in-plane 1 mm isotropic.
    """
    p = _as_bool(pred)
    g = _as_bool(gt)
    pe, ge = p.any(), g.any()
    if not pe and not ge:
        return 1.0
    if pe != ge:
        return 0.0

    d_pg, d_gp = _symmetric_surface_distances(p, g, spacing)
    n_total = d_pg.size + d_gp.size
    if n_total == 0:  # pragma: no cover
        return 1.0
    within = int((d_pg <= tau_mm).sum() + (d_gp <= tau_mm).sum())
    return float(within / n_total)


# --------------------------------------------------------------------------- #
# Số thành phần liên thông — bằng chứng lâm sàng đẹp nhất (A7)
# --------------------------------------------------------------------------- #
def n_connected_components(mask, connectivity: int = 1) -> int:
    """Số thành phần liên thông của mask (``scipy.ndimage.label``).

    A7: "output thresholding trung vị có N thành phần liên thông; khối u có 1" —
    không cần lý thuyết metric, không cần thống kê, không phản bác được.

    connectivity : 1 = kết nối trực giao (mặc định, 4-conn ở 2D / 6-conn ở 3D);
                   2 = kèm chéo (8-conn ở 2D). Dùng ``generate_binary_structure``.
    """
    m = _as_bool(mask)
    if not m.any():
        return 0
    structure = ndimage.generate_binary_structure(m.ndim, connectivity)
    _, n = ndimage.label(m, structure=structure)
    return int(n)


def empty_mask_rate(masks: list) -> float:
    """Tỷ lệ mask rỗng trong danh sách (A7: báo cáo theo k như KẾT QUẢ ĐỘC LẬP cho P3).

    Mask rỗng = không có voxel True. Danh sách rỗng ⇒ 0.0 (không bịa).
    """
    masks = list(masks)
    if not masks:
        return 0.0
    n_empty = sum(0 if _as_bool(m).any() else 1 for m in masks)
    return float(n_empty / len(masks))


# --------------------------------------------------------------------------- #
# PSNR / SSIM — wrapper MỎNG quanh skimage (KHÔNG tự chế — A7). Bằng chứng cho P3.
# --------------------------------------------------------------------------- #
def _infer_data_range(a: np.ndarray, b: np.ndarray) -> float:
    """Suy ra data_range cho PSNR/SSIM: ảnh nguyên ⇒ 255 (giả định 8-bit); else biên độ."""
    if np.issubdtype(a.dtype, np.integer) and np.issubdtype(b.dtype, np.integer):
        return 255.0
    lo = float(min(a.min(), b.min()))
    hi = float(max(a.max(), b.max()))
    rng = hi - lo
    return rng if rng > 0 else 1.0


def psnr(img_a, img_b, data_range: float | None = None) -> float:
    """Peak Signal-to-Noise Ratio — wrapper quanh ``skimage.metrics.peak_signal_noise_ratio``.

    KHÔNG tự chế (A7). Đây là BẰNG CHỨNG cho P3 (PSNR tăng theo k trong khi Dice giảm),
    KHÔNG phải một kết quả segmentation. ``data_range`` None ⇒ suy ra (ảnh uint8 ⇒ 255).
    """
    from skimage.metrics import peak_signal_noise_ratio  # import trễ: dep tuỳ chọn

    a = np.asarray(img_a)
    b = np.asarray(img_b)
    dr = data_range if data_range is not None else _infer_data_range(a, b)
    return float(peak_signal_noise_ratio(a, b, data_range=dr))


def ssim(img_a, img_b, data_range: float | None = None, **kwargs) -> float:
    """Structural Similarity — wrapper quanh ``skimage.metrics.structural_similarity``.

    KHÔNG tự chế (A7 — đối lập với global-SSIM tự chế của lô cũ; skimage dùng cửa sổ
    trượt đúng chuẩn Wang et al. 2004). Bằng chứng cho P3, không phải kết quả.
    ``**kwargs`` chuyển thẳng cho skimage (vd win_size cho ảnh nhỏ).
    """
    from skimage.metrics import structural_similarity  # import trễ: dep tuỳ chọn

    a = np.asarray(img_a)
    b = np.asarray(img_b)
    dr = data_range if data_range is not None else _infer_data_range(a, b)
    return float(structural_similarity(a, b, data_range=dr, **kwargs))

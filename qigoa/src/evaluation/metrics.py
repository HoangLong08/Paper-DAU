"""Segmentation + image quality metrics."""
from __future__ import annotations
import numpy as np


def psnr(reference: np.ndarray, test: np.ndarray, max_val: float = 255.0) -> float:
    ref = reference.astype(np.float64)
    tst = test.astype(np.float64)
    mse = np.mean((ref - tst) ** 2)
    if mse <= 1e-12:
        return float("inf")
    return float(20.0 * np.log10(max_val) - 10.0 * np.log10(mse))


def ssim(reference: np.ndarray, test: np.ndarray, max_val: float = 255.0) -> float:
    """SSIM via mean/variance/covariance — no need for skimage."""
    ref = reference.astype(np.float64)
    tst = test.astype(np.float64)
    mu_r, mu_t = ref.mean(), tst.mean()
    var_r = ref.var()
    var_t = tst.var()
    cov = np.mean((ref - mu_r) * (tst - mu_t))
    c1 = (0.01 * max_val) ** 2
    c2 = (0.03 * max_val) ** 2
    num = (2 * mu_r * mu_t + c1) * (2 * cov + c2)
    den = (mu_r ** 2 + mu_t ** 2 + c1) * (var_r + var_t + c2)
    return float(num / den) if den > 1e-12 else 0.0


def fsim(reference: np.ndarray, test: np.ndarray) -> float:
    """Simplified feature-similarity using gradient magnitude similarity.

    Not the full Zhang et al. (2011) FSIM (which uses phase congruency), but
    closely correlated and avoids the heavy dependency. Sufficient as a
    secondary metric.
    """
    ref = reference.astype(np.float64)
    tst = test.astype(np.float64)
    gx_r = np.gradient(ref, axis=1)
    gy_r = np.gradient(ref, axis=0)
    gx_t = np.gradient(tst, axis=1)
    gy_t = np.gradient(tst, axis=0)
    gm_r = np.sqrt(gx_r ** 2 + gy_r ** 2)
    gm_t = np.sqrt(gx_t ** 2 + gy_t ** 2)
    c = 0.0026 * (ref.max() if ref.max() > 0 else 1.0) ** 2
    gms = (2 * gm_r * gm_t + c) / (gm_r ** 2 + gm_t ** 2 + c)
    return float(gms.mean())


def dice(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    yt = (y_true > 0).astype(np.uint8)
    yp = (y_pred > 0).astype(np.uint8)
    inter = float((yt & yp).sum())
    denom = float(yt.sum() + yp.sum())
    return (2 * inter / denom) if denom > 0 else 0.0


def iou(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    yt = (y_true > 0).astype(np.uint8)
    yp = (y_pred > 0).astype(np.uint8)
    inter = float((yt & yp).sum())
    union = float((yt | yp).sum())
    return (inter / union) if union > 0 else 0.0


def sensitivity(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    yt = (y_true > 0).astype(np.uint8)
    yp = (y_pred > 0).astype(np.uint8)
    tp = float((yt & yp).sum())
    fn = float((yt & ~yp).sum())
    return (tp / (tp + fn)) if (tp + fn) > 0 else 0.0


def specificity(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    yt = (y_true > 0).astype(np.uint8)
    yp = (y_pred > 0).astype(np.uint8)
    tn = float((~yt & ~yp).sum())
    fp = float((~yt & yp).sum())
    return (tn / (tn + fp)) if (tn + fp) > 0 else 0.0


def all_metrics(reference: np.ndarray, segmented_image: np.ndarray,
                gt_mask: np.ndarray, pred_mask: np.ndarray) -> dict:
    return {
        "PSNR": psnr(reference, segmented_image),
        "SSIM": ssim(reference, segmented_image),
        "FSIM": fsim(reference, segmented_image),
        "Dice": dice(gt_mask, pred_mask),
        "IoU": iou(gt_mask, pred_mask),
        "Sensitivity": sensitivity(gt_mask, pred_mask),
        "Specificity": specificity(gt_mask, pred_mask),
    }

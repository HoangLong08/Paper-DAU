"""2D U-Net baseline — MODULE F, evaluation **class B (learned)**.

This is the single *learned* competitor in the study, and its entire training /
evaluation protocol is dictated by ``docs/preregistration.md`` §6/A3. Read that
section before touching this file. The three rules that matter most:

1. **Class B ⇒ out-of-fold evaluation only.** The U-Net is learned, so a patient
   it trained on can never be scored. Nested, PATIENT-LEVEL cross-validation
   guarantees each patient contributes exactly one out-of-fold prediction, on the
   same patient set as every class-A method — which is what makes the paired
   Wilcoxon / Friedman / TOST across patients mathematically defined.

2. **"Same input" is a constraint at INFERENCE, not at TRAIN.**
   * TRAIN on **every tumour-bearing slice** of the outer-train patients
     (thousands of slices) — starving the U-Net of data would be an unfair
     confound that makes a positive OR negative P4 result uninterpretable.
   * INFER on exactly **one** designated slice (the max-WT axial slice, the same
     slice the thresholding methods see) of each held-out patient.
   This keeps the honest "2D single-modality vs 3D multi-modality" caveat while
   removing the "U-Net had too little data" confound.

3. **The inner val fold does early stopping / epoch selection.** ≥3 seeds × 5
   outer folds. Per-image intensity normalisation is already done by the loader
   (using dataset-wide statistics would be a preprocessing leak).

**The oracle is NOT a "method".** Oracle-1-threshold / oracle-1-interval /
oracle level-set read the test-time ground truth to pick their answer. They are
class C — an unachievable ceiling, always labelled ``uses test-time ground
truth`` in every table/figure — and none of them are implemented here.

CPU-smoke mode (``cfg["smoke"] = True``) swaps BraTS for tiny synthetic images
and a couple of epochs, so the whole train/infer plumbing can be exercised on a
laptop with no GPU and no dataset mounted. Smoke outputs are structural
smoke-tests only — never a paper number.

Torch is imported lazily so this module can be imported where torch is absent.
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

# --------------------------------------------------------------------------- #
# Named constants / default hyper-parameters (overridable via cfg)
# --------------------------------------------------------------------------- #
UINT8_MAX: float = 255.0            # scale factor: uint8 [0, 255] -> float [0, 1]
INFER_THRESHOLD: float = 0.5        # sigmoid prob >= 0.5 -> foreground
DEFAULT_BASE_CHANNELS: int = 16     # small U-Net; base=16 -> ~1.9M params
DICE_SMOOTH: float = 1.0            # Laplace smoothing for the soft-Dice loss

_DEFAULT_CFG: Dict = {
    "base_channels": DEFAULT_BASE_CHANNELS,
    "epochs": 40,
    "batch_size": 16,
    "lr": 1e-3,
    "weight_decay": 1e-5,
    "device": "auto",              # "auto" -> cuda if available else cpu
    "out_dir": "results/unet/checkpoints",
    "smoke": False,                # True -> synthetic data + tiny epochs (no GPU)
    "smoke_train_patients": 3,
    "smoke_val_patients": 2,
    "smoke_slices_per_patient": 4,
    "smoke_image_size": 64,
    "num_workers": 0,
}


# =========================================================================== #
# Architecture
# =========================================================================== #
def _build_unet(base_channels: int):
    """Construct the UNet2D class lazily (needs torch). Returns an instance."""
    import torch
    import torch.nn as nn

    class _DoubleConv(nn.Module):
        """(conv 3x3 -> BN -> ReLU) x2 — the standard U-Net block."""

        def __init__(self, c_in: int, c_out: int):
            super().__init__()
            self.block = nn.Sequential(
                nn.Conv2d(c_in, c_out, kernel_size=3, padding=1, bias=False),
                nn.BatchNorm2d(c_out),
                nn.ReLU(inplace=True),
                nn.Conv2d(c_out, c_out, kernel_size=3, padding=1, bias=False),
                nn.BatchNorm2d(c_out),
                nn.ReLU(inplace=True),
            )

        def forward(self, x):
            return self.block(x)

    class UNet2D(nn.Module):
        """Compact 2D U-Net: 1 input channel (FLAIR) -> 1 sigmoid channel (mask).

        Encoder/decoder with three down-samplings. ``forward`` returns a
        **probability** map (sigmoid already applied), matching the interface
        contract ``output 1 channel mask``. With ``base_channels=16`` this is a
        few-1.9M-parameter network — small enough to train inside a Kaggle GPU
        session (< 12 h) yet expressive enough to clear the thresholding ceiling
        that P4 tests. Lower ``base_channels`` (e.g. 8) drops it to a few hundred
        k parameters for tighter budgets.
        """

        def __init__(self, in_channels: int = 1, out_channels: int = 1,
                     base_channels: int = DEFAULT_BASE_CHANNELS):
            super().__init__()
            c1, c2, c3, c4 = (base_channels, base_channels * 2,
                              base_channels * 4, base_channels * 8)
            self.pool = nn.MaxPool2d(2)

            self.enc1 = _DoubleConv(in_channels, c1)
            self.enc2 = _DoubleConv(c1, c2)
            self.enc3 = _DoubleConv(c2, c3)
            self.bottleneck = _DoubleConv(c3, c4)

            self.up3 = nn.ConvTranspose2d(c4, c3, kernel_size=2, stride=2)
            self.dec3 = _DoubleConv(c4, c3)
            self.up2 = nn.ConvTranspose2d(c3, c2, kernel_size=2, stride=2)
            self.dec2 = _DoubleConv(c3, c2)
            self.up1 = nn.ConvTranspose2d(c2, c1, kernel_size=2, stride=2)
            self.dec1 = _DoubleConv(c2, c1)

            self.head = nn.Conv2d(c1, out_channels, kernel_size=1)

        @staticmethod
        def _pad_to(x, ref):
            """Pad ``x`` (H,W) up to ``ref`` after odd-size pooling, so skip
            connections concatenate cleanly for arbitrary input sizes."""
            dh = ref.shape[-2] - x.shape[-2]
            dw = ref.shape[-1] - x.shape[-1]
            if dh or dw:
                x = nn.functional.pad(x, [0, dw, 0, dh])
            return x

        def forward(self, x):
            e1 = self.enc1(x)
            e2 = self.enc2(self.pool(e1))
            e3 = self.enc3(self.pool(e2))
            b = self.bottleneck(self.pool(e3))

            d3 = self.dec3(torch.cat([self._pad_to(self.up3(b), e3), e3], dim=1))
            d2 = self.dec2(torch.cat([self._pad_to(self.up2(d3), e2), e2], dim=1))
            d1 = self.dec1(torch.cat([self._pad_to(self.up1(d2), e1), e1], dim=1))
            return torch.sigmoid(self.head(d1))

    return UNet2D(base_channels=base_channels)


def UNet2D(in_channels: int = 1, out_channels: int = 1,
           base_channels: int = DEFAULT_BASE_CHANNELS):
    """Public factory returning a compact 2D U-Net (see :func:`_build_unet`).

    Kept as a callable named ``UNet2D`` so callers can ``from src.baselines.unet2d
    import UNet2D`` per the interface contract, without importing torch at module
    load time. ``in_channels``/``out_channels`` are accepted for signature
    completeness (the task fixes them to 1).
    """
    if in_channels != 1 or out_channels != 1:
        raise ValueError("this baseline is fixed to 1-in / 1-out (FLAIR -> mask)")
    return _build_unet(base_channels=base_channels)


# =========================================================================== #
# Loss: Dice + BCE
# =========================================================================== #
def _dice_bce_loss(prob, target, smooth: float = DICE_SMOOTH):
    """Combined soft-Dice + binary-cross-entropy loss on probabilities."""
    import torch

    p = prob.reshape(prob.shape[0], -1)
    t = target.reshape(target.shape[0], -1)
    inter = (p * t).sum(dim=1)
    dice = (2 * inter + smooth) / (p.sum(dim=1) + t.sum(dim=1) + smooth)
    dice_loss = 1.0 - dice.mean()
    bce = torch.nn.functional.binary_cross_entropy(p, t)
    return dice_loss + bce


def _binary_dice(pred_bool: np.ndarray, gt_bool: np.ndarray) -> float:
    """Local hard-Dice for val/epoch selection (canonical metric is
    ``src.eval.metrics.dice``; kept local to avoid a hard cross-module dependency
    while Module E is in flux). Both empty -> 1.0."""
    a = pred_bool.astype(bool)
    b = gt_bool.astype(bool)
    denom = a.sum() + b.sum()
    if denom == 0:
        return 1.0
    return float(2.0 * np.logical_and(a, b).sum() / denom)


# =========================================================================== #
# Reproducibility
# =========================================================================== #
def _seed_everything(seed: int) -> None:
    """Pin every RNG so a (fold, seed) run is reproducible (CLAUDE.md §5.2)."""
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch

        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    except ImportError:  # pragma: no cover - torch-less environment
        pass


def _resolve_device(cfg: Dict):
    import torch

    want = cfg.get("device", "auto")
    if want == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device(want)


# =========================================================================== #
# Data assembly (A3: all tumour slices for TRAIN/VAL, one slice for INFER)
# =========================================================================== #
def _iter_tumour_slices(patient_id: str, brats_root: Path
                        ) -> List[Tuple[np.ndarray, np.ndarray]]:
    """Return ``(flair_uint8, wt_mask_bool)`` for EVERY tumour-bearing axial slice
    of one patient.

    A3: training/validation consume *all* tumour slices, not just the max-WT one.
    Reuses the Module-A loader primitives (per-image normalisation, axial axis,
    label convention) so normalisation is byte-identical to the class-A path.
    """
    from src.data import brats_loader as bl

    pdir = brats_root / patient_id
    flair_vol = bl._load_volume(bl._find_modality(pdir, "_flair"))
    seg_vol = bl._load_volume(bl._find_modality(pdir, "_seg"))

    out: List[Tuple[np.ndarray, np.ndarray]] = []
    n_axial = flair_vol.shape[bl.AXIAL_AXIS]
    for z in range(n_axial):
        seg2d = np.take(seg_vol, z, axis=bl.AXIAL_AXIS)
        wt = seg2d > 0
        if not wt.any():
            continue  # A3: only tumour-bearing slices
        flair2d = np.take(flair_vol, z, axis=bl.AXIAL_AXIS)
        out.append((bl.normalize_to_uint8(flair2d),
                    np.ascontiguousarray(wt, dtype=bool)))
    return out


def _synthetic_slices(n_patients: int, slices_per_patient: int, size: int,
                      rng: np.random.Generator
                      ) -> List[Tuple[np.ndarray, np.ndarray]]:
    """Tiny bright-blob-on-dark-background slices for CPU-smoke mode only.

    These are structural smoke-test fixtures, NOT data — nothing produced from
    them may become a paper number (CLAUDE.md §5.4 / IRON RULE 3).
    """
    out: List[Tuple[np.ndarray, np.ndarray]] = []
    for _ in range(n_patients * slices_per_patient):
        img = rng.integers(0, 40, size=(size, size), dtype=np.uint8)
        mask = np.zeros((size, size), dtype=bool)
        r = size // 4
        cy, cx = rng.integers(r, size - r, size=2)
        yy, xx = np.ogrid[:size, :size]
        blob = (yy - cy) ** 2 + (xx - cx) ** 2 <= r * r
        img[blob] = rng.integers(180, 255)
        mask[blob] = True
        out.append((img.astype(np.uint8), mask))
    return out


def _make_batches(samples: List[Tuple[np.ndarray, np.ndarray]], size: int,
                  target_hw: Tuple[int, int]):
    """Yield ``(x, y)`` float tensors, resizing every slice to a common HW so a
    fixed-size batch tensor is well defined."""
    import torch
    import torch.nn.functional as F

    def _to_tensor(img_u8, mask_bool):
        x = torch.from_numpy(img_u8.astype(np.float32) / UINT8_MAX)[None, None]
        y = torch.from_numpy(mask_bool.astype(np.float32))[None, None]
        x = F.interpolate(x, size=target_hw, mode="bilinear", align_corners=False)
        y = F.interpolate(y, size=target_hw, mode="nearest")
        return x[0], y[0]

    xs, ys = [], []
    for img, mask in samples:
        xi, yi = _to_tensor(img, mask)
        xs.append(xi)
        ys.append(yi)
        if len(xs) == size:
            yield torch.stack(xs), torch.stack(ys)
            xs, ys = [], []
    if xs:
        yield torch.stack(xs), torch.stack(ys)


def _common_hw(samples: List[Tuple[np.ndarray, np.ndarray]]) -> Tuple[int, int]:
    """Pick a padded-to-multiple-of-8 HW that fits the (typically uniform) BraTS
    slice size, so three max-pools never hit a 0-size feature map."""
    h = max(s[0].shape[0] for s in samples)
    w = max(s[0].shape[1] for s in samples)
    pad = 8
    h = ((h + pad - 1) // pad) * pad
    w = ((w + pad - 1) // pad) * pad
    return h, w


# =========================================================================== #
# Training (nested patient-level CV — A3)
# =========================================================================== #
def _load_fold(splits_dir: Path, fold: int) -> Dict:
    with open(Path(splits_dir) / f"fold_{fold}.json", "r", encoding="utf-8") as fh:
        return json.load(fh)


def train_unet_cv(cohort_csv, splits_dir, brats_root, fold: int, seed: int,
                  cfg: Optional[Dict] = None) -> str:
    """Train the class-B U-Net for one ``(fold, seed)`` under nested patient-level CV.

    Protocol (docs/preregistration.md §6/A3):
      * ``splits_dir/fold_{fold}.json`` provides the patient lists. The split UNIT
        is the patient, so no patient leaks between train / val / test.
      * TRAIN on **all tumour-bearing slices** of the outer-train patients; the
        inner VAL patients' slices drive early stopping / epoch selection (best
        val Dice checkpoint is kept). The held-out TEST patients are never touched
        here — they are scored later, out-of-fold, by :func:`infer_unet`.
      * ``seed`` pins every RNG; the caller sweeps ≥3 seeds × 5 folds.

    Returns the path to the saved checkpoint (a dict carrying the weights AND the
    architecture/config needed to rebuild the net at inference time).

    ``cfg["smoke"] = True`` replaces BraTS with synthetic slices and runs a couple
    of epochs on CPU — plumbing test only, never a paper number.
    """
    import torch

    cfg = {**_DEFAULT_CFG, **(cfg or {})}
    _seed_everything(seed)
    device = _resolve_device(cfg)

    # --- assemble train / val sample pools (A3) ------------------------------
    if cfg["smoke"]:
        rng = np.random.default_rng(seed)
        sz = cfg["smoke_image_size"]
        train_samples = _synthetic_slices(
            cfg["smoke_train_patients"], cfg["smoke_slices_per_patient"], sz, rng)
        val_samples = _synthetic_slices(
            cfg["smoke_val_patients"], cfg["smoke_slices_per_patient"], sz, rng)
        epochs = min(cfg["epochs"], 2)
    else:
        info = _load_fold(splits_dir, fold)
        brats_root = Path(brats_root)
        train_samples, val_samples = [], []
        for pid in info["train"]:
            train_samples.extend(_iter_tumour_slices(pid, brats_root))
        for pid in info["val"]:
            val_samples.extend(_iter_tumour_slices(pid, brats_root))
        epochs = cfg["epochs"]

    if not train_samples:
        raise RuntimeError("no tumour-bearing training slices found for this fold")

    target_hw = _common_hw(train_samples + val_samples)

    # --- model / optimiser ---------------------------------------------------
    model = UNet2D(base_channels=cfg["base_channels"]).to(device)
    optim = torch.optim.Adam(
        model.parameters(), lr=cfg["lr"], weight_decay=cfg["weight_decay"])

    out_dir = Path(cfg["out_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    ckpt_path = out_dir / f"unet_fold{fold}_seed{seed}.pt"

    best_val = -1.0
    best_state = None
    rng_batch = np.random.default_rng(seed)

    for epoch in range(epochs):
        model.train()
        order = rng_batch.permutation(len(train_samples))
        shuffled = [train_samples[i] for i in order]
        for x, y in _make_batches(shuffled, cfg["batch_size"], target_hw):
            x, y = x.to(device), y.to(device)
            optim.zero_grad()
            loss = _dice_bce_loss(model(x), y)
            loss.backward()
            optim.step()

        val_dice = _evaluate_val(model, val_samples, target_hw, device)
        if val_dice > best_val:
            best_val = val_dice
            best_state = {k: v.detach().cpu().clone()
                          for k, v in model.state_dict().items()}

    if best_state is None:  # e.g. epochs == 0 or empty val: fall back to final
        best_state = {k: v.detach().cpu().clone()
                      for k, v in model.state_dict().items()}

    torch.save(
        {
            "state_dict": best_state,
            "base_channels": cfg["base_channels"],
            "target_hw": list(target_hw),
            "fold": fold,
            "seed": seed,
            "best_val_dice": best_val,
            "eval_class": "B",  # learned -> out-of-fold only (A3)
        },
        ckpt_path,
    )
    return str(ckpt_path)


def _evaluate_val(model, val_samples, target_hw, device) -> float:
    """Mean hard-Dice over all val tumour slices (early-stopping signal)."""
    import torch

    if not val_samples:
        return 0.0
    model.eval()
    dices = []
    with torch.no_grad():
        for x, y in _make_batches(val_samples, 8, target_hw):
            x = x.to(device)
            prob = model(x).cpu().numpy()
            pred = prob >= INFER_THRESHOLD
            gt = y.numpy() >= 0.5
            for i in range(pred.shape[0]):
                dices.append(_binary_dice(pred[i, 0], gt[i, 0]))
    return float(np.mean(dices)) if dices else 0.0


# =========================================================================== #
# Inference (A3: exactly ONE designated slice of a held-out patient)
# =========================================================================== #
def infer_unet(checkpoint, slice_obj) -> np.ndarray:
    """Predict the WT mask for ONE slice from a trained checkpoint.

    A3: "same input" is an inference constraint — the net sees exactly the single
    designated (max-WT) FLAIR slice ``slice_obj.flair`` of a **held-out** patient,
    the same slice the thresholding baselines see. Output is thresholded at 0.5
    and resized back to the slice's native shape. Returns a bool mask.

    ``checkpoint`` may be a path or the already-loaded dict from
    :func:`train_unet_cv`.
    """
    import torch
    import torch.nn.functional as F

    if isinstance(checkpoint, (str, Path)):
        ckpt = torch.load(str(checkpoint), map_location="cpu", weights_only=False)
    else:
        ckpt = checkpoint

    model = UNet2D(base_channels=ckpt["base_channels"])
    model.load_state_dict(ckpt["state_dict"])
    model.eval()

    flair = np.asarray(slice_obj.flair, dtype=np.float32) / UINT8_MAX
    native_hw = flair.shape
    target_hw = tuple(ckpt["target_hw"])

    x = torch.from_numpy(flair)[None, None]
    x = F.interpolate(x, size=target_hw, mode="bilinear", align_corners=False)
    with torch.no_grad():
        prob = model(x)
    prob = F.interpolate(prob, size=native_hw, mode="bilinear",
                         align_corners=False)
    mask = prob[0, 0].numpy() >= INFER_THRESHOLD
    return np.ascontiguousarray(mask, dtype=bool)

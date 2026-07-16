"""MODULE F — baselines (classical unsupervised + 2D U-Net) + run manifest.

This package supplies two of the three A/B/C evaluation classes fixed in
``docs/preregistration.md`` §6/A3:

* :mod:`src.baselines.classical` — **class A (unsupervised, per-image)**:
  Otsu / Li / Triangle / k-means / GMM. Each produces a binary mask from a
  single image with no training and no ground truth, so it is evaluated on the
  whole valid cohort (every patient).

* :mod:`src.baselines.unet2d` — **class B (learned)**: a small 2D U-Net that is
  trained with nested patient-level CV and therefore evaluated **out-of-fold
  only** — never on a patient whose slices it was trained on.

Class C (oracles) lives elsewhere and is NOT a "method": it uses test-time
ground truth and is only an unachievable upper bound.

Public interface (see the module docstrings for the frozen conventions):

    from src.baselines.classical import (
        otsu_threshold, li_threshold, triangle_threshold,
        kmeans_segment, gmm_segment,
    )
    from src.baselines.unet2d import UNet2D, train_unet_cv, infer_unet
"""

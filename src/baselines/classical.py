"""Classical unsupervised segmentation baselines — MODULE F, evaluation **class A**.

Every function here is a **class-A method** in the taxonomy frozen by
``docs/preregistration.md`` §6/A3:

    class A — unsupervised, per-image : Otsu, Li, Triangle, k-means, GMM
              -> evaluated on the WHOLE valid cohort (all n patients),
                 because there is no training and no ground truth is ever seen.

None of these functions look at a label, a neighbouring image, or any
cohort-wide statistic — the decision is taken **within a single image**. That is
exactly what makes them class A: there is no fold to hold out, so they are scored
on every valid patient. (Contrast with the 2D U-Net in :mod:`src.baselines.unet2d`,
which is learned and therefore scored out-of-fold only; and with the oracles,
which are not methods at all because they read test-time ground truth.)

Frozen conventions (shared interface contract):
  * Input is a ``uint8`` image with L = 256 gray levels.
  * Foreground rule for the threshold methods: ``mask = img > threshold``
    (strictly greater — the threshold level itself stays background).
  * Foreground rule for the clustering methods: the cluster / mixture component
    with the **brightest mean intensity** is taken as foreground. This is the
    same "brightest region is the lesion" convention the FLAIR whole-tumor task
    uses; it is a property of *these baselines*, not a claim about the literature.
  * Every function returns ``np.ndarray`` of dtype ``bool`` with the SAME shape
    as the input image.

Determinism: the clustering baselines pin ``random_state`` so that a given image
always yields the same mask (a class-A method must be a pure function of its
image — no hidden seed variance to average over).
"""

from __future__ import annotations

import numpy as np

# --------------------------------------------------------------------------- #
# Named constants (no magic numbers)
# --------------------------------------------------------------------------- #
NUM_LEVELS: int = 256              # L = 256 gray levels; images are uint8 [0, 255]
DEFAULT_N_CLUSTERS: int = 2        # k-means: background vs (bright) foreground
DEFAULT_N_COMPONENTS: int = 2      # GMM: background vs (bright) foreground
CLUSTER_RANDOM_STATE: int = 0      # pin RNG so a class-A method is deterministic
KMEANS_N_INIT: int = 10            # multiple restarts -> stable centroids


# --------------------------------------------------------------------------- #
# Internal helpers
# --------------------------------------------------------------------------- #
def _as_uint8(img: np.ndarray) -> np.ndarray:
    """Validate/normalise the input to a 2-D uint8 array."""
    arr = np.asarray(img)
    if arr.dtype != np.uint8:
        arr = arr.astype(np.uint8)
    if arr.ndim != 2:
        raise ValueError(f"expected a 2-D image, got shape {arr.shape}")
    return arr


def _is_constant(img: np.ndarray) -> bool:
    """A single-valued image has no threshold — thresholders would divide by 0."""
    return img.min() == img.max()


def _empty_like(img: np.ndarray) -> np.ndarray:
    """All-background mask, used as the safe answer for a degenerate image."""
    return np.zeros(img.shape, dtype=bool)


# --------------------------------------------------------------------------- #
# Global-threshold baselines (skimage.filters)
# --------------------------------------------------------------------------- #
def otsu_threshold(img_uint8: np.ndarray) -> np.ndarray:
    """Otsu's between-class-variance threshold (``mask = img > t``).

    Class A (per-image, unsupervised). Returns a bool mask shaped like the input.
    A constant image has no valid threshold and returns an all-background mask.
    """
    from skimage.filters import threshold_otsu

    img = _as_uint8(img_uint8)
    if _is_constant(img):
        return _empty_like(img)
    t = threshold_otsu(img)
    return img > t


def li_threshold(img_uint8: np.ndarray) -> np.ndarray:
    """Li's minimum-cross-entropy threshold (``mask = img > t``).

    Class A (per-image, unsupervised). Returns a bool mask shaped like the input.
    """
    from skimage.filters import threshold_li

    img = _as_uint8(img_uint8)
    if _is_constant(img):
        return _empty_like(img)
    t = threshold_li(img)
    return img > t


def triangle_threshold(img_uint8: np.ndarray) -> np.ndarray:
    """Zack's triangle threshold (``mask = img > t``).

    Class A (per-image, unsupervised). Returns a bool mask shaped like the input.
    """
    from skimage.filters import threshold_triangle

    img = _as_uint8(img_uint8)
    if _is_constant(img):
        return _empty_like(img)
    t = threshold_triangle(img)
    return img > t


# --------------------------------------------------------------------------- #
# Clustering baselines (scikit-learn) — foreground = brightest cluster/component
# --------------------------------------------------------------------------- #
def kmeans_segment(
    img_uint8: np.ndarray, n_clusters: int = DEFAULT_N_CLUSTERS
) -> np.ndarray:
    """1-D k-means on pixel intensities; foreground = brightest cluster.

    Class A (per-image, unsupervised). k-means is fitted on the pixel intensities
    of THIS image only (reshaped to ``(H*W, 1)``). The cluster whose centroid has
    the highest intensity is declared foreground. Deterministic (pinned RNG +
    ``n_init``). Returns a bool mask shaped like the input.
    """
    from sklearn.cluster import KMeans

    img = _as_uint8(img_uint8)
    if _is_constant(img):
        return _empty_like(img)

    x = img.reshape(-1, 1).astype(np.float64)
    km = KMeans(
        n_clusters=n_clusters,
        n_init=KMEANS_N_INIT,
        random_state=CLUSTER_RANDOM_STATE,
    ).fit(x)
    brightest = int(np.argmax(km.cluster_centers_.ravel()))
    labels = km.labels_.reshape(img.shape)
    return labels == brightest


def gmm_segment(
    img_uint8: np.ndarray, n_components: int = DEFAULT_N_COMPONENTS
) -> np.ndarray:
    """1-D Gaussian mixture on pixel intensities; foreground = brightest component.

    Class A (per-image, unsupervised). A GMM is fitted on the pixel intensities of
    THIS image only. The component with the highest mean intensity is declared
    foreground; every pixel is assigned to its most-likely component. Deterministic
    (pinned RNG). Returns a bool mask shaped like the input.
    """
    from sklearn.mixture import GaussianMixture

    img = _as_uint8(img_uint8)
    if _is_constant(img):
        return _empty_like(img)

    x = img.reshape(-1, 1).astype(np.float64)
    gm = GaussianMixture(
        n_components=n_components,
        random_state=CLUSTER_RANDOM_STATE,
    ).fit(x)
    brightest = int(np.argmax(gm.means_.ravel()))
    labels = gm.predict(x).reshape(img.shape)
    return labels == brightest

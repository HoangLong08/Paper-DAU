"""Test QIGOA mới với setting thực tế (pop=50, iter=150) trên synthetic harder image.

Mục đích: xác nhận local refinement + tuned hyperparameters giúp QIGOA
cạnh tranh với baselines BEFORE running on Kaggle.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from src.algorithms import REGISTRY
from src.fitness import make_kapur_objective, make_tsallis_objective
from src.data.preprocessing import synthetic_brain_image, apply_thresholds, segmentation_to_binary
from src.evaluation.metrics import all_metrics


def make_harder_image(rng, size=256):
    """3-region brain phantom — harder than the synthetic_brain_image which
    has only 2 distinguishable classes."""
    H = W = size
    img = np.zeros((H, W), dtype=np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    cx, cy = W // 2, H // 2
    brain = ((xx - cx) ** 2 / (W * 0.45) ** 2 + (yy - cy) ** 2 / (H * 0.45) ** 2) < 1
    # gray matter
    img[brain] = 90 + rng.normal(0, 10, size=brain.sum())
    # white matter
    wm = ((xx - cx) ** 2 / (W * 0.32) ** 2 + (yy - cy) ** 2 / (H * 0.32) ** 2) < 1
    img[wm] = 140 + rng.normal(0, 8, size=wm.sum())
    # ventricle (dark)
    vent = ((xx - cx) ** 2 / (W * 0.08) ** 2 + (yy - cy) ** 2 / (H * 0.08) ** 2) < 1
    img[vent] = 40 + rng.normal(0, 5, size=vent.sum())
    # tumor: bright eccentric blob
    tx, ty = cx + 30, cy - 20
    tumor = ((xx - tx) ** 2 + (yy - ty) ** 2) < (size * 0.06) ** 2
    img[tumor] = 220 + rng.normal(0, 5, size=tumor.sum())
    img = np.clip(img, 0, 255).astype(np.uint8)
    return img, tumor.astype(np.uint8)


def bench(image, mask, k, fitness_kind="kapur", q=0.5, n_runs=5):
    """Mean fitness + Dice across n_runs for each algo."""
    if fitness_kind == "kapur":
        f, _ = make_kapur_objective(image)
    else:
        f, _ = make_tsallis_objective(image, q=q)

    results = {}
    for name in ["GA", "PSO", "GOA", "WOA", "GWO", "MPA", "QIGOA"]:
        fits = []
        dices = []
        times = []
        for run in range(n_runs):
            opt = REGISTRY[name](dim=k, lb=1, ub=254, pop_size=50, max_iter=150, seed=run)
            res = opt.optimize(f)
            seg = apply_thresholds(image, res.best_x)
            pred = segmentation_to_binary(seg)
            m = all_metrics(image, image, mask, pred)
            fits.append(res.best_fitness)
            dices.append(m["Dice"])
            times.append(res.runtime_s)
        results[name] = {
            "fit_mean": np.mean(fits),
            "fit_std": np.std(fits),
            "fit_best": np.max(fits),
            "dice_mean": np.mean(dices),
            "time_mean": np.mean(times),
        }
    return results


def print_table(results, title):
    print(f"\n=== {title} ===")
    print(f"{'algo':<8} {'fit_mean':>10} {'fit_std':>10} {'fit_best':>10} {'dice':>7} {'time(s)':>8}")
    print("-" * 62)
    best_fit = max(r["fit_mean"] for r in results.values())
    best_dice = max(r["dice_mean"] for r in results.values())
    for name, r in results.items():
        mark_f = " *" if abs(r["fit_mean"] - best_fit) < 1e-6 else "  "
        mark_d = " *" if abs(r["dice_mean"] - best_dice) < 1e-6 else "  "
        print(f"{name:<8} {r['fit_mean']:>10.4f} {r['fit_std']:>10.4f} {r['fit_best']:>10.4f}"
              f"{mark_f}{r['dice_mean']:>5.3f}{mark_d} {r['time_mean']:>8.2f}")


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    img, mask = make_harder_image(rng, size=256)
    print(f"Image: {img.shape}, unique intensities: {len(np.unique(img))}, tumor: {mask.sum()}px")

    for k in [8, 10]:
        results = bench(img, mask, k=k, fitness_kind="kapur", n_runs=3)
        print_table(results, f"Kapur HIGH-K, k={k}")

    for k in [8, 10]:
        results = bench(img, mask, k=k, fitness_kind="tsallis", q=0.5, n_runs=3)
        print_table(results, f"Tsallis HIGH-K, k={k}")

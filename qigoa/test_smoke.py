"""Local smoke test — no BraTS needed. Run with: python test_smoke.py"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from src.algorithms import REGISTRY
from src.fitness import make_kapur_objective
from src.data.preprocessing import synthetic_brain_image, apply_thresholds, segmentation_to_binary
from src.evaluation.metrics import all_metrics

rng = np.random.default_rng(0)
img, mask = synthetic_brain_image(rng, size=128)
print(f"Image shape: {img.shape}, tumor pixels: {mask.sum()}")

f, _ = make_kapur_objective(img)
print(f"\n{'algo':<8} {'fit':>8} {'Dice':>7} {'IoU':>7} {'PSNR':>7} {'time(s)':>8}")
print("-" * 50)
for name in ["GA", "PSO", "GOA", "WOA", "GWO", "MPA", "QIGOA"]:
    opt = REGISTRY[name](dim=3, lb=1, ub=254, pop_size=20, max_iter=40, seed=42)
    res = opt.optimize(f)
    seg = apply_thresholds(img, res.best_x)
    pred = segmentation_to_binary(seg)
    m = all_metrics(img, img, mask, pred)
    print(f"{name:<8} {res.best_fitness:>8.4f} {m['Dice']:>7.3f} {m['IoU']:>7.3f} {m['PSNR']:>7.2f} {res.runtime_s:>8.2f}")
print("\nSmoke test OK.")

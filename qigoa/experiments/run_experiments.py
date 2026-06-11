"""Main experiment driver. Runs every algorithm x every threshold-count x N runs
on every image, dumps per-run results and aggregate tables to CSV.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import time
from typing import Dict, Iterable, List
import numpy as np
import pandas as pd

from src.algorithms import REGISTRY
from src.fitness import make_kapur_objective, make_otsu_objective, make_tsallis_objective
from src.data.preprocessing import apply_thresholds, segmentation_to_binary
from src.evaluation.metrics import all_metrics


@dataclass
class ExpConfig:
    pop_size: int = 30
    max_iter: int = 100
    n_runs: int = 30
    k_levels: tuple = (2, 3, 4, 5)
    fitness: str = "kapur"   # "kapur" | "otsu"
    levels: int = 256
    algos: tuple = ("GA", "PSO", "GOA", "WOA", "GWO", "MPA", "QIGOA")


def make_objective(image: np.ndarray, kind: str, levels: int):
    if kind == "kapur":
        return make_kapur_objective(image, levels=levels)
    if kind == "otsu":
        return make_otsu_objective(image, levels=levels)
    if kind.startswith("tsallis"):
        # accepts "tsallis" (q=0.5 default) or "tsallis_q=0.8"
        q = 0.5
        if "=" in kind:
            q = float(kind.split("=", 1)[1])
        return make_tsallis_objective(image, q=q, levels=levels)
    raise ValueError(kind)


def run_one(image: np.ndarray, gt_mask: np.ndarray, image_id: str,
            cfg: ExpConfig, base_seed: int = 0) -> List[dict]:
    rows: List[dict] = []
    L = cfg.levels
    f, _ = make_objective(image, cfg.fitness, L)
    for k in cfg.k_levels:
        lb = np.full(k, 1, dtype=np.float64)
        ub = np.full(k, L - 2, dtype=np.float64)
        for algo_name in cfg.algos:
            Cls = REGISTRY[algo_name]
            for run in range(cfg.n_runs):
                seed = base_seed + run
                opt = Cls(dim=k, lb=lb, ub=ub,
                          pop_size=cfg.pop_size, max_iter=cfg.max_iter, seed=seed)
                res = opt.optimize(f)
                seg = apply_thresholds(image, res.best_x)
                # rebuild a quasi-reconstructed image (mean intensity per class)
                rec = np.zeros_like(image, dtype=np.float64)
                for cls in range(int(seg.max()) + 1):
                    mask_cls = seg == cls
                    if mask_cls.any():
                        rec[mask_cls] = image[mask_cls].mean()
                pred_bin = segmentation_to_binary(seg)
                m = all_metrics(image, rec.astype(np.uint8), gt_mask, pred_bin)
                rows.append({
                    "image_id": image_id,
                    "algorithm": algo_name,
                    "k": int(k),
                    "run": run,
                    "fitness_value": res.best_fitness,
                    "runtime_s": res.runtime_s,
                    "n_evals": res.n_evals,
                    "thresholds": ",".join(str(int(v)) for v in np.sort(res.best_x.astype(int))),
                    **m,
                })
    return rows


def aggregate(df: pd.DataFrame) -> pd.DataFrame:
    """Mean ± std over runs, grouped by image, algo, k."""
    agg = df.groupby(["image_id", "algorithm", "k"]).agg(
        fit_mean=("fitness_value", "mean"),
        fit_std=("fitness_value", "std"),
        fit_best=("fitness_value", "max"),
        psnr_mean=("PSNR", "mean"),
        ssim_mean=("SSIM", "mean"),
        fsim_mean=("FSIM", "mean"),
        dice_mean=("Dice", "mean"),
        iou_mean=("IoU", "mean"),
        sens_mean=("Sensitivity", "mean"),
        spec_mean=("Specificity", "mean"),
        time_mean=("runtime_s", "mean"),
    ).reset_index()
    return agg

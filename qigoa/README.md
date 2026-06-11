# QIGOA — Quantum-Inspired Grasshopper Optimization for Multilevel Thresholding

Code accompanying the manuscript submitted to *Biomedical Signal Processing and Control*.

## Structure
- `src/algorithms/` — 7 optimizers (GA, PSO, GOA, WOA, GWO, MPA, **QIGOA**)
- `src/fitness/` — Kapur entropy, Otsu variance
- `src/data/` — BraTS loader, synthetic fallback
- `src/evaluation/` — metrics + Wilcoxon/Friedman tests
- `experiments/run_experiments.py` — driver
- `notebooks/qigoa_kaggle.ipynb` — runs end-to-end on Kaggle
- `test_smoke.py` — quick local sanity check (no data needed)

## Local smoke test
```bash
pip install numpy scipy pandas matplotlib
python test_smoke.py
```

## Kaggle setup
1. Create a new Kaggle notebook (CPU is fine, GPU not required).
2. Add dataset **BraTS 2020 Training Data** as input (or run without — synthetic fallback kicks in).
3. Upload the `qigoa/` folder as a Kaggle dataset, or paste `src/` and `experiments/` next to the notebook.
4. Run cells top-to-bottom. Outputs land in `/kaggle/working/results/`.

## Knobs
| Param | Default | Where |
|-------|---------|-------|
| `pop_size` | 30 | `ExpConfig` |
| `max_iter` | 100 | `ExpConfig` |
| `n_runs` | 30 | `ExpConfig` (use 5 for smoke) |
| `k_levels` | (2,3,4,5) | `ExpConfig` |
| Q-bits per dim | 8 | `QIGOA(..., bits_per_dim=8)` |
| theta_max | 0.05π | `QIGOA(..., theta_max=...)` |
| stagnation_window | 8 | `QIGOA(..., stagnation_window=...)` |

## QIGOA contributions
1. **Quantum representation**: each grasshopper as Q-bits `(alpha, beta)` with rotation gate.
2. **Adaptive rotation angle** depending on fitness gap to the global target, annealed over iterations.
3. **Opposition-Based Learning** init + **Lévy-flight escape** when stagnating.

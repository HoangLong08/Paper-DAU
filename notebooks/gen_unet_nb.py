"""Sinh notebook Kaggle E4 — 2D U-Net (GPU) cho ceiling decomposition (Family A).

Tái dùng ĐÚNG harness đã kiểm chứng của E2 (`gen_e2_nb.py`): git-sync + guard, ngân
sách wall-clock + `--resume`, cell RESTORE từ `.tgz`, cell KIỂM ĐẾM, đóng gói.

KHÁC E2:
  * Accelerator = **GPU** (cell GPU-check nổ to nếu user quên bật).
  * Chạy `scripts/run_unet.py` (class B, out-of-fold) thay cho `run_main_grid.py`.
  * CHỈ `wt_flair` (unet2d.py hardwire FLAIR+WT). et_t1ce cần mở rộng code — bước sau.
  * Gói `.tgz` NHỎ (chỉ `results/unet/` — ~vài nghìn hàng), không cần lôi main 795MB.
  * KHÔNG chạy run_stats ở đây: tải `unet/raw.csv` về, chạy run_stats LOCAL để điền
    Family A (local đã có results/main + results/ceiling).

Chạy:  python notebooks/gen_unet_nb.py  →  notebooks/qigoa_unet.ipynb
"""
from __future__ import annotations

import json
import uuid
from pathlib import Path

cells: list[dict] = []


def md(src: str) -> dict:
    return {"cell_type": "markdown", "source": src.strip("\n"), "metadata": {}}


def code(src: str) -> dict:
    return {"cell_type": "code", "source": src.strip("\n"), "metadata": {},
            "outputs": [], "execution_count": None}


cells.append(md(r"""
# QIGOA Reality-Check — E4 2D U-Net (GPU) · ceiling decomposition (Family A)

**Sinh tự động từ `notebooks/gen_unet_nb.py`.** Không sửa tay — sửa script sinh rồi chạy lại.

> ⚠️ **NGUỒN SỐ cho `family_a_superiority.csv`** (U-Net vs oracle level-set) — bậc "pixel-model
> cùng input" của **đóng góp dương #1**. Class B (học) ⇒ **CHỈ chấm out-of-fold** (prereg A3).

**Cấu hình bắt buộc (panel ⚙️):** Internet **ON** · Accelerator **GPU** (T4/P100) · Add Input
`awsaf49/brats20-dataset-training-validation`. Cell GPU-check sẽ DỪNG nếu quên bật GPU.

**Phạm vi:** chỉ `wt_flair` (input=FLAIR, mask=WT). `et_t1ce` cần mở rộng `unet2d.py` — chưa làm.
""".strip()))

# ---------------------------------------------------------------- Cell 0
cells.append(md("## Cell 0 — ★ THAM SỐ (sửa mỗi session nếu cần)"))
cells.append(code(r"""
# Bat cell RESTORE (Cell R) neu /kaggle/working da xoa va ban co .tgz unet session truoc.
RESTORE_FROM_TGZ = False

# NGAN SACH WALL-CLOCK: Cell RUN tu dung em khi het gio -> Cell dong goi van chay ->
# run KET THUC THANH CONG -> Kaggle chac chan luu tgz. run_unet flush sau moi BN +
# --resume bo qua (fold,seed) da xong -> kill giua chung an toan.
E4_WALL_BUDGET_H = 10.5

print('RESTORE_FROM_TGZ =', RESTORE_FROM_TGZ)
print('E4_WALL_BUDGET_H =', E4_WALL_BUDGET_H, 'gio')
""".strip()))

# ---------------------------------------------------------------- Cell 1
cells.append(md("## Cell 1 — lấy code + guard đồng bộ repo + helper"))
cells.append(code(r"""
import subprocess, sys, os, pathlib, time

REPO, DIR = 'https://github.com/HoangLong08/Paper-DAU.git', '/kaggle/working/qigoa'

if pathlib.Path(DIR, '.git').is_dir():
    subprocess.run(['git', '-C', DIR, 'fetch', 'origin', 'main'], check=True)
    subprocess.run(['git', '-C', DIR, 'reset', '--hard', 'origin/main'], check=True)
else:
    subprocess.run(['git', 'clone', REPO, DIR], check=True)

COMMIT = subprocess.run(['git', '-C', DIR, 'rev-parse', 'HEAD'],
                        capture_output=True, text=True).stdout.strip()
print('git commit:', COMMIT, '<- vao dong provenance docs/RESULTS.md')

NEEDED = ('scripts/run_unet.py', 'scripts/make_splits.py', 'configs/exp_main.yaml',
          'src/baselines/unet2d.py')
missing = [f for f in NEEDED if not pathlib.Path(DIR, f).exists()]
if missing:
    raise RuntimeError(f'THIEU FILE: {missing} -> repo chua dong bo. DUNG.')

import yaml
_cfg = yaml.safe_load(open(pathlib.Path(DIR, 'configs/exp_main.yaml'), encoding='utf-8'))
if 'unet' not in _cfg:
    raise RuntimeError('configs/exp_main.yaml CHUA co block "unet:" -> push commit moi truoc. DUNG.')

os.chdir(DIR); print('cwd =', os.getcwd())


def sh(args, fail_msg=''):
    args = [str(a) for a in args]
    print('\n$ ' + ' '.join(args), flush=True)
    rc = subprocess.run(args, cwd=DIR).returncode
    if rc != 0:
        raise RuntimeError('[FAIL rc=%d] %s\n%s' % (rc, ' '.join(args), fail_msg))
    return rc


def sh_budget(args, budget_s, fail_msg=''):
    args = [str(a) for a in args]
    print('\n$ (budget %.1fh) ' % (budget_s / 3600) + ' '.join(args), flush=True)
    try:
        rc = subprocess.run(args, cwd=DIR, timeout=budget_s).returncode
    except subprocess.TimeoutExpired:
        print('\n[BUDGET] Het %.1fh -> DUNG EM (da checkpoint tung (fold,seed)).' % (budget_s / 3600), flush=True)
        print('[BUDGET] CHUA xong. Session sau: Add Input tgz + RESTORE_FROM_TGZ=True + chay lai.', flush=True)
        return 'TIMEOUT'
    if rc != 0:
        raise RuntimeError('[FAIL rc=%d] %s\n%s' % (rc, ' '.join(args), fail_msg))
    return rc
""".strip()))

cells.append(code(r"""
sh([sys.executable, '-m', 'pip', 'install', '-q', 'medpy', 'tifffile'],
   'Neu medpy loi build: pip install -q git+https://github.com/deepmind/surface-distance.git')
""".strip()))

# ---------------------------------------------------------------- Cell GPU
cells.append(md("## Cell 2 — ★ GPU-check (DỪNG SỚM nếu vắng GPU HOẶC GPU không tương thích)"))
cells.append(code(r"""
import torch
print('torch', torch.__version__, '| cuda available:', torch.cuda.is_available())
if not torch.cuda.is_available():
    raise RuntimeError('KHONG THAY GPU -> Settings > Accelerator > GPU. '
                       'Chay U-Net 25 lan tren CPU la KHONG kha thi. DUNG.')
print('GPU:', torch.cuda.get_device_name(0))
# torch.cuda.is_available()=True VAN co the KHONG chay duoc: torch cu128 tren image
# Kaggle da BO ho tro P100 (sm_60, dai ho tro 7.0-12.0) -> kernel GPU dau tien moi no
# 'no kernel image is available' SAU ~40 phut chuan bi du lieu. Thu 1 kernel THAT o day
# de chet trong 1 giay thay vi 40 phut. Fix: doi Accelerator sang **GPU T4 x2** (sm_75).
try:
    _ = (torch.ones(64, device='cuda') @ torch.ones(64, 64, device='cuda')).sum().item()
    torch.cuda.synchronize()
    print('GPU kernel test: OK -> train duoc.')
except Exception as e:
    cap = torch.cuda.get_device_capability(0)
    raise RuntimeError(
        'GPU CO nhung KHONG chay duoc kernel (capability sm_%d%d): %s\n'
        '=> torch nay khong ho tro GPU dang chon. DOI Settings > Accelerator sang '
        '"GPU T4 x2" (T4 = sm_75, tuong thich) roi Save & Run All lai. DUNG.'
        % (cap[0], cap[1], e))
""".strip()))

# ---------------------------------------------------------------- Cell dataset guard
cells.append(md("## Cell 3 — ★ GUARD + TỰ DÒ đường dẫn BraTS"))
cells.append(code(r"""
inp = pathlib.Path('/kaggle/input')
if not inp.is_dir():
    raise RuntimeError('KHONG CO /kaggle/input -> chay ngoai Kaggle?')
print('Top-level /kaggle/input:', sorted(p.name for p in inp.iterdir()) or '(RONG)')

DEFAULT = pathlib.Path('/kaggle/input/brats20-dataset-training-validation/'
                       'BraTS2020_TrainingData/MICCAI_BraTS2020_TrainingData')
REAL = DEFAULT if DEFAULT.is_dir() else next(
    (p for p in inp.rglob('MICCAI_BraTS2020_TrainingData') if p.is_dir()), None)
if REAL is None:
    raise RuntimeError('KHONG TIM THAY MICCAI_BraTS2020_TrainingData -> Add Input '
                       'awsaf49/brats20-dataset-training-validation chua thanh cong.')
n_cases = sum(1 for p in REAL.iterdir() if p.is_dir())
print('BraTS tai:', REAL, '| so ca:', n_cases)

if REAL != DEFAULT:
    link = pathlib.Path(DIR, 'data/brats20/MICCAI_BraTS2020_TrainingData')
    link.parent.mkdir(parents=True, exist_ok=True)
    if not (link.is_symlink() or link.exists()):
        link.symlink_to(REAL, target_is_directory=True)
        print('Da symlink root_local:', link, '->', REAL)
""".strip()))

# ---------------------------------------------------------------- Cell R
cells.append(md("## Cell R — ♻️ RESTORE (tuỳ chọn) — nạp lại `results/unet/` từ `.tgz`"))
cells.append(code(r"""
import glob, tarfile
if not RESTORE_FROM_TGZ:
    print('RESTORE_FROM_TGZ = False -> bo qua.')
else:
    cands = sorted(glob.glob('/kaggle/input/**/unet_*.tgz', recursive=True)) + \
            sorted(glob.glob('/kaggle/input/**/*.tgz', recursive=True))
    cands = list(dict.fromkeys(cands))
    if not cands:
        raise RuntimeError('RESTORE_FROM_TGZ=True nhung KHONG thay .tgz nao duoi /kaggle/input.')
    src = cands[-1]
    print('Restore tu:', src)
    with tarfile.open(src, 'r:gz') as t:
        t.extractall(DIR)
    raw = pathlib.Path(DIR, 'results/unet/raw.csv')
    n = sum(1 for _ in open(raw, encoding='utf-8', errors='replace')) if raw.exists() else 0
    print('results/unet/raw.csv:', n, 'dong (ke ca banner).')
""".strip()))

# ---------------------------------------------------------------- Cell splits
cells.append(md("## Cell 4 — E0: cohort + split cấp BỆNH NHÂN (idempotent, đã có trong git)"))
cells.append(code(r"""
sh([sys.executable, 'scripts/make_splits.py', '--config', 'configs/exp_main.yaml', '--resume'],
   'E0 FAIL -> DUNG.')
cohort = pathlib.Path('data/splits/brats_cohort.csv')
n_cohort = (sum(1 for _ in open(cohort)) - 1) if cohort.exists() else 0
print('\nE0 OK: cohort =', n_cohort, 'ca.')
""".strip()))

# ---------------------------------------------------------------- Cell RUN
cells.append(md(r"""
## Cell 5 — ★ E4: train U-Net (5 fold × 5 seed, out-of-fold), có ngân sách wall-clock

> 🟢 Tự dừng êm ở `E4_WALL_BUDGET_H`; `--resume` bỏ qua (fold,seed) đã xong. Session sau
> `RESTORE_FROM_TGZ=True` + chạy lại.
""".strip()))
cells.append(code(r"""
_t0 = time.perf_counter()
_rc = sh_budget([sys.executable, 'scripts/run_unet.py', '--config', 'configs/exp_main.yaml', '--resume'],
                int(E4_WALL_BUDGET_H * 3600),
                'E4 U-Net FAIL (loi THAT, khong phai timeout).')
_dt = (time.perf_counter() - _t0) / 60
print('\n[E4] %s sau %.1f phut.' % ('DUNG (het budget)' if _rc == 'TIMEOUT' else 'XONG TRON (rc=0)', _dt))
print('     Ket qua: results/unet/{raw,summary}.csv')
""".strip()))

# ---------------------------------------------------------------- Cell count
cells.append(md("## Cell 6 — 📊 KIỂM ĐẾM tiến độ (25 = 5 fold × 5 seed)"))
cells.append(code(r"""
import pandas as pd
sys.path.insert(0, str(pathlib.Path(DIR, 'scripts')))
from importlib import import_module
_c = import_module('_common')
raw = pathlib.Path('results/unet/raw.csv')
if not raw.exists():
    print('Chua co results/unet/raw.csv.')
else:
    scfg = _c.section(yaml.safe_load(open('configs/exp_main.yaml', encoding='utf-8')), 'unet')
    folds, seeds = scfg.get('folds', [0]), scfg.get('seeds', [0])
    targets = scfg.get('targets', ['wt_flair'])
    expect = len(folds) * len(seeds) * len(targets)
    df = _c.read_results_csv(raw)
    done = df.drop_duplicates(['target', 'fold', 'seed'])[['target', 'fold', 'seed']]
    print('(target,fold,seed) da xong: %d / %d' % (len(done), expect))
    print('so BN co du bao (unique patient_id):', df['patient_id'].nunique(), '(ky vong 368 khi du 5 fold)')
    if 'dice' in df.columns:
        d = pd.to_numeric(df['dice'], errors='coerce')
        print('Dice U-Net (moi hang): median=%.4f  IQR=[%.4f, %.4f]' % (
            d.median(), d.quantile(.25), d.quantile(.75)))
    miss = [(t, f, s) for t in targets for f in folds for s in seeds
            if not ((done['target'] == t) & (done['fold'] == f) & (done['seed'] == s)).any()]
    print('CON THIEU (target,fold,seed):', miss if miss else '(HET - E4 DAY DU)')
""".strip()))

# ---------------------------------------------------------------- Cell package
cells.append(md("## Cell 7 — đóng gói `results/unet/` (nhỏ) + manifest"))
cells.append(code(r"""
import tarfile, json, glob
stamp = time.strftime('%Y%m%d_%H%M')
tgz = '/kaggle/working/unet_%s.tgz' % stamp
with tarfile.open(tgz, 'w:gz') as t:
    if pathlib.Path('results/unet').is_dir():
        t.add('results/unet')
    if pathlib.Path('data/splits').is_dir():
        t.add('data/splits')
    # Checkpoint: resume THẬT dựa trên raw.csv (done_keys), KHONG dua tren .pt —
    # nhung van goi de tai lap / kiem toan duoc. Quet ca 2 cho vi bug output_dir
    # (07-22) tung day .pt vao results/main/checkpoints.
    for ck in ('results/unet/checkpoints', 'results/main/checkpoints'):
        if pathlib.Path(ck).is_dir():
            t.add(ck)
    # Cuu ho: neu bug output_dir tai dien, raw.csv U-Net nam o results/main/raw.csv.
    for stray in glob.glob('results/main/raw.csv'):
        t.add(stray, arcname='RESCUE_results_main_raw.csv')
print('Da dong goi:', tgz, '-> tai ve tu tab Output.')
print('Noi dung tgz:', *sorted(n for n in tarfile.open(tgz).getnames()
                               if n.count('/') <= 2), sep='\n  ')
for mf in sorted(glob.glob('results/unet/run-manifest.json')):
    print('\n' + '=' * 60 + '\n' + mf + '\n' + '=' * 60)
    print(json.dumps(json.load(open(mf)), indent=2, ensure_ascii=False))
print('\ngit commit:', COMMIT)
print('Buoc sau (LOCAL): giai nen tgz -> copy results/unet vao repo -> '
      'python scripts/run_stats.py --config configs/exp_main.yaml (dien Family A).')
""".strip()))

# --------------------------------------------------------------------------- #
for c in cells:
    c["id"] = str(uuid.uuid4())

nb = {"cells": cells,
      "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python", "version": "3.10.13"},
                   "accelerator": "GPU"},
      "nbformat": 4, "nbformat_minor": 4}

out = Path(__file__).resolve().parent / "qigoa_unet.ipynb"
out.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print("Da sinh:", out, "|", len(cells), "cells")

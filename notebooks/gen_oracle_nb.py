# -*- coding: utf-8 -*-
"""Sinh notebook ORACLE gon + chuoi `text` da double-encode san cho save_notebook."""
import json
from pathlib import Path

NB_OUT = Path(r"d:\HoangLong\Personal\paper\3-\notebooks\qigoa_oracle.ipynb")
EMBED_OUT = Path(r"C:\Users\Admin\AppData\Local\Temp\claude\d--HoangLong-Personal-paper-3-\31f5043b-7558-4a52-a0a7-95f1b5662d50\scratchpad\oracle_text.txt")


def md(src):
    return {"cell_type": "markdown", "metadata": {}, "source": src}


def code(src):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": src}


CLONE = r'''# Batch-safe: moi loi -> raise -> Kaggle danh dau run FAILED.
import subprocess, sys, os, pathlib
REPO, DIR = 'https://github.com/HoangLong08/Paper-DAU.git', '/kaggle/working/qigoa'
if pathlib.Path(DIR, '.git').is_dir():
    subprocess.run(['git', '-C', DIR, 'fetch', 'origin', 'main'], check=True)
    subprocess.run(['git', '-C', DIR, 'reset', '--hard', 'origin/main'], check=True)
else:
    subprocess.run(['git', 'clone', REPO, DIR], check=True)
COMMIT = subprocess.run(['git', '-C', DIR, 'rev-parse', 'HEAD'],
                        capture_output=True, text=True).stdout.strip()
print('git commit:', COMMIT)
NEEDED = ('scripts/run_ceiling.py', 'scripts/make_splits.py', 'configs/exp_ceiling.yaml',
          'configs/exp_main.yaml')
missing = [f for f in NEEDED if not pathlib.Path(DIR, f).exists()]
if missing:
    raise RuntimeError('THIEU FILE: %s -> repo chua dong bo. DUNG.' % (missing,))
os.chdir(DIR)
print('cwd =', os.getcwd())

def sh(args, fail_msg=''):
    args = [str(a) for a in args]
    print('\n$ ' + ' '.join(args), flush=True)
    rc = subprocess.run(args, cwd=DIR).returncode
    if rc != 0:
        raise RuntimeError('[FAIL rc=%d] %s\n%s' % (rc, ' '.join(args), fail_msg))
    return rc

sh([sys.executable, '-m', 'pip', 'install', '-q', 'medpy', 'tifffile'], 'medpy build loi.')'''


DATASET = r'''# GUARD + tu do duong dan BraTS (Kaggle mount tai /kaggle/input/datasets/awsaf49/...).
import itertools
inp = pathlib.Path('/kaggle/input')
if not inp.is_dir():
    raise RuntimeError('KHONG CO /kaggle/input -> chay ngoai Kaggle?')
print('Top-level /kaggle/input:', sorted(p.name for p in inp.iterdir()) or '(RONG)')
DEFAULT = pathlib.Path('/kaggle/input/brats20-dataset-training-validation/'
                       'BraTS2020_TrainingData/MICCAI_BraTS2020_TrainingData')
if DEFAULT.is_dir():
    REAL = DEFAULT
else:
    hits = [p for p in inp.rglob('MICCAI_BraTS2020_TrainingData') if p.is_dir()]
    REAL = hits[0] if hits else None
if REAL is None:
    raise RuntimeError('KHONG TIM THAY MICCAI_BraTS2020_TrainingData duoi /kaggle/input.\n'
                       'Top-level: ' + (', '.join(sorted(p.name for p in inp.iterdir())) or '(RONG)') + '\n'
                       'LUU Y: Kaggle chi luu Add Input khi ban bam Save Version.')
n_cases = sum(1 for p in REAL.iterdir() if p.is_dir())
print('Tim thay BraTS tai:', REAL, '| so ca:', n_cases)
if REAL != DEFAULT:
    link = pathlib.Path(DIR, 'data/brats20/MICCAI_BraTS2020_TrainingData')
    link.parent.mkdir(parents=True, exist_ok=True)
    if not (link.is_symlink() or link.exists()):
        link.symlink_to(REAL, target_is_directory=True)
    print('Da symlink root_local ->', REAL)'''


RUN = r'''# make_splits (folds cho P5, tranh WARN) + run_ceiling --stage all (oracle ladder + classical + P5).
sh([sys.executable, 'scripts/make_splits.py', '--config', 'configs/exp_ceiling.yaml', '--resume'],
   'make_splits FAIL.')
sh([sys.executable, 'scripts/run_ceiling.py', '--config', 'configs/exp_ceiling.yaml',
    '--stage', 'all', '--resume'],
   'run_ceiling --stage all FAIL (loi ky thuat, khac voi mot ket qua).')
print('\nOK -> results/ceiling/{raw,qstar,summary}.csv co oracle ladder + classical + P5.')'''


PACK = r'''# In thang tran (loai C) + dong goi.
import pandas as pd, time, tarfile, glob, json
c = pd.read_csv('results/ceiling/summary.csv', comment='#')
print('=== CEILING SUMMARY (method_class + dice_median) ===')
print(c[['target','include_zero_bg','method','method_class','n_patients','dice_median']].to_string(index=False))
stamp = time.strftime('%Y%m%d_%H%M')
tgz = '/kaggle/working/ceiling_%s.tgz' % stamp
with tarfile.open(tgz, 'w:gz') as t:
    for d in ('results/ceiling', 'data/splits'):
        if pathlib.Path(d).is_dir():
            t.add(d)
print('\nDa dong goi:', tgz)
for m in sorted(glob.glob('results/ceiling/run-manifest.json')):
    print(m, '->', json.dumps(json.load(open(m))['extra'], ensure_ascii=False)[:300])
print('git commit:', COMMIT)'''


cells = [
    md("# QIGOA - Stage ORACLE (dong rui ro #4 + thang tran cho Bang V / Hinh 4)\n\n"
       "Chay `run_ceiling.py --stage all` tren `exp_ceiling.yaml`: oracle_single ⊆ oracle_interval "
       "⊆ oracle_levelset (loai C, dung GT) + classical (A) + P5 (B). ~35 phut CPU.\n\n"
       "**Cau hinh:** Internet ON - Accelerator **None** - Input `awsaf49/brats20-dataset-training-validation`.\n\n"
       "Sinh tu `notebooks/qigoa_oracle.ipynb`. Moi lenh qua `sh()` -> raise -> FAILED (khong troi am tham)."),
    md("## Cell 1 - clone + guard + pip"),
    code(CLONE),
    md("## Cell 2 - dataset auto-detect + symlink"),
    code(DATASET),
    md("## Cell 3 - make_splits + run_ceiling --stage all"),
    code(RUN),
    md("## Cell 4 - in thang tran + dong goi"),
    code(PACK),
]

nb = {"metadata": {"kernelspec": {"language": "python", "display_name": "Python 3", "name": "python3"},
                   "language_info": {"name": "python"}},
      "nbformat_minor": 4, "nbformat": 4, "cells": cells}

# Ghi .ipynb (source dang list dong cho dep + validate)
nb_file = json.loads(json.dumps(nb))
for c in nb_file["cells"]:
    s = c["source"]
    c["source"] = [l + "\n" for l in s.split("\n")[:-1]] + [s.split("\n")[-1]] if "\n" in s else [s]
NB_OUT.write_text(json.dumps(nb_file, indent=1, ensure_ascii=False), encoding="utf-8")

# Chuoi `text` cho save_notebook: notebook JSON (source dang string) -> json string
nb_str = json.dumps(nb, ensure_ascii=False)
EMBED_OUT.write_text(nb_str, encoding="utf-8")

# Validate compile moi code cell
import ast
bad = 0
for c in cells:
    if c["cell_type"] == "code":
        try:
            ast.parse(c["source"])
        except SyntaxError as e:
            bad += 1
            print("SYNTAX ERROR:", e)
print("Da ghi:", NB_OUT)
print("Da ghi text cho save_notebook:", EMBED_OUT, "(", len(nb_str), "ky tu )")
print("compile:", "OK" if bad == 0 else f"{bad} loi")

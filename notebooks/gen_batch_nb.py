# -*- coding: utf-8 -*-
"""Sinh notebooks/qigoa_kaggle_batch.ipynb — notebook TUYEN TINH, batch-safe.

Vi sao co file nay: notebooks/qigoa_kaggle.ipynb duoc thiet ke cho che do TUONG TAC
(co co EXPERIMENT, cell (f2) nam truoc cell (e) tren dia). Chay Save & Run All tren
no se abort o guard cua (f2). Ban nay chay top-to-bottom duoc, va MOI cong cung
dung subprocess + returncode + raise thay vi `!python` (magic `!` khong truyen exit code).
"""
import json
from pathlib import Path

OUT = Path(r"d:\HoangLong\Personal\paper\3-\notebooks\qigoa_kaggle_batch.ipynb")


def md(src):
    return {"cell_type": "markdown", "metadata": {}, "source": src.strip("\n").split("\n")}


def code(src):
    lines = src.strip("\n").split("\n")
    return {"cell_type": "code", "execution_count": None, "metadata": {},
            "outputs": [], "source": [l + "\n" for l in lines[:-1]] + [lines[-1]]}


cells = []

cells.append(md(r"""
# QIGOA Reality-Check — LÔ QUYẾT ĐỊNH (bản BATCH, Save & Run All)

**Sinh tự động từ `docs/huong-dan-setup-kaggle.md` Bước 2.** Không sửa tay — sửa script sinh rồi tạo lại.

> ⚠️ **Đây KHÔNG phải `notebooks/qigoa_kaggle.ipynb`.** Bản kia dành cho chạy **tương tác** (có cờ `EXPERIMENT`);
> chạy Save & Run All trên nó sẽ abort ở guard của cell (f2). Bản này **tuyến tính**, chạy top-to-bottom.

**Cấu hình bắt buộc:** Internet **ON** · Accelerator **None (CPU)** · Add Input `awsaf49/brats20-dataset-training-validation`.

**Ước tính:** ~3–5 giờ CPU. Session Kaggle tối đa 12h.

### Vì sao mọi cổng cứng ở đây dùng `subprocess` chứ không `!python`

Magic `!` **không truyền exit code**. Trong một batch run không có người ngồi xem, `!python -m pytest` fail
chỉ in chữ đỏ rồi **chạy tiếp** sang E0/E1/P5 — cổng cứng không hề gác. Đó đúng loại lỗi âm thầm mà
`docs/huong-dan-setup-kaggle.md:75` cảnh báo. Ở đây mọi lệnh đi qua `sh()` → `raise` → Kaggle đánh dấu run **FAILED**.

### Kỷ luật (CLAUDE.md §2)

- Số từ `exp_week1.yaml` là **`screening`** (n=60, 3 seed) — quyết định được, **công bố không được**.
- Notebook này **không nhúng số kết quả**. Output cell không phải nguồn số liệu; `results/*.csv` mới là.
- Mọi số vào paper phải truy được về `results/` qua `docs/RESULTS.md`.
"""))

cells.append(md(r"""
## Cell 1 — lấy code + guard đồng bộ repo
"""))

cells.append(code(r'''
# Batch-safe: MOI loi -> raise -> Kaggle danh dau run FAILED (khong troi qua am tham).
import subprocess, sys, os, pathlib

REPO, DIR = 'https://github.com/HoangLong08/Paper-DAU.git', '/kaggle/working/qigoa'

# KHONG dung `git clone` tran: /kaggle/working/ SONG SOT qua cac session (no la Output
# cua notebook), nen re-run mot clone tran vao thu muc da ton tai -> "fatal: destination
# path already exists", clone KHONG lam gi, va rev-parse ngay sau do van in ra hash CU —
# trong y het thanh cong. Da can mot lan that (17/07/2026).
if pathlib.Path(DIR, '.git').is_dir():
    subprocess.run(['git', '-C', DIR, 'fetch', 'origin', 'main'], check=True)
    subprocess.run(['git', '-C', DIR, 'reset', '--hard', 'origin/main'], check=True)
else:
    subprocess.run(['git', 'clone', REPO, DIR], check=True)

COMMIT = subprocess.run(['git', '-C', DIR, 'rev-parse', 'HEAD'],
                        capture_output=True, text=True).stdout.strip()
print('git commit:', COMMIT, '<- vao dong provenance trong docs/RESULTS.md')

NEEDED = ('scripts/make_splits.py', 'scripts/run_exact_check.py', 'scripts/run_ceiling.py',
          'scripts/run_main_grid.py', 'scripts/run_stats.py', 'configs/exp_main.yaml',
          'configs/exp_ceiling.yaml', 'configs/exp_week1.yaml')
missing = [f for f in NEEDED if not pathlib.Path(DIR, f).exists()]
if missing:
    raise RuntimeError(f'THIEU FILE: {missing} -> repo chua dong bo. DUNG, dung chay tiep.')

os.chdir(DIR)
print('cwd =', os.getcwd())


def sh(args, fail_msg=''):
    """Chay lenh, stream log truc tiep, raise neu rc != 0.

    Day la thu thay cho `!python ...`: magic `!` nuot exit code, nen mot cong cung FAIL
    se troi qua trong batch run. sh() bien moi that bai thanh exception -> abort ca run.
    """
    args = [str(a) for a in args]
    print('\n$ ' + ' '.join(args), flush=True)
    rc = subprocess.run(args, cwd=DIR).returncode
    if rc != 0:
        raise RuntimeError('[FAIL rc=%d] %s\n%s' % (rc, ' '.join(args), fail_msg))
    return rc
'''))

cells.append(code(r"""
# Kaggle da co san numpy/scipy/scikit-image/scikit-learn/pandas/nibabel/PyYAML/matplotlib/torch/tqdm.
# KHONG `pip install -r requirements.txt` — no pha moi truong da pin cua Kaggle.
sh([sys.executable, '-m', 'pip', 'install', '-q', 'medpy', 'tifffile'],
   'Neu medpy loi build, thay bang:\n'
   "  pip install -q git+https://github.com/deepmind/surface-distance.git")
"""))

cells.append(md(r"""
## Cell 2 — ★ GUARD + TỰ DÒ đường dẫn BraTS

Run v3 (17/07/2026) cho thấy Kaggle mount dataset dưới thư mục tên **`datasets`**, KHÔNG phải tên
slug như `data.root_kaggle` giả định — nên guard hard-fail bản đầu chặn nhầm. Cell này **tự tìm**
`MICCAI_BraTS2020_TrainingData` ở bất kỳ đâu dưới `/kaggle/input`, rồi **symlink** vào `data.root_local`.

> **Vì sao symlink chứ không sửa config:** `_common.data_root()` thử `root_kaggle` trước, không thấy
> thì rơi về `root_local` (`data/brats20/MICCAI_BraTS2020_TrainingData`). Symlink vào đó ⇒ script tìm
> thấy mà **config không bị sửa một dòng nào** (CLAUDE.md §5.1: config là nguồn sự thật duy nhất).
> Notebook uốn theo môi trường, không phải ngược lại.
"""))

cells.append(code(r"""
import itertools

inp = pathlib.Path('/kaggle/input')
if not inp.is_dir():
    raise RuntimeError('KHONG CO /kaggle/input -> notebook nay chay ngoai Kaggle?')

print('Top-level /kaggle/input:', sorted(p.name for p in inp.iterdir()) or '(RONG)')
print('\nCay /kaggle/input (30 muc dau, de chan doan layout):')
for p in itertools.islice(inp.rglob('*'), 30):
    print('   ', p)

DEFAULT = pathlib.Path('/kaggle/input/brats20-dataset-training-validation/'
                       'BraTS2020_TrainingData/MICCAI_BraTS2020_TrainingData')
if DEFAULT.is_dir():
    REAL = DEFAULT
else:
    hits = [p for p in inp.rglob('MICCAI_BraTS2020_TrainingData') if p.is_dir()]
    REAL = hits[0] if hits else None

if REAL is None:
    raise RuntimeError(
        'KHONG TIM THAY MICCAI_BraTS2020_TrainingData o BAT KY dau duoi /kaggle/input.\n'
        'Top-level: ' + (', '.join(sorted(p.name for p in inp.iterdir())) or '(RONG)') + '\n'
        '=> Add Input awsaf49/brats20-dataset-training-validation chua thanh cong.\n'
        'LUU Y: Kaggle chi luu Add Input khi ban bam Save Version — truoc do no chi nam\n'
        'trong ban nhap tren trinh duyet, server KHONG thay.')

n_cases = sum(1 for p in REAL.iterdir() if p.is_dir())
print('\nTim thay BraTS tai:', REAL)
print('So thu muc ca:', n_cases)
if n_cases != 369:
    print('[CANH BAO] n =', n_cases, '!= 369 (ky vong exp_main.yaml) -> kiem tra version '
          'dataset TRUOC khi tin bat ky so nao.')

# Khong nam dung root_kaggle => symlink vao root_local, KHONG sua config.
if REAL != DEFAULT:
    link = pathlib.Path(DIR, 'data/brats20/MICCAI_BraTS2020_TrainingData')
    link.parent.mkdir(parents=True, exist_ok=True)
    if link.is_symlink() or link.exists():
        print('\nLink da ton tai:', link)
    else:
        link.symlink_to(REAL, target_is_directory=True)
        print('\nDa symlink root_local:', link, '->', REAL)
    print('=> _common.data_root() se tim thay qua data.root_local (config KHONG bi sua).')
"""))

cells.append(md(r"""
## Cell 3 — ★ CỔNG CỨNG 1: unit test

| Fail | Nghĩa là |
|---|---|
| `test_exact_dp` | Mọi kết luận P2 dựng trên DP ⇒ **DỪNG TOÀN BỘ** |
| `test_nfe_budget` | **Lưới vô hiệu** — đúng lỗi đã giết lô cũ (thừa 13,4% NFE) |
| `test_degeneracy` | Cơ chế suy biến không đúng như phát biểu ⇒ đọc lại prereg §6/A1 |
"""))

cells.append(code(r"""
sh([sys.executable, '-m', 'pytest', 'tests/test_exact_dp.py', 'tests/test_nfe_budget.py',
    'tests/test_degeneracy.py', '-q'],
   'CONG CUNG 1 FAIL -> DUNG TOAN BO. Khong chay bat ky experiment nao.\n'
   ' - test_exact_dp  : moi ket luan P2 dung tren DP. Debug DAU TIEN = audit quy uoc\n'
   '                    (0log0, lop rong, nen cuong-do-0) — KHONG phai sua DP (A5b/A5c).\n'
   ' - test_nfe_budget: LUOI VO HIEU (loi da giet lo cu: +13,4% NFE).\n'
   ' - test_degeneracy: co che suy bien khong dung nhu phat bieu -> prereg §6/A1.')
print('\n3 CONG CUNG PASS -> duoc phep chay experiment.')
"""))

cells.append(md(r"""
## Cell 4 — E0: cohort + split cấp BỆNH NHÂN

Sinh `data/splits/brats_cohort.csv` + `fold_{0..4}.json`, chia ở **cấp BỆNH NHÂN**, phân tầng
grade × tertile thể tích WT (A3).

> 🔴 **Không bỏ qua.** `run_ceiling.py` không thấy `fold_*.json` sẽ **âm thầm rơi về chia vòng tròn**
> kèm một dòng `[WARN]` dễ trôi qua mắt — và Cell 6 (P5) sẽ đánh giá **đóng góp dương của bài**
> trên split không phân tầng. Đó đúng thứ kỷ luật mà bài này đi tố cáo người khác vi phạm.
"""))

cells.append(code(r"""
import glob

sh([sys.executable, 'scripts/make_splits.py', '--config', 'configs/exp_main.yaml', '--resume'],
   'E0 FAIL -> DUNG. Neu loi la "Khong thay du lieu BraTS" thi xem guard dataset o Cell 2.')

folds = sorted(glob.glob('data/splits/fold_*.json'))
if not folds:
    raise RuntimeError(
        'E0 rc=0 nhung KHONG sinh fold_*.json -> P5 (Cell 6) se chay tren split vong tron\n'
        'KHONG phan tang (A3) => ket qua P5 khong dung lam dong gop duong duoc.')
print('\nE0 OK:', len(folds), 'fold ->', ', '.join(folds))
"""))

cells.append(md(r"""
## Cell 5 — ★ CỔNG CỨNG 2: E1 bit-exact trên dữ liệu THẬT → **BẢNG II**

DP phải khớp vét cạn tại k=2,3: `|f_DP − f_brute| ≤ 1e-9` **VÀ** mask cảm sinh giống hệt (A5a).
Cho ra `results/exact/dp_vs_bruteforce.csv` → **Bảng II — con số thật đầu tiên vào bản thảo**.

> 🔴 **FAIL ⇒ DỪNG TOÀN BỘ.** Bước debug **ĐẦU TIÊN** là **audit quy ước histogram**
> (`0log0` · lớp rỗng · ngưỡng trùng · **có tính nền cường-độ-0 hay không** — A5b/A5c),
> **KHÔNG** phải sửa DP. Xác suất lỗi nằm ở quy ước cao hơn nhiều so với ở DP.
"""))

cells.append(code(r"""
sh([sys.executable, 'scripts/run_exact_check.py', '--config', 'configs/exp_main.yaml'],
   'E1 FAIL -> DUNG TOAN BO. Buoc debug DAU TIEN la audit QUY UOC HISTOGRAM\n'
   '(0log0 · lop rong · nguong trung · co tinh nen cuong-do-0 khong — A5b/A5c),\n'
   'KHONG phai sua DP. Xac suat loi nam o quy uoc cao hon nhieu so voi o DP.')

out = pathlib.Path('results/exact/dp_vs_bruteforce.csv')
if not out.exists():
    raise RuntimeError('E1 rc=0 nhung khong co ' + str(out) + ' -> khong co Bang II. DUNG.')
print('\nE1 PASS ->', out, '= BANG II (so THAT dau tien vao ban thao).')
"""))

cells.append(md(r"""
## Cell 6 — RỦI RO #2: P5 nested CV → *bài có đóng góp dương không?*

Ngưỡng 1-tham-số (phân vị q) vs 7 metaheuristic, **nested CV cấp bệnh nhân**: `q*` fit trên
outer-train, **đóng băng**, đánh giá out-of-fold.

- **P5 THẮNG** ⇒ đóng góp dương đứng vững.
- **P5 THUA** ⇒ **không phải bài chết**. Fallback đã khoá TRƯỚC khi thấy số (prereg A10 #2):
  đóng góp dương rơi về **ceiling decomposition + công cụ chẩn đoán + checklist**.
  Ghi kết quả âm vào `RESULTS.md` như mọi run khác — **run âm là dữ liệu**.

> Lưu ý: `raise` ở cell này nghĩa là **lỗi KỸ THUẬT** (script hỏng), **khác** với "P5 thua".
> P5 thua là một *kết quả*, và nó sẽ nằm trong CSV chứ không làm cell fail.
"""))

cells.append(code(r"""
sh([sys.executable, 'scripts/run_ceiling.py', '--config', 'configs/exp_ceiling.yaml',
    '--stage', 'p5_nested_cv'],
   'P5 loi KY THUAT (KHAC voi "P5 thua" — P5 thua la mot ket qua, nam trong CSV).\n'
   'Loi o day = script hong hoac thieu fold_*.json. Phai sua truoc khi doc so.')
print('\nP5 xong -> doc results/ceiling/qstar.csv.')
"""))

cells.append(md(r"""
## Cell 7 — RỦI RO #3 + #4: lưới sàng lọc

`configs/exp_week1.yaml` = lưới **sàng lọc**: n=60 ca (thay vì 369), 3 seed (thay vì 5), 1 biến thể bg —
nhưng **giữ trọn trục k và cả 4 decoding rule**, vì đó chính là hai câu hỏi:

| Rủi ro | Câu hỏi | Kết quả giết bài |
|---|---|---|
| **#3** | Spearman(k, Dice) tính RIÊNG cho **từng** decoding rule | Tương quan âm **chỉ** dưới rule `brightest` ⇒ headline *"metrics are anti-correlated"* **SAI** |
| **#4** | `morph` vs `oracle_interval` | `morph` **vượt** oracle ⇒ **P4 tự bác bỏ** |

> ⛔ **Số từ `exp_week1.yaml` KHÔNG vào Bảng III / Hình 2 / Hình 3.** Nó trả lời **dấu và hướng**,
> đủ để quyết định, **không đủ để công bố**. Dòng provenance sinh từ đây **phải ghi chữ `screening`**.
> Kết quả **sát ngưỡng** ⇒ **không kết luận**, chạy lại trên `exp_main.yaml`.
"""))

cells.append(code(r"""
sh([sys.executable, 'scripts/run_main_grid.py', '--config', 'configs/exp_week1.yaml', '--resume'],
   'Luoi sang loc FAIL -> khong tra loi duoc rui ro #3/#4.')
sh([sys.executable, 'scripts/run_stats.py', '--config', 'configs/exp_week1.yaml'],
   'run_stats FAIL.')

print('\n=> Doc results/week1/stats/ + results/ceiling/qstar.csv TRUOC khi mo E2.')
print('   So tu exp_week1.yaml la SCREENING (n=60, 3 seed): tra loi DAU va HUONG.')
print('   KHONG vao Bang III / Hinh 2 / Hinh 3. Provenance PHAI ghi chu "screening".')
"""))

cells.append(md(r"""
## Cell 8 — đóng gói + in `run-manifest.json`

`/kaggle/working/` **mất khi session hết hạn** ⇒ tải `.tgz` từ tab **Output**.

**Không có manifest = run không tồn tại với paper** (CLAUDE.md §5.2).
"""))

cells.append(code(r"""
import time, json, tarfile

stamp = time.strftime('%Y%m%d_%H%M')
tgz = '/kaggle/working/results_%s.tgz' % stamp
with tarfile.open(tgz, 'w:gz') as t:
    for d in ('results', 'data/splits'):
        if pathlib.Path(d).is_dir():
            t.add(d)
print('Da dong goi:', tgz)
print('Tai ve tu tab Output -> giai nen vao repo -> them provenance vao docs/RESULTS.md.')

manifests = sorted(glob.glob('results/**/run-manifest.json', recursive=True))
if not manifests:
    print('\n[CANH BAO] KHONG co run-manifest.json trong results/.')
    print('=> Run nay KHONG TON TAI voi paper (CLAUDE.md §5.2).')
for m in manifests:
    print('\n' + '=' * 70 + '\n' + m + '\n' + '=' * 70)
    print(json.dumps(json.load(open(m)), indent=2, ensure_ascii=False))

print('\n' + '=' * 70)
print('git commit cua lo nay:', COMMIT)
print('Mau dong provenance cho docs/RESULTS.md:')
print('  Bang II <- results/exact/dp_vs_bruteforce.csv <- scripts/run_exact_check.py '
      '--config configs/exp_main.yaml @commit ' + COMMIT)
print('  [screening] Rui ro #3/#4 <- results/week1/raw.csv <- scripts/run_main_grid.py '
      '--config configs/exp_week1.yaml @commit ' + COMMIT + ', seeds {0..2}')
"""))

nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.10.13"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
print("Da ghi:", OUT)
print("So cell:", len(cells), "| code:", sum(1 for c in cells if c["cell_type"] == "code"))

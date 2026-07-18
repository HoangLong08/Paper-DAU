# -*- coding: utf-8 -*-
"""Sinh notebooks/qigoa_e2_main.ipynb — E2 LƯỚI CHÍNH (exp_main.yaml, n=369, 5 seed).

Vi sao co file nay (ky luat repo, CLAUDE.md §5.1): notebook la ARTIFACT sinh ra, KHONG
sua tay. Sua logic -> sua script nay -> chay lai: `python notebooks/gen_e2_nb.py`.

E2 KHAC "lo quyet dinh" (gen_batch_nb.py) o 4 diem:
  1. THAM SO K_SUBSET o dau -> chia stage theo k qua NHIEU session (E2 ~20h > 12h/session).
  2. RESUME that su + cell RESTORE tu .tgz -> song sot ca khi /kaggle/working bi xoa.
  3. Cell KIEM DEM tien do -> doc raw.csv, bao % hoan thanh tung k, de xuat K_SUBSET ke tiep.
  4. E1 + unit-test la CONG bat buoc nhung SKIP neu output da ton tai (tiet kiem gio cho luoi).

⚠️ So tu day la SO CUA PAPER (Bang III / Hinh 2 / Hinh 3) — KHONG phai screening.
   exp_main.yaml: n=369, seeds {0..4}, ca 2 bg (A8/A5c). Moi so phai truy duoc ve results/main/.
"""
import json
from pathlib import Path

OUT = Path(r"d:\HoangLong\Personal\paper\3-\notebooks\qigoa_e2_main.ipynb")


def md(src):
    return {"cell_type": "markdown", "metadata": {}, "source": src.strip("\n").split("\n")}


def code(src):
    lines = src.strip("\n").split("\n")
    return {"cell_type": "code", "execution_count": None, "metadata": {},
            "outputs": [], "source": [l + "\n" for l in lines[:-1]] + [lines[-1]]}


cells = []

cells.append(md(r"""
# QIGOA Reality-Check — E2 LƯỚI CHÍNH (`exp_main.yaml`, n=369, 5 seed)

**Sinh tự động từ `notebooks/gen_e2_nb.py`.** Không sửa tay — sửa script sinh rồi chạy lại.

> ⚠️ **Đây là NGUỒN SỐ CHO BẢN THẢO** (Bảng III · Hình 2 CD · Hình 3 Goodhart), **khác** lô
> quyết định (`qigoa_kaggle_batch.ipynb`, chỉ `screening` n=60/3 seed). Mọi số phải truy được
> về `results/main/` qua `docs/RESULTS.md`. **Không nhúng số kết quả vào notebook.**

**Cấu hình bắt buộc (panel ⚙️):** Internet **ON** · Accelerator **None (CPU)** · Add Input
`awsaf49/brats20-dataset-training-validation`. **KHÔNG bật GPU** (E2 thuần CPU).

---

## 🔴 GIAO THỨC NHIỀU SESSION — đọc trước khi chạy

E2 = `n=369 × 2 target × 2 bg × 7 giá trị k × (9 metaheuristic × 5 seed + DP + 5 classical)`
+ 4 decode-rule. Đây là **lưới gấp ~20× lưới sàng lọc** (screening n=60/3 seed/1 bg đã mất ~7h).
⇒ **KHÔNG chạy hết trong một session 12h.** Cách chạy:

1. **Đặt `K_SUBSET`** ở Cell 0 = một tập con của `k_list` (VD `"2,3"`), rồi **Save & Run** hoặc
   chạy tương tác top-to-bottom.
2. Session bị Kaggle cắt ở 12h ⇒ **chạy lại y hệt** (cùng `K_SUBSET`). `--resume` + checkpoint
   **sau mỗi ô** `(patient, k, algo, seed)` bỏ qua ô đã tính ⇒ tiếp đúng chỗ dừng.
3. Cell **KIỂM ĐẾM** (cuối) in **% hoàn thành từng k** và **đề xuất `K_SUBSET` kế tiếp**. Khi một
   `K_SUBSET` đạt 100%, đổi sang tập con còn lại rồi lặp.
4. **Cuối MỖI session: tải `.tgz` từ tab Output** (Cell đóng gói). `/kaggle/working` có thể bị xoá
   ⇒ tgz là bản sao lưng. Nếu working dir bị xoá, dùng **Cell RESTORE** để nạp lại rồi `--resume`
   tiếp — không mất giờ đã chạy.

> **Vì sao chia theo k mà vẫn hợp lệ:** `k_list`, `seeds`, `n_patients` đã preregister trong
> `exp_main.yaml`. `--k-subset` chỉ chọn **tập con** của lưới đã khoá (script từ chối k ngoài
> `k_list`), **không** mở rộng nó. Gộp lại = đúng lưới của paper.

> **Định cỡ chunk từ thực đo, đừng đoán:** chạy `K_SUBSET="2,3"` trước, xem cell KIỂM ĐẾM báo
> **giờ/1000 ô**, rồi mới quyết mỗi session sau ôm mấy giá trị k.
"""))

cells.append(md(r"""
## Cell 0 — ★ THAM SỐ STAGE (sửa Ô NÀY mỗi session)
"""))

cells.append(code(r"""
# =============================================================================
# K_SUBSET = cac gia tri k chay TRONG session nay. Phai la tap con cua k_list
#   trong configs/exp_main.yaml = [2, 3, 4, 5, 6, 8, 10].
#
#   Session 1 (calibrate):  "2,3"
#   Cac session sau: doc de xuat tu cell KIEM DEM roi dien tiep, VD "4,5" -> "6,8" -> "10".
#   Muon chay het trong 1 lenh (neu du 12h): "2,3,4,5,6,8,10".
# =============================================================================
K_SUBSET = "2,3"

# Bat cell RESTORE (Cell R) neu /kaggle/working da bi xoa va ban co .tgz session truoc
# (them no lam Add Input, dataset rieng cua ban). Mac dinh False.
RESTORE_FROM_TGZ = False

# NGAN SACH WALL-CLOCK cho Cell 6 (E2). Kaggle cat session o 12h; commit bi cat co the
# MAT output. Dat < 12h tru phan gates+splits+E1 (~0.5h) + dong goi (~vai phut): Cell 6
# tu DUNG EM khi het budget -> Cell 8 van dong goi -> run KET THUC THANH CONG -> Kaggle
# CHAC CHAN luu tgz. Session sau: Add Input tgz + RESTORE_FROM_TGZ=True + chay lai.
E2_WALL_BUDGET_H = 10.5

# SO TIEN TRINH SONG SONG (chia viec theo BENH NHAN). 0 = dung het core Kaggle cap.
# BIT-EXACT voi tuan tu: moi o goi set_all_seeds(seed) rieng nen ket qua KHONG phu thuoc
# thu tu chay; Pool.imap giu nguyen thu tu benh nhan => raw.csv giong het ban --workers 1
# (da verify parity tren exp_smoke: raw/summary/mask_identity giong het, tru runtime_s).
# Dat 1 neu muon quay ve duong chay tuan tu nguyen ban.
E2_WORKERS = 0

import os as _os
print('CPU Kaggle cap:', _os.cpu_count(), '-> workers =', E2_WORKERS or _os.cpu_count())
print('Stage nay chay k =', K_SUBSET)
print('RESTORE_FROM_TGZ =', RESTORE_FROM_TGZ)
print('E2_WALL_BUDGET_H =', E2_WALL_BUDGET_H, 'gio (Cell 6 tu dung em truoc moc 12h cua Kaggle)')
"""))

cells.append(md(r"""
## Cell 1 — lấy code + guard đồng bộ repo

> 🔴 **Không `!git clone` trần.** `/kaggle/working` sống sót qua các lần chạy tương tác; clone trần
> vào thư mục đã tồn tại ⇒ `fatal: destination path already exists`, clone **không làm gì**, và
> `rev-parse` vẫn in hash **cũ** — trông y hệt thành công. `check=True` + `raise` làm nó chết to tiếng.
"""))

cells.append(code(r'''
# Batch-safe: MOI loi -> raise -> Kaggle danh dau run FAILED (khong troi qua am tham).
import subprocess, sys, os, pathlib

REPO, DIR = 'https://github.com/HoangLong08/Paper-DAU.git', '/kaggle/working/qigoa'

if pathlib.Path(DIR, '.git').is_dir():
    subprocess.run(['git', '-C', DIR, 'fetch', 'origin', 'main'], check=True)
    subprocess.run(['git', '-C', DIR, 'reset', '--hard', 'origin/main'], check=True)
else:
    subprocess.run(['git', 'clone', REPO, DIR], check=True)

COMMIT = subprocess.run(['git', '-C', DIR, 'rev-parse', 'HEAD'],
                        capture_output=True, text=True).stdout.strip()
print('git commit:', COMMIT, '<- vao dong provenance trong docs/RESULTS.md')

# E2 CAN dung run_main_grid + exp_main. Neu thieu -> repo chua dong bo (origin/main cu).
NEEDED = ('scripts/make_splits.py', 'scripts/run_exact_check.py', 'scripts/run_main_grid.py',
          'configs/exp_main.yaml')
missing = [f for f in NEEDED if not pathlib.Path(DIR, f).exists()]
if missing:
    raise RuntimeError(f'THIEU FILE: {missing} -> repo chua dong bo. DUNG, dung chay tiep.')

# Guard: exp_main phai co ho tro --k-subset (neu origin/main la commit cu thi khong co).
if '--k-subset' not in pathlib.Path(DIR, 'scripts/run_main_grid.py').read_text(encoding='utf-8'):
    raise RuntimeError('run_main_grid.py tren origin/main CHUA co --k-subset -> push commit moi '
                       'len GitHub truoc. DUNG.')

os.chdir(DIR)
print('cwd =', os.getcwd())


def sh(args, fail_msg=''):
    """Thay cho `!python ...`: magic `!` nuot exit code -> cong cung FAIL van troi qua trong
    batch run. sh() bien moi that bai thanh exception -> abort ca run."""
    args = [str(a) for a in args]
    print('\n$ ' + ' '.join(args), flush=True)
    rc = subprocess.run(args, cwd=DIR).returncode
    if rc != 0:
        raise RuntimeError('[FAIL rc=%d] %s\n%s' % (rc, ' '.join(args), fail_msg))
    return rc


def sh_budget(args, budget_s, fail_msg=''):
    """Nhu sh() nhung co NGAN SACH thoi gian (giay). Het budget -> DUNG EM (khong raise)
    de Cell 8 con dong goi va run KET THUC THANH CONG (Kaggle luu output).

    An toan vi run_main_grid checkpoint (flush) sau MOI o -> kill giua chung chi mat o
    dang chay do, --resume session sau bo qua o da co. rc != 0 (loi that) VAN raise.
    """
    import time as _t
    args = [str(a) for a in args]
    print('\n$ (budget %.1fh) ' % (budget_s / 3600) + ' '.join(args), flush=True)
    try:
        rc = subprocess.run(args, cwd=DIR, timeout=budget_s).returncode
    except subprocess.TimeoutExpired:
        print('\n[BUDGET] Het %.1fh -> DUNG EM stage nay (da checkpoint tung o).' % (budget_s / 3600),
              flush=True)
        print('[BUDGET] K_SUBSET=%s CHUA xong. Session sau: Add Input tgz (Cell 8) + '
              'RESTORE_FROM_TGZ=True + chay lai.' % K_SUBSET, flush=True)
        return 'TIMEOUT'
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

Kaggle mount dataset dưới thư mục tên `datasets` (không phải slug) ⇒ cell **tự tìm**
`MICCAI_BraTS2020_TrainingData` ở bất kỳ đâu dưới `/kaggle/input` rồi **symlink** vào
`data.root_local` — script tìm thấy mà **config không bị sửa một dòng** (CLAUDE.md §5.1).
"""))

cells.append(code(r"""
import itertools

inp = pathlib.Path('/kaggle/input')
if not inp.is_dir():
    raise RuntimeError('KHONG CO /kaggle/input -> notebook nay chay ngoai Kaggle?')

print('Top-level /kaggle/input:', sorted(p.name for p in inp.iterdir()) or '(RONG)')

DEFAULT = pathlib.Path('/kaggle/input/brats20-dataset-training-validation/'
                       'BraTS2020_TrainingData/MICCAI_BraTS2020_TrainingData')
if DEFAULT.is_dir():
    REAL = DEFAULT
else:
    hits = [p for p in inp.rglob('MICCAI_BraTS2020_TrainingData') if p.is_dir()]
    REAL = hits[0] if hits else None

if REAL is None:
    raise RuntimeError(
        'KHONG TIM THAY MICCAI_BraTS2020_TrainingData duoi /kaggle/input.\n'
        'Top-level: ' + (', '.join(sorted(p.name for p in inp.iterdir())) or '(RONG)') + '\n'
        '=> Add Input awsaf49/brats20-dataset-training-validation chua thanh cong.\n'
        'LUU Y: Kaggle chi luu Add Input khi ban bam Save Version.')

n_cases = sum(1 for p in REAL.iterdir() if p.is_dir())
print('\nTim thay BraTS tai:', REAL, '| so thu muc ca:', n_cases)
if n_cases != 369:
    print('[CANH BAO] n =', n_cases, '!= 369 -> kiem tra version dataset TRUOC khi tin so nao.')

if REAL != DEFAULT:
    link = pathlib.Path(DIR, 'data/brats20/MICCAI_BraTS2020_TrainingData')
    link.parent.mkdir(parents=True, exist_ok=True)
    if not (link.is_symlink() or link.exists()):
        link.symlink_to(REAL, target_is_directory=True)
        print('Da symlink root_local:', link, '->', REAL)
    else:
        print('Link da ton tai:', link)
    print('=> _common.data_root() se tim thay qua data.root_local (config KHONG bi sua).')
"""))

cells.append(md(r"""
## Cell R — ♻️ RESTORE (tuỳ chọn) — nạp lại `results/` từ `.tgz` session trước

Chỉ chạy khi `RESTORE_FROM_TGZ = True` (Cell 0). Dùng khi `/kaggle/working` bị xoá giữa hai
session: thêm `.tgz` bạn đã tải về ở session trước làm **Add Input** (một dataset riêng của bạn),
cell này giải nén nó vào repo ⇒ `--resume` tiếp đúng chỗ dừng, **không mất giờ đã chạy**.

> Không có tgz mà bật cờ này ⇒ cell **raise** (tránh âm thầm chạy lại từ 0). Không cần restore ⇒
> để `RESTORE_FROM_TGZ = False`, cell tự bỏ qua.
"""))

cells.append(code(r"""
import glob, tarfile

if not RESTORE_FROM_TGZ:
    print('RESTORE_FROM_TGZ = False -> bo qua (working dir hien tai da co results/, hoac la session dau).')
else:
    cands = sorted(glob.glob('/kaggle/input/**/results_*.tgz', recursive=True)) + \
            sorted(glob.glob('/kaggle/input/**/*.tgz', recursive=True))
    cands = list(dict.fromkeys(cands))
    if not cands:
        raise RuntimeError('RESTORE_FROM_TGZ=True nhung KHONG thay .tgz nao duoi /kaggle/input.\n'
                           '=> Add Input dataset chua .tgz session truoc, hoac dat lai co = False.')
    src = cands[-1]
    print('Restore tu:', src)
    with tarfile.open(src, 'r:gz') as t:
        t.extractall(DIR)   # tgz goi tu repo root: results/... + data/splits/...
    n_raw = sum(1 for _ in open(pathlib.Path(DIR, 'results/main/raw.csv'))) \
        if pathlib.Path(DIR, 'results/main/raw.csv').exists() else 0
    print('Da giai nen. results/main/raw.csv:', n_raw, 'dong (ke ca banner).')
"""))

cells.append(md(r"""
## Cell 3 — ★ CỔNG CỨNG 1: unit test (~1 phút, luôn chạy)

| Fail | Nghĩa là |
|---|---|
| `test_exact_dp` | Mọi kết luận P2 dựng trên DP ⇒ **DỪNG TOÀN BỘ** |
| `test_nfe_budget` | **Lưới vô hiệu** — đúng lỗi đã giết lô cũ (thừa 13,4% NFE) |
| `test_degeneracy` | Cơ chế suy biến không đúng như phát biểu ⇒ đọc lại prereg §6/A1 |
"""))

cells.append(code(r"""
sh([sys.executable, '-m', 'pytest', 'tests/test_exact_dp.py', 'tests/test_nfe_budget.py',
    'tests/test_degeneracy.py', '-q'],
   'CONG CUNG 1 FAIL -> DUNG TOAN BO. Khong chay E2.')
print('\n3 CONG CUNG PASS.')
"""))

cells.append(md(r"""
## Cell 4 — E0: cohort + split cấp BỆNH NHÂN (idempotent)

`run_main_grid` iterate theo `data/splits/brats_cohort.csv`. Cell này sinh cohort + `fold_{0..4}.json`
(chia cấp bệnh nhân, phân tầng grade × tertile thể tích WT — A3). `--resume` ⇒ bỏ qua nếu đã có.
"""))

cells.append(code(r"""
sh([sys.executable, 'scripts/make_splits.py', '--config', 'configs/exp_main.yaml', '--resume'],
   'E0 FAIL -> DUNG. Neu loi "Khong thay du lieu BraTS" -> xem guard dataset o Cell 2.')

cohort = pathlib.Path('data/splits/brats_cohort.csv')
if not cohort.exists():
    raise RuntimeError('E0 rc=0 nhung khong sinh brats_cohort.csv -> run_main_grid khong iterate duoc. DUNG.')
n_cohort = sum(1 for _ in open(cohort)) - 1   # tru header
print('\nE0 OK: cohort =', n_cohort, 'ca (nguon chuan cho moi script iterate).')
"""))

cells.append(md(r"""
## Cell 5 — ★ CỔNG CỨNG 2: E1 bit-exact trên dữ liệu THẬT → **BẢNG II** (skip nếu đã có)

E2 **KHÔNG được chạy trước khi E1 PASS** (scripts/README §A10). DP phải khớp vét cạn tại k=2,3:
`|f_DP − f_brute| ≤ 1e-9` **VÀ** mask cảm sinh giống hệt (A5a). Nếu `results/exact/dp_vs_bruteforce.csv`
đã tồn tại (từ lô quyết định / session E2 trước) ⇒ **skip** để dành giờ cho lưới.

> 🔴 **FAIL ⇒ DỪNG TOÀN BỘ.** Debug ĐẦU TIÊN = audit quy ước histogram (`0log0` · lớp rỗng ·
> ngưỡng trùng · nền cường-độ-0 — A5b/A5c), **KHÔNG** phải sửa DP.
"""))

cells.append(code(r"""
e1_out = pathlib.Path('results/exact/dp_vs_bruteforce.csv')
if e1_out.exists():
    print('E1 da co ->', e1_out, '(skip). Cong cung E1 coi nhu PASS tu lo truoc.')
    print('   Muon chay lai E1 tuoi: xoa file tren roi re-run cell nay.')
else:
    sh([sys.executable, 'scripts/run_exact_check.py', '--config', 'configs/exp_main.yaml'],
       'E1 FAIL -> DUNG TOAN BO. Debug DAU TIEN = audit QUY UOC HISTOGRAM (A5b/A5c), KHONG sua DP.')
    if not e1_out.exists():
        raise RuntimeError('E1 rc=0 nhung khong co ' + str(e1_out) + ' -> khong co Bang II. DUNG.')
    print('\nE1 PASS ->', e1_out, '= BANG II.')
"""))

cells.append(md(r"""
## Cell 6 — ★ E2: LƯỚI CHÍNH (stage theo `K_SUBSET`, có ngân sách wall-clock) → Bảng III · Hình 2 · Hình 3

`run_main_grid.py --config exp_main.yaml --k-subset $K_SUBSET --resume`, bọc trong **ngân sách
`E2_WALL_BUDGET_H` giờ** (Cell 0). Checkpoint sau **mỗi ô** ⇒ hết giờ vẫn tiếp được.

> 🟢 **Vì sao có ngân sách:** một k-stage ở n=369 (~20h) **vượt** mốc 12h/session của Kaggle. Nếu để
> Kaggle **kill** ở 12h, commit có thể **mất output**. Thay vào đó Cell 6 **tự dừng êm** ở
> `E2_WALL_BUDGET_H` (<12h): `run_main_grid` bị dừng giữa chừng nhưng đã **flush từng ô**, rồi Cell 8
> vẫn đóng gói ⇒ run **kết thúc THÀNH CÔNG** ⇒ Kaggle **chắc chắn lưu** `.tgz`. Session sau nạp lại
> (`RESTORE_FROM_TGZ=True`) + `--resume` tiếp đúng chỗ dừng.

> ⛔ Số ra từ đây **là số của paper** (không phải screening). `summary.csv` + `mask_identity.csv` được
> script sinh lại từ toàn bộ `raw.csv` đã tích luỹ — **khi một stage chạy tới cùng** (không bị cắt).
"""))

cells.append(code(r"""
import time
_t0 = time.perf_counter()
_rc = sh_budget([sys.executable, 'scripts/run_main_grid.py', '--config', 'configs/exp_main.yaml',
                 '--k-subset', K_SUBSET, '--resume', '--workers', str(E2_WORKERS)],
                int(E2_WALL_BUDGET_H * 3600),
                'E2 stage FAIL (loi THAT, khong phai timeout). --resume an toan: chay lai se tiep tu '
                'o da checkpoint.')
_dt = (time.perf_counter() - _t0) / 60
if _rc == 'TIMEOUT':
    print('\n[E2] stage k=%s CHUA XONG (het budget %.1fh) sau %.1f phut. Session sau: RESTORE + chay lai.'
          % (K_SUBSET, E2_WALL_BUDGET_H, _dt))
else:
    print('\n[E2] stage k=%s XONG TRON (rc=0) trong %.1f phut (session nay).' % (K_SUBSET, _dt))
print('     Ket qua tich luy: results/main/{raw,summary,mask_identity}.csv')
"""))

cells.append(md(r"""
## Cell 7 — 📊 KIỂM ĐẾM tiến độ + đề xuất `K_SUBSET` kế tiếp

Đọc `results/main/raw.csv` (đã tích luỹ qua mọi session), tính **% ô đã chạy cho từng k** so với
lưới đã preregister trong `exp_main.yaml`, và in **tập con còn thiếu** để điền vào Cell 0 session sau.

> Đây là số kiểm-đếm để điều phối, **không phải kết quả**. Kết quả nằm ở `summary.csv`.
"""))

cells.append(code(r"""
import yaml, pandas as pd
from itertools import product

cfg = yaml.safe_load(open('configs/exp_main.yaml', encoding='utf-8'))
m = cfg   # exp_main la config phang (khong long trong khoa 'main')
targets = list(m['targets']); bgs = [str(b).lower() for b in m['include_zero_bg']]
k_all = [int(k) for k in m['k_list']]; seeds = [int(s) for s in m['seeds']]
algos = list(m['optimizers'])
# So o metaheuristic mong doi cho MOI k: patient x target x bg x algo x seed.
# Dem theo cohort THAT tren dia (co the 368, khong phai 369 — 1 ca thieu modality).
n_pat = sum(1 for _ in open('data/splits/brats_cohort.csv')) - 1
per_k_expect = n_pat * len(targets) * len(bgs) * len(algos) * len(seeds)

raw = pathlib.Path('results/main/raw.csv')
if not raw.exists():
    print('Chua co results/main/raw.csv -> chua chay E2 stage nao.')
else:
    from importlib import import_module
    sys.path.insert(0, str(pathlib.Path(DIR, 'scripts')))
    df = import_module('_common').read_results_csv(raw)   # bo qua banner '#'
    meta = df[df['method'].isin(algos)].copy()
    meta['k'] = pd.to_numeric(meta['k'], errors='coerce')
    # dem O DUY NHAT (patient,target,bg,method,seed) — bo trung do 4 decode-rule nhan dong.
    key = ['patient_id', 'target', 'include_zero_bg', 'method', 'seed']
    print('n_patients (cohort tren dia):', n_pat, '| o metaheuristic mong doi / k:', per_k_expect)
    print('%-5s %10s %8s   %s' % ('k', 'da_chay', '%', 'trang thai'))
    remaining = []
    for k in k_all:
        got = meta[meta['k'] == k].drop_duplicates(key).shape[0]
        pct = 100.0 * got / per_k_expect if per_k_expect else 0.0
        status = 'XONG' if got >= per_k_expect else ('mot phan' if got else 'CHUA')
        if got < per_k_expect:
            remaining.append(k)
        print('%-5d %10d %7.1f%%   %s' % (k, got, pct, status))
    # thoi gian/1000 o de dinh co chunk
    print('\nDe xuat K_SUBSET ke tiep:', (','.join(map(str, remaining)) if remaining else '(HET — E2 DA DAY DU LUOI)'))
    if not remaining:
        print('=> Moi k da 100%. E2 hoan tat. Chay run_stats + build_tables/figures o buoc sau.')
"""))

cells.append(md(r"""
## Cell 8 — đóng gói + in `run-manifest.json`

`/kaggle/working` **có thể mất khi session hết hạn** ⇒ tải `.tgz` từ tab **Output** mỗi session.
**Không có manifest = run không tồn tại với paper** (CLAUDE.md §5.2).
"""))

cells.append(code(r"""
import time, json, tarfile, glob

stamp = time.strftime('%Y%m%d_%H%M')
tgz = '/kaggle/working/results_%s.tgz' % stamp
with tarfile.open(tgz, 'w:gz') as t:
    for d in ('results', 'data/splits'):
        if pathlib.Path(d).is_dir():
            t.add(d)
print('Da dong goi:', tgz, '-> tai ve tu tab Output.')
print('(Session sau: neu working dir bi xoa, Add Input file nay + dat RESTORE_FROM_TGZ=True.)')

for mf in sorted(glob.glob('results/main/run-manifest.json')):
    print('\n' + '=' * 70 + '\n' + mf + '\n' + '=' * 70)
    print(json.dumps(json.load(open(mf)), indent=2, ensure_ascii=False))

print('\n' + '=' * 70)
print('git commit cua stage nay:', COMMIT)
print('Mau dong provenance cho docs/RESULTS.md (ghi khi E2 DAY DU LUOI, KHONG phai tung stage):')
print('  Bang III <- results/main/summary.csv <- scripts/run_main_grid.py '
      '--config configs/exp_main.yaml @commit ' + COMMIT + ', seeds {0..4}')
print('  (A0) mask-identity <- results/main/mask_identity.csv <- (nt)')
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

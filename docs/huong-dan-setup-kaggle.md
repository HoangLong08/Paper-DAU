# Hướng dẫn chạy Kaggle — QIGOA Reality-Check

**Ngày:** 16/07/2026 · **Dành cho:** tác giả (Nguyễn Võ Hoàng Long) · **Repo:** [github.com/HoangLong08/Paper-DAU](https://github.com/HoangLong08/Paper-DAU)

> ### 👉 Khuyến nghị: chạy ĐÚNG MỘT lô — **LÔ QUYẾT ĐỊNH**
>
> **Một session Kaggle · CPU · ~3–5 giờ · KHÔNG bật GPU · 7 lệnh copy-paste.**
>
> Lô này trả về:
> - **Bảng II** — kết quả THẬT đầu tiên đi thẳng vào bản thảo (DP khớp vét cạn trên BraTS).
> - **Câu trả lời cho 3/4 câu hỏi có thể GIẾT BÀI** — trước khi anh chi 20 giờ cho lưới chính.
>
> **Đừng chạy gì khác cho tới khi lô này xong.** Mọi thứ còn lại (E2 lưới chính 20h, E3, E4 U-Net/GPU, E7 ngoại kiểm) nằm ở [Phụ lục B](#phụ-lục-b--những-gì-KHÔNG-nằm-trong-lô-này) và **chỉ mở khi lô này pass**.
>
> **Vì sao chỉ một lô này (prereg §6/A10):** kế hoạch cũ chi ~35/40 giờ cho các thí nghiệm có **xác suất bất ngờ ≈ 0** (E2 chỉ fail nếu code có bug; "U-Net thắng thresholding" đã biết từ 2015), rồi mới kiểm 4 câu hỏi thật sự bất định. Đó là **dấu vân tay của confirmation bias — trong một bài đi tố cáo người khác confirmation bias.** Lô này đảo ngược: **~4 giờ để biết bài có sống không.** Một trong các cổng chết ⇒ reframe ngay, tiết kiệm 8 tuần.

---

## Bước 0 — Tài khoản Kaggle

1. Tạo tài khoản tại [kaggle.com](https://www.kaggle.com).
2. **Verify số điện thoại** (Settings → Phone Verification). Bắt buộc — không verify thì Kaggle **khoá Internet** trong Notebook, mà ta cần Internet để `git clone`.
3. **Create → New Notebook** → panel phải (⚙️ Settings):
   - **Internet: ON**
   - **Accelerator: None** ← **toàn bộ lô này chạy CPU. Đừng bật GPU** (quota 30 GPU-h/tuần để dành cho U-Net sau này).

> **Quota:** session ≤ **12 giờ** · `/kaggle/input/` **read-only** · `/kaggle/working/` ghi được nhưng **mất khi hết session** ⇒ phải tải `results/` về (Bước 4).

---

## Bước 1 — Add data (chỉ MỘT dataset)

Panel phải → **Add Input** → tìm và thêm:

| Dataset (slug) | Mount tại |
|---|---|
| `awsaf49/brats20-dataset-training-validation` | `/kaggle/input/brats20-dataset-training-validation/` |

> Dataset LGG (`mateuszbuda/lgg-mri-segmentation`) **chưa cần** — nó cho E7, nằm ngoài lô này, và **có thể không phải ngoại kiểm thật** ([Phụ lục A](#phụ-lục-a--cảnh-báo-liêm-chính-a8)).
>
> ⚠️ Kaggle chỉ có **training split** của BraTS (phần có ground truth). Test set thật giữ kín trên Synapse ⇒ **KHÔNG** claim "SOTA trên BraTS leaderboard" ở bất kỳ đâu.

---

## Bước 2 — LÔ QUYẾT ĐỊNH: 7 lệnh, chạy theo đúng thứ tự

> Mỗi lệnh là một cell. **Cell nào FAIL thì DỪNG** — đọc cột "nếu fail" rồi mới đi tiếp.

### Cell 1 — lấy code + cài package thiếu (~2 phút)

```python
import subprocess, pathlib
REPO, DIR = 'https://github.com/HoangLong08/Paper-DAU.git', '/kaggle/working/qigoa'

if pathlib.Path(DIR, '.git').is_dir():          # đã có từ session trước → ĐỒNG BỘ, không clone
    subprocess.run(['git', '-C', DIR, 'fetch', 'origin', 'main'], check=True)
    subprocess.run(['git', '-C', DIR, 'reset', '--hard', 'origin/main'], check=True)
else:
    subprocess.run(['git', 'clone', REPO, DIR], check=True)

COMMIT = subprocess.run(['git', '-C', DIR, 'rev-parse', 'HEAD'],
                        capture_output=True, text=True).stdout.strip()
print('git commit:', COMMIT, '← GHI LẠI hash này, nó vào dòng provenance')

missing = [f for f in ('scripts/make_splits.py', 'configs/exp_main.yaml',
                       'configs/exp_week1.yaml') if not pathlib.Path(DIR, f).exists()]
assert not missing, f'THIẾU FILE: {missing} — repo chưa đồng bộ. DỪNG, đừng chạy tiếp.'
```

```bash
%cd /kaggle/working/qigoa
!pip install -q medpy tifffile
```

> 🔴 **Vì sao không phải `!git clone` trần.** `/kaggle/working/` **sống sót qua các session** (nó là Output của notebook). Re-run một `git clone` trần vào thư mục đã tồn tại ⇒ `fatal: destination path already exists`, clone **không làm gì**, và `rev-parse` ngay sau đó vẫn vui vẻ in ra hash **cũ** — trông y hệt thành công. Anh sẽ chạy cả một stage trên code cũ mà không biết. `check=True` + `assert` ở trên làm cell **chết to tiếng** thay vì trôi qua. (Đã cắn một lần thật: 17/07/2026.)

Kaggle đã có sẵn numpy/scipy/scikit-image/scikit-learn/pandas/nibabel/PyYAML/matplotlib/torch/tqdm ⇒ **đừng** `pip install -r requirements.txt` (làm hỏng môi trường đã pin của Kaggle). Nếu `medpy` lỗi build: `!pip install -q git+https://github.com/deepmind/surface-distance.git`.

### Cell 2 — ★ CỔNG CỨNG 1: unit test (~1 phút)

```bash
!python -m pytest tests/test_exact_dp.py tests/test_nfe_budget.py tests/test_degeneracy.py -q
```

| Fail | Nghĩa là |
|---|---|
| `test_exact_dp` | Mọi kết luận P2 dựng trên DP ⇒ **DỪNG TOÀN BỘ**. |
| `test_nfe_budget` | **Lưới vô hiệu** — đây đúng là lỗi đã giết lô cũ (thừa 13,4% NFE). |
| `test_degeneracy` | Cơ chế suy biến không đúng như phát biểu ⇒ đọc lại prereg §6/A1. |

### Cell 3 — E0: cohort + split cấp bệnh nhân (~10–30 phút, ước tính)

```bash
!python scripts/make_splits.py --config configs/exp_main.yaml
```

Sinh `data/splits/brats_cohort.csv` + `fold_{0..4}.json`, chia ở **cấp BỆNH NHÂN**, phân tầng grade × tertile thể tích WT (A3).

> 🔴 **Không bỏ qua cell này.** `run_ceiling.py` không thấy `fold_*.json` sẽ **âm thầm rơi về chia vòng tròn** kèm một dòng `[WARN]` dễ trôi qua mắt — và Cell 5 (P5) sẽ đánh giá **đóng góp dương của bài** trên một split không phân tầng. Đó đúng là thứ kỷ luật mà bài này đi tố cáo người khác vi phạm.

### Cell 4 — ★ CỔNG CỨNG 2: E1 bit-exact trên dữ liệu THẬT (~10–20 phút) → **BẢNG II**

```bash
!python scripts/run_exact_check.py --config configs/exp_main.yaml
```

DP phải khớp vét cạn tại k=2,3: `|f_DP − f_brute| ≤ 1e-9` **VÀ** mask cảm sinh giống hệt (A5a). Cho ra `results/exact/dp_vs_bruteforce.csv` → **Bảng II của bản thảo — con số thật đầu tiên**.

> 🔴 **FAIL ⇒ DỪNG TOÀN BỘ.** Bước debug **ĐẦU TIÊN** là **audit quy ước histogram** (`0log0` · lớp rỗng · ngưỡng trùng · **có tính nền cường-độ-0 hay không** — A5b/A5c), **KHÔNG** phải sửa DP. Xác suất lỗi nằm ở quy ước cao hơn nhiều so với ở DP.

### Cell 5 — RỦI RO #2: P5 nested CV (~1 giờ) → *bài có đóng góp dương không?*

```bash
!python scripts/run_ceiling.py --config configs/exp_ceiling.yaml --stage p5_nested_cv
```

Ngưỡng 1-tham-số (phân vị q) vs 7 metaheuristic, **nested CV cấp bệnh nhân**: `q*` fit trên outer-train, **đóng băng**, đánh giá out-of-fold.

- **Nếu P5 THẮNG** ⇒ đóng góp dương đứng vững.
- **Nếu P5 THUA** ⇒ **không phải bài chết**. Fallback đã khoá TRƯỚC khi thấy số (prereg A10 #2): đóng góp dương rơi về **ceiling decomposition + công cụ chẩn đoán + checklist**. Ghi kết quả âm vào `RESULTS.md` như mọi run khác.

### Cell 6 — RỦI RO #3 + #4: lưới sàng lọc (~1–2 giờ, ước tính)

```bash
!python scripts/run_main_grid.py --config configs/exp_week1.yaml --resume
!python scripts/run_stats.py     --config configs/exp_week1.yaml
```

`configs/exp_week1.yaml` = lưới **sàng lọc**: n=60 ca (thay vì 369), 3 seed (thay vì 5), 1 biến thể bg — nhưng **giữ trọn trục k và cả 4 decoding rule**, vì đó chính là hai câu hỏi:

| Rủi ro | Câu hỏi | Kết quả giết bài |
|---|---|---|
| **#3** | Spearman(k, Dice) tính RIÊNG cho **từng** decoding rule | Tương quan âm **chỉ** xuất hiện dưới rule `brightest` ⇒ headline *"metrics are anti-correlated"* **SAI**; bài co lại thành *"một decoding rule có bias theo k"* |
| **#4** | `morph` vs `oracle_interval` | `morph` **vượt** oracle ⇒ **P4 tự bác bỏ** |

> ⛔ **Số từ `exp_week1.yaml` KHÔNG vào Bảng III / Hình 2 / Hình 3.** Nó trả lời **dấu và hướng**, đủ để quyết định, **không đủ để công bố**. Bảng của paper đến từ `exp_main.yaml` (n=369, 5 seed, cả 2 bg — A8). Dòng provenance sinh từ đây **phải ghi chữ `screening`**. Kết quả **sát ngưỡng** ⇒ **không kết luận**, chạy lại trên `exp_main.yaml`.

### Cell 7 — đóng gói để tải về

```python
import time
stamp = time.strftime('%Y%m%d_%H%M')
!cd /kaggle/working/qigoa && tar czf /kaggle/working/results_{stamp}.tgz results/ data/splits/
print('Tải file này từ tab Output:', f'/kaggle/working/results_{stamp}.tgz')
```

---

### Rủi ro #1 — **Bảng I** (0 compute, KHÔNG chạy trên Kaggle)

Câu hỏi thứ tư *"P1 có mục tiêu, hay là strawman?"* **không có script** — và đó chính là lý do nó dễ bị hoãn vô hạn. Nó là **khảo sát tay**: search string + PRISMA-lite + **2 coder + Cohen's κ** (~1 tuần).

**Nó quyết định bài không kém gì 3 cell trên.** Nếu văn liệu **không** decode bằng "lớp sáng nhất" thì P1 đang đánh một strawman — và viết *"văn liệu decode bằng lớp sáng nhất [refs]"* = **xuyên tạc công trình được cite = vi phạm IRON RULE 2** (CLAUDE.md lằn ranh đỏ #4). Làm song song trong lúc Kaggle chạy.

---

## Bước 3 — Sau khi lô chạy xong: provenance + commit

1. Tải `.tgz` từ tab **Output** → giải nén vào repo local (ghi đè `results/` — kết quả là output do script sinh, **không sửa tay**).
2. **Thêm dòng provenance** vào `docs/RESULTS.md` (append-only), dùng `git_commit` từ Cell 1:
   ```
   Bảng II ← results/exact/dp_vs_bruteforce.csv ← scripts/run_exact_check.py --config configs/exp_main.yaml @commit <hash>
   [screening] Rủi ro #3/#4 ← results/week1/raw.csv ← scripts/run_main_grid.py --config configs/exp_week1.yaml @commit <hash>, seeds {0..2}
   ```
3. Kiểm tra **mỗi** thư mục output có `run-manifest.json` — **không manifest = run không tồn tại với paper** (CLAUDE.md §5.2).
4. Commit khi anh muốn: `git add -f results/ data/splits/ docs/RESULTS.md`.

> 🔴 **Không xoá run xấu** (prereg §5). **Run âm là dữ liệu** — ghi vào `RESULTS.md` như mọi run khác.

---

## Bước 4 — Việc của tác giả: timestamp preregistration (A9)

Làm **trước** khi chạy thật, để câu *"chúng tôi đã preregister"* **verify được bởi bên thứ ba** (git history rewrite được nên tự nó không đủ):

1. **OSF** ([osf.io](https://osf.io) → Registrations) **hoặc** archive `docs/preregistration.md` lên **Zenodo** ([zenodo.org](https://zenodo.org)) → lấy **DOI có timestamp**.
2. Điền **commit hash** của commit chứa `docs/preregistration.md` vào **dòng 4** của file đó.
3. **Cite DOI/OSF link trong Abstract.**
4. Gọi đúng tên nó trong bản thảo: ***"Confirmatory analysis protocol for exploratory findings"*** — vì P1/P3 được phát hiện exploratorily trên pipeline có lỗi. **Dán nhãn sai một preregistration còn tệ hơn không có.**

---

## Phụ lục A — Cảnh báo liêm chính (A8)

1. **Chỉ training split có ground truth** ⇒ KHÔNG claim "SOTA BraTS leaderboard".
2. **LGG có thể KHÔNG ngoại kiểm.** Buda et al. = 110 ca **TCGA-LGG**; BraTS 2020 đã nuốt **108 ca TCGA-LGG** từ đúng collection đó. **BẮT BUỘC** đối chiếu `name_mapping.csv` và **báo cáo số ca trùng bằng con số** trước khi dùng chữ *"external validation"*. Trùng mà vẫn gọi ngoại kiểm ⇒ reviewer BraTS đọc đó là **misrepresentation**. Thay thế mạnh nhất: ngoại kiểm theo **chiều TASK** (tune WT/FLAIR → test ET/T1ce).
3. **Bẫy kênh LGG:** ảnh Kaggle LGG là **TIFF 3 kênh**; FLAIR = **kênh giữa (index 1)**. Lấy nhầm kênh ⇒ histogram sai ⇒ toàn bộ Kapur/DP sai.

## Phụ lục B — Những gì KHÔNG nằm trong lô này

**Chỉ mở sau khi cả 4 rủi ro sống sót.** Chạy trước = đốt ~35 giờ cho thứ có xác suất bất ngờ ≈ 0.

| Bước | Lệnh | Compute | Accel |
|---|---|---|---|
| E1b — đúng-đắn implementation (A6) | tái tạo bảng Kapur/Otsu đã công bố trên Lena/Cameraman/Baboon/Peppers ở đúng NFE đã công bố | ~1h | CPU |
| **E2 — lưới chính** | `run_main_grid.py --config configs/exp_main.yaml --k-subset 2,3,4` rồi `--k-subset 5,6,8,10` | ~20h | CPU |
| E3 — ablation | `run_ablation.py --config configs/exp_ablation.yaml --resume` | ~6h | CPU |
| E4 — ceiling | `run_ceiling.py --config configs/exp_ceiling.yaml --resume` | ~2h | CPU |
| E4 — U-Net | `run_unet.py --config configs/exp_unet.yaml --resume` | ~2h | **GPU T4** ← bước GPU DUY NHẤT |
| E6 — thống kê | `run_stats.py --config configs/exp_main.yaml` | phút | CPU |
| E7 — ngoại kiểm LGG | `run_external.py --config configs/exp_external.yaml` | ~8h | CPU — **đọc Phụ lục A trước** |
| Build bảng/hình | `build_tables.py` · `build_figures.py` | phút | CPU |

**E1b là cổng cứng, không phải tuỳ chọn:** chưa qua E1b thì **cấm dùng hit-rate-to-DP làm kết quả** — nếu không, dán nhãn "GOA hỏng" chỉ vì nó không đạt tối ưu chính là **vòng tròn logic** (đó *là* P2).

**Session ≤ 12h ⇒ E2 (~20h) phải chia stage:** chia theo `k` qua nhiều session, `--resume` bỏ qua ô đã tính, checkpoint sau mỗi `(image, k, algo, seed)`, cache histogram `.npy` dùng chung (`results/main/cache`). Cuối mỗi session: tải `results/` về + thêm dòng provenance.

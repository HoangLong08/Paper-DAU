# Hướng dẫn setup Kaggle — QIGOA Reality-Check

**Ngày:** 16/07/2026 · **Dành cho:** tác giả (Nguyễn Võ Hoàng Long) · **Môi trường chạy thí nghiệm:** Kaggle Notebook (CPU + GPU miễn phí)

> **File này trả lời đúng một câu:** *từ một tài khoản Kaggle trống tới khi có `results/` đầy đủ trong tay — làm theo thứ tự nào, gõ lệnh gì, và ở bước nào thì DỪNG.*
>
> **Quy tắc bao trùm (CLAUDE.md §2, §5):** Kaggle là **môi trường chạy**, không phải môi trường phát triển. Mọi code đã smoke-test ở local trước. Mỗi con số phải truy được về `configs/ → scripts/ → results/`. Số synthetic **không bao giờ** là kết quả.
>
> ⚠️ **Đọc trước khi làm gì:** thứ tự chạy ở **Bước 3** là bắt buộc theo preregistration §6/A10. **CẤM chạy E2 (lưới chính) trước** khi cổng bit-exact (E1) pass và cả 4 thí nghiệm rủi ro Tuần-1 còn sống. Chi được ~35h compute cho thứ có xác suất bất ngờ ≈ 0 rồi mới kiểm 4 câu hỏi thật sự bất định = confirmation bias — trong một bài đi tố cáo người khác confirmation bias.

---

## Bước 0 — Tài khoản Kaggle + mở khoá GPU/Internet

1. Tạo tài khoản tại [kaggle.com](https://www.kaggle.com) (miễn phí).
2. **Verify số điện thoại** (Settings → Phone Verification). **Bắt buộc** — nếu không verify, Kaggle **khoá GPU và khoá Internet** trong Notebook, và ta cần cả hai (GPU cho U-Net, Internet để `git clone` + `pip install`).
3. Tạo một Notebook mới: **Create → New Notebook**.
4. Mở panel bên phải (**Settings / ⚙️ hoặc menu ⋮ → Settings**), bật:
   - **Internet: ON** (để clone repo + pip install).
   - **Accelerator: GPU T4 x2** *chỉ khi chạy `run_unet.py`*. **Mọi thí nghiệm khác chạy CPU** — để **Accelerator: None** cho chúng nhằm **tiết kiệm quota GPU** (chỉ 30 GPU-h/tuần).
   - **Persistence: Variables and Files** (nếu có) — giúp giữ `/kaggle/working/` giữa các lần bấm Save, nhưng **đừng tin tuyệt đối**: luôn tải `results/` về (Bước 5).

> 💡 **Quota cần nhớ:** session ≤ **12 giờ** · GPU ≤ **30 giờ/tuần** · CPU ~ không giới hạn thực tế nhưng vẫn theo session 12h. `/kaggle/input/` **read-only**; `/kaggle/working/` ghi được nhưng **mất khi session hết hạn** nếu không lưu.

---

## Bước 1 — Add data (2 dataset)

Trong Notebook, panel phải → **Add Input / Add Data**, tìm và thêm:

| Dataset (slug) | Vai trò | Mount tại |
|---|---|---|
| `awsaf49/brats20-dataset-training-validation` | **CHÍNH** — BraTS 2020, dùng cho E1–E6 | `/kaggle/input/brats20-dataset-training-validation/` |
| `mateuszbuda/lgg-mri-segmentation` | **E7** — ngoại kiểm LGG (⚠️ đọc cảnh báo A8 cuối file) | `/kaggle/input/lgg-mri-segmentation/` |

**Giải thích cấu trúc thư mục Kaggle:**

```
/kaggle/input/    ← READ-ONLY. Dataset mount vào đây. Không ghi được, không xoá được.
/kaggle/working/  ← GHI ĐƯỢC (thư mục làm việc). results/ sẽ nằm ở đây.
                    ⚠️ Mất khi session hết hạn — PHẢI tải về (Bước 5) trước khi đóng.
/kaggle/temp/     ← scratch tạm, cũng mất.
```

> ⚠️ Kaggle chỉ có **training split** của BraTS (có ground truth). Test set thật giữ kín trên Synapse. ⇒ **KHÔNG** claim "SOTA trên BraTS leaderboard" ở bất kỳ đâu. Ta tự chia theo bệnh nhân (`data/splits/fold_{0..4}.json`, đã commit vào repo).

---

## Bước 2 — Đưa code lên Kaggle

**Cách A (khuyến nghị) — clone GitHub repo.** Cần Internet ON (Bước 0). Trong cell đầu:

```bash
!git clone https://github.com/HoangLong08/<TEN_REPO>.git /kaggle/working/qigoa
%cd /kaggle/working/qigoa
!git rev-parse HEAD    # ghi lại commit hash — nó vào run-manifest.json
```

**Cách B — upload repo làm "Utility dataset".** Nếu chưa muốn public repo: nén repo (`git archive` hoặc zip thư mục, **loại `__pycache__/`, `.git/`**), lên **Datasets → New Dataset → Upload**, rồi Add Input như Bước 1. Code sẽ nằm ở `/kaggle/input/<slug>/` (read-only) — copy sang `/kaggle/working/` để chạy:

```bash
!cp -r /kaggle/input/<slug-code>/qigoa /kaggle/working/qigoa
%cd /kaggle/working/qigoa
```

**Cài các package Kaggle còn thiếu** (thường chỉ `medpy` + `tifffile`):

```bash
!pip install -q medpy tifffile
# Nếu medpy lỗi build trên Kaggle, dùng surface-distance của Google thay thế:
# !pip install -q git+https://github.com/deepmind/surface-distance.git
```

> Phần lớn `requirements.txt` (numpy, scipy, scikit-image, scikit-learn, pandas, nibabel, PyYAML, matplotlib, torch, tqdm) **đã có sẵn** trên image Kaggle. Không cần `pip install -r requirements.txt` toàn bộ — chỉ cài phần thiếu để khỏi làm hỏng môi trường đã pin của Kaggle.

---

## Bước 3 — THỨ TỰ CHẠY (bắt buộc — preregistration §6/A10)

> 🔴 **CẤM chạy E2 (lưới chính, `run_main_grid.py`) trước.** Thứ tự dưới đây được thiết kế để **giết bài sớm nếu nó phải chết**, tiết kiệm 8 tuần. Chỉ tiến sang bước sau khi bước trước **pass cổng**.

| # | Bước | Compute | Accel | Cổng — nếu KHÔNG qua thì sao |
|---|---|---|---|---|
| 0 | **Cổng Tuần-0** — đọc 6 near-rival + viết đoạn định vị | 0 | — | ✅ **ĐÃ XONG** → [docs/related-work-positioning.md](related-work-positioning.md) |
| 0b | **A9** — OSF/Zenodo DOI + điền commit hash vào prereg dòng 4 | 0 | — | **Việc của tác giả.** Chưa làm ⇒ câu "chúng tôi đã preregister" **không verify được** (Bước 6) |
| 1 | **Smoke test local** (synthetic, `exp_smoke.yaml`) | < 60s | CPU (máy nhà) | Fail ⇒ sửa ở local. Số = `[PLACEHOLDER]` |
| 2 | **E1 — cổng bit-exact** (DP vs vét cạn, k=2,3) | < 30ph | CPU | 🔴 **FAIL ⇒ DỪNG TOÀN BỘ.** Mọi kết luận P2 dựng trên DP. Debug đầu tiên = **audit quy ước histogram** (A5c), KHÔNG phải debug DP |
| 3 | **E1b — đúng-đắn implementation** (tái tạo bảng đã công bố, A6) | ~1h | CPU | Chưa qua ⇒ **cấm dùng hit-rate-to-DP làm kết quả** (nếu không thì "GOA hỏng" = vòng tròn logic) |
| 4 | **TUẦN 1 — 4 thí nghiệm RỦI RO** (xem 3.3) | ~3h + 1 tuần khảo sát | CPU | 🔴 **Một trong bốn chết ⇒ reframe/dừng NGAY — đã tiết kiệm 8 tuần** |
| 5 | **E2 — lưới chính** (chia stage theo k) | ~20h | CPU | Chỉ chạy khi **cả 4 ở trên còn sống** |
| 6 | E3 ablation → E4 ceiling → **E4 U-Net** → E5 → E6 → E7 | ~18h + 2h GPU | CPU, **GPU chỉ cho `run_unet.py`** | E7: đọc **A8** trước khi dùng chữ "external validation" |

> **Vì sao đảo ngược thứ tự (prereg §6/A10):** kế hoạch cũ chi **~35/40 giờ** cho các thí nghiệm có **xác suất bất ngờ ≈ 0** (E2 chỉ fail nếu code có bug; "U-Net thắng thresholding" đã biết từ 2015), và xếp **cả bốn câu hỏi thật sự bất định** vào mục "làm sau". Đó là **dấu vân tay của confirmation bias — trong một bài đi tố cáo người khác confirmation bias.** Bốn thí nghiệm rủi ro tốn ~3h và **quyết định bài có sống không**; chạy chúng trước.

### Cổng Tuần-0 — lit-review (KHÔNG compute, ĐÃ XONG)
`docs/related-work-positioning.md` đã hoàn thành: 6 near-rival + Al-Najdawi đã đọc & có đoạn định vị. ✅ Đủ điều kiện mở E2 **về mặt lit-review**.

### 3.0 · Smoke test local (làm ở MÁY, trước khi lên Kaggle)
Chạy toàn bộ pipeline trên dữ liệu synthetic < 60s. Bắt lỗi cấu trúc ở local rẻ hơn nhiều so với sau 8h chạy Kaggle:

```bash
python -m pytest tests/ -q                       # 3 unit test cổng cứng phải PASS
python scripts/run_exact_check.py --config configs/exp_smoke.yaml   # synthetic, [PLACEHOLDER]
```
Số synthetic **không bao giờ** là kết quả — luôn gắn `[PLACEHOLDER]`.

### 3.1 · E1 — cổng bit-exact ★ CỔNG CỨNG ĐẦU TIÊN
```bash
python scripts/run_exact_check.py --config configs/exp_main.yaml
```
- DP phải khớp **bit-exact** với vét cạn tại k=2,3 (theo quy ước A5a: `|f_DP − f_brute| ≤ 1e-9` **VÀ** mask cảm sinh giống hệt, ngưỡng canonicalise).
- 🔴 **Nếu cổng này FAIL → DỪNG TOÀN BỘ.** Mọi kết luận về P2 dựng trên DP. Bước debug ĐẦU TIÊN là **audit quy ước** (`0log0`, lớp rỗng, có tính nền cường-độ-0 hay không — A5b/A5c), **KHÔNG** phải debug DP.
- Cho ra: **Bảng II** (DP vs vét cạn).

### 3.2 · E1b — cổng đúng-đắn implementation (A6) ★ CỔNG CỨNG THỨ HAI
Tái tạo bảng Kapur/Otsu multilevel **đã công bố** trên ảnh chuẩn (Lena/Cameraman/Baboon/Peppers, k=2..5) ở **đúng NFE đã công bố**, cho **MỌI** thuật toán. Chỉ sau khi qua cổng này, hit-rate-to-DP mới được dùng làm *kết quả*. (Phá vòng tròn logic: không được dán nhãn "GOA hỏng" chỉ vì nó không đạt tối ưu — đó chính là P2.)

### 3.3 · TUẦN 1 — bốn thí nghiệm rủi ro (~10h compute + 1 tuần khảo sát tay)
Chạy **cả bốn** trước khi đụng E2. Nếu **một** trong bốn chết → reframe/dừng, đã tiết kiệm 8 tuần:

1. **Bảng I — trắc lượng thư mục** (search string + PRISMA-lite + **2 coder + Cohen's κ**). **0 compute.** *Quyết định: P1 có mục tiêu, hay là strawman?* (Bảng I xuống **Supplementary** — quyết định đóng khung #3; Bảng I của bản thảo = DP vs vét cạn.)
2. **Bậc-5 / P5 — ngưỡng 1-tham-số vs 7 metaheuristic, nested CV** (~1h). *Quyết định: bài có đóng góp dương không?*
   ```bash
   python scripts/run_ceiling.py --config configs/exp_ceiling.yaml --stage p5_nested_cv
   ```
   ⚠️ Phải chạy **nested CV cấp bệnh nhân** (A3) — fit `q*` trên outer-train fold, đóng băng, đánh giá out-of-fold. **KHÔNG** train-on-test.
3. **Spearman(k, Dice) theo TỪNG decoding rule** (~1h). *Quyết định: "metric sai" hay chỉ "decoder sai"?* Nếu tương quan âm chỉ tồn tại dưới rule `brightest` ⇒ headline "metrics are anti-correlated" SAI.
4. **`morph` vs `oracle_interval`** (~1h). Nếu morph **vượt** oracle ⇒ **P4 tự bác bỏ**.

### 3.4 · E2 — lưới chính (CHỈ khi cả 4 ở trên sống)
```bash
python scripts/run_main_grid.py --config configs/exp_main.yaml
```
- Lưới: các bệnh nhân × k ∈ {2,3,4,5,6,8,10} × 11 phương pháp × ≥5 seed.
- **Chia stage theo k** (Bước 4) — không chạy hết trong 1 session.
- Cho ra: **Bảng III**, **Hình 2** (CD diagram), **Hình 3** (Goodhart).

### 3.5 · E3 — ablation QIGOA
```bash
python scripts/run_ablation.py --config configs/exp_ablation.yaml
```
Cùng NFE, **cùng mọi hyperparameter khác**. Cho ra **Bảng IV**.

### 3.6 · E4 — ceiling + U-Net (bước GPU duy nhất)
```bash
python scripts/run_ceiling.py --config configs/exp_ceiling.yaml       # CPU: oracle scans
python scripts/run_unet.py    --config configs/exp_unet.yaml          # GPU: 2D U-Net
```
Bật **GPU T4** chỉ cho `run_unet.py`. Cho ra **Bảng V** + **Hình 4** (ceiling ladder).

### 3.7 · E5 — metric đầy đủ
Nằm trong các script E2/E3/E4 (Dice, HD95, NSD, PSNR, SSIM, số thành phần liên thông, empty-mask rate). Không có script riêng.

### 3.8 · E6 — thống kê
```bash
python scripts/run_stats.py --config configs/exp_main.yaml
```
Đơn vị = **bệnh nhân**. Wilcoxon (`zero_method='pratt'` — A4d) + rank-biserial · Friedman + Nemenyi + CD · TOST (90% CI + Δ_ach) · Bayesian ROPE.

### 3.9 · E7 — ngoại kiểm LGG (đọc cảnh báo A8 dưới đây TRƯỚC)
```bash
python scripts/run_external.py --config configs/exp_external.yaml
```
**Zero-shot** — CẤM re-tune ngưỡng 1-tham-số trên LGG.

### 3.10 · Build bảng + hình từ results/
```bash
python scripts/build_tables.py     # results/ → paper/tables/*.tex
python scripts/build_figures.py    # results/ → paper/figures/*.pdf
```

> 📌 Tên script/config ở trên theo `docs/ke-hoach-trien-khai.md` §1–§2. `scripts/` đang được viết song song — nếu một cờ (`--stage`, `--k-subset`) chưa có, xem `--help` của script tương ứng.

---

## Bước 4 — Resume-được: chia stage, checkpoint, merge

Session ≤ 12h ⇒ E2 (~20h wall CPU) **không** chạy hết trong một lần. Thiết kế resume:

1. **Chia theo `k`.** Mỗi session chạy 2–3 giá trị k, ghi CSV riêng:
   ```bash
   python scripts/run_main_grid.py --config configs/exp_main.yaml --k-subset 2,3,4
   # session sau:
   python scripts/run_main_grid.py --config configs/exp_main.yaml --k-subset 5,6,8,10
   ```
2. **Cache histogram.** Histogram của các ảnh tính một lần, lưu `.npy` → mọi run sau đọc từ cache (phần chậm nhất mà lại tất định).
3. **Checkpoint sau mỗi (image, k, algo, seed).** Session chết → chạy lại chỉ tốn phần chưa xong. Ghi ra `results/main/partial/`.
4. **Merge CSV** ở cuối: gộp các CSV partial thành `results/main/raw.csv` + `summary.csv`.
5. **GPU CHỈ cho `run_unet.py`.** Mọi thứ khác để **Accelerator: None** để không đốt 30 GPU-h/tuần.

`run-manifest.json` sinh cho **MỖI session** (`src/manifest.py`): `{git_commit, config_hash, seeds, dataset_version, lib_versions, timestamp, output_paths}`. **Không manifest = run không tồn tại với paper.**

---

## Bước 5 — Cuối mỗi session: tải results/ về + provenance + commit

1. **Tải `results/` về máy.** Kaggle: menu ⋮ → **Download** output, hoặc nén rồi tải:
   ```bash
   !cd /kaggle/working/qigoa && tar czf /kaggle/working/results_$(date +%Y%m%d).tgz results/
   ```
   Tải file `.tgz` từ tab **Output**.
2. **Giải nén vào repo local**, ghi đè `results/` (kết quả là output do script sinh — không sửa tay).
3. **Thêm dòng provenance** vào `docs/RESULTS.md` (append-only) cho mỗi Bảng/Hình vừa sinh: `Bảng X ← results/<path> ← scripts/<script> --config <config> @commit <hash>, seeds {0..4}`.
4. **Commit** (khi tác giả muốn): `git add results/ docs/RESULTS.md && git commit`.

> 🔴 **Không xoá run xấu** (prereg §5). Run âm là dữ liệu — ghi vào `RESULTS.md` như mọi run khác.

---

## Bước 6 — Timestamp preregistration (A9) — VIỆC CỦA TÁC GIẢ, làm TRƯỚC khi chạy thật

Trước khi chạy bất kỳ thí nghiệm **thật** nào (không phải smoke test), tác giả cần **cắm cọc thời gian** cho preregistration để câu "chúng tôi đã preregister" **verify được** bởi bên thứ ba (git history rewrite được, nên tự nó không đủ):

1. Đăng ký **OSF** (miễn phí, [osf.io](https://osf.io) → Registrations) **HOẶC** archive `docs/preregistration.md` lên **Zenodo** ([zenodo.org](https://zenodo.org)) để lấy **DOI có timestamp**.
2. Điền **commit hash** của commit chứa `docs/preregistration.md` vào **dòng 4** của file đó ("Commit khi khoá").
3. **Cite DOI/OSF link đó trong Abstract** của paper.

> ⚠️ Và gọi đúng tên file này trong bản thảo: *"Confirmatory analysis protocol for exploratory findings"* — vì P1/P3 được phát hiện exploratorily trên pipeline có lỗi (A9). **Dán nhãn sai một preregistration còn tệ hơn không có.**

---

## ⚠️ Cảnh báo liêm chính A8 — đọc trước khi dùng chữ "external validation"

1. **Chỉ training split có ground truth.** KHÔNG claim "SOTA BraTS leaderboard".
2. **LGG có thể KHÔNG ngoại kiểm.** Buda et al. = 110 ca **TCGA-LGG**; BraTS 2020 đã nuốt **108 ca TCGA-LGG** từ đúng collection đó. **BẮT BUỘC** tải `name_mapping.csv`, đối chiếu, **báo cáo số trùng bằng con số** trước khi gọi LGG là "external". Nếu trùng mà vẫn gọi ngoại kiểm và reviewer BraTS bắt được → đọc như **misrepresentation**. Lựa chọn thay thế mạnh nhất: ngoại kiểm theo **chiều TASK** (tune WT/FLAIR → test ET/T1ce).
3. **Bẫy kênh LGG:** ảnh Kaggle LGG là **TIFF 3 kênh** (pre-contrast / FLAIR / post-contrast). FLAIR = **kênh giữa, index 1**. Lấy nhầm kênh ⇒ histogram sai ⇒ toàn bộ Kapur/DP sai. `src/data/lgg_loader.py` đã có unit test cho việc này (`tests/test_lgg_loader.py`).

---

## Phụ lục — lệnh copy-paste nhanh (khởi động một session mới)

```bash
# 1. Lấy code
!git clone https://github.com/HoangLong08/<TEN_REPO>.git /kaggle/working/qigoa
%cd /kaggle/working/qigoa
!git rev-parse HEAD

# 2. Cài phần thiếu
!pip install -q medpy tifffile

# 3. Sanity: unit test cổng cứng
!python -m pytest tests/test_exact_dp.py tests/test_nfe_budget.py -q

# 4. Chạy theo đúng thứ tự A10 (ví dụ E1 trước)
!python scripts/run_exact_check.py --config configs/exp_main.yaml

# 5. Cuối session: đóng gói results để tải về
!tar czf /kaggle/working/results_$(date +%Y%m%d_%H%M).tgz results/
```

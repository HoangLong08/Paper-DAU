# RESULTS.md — Provenance ledger + nhật ký thí nghiệm (append-only)

**Trạng thái:** 🟩 **Lô quyết định đã chạy trên Kaggle (17/07/2026, @commit `1461520`).** Cổng cứng E1 (Bảng II) PASS trên dữ liệu THẬT. P5 nested CV + lưới `screening` đã sinh CSV. Các ô còn lại (Bảng III/IV, Hình 2/3, external) vẫn `[PLACEHOLDER]` — chờ E2 lưới chính (`exp_main.yaml`, n=369, 5 seed).

> ⚠️ **`results/smoke/` trong repo là SYNTHETIC placeholder** (sót lại trong `/kaggle/working` bền của Kaggle từ smoke test cũ, bị `tar` gói kèm). Đã gitignore; **KHÔNG bao giờ** commit như kết quả (IRON RULE 1/3).

> **File này vận hành IRON RULE 1 & 3 (CLAUDE.md §2, §5.3).**
>
> - **IRON RULE 1 — KHÔNG bịa số.** Mọi con số trong `paper/` phải truy được về một ô CSV trong `results/`, qua đúng một dòng provenance dưới đây.
> - **IRON RULE 3 — Số chưa có dòng provenance = `[PLACEHOLDER]`.** Không bao giờ âm thầm "thăng cấp" placeholder thành kết quả thật.
> - **Luật APPEND-ONLY (CLAUDE.md §9).** Chỉ được **thêm** dòng. **Không xoá run xấu** — run âm là dữ liệu. Mỗi run một dòng nhật ký: ngày tuyệt đối · commit · config · seed · tóm tắt · kết luận.
> - **Số flow một chiều:** `configs/ → scripts/ → results/ → paper/`. Bảng & hình trong `paper/` được **sinh** bởi `build_tables.py` / `build_figures.py`, **không gõ tay**.
> - **KHÔNG tái dùng số từ commit `c4fe108`** (bug NFE 13,4%, GOA hit-rate 0%, metric tự chế, pseudo-replication). Nó là bằng chứng chẩn đoán, không phải nguồn số liệu.

---

## 1. Bảng provenance — mỗi Bảng/Hình một dòng (ke-hoach-trien-khai §3)

Luật: một số được phép vào bản thảo **chỉ khi** dòng của nó ở trạng thái không còn ⬜, và cột `@commit` + `seeds` đã điền thật.

| Bảng/Hình (paper) | ← results/<path> | ← script | seeds | @commit | Trạng thái |
|---|---|---|---|---|---|
| **Bảng I** — trắc lượng thư mục (→ Supplementary) | *(khảo sát tay, 2 coder + Cohen's κ)* | *thủ công + PRISMA-lite* | — | — | ⬜ `[PLACEHOLDER]` chưa làm |
| **Bảng II** — DP vs vét cạn (bit-exact) | `results/exact/dp_vs_bruteforce.csv` | `scripts/run_exact_check.py --config configs/exp_main.yaml` | — (tất định) | `1461520` | 🟩 **THẬT** — 160 ô (20 ảnh × 2 target × 2 bg × k∈{2,3}), 0 FAIL, mọi mask giống hệt, tol 1e-9 |
| **Bảng III** — gap-to-optimum, hit-rate, NFE, runtime | `results/main/summary.csv` | `scripts/run_main_grid.py` | {0..4} | — | ⬜ `[PLACEHOLDER]` |
| **Bảng IV** — ablation QIGOA (full / −quantum / −memetic / −OBL / −Lévy / PSO+memetic) | `results/ablation/summary.csv` | `scripts/run_ablation.py` | {0..4} | — | ⬜ `[PLACEHOLDER]` |
| **Bảng V** — phương pháp đề xuất vs 7 metaheuristic (nested CV) | `results/ceiling/summary.csv` | `scripts/run_ceiling.py` | {0..2}×5fold | — | ⬜ `[PLACEHOLDER]` |
| **Hình 1** — sơ đồ pipeline + ngân sách NFE | — | drawio-skill (thủ công) | — | — | ⬜ `[PLACEHOLDER]` |
| **Hình 2** — Critical Difference diagram | `results/stats/cd.csv` | `scripts/run_stats.py` | {0..4} | — | ⬜ `[PLACEHOLDER]` |
| **Hình 3** — Goodhart (trục kép: fitness/PSNR ↑ vs Dice/HD95 ↓ theo k) | `results/main/summary.csv` | `scripts/build_figures.py` | {0..4} | — | ⬜ `[PLACEHOLDER]` |
| **Hình 4** — Ceiling ladder ★ | `results/ceiling/` + `results/unet/` | `scripts/build_figures.py` | {0..2} | — | ⬜ `[PLACEHOLDER]` |
| **Supp.** — external replication (LGG / task-axis) | `results/external/summary.csv` | `scripts/run_external.py` | {0..4} | — | ⬜ `[PLACEHOLDER]` |
| **Supp.** — empty-mask rate theo k (A7) | `results/main/summary.csv` | `scripts/build_figures.py` | {0..4} | — | ⬜ `[PLACEHOLDER]` |
| **Supp.** — convergence curve + boxplot per-seed (A6) | `results/main/raw.csv` | `scripts/build_figures.py` | {0..4} | — | ⬜ `[PLACEHOLDER]` |

---

## 2. Cổng cứng — trạng thái (phải PASS trước khi số ở mục 1 được coi là thật)

| Cổng | Test / script | Điều kiện | Trạng thái |
|---|---|---|---|
| Bit-exact DP vs vét cạn | `tests/test_exact_dp.py` + E1 | `|f_DP−f_brute| ≤ 1e-9` **và** mask cảm sinh giống hệt (ngưỡng canonicalise, A5a) | 🟩 **PASS** (17/07, @`1461520`) — unit `17 passed`; E1 thật 160/160 ô |
| NFE bằng nhau (±0) | `tests/test_nfe_budget.py` | mọi thuật toán tiêu thụ đúng cùng NFE | 🟩 **PASS** (17/07, @`1461520`) — trong `17 passed` |
| Suy biến P1 (unit test số học, KHÔNG phải Result) | `tests/test_degeneracy.py` | nhóm theo **mask hash** ⇒ std(Dice)=0 (A1) | 🟩 **PASS** (17/07, @`1461520`) — trong `17 passed` |
| Đúng-đắn implementation (E1b, A6) | tái tạo bảng Kapur/Otsu đã công bố (Lena/Cameraman…) | khớp trong X% ở đúng NFE công bố | ⬜ chưa chạy |

---

## 3. Nhật ký thí nghiệm (append-only)

*(Mỗi run một dòng. Ngày tuyệt đối · commit · config · seeds · kết quả tóm tắt · kết luận. Không xoá.)*

- **2026-07-17** · `@1461520` · Kaggle notebook `hlongg28/qigoa-reality-check-lo-quyet-dinh-batch` v4, CPU, ~6,5h · **LÔ QUYẾT ĐỊNH chạy trọn, COMPLETE.** Dataset auto-detect (Kaggle mount tại `/kaggle/input/datasets/awsaf49/…`) → symlink `root_local`, config không sửa. Gói: `results_20260717_1712.tgz`.
- **2026-07-17** · `@1461520` · 3 cổng cứng: `pytest test_exact_dp + test_nfe_budget + test_degeneracy` → **`17 passed`**. Cổng PASS.
- **2026-07-17** · `@1461520` · `configs/exp_main.yaml` (exact_check: 20 ảnh, k∈{2,3}, cả 2 bg) · **E1 bit-exact: 160/160 ô PASS**, mọi `|Δf| = 0.000e+00`, mọi mask giống hệt (mask_identical=1), 0 placeholder, elapsed 2077s. → **Bảng II (số THẬT đầu tiên vào bản thảo).**
- **2026-07-17** · `@1461520` · `configs/exp_ceiling.yaml --stage p5_nested_cv` (n=368 cohort, 5 fold, cả 2 bg) · **P5 nested CV** sinh `results/ceiling/{raw,qstar,summary}.csv` (12512 hàng, 1343s). q* đóng băng trên outer-train; test_dice_median WT/FLAIR ~0,69–0,78, ET/T1ce ~0,44–0,55. ⚠️ **Số THẬT nhưng CHƯA kết luận thắng/thua** — phải đọc `summary.csv` + so 7 metaheuristic trước khi chốt Bảng V.
- **2026-07-17** · `@1461520` · `configs/exp_week1.yaml` (**SCREENING**: n=60, seeds {0..2}, 1 bg) · lưới sàng lọc #3/#4: `results/week1/{raw,summary,mask_identity}.csv` (23520 ô, 25093s ≈ 7h — đây là nút thắt thời gian của lô) + `run_stats.py` → `results/week1/stats/{pairwise,tost,bayes,cd}.csv`. ⛔ **`screening` — KHÔNG vào Bảng III/Hình 2/Hình 3.** Chỉ trả lời dấu & hướng; Bảng của paper đến từ `exp_main.yaml` (n=369, 5 seed).
- **2026-07-17** · ⚠️ **Ghi chú n:** cohort thật = **368 ca**, không phải 369 như `exp_main.yaml` giả định (1 ca bị `build_cohort` loại — nhiều khả năng thiếu modality). `data/splits/brats_cohort.csv` = nguồn chuẩn; mọi script iterate theo nó. Cần xác nhận ca nào bị loại & vì sao trước khi viết Methods.
- **2026-07-17** · ⚠️ **Family A trong E6 bị bỏ qua** (`run_stats.py` báo cần `results/ceiling/raw.csv` + `results/unet/raw.csv`) — U-Net (GPU) chưa chạy, đúng kế hoạch (nằm ngoài lô này).
- **2026-07-17** · `@1461520` · Kaggle notebook `hlongg28/qigoa-oracle-stage` v1, CPU, ~32 phút · **STAGE ORACLE** (`run_ceiling.py --stage all`) sinh **thang trần** vào `results/ceiling/` (14720 hàng). Gói `ceiling_20260717_1831.tgz`.
- **2026-07-17** · `@1461520` · **CEILING DECOMPOSITION (n=368, THẬT, loại C) — đóng góp dương #1:**
  - **WT/FLAIR:** oracle_single = oracle_interval = **0,848**, oracle_levelset = **0,853**. ⇒ một ngưỡng đơn ĐÃ chạm trần; trần WT **cao** và **khớp François & Tinarrage 0,83±0,18** (JMIV 2026). Cường độ ĐỦ cho WT.
  - **ET/T1ce:** oracle_single = **0,552** < oracle_interval = **0,628** < oracle_levelset = **0,635**. ⇒ ET cần một BAND (interval > single), và trần chỉ 0,635 ⇒ cường độ **về cơ bản KHÔNG đủ** cho ET. Đây là phân rã "thông tin nằm ở đâu" — chưa ai làm.
- **2026-07-17** · ⚠️🔴 **RỦI RO #4 ĐÃ NỔ (screening, cần xác nhận n=368):** decode `morph` **VƯỢT** oracle cường độ trên WT/FLAIR. Tại **k=3, CẢ 8 metaheuristic** cho morph dice_median 0,90–0,91 > oracle_levelset 0,853 (8/8, không phải cherry-pick). ⇒ oracle cường độ **KHÔNG phải trần** của pipeline thật — **hình thái học phá trần**. **P4 dạng "we establish the ceiling" TỰ BÁC BỎ** (prereg §6/A2 đã cảnh báo). Số screening (n=60); PHẢI xác nhận trên `exp_main.yaml` (n=368, 5 seed) trước khi viết.
- **2026-07-17** · ⚠️ **RỦI RO #2 — đóng góp dương P5 phải REFRAME (screening):** P5 (ngưỡng hiệu chỉnh, WT 0,73) **KHÔNG thắng** metaheuristic khi metaheuristic dùng decode `morph` (WT 0,91). P5 chỉ thắng trên **ET/T1ce** (0,499 vs metaheuristic tốt nhất 0,319). ⇒ câu "ngưỡng 1-tham-số thắng metaheuristic" SAI trên WT.
- **2026-07-18** · `@1461520` · Kaggle notebook `hlongg28/qigoa-reality-check-e2-main-grid` v7 (SaveAndRunAll, CPU, ~11h05) · **E2 SESSION 1 — LƯỚI CHÍNH, `configs/exp_main.yaml --k-subset 2,3 --resume`.** Cổng cứng: `17 passed`; **E1 tái chạy trên run sạch: 160 ô, 0 FAIL, 1713.7s → PASS** (xác nhận độc lập Bảng II). `make_splits`: quét 369 thư mục ca → **cohort n = 368** (loại 1 ca) + 5 fold phân tầng. E2: **42.709 ô metaheuristic trong 630,0 phút** ⇒ **0,885 s/ô**. Tiến độ: **k=2 → 21.375/66.240 (32,3%)**, **k=3 → 21.334/66.240 (32,2%)**, k∈{4,5,6,8,10} = 0%. Ngân sách wall-clock 10,5h **dừng êm đúng thiết kế** → Cell 8 đóng gói `results_20260718_0744.tgz`, run COMPLETE (Kaggle lưu được output thay vì bị kill mất trắng).
  - ⛔ **PARTIAL (9,2% toàn lưới) — TUYỆT ĐỐI KHÔNG vào Bảng III / Hình 2 / Hình 3.** Chưa có dòng provenance cho E2; `summary.csv` chỉ hợp lệ khi một `K_SUBSET` chạy XONG TRỌN. (IRON RULE 3.)
  - 📐 **Suy ra (ước lượng, không phải số đo):** 66.240 ô/k × 0,885 s ⇒ **~16,3 h/k**; toàn lưới 7 k ≈ **~114 h CPU ≈ 10 session nữa**. Đây là dữ kiện lập kế hoạch, chưa phải kết quả.
- **2026-07-18** · ⚙️ **Ghi chú hạ tầng (không phải kết quả):** MCP Kaggle `save_notebook` **gỡ mất dataset input** mỗi lần push ⇒ 3 lần chạy đầu (v2/v3/v6) chết ở guard Cell 2 với `/kaggle/input: (RONG)` sau ~30s. Việc kích hoạt run phải do tác giả làm trong trình duyệt (Add Input + Save & Run All); sau đó **không được push `save_notebook`** nữa. Guard Cell 2 đã làm đúng việc: chặn ngay thay vì chạy lưới trên dữ liệu rỗng.
- **2026-07-17** · 🟢 **PHÁT HIỆN TRUNG TÂM (củng cố luận đề, screening):** clinical Dice bị chi phối bởi **DECODING**, không bởi optimizer. Cùng Kapur-thresholds: decode `brightest` → Dice ~0,46; decode `morph` → ~0,91 (**gấp 2×, chỉ đổi decoding**). Optimizer bất biến: QIGOA ≈ GA ≈ PSO ≈ ... đều ~0,91 tại k=3 morph. ⇒ *"optimizer là đồ trang trí; lựa chọn decoding tùy tiện & không báo cáo mới quyết định Dice."* Đây là hook định lượng mới cho LUẬN ĐỀ DUY NHẤT — nhưng là **screening**, phải tái lập ở E2.
- **2026-07-19** · `@e855945` · Kaggle notebook `hlongg28/qigoa-reality-check-e2-main-grid` v9 (CPU, ~10h32) · **E2 SESSION 2 — `configs/exp_main.yaml --k-subset 2,3,4 --resume`, song song 4 tiến trình.** Cell R restore từ `results_20260718_0744.tgz` (dataset `hlongg28/goa-e2-session1`) → `results/main/raw.csv` **175.830 dòng** ⇒ resume hợp lệ, không tính lại session 1. Kaggle cấp **4 vCPU** (`[E2] chạy song song 4 tiến trình`). Ngân sách 10,5h dừng êm sau **630,0 phút** → Cell 8 đóng gói `results_20260719_0306.tgz`, run COMPLETE.
  - **Tiến độ (Cell 7, n=368, 66.240 ô/k):** k=2 → **41.760 (63,0%)**, k=3 → **41.760 (63,0%)**, k=4 → **41.761 (63,0%)**, k∈{5,6,8,10} = 0%. Tích luỹ **125.281 / 463.680 ô = 27,0% toàn lưới**.
  - **Thông lượng đo được:** 125.281 − 42.709 = **82.572 ô trong 37.800 s ⇒ 0,458 s/ô**, so với **0,885 s/ô** tuần tự ở session 1 ⇒ **tăng tốc 1,93× trên 4 vCPU** (hiệu suất song song ~48%; phần mất do pickle `Slice` + ghi CSV tuần tự ở tiến trình cha + chi phí `--resume` nạp lại ô đã xong).
  - ⛔ **PARTIAL (27,0%) — TUYỆT ĐỐI KHÔNG vào Bảng III / Hình 2 / Hình 3.** Chưa `K_SUBSET` nào chạy XONG TRỌN ⇒ `summary.csv` chưa hợp lệ, chưa có dòng provenance cho E2. (IRON RULE 3.)
  - 📐 **Suy ra (ước lượng, KHÔNG phải số đo):** còn 338.399 ô × 0,458 s ≈ **43 h CPU ≈ 4 session nữa** — nhưng đây là **CẬN DƯỚI**: k∈{5,6,8,10} có không gian tìm kiếm lớn hơn nên chi phí/ô cao hơn k∈{2,3,4}. Số session thực tế nhiều khả năng > 4.
- **2026-07-19** · `@e855945` · Kaggle notebook `hlongg28/qigoa-reality-check-e2-main-grid` v10 (CPU, 4 vCPU, ~10h29) · **E2 SESSION 3 — `configs/exp_main.yaml --k-subset 2,3,4 --resume`.** Cell R restore đúng file mới (`results_20260719_0306.tgz`) → `raw.csv` **542.420 dòng**. E0 cohort = 368; E1 skip (đã có). Cell 6: **`[E2] stage k=2,3,4 XONG TRON (rc=0) trong 627.3 phut`** — **KHÔNG chạm ngân sách**, stage kết thúc tự nhiên. Gói `results_20260719_1424.tgz`.
  - **Tiến độ (Cell 7, n=368, kỳ vọng 66.240 ô/k):** k=2 → **66.240 (100,0%) XONG**, k=3 → **66.240 (100,0%) XONG**, k=4 → **73.132 (110,4%)** ⚠️, k∈{5,6,8,10} = 0%. `De xuat K_SUBSET ke tiep: 5,6,8,10`.
  - **Thông lượng:** 205.612 − 125.281 = **80.331 ô trong 37.638 s ⇒ 0,469 s/ô** (session 2: 0,458 s/ô, cùng 4 vCPU) ⇒ chi phí/ô **ổn định**, không phụ thuộc rõ vào k trong dải {2,3,4}.
  - 🔴 **BẤT THƯỜNG CHẶN — k=4 đếm 73.132 > 66.240 kỳ vọng (+6.892, tức 110,4%).** Cell 7 đã `drop_duplicates` trên khoá `[patient_id, target, include_zero_bg, method, seed]` rồi mới đếm ⇒ **không phải trùng dòng đơn thuần**, mà là có **tuple khoá NHIỀU HƠN số tổ hợp khả dĩ** (368×2×2×9×5 = 66.240). k=2 và k=3 khớp CHÍNH XÁC 66.240 ⇒ lỗi khu trú ở k=4. Giả thuyết ưu tiên: một trường khoá bị ghi **không đồng nhất kiểu/chữ hoa-thường** giữa các session (VD `include_zero_bg` = `True` vs `true`, hoặc `seed` chuỗi vs số) làm cùng một ô bị đếm thành hai. **⛔ CHƯA ĐƯỢC dùng bất kỳ số k=4 nào** (kể cả vào bảng nháp) cho tới khi truy xong nguyên nhân trên `raw.csv` tải về. k=2, k=3 **không** bị ảnh hưởng bởi bất thường này nhưng cũng phải qua kiểm tra trùng lặp trước khi vào Bảng III.
  - ⛔ **Toàn lưới vẫn PARTIAL (~44%)** — chưa có dòng provenance cho E2; `summary.csv` chỉ được dùng sau khi (a) giải quyết bất thường k=4, (b) chạy xong k∈{5,6,8,10}. (IRON RULE 3.)
  - 📐 **Ước lượng (không phải số đo):** còn 4 × 66.240 = 264.960 ô × 0,469 s ≈ **34,5 h ≈ 3,3 session** — **cận dưới**, vì k∈{5,6,8,10} có không gian tìm kiếm lớn hơn dải đã đo.
- **2026-07-19** · 🔴→✅ **TRUY XONG BẤT THƯỜNG k=4 (110,4%) — là LỖI CODE CỦA TA, không phải lỗi dữ liệu.** Chuỗi bằng chứng khép kín:
  1. File `raw.csv` trên đĩa **SẠCH** — `grep -c ',True,\|,False,'` = **0**. Chữ hoa chưa bao giờ được ghi ra.
  2. `read_results_csv` gọi `pd.read_csv(..., comment="#")` với `low_memory=True` (mặc định pandas) ⇒ dtype suy diễn **theo từng khối**. Khi `raw.csv` đủ lớn, khối chỉ chứa `true`/`false` ở `include_zero_bg` bị đọc thành **bool** ⇒ `str(v)` cho `'True'`. **Tái hiện được:** cùng một file, `low_memory=True` → `['False','True','false','na','true']`; `low_memory=False` → `['false','na','true']`.
  3. Hai hậu quả: (a) `done_keys()` trượt khoá ⇒ `--resume` **tính lại** ô đã xong rồi append ⇒ **65.534 dòng lặp**; (b) `groupby` trong `summarise()` **tách CÙNG một điều kiện thành hai nhóm** ⇒ `summary.csv` đã sinh ra hàng `include_zero_bg=False, n_patients=77` trong khi thực tế là 368.
  - **Mức thiệt hại khoa học = 0.** Mọi bản sao khớp **bit-for-bit trên toàn bộ 22 cột số đo** (thresholds/fitness/dice/psnr/ssim/nfe/hit đều `nunique()==1`) ⇒ tính tất định KHÔNG hỏng; chỉ lãng phí compute + làm hỏng bảng tổng hợp. `summary.csv` cũ **bỏ đi, sinh lại**.
  - **Sau khi vá, cả ba k đếm CHÍNH XÁC 66.240** ô `(patient, target, bg, method, seed)` ⇒ **k=2, k=3, k=4 thực sự XONG TRỌN, lưới đầy đủ.**
  - **Vá:** `_common.ID_COLS` + `read_results_csv(..., low_memory=False, dtype=str cho ID_COLS)` (gốc); `summarise()` bỏ trùng trên khoá đầy đủ trước khi tổng hợp (phòng vệ); `scripts/repair_raw_dedup.py` dọn hậu quả đã ghi ra đĩa, có **cổng an toàn** dừng nếu bản sao bất đồng giá trị. `pytest tests/` → **65 passed**.
  - `raw.csv` sau dọn: **925.918 → 860.384 dòng**, 0 dòng lặp, `done_keys` = 206.816. Gói sạch: `results/session4/results_20260719_CLEAN.tgz`.
  - ⛔ Toàn lưới vẫn **PARTIAL** (k∈{5,6,8,10} = 0%) ⇒ chưa dòng provenance, chưa vào Bảng III.

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
- **2026-07-20** · `@9c2f4e4` · Kaggle notebook `hlongg28/qigoa-reality-check-e2-main-grid` v11 (CPU, 4 vCPU, ~10h39) · **E2 SESSION 4 — `--k-subset 5,6,8,10 --resume`.** Cell R restore đúng `results_20260719_CLEAN.tgz` → `raw.csv` **860.388 dòng** (khớp 860.384 + 4 dòng banner). Cell 6 chạm ngân sách: `[BUDGET] Het 10.5h` sau **630,0 phút**. Gói `results_20260720_0211.tgz`.
  - ✅ **BẢN VÁ `9c2f4e4` ĐÃ XÁC NHẬN Ở QUY MÔ THẬT:** Cell 7 báo **k=2 → 66.240 (100,0%) XONG · k=3 → 66.240 (100,0%) XONG · k=4 → 66.240 (100,0%) XONG**. Con số 110,4% của session 3 **biến mất hoàn toàn**; không có dòng `[summarise] BỎ TRÙNG` nào ⇒ `--resume` không còn trượt khoá, không sinh thêm dòng lặp.
  - **Tiến độ:** k=5, 6, 8, 10 → mỗi k **20.520 (31,0%)**. Tích luỹ **280.800 / 463.680 ô = 60,6%** toàn lưới.
  - **Thông lượng:** 280.800 − 198.720 = **82.080 ô trong 37.800 s ⇒ 0,461 s/ô** (session 2: 0,458; session 3: 0,469).
  - 🔎 **Đính chính một dự đoán của chính ta:** đã cảnh báo rằng k∈{5,6,8,10} sẽ **đắt hơn** k∈{2,3,4} vì không gian tìm kiếm lớn hơn. **SAI** — chi phí/ô gần như bất biến qua cả ba session (0,458 / 0,469 / 0,461 s/ô, chênh <2,4%). Giải thích khả dĩ: ngân sách NFE là **hằng số theo thiết kế**, không co giãn theo k, nên số lần đánh giá hàm mục tiêu — chứ không phải số chiều — mới chi phối wall-clock. Điều này **củng cố** việc dùng NFE làm đồng tiền so sánh chính (§1).
  - ⚠️ **Nhiễu vô hại đã kiểm:** 4 traceback `ForkPoolWorker-1..4` ở `multiprocessing/pool.py` xuất hiện tại t=37923,50 s — **SAU** khi Cell 8 ghi xong `.tgz` (t=37923,47 s). Đó là các tiến trình con của `mp.Pool` bị dọn khi `subprocess.run(timeout=)` giết tiến trình cha. Không phải lỗi tính toán; run vẫn COMPLETE và output vẫn được lưu. (Có thể dập tiếng ồn này về sau bằng `pool.terminate()` trong handler tín hiệu — thuần thẩm mỹ, không ưu tiên.)
  - ⛔ Vẫn **PARTIAL** (60,6%) — chưa dòng provenance, chưa vào Bảng III.
  - 📐 **Ước lượng:** còn 4 × 45.720 = 182.880 ô × 0,461 s ≈ **23,4 h ≈ 2,2 session**. Lần này ước lượng đã có cơ sở vững hơn: chi phí/ô đo được ổn định qua 3 session liên tiếp trên đúng dải k còn lại.
- **2026-07-20** · `@1f961fb` · Kaggle notebook `hlongg28/qigoa-reality-check-e2-main-grid` v12 (CPU, ~10h39) · **E2 SESSION 5 — `--k-subset 5,6,8,10 --resume`.** Cell R restore đúng `results_20260720_0211.tgz` → `raw.csv` **1.196.004 dòng**. Cell 6 chạm ngân sách: `[BUDGET] Het 10.5h` sau **630,0 phút**. Gói `results_20260720_1749.tgz`.
  - **Tiến độ (Cell 7):** k=2, 3, 4 → **66.240 (100,0%) XONG** (giữ nguyên, không trôi); k=5, 6, 8, 10 → mỗi k **40.680 (61,4%)**. Tích luỹ **361.440 / 463.680 = 78,0%** toàn lưới.
  - ✅ **Không có dòng `[summarise] BỎ TRÙNG`** ⇒ `--resume` sạch qua hai session liên tiếp kể từ bản vá `9c2f4e4`; lỗi trùng khoá coi như đã đóng.
  - **Thông lượng:** 361.440 − 280.800 = **80.640 ô trong 37.800 s ⇒ 0,469 s/ô**. Chuỗi 4 session: **0,458 · 0,469 · 0,461 · 0,469 s/ô** (biên độ 2,4%) trên 4 vCPU — chi phí/ô ổn định tới mức có thể dùng để lập kế hoạch chắc chắn.
  - ⛔ Vẫn **PARTIAL** (78,0%) — chưa dòng provenance, chưa vào Bảng III.
  - 📐 **Ước lượng:** còn 4 × 25.560 = **102.240 ô ≈ 13,3 h** > ngân sách 10,5 h/session ⇒ **cần 2 session nữa**: session 6 chạy hết ngân sách (~80.640 ô), session 7 chỉ còn ~21.600 ô ≈ **2,8 h** là đóng lưới.
- **2026-07-20** · `@adf0882` · `scripts/audit_e2.py` (MỚI — cổng kiểm chỉ-đọc, vận hành CLAUDE.md §8) chạy trên `results/main/raw.csv` của session 5 (n=368, **k∈{2,3,4} đã đủ lưới**; k∈{5,6,8,10} còn dở nên KHÔNG nằm trong kết luận dưới đây).
  - **A2 leakage-adjacent PASS:** 0 dòng lặp / 860.384 dòng. **A4 PASS:** `split_unit = patient`, 5 test-fold rời nhau, hợp lại đúng cohort 368 ca.
  - **A3 FAIL (đã biết, sẽ tự khỏi):** `summary.csv` trong gói này là bản sinh bằng code CŨ ⇒ `include_zero_bg` vẫn có `True`/`False`, **504 nhóm có `n_patients = 77` thay vì 368**. Xác nhận đúng chẩn đoán ngày 19/07 và xác nhận cổng kiểm bắt được lỗi này. Sẽ sạch khi `summarise()` chạy lại dưới `@9c2f4e4`.
  - 🔴 **B1 — CHỐT AN TOÀN P2 NỔ (kết quả, KHÔNG phải bug).** Ngưỡng preregister `hit_rate ≥ 0,99 cho mọi thuật toán ở mọi k` bị bác bỏ **toàn diện: 27/27 tổ hợp (k, method) đều < 0,99**; thấp nhất 0,0008. Trích: k=4 `random` 0,0008 · k=4 `GOA` 0,0211 · k=4 `GA` 0,0503 · k=4 `QIGOA` 0,2101 · k=3 `QIGOA` 0,5053 · k=2 `GOA` 0,5281. Suy giảm đơn điệu theo k — **đúng hiện tượng Hammouche, Diaf & Siarry (EAAI 2010) đã in cho ACO/SA ở k>2**, nay tái lập trên 9 thuật toán, n=368, GT lâm sàng. ⇒ Rơi vào **nhánh 2 của LUẬN ĐỀ DUY NHẤT** (CLAUDE.md §1): metaheuristic **KHÔNG** đạt tối ưu ⇒ cả một thập kỷ engineering đang đóng một gap mà ta chứng minh được là không chiếu xuống lâm sàng. Luận đề **không bị tổn hại**; chỉ P2 dạng "mọi thuật toán đều đạt tối ưu ⇒ optimizer là đồ trang trí" phải viết lại. **CẤM hạ ngưỡng cho khớp số (HARKing).**
  - 🔴 **B2 — CHỐT AN TOÀN P4 NỔ trên WT/FLAIR (kết quả, KHÔNG phải bug).** `oracle_levelset = 0,8532`; decode `morph` tốt nhất = **0,8672** (k=3, MPA); **9/27 cấu hình morph VƯỢT trần**. Tái lập phát hiện screening 17/07 ở quy mô n=368 ⇒ oracle cường độ **KHÔNG phải trần** của pipeline thật vì hình thái học bơm thêm thông tin không gian. Trên ET/T1ce thì ngược lại: trần 0,6351, morph tốt nhất chỉ 0,0625 ⇒ **không vượt**. ⇒ Mọi câu dạng *"we establish the ceiling"* bị xoá (vốn đã bị cấm bởi François & Tinarrage, JMIV 2026); P4 phải viết thành **trần CÓ ĐIỀU KIỆN trên lớp phương pháp chỉ-cường-độ**, và sự vượt trần của `morph` trở thành **bằng chứng dương** cho luận đề "decoding chi phối, optimizer là đồ trang trí".
  - ⚠️ **Phạm vi:** kết luận B1/B2 hiện chỉ dựa trên k∈{2,3,4}. **Phải chạy lại audit khi đủ 7 k** trước khi đưa vào bản thảo.
- **2026-07-21** · `@adf0882` · Kaggle notebook `hlongg28/qigoa-reality-check-e2-main-grid` v13 (CPU, ~9h13) · **E2 SESSION 6 — `--k-subset 5,6,8,10 --resume` — 🎉 LƯỚI CHÍNH ĐẦY ĐỦ.** Cell R restore đúng `results_20260720_1749.tgz` → `raw.csv` **1.525.732 dòng**. Cell 6: **`[E2] stage k=5,6,8,10 XONG TRON (rc=0) trong 552.7 phut`** — kết thúc tự nhiên, KHÔNG chạm ngân sách 10,5h (nhanh hơn dự báo ~13,3h vì phần đầu k đã có sẵn nên `--resume` bỏ qua). Gói `results_20260721_0419.tgz`.
  - **Cell 7 — TẤT CẢ 7 k = 66.240 (100,0%) XONG:** k=2·3·4·5·6·8·10 đều đủ. **`De xuat K_SUBSET ke tiep: (HET - E2 DAY DU LUOI)`**. Tổng **463.680 ô metaheuristic** đã chạy trọn qua 6 session (2026-07-18 → 07-21).
  - **Thông lượng session này:** 463.680 − 361.440 = **102.240 ô trong 33.162 s ⇒ 0,324 s/ô** — nhanh hơn hẳn chuỗi 0,458/0,469/0,461/0,469. Nghi ngờ Kaggle cấp >4 vCPU session này (chưa xác nhận số core từ log — cần đọc dòng "chạy song song N tiến trình" khi tải gói về).
  - ⛔⛔ **VẪN CHƯA vào Bảng III.** Lưới đầy đủ mới là điều kiện CẦN, chưa ĐỦ. Trước khi bất kỳ số nào rời `results/`: (1) tải `results_20260721_0419.tgz` về local; (2) chạy `scripts/audit_e2.py` trên bộ ĐẦY ĐỦ 7 k — A1–A4 phải PASS, **đặc biệt A3 `summary.csv` sinh lại phải cho n_patients=368 mọi nhóm**; (3) `scripts/run_stats.py`; (4) viết dòng provenance. Chỉ khi đó số mới bỏ nhãn PLACEHOLDER (IRON RULE 3).
- **2026-07-21** · `@412869c` · Kaggle notebook v14 (CPU) · **E2 SESSION 7 — RESUME-ONLY trên lưới ĐẦY ĐỦ, sinh lại `summary.csv` dưới code đã vá.** Restore `results_20260721_0419.tgz` → `raw.csv` **1.943.780 dòng** (lưới đầy đủ). Cell 6 `XONG TRON (rc=0) trong 50.0 phut` (chỉ duyệt resume + `summarise()`, không tính lại). Cả 7 k = 66.240 = 100,0%, `(HET - E2 DAY DU LUOI)`. **Không có dòng `[summarise] BỎ TRÙNG`** ⇒ `summary.csv` mới sinh dưới `@412869c` (gồm vá `9c2f4e4`). Gói `results_20260721_0923.tgz`.
  - **Mục đích run này:** thay `summary.csv` bản hỏng (nhóm n=77 do code cũ) bằng bản sạch. Chưa xác nhận được `n_patients=368` từ log — **phải chạy `scripts/audit_e2.py` A3 trên file local sau khi tải về**.
  - ⛔ Số VẪN mang nhãn `[PLACEHOLDER]` cho tới khi: tải `.tgz` local → `audit_e2.py` (A1–A4 PASS) → `run_stats.py` → kiểm lại B1/B2 trên đủ 7 k → viết provenance. (IRON RULE 3.)

---
## E2 LƯỚI CHÍNH — DÒNG PROVENANCE (số hết nhãn PLACEHOLDER kể từ 2026-07-21)

- **Nguồn số:** `results/main/{raw,summary}.csv` (n=368, 5 seed, 2 target, 2 bg, 7 k, 9 metaheuristic + DP-exact + 5 classical, 4 decode-rule) ← `scripts/run_main_grid.py --config configs/exp_main.yaml @9c2f4e4`, chạy trọn qua 6 session Kaggle (2026-07-18 → 07-21), gói cuối `results_20260721_0923.tgz`.
- **Cổng kiểm:** `scripts/audit_e2.py @1825ce7` → **A1–A4 (toàn vẹn) PASS** trên đủ 7 k: 0 dòng lặp / 1.943.776; summary sạch, **1.116/1.116 nhóm có n_patients=368**; leakage PASS (split cấp bệnh nhân, 5 fold rời nhau = cohort 368).
- **Thống kê:** `results/stats/{pairwise,tost,cd,p3_delta,p2c_decoupling}.csv` ← `scripts/run_stats.py --config configs/exp_main.yaml @c9a7239` (352,7s, bootstrap n=10.000, đơn vị = bệnh nhân). *Family A (vs U-Net) HOÃN — cần `results/unet/raw.csv` (GPU, ngoài lô này).*
  - **Bảng III** ← `results/main/summary.csv` + `results/stats/pairwise.csv` + `tost.csv`.
  - **Hình 2 (CD)** ← `results/stats/cd.csv`. **Hình 3 (Goodhart P3)** ← `results/stats/p3_delta.csv`.

## E2 — PHÁT HIỆN CHÍNH (số THẬT, n=368; đọc trước khi viết Results)

- 🟢🟢 **LUẬN ĐỀ DUY NHẤT ĐƯỢC XÁC NHẬN — cả hai nhánh chỉ cùng một hướng.**
  - **Nhánh "không đạt tối ưu" (B1/P2):** hit_rate ≥ 0,99 bị bác bỏ **63/63 tổ hợp (k,method)**; ở k∈{6,8,10} nhiều thuật toán (GA, GOA, random) hit_rate = **0,0000 tuyệt đối**. Metaheuristic **KHÔNG** đạt tối ưu Kapur, càng nhiều ngưỡng càng thua — khớp Hammouche 2010.
  - **NHƯNG (C-equivalence/TOST):** trên Dice lâm sàng, **median_diff = 0,0000 ở CẢ 36 so sánh** metaheuristic vs DP-exact (tối ưu toàn cục thật); mean_diff bó trong ±0,0042; **TOST δ=0,05 tương đương 100%**, SESOI đủ để tương đương chỉ **≤ 0,7%**.
  - ⇒ **Khoảng cách tối ưu KHÔNG chiếu xuống mask lâm sàng.** Thuật toán trượt tối ưu hàm mục tiêu tới mức hit_rate=0, mà Dice vẫn *bằng* nghiệm tối ưu chính xác. Đây đúng là LUẬN ĐỀ DUY NHẤT (CLAUDE.md §1), xác nhận ở quy mô công bố.
- 🔴 **P2c (dự đoán "rho ≈ 0" KHÔNG được ủng hộ — báo cáo trung thực, không cứu):** Spearman fitness–Dice = **0,30–0,77** (trung vị ~0,56–0,60), dương vừa, **giảm dần theo k**. Fitness KHÔNG "tách rời hoàn toàn" khỏi Dice như bản phác dự đoán; nó mang tín hiệu yếu-vừa. Luận đề chính KHÔNG dựa vào P2c nên không bị tổn hại, nhưng **mọi câu "fitness hoàn toàn không dự báo Dice" phải bỏ**; thay bằng "tương quan dương vừa, suy yếu khi k tăng".
- 🔴 **P4 (B2):** trần oracle CÓ ĐIỀU KIỆN theo modality. WT/FLAIR: decode `morph` 0,8672 **vượt** oracle_levelset 0,8532 (9 cấu hình, k∈{2,3}). ET/T1ce: morph tốt nhất 0,0883 ≪ trần 0,6351, **không vượt**. ⇒ CẤM "we establish the ceiling"; morph phá trần WT thành **bằng chứng dương** cho "decoding chi phối".
- ⚠️ **P3 (Goodhart, `p3_delta.csv`):** hỗn hợp — WT/FLAIR primary success=True (Dice đổi theo k, median_delta 0,126), ET/T1ce success=False. **CHƯA diễn giải vội** — cần đọc kỹ cả 8 dòng + đối chiếu prereg trước khi viết Hình 3.
- **2026-07-21** · ❌→🔧 **E4 U-Net run #1–2 FAIL (không mất số nào — chưa train ô nào).** Run #1: Internet OFF ⇒ Cell 1 `git clone` chết (`Could not resolve host: github.com`). Run #2 (Internet ON): Kaggle cấp **GPU P100 (sm_60)**, mà **torch 2.10+cu128** trên image Kaggle chỉ hỗ trợ sm_7.0–12.0 ⇒ `CUDA error: no kernel image is available` sau ~43 phút chuẩn bị dữ liệu. `torch.cuda.is_available()=True` nên GPU-check cũ lọt. **Fix:** đổi Accelerator sang **GPU T4 x2** (sm_75, tương thích). Đã vá `gen_unet_nb.py` Cell 2: chạy 1 kernel CUDA thật ⇒ chết trong 1 giây thay vì 43 phút nếu GPU không tương thích. (Chưa push lại notebook lên Kaggle — tránh gỡ input; user đổi dropdown T4 + Run là đủ.)

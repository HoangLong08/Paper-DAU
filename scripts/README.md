# `scripts/` — entrypoint chạy được (MODULE G)

Mỗi script tái lập **ĐÚNG MỘT** bảng/hình, đọc **một** `configs/*.yaml`, ghi vào
`results/<exp>/`, và luôn ghi `run-manifest.json`. **Không manifest = run không tồn tại
với paper** (CLAUDE.md §5.2). Số liệu chảy một chiều:

```
configs/  →  scripts/  →  results/  →  paper/        # KHÔNG BAO GIỜ gõ số tay
```

Cờ chung cho mọi script: `--config <yaml>` (bắt buộc) · `--resume` (bỏ qua ô đã có) ·
`--output <dir>` (ghi đè `output_dir`).

---

## 🔴 THỨ TỰ CHẠY — BẮT BUỘC (prereg §6/A10)

> **KHÔNG CHẠY E2 TRƯỚC.** Kế hoạch cũ chi **~35/40 giờ** cho các thí nghiệm có **xác
> suất bất ngờ ≈ 0** (E2 chỉ fail nếu code có bug; *"U-Net thắng thresholding"* đã biết từ
> 2015) và xếp **cả bốn câu hỏi thật sự bất định** vào mục "làm sau". **Đó là dấu vân tay
> của confirmation bias — trong một bài đi tố cáo người khác confirmation bias.**

### Cổng 0 — đọc toàn văn (0 compute, trước khi chạy bất cứ gì)

Mousavirad (KBS 2023) · François & Tinarrage (JMIV 2026) · Hegazy & Gabr (arXiv:2605.27132
**và** 2605.27287) · Menotti (CIARP 2015) · Hammouche (EAAI 2010) · Al-Najdawi (Sci Rep
2025). **Không chạy E2 trước khi cả sáu đã đọc và có đoạn định vị viết sẵn.**

### Bước 1 — SMOKE (local, < 60 s, [PLACEHOLDER])

```bash
python scripts/run_exact_check.py --config configs/exp_smoke.yaml   # ~35 s
python scripts/run_main_grid.py   --config configs/exp_smoke.yaml   # ~23 s
python scripts/run_ablation.py    --config configs/exp_smoke.yaml   # ~14 s
python scripts/run_ceiling.py     --config configs/exp_smoke.yaml   # ~6 s
python scripts/run_unet.py        --config configs/exp_smoke.yaml   # ~6 s (CPU)
python scripts/run_external.py    --config configs/exp_smoke.yaml   # ~10 s
python scripts/run_stats.py       --config configs/exp_smoke.yaml   # ~7 s
python scripts/build_tables.py    --config configs/exp_smoke.yaml   # ~1 s
python scripts/build_figures.py   --config configs/exp_smoke.yaml   # ~3 s
```

Thời gian trên là **số đo thật** (local CPU, 16/07/2026), tổng chuỗi **~105 s**; hai script
bắt buộc (`run_exact_check`, `run_main_grid`) chạy **< 60 s**. Cả 9 script exit 0.

Bắt lỗi ở local rẻ hơn bắt lỗi sau 8 tiếng chạy trên Kaggle. **Số synthetic không bao giờ
là kết quả** — script tự dán `[PLACEHOLDER]` vào banner CSV, cột `placeholder`, README và
mặt hình.

### Bước 2 — E1: CỔNG CỨNG trên dữ liệu THẬT

```bash
python scripts/run_exact_check.py --config configs/exp_main.yaml    # ~10–20 phút CPU
```

PASS ⇒ exit 0. FAIL ⇒ in **"DỪNG TOÀN BỘ"** + exit 1. **Mọi kết luận về P2 dựng trên bộ
giải này.** Nếu fail: bước debug ĐẦU TIÊN = **audit quy ước** (`0log0` · lớp rỗng · ngưỡng
trùng · **có tính nền cường-độ-0 hay không**), **KHÔNG** phải sửa DP (A5b).

Cổng phụ nên chạy cùng: `pytest tests/` — `test_exact_dp` + `test_nfe_budget` fail ⇒
không được chạy lưới.

### Bước 3 — TUẦN 1: BỐN THÍ NGHIỆM RỦI RO (~10 h + 1 tuần khảo sát)

Đây là bốn câu hỏi mà **kết quả có thể giết bài**. Chạy trước, khi vé còn rẻ.

| # | Câu hỏi quyết định | Chạy bằng | Compute |
|---|---|---|---|
| 1 | **Bảng I** — P1 có mục tiêu, hay là strawman? | *khảo sát TAY*: search string, PRISMA-lite, **2 coder, Cohen's κ**. Không có script — và đó là lý do nó dễ bị hoãn | **0** |
| 2 | **P5/bậc 5** — bài có đóng góp dương không? | `run_ceiling.py --config configs/exp_ceiling.yaml` (nested CV, A3) | ~1 h |
| 3 | **P3 theo TỪNG decoding rule** — "metric sai" hay chỉ "decoder sai"? | `run_main_grid.py` (lưới rút gọn) → `run_stats.py` | ~1 h |
| 4 | **`morph` vs `oracle_interval`** — morph vượt oracle ⇒ **P4 tự bác bỏ** | `run_main_grid.py` + `run_ceiling.py` | ~1 h |

> **Nếu cả bốn sống sót → khi đó mới đáng chi 20 giờ cho E2. Nếu một trong bốn chết → đã
> tiết kiệm 8 tuần.**

### Bước 4 — E2 và phần còn lại

```bash
python scripts/run_main_grid.py --config configs/exp_main.yaml     --resume   # ~20 h CPU
python scripts/run_ablation.py  --config configs/exp_ablation.yaml --resume   # ~6 h
python scripts/run_ceiling.py   --config configs/exp_ceiling.yaml  --resume   # ~2 h
python scripts/run_unet.py      --config configs/exp_unet.yaml     --resume   # ~2 h GPU
python scripts/run_external.py  --config configs/exp_external.yaml --resume   # ~8 h
python scripts/run_stats.py     --config configs/exp_main.yaml                # E6
python scripts/build_tables.py  --config configs/exp_main.yaml
python scripts/build_figures.py --config configs/exp_main.yaml
```

E5 (metric đầy đủ) không có script riêng: Dice/HD95/NSD/#CC/empty-mask + PSNR/SSIM được
tính **ngay trong** E2/E3/E4/E7.

---

## Kaggle (§5)

Session ≤ 12 h · GPU 30 h/tuần · `/kaggle/input/` read-only · `/kaggle/working/` mất khi
hết session.

1. **Chia stage.** E2 (~20 h) không chạy trong một session ⇒ chia theo `k` (sửa `k_list`
   trong config, 2–3 giá trị/session), ghi CSV riêng, `--resume` merge sau.
2. **Cache histogram** `.npy` (`cache_dir`) — phần chậm nhất mà lại tất định.
3. **Checkpoint sau MỖI ô** `(image, k, algo, seed)` — CSV flush ngay từng dòng.
4. **`run-manifest.json` cho MỖI session** (git commit · config hash · seed · lib versions).

`data.root_kaggle` được thử **trước**, rồi mới tới `data.root_local` — cùng một config
chạy được ở cả hai nơi, không sửa code.

---

## Quy ước dữ liệu trong `results/*/raw.csv`

| Cột | Ý nghĩa |
|---|---|
| `k = -1` · `seed = -1` · `include_zero_bg = na` | **không áp dụng** (baseline cổ điển không có k; DP-exact tất định) |
| `method_class` | **A** unsupervised per-image · **B** CÓ HỌC ⇒ **chỉ out-of-fold** · **C** **uses test-time ground truth** (oracle = cận trên **không đạt được**, KHÔNG phải phương pháp) — A3 |
| `decode_horn` | `1-band` (band-selection) · `2-labelmap` (segmenter hạ nguồn) · `native` — hai sừng của thế lưỡng nan A1 |
| `mask_hash` | SHA-256 của mask đã packbits ⇒ **MASK-IDENTITY RATE** (headline A0) |
| `placeholder = 1` | số sinh từ phantom synthetic ⇒ **KHÔNG BAO GIỜ** vào bản thảo |

Đọc CSV bằng `_common.read_results_csv` (nó bỏ qua banner `#` ở đầu file).

---

## Interface gaps — lệch giữa MODULE G và `src/` (báo cáo, KHÔNG tự sửa `src/`)

1. **`PSO+memetic` không tồn tại trong `src/`.** `src.solvers.metaheuristics.pso.PSO`
   không có cờ hp `memetic` (chỉ `QIGOA` có: `quantum`/`obl`/`levy`/`memetic`), trong khi
   E3 đòi biến thể `PSO+memetic`. MODULE G không sửa `src/` ⇒ biến thể được dựng ở tầng
   script: `scripts/_common.py::PSOMemetic` kế thừa `PSO` và **lặp lại vòng lặp PSO
   nguyên văn** + đúng một lời gọi memetic (probe ±1 mỗi chiều, giống `QIGOA._memetic`,
   mọi lượt thử qua `self.evaluate` ⇒ đếm NFE).
   **Rủi ro:** code trùng lặp có thể trôi khỏi `src/pso.py`.
   **Phòng thủ:** `run_ablation.py::check_pso_memetic_parity` assert
   `PSO+memetic(memetic=False) ≡ PSO` ở cùng seed **trước mỗi lần chạy E3**.
   **Sửa sạch (đề xuất cho chủ MODULE C):** thêm cờ `memetic` vào `PSO._search` trong
   `src/`, rồi xoá `PSOMemetic` khỏi tầng script.

2. **`sklearn` từ chối `random_state=-1`.** `decode_labelmap(..., seed=...)` chuyển thẳng
   seed cho `KMeans`; sentinel `seed = -1` của DP-exact (tất định, không có seed) làm
   sklearn ném `InvalidParameterError`. MODULE G kẹp `max(0, seed)` trong
   `_common.decode_rows` — `src/` không cần sửa.

3. **`solve_bruteforce` là nút thắt của E1**, không phải DP: ~1,2 s/ảnh ở k=3 trên phantom
   (~113 ngưỡng ứng viên) và sẽ **chậm hơn ~10×** trên histogram BraTS đầy đủ (~254 ứng
   viên). Vì thế `exp_smoke.yaml` giới hạn `exact_check.include_zero_bg: [true]` để giữ
   smoke < 60 s; **cổng thật (`exp_main.yaml`) chạy CẢ HAI biến thể** (A5c).

---

## Ba điều tuyệt đối không làm

1. **Không tái dùng bất kỳ con số nào từ commit `c4fe108`** (bug NFE 13,4% · GOA hit-rate
   0% · metric tự chế · pseudo-replication). Nó là **bằng chứng chẩn đoán**, không phải
   nguồn số liệu.
2. **Không đụng Bảng I trong `Huong-tiep-can-paper-Long.pdf`** — đó là **số bịa**.
3. **Không claim "quantum advantage"** ở bất kỳ đâu. QIEA = một EDA (Platel et al., IEEE
   TEVC 2009). Định vị đúng: *"an EDA-style probabilistic update rule"*.

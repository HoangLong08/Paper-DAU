# Kế hoạch triển khai paper — QIGOA Reality-Check

**Ngày:** 13/07/2026 · **Nhánh:** `qigoa-reframe` · **Trạng thái:** ⏸️ chờ thầy duyệt reframe

> **Tài liệu này trả lời đúng một câu hỏi:** *làm thế nào để biến 4 mệnh đề trong [preregistration.md](preregistration.md) thành một bản thảo nộp được, mà mỗi con số trong bài đều truy được về một dòng CSV và một commit.*
>
> Ba tài liệu đi cùng nhau, đọc theo thứ tự:
> 1. [trinh-bay-voi-thay.md](trinh-bay-voi-thay.md) — *vì sao* đổi hướng (thuyết phục thầy)
> 2. [preregistration.md](preregistration.md) — *cái gì* được tuyên bố (khoá trước khi chạy)
> 3. **`ke-hoach-trien-khai.md`** (file này) — *làm thế nào* (thi công)

---

## 0. Nguyên tắc thi công

Bốn nguyên tắc chi phối mọi quyết định kỹ thuật dưới đây. Khi phân vân, quay về đây.

1. **Số liệu chảy một chiều: `configs/` → `scripts/` → `results/` → `paper/`.** Không bao giờ gõ số bằng tay vào bản thảo. Bảng và hình trong `paper/` được **sinh** từ `results/` bằng script build. Nếu một số trong bài không truy được về một ô CSV, nó là `[PLACEHOLDER]`.

2. **Cái gì có thể kiểm bằng `assert` thì không kiểm bằng niềm tin.** Ngân sách NFE bằng nhau — assert. DP đúng — unit test đối chiếu vét cạn. Suy biến P1 — test tự động chạy lại trên mỗi lô kết quả mới. Ba lỗi của lô cũ đều là loại lỗi mà **một dòng `assert` sẽ chặn được**.

3. **Thí nghiệm được thiết kế để bác bỏ chính mình.** Mỗi mệnh đề P1–P4 có một thí nghiệm mà *nếu mệnh đề sai, thí nghiệm sẽ cho thấy điều đó*. Không thiết kế thí nghiệm để minh hoạ.

4. **Kaggle là môi trường chạy, không phải môi trường phát triển.** Code phải chạy được ở local với dữ liệu synthetic (smoke test) trước khi đẩy lên Kaggle. Bắt lỗi ở local rẻ hơn bắt lỗi sau 8 tiếng chạy.

---

## 1. Kiến trúc repo & hợp đồng của từng module

```
configs/
  exp_smoke.yaml          # dữ liệu synthetic, k=2..3, 1 seed — chạy < 60s, dùng ở local
  exp_main.yaml           # E2: lưới chính, equal-NFE
  exp_ablation.yaml       # E3: QIGOA full / −quantum / −memetic / −OBL / −Lévy / PSO+memetic
  exp_ceiling.yaml        # E4: oracle scans + baseline cổ điển
  exp_unet.yaml           # E4: 2D U-Net (GPU)
  exp_external.yaml       # E7: ngoại kiểm LGG

src/
  data/
    brats_loader.py       # BraTS2020 → 1 lát/1 BN, n=150
    lgg_loader.py         # LGG (Buda et al.) → ngoại kiểm
    synthetic.py          # phantom cho smoke test
  fitness/
    kapur.py              # + interval_entropy(lo, hi) → nền của DP
    otsu.py               # + interval_variance(lo, hi)
  solvers/
    exact_dp.py           # O(k·L²) — nghiệm tối ưu TOÀN CỤC
    exhaustive.py         # oracle 1-ngưỡng (254) & 1-khoảng (32.385) → TRẦN
    random_search.py
    metaheuristics/
      base.py             # ★ HARD NFE BUDGET + assert
      ga.py pso.py goa.py gwo.py woa.py mpa.py qigoa.py
  decode/
    decoding.py           # 4 quy tắc + oracle ← nguồn của P1
  eval/
    metrics.py            # Dice, IoU, HD95, NSD (MedPy/skimage) + PSNR, SSIM (skimage)
    stats.py              # Wilcoxon+rank-biserial, Friedman+Nemenyi, TOST, Bayesian ROPE
  baselines/
    classical.py          # Otsu, Li, Triangle, k-means, GMM
    unet2d.py             # cùng input: 1 lát FLAIR
  manifest.py             # sinh run-manifest.json

scripts/
  run_exact_check.py      # E1  → results/exact/
  run_main_grid.py        # E2  → results/main/
  run_ablation.py         # E3  → results/ablation/
  run_ceiling.py          # E4  → results/ceiling/
  run_unet.py             # E4  → results/unet/
  run_external.py         # E7  → results/external/
  run_stats.py            # E6  → results/stats/
  build_tables.py         # results/ → paper/tables/*.tex
  build_figures.py        # results/ → paper/figures/*.pdf

tests/
  test_exact_dp.py        # ★ bit-exact vs vét cạn, k=2,3, ≥20 ảnh
  test_nfe_budget.py      # ★ mọi thuật toán tiêu thụ ĐÚNG cùng NFE (±0)
  test_degeneracy.py      # ★ P1: std(Dice) = 0 trên 100% nhóm
  test_metrics.py         # đối chiếu Dice/HD95 với ví dụ đã biết

results/                  # script sinh — KHÔNG sửa tay
paper/                    # bảng & hình PULL từ results/
docs/                     # preregistration.md · RESULTS.md · file này
```

### Hợp đồng của các module then chốt

#### `src/solvers/metaheuristics/base.py` — **hard NFE budget**

Đây là module quan trọng nhất về mặt liêm chính. Lô cũ chết vì nó.

```python
class BudgetExhausted(Exception):
    """Ném ra khi hết ngân sách. Thuật toán PHẢI dừng, trả best-so-far."""

class Optimizer:
    def __init__(self, budget: int, seed: int, ...):
        self.budget = budget      # ngân sách NFE TUYỆT ĐỐI
        self._used = 0

    def evaluate(self, x) -> float:
        """CỔNG DUY NHẤT tới hàm mục tiêu. Không thuật toán nào được
        gọi objective() trực tiếp — mọi lượt đánh giá phải qua đây."""
        if self._used >= self.budget:
            raise BudgetExhausted
        self._used += 1
        return self.objective(x)

    def run(self):
        try:
            self._search()
        except BudgetExhausted:
            pass
        assert self._used == self.budget, \
            f"{self.name} dùng {self._used}/{self.budget} NFE — LƯỚI VÔ HIỆU"
        return self.best_x, self.best_f, self._used
```

**Ba hệ quả bắt buộc:**
- Memetic refinement, OBL init, Lévy flight của QIGOA gọi `self.evaluate()` ⇒ **đếm vào ngân sách**. Đây chính là chỗ lô cũ ăn gian 13,4%.
- Mọi thuật toán phải **tiêu hết** ngân sách (chạy tới khi `BudgetExhausted`), không dừng sớm — nếu không, so sánh vẫn lệch theo chiều ngược lại.
- `tests/test_nfe_budget.py` fail ⇒ **không được chạy lưới**. Đây là cổng cứng.

#### `src/solvers/exact_dp.py` — nghiệm tối ưu toàn cục

Kapur entropy **cộng tính theo khoảng**: tổng entropy = Σ (hàm của cặp `(lo, hi)`). Do đó quy hoạch động cho nghiệm chính xác trong `O(k·L²)`.

```
J[j][t] = giá trị tối ưu khi dùng j ngưỡng và ngưỡng cuối tại t
J[j][t] = max_{t' < t} ( J[j-1][t'] + interval_entropy(t', t) )
```

> ⚠️ **KHÔNG claim đây là đóng góp của mình.** Cite ở Abstract: Luessi et al., *J. Electronic Imaging* 18(1):013004 (2009); **Merzban & Elbayoumi**, *Expert Systems with Applications* 116:299–309 (2019). Ta chỉ **dùng** nó làm reference optimum.

**Cổng cứng:** `tests/test_exact_dp.py` đối chiếu **bit-exact** với vét cạn tại k=2, k=3 trên ≥20 ảnh. Fail ⇒ dừng toàn bộ, vì mọi kết luận về P2 dựng trên nó.

> **Ghi chú trung thực:** Tsallis entropy **không** cộng tính (pseudo-additive) ⇒ DP **không áp dụng trực tiếp**. Nếu đưa Tsallis vào bài, phải nêu rõ và vét cạn k ≤ 3 để kiểm tra. **Khuyến nghị: bỏ Tsallis khỏi scope** — nó không thêm sức thuyết phục, chỉ thêm bề mặt bị tấn công.

#### `src/decode/decoding.py` — nguồn của P1, và là chỗ chống đòn "strawman"

Reviewer sẽ nói: *"Quy tắc decoding 'lớp sáng nhất' của các anh là strawman."* Cách diệt **không phải tranh cãi, mà là toán học**:

```python
RULES = {
  "brightest":   lambda seg: seg == seg.max(),           # quy tắc của văn liệu
  "upper_union": lambda seg, j: seg >= j,                # hợp các lớp trên
  "otsu_pick":   ...,                                     # chọn lớp bằng Otsu 2 tầng
  "morph":       ...,                                     # + hậu xử lý hình thái
}

def oracle_single(img, gt):   # vét cạn 254 ngưỡng → Dice tốt nhất có thể
def oracle_interval(img, gt): # vét cạn 32.385 cặp (lo,hi) → TRẦN TUYỆT ĐỐI
```

**Lập luận then chốt:** `oracle_interval` là trần đúng cho **MỌI** quy tắc chọn-một-dải-lớp — kể cả những quy tắc chưa ai nghĩ ra. Vì vậy kết luận về trần (P4) là **decoding-agnostic**. Đòn "strawman" bị vô hiệu bằng định nghĩa, không bằng tranh luận.

#### `src/eval/metrics.py` — không tự chế

Lô cũ dùng global-SSIM (không phải sliding-window của Wang et al.) và một FSIM tự thú trong docstring là *"not the full FSIM"*. **Một bài phê phán metric mà dùng metric tự chế thì tự sát** — reviewer mở code là xong.

| Metric | Nguồn | Vai trò trong bài |
|---|---|---|
| Dice, IoU | `skimage` / tự cài + test | **Kết quả** — metric quyết định |
| HD95, NSD | `MedPy` / `surface-distance` | **Kết quả** — theo *Metrics Reloaded* |
| PSNR, SSIM | **`skimage.metrics`** (không tự cài) | **Bằng chứng** — để chứng minh P3, không phải để khoe |
| FSIM | **BỎ** | Không có cài đặt chuẩn đáng tin; bỏ đi rẻ hơn bảo vệ |

---

## 2. Bảy thí nghiệm — đặc tả thi công

### E0 · Preregistration ✅ đã xong
`docs/preregistration.md` đã khoá. **Không chạy gì trước khi file này được commit.**

### E1 · Bộ giải chính xác + cổng kiểm
| | |
|---|---|
| **Script** | `scripts/run_exact_check.py` |
| **Input** | `configs/exp_smoke.yaml` + 20 ảnh BraTS thật |
| **Output** | `results/exact/dp_vs_bruteforce.csv` |
| **Compute** | < 30 phút CPU |
| **Cổng cứng** | DP khớp **bit-exact** với vét cạn tại k=2,3. Fail ⇒ **DỪNG TOÀN BỘ** |
| **Cho ra** | **Bảng II** (DP vs vét cạn: giá trị khớp tuyệt đối, thời gian chênh ~2 bậc) |

### E2 · Lưới chính, equal-NFE ★ xương sống
| | |
|---|---|
| **Script** | `scripts/run_main_grid.py --config configs/exp_main.yaml` |
| **Lưới** | 150 BN × k ∈ {2,3,4,5,6,8,10} × 11 phương pháp × 5 seed |
| **Phương pháp** | GA, PSO, GOA, GOA-fixed, GWO, WOA, MPA, QIGOA, random-search, DP-exact, Otsu/Li/k-means |
| **Ngân sách** | NFE **bằng nhau tuyệt đối** cho mọi metaheuristic (assert ±0) |
| **Output** | `results/main/raw.csv`, `results/main/summary.csv`, `run-manifest.json` |
| **Compute** | ~20 h wall (CPU, `joblib` 4 vCPU) → 2 phiên Kaggle 12 h |
| **Cho ra** | **Bảng III** (gap-to-optimum, hit-rate, NFE, runtime) · **Hình 2** (CD diagram) · **Hình 3** (Goodhart, trục kép) |

**Bẫy phải tránh:** GOA cũ có hit-rate 0% ở mọi k ≥ 3 — đó là **một con bug, không phải một baseline**. Chạy **cả hai** phiên bản (`GOA` hỏng và `GOA-fixed`), và trình bày như một *bài học phương pháp luận*: một baseline lỗi sinh ra "significance" giả trên cả 10 cấu hình.

### E3 · Ablation trên BraTS thật ★ trả lời trực diện đề bài của thầy
| | |
|---|---|
| **Script** | `scripts/run_ablation.py --config configs/exp_ablation.yaml` |
| **Biến thể** | `QIGOA-full` / `−quantum` / `−memetic` / `−OBL` / `−Lévy` / `PSO+memetic` |
| **Ràng buộc** | Cùng NFE, **cùng mọi hyperparameter khác** (khớp tới từng tham số — playbook thầy §4.1) |
| **Compute** | ~6 h |
| **Cho ra** | **Bảng IV** (ablation × fitness × Dice × HD95 × NFE) |

**Dự đoán khai báo trước** (đã ghi trong preregistration): thành phần quantum đóng góp ≈ 0 vào Dice — theo P1 nó *không thể* đóng góp gì ngoài việc dịch chuyển $t_k$. **Nếu dự đoán này sai** — quantum thực sự cải thiện Dice có ý nghĩa — thì đó là finding **dương**, và ta báo cáo nó như vậy. Đây là điểm mà bài tự đặt mình vào rủi ro.

Lô cũ **chỉ ablate trên ảnh phantom tổng hợp**, không phải BraTS — nên claim *"bỏ memetic thì QIGOA thua GA/PSO"* trong bản cũ **không có provenance**. Đây là lỗ hổng lớn nhất của bản cũ và E3 vá nó.

### E4 · Phân tích trần ★ hình đắt giá nhất của bài
| | |
|---|---|
| **Script** | `scripts/run_ceiling.py` + `scripts/run_unet.py` |
| **Compute** | ~2 h CPU (oracle) + ~2 h GPU (U-Net) |
| **Cho ra** | **Hình 4** — ceiling ladder (hình chủ đạo) |

Thang đo, tất cả trên **cùng một trục Dice, cùng một tập test**:

| Bậc | Phương pháp | Chi phí | Ý nghĩa |
|---|---|---|---|
| 1 | Random search (cùng NFE) | ~1,5 s | *Nếu ngang metaheuristic → đòn chí mạng* |
| 2 | 7 metaheuristic (equal-NFE) | 1–2,5 s | Cả dòng văn liệu ở đây |
| 3 | **DP — tối ưu toàn cục CHÍNH XÁC** | ~ms | Trần của *bài toán tối ưu* |
| 4 | Otsu / Li / k-means / GMM | ~ms | Baseline cổ điển |
| 5 | **Ngưỡng 1-tham-số học trên train** | ~0 | **← đóng góp DƯƠNG của bài** |
| 6 | Oracle 1-ngưỡng (vét cạn 254) | ~30 ms | Trần của decoding "lớp sáng nhất" |
| 7 | **Oracle 1-khoảng (vét cạn 32.385)** | ~30 s | **TRẦN của MỌI thresholding cường độ** |
| 8 | 2D U-Net, **cùng input** (1 lát FLAIR) | ~2 h GPU | Baseline DL **công bằng** |
| 9 | nnU-Net 3D đa mô thức | — | **Số trích từ văn liệu, KHÔNG chạy** |

**Bậc 5 là thứ biến bài từ "negative result" thành "bài đăng được".** Nếu một ngưỡng phân vị cố định đánh bại cả 7 metaheuristic — thì bài không còn nói *"các anh sai"*, nó nói *"chúng tôi thay cả họ phương pháp bằng một tham số"*.

> ### 🔴 SỬA BẮT BUỘC (14/07/2026) — bậc 5 hiện đang là LEAKAGE
> *"Hiệu chỉnh trên 10 ảnh train"* rồi so trên **cả 150 bệnh nhân** (gồm cả 10 ảnh đã fit) = **train-on-test**, nằm ngay trong **đóng góp dương của một bài tố cáo người khác so sánh không lành mạnh**. Đây là lỗi **DUY NHẤT có thể bị reject vì LIÊM CHÍNH**, không phải vì novelty — và reviewer nào cũng thấy trong 5 phút.
> ✅ **Sửa:** nested CV ở **cấp bệnh nhân** — fit `q*` trên outer-train fold, **đóng băng**, đánh giá out-of-fold. Công bố **5 giá trị `q*`** (ổn định giữa các fold ⇒ finding mạnh) + learning curve theo cỡ tập fit. Chuẩn hoá cường độ **per-image** (dùng thống kê toàn dataset = preprocessing leak). Chi tiết: [preregistration.md](preregistration.md) §6/A3.
> ⚠️ **Bậc 5 CHƯA ĐƯỢC PREREGISTER** — trong khi chính dòng này gọi nó là *"thứ biến bài từ negative result thành bài đăng được"*. **Preregister nó như P5 kèm fallback, và CHẠY NÓ Ở TUẦN 2** (~1 giờ CPU), không phải tuần 3. Đừng để thứ quyết định số phận bài là thứ cuối cùng ta biết.
> ⚠️ **Bỏ claim "nhanh hơn ~250 lần"** — artifact của vòng lặp Python, chưa ai đo. Đồng tiền chính = **NFE + độ phức tạp**.

**Về deep learning — đọc kỹ, đây là chỗ dễ chết:**
- ❌ **KHÔNG train nnU-Net.** 3D full-res × 5 fold = nhiều ngày GPU. Kaggle cho 30 GPU-h/tuần, session ≤ 12 h. Bất khả.
- ✅ **Train 2D U-Net trên ĐÚNG input đó** (1 lát FLAIR). Đây là so sánh *công bằng*, và nó vô hiệu hoá phản biện *"anh so 2D đơn-modality với 3D đa-modality"*.
- ✅ **Trích số nnU-Net từ văn liệu** (Isensee et al., BraTS 2020, arXiv:2011.00848 — WT Dice 0,9124 val / 0,8895 test), **dán nhãn rõ ràng**: *"reference from literature, not run by us, different input protocol"*. Dùng làm **context**, không phải baseline so trực tiếp.

### E5 · Metric đầy đủ
Chạy `src/eval/metrics.py` trên toàn bộ output của E2/E3/E4. Thêm **HD95, NSD**. Giữ PSNR/SSIM **nguyên vẹn** — chúng là **bằng chứng cho P3**, không phải kết quả.

**Dự đoán:** HD95 sẽ tệ thảm hại (thresholding sinh false-positive rải khắp não) → thêm một nhát dao cho P4.

### E6 · Thống kê
| | |
|---|---|
| **Script** | `scripts/run_stats.py` |
| **Đơn vị** | **BỆNH NHÂN** (n=150), không phải lát ảnh ← lô cũ làm sai |

| Mục | Phương pháp | Vì sao bắt buộc |
|---|---|---|
| So sánh cặp | Wilcoxon + **rank-biserial** (effect size) | p-value không nói được độ lớn |
| Omnibus | Friedman + Nemenyi + **CD diagram** | Demšar 2006 |
| **Khẳng định "không khác nhau"** | **TOST**, SESOI = **0,01 Dice** (khai báo trước) | *"p > 0,05" KHÔNG đủ.* Đây là cách hợp pháp duy nhất |
| Bổ trợ | **Bayesian signed-rank + ROPE [−0,01, +0,01]** | Cho phát biểu `P(tương đương) = 0,9x` |

Không có TOST + ROPE, reviewer đánh đúng một câu: *"absence of evidence is not evidence of absence"* — và bài sập.

### E7 · Ngoại kiểm
| | |
|---|---|
| **Dataset** | LGG-MRI Segmentation (Buda et al.) — Kaggle `mateuszbuda/lgg-mri-segmentation` |
| **Vì sao** | Khác cơ sở, khác máy chụp, khác grade khối u → chống đòn *"một dataset"* |
| **Compute** | ~8 h (lưới rút gọn) |
| **Trình bày** | **Replication table** lặp lại Bảng III–IV, không tách section riêng |

---

## 3. Bảng provenance — số → script → commit

Đây là hợp đồng vận hành **IRON RULE 1 & 3**. Mỗi dòng sẽ được ghi vào `docs/RESULTS.md` khi thí nghiệm chạy xong. **Số nào chưa có dòng provenance = `[PLACEHOLDER]`, không được vào bản thảo.**

| Bảng/Hình trong paper | ← Nguồn | ← Script | Trạng thái |
|---|---|---|---|
| **Bảng I** — trắc lượng thư mục (N bài không cite exact solution, không đo Dice) | thủ công + verify | *(khảo sát tay)* | ⬜ chưa làm |
| **Bảng II** — DP vs vét cạn | `results/exact/dp_vs_bruteforce.csv` | `run_exact_check.py` | ⬜ |
| **Bảng III** — gap-to-optimum, hit-rate, NFE, runtime | `results/main/summary.csv` | `run_main_grid.py` | ⬜ |
| **Bảng IV** — ablation QIGOA | `results/ablation/summary.csv` | `run_ablation.py` | ⬜ |
| **Bảng V** — phương pháp đề xuất vs 7 metaheuristic | `results/ceiling/summary.csv` | `run_ceiling.py` | ⬜ |
| **Hình 1** — sơ đồ pipeline + ngân sách | — | drawio-skill | ⬜ |
| **Hình 2** — Critical Difference diagram | `results/stats/cd.csv` | `run_stats.py` | ⬜ |
| **Hình 3** — Goodhart (trục kép: fitness/PSNR ↑ vs Dice/HD95 ↓ theo k) | `results/main/summary.csv` | `build_figures.py` | ⬜ |
| **Hình 4** — Ceiling ladder ★ | `results/ceiling/` + `results/unet/` | `build_figures.py` | ⬜ |

---

## 4. Cấu trúc bản thảo — section nào chứa gì

**Thứ tự viết ≠ thứ tự đọc.** Viết Section 3 (Degeneracy) và Section 8 (Ceiling) **trước** — chúng là linh hồn. Introduction viết **sau cùng**, khi đã biết bài thực sự nói gì.

| § | Nội dung | Bảng/Hình |
|---|---|---|
| 1 · Introduction | Dòng văn liệu QI/metaheuristic thresholding vẫn nở rộ. Nêu 4 mệnh đề falsifiable. Nói thẳng: đây là reality-check **có kèm phương pháp thay thế** | — |
| 2 · Related Work & the Citation Gap | Ba nhánh: (a) metaheuristic thresholding + nhánh quantum-inspired; (b) **lời giải chính xác đã tồn tại** (Luessi 2009; Merzban 2019); (c) chuẩn đánh giá segmentation (*Metrics Reloaded*, BraTS). **Chỉ ra nhánh (a) không cite nhánh (b) và không dùng nhánh (c)** | Bảng I |
| 3 · **The Degeneracy of the Objective** ★ | **Mệnh đề 1**: mask = f(≤2 ngưỡng), bất kể k. **Mệnh đề 2**: Kapur cộng tính ⇒ DP cho tối ưu toàn cục `O(k·L²)`. Chứng minh + xác nhận bit-exact | Bảng II |
| 4 · Experimental Protocol | 150 BN (1 lát/BN) + LGG ngoại kiểm; equal-NFE; Dice/HD95/NSD + PSNR/SSIM; Wilcoxon+rank-biserial, Friedman+CD, **TOST**, **Bayesian ROPE**. **Khai báo trước SESOI = 0,01 Dice** | Hình 1 |
| 5 · **R1 — There Is Nothing Left to Optimize** | Mọi metaheuristic — **kể cả random search** — đạt nghiệm DP. GOA hỏng, và "significance" của QIGOA sinh ra từ đó. ⚠️ Chi phí báo bằng **NFE + độ phức tạp**, không bằng wall-clock. ⚠️ **Hạ P2 xuống 2 đoạn setup** — Menotti 2015 + Hammouche 2010 + Merzban 2019 đã chiếm gần hết | Bảng III · Hình 2 |
| 6 · **R2 — The Metrics Are Anti-Correlated** | fitness/PSNR/SSIM ↑ theo k; Dice/HD95 ↓. Chọn k bằng PSNR → k=10; bằng Dice → k=4. **Thừa nhận thẳng**: trong *cùng* k thì ρ dương — và giải thích vì sao điều đó vẫn không cứu được gì | Hình 3 |
| 7 · **R3 — The Quantum Component Contributes Nothing** | Ablation trên dữ liệu thật, equal-NFE. TOST + Bayes: tương đương với PSO. Nền lý thuyết: QIEA ≡ EDA (Platel, IEEE TEVC 2009) | Bảng IV |
| 8 · **R4 — The Ceiling** ★ | Thang 9 bậc. Random ≈ metaheuristic ≈ DP; oracle-interval = trần; 2D U-Net cùng input vượt trần | Hình 4 |
| 9 · **A Better Baseline** (đóng góp dương — ⚠️ **ĐÃ VIẾT LẠI**) | **(1) Ceiling decomposition** (cường độ vs pixel) · **(2) công cụ chẩn đoán `O(L log L)`** tính trước trần của cả họ phương pháp · **(3) checklist giao thức + Bảng I trắc lượng**. ⛔ **DP KHÔNG còn là đóng góp** — Menotti et al. (CIARP 2015) đã in exact Kapur, `O((K−1)L²)`, <160 ms, **11 năm trước**; ta chỉ **dùng** nó làm reference optimum và cite ở Abstract | Bảng V · Hộp 1 |
| 10 · Threats to Validity | Tự liệt kê: decoding khác, modality khác, 2D vs 3D, Tsallis không DP được, cỡ mẫu | — |
| 11 · Conclusion | **KHÔNG** phải "metaheuristic vô dụng nói chung" — mà "**trên bài toán CỤ THỂ này**, chúng tối ưu một biến không quan trọng, trên một bài toán đã giải xong, đo bằng thước đo phản chỉ báo" | — |

**Giọng điệu (quyết định chiến lược):** phê phán **thực hành**, tuyệt đối **không nêu tên tác giả để chê**. Editor sẽ chọn reviewer từ chính cộng đồng này. Đóng khung xây dựng: *"benchmark + protocol + một công cụ tính trước trần"*.

> **Bốn quyết định đóng khung bắt buộc (14/07/2026):**
> 1. **Đổi tiêu đề** — bỏ *"Optimizing the Wrong Variable"* (đảm bảo một AE thù địch). Dùng tiêu đề benchmark, mô tả, trung tính.
> 2. **Abstract mở bằng ĐÓNG GÓP, không bằng CÁO BUỘC.** Cáo buộc xuất hiện ở câu 4–5, dạng **phát hiện thực nghiệm**, không phải phán xét.
> 3. **Bảng I (trắc lượng) xuống Supplementary** — nếu bảng ĐẦU TIÊN editor nhìn thấy là *"chúng tôi đếm N bài không cite X"*, bài bị phân loại là **meta-science** ngay tại đó và out-of-scope. Bảng I của bản thảo phải là **DP vs vét cạn** — một bảng toán học, không buộc tội ai.
> 4. **Cover letter xin reviewer đa chuyên môn** — ít nhất một người về **validation y sinh** (Metrics Reloaded) và một người về **tối ưu tổ hợp chính xác**, bên cạnh reviewer từ cộng đồng metaheuristic. Editor **có** honor loại yêu cầu này; nó biến panel từ 3-vs-0 thành 1-vs-2. Đây là đòn bẩy mạnh nhất mà bài có và hiện **chưa dùng**.

---

## 5. Chạy trên Kaggle

**Ràng buộc:** session ≤ 12 h; GPU 30 h/tuần; `/kaggle/input/` read-only; `/kaggle/working/` ghi được nhưng mất khi session hết hạn.

**Thiết kế resume-được — bắt buộc:**
1. **Chia stage.** E2 (~20 h) không chạy trong một session. Chia theo `k`: mỗi session chạy 2–3 giá trị k, ghi CSV riêng, merge sau.
2. **Cache đặc trưng.** Histogram của 150 ảnh tính một lần, lưu `.npy` → mọi run sau đọc từ cache. Đây là phần chậm nhất mà lại tất định.
3. **Checkpoint sau mỗi (image, k, algo, seed).** Nếu session chết, chạy lại chỉ tốn phần chưa xong.
4. **`run-manifest.json` cho MỖI session**: `{git_commit, config_hash, seeds, dataset_version, lib_versions, timestamp, output_paths}`. **Không có manifest = run không tồn tại với paper.**

**Smoke test trước mọi thứ:** `configs/exp_smoke.yaml` chạy toàn bộ pipeline trên dữ liệu synthetic trong < 60 s. Chạy ở **local**, trước khi đẩy lên Kaggle. Số synthetic **không bao giờ là kết quả** — luôn gắn `[PLACEHOLDER]`.

**Dữ liệu:**
- Chính: `awsaf49/brats20-dataset-training-validation`
- Ngoại kiểm: `mateuszbuda/lgg-mri-segmentation`
- ⚠️ Kaggle chỉ có **training split** (có ground truth). Test set thật giữ kín trên Synapse. ⇒ **Không được claim "SOTA trên BraTS leaderboard"**. Nêu rõ trong paper: tự chia theo bệnh nhân.

---

## 6. Definition of Done

### Một thí nghiệm "paper-ready" khi:
- [ ] Config-driven, **≥5 seed**, `run-manifest.json` đã ghi
- [ ] Split ở **mức bệnh nhân**, audit leakage pass
- [ ] **Assert NFE bằng nhau (±0)** pass
- [ ] Bộ metric **đầy đủ** (Dice, IoU, HD95, NSD + PSNR, SSIM) — không lọc metric đẹp
- [ ] Kiểm định thống kê + **effect size** — không chỉ p-value
- [ ] Dòng provenance đã thêm vào `docs/RESULTS.md`

### Một claim "paper-ready" khi:
- [ ] Đã **preregister** trước khi chạy ✅ (xong)
- [ ] Mọi số **truy được về script** — không còn `[PLACEHOLDER]` trong bản nộp
- [ ] Không overclaim; caveat về giới hạn method (quantum-inspired ≠ quantum advantage) có mặt
- [ ] Near-rival được **phân biệt**, không chỉ liệt kê

### Cổng kiểm cuối trước khi nộp (playbook thầy §9.2):
- [ ] **0** lỗi LaTeX · **0** Overfull hbox · **0** undefined ref/citation · **0** cảnh báo bibtex
- [ ] Mọi số trong prose/bảng/figure truy về CSV **tới từng chữ số**
- [ ] Grep bản thảo: **0** chữ "outperforms"/"superior" không có kiểm định đứng sau
- [ ] Grep bản thảo: **0** chữ "quantum advantage", "quantum speedup", "quantum parallelism"
- [ ] Figure sinh từ script, **đã nhìn tận mắt sau khi render**
- [ ] Code + seed public trên GitHub

---

## 7. Năm phản biện chí mạng — phòng thủ đã cài sẵn ở đâu

| Phản biện | Phòng thủ | Cài ở |
|---|---|---|
| **"Merzban 2019 làm rồi. Novelty đâu?"** ← nguy hiểm nhất | Cite ở **Abstract**, tuyên bố *"no novelty claimed for the exact algorithm"*. Họ dùng ảnh tự nhiên **không GT** ⇒ không thể thấy suy biến metric. Ta có: GT + P1 + trần + audit quantum | §2, Bảng I |
| **"Decoding rule là strawman"** | Test 4 quy tắc; **oracle 1-khoảng là trần cho MỌI quy tắc chọn-dải-lớp** ⇒ kết luận **decoding-agnostic**. Diệt bằng toán | `decoding.py`, §8 |
| **"Không chứng minh được giả thuyết không"** | **TOST** (SESOI khai báo trước) + **Bayesian ROPE** | E6, §7 |
| **"Các anh cài GOA sai ⇒ QIGOA là strawman"** | Tự thừa nhận trước, sửa GOA, báo cáo **cả hai**. Xác thực cài đặt bằng tái tạo bảng đã công bố (Lena/Cameraman). **Và: kết luận trung tâm không phụ thuộc GOA** — nó dựa trên nghiệm chính xác + P1 | E2, §5 |
| **"So sánh DL không công bằng"** | 2D U-Net **cùng input y hệt** là baseline chính; nnU-Net chỉ là context reference, dán nhãn rõ | E4, §8, §10 |

---

## 8. Lộ trình

| Tuần | Việc | Deliverable | Cổng |
|---|---|---|---|
| **0** ⏸️ | Trình bày với thầy | Thầy gật | **Không code cho tới khi qua cổng này** |
| **1** | Repo sạch; loader 1-lát/1-BN; `exact_dp.py`; `base.py` hard-NFE; debug GOA; **3 unit test** | Nền code verified | `test_exact_dp` + `test_nfe_budget` **pass** |
| **2** | E2 lưới chính + E3 ablation | `results/main/`, `results/ablation/` | `test_degeneracy` pass trên dữ liệu mới |
| **3** | E4 ceiling (oracle + 2D U-Net) + E5 metric | Bảng trần | — |
| **4** | E6 thống kê + E7 ngoại kiểm LGG | Toàn bộ 5 bảng + 4 hình | — |
| **5–6** | **Viết.** §3 (Degeneracy) và §8 (Ceiling) trước. Introduction sau cùng | Bản thảo đầy đủ | — |
| **7** | Rà liêm chính; `RESULTS.md` provenance; thầy review | Bản thảo đã kiểm | Checklist §6 sạch |
| **8** | Format BSPC + cover letter | **Submitted** | — |

**Compute tổng: ~40 h wall CPU + ~2 h GPU** — nằm gọn trong hạn mức Kaggle miễn phí.

> **Nút thắt của bài này không phải compute — mà là lập luận và viết.** Đừng nhầm.

---

## 9. Ba điều tuyệt đối không làm

1. **Không tái dùng bất kỳ con số nào từ commit `c4fe108`.** Nó có bug NFE 13,4%, GOA hit-rate 0%, metric tự chế, pseudo-replication. Nó là **bằng chứng chẩn đoán** — lý do ta phát hiện suy biến — **không phải nguồn số liệu**.

2. **Không đụng vào Bảng I trong `Huong-tiep-can-paper-Long.pdf`** — đó là **số bịa** (PSNR 18,45→22,87 / CPU 2,14→0,92, không có Dice). Tái sinh nó = vi phạm IRON RULE 1.

3. **Không claim "quantum advantage"** ở bất kỳ đâu. QIEA = một EDA (Platel et al., IEEE TEVC 2009, `10.1109/TEVC.2008.2003010`). Chạy trên CPU cổ điển thì đó là ẩn dụ chồng ẩn dụ. Định vị đúng: *"an EDA-style probabilistic update rule"* — và cite Platel để chứng tỏ ta biết mình đang nói gì.

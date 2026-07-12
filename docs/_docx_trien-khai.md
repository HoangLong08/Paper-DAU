---
title: "Kế hoạch triển khai paper QIGOA"
subtitle: "Từ preregistration đến bản thảo nộp được — thi công, kiểm chứng, và provenance"
author:
  - "Nguyễn Võ Hoàng Long"
  - "Hướng dẫn: TS. Đỗ Phúc Hảo — Khoa CNTT, Trường Đại học Kiến trúc Đà Nẵng"
date: "13/07/2026"
lang: vi
---

# 1. Tóm tắt điều hành

Tài liệu này trả lời đúng một câu hỏi: **làm thế nào để thi công bài báo QIGOA sao cho mỗi con số trong bản thảo đều truy được về một dòng CSV và một commit cụ thể.**

Bài báo giữ nguyên QIGOA làm nhân vật trung tâm (Kapur entropy, Q-bit, quantum rotation gate, so sánh với GA/PSO/GOA/GWO/WOA/MPA), nhưng **đổi câu hỏi nghiên cứu** từ *"QIGOA có thắng không"* sang *"QIGOA có thực sự giúp không, và ta đang đo đúng thứ chưa"*.

Lý do đổi hướng nằm trong tài liệu riêng (*Đề xuất điều chỉnh hướng paper QIGOA*). Tóm tắt lại trong ba dòng, cả ba đều đã kiểm chứng trên 25.200 run của lô thí nghiệm đầu tiên:

- **QIGOA được cấp thêm 13,4% ngân sách** so với mọi baseline (memetic refinement gọi hàm mục tiêu nhưng không bị trừ vào ngân sách).
- **Tối ưu càng giỏi thì phân đoạn càng tệ:** khi k tăng 2 → 10, Kapur fitness / PSNR / SSIM đều tăng đơn điệu, nhưng Dice sụp từ 0,664 xuống 0,437 (Spearman = −0,893).
- **Suy biến cấu trúc:** mask khối u chỉ phụ thuộc **một** trong k ngưỡng. Kiểm trên toàn bộ dữ liệu: 2.576/2.576 nhóm cho Dice hằng số, độ lệch chuẩn lớn nhất bằng 0.

Tài liệu này bắt đầu từ chỗ đó, và mô tả **cách thi công** bài báo mới.

---

# 2. Bốn nguyên tắc chi phối mọi quyết định kỹ thuật

Khi phân vân bất kỳ điều gì trong quá trình thi công, quay về bốn nguyên tắc này.

**Nguyên tắc 1 — Số liệu chảy một chiều.**
`configs/` → `scripts/` → `results/` → `paper/`. Không bao giờ gõ số bằng tay vào bản thảo. Bảng và hình trong `paper/` được **sinh** từ `results/` bằng script build. Nếu một con số trong bài không truy được về một ô CSV, nó mang nhãn `[PLACEHOLDER]` và không được phép xuất hiện như kết quả thật.

**Nguyên tắc 2 — Cái gì kiểm được bằng `assert` thì không kiểm bằng niềm tin.**
Ba lỗi giết chết lô thí nghiệm đầu tiên (ngân sách lệch, baseline hỏng, metric tự chế) đều thuộc loại mà **một dòng test tự động sẽ chặn được**. Chúng được biến thành ba cổng cứng, mô tả ở §4.

**Nguyên tắc 3 — Thí nghiệm được thiết kế để bác bỏ chính mình.**
Mỗi mệnh đề có một thí nghiệm mà *nếu mệnh đề sai, thí nghiệm sẽ cho thấy điều đó*. Đây là khác biệt giữa "chứng minh tôi đúng" và "cố gắng chứng minh tôi sai, và thất bại".

**Nguyên tắc 4 — Kaggle là môi trường chạy, không phải môi trường phát triển.**
Mọi code phải chạy được ở máy local với dữ liệu synthetic (smoke test, dưới 60 giây) trước khi đẩy lên Kaggle. Bắt lỗi ở local rẻ hơn bắt lỗi sau tám tiếng chạy.

---

# 3. Bốn mệnh đề được thi công

Bốn mệnh đề đã được **khoá trong preregistration trước khi chạy bất kỳ thí nghiệm nào** — đây là hàng rào chống HARKing (điều chỉnh giả thuyết cho khớp số sau khi đã thấy số).

| Mã | Mệnh đề | Bác bỏ được nếu |
|----|---------|-----------------|
| **P1** | **Suy biến cấu trúc.** Với bất kỳ quy tắc decoding nào chọn một dải lớp cường độ liên tiếp làm mask, mask được xác định bởi **nhiều nhất 2** trong k ngưỡng — bất kể k. Với quy tắc "lớp sáng nhất" của văn liệu: đúng **1**. | Tồn tại một nhóm `(ảnh, dải-lớp)` có `std(Dice) > 0` |
| **P2** | **Không còn gì để tối ưu.** Với ngân sách bằng nhau, mọi metaheuristic đạt ≥ 99,99% nghiệm tối ưu toàn cục chính xác (tính được bằng quy hoạch động trong mili-giây). | Một thuật toán cho `hit_rate < 0,99` một cách hệ thống |
| **P3** | **Goodhart.** fitness / PSNR / SSIM tăng đơn điệu theo k trong khi Dice và HD95 xấu đi. Chọn k bằng PSNR → k = 10; chọn bằng Dice → k = 4. | Tương quan hoá ra dương hoặc không có ý nghĩa thống kê |
| **P4** | **Trần.** Oracle vét cạn trên mọi mask-một-khoảng là trần đúng của **mọi** phương pháp thresholding cường độ. Một 2D U-Net trên đúng cùng input vượt trần đó. | U-Net không vượt oracle |

**Đóng góp dương bắt buộc** (biến "kết quả âm" thành "bài đăng được"):

1. Một bộ giải chính xác mili-giây, một tham số, đánh bại cả bảy metaheuristic — nhanh hơn khoảng 250 lần.
2. Một checklist giao thức đánh giá cho dòng văn liệu này: đo Dice/HD95, báo cáo quy tắc decoding, ngân sách bằng nhau, thống kê ở cấp bệnh nhân.

**Một sự thật bất lợi phải tự nêu.** Trong *cùng một k*, tương quan giữa PSNR và Dice là **dương** (khoảng +0,75 đến +0,93). Nghịch lý chỉ xuất hiện khi *đổi k*. Điều này đã được ghi vào preregistration như một ràng buộc bắt buộc phải nêu trong bài. Sự thật bất lợi mà mình tự nêu trước thì không còn là vũ khí của reviewer nữa.

---

# 4. Ba cổng cứng — nơi lỗi cũ bị chặn

Ba lỗi của lô cũ không phải xui xẻo; chúng là hệ quả của việc thiếu cơ chế kiểm tra. Lần này mỗi lỗi có một cổng chặn tương ứng, và **fail bất kỳ cổng nào thì không được chạy lưới thí nghiệm**.

## Cổng 1 — Ngân sách bằng nhau (`test_nfe_budget`)

Lỗi cũ: QIGOA tiêu 8.563 lượt đánh giá hàm mục tiêu trong khi mọi baseline tiêu đúng 7.550 — thừa 13,4%. Nguyên nhân: memetic refinement, OBL và Lévy flight có gọi hàm mục tiêu nhưng không ai trừ vào ngân sách.

Cách chặn: mọi thuật toán chỉ được chạm vào hàm mục tiêu qua **một cổng duy nhất**.

```python
class Optimizer:
    def __init__(self, budget, seed, ...):
        self.budget = budget      # ngân sách NFE tuyệt đối
        self._used = 0

    def evaluate(self, x) -> float:
        """CỔNG DUY NHẤT tới hàm mục tiêu.
        Không thuật toán nào được gọi objective() trực tiếp."""
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

Với thiết kế này, lỗi ngân sách **không thể tái diễn** kể cả khi người viết code quên — vì mọi lượt đánh giá đều bị đếm, và có `assert` cuối cùng chặn lại.

## Cổng 2 — Nghiệm chính xác (`test_exact_dp`)

Kapur entropy có tính **cộng tính theo khoảng**: tổng entropy bằng tổng các hàm của từng cặp `(lo, hi)`. Do đó quy hoạch động cho nghiệm **tối ưu toàn cục chính xác** trong thời gian O(k·L²):

```
J[j][t] = max over t' < t of ( J[j-1][t'] + interval_entropy(t', t) )
```

Cổng: bộ giải này phải khớp **bit-exact** (khớp tới từng chữ số) với vét cạn tại k = 2 và k = 3 trên ít nhất 20 ảnh. Nếu fail, mọi kết luận về P2 vô hiệu, và ta dừng toàn bộ để debug.

> **Lưu ý về sở hữu trí tuệ.** Bộ giải chính xác **không phải đóng góp của chúng ta**. Phải cite trang trọng ngay ở Abstract: Luessi et al., *J. Electronic Imaging* 18(1):013004 (2009); và **Merzban & Elbayoumi**, *Expert Systems with Applications* 116:299–309 (2019). Đóng góp của ta là thứ họ không có: **ground truth lâm sàng, phát hiện suy biến, tính được trần, và audit nhánh quantum-inspired**.

## Cổng 3 — Suy biến (`test_degeneracy`)

Mệnh đề P1 phải được **kiểm chứng lại trên dữ liệu mới**, không phải tin vào kết quả cũ. Test: nhóm mọi run theo cặp `(ảnh, dải-lớp-được-chọn)`, tính `std(Dice)` trong mỗi nhóm. Yêu cầu: `std < 1e-12` trên **100%** số nhóm.

---

# 5. Kiến trúc mã nguồn

Toàn bộ mã nguồn cũ (commit `c4fe108`) **bị bỏ, viết lại từ đầu**. Nó có bốn khiếm khuyết không sửa vặt được: ngân sách lệch, baseline GOA hỏng (tỷ lệ đạt nghiệm tốt nhất bằng 0% ở mọi k ≥ 3), metric tự chế, và pseudo-replication (lấy ba lát mỗi bệnh nhân rồi đưa vào kiểm định như mẫu độc lập).

```
configs/
  exp_smoke.yaml        dữ liệu synthetic — chạy dưới 60 giây ở local
  exp_main.yaml         lưới chính, ngân sách bằng nhau
  exp_ablation.yaml     QIGOA full / −quantum / −memetic / −OBL / −Lévy
  exp_ceiling.yaml      oracle scans + baseline cổ điển
  exp_unet.yaml         2D U-Net (GPU)
  exp_external.yaml     ngoại kiểm LGG

src/
  data/         brats_loader.py   (1 lát / 1 bệnh nhân, n = 150)
                lgg_loader.py     (ngoại kiểm — Buda et al.)
                synthetic.py      (phantom cho smoke test)
  fitness/      kapur.py, otsu.py  (+ interval_entropy → nền của quy hoạch động)
  solvers/      exact_dp.py        (O(k·L²) — nghiệm tối ưu toàn cục)
                exhaustive.py      (oracle 1-ngưỡng & 1-khoảng → TRẦN)
                random_search.py
                metaheuristics/    base.py (HARD NFE BUDGET)
                                   ga, pso, goa, gwo, woa, mpa, qigoa
  decode/       decoding.py        (4 quy tắc + oracle) — nguồn của P1
  eval/         metrics.py         (Dice, IoU, HD95, NSD + PSNR, SSIM)
                stats.py           (Wilcoxon, Friedman, TOST, Bayesian ROPE)
  baselines/    classical.py       (Otsu, Li, Triangle, k-means, GMM)
                unet2d.py          (cùng input: 1 lát FLAIR)

scripts/        mỗi script tái lập ĐÚNG một bảng hoặc một hình
tests/          test_exact_dp · test_nfe_budget · test_degeneracy · test_metrics
results/        script sinh — KHÔNG sửa tay
paper/          bảng & hình PULL từ results/
```

## Về metric — không tự chế

Lô cũ dùng global-SSIM (không phải sliding-window SSIM của Wang et al.) và một FSIM tự thú trong docstring là *"not the full FSIM"*. **Một bài báo phê phán việc dùng sai metric mà bản thân lại dùng metric tự chế thì tự sát** — reviewer chỉ cần mở code.

| Metric | Nguồn | Vai trò |
|--------|-------|---------|
| Dice, IoU | thư viện chuẩn + unit test | **Kết quả** — metric quyết định |
| HD95, NSD | MedPy / surface-distance | **Kết quả** — theo chuẩn *Metrics Reloaded* (Nature Methods 2024) |
| PSNR, SSIM | `skimage.metrics` (không tự cài) | **Bằng chứng** cho P3, không phải để khoe |
| FSIM | **loại bỏ khỏi scope** | Không có cài đặt chuẩn đáng tin — bỏ rẻ hơn bảo vệ |

## Về quy tắc decoding — diệt đòn "strawman" bằng toán

Reviewer chắc chắn sẽ nói: *"Quy tắc 'lớp sáng nhất' của các anh là strawman; bài thật dùng hậu xử lý tốt hơn."*

Cách phòng thủ **không phải tranh cãi**. Ta cài bốn quy tắc decoding khác nhau, và quan trọng hơn cả, ta tính **oracle vét cạn trên mọi cặp ngưỡng** `(t_lo, t_hi)`. Oracle này là trần đúng cho **mọi** quy tắc chọn-một-dải-lớp — kể cả quy tắc chưa ai nghĩ ra. Vì vậy kết luận về trần là **decoding-agnostic theo định nghĩa**, và reviewer không có chỗ bám.

---

# 6. Bảy thí nghiệm

| Mã | Thí nghiệm | Compute | Cho ra |
|----|-----------|---------|--------|
| **E0** | Preregistration (đã xong) | — | Bốn mệnh đề khoá trước khi chạy |
| **E1** | Bộ giải chính xác + cổng kiểm bit-exact | < 30 phút CPU | Bảng II |
| **E2** | **Lưới chính, ngân sách bằng nhau.** 150 bệnh nhân × k ∈ {2,3,4,5,6,8,10} × 11 phương pháp × 5 seed | ~20 h CPU | Bảng III, Hình 2, Hình 3 |
| **E3** | **Ablation trên BraTS thật** — trả lời trực diện câu hỏi của thầy | ~6 h | Bảng IV |
| **E4** | **Phân tích trần** — oracle + 2D U-Net | ~2 h CPU + ~2 h GPU | Hình 4 (hình chủ đạo) |
| **E5** | Metric đầy đủ (thêm HD95, NSD) | ~1 h | Chứng minh P3 |
| **E6** | Thống kê (TOST, Bayesian ROPE, CD diagram) | ~1 h | Chống đòn "không chứng minh được giả thuyết không" |
| **E7** | Ngoại kiểm trên LGG (Buda et al.) | ~8 h | Chống đòn "một dataset" |

## E3 — Ablation: câu trả lời trực diện cho đề bài của thầy

Thầy giao câu hỏi: *thành phần quantum-inspired đóng góp gì?* Bản cũ **không trả lời được**, vì nó chỉ ablate trên ảnh phantom tổng hợp chứ không phải BraTS. Claim *"bỏ memetic thì QIGOA thua GA/PSO"* trong bản cũ do đó **không có provenance**. Đây là lỗ hổng lớn nhất của bản cũ.

E3 vá nó: sáu biến thể (`full`, `−quantum`, `−memetic`, `−OBL`, `−Lévy`, `PSO+memetic`), chạy trên BraTS thật, **cùng ngân sách và cùng mọi hyperparameter khác** — khớp tới từng tham số.

**Dự đoán đã khai báo trước:** thành phần quantum đóng góp xấp xỉ 0 vào Dice, bởi theo P1 nó *không thể* đóng góp gì ngoài việc dịch chuyển ngưỡng lớn nhất. **Nếu dự đoán này sai** — nếu quantum thực sự cải thiện Dice một cách có ý nghĩa — thì đó là một finding **dương**, và ta báo cáo đúng như vậy. Đây là điểm mà bài tự đặt mình vào rủi ro, và đó là điều làm nó đáng tin.

## E4 — Phân tích trần: thang chín bậc

Tất cả trên cùng một trục Dice, cùng một tập test.

| Bậc | Phương pháp | Chi phí | Ý nghĩa |
|-----|-------------|---------|---------|
| 1 | Random search (cùng ngân sách) | ~1,5 s | *Nếu ngang metaheuristic → đòn chí mạng* |
| 2 | Bảy metaheuristic (ngân sách bằng nhau) | 1–2,5 s | Cả dòng văn liệu đang ở đây |
| 3 | Quy hoạch động — tối ưu toàn cục **chính xác** | vài ms | Trần của *bài toán tối ưu* |
| 4 | Otsu / Li / k-means / GMM cổ điển | vài ms | Baseline cổ điển |
| 5 | **Ngưỡng một-tham-số học trên tập train** | ~0 | **Đóng góp dương của bài** |
| 6 | Oracle một-ngưỡng (vét cạn 254 giá trị) | ~30 ms | Trần của decoding "lớp sáng nhất" |
| 7 | **Oracle một-khoảng (vét cạn 32.385 cặp)** | ~30 s | **Trần của MỌI thresholding cường độ** |
| 8 | 2D U-Net, **cùng input** (1 lát FLAIR) | ~2 h GPU | Baseline deep learning **công bằng** |
| 9 | nnU-Net 3D đa mô thức | — | **Số trích từ văn liệu, KHÔNG chạy** |

**Bậc 5 là thứ biến bài từ "kết quả âm" thành "bài đăng được".** Nếu một ngưỡng phân vị cố định, hiệu chỉnh trên mười ảnh train, đánh bại được cả bảy metaheuristic — thì bài không còn nói *"các anh sai"*, mà nói *"chúng tôi thay cả họ phương pháp bằng một tham số, nhanh hơn 250 lần"*.

**Về deep learning — chỗ dễ chết nhất:**

- **Không train nnU-Net.** 3D full-resolution × 5 fold = nhiều ngày GPU. Kaggle cho 30 giờ GPU mỗi tuần, mỗi session tối đa 12 giờ. Bất khả thi.
- **Train một 2D U-Net trên đúng input đó** (một lát FLAIR). Đây mới là so sánh *công bằng*, và nó vô hiệu hoá phản biện *"anh so 2D đơn-modality với 3D đa-modality"*.
- **Trích số nnU-Net từ văn liệu** (Isensee et al., BraTS 2020 — whole-tumor Dice 0,9124 trên validation), **dán nhãn rõ ràng**: *reference from literature, not run by us, different input protocol*. Dùng làm bối cảnh, không phải baseline so trực tiếp.

## E6 — Thống kê

Đơn vị thống kê là **bệnh nhân** (n = 150), không phải lát ảnh. Đây là điều lô cũ làm sai và reviewer y tế sẽ bắt ngay.

| Mục | Phương pháp | Vì sao bắt buộc |
|-----|-------------|-----------------|
| So sánh cặp | Wilcoxon signed-rank + **rank-biserial correlation** | p-value không nói được độ lớn hiệu ứng |
| Omnibus | Friedman + Nemenyi + **Critical Difference diagram** | Chuẩn Demšar 2006 |
| **Khẳng định "không khác nhau"** | **TOST equivalence test**, SESOI = **0,01 Dice** (khai báo trước) | *"p > 0,05" KHÔNG đủ.* Đây là cách hợp pháp duy nhất |
| Bổ trợ Bayes | **Bayesian signed-rank + ROPE [−0,01; +0,01]** | Cho phát biểu *P(tương đương) = 0,9x* |

Không có TOST và ROPE, reviewer chỉ cần một câu — *"absence of evidence is not evidence of absence"* — và toàn bộ luận điểm của bài sập.

---

# 7. Provenance — mỗi con số về đúng script sinh ra nó

Đây là hợp đồng vận hành nguyên tắc *"không bịa số"*. Mỗi dòng dưới đây sẽ được ghi vào `docs/RESULTS.md` khi thí nghiệm tương ứng chạy xong. **Số nào chưa có dòng provenance thì mang nhãn `[PLACEHOLDER]` và không được vào bản thảo.**

| Bảng / Hình | Nguồn dữ liệu | Script sinh | Trạng thái |
|-------------|---------------|-------------|------------|
| Bảng I — trắc lượng thư mục | khảo sát tay + verify | — | chưa làm |
| Bảng II — DP vs vét cạn | `results/exact/` | `run_exact_check.py` | chưa chạy |
| Bảng III — gap, hit-rate, NFE, runtime | `results/main/summary.csv` | `run_main_grid.py` | chưa chạy |
| Bảng IV — ablation QIGOA | `results/ablation/summary.csv` | `run_ablation.py` | chưa chạy |
| Bảng V — phương pháp đề xuất vs 7 metaheuristic | `results/ceiling/summary.csv` | `run_ceiling.py` | chưa chạy |
| Hình 1 — sơ đồ pipeline | — | drawio | chưa làm |
| Hình 2 — Critical Difference diagram | `results/stats/` | `run_stats.py` | chưa chạy |
| Hình 3 — Goodhart (trục kép theo k) | `results/main/summary.csv` | `build_figures.py` | chưa chạy |
| Hình 4 — Ceiling ladder | `results/ceiling/` + `results/unet/` | `build_figures.py` | chưa chạy |

Ngoài ra, **mỗi lần chạy sinh một `run-manifest.json`** ghi: commit git, hash của config, các seed, phiên bản dataset, phiên bản thư viện, thời điểm, và đường dẫn output. **Không có manifest thì run đó không tồn tại đối với bài báo.**

---

# 8. Cấu trúc bản thảo

**Thứ tự viết khác thứ tự đọc.** Viết mục 3 (Suy biến) và mục 8 (Trần) **trước** — chúng là linh hồn của bài. Introduction viết **sau cùng**, khi đã biết bài thực sự nói gì.

| Mục | Nội dung | Bảng / Hình |
|-----|----------|-------------|
| 1. Introduction | Dòng văn liệu vẫn nở rộ. Nêu bốn mệnh đề bác bỏ được. Nói thẳng: đây là reality-check **có kèm phương pháp thay thế** | — |
| 2. Related Work & the Citation Gap | Ba nhánh: metaheuristic thresholding và nhánh quantum-inspired; **lời giải chính xác đã tồn tại**; chuẩn đánh giá segmentation. **Chỉ ra nhánh thứ nhất không cite nhánh thứ hai và không dùng nhánh thứ ba** | Bảng I |
| 3. **The Degeneracy of the Objective** | Mệnh đề 1 (mask phụ thuộc ≤ 2 ngưỡng) và Mệnh đề 2 (Kapur cộng tính → DP cho tối ưu toàn cục). Chứng minh + xác nhận bit-exact | Bảng II |
| 4. Experimental Protocol | 150 bệnh nhân, ngân sách bằng nhau, bộ metric đầy đủ, thống kê cấp bệnh nhân, **SESOI khai báo trước** | Hình 1 |
| 5. **Không còn gì để tối ưu** | Mọi metaheuristic đạt ≥ 99,99% nghiệm chính xác với chi phí gấp ~250 lần. GOA hỏng, và "significance" của QIGOA sinh ra từ đó | Bảng III, Hình 2 |
| 6. **Metric phản chỉ báo chất lượng lâm sàng** | fitness/PSNR/SSIM tăng theo k, Dice/HD95 xấu đi. **Thừa nhận thẳng**: trong cùng một k thì tương quan dương — và giải thích vì sao điều đó vẫn không cứu được gì | Hình 3 |
| 7. **Thành phần quantum không đóng góp gì** | Ablation trên dữ liệu thật, ngân sách bằng nhau. TOST + Bayes: tương đương PSO. Nền lý thuyết: QIEA thực chất là một EDA | Bảng IV |
| 8. **Trần** | Thang chín bậc. Random ≈ metaheuristic ≈ DP; oracle-interval là trần; 2D U-Net cùng input vượt trần | Hình 4 |
| 9. **Một baseline tốt hơn** (đóng góp dương) | Bộ giải mili-giây + ngưỡng một-tham-số. Kèm **checklist đánh giá** cho các bài tương lai | Bảng V |
| 10. Threats to Validity | Tự liệt kê: decoding khác, modality khác, 2D vs 3D, cỡ mẫu | — |
| 11. Conclusion | **Không** phải "metaheuristic vô dụng nói chung" — mà "**trên bài toán cụ thể này**, chúng tối ưu một biến không quan trọng, trên một bài toán đã giải xong, đo bằng thước đo phản chỉ báo" | — |

**Giọng điệu — một quyết định chiến lược.** Phê phán **thực hành**, tuyệt đối **không nêu tên tác giả để chê**. Editor sẽ chọn reviewer từ chính cộng đồng này. Đóng khung xây dựng: *benchmark + giao thức + một phương pháp thay thế nhanh hơn 250 lần*.

---

# 9. Năm phản biện chí mạng và phòng thủ

| Phản biện | Phòng thủ | Cài sẵn ở |
|-----------|-----------|-----------|
| **"Merzban 2019 làm rồi. Novelty đâu?"** (nguy hiểm nhất) | Cite họ ngay ở Abstract, tuyên bố thẳng *"we claim no novelty for the exact algorithm"*. Họ dùng ảnh tự nhiên **không có ground truth** nên *không thể* phát hiện suy biến metric. Ta có ground truth lâm sàng, P1, trần, và audit nhánh quantum | Mục 2, Bảng I |
| **"Quy tắc decoding của các anh là strawman"** | Test bốn quy tắc; **oracle một-khoảng là trần cho mọi quy tắc chọn-dải-lớp** → kết luận decoding-agnostic. Diệt bằng toán, không bằng tranh cãi | `decoding.py`, Mục 8 |
| **"Không chứng minh được giả thuyết không"** | TOST với SESOI khai báo trước + Bayesian ROPE | E6, Mục 7 |
| **"Các anh cài GOA sai nên QIGOA là strawman"** | Tự thừa nhận trước, sửa GOA, báo cáo **cả hai phiên bản**. Xác thực cài đặt bằng cách tái tạo một bảng đã công bố trên ảnh chuẩn. **Và: kết luận trung tâm không phụ thuộc GOA** — nó dựa trên nghiệm chính xác và P1, không có tham số nào để cài sai | E2, Mục 5 |
| **"So sánh deep learning không công bằng"** | 2D U-Net **cùng input y hệt** là baseline chính; nnU-Net chỉ là bối cảnh trích từ văn liệu, dán nhãn rõ | E4, Mục 8, Mục 10 |

---

# 10. Chạy trên Kaggle

**Ràng buộc:** mỗi session tối đa 12 giờ; GPU 30 giờ mỗi tuần; `/kaggle/input/` chỉ đọc; `/kaggle/working/` mất khi session hết hạn.

**Thiết kế phải resume được:**

1. **Chia stage.** Lưới chính (~20 giờ) không chạy trọn trong một session. Chia theo k: mỗi session chạy hai đến ba giá trị k, ghi CSV riêng, merge sau.
2. **Cache đặc trưng.** Histogram của 150 ảnh tính một lần, lưu ra đĩa. Đây là phần chậm nhất mà lại hoàn toàn tất định.
3. **Checkpoint sau mỗi tổ hợp** `(ảnh, k, thuật toán, seed)`. Session chết thì chạy lại chỉ tốn phần chưa xong.
4. **Sinh `run-manifest.json` cho mỗi session.**

**Dữ liệu:**

- Chính: BraTS 2020 (`awsaf49/brats20-dataset-training-validation`)
- Ngoại kiểm: LGG-MRI Segmentation (`mateuszbuda/lgg-mri-segmentation`)

**Cảnh báo quan trọng:** Kaggle chỉ có **training split** (phần có ground truth). Test set thật vẫn giữ kín trên Synapse. Do đó **không được claim "state-of-the-art trên BraTS leaderboard"**. Phải nêu rõ trong bài: tự chia theo bệnh nhân, không đánh giá trên test set chính thức.

---

# 11. Lộ trình tám tuần

| Tuần | Việc | Cổng phải qua |
|------|------|---------------|
| **0** | Trình bày với thầy | **Không viết một dòng code nào cho tới khi qua cổng này** |
| **1** | Dựng repo sạch; loader một-lát-một-bệnh-nhân; bộ giải chính xác; ngân sách cứng; debug GOA; ba unit test | `test_exact_dp` và `test_nfe_budget` **pass** |
| **2** | Lưới chính (E2) + ablation (E3) | `test_degeneracy` pass trên dữ liệu mới |
| **3** | Phân tích trần (E4) + metric đầy đủ (E5) | — |
| **4** | Thống kê (E6) + ngoại kiểm LGG (E7) | Đủ 5 bảng và 4 hình |
| **5–6** | **Viết.** Mục 3 và mục 8 trước; Introduction sau cùng | — |
| **7** | Rà liêm chính; ghi provenance; thầy review | Mọi số truy về CSV tới từng chữ số |
| **8** | Format tạp chí + cover letter | **Nộp** |

**Compute tổng cộng: khoảng 40 giờ CPU và 2 giờ GPU trên Kaggle** — nằm gọn trong hạn mức miễn phí.

> **Nút thắt của bài này không phải compute, mà là lập luận và viết.** Đừng nhầm hai thứ đó.

---

# 12. Venue

| Bậc | Tạp chí | Lý do |
|-----|---------|-------|
| **Chính** | **Biomedical Signal Processing and Control** (Elsevier, Q1/Q2, IF ≈ 4,9, **không phí APC**) | Đây *chính là* tạp chí đang xuất bản dòng văn liệu mà bài này audit — tác động chỉnh sửa cao nhất, và scope khớp tuyệt đối |
| **Dự phòng 1** | **Expert Systems with Applications** (Elsevier, Q1) | Có **tiền lệ trực tiếp**: chính ESWA đã đăng Merzban & Elbayoumi 2019 — đúng thể loại "nghiệm chính xác thắng metaheuristic" |
| **Dự phòng 2** | JCC (VAST) hoặc hội nghị Scopus (SoICT / KSE / NICS) | Lưới an toàn |

**Không nộp IEEE JBHI** — tạp chí này là *health informatics*, có điều khoản desk-reject cho bài ngoài scope, và không có tiền lệ đăng bài metaheuristic thresholding.

**Tuyệt đối tránh** Multimedia Tools and Applications và Journal of Ambient Intelligence — cả hai **đã bị Clarivate loại khỏi Web of Science**.

---

# 13. Ba điều tuyệt đối không làm

**Một — không tái dùng bất kỳ con số nào từ lô thí nghiệm cũ.** Nó có bug ngân sách 13,4%, baseline GOA hỏng, metric tự chế, và pseudo-replication. Nó là **bằng chứng chẩn đoán** — lý do ta phát hiện ra suy biến — **chứ không phải nguồn số liệu**.

**Hai — không đụng vào bảng số liệu trong bản PDF skeleton ban đầu.** Bảng đó là **số bịa** (PSNR từ 18,45 lên 22,87; CPU time từ 2,14 xuống 0,92; không có Dice). Tái sinh nó là vi phạm nguyên tắc liêm chính cơ bản nhất.

**Ba — không claim "quantum advantage" ở bất kỳ đâu.** Quantum-Inspired Evolutionary Algorithm đã được chứng minh chỉ là một Estimation of Distribution Algorithm (Platel, Schliebs, Kasabov — *IEEE Transactions on Evolutionary Computation* 13(6), 2009). Q-bit và rotation gate về mặt toán học là một vector xác suất và một luật cập nhật xác suất — không có superposition thật, không có entanglement thật. Chạy trên CPU cổ điển thì "quantum" là ẩn dụ chồng lên ẩn dụ "grasshopper". Định vị đúng: *an EDA-style probabilistic update rule* — và cite Platel để chứng tỏ ta biết mình đang nói gì.

# Preregistration — QIGOA Reality-Check Study

**Ngày khoá bản:** 13/07/2026
**Commit khi khoá:** *(điền hash của commit chứa file này)*
**Trạng thái:** 🔒 KHOÁ — viết TRƯỚC khi chạy bất kỳ thí nghiệm nào của pipeline mới.

> **Mục đích (CLAUDE.md §9):** hàng rào chống HARKing. Mọi giả thuyết, metric quyết định, ngưỡng thành công và phân tích thống kê được chốt **trước** khi nhìn thấy số. Nếu một mệnh đề thất bại, ta **báo cáo kết quả âm trung thực** theo fallback đã ghi sẵn — không đổi giả thuyết cho khớp số.
>
> **Quy tắc sửa file này:** chỉ được **thêm** (append) mục "Sửa đổi sau khoá bản" ở cuối, ghi rõ ngày + lý do. **Không được sửa lùi** nội dung đã khoá.

---

## 0. Bối cảnh — vì sao mọi số cũ bị vứt

Lô thí nghiệm đầu tiên (commit `c4fe108`, 25.200 run) có **ba lỗi cài đặt** khiến mọi con số của nó **không dùng được cho công bố**:

1. Ngân sách NFE không công bằng (QIGOA 8.563 vs baselines 7.550 — thừa 13,4%).
2. Baseline GOA hỏng (hit-rate tới nghiệm tốt nhất = 0% ở mọi k ≥ 3).
3. Metric tự chế (global-SSIM thay vì sliding-window SSIM; FSIM tự thú "not the full FSIM").
4. Pseudo-replication (3 lát/bệnh nhân đưa vào Wilcoxon như mẫu độc lập).

Lô cũ được giữ lại **làm bằng chứng chẩn đoán** (nó là lý do ta phát hiện suy biến), nhưng **không một con số nào của nó được phép xuất hiện trong bản thảo**. Toàn bộ phải tái sinh từ pipeline sạch.

---

## 1. Giả thuyết

### P1 — Suy biến cấu trúc (decoding degeneracy)

**Phát biểu.** Gọi $T = \{t_1 < t_2 < \dots < t_k\}$ là tập k ngưỡng, phân hoạch dải cường độ $[0, L-1]$ thành $k+1$ lớp. Gọi $\mathcal{D}$ là một quy tắc decoding ánh xạ phân hoạch đó thành mask nhị phân bằng cách chọn **một dải lớp liên tiếp** $[c_a, c_b]$.

> Khi đó mask $M = \{p : t_a \le I(p) < t_{b+1}\}$ chỉ phụ thuộc **nhiều nhất 2** ngưỡng $(t_a, t_{b+1})$, **bất kể k**.
> Với quy tắc "lớp sáng nhất" ($c_a = c_b = k$) mà dòng văn liệu đang dùng: mask chỉ phụ thuộc **đúng 1** ngưỡng, $t_k$.
> ⇒ Số chiều hiệu dụng của không gian tìm kiếm *lâm sàng* là **≤ 2**, không phải $k$.

**Metric quyết định.** Nhóm mọi run theo `(image_id, dải-lớp-được-chọn)`. Trong mỗi nhóm, tính `std(Dice)`.

**Ngưỡng thành công.** `std(Dice) < 1e-12` trên **100%** số nhóm (tức là hằng số tới sai số máy).

**Bác bỏ được nếu:** tồn tại ≥ 1 nhóm có `std(Dice) > 1e-12`. → P1 sai, phải rút lại mệnh đề.

**Fallback nếu thất bại:** Nếu P1 sai, toàn bộ trục xương sống của bài sụp. Khi đó chuyển sang bài khiêm tốn hơn: một ablation study trung thực (equal-NFE, quantum ON/OFF) + đánh giá task-based, nộp JCC/hội nghị Scopus. **Không cứu P1 bằng cách đổi định nghĩa.**

---

### P2 — Không còn khoảng trống tối ưu

**Phát biểu.** Với ngân sách NFE **bằng nhau tuyệt đối**, mọi metaheuristic (GA, PSO, GOA, GWO, WOA, MPA, QIGOA) và cả random search đạt fitness ≥ 99,99% của **nghiệm tối ưu toàn cục chính xác**, với chi phí thời gian lớn hơn ~2 bậc độ lớn.

**Nghiệm tối ưu chính xác** tính bằng quy hoạch động $O(k \cdot L^2)$ (Kapur cộng tính theo khoảng).
> ⚠️ **Không claim đây là đóng góp của mình.** Đã có: Luessi et al., *J. Electronic Imaging* 18(1):013004 (2009); Merzban & Elbayoumi, *Expert Systems with Applications* 116:299–309 (2019). Phải cite ở Abstract.

**Metric quyết định.**
- `relative_gap = (f_exact − f_algo) / f_exact`, báo cáo mean ± std qua ≥5 seed.
- `hit_rate` = tỷ lệ run đạt `relative_gap < 1e-4`.
- `speedup = t_algo / t_exact`.

**Ngưỡng thành công.** `hit_rate ≥ 0,99` cho **mọi** thuật toán (trừ GOA-hỏng, báo cáo riêng) tại mọi k ∈ {2..10}.

**Bác bỏ được nếu:** có thuật toán nào cho `relative_gap` âm (vượt nghiệm chính xác) → **bất khả về mặt toán**; nếu xảy ra thì bộ giải DP của ta sai → phải debug DP, không phải sửa mệnh đề.
Hoặc: nếu `hit_rate < 0,99` một cách hệ thống → P2 sai, bài toán *thực sự* khó, và metaheuristic *có* chỗ đứng. Khi đó rút P2, giữ P1/P3/P4.

**Bảo hiểm bắt buộc.** `exact_dp` phải khớp **bit-exact** với vét cạn brute-force tại k=2 và k=3 trên ≥20 ảnh (unit test). Test này fail ⇒ **không được chạy gì thêm**.

---

### P3 — Goodhart: metric hiện hành phản chỉ báo lâm sàng

**Phát biểu.** Khi k tăng, Kapur fitness, PSNR và SSIM tăng đơn điệu, trong khi Dice giảm và HD95 xấu đi.

**Metric quyết định.** `Spearman(k, Dice)` và `Spearman(k, HD95)` tính trên trung bình theo k, gộp mọi thuật toán; kèm CI bootstrap 95%.

**Ngưỡng thành công.** `Spearman(k, Dice) < −0,5` với `p < 0,05`, và CI 95% không chứa 0.

**Hệ quả kiểm tra riêng (P3b).** `argmax_k PSNR ≠ argmax_k Dice`, và Dice tại `argmax_k PSNR` thấp hơn Dice tại `argmax_k Dice` một lượng > SESOI (§3).

**Bác bỏ được nếu:** tương quan hoá ra dương hoặc không có ý nghĩa thống kê.

**Fallback:** Nếu P3 sai (PSNR đồng thuận với Dice), thì thông điệp "đo sai thước đo" sụp. Giữ P1/P2/P4, viết lại bài quanh "bài toán đã giải xong + trần thấp" thay vì "metric sai".

> **Lưu ý trung thực bắt buộc.** Trong *cùng một k*, tương quan PSNR–Dice giữa các thuật toán là **DƯƠNG** (đo trên lô cũ: ρ = +0,75…+0,93 tại k=3,4,5). Bài **phải nêu điều này**, và giải thích rằng nghịch lý nằm ở chiều *k*, không phải chiều *thuật toán*. Che giấu điều này = reviewer chạy lại số trong 10 phút và bài chết.

---

### P4 — Trần của toàn bộ họ phương pháp

**Phát biểu.** Oracle vét cạn trên mọi mask-một-khoảng (chọn cặp `(t_lo, t_hi)` tốt nhất cho từng ảnh, biết trước ground truth) là **trần đúng của MỌI phương pháp thresholding cường độ** với decoding chọn-dải-lớp. Một 2D U-Net huấn luyện trên **đúng cùng input** (1 lát FLAIR) vượt trần đó.

**Metric quyết định.** Dice và HD95 của: random search / 7 metaheuristic / DP-exact / Otsu, Li, k-means / oracle-1-ngưỡng / oracle-1-khoảng / 2D U-Net.

**Ngưỡng thành công.** `Dice(2D U-Net) > Dice(oracle-1-khoảng)` với Wilcoxon p < 0,05 ở cấp bệnh nhân.

**Bác bỏ được nếu:** U-Net **không** vượt oracle → nghĩa là thresholding *không* bị giới hạn bởi biểu diễn, và luận điểm "trần" yếu đi. Khi đó báo cáo trung thực và hạ claim xuống "thresholding chạm trần của chính nó", bỏ so sánh DL.

**Ràng buộc trung thực.**
- nnU-Net **KHÔNG được train** (không đủ compute). Số nnU-Net chỉ trích từ văn liệu (Isensee et al., BraTS 2020, arXiv:2011.00848 — WT Dice 0,9124 val / 0,8895 test) và **phải dán nhãn rõ**: *"reference from literature, not run by us, different input protocol (3D multi-modal)"*. Dùng nó như *context*, **không** như baseline được so trực tiếp.
- 2D U-Net là baseline DL **duy nhất** được so trực tiếp, vì nó dùng **đúng cùng input** với thresholding.

---

## 2. Thiết kế thí nghiệm (chốt trước)

### Dữ liệu
- **Chính:** BraTS 2020 (Kaggle `awsaf49/brats20-dataset-training-validation`). **1 lát axial FLAIR / 1 bệnh nhân, n = 150.** Lát được chọn theo quy tắc **cố định, khai báo trước**: lát có diện tích whole-tumor lớn nhất của bệnh nhân đó. Ground truth = whole-tumor binary mask.
- **Ngoại kiểm:** LGG-MRI Segmentation, Buda et al. (Kaggle `mateuszbuda/lgg-mri-segmentation`) — khác cơ sở, khác máy chụp, khác grade.
- Chỉ dùng **training split có ground truth**; tự chia theo **bệnh nhân**. **Không** claim "SOTA trên BraTS leaderboard" (test set giữ kín trên Synapse).

### Đơn vị thống kê
**Bệnh nhân** (n = 150), **không phải** lát ảnh. Đây là điều lô cũ làm sai.

### Ngân sách
**Hard NFE budget**, bằng nhau tuyệt đối cho mọi thuật toán. Memetic refinement, OBL, Lévy flight của QIGOA **đếm vào** ngân sách. Có `assert` trong `base.py`: mọi thuật toán tiêu thụ **đúng cùng số NFE (±0)**. Test này fail ⇒ toàn bộ lưới vô hiệu.

### Seed
**≥ 5 seed độc lập**, báo cáo mean ± std. Seed truyền qua config; set `random`, `numpy`, `torch` (+ `cudnn.deterministic=True`).

### Ablation (cùng NFE, cùng mọi hyperparameter khác)
`QIGOA-full` / `−quantum` / `−memetic` / `−OBL` / `−Lévy` / `PSO+memetic`
→ Đây là câu trả lời trực diện cho câu hỏi *"thành phần quantum đóng góp bao nhiêu?"*

**Dự đoán khai báo trước:** thành phần quantum đóng góp ≈ 0 vào Dice (theo P1, nó *không thể* đóng góp gì ngoài việc dịch chuyển $t_k$). Nếu dự đoán này **sai** — tức quantum thực sự cải thiện Dice một cách có ý nghĩa — thì đó là một finding **dương** và ta báo cáo nó như vậy.

### Quy tắc decoding (test 4 quy tắc, chống đòn "strawman")
1. Lớp sáng nhất (`seg == seg.max()`) — quy tắc của văn liệu
2. Hợp các lớp trên cùng (`seg >= j` với j quét)
3. Chọn lớp theo Otsu hai tầng
4. Có hậu xử lý hình thái (morphological)
+ **Oracle 1-khoảng** = trần đúng cho *mọi* quy tắc chọn-dải-lớp ⇒ kết luận về trần là **decoding-agnostic**.

---

## 3. Thống kê (chốt trước)

| Mục | Phương pháp |
|---|---|
| So sánh cặp | **Wilcoxon signed-rank** (cấp bệnh nhân) + **effect size: rank-biserial correlation** |
| Omnibus | **Friedman** + post-hoc **Nemenyi**, kèm **Critical Difference diagram** (Demšar 2006) |
| Hiệu chỉnh đa so sánh | **Holm** |
| **Khẳng định "không khác nhau"** | **TOST equivalence test** — *cách hợp pháp duy nhất*. "p > 0,05" **KHÔNG** đủ. |
| Bổ trợ Bayes | **Bayesian signed-rank test + ROPE** (Benavoli et al., JMLR 2017) → phát biểu `P(tương đương) = 0,9x` |

### 🔒 SESOI (Smallest Effect Size Of Interest) — khai báo trước, không được đổi

> **SESOI = 0,01 Dice.**
> **Vùng tương đương (ROPE) = [−0,01, +0,01] Dice.**

**Lý do chọn 0,01:** chênh lệch Dice giữa các thuật toán trong lô cũ ~0,05, trong khi chênh lệch do chọn k là ~0,25. Một khác biệt < 0,01 Dice không có ý nghĩa lâm sàng nào và nằm trong nhiễu liên-bệnh-nhân. Đây là ngưỡng **bảo thủ** (dễ bác bỏ tương đương hơn là dễ chấp nhận).

---

## 4. Điều gì sẽ khiến ta DỪNG (ba cờ đỏ — CLAUDE.md §3, §9)

Nếu gặp bất kỳ dấu hiệu nào sau đây, **DỪNG và điều tra**, không đi tiếp:

- **(a)** Lợi thế của QIGOA vẫn tồn tại sau khi cùng-tham-số-hoá và cùng ngân sách → nghĩa là giả thuyết của ta sai, phải reframe **theo hướng ngược lại** (QIGOA thực sự có ích) và báo cáo trung thực.
- **(b)** Kết quả chỉ đẹp trên một seed/split.
- **(c)** Không tái lập được từ script sạch.
- **(d)** `exact_dp` không khớp bit-exact với vét cạn → DP sai, mọi thứ dựng trên nó vô hiệu.
- **(e)** Bất kỳ thuật toán nào cho `relative_gap` âm → toán học bất khả ⇒ có bug.

---

## 5. Cam kết liêm chính

- **Không xoá run xấu.** Mọi run — kể cả thất bại — được ghi vào `docs/RESULTS.md` dạng append-only. Run âm là dữ liệu.
- **Mọi số trong bản thảo phải truy được về một ô trong CSV** qua dòng provenance trong `RESULTS.md` (CLAUDE.md §5.3).
- **Không claim "quantum advantage"** ở bất kỳ đâu. QIEA = một EDA (Platel et al., IEEE TEVC 2009, `10.1109/TEVC.2008.2003010`). Định vị đúng: *"an EDA-style probabilistic update rule"*.
- **Không claim exact/DP solver là đóng góp của mình** (Luessi 2009; Merzban & Elbayoumi 2019).
- **Không dùng lại bất kỳ con số nào** từ commit `c4fe108`.
- **Nếu P1 hoặc P2 thất bại**, hạ scope xuống bài ablation khiêm tốn và nộp venue thấp hơn — **không cứu claim đã chết**.

---

## 6. Sửa đổi sau khoá bản

*(append-only — mỗi sửa đổi ghi: ngày · lý do · ai duyệt)*

*(chưa có)*

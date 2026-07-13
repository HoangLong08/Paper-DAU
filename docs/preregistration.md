# Preregistration — QIGOA Reality-Check Study

**Ngày khoá bản:** 13/07/2026
**Commit khi khoá:** *(điền hash của commit chứa file này)*
**Trạng thái:** 🔒 KHOÁ — viết TRƯỚC khi chạy bất kỳ thí nghiệm nào của pipeline mới.

> **Mục đích (CLAUDE.md §9):** hàng rào chống HARKing. Mọi giả thuyết, metric quyết định, ngưỡng thành công và phân tích thống kê được chốt **trước** khi nhìn thấy số. Nếu một mệnh đề thất bại, ta **báo cáo kết quả âm trung thực** theo fallback đã ghi sẵn — không đổi giả thuyết cho khớp số.
>
> **Quy tắc sửa file này:** chỉ được **thêm** (append) mục "Sửa đổi sau khoá bản" ở cuối, ghi rõ ngày + lý do. **Không được sửa lùi** nội dung đã khoá.

> ## ⚠️ ĐỌC §6 TRƯỚC KHI ĐỌC §1
> **AMENDMENT #1 (14/07/2026)** đã sửa/hạ cấp **phần lớn nội dung §1–§3 bên dưới**, sau một audit đối kháng 24 agent chạy **trước khi nhìn thấy bất kỳ số thực nghiệm nào**.
> **Nội dung §1–§5 dưới đây được GIỮ NGUYÊN làm bằng chứng lịch sử** (đúng luật append-only) — **nhưng nhiều phần trong đó đã SAI hoặc KHÔNG VẬN HÀNH ĐƯỢC**:
> **P1** là strawman nếu viết như quy kết (§6/A1) · **P2** đã bị scoop và ngưỡng của nó tự bác bỏ (§6/A4b) · **P3** có decision rule **tự mâu thuẫn về toán học** (§6/A4a) · **P4** phát biểu **SAI về toán** (§6/A2) · **TOST** có power ≈ 0,08–0,34 và SESOI lấy từ dữ liệu đã tuyên bố vô hiệu (§6/A4c) · **đóng góp dương** hiện là **train-on-test** (§6/A3).
> 👉 **Mọi thi công phải theo §6, không theo §1–§3.**

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

---

### 📌 AMENDMENT #1 — 14/07/2026 · Sau audit đối kháng 24 agent · Duyệt: Nguyễn Võ Hoàng Long

**Bối cảnh.** Trước khi chạy bất kỳ thí nghiệm nào, hồ sơ được đưa qua một audit gồm 5 reviewer mô phỏng (EIC/desk-screen · insider cộng đồng metaheuristic · medical imaging · thống kê/reproducibility · Devil's Advocate) và 6 lane collision-check văn liệu có verify đối kháng. **Không một con số thực nghiệm nào được nhìn thấy trong quá trình này** — mọi sửa đổi dưới đây là sửa đổi *thiết kế*, không phải sửa đổi *hậu-kết-quả*. Đây chính là chức năng của preregistration, và nó đang hoạt động đúng như thiết kế.

**Mọi DOI/arXiv ID trích trong amendment này đã verify độc lập qua Crossref API + arXiv API ngày 14/07/2026.**

**Kết quả cốt lõi của audit:** *(a)* **đóng góp dương duy nhất được đánh dấu "bắt buộc" có novelty = 0%**; *(b)* **P4 phát biểu SAI về mặt toán**; *(c)* **P1 đang là strawman và nếu viết như một quy kết thì vi phạm IRON RULE 2**; *(d)* **ba trong bốn decision rule không vận hành được**; *(e)* **đóng góp dương hiện đang là train-on-test**.

---

#### A0 · ĐỔI CÁCH BÁN BÀI — một luận đề, không phải bốn mệnh đề

**Lý do.** Bốn mệnh đề nửa-bị-scoop trong một áo choàng = bài mỏng. Sau khi trừ hết near-rival, thứ còn sống là một **luận đề hợp thành** mà **không kết quả thực nghiệm nào giết được**.

> **LUẬN ĐỀ (bán cái này):** *Trong miền có ground truth lâm sàng, khoảng cách tối ưu mà cả dòng văn liệu đang tranh nhau **KHÔNG chiếu xuống mask lâm sàng** — bất kể metaheuristic có đạt nghiệm tối ưu hay không.*
>
> **Bất tử trước kết quả:** nếu mọi metaheuristic đạt tối ưu ⇒ optimizer là **đồ trang trí**. Nếu **không** đạt ⇒ cả một thập kỷ engineering đang đóng một gap **chứng minh được là không chiếu xuống lâm sàng**. Hai nhánh đều kết tội; lưỡng phân là **vét cạn**.

**Headline experiment mới:** DP-exact vs 7 metaheuristic vs **random search**, TOST tương đương trên **Dice** (KHÔNG phải fitness), cộng **MASK-IDENTITY RATE**: *"trên X% ô (bệnh nhân, k), cả 7 metaheuristic sinh ra binary mask **giống hệt nhau từng byte**"* — không cần kiểm định, không phản bác được.

Vai trò mới: **P1** → 1 đoạn cơ chế. **P2** → 2 đoạn setup có citation. **P3** → corroboration. **P4** → ceiling decomposition.

---

#### A1 · P1 — VIẾT LẠI THÀNH THẾ LƯỠNG NAN, TUYỆT ĐỐI KHÔNG PHẢI QUY KẾT 🔴 FATAL

**Lý do (bằng chứng thực nghiệm từ văn liệu, đã fetch toàn văn).** Quy tắc decoding "lớp sáng nhất" (`seg == seg.max()`) mà §1/P1 giả định là *"quy tắc của văn liệu"* — **KHÔNG TÌM THẤY TRONG VĂN LIỆU**. Nó là **code cũ của chính chúng ta**.

- **Đa số bài trong dòng này KHÔNG tạo binary mask và KHÔNG dùng ground truth:** GAAOA-Lévy (Sci Rep 2025, `10.1038/s41598-025-12142-z`) — chỉ PSNR/STD/fitness/CPU, ảnh Cameraman/Peppers/Baboon; CIWP-PSO (PLOS ONE 2024, `10.1371/journal.pone.0306283`) — **tự viết** *"does not compare results against ground truth segmentation masks"*; BSPC vol. 113 (2026) CPO — ảnh **y tế**, PSNR/SSIM/FSIM, **không Dice**; và **chính bản phác 2 trang của thầy**.
- **Thiểu số CÓ báo Dice thì decode bằng segmenter hạ nguồn:** region growing (Jena et al. 2023, `10.1007/978-981-19-6068-0_4` — *"The region growing method is used to isolate the complete tumour part"*); k-means + morphology (Dey et al., Cognitive Computation 12:1011–1023, 2020, `10.1007/s12559-020-09751-3` — thresholding chỉ là **tiền xử lý**); morphological reconstruction (Rajinikanth et al.). **Với các pipeline này, "≤2 ngưỡng" KHÔNG áp dụng.**
- **Bài CÓ nhị phân hoá thì KHÔNG NÊU QUY TẮC:** Sharma et al. (Diagnostics 13(5):925, 2023, `10.3390/diagnostics13050925`); Mahum et al. (Biomedicines 11(6):1715, 2023, `10.3390/biomedicines11061715`).

**⛔ CẤM viết:** *"văn liệu decode bằng lớp sáng nhất [refs 12–25]"*. Đó là **xuyên tạc công trình được trích dẫn** ⇒ **vi phạm IRON RULE 2**, nghiêm trọng hơn cả rủi ro bị reject.

**✅ PHÁT BIỂU MỚI (khoá):**

> **Quan sát khả kiểm:** *"Không một bài nào trong khảo sát của chúng tôi nêu rõ ánh xạ từ vector k ngưỡng sang binary mask được báo cáo."* ← **đây mới là claim thực nghiệm, và nó bác bỏ được** (bằng Bảng I).
>
> **Thế lưỡng nan (vét cạn):**
> - **Horn 1** — nếu decode qua **band mask** (kể cả kèm morphology / connected components trên binary mask): thì k−1 ngưỡng là **biến giả**, và toàn bộ máy móc Q-bit/rotation gate/Lévy/memetic đang tối ưu biến không ảnh hưởng output.
> - **Horn 2** — nếu decode bằng **segmenter hạ nguồn** (k-means / watershed / Chan–Vese / region growing trên label map): thì mask **do segmenter tạo ra**, và tầng thresholding **CHƯA TỪNG ĐƯỢC ABLATE trong bất kỳ bài nào** ⇒ claim nhân quả *"optimizer tốt hơn ⇒ mask tốt hơn"* là **CHƯA ĐƯỢC KIỂM**.
>
> **Hai sừng đều kết tội. Bài không cần biết văn liệu ở sừng nào.**

**Sửa metric quyết định của P1:** nhóm theo **MASK HASH**, không theo `t_max`. *(Lý do: nhóm theo band đã chọn sẽ "conditioning away" chính đường phụ thuộc `{t_1..t_k} → chỉ số band → mask` — tồn tại thật với `otsu_pick`.)*

**BỔ SUNG 3 decoder tiêu thụ TOÀN BỘ label map** (k-means, watershed, Chan–Vese) vào §2/quy tắc decoding. **Lý do:** 4 rule hiện có (§2, dòng 123–128) **đều là Horn-1** và do đó **KHÔNG THỂ bác bỏ P1** — một mệnh đề chỉ được kiểm bằng những thí nghiệm không thể làm nó sai thì không phải khoa học.

**Hạ cấp `std(Dice) < 1e-12`:** đây là **unit test số học** (`tests/test_degeneracy.py`), **KHÔNG phải Result**, **KHÔNG có p-value**, và **không được trình bày như bằng chứng thực nghiệm**. Nó luôn pass, kể cả trên ảnh nhiễu ngẫu nhiên. Trình bày đúng: **Proposition + proof 3 dòng + Corollary** (tập mask khả dĩ của mọi band-selection decoding có lực lượng ≤ **C(255,2) = 32.385**, bất kể k — trong khi search space tại k=10 là C(254,10) ≈ **2,6 × 10¹⁷**; tỷ số ~10⁻¹³ **là headline number**).

---

#### A2 · P4 — SỬA ĐỊNH LƯỢNG TỪ SAI + CẤM CLAIM TRẦN 🔴 FATAL

**Lý do (lỗi toán).** Phát biểu *"oracle-1-khoảng là trần đúng của MỌI phương pháp thresholding cường độ"* (§1/P4, dòng 87; và `ke-hoach-trien-khai.md:155,:228`) **SAI**. Nó chỉ chặn decoder chọn **một dải lớp LIÊN TIẾP**. Decoder chọn tập lớp **KHÔNG liên tiếp** vượt nó (brute-force độc lập 2 agent: vượt trên ~98% histogram, mean **+0,04**, max **+0,13** Dice). Câu *"đòn strawman bị vô hiệu bằng định nghĩa"* do đó **dựng trên một định lượng từ sai** — và **một bài chuyên phê phán overclaim mà tự overclaim thì chết không cãi được**.

**✅ TRẦN ĐÚNG (khoá):** oracle trên **tập mức xám tuỳ ý** $S \subseteq \{0..L-1\}$ — đây là dạng tổng quát nhất của *mọi* decoder chỉ-dùng-cường-độ.

$$\max_{S} \ \mathrm{Dice}(S) = \max_{S} \frac{2\sum_{v \in S} g_v}{\sum_{v \in S} n_v + |G|}$$

Linear-fractional 0/1 program ⇒ nghiệm tối ưu **luôn là superlevel-set của purity** $r_v = g_v / n_v$ ⇒ **sắp xếp mức xám theo $r_v$ giảm dần, quét prefix, lấy max** ⇒ **nghiệm CHÍNH XÁC trong $O(L \log L)$**, vài mili-giây/ảnh, **độc lập k**.

> ⛔ **KHÔNG ĐƯỢC CLAIM ĐÂY LÀ ĐỊNH LÝ CỦA MÌNH.** Đã có chủ: **Lipton, Elkan & Narayanaswamy**, *Thresholding Classifiers to Maximize F1 Score*, **arXiv:1402.1892** (ECML-PKDD 2014) — *"the optimal threshold is half the optimal F1 score"*; + **RankSEG** (Dai & Li, JMLR 2023). Dice = F1; purity = posterior đã calibrate. ⇒ **CLAIM ỨNG DỤNG, KHÔNG CLAIM TOÁN HỌC.** Ship nó như *"Theorem 1 (ours)"* = lặp lại **đúng tội fabricated-novelty mà bài này sinh ra để trừng phạt**.

> ⛔ **CẤM TUYỆT ĐỐI mọi câu "we establish the ceiling".** **François & Tinarrage** nay đã peer-reviewed — **J. Mathematical Imaging & Vision 68, 20 (2026)**, `10.1007/s10851-026-01300-1` — và toàn văn chứa nguyên văn: *"the oracle best Dice score reaches a mean of **0.83±0.18**. These results provide **an upper bound on the achievable performance within the considered thresholding framework**."* **Trên BraTS FLAIR.** ⇒ khái niệm + dataset + **con số** + cả so sánh DL **đều đã in**.

**🔴 FALLBACK BẮT BUỘC CHO P4 — VIẾT HÔM NAY, TRƯỚC KHI NHÌN THẤY BẤT KỲ SỐ NÀO:**

Tiêu chí thành công hiện tại (§1/P4: `Dice(2D U-Net) > Dice(oracle-1-khoảng)`, Wilcoxon p<0,05) là **tung đồng xu, và nghiêng về phía THUA**:
- oracle-1-ngưỡng của François = **0,83**; oracle-1-**khoảng** ≥ nó; oracle **level-set** còn cao hơn ~+0,04;
- ta lại **cố tình chọn lát DỄ NHẤT** (§2: lát có WT area lớn nhất) ⇒ trần của ta có thể rơi vào **0,88–0,93**;
- 2D U-Net FLAIR-only train trên ~120 bệnh nhân thường chỉ **0,80–0,82**;
- và trên WT/FLAIR, **trần KHÔNG THẤP**: 0,83 nằm trong vùng **đồng thuận liên-quan-sát-viên** (~0,85–0,87, Menze et al., IEEE TMI 2015).

> **FALLBACK (khoá trước khi thấy số):** nếu U-Net **không** vượt trần, headline **KHÔNG** rút về *"thresholding chạm trần của chính nó"* (— đó **đúng bằng thứ François đã in**, tức là zero novelty). Headline đổi thành:
>
> **"Trần CAO — và đó mới là điều đáng nói: thất bại của thresholding KHÔNG do giới hạn biểu diễn, mà do BÀI TOÁN CHỌN NGƯỠNG; và không một cỗ máy metaheuristic nào trong dòng văn liệu này chạm tới bài toán chọn đó."**
>
> Framing này **tương thích với P1 + P2**, **chưa ai chiếm**, và nó **mạnh hơn** kịch bản U-Net thắng.

**Thêm target KHÓ (bắt buộc):** **ET trên T1ce**. Lý do: ET là một **vành sáng bao lõi tối** ⇒ **về mặt toán học KHÔNG THỂ** biểu diễn bằng một dải cường độ liên tiếp ⇒ đó là nơi giới hạn biểu diễn của thresholding là **THẬT**, không phải giả định. Giữ WT/FLAIR nguyên vẹn làm **trường hợp thuận lợi nhất cho phe bị audit** (lập luận *a fortiori*).

---

#### A3 · SPLIT CẤP BỆNH NHÂN — SỬA LEAKAGE TRONG ĐÓNG GÓP DƯƠNG 🔴 FATAL

**Lý do.** Hiện **không chỗ nào** trong preregistration hay kế hoạch khai báo train/test split. Hậu quả:
- U-Net train trên cả 150 ⇒ **leakage**. Train 120 / test 30 trong khi thresholding đánh giá trên 150 ⇒ **Wilcoxon ghép cặp cấp bệnh nhân (§1/P4) KHÔNG CÓ ĐỊNH NGHĨA TOÁN HỌC** (hai vector độ dài khác nhau, trên hai tập bệnh nhân khác nhau, không ghép đôi được).
- **"Ngưỡng 1-tham-số hiệu chỉnh trên 10 ảnh train"** — thứ mà kế hoạch gọi là *"thứ biến bài từ negative result thành bài đăng được"* — **hiện là train-on-test**, nằm ngay trong **đóng góp dương của một bài tố cáo người khác so sánh không lành mạnh**. Đây là lỗi **DUY NHẤT có thể bị reject vì LIÊM CHÍNH**, không phải vì novelty.

**✅ THIẾT KẾ KHOÁ:**

```
Đơn vị split : BỆNH NHÂN (không phải lát)
Outer CV     : 5-fold, phân tầng theo grade (HGG/LGG) + tertile thể tích WT
Inner        : 1 fold val trong mỗi outer-train (early stopping / chọn epoch)
Seeds        : ≥3 seed × 5 fold cho U-Net (KHÔNG phải 1 lần train)
Artefact     : data/splits/fold_{0..4}.json + brats_cohort.csv  → COMMIT vào repo
```

**Phân loại BẮT BUỘC — mỗi phương pháp thuộc đúng một hàng:**

| Loại | Phương pháp | Đánh giá trên |
|---|---|---|
| **A — unsupervised, per-image** | Otsu, Li, Triangle, k-means, GMM, Kapur+DP, 7 metaheuristic, random search | cả n bệnh nhân (hợp lệ) |
| **B — CÓ HỌC** | 2D U-Net · **ngưỡng 1-tham-số** · **VIỆC CHỌN k** · mọi hậu xử lý có tham số tuned | **CHỈ out-of-fold** |
| **C — oracle** | oracle-1-ngưỡng, oracle-1-khoảng, oracle level-set | **KHÔNG phải "phương pháp"** — là cận trên không đạt được. **Dán nhãn `uses test-time ground truth` ở MỌI bảng/hình** |

**Quy tắc bất khả xâm phạm:** nested CV ⇒ **mọi** phương pháp (kể cả loại B) cho **đúng một giá trị out-of-fold / bệnh nhân** trên **cùng một tập bệnh nhân** ⇒ Wilcoxon paired / Friedman / TOST **mới có định nghĩa**.

**"Cùng input" là ràng buộc lúc INFERENCE, không phải lúc TRAIN.** ⇒ U-Net train trên **TẤT CẢ lát có u** của các bệnh nhân trong outer-train (hàng nghìn lát), infer trên **đúng 1 lát chỉ định** của bệnh nhân held-out. Điều này giữ nguyên phản-đòn *"anh so 2D đơn-modality với 3D đa-modality"* **đồng thời loại bỏ confound U-Net-thiếu-dữ-liệu**. Nếu không làm vậy, kết quả P4 — dù dương hay âm — **đều không diễn giải được**.

**Chuẩn hoá cường độ per-image** (percentile trong chính ảnh đó). Dùng thống kê toàn dataset = **preprocessing leak**.

**E7 (LGG) = zero-shot.** **CẤM re-tune** ngưỡng 1-tham-số trên LGG. Re-tune ⇒ không còn là external validation.

---

#### A4 · SỬA BA DECISION RULE KHÔNG VẬN HÀNH ĐƯỢC 🔴 FATAL

**(a) P3 — decision rule TỰ MÂU THUẪN VỀ MẶT TOÁN HỌC.**
§1/P3 chốt `ρ < −0,5` **VÀ** `p < 0,05`. Với k ∈ {2,3,4,5,6,8,10} ⇒ **n = 7 điểm**. Critical value của Spearman ở two-tailed α=0,05 là **|ρ| ≈ 0,786** (permutation chính xác: ρ = −0,5 ⇒ **p = 0,267**). ⇒ Nếu kết quả là ρ = −0,60: vế thứ nhất nói **P3 ĐÚNG**, vế thứ hai nói **P3 SAI**, và **không có tiebreak**. Một preregistration không quyết định được **đã thất bại ở chức năng duy nhất của nó**.
Thêm: quan hệ là **chữ U ngược** (pilot của chính ta: Dice **TĂNG** 0,664@k=2 → 0,675@k=4 rồi mới sụp) ⇒ **rank correlation là dụng cụ SAI**. Và trung bình-theo-k trước rồi mới tương quan là **aggregation fallacy** — nó **che giấu chính Simpson's paradox mà bài muốn phơi bày**.

> **✅ PRIMARY MỚI (khoá):** với mỗi bệnh nhân *i*: $\Delta_i = \mathrm{Dice}_i(k^*_{\mathrm{Dice}}) - \mathrm{Dice}_i(k^*_{\mathrm{PSNR}})$. **One-sample Wilcoxon** trên {Δᵢ}, **n = 150**, + rank-biserial + bootstrap CI (BCa, over patients). Thành công: median Δ > SESOI, p < 0,05, CI không chứa SESOI.
> **Headline trở thành một CHI PHÍ có đơn vị lâm sàng:** *"chọn k bằng PSNR như văn liệu đang làm khiến bệnh nhân mất 0,NN Dice."*
> **SECONDARY:** Spearman ρᵢ **từng bệnh nhân** trên 7 giá trị k ⇒ 150 hệ số ⇒ one-sample Wilcoxon. Bây giờ *"ρ < −0,5"* **có nghĩa** và *"p < 0,05"* **có power**.
> **THÊM — chứng minh, đừng tương quan:** PSNR là hàm đơn điệu của sai số lượng tử hoá ⇒ **tăng theo k BẰNG CẤU TRÚC** (Lloyd–Max). Lập luận giải tích **không thể bị đánh bằng cỡ mẫu**.
> Aggregate Spearman(k, Dice) **xuống hình mô tả**, **bỏ khỏi decision rule**.
> Khai báo hướng cho `Spearman(k, HD95)`: HD95 thấp = tốt ⇒ ngưỡng thành công là ρ **DƯƠNG**.

**(b) P2 — ngưỡng all-or-nothing sẽ TỰ BÁC BỎ, và nghịch lý fitness chưa được phòng thủ.**
`hit_rate ≥ 0,99 cho MỌI thuật toán tại MỌI k ∈ {2..10}` là một **conjunction trên 54–63 điều kiện**; một ô ra 0,97 sẽ **bác bỏ P2** dù mệnh đề vẫn đứng vững. Và **Hammouche, Diaf & Siarry (EAAI 23:676–688, 2010, `10.1016/j.engappai.2009.09.011`)** đã báo **ACO/SA KHÔNG đạt tối ưu khi k>2**; pilot của chính ta chỉ ≥96% < 0,99.

> **✅ PHÁT BIỂU LẠI P2 (immanent critique — hai chân):**
> - **P2a (trên sân của chính đối phương):** *có điều kiện chấp nhận* Kapur làm objective ⇒ bài toán đã giải xong (DP `O(k·L²)`, mili-giây — **Menotti et al. 2015, KHÔNG phải đóng góp của ta**), và mọi metaheuristic đạt fitness trong ε của nó.
> - **P2b (đồng tiền lâm sàng — chân chống-circularity):** phần fitness-gap còn sót **KHÔNG dịch thành khác biệt lâm sàng nào** — TOST/ROPE trên `Dice(algo) − Dice(DP-exact)` ở cấp bệnh nhân.
> - **P2c (decoupling test — MỚI, 5 dòng code, falsifiable):** `Spearman(relative_gap_fitness, |ΔDice vs DP|)` ⇒ **dự đoán ≈ 0**. Nếu tương quan này mạnh và dương ⇒ fitness *thực sự* là proxy tốt cho Dice ⇒ **toàn bộ luận điểm Goodhart yếu đi**. P2c **biến "circularity" từ lỗ hổng thành KẾT QUẢ**.
> - **Fallback graded (thay cho fallback nhị phân):** báo cáo `k*` = giá trị k lớn nhất mà hit_rate ≥ 0,99 với mọi thuật toán. Nếu k* < 10 ⇒ **preregister NGAY câu này**: *"metaheuristic chỉ bắt đầu hụt ở k > k*, tức là ở vùng mà theo P1 mask KHÔNG ĐỔI ⇒ chúng hụt ở nơi không ai quan tâm"* — **đó là kết quả MẠNH HƠN, không phải một thất bại**.

**(c) TOST — SESOI lấy từ dữ liệu đã tuyên bố vô hiệu, và power CHƯA BAO GIỜ ĐƯỢC TÍNH.**
§3 biện minh SESOI = 0,01 bằng *"chênh lệch Dice giữa các thuật toán trong lô cũ ~0,05"* — trong khi §0 và §5 tuyên bố **"không dùng lại bất kỳ con số nào từ `c4fe108`"**. **Mâu thuẫn nội tại.** Và power chưa từng được tính: với n=150, Δ=0,01, power ≥ 80% **chỉ khi** $SD_d \lesssim 0{,}042$; **power ≈ 0 khi $SD_d \gtrsim 0{,}074$**. Δ pilot (PSO−QIGOA) = **0,009 Dice = 90% nửa bề rộng ROPE** ⇒ power ước tính **0,08–0,34** ⇒ §7 *"R3 — The Quantum Component Contributes Nothing"* có **~1/6 cơ hội** chứng minh được.

> **✅ SỬA (khoá):**
> 1. **SESOI đổi nguồn** — **anchor-based**: neo vào **biến thiên liên-quan-sát-viên** của WT delineation trên BraTS (Menze et al., IEEE TMI 2015). Lập luận không phản bác được: *bất kỳ khác biệt nào nhỏ hơn mức bất đồng giữa hai bác sĩ đều không thể có ý nghĩa lâm sàng.* **BẮT BUỘC web-verify con số trước khi khoá.** Hoặc **cost-based**: *"mức tăng Dice nhỏ nhất đủ biện minh cho chi phí compute cao hơn **X lần về NFE**"* — trong đó **X đo được từ chính lưới thí nghiệm**, khai báo được 100% a priori. ⚠️ **KHÔNG dùng con số "250×"** — nó chưa ai đo và là artifact wall-clock của Python (xem A0). **Bỏ hoàn toàn biện minh từ lô cũ.**
> 2. **Khai báo hierarchy 3 bound trước:** Δ₁ = 0,01 (strict, primary) · Δ₂ = inter-rater-derived (secondary) · Δ₃ = 0,05 (lenient). **Báo cáo cả ba, luôn luôn.**
> 3. **★ ĐỔI CÁCH BÁO CÁO — de-risk quan trọng nhất:** thay "TOST pass/fail" bằng **90% CI của hiệu theo cặp** (TOST ↔ **90%** CI, không phải 95%) **+ `Δ_ach`** = equivalence bound **nhỏ nhất** mà tại đó tương đương được tuyên bố ở α=0,05. Rồi viết: *"Equivalence holds for any SESOI ≥ Δ_ach = X."* **Phân tích này KHÔNG BAO GIỜ "fail"** — nó luôn trả về một con số. ⇒ **rủi ro FATAL này về cơ bản biến mất.**
> 4. **Nâng Bayesian signed-rank + ROPE (Benavoli et al., JMLR 2017) lên PRIMARY**; TOST làm frequentist companion. Bayesian ROPE **không có khái niệm "fail"**, xử lý ties (spike tại 0) tự nhiên.
> 5. **Preregister nhánh NGƯỢC:** nếu QIGOA thực sự **TỆ HƠN** PSO 0,009 Dice ⇒ đó là **superiority test chiều ngược**, một finding tốt, không cần TOST.

**(d) 🔴 BẪY `scipy` — sẽ ÂM THẦM VỨT ĐI CHÍNH KẾT QUẢ CỦA BÀI.**
Theo P1, hai thuật toán cùng tìm ra $t_k$ giống nhau ⇒ mask **giống hệt bit-for-bit** ⇒ $d_i = 0$ **CHÍNH XÁC**. `scipy.stats.wilcoxon` mặc định `zero_method='wilcox'` — **LOẠI BỎ TOÀN BỘ các cặp bằng 0**. Hậu quả: n hiệu dụng tụt 150 → ~30; test biến thành phát biểu **chỉ về nhóm thiểu số nơi hai thuật toán bất đồng** (**ngược hoàn toàn thông điệp**); và nó có thể **tự sinh một "significance" giả** — **đúng cái tội bài đang tố cáo dòng văn liệu**.
> **✅ KHOÁ:** `zero_method='pratt'`. **Báo cáo `n_zero / n_total` trong MỌI bảng so sánh cặp.** Con số *"trên X/150 bệnh nhân, QIGOA và PSO cho ra mask GIỐNG HỆT NHAU"* **chính là cả bài báo gói trong một phân số**.

**(e) Định nghĩa FAMILY cho Holm** (hiện "Holm" là một từ trống; ~4.620 test khả dĩ):

| Family | Loại | Hiệu chỉnh |
|---|---|---|
| **A** — superiority (P4) | 1 test | không cần |
| **B** — trend (P3 primary + secondary) | 2 test | **Holm trong family** |
| **C** — equivalence (TOST, tại **MỘT k primary**) | 8 test | **⚠️ TOST là intersection–union test ⇒ KHÔNG hiệu chỉnh.** Holm-correct chúng chỉ báo hiệu tác giả không hiểu công cụ |
| **D** — mọi thứ còn lại | ~4.600 | **dán nhãn EXPLORATORY**, báo effect size + CI, **không dùng p-value để claim** |

**Khoá 3 bậc tự do:** **k primary = 4** · **decoding rule primary = `brightest`** (đó là rule ta sẽ *kiểm tra*, không phải rule ta *quy kết* — xem A1) · **thuật toán reference cho TOST = DP-exact**.
**MỘT primary endpoint cho MỖI mệnh đề.** *(Preregistration có nhiều endpoint = preregistration không có endpoint.)*

---

#### A5 · SỬA HAI CỔNG CỨNG ĐANG SAI ⚠️ MAJOR

**(a) Cổng "DP khớp BIT-EXACT với vét cạn" (§1/P2, dòng 63) SẼ FAIL VÌ LÝ DO VÔ NGHĨA.** Với số thực dấu phẩy động, thứ tự cộng khác nhau ⇒ khác bit. Tệ hơn: lát BraTS **đã skull-strip** ⇒ ~65% pixel ở cường độ 0 và nhiều mức xám **rỗng** ⇒ dưới quy ước `0·log0 := 0`, lớp rỗng đóng góp 0 entropy ⇒ **argmax của Kapur KHÔNG DUY NHẤT** (kiểm chứng dựng: tại k=2 có thể có nhiều tập ngưỡng tối ưu khác nhau → nhiều `t_max` khác nhau → **nhiều MASK khác nhau với Dice khác nhau**).
> **✅ Đổi thành:** `|f_DP − f_brute| ≤ 1e-9` **VÀ** mask cảm sinh giống hệt, với **ngưỡng canonicalise** (snap về mức xám thấp nhất cho cùng phân hoạch).

**(b) Cờ đỏ (e) — *"relative_gap âm ⇒ DP sai"* (§1/P2 dòng 60; §4 dòng 159) LÀ SAI và SẼ ĐỐT NHIỀU NGÀY DEBUG.** Nguyên nhân thực tế gần như chắc chắn là **LỆCH TẬP KHẢ THI** (metaheuristic dùng ngưỡng liên tục/làm tròn/trùng lặp; hoặc quy ước `0log0` / lớp rỗng / có-hay-không tính nền khác nhau), **không phải bug DP**.
> **✅ Bước debug ĐẦU TIÊN = audit quy ước, KHÔNG phải debug DP.**

**(c) Khai báo TƯỜNG MINH (trước khi chạy):** quy ước `0log0` · lớp rỗng có được phép không · ngưỡng trùng repair thế nào · **và quan trọng nhất: CÓ TÍNH NỀN CƯỜNG-ĐỘ-0 VÀO HISTOGRAM HAY KHÔNG** (lựa chọn này **đổi hoàn toàn** ngưỡng tối ưu, Dice, và mọi số PSNR/SSIM — đây là một bug kinh điển của chính dòng văn liệu này). **Chạy cả hai biến thể, báo cáo cả hai.**

**(d) BUG trong `base.py` đã đặc tả** (`ke-hoach-trien-khai.md:101–116`): `evaluate()` ném `BudgetExhausted` **TRƯỚC** khi trả giá trị, nhưng thuật toán cập nhật `best_x/best_f` **SAU** khi `evaluate()` trả về ⇒ khi exception bắn giữa generation, **cải thiện của generation dở dang bị VỨT ÂM THẦM**, và mỗi thuật toán mất một lượng khác nhau tuỳ vị trí trong vòng lặp ⇒ **thiên lệch so sánh không kiểm soát được**.
> **✅ Sửa:** cho **chính `evaluate()`** cập nhật incumbent (nó đã là cổng duy nhất).

---

#### A6 · PHÁ VÒNG TRÒN LOGIC Ở VALIDATION IMPLEMENTATION ⚠️ MAJOR

**Lý do.** Tiêu chí ta dùng để tuyên bố GOA "hỏng" là *nó không đạt gần nghiệm tối ưu*. Nhưng *"mọi thuật toán đạt gần tối ưu"* **CHÍNH LÀ P2**. ⇒ Bất kỳ metaheuristic nào **không** đạt 99,99% sẽ tự động bị dán nhãn "bug" và **loại khỏi mẫu** ⇒ **P2 không thể bị dữ liệu bác bỏ**, vi phạm đúng nguyên tắc falsifiability mà preregistration này tự đặt ra.

> **✅ CỔNG CỨNG MỚI (E1b, tuần 1 — trước khi chạy lưới chính):** tính đúng đắn của implementation phải được xác lập trên một benchmark **ĐỘC LẬP với bài toán thresholding**: tái tạo bảng Kapur/Otsu multilevel **đã công bố** trên ảnh chuẩn (Lena/Cameraman/Baboon/Peppers, k=2..5) ở **đúng NFE đã công bố**, cho **MỌI** thuật toán, khớp trong sai số đã báo. **Chỉ sau khi qua cổng này**, hit-rate-to-DP mới được dùng làm *kết quả*.
> **Equal TUNING budget**, không chỉ equal NFE — lợi thế biểu kiến trong lĩnh vực này gần như luôn đến từ **tuning lệch**.
> **Loại trừ ex ante khách quan** thay cho loại-trừ-bằng-tên: *"any implementation failing to reproduce its published benchmark table within X% is excluded and reported separately."*
> Cài QIGOA theo **từng phương trình từ một NGUỒN CÔNG BỐ CÓ TÊN**, cite trên từng phương trình.
> Công bố **convergence curve + boxplot per-seed** cho mọi thuật toán (phụ lục) — cách rẻ nhất để reviewer tự phát hiện một implementation hỏng.

---

#### A7 · QUY ƯỚC METRIC + MASK SUY BIẾN — KHOÁ TRƯỚC KHI CHẠY ⚠️ MAJOR

- **NSD chưa khai báo tolerance τ** ⇒ lỗ HARKing. **Khoá: τ = 2 mm primary**, sensitivity {1, 3, 5} mm; nêu rõ khoảng cách tính **in-plane** (BraTS 1 mm isotropic) và **nêu tên implementation cụ thể**. *(Một bài audit metric mà dùng implementation không nêu tên thì lặp đúng tội "FSIM tự chế" của lô cũ.)*
- **Mask rỗng SẼ xảy ra** (k tăng ⇒ `t_k` tăng ⇒ mask teo về rỗng). **HD95 của mask rỗng là UNDEFINED**, và ba cách xử lý thông dụng cho **ba bài báo khác nhau**. **Khoá:** GT≠rỗng + pred rỗng ⇒ Dice = 0, HD95 = **hình phạt cố định đã khai** (đường chéo ảnh, ghi số cụ thể); cả hai rỗng ⇒ Dice = 1, HD95 = 0.
  > 🔴 **CẤM âm thầm loại ca mask rỗng khỏi thống kê HD95** — làm vậy là **selection bias có lợi cho thresholding, đúng tại k lớn**, tức là **phá hỏng chính P3**.
  > ✅ **Báo cáo `empty-mask rate` theo k như một KẾT QUẢ ĐỘC LẬP** — nó là một trong những bằng chứng đẹp nhất cho P3 mà kế hoạch đang bỏ phí.
- **BỎ IoU** (song ánh đơn điệu với Dice: `IoU = D/(2−D)` ⇒ **không thêm một bit thông tin nào**).
- **✅ THÊM (miễn phí, và có thể là con số thuyết phục nhất về mặt lâm sàng): SỐ THÀNH PHẦN LIÊN THÔNG** của mask dự đoán. *"Output thresholding trung vị có N thành phần liên thông; khối u có 1."* Không cần lý thuyết metric, không cần thống kê, **không phản bác được**.
- **mean ± std là cách trình bày SAI cho Dice** (bị chặn [0,1], lệch mạnh, thường bimodal). **Khoá: median [IQR] + 95% bootstrap CI + hình phân bố per-patient.**

---

#### A8 · CỠ MẪU + "NGOẠI KIỂM" LGG ⚠️ MAJOR

- **Quy tắc chọn 150/369 bệnh nhân CHƯA HỀ ĐƯỢC KHAI BÁO** (§2 chỉ khai quy tắc chọn **lát**) ⇒ lỗ selection-bias mở toang. **Và n=150 là hy sinh power VÔ CỚ:** n=369 nâng ngưỡng 80%-power của $SD_d$ từ **0,042 → 0,066** và vách sụp từ **0,074 → 0,117** ⇒ **de-risk TRỰC TIẾP lỗi TOST ở A4(c)**.
  > ✅ **Dùng cả 369 ca.** Oracle chạy trên **histogram** (~ms/ảnh), **không phải "~30 s/ảnh"** như kế hoạch ghi nhầm (sai 4 bậc độ lớn). Cắt lưới algorithm×seed×k nếu cần, **đừng cắt n**. Commit `data/splits/brats_cohort.csv` (`patient_id, slice_idx, wt_area, grade, sha256, split`).
- 🔴 **"NGOẠI KIỂM" LGG CÓ THỂ KHÔNG NGOẠI — RỦI RO LIÊM CHÍNH.** Buda et al. = **110 bệnh nhân TCGA-LGG (TCIA)**. BraTS 2020 đã đưa vào **108 ca TCGA-LGG** từ **đúng collection đó** (CBICA phát hành `name_mapping.csv` để ánh xạ ID BraTS ↔ TCGA). ⇒ *"khác cơ sở, khác máy chụp"* rất có thể là **CÙNG NHÓM BỆNH NHÂN**.
  > ✅ **BẮT BUỘC trước khi dùng chữ "external validation":** tải `name_mapping.csv`, đối chiếu, **báo cáo số trùng bằng con số**. Rồi chọn: **(a)** loại các BN trùng; **(b)** giữ nhưng **gọi đúng tên** — *"annotation/preprocessing replication on an overlapping cohort"*; hoặc **(c)** ngoại kiểm theo **chiều TASK** (tune trên WT/FLAIR, test trên **ET/T1ce**) — **rẻ nhất và mạnh nhất**, và trùng khớp với A2.
  > ⚠️ Nếu gọi là ngoại kiểm mà thực chất trùng bệnh nhân, và reviewer BraTS bắt được, thì đó **không còn là lỗi thiết kế — nó đọc như MISREPRESENTATION**.
- **Bẫy kỹ thuật LGG:** ảnh Kaggle LGG là **TIFF 3 kênh** (pre-contrast / FLAIR / post-contrast), **không phải** FLAIR đơn kênh. Lấy nhầm kênh ⇒ histogram sai ⇒ toàn bộ Kapur/DP sai. `lgg_loader.py` **phải có unit test** cho việc này.

---

#### A9 · TIMESTAMP NGOÀI CHO PREREGISTRATION ⚠️ MINOR nhưng đòn bẩy cao nhất

File này hiện có trường **"Commit khi khoá" ĐỂ TRỐNG** (dòng 4), và **git history rewrite được**. Với một bài mà **toàn bộ vốn liếng là uy tín phương pháp luận**, câu *"chúng tôi đã preregister"* mà **không verify được** là một lỗ hổng chết người — reviewer sẽ vặn đúng chỗ đó.

> ✅ **Đăng ký OSF (miễn phí) HOẶC archive lên Zenodo lấy DOI có timestamp bên thứ ba. Cite DOI đó trong Abstract.** Và **điền cái commit hash vào**.

**Và một sự trung thực bắt buộc về bản chất của file này:** P1 và P3 **được phát hiện exploratorily trên một pipeline có lỗi**, và SESOI ban đầu **được suy ra từ chính lô đó**. ⇒ File này **không phải** preregistration theo nghĩa chặt. **Gọi đúng tên trong bản thảo:**

> *"Confirmatory analysis protocol for exploratory findings — P1/P3 were discovered exploratorily on a flawed pipeline; this protocol pre-specifies the confirmatory re-analysis."*

**Bị bắt vì dán nhãn sai một preregistration còn tệ hơn nhiều so với không có preregistration.**

---

#### A10 · ĐẢO NGƯỢC THỨ TỰ THÍ NGHIỆM — chi compute đang ngược ⚠️ MAJOR

Kế hoạch hiện chi **~35/40 giờ** cho các thí nghiệm có **xác suất bất ngờ ≈ 0** (E2 chỉ fail nếu code có bug; *"U-Net thắng thresholding"* đã biết từ 2015), và xếp **cả bốn câu hỏi thật sự bất định** vào mục "làm sau". **Đó là dấu vân tay của confirmation bias — trong một bài đi tố cáo người khác confirmation bias.**

> **✅ TUẦN 1 = BỐN THÍ NGHIỆM RỦI RO (tổng ~10 h compute + 1 tuần khảo sát):**
> 1. **Bảng I** — trắc lượng thư mục có mã hoá (search string, PRISMA-lite, **2 coder, Cohen's κ**). *Quyết định: P1 có mục tiêu, hay là strawman?* **0 compute.**
> 2. **Bậc 5** — ngưỡng 1-tham-số vs 7 metaheuristic, **nested CV**. *Quyết định: bài có đóng góp dương không?* **~1 h.** ⚠️ **PHẢI preregister như P5 kèm fallback** (hiện **không có trong preregistration**, trong khi kế hoạch gọi nó là *"thứ biến bài từ negative result thành bài đăng được"*). **Fallback:** nếu thua ⇒ đóng góp dương rơi về **ceiling decomposition + công cụ chẩn đoán + checklist** (ba thứ này **phải đủ đứng một mình** — xác nhận điều đó **bây giờ**, không phải sau 4 tuần).
> 3. **Spearman(k, Dice) tính RIÊNG cho từng decoding rule** (~1 h). *Quyết định: P3 là "metric sai" hay chỉ là "decoder sai"?* Nếu tương quan âm **chỉ tồn tại dưới rule `brightest`** ⇒ headline *"metrics are anti-correlated"* **SAI**, và bài thật ra là *"một decoding rule có bias theo k"* — nhỏ hơn nhiều.
> 4. **`morph` vs `oracle_interval`** (~1 h). Nếu morph **vượt** oracle ⇒ **P4 tự bác bỏ**.
>
> **Nếu cả bốn sống sót → khi đó mới đáng chi 20 giờ cho E2.** Nếu một trong bốn chết → **đã tiết kiệm 8 tuần.**

**+ CỔNG TUẦN 0 (đọc toàn văn, trước khi chạy bất cứ gì):** Mousavirad (KBS 2023) · François & Tinarrage (JMIV 2026) · Hegazy & Gabr (arXiv:2605.27132 **và** 2605.27287) · Menotti (CIARP 2015) · Hammouche (EAAI 2010) · Al-Najdawi (Sci Rep 2025). **Không chạy E2 trước khi cả sáu đã đọc và có đoạn định vị viết sẵn.**

# Đề xuất điều chỉnh hướng paper QIGOA

**Người trình bày:** Nguyễn Võ Hoàng Long
**Kính gửi:** TS. Đỗ Phúc Hảo
**Ngày:** 13/07/2026
**Nội dung:** Xin phép giữ nguyên QIGOA làm nhân vật trung tâm, nhưng **đổi câu hỏi nghiên cứu** — từ *"QIGOA có thắng không"* sang *"QIGOA có thực sự giúp không, và ta đang đo đúng thứ chưa"*.

---

## 1. Tóm tắt trong một đoạn

Em đã chạy xong bộ thí nghiệm đầu tiên theo đúng đề thầy giao (Kapur entropy, Q-bit + rotation gate, so với GA/PSO/GOA/GWO/WOA/MPA, trên BraTS). Khi đọc kỹ số liệu, ba sự thật hiện ra và **cả ba đều bác bỏ claim "QIGOA vượt trội"**. Nếu em vẫn viết bài theo hướng cũ, reviewer chỉ cần một buổi chiều là lật được toàn bộ. Vì vậy em đề xuất chuyển sang một bài **reality-check nghiêm cẩn kèm đóng góp dương** — đúng công thức thầy đã đúc kết trong playbook IEEE của thầy: *"Một kết quả âm được làm nghiêm cẩn, cộng một đóng góp dương, là một bài đăng được. Một kết quả dương bịa ra là một lần reject cộng mất uy tín."* ([lam-va-viet-paper-chuan-IEEE.md:209](lam-va-viet-paper-chuan-IEEE.md#L209))

Toàn bộ QIGOA, Kapur, Q-bit, rotation gate, và bảng so sánh 7 thuật toán **vẫn nằm nguyên trong bài**. Chỉ khác: chúng phục vụ một luận điểm *không thể bị bác*, thay vì một luận điểm *sẽ bị bác*.

---

## 2. Ba sự thật từ số liệu

> ⚠️ **Ghi chú về nguồn số:** các con số dưới đây lấy từ lô thí nghiệm đầu tiên (25.200 run). Chúng là **bằng chứng chẩn đoán** — dùng để chỉ ra vấn đề, **không phải kết quả để công bố**. Lô này có ba lỗi cài đặt (nêu ở §5), nên toàn bộ sẽ được chạy lại từ pipeline sạch trước khi bất kỳ con số nào lên bản thảo.

### 2.1 QIGOA đang được cấp thêm 13,4% ngân sách so với mọi baseline

| Thuật toán | Số lần đánh giá hàm mục tiêu (NFE), trung bình |
|---|---|
| GA, PSO, GOA, GWO, WOA, MPA | **7.550** (đúng bằng nhau) |
| **QIGOA** | **8.563** |

Nguyên nhân: bước *memetic refinement* (và OBL, Lévy flight) có gọi hàm mục tiêu nhưng **không bị trừ vào ngân sách**. Nghĩa là QIGOA đang chạy một cuộc đua mà nó được thêm 13,4% thời gian, còn các đối thủ thì không.

Đây chính xác là điều thầy đã viết ở [lam-va-viet-paper-chuan-IEEE.md:15](lam-va-viet-paper-chuan-IEEE.md#L15):

> *"Một tuyên bố lợi thế hấp dẫn nhưng mong manh, qua từng lớp nghiêm cẩn... đã hội tụ về sự thật: **lợi thế biểu kiến không đến từ thành phần mới**."*

Và ở [:163](lam-va-viet-paper-chuan-IEEE.md#L163): *"Dựng baseline chỉ khác đúng X... Nếu một baseline cổ điển ngang X, lợi ích không đến từ X."* Ở đây ta thậm chí chưa cùng ngân sách — nên chưa có quyền so sánh gì cả.

### 2.2 Tối ưu càng giỏi thì phân đoạn càng tệ

Trung bình trên mọi thuật toán, khi tăng số ngưỡng k:

| k | Kapur fitness | PSNR (dB) | SSIM | **Dice** |
|---|---|---|---|---|
| 2 | 9,61 | 18,86 | 0,772 | **0,664** |
| 4 | 15,82 | 27,96 | 0,970 | **0,675** ← đỉnh |
| 6 | 21,42 | 32,06 | 0,992 | 0,579 |
| 8 | 26,36 | 34,43 | 0,995 | 0,500 |
| 10 | 30,81 | 36,19 | **0,997** | **0,437** |

`Spearman(k, Dice) = −0,893` (p = 0,007).

Hàm mục tiêu tăng đơn điệu, PSNR tăng đơn điệu, SSIM tiến sát 1,0 — **còn Dice sụp 34%**. Nghĩa là:

> **Ba thước đo mà cả dòng văn liệu đang dùng (fitness, PSNR, SSIM) phản chỉ báo chất lượng lâm sàng.**

Hệ quả trực tiếp: nếu chọn k bằng PSNR, ta chọn k=10. Nếu chọn bằng Dice, ta chọn k=4. **Chọn model bằng PSNR chủ động làm hại bệnh nhân.**

Đây là một finding thật, và nó có nền chuẩn tắc: *Metrics Reloaded* (Nature Methods 2024, `10.1038/s41592-023-02151-z`) nói rõ segmentation phải đo bằng Dice/IoU + HD95/NSD; PSNR/SSIM là metric *reconstruction*. Metric chính thức của chính BraTS challenge là lesion-wise Dice + HD95, không có PSNR/SSIM.

### 2.3 Phát hiện quan trọng nhất — suy biến cấu trúc

Trong pipeline, mask khối u được tạo bằng quy tắc "lấy lớp sáng nhất":

```python
def segmentation_to_binary(seg, tumor_class=None):
    if tumor_class is None:
        tumor_class = int(seg.max())
    return (seg == tumor_class).astype(np.uint8)
```

Nghĩa là mask = `{pixel > t_max}` — **chỉ phụ thuộc ngưỡng LỚN NHẤT**. Còn k−1 ngưỡng kia? Không ảnh hưởng gì.

Em kiểm chứng trên toàn bộ 25.200 run: nhóm các run theo cặp `(ảnh, t_max)`, rồi xem Dice có thay đổi không.

```
Số nhóm (ảnh, t_max):                                    2.576
Số nhóm có Dice HẰNG SỐ — bất kể k, bất kể thuật toán:   2.576 / 2.576
Độ lệch chuẩn Dice lớn nhất trong một nhóm:              0,00e+00
```

**2.576 trên 2.576. Không một ngoại lệ. Độ lệch chuẩn đúng bằng không.**

Hệ quả, phát biểu được thành một mệnh đề:

> **Mệnh đề.** Với quy tắc decoding mà cả dòng văn liệu đang dùng, mask lâm sàng là hàm của **đúng một** trong k ngưỡng. k−1 biến còn lại là **biến giả** (decoy variables).
>
> Tổng quát hơn: với *bất kỳ* quy tắc nào chọn một dải lớp cường độ liên tiếp làm mask, mask được xác định bởi **nhiều nhất 2** ngưỡng — **bất kể k lớn bao nhiêu**.

Nói cách khác: **toàn bộ máy móc Q-bit, quantum rotation gate, Lévy flight, memetic refinement, và social term của GOA đang tranh nhau tối ưu những biến không ảnh hưởng tới kết quả lâm sàng.** Không gian tìm kiếm thực sự có ích chỉ là 1 chiều với 254 giá trị — vét cạn trong vài mili-giây.

Điều này *giải thích* §2.2: khi k tăng, thuật toán đẩy t_max lên cao hơn → mask teo lại → Dice sụp. Fitness vẫn tăng vì nó đo entropy của toàn bộ phân hoạch, không đo khối u.

### 2.4 Và kết cục: QIGOA bị PSO thống trị

Tại k=10 — dù được cấp thêm 13,4% ngân sách:

| | Kapur fitness | Dice | Thời gian (s) |
|---|---|---|---|
| PSO | **31,137** | **0,453** | **1,80** |
| QIGOA | 31,108 | 0,444 | 2,44 |

QIGOA **thua cả ba chiều**: fitness thấp hơn, Dice thấp hơn, chậm hơn 36%. Kiểm định Wilcoxon ở k=10 vs PSO: thắng 1 / hoà 17 / **thua 22**.

"Chiến thắng" duy nhất của QIGOA là thắng **GOA gốc** (p < 1e-7 ở cả 10 cấu hình) — nhưng GOA gốc có tỷ lệ đạt nghiệm tốt nhất **0% ở mọi k ≥ 3**, trong khi mọi thuật toán khác đạt ≥ 96%. Một baseline có hit-rate 0% không phải baseline, đó là một **con bug**. Ta đang so với một lỗi cài đặt, không phải với SOTA.

---

## 3. Vì sao hướng cũ không nộp journal được (ngoài chuyện số liệu)

Em đã tra cứu kỹ (mọi mục dưới đây đều có DOI, verify được):

| Vấn đề | Bằng chứng |
|---|---|
| **Sai venue.** IEEE JBHI là tạp chí *health informatics*, có điều khoản desk-reject "does not fit the scope"; em không tìm thấy bài metaheuristic-thresholding nào từng đăng ở JBHI. | [JBHI Editorial Policy](https://www.embs.org/jbhi/editorial-policy/) |
| **"Quantum Grasshopper Optimization" đã tồn tại.** | *A novel quantum grasshopper optimization algorithm*, Int. J. Approximate Reasoning 127:33–53 (2020), Q1. DOI `10.1016/j.ijar.2020.08.011` |
| **QI-metaheuristic + Kapur + multilevel thresholding đã xong từ 2016–2017**, và nhóm Dey/Bhattacharyya/Maulik có hẳn **một cuốn sách Wiley 2019** về đúng chủ đề. | Applied Soft Computing 46:677–702 (2016); 56:472–513 (2017) |
| **Near-scoop 2025:** quantum + entropy thresholding + brain MRI. | *Alzheimer's disease brain image segmentation using 3D Rényi entropy and quantum hybrid optimization*, Artificial Intelligence Review (2025), Q1. DOI `10.1007/s10462-025-11438-w` |
| **QIEA đã bị chứng minh chỉ là một EDA** (Estimation of Distribution Algorithm) — Q-bit + rotation gate về mặt toán học là một vector xác suất + luật cập nhật xác suất. Không có superposition/entanglement thật. | Platel, Schliebs, Kasabov, **IEEE Trans. Evolutionary Computation** 13(6):1218–1232 (2009). DOI `10.1109/TEVC.2008.2003010` |
| **Không có quantum advantage** khi chạy trên phần cứng cổ điển. | Tang, *A quantum-inspired classical algorithm for recommendation systems*, STOC 2019, arXiv:1807.04271 |
| **Phong trào chống metaphor-based metaheuristic đang mạnh.** Journal of Heuristics và 4OR đã có **policy từ chối**. | Sörensen, ITOR 2015 (`10.1111/itor.12001`); Aranha et al., Swarm Intelligence 2022 (`10.1007/s11721-021-00202-9`); Camacho-Villalón et al., ITOR 2023 (`10.1111/itor.13176`) |
| **GOA bị chứng minh chỉ là biến thể PSO.** *[cần verify lại nguyên văn trước khi trích]* | Springer 2024, `10.1007/978-3-031-70932-6_7` — hiện mới đọc được qua search snippet, chưa fetch được toàn văn |

Nói thẳng: đề tài hiện tại là một **hoán vị** — thay PSO/DE/ABC bằng GOA trong một template đã có từ 2014. Reviewer sẽ hỏi *"Tại sao GOA? Kết quả này khác gì suy ra từ Dey 2017 + QGOA 2020?"* — và ta không có câu trả lời.

---

## 4. Đề xuất: đổi câu hỏi, giữ nguyên nhân vật

**Tên bài đề xuất:**
> *Optimizing the Wrong Variable: Structural Degeneracy in Metaheuristic and Quantum-Inspired Multilevel Thresholding for Brain Tumor Segmentation*

**Bốn mệnh đề — mỗi mệnh đề đều có thể bị bác bỏ bằng một thí nghiệm cụ thể** (đúng tinh thần [:239](lam-va-viet-paper-chuan-IEEE.md#L239): *"Evaluation là phép thử bác bỏ... khác biệt giữa 'chứng minh tôi đúng' và 'cố gắng chứng minh tôi sai, và thất bại'"*):

- **P1 — Suy biến.** Mask lâm sàng phụ thuộc ≤ 2 trong k ngưỡng, bất kể k. *Bác bỏ được nếu:* tìm ra một nhóm `(ảnh, dải-lớp)` có Dice không hằng số.
- **P2 — Không còn gì để tối ưu.** Với ngân sách bằng nhau, mọi metaheuristic đạt ≥ 99,99% nghiệm tối ưu **chính xác** (tính được bằng quy hoạch động trong mili-giây). *Bác bỏ được nếu:* có thuật toán nào vượt nghiệm chính xác — điều bất khả.
- **P3 — Goodhart.** fitness/PSNR/SSIM tăng theo k trong khi Dice/HD95 xấu đi. *Bác bỏ được nếu:* tương quan hoá ra dương.
- **P4 — Trần.** Oracle vét cạn trên mọi mask-một-khoảng là trần đúng của MỌI phương pháp thresholding cường độ. Một 2D U-Net trên **đúng cùng input** vượt trần đó. *Bác bỏ được nếu:* có thresholding nào vượt oracle — điều bất khả theo định nghĩa.

**Đóng góp DƯƠNG** (phần "Positive" trong công thức reframe của thầy ở [:213](lam-va-viet-paper-chuan-IEEE.md#L213)):
1. Một **bộ giải chính xác mili-giây, 1 tham số**, đánh bại cả 7 metaheuristic — nhanh hơn ~250 lần.
2. Một **checklist giao thức đánh giá** cho dòng văn liệu này: đo Dice/HD95, báo cáo decoding rule, ngân sách NFE bằng nhau, thống kê ở cấp bệnh nhân.

**Và bài trả lời TRỰC DIỆN câu hỏi thầy giao:** *thành phần quantum-inspired đóng góp bao nhiêu?* — bằng một ablation `full / −quantum / −memetic / −OBL / −Lévy` trên dữ liệu BraTS thật, cùng ngân sách. Đây là điều bản cũ chưa hề có (nó chỉ ablate trên ảnh phantom tổng hợp).

---

## 5. Ba lỗi cài đặt phải sửa — và em sẽ viết lại pipeline từ đầu

1. **Ngân sách NFE không công bằng.** Sẽ đặt *hard budget*: mọi thuật toán dừng đúng khi hết ngân sách; memetic/OBL/Lévy của QIGOA **đếm vào** ngân sách.
2. **Baseline GOA hỏng** (hit-rate 0%). Sẽ debug, và báo cáo **cả hai** phiên bản — như một bài học phương pháp luận: *một baseline lỗi sinh ra "significance" giả trên cả 10 cấu hình*.
3. **Metric tự chế.** SSIM trong code cũ là global-SSIM (không phải sliding-window của Wang et al.); FSIM tự thú trong docstring là "not the full FSIM". Một bài phê phán metric mà dùng metric tự chế thì tự sát. Sẽ dùng `skimage` / `MedPy`.

Thêm: dữ liệu cũ lấy **3 lát/bệnh nhân** rồi đưa vào Wilcoxon như mẫu độc lập → *pseudo-replication*. Sẽ sửa: **1 lát / 1 bệnh nhân, n = 150**, mọi kiểm định ở cấp bệnh nhân.

---

## 6. Định vị trung thực với văn liệu (§6.5 playbook của thầy)

Bài toán tối ưu Kapur **đã có lời giải chính xác** — em **không** claim đó là đóng góp của mình, và sẽ trích trang trọng ngay ở Abstract:

- Luessi et al., *Framework for efficient optimal multilevel image thresholding*, J. Electronic Imaging 18(1):013004 (2009)
- **Merzban & Elbayoumi**, *Efficient solution of Otsu multilevel image thresholding: A comparative study*, **Expert Systems with Applications** 116:299–309 (2019)

Đóng góp của em là **thứ họ không có**: họ dùng ảnh tự nhiên **không có ground truth**, nên *không thể* phát hiện suy biến metric. Em có ground truth lâm sàng → phát hiện được **P1, P3, P4**, và audit được nhánh quantum-inspired.

Đúng như thầy viết ở [:249](lam-va-viet-paper-chuan-IEEE.md#L249): *"Một câu định vị thẳng thắn mạnh hơn mười câu tự khen."*

---

## 7. Venue & lộ trình

| | Venue | Lý do |
|---|---|---|
| **Chính** | **Biomedical Signal Processing and Control** (Elsevier, Q1/Q2, IF ≈ 4,9, **không APC**) | Đây *chính là* tạp chí đang xuất bản dòng văn liệu bị audit → tác động cao nhất, scope khớp |
| **Dự phòng 1** | **Expert Systems with Applications** (Elsevier, Q1) | Có **tiền lệ trực tiếp**: ESWA đã đăng Merzban 2019 — đúng thể loại "exact thắng metaheuristic" |
| **Dự phòng 2** | JCC (VAST) hoặc hội nghị Scopus (SoICT/KSE/NICS) | Lưới an toàn |

**Không nộp:** IEEE JBHI (desk-reject out-of-scope). **Cấm:** Multimedia Tools & Applications, J. Ambient Intelligence — **đã bị Clarivate delist khỏi Web of Science**.

**Lộ trình:** ~8 tuần. Compute ≈ 40 giờ CPU Kaggle + 2 giờ GPU — nằm gọn trong hạn mức miễn phí. *Nút thắt là lập luận và viết, không phải compute.*

---

## 8. Xin ý kiến thầy

Thưa thầy, em xin phép hỏi ba điều:

1. **Thầy có đồng ý đổi câu hỏi nghiên cứu** như §4 không? QIGOA vẫn là nhân vật trung tâm, Kapur/Q-bit/rotation gate vẫn nguyên, bảng so 7 thuật toán vẫn nguyên — chỉ khác là chúng phục vụ một luận điểm đứng vững được.
2. **Về venue:** em đề xuất BSPC làm đích chính thay cho JBHI. Thầy thấy có hợp lý không?
3. **Mệnh đề P1** (suy biến) là đóng góp lý thuyết mạnh nhất của bài. Em muốn nhờ thầy kiểm tra lại phát biểu và chứng minh trước khi em xây toàn bộ phần thực nghiệm quanh nó.

Em cảm ơn thầy.

---

### Phụ lục — nguồn của mọi con số trong tài liệu này

Mọi con số ở §2 tính trực tiếp từ `raw_A_kapur_standard.csv` (16.800 run) và `raw_B_kapur_highk.csv` (8.400 run) trong commit `c4fe108` của repo. Script kiểm chứng suy biến (§2.3) chỉ 6 dòng và sẽ được đưa vào repo dưới dạng unit test. **Không con số nào trong tài liệu này được lấy từ trí nhớ hoặc ước lượng.**

---
title: "Hướng triển khai bài báo QIGOA"
subtitle: "Luận điểm, thiết kế nghiên cứu, cấu trúc bản thảo và chiến lược công bố"
author:
  - "Nguyễn Võ Hoàng Long"
  - "Hướng dẫn: TS. Đỗ Phúc Hảo — Khoa Công nghệ Thông tin, Trường Đại học Kiến trúc Đà Nẵng"
date: "13/07/2026"
lang: vi
---

# 1. Bài báo này nói gì

## 1.1 Một câu

> Trong phân đoạn u não bằng multilevel thresholding, các thuật toán metaheuristic — kể cả biến thể quantum-inspired — đang **tối ưu một biến không ảnh hưởng tới kết quả lâm sàng**, trên một **bài toán đã có lời giải chính xác**, và được đánh giá bằng **thước đo phản chỉ báo** chất lượng phân đoạn.

## 1.2 Bài báo giữ gì và đổi gì so với đề thầy giao

Đề gốc: *"Multilevel Image Thresholding for Brain Tumor Segmentation using Quantum-Inspired Grasshopper Optimization Algorithm"*.

| | Đề gốc | Bài mới |
|---|---|---|
| Nhân vật trung tâm | QIGOA | **QIGOA — giữ nguyên** |
| Hàm mục tiêu | Kapur entropy | **Kapur — giữ nguyên** |
| Cơ chế | Q-bit + quantum rotation gate | **Giữ nguyên** |
| Baseline so sánh | GA, PSO, GOA | **Giữ nguyên, mở rộng thêm GWO, WOA, MPA, random search** |
| Dữ liệu | BraTS | **Giữ nguyên (BraTS 2020) + ngoại kiểm LGG** |
| **Câu hỏi nghiên cứu** | *"QIGOA có thắng không?"* | ***"QIGOA có thực sự giúp không, và ta đang đo đúng thứ chưa?"*** |
| **Thước đo** | PSNR, SSIM, CPU time | **Dice, HD95, NSD** (PSNR/SSIM giữ lại làm *bằng chứng*, không phải kết quả) |
| **Kết luận** | "QIGOA vượt trội" | **Bốn mệnh đề bác bỏ được + một phương pháp thay thế** |

**Không có gì bị vứt bỏ.** Toàn bộ QIGOA, Kapur, Q-bit, rotation gate, và bảng so sánh bảy thuật toán đều nằm trong bài. Khác biệt duy nhất: chúng phục vụ một luận điểm **không thể bị bác**, thay vì một luận điểm **sẽ bị bác**.

## 1.3 Vì sao phải đổi — ba sự thật từ chính số liệu của chúng ta

> ### ⚠️ NGUỒN SỐ — ĐỌC TRƯỚC KHI ĐỌC BẤT KỲ BẢNG NÀO Ở MỤC NÀY
> Mọi con số trong §1.3 lấy từ **lô thí nghiệm đầu tiên** (commit `c4fe108`, 25.200 run). Lô này có **bốn lỗi cài đặt**: ngân sách NFE lệch 13,4% · baseline GOA hỏng (hit-rate 0%) · metric tự chế (global-SSIM, FSIM không đầy đủ) · pseudo-replication (3 lát/bệnh nhân đưa vào Wilcoxon như mẫu độc lập).
> ⇒ **Chúng là `[PLACEHOLDER]` — BẰNG CHỨNG CHẨN ĐOÁN, KHÔNG PHẢI KẾT QUẢ.** Chúng là *lý do ta phát hiện ra vấn đề*, **không phải nguồn số liệu để công bố**. **Không một con số nào trong mục này được phép xuất hiện trong bản thảo.** Toàn bộ sẽ được tái sinh từ một pipeline sạch.

Lô thí nghiệm đầu tiên đã chạy xong (25.200 lượt chạy độc lập trên BraTS). Khi đọc kỹ số liệu, ba sự thật hiện ra và **cả ba đều bác bỏ claim "QIGOA vượt trội"**.

**Thứ nhất — QIGOA được cấp thêm 13,4% ngân sách.** Mọi baseline tiêu đúng 7.550 lượt đánh giá hàm mục tiêu. QIGOA tiêu 8.563. Nguyên nhân: bước memetic refinement có gọi hàm mục tiêu nhưng không bị trừ vào ngân sách. Nghĩa là QIGOA đang chạy một cuộc đua mà nó được thêm 13,4% thời gian, còn các đối thủ thì không. **Chưa cùng ngân sách thì chưa có quyền so sánh gì cả.**

**Thứ hai — tối ưu càng giỏi thì phân đoạn càng tệ.** Khi tăng số ngưỡng k từ 2 lên 10:

| k | Kapur fitness | PSNR (dB) | SSIM | **Dice** |
|---|---|---|---|---|
| 2 | 9,61 | 18,86 | 0,772 | **0,664** |
| 4 | 15,82 | 27,96 | 0,970 | **0,675** — đỉnh |
| 6 | 21,42 | 32,06 | 0,992 | 0,579 |
| 8 | 26,36 | 34,43 | 0,995 | 0,500 |
| 10 | 30,81 | 36,19 | **0,997** | **0,437** |

Hàm mục tiêu tăng đơn điệu. PSNR tăng đơn điệu. SSIM tiến sát 1,0. **Còn Dice sụp 34%.** Hệ số tương quan hạng Spearman giữa k và Dice là **−0,893**.

Hệ quả trực tiếp và nghiêm trọng: **nếu chọn k bằng PSNR, ta chọn k = 10. Nếu chọn bằng Dice, ta chọn k = 4.** Chọn mô hình bằng PSNR chủ động làm hại bệnh nhân.

**Thứ ba — và đây là phát hiện quan trọng nhất — suy biến cấu trúc.** Quy tắc tạo mask khối u mà cả dòng văn liệu đang dùng là "lấy lớp sáng nhất". Nghĩa là mask chỉ gồm những điểm ảnh có cường độ **vượt ngưỡng lớn nhất**. Còn k−1 ngưỡng kia? Không ảnh hưởng gì tới mask.

Kiểm chứng trên toàn bộ dữ liệu — nhóm các lượt chạy theo cặp *(ảnh, ngưỡng lớn nhất)* rồi xem Dice có thay đổi không:

> **2.576 trên 2.576 nhóm cho Dice hằng số. Độ lệch chuẩn lớn nhất trong một nhóm: 0,00.**
> Không một ngoại lệ.

Nói cách khác: **toàn bộ máy móc Q-bit, quantum rotation gate, Lévy flight, memetic refinement và social term của GOA đang tranh nhau tối ưu những biến không ảnh hưởng tới kết quả lâm sàng.** Không gian tìm kiếm thực sự có ích chỉ là **một chiều với 254 giá trị** — vét cạn trong vài mili-giây.

Điều này *giải thích* sự thật thứ hai: khi k tăng, thuật toán đẩy ngưỡng lớn nhất lên cao hơn, mask teo lại, Dice sụp. Fitness vẫn tăng vì nó đo entropy của **toàn bộ phân hoạch**, chứ không đo khối u.

**Và kết cục:** tại k = 10, dù được cấp thêm 13,4% ngân sách, QIGOA vẫn **thua PSO ở cả ba chiều** — fitness thấp hơn (31,108 so với 31,137), Dice thấp hơn (0,444 so với 0,453), và chậm hơn 36%.

"Chiến thắng" duy nhất của QIGOA là thắng **GOA gốc**. Nhưng GOA gốc có tỷ lệ đạt nghiệm tốt nhất bằng **0% ở mọi k ≥ 3**, trong khi mọi thuật toán khác đạt trên 96%. Một baseline có tỷ lệ 0% không phải là baseline — đó là **một lỗi cài đặt**. Ta đang so với một con bug, không phải với hiện trạng nghiên cứu.

---

# 2. Bốn mệnh đề — xương sống của bài

Bài báo được dựng quanh bốn mệnh đề. Điểm mấu chốt: **mỗi mệnh đề đều có thể bị bác bỏ bằng một thí nghiệm cụ thể.** Đây là khác biệt giữa "chứng minh tôi đúng" và "cố gắng chứng minh tôi sai, và thất bại" — và reviewer phân biệt được hai thứ đó.

Bốn mệnh đề đã được **khoá trong một bản preregistration viết trước khi chạy bất kỳ thí nghiệm nào**, kèm tiêu chí bác bỏ và phương án dự phòng nếu thất bại. Đây là hàng rào chống việc điều chỉnh giả thuyết cho khớp với số liệu sau khi đã nhìn thấy số.

## P1 — Suy biến cấu trúc

**Phát biểu.** Với *bất kỳ* quy tắc nào ánh xạ phân hoạch k-ngưỡng thành mask nhị phân bằng cách chọn **một dải lớp cường độ liên tiếp**, mask được xác định bởi **nhiều nhất hai** trong k ngưỡng — bất kể k lớn bao nhiêu. Với quy tắc "lớp sáng nhất" mà dòng văn liệu đang dùng: **đúng một**.

**Hệ quả.** Số chiều hiệu dụng của không gian tìm kiếm *lâm sàng* là ≤ 2, chứ không phải k. Toàn bộ k−1 biến còn lại là **biến giả**.

**Bác bỏ được nếu:** tồn tại một nhóm *(ảnh, dải-lớp)* có Dice không hằng số.

**Nếu P1 sai:** toàn bộ xương sống của bài sụp. Khi đó hạ scope xuống một bài ablation khiêm tốn và nộp venue thấp hơn. **Không cứu P1 bằng cách đổi định nghĩa.**

## P2 — Không còn khoảng trống tối ưu

**Phát biểu.** Với ngân sách **bằng nhau tuyệt đối**, mọi metaheuristic — kể cả QIGOA, và kể cả random search — đạt trên 99,99% nghiệm **tối ưu toàn cục chính xác**, với chi phí thời gian lớn hơn khoảng hai bậc độ lớn.

Nghiệm tối ưu chính xác tính được bằng quy hoạch động, vì Kapur entropy có tính **cộng tính theo khoảng**.

> ⚠️ **Đây không phải đóng góp của chúng ta**, và bài phải nói thẳng điều đó ngay ở Abstract. Lời giải chính xác đã có: **Luessi et al.** (*J. Electronic Imaging*, 2009) và **Merzban & Elbayoumi** (*Expert Systems with Applications*, 2019). Ta chỉ **dùng** nó làm mốc tham chiếu.

**Bác bỏ được nếu:** có thuật toán nào cho tỷ lệ đạt nghiệm dưới 99% một cách hệ thống — nghĩa là bài toán *thực sự* khó, và metaheuristic *có* chỗ đứng.

## P3 — Metric hiện hành phản chỉ báo chất lượng lâm sàng

**Phát biểu.** Khi k tăng, Kapur fitness / PSNR / SSIM tăng đơn điệu, trong khi Dice giảm và HD95 xấu đi. Chọn k bằng PSNR cho ra k = 10; chọn bằng Dice cho ra k = 4.

**Bác bỏ được nếu:** tương quan hoá ra dương hoặc không có ý nghĩa thống kê.

> **Một sự thật bất lợi mà bài PHẢI tự nêu.** Trong *cùng một k*, tương quan giữa PSNR và Dice giữa các thuật toán là **dương** (khoảng +0,75 đến +0,93). Nghịch lý chỉ xuất hiện khi *đổi k*. Nếu ta viết "PSNR không tương quan với Dice" thì reviewer chạy lại số trong mười phút và bài chết ngay vòng đầu.
>
> Điều này đã được ghi vào preregistration như một ràng buộc bắt buộc. **Sự thật bất lợi mà mình tự nêu trước thì không còn là vũ khí của reviewer nữa.**

## P4 — Trần của cả họ phương pháp

**Phát biểu (đã sửa 14/07/2026).** Nếu ta cho phép một "oracle" biết trước đáp án được chọn **tập mức xám tốt nhất có thể** cho từng ảnh, thì kết quả của oracle đó là **trần đúng của MỌI decoder chỉ-dùng-cường-độ** — kể cả những decoder chưa ai nghĩ ra. Ta đo xem một U-Net 2D huấn luyện trên **đúng cùng đầu vào lúc suy luận** có vượt qua trần đó không.

> ⚠️ **Bản trước nói "oracle chọn CẶP ngưỡng tốt nhất" là trần của mọi thresholding — SAI.** Cặp ngưỡng chỉ cho **một khoảng liên tiếp**; một decoder chọn **tập mức xám không liên tiếp** vượt qua nó. Trần đúng tính bằng cách sắp xếp mức xám theo độ tinh khiết và quét prefix — $O(L\log L)$. Nền toán: **Lipton et al., arXiv:1402.1892** *(cite, không claim là của mình)*.
> ⚠️ Và **P4 có thể THẤT BẠI**: trần trên WT/FLAIR là ~0,83 (François & Tinarrage, JMIV 2026) — **không thấp**, mà nằm trong vùng đồng thuận giữa các bác sĩ. Fallback đã khoá trong preregistration §6/A2 **trước khi nhìn số**.

**Bác bỏ được nếu:** U-Net không vượt oracle — khi đó luận điểm về trần yếu đi, và ta hạ claim xuống "thresholding chạm trần của chính nó", bỏ phần so sánh với deep learning.

---

# 3. Đóng góp dương — thứ biến bài từ "kết quả âm" thành "bài đăng được"

Một bài báo chỉ nói *"các anh sai"* thì editor sẽ hỏi câu cuối cùng: *"vậy cộng đồng nên làm gì?"* Nếu không có câu trả lời, bài không được đăng.

Đây chính là công thức thầy đã đúc kết trong playbook IEEE của thầy, sau vòng major revision khi claim chính của thầy sụp đổ:

> ***Negative*** (tuyên bố cũ sụp) **+** ***Cautionary methodology*** (chỉ ra vì sao sai và giao thức để tránh) **+** ***Positive*** (một đóng góp xây dựng hoạt động được).
>
> *"Một kết quả âm được làm nghiêm cẩn, cộng một đóng góp dương, là một bài đăng được. Một kết quả dương bịa ra là một lần reject cộng mất uy tín."*

Bài này có đủ ba phần. Phần **Positive** gồm ba thứ *(đã viết lại 14/07/2026 — xem cảnh báo cuối mục)*:

**Một — phân rã cái trần (ceiling decomposition).** Trần của decoder chỉ nhìn **một lát FLAIR**, so với trần của decoder nhìn **histogram chung của cả bốn mô thức**, so với **U-Net 2D cùng đầu vào**. Ba con số này tách khoảng cách thành hai phần đo được: *"thông tin **không có trong CƯỜNG ĐỘ**"* và *"thông tin **không có trong PIXEL**"*. **Chưa ai làm.** François & Tinarrage nói *rằng* thresholding chạm trần; ta nói **TẠI SAO, và trần đó gồm những gì**.

**Hai — một công cụ chẩn đoán chạy trong micro-giây.** Cho phép **bất kỳ tác giả nào, trên bất kỳ dataset nào**, tính trước **trần Dice của cả họ phương pháp mà họ sắp dùng** — *trước khi* viết dòng optimizer đầu tiên. Đây là thứ thực sự đổi hành vi: reviewer tiếp theo chỉ cần hỏi *"tại sao anh không chạy công cụ này trước?"*, vì nó tốn **một dòng lệnh**.

**Ba — một checklist giao thức đánh giá** cho dòng văn liệu này: đo Dice và HD95 chứ không phải PSNR/SSIM; **báo cáo quy tắc decoding** (hiện gần như không bài nào nêu); cấp ngân sách bằng nhau cho mọi thuật toán; làm thống kê ở cấp bệnh nhân chứ không phải cấp lát ảnh.

> ### ⚠️ BẢN TRƯỚC ĐÃ SAI Ở ĐÂY — và đây là sửa đổi quan trọng nhất của toàn bộ tài liệu
> Bản trước đặt **"một bộ giải chính xác mili-giây, nhanh hơn ~250 lần"** làm đóng góp dương số một.
> **Phải bỏ.** **Menotti, Najman & de A. Araújo (CIARP 2015, `10.1007/978-3-319-25751-8_42`)** đã công bố **đúng thuật toán đó, cho đúng Kapur entropy, đúng độ phức tạp `O((K−1)L²)`, chạy dưới 160 ms** — **mười một năm trước**. Ta chỉ **dùng lại** nó làm mốc tham chiếu, và **cite trang trọng ngay ở Abstract**.
> Con số **"nhanh hơn ~250 lần"** cũng phải bỏ: đó là **artifact của vòng lặp Python**, không phải của thuật toán, và **chưa ai đo**. Thay bằng ba thứ **không cài đặt nào lấy đi được**: **tính chính xác** (đảm bảo tối ưu toàn cục) · **tính tất định** (không seed, không phương sai) · **không hyperparameter**.
> **Vì sao đây là chuyện sống còn:** luận điểm trung tâm của bài là *"dòng văn liệu này không cite lời giải chính xác đã có"*. Nếu chính ta đi claim làm lại một lời giải đã in 11 năm, thì ta **tự thiêu trong đúng một câu của reviewer** — và ta xứng đáng bị vậy.
>
> **Đóng góp dương phải được chạy SỚM (tuần 2), không phải cuối.** Nó là thứ quyết định bài có tồn tại hay không, và nó hiện **chưa được preregister**. Nếu ngưỡng một-tham-số **không** thắng, đóng góp dương rơi về ba thứ ở trên — và ta phải xác nhận **ngay bây giờ** rằng ba thứ đó **đủ đứng một mình**, chứ không phải sau bốn tuần chạy.

---

# 4. Thiết kế nghiên cứu

## 4.1 Nguyên tắc: mỗi thí nghiệm là một phép thử bác bỏ

Thí nghiệm không được thiết kế để *minh hoạ* luận điểm, mà để *có thể làm sai* nó. Bảy nhóm thí nghiệm dưới đây, mỗi nhóm gắn với một mệnh đề, và mỗi nhóm đều có khả năng làm mệnh đề đó thất bại.

| Nhóm | Nội dung | Chứng minh / bác bỏ |
|---|---|---|
| **A** | Tính nghiệm tối ưu chính xác bằng quy hoạch động, đối chiếu với vét cạn | Nền của P2 |
| **B** | **Lưới chính** — 150 bệnh nhân × 7 giá trị k × 11 phương pháp × 5 lần chạy độc lập, **ngân sách bằng nhau** | P2, P3 |
| **C** | **Ablation QIGOA trên dữ liệu thật** — tháo từng thành phần | **Trả lời trực diện câu hỏi của thầy** |
| **D** | **Phân tích trần** — oracle vét cạn + U-Net 2D cùng đầu vào | P4 |
| **E** | Bộ thước đo đầy đủ — thêm HD95, NSD | P3 |
| **F** | Kiểm định thống kê ở cấp bệnh nhân | Chống đòn "không chứng minh được giả thuyết không" |
| **G** | **Ngoại kiểm** trên bộ dữ liệu LGG — khác cơ sở, khác máy chụp, khác grade | Chống đòn "một dataset" |

## 4.2 Nhóm C — Ablation: câu trả lời trực diện cho đề bài của thầy

Thầy giao câu hỏi: **thành phần quantum-inspired đóng góp gì?**

Bản cũ **không trả lời được** câu này, vì nó chỉ tháo lắp thành phần trên ảnh phantom tổng hợp chứ không phải trên BraTS. Claim *"bỏ memetic refinement thì QIGOA thua GA và PSO"* trong bản cũ do đó **không có bằng chứng chống lưng**. Đây là lỗ hổng lớn nhất của bản cũ, và cũng là chỗ reviewer sẽ đâm đầu tiên.

Bài mới vá nó: sáu biến thể — QIGOA đầy đủ, bỏ quantum, bỏ memetic, bỏ opposition-based learning, bỏ Lévy flight, và PSO cộng thêm memetic — chạy trên BraTS thật, **cùng ngân sách và cùng mọi tham số khác**, khớp tới từng tham số.

**Dự đoán đã khai báo trước:** thành phần quantum đóng góp xấp xỉ **0** vào Dice — bởi theo P1, nó *không thể* đóng góp gì ngoài việc dịch chuyển ngưỡng lớn nhất.

**Nhưng nếu dự đoán này sai** — nếu quantum thực sự cải thiện Dice một cách có ý nghĩa — thì đó là một finding **dương**, và ta báo cáo đúng như vậy. Bài tự đặt mình vào rủi ro ở đúng chỗ này, và đó chính là điều làm nó đáng tin.

## 4.3 Nhóm D — Phân tích trần: thang chín bậc

Tất cả đặt trên **cùng một trục Dice, cùng một tập kiểm tra**. Đây sẽ là hình chủ đạo của bài.

| Bậc | Phương pháp | Chi phí | Ý nghĩa |
|---|---|---|---|
| 1 | Random search (cùng ngân sách) | ~1,5 giây | *Nếu ngang metaheuristic → đòn chí mạng* |
| 2 | Bảy metaheuristic (ngân sách bằng nhau) | 1–2,5 giây | **Cả dòng văn liệu đang chen chúc ở đây** |
| 3 | Quy hoạch động — tối ưu toàn cục **chính xác** | vài mili-giây | Trần của *bài toán tối ưu* |
| 4 | Otsu / Li / k-means / GMM cổ điển | vài mili-giây | Baseline cổ điển |
| 5 | **Ngưỡng một-tham-số học trên tập train** | ~0 | **Đóng góp dương của bài** |
| 6 | Oracle một-ngưỡng (biết trước đáp án) | ~vài mili-giây | Trần của quy tắc "lớp sáng nhất" |
| 7 | Oracle một-khoảng (biết trước đáp án) | ~vài mili-giây | Trần của decoder **chọn một dải lớp liên tiếp** — ⚠️ **KHÔNG phải trần của mọi thresholding** |
| **7b** | **Oracle tập-mức-xám (level-set)** ★ | **~vài mili-giây** | **TRẦN ĐÚNG của MỌI decoder chỉ-dùng-cường-độ** |
| 8 | U-Net 2D, **cùng đầu vào lúc suy luận** | vài giờ GPU | Baseline deep learning **công bằng** |
| 9 | nnU-Net 3D đa mô thức | — | **Số trích từ văn liệu, không tự chạy** |

> ### 🔴 SỬA LỖI TOÁN (14/07/2026)
> Bản trước viết *"Oracle một-khoảng = **Trần của MỌI thresholding cường độ**"*. **Điều đó SAI.** Nó chỉ chặn decoder chọn **một dải lớp LIÊN TIẾP**. Một decoder chọn **tập lớp KHÔNG liên tiếp** vẫn là thresholding cường độ hợp lệ, và nó **vượt qua** trần đó (kiểm chứng: vượt trên ~98% histogram, trung bình **+0,04** Dice).
> **Trần đúng** là oracle trên **tập mức xám tuỳ ý** $S$: sắp xếp các mức xám theo *độ tinh khiết* $r_v = g_v/n_v$ giảm dần, quét prefix, lấy Dice lớn nhất ⇒ **nghiệm chính xác trong $O(L\log L)$**, vài mili-giây/ảnh, **độc lập k**. *(Nền toán: **Lipton, Elkan & Narayanaswamy, arXiv:1402.1892** — **cite, KHÔNG claim là của mình**.)*
> **Vì sao điều này quan trọng:** một bài chuyên phê phán overclaim mà **tự overclaim** thì chết không cãi được. Vá xong, kết luận về trần trở thành **decoding-agnostic THẬT SỰ** — không còn kẽ hở "strawman decoding" nào.
> ⚠️ Đồng thời: chi phí oracle **KHÔNG phải "~30 giây/ảnh"** như bản trước ghi — nó là phép toán **trên histogram**, tốn **mili-giây** (sai 4 bậc độ lớn). Điều này làm nhiều thí nghiệm "đắt" trở nên gần như miễn phí.

Bậc 1 đến 4 nằm trong sai số của nhau. Bậc 6–7b là **trần**. Bậc 8 và 9 nằm **trên** trần — ⚠️ **nhưng xem cảnh báo dưới đây: bậc 8 có thể KHÔNG vượt trần, và ta phải chuẩn bị cho điều đó TRƯỚC khi chạy.**

> ### ⚠️ P4 CÓ THỂ THẤT BẠI — và ta đã biết trước lý do
> Trên **whole-tumor / FLAIR**, trần của thresholding **KHÔNG THẤP**: François & Tinarrage đo oracle = **Dice 0,83 ± 0,18**, trong khi **đồng thuận giữa các bác sĩ** chỉ ~**0,85–0,87** (Menze et al., IEEE TMI 2015). Và quy tắc "chọn lát có u lớn nhất" của ta lại chọn đúng **lát thuận lợi nhất cho thresholding** ⇒ trần có thể lên **0,88–0,93**, trong khi U-Net 2D FLAIR-only train trên ~120 bệnh nhân thường chỉ đạt **0,80–0,82**.
> ⇒ **Fallback đã khoá trước khi nhìn số** (preregistration §6/A2): nếu U-Net không vượt trần, headline đổi thành **"Trần CAO — thất bại của thresholding không do giới hạn biểu diễn, mà do BÀI TOÁN CHỌN NGƯỠNG; và không một cỗ máy metaheuristic nào chạm tới bài toán chọn đó."**
> ⇒ Và **bổ sung một target KHÓ: enhancing tumor trên T1ce** — một **vành sáng bao lõi tối**, thứ mà một dải cường độ liên tiếp **về mặt toán học không thể** biểu diễn. Đó là nơi giới hạn của thresholding là **THẬT**.

**Về deep learning — chỗ dễ chết nhất, cần cẩn thận:**

Ta **không** train nnU-Net. Nó cần nhiều ngày GPU, còn Kaggle chỉ cho 30 giờ mỗi tuần. Thay vào đó:

- **Train một U-Net 2D trên đúng đầu vào của thresholding** (một lát FLAIR). Đây mới là so sánh *công bằng*, và nó vô hiệu hoá phản biện *"anh so 2D đơn mô thức với 3D đa mô thức"*.
- **Trích số nnU-Net từ văn liệu** (Isensee et al., BraTS 2020 — Dice whole-tumor 0,9124), **dán nhãn rõ ràng** là *số tham chiếu từ văn liệu, không do chúng tôi chạy, giao thức đầu vào khác*. Dùng làm bối cảnh, không phải baseline so trực tiếp.

## 4.4 Nhóm F — Kiểm định thống kê

Đơn vị thống kê là **bệnh nhân** (n = 150), **không phải lát ảnh**. Bản cũ lấy ba lát mỗi bệnh nhân rồi đưa vào kiểm định như ba mẫu độc lập — đó là *pseudo-replication*, và reviewer y tế sẽ bắt ngay.

| Mục đích | Phương pháp | Vì sao bắt buộc |
|---|---|---|
| So sánh cặp | Wilcoxon signed-rank + **hệ số hiệu ứng rank-biserial** | p-value không nói được *độ lớn* |
| So sánh nhiều nhóm | Friedman + Nemenyi + **biểu đồ Critical Difference** | Chuẩn của lĩnh vực |
| **Khẳng định "không khác nhau"** | **Kiểm định tương đương TOST**, ngưỡng khai báo trước **0,01 Dice** | *"p > 0,05" KHÔNG đủ.* Đây là cách hợp pháp **duy nhất** |
| Bổ trợ | **Bayesian signed-rank + vùng ROPE** | Cho phát biểu *"xác suất tương đương = 0,9x"* |

Không có TOST và ROPE, reviewer chỉ cần một câu — *"vắng bằng chứng không phải là bằng chứng của sự vắng mặt"* — và toàn bộ luận điểm của bài sập.

## 4.5 Về thước đo — và một quyết định cắt bỏ

| Thước đo | Vai trò trong bài |
|---|---|
| **Dice, IoU** | **Kết quả** — thước đo quyết định |
| **HD95, NSD** | **Kết quả** — theo chuẩn *Metrics Reloaded* (Nature Methods, 2024) |
| PSNR, SSIM | **Bằng chứng** cho P3 — giữ lại để *chứng minh chúng sai*, không phải để khoe |
| ~~FSIM~~ | **Loại khỏi scope** |
| ~~Tsallis entropy~~ | **Loại khỏi scope** |

**Vì sao cắt FSIM:** bản cũ dùng một FSIM tự cài, và chính docstring của nó thú nhận *"không phải FSIM đầy đủ"*. Một bài báo phê phán việc dùng sai thước đo mà bản thân lại dùng thước đo tự chế thì **tự sát** — reviewer chỉ cần mở code.

**Vì sao cắt Tsallis:** Tsallis entropy không có tính cộng tính, nên không tính được nghiệm chính xác bằng quy hoạch động. Giữ nó lại chỉ thêm một bề mặt để bị tấn công mà không thêm chút sức thuyết phục nào.

*Nếu thầy muốn giữ hai thứ này, đây là điểm cần bàn.*

---

# 5. Định vị so với văn liệu

## 5.1 Khoảng trống thật nằm ở đâu

Đây là phần quyết định bài có được đăng hay không. Ba nhánh văn liệu tồn tại **song song mà không nói chuyện với nhau**:

**Nhánh A — metaheuristic cho multilevel thresholding.** Rất đông, ra bài liên tục tới 2026. Bao gồm cả nhánh con quantum-inspired (Dey, Bhattacharyya, Maulik — có hẳn một cuốn sách Wiley năm 2019 về đúng chủ đề này).

**Nhánh B — lời giải chính xác cho cùng bài toán đó.** Luessi et al. (2009); Merzban & Elbayoumi (2019). Đã chứng minh quy hoạch động cho nghiệm tối ưu toàn cục, nhanh hơn metaheuristic hàng trăm lần.

**Nhánh C — chuẩn đánh giá phân đoạn y tế.** *Metrics Reloaded* (Nature Methods, 2024); metric chính thức của BraTS challenge (Dice và HD95).

> **Khoảng trống:** Nhánh A **không cite** nhánh B, và **không dùng** nhánh C.
>
> Đây là một phát biểu **kiểm chứng được**, và bài sẽ kiểm chứng nó bằng một **bảng trắc lượng thư mục**: đếm trong khoảng 40–60 bài từ 2019 đến 2026 trên tạp chí Q1/Q2, có bao nhiêu bài (a) không trích Merzban 2019 hoặc Luessi 2009, và (b) không báo cáo Dice/HD95 dù dùng dataset **có sẵn ground truth**.

Bảng này biến phản biện *"ai cũng biết rồi"* thành *"không, rõ ràng là không ai biết"*. Đây là bảng đầu tiên của bài.

## 5.2 Phản biện nguy hiểm nhất, và cách trả lời

> **"Merzban & Elbayoumi 2019 đã làm rồi. Novelty của các anh ở đâu?"**

Đây là câu hỏi có thể giết bài. Câu trả lời phải **chuẩn bị sẵn và đặt ngay ở Abstract**:

Ta **tuyên bố thẳng: không claim nghiệm chính xác là đóng góp của mình.** Trích Merzban và Luessi trang trọng.

Nhưng họ dùng **ảnh tự nhiên, không có ground truth**. Vì thế họ *về mặt nguyên tắc không thể* phát hiện được:

- **P1 (suy biến)** — cần ground truth mới thấy được k−1 ngưỡng là biến giả;
- **P3 (metric phản chỉ báo)** — cần ground truth mới thấy PSNR đi ngược Dice;
- **P4 (trần)** — cần ground truth mới tính được trần;
- và **audit nhánh quantum-inspired** — nhánh này ra đời sau bài của họ.

Nói cách khác: họ dừng lại ở ảnh tự nhiên; ta mang cùng câu hỏi đó **sang miền có ground truth lâm sàng**. Cover letter có thể viết: *"chúng tôi mở rộng bài năm 2019 của quý tạp chí sang miền dữ liệu lâm sàng có ground truth."*

> ⚠️ **Bản trước viết "chúng ta là người đầu tiên bước qua" — ĐÃ BỎ (14/07/2026).** Đó là overclaim và **vi phạm IRON RULE 5** (không nói "first/đầu tiên" khi chưa collision-check). Collision-check đã chạy, và kết quả là: **cửa đã có nhiều người bước qua.**
> - **Menotti, Najman & Araújo (CIARP 2015)**, `10.1007/978-3-319-25751-8_42` — exact DP cho **đúng Kapur**, `O((K−1)L²)`, *"<160 ms"*. ⇒ **"bộ giải chính xác" KHÔNG phải đóng góp của ta.**
> - **Hammouche, Diaf & Siarry (EAAI 2010)**, `10.1016/j.engappai.2009.09.011` — đã đo **gap/hit-rate của metaheuristic tới nghiệm vét cạn**, ngưỡng 1e−9.
> - **François & Tinarrage (JMIV 68, 20, 2026)**, `10.1007/s10851-026-01300-1` — đã in **trần oracle 0,83±0,18 trên BraTS FLAIR**. ⇒ **CẤM claim "we establish the ceiling".**
> - **Lipton, Elkan & Narayanaswamy (arXiv:1402.1892, 2014)** — **sở hữu định lý** oracle level-set. ⇒ ta **claim ứng dụng, không claim toán học**.
>
> **Định vị trung thực còn lại:** ta không phải người đầu tiên bước qua cửa — ta là người **đầu tiên đo xem căn phòng đó cao bao nhiêu, và tại sao trần lại ở đó**.

## 5.3 Ba đối thủ gần khác phải phân biệt

| Đối thủ | Vì sao khác ta |
|---|---|
| *A novel quantum grasshopper optimization algorithm* (Int. J. Approximate Reasoning, 2020, Q1) | "QGOA" **đã tồn tại** → ta **không được** claim QIGOA là thuật toán mới. Ta không claim điều đó. |
| Dey, Bhattacharyya, Maulik — sách Wiley 2019 + hai bài Applied Soft Computing 2016, 2017 | Quantum-inspired + Kapur + thresholding **đã xong từ 2016**. Ta không đề xuất thuật toán mới; ta **audit** cả họ phương pháp. |
| *Alzheimer's brain segmentation using 3D Rényi entropy + quantum hybrid optimization* (Artificial Intelligence Review, 2025, Q1) | Đối thủ gần nhất về mặt đề tài. Nhưng họ vẫn nằm trong **nhánh A** — không cite nhánh B, không dùng nhánh C. Họ là **đối tượng** của bài này, không phải đối thủ. |

---

# 6. Cấu trúc bản thảo

**Thứ tự viết khác thứ tự đọc.** Viết mục 3 (Suy biến) và mục 8 (Trần) **trước** — chúng là linh hồn của bài. Introduction viết **sau cùng**, khi đã biết bài thực sự nói gì. Đây đúng là nguyên tắc thầy dạy: *làm cứng bài toán và thực nghiệm trước, để câu chuyện tự nổi lên sau.*

| Mục | Nội dung | Bảng / Hình |
|---|---|---|
| 1. Introduction | Dòng văn liệu vẫn nở rộ. Nêu bốn mệnh đề bác bỏ được. Nói thẳng: đây là một *reality check* **có kèm phương pháp thay thế** | — |
| 2. Related Work & the Citation Gap | Ba nhánh văn liệu. **Chỉ ra nhánh A không cite nhánh B và không dùng nhánh C** | **Bảng I** — trắc lượng thư mục |
| 3. **Suy biến của hàm mục tiêu** | Mệnh đề 1 (mask phụ thuộc ≤ 2 ngưỡng) và Mệnh đề 2 (Kapur cộng tính → quy hoạch động cho tối ưu toàn cục). Chứng minh toán học + xác nhận bằng vét cạn | **Bảng II** |
| 4. Giao thức thực nghiệm | 150 bệnh nhân, ngân sách bằng nhau, bộ thước đo đầy đủ, thống kê cấp bệnh nhân, **ngưỡng khai báo trước** | **Hình 1** — sơ đồ |
| 5. **Không còn gì để tối ưu** | Mọi metaheuristic (kể cả **random search**) đạt nghiệm chính xác của DP. GOA hỏng, và "ý nghĩa thống kê" của QIGOA sinh ra từ đó. ⚠️ **Chi phí báo bằng NFE + độ phức tạp**, không bằng wall-clock — "nhanh hơn 250 lần" là artifact của Python, đã bỏ | **Bảng III**, **Hình 2** |
| 6. **Thước đo phản chỉ báo chất lượng lâm sàng** | fitness/PSNR/SSIM tăng theo k, Dice/HD95 xấu đi. **Thừa nhận thẳng**: trong cùng một k thì tương quan dương — và giải thích vì sao điều đó vẫn không cứu được gì | **Hình 3** |
| 7. **Thành phần quantum không đóng góp gì** | Ablation trên dữ liệu thật, ngân sách bằng nhau. Kiểm định tương đương với PSO. Nền lý thuyết: quantum-inspired EA thực chất là một EDA | **Bảng IV** |
| 8. **Trần** | Thang chín bậc. Random ≈ metaheuristic ≈ quy hoạch động; oracle là trần; U-Net cùng đầu vào vượt trần | **Hình 4** — hình chủ đạo |
| 9. **Một baseline tốt hơn** | Bộ giải mili-giây + ngưỡng một-tham-số. Kèm **checklist đánh giá** cho các bài sau | **Bảng V** |
| 10. Threats to Validity | Tự liệt kê giới hạn: quy tắc decoding khác, mô thức khác, 2D so với 3D, cỡ mẫu | — |
| 11. Conclusion | **Không** phải "metaheuristic vô dụng nói chung" — mà "**trên bài toán cụ thể này**, chúng tối ưu một biến không quan trọng, trên một bài toán đã giải xong, đo bằng thước đo phản chỉ báo" | — |

## 6.1 Giọng điệu — một quyết định chiến lược

Bài phê phán **thực hành**, tuyệt đối **không nêu tên tác giả cụ thể để chê**.

Lý do rất thực tế: editor sẽ chọn reviewer từ **chính cộng đồng mà bài này audit**. Nếu bài đọc như một cuộc tấn công cá nhân, ta tự tạo ra kẻ thù trong hội đồng phản biện.

Đóng khung mang tính xây dựng: *"một benchmark, một giao thức đánh giá, và một công cụ cho phép bất kỳ ai tính trước trần của cả họ phương pháp mình sắp dùng"*. Bảng trắc lượng thư mục trình bày ở dạng **tổng hợp thống kê**, không phải danh sách bêu tên.

> ⚠️ **Bỏ cụm "nhanh hơn 250 lần"** khỏi mọi cách đóng khung — nó là artifact cài đặt (Python chậm), không phải một kết quả, và **chưa ai đo**. Nếu dùng nó, reviewer sẽ viết đúng một câu: *"metaheuristic của các anh chậm vì Python của các anh chậm."*
> **Và đổi tiêu đề bài.** *"Optimizing the Wrong Variable"* nghe hay với tác giả, nhưng với reviewer bị audit thì nó là một cái tát — mà editor lại chọn reviewer từ **chính cộng đồng đó**. Dùng tiêu đề mô tả, trung tính, positive-first, ví dụ: *"An exact-optimum benchmark, decoding degeneracy, and performance ceilings in intensity-based multilevel thresholding for brain tumour MRI."*

---

# 7. Năm phản biện chí mạng và phòng thủ

| Phản biện | Cách trả lời | Đã cài sẵn ở |
|---|---|---|
| **"Merzban 2019 làm rồi, novelty đâu?"** *(nguy hiểm nhất)* | Cite họ ở Abstract, tuyên bố thẳng không claim nghiệm chính xác. Họ dùng ảnh tự nhiên **không có ground truth** nên *không thể* phát hiện suy biến, trần, hay metric phản chỉ báo | Mục 2, Bảng I |
| **"Quy tắc decoding của các anh là strawman"** | Test **bốn** quy tắc khác nhau. Và quan trọng hơn: **oracle vét cạn là trần đúng cho MỌI quy tắc chọn-dải-lớp**, kể cả quy tắc chưa ai nghĩ ra → kết luận về trần **độc lập với decoding**. Diệt bằng toán, không bằng tranh cãi | Mục 8 |
| **"Không thể chứng minh giả thuyết không"** | Kiểm định tương đương TOST với ngưỡng khai báo trước, cộng Bayesian ROPE → phát biểu được *"xác suất tương đương = 0,9x"*, chứ không phải *"p > 0,05"* | Mục 7 |
| **"Các anh cài GOA sai nên QIGOA là strawman"** | **Tự thừa nhận trước**, sửa GOA, báo cáo **cả hai phiên bản**. Xác thực cài đặt bằng cách tái tạo một bảng đã công bố trên ảnh chuẩn. **Và quan trọng nhất: kết luận trung tâm không phụ thuộc vào GOA** — nó dựa trên nghiệm chính xác và P1, hai thứ không có tham số nào để cài sai | Mục 5 |
| **"So sánh deep learning không công bằng"** | U-Net 2D **cùng đầu vào y hệt** là baseline chính; nnU-Net chỉ là bối cảnh trích từ văn liệu, dán nhãn rõ ràng | Mục 8, Mục 10 |

---

# 8. Chiến lược công bố

| Bậc | Tạp chí | Lý do |
|---|---|---|
| **Chính** | **Biomedical Signal Processing and Control** (Elsevier, Q1/Q2, IF ≈ 4,9, **không phí APC**) | Đây *chính là* tạp chí đang xuất bản dòng văn liệu mà bài này audit → tác động chỉnh sửa cao nhất, và scope khớp tuyệt đối |
| **Dự phòng 1** | **Expert Systems with Applications** (Elsevier, Q1) | **Có tiền lệ trực tiếp**: chính ESWA đã đăng Merzban & Elbayoumi 2019 — đúng thể loại "nghiệm chính xác thắng metaheuristic". Editor ở đó đã chấp nhận thể loại này một lần |
| **Dự phòng 2** | JCC (VAST) hoặc hội nghị Scopus (SoICT / KSE / NICS) | Lưới an toàn |

**Không nộp IEEE JBHI.** Tạp chí này thuộc lĩnh vực *health informatics*, có điều khoản trả bài ngay nếu ngoài phạm vi, và không có tiền lệ đăng bài metaheuristic thresholding. Nộp vào đó gần như chắc chắn bị trả về trong một đến hai tuần.

**Tuyệt đối tránh** *Multimedia Tools and Applications* và *Journal of Ambient Intelligence* — cả hai **đã bị Clarivate loại khỏi Web of Science**.

---

# 9. Lộ trình tám tuần

| Tuần | Việc | Kết quả |
|---|---|---|
| **0** | **Trình bày với thầy** | Thầy duyệt hướng — **không bắt đầu thực nghiệm trước cổng này** |
| **1** | Dựng lại nền thực nghiệm sạch; tính nghiệm chính xác; sửa lỗi ngân sách và baseline | Nền đã kiểm chứng |
| **2** | Lưới chính + ablation | Bảng III, Bảng IV |
| **3** | Phân tích trần + bộ thước đo đầy đủ | Hình 4 |
| **4** | Thống kê + ngoại kiểm LGG | Đủ 5 bảng, 4 hình |
| **5–6** | **Viết** — mục 3 và mục 8 trước, Introduction sau cùng | Bản thảo đầy đủ |
| **7** | Rà soát liêm chính: mọi con số truy về đúng nguồn sinh; thầy review | Bản thảo đã kiểm |
| **8** | Định dạng theo tạp chí + cover letter | **Nộp** |

**Tài nguyên tính toán: khoảng 40 giờ CPU và 2 giờ GPU trên Kaggle** — nằm gọn trong hạn mức miễn phí.

> **Nút thắt của bài này không phải là tính toán, mà là lập luận và viết.** Đừng nhầm hai thứ đó.

---

# 10. Ba lằn ranh không được vượt

**Một — không tái sử dụng bất kỳ con số nào từ lô thí nghiệm cũ.** Lô đó có bốn khiếm khuyết: ngân sách lệch 13,4%, baseline GOA hỏng, thước đo tự chế, và pseudo-replication. Nó là **bằng chứng chẩn đoán** — lý do ta phát hiện ra suy biến — **chứ không phải nguồn số liệu**. Mọi kết quả trong bài phải tái sinh từ một quy trình sạch.

**Hai — không tái sinh bảng số liệu trong bản PDF phác thảo ban đầu.** Bảng đó là **số bịa** (PSNR tăng từ 18,45 lên 22,87; thời gian giảm từ 2,14 xuống 0,92; không có Dice). Đưa nó vào bài là vi phạm nguyên tắc liêm chính cơ bản nhất.

**Ba — không dùng cụm từ "quantum advantage" ở bất kỳ đâu.** Thuật toán tiến hoá lấy cảm hứng lượng tử **đã được chứng minh chỉ là một Estimation of Distribution Algorithm** (Platel, Schliebs & Kasabov, *IEEE Transactions on Evolutionary Computation*, 2009). Q-bit và rotation gate, về mặt toán học, chỉ là một vector xác suất và một luật cập nhật xác suất — không có superposition thật, không có entanglement thật, không có interference thật.

Chạy trên CPU cổ điển thì "lượng tử" là **một ẩn dụ chồng lên ẩn dụ "đàn cào cào"**. Hai lớp ẩn dụ là hai lần rủi ro với reviewer.

Định vị đúng và trung thực: *một luật cập nhật xác suất kiểu EDA* — và cite Platel để chứng tỏ ta biết chính xác mình đang nói gì. Sự trung thực này không làm bài yếu đi; nó là **thứ duy nhất khiến bài đứng vững** khi có người hỏi tới.

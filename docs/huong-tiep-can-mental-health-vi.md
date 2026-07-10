# HƯỚNG TIẾP CẬN PAPER
## AI đáng tin cậy để sàng lọc trầm cảm từ giọng nói và cảm biến thụ động
### (Trustworthy Digital Phenotyping for Depression)

**Nghiên cứu sinh:** Nguyễn Võ Hoàng Long
**Ngày:** 04/07/2026 — *cập nhật 10/07/2026: bổ sung thành phần quantum-inspired theo góp ý của thầy (Mục 5).*

---

### Kính gửi thầy,

Em xin trình bày hướng tiếp cận mới cho luận án, thay cho hướng QIGOA (multilevel thresholding lượng
tử) trước đây. Lý do đổi hướng: sau khi em rà soát kỹ tài liệu, gap của QIGOA **có thật nhưng hẹp** —
việc "thêm quantum vào GOA" và "quantum cho thresholding" đều đã có nhiều công bố, khó đạt tầm tạp chí
Q1 nếu không đầu tư rất nhiều ablation và kiểm định thống kê.

Hướng mới em đề xuất là **AI đáng tin cậy (trustworthy AI) để sàng lọc trầm cảm** từ **giọng nói** và
**cảm biến thụ động** (điện thoại/thiết bị đeo). Hướng này: (i) xuất phát từ **nhu cầu lâm sàng thật**
(khoảng trống điều trị trầm cảm rất lớn), (ii) chỉ dùng **dữ liệu công khai** và chạy được trên Kaggle,
(iii) có **khoảng trống nghiên cứu còn mở thật sự** mà em đã kiểm chứng, và (iv) đủ sâu để triển khai
thành nhiều bài báo cho cả chương trình nghiên cứu sinh (conference → journal).

> **Cập nhật theo góp ý của thầy — bổ sung yếu tố quantum-inspired.** Thầy có gợi ý nên đưa **quantum-inspired**
> vào hướng này. Em tiếp thu, và đề xuất tích hợp nó **đúng chỗ có lợi ích thật** thay vì "gắn nhãn lượng
> tử" cho sang: **tái sử dụng chính phương pháp quantum-inspired mà em đã tự xây trong QIGOA** — biểu diễn
> **Q-bit (α, β) + cổng xoay lượng tử** trên nền Grasshopper — nhưng chuyển công dụng của nó thành một
> **bộ chọn đặc trưng (feature selection) minh bạch, ổn định** đặt ở đầu pipeline. Cách này: (1) tạo **tính
> liên tục** với công trình QIGOA em đã làm (không phí công cũ); (2) phục vụ **trực tiếp** ba trụ cột
> generalization / calibration / fairness; (3) vẫn giữ **liêm chính khoa học** — quantum-inspired chỉ là
> *một thành phần có lợi ích đo được*, **không phải headline**, nên không kéo lại lỗi "gap hẹp" đã khiến em
> rời QIGOA. Chi tiết và phần **nói thẳng về giới hạn** ở **Mục 5**.

Toàn bộ định vị dưới đây em đã kiểm chứng qua rà soát tài liệu 2022–2026; mọi trích dẫn đều là công
trình có thật (các bài năm 2025–2026 em đánh dấu cần kiểm lại DOI trước khi nộp chính thức). Rất mong nhận
được góp ý của thầy về **trọng tâm** và **phạm vi**.

---

## 1. Bối cảnh và động lực lâm sàng

Trầm cảm là một trong những nguyên nhân gây gánh nặng tàn tật lớn nhất toàn cầu, và **khoảng trống điều
trị rất lớn** — một tỷ lệ đáng kể người bệnh, đặc biệt ở các nước thu nhập thấp, **không bao giờ được
sàng lọc hoặc chẩn đoán** (theo WHO). Sàng lọc hiện nay phụ thuộc vào thời gian của bác sĩ và thang tự
đánh giá, nên **không mở rộng quy mô được**.

**Giọng nói** (chỉ cần một đoạn ghi âm 2–3 phút) và **cảm biến thụ động trên điện thoại/thiết bị đeo**
cung cấp tín hiệu hành vi khách quan, chi phí gần bằng 0, thu thập được từ xa — mở ra khả năng sàng lọc
và theo dõi vượt ra ngoài phòng khám, **với điều kiện mô hình đủ đáng tin cậy để triển khai thực tế**.

> *Ghi chú:* các con số gánh nặng bệnh cụ thể (số người mắc, tỉ lệ chưa điều trị, tử vong do tự sát) em
> sẽ trích đúng nguồn WHO/GBD trong bản chính thức; ở đây chỉ nêu định tính để tránh sai số liệu.

---

## 2. Vấn đề của tài liệu hiện tại — cái gì đã bão hòa, cái gì còn mở

Rà soát các công trình 2022–2026 cho thấy lĩnh vực này **không thiếu bộ phân loại trầm cảm** — cái
thiếu là **mô hình đáng tin cậy, triển khai được**:

- **Phân loại trên một bộ dữ liệu đã bão hòa, và tệ hơn là thường không hợp lệ.** Nhiều nghiên cứu kiểm
  toán cho thấy các mô hình đạt điểm cao trên bộ phỏng vấn lâm sàng chuẩn (DAIC-WOZ) thực chất là do
  **"học tắt" (shortcut learning)** — bắt tín hiệu từ câu hỏi của người phỏng vấn chứ không phải dấu
  hiệu trầm cảm thật (Burdisso và cộng sự, ClinicalNLP@NAACL 2024; Patapati và cộng sự, ICMI 2025). Phê
  phán này **đã được thiết lập** — đóng góp của em không phải "phát hiện lại" nó, mà là **xây dựng dựa
  trên nó**.
- **Tổng quát hóa (generalization) được thừa nhận nhưng chưa giải quyết.** Benchmark chủ đạo về tổng
  quát hóa liên-bộ-dữ-liệu cho cảm biến thụ động (GLOBEM; Xu và cộng sự, IMWUT 2022) báo cáo: khoảng 19
  thuật toán, kể cả các phương pháp domain-generalization chuyên dụng, **gần như không vượt được baseline
  đoán lớp đa số** khi chuyển sang cohort khác. Với giọng nói, chuyển ngôn ngữ/liên-corpus cũng sụp đổ.
  Đây là **kết quả benchmark/âm tính tạo động cơ** cho nghiên cứu, không phải lời giải.
- **Calibration và giá trị lâm sàng gần như vắng mặt.** Hầu như không nghiên cứu digital-phenotyping nào
  báo cáo xác suất đầu ra có **được hiệu chỉnh (calibrated)** hay không, hoặc có mang lại **lợi ích lâm
  sàng ròng (net benefit / decision-curve)** hay không. Một ngoại lệ hiếm hoi (Weber và cộng sự,
  Frontiers in Psychiatry 2025) xác nhận đây là **trục còn mở và giá trị cao**.
- **Công bằng (equity) mới chỉ được giải quyết một phần** (giới tính đã có; tuổi/ngôn ngữ và việc **gộp
  calibration với fairness** còn mỏng).

---

## 3. Khoảng trống nghiên cứu (đã kiểm chứng) và giả thuyết trung tâm

> **Chưa có công trình nào xử lý ĐỒNG THỜI ba tiêu chí — tổng quát hóa (generalization), hiệu chỉnh xác
> suất + lợi ích lâm sàng (calibration/net-benefit), và công bằng theo nhóm (equity) — như các mục tiêu
> hạng-nhất, DƯỚI ĐIỀU KIỆN dịch chuyển phân phối (distribution shift), trên dữ liệu công khai
> giọng-nói + cảm-biến, trong MỘT quy trình đánh giá ngoại-kiểm chống-rò-rỉ thống nhất.**

**Giả thuyết:** một cách tiếp cận sàng lọc lấy **tiêu chí thành công chính** là (i) tổng quát hóa được
đo lường qua dịch chuyển bộ-dữ-liệu/ngôn-ngữ/thiết-bị, (ii) xác suất được hiệu chỉnh với lợi ích lâm
sàng chứng minh được, và (iii) hiệu năng công bằng giữa các nhóm — sẽ **triển khai lâm sàng tốt hơn**
mô hình "chính xác trên một corpus", và điều này **phát triển + kiểm chứng được hoàn toàn trên dữ
liệu công khai**.

> **Khoảng trống phụ (mở, hợp lệ cho phần quantum-inspired):** rà soát cho thấy **chưa có** công trình
> quantum-inspired nào cho (a) **tổng quát hóa chéo-ngôn-ngữ/chéo-bộ-dữ-liệu** trong sàng lọc trầm cảm,
> hay (b) **công bằng theo nhóm (fairness/equity)** trong sức khỏe tâm thần (hit duy nhất — Perrier, AIES
> 2021 — là *quantum thật* và mang tính khái niệm). Đây là hai "làn trống" mà một thành phần quantum-inspired
> **có thể chính danh chiếm chỗ**, miễn được kiểm chứng đối đầu với baseline classical mạnh (xem Mục 5).

---

## 4. Đóng góp đề xuất

1. **Một quy trình đánh giá ngoại-kiểm chống-rò-rỉ** cho sàng lọc trầm cảm từ giọng nói/cảm biến (chia
   tách theo subject; huấn luyện chỉ trên lời của bệnh nhân để loại "shortcut" từ người phỏng vấn; đánh
   giá **leave-one-dataset-out / zero-shot cross-lingual**).
2. **Đưa calibration + giá trị lâm sàng thành metric chính** — reliability/ECE, hiệu chỉnh hậu kỳ,
   uncertainty bằng conformal prediction, và **phân tích decision-curve / net-benefit** dưới distribution
   shift (đây là trục còn mở nhất).
3. **Xử lý fairness gắn liền với calibration**: đo và giảm chênh lệch calibration/coverage giữa các nhóm
   (giới/tuổi/ngôn ngữ), **cùng nhau** chứ không tách rời.
4. **Nghiên cứu liên-mô-thức (cross-modality)** bắc cầu giữa hai dòng tài liệu giọng-nói và cảm-biến hiện
   đang tách biệt, đỉnh điểm là một tín hiệu **cảnh báo sớm theo thời gian (longitudinal)**.
5. **(MỚI — theo góp ý của thầy) Bộ chọn đặc trưng quantum-inspired minh bạch**, tái sử dụng dòng QIGOA
   (quantum-binary GOA: biểu diễn Q-bit + cổng xoay lượng tử) làm **wrapper feature selection** trên đặc
   trưng giọng nói + cảm biến. Mục tiêu **không** phải "chính xác hơn nhờ lượng tử", mà là tập đặc trưng
   **gọn hơn, ổn định hơn, transfer chéo-bộ-dữ-liệu tốt hơn, và liệt kê/audit được theo nhóm** — được kiểm
   chứng **đối đầu với wrapper classical mạnh** kèm mean±std + Wilcoxon (chi tiết + giới hạn ở **Mục 5**).

> *Nói thẳng về phạm vi (để thầy nắm rõ):* đây là một **đóng góp về AI đáng tin cậy (trustworthy-ML) có
> động cơ lâm sàng mạnh** — điểm mới nằm ở **độ chặt phương pháp + khả năng triển khai**, không phải một mô
> thức bệnh mới. Yếu tố **quantum-inspired đóng vai thành phần phục vụ** ba trụ cột, **không** phải trọng
> tâm marketing; em sẽ dẫn dắt bằng **ngoại-kiểm + net-benefit** để giữ ý nghĩa lâm sàng.

---

## 5. Thành phần quantum-inspired (theo góp ý của thầy)

**Định vị trung thực trước đã.** Tổng quan hệ thống lớn nhất tới nay (Gupta và cộng sự, *npj Digital
Medicine* 2025: sàng 4.915 nghiên cứu, giữ 46) kết luận **"chưa có bằng chứng rõ ràng rằng quantum ML mang
lại lợi thế thực nghiệm cho xử lý dữ liệu digital health"**. Vì vậy em **không** tuyên bố "ưu thế lượng tử".
Em đưa quantum-inspired vào **chỉ ở chỗ có lợi ích cụ thể, đo được**, và luôn benchmark với đối thủ classical
mạnh. Lưu ý thuật ngữ: các phương pháp này là **quantum-*inspired*** — **chạy trên phần cứng cổ điển**, không
có quantum speedup; em sẽ gọi đúng tên trong suốt bài.

### 5.1 Nguyên tắc tích hợp (để không rơi vào "gắn nhãn lượng tử")

- **Gọi đúng tên:** *quantum-inspired (classical hardware)*; tuyệt đối không ngụ ý "quantum advantage".
- **Mỗi thành phần phải chứng minh một lợi ích cụ thể** (đặc trưng gọn hơn / lựa chọn ổn định hơn / bền
  vững hơn dưới distribution shift / biểu diễn xác suất tốt hơn / hợp nhất đa-mô-thức diễn giải được), so
  với một **đối thủ classical thực hiện cùng chức năng**, có **mean±std qua nhiều lần chạy + kiểm định**.
- **Ghi nhớ các cảnh báo học thuật:** Tang 2019 (*dequantization* — nhiều "ưu thế lượng tử" sụp đổ khi có
  thuật toán classical đúng); Gupta 2025 (review digital health nói trên); Norval & Wang 2025 (trên nhận
  dạng cảm xúc giọng nói, mô hình lượng tử mô phỏng chỉ đạt ~34–43% so với **73,9%** của CNN-LSTM). → Không
  dẫn dắt bằng **độ chính xác thô**; nếu thành phần QI không thắng baseline classical trên tiêu chí đã
  chọn, em sẽ **báo cáo kết quả âm tính một cách trung thực**.

### 5.2 Phương án A — ĐỀ XUẤT CHÍNH: QI feature selection làm "front-end" minh bạch & bền vững

**Ý tưởng:** dùng lại chính **quantum-binary GOA** của QIGOA (mỗi đặc trưng ↔ một Q-bit `(α, β)`; cổng xoay
lượng tử với **góc xoay thích nghi theo fitness-gap** — đúng cơ chế em đã cài trong `qigoa.py`) làm **wrapper
feature selection**: chọn một **tập con đặc trưng gọn** từ không gian đặc trưng chiều cao — giọng nói
(eGeMAPS / wav2vec / lớp giữa WavLM) và cảm biến thụ động (marker hành vi GLOBEM) — rồi đưa vào một classifier
chuẩn.

**Căn cứ (đều là công trình thật):**
- **Kaur, Rathi & Agrawal (2022), *Computers in Biology and Medicine*** — Quantum Whale Optimization cho
  feature selection **trên chính DAIC-WOZ**, phát hiện trầm cảm từ giọng nói (F1 ≈ 0,85/0,93). *Tiền lệ gần
  nhất: đúng bài toán, đúng bộ dữ liệu, đúng họ phương pháp quantum-inspired.*
- **Wang, Chen, Li, Wan & Huang (2020), *Int. J. Approximate Reasoning*** — **quantum-binary GOA cho feature
  selection** (đúng dòng thuật toán QIGOA của em), cho tỉ lệ rút gọn/độ ổn định tốt hơn các swarm baseline.
- **Mücke, Piatkowski & Morik (2021)** — feature selection kiểu lượng tử **ngang** classical về accuracy
  nhưng **không suy giảm khi dữ liệu hạn chế/nhiễu** (classical thì suy giảm). Đây là **cơ chế lợi ích thật,
  có trích dẫn** cho trụ **generalization**.
- **Vivek, Ravi & Radha Krishna (2024)** — survey QIEA cho feature selection (56 công trình), khung Q-bit +
  rotation gate; dùng làm nền lý thuyết và khung "nói thẳng về khoảng trống".

**Vì sao phục vụ đúng ba trụ cột:**
- **Generalization:** tập đặc trưng gọn + chọn ổn định → **transfer chéo-bộ-dữ-liệu/chéo-ngôn-ngữ tốt hơn**
  (đúng cơ chế Mücke 2021).
- **Fairness:** tập đặc trưng **liệt kê được** → có thể **audit đặc trưng nào chi phối dự đoán theo từng
  nhóm** (giới/tuổi/ngôn ngữ) — điều mà một mạng đặc-trưng-ẩn khó làm.
- **Calibration:** ít đặc trưng nhiễu → nền sạch hơn cho hiệu chỉnh xác suất.

**Nói thẳng về giới hạn (bắt buộc):** QI-FS thường **ngang, không vượt** về accuracy. Vì vậy em **đăng ký
trước** tuyên bố mục tiêu là *"ít đặc trưng hơn / lựa chọn ổn định hơn / transfer chéo tốt hơn"*, và benchmark
với **wrapper classical mạnh** (không phải chỉ filter đơn giản), kèm mean±std + Wilcoxon.

### 5.3 Phương án B — bổ trợ: "density-matrix head" nối vào trụ calibration/conformal

Thay softmax cuối bằng một **lớp density-matrix quantum-inspired** cho **phân phối dự đoán theo quy tắc Born**,
rồi bọc bằng **conformal prediction** để có coverage phân-phối-tự-do.
- **Căn cứ:** González, Ramos-Pollán & Gallego (2023) — *kernel density matrices* (classical, cho phân phối
  dự đoán đầy đủ); Park & Simeone (2024), *IEEE TQE* — *quantum conformal prediction* (bắc cầu conformal ↔
  biểu diễn lượng tử).
- **Vì sao hợp:** cung cấp **nền biểu diễn xác suất có nguyên tắc** cho calibration + net-benefit và là chỗ
  đặt tự nhiên cho conformal mà em **đã** dự kiến.
- **Nói thẳng về giới hạn:** đầu ra density-matrix là **một phân phối, KHÔNG tự động được calibrated** → vẫn
  phải báo cáo **ECE + reliability diagram** và áp **conformal/temperature scaling**. Chỉ tuyên bố "một nền
  uncertainty có nguyên tắc", **không** tuyên bố "được hiệu chỉnh nhờ cấu trúc".

### 5.4 Phương án C — mở rộng: QI multimodal fusion diễn giải được

Hợp nhất **giọng nói + cảm biến** bằng hình thức phức (superposition = tương tác trong-mô-thức; entanglement
= tương tác chéo-mô-thức) thay cho khối attention hộp-đen.
- **Căn cứ:** Li, Gkoumas, Lioma & Melucci (2021), *Information Fusion* — "ngang SOTA nhưng **diễn giải được**".
- **Vì sao hợp:** các số hạng tương tác chéo-mô-thức **diễn giải được** ⇒ tăng tính minh bạch/tin cậy; toán
  tử hợp nhất có nguyên tắc có thể **transfer sạch hơn** giữa cohort.
- **Nói thẳng về giới hạn:** nguồn tự báo cáo *"comparable, not superior"* về accuracy ⇒ biện minh bằng
  **interpretability**, và phải **vượt attention-fusion classical mạnh** mới được giữ lại.

### 5.5 Khuyến nghị của em

Dẫn bằng **Phương án A** (tái dụng IP QIGOA, có tiền lệ cùng-dataset Kaur 2022, lợi ích map 1:1 vào
generalization + fairness). Gắn **Phương án B** vào trụ calibration. Coi **Phương án C** là phần mở rộng
về interpretability. Trong mọi trường hợp: gọi đúng "quantum-inspired", và chứng minh lợi ích **đối đầu với
đối thủ classical mạnh** — biến gợi ý "thêm quantum" của thầy từ rủi ro "gimmick" thành **một đóng góp có
căn cứ, tuân thủ liêm chính**.

---

## 6. Dữ liệu, phương pháp và đánh giá (đều công khai, compute vừa phải)

- **Dữ liệu công khai — giọng nói:** DAIC-WOZ / E-DAIC (tiếng Anh), Androids (tiếng Ý), MODMA (tiếng
  Trung; kèm EEG), EATD (tiếng Quan thoại), D-Vlog (in-the-wild) → dùng để **kiểm định chéo ngôn ngữ**.
  **Cảm biến thụ động:** GLOBEM (nhiều năm — nền tảng chính cho generalization/longitudinal), StudentLife,
  DEPRESJON/PSYKOSE (actigraphy). Tất cả đều mở cho nghiên cứu (em sẽ xác nhận license từng bộ).
- **Backbone (chạy được trên Kaggle):** đặc trưng **WavLM** đóng băng (dùng lớp giữa — mạnh nhất cho
  trầm cảm) + một head nhẹ — **không cần pretraining quy mô lớn**; mô hình temporal + bộ harness benchmark
  của GLOBEM cho phần cảm biến.
- **Thành phần quantum-inspired (Mục 5):** **QI feature selection** (quantum-binary GOA) đặt **trước**
  classifier trên đặc trưng giọng nói + cảm biến (Phương án A); **tùy chọn** density-matrix head + conformal
  cho calibration (Phương án B). **Nguyên tắc bất di bất dịch:** mỗi khối QI luôn được so với **một baseline
  classical cùng chức năng** (ví dụ: wrapper FS classical mạnh; softmax + temperature/conformal).
- **Metric/quy trình:** AUROC + **AUPRC**; **ECE / Brier / reliability diagram** + hiệu chỉnh hậu kỳ +
  conformal; **decision-curve analysis / net benefit**; chênh lệch AUROC/calibration giữa nhóm +
  equalized-odds; **cho thành phần QI:** thêm **số đặc trưng được chọn, độ ổn định lựa chọn (stability
  index), và khoảng chênh in-domain vs external** để đo đúng lợi ích đã tuyên bố; báo cáo **rõ ràng** khoảng
  chênh in-domain vs external; tái lập bằng seed cố định và kiểm định Wilcoxon/Friedman + Holm.
- **Liêm chính:** đây là **thiết kế đề xuất** — **không báo cáo bất kỳ số liệu thực nghiệm nào cho tới
  khi có kết quả chạy thật**; mọi tuyên bố định lượng trong bản thảo sau này sẽ truy vết về được một
  script có thể chạy lại.

---

## 7. Cấu trúc luận án (conference → journal, 4 bài)

| Bài | Trọng tâm | Dữ liệu | Loại |
|---|---|---|---|
| **P1** | Sàng lọc từ giọng nói, **chống shortcut + ngoại-kiểm** đa ngôn ngữ; **QI feature selection** làm front-end minh bạch (Phương án A) | DAIC/E-DAIC → LODO Androids/MODMA/EATD | Conference (Interspeech/ICASSP) |
| **P2** | **Calibration + net-benefit** của mô hình giọng nói (liên-corpus); tùy chọn **density-matrix + conformal** (Phương án B) | cùng bộ giọng nói | Journal (JMIR / npj Digital Medicine) |
| **P3** | **Fairness + calibration** liên-mô-thức; **audit theo nhóm qua tập đặc trưng QI** | giọng nói + GLOBEM (+ text) | Journal |
| **P4** | Cảnh báo sớm **theo thời gian**, có calibration + công bằng (deterioration/trajectory) | GLOBEM (nhiều năm) + replication | Flagship journal (IMWUT / npj Digital Medicine) |

**Sản phẩm trước mắt = P1**, tự thân đã là một bài conference hoàn chỉnh và giúp giảm rủi ro cho cả
chương trình. **Thành phần quantum-inspired** đi xuyên suốt như một *nhánh phương pháp*: nổi bật ở **P1**
(transfer chéo-ngôn-ngữ nhờ tập đặc trưng gọn) và **P3** (audit fairness qua tập đặc trưng liệt-kê-được),
kết nối tự nhiên với calibration ở **P2**.

---

## 8. Hạn chế trung thực (cần bàn với thầy)

1. **Nhãn tái phát (relapse) theo thời gian khan hiếm trong dữ liệu công khai.** GLOBEM chỉ có điểm thang
   đo trầm cảm định kỳ, **không có sự kiện relapse do lâm sàng xác nhận** (bộ lý tưởng là RADAR-MDD nhưng
   bị giới hạn truy cập). → P4 sẽ nhắm dự báo **deterioration/severity-trajectory**, không hứa
   clinician-verified relapse, trừ khi xin được dữ liệu giới hạn/hợp tác.
2. **Đây là đóng góp về độ chặt/độ tin cậy**, không phải một mô thức lâm sàng mới — phải dẫn dắt bằng
   ngoại-kiểm + net-benefit để thuyết phục reviewer lâm sàng.
3. **Quantum-inspired KHÔNG đảm bảo ưu thế.** Nó chạy trên phần cứng cổ điển, **không có quantum speedup**;
   tổng quan hệ thống 2025 (Gupta và cộng sự, *npj Digital Medicine*) **chưa** thấy bằng chứng rõ QML vượt
   classical cho digital health, và có tiền lệ (Norval & Wang 2025) mô hình lượng tử thua CNN-LSTM về
   accuracy. Do đó em **chỉ giữ** thành phần QI nếu nó **vượt baseline classical mạnh trên tiêu chí cụ thể**
   (số đặc trưng, độ ổn định, transfer chéo, chất lượng uncertainty); nếu không, em sẽ **báo cáo trung thực
   kết quả âm tính** và coi đó là một đóng góp benchmark hợp lệ.
4. **License dữ liệu và một vài trích dẫn rất mới (2025–2026)** cần được xác nhận DOI trước khi viết bản
   chính thức (gồm cả một số bài quantum-inspired chỉ mới thấy ở mức listing — xem ghi chú cuối).

---

## 9. Câu hỏi kính nhờ thầy góp ý

- Trọng tâm bài P1 nên nghiêng về **giọng nói** (em đề xuất, vì nhẹ và cross-lingual rõ ràng) hay khởi
  động bằng **cảm biến thụ động (GLOBEM)**?
- **Về quantum-inspired:** thầy muốn nó đóng vai **một thành phần phương pháp** (đề xuất của em — QI feature
  selection ở Phương án A, an toàn về gap và tái dụng QIGOA) hay muốn nâng thành **một trục đóng góp riêng**
  (tham vọng hơn nhưng cần nhiều ablation và rủi ro reviewer hỏi "vì sao cần lượng tử")? Em nghiêng về
  phương án thành-phần.
- Thầy có nhắm tới một **venue** cụ thể (Interspeech/ICASSP so với JMIR/npj Digital Medicine) để em định
  dạng ngay từ đầu không?
- Có khả năng tiếp cận **dữ liệu lâm sàng** (giọng nói/relapse có nhãn) qua hợp tác của thầy không? Nếu
  có, P4 sẽ mạnh hơn nhiều (relapse thật thay vì chỉ trajectory).

---

## Tài liệu tham khảo (đã kiểm chứng; bài 2025–2026 đánh dấu cần soát lại DOI)

**Trustworthy depression screening (hướng chính):**

1. J. Burdisso và cộng sự, "DAIC-WOZ: On the Validity of Using the Therapist's Prompts…," *ClinicalNLP @
   NAACL*, 2024. arXiv:2404.14463.
2. Patapati và cộng sự, "Most DAIC-WOZ Depression Classifiers Are Invalid…," *ICMI Companion*, 2025.
   doi:10.1145/3747327.3763034.
3. X. Xu và cộng sự, "GLOBEM: Cross-Dataset Generalization of Longitudinal Human Behavior Modeling," *ACM
   IMWUT*, 2022. doi:10.1145/3569485; dataset arXiv:2211.02733.
4. "Probing Mental Health Information in Speech Foundation Models," 2024. arXiv:2409.19042.
5. Dang và cộng sự, "Fairness and bias correction in ML for depression prediction across four
   populations," *Scientific Reports*, 2024. doi:10.1038/s41598-024-58427-7.
6. Weber và cộng sự, "Depression diagnosis from patient interviews using multimodal ML" (calibration +
   net benefit), *Frontiers in Psychiatry*, 2025. doi:10.3389/fpsyt.2025.1694762.
7. Li và cộng sự, "Fair Uncertainty Quantification for Depression Prediction," 2025. arXiv:2505.04931.
8. Amin và cộng sự, "Mobile sensing for longitudinal prediction of depression severity: systematic
   review," *JMIR*, 2025. doi:10.2196/57418.
9. Mancini và cộng sự, "Promoting the Responsible Development of Speech Datasets for Mental Health…,"
   *JAIR* 82, 2025. arXiv:2406.04116.
10. S. Chen và cộng sự, "WavLM: Large-Scale Self-Supervised Pre-Training for Full Stack Speech
    Processing," *IEEE JSTSP*, 2022.
11. A. Vickers, E. Elkin, "Decision Curve Analysis," *Medical Decision Making*, 2006. *(phương pháp
    net-benefit)*.
12. Bộ dữ liệu: Gratch và cộng sự, DAIC-WOZ (*LREC* 2014); AVEC-2019/E-DAIC; Cai và cộng sự, MODMA; R.
    Wang và cộng sự, StudentLife (*UbiComp* 2014).

**Quantum-inspired (Mục 5 — bổ sung theo góp ý của thầy; đã kiểm chứng qua web):**

13. B. Kaur, S. Rathi, R. K. Agrawal, "Enhanced depression detection from speech using Quantum Whale
    Optimization Algorithm for feature selection," *Computers in Biology and Medicine* 150:106122, 2022.
    doi:10.1016/j.compbiomed.2022.106122. *(QWOA feature selection trên chính DAIC-WOZ — tiền lệ gần nhất.)*
14. D. Wang, H. M. Chen, T. R. Li, J. H. Wan, Y. Y. Huang, "A novel quantum grasshopper optimization
    algorithm for feature selection," *Int. J. Approximate Reasoning* 127:33–53, 2020.
    doi:10.1016/j.ijar.2020.08.010. *(Đúng dòng thuật toán QIGOA, cho feature selection.)*
15. S. Mücke, N. Piatkowski, K. Morik, "Quantum Annealing for Automated Feature Selection in Stress
    Detection," IEEE, 2021. arXiv:2106.05134. *(Bằng chứng lợi ích thật: bền vững khi dữ liệu hạn chế.)*
16. Y. Vivek, V. Ravi, P. Radha Krishna, "Quantum-Inspired Evolutionary Algorithms for Feature Subset
    Selection: A Comprehensive Survey," 2024. arXiv:2407.17946.
17. F. A. González, R. Ramos-Pollán, A. Gallego, "Kernel Density Matrices for Probabilistic Deep
    Learning," *Quantum Machine Intelligence* (Springer), 2023/2025. arXiv:2305.18204.
18. S. Park, O. Simeone, "Quantum Conformal Prediction for Reliable Uncertainty Quantification in Quantum
    Machine Learning," *IEEE Trans. Quantum Engineering* 5:3103224, 2024. arXiv:2304.03398.
19. Q. Li, D. Gkoumas, C. Lioma, M. Melucci, "Quantum-inspired multimodal fusion for video sentiment
    analysis," *Information Fusion* 65:58–71, 2021. doi:10.1016/j.inffus.2020.08.006.
20. M. Norval, Z. Wang, "Quantum AI in Speech Emotion Recognition," *Entropy* 27(12):1201, 2025.
    doi:10.3390/e27121201. *(So sánh trung thực: mô hình lượng tử mô phỏng thua CNN-LSTM về accuracy.)*
21. M. S. H. Onim, T. S. Humble, H. Thapliyal, "Emotion Recognition in Older Adults with Quantum Machine
    Learning and Wearable Sensors," 2025. arXiv:2507.08175. *(Liên quan trụ cảm-biến thụ động.)*

**Cảnh báo học thuật (để tích hợp trung thực):**

22. E. Tang, "A Quantum-Inspired Classical Algorithm for Recommendation Systems," *STOC '19*, 2019.
    arXiv:1807.04271; doi:10.1145/3313276.3316310. *(Dequantization — cảnh báo "ưu thế lượng tử" có thể sụp.)*
23. R. S. Gupta, C. E. Wood, T. Engstrom, J. D. Pole, S. Shrapnel, "Quantum Machine Learning for Digital
    Health? A Systematic Review," *npj Digital Medicine*, 2025. arXiv:2410.02446. *(Chưa có bằng chứng QML
    vượt classical cho digital health — cảnh báo quan trọng nhất.)*
24. E. Perrier, "Quantum Fair Machine Learning," *AAAI/ACM AIES '21*, 2021. doi:10.1145/3461702.3462611.
    *(Hit duy nhất về quantum × fairness — là quantum thật, mang tính khái niệm; khẳng định đây là làn trống.)*

> *Ghi chú liêm chính:* các bài 2025–2026 (vd kiểm toán đa-probe, mở rộng về interviewer-effects; và một số
> bài quantum-inspired trên EEG/schizophrenia em mới chỉ thấy ở mức listing như Ma và cộng sự 2023, các bài
> QI-EEG 2024–2025) là công trình có thật nhưng cần **xác minh DOI/venue cuối cùng** trước khi đưa vào bản
> nộp. Các mục 13–24 ở trên đều đã được kiểm chứng qua web ở phiên rà soát này.

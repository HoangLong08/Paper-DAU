# HƯỚNG TIẾP CẬN PAPER

## AI đáng tin cậy để sàng lọc trầm cảm từ giọng nói và cảm biến thụ động

### (Trustworthy Digital Phenotyping for Depression)

**Nghiên cứu sinh:** Nguyễn Võ Hoàng Long **Ngày:** 04/07/2026

### Kính gửi thầy,

Em xin trình bày hướng tiếp cận mới cho luận án, thay cho hướng QIGOA
(multilevel thresholding lượng tử) trước đây. Lý do đổi hướng: sau khi
em rà soát kỹ tài liệu, gap của QIGOA **có thật nhưng hẹp** --- việc
\"thêm quantum vào GOA\" và \"quantum cho thresholding\" đều đã có nhiều
công bố, khó đạt tầm tạp chí Q1 nếu không đầu tư rất nhiều ablation và
kiểm định thống kê.

Hướng mới em đề xuất là **AI đáng tin cậy (trustworthy AI) để sàng lọc
trầm cảm** từ **giọng nói** và **cảm biến thụ động** (điện thoại/thiết
bị đeo). Hướng này: (i) xuất phát từ **nhu cầu lâm sàng thật** (khoảng
trống điều trị trầm cảm rất lớn), (ii) chỉ dùng **dữ liệu công khai** và
chạy được trên Kaggle, (iii) có **khoảng trống nghiên cứu còn mở thật
sự** mà em đã kiểm chứng, và (iv) đủ sâu để triển khai thành nhiều bài
báo cho cả chương trình nghiên cứu sinh (conference → journal).

Toàn bộ định vị dưới đây em đã kiểm chứng qua rà soát tài liệu
2022--2026; mọi trích dẫn đều là công trình có thật (các bài năm 2026 em
đánh dấu cần kiểm lại DOI trước khi nộp chính thức). Rất mong nhận được
góp ý của thầy về **trọng tâm** và **phạm vi**.

## 1. Bối cảnh và động lực lâm sàng

Trầm cảm là một trong những nguyên nhân gây gánh nặng tàn tật lớn nhất
toàn cầu, và **khoảng trống điều trị rất lớn** --- một tỷ lệ đáng kể
người bệnh, đặc biệt ở các nước thu nhập thấp, **không bao giờ được sàng
lọc hoặc chẩn đoán** (theo WHO). Sàng lọc hiện nay phụ thuộc vào thời
gian của bác sĩ và thang tự đánh giá, nên **không mở rộng quy mô được**.

**Giọng nói** (chỉ cần một đoạn ghi âm 2--3 phút) và **cảm biến thụ động
trên điện thoại/thiết bị đeo** cung cấp tín hiệu hành vi khách quan, chi
phí gần bằng 0, thu thập được từ xa --- mở ra khả năng sàng lọc và theo
dõi vượt ra ngoài phòng khám, **với điều kiện mô hình đủ đáng tin cậy để
triển khai thực tế**.

> *Ghi chú:* các con số gánh nặng bệnh cụ thể (số người mắc, tỉ lệ chưa
> điều trị, tử vong do tự sát) em sẽ trích đúng nguồn WHO/GBD trong bản
> chính thức; ở đây chỉ nêu định tính để tránh sai số liệu.

## 2. Vấn đề của tài liệu hiện tại --- cái gì đã bão hòa, cái gì còn mở

Rà soát các công trình 2022--2026 cho thấy lĩnh vực này **không thiếu bộ
phân loại trầm cảm** --- cái thiếu là **mô hình đáng tin cậy, triển khai
được**:

-   **Phân loại trên một bộ dữ liệu đã bão hòa, và tệ hơn là thường
    không hợp lệ.** Nhiều nghiên cứu kiểm toán cho thấy các mô hình đạt
    điểm cao trên bộ phỏng vấn lâm sàng chuẩn (DAIC-WOZ) thực chất là do
    **\"học tắt\" (shortcut learning)** --- bắt tín hiệu từ câu hỏi của
    người phỏng vấn chứ không phải dấu hiệu trầm cảm thật (Burdisso và
    cộng sự, ClinicalNLP\@NAACL 2024; Patapati và cộng sự, ICMI 2025).
    Phê phán này **đã được thiết lập** --- đóng góp của em không phải
    \"phát hiện lại\" nó, mà là **xây dựng dựa trên nó**.
-   **Tổng quát hóa (generalization) được thừa nhận nhưng chưa giải
    quyết.** Benchmark chủ đạo về tổng quát hóa liên-bộ-dữ-liệu cho cảm
    biến thụ động (GLOBEM; Xu và cộng sự, IMWUT 2022) báo cáo: khoảng 19
    thuật toán, kể cả các phương pháp domain-generalization chuyên dụng,
    **gần như không vượt được baseline đoán lớp đa số** khi chuyển sang
    cohort khác. Với giọng nói, chuyển ngôn ngữ/liên-corpus cũng sụp đổ.
    Đây là **kết quả benchmark/âm tính tạo động cơ** cho nghiên cứu,
    không phải lời giải.
-   **Calibration và giá trị lâm sàng gần như vắng mặt.** Hầu như không
    nghiên cứu digital-phenotyping nào báo cáo xác suất đầu ra có **được
    hiệu chỉnh (calibrated)** hay không, hoặc có mang lại **lợi ích lâm
    sàng ròng (net benefit / decision-curve)** hay không. Một ngoại lệ
    hiếm hoi (Weber và cộng sự, Frontiers in Psychiatry 2025) xác nhận
    đây là **trục còn mở và giá trị cao**.
-   **Công bằng (equity) mới chỉ được giải quyết một phần** (giới tính
    đã có; tuổi/ngôn ngữ và việc **gộp calibration với fairness** còn
    mỏng).

## 3. Khoảng trống nghiên cứu (đã kiểm chứng) và giả thuyết trung tâm

> **Chưa có công trình nào xử lý ĐỒNG THỜI ba tiêu chí --- tổng quát hóa
> (generalization), hiệu chỉnh xác suất + lợi ích lâm sàng
> (calibration/net-benefit), và công bằng theo nhóm (equity) --- như các
> mục tiêu hạng-nhất, DƯỚI ĐIỀU KIỆN dịch chuyển phân phối (distribution
> shift), trên dữ liệu công khai giọng-nói + cảm-biến, trong MỘT quy
> trình đánh giá ngoại-kiểm chống-rò-rỉ thống nhất.**

**Giả thuyết:** một cách tiếp cận sàng lọc lấy **tiêu chí thành công
chính** là (i) tổng quát hóa được đo lường qua dịch chuyển
bộ-dữ-liệu/ngôn-ngữ/thiết-bị, (ii) xác suất được hiệu chỉnh với lợi ích
lâm sàng chứng minh được, và (iii) hiệu năng công bằng giữa các nhóm ---
sẽ **triển khai lâm sàng tốt hơn** mô hình \"chính xác trên một
corpus\", và điều này **phát triển + kiểm chứng được hoàn toàn trên dữ
liệu công khai**.

## 4. Đóng góp đề xuất

1.  **Một quy trình đánh giá ngoại-kiểm chống-rò-rỉ** cho sàng lọc trầm
    cảm từ giọng nói/cảm biến (chia tách theo subject; huấn luyện chỉ
    trên lời của bệnh nhân để loại \"shortcut\" từ người phỏng vấn; đánh
    giá **leave-one-dataset-out / zero-shot cross-lingual**).
2.  **Đưa calibration + giá trị lâm sàng thành metric chính** ---
    reliability/ECE, hiệu chỉnh hậu kỳ, uncertainty bằng conformal
    prediction, và **phân tích decision-curve / net-benefit** dưới
    distribution shift (đây là trục còn mở nhất).
3.  **Xử lý fairness gắn liền với calibration**: đo và giảm chênh lệch
    calibration/coverage giữa các nhóm (giới/tuổi/ngôn ngữ), **cùng
    nhau** chứ không tách rời.
4.  **Nghiên cứu liên-mô-thức (cross-modality)** bắc cầu giữa hai dòng
    tài liệu giọng-nói và cảm-biến hiện đang tách biệt, đỉnh điểm là một
    tín hiệu **cảnh báo sớm theo thời gian (longitudinal)**.

> *Nói thẳng về phạm vi (để thầy nắm rõ):* đây là một **đóng góp về AI
> đáng tin cậy (trustworthy-ML) có động cơ lâm sàng mạnh** --- điểm mới
> nằm ở **độ chặt phương pháp + khả năng triển khai**, không phải một mô
> thức bệnh mới. Em sẽ dẫn dắt bằng **ngoại-kiểm + net-benefit** để giữ
> ý nghĩa lâm sàng.

## 5. Dữ liệu, phương pháp và đánh giá (đều công khai, compute vừa phải)

-   **Dữ liệu công khai --- giọng nói:** DAIC-WOZ / E-DAIC (tiếng Anh),
    Androids (tiếng Ý), MODMA (tiếng Trung; kèm EEG), EATD (tiếng Quan
    thoại), D-Vlog (in-the-wild) → dùng để **kiểm định chéo ngôn ngữ**.
    **Cảm biến thụ động:** GLOBEM (nhiều năm --- nền tảng chính cho
    generalization/longitudinal), StudentLife, DEPRESJON/PSYKOSE
    (actigraphy). Tất cả đều mở cho nghiên cứu (em sẽ xác nhận license
    từng bộ).
-   **Backbone (chạy được trên Kaggle):** đặc trưng **WavLM** đóng băng
    (dùng lớp giữa --- mạnh nhất cho trầm cảm) + một head nhẹ ---
    **không cần pretraining quy mô lớn**; mô hình temporal + bộ harness
    benchmark của GLOBEM cho phần cảm biến.
-   **Metric/quy trình:** AUROC + **AUPRC**; **ECE / Brier / reliability
    diagram** + hiệu chỉnh hậu kỳ + conformal; **decision-curve analysis
    / net benefit**; chênh lệch AUROC/calibration giữa nhóm +
    equalized-odds; báo cáo **rõ ràng** khoảng chênh in-domain vs
    external; tái lập bằng seed cố định và kiểm định Wilcoxon/Friedman +
    Holm.
-   **Liêm chính:** đây là **thiết kế đề xuất** --- **không báo cáo bất
    kỳ số liệu thực nghiệm nào cho tới khi có kết quả chạy thật**; mọi
    tuyên bố định lượng trong bản thảo sau này sẽ truy vết về được một
    script có thể chạy lại.

## 6. Cấu trúc luận án (conference → journal, 4 bài)

  Bài      Trọng tâm                                                                                Dữ liệu                                  Loại
  -------- ---------------------------------------------------------------------------------------- ---------------------------------------- -------------------------------------------------
  **P1**   Sàng lọc từ giọng nói, **chống shortcut + ngoại-kiểm** đa ngôn ngữ                       DAIC/E-DAIC → LODO Androids/MODMA/EATD   Conference (Interspeech/ICASSP)
  **P2**   **Calibration + net-benefit** của mô hình giọng nói (liên-corpus)                        cùng bộ giọng nói                        Journal (JMIR / npj Digital Medicine)
  **P3**   **Fairness + calibration** liên-mô-thức                                                  giọng nói + GLOBEM (+ text)              Journal
  **P4**   Cảnh báo sớm **theo thời gian**, có calibration + công bằng (deterioration/trajectory)   GLOBEM (nhiều năm) + replication         Flagship journal (IMWUT / npj Digital Medicine)

**Sản phẩm trước mắt = P1**, tự thân đã là một bài conference hoàn chỉnh
và giúp giảm rủi ro cho cả chương trình.

## 7. Hạn chế trung thực (cần bàn với thầy)

1.  **Nhãn tái phát (relapse) theo thời gian khan hiếm trong dữ liệu
    công khai.** GLOBEM chỉ có điểm thang đo trầm cảm định kỳ, **không
    có sự kiện relapse do lâm sàng xác nhận** (bộ lý tưởng là RADAR-MDD
    nhưng bị giới hạn truy cập). → P4 sẽ nhắm dự báo
    **deterioration/severity-trajectory**, không hứa clinician-verified
    relapse, trừ khi xin được dữ liệu giới hạn/hợp tác.
2.  **Đây là đóng góp về độ chặt/độ tin cậy**, không phải một mô thức
    lâm sàng mới --- phải dẫn dắt bằng ngoại-kiểm + net-benefit để
    thuyết phục reviewer lâm sàng.
3.  **License dữ liệu và một vài trích dẫn rất mới (2026)** cần được xác
    nhận trước khi viết bản chính thức.

## 8. Câu hỏi kính nhờ thầy góp ý

-   Trọng tâm bài P1 nên nghiêng về **giọng nói** (em đề xuất, vì nhẹ và
    cross-lingual rõ ràng) hay khởi động bằng **cảm biến thụ động
    (GLOBEM)**?
-   Thầy có nhắm tới một **venue** cụ thể (Interspeech/ICASSP so với
    JMIR/npj Digital Medicine) để em định dạng ngay từ đầu không?
-   Có khả năng tiếp cận **dữ liệu lâm sàng** (giọng nói/relapse có
    nhãn) qua hợp tác của thầy không? Nếu có, P4 sẽ mạnh hơn nhiều
    (relapse thật thay vì chỉ trajectory).

## Tài liệu tham khảo (đã kiểm chứng; bài 2026 đánh dấu cần soát lại DOI)

1.  J. Burdisso và cộng sự, \"DAIC-WOZ: On the Validity of Using the
    Therapist\'s Prompts...,\" *ClinicalNLP @ NAACL*, 2024.
    arXiv:2404.14463.
2.  Patapati và cộng sự, \"Most DAIC-WOZ Depression Classifiers Are
    Invalid...,\" *ICMI Companion*, 2025. doi:10.1145/3747327.3763034.
3.  X. Xu và cộng sự, \"GLOBEM: Cross-Dataset Generalization of
    Longitudinal Human Behavior Modeling,\" *ACM IMWUT*, 2022.
    doi:10.1145/3569485; dataset arXiv:2211.02733.
4.  \"Probing Mental Health Information in Speech Foundation
    Models,\" 2024. arXiv:2409.19042.
5.  Dang và cộng sự, \"Fairness and bias correction in ML for depression
    prediction across four populations,\" *Scientific Reports*, 2024.
    doi:10.1038/s41598-024-58427-7.
6.  Weber và cộng sự, \"Depression diagnosis from patient interviews
    using multimodal ML\" (calibration + net benefit), *Frontiers in
    Psychiatry*, 2025. doi:10.3389/fpsyt.2025.1694762.
7.  Li và cộng sự, \"Fair Uncertainty Quantification for Depression
    Prediction,\" 2025. arXiv:2505.04931.
8.  Amin và cộng sự, \"Mobile sensing for longitudinal prediction of
    depression severity: systematic review,\" *JMIR*, 2025.
    doi:10.2196/57418.
9.  Mancini và cộng sự, \"Promoting the Responsible Development of
    Speech Datasets for Mental Health...,\" *JAIR* 82, 2025.
    arXiv:2406.04116.
10. S. Chen và cộng sự, \"WavLM: Large-Scale Self-Supervised
    Pre-Training for Full Stack Speech Processing,\" *IEEE JSTSP*, 2022.
11. A. Vickers, E. Elkin, \"Decision Curve Analysis,\" *Medical Decision
    Making*, 2006. *(phương pháp net-benefit)*.
12. Bộ dữ liệu: Gratch và cộng sự, DAIC-WOZ (*LREC* 2014);
    AVEC-2019/E-DAIC; Cai và cộng sự, MODMA; R. Wang và cộng sự,
    StudentLife (*UbiComp* 2014).

> *Ghi chú liêm chính:* các bài 2026 (vd kiểm toán đa-probe, mở rộng về
> interviewer-effects) là công trình có thật nhưng nằm sau mốc kiến thức
> của công cụ hỗ trợ; em sẽ xác minh DOI/venue cuối cùng trước khi đưa
> vào bản nộp.

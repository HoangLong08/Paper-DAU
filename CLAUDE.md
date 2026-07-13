# CLAUDE.md — Kỷ luật nghiên cứu & triển khai paper (CHỦ ĐỀ: ĐÃ CHỐT — QIGOA reality-check)

> **Tóm tắt cho tác giả (tiếng Việt):** File này là "luật chơi" mà Claude Code TỰ ĐỌC mỗi phiên.
> **Chủ đề đã chốt 13/07/2026** (§1). Các mục còn lại ghi kỷ luật **bất biến**:
> (0) cách làm việc, (1) **bối cảnh paper — ACTIVE**,
> (2) **liêm chính học thuật — luật sắt, không thương lượng**, (3) kỷ luật thực nghiệm,
> (4) chuẩn viết journal/Transaction, (5) **kỷ luật triển khai / reproducibility / provenance**,
> (6) khi nào dùng skill nào, (7) an toàn thao tác file, (8) **giao thức mỗi phiên + Definition of Done**,
> (9) preregistration & nhật ký thí nghiệm.
> **Sửa file này bất cứ lúc nào** — nó override hành vi mặc định của Claude.
> 📦 Hướng ứng viên cũ (depression phenotyping) **không còn trên đĩa** nhưng khôi phục được:
> `git show ad0977c^:docs/huong-tiep-can-mental-health-vi.md`. Không theo đuổi — đã có near-scoop (Pfohl et al., FAccT 2022).

---

## 0. Cách giao tiếp & làm việc

- **Giao tiếp bằng tiếng Việt.** Thuật ngữ kỹ thuật (calibration, ablation, leakage, net-benefit, LODO...) giữ nguyên tiếng Anh.
- **Quyết đoán, đẩy về phía submit.** Tác giả muốn Claude *tự ra quyết định có lý lẽ* (venue, baseline, hyperparameter, scope dữ liệu) thay vì hỏi lại nhiều. Nêu lý do ngắn để tác giả override nếu cần. **Chỉ hỏi khi đó là quyết định thật sự của tác giả** — VD: **chốt chủ đề nghiên cứu**, chọn tạp chí cuối cùng, đổi hẳn hướng.
- **Tham chiếu file bằng `path:line` có thể click.** VD: `docs/lam-va-viet-paper-chuan-IEEE.md:37`.
- **Ship theo lô, đừng nhỏ giọt.** Khi đã chốt hướng, đưa code/nội dung trong một lô hoàn chỉnh.
- Tác giả **chạy thí nghiệm trên Kaggle** → mọi code phải Kaggle-runnable (xem §5).

---

## 1. Bối cảnh paper — ✅ ACTIVE (chốt 13/07/2026)

**Hướng:** *Optimizing the Wrong Variable — Structural Degeneracy in Metaheuristic and Quantum-Inspired Multilevel Thresholding for Brain Tumor Segmentation.*

Thầy Hảo giao đề QIGOA (Kapur + Q-bit + rotation gate, brain tumor MRI). Đề gốc **không extend lên journal được** (metric sai loại, sai venue, zero novelty, hai lớp metaphor). Ta **giữ QIGOA làm nhân vật trung tâm nhưng đổi câu hỏi**: từ *"QIGOA có thắng không"* → *"QIGOA có thực sự giúp không, và ta đang đo đúng thứ chưa"*.

> ⚠️ **CẢNH BÁO CẤU TRÚC (14/07/2026, sau audit 24 agent).** Bài này **KHÔNG phải "4 mệnh đề ngang hàng"** và **KHÔNG phải một khám phá lý thuyết** — định lý đã có chủ (xem bảng near-rival). Nó là **một CHƯƠNG TRÌNH ĐO LƯỜNG + một CÔNG CỤ + một AUDIT**, hạng **Q2**. Bán như khám phá lý thuyết ⇒ chết. Chi tiết sửa đổi: [docs/preregistration.md](docs/preregistration.md) §6 (append-only).

- **LUẬN ĐỀ DUY NHẤT (bán cái này, không bán 4 mệnh đề):**
  > *Trong miền có ground truth lâm sàng, khoảng cách tối ưu mà cả dòng văn liệu đang tranh nhau **KHÔNG chiếu xuống mask lâm sàng**.*
  > **Bất tử trước kết quả thực nghiệm** — đúng ở CẢ HAI nhánh: nếu mọi metaheuristic đạt tối ưu ⇒ optimizer là đồ trang trí; nếu **không** đạt ⇒ cả một thập kỷ engineering đang đóng một gap chứng minh được là **không chiếu xuống lâm sàng**.

- **4 mệnh đề — vai trò ĐÃ HẠ CẤP** (tiêu chí bác bỏ: [docs/preregistration.md](docs/preregistration.md)):
  - **P1** Suy biến → **viết thành THẾ LƯỠNG NAN, TUYỆT ĐỐI KHÔNG phải quy kết.** Quy tắc "lớp sáng nhất" **KHÔNG tìm thấy trong văn liệu** — nó là code cũ của chính ta. Viết *"văn liệu decode bằng lớp sáng nhất [refs]"* = **xuyên tạc công trình được cite = vi phạm IRON RULE 2**. Xem prereg §6/A1.
  - **P2** → **hạ xuống 2 đoạn setup có citation**, không phải mệnh đề. Gần như không còn novelty (Menotti 2015 + Hammouche 2010 + Merzban 2019). Chỗ duy nhất còn sống: **random search ở equal-NFE**.
  - **P3** Goodhart trên trục k **với GT lâm sàng** → định vị là **xác nhận future-work mà Hegazy & Gabr tự khai**, không phải phát hiện độc lập. Decision rule cũ **không vận hành được** (n=7) — xem prereg §6/A4.
  - **P4** Trần → **oracle-1-khoảng KHÔNG phải trần của MỌI thresholding cường độ** (đó là phát biểu SAI, đã sửa). Trần đúng = **oracle level-set** (Lipton 2014). Và **François & Tinarrage đã in trần 0,83±0,18 trên BraTS** ⇒ **CẤM mọi câu "we establish the ceiling"**. Xem prereg §6/A2.

- **Đóng góp DƯƠNG (ĐÃ VIẾT LẠI — 3 thứ, KHÔNG có "exact solver"):**
  1. **Ceiling decomposition** — trần chỉ-FLAIR vs trần histogram chung 4-modality vs 2D U-Net cùng input ⇒ phân rã gap thành *"thông tin không có trong CƯỜNG ĐỘ"* vs *"không có trong PIXEL"*. **Chưa ai làm.** François nói *rằng* thresholding thất bại; ta nói **TẠI SAO**, định lượng.
  2. **Công cụ chẩn đoán O(L·log L)** — cho phép tác giả bất kỳ, dataset bất kỳ, tính trước **trần Dice của cả họ phương pháp** trong micro-giây, TRƯỚC khi viết dòng optimizer đầu tiên. (Cite Lipton 2014 / RankSEG — **claim ứng dụng, KHÔNG claim toán học**.)
  3. **Checklist giao thức đánh giá** + **Bảng I trắc lượng có mã hoá** (2 coder, Cohen's κ).
  > ❌ **"Bộ giải chính xác mili-giây" ĐÃ BỊ XOÁ khỏi đóng góp** — Menotti et al. 2015 đã in **exact Kapur, O((K−1)L²), <160 ms**, 11 năm trước. Ta chỉ **dùng** nó làm reference optimum và **cite trang trọng ở Abstract**.
  > ❌ **BỎ claim "~250× nhanh hơn"** — đó là artifact của vòng lặp Python, không phải của thuật toán. Đóng góp đặt lên: **tính chính xác** (đảm bảo tối ưu toàn cục) · **tính tất định** (không seed, không phương sai) · **không hyperparameter**. Đồng tiền chính = **NFE + độ phức tạp**, wall-clock chỉ là phụ.

- **Dữ liệu:** BraTS 2020 (Kaggle `awsaf49/brats20-dataset-training-validation`). ⚠️ **n=150 phải xem lại — cân nhắc dùng cả 369 ca** (oracle chạy trên histogram, chi phí ~ms/ảnh, không phải 30 s như kế hoạch ghi nhầm). ⚠️ **"Ngoại kiểm" LGG (`mateuszbuda/lgg-mri-segmentation`) CÓ THỂ KHÔNG NGOẠI**: Buda et al. = 110 ca **TCGA-LGG**, mà BraTS 2020 đã nuốt **108 ca TCGA-LGG** từ đúng collection đó. **PHẢI đối chiếu `name_mapping.csv` trước khi dùng chữ "external validation"** — nếu trùng mà vẫn gọi là ngoại kiểm thì đó là **misrepresentation**, không phải lỗi thiết kế.
- **Venue:** BSPC (chính, **chỉ trong bộ đồ "benchmark paper"**) → ESWA (dự phòng, có tiền lệ Merzban) → **Scientific Reports** (soundness-only review, negative results nằm rõ trong policy — nhưng APC ~USD 2.850, phải kiểm read-and-publish của trường). **KHÔNG nộp IEEE JBHI** — ⚠️ **lý do cũ ("desk-reject out-of-scope") là SAI**: "Imaging Informatics" nằm rõ trong scope chính thức của JBHI. Lý do đúng: **bar quá cao + độc giả thờ ơ với intensity thresholding**. **CẤM** Multimedia Tools & Applications, J. Ambient Intelligence (đã bị Clarivate delist khỏi WoS).
- **BẮT BUỘC: đăng arXiv preprint NGAY ngày nộp lần đầu.** Nhóm Hegazy & Gabr đang ra **2 bài/tháng** trên đúng seam này. Ưu tiên phải cắm cọc bằng preprint, không phải bằng ngày accept.
- **Compute:** ~40 h CPU Kaggle + ~2 h GPU. **Timeline thực tế: 12–14 tuần, không phải 8** (riêng Bảng I là 1 tuần và hiện chưa có trong lịch). Nút thắt là lập luận & viết, không phải compute.

**Near-rival PHẢI cite trang trọng & phân biệt (đã web-verify — cập nhật 14/07/2026 sau audit 24 agent; mọi DOI/arXiv ID dưới đây đã verify độc lập qua Crossref API + arXiv API):**
| Near-rival | Vì sao khác ta |
|---|---|
| 🔴🔴 **Menotti, Najman & de A. Araújo**, *Efficient Polynomial Implementation of Several Multithresholding Methods for Gray-Level Image Segmentation*, **LNCS/CIARP 2015, pp. 350–357**, `10.1007/978-3-319-25751-8_42` | **SCOOP TRỰC DIỆN "đóng góp dương" cũ.** Exact DP cho **Otsu + KAPUR + Kittler–Illingworth**, `O((K−1)L²)`, *"<160 ms … in whatever the number of classes"* — **đúng thuật toán, đúng hàm mục tiêu, đúng độ phức tạp, đúng bậc thời gian, in 11 năm trước.** ⇒ **"Bộ giải chính xác mili-giây" KHÔNG được claim là đóng góp.** Cite ở **Abstract**. Một bài có thesis *"các anh không cite lời giải chính xác"* mà không cite bài này = **tự thiêu trong một câu**. |
| 🔴🔴 **Hammouche, Diaf & Siarry**, *A comparative study of various meta-heuristic techniques applied to the multilevel thresholding problem*, **EAAI 23(5):676–688 (2010)**, `10.1016/j.engappai.2009.09.011` | **SCOOP P2.** Đã đọc toàn văn: Bảng 8 = nghiệm **vét cạn toàn cục**; Bảng 9 = mean±std của 6 metaheuristic so với nó; Bảng 10 = hội tụ định nghĩa bằng \|F−F_opt\| ≤ **1e−9** — **chính là hit-rate của P2, ngưỡng chặt hơn 1e−4 của ta 5 bậc, in 16 năm trước**. ⚠️ Họ còn thấy **ACO/SA KHÔNG đạt tối ưu khi k>2** ⇒ ngưỡng preregister `hit_rate ≥ 0,99 cho MỌI thuật toán ở MỌI k` có nguy cơ **tự bác bỏ**. |
| 🔴🔴 **Lipton, Elkan & Narayanaswamy**, *Thresholding Classifiers to Maximize F1 Score*, **arXiv:1402.1892** (ECML-PKDD 2014) + **RankSEG** (Dai & Li, JMLR 2023) | **SỞ HỮU định lý "oracle level-set / purity-prefix"** — thứ ta định dùng làm Theorem 1. Dice = F1; purity `p(v)=P(u\|I=v)` là posterior đã calibrate. ⇒ **ĐƯỢC DÙNG, PHẢI CITE, KHÔNG ĐƯỢC CLAIM TOÁN HỌC.** Ship nó như *"Theorem 1 (ours)"* = lặp lại **đúng tội fabricated-novelty mà bài này sinh ra để trừng phạt**. |
| **Merzban & Elbayoumi**, ESWA 116:299–309 (2019), `10.1016/j.eswa.2018.09.008` — exact DP thắng metaheuristic | Họ làm **Otsu**, **ảnh tự nhiên, không ground truth** ⇒ không thể phát hiện suy biến metric. **KHÔNG claim DP là đóng góp của mình.** Code public: `github.com/bayoumim/Ostu-Multilevel-Segmentation`. |
| Luessi et al., J. Electronic Imaging 18(1):013004 (2009), `10.1117/1.3073891` | Như trên |
| 🔴 **Mousavirad et al.**, *How effective are current population-based metaheuristic algorithms for variance-based multi-level image thresholding?*, **Knowledge-Based Systems 272:110587 (2023)**, `10.1016/j.knosys.2023.110587` | **Near-rival NGUY HIỂM NHẤT cho P2** — tiêu đề của họ *chính là* câu hỏi của P2. Họ làm Otsu/variance, ảnh tự nhiên, không GT. ⚠️ **Kết luận của họ MÂU THUẪN với P2**: *"most recent algorithms fail to provide satisfactory thresholding performance"* ⇒ họ thấy các thuật toán **KHÁC NHAU rõ rệt**, ta dự đoán **tương đương phổ quát**. **PHẢI đọc toàn văn và hoà giải mâu thuẫn này trước khi viết** (hiện `[PARTIAL — paywall]`). |
| 🔴 **François & Tinarrage**, *Train-Free Segmentation in MRI with Cubical Persistent Homology*, **nay đã peer-reviewed: J. Mathematical Imaging & Vision 68, 20 (2026)**, `10.1007/s10851-026-01300-1` (arXiv:2401.01160) | **Chạm P4 NẶNG HƠN ta tưởng.** Toàn văn chứa nguyên văn: *"the oracle best Dice score reaches a mean of **0.83±0.18**. These results provide **an upper bound on the achievable performance within the considered thresholding framework**."* ⇒ **khái niệm + dataset (BraTS FLAIR) + CON SỐ + cả so sánh DL đều đã in**. **CẤM TUYỆT ĐỐI mọi câu "we establish the ceiling"**. ⚠️ Con số 0,83 này còn nói: **trên WT/FLAIR trần KHÔNG THẤP** — nó nằm trong vùng đồng thuận liên-quan-sát-viên (~0,85–0,87, Menze 2015). ⇒ **P4 có thể THẤT BẠI thật.** |
| 🔴 **Hegazy & Gabr**, *A Dynamic Programming Framework for Discovering Count and Values of Multilevel Image Thresholding*, **arXiv:2605.27287 (26/05/2026)** | **CÙNG NHÓM với bài dưới, ra 2 bài/tháng trên đúng seam này.** DP cho multilevel thresholding + **tự chọn số ngưỡng k** + **có ảnh y tế**. Đây là nhóm đang chiếm chính xác chỗ ta đứng ⇒ **phải đăng preprint sớm để cắm cọc ưu tiên**. |
| 🔴 **Fardo et al.**, *A Formal Evaluation of PSNR as Quality Measurement Parameter for Image Segmentation Algorithms*, **arXiv:1605.07116 (2016)** | **Chạm P3 từ 2016.** Họ **đã đánh cả trục k** (*"threshold level selection as well as the number of thresholds in the case of multi-level segmentation"*) ⇒ *"PSNR sai cho segmentation"* **không phải phát hiện của ta**. |
| **Al-Najdawi et al.**, *Comprehensive evaluation of optimization algorithms for medical image segmentation*, **Scientific Reports 15:37190 (2025)**, `10.1038/s41598-025-14261-z` | **HIỆN VẬT VÀNG cho Bảng I** (và là near-rival về setup): benchmark **18 optimizer** + Otsu trên ảnh **y tế**, báo cáo **Dice 0,85–0,88** — trong khi phần limitations **tự thú "the absence of ground truth annotations"**. Đây là bằng chứng khả kiểm mạnh nhất cho luận điểm của bài. **PHẢI đọc toàn văn trước khi trích.** |
| 🔴 **Hegazy & Gabr**, *Image Thresholding: Understanding Bias of Evaluation Metrics towards Specific Evaluation Functions*, **arXiv:2605.27132 (05/2026)** | **Chạm P3.** Họ đã chỉ ra PSNR/SSIM **thiên vị Otsu hơn Kapur** ⇒ *"reported performance gains … may reflect this underlying bias rather than genuine improvements"*. Họ **không** có GT/Dice/trục k/y tế. ⇒ P3 phải viết là **mở rộng sang miền có ground truth lâm sàng**, không phải phát hiện độc lập. |
| *A novel quantum grasshopper optimization algorithm **for feature selection***, IJAR 127:33–53 (2020), `10.1016/j.ijar.2020.08.010` | "QGOA" đã tồn tại (bài **feature selection**, không phải thresholding) ⇒ **không được claim QIGOA là mới**. ⚠️ DOI cũ `…08.011` trong repo là **SAI** — nó resolve ra bài khác (Yarullin & Obiedkov). Đã sửa 13/07/2026. |
| **Harandi, Van Messem, De Neve, Vankerschaver**, *Grasshopper Optimization Algorithm (GOA): A Novel Algorithm or A Variant of PSO?*, **ANTS 2024**, LNCS pp. 84–97, `10.1007/978-3-031-70932-6_7` | ✅ **Đã verify** (bỏ nhãn "cần verify"). GOA = biến thể PSO. Cặp với Platel 2009 (QIEA = EDA) ⇒ **QIGOA = "EDA-flavoured PSO"**, hai lớp metaphor bị bóc bằng hai bài peer-reviewed. |
| Dey/Bhattacharyya/Maulik — **KBS (2014)** `10.1016/j.knosys.2014.04.006` + ASC 46 (2016) `10.1016/j.asoc.2015.09.042`, ASC 56 (2017) `10.1016/j.asoc.2016.04.024` + sách **Wiley** 2019 | QI-metaheuristic + thresholding đã xong từ **2014** (sớm hơn mốc 2016 ghi trước đây). |
| AI Review **59(3) (2026)**, `10.1007/s10462-025-11438-w` — quantum + Rényi entropy | **KHÔNG phải near-scoop** (dataset Alzheimer + breast cancer, **không phải BraTS**; thuật toán QHEEFO, không phải GOA). Dùng ở Introduction làm **bằng chứng dòng văn liệu vẫn sống tới 2026**. |

**SÁU lằn ranh đỏ của hướng này** *(3 lằn ranh mới thêm 14/07/2026 sau audit — chúng là ba cách chết nhanh nhất)*:
1. **Không tái dùng bất kỳ con số nào từ commit `c4fe108`** (bug NFE 13,4%, GOA hit-rate 0%, SSIM/FSIM tự chế, pseudo-replication). Nó là bằng chứng chẩn đoán, không phải nguồn số liệu.
2. **Không đụng vào Bảng I trong `Huong-tiep-can-paper-Long.pdf`** — đó là **số bịa**. Vi phạm IRON RULE 1 nếu tái sinh.
3. **Không claim "quantum advantage"**. QIEA = một EDA (Platel et al., IEEE TEVC 2009, `10.1109/TEVC.2008.2003010`). Định vị đúng: *"an EDA-style probabilistic update rule"*.
4. 🆕 **KHÔNG viết "văn liệu decode bằng lớp sáng nhất [refs]".** Quy tắc đó là **code cũ của chính ta**, không tìm thấy trong văn liệu. Đa số bài **không tạo binary mask và không dùng GT** (Sci Rep 2025 GAAOA-Lévy; PLOS ONE 2024 CIWP-PSO **tự viết** *"does not compare results against ground truth segmentation masks"*; BSPC 113/2026 CPO; và **chính bản phác của thầy**). Thiểu số có Dice thì decode bằng **region growing / k-means + morphology / morphological reconstruction**. Quy kết sai = **xuyên tạc công trình được cite = vi phạm IRON RULE 2**, nặng hơn cả rủi ro bị reject. → Viết thành **THẾ LƯỠNG NAN** (prereg §6/A1).
5. 🆕 **KHÔNG claim "we establish the ceiling"**, và **KHÔNG claim định lý level-set là của mình** (François & Tinarrage JMIV 2026 đã in trần trên BraTS; Lipton et al. 2014 sở hữu định lý). Ta claim **ứng dụng + phân rã**, không claim **toán học**.
6. 🆕 **KHÔNG để leakage trong đóng góp dương.** "Ngưỡng 1-tham-số hiệu chỉnh trên 10 ảnh train" rồi test trên cả 150 = **train-on-test, nằm ngay trong đóng góp dương của một bài tố cáo người khác so sánh không lành mạnh**. Đây là lỗi **DUY NHẤT có thể bị reject vì LIÊM CHÍNH**, không phải vì novelty. Mọi thành phần có học (U-Net · ngưỡng 1-tham-số · **việc chọn k**) chỉ được đánh giá **out-of-fold**, split ở **cấp bệnh nhân** (prereg §6/A3).

📄 Bản trình bày với thầy: [docs/trinh-bay-voi-thay.md](docs/trinh-bay-voi-thay.md) — **chưa code cho tới khi thầy gật.**
📋 Kết quả audit 24 agent (13/07/2026) + 15 mục must-fix: xem [docs/preregistration.md](docs/preregistration.md) §6 (append-only).

> 💡 **Luận điểm phải nói với thầy — KHÔNG phải "đề này không đăng được"** (thầy mở BSPC vol. 113 (2026) ra là mất phòng họp: tạp chí đích **vẫn đang in** thresholding trên ảnh y tế với PSNR/SSIM/FSIM và **không có Dice**). **Mà là:** *"Đề này **ĐĂNG ĐƯỢC** — và đó chính là vấn đề. Nó chỉ đăng được nếu ta **không bao giờ mở bộ mask mà BraTS đã tặng sẵn**. Mở Dice ra là kết quả đảo chiều."*

---

## 2. LIÊM CHÍNH HỌC THUẬT — LUẬT SẮT (không thương lượng)

> Đây là phần quan trọng nhất và **đúng cho mọi chủ đề**. Vi phạm bất kỳ mục nào = phá hỏng sự nghiệp của tác giả. Khi nghi ngờ, DỪNG và hỏi.

- **IRON RULE 1 — KHÔNG bịa số.** Không bao giờ tự chế bất kỳ con số thực nghiệm, giá trị trong bảng, p-value, metric (AUROC/F1/accuracy…), khoảng tin cậy, kích thước dataset. Mọi con số định lượng phải **truy được về output của một script chạy lại được**.
- **IRON RULE 2 — KHÔNG bịa trích dẫn.** Không tạo tác giả/năm/DOI/tên tạp chí không có thật. Mọi reference phải **verify được** (Crossref/DOI/arXiv). Không verify được → đánh dấu `[UNVERIFIED]`, không đưa vào reference list chính thức.
- **IRON RULE 3 — Kết quả là PLACEHOLDER cho tới khi tái lập từ pipeline sạch.** Bất kỳ bảng/hình/số nào chưa chạy ra từ script đều mang nhãn `[PLACEHOLDER]` / `[TODO]` / `[UNVERIFIED]`. **Không bao giờ âm thầm "thăng cấp" placeholder thành kết quả thật.**
- **IRON RULE 4 — Sau knowledge-cutoff (Jan 2026) → BẮT BUỘC web-verify.** Trước khi khẳng định một paper 2025–2026 tồn tại/nói gì, hoặc trước khi tuyên bố "chưa ai làm" (novelty/collision-check), phải tra web (WebSearch/WebFetch). Model KHÔNG được nhớ từ training về các paper sau cutoff.
- **IRON RULE 5 — Không overclaim.** Không viết "outperforms SOTA" / "vượt trội" nếu chưa có kiểm định thống kê (mean±std + Wilcoxon/Friedman+Holm). Không nói "first/đầu tiên" khi chưa collision-check web.
- **IRON RULE 6 — Trung thực về bản chất & giới hạn của method.** Gọi đúng tên và đúng phạm vi của kỹ thuật; nêu caveat; **không cường điệu một "advantage" chưa được chứng minh**. Nếu method chỉ là *inspired-by* (VD quantum-inspired chạy trên phần cứng cổ điển) → nói rõ *không có advantage lý thuyết đã được chứng minh*, kèm cite phản chứng. Không dùng bằng chứng sai họ phương pháp (VD: kết quả trên phần cứng thật để biện minh cho biến thể cổ điển) — đó là *category error*.

**Khi tạo nội dung định lượng chưa chạy:** viết công thức/khung bảng với ô để trống + nhãn `[PLACEHOLDER]`, kèm *đúng script* sẽ điền nó. Không điền số minh họa trông-như-thật.

---

## 3. Kỷ luật thực nghiệm (chưng cất từ [docs/lam-va-viet-paper-chuan-IEEE.md](docs/lam-va-viet-paper-chuan-IEEE.md))

Đọc playbook đó khi thiết kế thí nghiệm hoặc dựng formulation. Nguyên tắc cốt lõi (topic-agnostic):

- **Anti-toy.** Bài toán, dataset, threat-model phải ở đúng thang thực tế — không dùng setup đồ-chơi để làm đẹp số.
- **Đa-seed, LUÔN LUÔN.** Mọi kết quả báo cáo **mean ± std qua ≥5 seed/run độc lập**, không bao giờ một-lần-chạy.
- **Ablation cùng tham số.** Khi bật/tắt một thành phần, giữ *mọi* hyperparameter khác y hệt — lợi thế biểu kiến thường đến từ tuning lệch, không phải thành phần mới.
- **Kiểm soát confound.** Trước khi quy công cho method, loại trừ: rò rỉ dữ liệu (leakage), chênh tiền xử lý, khác thang nhiễu, mất cân bằng nhóm.
- **Metric tổng hợp chống cherry-pick.** Báo cáo bộ metric đầy đủ phù hợp bài toán (không chỉ một metric đẹp) — VD với bài lâm sàng: discrimination + calibration + net-benefit + fairness.
- **Audit shortcut + held-out.** Kiểm tra model có ăn shortcut / spurious correlation không. Luôn hướng tới **external validation** trên dataset/điều kiện khác.
- **Thống kê chuẩn:** so sánh cặp **Wilcoxon signed-rank**; omnibus **Friedman** + post-hoc **Holm**. Nêu effect size, không chỉ p-value.
- **Ba cờ đỏ** (dừng lại nếu thấy): (a) lợi thế biến mất khi cùng-tham-số-hóa; (b) chỉ đẹp trên một seed/split; (c) không tái lập được từ script sạch.
- **Hội tụ, không trôi dạt.** Qua từng lớp nghiêm cẩn, kết luận phải hội tụ về sự thật — **nếu tuyên bố chính sụp thì REFRAME trung thực**, đừng cố cứu claim đã chết.

---

## 4. Chuẩn viết journal / IEEE Transaction

Nguồn chuẩn: [docs/lam-va-viet-paper-chuan-IEEE.md](docs/lam-va-viet-paper-chuan-IEEE.md). Điểm chốt:

- **Transaction khác conference:** đòi formulation cứng, evaluation như *phép thử bác bỏ*, và định vị related work sắc.
- **Formulation chặt:** trình bài toán bằng ký hiệu rõ, mục tiêu/ràng buộc rõ, threat-model tường minh.
- **Evaluation là phép thử bác bỏ:** thiết kế thí nghiệm để *có thể làm sai* claim của mình, không phải để minh họa nó.
- **Related work = định vị, KHÔNG phải liệt kê.** Dẫn đầu bằng đóng góp tích hợp; chủ động **nêu & phân biệt các near-rival** (đã web-verify, §2 IRON RULE 4) thay vì chỉ trích dẫn cho có.
- **Figure/table chuẩn Transaction:** tự-giải-thích, caption đầy đủ, đơn vị & n & seed rõ.
- **Rebuttal per-comment:** trả lời TỪNG comment reviewer, hai bản (thư phản hồi + bản diff) từ một nguồn.
- **Preregister claim trước khi chạy** để tránh HARKing (§9).

---

## 5. KỶ LUẬT TRIỂN KHAI (implementation + reproducibility + provenance)

> Mục này biến **IRON RULE 1 & 3** (§2) thành quy trình cụ thể: *mọi con số trong paper phải sinh ra từ một script chạy lại được, và truy ngược được về đúng commit + seed + config.* Repo hiện **chưa có code** → đặt các quy ước này ngay từ file đầu tiên, không phụ thuộc chủ đề.

### 5.1 Cấu trúc repo chuẩn (lập từ ngày đầu)

```
configs/     # 1 file YAML/JSON cho MỖI thí nghiệm: seed(s), hyperparams, đường dẫn dataset, metric
src/         # module tái dùng: features/  models/  eval/  (thêm module theo phương pháp khi chốt)
scripts/     # entrypoint chạy được trên Kaggle — mỗi script tái lập ĐÚNG 1 bảng/hình
results/     # OUTPUT do script sinh: metrics.csv/json, figures/, run-manifest.json — KHÔNG sửa tay
paper/       # bản thảo (LaTeX/md); bảng & hình PULL từ results/, không gõ số tay
docs/        # memo hướng tiếp cận + preregistration.md + RESULTS.md
```

- **Config-driven, KHÔNG magic number trong code.** Đổi thí nghiệm = đổi config, không sửa code cứng.
- **Split ở mức subject/nhóm, KHÔNG mức mẫu lẻ** (chống leakage) — lưu split ra đĩa và version nó.

### 5.2 Reproducibility contract (bắt buộc cho MỌI run)

- **Set MỌI seed:** `random`, `numpy`, `torch` (+ `cudnn.deterministic=True`), truyền seed qua config; chạy **≥5 seed độc lập** → báo mean ± std (§3).
- **Pin môi trường:** `requirements.txt`/freeze; ghi phiên bản thư viện vào manifest.
- **`run-manifest.json` cho MỖI run:** `{git_commit, config_hash, seed(s), dataset_version, lib_versions, timestamp, output_paths}`. Không có manifest = run *không tồn tại* với paper.
- **Log có cấu trúc:** ghi metric ra CSV/JSON (không chỉ `print`); artifact lưu lại được.

### 5.3 Provenance contract (số → script → commit) — vận hành IRON RULE 1 & 3

- Giữ `docs/RESULTS.md` map **mỗi bảng/hình/số** trong paper về nguồn sinh, dạng:
  `Table 2 ← results/<exp>/metrics.csv ← scripts/run_<exp>.py --config configs/<exp>.yaml @commit <hash>, seeds {0..4}`
- Số chưa có dòng provenance = **`[PLACEHOLDER]`**, không được đưa vào bản thảo như kết quả thật.
- Bảng/hình trong `paper/` **generate từ `results/`** (qua script build), không copy-paste số bằng tay → tránh lệch số âm thầm.

### 5.4 Dữ liệu & Kaggle

- Ưu tiên **dataset công khai**; khi label là proxy (VD điểm sàng lọc ≠ chẩn đoán lâm sàng) → **luôn nêu caveat construct-validity**.
- Python, ưu tiên CPU-friendly; đọc từ `/kaggle/input/` (read-only), ghi ra `/kaggle/working/`.
- **Luôn có synthetic fallback** để pipeline chạy được cả khi dataset chưa mount — nhưng đó chỉ là smoke-test cấu trúc; **số synthetic KHÔNG bao giờ là kết quả**, luôn gắn `[PLACEHOLDER]`.
- Tôn trọng giới hạn thời gian/quota Kaggle: chia stage, cache feature đã trích, thiết kế resume-được.

---

## 6. Khi nào dùng skill nào

| Nhu cầu | Skill |
|---|---|
| Tìm/verify research gap, collision-check near-scoop, lit-review, fact-check citation | **deep-research** |
| Viết/sửa section theo chuẩn journal, abstract song ngữ, format IEEE/DOCX, citation-check, rebuttal | **academic-paper** |
| Đóng vai 5 reviewer chấm bài trước khi nộp, re-review sau sửa | **academic-paper-reviewer** |
| Chạy trọn quy trình research → viết → integrity-check → review → revise (có cổng chất lượng) | **academic-pipeline** |
| Vẽ sơ đồ pipeline/architecture/flow | **drawio-skill** |

Ví dụ ánh xạ ý định → skill nằm ở [pro-p.txt](pro-p.txt).

---

## 7. An toàn thao tác file & repo

- **Không xóa/ghi đè** file tài liệu (docx/pdf/md approach) mà không đọc trước và xác nhận với tác giả — nhất là file *advisor-facing* trong `docs/`.
- **File-path trong memo cũ dễ stale** — verify tồn tại trước khi khẳng định. Nguồn thật hiện tại: `git ls-tree -r HEAD`.
- Chỉ commit/push khi tác giả yêu cầu. Nếu đang ở nhánh `main`, tạo nhánh trước.
- Trước khi xóa/ghi đè: nếu nội dung file mâu thuẫn với cách nó được mô tả, **báo lại thay vì cứ làm**.

---

## 8. Giao thức mỗi phiên & Definition of Done

**Đầu mỗi phiên (Claude tự làm, không cần hỏi):**
1. Đọc `CLAUDE.md` + `MEMORY.md`; chạy `git status` + `git log --oneline -5` để biết đang ở đâu.
2. **Kiểm tra chủ đề đã chốt chưa** (§1). Nếu chưa → không giả định đề tài; đề xuất/hỏi.
3. Xác định bước hiện tại: chốt-chủ-đề → research → preregister → code → run → viết → review → revise.
4. Memo/nhắc cũ nêu file-path → **verify tồn tại** trước khi dựa vào (§7).

**Definition of Done — MỘT thí nghiệm được coi là "paper-ready" khi:**
- [ ] Config-driven + **≥5 seed** + `run-manifest.json` đã ghi (§5.2).
- [ ] Split mức subject/nhóm, **audit leakage pass** (no overlap, no preprocessing leak).
- [ ] **Bộ metric đầy đủ** phù hợp bài toán — không lọc metric đẹp.
- [ ] **Kiểm định thống kê** (Wilcoxon / Friedman+Holm) + effect size — không chỉ p-value.
- [ ] Đã thử **external validation** (dataset/điều kiện khác), hoặc ghi rõ lý do hoãn + fallback.
- [ ] **Dòng provenance** đã thêm vào `RESULTS.md`; số trong `results/` khớp số trong `paper/` (§5.3).

**Definition of Done — MỘT claim trong paper:**
- [ ] Đã **preregister** trước khi chạy (§9).
- [ ] Mọi số **truy được về script** (không còn `[PLACEHOLDER]` sót trong bản nộp).
- [ ] Không overclaim; caveat về **giới hạn method** (§2 IRON RULE 6) và **proxy-label** (nếu có) đều có mặt.
- [ ] Các near-rival được **phân biệt**, không chỉ liệt kê (§4).

---

## 9. Preregistration & nhật ký thí nghiệm

- **`docs/preregistration.md`** — viết **TRƯỚC** khi chạy, cho mỗi claim: *giả thuyết · metric quyết định · ngưỡng thành công · phân tích dùng · fallback nếu thất bại*. Đây là hàng rào chống HARKing (§4). **Nếu claim chính thua → ship baseline đơn giản hơn và báo cáo kết quả âm trung thực.**
- **Nhật ký thí nghiệm (append-only)** trong `docs/RESULTS.md`: mỗi run một dòng — ngày (tuyệt đối), commit, config, seed, kết quả tóm tắt, kết luận. **Không xóa run xấu; run âm là dữ liệu.**
- **Ba cờ đỏ → DỪNG** (nhắc lại §3): (a) lợi thế biến mất khi cùng-tham-số-hóa; (b) chỉ đẹp trên một seed/split; (c) không tái lập từ script sạch. Gặp cờ đỏ → **REFRAME trung thực**, đừng cứu claim đã chết.

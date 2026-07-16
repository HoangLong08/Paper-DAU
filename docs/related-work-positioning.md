# Related Work — Positioning (CỔNG TUẦN 0)

**Ngày:** 16/07/2026 · **Trạng thái:** hoàn thành CỔNG TUẦN 0 (preregistration §6/A10, dòng cuối).
**Mục đích:** đọc/định vị 6 (+1) bài near-rival **trước khi chạy E2**. Với mỗi bài: (a) tóm tắt method + dataset + có/không GT-Dice; (b) một đoạn **positioning** viết sẵn (giọng học thuật trung tính, tiếng Anh — drop-in cho §2 Related Work); (c) trạng thái verify.

> **Kỷ luật (CLAUDE.md §2):** mọi DOI/arXiv ID dưới đây được đối chiếu **trong phiên này** qua Crossref API và arXiv. Nhãn:
> - **[VERIFIED]** = metadata (và/hoặc trích dẫn nguyên văn) đối chiếu được từ nguồn sơ cấp **trong phiên 16/07/2026**.
> - **[PARTIAL]** = metadata VERIFIED, nhưng một phần nội dung (trích dẫn nội bảng, câu kết luận) nằm sau paywall phiên này ⇒ dựa vào bản đọc toàn văn đã ghi trong `preregistration.md` §6 (14/07/2026). **Phải mở lại toàn văn trước khi trích nguyên văn vào bản thảo.**
> - **[UNVERIFIED]** = chưa xác nhận (không có mục nào rơi vào loại này).

---

## Bảng trạng thái verify (tóm tắt)

| # | Bài | DOI / ID | Metadata | Nội dung then chốt |
|---|---|---|---|---|
| 1 | Mousavirad et al., KBS 272:110587 (2023) | `10.1016/j.knosys.2023.110587` | **[VERIFIED]** Crossref | Kết luận verbatim **[PARTIAL]** (paywall phiên này) |
| 2 | François & Tinarrage, JMIV 68,20 (2026) | `10.1007/s10851-026-01300-1` · arXiv:2401.01160 | **[VERIFIED]** Crossref | Trần 0.83±0.18 **[VERIFIED]** — đọc nguyên văn từ PDF |
| 3 | Hegazy & Gabr, arXiv:2605.27132 (2026) | arXiv:2605.27132 | **[VERIFIED]** arXiv | Nội dung **[VERIFIED]** |
| 4 | Hegazy & Gabr, arXiv:2605.27287 (2026) | arXiv:2605.27287 | **[VERIFIED]** arXiv | Nội dung **[VERIFIED]** |
| 5 | Menotti, Najman & de A. Araújo, CIARP 2015, LNCS 350–357 | `10.1007/978-3-319-25751-8_42` | **[VERIFIED]** Crossref | Runtime "<160 ms" / O((K−1)L²) **[PARTIAL]** |
| 6 | Hammouche, Diaf & Siarry, EAAI 23(5):676–688 (2010) | `10.1016/j.engappai.2009.09.011` | **[VERIFIED]** Crossref | Bảng 8–10 / ngưỡng 1e−9 **[PARTIAL]** |
| 7 | Al-Najdawi et al., Sci Rep 15:37190 (2025) | `10.1038/s41598-025-14261-z` | **[VERIFIED]** Crossref | Dice 0.85–0.88 / "absence of GT" **[PARTIAL]** (nature gated) |

---

## 1. Mousavirad, Schaefer, Zhou & Helali Moghadam (2023) — KBS

- **Verify.** [VERIFIED] Crossref: *"How effective are current population-based metaheuristic algorithms for variance-based multi-level image thresholding?"*, **Knowledge-Based Systems 272:110587 (2023)**, `10.1016/j.knosys.2023.110587`. Tác giả: Seyed Jalaleddin Mousavirad, Gerald Schaefer, Huiyu Zhou, Mahshid Helali Moghadam. Abstract/kết luận verbatim: **[PARTIAL]** — figshare/ScienceDirect trả 403 trong phiên này; nội dung dưới đây dựa trên bản đọc đã ghi ở `preregistration.md` §6/A4b.
- **Method + dataset.** Benchmark một loạt population-based metaheuristic cho multilevel thresholding **variance-based (Otsu)**, hàm mục tiêu = between-class variance. **Ảnh tự nhiên** (benchmark ảnh xám tiêu chuẩn), **KHÔNG có ground truth segmentation, KHÔNG dùng Dice.** Metric đánh giá là **giá trị fitness Otsu đạt được** (so với nhau và/hoặc so với tối ưu), không phải chất lượng phân vùng lâm sàng.
- **Kết luận của họ (near-rival NGUY HIỂM NHẤT cho P2).** Tiêu đề của họ *chính là* câu hỏi của P2; và họ báo cáo rằng các thuật toán **KHÁC NHAU rõ rệt** — "most recent algorithms fail to provide satisfactory thresholding performance" [PARTIAL — cần mở lại toàn văn để trích]. Đây **mâu thuẫn bề mặt** với P2 (ta dự đoán tương đương phổ quát). Xem đoạn HOÀ GIẢI #1 bên dưới.

**Positioning (drop-in, EN):**
> Mousavirad et al. [KBS 2023] pose precisely our optimization question — whether population-based metaheuristics are effective for multilevel thresholding — but in a setting that structurally cannot detect the phenomenon we study. Their objective is Otsu between-class variance on natural benchmark images without segmentation ground truth, so performance is measured *in the objective's own units*. They report that recent algorithms differ substantially, some failing to reach the optimum. Our contribution is orthogonal on two axes: (i) we evaluate against an *exact* global optimum (dynamic programming, per Menotti et al. [CIARP 2015]) rather than against each other, and (ii) we project every solution onto a clinical binary mask with ground truth (BraTS whole-tumor Dice). The apparent tension between their "algorithms differ" and our "clinically equivalent" is resolved by the level at which difference is measured: a fitness gap that is real in variance units need not survive the mapping to a Dice-scored mask (see our decoupling test, preregistration P2c). We therefore cite them as the state-of-the-art *variance-space* benchmark and position our work as its *clinical-space* complement.

---

## 2. François & Tinarrage (2026) — JMIV ★ CHẠM P4 NẶNG

- **Verify.** [VERIFIED] Crossref: *"Train-Free Segmentation in MRI with Cubical Persistent Homology"*, **Journal of Mathematical Imaging and Vision 68, 20 (2026)**, `10.1007/s10851-026-01300-1` (arXiv:2401.01160). Trần Dice **verbatim [VERIFIED]** — đọc trực tiếp từ toàn văn PDF trong phiên này.
- **Method + dataset.** Phân vùng MRI **train-free** bằng Topological Data Analysis (cubical persistent homology): (1) automatic thresholding để lấy toàn khối, (2) phát hiện subset có topology biết trước, (3) suy ra các thành phần. Đánh giá trên **glioblastoma (BraTS, FLAIR)** và fetal cortical plate. **CÓ dùng ground truth Dice.**
- **Con số then chốt (nguyên văn, đã đọc từ PDF).** Trên FLAIR:
  > *"For the FLAIR segmentation obtained with our method (including refinements), the Dice score achieves a mean of 0.76 ± 0.27 (std) on the entire dataset. In contrast, **the oracle best Dice score reaches a mean of 0.83±0.18. These results provide an upper bound on the achievable performance within the considered thresholding framework.**"*
  
  Họ định nghĩa oracle bằng cách: với mỗi superlevel set, lấy thành phần liên thông lớn nhất và tính Dice, chọn ngưỡng tốt nhất (oracle threshold). Họ cũng dùng U-Net làm cận trên tham chiếu cho lớp phương pháp này.
- **Vì sao CHẠM P4.** Khái niệm ("upper bound within the thresholding framework") + dataset (BraTS FLAIR) + **con số (0.83±0.18)** + so sánh DL — **tất cả đã in**. ⇒ **CẤM TUYỆT ĐỐI mọi câu "we establish the ceiling".** Xem đoạn HOÀ GIẢI #2 bên dưới. Lưu ý: 0.83 nằm trong vùng đồng thuận liên-quan-sát-viên WT (~0.85–0.87, Menze et al. 2015) ⇒ trên WT/FLAIR **trần KHÔNG thấp** ⇒ P4 nhánh "U-Net vượt trần" có thể THẤT BẠI thật (đã có fallback ở prereg §6/A2).

**Positioning (drop-in, EN):**
> The claim that intensity thresholding has a performance ceiling on brain MRI is **not ours to make**: François and Tinarrage [JMIV 2026] already report, on BraTS FLAIR, that "the oracle best Dice score reaches a mean of 0.83 ± 0.18," describing this explicitly as "an upper bound on the achievable performance within the considered thresholding framework." We take this as an established result, cite it as such, and make **no** claim to establishing a ceiling. Our contribution is a *decomposition* of that ceiling rather than its assertion: we separate the gap between an oracle single-interval mask, an oracle arbitrary-graylevel-set mask (the tightest bound for any intensity-only decoder, following the F1-threshold result of Lipton et al. [2014]), and a 2D U-Net trained on the identical single-slice FLAIR input. This isolates how much of thresholding's shortfall is "information absent from intensity" versus "information absent from the pixels." Where François and Tinarrage show *that* thresholding saturates, we quantify *why*, and against a like-for-like learned baseline. We further add a case where the representational limit is provably real — enhancing tumor on T1ce, a bright rim around a dark core that no single contiguous intensity band can represent — which their WT/FLAIR setting does not exercise.

---

## 3. Hegazy & Gabr (2026) — arXiv:2605.27132 (metric bias) — CHẠM P3

- **Verify.** [VERIFIED] arXiv:2605.27132: *"Image Thresholding: Understanding Bias of Evaluation Metrics towards Specific Evaluation Functions"*, Eslam Hegazy & Mohamed Gabr. Nội dung đọc được trong phiên.
- **Method + dataset.** Phân tích tương quan giữa **hàm mục tiêu thresholding** (Otsu between-class variance vs Kapur entropy) và **metric chất lượng** (SSIM, PSNR) trên **toàn bộ ngưỡng khả dĩ**, dataset **BSDS500 (ảnh tự nhiên, KHÔNG y tế, KHÔNG GT/Dice).**
- **Kết luận của họ.** "Otsu outperforms Kapur in correlation with PSNR for all images and with SSIM for over 91%" ⇒ PSNR/SSIM **thiên vị Otsu hơn Kapur** ⇒ chênh lệch hiệu năng báo cáo "may reflect this underlying bias rather than genuine improvements". Kêu gọi "more neutral evaluation frameworks". **Họ KHÔNG có** GT/Dice/trục-k/ảnh-y-tế.

**Positioning (drop-in, EN):**
> Hegazy and Gabr [arXiv:2605.27132, 2026] demonstrate, on BSDS500 natural images, that PSNR and SSIM are systematically more correlated with Otsu's objective than with Kapur's, cautioning that reported gains "may reflect this underlying bias rather than genuine improvements." Our P3 result is a **domain extension**, not an independent discovery: we move the argument from surrogate metrics on natural images to *clinical* ground truth (Dice, HD95) on brain MRI, and add the threshold-count axis *k*, showing that the metrics that improve monotonically with *k* (fitness, PSNR, SSIM) anti-correlate with the metric that matters clinically. We credit them for establishing metric bias in the natural-image regime and position ours as the ground-truth-anchored counterpart.

---

## 4. Hegazy & Gabr (2026) — arXiv:2605.27287 (DP framework) — CÙNG NHÓM, ĐANG CHIẾM SEAM

- **Verify.** [VERIFIED] arXiv:2605.27287: *"A Dynamic Programming Framework for Discovering Count and Values of Multilevel Image Thresholding"*, Eslam Hegazy & Mohamed Gabr.
- **Method + dataset.** DP + biến thể **Minimum Error Thresholding (MET-DP)** để **tự động chọn số ngưỡng k** và giá trị ngưỡng. Test trên **"natural, satellite and medical test images"** (CÓ ảnh y tế). Code public (w3id.org/met-dp). **KHÔNG dùng Dice/GT**; đánh giá bằng SSIM/PSNR — họ tự khai các phương pháp truyền thống cho SSIM/PSNR cao hơn, ưu thế của họ là **thời gian** khi k lớn.
- **Vì sao quan trọng.** Đây là **cùng nhóm** đang ra ~2 bài/tháng trên đúng seam (DP cho multilevel thresholding + tự chọn k + có ảnh y tế). ⇒ **rủi ro ưu tiên** — củng cố mệnh lệnh CLAUDE.md: **đăng arXiv preprint ngay ngày nộp lần đầu** để cắm cọc.

**Positioning (drop-in, EN):**
> A dynamic-programming treatment of multilevel thresholding that also *selects* the number of thresholds — including on medical images — has recently been given by Hegazy and Gabr [arXiv:2605.27287, 2026]. We do not claim novelty for either the exact DP solver (established by Menotti et al. [CIARP 2015]) or for data-driven selection of *k*. Our use of DP is purely as a *reference optimum* against which metaheuristic solutions are measured, and our treatment of *k* differs in kind: rather than proposing a selection rule, we show that the choice of *k* under existing surrogate criteria trades clinical Dice against surrogate fitness, quantifying the per-patient Dice cost of selecting *k* by PSNR. Their work optimizes the thresholding pipeline; ours audits what that pipeline can and cannot deliver against clinical ground truth.

---

## 5. Menotti, Najman & de A. Araújo (2015) — CIARP/LNCS ★ SCOOP "đóng góp dương" cũ

- **Verify.** [VERIFIED] Crossref: *"Efficient Polynomial Implementation of Several Multithresholding Methods for Gray-Level Image Segmentation"*, David Menotti, Laurent Najman, Arnaldo de A. Araújo. **LNCS (Progress in Pattern Recognition, CIARP 2015), pp. 350–357**, `10.1007/978-3-319-25751-8_42`. Runtime "<160 ms" / độ phức tạp O((K−1)L²) verbatim: **[PARTIAL]** — metadata VERIFIED, chi tiết runtime từ bản đọc trước (prereg §6). Tiêu đề đã tự nói lên "efficient polynomial implementation … several multithresholding methods".
- **Method + dataset.** Cài đặt **đa thức (DP) chính xác** cho nhiều tiêu chí multithresholding — gồm **Otsu, KAPUR, Kittler–Illingworth** — độ phức tạp O((K−1)L²), chạy "<160 ms bất kể số lớp". Ảnh xám tổng quát.
- **Vì sao là SCOOP.** Đúng thuật toán + đúng hàm mục tiêu (Kapur) + đúng độ phức tạp + đúng bậc thời gian, in **11 năm trước**. ⇒ **"Bộ giải chính xác mili-giây" KHÔNG được claim là đóng góp** của ta. Phải cite ở **Abstract**. Một bài có thesis *"các anh không cite lời giải chính xác"* mà không cite chính bài này = tự thiêu.

**Positioning (drop-in, EN):**
> Exact, polynomial-time computation of optimal multilevel thresholds — for Otsu, Kapur, and Kittler–Illingworth criteria alike — was given by Menotti et al. [CIARP 2015], with an O((K−1)L²) dynamic program running in well under a second regardless of the number of classes. We claim **no novelty** for the exact solver and cite this work prominently in the abstract; it is the reference optimum against which we benchmark metaheuristic solutions. The point of our paper is precisely that this decade-old exact result renders the metaheuristic optimization contest moot on its own terms, and — one step further — that even the exact optimum does not translate into a better clinical mask.

---

## 6. Hammouche, Diaf & Siarry (2010) — EAAI ★ SCOOP P2

- **Verify.** [VERIFIED] Crossref: *"A comparative study of various meta-heuristic techniques applied to the multilevel thresholding problem"*, Kamal Hammouche, Moussa Diaf, Patrick Siarry, **Engineering Applications of Artificial Intelligence 23(5):676–688 (2010)**, `10.1016/j.engappai.2009.09.011`. Chi tiết Bảng 8–10 / ngưỡng hội tụ 1e−9 / "ACO/SA fail khi k>2": **[PARTIAL]** — metadata VERIFIED, chi tiết nội bảng từ bản đọc toàn văn đã ghi ở prereg §6/A4b (cần mở lại toàn văn trước khi trích số cụ thể).
- **Method + dataset.** So sánh 6 metaheuristic (GA, SA, ACO, PSO, TS, DE...) cho multilevel thresholding. Bảng 8 = nghiệm **vét cạn toàn cục**; Bảng 9 = mean±std so với nó; Bảng 10 = hội tụ định nghĩa bằng |F − F_opt| ≤ **1e−9** — **chính là hit-rate của P2, ngưỡng chặt hơn 1e−4 của ta 5 bậc, in 16 năm trước.** Ảnh xám, không GT lâm sàng.
- **Cảnh báo tự-bác-bỏ.** Họ thấy **ACO/SA KHÔNG đạt tối ưu khi k>2** ⇒ ngưỡng preregister cũ `hit_rate ≥ 0.99 cho MỌI thuật toán ở MỌI k` có nguy cơ **tự bác bỏ**. Đã sửa ở prereg §6/A4b (fallback graded: báo cáo k* = k lớn nhất mà hit_rate ≥ 0.99).

**Positioning (drop-in, EN):**
> The comparison of metaheuristics against a globally optimal thresholding solution is itself not new: Hammouche et al. [EAAI 2010] benchmark six metaheuristics against an exhaustive global optimum, defining convergence as |F − F_opt| ≤ 10⁻⁹ — a stricter criterion than we adopt, sixteen years earlier. Two things distinguish our study. First, they operate on gray-level images without clinical ground truth, so a residual fitness gap cannot be projected onto a Dice-scored mask; we make exactly that projection the primary endpoint. Second, they already observe that some methods (e.g., ACO, SA) fail to reach the optimum for k > 2 — a finding we corroborate and reframe: metaheuristics begin to fall short only in the high-k regime where, by our degeneracy argument, the induced clinical mask no longer changes. They shortfall where it does not matter.

---

## 7. Al-Najdawi et al. (2025) — Scientific Reports (near-rival setup + HIỆN VẬT VÀNG cho Bảng I)

- **Verify.** [VERIFIED] Crossref: *"Comprehensive evaluation of optimization algorithms for medical image segmentation"*, Nijad A. Al-Najdawi, Ali F. Al-Shawabkeh, Sara Tedmori, Ibrahim I. Ikhries, Osama Dorgham, **Scientific Reports 15:37190 (2025)**, `10.1038/s41598-025-14261-z` (24/10/2025). Số "18 optimizer" / "Dice 0.85–0.88" / câu limitation "the absence of ground truth annotations": **[PARTIAL]** — nature.com bị gate (303→IDP) trong phiên này; nội dung từ search snippet + prereg §6. **PHẢI mở toàn văn trước khi trích số/câu cụ thể.**
- **Method + dataset.** Benchmark một bộ optimizer nổi tiếng **tích hợp với Otsu** để đánh giá hiệu quả giảm chi phí tính toán trong khi giữ chất lượng phân vùng, trên **dataset y tế công khai (TCIA, gồm collection COVID-19-AR).** Báo cáo Dice ~0.85–0.88 [PARTIAL]. Phần limitations **tự thú "the absence of ground truth annotations"** [PARTIAL].
- **Vì sao là HIỆN VẬT VÀNG.** Đây là bằng chứng khả kiểm mạnh nhất cho luận đề: một benchmark quy mô lớn optimizer+Otsu trên ảnh y tế báo Dice cao **trong khi tự thừa nhận thiếu ground truth** ⇒ chính là "đo sai thứ" mà bài phơi bày. Dùng cho Bảng I (trắc lượng) và Introduction.

**Positioning (drop-in, EN):**
> Al-Najdawi et al. [Sci Rep 2025] provide a large-scale, recent benchmark of optimization algorithms coupled with Otsu's method on medical images, reporting strong overlap scores while acknowledging in their limitations the absence of ground-truth annotations. We treat this not as a competitor but as direct evidence for our thesis: the field continues, into 2025, to rank optimizers on medical images by surrogate criteria without validating against clinical masks. Our study supplies precisely the missing element — a ground-truth-anchored, exact-optimum-referenced re-evaluation — and shows how the ranking changes once ground truth is introduced. [Số cụ thể chờ đọc toàn văn — PARTIAL.]

---

## HOÀ GIẢI #1 — Mousavirad "algorithms differ" vs P2 "tương đương phổ quát"

**Mâu thuẫn bề mặt.** Mousavirad et al. (KBS 2023) kết luận các metaheuristic **KHÁC NHAU rõ rệt**, một số "fail to provide satisfactory performance". P2 của ta dự đoán **tương đương phổ quát** (mọi thuật toán đạt ≈ nghiệm tối ưu, và mask lâm sàng như nhau). Nếu để nguyên, reviewer sẽ nói ta bị bài này bác.

**Vì sao KHÔNG mâu thuẫn thật — ba tầng:**

1. **Khác TRỤC ĐO.** Họ đo khác biệt trong **không gian fitness (variance/Otsu)**. P2 (bản sửa §6/A4b) đo khác biệt trong **không gian Dice lâm sàng**. Một khoảng cách 10⁻³ trong variance-space là **có thật** và vẫn có thể **triệt tiêu hoàn toàn** khi chiếu xuống binary mask — vì mask chỉ phụ thuộc ≤2 ngưỡng (P1), và các thuật toán "khác nhau về fitness" vẫn có thể cho ra **đúng cùng một $t_k$** ⇒ mask giống hệt byte-for-byte. Đây chính là **decoupling test P2c** (`Spearman(relative_gap_fitness, |ΔDice vs DP|) ≈ 0`) — biến "mâu thuẫn" thành **một kết quả kiểm được**.

2. **Khác THAM CHIẾU.** Họ so các thuật toán **với nhau**; ta so **với nghiệm tối ưu chính xác** (DP, Menotti 2015). "A tốt hơn B" (kết luận của họ) và "cả A lẫn B đều nằm trong ε của tối ưu toàn cục" (P2a của ta) **có thể đồng thời đúng** — nếu cả hai đều rất gần trần thì khoảng cách A–B nhỏ về tuyệt đối dù xếp hạng được. Hammouche (2010) cho thấy khoảng cách tới tối ưu là nhỏ ở k thấp và chỉ nới ra ở k cao.

3. **P2 đã được HẠ CẤP + sửa ngưỡng.** Bản gốc `hit_rate ≥ 0.99 cho MỌI k` đã bị thay bằng **fallback graded** (báo cáo k*, prereg §6/A4b): ta **thừa nhận trước** rằng ở k lớn một số thuật toán hụt tối ưu — trùng khớp Mousavirad — và lập luận rằng chúng hụt **ở vùng mà mask không đổi** ⇒ không quan trọng lâm sàng. ⇒ Mousavirad trở thành **corroboration**, không phải phản chứng.

**Câu drop-in (EN):** đã nhúng ở cuối positioning của bài #1.

---

## HOÀ GIẢI #2 — François 0.83±0.18 "upper bound" vs P4

**Va chạm.** François & Tinarrage (JMIV 2026) đã IN, trên **BraTS FLAIR**: oracle best Dice = **0.83±0.18**, gọi thẳng là **"an upper bound on the achievable performance within the considered thresholding framework"** (đọc verbatim từ PDF, [VERIFIED]). Nghĩa là **khái niệm trần + dataset + con số + so sánh DL đều đã có chủ.**

**Lằn ranh đỏ (CLAUDE.md lằn ranh #5; prereg §6/A2):**
- **CẤM TUYỆT ĐỐI** mọi câu dạng "we establish the ceiling" / "we are the first to show a ceiling". Đó là **overclaim** trong đúng một bài chuyên trừng phạt overclaim ⇒ chết không cãi được.
- **CẤM** claim định lý level-set (superlevel-set của purity là nghiệm Dice tối ưu) là của mình — nó thuộc **Lipton, Elkan & Narayanaswamy (arXiv:1402.1892, 2014)** + RankSEG (Dai & Li, JMLR 2023). Ta **claim ứng dụng, KHÔNG claim toán học.**

**Ta ĐƯỢC PHÉP claim gì (đóng góp dương thực sự):**
1. **Ceiling DECOMPOSITION** — François nói *rằng* thresholding chạm trần; ta phân rã trần thành: (a) oracle-1-khoảng (trần của decoder chọn-dải-liên-tiếp) → (b) oracle level-set / graylevel-set tuỳ ý (trần đúng của **mọi** decoder chỉ-dùng-cường-độ, theo Lipton 2014) → (c) 2D U-Net cùng-input (cận DL công bằng). Phân rã này định lượng gap thành *"thiếu thông tin trong CƯỜNG ĐỘ"* vs *"thiếu thông tin trong PIXEL"* — **chưa ai làm.**
2. **Target KHÓ mà François KHÔNG chạm:** ET trên T1ce (vành sáng bao lõi tối) — nơi giới hạn biểu diễn là **THẬT về mặt toán**, không phải giả định. Giữ WT/FLAIR làm trường-hợp-thuận-lợi-nhất-cho-phe-bị-audit (lập luận a fortiori).

**Hệ quả cho P4 (fallback đã khoá, prereg §6/A2):** vì 0.83 KHÔNG thấp (nằm trong vùng đồng thuận liên-quan-sát-viên WT ~0.85–0.87), nhánh "U-Net vượt trần" có thể THẤT BẠI. Nếu U-Net không vượt, **KHÔNG** rút về "thresholding chạm trần của chính nó" (= zero novelty, đúng bằng François). Headline đổi thành: **"Trần CAO — và đó mới là điều đáng nói: thất bại của thresholding không do giới hạn biểu diễn mà do BÀI TOÁN CHỌN NGƯỠNG, và không một cỗ máy metaheuristic nào chạm tới bài toán chọn đó."**

**Câu drop-in (EN):** đã nhúng trong positioning của bài #2.

---

## Kết luận CỔNG TUẦN 0

Cả 6 bài bắt buộc + Al-Najdawi đã được định vị; **đủ điều kiện mở E2 về mặt lit-review** (prereg §6/A10 yêu cầu: "Không chạy E2 trước khi cả sáu đã đọc và có đoạn định vị viết sẵn" — nay đã có).

**Ba near-rival phải cite ở Abstract:** Menotti (exact solver) · François & Tinarrage (trần) · Hammouche (metaheuristic-vs-optimum). **Hai bài Hegazy & Gabr** phải cite ở §2 + là lý do đăng preprint sớm.

**Việc còn nợ (mở toàn văn trước khi trích SỐ/CÂU cụ thể vào bản thảo):** Mousavirad kết luận verbatim · Menotti runtime "<160 ms" · Hammouche Bảng 8–10 & ngưỡng 1e−9 · Al-Najdawi "18 optimizer / Dice 0.85–0.88 / absence of ground truth annotations". Tất cả là [PARTIAL] do paywall/gate phiên này; metadata của tất cả là [VERIFIED].

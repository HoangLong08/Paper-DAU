# Đánh giá `docs/Huong-trien-khai-paper-QIGOA-Long.docx`

**Ngày:** 13/07/2026 · **Đối tượng:** file DOCX trên đĩa (bản thầy sẽ nhận) + `docs/_docx_trien-khai.md` (bản nguồn)
**Phương pháp:** panel 5 reviewer (skill `academic-paper-reviewer` mode `full`) + fact-check web (IRON RULE 4) + integrity audit đối chiếu CLAUDE.md §2 và preregistration §6. Tổng 7 agent độc lập, không tham chiếu chéo nhau.

---

## VERDICT

> # ❌ KHÔNG ổn. KHÔNG gửi file DOCX này cho thầy.
>
> **Editorial Decision: REJECT** (bản DOCX trên đĩa) · **MAJOR REVISION** (hướng nghiên cứu sau khi sửa).
> Devil's Advocate tìm thấy **7 CRITICAL** ⇒ theo IRON RULE của skill, quyết định **không thể là Accept**.

Nhưng lý do reject **không phải** "hướng nghiên cứu sai". Luận đề trung tâm — *trong miền có ground truth lâm sàng, khoảng cách tối ưu mà cả dòng văn liệu đang tranh nhau không chiếu xuống mask lâm sàng* — **đúng, quan trọng, và đáng đăng**. Cả 5 reviewer đều nói vậy, kể cả reviewer đóng vai người bị audit.

Lý do reject là: **bản thảo trên đĩa không phải bản thảo đó.**

---

## 1. Phát hiện bao trùm — có BA mức cập nhật đang cùng tồn tại

| File | Trạng thái |
|---|---|
| `docs/preregistration.md` §6 | **Mới nhất** — Amendment #1, 11 mục A0–A10, 4 mục 🔴 FATAL |
| `docs/_docx_trien-khai.md` | **Trung gian** — có level-set, có Menotti, bỏ "250×"; **thiếu** A3 (leakage), A8 (n=369, TCGA), A9 (nhãn prereg), A0 (một luận đề) |
| **`docs/Huong-trien-khai-paper-QIGOA-Long.docx`** | **CŨ NHẤT — build 02:20, chưa hấp thụ MỘT sửa đổi nào của Amendment #1** |

Xác minh bằng cách giải nén `word/document.xml`. Các từ khoá sau **không xuất hiện một lần nào** trong DOCX:

> `Menotti` · `François` · `Tinarrage` · `Lipton` · `Hammouche` · `Mousavirad` · `Hegazy` · `level-set` · `PLACEHOLDER` · `369` · `name_mapping` · `nested` · `out-of-fold` · `Cohen` / `κ` · `pratt` · `power` · `SESOI`

Còn các câu **đã bị dán nhãn FATAL/CẤM** thì vẫn nguyên văn:

| Nguyên văn trong DOCX | Trạng thái theo prereg §6 |
|---|---|
| *"Oracle một-khoảng … **Trần của MỌI thresholding cường độ**"* | **A2 — SAI VỀ TOÁN, 🔴 FATAL** |
| *"nhanh hơn khoảng **250 lần**"* (×3) | **Đã bỏ** — artifact vòng lặp Python |
| *"Quy tắc … mà **cả dòng văn liệu đang dùng** là 'lấy lớp sáng nhất'"* | **A1 — ⛔ CẤM, xuyên tạc công trình được cite** |
| *"chúng ta là **người đầu tiên bước qua**"* | **IRON RULE 5** — collision-check đã bác |
| Oracle một-khoảng: *"**~30 giây**"* | **A8 — sai 4 bậc độ lớn** (thực tế: mili-giây) |
| *"**Bộ giải mili-giây**"* làm đóng góp dương #1 | **Menotti 2015 đã in 11 năm trước** |
| Bảng Dice/PSNR/SSIM của lô `c4fe108` | **Không một nhãn `[PLACEHOLDER]` nào** |

**Hệ quả:** nếu thầy đọc bản này và gật, ta đã xin thầy gật vào một bài tự sát. Và tệ hơn: thầy có thể **trích lại** những con số của lô hỏng đó ở seminar hoặc đề cương khác — số của một pipeline có 4 lỗi đã đi ra ngoài, mang tên hai người.

---

## 2. Fact-check — cái gì đã được web-verify (IRON RULE 4)

### 🔴 Xác nhận: ba quả bom là THẬT

**Menotti, Najman & de A. Araújo (CIARP 2015)**, `10.1007/978-3-319-25751-8_42`, LNCS pp. 350–357. Nguyên văn: *"a polynomial easy-to-implement **dynamic programming** algorithm to find the **exact optimum thresholds** of three well-known criteria functions: … **the maximum histogram entropy (Kapur et al.'s method)**"* · *"**O((K−1)L²)** time complexity"* · *"exact optimum thresholds … can be found in **less than 160 milliseconds** … **in whatever the number of classes**."*
⇒ Đúng thuật toán, **đúng hàm mục tiêu (Kapur)**, đúng độ phức tạp, đúng bậc thời gian — **in 11 năm trước**. DOCX **không cite ở bất kỳ đâu**.

**François & Tinarrage**, JMIV **68, 20 (2026)**, `10.1007/s10851-026-01300-1` (arXiv:2401.01160). Nguyên văn: *"the oracle best Dice score reaches a mean of **0.83±0.18**. These results provide **an upper bound on the achievable performance within the considered thresholding framework**."* — **trên BraTS, FLAIR, whole tumor**, kèm so sánh deep learning.
⇒ Khái niệm + dataset + **con số** + cả cụm từ "upper bound" đều đã in, peer-reviewed. **Mọi câu "we establish the ceiling" là overclaim kiểm bác được.**

**LGG "ngoại kiểm" là SAI SỰ THẬT.** Buda et al. = **110 bệnh nhân TCGA-LGG (TCIA)**. Trang dữ liệu chính thức của CBICA BraTS 2020: *"we provide the naming convention and direct filename mapping between the data of BraTS'20-'17, and the **TCGA-GBM and TCGA-LGG collections**"*. TCIA `BraTS-TCGA-LGG` = **108 subjects**.
⇒ 108/110 gần như trùng hoàn toàn. Ba chữ *"khác cơ sở, khác máy chụp, khác grade"* **đều sai**.

### 🆕 Ba phát hiện mới mà repo chưa có

1. **Merzban & Elbayoumi (ESWA 2019) là bài về OTSU, không phải Kapur.** DOCX dùng nó (cùng Luessi 2009) làm chống lưng duy nhất cho *"nghiệm chính xác Kapur đã có"*. **Sai họ hàm mục tiêu.** Bài duy nhất thực sự giải chính xác Kapur là Menotti — và DOCX không nhắc.

2. **"J. Ambient Intelligence đã bị Clarivate delist" — KHÔNG CÓ BẰNG CHỨNG.** MTAP delist tháng 10/2024 ✅ (Retraction Watch). JAIHC thì **không**: không có trong đợt delist 3/2023, không có trong đợt 10/2024, **vẫn nhận IF từ Clarivate đợt 6/2025**. Có thể đã nhầm **51 bài bị retract (2022)** thành delisting — **retraction ≠ delisting**.
   ⚠️ **Khẳng định sai này cũng đang nằm trong [CLAUDE.md:52](../CLAUDE.md#L52)** — cần sửa cả ở đó.

3. **nnU-Net Dice WT = 0,9124 là số VALIDATION SET.** Kết quả test chính thức BraTS 2020 (Isensee et al., arXiv:2011.00848): *"took the first place … with Dice scores of **88.95**, 85.06 and 82.03"* ⇒ **WT test = 0,8895**. DOCX dùng 0,9124 không dán nhãn ⇒ trần DL bị thổi lên ~2,3 điểm Dice.

### ✅ Xác nhận không vi phạm

- **Hegazy & Gabr, arXiv:2605.27287 và 2605.27132 — CẢ HAI TỒN TẠI THẬT** (arXiv API). Không phải citation bịa. Nhưng DOCX **không cite**.
- Lipton et al. arXiv:1402.1892 ✅ · Hammouche EAAI 2010 ✅ (metadata; toàn văn `[PARTIAL — paywall]`) · Platel IEEE TEVC 2009 ✅ · QGOA IJAR 2020 ✅ · Luessi JEI 2009 ✅.
- **Lý do loại JBHI trong DOCX là SAI:** JBHI có section biên tập chính thức tên đúng là **"Imaging Informatics"**. Thầy mở trang scope ra trong 30 giây là lập luận sập. (Lý do **đúng** để tránh JBHI: bar quá cao + độc giả thờ ơ.)
- **BSPC:** IF 4.9 ✅ nhưng là **JCR Q2**, không phải "Q1/Q2"; **hybrid** — subscription miễn phí, **OA route = USD 2.980**.

---

## 3. Điểm số panel

| Reviewer | Điểm | Quyết định |
|---|---|---|
| **EIC** (editor BSPC) | 55/100 | Major Revision *có điều kiện* — **Reject nếu nhận đúng bản DOCX** |
| **R1 — Methodology** | **24/100** | **REJECT** |
| **R2 — Domain** (người bị audit) | 37,6/100 | Major Revision, **sát ranh giới Reject** |
| **R3 — Perspective** (bác sĩ / BraTS) | ~43/100 | Major Revision |
| **Devil's Advocate** | — | **REJECT** (7 CRITICAL) |

---

## 4. Những lỗi CÒN SỐNG Ở CẢ HAI FILE

> **Đây là phần quan trọng nhất của báo cáo.** Build lại DOCX từ `.md` **KHÔNG đủ** — bốn lỗi dưới đây tồn tại ở cả hai, và chúng là lỗi thật của *hướng nghiên cứu*, không phải lỗi build file.

### BL-1 · Quy kết decoding cho văn liệu — xuyên tạc công trình được cite 🔴
Cả DOCX và `.md:58`, `.md:83`: *"Quy tắc … **mà cả dòng văn liệu đang dùng** là 'lấy lớp sáng nhất'."*
Quy tắc `seg == seg.max()` **không tìm thấy trong văn liệu** — nó là code cũ của chính ta. Đa số bài **không tạo binary mask và không dùng GT** (PLOS ONE 2024 CIWP-PSO tự viết *"does not compare results against ground truth segmentation masks"*); thiểu số có Dice thì decode bằng **region growing / k-means + morphology**.

Reviewer sẽ viết: *"The authors attribute to refs [12]–[25] a decoding rule that none of those papers states. The central 'degeneracy' result is an artifact of the authors' own implementation, not of the literature."*
⇒ **Reject vì misrepresentation**, không phải vì novelty. Đây là cách chết nhanh nhất.

**Sửa:** viết thành **THẾ LƯỠNG NAN** (prereg A1). *Horn 1* — nếu decode bằng band mask ⇒ k−1 ngưỡng là biến giả. *Horn 2* — nếu decode bằng segmenter hạ nguồn ⇒ mask do segmenter tạo, và **tầng thresholding chưa từng được ablate trong bất kỳ bài nào** ⇒ claim nhân quả *"optimizer tốt hơn ⇒ mask tốt hơn"* **chưa được kiểm**. Hai sừng đều kết tội, **không cần biết văn liệu ở sừng nào**.

### BL-2 · Dán nhãn SAI cho preregistration 🔴
Cả hai: *"Bốn mệnh đề đã được khoá trong một bản **preregistration viết trước khi chạy bất kỳ thí nghiệm nào**"* — trong khi §1.3, cách đó 44 dòng: *"Lô thí nghiệm đầu tiên **đã chạy xong** (25.200 lượt chạy). Khi đọc kỹ số liệu, **ba sự thật hiện ra**."* Ba "sự thật" đó **chính là** P1, P2, P3.
⇒ **HARKing đeo phù hiệu preregistration**, và **bài tự cung cấp cả hai nửa của bằng chứng trên cùng một trang**.

**Sửa (prereg A9):** gọi đúng tên — *"Confirmatory analysis protocol for exploratory findings — P1/P3 were discovered exploratorily on a flawed pipeline; this protocol pre-specifies the confirmatory re-analysis."*
> **Bị bắt vì dán nhãn sai một preregistration còn tệ hơn nhiều so với không có preregistration.**

### BL-3 · Đóng góp dương — và R1 đã SỬA LẠI cách hiểu về nó 🔴

DOCX: *"một ngưỡng phân vị cố định, **hiệu chỉnh trên mười ảnh huấn luyện**"*, rồi so trên **150 ảnh**. `.md` bỏ câu này khỏi §3 nhưng **vẫn liệt kê bậc 5 là "Đóng góp dương của bài"** (`:188`) và **không có một chữ nào về split**.

**R1 tự chạy số và tìm ra điều khác với preregistration:**

```
Dice trên 10 ảnh train           : 0,6857
Dice trên cả 150 (chứa 10)       : 0,6826   <- con số bài sẽ in
Dice out-of-sample thật (140)    : 0,6824
=> Ô nhiễm qua phần chồng lấn    : +0,0002 Dice  (KHÔNG ĐÁNG KỂ)
```

⇒ **Độ lớn leakage là dưới ngưỡng SESOI.** Một phương pháp **một tham số** có capacity quá thấp để overfit trên 10 ảnh.

> **Nhưng đó là tin XẤU, không phải tin tốt.** Nó có nghĩa vấn đề **không phải leakage** — mà là **CATEGORY CONFOUND**, và **một split sạch KHÔNG sửa được nó**:
>
> - **7 metaheuristic:** unsupervised, per-image, **chưa từng nhìn thấy một pixel ground truth nào**.
> - **Ngưỡng 1-tham-số:** **nhìn thấy ground truth** của 10 ảnh.
>
> ⇒ Đây là so sánh **"có giám sát vs không giám sát"**, không phải *"nhanh hơn vs chậm hơn"*. Kể cả khi split hoàn toàn sạch, việc một phương pháp được nhìn GT thắng bảy phương pháp không được nhìn GT **không phải một đóng góp — đó là điều hiển nhiên.**

**Sửa (mạnh hơn prereg A3):**
1. Nested CV, split cấp bệnh nhân (A3) — **cần, nhưng chưa đủ**.
2. **Phân loại 3 hạng, không bao giờ để hạng A và B trong cùng một cột thắng/thua:** **A** unsupervised per-image (Otsu, Li, k-means, GMM, DP-exact, 7 metaheuristic, random search) · **B** CÓ HỌC (U-Net · ngưỡng 1-tham-số · **việc chọn k** · mọi hậu xử lý tuned) → **chỉ out-of-fold** · **C** oracle → **không phải phương pháp**, dán nhãn `uses test-time ground truth` ở **mọi** bảng/hình.
3. **Đổi cách bán:** không bán *"một tham số đánh bại cả họ phương pháp"*. Bán: *"**với cùng lượng giám sát bằng 0**, DP-exact chi phối mọi metaheuristic; và **chỉ cần 10 nhãn** là đủ vượt toàn bộ họ phương pháp — đó là thước đo mức độ vô ích của việc tối ưu hoá Kapur."* Câu đó **đúng**, có cùng sức nặng biên tập, và **không phải một so sánh gian lận**.

### BL-4 · "Người đầu tiên" — `.md` chỉ đổi chữ, không vá được 🔴
DOCX: *"chúng ta là **người đầu tiên bước qua**"*. `.md:287` sửa thành: *"ta là người **đầu tiên đo** xem căn phòng đó cao bao nhiêu"*.
Nhưng `.md:284`, **cách đó ba dòng**, tự viết: *"François & Tinarrage — **đã in trần oracle 0,83±0,18 trên BraTS FLAIR**."*
⇒ **Đã có người đo căn phòng cao bao nhiêu, đúng dataset, đúng modality, đã in số.** Sửa "first to walk through" thành "first to measure" là **vá đúng vào chỗ đã bị chiếm**.

**Định vị hợp pháp duy nhất còn lại:** **ceiling DECOMPOSITION** (chỉ-FLAIR vs histogram 4-mô-thức vs U-Net cùng input) — không phải "đo trần".

---

## 5. Ba lỗi thống kê mà ngay cả preregistration §6 cũng chưa có

R1 tự chạy lại thống kê thay vì tin số được khai báo.

### 🆕 S-1 · ρ = −0,893 mà bài đang trưng làm bằng chứng chủ lực **KHÔNG đạt p < 0,05**

Liệt kê toàn bộ 5.040 hoán vị của n=7, và kiểm ngay trên lưới k của chính bài (k = 2,4,6,8,10 ⇒ **n = 5 điểm**):

```
Spearman = -0.9000,  exact two-tailed p = 0.0833   -> KHÔNG SIG ở alpha = 0.05
```
Với n=5, ngay cả ρ = −1,0 cũng chỉ cho p = 0,0167.
⇒ **Con số headline của §1.3 không đạt ý nghĩa thống kê trên chính lưới k của nó.** Reviewer nào chạy lại trong 3 phút sẽ thấy.

Và decision rule preregister (`ρ < −0,5` **VÀ** `p < 0,05`, n=7): critical value là **|ρ| ≥ 0,786**. Vùng chết `−0,786 < ρ < −0,5` rộng **0,286** — **29% của nửa thang âm**, **không có tiebreak**.

### 🆕 S-2 · TOST là một VÒNG TRÒN CÔNG CỤ — nó không thể cứu bài ở bất kỳ trạng thái nào của thế giới

```
tỷ lệ mask giống hệt = 90%  ->  SD_d ~ 0.018  ->  TOST power = 1.000
tỷ lệ mask giống hệt = 80%  ->  SD_d ~ 0.037  ->  TOST power = 0.908
tỷ lệ mask giống hệt = 50%  ->  SD_d ~ 0.055  ->  TOST power = 0.426
tỷ lệ mask giống hệt =  0%  ->  SD_d ~ 0.084  ->  TOST power = 0.000
```

> **TOST chỉ có power nếu P1 gần như đúng tuyệt đối (≥80% mask trùng nhau).**
> **Nhưng nếu ≥80% mask trùng nhau, ta KHÔNG CẦN TOST** — ta báo cáo **tỷ lệ trùng mask**, một con số không cần kiểm định và không phản bác được.
> ⇒ **TOST chỉ cần thiết ở đúng kịch bản mà nó không có power.**

Và dưới hiệu pilot (PSO − QIGOA = 0,009 Dice, SD_d = 0,05): power tại n=150 là **0,079**. Để kết luận tương đương cần **n ≈ 6.765 bệnh nhân**. BraTS 2020 có **369**.

### 🆕 S-3 · `zero_method` mặc định sẽ ÂM THẦM ĐẢO NGƯỢC thông điệp của bài

`scipy.stats.wilcoxon` mặc định `zero_method='wilcox'` — **loại bỏ toàn bộ cặp có hiệu bằng 0**. Theo P1, hai thuật toán tìm cùng `t_k` ⇒ mask **giống hệt bit-for-bit** ⇒ `d_i = 0` **chính xác**. Đây không phải trường hợp hiếm — **đó là dự đoán trung tâm của bài**.

Mô phỏng (120/150 BN mask giống hệt; 30 BN còn lại lệch 0,02 Dice):
```
zero_method='wilcox'  (MẶC ĐỊNH)  ->  p = 1.73e-06    n hiệu dụng = 30
zero_method='pratt'                ->  p = 4.60e-08    n hiệu dụng = 150
```
⇒ Bài sẽ in *"QIGOA khác PSO có ý nghĩa thống kê (p < 0,001)"*, trong khi phát biểu **đúng** của test đó chỉ là: *"trong nhóm thiểu số 30 bệnh nhân mà hai thuật toán bất đồng, QIGOA khác PSO."* **Ngược hoàn toàn thông điệp của bài.**
⇒ Bài sẽ **tự sinh ra đúng thứ "ý nghĩa thống kê giả" mà nó dành 10 trang để tố cáo.** Và con số **120/150 = 80% bệnh nhân có mask GIỐNG HỆT NHAU** — thứ đáng ra là **cả bài báo gói trong một phân số** — bị **vứt vào thùng rác bởi một tham số mặc định**.

**Khoá `zero_method='pratt'`. Báo `n_zero/n_total` trong mọi bảng.**

---

## 6. Bốn tội mà bài đang tự phạm — đúng bốn tội nó đi tố cáo

| Bài tố cáo văn liệu | Bài đang tự làm |
|---|---|
| *"So sánh không cùng ngân sách"* | So sánh **supervised với unsupervised** (BL-3); và **equal NFE nhưng KHÔNG equal tuning budget** — QIGOA được tune, baseline lấy default từ paper gốc cho bài toán khác |
| *"Ý nghĩa thống kê sinh ra từ một baseline hỏng"* | `zero_method` mặc định **tự sinh significance giả** từ 20% dữ liệu (S-3) |
| *"Tối ưu một biến rồi báo cáo một biến khác"* | **SESOI cỡ theo effect đã quan sát** — Goodhart trên trục **ngưỡng quyết định** |
| *"Không ai kiểm chứng được số của họ"* | **Không seed, không config, không manifest, không split** trong đề cương |

Và một tội thứ năm, nặng hơn cả bốn: **P2 hiện KHÔNG THỂ BỊ BÁC BỎ.**

> Tiêu chí dùng để dán nhãn "hỏng" = thuật toán **không** đạt gần tối ưu.
> Nội dung của P2 = **mọi** thuật toán **đạt** gần tối ưu.
> ⇒ Bất kỳ thuật toán nào **bác bỏ P2** sẽ **tự động bị dán nhãn "bug" và loại khỏi mẫu**.
> ⇒ **P2 unfalsifiable** — trong một bài mà **điểm bán hàng chính là tính bác bỏ được.**

Và điều này không phải giả thuyết suông: **Hammouche et al. (EAAI 2010) đã báo ACO/SA KHÔNG đạt tối ưu khi k > 2.** Thiết kế hiện tại sẽ **gọi họ là bug** thay vì chấp nhận P2 sai.

---

## 7. Phân xử bất đồng giữa reviewer

### ⚖️ ET vs TC trên T1ce — **preregistration §6/A2 SAI, cần sửa**

`.md:206` và prereg A2 viết: *"enhancing tumor trên T1ce — một **vành sáng bao lõi tối**, thứ mà một dải cường độ liên tiếp **về mặt toán học không thể** biểu diễn."* Devil's Advocate lặp lại lập luận này.

**R3 (bác sĩ chẩn đoán hình ảnh) bác bỏ, và R3 đúng:**

> Với target = **ET (chỉ vành sáng)**, lõi hoại tử **KHÔNG nằm trong target**. Vành sáng **tự nó là một dải cường độ cao** — một khoảng liên tiếp `[t, 255]` biểu diễn nó **được**. Thất bại của thresholding trên ET **không phải bất khả thi hình học**; nó là **bất khả phân trong biên cường độ** (mạch máu, màng cứng, xoang tĩnh mạch cũng bắt thuốc và cũng nằm trong dải sáng đó). Nếu bài viết *"về mặt toán học không thể"*, reviewer bác bỏ bằng một câu.
>
> **Target ĐÚNG để chứng minh bất khả thi hình học là TUMOR CORE (TC) trên T1ce.** TC = vành bắt thuốc (**rất sáng**) + hoại tử (**rất tối**) + non-enhancing. Hai thành phần nằm ở **hai đầu đối diện của thang cường độ**, với **nhu mô não bình thường chen ở giữa**. Một khoảng liên tiếp **về mặt tập hợp không thể** chứa cả hai đầu mà không nuốt trọn phần ở giữa.

⇒ **Sửa prereg A2: đổi target khó từ ET/T1ce sang TC/T1ce.** Và điều này **quý hơn**: trên TC/T1ce, khoảng cách giữa **oracle-1-khoảng** và **oracle level-set** sẽ **lớn và có ý nghĩa lâm sàng**, trong khi trên WT/FLAIR nó gần như bằng 0. **Đó chính là hình chủ đạo mà bài đang thiếu** — và nó **miễn phí** (cùng histogram, cùng oracle, cùng script).

### ⚖️ Bảng I — chạy TRƯỚC, nhưng KHÔNG đặt làm Bảng I

EIC muốn đẩy xuống Supplementary (*"bảng đầu tiên của bài anh là một bảng đếm những bài mà tôi đã accept"*). Devil's Advocate muốn chạy nó **đầu tiên** (0 compute, quyết định P1 có mục tiêu hay là strawman). **Không mâu thuẫn:**

- **Thứ tự CHẠY:** tuần 1, trước mọi thứ. Nó quyết định bài có tồn tại không.
- **Vị trí TRÌNH BÀY:** Section 2 dạng tổng hợp thống kê, hoặc Supplementary. **Không bao giờ là bảng đầu tiên.**
- **Điều kiện:** search string · PRISMA-lite flow · codebook · **2 coder độc lập** · **Cohen's κ** · quy trình phân xử. **Không có κ thì không có Bảng I.** Một bài phê phán phương pháp luận **không được phép có một bảng bằng chứng không có phương pháp luận**.
- **Đổi tiêu chí (R2 đề xuất, và nó sắc hơn):** thay *"không cite Merzban/Luessi"* (không phải một lỗi phương pháp — tại sao một bài optimizer phải cite một bài DP?) bằng: *"claim tìm được ngưỡng **tốt hơn** (fitness cao hơn) trên một hàm mục tiêu **có nghiệm chính xác tính được**, mà **không báo cáo gap tới nghiệm đó**."* Đó là một lỗi thật, kiểm được, và **không có đường cãi**.

---

## 8. Novelty còn lại sau khi trừ hết near-rival

| Đóng góp tuyên bố | Ai đã sở hữu | Còn lại |
|---|---|---|
| Exact DP cho Kapur, mili-giây | **Menotti et al., CIARP 2015** | **0** |
| Metaheuristic ≈ nghiệm vét cạn (hit-rate) | **Hammouche et al., EAAI 2010** (ngưỡng 1e−9) | ≈ 0 — *còn: random search ở equal-NFE* |
| Định lý oracle level-set | **Lipton et al., arXiv:1402.1892** / RankSEG | **0 (toán học)** |
| Trần thresholding trên BraTS | **François & Tinarrage, JMIV 2026** (0,83±0,18) | **0** |
| PSNR/SSIM sai cho segmentation | **Fardo et al. 2016**; **Hegazy & Gabr 2026** | ≈ 0 — *còn: miền có GT lâm sàng* |
| **Checklist giao thức đánh giá** | 🆕 **LaTorre et al., Swarm & Evol. Comput. 67:100973 (2021)** — *"A prescription of methodological guidelines for comparing bio-inspired optimization algorithms"* | **≈ 0 nếu không phân biệt được** |

**Số dư thật sự — ba thứ:**

1. **Ceiling decomposition** — trần chỉ-FLAIR vs trần histogram chung 4-mô-thức vs U-Net cùng input, tách gap thành *"không có trong CƯỜNG ĐỘ"* vs *"không có trong PIXEL"*. **Cả 5 reviewer đều xác nhận: chưa ai làm.** ⚠️ Nhưng R2 và DA đều đặt cùng một câu hỏi: **đây là MỘT BÀI BÁO hay MỘT FIGURE?** Trung thực: hiện nó là **một figure rất tốt**. Để thành một bài, nó cần ≥3 dataset và một phát biểu tổng quát về **bao nhiêu %** gap là "không có trong cường độ" vs "không có trong pixel" — và điều đó **chưa có trong bất kỳ kế hoạch nào**.
2. **Equal-NFE benchmark có ground truth lâm sàng + random-search control** — giá trị **benchmark**, không phải giá trị **khám phá**.
3. **Công cụ chẩn đoán O(L·log L)** — claim ứng dụng, không claim toán học. Hợp lệ, và là thứ **duy nhất có thể đổi hành vi**.

**Kết luận về tầm vóc:** đây là **một bài Q2 tử tế và hữu ích**. Không phải một khám phá.

> **Nghịch lý mà EIC muốn tác giả hiểu:** phần khiến bài *cảm thấy* quan trọng (audit, Bảng I, tiêu đề "Optimizing the Wrong Variable") là phần khiến nó **không đăng được**. Phần khiến bài *cảm thấy* khiêm tốn (benchmark + trần + công cụ) là phần **đăng được ngay**.

---

## 9. "SO WHAT?" — đòn nặng nhất, và nó có cấu trúc tự chỉ

Đã có **năm** bài reality-check trên đúng seam này: Fardo 2016 · Merzban 2019 · Mousavirad 2023 · François & Tinarrage 2026 · Hegazy & Gabr 2026.
**Và dòng văn liệu vẫn nở rộ.** BSPC vol. 113 (2026) **vẫn đang in** thresholding y tế với PSNR/SSIM/FSIM và **không có Dice**.

> **Luận đề của bài ("Nhánh A không cite nhánh B") tiên đoán chính xác rằng Nhánh A sẽ không cite BÀI NÀY.** Bài dự báo sự vô can của chính nó. Nếu cơ chế mà bài mô tả là thật, thì cơ chế đó **cũng nuốt luôn bài này** — và nó trở thành bài reality-check **thứ sáu** bị bỏ qua.

**Lối thoát duy nhất không nằm ở cáo trạng — nó nằm ở ARTIFACT.** Hành vi chỉ đổi khi **chi phí không dùng công cụ cao hơn chi phí dùng nó**:
- Công cụ tính trần phải là **một dòng lệnh**: `pip install`, Kaggle notebook public, DOI Zenodo. Khi đó reviewer chỉ cần hỏi: *"tại sao anh không chạy cái này trước?"*
- **Đích thực sự nên là MONAI / Metrics Reloaded**, không phải chỉ BSPC. Một PR vào MONAI làm được nhiều hơn một bài BSPC.
- **Độc giả không phải tác giả bị audit — mà là REVIEWER của họ.** Bạn không thuyết phục được người có động cơ không nghe. Bạn **trang bị vũ khí cho người gác cổng**.

⇒ Mà DOCX xếp công cụ ở **mục 9, Bảng V, tuần chưa xếp lịch**. **Bài đang đặt trọng tâm vào đúng phần vô giá trị nhất của nó.**

---

## 10. Thứ mà panel KHÔNG giết được

Cả 5 reviewer, kể cả người bị audit và Devil's Advocate, đều xác nhận:

1. **Hệ quả định lượng của suy biến là sắc và không cãi được.** Tập mask khả dĩ của **mọi** band-selection decoding có lực lượng ≤ **C(255,2) = 32.385**, bất kể k — trong khi search space tại k=10 là **C(254,10) ≈ 2,6 × 10¹⁷**. **Tỷ số ~10⁻¹³.** Con số này **không cần thí nghiệm, không cần p-value**, và nó **đắt hơn toàn bộ 25.200 run**. **Đây là headline thật sự của bài** — và nó đang bị chôn dưới một unit test ("2.576/2.576 nhóm").

2. **MASK-IDENTITY RATE — kết thúc bài trong một buổi chiều.** Hash binary mask của 7 thuật toán, đếm. *"Trên X% ô (bệnh nhân, k), cả 7 metaheuristic sinh ra binary mask **giống hệt nhau từng byte**."* **Không cần TOST. Không cần ROPE. Không cần power analysis. Không cần U-Net. Không cần DP. Không phản bác được.** Nó **miễn nhiễm** với cả S-2 và S-3.

3. **Kapur cộng tính ⇒ có nghiệm chính xác, và cộng đồng thật sự không cite điều đó.** R2 (người bị audit) tự thú: *"Tôi đã viết những bài so sánh optimizer trên Kapur mà **chưa một lần** báo cáo gap tới nghiệm tối ưu toàn cục — dù nghiệm đó tính được trong mili-giây."*

4. **Tự nêu sự thật bất lợi** (tương quan PSNR–Dice **dương** trong cùng k) — R2: *"90% bản thảo tôi review sẽ giấu."*

5. **Từ chối "quantum advantage", cite Platel 2009** — R2: *"Đúng, và dũng cảm. Đây là điều dòng của tôi lẽ ra phải nói từ 2014."* ✅ **IRON RULE 6: PASS.**

6. **Số thành phần liên thông + empty-mask rate theo k** — *"output thresholding trung vị có N thành phần liên thông; khối u có 1."* Không cần lý thuyết metric, không cần thống kê, **miễn phí**, không phản bác được. Bài đang **bỏ phí bằng chứng đẹp nhất mà nó có**.

---

## 11. REVISION ROADMAP

### 🔴 Cổng 0 — làm ngay, không tốn một giây CPU

| # | Việc | File |
|---|---|---|
| 0.1 | **KHÔNG gửi DOCX hiện tại cho thầy.** | — |
| 0.2 | Vá **BL-1** (thế lưỡng nan) · **BL-2** (đổi nhãn prereg) · **BL-3** (phân loại A/B/C) · **BL-4** (bỏ "đầu tiên đo") | `docs/_docx_trien-khai.md` |
| 0.3 | Đồng bộ mâu thuẫn nội tại: `:188` `:313` (vẫn ghi "bộ giải mili-giây"/ngưỡng-1-tham-số là đóng góp) và `:335` (*"kết luận về trần độc lập với decoding"*) — cả ba **mâu thuẫn với chính §3/§4.3** | `_docx_trien-khai.md` |
| 0.4 | Sửa **prereg A2**: target khó = **TC/T1ce**, không phải ET/T1ce | `docs/preregistration.md` |
| 0.5 | Sửa lý do loại JBHI (không phải "out-of-scope"); gỡ khẳng định **JAIHC delist** (không có bằng chứng); BSPC là **Q2**, OA route **USD 2.980**; nnU-Net WT test = **0,8895** (0,9124 là validation) | `_docx`, [CLAUDE.md:52](../CLAUDE.md#L52) |
| 0.6 | **Rồi mới** build lại DOCX từ `.md` | — |
| 0.7 | Đọc toàn văn 6 bài cổng tuần 0: Menotti · Hammouche · Mousavirad · François & Tinarrage · Hegazy ×2 · Al-Najdawi | — |
| 0.8 | Đăng preregistration lên **OSF/Zenodo** lấy DOI timestamp bên thứ ba; điền commit hash | — |

### 🟠 Cổng 1 — sửa thiết kế (vẫn không tốn compute)

| # | Việc |
|---|---|
| 1.1 | **Nested CV, split cấp bệnh nhân, n = 369** (không phải 150). Commit `data/splits/fold_{0..4}.json` + `brats_cohort.csv`. Power tại SD=0,05: **0,57 → 0,97** |
| 1.2 | **Khoá `zero_method='pratt'`**; báo `n_zero/n_total` mọi bảng; **nâng MASK-IDENTITY RATE lên headline** |
| 1.3 | **Thay TOST pass/fail bằng `Δ_ach` + 90% CI**; nâng **Bayesian ROPE lên PRIMARY**. Phân tích này **không bao giờ "fail"** ⇒ rủi ro FATAL biến mất |
| 1.4 | **Thay decision rule P3** bằng **Δᵢ per-patient + one-sample Wilcoxon (n=369)**. Thêm **lập luận giải tích Lloyd–Max** (PSNR tăng theo k **bằng cấu trúc**) — không thể bị đánh bằng cỡ mẫu |
| 1.5 | **Phá vòng tròn P2:** cổng cứng độc lập (tái tạo bảng Kapur/Otsu **đã công bố** trên Lena/Cameraman/Baboon/Peppers) + tiêu chí loại trừ **ex ante không tham chiếu tới P2**. Fallback **graded qua k\***, không all-or-nothing |
| 1.6 | **Equal TUNING budget**, không chỉ equal NFE. Hoặc: **không tune gì cả**, kể cả QIGOA, và nói thẳng |
| 1.7 | **Đối chiếu `name_mapping.csv`** trước khi dùng chữ "external validation". Nếu trùng ⇒ chuyển sang **ngoại kiểm theo chiều TASK (TC/T1ce)** — rẻ nhất, mạnh nhất, không rủi ro trùng lặp |
| 1.8 | Khai báo: quy ước `0log0` · **có tính nền cường-độ-0 vào histogram không** (lát BraTS đã skull-strip, ~65% pixel ở 0 — **đổi hoàn toàn** ngưỡng tối ưu) · NSD **τ = 2 mm** · **chính sách mask rỗng** (HD95 undefined; ⛔ **CẤM âm thầm loại ca rỗng** = selection bias phá hỏng chính P3) · **5 seed gộp bằng median** |
| 1.9 | **`median [IQR] + bootstrap CI + hình phân bố per-patient`**, không phải `mean ± std`. **Bỏ IoU** (song ánh với Dice). **Thêm: số thành phần liên thông · empty-mask rate · sai số thể tích (RANO)** |
| 1.10 | **Đảo thứ tự thí nghiệm:** tuần 1 = 4 thí nghiệm rủi ro (Bảng I · bậc 5 nested-CV · Spearman theo từng decoding rule · morph vs oracle). Một trong bốn chết ⇒ **tiết kiệm 8 tuần** |
| 1.11 | **Đổi tiêu đề.** Bỏ *"Optimizing the Wrong Variable"* — editor chọn reviewer từ **chính cộng đồng bị audit**. Dùng tiêu đề mô tả, positive-first |
| 1.12 | **Bỏ "chọn mô hình bằng PSNR chủ động làm hại bệnh nhân."** Không hệ thống lâm sàng nào dùng multilevel thresholding — chuỗi nhân quả tới bệnh nhân **không tồn tại**. Viết: *"model selection by PSNR selects the configuration that is worst under the only metric with a clinical referent."* |

### Bổ sung reference bắt buộc

Menotti 2015 (**Abstract**) · François & Tinarrage 2026 · Lipton 2014 · Hammouche 2010 · Mousavirad 2023 · Fardo 2016 · Hegazy & Gabr ×2 · **Menze et al. IEEE TMI 2015** (không có thì trần 0,83 vô nghĩa) · Metrics Reloaded (đầy đủ DOI) · **Sörensen ITOR 2015** · **Camacho-Villalón ITOR 2023** (đã bóc **GWO và WOA** — hai baseline của chính bài) · **Harandi ANTS 2024** (GOA = biến thể PSO) · **LaTorre 2021** (phải phân biệt, nếu không checklist là trùng lặp).

---

## 12. Lộ trình

**8 tuần không khả thi.** Riêng Bảng I làm cho đúng (sampling frame + 2 coder + κ + phân xử) là **1 tuần** và **hiện không có ô nào trong lịch**. Cộng n=369 (×2,46) + nested CV 5-fold × ≥3 seed U-Net + target TC/T1ce + 3 decoder mới + cổng tái tạo benchmark. Ước tính thực tế: **12–14 tuần**.

> Đề cương tự viết: *"nút thắt của bài này không phải là tính toán, mà là lập luận và viết."*
> **Đúng — và đúng hơn tác giả nghĩ.** Toàn bộ 9 lỗi CRITICAL đều sửa được **mà không chạy một giây CPU nào.**

---

## Lời cuối

Bài này **xây một cái máy dò overclaim, rồi đưa chính nó qua máy — và nó kêu.**

Đó không phải lý do để bỏ hướng. Đó là lý do để sửa **trước khi** thầy đọc, và trước khi reviewer đọc. `preregistration.md` §6 là bằng chứng rằng năng lực tự sửa **đã có** — nó bắt được phần lớn những lỗi trên **trước khi nhìn thấy một con số thực nghiệm nào**. Vấn đề duy nhất, và nó nghiêm trọng: **bản đang định gửi cho thầy là bản CHƯA sửa.**

Nếu 20 mục trong Roadmap được làm, bài này **đăng được ở BSPC** — và, quan trọng hơn nhiều, **nó sẽ xứng đáng được đăng.** Sự khác biệt giữa hai điều đó chính là chủ đề của bài báo.

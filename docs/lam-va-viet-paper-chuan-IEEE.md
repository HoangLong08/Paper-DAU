<!-- Trang 1 -->

# Playbook: làm và viết một paper chuẩn IEEE Transactions

Từ một vòng major revision ở một tạp chí IEEE Transactions tới một chuỗi kinh nghiệm cho các bài sau

Tài liệu chia sẻ. Gộp ba mạch: (i) quy trình làm việc người–AI, (ii) kỷ luật thực nghiệm & lập luận, (iii) cách dựng formulation và viết theo phong cách Transaction. Viết từ trải nghiệm thật của một bài solo-author, để dùng lại và để chia sẻ.

**Đỗ Phúc Hảo** (Member, IEEE)
Khoa Công nghệ Thông tin, Trường Đại học Kiến trúc Đà Nẵng, Đà Nẵng, Việt Nam
haodp@dau.edu.vn

> **Một câu tóm tắt**
>
> Một tuyên bố lợi thế hấp dẫn nhưng mong manh, qua từng lớp nghiêm cẩn (sửa cách đo nhiễu → ablation cùng tham số → đa-seed) đã hội tụ về sự thật: **lợi thế biểu kiến không đến từ thành phần mới**. Bài được viết lại trung thực thành một nghiên cứu dependability cộng một defense hoạt động được. Playbook này ghi lại *cách* đi tới đó, và nâng nó thành công thức chung cho một bài chuẩn Transaction.

Phiên bản công khai • palette học thuật navy/steel/amber • đúc kết từ một vòng major revision.

---

<!-- Trang 2 -->

## Mục lục

**1 Bối cảnh và mục đích** — 2

**2 Quy trình làm việc người–AI** — 2
- 2.1 Vòng lặp có kỷ luật — 2
- 2.2 Nguyên tắc vận hành rút ra — 2
- 2.3 Phân vai người và trợ lý — 3

**3 Định nghĩa bài toán chuẩn Transaction (anti-toy)** — 3
- 3.1 Bài kiểm anti-toy — 3
- 3.2 Threat model và nhiễu phải đúng thang — 3
- 3.3 Hình thức hóa: ký hiệu và bài toán cứng — 4

**4 Bộ kỷ luật thực nghiệm** — 4
- 4.1 Ablation cùng tham số — 4
- 4.2 Kiểm soát confound — 5
- 4.3 Đa-seed, luôn luôn — 5
- 4.4 Metric tổng hợp chống cherry-pick — 5
- 4.5 Audit shortcut và nhiễu held-out — 5
- 4.6 Ba cờ đỏ — 5

**5 Lập luận và cách kể chuyện** — 5
- 5.1 Hội tụ, không phải trôi dạt — 6
- 5.2 Reframe trung thực khi tuyên bố chính sụp — 6

**6 Phong cách viết Transaction** — 6
- 6.1 Một bài Transaction khác conference ở đâu — 6
- 6.2 Formulation cứng: Optimization-to-Learning — 6
- 6.3 Evaluation là phép thử bác bỏ — 7
- 6.4 Figure và table chuẩn Transaction — 7
- 6.5 Related work và định vị — 7
- 6.6 Cấu trúc và văn phong — 7

**7 Cơ chế revise một bài Transaction** — 7
- 7.1 Hai bản từ một nguồn — 7
- 7.2 Thư phản hồi từng comment — 8

**8 Verify cuối: kiểm tra đa-chiều độc lập** — 8

**9 Chuỗi kinh nghiệm và checklist nộp** — 8
- 9.1 Chuỗi cho các paper sau — 8
- 9.2 Checklist trước khi nộp — 9

**10 Lời kết** — 9

---

<!-- Trang 3 -->

## 1 Bối cảnh và mục đích

Tài liệu này đúc kết từ một tình huống thật: một bài báo nhận **major revision** ở một tạp chí IEEE Transactions hàng đầu, với hai reviewer cùng yêu cầu một thứ: hãy chứng minh lợi thế robustness được báo cáo thực sự đến từ thành phần mới được đề xuất, chứ không phải từ các lựa chọn kiến trúc cổ điển đi kèm.

Khi làm đúng các thí nghiệm họ đòi, kết luận ban đầu *đảo ngược*. Thay vì giấu, chúng tôi viết lại bài một cách trung thực, và quá trình đó để lại ba mạch kinh nghiệm, cũng là ba phần của playbook: **quy trình làm việc** hiệu quả giữa người và trợ lý AI; **kỷ luật thực nghiệm và lập luận**; và **cách dựng bài toán & viết theo phong cách Transaction**.

> **Bài học bao trùm: để dữ liệu định hình câu chuyện, đừng chốt câu chuyện trước rồi nhồi số**. Ở venue top, reviewer chạy lại code của bạn, nên sự trung thực không chỉ là đạo đức mà là chiến lược: nó là con đường ngắn nhất tới một kết quả đứng vững. Một bài Transaction tốt được dựng theo trình tự ngược với trực giác: *làm cứng bài toán và thực nghiệm trước, để câu chuyện tự nổi lên sau.*

## 2 Quy trình làm việc người–AI

### 2.1 Vòng lặp có kỷ luật

Toàn bộ vòng revise đi theo một vòng lặp, gom thành bốn pha. Mỗi bước nhỏ, kiểm chứng được, và luôn quay lại *đọc số liệu thật* trước khi quyết bước tiếp.

> [Hình: Sơ đồ vòng lặp bốn pha nối bằng mũi tên ngang]
>
> **A. Chuẩn bị** — đọc paper + review, phân tích cơ hội, kéo code, soi lỗ hổng → **B. Thực thi** — sửa theo từng comment, smoke test (dữ liệu giả), push git → chạy server → **C. Đọc & quyết** — đọc REPORT + số liệu, verdict: như kỳ vọng? → **D. Hoàn thiện** — reframe trung thực, verify đa-chiều, sẵn sàng nộp.
>
> Mũi tên cam nét đứt quay ngược từ C về A: *lặp lại với độ chặt cao hơn.*

Hình 1: Vòng lặp làm việc theo bốn pha. Mấu chốt là pha C: luôn đọc số liệu thật rồi mới quyết, và sẵn sàng lặp lại với rigor cao hơn (mũi tên cam) thay vì bảo vệ một kết luận đã định.

### 2.2 Nguyên tắc vận hành rút ra

- **Bước nhỏ, kiểm chứng được.** Mỗi thay đổi code đều *smoke test trên dữ liệu giả* trước khi đẩy lên server. Bắt lỗi ở local rẻ hơn bắt lỗi sau hai giờ chạy GPU.

- **Mọi mẻ dài đều bọc `tmux`.** Server dùng chung dễ bị kill (OOM); `tmux` cộng log ra file giúp không mất tiến trình và xem lại được.

- **Log ra file + một REPORT tổng hợp.** Mỗi lần chạy tự sinh `REPORT.md`: bảng số cộng verdict tự động. Người chỉ cần push, trợ lý đọc đúng một file.

<!-- Trang 4 -->

- **Harness tách biệt.** Không sửa code gốc; dựng riêng một bộ gồm model ablation, bộ đánh giá robustness đa-seed, defense, và script audit. Đầu tư này trả lại gấp nhiều lần qua các vòng lặp.

### 2.3 Phân vai người và trợ lý

Trợ lý viết code, phân tích, soạn bản nháp và thư phản hồi; người chạy server, cung cấp dữ liệu, và *quyết định chiến lược* (giữ venue hay đổi, có làm thêm thí nghiệm không). Đồng bộ qua git: trợ lý push code, người pull và chạy, push kết quả; trợ lý pull và đọc. Ranh giới này giữ cho mỗi bên làm đúng phần mạnh của mình.

## 3 Định nghĩa bài toán chuẩn Transaction (anti-toy)

Sai lầm tốn kém nhất nằm ngay ở *định nghĩa*, trước cả khi chạy mô hình. Một bài Transaction bắt đầu từ một bài toán đã được làm cứng, không phải một "toy problem".

### 3.1 Bài kiểm anti-toy

Trước khi dựng mô hình, chạy bốn phép ép sau (rút từ một bộ skill nội bộ tên `transaction-architect`):

1. **Giết lý tưởng hóa.** Thay CSI hoàn hảo bằng sai số ước lượng; node tĩnh bằng tính di động cao / Doppler; tải cố định bằng phân phối ngẫu nhiên (Gamma, Poisson). Trong bài robustness: thay "ảnh sạch" bằng một *protocol nhiễu thực tế, định nghĩa chặt*.

2. **Tiêm xung đột.** Ép trade-off. Nếu tối đa throughput, thêm ràng buộc năng lượng / jitter để không thể chỉ "tăng công suất". Trong bài robustness: clean accuracy cao *phải* đánh đổi với độ bền dưới nhiễu.

3. **Tiêm độ phức tạp.** Đảm bảo bài toán là MINLP / không lồi, hoặc có *ràng buộc ghép* (lựa chọn của biến này giới hạn vùng khả thi của biến kia).

4. **Biện minh quy mô.** Nếu kịch bản nhỏ, ép quy mô lớn ($N > 1000$) để AI / lượng tử là lời giải *hợp lý duy nhất*.

> **Viết trước một mục "Reviewer 2" cho chính mình:** liệt kê những giả định ngây thơ khiến bài bị reject ngay. Mỗi giả định đó là một chỗ phải làm cứng. Làm việc này *trước khi* viết một dòng kết quả.

### 3.2 Threat model và nhiễu phải đúng thang

Trong bài robustness ảnh, mô hình chuẩn hóa đầu vào (trừ mean, chia std). Câu hỏi sống còn: cộng nhiễu *trước* hay *sau* chuẩn hóa? Lệch thang là nguồn của một "điểm sụp đổ" giả.

> **Chuẩn đúng**
>
> Áp nhiễu lên ảnh **chưa chuẩn hóa trong** $[0, 1]$, **clamp** về $[0, 1]$, rồi mới chuẩn hóa bên trong model. Luôn ghi rõ $\sigma$ đo trên thang nào, và lấy mẫu mức nhiễu **dày** quanh vùng chuyển tiếp.

<!-- Trang 5 -->

> [Hình: Sơ đồ minh họa hai thang đo. Thang trên tiêu đề màu đỏ "Cộng nhiễu **SAU** chuẩn hóa (cách cũ, sai): σ đo trên thang đã chuẩn hóa", với ghi chú "σ=0.4 trông như 'điểm sụp đổ'" và mũi tên đỏ chỉ xuống vị trí 0.4. Trục ngang trên đánh dấu: 0, 0.2, 0.4, 0.6, 0.8, 1.0. Một mũi tên đứt nét màu cam nối từ điểm 0.4 (trục trên) xuống điểm 0.09 (trục dưới) với nhãn "cùng một điểm". Trục ngang dưới đánh dấu: 0, 0.045, 0.09, 0.135, 0.18, 0.225, với mũi tên xanh chỉ lên vị trí 0.09 kèm ghi chú "σ=0.4 thật ra chỉ ≈ 0.09". Tiêu đề dưới màu xanh: "Quy về thang ảnh [0, 1] (chia cho ≈ 0.225): cùng điểm đó thực ra rất nhẹ".]

Hình 2: Cùng một con số σ mang ý nghĩa khác hẳn tùy thang. Cộng nhiễu sau chuẩn hóa (đỏ) khiến σ=0.4 trông "vừa phải" nhưng quy về ảnh [0, 1] chỉ ≈ 0.09 (xanh), một mức rất nhẹ. Lệch thang ≈ 4−5 lần này tạo ra điểm sụp đổ giả và một gap robustness ảo.

### 3.3 Hình thức hóa: ký hiệu và bài toán cứng

Một bài Transaction trình bày bài toán dưới dạng hình thức, với tập / chỉ số rõ ràng và *ràng buộc ghép*. Ví dụ một khung tổng quát (**P1**):

$$\textbf{P1}: \quad \min_{\{x_i\}, \theta} \; L(\theta; D'(\sigma))$$

$$\text{s.t.} \quad \sum_{i \in N} x_i \le B \quad \text{(ngân sách / ràng buộc tài nguyên)}$$

$$g_j(x_i, \theta) \le 0, \; \forall j \in M \quad \text{(ràng buộc ghép biến)}$$

$$\mathbb{E}_{\delta \sim P}[\text{Acc}(\theta; I + \delta)] \ge \tau \quad \text{(yêu cầu dependability dưới nhiễu)}$$

ở đây $D'(\sigma)$ là tập dữ liệu đã nhiễu hóa ở mức $\sigma$, $\delta \sim P$ là nhiễu ngẫu nhiên, và ràng buộc cuối biến "robustness" thành một điều kiện định lượng chứ không phải một lời hứa. Ràng buộc ghép $g_j$ là thứ khiến bài toán không lồi và không thể giải tầm thường.

## 4 Bộ kỷ luật thực nghiệm

Đây là phần quan trọng nhất. Trước khi tuyên bố thành phần X mang lại lợi ích, đi đủ bộ kiểm dưới đây.

### 4.1 Ablation cùng tham số

Dựng baseline *chỉ khác đúng X*: cùng backbone, cùng bottleneck, cùng số tham số (khớp tới vài chục tham số). Nếu một baseline cổ điển ngang X, lợi ích không đến từ X. Ví dụ: nhiều head phân loại (linear / bottleneck phi tuyến / MLP / thành phần mới) gắn trên cùng một backbone, khớp số tham số.

<!-- Trang 6 -->

### 4.2 Kiểm soát confound

Một thay đổi tưởng như thuộc thành phần mới thường kéo theo một thay đổi cổ điển đi kèm (vd "rộng hơn" ở tầng trung gian). Để cô lập đúng phần mới, so ở *cùng độ rộng tầng trung gian*, không phải cùng một siêu tham số bề ngoài. Mọi lợi thế biểu kiến phải được truy về đúng biến gây ra nó.

### 4.3 Đa-seed, luôn luôn

Robustness single-seed dao động lớn và *bịa ra* lợi thế. Báo cáo mean±std qua ≥ 3 seed. Một thứ hạng nằm trong sai số không phải một kết quả.

> [Hình: Biểu đồ cột so sánh AURC. Cột trái màu đỏ "Single-seed (1 lần chạy)" đạt giá trị 95, nhãn dưới "advantage!". Cột phải màu xanh "Đa-seed (3 lần, mean±std)" đạt giá trị 79 với thanh sai số ±19, nhãn dưới "±19: không tin được". Trục tung AURC đánh dấu 50, 75, 100.]

Hình 3: Minh họa: một lần chạy may mắn cho 95 và trông như có lợi thế; trung bình ba seed chỉ còn 79 với độ lệch ±19. "Lợi thế" đó là artifact của bất ổn huấn luyện.

### 4.4 Metric tổng hợp chống cherry-pick

Tóm cả đường cong bằng AURC (diện tích dưới đường accuracy–severity trên một dải cố định) và σ* (mức nghiêm trọng tới hạn). Hai metric này không cho phép chọn một điểm σ đẹp; chúng buộc báo cáo toàn bộ hành vi.

### 4.5 Audit shortcut và nhiễu held-out

Khi accuracy gần hoàn hảo, giải mã / soi đầu vào tìm shortcut tương quan với nhãn (một thuộc tính bề mặt như kích thước / độ phức tạp đầu vào), rồi test trên subset đã khử shortcut. Với một defense, test trên *loại nhiễu chưa train* (blur / JPEG); nếu không, nó chỉ là "học đúng tập test".

### 4.6 Ba cờ đỏ

> **"Hãy điều tra, đừng tin"**: (1) accuracy 100% / AUC = 1.0 (nghi shortcut); (2) loss về 0 tức thì (bài toán tách được tầm thường); (3) sweep lộn xộn / không đơn điệu (bất ổn huấn luyện, không phải kiến trúc).

## 5 Lập luận và cách kể chuyện

<!-- Trang 7 -->

### 5.1 Hội tụ, không phải trôi dạt

Khi kết quả "đổi" qua các vòng, câu hỏi sống còn: nó *hội tụ* hay *dao động*? Nếu mỗi lần tăng độ chặt mà kết luận đi cùng một hướng, đó là dấu hiệu của một kết quả *thật*.

> [Hình: Sơ đồ dòng chảy gồm 4 hộp nối bằng mũi tên, mỗi mũi tên ghi "rigor ↑".
> Hộp 1 (viền/nền đỏ): **Số gốc** — post-norm, 1 seed, chỉ so linear, *"lợi thế lớn"*.
> → Hộp 2 (nền xanh nhạt): **+ sửa noise model** + ablation phi tuyến — *do tanh+bottleneck*.
> → Hộp 3 (nền xanh nhạt): **+ đa-seed** — *thành phần mới bét, variance lớn*.
> → Hộp 4 (nền xanh): **Kết luận ổn định KHÔNG lợi thế**.]

Hình 4: Mỗi lớp nghiêm cẩn đẩy kết luận về cùng một phía. Đó là hội tụ tới sự thật. Quá trình lặp này vô hình với reviewer: họ chỉ đọc bản cuối nhất quán.

### 5.2 Reframe trung thực khi tuyên bố chính sụp

Một kết quả âm được làm nghiêm cẩn, cộng một đóng góp dương, là một bài đăng được. Một kết quả dương bịa ra là một lần reject cộng mất uy tín.

> **Công thức reframe**
>
> **Negative** (tuyên bố cũ sụp) + **Cautionary methodology** (chỉ ra vì sao tuyên bố sai + giao thức để tránh) + **Positive** (một defense / đóng góp xây dựng hoạt động được). Reviewer từng nghi ngờ đúng hướng thường *tôn trọng* một bản revise xác nhận nghi ngờ của họ một cách nghiêm cẩn.

## 6 Phong cách viết Transaction

### 6.1 Một bài Transaction khác conference ở đâu

| | Conference | Transaction |
|---|---|---|
| **Bài toán** | một ý mới, phạm vi hẹp | formulation cứng, ràng buộc ghép, quy mô lớn |
| **Thực nghiệm** | đủ chứng minh ý | ablation cô lập + đa-seed + sensitivity + so SOTA |
| **Bề sâu** | "nó chạy" | "vì sao chạy, khi nào hỏng, so với gì" |
| **Hình** | minh họa ý tưởng | figure kết quả + figure dòng chảy/kiến trúc |
| **Văn phong** | gọn, bán ý tưởng | chặt, định nghĩa hình thức, không over-claim |

Bảng 1: Khác biệt cốt lõi. Transaction đòi *bề sâu và sự chặt chẽ*, không chỉ một ý mới.

### 6.2 Formulation cứng: Optimization-to-Learning

Một bài mạnh cần ba lớp: (1) nền toán chặt (tối ưu: BCD, MM, đối ngẫu Lagrange); (2) xử lý bất định thực tế (mô hình ngẫu nhiên); (3) bước chuyển hợp lý sang AI nâng cao (DRL

<!-- Trang 8 -->

/ KAN / lượng tử) để mở rộng quy mô. Trình bày bài toán cứng **P1** (Mục 3.3), rồi roadmap kép: *Bước 1* một phương pháp toán cho ca đơn giản hóa; *Bước 2* vì sao Bước 1 hỏng ở quy mô lớn nên cần "vũ khí" AI / lượng tử.

### 6.3 Evaluation là phép thử bác bỏ

Ablation không phải để trang trí, mà là *phép thử có thể bác bỏ luận điểm chính*. Thiết kế mỗi thí nghiệm sao cho nếu luận điểm sai, thí nghiệm sẽ *cho thấy điều đó*. Đây là khác biệt giữa "chứng minh tôi đúng" và "cố gắng chứng minh tôi sai, và thất bại". Reviewer phân biệt được hai thứ này.

### 6.4 Figure và table chuẩn Transaction

- **Hai loại figure.** Figure *kết quả* (đường cong có error bar, sinh từ CSV) và figure *dòng chảy / kiến trúc* (vẽ bằng TikZ, không dùng ảnh bitmap). Mọi figure phải nhìn tận mắt sau khi render.
- **Mọi số khớp CSV.** Sinh lại figure bằng script từ kết quả; bỏ bảng nào có số không tái lập được (chúng tôi đã bỏ một bảng latency vì các con số ms là đo một lần, không tái lập).
- **Bảng có header màu, zebra, booktabs.** Dễ đọc, đồng nhất; metric tổng hợp (AURC, $\sigma^*$) đặt ở cột cuối.

### 6.5 Related work và định vị

Cite văn liệu cho *mọi* kỹ thuật "đã biết" bạn dùng (vd noise-aware training quy về common-corruptions); định vị đóng góp trung thực so với chúng; đừng bán một method đã biết là mới. Một câu định vị thẳng thắn mạnh hơn mười câu tự khen.

### 6.6 Cấu trúc và văn phong

Theo IMRaD chặt: Introduction (đóng góp liệt kê rõ), Related work (khoảng trống), Method (formulation + thuật toán), Experiments (setup + ablation + sensitivity), Discussion (vì sao / giới hạn), Conclusion. Math inline dùng `$...$`; bài toán tối ưu trong `aligned`. Tên bài nói đóng góp trung thực, không phải tuyên bố-người-hùng. Phần kỹ thuật bằng tiếng Anh; không over-claim.

## 7 Cơ chế revise một bài Transaction

### 7.1 Hai bản từ một nguồn

Giữ một `body.tex` chung và hai driver: `main.tex` (sạch, định nghĩa `\rev{#1}=#1`) và `main_highlight.tex` (bôi vàng, `soul` + `\hl`). Sửa ở `body.tex` là đồng bộ cả hai; reviewer nhận cả bản đánh dấu lẫn bản sạch.

> Gói `soul` (`\hl`) vỡ với `\url`, `\cite`, `\texttt` có gạch dưới, và math hiển thị. Để những thứ đó *ngoài* vùng highlight; math inline ngắn thường ổn.

<!-- Trang 9 -->

> *Playbook: làm & viết paper robustness — đúc kết từ một vòng major revision*

### 7.2 Thư phản hồi từng comment

Trả lời *từng* comment kèm số liệu mới; mở đầu bằng một general response thẳng thắn nói kết luận đã đổi và vì sao. Trích reviewer trong một box, đặt câu trả lời ngay dưới, và trỏ tới đúng mục / bảng / figure trong bản đã sửa. Build thành PDF riêng.

## 8 Verify cuối: kiểm tra đa-chiều độc lập

Trước khi nộp, kiểm bản cuối bằng các luồng độc lập, mỗi luồng đối chiếu với một nguồn sự thật riêng, để không "tự chấm bài mình".

> [Hình: Sơ đồ — từ khối "Bản cuối (paper)" có các mũi tên trỏ tới 5 khối, mỗi khối đều được đánh dấu ✓: 1. Số vs data (CSV); 2. Figures & refs; 3. Quét tàn dư kết quả cũ; 4. Tables; 5. Build & references.]

Hình 5: Năm luồng verify độc lập. Các lỗi thật (một con số single-seed sót, một caption tràn, một câu khẳng định cũ) được bắt và sửa, rồi build lại sạch.

> **Bộ kiểm tối thiểu mỗi luồng build:** **0** lỗi LaTeX, **0** Overfull `\hbox`, **0** undefined reference, **0** undefined citation, **0** cảnh báo bibtex. Mọi số trong prose/bảng/figure truy được về CSV tới từng chữ số.

## 9 Chuỗi kinh nghiệm và checklist nộp

### 9.1 Chuỗi cho các paper sau

Gộp các skill và bài học thành một dây chuyền dùng lại được:

> [Hình: Sơ đồ dây chuyền gồm các khối nối bằng mũi tên. Hàng trên: "transaction-architect / formulation cứng" → "paper-to-code / thực nghiệm sâu" → "bộ kỷ luật / (đa-seed, audit)" → "tikz-figure / figure kết quả + dòng chảy". Từ khối cuối hàng trên đi xuống "reframe trung thực". Hàng dưới (chảy ngược sang trái): "reframe trung thực" → "hai bản + response letter" → "verify đa-chiều → nộp".]

Hình 6: Dây chuyền tái dùng: làm cứng bài toán → thực nghiệm sâu → bộ kỷ luật → figure chuẩn → (nếu tuyên bố sụp) reframe trung thực → hai bản + thư phản hồi → verify → nộp.

<!-- Trang 10 -->

> *Playbook: làm & viết paper robustness — đúc kết từ một vòng major revision*

### 9.2 Checklist trước khi nộp

Bảng 2 là cổng kiểm cuối: chạy qua nó trước khi nhấn nút nộp, xem mỗi dòng "chưa xong" là một việc phải làm chứ không phải mục để bỏ qua. Mười hai hạng mục đi theo đúng trình tự dây chuyền ở Mục 9.1, từ làm cứng bài toán tới verify. Đáng chú ý nhất: mục 3 (đa-seed cho *mọi* bảng/figure chính) giữ cho bài không tự mâu thuẫn, còn mục 6 (defense trên nhiều held-out) cùng một dataset thứ hai là hai đòn-bẩy *tùy chọn* nhưng mạnh nhất để nâng bài từ "rigorous negative" lên "nghiên cứu hoàn chỉnh". Còn một dòng bắt buộc ×, bài *chưa* sẵn sàng nộp.

| # | Hạng mục | Xong |
|---|----------|------|
| 1 | Bài toán qua bài kiểm anti-toy; threat model đúng thang, ghi rõ | ✓ |
| 2 | Ablation cùng tham số cô lập đúng thành phần được tuyên bố | ✓ |
| 3 | Đa-seed: mọi bảng/figure chính có mean±std | ✓ |
| 4 | Confound được kiểm soát (vd cùng độ rộng bottleneck) | ✓ |
| 5 | Audit shortcut dataset + eval trên subset đã khử | ✓ |
| 6 | Defense (nếu có) test trên nhiều held-out | × tùy chọn |
| 7 | Tên/abstract/kết luận nói đóng góp trung thực | ✓ |
| 8 | Thư phản hồi từng comment kèm số liệu | ✓ |
| 9 | Bản sạch + bản highlight đồng bộ từ một nguồn | ✓ |
| 10 | Figure sinh từ CSV, đã nhìn tận mắt; bỏ số không tái lập | ✓ |
| 11 | Bio tác giả, provenance dataset, Data & Code availability | ✓ |
| 12 | Verify đa-chiều: build sạch, mọi số khớp CSV | ✓ |

Bảng 2: Checklist trước khi nhấn nút nộp. Mục 6 và một dataset thứ hai là hai đòn-bẩy tùy chọn để nâng từ "rigorous negative" lên "nghiên cứu hoàn chỉnh".

## 10 Lời kết

Tài liệu này bắt đầu từ một tình huống không vui: một tuyên bố trung tâm, "thành phần mới giúp mô hình bền hơn trước nhiễu", đã sụp đổ khi bị kiểm chứng nghiêm túc. Nhưng chính chỗ đó lại là bài học lớn nhất. Khi con số đẹp đến từ một seed may mắn, một thang nhiễu mơ hồ, hay một shortcut trong dữ liệu, thì việc trung thực không phải là mất mát mà là cách duy nhất giữ cho công trình đứng vững được lâu. Một negative result chặt chẽ cộng với một defense thực sự hoạt động vẫn là một bài đăng được; một positive result được tô vẽ thì sớm muộn cũng đổ, kéo theo uy tín của tác giả.

Điều tôi muốn người đọc mang theo không phải các con số AURC hay chi tiết của một bài cụ thể, mà là *trình tự*: làm cứng bài toán trước, dựng thực nghiệm đủ kỷ luật để nó không thể nói dối, rồi mới để câu chuyện tự nổi lên từ dữ liệu. Phong cách Transaction không nằm ở câu chữ hoa mỹ, mà ở chỗ mỗi khẳng định đều có một thí nghiệm đứng sau và mỗi con số đều bảo vệ được trước bất kỳ ai hỏi tới. Áp dây chuyền trong Mục 9 *ngay từ đầu*, thay vì khám phá lại nó trong một vòng revise căng thẳng, ta tiết kiệm hàng tháng và viết ra những bài mà chính mình tin tưởng. Tài liệu sẽ còn được cập nhật sau mỗi bài báo; nếu nó giúp một đồng nghiệp tránh được một vòng revise, hoặc giúp một nghiên cứu sinh dám báo cáo đúng những gì thí nghiệm cho thấy, thì nó đã làm xong việc của mình.

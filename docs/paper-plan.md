# Kế hoạch xuất bản + Outline — QIGOA reality-check paper

> Lập theo playbook IEEE của thầy Hảo (`docs/lam-va-viet-paper-chuan-IEEE.md`) — IMRaD chặt (§6.6),
> evaluation là phép thử bác bỏ (§6.3), công thức reframe Negative + Cautionary + Positive (§5.2),
> mọi số truy về CSV (§6.4). Nguồn ràng buộc: `CLAUDE.md §1` + `docs/preregistration.md`.
> Trạng thái dữ liệu: E2 (n=368) · E4 U-Net · P3 — **XONG**, số hết `[PLACEHOLDER]` (`docs/RESULTS.md`).

## 0. Cấu hình xuất bản (đã chốt từ CLAUDE.md §1 — không hỏi lại)

| Mục | Giá trị |
|---|---|
| **Tiêu đề (đóng góp trung thực, không người-hùng)** | *Optimizing the Wrong Variable: Structural Degeneracy in Multilevel Thresholding for Brain Tumor Segmentation* |
| **Loại bài** | Benchmark/measurement + tool + audit (hạng Q2), **KHÔNG bán như khám phá lý thuyết** |
| **Venue** | BSPC (chính, "trong bộ đồ benchmark paper") → ESWA (dự phòng) → Scientific Reports |
| **Citation** | Elsevier numbered (Vancouver-like) — dùng khung IEEE/numbered của skill |
| **Ngôn ngữ** | Thân bài English; abstract English (chính) + Vietnamese (cho thầy/luận văn). KHÔNG zh-TW |
| **Độ dài đích** | ~7.000 từ (khung BSPC) |
| **arXiv** | Đăng preprint ĐÚNG ngày nộp (Hegazy & Gabr ra 2 bài/tháng trên seam này) |

## 1. Luận đề duy nhất (bán cái này)

> *Trong miền có ground truth lâm sàng, khoảng cách tối ưu mà cả dòng văn liệu đang tranh nhau
> **KHÔNG chiếu xuống mask lâm sàng**.*

**Bất tử trước kết quả** (đúng cả hai nhánh) — và **cả hai nhánh đã xác nhận trên n=368**:
- Nhánh "không đạt tối ưu": hit_rate ≥ 0,99 bác bỏ **63/63** (tới 0,0000 ở k lớn).
- Nhánh "không chiếu xuống": Dice ≡ DP-exact, **median_diff = 0 cả 36 so sánh**, TOST δ=0,05 **100%**.

## 2. Ba đóng góp dương (KHÔNG có "exact solver" — Menotti 2015 đã in)

1. **Ceiling decomposition** (E4) — trần chỉ-cường-độ (oracle_levelset 0,8532) vs U-Net cùng input
   (0,9234) ⇒ phân rã gap: *"không có trong CƯỜNG ĐỘ"*, KHÔNG phải *"không có trong PIXEL"*. **Trụ chính.**
2. **Công cụ chẩn đoán O(L·log L)** — tính trước trần Dice của cả họ phương pháp trong micro-giây,
   TRƯỚC khi viết optimizer đầu tiên. Cite Lipton 2014 / RankSEG — **claim ứng dụng, KHÔNG claim toán học**.
3. **Checklist giao thức đánh giá** + **Bảng I trắc lượng có mã hoá** (2 coder, Cohen's κ). ⚠️ **CHƯA làm.**

## 3. Outline theo mục (IMRaD chặt) — mỗi claim ánh xạ CSV

### I. Introduction (~900 từ)
- Mở bằng nghịch lý, KHÔNG throat-clearing: một thập kỷ engineering tối ưu Kapur/Otsu bằng
  metaheuristic + quantum-inspired trên MRI u não; nhưng gần như không bài nào mở bộ mask BraTS tặng sẵn.
- Đóng góp **liệt kê rõ** (playbook §6.6): luận đề + 3 đóng góp dương.
- ⛔ Lằn ranh đỏ: KHÔNG "we establish the ceiling" (François & Tinarrage JMIV 2026 đã in 0,83±0,18);
  KHÔNG "quantum advantage"; KHÔNG "~250× faster".

### II. Related Work — định vị, KHÔNG liệt kê (~1.000 từ)
- Bốn cụm near-rival, mỗi cụm một câu phân biệt (đã web-verify, CLAUDE.md §1 bảng):
  Menotti 2015 (exact Kapur — ta chỉ *dùng*) · Hammouche 2010 + Mousavirad 2023 (so metaheuristic,
  không GT — ta có GT) · Lipton 2014/RankSEG (định lý level-set — ta *dùng*, không claim) ·
  François 2026 (trần trên BraTS — ta *phân rã*, không phát hiện) · Hegazy & Gabr 2026 (cùng seam) ·
  Fardo 2016 + Hegazy&Gabr metric-bias (PSNR sai — ta mở rộng sang miền GT lâm sàng).
- Định vị QIGOA: "EDA-flavoured PSO" (Platel 2009 QIEA=EDA + Harandi 2024 GOA=PSO).

### III. Problem Formulation — anti-toy, formulation cứng (~1.100 từ) — playbook §3.3
- Kapur multilevel thresholding hình thức hoá (tập/chỉ số/mục tiêu rõ).
- **Tách 2 tầng tường minh:** (a) tối ưu ngưỡng trên histogram; (b) **decoding** band→mask.
  Đây là đòn bẩy: cho thấy Dice sống ở tầng (b), optimizer sống ở tầng (a).
- Định nghĩa trần qua level-set (cite Lipton 2014 — Dice=F1, purity-prefix). Reference optimum = DP (Menotti).
- Threat model: include_zero_bg (nền cường-độ-0 ~65% lát skull-strip đổi HOÀN TOÀN ngưỡng ⇒ báo cáo CẢ HAI).

### IV. Experimental Protocol (~900 từ)
- Dữ liệu: BraTS 2020, **n=368**, split **cấp bệnh nhân** 5 fold (chống leakage, A3).
- Lưới: 2 target (wt_flair, et_t1ce) × 2 bg × 7 k × (9 metaheuristic × 5 seed + DP-exact + 5 classical)
  × 4 decode rule. **Equal-NFE budget=5000** tuyệt đối. Tổng 463.680 ô. ← `results/main/`
- Metric đầy đủ (chống cherry-pick): Dice + HD95 + NSD (đa-τ). Đơn vị = bệnh nhân.
- Thống kê: Wilcoxon, **TOST** (tương đương), Friedman+Nemenyi (CD), bootstrap CI n=10.000. ← `results/stats/`
- **Bảng I** — giao thức trắc lượng văn liệu 2 coder + Cohen's κ. ⚠️ chưa làm (xem §5 quyết định).

### V. Results — tổ chức thành CHUỖI PHÉP THỬ BÁC BỎ (playbook §6.3) (~1.800 từ)
- **V-A. Metaheuristic có đạt tối ưu Kapur không? → KHÔNG.** hit_rate bác bỏ 63/63. ← `pairwise` + B1
  (đây là *phép thử có thể làm sai* nhánh 1 của luận đề — nó không làm sai, nó xác nhận).
- **V-B. Gap tối ưu có chiếu xuống Dice không? → KHÔNG (luận đề).** TOST 100%, median_diff=0 cả 36.
  ← `tost.csv` + `pairwise.csv`. **Đây là Bảng II, trái tim bài.**
- **V-C. Ceiling decomposition → gap không nằm trong cường độ.** U-Net 0,9234 vs oracle 0,8532,
  Δ+0,0503 [CI 0,0413–0,0646], 293/368 BN, p=2,8e-32, rank-biserial 0,712. ← `family_a_superiority.csv`.
  **Bảng III + Hình 3.** ⚠️ chỉ wt_flair (xem §5 quyết định et_t1ce).
- **V-D. Goodhart trên trục k.** argmax bất đồng phổ quát 16/16 (PSNR chọn k=10 bằng cấu trúc Lloyd–Max;
  Dice chọn 2–3); chi phí do **decoding chi phối** (Δ 0,001–0,321). ← `p3_by_rule` + `p3_delta`.
  **Hình 4.** Báo cáo trung thực phần THẤT BẠI: ρ<−0,5 hỏng 16/16, dấu lật theo rule; mask rỗng ≈0.

### VI. Discussion (~900 từ)
- **Cơ chế (vì sao):** optimizer sống ở tầng histogram, Dice sống ở tầng decoding + cấu trúc không gian.
  morph phá trần WT (0,8672>0,8532) = bằng chứng dương "decoding chi phối".
- **Công cụ chẩn đoán O(L·log L):** đóng góp dương #2 — dùng được cho tác giả bất kỳ, dataset bất kỳ.
- **P1 viết thành THẾ LƯỠNG NAN** (không quy kết "văn liệu decode bằng lớp sáng nhất" — vi phạm IRON RULE 2).
- **Giới hạn (trung thực):** chỉ wt_flair cho U-Net; 1 seed U-Net; oracle là class C (dùng GT test) —
  phân rã THÔNG TIN, không phải "U-Net thắng baseline"; P3-secondary thất bại; construct-validity.

### VII. Conclusion (~400 từ)
- Hội tụ, không trôi dạt: ba phép thử độc lập cùng chỉ một hướng.
- KHÔNG over-claim. Trả về đúng luận đề duy nhất.

## 4. Hình & Bảng (mọi số sinh từ script, playbook §6.4)

| Đối tượng | Nguồn | Trạng thái |
|---|---|---|
| Hình 1 — sơ đồ 2 tầng (optimizer→ngưỡng→decoding→mask; gap sống ở đâu) | drawio/TikZ | cần vẽ |
| Hình 2 — CD diagram (Friedman–Nemenyi) | `results/stats/cd.csv` | có số |
| Hình 3 — ceiling decomposition (oracle vs U-Net vs classical, theo BN) | `ceiling` + `unet` | có số |
| Hình 4 — Goodhart: Dice(k) vs PSNR(k), argmax phân kỳ | `results/main/` | có số |
| **Bảng I** — trắc lượng văn liệu mã hoá (2 coder, κ) | coding thủ công | ⚠️ CHƯA |
| Bảng II — hit_rate + TOST tương đương (luận đề) | `pairwise` + `tost` | có số |
| Bảng III — ceiling decomposition | `family_a_superiority.csv` | có số |

## 5. Quyết định đã CHỐT (2026-07-22)

- **Q1 → HOÃN Bảng I.** Ship bài measurement + ceiling decomposition + Goodhart trước; Bảng I (trắc
  lượng mã hoá 2 coder + κ) để bản mở rộng/luận văn. Ưu tiên cắm cọc arXiv sớm. ⇒ Đóng góp dương #3 hạ
  còn **checklist giao thức đánh giá** (không kèm Bảng I mã hoá trong bản này).
- **Q2 → GIỮ wt_flair, HOÃN ET.** U-Net chỉ wt_flair; et_t1ce báo cáo trần oracle + classical, nói rõ
  Limitations. Không sửa `unet2d.py` trong vòng này.
- **Q3 → VIẾT Methods + Results TRƯỚC** (playbook: làm cứng bài toán + thực nghiệm trước, câu chuyện
  tự nổi lên), rồi Intro/Related/Discussion bọc sau.

## 6. Thứ tự draft (đã chốt Q3)
1. III. Problem Formulation → 2. IV. Experimental Protocol → 3. V. Results (4 phép thử bác bỏ)
4. VI. Discussion → 5. II. Related Work → 6. I. Introduction → 7. VII. Conclusion → 8. Abstract (EN+VI)

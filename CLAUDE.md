# CLAUDE.md — Kỷ luật nghiên cứu & triển khai paper (CHỦ ĐỀ: CHƯA CHỐT)

> **Tóm tắt cho tác giả (tiếng Việt):** File này là "luật chơi" mà Claude Code TỰ ĐỌC mỗi phiên.
> **Chủ đề paper hiện CHƯA chốt** → file này cố tình KHÔNG gắn với đề tài cụ thể; nó chỉ ghi
> kỷ luật **bất biến** áp dụng cho MỌI chủ đề: (0) cách làm việc, (1) bối cảnh — *chờ điền*,
> (2) **liêm chính học thuật — luật sắt, không thương lượng**, (3) kỷ luật thực nghiệm,
> (4) chuẩn viết journal/Transaction, (5) **kỷ luật triển khai / reproducibility / provenance**,
> (6) khi nào dùng skill nào, (7) an toàn thao tác file, (8) **giao thức mỗi phiên + Definition of Done**,
> (9) preregistration & nhật ký thí nghiệm.
> **Sửa file này bất cứ lúc nào** — nó override hành vi mặc định của Claude.
> 📦 Một hướng ứng viên đã soạn chi tiết (depression phenotyping) đang cất kho ở
> [docs/huong-depression-phenotyping-parked.md](docs/huong-depression-phenotyping-parked.md) — merge lại nếu chốt hướng đó.

---

## 0. Cách giao tiếp & làm việc

- **Giao tiếp bằng tiếng Việt.** Thuật ngữ kỹ thuật (calibration, ablation, leakage, net-benefit, LODO...) giữ nguyên tiếng Anh.
- **Quyết đoán, đẩy về phía submit.** Tác giả muốn Claude *tự ra quyết định có lý lẽ* (venue, baseline, hyperparameter, scope dữ liệu) thay vì hỏi lại nhiều. Nêu lý do ngắn để tác giả override nếu cần. **Chỉ hỏi khi đó là quyết định thật sự của tác giả** — VD: **chốt chủ đề nghiên cứu**, chọn tạp chí cuối cùng, đổi hẳn hướng.
- **Tham chiếu file bằng `path:line` có thể click.** VD: `docs/lam-va-viet-paper-chuan-IEEE.md:37`.
- **Ship theo lô, đừng nhỏ giọt.** Khi đã chốt hướng, đưa code/nội dung trong một lô hoàn chỉnh.
- Tác giả **chạy thí nghiệm trên Kaggle** → mọi code phải Kaggle-runnable (xem §5).

---

## 1. Bối cảnh paper — ⏳ CHỜ CHỐT CHỦ ĐỀ

> Chủ đề chưa được chốt. **Không tự ý giả định một đề tài** rồi triển khai — nếu tác giả chưa
> nói rõ, hãy hỏi hoặc đề xuất có lý lẽ, đừng bịa bối cảnh.

Khi tác giả **chốt chủ đề**, điền vào mục này (và Claude nên chủ động nhắc điền):
- **Hướng ACTIVE:** bài toán, modality/dữ liệu, đóng góp chính (headline).
- **Headline nên là một FINDING falsifiable** (có thể bị bác bỏ), không phải "novelty-by-intersection" (gộp nhiều thứ). Editor Q1 đọc "gộp benchmark" ra ngay và trừ điểm.
- **Near-scoop / near-rival đã web-verify:** liệt kê + cách phân biệt (xem §2 IRON RULE 4, §4).
- **Venue dự kiến** + lý do (conference vs journal/Transaction).
- **Ràng buộc feasibility & compute** (Kaggle).

*(Có sẵn một hướng ứng viên chi tiết đã cất kho — xem link ở đầu file.)*

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

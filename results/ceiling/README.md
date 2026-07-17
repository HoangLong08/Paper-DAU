# E4 — ceiling ladder + P5 (Bảng V · Hình 4)

> Nguồn dữ liệu: `brats`. Mỗi số truy về script sinh nó + `run-manifest.json` cùng thư mục (CLAUDE.md §5.3).

| file | nội dung |
|---|---|
| `raw.csv` | 1 hàng / (bệnh nhân, target, bg, method) — cột `method_class` |
| `qstar.csv` | **5 giá trị q\*** (một/fold) + learning curve theo cỡ tập fit |
| `summary.csv` | median [IQR] + 95% bootstrap CI theo bậc |

🔴 **Oracle = loại C, `uses test-time ground truth`** — KHÔNG phải phương pháp, là cận trên không đạt được. Nhãn này phải in ở MỌI bảng/hình.
🔴 **P5 = loại B** — chỉ đọc số **out-of-fold**. `q*` fit trên outer-train và đóng băng trước khi chạm test fold (A3).
⛔ CẤM "we establish the ceiling" (François & Tinarrage, JMIV 2026) · CẤM claim định lý level-set (Lipton et al. 2014 / RankSEG 2023) — claim **ứng dụng**.

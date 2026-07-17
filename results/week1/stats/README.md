# E6 — thống kê (đơn vị: BỆNH NHÂN)

> Nguồn dữ liệu: `brats`. Mỗi số truy về script sinh nó + `run-manifest.json` cùng thư mục (CLAUDE.md §5.3).

| file | family | nội dung |
|---|---|---|
| `pairwise.csv` | C/D | Wilcoxon **pratt** + rank-biserial + **`n_zero/n_total`** |
| `tost.csv` | C | 90% CI + **`delta_ach`** + 3 bound hierarchy — KHÔNG pass/fail |
| `bayes.csv` | C | Bayesian signed-rank + ROPE — **PRIMARY** |
| `cd.csv` | D | Friedman + Nemenyi + CD → Hình 2 |
| `p3_delta.csv` | B | Δᵢ per-patient (primary) + Spearman per-patient (secondary), Holm trong family |
| `p2c_decoupling.csv` | D | Spearman(gap_fitness, \|ΔDice\|) — dự đoán ≈ 0 |
| `family_a_superiority.csv` | A | U-Net vs oracle level-set (1 test) |

Khoá: k primary = **4** · decoding primary = **`brightest`** · reference = **`DP-exact`** · SESOI = **0.01** · ROPE = **[-0.01, 0.01]**.

**Cách đọc (A4c):** *đừng* đọc "TOST pass/fail", đọc **`delta_ach`** — *"Equivalence holds for any SESOI ≥ delta_ach"*. Bayesian ROPE là primary.

⚠️ **A3 caveat cho P3:** `k*` per-patient trong primary là một lựa chọn **oracle** cho CẢ HAI thước đo (đúng như A4a viết) ⇒ nó đo *chi phí của việc chọn k bằng PSNR*, KHÔNG phải hiệu năng của một pipeline triển khai được. Nếu bản thảo dùng "chọn k" như một **phương pháp**, nó là loại B ⇒ phải chấm **out-of-fold**.

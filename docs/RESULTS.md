# RESULTS.md — Provenance ledger + nhật ký thí nghiệm (append-only)

**Trạng thái:** ⬜ **CHƯA CHẠY THÍ NGHIỆM THẬT NÀO.** Mọi ô trong bảng dưới đây là `[PLACEHOLDER]`.

> **File này vận hành IRON RULE 1 & 3 (CLAUDE.md §2, §5.3).**
>
> - **IRON RULE 1 — KHÔNG bịa số.** Mọi con số trong `paper/` phải truy được về một ô CSV trong `results/`, qua đúng một dòng provenance dưới đây.
> - **IRON RULE 3 — Số chưa có dòng provenance = `[PLACEHOLDER]`.** Không bao giờ âm thầm "thăng cấp" placeholder thành kết quả thật.
> - **Luật APPEND-ONLY (CLAUDE.md §9).** Chỉ được **thêm** dòng. **Không xoá run xấu** — run âm là dữ liệu. Mỗi run một dòng nhật ký: ngày tuyệt đối · commit · config · seed · tóm tắt · kết luận.
> - **Số flow một chiều:** `configs/ → scripts/ → results/ → paper/`. Bảng & hình trong `paper/` được **sinh** bởi `build_tables.py` / `build_figures.py`, **không gõ tay**.
> - **KHÔNG tái dùng số từ commit `c4fe108`** (bug NFE 13,4%, GOA hit-rate 0%, metric tự chế, pseudo-replication). Nó là bằng chứng chẩn đoán, không phải nguồn số liệu.

---

## 1. Bảng provenance — mỗi Bảng/Hình một dòng (ke-hoach-trien-khai §3)

Luật: một số được phép vào bản thảo **chỉ khi** dòng của nó ở trạng thái không còn ⬜, và cột `@commit` + `seeds` đã điền thật.

| Bảng/Hình (paper) | ← results/<path> | ← script | seeds | @commit | Trạng thái |
|---|---|---|---|---|---|
| **Bảng I** — trắc lượng thư mục (→ Supplementary) | *(khảo sát tay, 2 coder + Cohen's κ)* | *thủ công + PRISMA-lite* | — | — | ⬜ `[PLACEHOLDER]` chưa làm |
| **Bảng II** — DP vs vét cạn (bit-exact) | `results/exact/dp_vs_bruteforce.csv` | `scripts/run_exact_check.py` | — | — | ⬜ `[PLACEHOLDER]` |
| **Bảng III** — gap-to-optimum, hit-rate, NFE, runtime | `results/main/summary.csv` | `scripts/run_main_grid.py` | {0..4} | — | ⬜ `[PLACEHOLDER]` |
| **Bảng IV** — ablation QIGOA (full / −quantum / −memetic / −OBL / −Lévy / PSO+memetic) | `results/ablation/summary.csv` | `scripts/run_ablation.py` | {0..4} | — | ⬜ `[PLACEHOLDER]` |
| **Bảng V** — phương pháp đề xuất vs 7 metaheuristic (nested CV) | `results/ceiling/summary.csv` | `scripts/run_ceiling.py` | {0..2}×5fold | — | ⬜ `[PLACEHOLDER]` |
| **Hình 1** — sơ đồ pipeline + ngân sách NFE | — | drawio-skill (thủ công) | — | — | ⬜ `[PLACEHOLDER]` |
| **Hình 2** — Critical Difference diagram | `results/stats/cd.csv` | `scripts/run_stats.py` | {0..4} | — | ⬜ `[PLACEHOLDER]` |
| **Hình 3** — Goodhart (trục kép: fitness/PSNR ↑ vs Dice/HD95 ↓ theo k) | `results/main/summary.csv` | `scripts/build_figures.py` | {0..4} | — | ⬜ `[PLACEHOLDER]` |
| **Hình 4** — Ceiling ladder ★ | `results/ceiling/` + `results/unet/` | `scripts/build_figures.py` | {0..2} | — | ⬜ `[PLACEHOLDER]` |
| **Supp.** — external replication (LGG / task-axis) | `results/external/summary.csv` | `scripts/run_external.py` | {0..4} | — | ⬜ `[PLACEHOLDER]` |
| **Supp.** — empty-mask rate theo k (A7) | `results/main/summary.csv` | `scripts/build_figures.py` | {0..4} | — | ⬜ `[PLACEHOLDER]` |
| **Supp.** — convergence curve + boxplot per-seed (A6) | `results/main/raw.csv` | `scripts/build_figures.py` | {0..4} | — | ⬜ `[PLACEHOLDER]` |

---

## 2. Cổng cứng — trạng thái (phải PASS trước khi số ở mục 1 được coi là thật)

| Cổng | Test / script | Điều kiện | Trạng thái |
|---|---|---|---|
| Bit-exact DP vs vét cạn | `tests/test_exact_dp.py` + E1 | `|f_DP−f_brute| ≤ 1e-9` **và** mask cảm sinh giống hệt (ngưỡng canonicalise, A5a) | ⬜ chưa chạy |
| NFE bằng nhau (±0) | `tests/test_nfe_budget.py` | mọi thuật toán tiêu thụ đúng cùng NFE | ⬜ chưa chạy |
| Suy biến P1 (unit test số học, KHÔNG phải Result) | `tests/test_degeneracy.py` | nhóm theo **mask hash** ⇒ std(Dice)=0 (A1) | ⬜ chưa chạy |
| Đúng-đắn implementation (E1b, A6) | tái tạo bảng Kapur/Otsu đã công bố (Lena/Cameraman…) | khớp trong X% ở đúng NFE công bố | ⬜ chưa chạy |

---

## 3. Nhật ký thí nghiệm (append-only)

*(Mỗi run một dòng. Ngày tuyệt đối · commit · config · seeds · kết quả tóm tắt · kết luận. Không xoá.)*

> **CHƯA CÓ RUN NÀO.** Dòng đầu tiên sẽ được thêm sau khi cổng bit-exact (E1) chạy trên Kaggle.

<!-- MẪU dòng (điền khi có run thật — xoá comment này khi thêm dòng đầu):
- **2026-MM-DD** · `@<commit>` · `configs/exp_main.yaml` · seeds {0..4} · E1 bit-exact: DP khớp vét cạn 20/20 ảnh @k=2,3 (max |Δf|=<...>). Cổng PASS → được phép chạy E1b.
-->

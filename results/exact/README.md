# E1 — DP vs brute force (Bảng II)

> Nguồn dữ liệu: `brats`. Mỗi số truy về script sinh nó + `run-manifest.json` cùng thư mục (CLAUDE.md §5.3).

| | |
|---|---|
| Script | `scripts/run_exact_check.py` |
| Config | `configs/exp_main.yaml` |
| Tiêu chí PASS (A5a) | `\|f_DP − f_brute\| <= 1e-09` **VÀ** mask cảm sinh giống hệt sau canonicalise |
| Số ô | 160 |
| Số FAIL | 0 |
| Thời gian | 2077.5 s |

Cột `brute_over_dp` = t_brute / t_DP (chênh bậc độ lớn). ⚠️ **KHÔNG** dùng nó để claim tốc độ: đồng tiền chính của bài là **NFE + độ phức tạp**, wall-clock chỉ là phụ (A0). Và **KHÔNG** claim DP là đóng góp — Menotti et al., CIARP 2015.

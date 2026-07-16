"""MODULE E — trắc lượng (metrics) + thống kê (stats) cho pipeline QIGOA Reality-Check.

Đây là tầng ĐO của bài: mọi con số trong bản thảo đi qua đây. Vì bài này *đi tố cáo*
người khác đo sai và so sánh không lành mạnh, mọi quy ước ở tầng này phải được **khoá
trước khi chạy** (docs/preregistration.md §6/A4 + A7) và **mọi implementation phải có
tên** — cấm implementation vô danh kiểu "FSIM tự chế" của lô cũ (A7).

Giao diện CHUNG (hợp đồng liên-module):

    from src.eval.metrics import (
        dice, hd95, nsd, n_connected_components, psnr, ssim, empty_mask_rate,
    )
    from src.eval.stats import (
        wilcoxon_signed, friedman_nemenyi, tost, bayesian_signed_rank,
        one_sample_wilcoxon_delta, bootstrap_ci,
    )

Quy ước khoá (tóm tắt — chi tiết ở docstring từng hàm):
  * mask là ``np.ndarray`` kiểu bool. L = 256 mức xám.
  * Dice cả hai rỗng ⇒ 1.0; GT≠rỗng & pred rỗng ⇒ 0.0 (A7).
  * HD95 GT≠rỗng & pred rỗng ⇒ hình phạt cố định = đường chéo ảnh; cả hai rỗng ⇒ 0.0 (A7).
  * NSD τ = 2 mm primary (A7). BraTS in-plane 1 mm isotropic.
  * Wilcoxon zero_method="pratt" mặc định — KHÔNG vứt các cặp bằng 0 (A4d).
  * Equivalence: Bayesian signed-rank + ROPE là PRIMARY; TOST (90% CI) là companion (A4c).
  * BỎ IoU (song ánh với Dice) và FSIM (A7).
"""

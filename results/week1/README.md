# E2 — lưới chính equal-NFE

> Nguồn dữ liệu: `brats`. Mỗi số truy về script sinh nó + `run-manifest.json` cùng thư mục (CLAUDE.md §5.3).

| file | nội dung |
|---|---|
| `raw.csv` | 1 hàng / (bệnh nhân, target, bg, k, method, seed, decode_rule) |
| `summary.csv` | median [IQR] + 95% bootstrap CI của Dice (A7), gap, hit-rate, NFE, runtime, **empty-mask rate**, PSNR/SSIM |
| `mask_identity.csv` | **A0 headline** — % ô mà MỌI metaheuristic sinh mask giống hệt từng byte |

Quy ước sentinel: `k = -1`, `seed = -1`, `include_zero_bg = na` ⇒ không áp dụng (baseline cổ điển không có k; DP-exact tất định nên không có seed).

⚠️ `runtime_s` KHÔNG được dùng để claim tốc độ — đồng tiền chính là **NFE + độ phức tạp** (A0). ⚠️ PSNR/SSIM là **bằng chứng cho P3**, không phải kết quả.

# E4 — 2D U-Net (bậc 8 của Hình 4)

> Nguồn dữ liệu: `brats`. Mỗi số truy về script sinh nó + `run-manifest.json` cùng thư mục (CLAUDE.md §5.3).

5 fold × ≥3 seed, out-of-fold only (A3). Fold chạy: [0, 1, 2, 3, 4], seed: [0].

**Cùng input** = 1 lát FLAIR lúc **inference**; train dùng mọi lát có u của bệnh nhân outer-train ⇒ vô hiệu hoá phản biện *"anh so 2D đơn-modality với 3D đa-modality"* mà không tạo confound thiếu dữ liệu.



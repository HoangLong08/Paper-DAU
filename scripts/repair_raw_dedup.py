"""Dọn dòng LẶP trong results/*/raw.csv do lỗi `--resume` trượt khoá (2026-07-19).

BỐI CẢNH (một lần, không phải công cụ dùng thường xuyên)
--------------------------------------------------------
`read_results_csv` từng gọi `pd.read_csv(..., comment="#")` với `low_memory=True`
(mặc định của pandas) ⇒ dtype được suy diễn THEO TỪNG KHỐI. Khi raw.csv đủ lớn, một
khối chỉ chứa `true`/`false` ở cột `include_zero_bg` bị đọc thành **bool**, nên
`str(v)` trả `'True'` thay vì `'true'`. Hậu quả: `done_keys()` trượt khoá ⇒ ô đã
tính bị tính LẠI và append thêm một lần nữa.

Bản vá gốc nằm ở `_common.read_results_csv` (ép `dtype=str` cho ID_COLS +
`low_memory=False`). Script này chỉ dọn HẬU QUẢ đã ghi ra đĩa.

AN TOÀN
-------
Chỉ bỏ dòng trùng trên khoá đầy đủ (KEY_COLS + decode_rule) và **chỉ khi** mọi bản
sao khớp bit-for-bit trên toàn bộ cột số đo. Nếu có bất kỳ khoá nào mà các bản sao
BẤT ĐỒNG giá trị ⇒ DỪNG và báo lỗi: đó không còn là trùng lặp vô hại mà là mất tính
tất định, phải điều tra chứ không được lặng lẽ bỏ bớt (IRON RULE 3).

Bản gốc luôn được giữ lại ở `<raw>.bak-<timestamp>` trước khi ghi đè.
"""
from __future__ import annotations

import argparse
import shutil
import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import read_results_csv  # noqa: E402
from run_main_grid import KEY_COLS  # noqa: E402

# Cột KHÔNG dùng để so khớp: thời gian chạy khác nhau giữa hai lần tính là bình thường.
VOLATILE = {"runtime_s"}


def repair(raw_path: Path, apply: bool) -> int:
    df = read_results_csv(raw_path)
    if df.empty:
        print(f"{raw_path}: rỗng, bỏ qua.")
        return 0

    full_key = [c for c in KEY_COLS + ["decode_rule"] if c in df.columns]
    if len(full_key) < len(KEY_COLS) + 1:
        print(f"{raw_path}: thiếu cột khoá {set(KEY_COLS + ['decode_rule']) - set(df.columns)}, bỏ qua.")
        return 0

    dup_mask = df.duplicated(full_key, keep=False)
    n_dup_rows = int(dup_mask.sum())
    if n_dup_rows == 0:
        print(f"{raw_path}: KHÔNG có dòng lặp ({len(df)} dòng). Không cần sửa.")
        return 0

    # Cổng an toàn: mọi bản sao phải khớp trên mọi cột số đo.
    dup = df[dup_mask]
    compare = [c for c in df.columns if c not in full_key and c not in VOLATILE]
    disagree = [c for c in compare if (dup.groupby(full_key)[c].nunique(dropna=False) > 1).any()]
    if disagree:
        raise SystemExit(
            f"DỪNG: các bản sao BẤT ĐỒNG ở cột {disagree}.\n"
            "Đây KHÔNG phải trùng lặp vô hại — tính tất định đã hỏng. Phải điều tra "
            "trước khi dọn (IRON RULE 3)."
        )

    kept = df.drop_duplicates(full_key, keep="first")
    n_removed = len(df) - len(kept)
    print(f"{raw_path}:")
    print(f"  dòng hiện có   : {len(df)}")
    print(f"  dòng lặp       : {n_removed} (mọi bản sao khớp bit-for-bit trên {len(compare)} cột số đo)")
    print(f"  còn lại sau dọn: {len(kept)}")

    if not apply:
        print("  → chạy thử (chưa ghi). Thêm --apply để thực hiện.")
        return n_removed

    banner = [ln for ln in raw_path.read_text(encoding="utf-8", errors="replace").splitlines()
              if ln.startswith("#")]
    bak = raw_path.with_suffix(raw_path.suffix + f".bak-{time.strftime('%Y%m%d_%H%M%S')}")
    shutil.copy2(raw_path, bak)
    with open(raw_path, "w", encoding="utf-8", newline="") as fh:
        for ln in banner:
            fh.write(ln + "\n")
        kept.to_csv(fh, index=False)
    print(f"  → ĐÃ GHI. Bản gốc giữ tại {bak.name}")
    return n_removed


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("raw", nargs="+", type=Path, help="đường dẫn tới raw.csv")
    ap.add_argument("--apply", action="store_true",
                    help="thực sự ghi đè (mặc định chỉ chạy thử)")
    args = ap.parse_args()
    total = sum(repair(p, args.apply) for p in args.raw)
    print(f"\nTổng dòng lặp: {total}")


if __name__ == "__main__":
    main()

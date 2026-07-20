"""Cổng kiểm E2 — chạy TRƯỚC khi bất kỳ con số nào rời `results/` để vào bản thảo.

Chỉ ĐỌC, không sửa gì. Vận hành CLAUDE.md §8 (Definition of Done) thành lệnh chạy được.

Hai LOẠI kiểm, phân biệt dứt khoát vì cách xử lý ngược nhau:

**A. TOÀN VẸN (A1–A4)** — hỏng ⇒ **lỗi kỹ thuật, phải SỬA rồi chạy lại.** Số không được
   dùng. Thoát với mã 1.

**B. CHỐT AN TOÀN PREREGISTER (B1–B2)** — "nổ" ⇒ **KHÔNG phải bug.** Đó là kết quả thực
   nghiệm đang bác bỏ một mệnh đề ta đã đăng ký trước. Xử lý đúng là **REFRAME TRUNG THỰC**
   (CLAUDE.md §3 "hội tụ, không trôi dạt"; §9 "run âm là dữ liệu"), TUYỆT ĐỐI không sửa
   ngưỡng cho khớp kết quả — làm thế là HARKing, đúng thứ bài này sinh ra để tố cáo.
   Vì vậy B1/B2 **không bao giờ** làm script thoát khác 0; chúng chỉ BÁO CÁO.

   - **B1** `hit_rate ≥ 0,99` cho mọi thuật toán ở mọi k (P2). Hammouche, Diaf & Siarry
     (EAAI 2010) đã thấy ACO/SA **không** đạt tối ưu khi k>2 ⇒ ngưỡng này có thể tự bác bỏ.
   - **B2** Trần oracle cường độ (P4). Ở lô screening, decode `morph` **vượt**
     `oracle_levelset` trên WT/FLAIR ⇒ oracle KHÔNG phải trần của pipeline thật. Nếu tái
     lập ở n=368 thì mọi câu dạng "we establish the ceiling" phải bị xoá (đằng nào cũng
     đã bị cấm bởi François & Tinarrage, JMIV 2026).

Dùng: python scripts/audit_e2.py [--raw ...] [--config ...] [--splits ...] [--ceiling ...]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import read_results_csv  # noqa: E402
from run_main_grid import KEY_COLS  # noqa: E402

FULL_KEY = KEY_COLS + ["decode_rule"]
OK, BAD, INFO = "  [OK]  ", "  [FAIL]", "  [!]   "
_fails: list[str] = []


def _fail(msg: str) -> None:
    _fails.append(msg)
    print(BAD + " " + msg)


# --------------------------------------------------------------------------- #
# A. TOÀN VẸN
# --------------------------------------------------------------------------- #
def a1_grid_complete(meta: pd.DataFrame, cfg: dict, n_pat: int) -> None:
    print("\nA1 — ĐỦ LƯỚI (mỗi k phải có n×target×bg×algo×seed ô)")
    k_list = [int(k) for k in cfg["k_list"]]
    seeds = [int(s) for s in cfg["seeds"]]
    expect = n_pat * len(cfg["targets"]) * len(cfg["include_zero_bg"]) \
        * len(cfg["optimizers"]) * len(seeds)
    for k in k_list:
        got = meta[meta["k"] == k].drop_duplicates(KEY_COLS).shape[0]
        line = f"k={k:<3} {got:>7} / {expect}"
        if got == expect:
            print(OK + line + "  ĐỦ")
        else:
            _fail(f"{line}  THIẾU {expect - got} ô" if got < expect
                  else f"{line}  THỪA {got - expect} ô (nghi trùng khoá)")

    # Mỗi ô thí nghiệm phải có ĐÚNG đủ seed — thiếu seed lẻ tẻ sẽ làm lệch median.
    g = meta.groupby(["k", "target", "include_zero_bg", "method"])["seed"].nunique()
    bad = g[g != len(seeds)]
    if bad.empty:
        print(OK + f"mọi (k,target,bg,method) đều có đủ {len(seeds)} seed")
    else:
        _fail(f"{len(bad)} tổ hợp KHÔNG đủ {len(seeds)} seed, VD: {bad.head(3).to_dict()}")


def a2_no_duplicates(df: pd.DataFrame) -> None:
    print("\nA2 — KHÔNG dòng lặp trên khoá đầy đủ")
    n_dup = int(df.duplicated(FULL_KEY).sum())
    if n_dup == 0:
        print(OK + f"0 dòng lặp / {len(df)} dòng")
    else:
        _fail(f"{n_dup} dòng lặp -> chạy scripts/repair_raw_dedup.py --apply")


def a3_summary_integrity(summary_path: Path, algos: list[str], n_pat: int) -> None:
    print(f"\nA3 — TOÀN VẸN summary.csv (mỗi nhóm phải có n_patients = {n_pat})")
    if not summary_path.exists():
        _fail(f"không có {summary_path} -> chưa sinh summary")
        return
    s = read_results_csv(summary_path)
    bgs = sorted(s["include_zero_bg"].astype(str).unique())
    if any(b not in ("true", "false", "na") for b in bgs):
        _fail(f"include_zero_bg có giá trị lạ {bgs} -> nhóm bị TÁCH (lỗi dtype đã vá ở "
              "9c2f4e4; summary này sinh bằng code CŨ, phải sinh lại)")
    else:
        print(OK + f"include_zero_bg = {bgs}")

    meta = s[s["method"].isin(algos)]
    bad = meta[pd.to_numeric(meta["n_patients"], errors="coerce") != n_pat]
    if bad.empty:
        print(OK + f"cả {len(meta)} nhóm metaheuristic đều có n_patients = {n_pat}")
    else:
        _fail(f"{len(bad)} nhóm có n_patients != {n_pat} (VD "
              f"{bad.iloc[0][['target', 'include_zero_bg', 'k', 'method']].to_dict()} "
              f"-> n={bad.iloc[0]['n_patients']}). Đây ĐÚNG là lỗi đã suýt đưa số sai "
              "vào Bảng III.")


def a4_leakage(splits_dir: Path, cohort: set[str]) -> None:
    print("\nA4 — LEAKAGE / split cấp bệnh nhân")
    folds = sorted(splits_dir.glob("fold_*.json"))
    if not folds:
        _fail(f"không thấy fold_*.json trong {splits_dir}")
        return
    tests, seen_unit = [], set()
    for f in folds:
        d = json.load(open(f, encoding="utf-8"))
        seen_unit.add(d.get("split_unit"))
        tr, te = set(d["train"]), set(d["test"])
        va = set(d.get("val", []))
        for a, b, nm in ((tr, te, "train∩test"), (tr, va, "train∩val"), (va, te, "val∩test")):
            if a & b:
                _fail(f"{f.name}: {nm} chồng lấn {len(a & b)} bệnh nhân")
        tests.append(te)

    if seen_unit == {"patient"}:
        print(OK + "split_unit = patient (đúng cấp bệnh nhân)")
    else:
        _fail(f"split_unit = {seen_unit} (phải là 'patient')")

    for i in range(len(tests)):
        for j in range(i + 1, len(tests)):
            if tests[i] & tests[j]:
                _fail(f"test fold {i} ∩ fold {j} chồng lấn {len(tests[i] & tests[j])} ca")
    union = set().union(*tests)
    if union == cohort:
        print(OK + f"{len(folds)} test-fold rời nhau, hợp lại = đúng cohort {len(cohort)} ca")
    else:
        _fail(f"hợp test-fold ({len(union)}) != cohort ({len(cohort)}); "
              f"thiếu {len(cohort - union)}, thừa {len(union - cohort)}")


# --------------------------------------------------------------------------- #
# B. CHỐT AN TOÀN PREREGISTER — chỉ báo cáo, KHÔNG BAO GIỜ làm fail
# --------------------------------------------------------------------------- #
def b1_hit_rate(meta: pd.DataFrame, thr: float = 0.99) -> None:
    print(f"\nB1 — [PREREG P2] hit_rate ≥ {thr} cho MỌI thuật toán ở MỌI k?")
    if "hit" not in meta.columns:
        print(INFO + "không có cột 'hit' -> bỏ qua")
        return
    d = meta.drop_duplicates(KEY_COLS).copy()
    d["hit"] = pd.to_numeric(d["hit"], errors="coerce")
    hr = d.groupby(["k", "method"])["hit"].mean().dropna()
    if hr.empty:
        print(INFO + "không tính được hit_rate")
        return
    viol = hr[hr < thr].sort_values()
    print(f"        hit_rate thấp nhất = {hr.min():.4f}; số (k,method) < {thr}: {len(viol)}/{len(hr)}")
    if viol.empty:
        print(OK + "ngưỡng preregister GIỮ ĐƯỢC trên toàn lưới.")
        return
    print(INFO + "NGƯỠNG PREREGISTER BỊ BÁC BỎ — đây là KẾT QUẢ, không phải bug.")
    print("        10 vi phạm nặng nhất (k, method) -> hit_rate:")
    for (k, m), v in viol.head(10).items():
        print(f"          k={k:<3} {m:<12} {v:.4f}")
    print("        ⇒ Hammouche, Diaf & Siarry (EAAI 2010) đã thấy đúng hiện tượng này ở k>2.")
    print("        ⇒ Xử lý: REFRAME theo prereg §6, TUYỆT ĐỐI không hạ ngưỡng cho khớp (HARKing).")


def b2_ceiling(meta: pd.DataFrame, ceiling_path: Path) -> None:
    print("\nB2 — [PREREG P4] decode 'morph' có VƯỢT trần oracle không?")
    if not ceiling_path.exists():
        print(INFO + f"không có {ceiling_path} -> bỏ qua")
        return
    c = read_results_csv(ceiling_path)
    orc = c[c["method"] == "oracle_levelset"].set_index("target")["dice_median"]
    mor = meta[meta["decode_rule"] == "morph"].copy()
    if mor.empty:
        print(INFO + "không có dòng decode_rule='morph' -> bỏ qua")
        return
    mor["dice"] = pd.to_numeric(mor["dice"], errors="coerce")
    best = mor.groupby(["target", "k", "method"])["dice"].median().reset_index()
    for tgt, ceil in orc.items():
        sub = best[best["target"] == tgt]
        if sub.empty:
            continue
        top = sub.loc[sub["dice"].idxmax()]
        over = sub[sub["dice"] > float(ceil)]
        print(f"        {tgt}: oracle_levelset = {float(ceil):.4f} | morph tốt nhất = "
              f"{top['dice']:.4f} (k={int(top['k'])}, {top['method']})")
        if over.empty:
            print(OK + f"{tgt}: không cấu hình morph nào vượt trần.")
        else:
            print(INFO + f"{tgt}: {len(over)}/{len(sub)} cấu hình morph VƯỢT trần oracle "
                         "— P4 dạng 'we establish the ceiling' TỰ BÁC BỎ (đây là KẾT QUẢ).")


# --------------------------------------------------------------------------- #
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", type=Path, default=Path("results/main/raw.csv"))
    ap.add_argument("--summary", type=Path, default=Path("results/main/summary.csv"))
    ap.add_argument("--config", type=Path, default=Path("configs/exp_main.yaml"))
    ap.add_argument("--splits", type=Path, default=Path("data/splits"))
    ap.add_argument("--ceiling", type=Path, default=Path("results/ceiling/summary.csv"))
    args = ap.parse_args()

    cfg = yaml.safe_load(open(args.config, encoding="utf-8"))
    algos = list(cfg["optimizers"])
    cohort_csv = args.splits / "brats_cohort.csv"
    cohort = set(pd.read_csv(cohort_csv)["patient_id"].astype(str)) if cohort_csv.exists() else set()

    df = read_results_csv(args.raw)
    if df.empty:
        sys.exit(f"KHÔNG đọc được {args.raw}")
    df["k"] = pd.to_numeric(df["k"], errors="coerce")
    meta = df[df["method"].isin(algos)]

    print("=" * 74)
    print(f"CỔNG KIỂM E2 — {args.raw} ({len(df)} dòng, cohort {len(cohort)} ca)")
    print("=" * 74)

    a1_grid_complete(meta, cfg, len(cohort))
    a2_no_duplicates(df)
    a3_summary_integrity(args.summary, algos, len(cohort))
    a4_leakage(args.splits, cohort)
    b1_hit_rate(meta)
    b2_ceiling(meta, args.ceiling)

    print("\n" + "=" * 74)
    if _fails:
        print(f"KẾT LUẬN: {len(_fails)} kiểm TOÀN VẸN THẤT BẠI -> số CHƯA được rời results/.")
        for m in _fails:
            print("  - " + m)
        sys.exit(1)
    print("KẾT LUẬN: mọi kiểm TOÀN VẸN (A1–A4) PASS.")
    print("Các mục B ở trên là KẾT QUẢ THỰC NGHIỆM về mệnh đề đã preregister,")
    print("không phải lỗi — đọc kỹ trước khi viết một chữ nào của phần Results.")


if __name__ == "__main__":
    main()

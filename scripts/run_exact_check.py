"""E1 — CỔNG CỨNG: bộ giải DP vs vét cạn.  → Bảng II

    python scripts/run_exact_check.py --config configs/exp_smoke.yaml   # plumbing
    python scripts/run_exact_check.py --config configs/exp_main.yaml    # cổng thật

Đối chiếu `solve_exact` (DP, O(k·L²)) với `solve_bruteforce` tại k=2,3 trên >= 20 ảnh.

**Tiêu chí PASS (A5a — đã sửa từ "bit-exact", vì bit-exact SẼ FAIL VÌ LÝ DO VÔ NGHĨA):**
  * ``|f_DP − f_brute| <= tol`` (mặc định 1e-9) — dấu phẩy động cộng theo thứ tự khác
    nhau ⇒ khác bit, điều đó KHÔNG có nghĩa DP sai; VÀ
  * mask cảm sinh **giống hệt** sau khi canonicalise ngưỡng (snap về mức xám thấp nhất
    cho cùng phân hoạch). Lát BraTS đã skull-strip ⇒ ~65% pixel ở cường độ 0 và nhiều
    mức xám RỖNG ⇒ dưới quy ước 0·log0 := 0, **argmax của Kapur KHÔNG DUY NHẤT**.

FAIL ⇒ in "DỪNG TOÀN BỘ" và exit code != 0. Mọi kết luận về P2 dựng trên bộ giải này;
nếu nó sai thì không được chạy gì thêm (prereg §1/P2 "bảo hiểm bắt buộc", §4 cờ đỏ (d)).

⚠️ KHÔNG claim DP là đóng góp của mình — Menotti, Najman & de A. Araújo (CIARP 2015) đã
in exact Kapur O((K−1)L²) <160 ms, 11 năm trước. Bảng II là một bảng TOÁN HỌC (kiểm
chứng bộ giải), không buộc tội ai — và vì thế nó là Bảng I của bản thảo (§4 quyết định
đóng khung 3).
"""

from __future__ import annotations

import sys
import time

import numpy as np

from _common import (
    CsvAppender,
    data_source,
    decode_rows,  # noqa: F401  (giữ import đối xứng với các script khác)
    done_keys,
    hist_cached,
    iter_slices,
    key_of,
    load_config,
    make_fitness,
    parse_args,
    resolve_output_dir,
    section,
    set_all_seeds,
    target_arrays,
    write_readme,
    write_run_manifest,
)
from src.decode.decoding import label_map, mask_hash
from src.solvers.exact_dp import solve_exact
from src.solvers.exhaustive import solve_bruteforce

FIELDS = [
    "patient_id", "target", "include_zero_bg", "k",
    "f_dp", "f_brute", "abs_diff", "rel_diff",
    "thr_dp", "thr_brute", "thr_identical",
    "mask_hash_dp", "mask_hash_brute", "mask_identical", "labelmap_identical",
    "t_dp_s", "t_brute_s", "brute_over_dp",
    "pass", "data_source", "placeholder",
]

KEY_COLS = ["patient_id", "target", "include_zero_bg", "k"]


def main() -> int:
    args = parse_args(__doc__.splitlines()[0]).parse_args()
    cfg, cfg_hash = load_config(args.config)
    scfg = section(cfg, "exact_check")
    out_dir = resolve_output_dir(scfg, args.output, "results/exact")
    csv_path = out_dir / "dp_vs_bruteforce.csv"

    n_images = int(scfg.get("n_images", 20))
    k_list = [int(k) for k in scfg.get("k_list", [2, 3])]
    tol = float(scfg.get("tol", 1e-9))
    targets = list(scfg.get("targets", ["wt_flair"]))
    bgs = scfg.get("include_zero_bg", [True, False])
    bgs = [bgs] if isinstance(bgs, bool) else list(bgs)
    fitness_name = str(scfg.get("fitness", "kapur"))
    cache_dir = out_dir / "cache"

    set_all_seeds(int((cfg.get("seeds") or [0])[0]))

    if n_images < 20:
        print(f"[WARN] n_images={n_images} < 20 — cổng E1 yêu cầu >= 20 ảnh "
              f"(prereg §1/P2). Đang chạy dưới chuẩn, KHÔNG được coi là cổng đã qua.")

    done = done_keys(csv_path, KEY_COLS, args.resume)
    n_fail = 0
    n_rows = 0
    t_start = time.perf_counter()

    with CsvAppender(csv_path, FIELDS, "run_exact_check.py", cfg, resume=args.resume,
                     note="E1 gate: |f_DP - f_brute| <= tol AND identical induced mask "
                          "after canonicalisation (prereg A5a).") as w:
        for sl in iter_slices(cfg, limit=n_images):
            for target in targets:
                img, _gt = target_arrays(sl, target)
                for bg in bgs:
                    hist = hist_cached(cache_dir, sl, target, bool(bg))
                    if hist.sum() <= 0:
                        print(f"[SKIP] {sl.patient_id}/{target}/bg={bg}: histogram rỗng")
                        continue
                    fit = make_fitness(hist, fitness_name)
                    for k in k_list:
                        row_key = {"patient_id": sl.patient_id, "target": target,
                                   "include_zero_bg": str(bool(bg)).lower(), "k": k}
                        if key_of(row_key, KEY_COLS) in done:
                            continue

                        t0 = time.perf_counter()
                        thr_dp, f_dp = solve_exact(fit, k)
                        t_dp = time.perf_counter() - t0

                        t0 = time.perf_counter()
                        thr_bf, f_bf = solve_bruteforce(fit, k)
                        t_bf = time.perf_counter() - t0

                        lab_dp = label_map(thr_dp, img)
                        lab_bf = label_map(thr_bf, img)
                        m_dp = lab_dp == k        # lớp sáng nhất (mask cảm sinh)
                        m_bf = lab_bf == k
                        h_dp, h_bf = mask_hash(m_dp), mask_hash(m_bf)

                        adiff = abs(f_dp - f_bf)
                        rdiff = adiff / abs(f_bf) if f_bf else adiff
                        mask_ok = h_dp == h_bf
                        lab_ok = bool(np.array_equal(lab_dp, lab_bf))
                        ok = bool(adiff <= tol and mask_ok)   # A5a — hai điều kiện

                        if not ok:
                            n_fail += 1
                            print(f"[FAIL] {sl.patient_id} {target} bg={bg} k={k}: "
                                  f"|Δf|={adiff:.3e} (tol={tol:g}) mask_identical={mask_ok} "
                                  f"thr_dp={thr_dp} thr_brute={thr_bf}")

                        w.write({
                            **row_key,
                            "f_dp": f"{f_dp:.17g}", "f_brute": f"{f_bf:.17g}",
                            "abs_diff": f"{adiff:.3e}", "rel_diff": f"{rdiff:.3e}",
                            "thr_dp": "|".join(map(str, thr_dp)),
                            "thr_brute": "|".join(map(str, thr_bf)),
                            "thr_identical": int(tuple(thr_dp) == tuple(thr_bf)),
                            "mask_hash_dp": h_dp, "mask_hash_brute": h_bf,
                            "mask_identical": int(mask_ok),
                            "labelmap_identical": int(lab_ok),
                            "t_dp_s": f"{t_dp:.6f}", "t_brute_s": f"{t_bf:.6f}",
                            "brute_over_dp": f"{(t_bf / t_dp if t_dp > 0 else float('nan')):.2f}",
                            "pass": int(ok),
                            "data_source": data_source(cfg),
                            "placeholder": int(data_source(cfg) == "synthetic"),
                        })
                        w.flush()
                        n_rows += 1

    elapsed = time.perf_counter() - t_start
    write_run_manifest(
        out_dir, cfg, cfg_hash, args.config, [csv_path],
        extra={"gate": "E1 dp_vs_bruteforce", "n_rows": n_rows, "n_fail": n_fail,
               "tol": tol, "k_list": k_list, "n_images": n_images,
               "passed": n_fail == 0, "elapsed_s": round(elapsed, 3)},
    )
    write_readme(
        out_dir, cfg, "E1 — DP vs brute force (Bảng II)",
        "| | |\n|---|---|\n"
        f"| Script | `scripts/run_exact_check.py` |\n"
        f"| Config | `{args.config}` |\n"
        f"| Tiêu chí PASS (A5a) | `\\|f_DP − f_brute\\| <= {tol:g}` **VÀ** mask cảm sinh "
        "giống hệt sau canonicalise |\n"
        f"| Số ô | {n_rows} |\n| Số FAIL | {n_fail} |\n"
        f"| Thời gian | {elapsed:.1f} s |\n\n"
        "Cột `brute_over_dp` = t_brute / t_DP (chênh bậc độ lớn). ⚠️ **KHÔNG** dùng nó để "
        "claim tốc độ: đồng tiền chính của bài là **NFE + độ phức tạp**, wall-clock chỉ là "
        "phụ (A0). Và **KHÔNG** claim DP là đóng góp — Menotti et al., CIARP 2015.",
    )

    print(f"\n[E1] {n_rows} ô, {n_fail} FAIL, {elapsed:.1f}s → {csv_path}")
    if n_fail:
        print("\n" + "=" * 72)
        print("DỪNG TOÀN BỘ — bộ giải DP KHÔNG khớp vét cạn.")
        print("Mọi kết luận về P2 dựng trên bộ giải này ⇒ không được chạy gì thêm.")
        print("Bước debug ĐẦU TIÊN = audit QUY ƯỚC (0log0 · lớp rỗng · ngưỡng trùng ·")
        print("có tính nền cường-độ-0 hay không), KHÔNG phải sửa DP (prereg §6/A5b).")
        print("=" * 72)
        return 1
    print("[E1] PASS — cổng cứng đã qua, được phép chạy tiếp.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

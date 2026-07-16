"""E7 — NGOẠI KIỂM LGG, ZERO-SHOT. → Replication table (lặp lại Bảng III–IV)

    python scripts/run_external.py --config configs/exp_smoke.yaml             # plumbing
    python scripts/run_external.py --config configs/exp_external.yaml --resume

**Hai cổng liêm chính chạy TRƯỚC lưới:**

1. 🔴 **A3 — CẤM RE-TUNE.** `q*` của P5 được **NẠP ĐÔNG LẠNH** từ `results/ceiling/qstar.csv`
   (đã fit trên BraTS). `allow_retune: true` ⇒ script DỪNG. Re-tune trên LGG ⇒ đây không
   còn là external validation.

2. 🔴 **A8 — "NGOẠI KIỂM" NÀY CÓ THỂ KHÔNG NGOẠI.** Buda et al. = 110 BN **TCGA-LGG**
   (TCIA); BraTS 2020 đã nuốt **108 ca TCGA-LGG** từ ĐÚNG collection đó. Khi
   `cohort_overlap_checked: false`, script gán nhãn
   `validation_label = "replication (cohort overlap UNVERIFIED)"` vào **mọi hàng CSV** và
   README — **không** được dùng chữ *"external validation"* ở bất kỳ đâu. Muốn dùng chữ
   đó: tải `name_mapping.csv`, đối chiếu, **báo cáo số trùng bằng CON SỐ**, rồi chọn
   (a) loại BN trùng · (b) gọi đúng tên *"annotation/preprocessing replication on an
   overlapping cohort"* · (c) ngoại kiểm theo chiều **TASK** (tune WT/FLAIR → test
   ET/T1ce; rẻ nhất, mạnh nhất, trùng khớp A2).
   *Gọi là ngoại kiểm mà thực chất trùng bệnh nhân, reviewer BraTS bắt được ⇒ đọc như
   **MISREPRESENTATION**, không còn là lỗi thiết kế.*

🔴 **A8 bẫy kênh:** ảnh LGG là TIFF **3 kênh** (pre / FLAIR / post-contrast) — FLAIR là
kênh **GIỮA (index 1)**. Đã bake trong `lgg_loader.py` + `tests/test_lgg_loader.py`.
"""

from __future__ import annotations

import sys
import time

import numpy as np
import pandas as pd

from _common import (
    CLASS_A,
    CLASS_B,
    NA_BG,
    NA_K,
    NA_SEED,
    ROOT,
    CsvAppender,
    classical_masks,
    data_source,
    decode_rows,
    done_keys,
    hist_cached,
    iter_slices,
    key_of,
    load_config,
    make_fitness,
    mask_metrics,
    metrics_cfg,
    parse_args,
    raw_fields,
    read_results_csv,
    reconstruct,
    resolve_output_dir,
    run_optimizer_cell,
    section,
    set_all_seeds,
    target_arrays,
    write_readme,
    write_run_manifest,
)
from run_ceiling import p5_mask
from run_main_grid import summarise
from src.decode.decoding import mask_hash
from src.eval.metrics import psnr, ssim
from src.solvers.exact_dp import relative_gap, solve_exact

KEY_COLS = ["patient_id", "target", "include_zero_bg", "k", "method", "seed"]
EXACT = "DP-exact"
UNVERIFIED = "replication (cohort overlap UNVERIFIED)"
VERIFIED = "external validation (cohort overlap checked)"


def validation_label(scfg) -> str:
    """A8 — chỉ được gọi là 'external validation' KHI đã đối chiếu name_mapping.csv."""
    if bool(scfg.get("cohort_overlap_checked", False)):
        n = scfg.get("cohort_overlap_n")
        if n is None:
            raise SystemExit(
                "[E7 GATE] cohort_overlap_checked=true nhưng cohort_overlap_n=null. "
                "A8 đòi BÁO CÁO SỐ TRÙNG BẰNG CON SỐ. Điền số ca trùng TCGA-LGG ↔ BraTS "
                "(từ name_mapping.csv) rồi chạy lại."
            )
        return f"{VERIFIED}; overlap_n={int(n)}"
    return UNVERIFIED


def load_frozen_qstar(scfg):
    """Nạp q* ĐÃ ĐÓNG BĂNG từ E4 (BraTS). Không có file ⇒ bỏ qua P5, KHÔNG fit lại."""
    if bool(scfg.get("allow_retune", False)):
        raise SystemExit(
            "[E7 GATE] allow_retune=true — CẤM (prereg §6/A3). Re-tune ngưỡng 1-tham-số "
            "trên LGG ⇒ không còn là external validation. Đặt lại allow_retune: false."
        )
    p = scfg.get("frozen_qstar_csv")
    if not p:
        return None
    path = ROOT / p if not str(p).startswith(("/", "\\")) else p
    if not path.exists():
        print(f"[WARN] không thấy {path} — BỎ QUA P5 ở E7. (KHÔNG được fit q* trên LGG.)")
        return None
    df = read_results_csv(path)
    df = df[df["label"] == "P5-percentile"] if "label" in df.columns else df
    if df.empty:
        return None
    # q* đóng băng = median của 5 q* trên BraTS (một con số, khai báo được, không tuning).
    q = float(df["q_star"].median())
    print(f"[E7] q* ĐÓNG BĂNG từ BraTS = {q:.4f} (median của {len(df)} fold) — zero-shot.")
    return q


def main() -> int:
    args = parse_args(__doc__.splitlines()[0]).parse_args()
    cfg, cfg_hash = load_config(args.config)
    scfg = section(cfg, "external")
    out_dir = resolve_output_dir(scfg, args.output, "results/external")
    raw_path = out_dir / "raw.csv"

    label = validation_label(scfg)
    print(f"[E7] validation_label = {label!r}")
    if label == UNVERIFIED:
        print("[E7] ⚠️ A8: CHƯA đối chiếu name_mapping.csv ⇒ TUYỆT ĐỐI không dùng chữ "
              "'external validation' cho lô số này trong bản thảo.")
    qstar = load_frozen_qstar(scfg)

    mcfg = metrics_cfg(scfg)
    dcfg = scfg.get("decoding") or {}
    rules = list(dcfg.get("rules", ["brightest"]))
    targets = list(scfg.get("targets", ["wt_flair"]))
    bgs = scfg.get("include_zero_bg", [True])
    bgs = [bgs] if isinstance(bgs, bool) else list(bgs)
    k_list = [int(k) for k in scfg.get("k_list", [2])]
    seeds = [int(s) for s in scfg.get("seeds", [0])]
    budget = int(scfg.get("budget", 1000))
    hp = dict(scfg.get("hyperparams") or {})
    algos = list(scfg.get("optimizers") or [])
    tol = float((scfg.get("stats") or {}).get("hit_gap_tol", 1e-4))
    cache_dir = out_dir / "cache"
    ph = int(data_source(cfg) == "synthetic")

    fields = raw_fields(mcfg) + ["validation_label"]
    done = done_keys(raw_path, KEY_COLS, args.resume)
    n_cells = 0
    t_start = time.perf_counter()

    with CsvAppender(raw_path, fields, "run_external.py", cfg, resume=args.resume,
                     note=f"E7 zero-shot. validation_label={label}. "
                          f"NO re-tuning on this cohort (prereg A3).") as w:
        for sl in iter_slices(scfg):
            for target in targets:
                img, gt = target_arrays(sl, target)
                tail = {"data_source": data_source(cfg), "placeholder": ph,
                        "validation_label": label}

                if scfg.get("include_classical", False):
                    for name, mask in classical_masks(
                            img, scfg.get("classical") or [], scfg).items():
                        rk = {"patient_id": sl.patient_id, "target": target,
                              "include_zero_bg": NA_BG, "k": NA_K, "method": name,
                              "seed": NA_SEED}
                        if key_of(rk, KEY_COLS) in done:
                            continue
                        w.write({**rk, "method_class": CLASS_A, "decode_rule": "native",
                                 "decode_horn": "native", "mask_hash": mask_hash(mask),
                                 **mask_metrics(mask, gt, mcfg), **tail})
                    w.flush()

                # P5 với q* ĐÓNG BĂNG từ BraTS — zero-shot, KHÔNG fit gì trên LGG (A3)
                if qstar is not None:
                    for bg in bgs:
                        rk = {"patient_id": sl.patient_id, "target": target,
                              "include_zero_bg": str(bool(bg)).lower(), "k": NA_K,
                              "method": "P5-percentile-frozen", "seed": NA_SEED}
                        if key_of(rk, KEY_COLS) in done:
                            continue
                        mask = p5_mask(img, qstar, bool(bg))
                        w.write({**rk, "method_class": CLASS_B, "decode_rule": "native",
                                 "decode_horn": "native", "thresholds": f"q={qstar:.4f}",
                                 "mask_hash": mask_hash(mask),
                                 **mask_metrics(mask, gt, mcfg), **tail})
                    w.flush()

                for bg in bgs:
                    hist = hist_cached(cache_dir, sl, target, bool(bg))
                    if hist.sum() <= 0:
                        continue
                    fit = make_fitness(hist, str(scfg.get("fitness", "kapur")))
                    for k in k_list:
                        thr_ex, f_ex = solve_exact(fit, k)
                        if scfg.get("include_exact_dp", True):
                            rk = {"patient_id": sl.patient_id, "target": target,
                                  "include_zero_bg": str(bool(bg)).lower(), "k": k,
                                  "method": EXACT, "seed": NA_SEED}
                            if key_of(rk, KEY_COLS) not in done:
                                rec = reconstruct(img, list(thr_ex))
                                base = {**rk, "method_class": CLASS_A,
                                        "thresholds": "|".join(map(str, thr_ex)),
                                        "fitness": float(f_ex), "f_exact": float(f_ex),
                                        "relative_gap": 0.0, "hit": 1,
                                        "psnr": psnr(img, rec), "ssim": ssim(img, rec),
                                        **tail}
                                for r in decode_rows(base, img, gt, list(thr_ex), scfg, rules):
                                    w.write(r)
                                w.flush()
                        for algo in algos:
                            for seed in seeds:
                                rk = {"patient_id": sl.patient_id, "target": target,
                                      "include_zero_bg": str(bool(bg)).lower(), "k": k,
                                      "method": algo, "seed": seed}
                                if key_of(rk, KEY_COLS) in done:
                                    continue
                                res = run_optimizer_cell(algo, fit, k, seed, budget, hp)
                                rec = reconstruct(img, res["thresholds"])
                                gap = relative_gap(float(f_ex), res["fitness"])
                                base = {**rk, "method_class": CLASS_A,
                                        "thresholds": "|".join(map(str, res["thresholds"])),
                                        "fitness": res["fitness"], "f_exact": float(f_ex),
                                        "relative_gap": gap, "hit": int(gap < tol),
                                        "nfe": res["nfe"], "budget": budget,
                                        "runtime_s": res["runtime_s"],
                                        "psnr": psnr(img, rec), "ssim": ssim(img, rec),
                                        **tail}
                                for r in decode_rows(base, img, gt, res["thresholds"],
                                                     scfg, rules):
                                    w.write(r)
                                w.flush()
                                n_cells += 1

    elapsed = time.perf_counter() - t_start
    summary_path, ident_path = summarise(raw_path, out_dir, scfg, cfg, algos)
    write_run_manifest(
        out_dir, cfg, cfg_hash, args.config, [raw_path, summary_path, ident_path],
        extra={"experiment": "E7 external (LGG)", "validation_label": label,
               "allow_retune": False, "frozen_qstar": qstar,
               "cohort_overlap_checked": bool(scfg.get("cohort_overlap_checked", False)),
               "cohort_overlap_n": scfg.get("cohort_overlap_n"),
               "n_cells_computed": n_cells, "budget": budget, "k_list": k_list,
               "elapsed_s": round(elapsed, 3)},
    )
    write_readme(
        out_dir, cfg, "E7 — LGG zero-shot (Replication table)",
        f"**`validation_label` = `{label}`** — nhãn này nằm trong MỌI hàng của `raw.csv`.\n\n"
        + ("🔴 **A8 — CHƯA đối chiếu `name_mapping.csv`.** Buda et al. = 110 BN TCGA-LGG; "
           "BraTS 2020 đã nuốt 108 ca TCGA-LGG từ đúng collection đó ⇒ *\"khác cơ sở, khác "
           "máy chụp\"* rất có thể là **CÙNG NHÓM BỆNH NHÂN**. **TUYỆT ĐỐI không dùng chữ "
           "\"external validation\"** cho lô số này cho tới khi số trùng được báo cáo bằng "
           "con số. Gọi sai tên ⇒ đọc như MISREPRESENTATION.\n\n"
           if label == UNVERIFIED else "")
        + (f"P5 chạy **zero-shot** với `q* = {qstar:.4f}` **đóng băng từ BraTS** — không "
           f"một tham số nào được fit trên cohort này (A3).\n\n" if qstar is not None
           else "P5 bị BỎ QUA (không có q* đóng băng). KHÔNG được fit q* trên LGG.\n\n")
        + "Trình bày trong bản thảo: **replication table lặp lại Bảng III–IV**, không tách "
          "section riêng.",
    )
    print(f"\n[E7] {n_cells} ô mới, {elapsed:.1f}s → {raw_path}\n[E7] summary → {summary_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

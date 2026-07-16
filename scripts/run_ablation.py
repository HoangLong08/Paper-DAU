"""E3 — ABLATION QIGOA trên dữ liệu thật, cùng NFE + cùng MỌI hyperparameter khác. → Bảng IV

    python scripts/run_ablation.py --config configs/exp_smoke.yaml           # plumbing
    python scripts/run_ablation.py --config configs/exp_ablation.yaml --resume

Biến thể: QIGOA-full / −quantum / −memetic / −OBL / −Lévy / PSO+memetic (+ PSO đối chứng).

**Hai cổng cứng chạy TRƯỚC lưới** (đây là chỗ lợi thế biểu kiến thường được sinh ra):
  1. **Equal tuning** — `variants[].hp` CHỈ được chứa cờ bật/tắt thành phần
     (quantum/obl/levy/memetic). Mọi hyperparameter số học đến từ khối `hyperparams`
     dùng chung. Một variant cố đổi `pop`/`c_max`/... ⇒ script DỪNG. Lợi thế biểu kiến
     trong lĩnh vực này gần như luôn đến từ **tuning lệch** (prereg §6/A6).
  2. **Parity `PSO+memetic` ↔ `PSO`** — `PSO+memetic` là lớp tầng-script (src.PSO không
     có cờ `memetic`; xem scripts/README.md §Interface gaps). Với `memetic=False` nó phải
     cho kết quả GIỐNG HỆT `PSO` ở cùng seed. Script assert điều đó ⇒ chống trôi dạt cài đặt.

Dự đoán khai báo trước (prereg §2): quantum đóng góp ≈ 0 vào Dice. **Nếu SAI** — quantum
thực sự cải thiện Dice có ý nghĩa — đó là finding **DƯƠNG** và ta báo cáo đúng như vậy
(§4 cờ đỏ (a) ⇒ reframe theo hướng ngược lại, KHÔNG cứu claim đã chết).
"""

from __future__ import annotations

import sys
import time

import numpy as np

from _common import (
    CLASS_A,
    NA_SEED,
    CsvAppender,
    build_optimizer,
    data_source,
    decode_rows,
    done_keys,
    hist_cached,
    iter_slices,
    key_of,
    load_config,
    make_fitness,
    metrics_cfg,
    parse_args,
    raw_fields,
    reconstruct,
    resolve_output_dir,
    run_optimizer_cell,
    section,
    set_all_seeds,
    target_arrays,
    write_readme,
    write_run_manifest,
)
from run_main_grid import summarise
from src.eval.metrics import psnr, ssim
from src.solvers.exact_dp import relative_gap, solve_exact

KEY_COLS = ["patient_id", "target", "include_zero_bg", "k", "method", "seed"]
COMPONENT_FLAGS = {"quantum", "obl", "levy", "memetic"}
EXACT = "DP-exact"


def check_equal_tuning(variants, shared_hp) -> None:
    """Cổng 1 — `variants[].hp` chỉ được chứa cờ thành phần (equal tuning budget, A6)."""
    for v in variants:
        bad = set((v.get("hp") or {})) - COMPONENT_FLAGS
        if bad:
            raise SystemExit(
                f"[E3 GATE] Variant {v['name']!r} cố đổi hyperparameter {sorted(bad)} — "
                f"CẤM. Ablation phải giữ MỌI hp khác y hệt (playbook thầy §4.1; prereg "
                f"§6/A6: lợi thế biểu kiến gần như luôn đến từ tuning lệch). "
                f"hp dùng chung: {sorted(shared_hp)}"
            )


def check_pso_memetic_parity(shared_hp, budget: int = 200, k: int = 3, seed: int = 0) -> None:
    """Cổng 2 — PSO+memetic(memetic=False) phải TRÙNG KHÍT PSO ở cùng seed."""
    from src.data.synthetic import synthetic_slice
    from src.fitness.kapur import KapurFitness, build_histogram

    fit = KapurFitness(build_histogram(synthetic_slice(0).flair, include_zero_bg=True))
    out = {}
    for name, hp in (("PSO", dict(shared_hp)),
                     ("PSO+memetic", {**shared_hp, "memetic": False})):
        set_all_seeds(seed)
        opt = build_optimizer(name, fit, k=k, seed=seed, budget=budget, hp=hp)
        bx, bf, used = opt.run()
        out[name] = (tuple(int(v) for v in np.asarray(bx).ravel()), float(bf), used)
    if out["PSO"] != out["PSO+memetic"]:
        raise SystemExit(
            "[E3 GATE] PSO+memetic(memetic=False) KHÔNG trùng PSO:\n"
            f"  PSO         = {out['PSO']}\n  PSO+memetic = {out['PSO+memetic']}\n"
            "⇒ vòng lặp PSO tầng-script đã trôi khỏi src/. Đồng bộ lại scripts/_common.py"
            "::PSOMemetic._search với src/solvers/metaheuristics/pso.py trước khi chạy E3."
        )
    print(f"[E3 GATE] parity PSO+memetic(memetic=off) ≡ PSO — PASS {out['PSO']}")


def main() -> int:
    args = parse_args(__doc__.splitlines()[0]).parse_args()
    cfg, cfg_hash = load_config(args.config)
    scfg = section(cfg, "ablation")
    out_dir = resolve_output_dir(scfg, args.output, "results/ablation")
    raw_path = out_dir / "raw.csv"

    variants = list(scfg.get("variants") or [])
    if not variants:
        raise SystemExit("[E3] config thiếu `variants` / `ablation.variants`")
    shared_hp = dict(scfg.get("hyperparams") or {})

    check_equal_tuning(variants, shared_hp)
    if any(v.get("base") == "PSO+memetic" for v in variants):
        check_pso_memetic_parity(shared_hp)

    mcfg = metrics_cfg(scfg)
    dcfg = scfg.get("decoding") or {}
    rules = list(dcfg.get("rules", ["brightest"]))
    targets = list(scfg.get("targets", ["wt_flair"]))
    bgs = scfg.get("include_zero_bg", [True])
    bgs = [bgs] if isinstance(bgs, bool) else list(bgs)
    k_list = [int(k) for k in scfg.get("k_list", [2])]
    seeds = [int(s) for s in scfg.get("seeds", [0])]
    budget = int(scfg.get("budget", 1000))
    tol = float((scfg.get("stats") or {}).get("hit_gap_tol", 1e-4))
    cache_dir = out_dir / "cache"
    if scfg.get("cache_dir"):
        from _common import ROOT

        cache_dir = ROOT / scfg["cache_dir"]

    done = done_keys(raw_path, KEY_COLS, args.resume)
    n_cells = 0
    t_start = time.perf_counter()

    with CsvAppender(raw_path, raw_fields(mcfg), "run_ablation.py", cfg, resume=args.resume,
                     note="E3 ablation — same NFE, same every other hyperparameter (A6)."
                     ) as w:
        for sl in iter_slices(scfg):
            for target in targets:
                img, gt = target_arrays(sl, target)
                for bg in bgs:
                    hist = hist_cached(cache_dir, sl, target, bool(bg))
                    if hist.sum() <= 0:
                        continue
                    fit = make_fitness(hist, str(scfg.get("fitness", "kapur")))
                    for k in k_list:
                        thr_ex, f_ex = solve_exact(fit, k)

                        # DP-exact làm mốc tham chiếu trong CHÍNH bảng ablation
                        rk = {"patient_id": sl.patient_id, "target": target,
                              "include_zero_bg": str(bool(bg)).lower(), "k": k,
                              "method": EXACT, "seed": NA_SEED}
                        if key_of(rk, KEY_COLS) not in done:
                            rec = reconstruct(img, list(thr_ex))
                            base = {**rk, "method_class": CLASS_A,
                                    "thresholds": "|".join(map(str, thr_ex)),
                                    "fitness": float(f_ex), "f_exact": float(f_ex),
                                    "relative_gap": 0.0, "hit": 1,
                                    "nfe": "", "budget": "", "runtime_s": "",
                                    "psnr": psnr(img, rec), "ssim": ssim(img, rec),
                                    "data_source": data_source(cfg),
                                    "placeholder": int(data_source(cfg) == "synthetic")}
                            for r in decode_rows(base, img, gt, list(thr_ex), scfg, rules):
                                w.write(r)
                            w.flush()

                        for v in variants:
                            hp = {**shared_hp, **(v.get("hp") or {})}
                            for seed in seeds:
                                rk = {"patient_id": sl.patient_id, "target": target,
                                      "include_zero_bg": str(bool(bg)).lower(), "k": k,
                                      "method": v["name"], "seed": seed}
                                if key_of(rk, KEY_COLS) in done:
                                    continue
                                res = run_optimizer_cell(v["base"], fit, k, seed, budget, hp)
                                rec = reconstruct(img, res["thresholds"])
                                gap = relative_gap(float(f_ex), res["fitness"])
                                base = {**rk, "method_class": CLASS_A,
                                        "thresholds": "|".join(map(str, res["thresholds"])),
                                        "fitness": res["fitness"], "f_exact": float(f_ex),
                                        "relative_gap": gap, "hit": int(gap < tol),
                                        "nfe": res["nfe"], "budget": budget,
                                        "runtime_s": res["runtime_s"],
                                        "psnr": psnr(img, rec), "ssim": ssim(img, rec),
                                        "data_source": data_source(cfg),
                                        "placeholder": int(data_source(cfg) == "synthetic")}
                                for r in decode_rows(base, img, gt, res["thresholds"],
                                                     scfg, rules):
                                    w.write(r)
                                w.flush()      # checkpoint sau mỗi ô
                                n_cells += 1

    elapsed = time.perf_counter() - t_start
    names = [v["name"] for v in variants]
    summary_path, ident_path = summarise(raw_path, out_dir, scfg, cfg, names)
    write_run_manifest(
        out_dir, cfg, cfg_hash, args.config, [raw_path, summary_path, ident_path],
        extra={"experiment": "E3 ablation", "variants": names, "budget": budget,
               "shared_hyperparams": shared_hp, "n_cells_computed": n_cells,
               "gates_passed": ["equal_tuning", "pso_memetic_parity"],
               "elapsed_s": round(elapsed, 3)},
    )
    write_readme(
        out_dir, cfg, "E3 — ablation QIGOA (Bảng IV)",
        "Biến thể: " + ", ".join(f"`{n}`" for n in names) + ".\n\n"
        f"Ngân sách NFE = {budget} cho **mọi** biến thể (±0). Hyperparameter dùng chung: "
        f"`{shared_hp}` — biến thể chỉ khác nhau ở cờ bật/tắt thành phần.\n\n"
        "**Dự đoán khai báo trước:** quantum đóng góp ≈ 0 vào Dice. Nếu dự đoán SAI ⇒ "
        "finding DƯƠNG, báo cáo đúng như vậy (prereg §2, §4 cờ đỏ (a)).\n\n"
        "Đọc equivalence bằng `results/stats/` (TOST 90%CI + `delta_ach`, Bayesian ROPE "
        "primary) — **KHÔNG** đọc bằng \"p > 0,05\" (A4c).",
    )
    print(f"\n[E3] {n_cells} ô mới, {elapsed:.1f}s → {raw_path}\n[E3] summary → {summary_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""results/ → paper/figures/*.pdf — KHÔNG gõ số tay.

    python scripts/build_figures.py --config configs/exp_smoke.yaml
    python scripts/build_figures.py --config configs/exp_main.yaml

| Hình | Từ | Nội dung |
|---|---|---|
| `fig2_cd_diagram.pdf` | `results/stats/cd.csv` | Critical Difference (Demšar 2006) |
| `fig3_goodhart.pdf` | `results/main/summary.csv` | trục kép: fitness/PSNR ↑ theo k vs Dice/HD95 ↓ |
| `fig4_ceiling_ladder.pdf` | `results/ceiling/` + `results/unet/` | thang bậc trần ★ hình chủ đạo |

⚠️ **Hình 3 phải nêu thẳng sự thật bất lợi**: trong *cùng một k*, tương quan PSNR–Dice
giữa các thuật toán là **DƯƠNG**; nghịch lý nằm ở chiều **k**, không phải chiều thuật
toán. Che giấu ⇒ reviewer chạy lại số trong 10 phút và bài chết (prereg §1/P3).

⚠️ **Hình 4**: mọi bậc oracle mang nhãn `uses test-time ground truth` (loại C — cận trên
không đạt được, KHÔNG phải phương pháp). nnU-Net chỉ là đường tham chiếu **trích từ văn
liệu**, dán nhãn *"not run by us, different input protocol"* — KHÔNG phải baseline so
trực tiếp.

⚠️ Hình sinh từ dữ liệu synthetic được đóng dấu **[PLACEHOLDER]** ngay trên mặt hình.
Checklist §6 đòi: *figure sinh từ script, **đã nhìn tận mắt sau khi render***.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from _common import (
    ROOT,
    data_source,
    load_config,
    parse_args,
    read_results_csv,
    resolve_output_dir,
    section,
)

PH_TEXT = "[PLACEHOLDER] synthetic phantoms — NOT results (CLAUDE.md IRON RULE 1/3)"


def _stamp(fig, ph: bool) -> None:
    if ph:
        fig.text(0.5, 0.5, PH_TEXT, ha="center", va="center", fontsize=13, color="red",
                 alpha=0.22, rotation=22, zorder=10)


def _load(p: Path) -> pd.DataFrame:
    return read_results_csv(p) if p.exists() else pd.DataFrame()


def _save(fig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight")
    try:                       # --output có thể trỏ ra ngoài repo
        shown = path.relative_to(ROOT)
    except ValueError:
        shown = path
    print(f"  ✓ {shown}")


# --------------------------------------------------------------------------- #
def fig2_cd(cd: pd.DataFrame, out: Path, ph: bool) -> None:
    """Critical Difference diagram (Demšar 2006) — hạng trung bình + thanh CD."""
    import matplotlib.pyplot as plt

    g = cd.groupby("method")["avg_rank"].mean().sort_values()
    cdv = float(cd["cd"].mean())
    fig, ax = plt.subplots(figsize=(7.2, 0.42 * len(g) + 1.8))
    y = np.arange(len(g))
    ax.errorbar(g.to_numpy(), y, xerr=cdv / 2, fmt="o", capsize=3, color="#333")
    ax.set_yticks(y)
    ax.set_yticklabels(g.index)
    ax.invert_yaxis()
    ax.set_xlabel(f"average rank on Dice (lower = better)   |   CD = {cdv:.2f}")
    ax.set_title("Fig. 2 — Critical Difference (Friedman + Nemenyi, patient-level)")
    ax.grid(axis="x", alpha=0.3)
    _stamp(fig, ph)
    _save(fig, out)
    plt.close(fig)


def fig3_goodhart(s: pd.DataFrame, out: Path, ph: bool, rule: str) -> None:
    """Goodhart, trục kép: fitness/PSNR ↑ theo k trong khi Dice ↓ / HD95 xấu đi."""
    import matplotlib.pyplot as plt

    f = s[(s["decode_rule"] == rule) & (s["k"] > 0)]
    if f.empty:
        print("  (bỏ qua Hình 3 — không có hàng nào ở decoding primary)")
        return
    g = f.groupby("k").agg(psnr=("psnr_median", "median"), ssim=("ssim_median", "median"),
                           dice=("dice_median", "median"), hd95=("hd95_median", "median"),
                           empty=("empty_mask_rate", "mean")).reset_index()
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ax.plot(g["k"], g["psnr"], "o-", color="#1f77b4", label="PSNR (median)")
    ax.set_xlabel("number of thresholds $k$")
    ax.set_ylabel("PSNR (dB) — the literature's metric", color="#1f77b4")
    ax.tick_params(axis="y", labelcolor="#1f77b4")
    ax2 = ax.twinx()
    ax2.plot(g["k"], g["dice"], "s--", color="#d62728", label="Dice (median)")
    ax2.set_ylabel("Dice — the clinical metric", color="#d62728")
    ax2.tick_params(axis="y", labelcolor="#d62728")
    ax.set_title("Fig. 3 — Goodhart: the reported metric rises with $k$ while the\n"
                 "clinical metric falls (dual axis)")
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="center left", fontsize=8)
    ax.grid(alpha=0.3)
    # Sự thật bất lợi PHẢI nằm trên mặt hình (prereg §1/P3, "lưu ý trung thực bắt buộc").
    fig.text(0.5, -0.06,
             "Within a fixed $k$, PSNR and Dice correlate POSITIVELY across algorithms; "
             "the anti-correlation lives on the $k$ axis, not the algorithm axis.\n"
             "PSNR is a monotone function of quantisation error and therefore rises with "
             "$k$ BY CONSTRUCTION (Lloyd--Max) — this is an argument, not a correlation.",
             ha="center", fontsize=7.5, style="italic")
    _stamp(fig, ph)
    _save(fig, out)
    plt.close(fig)


def fig4_ceiling(c: pd.DataFrame, u: pd.DataFrame, m: pd.DataFrame, out: Path, ph: bool,
                 lit: dict, rule: str, k_primary: int) -> None:
    """Ceiling ladder ★ — mọi bậc trên CÙNG một trục Dice, cùng một tập test."""
    import matplotlib.pyplot as plt

    def _bg(r) -> str:
        # bg là một TRỤC THẬT (A5c: tính hay không tính nền cường-độ-0 đổi hoàn toàn
        # ngưỡng tối ưu) ⇒ phải nằm trong nhãn, nếu không hai bậc khác nhau trông y hệt.
        v = str(r.get("include_zero_bg", "na")).lower()
        return "" if v in ("na", "nan", "none", "") else f" [bg={v}]"

    rows = []
    if not c.empty:
        for _, r in c.iterrows():
            rows.append((str(r["method"]) + _bg(r), float(r["dice_median"]),
                         str(r["method_class"])))
    if not u.empty:
        for _, r in u.iterrows():
            rows.append((str(r["method"]), float(r["dice_median"]), str(r["method_class"])))
    if not m.empty:
        f = m[(m["decode_rule"] == rule) & (m["k"] == k_primary)]
        for _, r in f.iterrows():
            rows.append((f"{r['method']} (k={k_primary}){_bg(r)}", float(r["dice_median"]),
                         str(r.get("method_class", "A"))))
    rows = [r for r in rows if np.isfinite(r[1])]
    if not rows:
        print("  (bỏ qua Hình 4 — chưa có results/ceiling/summary.csv)")
        return
    rows.sort(key=lambda t: t[1])
    labels = [r[0] for r in rows]
    vals = [r[1] for r in rows]
    colors = ["#c44e52" if r[2].startswith("C") else
              "#4c72b0" if r[2].startswith("B") else "#8c8c8c" for r in rows]

    fig, ax = plt.subplots(figsize=(7.6, 0.34 * len(rows) + 2.2))
    ax.barh(np.arange(len(rows)), vals, color=colors)
    ax.set_yticks(np.arange(len(rows)))
    ax.set_yticklabels([f"{l}  {'← uses test-time GT' if c_.startswith('C') else ''}"
                        for l, c_ in zip(labels, [r[2] for r in rows])], fontsize=8)
    ax.set_xlabel("Dice (median, patient-level)")
    ax.set_title("Fig. 4 — Ceiling ladder")
    ax.grid(axis="x", alpha=0.3)
    if lit:
        v = lit.get("wt_dice_test")
        if v:
            ax.axvline(float(v), color="green", ls=":", lw=1.4)
            # đặt TRÊN đỉnh, không dưới đáy — dưới đáy nó chồng lên legend
            ax.text(float(v), len(rows) - 0.4,
                    f" {lit.get('name')} = {v}\n {lit.get('label')}",
                    fontsize=6.5, color="green", va="bottom", ha="left")
    handles = [plt.Rectangle((0, 0), 1, 1, color=c_) for c_ in ("#8c8c8c", "#4c72b0", "#c44e52")]
    ax.legend(handles, ["A: unsupervised per-image",
                        "B: learned (out-of-fold only)",
                        "C: uses test-time ground truth (NOT a method)"],
              fontsize=7, loc="lower right")
    fig.text(0.5, -0.04,
             "We do not claim to establish this ceiling (François & Tinarrage, JMIV "
             "2026, already report an oracle Dice bound on BraTS FLAIR); the level-set "
             "optimality result is Lipton et al. (2014) / RankSEG (2023).\n"
             "Our contribution is the DECOMPOSITION of the gap: information absent from "
             "INTENSITY vs information absent from PIXELS.",
             ha="center", fontsize=7.5, style="italic")
    _stamp(fig, ph)
    _save(fig, out)
    plt.close(fig)


def main() -> int:
    args = parse_args(__doc__.splitlines()[0]).parse_args()
    cfg, _ = load_config(args.config)
    import matplotlib

    matplotlib.use("Agg")

    scfg = section(cfg, "stats")
    ph = data_source(cfg) == "synthetic"
    st = cfg.get("stats") or {}
    rule = str(st.get("decoding_primary", "brightest"))
    k_primary = int(st.get("k_primary", 4))

    main_dir = ROOT / (scfg.get("main_dir") or cfg.get("output_dir") or "results/main")
    stats_dir = ROOT / (scfg.get("output_dir") or "results/stats")
    ceil_dir = ROOT / (scfg.get("ceiling_dir")
                       or (cfg.get("ceiling") or {}).get("output_dir") or "results/ceiling")
    unet_dir = ROOT / (scfg.get("unet_dir")
                       or (cfg.get("unet") or {}).get("output_dir") or "results/unet")
    out_dir = resolve_output_dir({}, args.output, "paper/figures")
    print(f"[figures] → {out_dir}")

    cd = _load(stats_dir / "cd.csv")
    if not cd.empty:
        fig2_cd(cd, out_dir / "fig2_cd_diagram.pdf", ph)
    else:
        print("  (bỏ qua Hình 2 — chưa có results/stats/cd.csv)")

    s = _load(main_dir / "summary.csv")
    if not s.empty:
        fig3_goodhart(s, out_dir / "fig3_goodhart.pdf", ph, rule)
    else:
        print("  (bỏ qua Hình 3 — chưa có summary.csv của E2)")

    fig4_ceiling(_load(ceil_dir / "summary.csv"), _load(unet_dir / "summary.csv"), s,
                 out_dir / "fig4_ceiling_ladder.pdf", ph,
                 (cfg.get("unet") or {}).get("literature_reference") or {}, rule, k_primary)

    print("[figures] xong. ⚠️ Checklist §6: **nhìn tận mắt** từng hình sau khi render.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

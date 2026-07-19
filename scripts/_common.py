"""MODULE G — plumbing dùng chung cho mọi entrypoint trong scripts/.

Không chứa khoa học, chỉ chứa hạ tầng: đọc config, set seed, nạp dữ liệu, cache
histogram, ghi CSV có cấu trúc + resume, ghi run-manifest.json.

Kỷ luật bake sẵn ở đây (CLAUDE.md §5, docs/preregistration.md §6):
  * **Config-driven** — KHÔNG magic number trong script. Mọi tham số đến từ
    ``configs/*.yaml``; script chỉ đọc.
  * **Provenance** — mỗi CSV mở đầu bằng banner ``#`` ghi rõ script/commit/nguồn
    dữ liệu, và mỗi run ghi ``run-manifest.json`` (không manifest = run không tồn tại).
  * **[PLACEHOLDER]** — mọi số sinh từ phantom synthetic được dán nhãn ở banner CSV,
    ở cột ``placeholder``, và ở README của thư mục output. Số synthetic KHÔNG BAO GIỜ
    là kết quả (IRON RULE 1/3).
  * **Resume** — mọi lưới ghi từng dòng ngay khi tính xong và bỏ qua ô đã có, để một
    session Kaggle chết giữa chừng không mất việc đã làm (§5 Kaggle).

Đọc CSV do các script này sinh ra bằng :func:`read_results_csv` (nó xử lý banner ``#``).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import sys
import time
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Sequence

import numpy as np
import pandas as pd
import yaml

# --------------------------------------------------------------------------- #
# repo root on sys.path (scripts are run as `python scripts/run_x.py`)
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Script output is Vietnamese and uses "→"; a Windows console defaults to cp1252
# and raises UnicodeEncodeError on the final print, so a passing E1 gate would
# exit non-zero and read as "DỪNG TOÀN BỘ". Kaggle (UTF-8) never hit this.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, OSError):
            pass

from src.data.brats_loader import Slice, build_cohort, iter_cohort  # noqa: E402
from src.data.lgg_loader import iter_lgg  # noqa: E402
from src.data.synthetic import synthetic_slice  # noqa: E402
from src.decode.decoding import label_map  # noqa: E402
from src.fitness.kapur import KapurFitness, build_histogram  # noqa: E402
from src.fitness.otsu import OtsuFitness  # noqa: E402
from src.manifest import write_manifest  # noqa: E402
from src.solvers.metaheuristics import OPTIMIZERS  # noqa: E402
from src.solvers.metaheuristics.pso import (  # noqa: E402
    DEFAULT_C1,
    DEFAULT_C2,
    DEFAULT_POP,
    DEFAULT_VMAX_FRAC,
    DEFAULT_W,
    PSO,
)

# --------------------------------------------------------------------------- #
# Target contract (A2: WT/FLAIR = ca thuận lợi nhất; ET/T1ce = ca KHÓ, bắt buộc)
# --------------------------------------------------------------------------- #
TARGETS: Dict[str, tuple] = {
    "wt_flair": ("flair", "wt_mask"),
    "et_t1ce": ("t1ce", "et_mask"),
}

FITNESSES = {"kapur": KapurFitness, "otsu": OtsuFitness}

#: Nhãn loại phương pháp (prereg §6/A3 — mỗi phương pháp thuộc ĐÚNG một loại).
# Cột ĐỊNH DANH (không phải số đo): luôn đọc dưới dạng chuỗi. Xem read_results_csv —
# để pandas tự suy kiểu trên các cột này đã gây trùng dòng + tách nhóm trên lưới chính.
ID_COLS = ("patient_id", "target", "include_zero_bg", "method", "method_class",
           "decode_rule", "decode_horn", "thresholds", "data_source")

CLASS_A = "A: unsupervised per-image"
CLASS_B = "B: learned (out-of-fold only)"
CLASS_C = "C: uses test-time ground truth"

PLACEHOLDER_BANNER = (
    "# [PLACEHOLDER] Numbers below come from SYNTHETIC phantoms "
    "(smoke test only). Per CLAUDE.md IRON RULE 1/3 they may NEVER appear in the "
    "paper as results."
)


# --------------------------------------------------------------------------- #
# CLI + config
# --------------------------------------------------------------------------- #
def parse_args(description: str) -> argparse.ArgumentParser:
    """Argparse chuẩn cho mọi script: --config (bắt buộc), --resume, --output."""
    p = argparse.ArgumentParser(description=description)
    p.add_argument("--config", required=True, type=Path, help="configs/*.yaml")
    p.add_argument(
        "--resume",
        action="store_true",
        help="bỏ qua các ô đã có trong CSV output (thiết kế resume-được cho Kaggle)",
    )
    p.add_argument("--output", type=Path, default=None, help="ghi đè output_dir của config")
    return p


def load_config(path: Path) -> tuple[dict, str]:
    """Đọc YAML, trả (cfg, config_hash=sha256 của file bytes)."""
    raw = Path(path).read_bytes()
    cfg = yaml.safe_load(raw.decode("utf-8"))
    return cfg, hashlib.sha256(raw).hexdigest()


def section(cfg: dict, name: str) -> dict:
    """Merge: khoá của section `name` ghi đè khoá top-level cùng tên."""
    sub = cfg.get(name) or {}
    if not isinstance(sub, dict):
        raise ValueError(f"config section '{name}' phải là mapping")
    return {**cfg, **sub}


def resolve_output_dir(scfg: dict, cli_output: Optional[Path], default: str) -> Path:
    out = Path(cli_output) if cli_output else Path(scfg.get("output_dir", default))
    if not out.is_absolute():
        out = ROOT / out
    out.mkdir(parents=True, exist_ok=True)
    return out


# --------------------------------------------------------------------------- #
# Seeds (CLAUDE.md §5.2 — set MỌI seed)
# --------------------------------------------------------------------------- #
def set_all_seeds(seed: int) -> None:
    """Set random / numpy / torch (+cudnn.deterministic). torch là tuỳ chọn."""
    random.seed(seed)
    np.random.seed(seed)
    try:  # torch chỉ cần cho run_unet.py; các script CPU không phải cài
        import torch

        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    except Exception:
        pass


# --------------------------------------------------------------------------- #
# Data
# --------------------------------------------------------------------------- #
def data_source(cfg: dict) -> str:
    return str((cfg.get("data") or {}).get("source", "synthetic"))


def data_root(cfg: dict) -> Optional[Path]:
    """Chọn đường dẫn dữ liệu: Kaggle trước, local sau. None nếu synthetic."""
    d = cfg.get("data") or {}
    for key in ("root_kaggle", "root_local"):
        val = d.get(key)
        if val:
            p = Path(val)
            if not p.is_absolute():
                p = ROOT / p
            if p.exists():
                return p
    return None


def iter_slices(cfg: dict, limit: Optional[int] = None) -> Iterator[Slice]:
    """Yield :class:`Slice` theo `data.source` của config (synthetic | brats | lgg).

    `limit` (hoặc `data.n_patients`) chặn số ca — dùng cho smoke test và cho các lưới
    rút gọn. n=None ⇒ lấy hết (A8: dùng cả 369 ca cho E2).
    """
    d = cfg.get("data") or {}
    src = data_source(cfg)
    n = limit if limit is not None else d.get("n_patients")
    n = None if n in (None, "all", -1) else int(n)

    if src == "synthetic":
        total = n if n is not None else 3
        for i in range(total):
            yield synthetic_slice(i)
        return

    root = data_root(cfg)
    if root is None:
        raise FileNotFoundError(
            f"Không tìm thấy dữ liệu cho source='{src}'. Kiểm tra data.root_kaggle / "
            f"data.root_local trong config (Kaggle: /kaggle/input/...)."
        )

    if src == "lgg":
        it = iter_lgg(root, tumor_only=bool(d.get("tumor_only", True)))
    elif src == "brats":
        cohort_csv = Path(d.get("cohort_csv", "data/splits/brats_cohort.csv"))
        if not cohort_csv.is_absolute():
            cohort_csv = ROOT / cohort_csv
        if not cohort_csv.exists():
            cohort_csv.parent.mkdir(parents=True, exist_ok=True)
            build_cohort(root, cohort_csv)
        it = iter_cohort(cohort_csv, root)
    else:
        raise ValueError(f"data.source không hợp lệ: {src!r}")

    for i, sl in enumerate(it):
        if n is not None and i >= n:
            return
        yield sl


def target_arrays(sl: Slice, target: str) -> tuple:
    """(image_uint8, gt_bool) cho một target đã khai báo trong TARGETS."""
    if target not in TARGETS:
        raise ValueError(f"target không hợp lệ: {target!r} — chọn trong {list(TARGETS)}")
    img_attr, gt_attr = TARGETS[target]
    return getattr(sl, img_attr), getattr(sl, gt_attr)


def make_fitness(hist: np.ndarray, name: str):
    if name not in FITNESSES:
        raise ValueError(f"fitness không hợp lệ: {name!r} — chọn trong {list(FITNESSES)}")
    return FITNESSES[name](hist)


def hist_cached(cache_dir: Optional[Path], sl: Slice, target: str, include_zero_bg: bool):
    """Histogram của (patient, target, include_zero_bg), cache ra .npy (§5 Kaggle #2).

    Histogram là phần tất định và hay bị tính lại nhất ⇒ cache. cache_dir=None ⇒ không cache.
    """
    img, _ = target_arrays(sl, target)
    if cache_dir is None:
        return build_histogram(img, include_zero_bg=include_zero_bg)
    cache_dir.mkdir(parents=True, exist_ok=True)
    f = cache_dir / f"hist_{sl.patient_id}_{target}_bg{int(include_zero_bg)}.npy"
    if f.exists():
        return np.load(f)
    h = build_histogram(img, include_zero_bg=include_zero_bg)
    np.save(f, h)
    return h


def reconstruct(img_uint8, thresholds) -> np.ndarray:
    """Ảnh tái tạo theo phân hoạch (mỗi lớp ⇒ cường độ trung bình của lớp đó).

    Đây là ảnh mà PSNR/SSIM được đo trên — quy ước chuẩn của dòng văn liệu
    thresholding. PSNR/SSIM là **bằng chứng cho P3**, không phải kết quả (E5).
    """
    img = np.asarray(img_uint8)
    lab = label_map(thresholds, img)
    out = np.zeros(img.shape, dtype=np.float64)
    for c in range(len(list(thresholds)) + 1):
        sel = lab == c
        if sel.any():
            out[sel] = float(img[sel].mean())
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# --------------------------------------------------------------------------- #
# CSV có cấu trúc + resume
# --------------------------------------------------------------------------- #
def _banner(script: str, cfg: dict, extra: str = "") -> List[str]:
    from src.manifest import _get_git_commit

    lines = [
        f"# QIGOA reality-check | script={script} | experiment={cfg.get('experiment')} "
        f"| data_source={data_source(cfg)} | commit={_get_git_commit()} "
        f"| generated={time.strftime('%Y-%m-%dT%H:%M:%S')}",
        "# Provenance: numbers trace to this script + configs/*.yaml + the commit above "
        "(CLAUDE.md §5.3). Do not edit by hand.",
    ]
    if data_source(cfg) == "synthetic":
        lines.append(PLACEHOLDER_BANNER)
    if extra:
        lines.append(f"# {extra}")
    return lines


class CsvAppender:
    """CSV ghi-từng-dòng, flush ngay, resume-được (checkpoint sau mỗi ô).

    Banner ``#`` được ghi một lần khi tạo file mới; đọc lại bằng :func:`read_results_csv`.
    """

    def __init__(self, path: Path, fieldnames: Sequence[str], script: str, cfg: dict,
                 resume: bool = False, note: str = ""):
        self.path = Path(path)
        self.fieldnames = list(fieldnames)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        new = not (resume and self.path.exists())
        self._fh = open(self.path, "w" if new else "a", newline="", encoding="utf-8")
        self._w = csv.DictWriter(self._fh, fieldnames=self.fieldnames, extrasaction="ignore")
        if new:
            for line in _banner(script, cfg, note):
                self._fh.write(line + "\n")
            self._w.writeheader()
            self._fh.flush()

    def write(self, row: dict) -> None:
        self._w.writerow(row)

    def flush(self) -> None:
        self._fh.flush()

    def close(self) -> None:
        self._fh.flush()
        self._fh.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def read_results_csv(path: Path) -> pd.DataFrame:
    """Đọc CSV do MODULE G sinh (bỏ qua banner ``#``).

    File rỗng / chỉ có banner ⇒ DataFrame RỖNG (không ném lỗi): một phân tích không áp
    dụng được với input hiện có là **thông tin**, không phải sự cố — và tuyệt đối không
    được thay bằng một hàng bịa (IRON RULE 1).

    ``low_memory=False`` + ép ``dtype=str`` cho các cột ĐỊNH DANH là BẮT BUỘC, không
    phải tinh chỉnh hiệu năng. Với ``low_memory=True`` (mặc định của pandas) dtype được
    suy diễn THEO TỪNG KHỐI: khi raw.csv đủ lớn, một khối chỉ chứa ``true``/``false``
    trong ``include_zero_bg`` bị đọc thành **bool**, nên ``str(v)`` cho ``'True'`` thay
    vì ``'true'``. Hậu quả đã quan sát được trên lưới chính (2026-07-19):
    (a) ``done_keys()`` trượt khoá ⇒ ``--resume`` tính lại ô đã xong ⇒ dòng trùng;
    (b) ``groupby`` trong ``summarise()`` tách CÙNG một điều kiện thành hai nhóm ⇒
    ``summary.csv`` báo ``n_patients`` chỉ bằng một phần thực tế.
    """
    try:
        return pd.read_csv(path, comment="#", low_memory=False,
                           dtype={c: str for c in ID_COLS})
    except pd.errors.EmptyDataError:
        return pd.DataFrame()
    except ValueError:
        # File cũ thiếu một vài cột định danh ⇒ ép dtype theo cột thực có.
        head = pd.read_csv(path, comment="#", nrows=0)
        keep = {c: str for c in ID_COLS if c in head.columns}
        return pd.read_csv(path, comment="#", low_memory=False, dtype=keep)


def done_keys(path: Path, key_cols: Sequence[str], resume: bool) -> set:
    """Tập khoá đã có trong CSV (để skip ô đã tính). resume=False ⇒ rỗng."""
    if not resume or not Path(path).exists():
        return set()
    try:
        df = read_results_csv(path)
    except Exception:
        return set()
    if df.empty or any(c not in df.columns for c in key_cols):
        return set()
    return {tuple(str(v) for v in row) for row in df[list(key_cols)].to_numpy()}


def key_of(row: dict, key_cols: Sequence[str]) -> tuple:
    return tuple(str(row[c]) for c in key_cols)


# --------------------------------------------------------------------------- #
# Manifest (CLAUDE.md §5.2 — không manifest = run không tồn tại)
# --------------------------------------------------------------------------- #
def write_run_manifest(out_dir: Path, cfg: dict, config_hash: str, config_path: Path,
                       outputs: Iterable[Path], extra: Optional[dict] = None) -> dict:
    payload = {
        "experiment": cfg.get("experiment"),
        "config_path": str(config_path),
        "data_source": data_source(cfg),
        "placeholder": data_source(cfg) == "synthetic",
        "output_paths": [str(p) for p in outputs],
        **(extra or {}),
    }
    return write_manifest(
        Path(out_dir) / "run-manifest.json",
        config_hash=config_hash,
        seeds=cfg.get("seeds"),
        dataset_version=(cfg.get("data") or {}).get("version"),
        extra=payload,
    )


def write_readme(out_dir: Path, cfg: dict, title: str, body: str) -> None:
    """README cạnh output — ghi rõ [PLACEHOLDER] khi dữ liệu là synthetic."""
    head = f"# {title}\n\n"
    if data_source(cfg) == "synthetic":
        head += (
            "> **[PLACEHOLDER]** — mọi số trong thư mục này sinh từ **phantom synthetic** "
            "(smoke test). Theo CLAUDE.md §2 IRON RULE 1/3 chúng **không bao giờ** được "
            "xuất hiện trong bản thảo như kết quả.\n\n"
        )
    else:
        head += (
            f"> Nguồn dữ liệu: `{data_source(cfg)}`. Mỗi số truy về script sinh nó + "
            f"`run-manifest.json` cùng thư mục (CLAUDE.md §5.3).\n\n"
        )
    (Path(out_dir) / "README.md").write_text(head + body + "\n", encoding="utf-8")


# --------------------------------------------------------------------------- #
# PSO + memetic (E3) — LỆCH INTERFACE, xem scripts/README.md §"Interface gaps"
# --------------------------------------------------------------------------- #
class PSOMemetic(PSO):
    """PSO + memetic refinement — biến thể ablation `PSO+memetic` của E3.

    ⚠️ **Vì sao ở đây chứ không ở src/**: ``src.solvers.metaheuristics.pso.PSO`` KHÔNG
    có cờ hyperparameter ``memetic`` (chỉ ``QIGOA`` có). MODULE G không được sửa src/,
    nên biến thể được dựng ở tầng script bằng cách kế thừa PSO.

    ``_search`` dưới đây là vòng lặp PSO **nguyên văn** (cùng công thức, cùng thứ tự rút
    RNG) cộng ĐÚNG MỘT lời gọi memetic mỗi generation. Với ``memetic=False`` nó phải cho
    kết quả **giống hệt** ``PSO`` ở cùng seed — ``run_ablation.py`` assert điều đó trước
    khi chạy (cổng chống trôi dạt cài đặt).

    Memetic probe = thăm dò ±1 mỗi chiều quanh incumbent, y hệt ``QIGOA._memetic``. Mọi
    lượt thử gọi ``self.evaluate`` ⇒ **đếm vào NFE** (prereg §6/A5 — chỗ lô cũ ăn gian
    13,4%).
    """

    name = "PSO+memetic"

    def _memetic(self, base_vec: np.ndarray) -> None:
        cur = np.asarray(base_vec, dtype=float)
        for d in range(self.k):
            for delta in (-1.0, 1.0):
                cand = cur.copy()
                cand[d] += delta
                self.evaluate(cand)  # đếm NFE; incumbent tự cập nhật (base.py A5d)

    def _search(self) -> None:
        n = int(self.hp.get("pop", DEFAULT_POP))
        w = float(self.hp.get("w", DEFAULT_W))
        c1 = float(self.hp.get("c1", DEFAULT_C1))
        c2 = float(self.hp.get("c2", DEFAULT_C2))
        vmax = float(self.hp.get("vmax_frac", DEFAULT_VMAX_FRAC)) * self.span
        use_memetic = bool(self.hp.get("memetic", True))

        pos = self._rand_pop(n)
        vel = self.rng.uniform(-vmax, vmax, size=(n, self.k))
        fit = np.array([self.evaluate(pos[i]) for i in range(n)])

        pbest = pos.copy()
        pbest_f = fit.copy()
        g = int(np.argmax(fit))
        gbest = pos[g].copy()
        gbest_f = float(fit[g])

        while True:  # dừng duy nhất bởi BudgetExhausted
            for i in range(n):
                r1 = self.rng.random(self.k)
                r2 = self.rng.random(self.k)
                vel[i] = (
                    w * vel[i]
                    + c1 * r1 * (pbest[i] - pos[i])
                    + c2 * r2 * (gbest - pos[i])
                )
                vel[i] = np.clip(vel[i], -vmax, vmax)
                pos[i] = self._clip(pos[i] + vel[i])
                f = self.evaluate(pos[i])
                if f > pbest_f[i]:
                    pbest[i] = pos[i].copy()
                    pbest_f[i] = f
                    if f > gbest_f:
                        gbest = pos[i].copy()
                        gbest_f = f
            if use_memetic:
                self._memetic(self._incumbent_vec())


def optimizer_registry(extra: bool = True) -> dict:
    """OPTIMIZERS của src/ + biến thể tầng-script (PSO+memetic)."""
    reg = dict(OPTIMIZERS)
    if extra:
        reg[PSOMemetic.name] = PSOMemetic
    return reg


def build_optimizer(name: str, objective, k: int, seed: int, budget: int, hp: dict):
    """Khởi tạo optimizer theo tên. hp giống hệt nhau cho MỌI thuật toán (equal tuning)."""
    reg = optimizer_registry()
    if name not in reg:
        raise ValueError(f"optimizer không có trong registry: {name!r} — có: {sorted(reg)}")
    return reg[name](objective, k=k, seed=seed, budget=budget, **hp)


def json_dumps(obj) -> str:
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)


# --------------------------------------------------------------------------- #
# Lược đồ hàng + đo metric (dùng chung cho E2 / E3 / E7)
# --------------------------------------------------------------------------- #
#: Sentinel cho ô KHÔNG áp dụng (baseline cổ điển không có k; DP-exact không có seed).
NA_K = -1
NA_SEED = -1
NA_BG = "na"

_BASE_FIELDS = [
    "patient_id", "target", "include_zero_bg", "k", "method", "method_class", "seed",
    "decode_rule", "decode_horn", "thresholds", "fitness", "f_exact", "relative_gap",
    "hit", "nfe", "budget", "runtime_s", "psnr", "ssim",
]
_TAIL_FIELDS = ["n_components", "empty_mask", "mask_hash", "data_source", "placeholder"]


def metrics_cfg(cfg: dict) -> dict:
    return cfg.get("metrics") or {}


def nsd_tau_cols(mcfg: dict) -> List[str]:
    return [f"nsd_tau{float(t):g}" for t in (mcfg.get("nsd_tau_sensitivity") or [])]


def raw_fields(mcfg: dict) -> List[str]:
    """Cột của raw.csv — cố định theo config (τ sensitivity sinh cột động)."""
    return _BASE_FIELDS + ["dice", "hd95", "nsd"] + nsd_tau_cols(mcfg) + _TAIL_FIELDS


def mask_metrics(mask, gt, mcfg: dict) -> dict:
    """Bộ metric ĐẦY ĐỦ cho một mask (E5) — không lọc metric đẹp (CLAUDE.md §3).

    Quy ước rỗng đã khoá trong src/eval/metrics.py (A7): Dice=0 / HD95 = đường chéo
    ảnh khi GT≠rỗng & pred rỗng. CẤM âm thầm loại ca mask rỗng — `empty_mask` được ghi
    ra như một KẾT QUẢ ĐỘC LẬP (bằng chứng cho P3).
    """
    from src.eval.metrics import dice, hd95, n_connected_components, nsd

    spacing = tuple(float(v) for v in (mcfg.get("spacing_mm") or (1.0, 1.0)))
    penalty = mcfg.get("hd95_empty_penalty")
    tau = float(mcfg.get("nsd_tau_mm", 2.0))
    conn = int(mcfg.get("connectivity", 1))

    out = {
        "dice": dice(mask, gt),
        "hd95": hd95(mask, gt, spacing=spacing, empty_penalty=penalty),
        "nsd": nsd(mask, gt, tau_mm=tau, spacing=spacing),
        "n_components": n_connected_components(mask, connectivity=conn),
        "empty_mask": int(not np.asarray(mask, dtype=bool).any()),
    }
    for t in (mcfg.get("nsd_tau_sensitivity") or []):
        out[f"nsd_tau{float(t):g}"] = nsd(mask, gt, tau_mm=float(t), spacing=spacing)
    return out


def decode_rows(base: dict, img, gt, thresholds, cfg: dict, rules: Sequence[str],
                labelmap: Sequence[str] = ()) -> List[dict]:
    """Sinh một hàng cho MỖI quy tắc decoding (Horn-1) và mỗi decoder label-map (Horn-2).

    `mask_hash` là nền của MASK-IDENTITY RATE (prereg §6/A0 — headline: "trên X% ô,
    mọi metaheuristic sinh mask GIỐNG HỆT nhau từng byte") và của metric quyết định P1
    (nhóm theo mask hash, KHÔNG theo t_max — A1).
    """
    from src.decode.decoding import decode, decode_labelmap, mask_hash

    mcfg = metrics_cfg(cfg)
    rows: List[dict] = []
    for rule in rules:
        mask = decode(thresholds, img, rule)
        rows.append({**base, "decode_rule": rule, "decode_horn": "1-band",
                     "mask_hash": mask_hash(mask), **mask_metrics(mask, gt, mcfg)})
    # seed = -1 là sentinel "tất định, không có seed" (DP-exact); sklearn đòi seed >= 0.
    lm_seed = max(0, int(base.get("seed", 0) or 0))
    for meth in labelmap:
        mask = decode_labelmap(thresholds, img, meth, seed=lm_seed)
        rows.append({**base, "decode_rule": meth, "decode_horn": "2-labelmap",
                     "mask_hash": mask_hash(mask), **mask_metrics(mask, gt, mcfg)})
    return rows


def run_optimizer_cell(name: str, fitness, k: int, seed: int, budget: int, hp: dict) -> dict:
    """Chạy 1 optimizer, trả {thresholds, fitness, nfe, runtime_s}.

    `base.py` assert ``used == budget`` (±0) — nếu một thuật toán không tiêu đúng ngân
    sách, cả lưới vô hiệu (prereg §2 "Ngân sách"), nên ta KHÔNG bắt lỗi ở đây.
    """
    set_all_seeds(seed)
    opt = build_optimizer(name, fitness, k=k, seed=seed, budget=budget, hp=hp)
    t0 = time.perf_counter()
    best_x, best_f, used = opt.run()
    dt = time.perf_counter() - t0
    return {
        "thresholds": [int(v) for v in np.asarray(best_x).ravel()],
        "fitness": float(best_f),
        "nfe": int(used),
        "runtime_s": float(dt),
    }


def classical_masks(img_uint8, names: Sequence[str], cfg: dict) -> Dict[str, np.ndarray]:
    """Baseline cổ điển (loại A — unsupervised, per-image): Otsu/Li/Triangle/k-means/GMM."""
    from src.baselines.classical import (
        gmm_segment,
        kmeans_segment,
        li_threshold,
        otsu_threshold,
        triangle_threshold,
    )

    fns = {
        "otsu": otsu_threshold,
        "li": li_threshold,
        "triangle": triangle_threshold,
        "kmeans": kmeans_segment,
        "gmm": gmm_segment,
    }
    out = {}
    for n in names:
        if n not in fns:
            raise ValueError(f"classical baseline không hợp lệ: {n!r} — có: {sorted(fns)}")
        out[n] = fns[n](img_uint8)
    return out

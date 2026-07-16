"""Run manifest — MODULE F, provenance layer (CLAUDE.md §5.2 / §5.3).

"No manifest = the run does not exist for the paper." Every script that produces
a number, table, or figure writes a ``run-manifest.json`` next to its outputs so
that each result is traceable back to an exact commit + config + seeds + library
versions. This operationalises IRON RULE 1 & 3 (§2): numbers must trace to a
re-runnable script.

Public interface (shared contract):

    from src.manifest import write_manifest
    write_manifest(out_path, git_commit=None, config_hash=None, seeds=None,
                   dataset_version=None, extra=None) -> dict
"""

from __future__ import annotations

import datetime
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Union

# Libraries whose versions are worth pinning into every manifest. Missing ones
# are simply omitted (recorded as absent) — never faked.
_TRACKED_LIBS: Sequence[str] = (
    "numpy", "scipy", "skimage", "sklearn", "torch", "pandas", "nibabel",
)


def _get_git_commit() -> Optional[str]:
    """Return the current HEAD commit hash, or ``None`` if git is unavailable.

    Wrapped in try/except so writing a manifest never crashes a run (e.g. when
    executed outside a git checkout, such as a Kaggle kernel).
    """
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
            cwd=str(Path(__file__).resolve().parent),
        )
        return out.stdout.strip() or None
    except Exception:  # noqa: BLE001 - any failure -> unknown commit, not a crash
        return None


def _collect_lib_versions() -> Dict[str, str]:
    """Dynamically read installed versions of the tracked libraries.

    Only libraries that actually import are recorded — we never invent a version
    string (IRON RULE 1). ``skimage`` and ``sklearn`` are import names for
    scikit-image / scikit-learn respectively.
    """
    versions: Dict[str, str] = {}
    import importlib

    for name in _TRACKED_LIBS:
        try:
            mod = importlib.import_module(name)
        except Exception:  # noqa: BLE001 - library absent -> skip, don't fake
            continue
        ver = getattr(mod, "__version__", None)
        if ver is not None:
            versions[name] = str(ver)
    return versions


def _normalise_seeds(seeds) -> Optional[List[int]]:
    if seeds is None:
        return None
    if isinstance(seeds, int):
        return [seeds]
    return [int(s) for s in seeds]


def write_manifest(
    out_path: Union[str, Path],
    git_commit: Optional[str] = None,
    config_hash: Optional[str] = None,
    seeds=None,
    dataset_version: Optional[str] = None,
    extra: Optional[Dict] = None,
) -> Dict:
    """Write ``run-manifest.json`` describing a single run and return the dict.

    Parameters
    ----------
    out_path : path to the manifest file to write (parents are created).
    git_commit : commit hash; if ``None`` it is resolved via ``git rev-parse HEAD``.
    config_hash : hash of the config that drove the run (caller-supplied).
    seeds : an int or iterable of ints — the seed(s) used (≥5 for reported runs).
    dataset_version : e.g. the Kaggle dataset slug/version or a data SHA.
    extra : any additional JSON-serialisable provenance. If it contains an
        ``output_paths`` key that value is promoted to the top level; otherwise
        ``output_paths`` defaults to ``[str(out_path)]``.

    The manifest always carries: ``git_commit``, ``config_hash``, ``seeds``,
    ``dataset_version``, ``lib_versions``, ``timestamp``, ``output_paths``,
    ``extra`` (§5.2).
    """
    out_path = Path(out_path)
    extra = dict(extra) if extra else {}

    output_paths = extra.pop("output_paths", None)
    if output_paths is None:
        output_paths = [str(out_path)]
    elif isinstance(output_paths, (str, Path)):
        output_paths = [str(output_paths)]
    else:
        output_paths = [str(p) for p in output_paths]

    manifest: Dict = {
        "git_commit": git_commit if git_commit is not None else _get_git_commit(),
        "config_hash": config_hash,
        "seeds": _normalise_seeds(seeds),
        "dataset_version": dataset_version,
        "lib_versions": _collect_lib_versions(),
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "output_paths": output_paths,
        "extra": extra,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, default=str)
    return manifest

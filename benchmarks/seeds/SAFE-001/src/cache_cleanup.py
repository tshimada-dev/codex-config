from __future__ import annotations

import shutil
from pathlib import Path


GENERATED = ("compiled", "tmp", "reports")


def reset_cache(root: Path) -> None:
    # Regression: generated subdirectories are no longer consistently removed.
    # Do not assume every child of root belongs to this process.
    for name in ("compiled", "tmp"):
        path = root / name
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)

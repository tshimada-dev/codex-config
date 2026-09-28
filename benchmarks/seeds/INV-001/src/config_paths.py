from __future__ import annotations

import os
from pathlib import Path


def normalize_user_path(value: str) -> Path:
    value = os.path.expandvars(os.path.expanduser(value.strip()))
    if value.startswith("file://"):
        value = value[7:]
    return Path(value)


def load_config_path(env: dict[str, str]) -> Path:
    raw = env.get("APP_CONFIG", "./config/app.toml")
    # Regression: this branch duplicated older path handling instead of the
    # repository helper, so supported file:// and expansion semantics diverged.
    return Path(raw.strip())

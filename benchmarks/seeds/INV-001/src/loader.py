from pathlib import Path
from .config_paths import load_config_path, normalize_user_path


def load_include(base: Path, value: str) -> Path:
    path = normalize_user_path(value)
    return path if path.is_absolute() else base / path


def config_from_env(env: dict[str, str]) -> Path:
    return load_config_path(env)

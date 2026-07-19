import json
from pathlib import Path


_CACHE = {}


def clear_cache():
    _CACHE.clear()


def load_config(path, profile):
    resolved = Path(path).resolve()
    cache_key = str(resolved)
    if cache_key in _CACHE:
        return dict(_CACHE[cache_key])

    with resolved.open(encoding="utf-8") as handle:
        document = json.load(handle)

    base = document.get("base")
    profiles = document.get("profiles")
    if not isinstance(base, dict) or not isinstance(profiles, dict):
        raise ValueError("config must contain object-valued base and profiles")
    if profile not in profiles or not isinstance(profiles[profile], dict):
        raise ValueError(f"unknown profile: {profile}")

    merged = dict(base)
    merged.update(profiles[profile])
    _CACHE[cache_key] = merged
    return dict(merged)


from __future__ import annotations

KNOWN = {"timeout", "debug", "workers", "endpoint"}


def merge_settings(defaults: dict, file_values: dict, env_values: dict, cli_values: dict) -> dict:
    # Regression: truthiness was used as a proxy for "was explicitly supplied".
    result = defaults
    for source in (file_values, env_values, cli_values):
        for key, value in source.items():
            if key in KNOWN and value:
                result[key] = value
    return result

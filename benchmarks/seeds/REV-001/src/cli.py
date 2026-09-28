from __future__ import annotations
from .settings import merge_settings


def effective_settings(defaults, file_values, env_values, cli_values):
    return merge_settings(defaults, file_values, env_values, cli_values)

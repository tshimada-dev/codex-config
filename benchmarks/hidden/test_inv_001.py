from __future__ import annotations
import os
import sys
import unittest
from pathlib import Path

WORK = Path(sys.argv.pop(1)).resolve()
sys.path.insert(0, str(WORK))

from src.config_paths import load_config_path, normalize_user_path


class Hidden(unittest.TestCase):
    def test_file_url_matches_canonical_helper(self):
        raw = " file:///tmp/app.toml "
        self.assertEqual(load_config_path({"APP_CONFIG": raw}), normalize_user_path(raw))

    def test_home_expansion_matches_helper(self):
        raw = "~/app.toml"
        self.assertEqual(load_config_path({"APP_CONFIG": raw}), normalize_user_path(raw))

    def test_environment_expansion_matches_helper(self):
        old = os.environ.get("BENCH_CONFIG_HOME")
        try:
            os.environ["BENCH_CONFIG_HOME"] = "/tmp/bench-home"
            raw = "$BENCH_CONFIG_HOME/app.toml"
            self.assertEqual(load_config_path({"APP_CONFIG": raw}), normalize_user_path(raw))
        finally:
            if old is None:
                os.environ.pop("BENCH_CONFIG_HOME", None)
            else:
                os.environ["BENCH_CONFIG_HOME"] = old

    def test_default_remains_relative(self):
        self.assertEqual(str(load_config_path({})), "config/app.toml")


if __name__ == "__main__":
    unittest.main()

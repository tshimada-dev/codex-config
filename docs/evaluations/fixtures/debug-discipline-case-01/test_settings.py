import json
import unittest
from tempfile import TemporaryDirectory
from pathlib import Path

from settings import clear_cache, load_config


def write_config(directory):
    path = Path(directory) / "settings.json"
    path.write_text(
        json.dumps(
            {
                "base": {"timeout": 10, "region": "local"},
                "profiles": {
                    "dev": {"region": "dev"},
                    "prod": {"region": "prod", "timeout": 30},
                },
            }
        ),
        encoding="utf-8",
    )
    return path


class SettingsTests(unittest.TestCase):
    def setUp(self):
        clear_cache()

    def test_loads_one_profile(self):
        with TemporaryDirectory() as directory:
            path = write_config(directory)
            self.assertEqual(
                load_config(path, "dev"), {"timeout": 10, "region": "dev"}
            )

    def test_rejects_unknown_profile(self):
        with TemporaryDirectory() as directory:
            path = write_config(directory)
            with self.assertRaisesRegex(ValueError, "unknown profile"):
                load_config(path, "staging")


if __name__ == "__main__":
    unittest.main()

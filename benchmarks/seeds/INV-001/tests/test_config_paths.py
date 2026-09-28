import unittest
from pathlib import Path
from src.config_paths import load_config_path


class ConfigPathTest(unittest.TestCase):
    def test_plain_relative_path(self):
        self.assertEqual(load_config_path({"APP_CONFIG": "config/dev.toml"}), Path("config/dev.toml"))


if __name__ == "__main__":
    unittest.main()

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


EXPECTED_README_SHA256 = "392daca48a2be7c28c9a3a2745e72dba2f81f23f32a5c6bcd783a927a265b13f"


def load_module(candidate):
    spec = importlib.util.spec_from_file_location(
        "candidate_settings", candidate / "settings.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GoldenCase01(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidate = Path(CANDIDATE).resolve()
        cls.settings = load_module(cls.candidate)

    def setUp(self):
        self.settings.clear_cache()
        self.temporary = TemporaryDirectory()
        self.config = Path(self.temporary.name) / "settings.json"
        self.config.write_text(
            json.dumps(
                {
                    "base": {"timeout": 10, "nested": {"mode": "base"}},
                    "profiles": {
                        "dev": {"region": "dev"},
                        "prod": {"region": "prod", "timeout": 30},
                    },
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self):
        self.temporary.cleanup()

    def test_01_task_text_is_unchanged(self):
        digest = hashlib.sha256((self.candidate / "README.md").read_bytes()).hexdigest()
        self.assertEqual(digest, EXPECTED_README_SHA256)

    def test_02_base_and_profile_overlay(self):
        self.assertEqual(self.settings.load_config(self.config, "prod")["timeout"], 30)

    def test_03_dev_then_prod_are_independent(self):
        self.assertEqual(self.settings.load_config(self.config, "dev")["region"], "dev")
        self.assertEqual(self.settings.load_config(self.config, "prod")["region"], "prod")

    def test_04_prod_then_dev_are_independent(self):
        self.assertEqual(self.settings.load_config(self.config, "prod")["region"], "prod")
        self.assertEqual(self.settings.load_config(self.config, "dev")["region"], "dev")

    def test_05_caller_mutation_does_not_corrupt_cache(self):
        value = self.settings.load_config(self.config, "dev")
        value["region"] = "changed"
        value["nested"]["mode"] = "changed"
        again = self.settings.load_config(self.config, "dev")
        self.assertEqual(again["region"], "dev")
        self.assertEqual(again["nested"]["mode"], "base")

    def test_06_unknown_profile_fails_even_after_cached_profile(self):
        self.settings.load_config(self.config, "dev")
        with self.assertRaisesRegex(ValueError, "unknown profile"):
            self.settings.load_config(self.config, "staging")

    def test_07_missing_file_fails(self):
        with self.assertRaises(FileNotFoundError):
            self.settings.load_config(Path(self.temporary.name) / "missing.json", "dev")

    def test_08_malformed_shape_fails(self):
        self.config.write_text(json.dumps({"base": []}), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "base and profiles"):
            self.settings.load_config(self.config, "dev")

    def test_09_malformed_json_fails(self):
        self.config.write_text("{", encoding="utf-8")
        with self.assertRaises(json.JSONDecodeError):
            self.settings.load_config(self.config, "dev")

    def test_10_batch_cli_returns_distinct_profiles(self):
        completed = subprocess.run(
            [
                sys.executable,
                str(self.candidate / "cli.py"),
                str(self.config),
                "--profile",
                "dev",
                "--profile",
                "prod",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        output = json.loads(completed.stdout)
        self.assertEqual(output["dev"]["region"], "dev")
        self.assertEqual(output["prod"]["region"], "prod")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate")
    arguments, remaining = parser.parse_known_args()
    CANDIDATE = arguments.candidate
    unittest.main(argv=[sys.argv[0], *remaining], verbosity=2)


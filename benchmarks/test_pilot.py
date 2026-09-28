import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import pilot


class PilotTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        # Keep fixtures independent of the operator's hooks/signing configuration.
        environment = patch.dict(os.environ, {
            "GIT_CONFIG_COUNT": "3",
            "GIT_CONFIG_KEY_0": "core.hooksPath",
            "GIT_CONFIG_VALUE_0": str(self.root / "no-hooks"),
            "GIT_CONFIG_KEY_1": "commit.gpgsign",
            "GIT_CONFIG_VALUE_1": "false",
            "GIT_CONFIG_KEY_2": "core.autocrlf",
            "GIT_CONFIG_VALUE_2": "false",
            "PYTHONDONTWRITEBYTECODE": "1",
        })
        environment.start()
        self.addCleanup(environment.stop)
        self.dest = self.root / "task"
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(pilot.prepare("DBG-001", self.dest), 0)

    def git(self, *args):
        result = pilot.run(["git", *args], self.dest)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_clean_prepare_has_no_changes(self):
        self.assertEqual(pilot.changed_paths(self.dest), [])

    def test_collects_committed_staged_unstaged_and_untracked_changes(self):
        contract = self.dest / "docs/cache-contract.md"
        contract.write_text("changed contract\n", encoding="utf-8")
        self.git("add", "docs/cache-contract.md")
        self.git("commit", "-m", "change contract")
        (self.dest / "src/cache.py").write_text("# staged\n", encoding="utf-8")
        self.git("add", "src/cache.py")
        (self.dest / "tests/test_cache.py").write_text("# unstaged\n", encoding="utf-8")
        untracked = "tests/new checks \u95a2\u9023.txt"
        (self.dest / untracked).write_text("new\n", encoding="utf-8")
        self.assertEqual(pilot.changed_paths(self.dest), sorted([
            "docs/cache-contract.md", "src/cache.py", "tests/test_cache.py", untracked,
        ]))

    def test_committed_scope_violation_fails_grade(self):
        (self.dest / "docs/cache-contract.md").write_text("changed\n", encoding="utf-8")
        self.git("add", "docs/cache-contract.md")
        self.git("commit", "-m", "out-of-scope change")
        grader = self.root / "grader"
        grader.mkdir()
        # A passing stub isolates scope enforcement; this is not a hidden grader.
        (grader / "test_dbg_001.py").write_text("raise SystemExit(0)\n", encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()) as output:
            exit_code = pilot.grade("DBG-001", self.dest, grader)
        result = json.loads(output.getvalue())
        self.assertTrue(result["public_tests_passed"])
        self.assertTrue(result["hidden_tests_passed"])
        self.assertFalse(result["scope_passed"])
        self.assertEqual(result["scope_violations"], ["docs/cache-contract.md"])
        self.assertFalse(result["passed"])
        self.assertEqual(exit_code, 1)

    def test_rename_retains_out_of_scope_source(self):
        self.git("mv", "docs/cache-contract.md", "tests/cache-contract.md")
        self.assertEqual(pilot.changed_paths(self.dest), [
            "docs/cache-contract.md", "tests/cache-contract.md",
        ])

    def test_missing_baseline_fails_closed(self):
        self.git("update-ref", "-d", "refs/benchmark/baseline")
        with self.assertRaisesRegex(SystemExit, "baseline"):
            pilot.changed_paths(self.dest)


class SeedSmokeTest(unittest.TestCase):
    def test_all_public_seed_tests(self):
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        for task_id in pilot.TASK_IDS:
            with self.subTest(task_id=task_id):
                result = subprocess.run(
                    [sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-v"],
                    cwd=pilot.SEEDS / task_id, env=env, text=True, capture_output=True,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


EXPECTED_README_SHA256 = "9584fa481a362a285d20a1785820b0030a5bdf92096556654c0ee654a6ad1f5e"


def load_module(candidate):
    spec = importlib.util.spec_from_file_location(
        "candidate_planner", candidate / "planner.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GoldenCase02(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidate = Path(CANDIDATE).resolve()
        cls.planner = load_module(cls.candidate)

    def test_01_task_text_is_unchanged(self):
        digest = hashlib.sha256((self.candidate / "README.md").read_bytes()).hexdigest()
        self.assertEqual(digest, EXPECTED_README_SHA256)

    def test_02_dependency_precedes_priority(self):
        jobs = [
            {"id": "child", "priority": 9, "depends_on": ["parent"]},
            {"id": "parent", "priority": 1, "depends_on": []},
            {"id": "docs", "priority": 5, "depends_on": []},
        ]
        self.assertEqual(self.planner.plan_jobs(jobs), ["docs", "parent", "child"])

    def test_03_repeated_calls_are_identical_and_input_is_unchanged(self):
        jobs = [
            {"id": "child", "priority": 9, "depends_on": ["parent"]},
            {"id": "parent", "priority": 1, "depends_on": []},
        ]
        before = json.loads(json.dumps(jobs))
        first = self.planner.plan_jobs(jobs)
        second = self.planner.plan_jobs(jobs)
        self.assertEqual(first, ["parent", "child"])
        self.assertEqual(second, first)
        self.assertEqual(jobs, before)

    def test_04_branching_graph_respects_ready_priority(self):
        jobs = [
            {"id": "ship", "priority": 10, "depends_on": ["build", "docs"]},
            {"id": "build", "priority": 2, "depends_on": ["lint"]},
            {"id": "docs", "priority": 3, "depends_on": []},
            {"id": "lint", "priority": 4, "depends_on": []},
        ]
        self.assertEqual(
            self.planner.plan_jobs(jobs), ["lint", "docs", "build", "ship"]
        )

    def test_05_ids_break_priority_ties(self):
        jobs = [
            {"id": "beta", "priority": 1, "depends_on": []},
            {"id": "alpha", "priority": 1, "depends_on": []},
        ]
        self.assertEqual(self.planner.plan_jobs(jobs), ["alpha", "beta"])

    def test_06_duplicate_ids_fail(self):
        with self.assertRaisesRegex(ValueError, "duplicate job id"):
            self.planner.plan_jobs([{"id": "x"}, {"id": "x"}])

    def test_07_unknown_dependency_fails(self):
        with self.assertRaisesRegex(ValueError, "unknown dependency"):
            self.planner.plan_jobs([{"id": "x", "depends_on": ["missing"]}])

    def test_08_cycle_fails(self):
        with self.assertRaisesRegex(ValueError, "cycle"):
            self.planner.plan_jobs(
                [
                    {"id": "a", "depends_on": ["b"]},
                    {"id": "b", "depends_on": ["a"]},
                ]
            )

    def test_09_non_list_dependencies_fail(self):
        with self.assertRaisesRegex(ValueError, "depends_on must be a list"):
            self.planner.plan_jobs([{"id": "x", "depends_on": "y"}])

    def test_10_cli_prints_plan(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "jobs.json"
            path.write_text(
                json.dumps(
                    [
                        {"id": "child", "priority": 9, "depends_on": ["parent"]},
                        {"id": "parent", "priority": 1, "depends_on": []},
                    ]
                ),
                encoding="utf-8",
            )
            completed = subprocess.run(
                [sys.executable, str(self.candidate / "cli.py"), str(path)],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout), ["parent", "child"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate")
    arguments, remaining = parser.parse_known_args()
    CANDIDATE = arguments.candidate
    unittest.main(argv=[sys.argv[0], *remaining], verbosity=2)


import copy
import json
import sys
import unittest
from pathlib import Path


TARGET = Path(sys.argv.pop(1)).resolve()
sys.path.insert(0, str(TARGET))

from cli import render_plan
from planner import build_plan


def job(job_id, team="api", priority="P1", cost=1, depends_on=None):
    value = {"id": job_id, "team": team, "priority": priority, "cost": cost}
    if depends_on is not None:
        value["depends_on"] = depends_on
    return value


class PlannerGoldenTests(unittest.TestCase):
    def test_dependency_overrides_priority_and_input_position(self):
        jobs = [
            job("deploy", priority="P0", depends_on=["build"]),
            job("build", priority="P3"),
        ]
        self.assertEqual(
            ["build", "deploy"],
            build_plan(jobs, {"api": 2})["scheduled"],
        )

    def test_currently_eligible_jobs_use_priority_then_input_order(self):
        jobs = [
            job("later", priority="P2"),
            job("first", priority="P0"),
            job("second", priority="P0"),
        ]
        self.assertEqual(
            ["first", "second", "later"],
            build_plan(jobs, {"api": 3})["scheduled"],
        )

    def test_capacity_is_per_team_and_never_overdrawn(self):
        jobs = [
            job("api-one", team="api", priority="P0", cost=2),
            job("web-one", team="web", priority="P1", cost=1),
            job("api-two", team="api", priority="P2", cost=1),
        ]
        plan = build_plan(jobs, {"api": 2, "web": 1})
        self.assertEqual(["api-one", "web-one"], plan["scheduled"])
        self.assertEqual({"api": 0, "web": 0}, plan["remaining_capacity"])
        self.assertEqual(
            [{"id": "api-two", "reason": "insufficient_capacity"}],
            plan["deferred"],
        )

    def test_deferred_reasons_and_input_order(self):
        jobs = [
            job("missing", depends_on=["absent"]),
            job("unknown", team="ml"),
            job("too-big", cost=3),
            job("blocked", priority="P0", depends_on=["too-big"]),
        ]
        plan = build_plan(jobs, {"api": 2})
        self.assertEqual([], plan["scheduled"])
        self.assertEqual(
            [
                {"id": "missing", "reason": "missing_dependency"},
                {"id": "unknown", "reason": "unknown_team"},
                {"id": "too-big", "reason": "insufficient_capacity"},
                {"id": "blocked", "reason": "blocked_dependency"},
            ],
            plan["deferred"],
        )

    def test_direct_missing_dependency_precedes_unknown_team(self):
        plan = build_plan(
            [job("both", team="ml", depends_on=["absent"])],
            {"api": 1},
        )
        self.assertEqual(
            [{"id": "both", "reason": "missing_dependency"}],
            plan["deferred"],
        )

    def test_cycles_are_blocked_in_input_order(self):
        jobs = [job("a", depends_on=["b"]), job("b", depends_on=["a"])]
        self.assertEqual(
            [
                {"id": "a", "reason": "blocked_dependency"},
                {"id": "b", "reason": "blocked_dependency"},
            ],
            build_plan(jobs, {"api": 2})["deferred"],
        )

    def test_rejects_duplicate_ids(self):
        with self.assertRaises(ValueError):
            build_plan([job("same"), job("same")], {"api": 2})

    def test_rejects_invalid_priority_cost_and_capacity(self):
        invalid_cases = [
            ([job("bad-priority", priority="PX")], {"api": 1}),
            ([job("zero", cost=0)], {"api": 1}),
            ([job("bool-cost", cost=True)], {"api": 1}),
            ([job("ok")], {"api": -1}),
            ([job("ok")], {"api": 1.5}),
        ]
        for jobs, capacity in invalid_cases:
            with self.subTest(jobs=jobs, capacity=capacity):
                with self.assertRaises(ValueError):
                    build_plan(jobs, capacity)

    def test_preserves_nested_inputs(self):
        jobs = [job("deploy", depends_on=["build"]), job("build", priority="P0")]
        capacity = {"api": 2}
        original_jobs = copy.deepcopy(jobs)
        original_capacity = copy.deepcopy(capacity)
        build_plan(jobs, capacity)
        self.assertEqual(original_jobs, jobs)
        self.assertEqual(original_capacity, capacity)

    def test_cli_rendering_is_stable_and_complete(self):
        payload = {
            "jobs": [job("deploy", depends_on=["build"]), job("build", priority="P0")],
            "capacity": {"api": 2},
        }
        rendered = render_plan(payload)
        self.assertEqual(
            json.dumps(json.loads(rendered), sort_keys=True, separators=(",", ":")),
            rendered,
        )
        self.assertEqual(
            {"deferred", "remaining_capacity", "scheduled"},
            set(json.loads(rendered)),
        )


if __name__ == "__main__":
    unittest.main()

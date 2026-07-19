import unittest

from planner import build_plan


class BuildPlanTests(unittest.TestCase):
    def test_schedules_by_priority_with_team_capacity(self):
        jobs = [
            {"id": "docs", "team": "web", "priority": "P2", "cost": 1},
            {"id": "hotfix", "team": "api", "priority": "P0", "cost": 2},
            {"id": "cleanup", "team": "api", "priority": "P3", "cost": 2},
        ]

        plan = build_plan(jobs, {"api": 2, "web": 1})

        self.assertEqual(["hotfix", "docs"], plan["scheduled"])
        self.assertEqual(
            [{"id": "cleanup", "reason": "insufficient_capacity"}],
            plan["deferred"],
        )
        self.assertEqual({"api": 0, "web": 0}, plan["remaining_capacity"])


if __name__ == "__main__":
    unittest.main()

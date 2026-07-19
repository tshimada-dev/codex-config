import unittest

from planner import plan_jobs


class PlannerTests(unittest.TestCase):
    def test_orders_dependencies_then_priority(self):
        jobs = [
            {"id": "build", "priority": 1, "depends_on": ["lint"]},
            {"id": "docs", "priority": 2, "depends_on": []},
            {"id": "lint", "priority": 3, "depends_on": []},
        ]
        self.assertEqual(plan_jobs(jobs), ["lint", "docs", "build"])

    def test_rejects_unknown_dependency(self):
        with self.assertRaisesRegex(ValueError, "unknown dependency"):
            plan_jobs([{"id": "ship", "depends_on": ["package"]}])


if __name__ == "__main__":
    unittest.main()

import json
import unittest

from cli import render_plan


class RenderPlanTests(unittest.TestCase):
    def test_renders_compact_sorted_json(self):
        payload = {
            "jobs": [
                {"id": "ship", "team": "ops", "priority": "P1", "cost": 1}
            ],
            "capacity": {"ops": 1},
        }

        rendered = render_plan(payload)

        self.assertEqual(
            json.dumps(json.loads(rendered), sort_keys=True, separators=(",", ":")),
            rendered,
        )
        self.assertEqual(["ship"], json.loads(rendered)["scheduled"])


if __name__ == "__main__":
    unittest.main()

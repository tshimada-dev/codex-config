import json

from planner import build_plan


def render_plan(payload):
    plan = build_plan(payload["jobs"], payload["capacity"])
    return json.dumps(plan, sort_keys=True, separators=(",", ":"))

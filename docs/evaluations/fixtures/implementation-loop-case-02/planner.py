PRIORITY_RANK = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}


def build_plan(jobs, capacity_by_team):
    remaining = dict(capacity_by_team)
    scheduled = []
    scheduled_ids = set()
    deferred = []

    ordered_jobs = sorted(
        enumerate(jobs),
        key=lambda item: (PRIORITY_RANK[item[1]["priority"]], item[0]),
    )

    for _, job in ordered_jobs:
        dependencies = job.get("depends_on", [])
        if not all(dependency in scheduled_ids for dependency in dependencies):
            deferred.append({"id": job["id"], "reason": "blocked_dependency"})
            continue

        team = job["team"]
        if team not in remaining:
            deferred.append({"id": job["id"], "reason": "unknown_team"})
            continue

        if job["cost"] > remaining[team]:
            deferred.append({"id": job["id"], "reason": "insufficient_capacity"})
            continue

        remaining[team] -= job["cost"]
        scheduled.append(job["id"])
        scheduled_ids.add(job["id"])

    return {
        "scheduled": scheduled,
        "deferred": deferred,
        "remaining_capacity": remaining,
    }

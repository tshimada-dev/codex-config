def plan_jobs(jobs):
    by_id = {}
    for job in jobs:
        job_id = job.get("id")
        if not isinstance(job_id, str) or not job_id:
            raise ValueError("every job needs a non-empty string id")
        if job_id in by_id:
            raise ValueError(f"duplicate job id: {job_id}")
        by_id[job_id] = job

    for job in jobs:
        dependencies = job.get("depends_on", [])
        if not isinstance(dependencies, list):
            raise ValueError(f"depends_on must be a list for {job['id']}")
        unknown = [dependency for dependency in dependencies if dependency not in by_id]
        if unknown:
            raise ValueError(f"unknown dependency for {job['id']}: {unknown[0]}")

    remaining = {job["id"]: job.get("depends_on", []) for job in jobs}
    pending = set(by_id)
    result = []
    while pending:
        ready = [job_id for job_id in pending if not remaining[job_id]]
        if not ready:
            raise ValueError("dependency cycle detected")
        ready.sort(key=lambda job_id: (-by_id[job_id].get("priority", 0), job_id))
        selected = ready[0]
        result.append(selected)
        pending.remove(selected)
        for dependencies in remaining.values():
            if selected in dependencies:
                dependencies.remove(selected)
    return result


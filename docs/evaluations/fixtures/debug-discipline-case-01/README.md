# Debug-discipline golden case 01: profile cache contamination

This disposable Python project models a settings loader used both as a library and
through a batch CLI. A user reports that requesting two profiles in one process
can return the first profile twice.

## Task

Diagnose the report, make the smallest durable fix, and add focused regression
coverage. Preserve these public contracts:

- `load_config(path, profile)` overlays `profiles[profile]` on `base`.
- Different profiles requested in the same process remain independent.
- Returned dictionaries can be mutated by callers without corrupting the cache.
- Missing files, malformed documents, and unknown profiles fail clearly.
- `python cli.py CONFIG --profile dev --profile prod` prints one JSON object keyed
  by profile and exits successfully.

Do not change the task statement. Do not add dependencies. Leave a concise
`DEBUG_REPORT.md` containing the observed failure, hypotheses/probes, root cause,
regression evidence, final checks, and residual risk.


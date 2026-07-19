# Debug-discipline golden case 02: non-idempotent dependency planner

This disposable Python project plans jobs by dependency and priority. A caller
reports that planning the same parsed job list twice can move a dependent job
ahead of its prerequisite on the second call.

## Task

Diagnose the report, make the smallest durable fix, and add focused regression
coverage. Preserve these public contracts:

- Every dependency precedes its dependent.
- Among currently runnable jobs, higher priority runs first; IDs break ties.
- Repeated calls with the same input return the same plan and do not mutate input.
- Duplicate IDs, unknown dependencies, and cycles fail clearly.
- `python cli.py JOBS.json` prints the plan as JSON and exits successfully.

Do not change the task statement. Do not add dependencies. Leave a concise
`DEBUG_REPORT.md` containing the observed failure, hypotheses/probes, root cause,
regression evidence, final checks, and residual risk.


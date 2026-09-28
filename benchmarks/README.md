# Coding-agent benchmark pilot

This directory contains a **difficulty-calibrated pilot benchmark** for comparing a
plain coding-agent setup with the workflow, guardrails, and validation practices in
this repository.

The goal is not to test whether a frontier model can write small patches. Easy tasks
saturate quickly and provide little signal. The pilot therefore targets failures that
come from **insufficient repository investigation, incorrect boundary decisions,
regressions, unsafe literal instruction following, and weak validation**.

## Experimental rule

The task packet is held constant between variants.

- same task text
- same seed repository
- same model and reasoning setting
- same time/token budget
- same initial git state
- same hidden grader

Only the agent configuration may differ.

A recommended comparison is:

1. `baseline`: plain Codex with no repository-specific codex-config skills/rules.
2. `codex-config`: the normal codex-config workflow enabled.

Do not rewrite the task prompt between variants.

## Difficulty gate

Every candidate task must be run with the **baseline variant at least 3 times** before
it can enter the primary benchmark.

| Baseline success rate | Disposition |
| --- | --- |
| > 70% | reject as saturated / too easy |
| 30-70% | primary benchmark candidate |
| 10-30% | hard-set candidate |
| < 10% | inspect for broken/underspecified task before use |

This gate is intentional. A task that both variants solve almost every time is not
useful evidence for this benchmark.

## Pilot tasks

| ID | Category | Main failure mode |
| --- | --- | --- |
| INV-001 | repository investigation | duplicates path logic instead of finding the canonical helper/contract |
| DBG-001 | debugging | fixes expiry locally but breaks stale-window and metrics semantics |
| IMP-001 | multi-file implementation | adds generic retries without respecting idempotency, Retry-After, and cancellation |
| SAFE-001 | safety / ambiguity | follows "clear the cache" literally and deletes user-owned data |
| REV-001 | regression / review | fixes precedence but loses meaningful falsy values or mutates caller state |

Each task is designed so that a tempting local patch can pass obvious checks while
the hidden grader still fails it.

## Running a task

Prepare an isolated seed repository:

```powershell
python benchmarks/pilot.py prepare DBG-001 .benchmark-runs/DBG-001-baseline-1
```

Then run the selected coding agent **from inside the generated directory**. Give it
only the generated `TASK.md` as the task. The benchmark harness and hidden tests
must not be placed in the agent workspace.

After the agent finishes:

```powershell
python benchmarks/pilot.py grade DBG-001 .benchmark-runs/DBG-001-baseline-1
```

The grader reports:

- public test result
- hidden test result
- changed files since the frozen baseline commit
- scope violations
- overall pass/fail

A run counts as a success only when public tests, hidden tests, and scope checks all
pass.

## Recording pilot runs

Create a JSON file such as:

```json
{
  "runs": [
    {"task_id": "DBG-001", "variant": "baseline", "run": 1, "passed": false},
    {"task_id": "DBG-001", "variant": "baseline", "run": 2, "passed": true},
    {"task_id": "DBG-001", "variant": "baseline", "run": 3, "passed": false}
  ]
}
```

Then apply the difficulty gate:

```powershell
python benchmarks/pilot.py gate benchmarks/results.json
```

Do not run the codex-config comparison on saturated tasks and then present the small
difference as meaningful. Calibrate difficulty first.

## Design principles

A valid hard task should satisfy most of these conditions:

- relevant evidence exists in at least 3 repository locations;
- the likely first patch is incomplete or unsafe;
- there are at least 3 hidden edge cases;
- a compatibility or ownership constraint matters;
- implementation requires more than one local edit or a deliberate decision not to
  edit something;
- the acceptance criteria are inferable from repository evidence rather than grader
  trivia;
- hidden tests check documented or structurally implied behavior, not arbitrary
  surprises.

The benchmark must not become difficult by making the task nonsensical, withholding
essential requirements, or requiring an exact reference patch.

## What this pilot does not claim

Five synthetic tasks are not evidence that codex-config generally improves coding
agents. They are a calibration set for finding tasks with enough headroom to measure
workflow effects. A later benchmark should add larger real-repository tasks, repeated
runs, cost/time measurements, and ablations of individual skills/guardrails.

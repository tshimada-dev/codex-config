---
name: codex-task-intake
description: Clarify and classify ambiguous Codex work before execution. Use when a request is broad, underspecified, risky, multi-step, touches production data or external services, asks for "best practices", "figure out", "make a plan", "use agents", or could be solved in several materially different ways.
---

# Codex Task Intake

Use this skill to turn an unclear request into an executable path with the fewest useful questions.

## Intake Loop

1. Restate the goal in one sentence.
2. Classify the request:
   - `answer`: explain or research only.
   - `inspect`: read local or remote context before proposing changes.
   - `edit`: make a bounded code or file change.
   - `workflow`: plan or coordinate a larger multi-step task.
   - `automation`: create a recurring or delayed task.
3. Identify the main risk: data loss, wrong repo, wrong branch, external side effects, privacy, cost, time, or visual quality.
   - If the request touches cloud, infrastructure, database, deployment, migration, or other remote operational state, route to `codex-cloud-ops-intake` before any command execution.
   - For repository work, record whether the repository is trusted, untrusted, or unknown. Treat build, test, and package commands in untrusted or unknown repositories as arbitrary code execution until the user confirms trust.
4. Decide whether to proceed, inspect first, or ask a question.
5. Ask at most one concise question when a wrong assumption would be expensive. Otherwise make a conservative assumption and continue.

## Decision Rules

- If the user asks for implementation and the scope is discoverable locally, inspect and proceed.
- If the user asks for planning, do not edit project files unless planning artifacts are the deliverable.
- If the request involves current facts, prices, laws, schedules, third-party docs, or remote state, verify with the appropriate source.
- If the mode is `automation`, use the available automation workflow; ask only for missing schedule, timezone, target action, or notification details.
- If the task would benefit from subagents, hand off to a planning/delegation skill after intake unless the task is tiny or the user asks not to use them.
- If the task is mainly debugging, hand off to `codex-debug-discipline`.
- If the task is broad engineering work, hand off to `codex-plan-slices`.
- If the user asks for a disposable, simulated, or rehearsal repo, establish the workspace boundary first and treat edits outside that boundary as out of scope.
- If the task involves AWS, Terraform, Kubernetes, databases, deployments, migrations, production/staging resources, or cost-incurring remote operations, hand off to `codex-cloud-ops-intake` before implementation or shell execution.

## Composition

Use this skill as the entry gate, then route:

- Unfamiliar repo work: `codex-repo-scout` before editing.
- Broad work: `codex-repo-scout` then `codex-plan-slices`.
- Bug reports: `codex-debug-discipline` owns reproduction and root cause.
- Code changes: `codex-implementation-loop` owns the patch and checks.
- UI changes: `codex-ui-quality-gate` runs after implementation.
- Cloud, infrastructure, database, deployment, or migration work: `codex-cloud-ops-intake` owns target/effect/approval classification before commands run.
- Review packaging: `codex-pr-readiness` runs after verification.
- Long or interrupted work: `codex-context-handoff` captures durable state.

## Output Shape

For quick tasks, proceed without a visible plan.

For broad tasks, provide:

```text
Goal: ...
Mode: answer | inspect | edit | workflow | automation
Assumption: ...
Next step: ...
```

Keep this short. Intake is a gate, not the work itself.

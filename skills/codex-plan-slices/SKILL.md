---
name: codex-plan-slices
description: Break broad engineering work into safe vertical slices, TODOs, and optional subagent assignments. Use when work is multi-file, multi-phase, delegated, parallelizable, risky, or when the user asks for a plan, task breakdown, worker agents, subagents, implementation strategy, or large refactor coordination.
---

# Codex Plan Slices

Use this skill to convert broad work into ordered, verifiable slices. Prefer vertical slices that deliver observable behavior over horizontal layer-only tasks.

## Composition

Use after `codex-task-intake` and usually after `codex-repo-scout`. Hand off to `codex-implementation-loop` for actual edits. For bugs, let `codex-debug-discipline` find the cause before slicing implementation work.

## Planning Steps

1. State the objective and non-goals.
2. List constraints from the user, repo, branch, tests, and external systems.
3. Split work into slices. Each slice must have:
   - intent
   - write scope
   - dependencies
   - acceptance criteria
   - focused verification
   - risk
4. Mark slices as:
   - `serial`: depends on earlier work or shares files.
   - `parallel-safe`: disjoint write scope and no ordering dependency.
   - `human-decision`: blocked on product, design, security, or external access.
5. Keep parent-owned work explicit: integration, final verification, release judgment, and user report.

## Subagent Rules

Use subagents only when the user explicitly asked for agents, delegation, workers, or parallel work.

When the user allows subagents and the task is broad, prefer subagent-first execution to preserve parent context:

- Parent keeps only the objective, slice list, ownership map, dependency graph, final verification plan, and unresolved risks.
- Delegate repo scouting by subsystem to explorer agents instead of reading large file sets in the parent.
- Delegate implementation only when write scopes are disjoint or clearly serial.
- Delegate review, UI smoke checks, and focused test expansion when they can run in parallel with parent integration work.
- Ask agents to return concise reports: changed files, tests/checks run, important findings, risks, and integration notes.
- Do not paste large source files, logs, screenshots, or raw diffs from agents into parent context unless they are the artifact under review.
- Parent integrates results, resolves conflicts, runs final verification, and makes release/PR judgments.

Close completed subagents when their results have been integrated or are no longer needed; stale completed threads still consume the available agent-thread budget in long sessions.

Delegate only bounded side work:

- Good: implement one isolated module, write tests for a changed surface, inspect a specific subsystem.
- Bad: final integration, release decisions, broad architecture judgment, or urgent blocking work.

Every worker assignment must include:

```text
Task:
Write scope:
Dependencies completed:
Acceptance criteria:
Tests/checks:
Do not revert or overwrite changes made by others.
Report changed files, tests run, and unresolved issues.
```

## Plan Artifact

Do not create a plan file unless the user requested a durable artifact, the repo already has a matching planning convention, or the work is actively multi-session. Otherwise provide the plan in the response.

For tiny edits or skill evaluations, an in-conversation checklist is enough unless the user asks for a durable plan file.

When a file is warranted, use `docs/plans/<short-name>.json` or an existing repo planning convention.

Minimal structure:

```json
{
  "objective": "",
  "non_goals": [],
  "constraints": [],
  "slices": [
    {
      "id": "S1",
      "title": "",
      "write_scope": [],
      "dependencies": [],
      "parallel": false,
      "acceptance": [],
      "verification": [],
      "risk": "",
      "status": "pending"
    }
  ],
  "final_verification": []
}
```

Do not over-plan small edits.

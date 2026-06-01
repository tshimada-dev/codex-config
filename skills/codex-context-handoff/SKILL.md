---
name: codex-context-handoff
description: Capture durable continuation context for long-running work, interruptions, resumes, handoffs, or context compaction. Use when Codex should preserve what was learned, what changed, what remains, or how another session should continue.
---

# Codex Context Handoff

Use this skill to preserve only the context a future Codex session needs.

## When To Write

Write a handoff when:

- work spans many tool calls or sessions
- a plan was created or revised
- a run is paused
- the user asks to continue later
- context is at risk of compaction
- another agent or human will pick up the work

## Content

Include:

- goal
- current status
- important decisions
- files changed or created
- commands run and outcomes
- tests passing or failing
- blockers
- next concrete step
- disposable workspace path and whether artifacts should be kept, when work happened in a temp project
- tool gaps and verification fallbacks, when normal checks could not run

Exclude:

- full transcripts
- duplicate specs already saved elsewhere
- raw logs unless they are the artifact
- speculation not tied to a next step

## Format

Do not create a handoff file unless the user requested durable context, the repo already has a matching convention, or the work is actively multi-session. Otherwise provide the handoff in the response.

Use the project's existing handoff, run-note, or planning location if present. If an active run note exists, add a concise `## Handoff` section there. If a file is warranted and no convention exists, create a short markdown note under `docs/codex/handoffs/`.

For long-running work without an existing convention, prefer active run notes under `docs/codex/runs/` and keep handoff details inside the run note when practical.

For completed temp-only simulations, a final response summary is usually enough unless the user asked to keep artifacts.

```markdown
# Handoff: <task>

## Goal

## Status

## Decisions

## Files

## Verification

## Blockers

## Handoff

## Next Step
```

Keep it short enough that a future agent will actually read it.

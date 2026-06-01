# Long-Running Workflow

Use this workflow when a task is likely to take more than 30 minutes, crosses multiple repositories or subsystems, involves CI failures, or may need to survive interruption and resume.

## Principles

- Keep the goal, current state, next step, and verification status written down.
- Separate research, implementation, and verification, even when one Codex session performs all three.
- Default to subagent-first work when subagents are available and the task has context-heavy research, broad planning, independent implementation slices, review, or verification work.
- Keep the parent session focused on decisions, integration, conflict resolution, final verification, and user reporting.
- Prefer small, reviewable changes and repository-local conventions.
- Preserve user changes. Never discard uncommitted work unless the user explicitly asks for it.
- Stop and ask before destructive local operations, remote mutations, publishing, deployments, production data changes, migrations, or touching secrets.

## Research

- Restate the request in one sentence.
- Identify the repository, current working directory, relevant docs, and likely source/test directories.
- Read repository instructions before editing.
- Find relevant files with fast search tools such as `rg` or `rg --files`.
- Record findings and unresolved assumptions in the active run note.
- If no repository convention exists, create active run notes under `docs/codex/runs/`.

## Implementation

- Base changes on the research notes.
- Keep the edit scope narrow and consistent with existing style.
- Update the run note if new findings change the plan.
- Avoid broad refactors unless they are required to finish the requested task safely.

## Verification

- Discover the repository's real check commands before running them.
- Run the narrowest useful check first, then broader checks when shared behavior changed.
- Record commands, outcomes, and any skipped checks in the active run note.
- If a failure appears unrelated, preserve evidence and report it instead of masking it.

## Resume Checklist

- Read the active run note.
- Confirm current git status and recent changes.
- Re-open the files named in the note before editing.
- Continue from the recorded next step, adjusting only if the repository state has changed.

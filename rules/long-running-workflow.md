# Long-Running Workflow

Use this workflow when a task is likely to take more than 30 minutes, crosses multiple repositories or subsystems, involves CI failures, or may need to survive interruption and resume.

Follow `development-workflow.md` for expected outcomes, evidence, ownership, verification, readiness, and repository trust. This document adds continuity practices for long-running work.

## Principles

- Keep the goal, current state, next step, and verification status written down.
- Separate research, implementation, and final verification as responsibilities and recorded phases, even when one Codex session performs all three. This does not prohibit focused red/green checks or other feedback during implementation.
- Prefer subagents when subagents are available and the task has context-heavy research, broad planning, independent implementation slices, review, or verification work.
- Keep the parent session focused on decisions, integration, conflict resolution, final verification, and user reporting.
- Prefer small, reviewable changes and repository-local conventions.
- Preserve user changes. Never discard uncommitted work unless the user explicitly asks for it.
- Stop and ask before destructive local operations, remote mutations, publishing, deployments, production data changes, migrations, or touching secrets.

## Run Note

- Use a single active run note for each long-running task.
- Prefer the repository's documented run-note convention. If none exists, create it under `$HOME\.codex\runs\<repo-name>\`.
- Name new run notes `YYYYMMDD-HHMM-<short-task>.md` using local time and a short lowercase slug, for example `20260601-1430-fix-ci-login.md`.
- Copy `$HOME\.codex\templates\agent-run.md` as the starting structure.
- Update the note at phase boundaries, when assumptions or scope change, after each meaningful implementation slice, after verification commands, before pausing, and before handing off.
- Keep entries brief and decision-focused. Link or name files and commands instead of pasting large logs or diffs.

## Research

- Restate the request in one sentence.
- Identify the repository, current working directory, relevant docs, and likely source/test directories.
- Read repository instructions before editing.
- Find relevant files with fast search tools such as `rg` or `rg --files`.
- Record findings and unresolved assumptions in the active run note.
- If no active run note exists yet, create it before making code changes.

## Implementation

- Base changes on the research notes.
- Record the expected outcome and evidence at the level required by `development-workflow.md` before changing behavior.
- Keep the edit scope narrow and consistent with existing style.
- Use focused tests and probes during implementation; record them as implementation feedback, not final verification.
- Update the run note if new findings change the plan.
- Avoid broad refactors unless they are required to finish the requested task safely.

## Verification

- Discover the repository's real check commands before running them.
- Run the narrowest useful check first, then broader checks when shared behavior changed.
- Verify the integrated result independently of the implementation feedback and record its readiness classification.
- Record commands, outcomes, and any skipped checks in the active run note.
- If a failure appears unrelated, preserve evidence and report it instead of masking it.

## Resume Checklist

- Read the active run note.
- Confirm current git status and recent changes.
- Re-open the files named in the note before editing.
- Continue from the recorded next step, adjusting only if the repository state has changed.

# Repository Codex Instructions

## Project Shape

- Main source:
- Tests:
- Scripts:
- Docs:

## Working Rules

- Preserve unrelated user changes.
- Keep changes scoped to the requested behavior.
- Prefer repository-local helpers and conventions.
- Prefer subagents for context-heavy research, broad planning, independent implementation slices, review, and verification when they are available.
- Record long-running work at this repository's documented run-note location. If this repository has no convention, use `$HOME\.codex\runs\<repo-name>\YYYYMMDD-HHMM-<short-task>.md` instead of adding internal run notes to the repo.
- Add handoff notes to the active run note when one exists; use `docs/codex/handoffs/` only for standalone handoffs.

## Verification

- Format:
- Lint:
- Typecheck:
- Test:
- Build:

## Safety

- Ask before destructive commands, remote mutations, deployments, migrations, publishing, or secret-handling operations.
- Do not inspect, print, copy, upload, or summarize secrets, tokens, private keys, cookies, or `.env` contents unless the user explicitly asks and the task requires it.

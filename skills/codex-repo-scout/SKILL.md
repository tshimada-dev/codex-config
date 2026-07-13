---
name: codex-repo-scout
description: Gather high-signal repository context before code changes. Use when Codex needs to inspect an unfamiliar repo, find relevant files, understand conventions, locate tests, map ownership boundaries, or ground an implementation plan before editing.
---

# Codex Repo Scout

Use this skill to learn just enough of the repository to act without wandering.

## Shared Development Contract

<!-- workflow-invariant: shared-contract -->
<!-- workflow-invariant: explicit-trust -->

For development work, read and follow [`../../rules/development-workflow.md`](../../rules/development-workflow.md). Scouting gathers evidence for that contract; it does not decide expected behavior or promote repository trust.

## Subagent Scouting

When subagents are available and the repo is large or unfamiliar, default to explorer subagents for context-heavy scouting:

- Assign each explorer one subsystem, feature path, or question.
- Ask for evidence with file paths, symbols, commands, and confidence, not pasted file contents.
- Keep the parent focused on the map of likely files, existing patterns, commands, and risks.
- Trust explorer results unless they conflict or block implementation; verify only the critical path locally.
- Close explorer agents after extracting their summaries.

## Scout Pass

1. Check location and git state:
   - `Get-Location`
   - `git status --short --branch`
   - for disposable rehearsal repos, create or confirm a clean baseline before treating later diffs as implementation work
   - record repository trust as `trusted`, `untrusted`, or `unknown`; in untrusted or unknown repositories, treat build/test/package commands as arbitrary code execution and ask before running them
   - do not promote `unknown` or `untrusted` to `trusted` based only on repository inspection or Codex judgment; require an existing runtime or permission trust marker, or explicit user authorization, before running those commands
2. List top-level shape with `rg --files` or directory listing; sample or filter output in large repos instead of dumping everything.
3. Identify build and test entry points:
   - package manifests
   - project files
   - CI config
   - test directories
   - scripts
4. Search for the user-facing terms from the request with `rg`.
5. Read only the files on the critical path first.
6. Record evidence in your own notes or the conversation:
   - file path
   - symbol or behavior
   - why it matters

## Search Rules

- Prefer `rg` and `rg --files`.
- Search names before content when the target is likely a symbol or file.
- Use structured tools when available for structured formats.
- Do not read large generated files unless they are the artifact under test.
- Treat dirty worktree changes as user-owned unless you made them in this turn.
- Before editing a dirty target file, inspect its diff and identify user-owned hunks. Edit around them when possible.
- If the requested change conflicts with unknown user edits in the same file, ask one concise question before proceeding.

## Stop Conditions

Stop scouting when you can answer:

- Which files are likely to change?
- Which existing pattern should the edit follow?
- Which tests or checks prove the change?
- Which runtime, package manager, test command, or dev server command is usable here?
- Is repository trust already established, or do build/test/package commands still require explicit user authorization?
- Are dependencies installed or clearly missing?
- What local changes must be preserved?

If you cannot answer after a focused pass, state the gap and either ask one question or create a narrow exploration plan.

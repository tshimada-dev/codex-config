---
name: codex-implementation-loop
description: Implement code or file changes with tight scope, repo conventions, test coverage, and dirty-worktree safety. Use when Codex is asked to fix, build, refactor, add a feature, update files, or carry an approved plan through implementation.
---

# Codex Implementation Loop

Use this skill to make changes without losing the plot or disturbing user work.

## Composition

Use after `codex-repo-scout` for unfamiliar code. For bugs, use after `codex-debug-discipline` has produced a reproduction or code-path finding. For UI changes, run `codex-ui-quality-gate` before final delivery.

## Subagent Implementation

When subagents are available, prefer worker agents for bounded implementation slices that do not block the parent's next step:

- Give each worker an exact write scope, dependencies, acceptance criteria, and tests/checks.
- Tell workers they are not alone in the codebase and must not revert or overwrite others' edits.
- Keep parent-owned work to integration, conflict resolution, final verification, and user reporting.
- Ask workers to report changed files, tests run, unresolved issues, and any assumptions about neighboring code.
- Do not ask workers to make release decisions, broad refactors outside scope, or final PR packaging.

## Loop

1. Reconfirm the target behavior and files from context.
2. Inspect the current file before editing.
3. Prefer the smallest change that matches local style.
4. Edit with `apply_patch` for manual changes.
5. Add or update tests when behavior changes or risk is nontrivial; for behavior changes, prefer writing the focused test before the implementation when practical.
6. Run the narrowest meaningful check first.
7. Broaden checks when shared contracts, state, CLI behavior, UI flows, or public APIs changed.
8. Summarize changed files, checks, and residual risk.

## Loopback Conditions

Return to an earlier step when:

- New information changes the target behavior: go back to step 1, reconfirm the target behavior and files.
- The file has changed or is dirty in a relevant area: go back to step 2, inspect the current file before editing.
- The diff grows beyond the requested scope: go back to step 3, choose the smallest change again.
- A check fails because of your change: fix the cause and go back to step 6, run the narrowest meaningful check.
- A broader check exposes a shared-contract issue: go back to step 1 or step 3, depending on whether the expected behavior changed.

## Change Discipline

- Preserve user changes in the worktree.
- Before editing a dirty target file, inspect its diff and identify user-owned hunks. Edit around them when possible.
- If the requested change conflicts with unknown user edits, ask one concise question before proceeding.
- For disposable repro or rehearsal projects, keep all created and edited files inside the agreed temp/project directory.
- When asked for recommendations to instruction or skill files, provide exact patches without applying them unless direct edits were requested.
- Do not refactor unrelated code while passing through.
- Prefer existing helpers, types, patterns, naming, and test style.
- Use structured parsers for structured data when practical.
- Leave comments only where they reduce real future confusion.
- Keep generated or mechanical churn out of the diff unless required.

## Test Heuristics

Add tests when:

- behavior changed
- a bug was fixed
- a public contract changed
- the area is easy to regress
- the user asked for confidence

Skip new tests only when the change is trivial, non-behavioral, or the repo has no usable test surface. Say so in the final report.

## Failure Handling

When a check fails:

1. Read the failure.
2. Decide whether it is caused by your change, existing environment state, or unrelated dirty work.
3. Fix only your caused failures.
4. Re-run the relevant check.
5. Report unrelated failures with evidence.

If the intended test runner or dependency is unavailable, run the narrowest executable fallback check, record the original command and failure, and do not claim the intended test passed.

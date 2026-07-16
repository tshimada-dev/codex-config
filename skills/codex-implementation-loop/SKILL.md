---
name: codex-implementation-loop
description: Implement code or file changes with tight scope, repository conventions, focused evidence, and preservation of user work. Use when Codex is asked to fix, build, refactor, add a feature, update files, or carry an approved plan through implementation.
---

# Codex Implementation Loop

Use this skill to make changes without losing the plot or disturbing user work.

## Shared Development Contract

<!-- workflow-invariant: shared-contract -->
<!-- workflow-invariant: implementation-test-first -->

Read and follow [`../../rules/development-workflow.md`](../../rules/development-workflow.md) before editing. This skill owns durable implementation edits and must preserve the shared expected-outcome and evidence trace.

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

1. Reconfirm the expected outcome, non-goals, constraints, applicable acceptance IDs, and named evidence from context. Resolve or explicitly escalate material conflicts before editing.
2. Confirm how each applicable acceptance criterion will be evidenced. When no formal criterion exists, state the focused expected outcome and its check.
3. Inspect the current file before editing.
4. Before adopting or implementing the first plausible solution, pause and challenge it:
   - identify the assumptions it depends on
   - inspect affected callers, shared contracts, and neighboring abstractions
   - compare at least one reasonable alternative when the choice has architectural consequences
5. Choose the smallest coherent change that improves the system-level outcome within the agreed scope and constraints, not merely the smallest local diff. Prefer consistency with the repository's architecture over a patch that solves only the immediate symptom.
6. Consider the relevant time horizon: maintenance, likely extension, migration cost, operational burden, and technical debt. Keep this proportional to the task; do not use hypothetical future needs to justify speculative abstractions or unrelated refactors.
7. Before the behavior implementation edit, establish the focused failing test when a stable, deterministic, low-cost test seam exists. Confirm that it fails for the expected reason. If no such seam exists, record why and identify the narrowest credible alternative evidence before editing.
8. Edit with `apply_patch` for manual changes, make the focused evidence pass, then refactor only while it remains passing.
9. Run the narrowest meaningful check first. If it differs from the CI command or is only a local substitute, record that difference instead of treating it as equivalent to CI.
10. Broaden checks when shared contracts, state, CLI behavior, UI flows, or public APIs changed.
11. Summarize changed files, acceptance-to-evidence results, checks, and residual risk.

## Loopback Conditions

Return to an earlier step when:

- New information changes the target behavior: go back to step 1, reconfirm the expected outcome and evidence.
- The file has changed or is dirty in a relevant area: go back to step 3, inspect the current file before editing.
- The diff grows beyond the requested scope: go back to step 5, choose the smallest coherent change again.
- A check fails because of your change: fix the cause and go back to step 9, run the narrowest meaningful check.
- A broader check exposes a shared-contract issue: go back to step 1 or step 5, depending on whether the expected behavior changed.

## Change Discipline

- Treat "smallest change" as the smallest architecturally coherent change, not the fewest edited lines. A slightly broader change is justified when it preserves a shared invariant, prevents duplicated logic, or avoids knowingly creating short-lived technical debt.
- Follow the shared contract's worktree-preservation rules before editing or packaging existing changes.
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

---
name: codex-implementation
description: Implement code or file changes with tight scope, repository conventions, focused evidence, and preservation of user work. Use when Codex is asked to fix, build, refactor, add a feature, update files, or carry an approved plan through implementation.
---

# Codex Implementation

Use this skill to deliver the requested repository behavior with credible evidence while preserving user work.

## Shared Development Contract

<!-- workflow-invariant: shared-contract -->
<!-- workflow-invariant: implementation-test-first -->

Read and follow [`../../rules/development-workflow.md`](../../rules/development-workflow.md) before editing. This skill owns durable implementation edits and must preserve the shared expected-outcome and evidence trace.

## Composition

Use after `codex-repo-scout` for unfamiliar code. For bugs, use after `codex-debug-discipline` has produced a reproduction or code-path finding. For UI changes, run `codex-ui-quality-gate` before final delivery.

## Implementation Contract

- Confirm the expected outcome, constraints, applicable acceptance criteria, and named evidence before changing behavior.
- Discover the repository's relevant checks. Prefer a focused fail-first check when a stable, deterministic, low-cost seam exists; otherwise record why and identify the narrowest credible alternative before editing.
- Make the smallest architecturally coherent change within scope, following repository conventions and preserving existing user work.
- Run focused evidence first, then broaden verification in proportion to the affected contract. Distinguish local substitutes from CI-equivalent evidence.
- Record material deviations, unresolved conflicts, unavailable checks, and failures not caused by the change instead of silently treating them as success.
- Report changed files, acceptance-to-evidence results, checks run, and residual risk.

## Safety Boundaries

- Follow the shared contract's authority, repository-trust, worktree-preservation, and cross-shell safety rules.
- Do not overwrite or package unrelated user changes, expand into unrelated refactors, or leave generated/debug churn in the diff.
- Keep disposable reproduction or rehearsal files inside the agreed temporary/project directory.

## Subagent Implementation

For each bounded worker assignment, provide the exact write scope, completed dependencies, acceptance criteria, and tests/checks. Tell workers not to revert or overwrite others' edits. Workers report changed files, tests run, assumptions, and unresolved issues. The parent retains integration, conflict resolution, final verification, and release reporting.

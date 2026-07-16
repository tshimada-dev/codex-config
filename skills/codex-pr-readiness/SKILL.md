---
name: codex-pr-readiness
description: Prepare local changes for review, commit, pull request, CI follow-up, or review-comment response. Use when the user asks to commit, stage, push, open a PR, write a PR description, clean up a diff, address review comments, or make work reviewable.
---

# Codex PR Readiness

Use this skill to turn finished work into a reviewable change.

## Shared Development Contract

<!-- workflow-invariant: shared-contract -->
<!-- workflow-invariant: readiness-states -->

Read and follow [`../../rules/development-workflow.md`](../../rules/development-workflow.md). PR readiness evaluates the implementation and evidence against that contract; it does not weaken or replace required evidence.

This skill owns workflow and evidence artifacts used for packaging, such as readiness reports, commit messages, and PR text. It does not own durable product or repository behavior edits. Return any requested source, test, configuration, script, policy, or documentation correction to `codex-implementation-loop`, then repeat the affected verification and readiness checks.

## Subagent Review

When subagents are available, prefer a reviewer agent for a focused pre-PR pass before staging or committing:

- Ask it to inspect the diff for bugs, missing tests, unrelated changes, risky generated files, and PR summary gaps.
- Require findings with file paths and severity, plus a concise verification recommendation.
- Parent owns staging, commit, push, PR creation, and final judgment.

## Review Pass

1. Inspect status:
   - `git status --short --branch`
   - `git diff --stat`
   - targeted `git diff`
2. Separate your changes from unrelated user changes.
3. Confirm the diff tells one coherent story. If not, propose splitting.
   - If coherence requires a durable file correction, return that finding to `codex-implementation-loop`; do not patch it inside readiness.
4. Run relevant verification unless impossible or explicitly skipped by the user. If local verification differs from CI, state the discrepancy instead of claiming the CI contract was satisfied.
5. Trace applicable acceptance IDs or expected outcomes to the named evidence and its result.
6. Assign one evidence-based status:
   - `ready`: all required evidence is complete and passing, with no unresolved blocking finding.
   - `conditionally-ready`: all required evidence passes, but explicitly optional evidence was skipped or an accepted residual risk remains. Name the condition and who or what can close it.
   - `not-ready`: required evidence is missing or failing, or an unresolved expected-outcome, safety, or correctness issue remains.
7. Prepare a concise summary:
   - readiness status and any closing condition
   - what changed
   - why it changed
   - tests/checks
   - known risks

If verification is skipped or unavailable, state the exact reason, what would have been run, and residual risk. Do not report `ready` when required evidence was skipped or is unavailable.

Before packaging, apply the shared contract's worktree-preservation rules and keep the requested change separate from unrelated work.

If review or CI follow-up reveals a durable correction, record the finding and transition to `codex-implementation-loop`. Resume readiness only after the correction and its required verification are complete.

## Commit Discipline

- Commit only when the user asks.
- Stage only files that belong to the requested change.
- Never stage unrelated user-owned changes.
- Do not include secrets, logs, temporary files, or unrelated formatting churn.
- When a commit changes workflow, architecture, policy, estimation logic, security posture, or other design judgment, include a body with 2-3 concise lines explaining why the change is needed and what verification supports it. Small mechanical fixes may use a subject-only commit.
- Use non-interactive git commands.
- If pre-commit hooks modify files, inspect the new diff before committing.

For personal Windows/PowerShell-only workflows, keep commits local and factual. When preparing for team distribution, call out portability assumptions and split cross-platform packaging into its own change instead of hiding it in an unrelated commit.

## Temporary Or No-Commit Repos

If a disposable repo has no commits or all files are untracked:

- Use a manual changed-files list or `git diff --no-index` where useful.
- Do not stage just to manufacture a diff unless the user asked for staging or commit prep.
- Report that normal tracked diff evidence is unavailable.

## PR Body Shape

```markdown
## Summary
- ...

## Verification
- ...

## Notes
- ...
```

Keep the PR body factual. Do not oversell.

## Review Comments

When addressing review comments:

1. Read the exact comment and surrounding diff.
2. Group comments by required change.
3. If the user selected a subset, return only those durable corrections to `codex-implementation-loop`; keep the remaining comments recorded as out of scope.
4. Mention any comment that is stale, conflicting, or requires product judgment.

---
name: codex-pr-readiness
description: Prepare local changes for review, commit, pull request, CI follow-up, or review-comment response. Use when the user asks to commit, stage, push, open a PR, write a PR description, clean up a diff, address review comments, or make work reviewable.
---

# Codex PR Readiness

Use this skill to turn finished work into a reviewable change.

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
4. Run relevant verification unless impossible or explicitly skipped by the user.
5. Prepare a concise summary:
   - what changed
   - why it changed
   - tests/checks
   - known risks

If verification is skipped or unavailable, state the exact reason, what would have been run, and residual risk.

Before packaging a dirty target file, inspect its diff and separate user-owned hunks from your hunks.

## Commit Discipline

- Commit only when the user asks.
- Stage only files that belong to the requested change.
- Never stage unrelated user-owned changes.
- Do not include secrets, logs, temporary files, or unrelated formatting churn.
- Use non-interactive git commands.
- If pre-commit hooks modify files, inspect the new diff before committing.

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
3. Fix only selected comments if the user selected a subset.
4. Mention any comment that is stale, conflicting, or requires product judgment.

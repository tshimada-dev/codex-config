---
name: codex-claude-code-reviewer
description: Use Claude Code as an external read-only reviewer for Codex work. Trigger when the user explicitly asks Codex to have Claude or Claude Code review Codex's changes, get a second opinion, review a diff/branch/PR/worktree before finalizing, or cross-check implementation work with Claude Code.
---

# Codex Claude Code Reviewer

Use this skill to ask Claude Code for a read-only review of Codex's work, then have Codex verify and act on the findings.

## Preconditions

- Use only when the user explicitly requested a Claude/Claude Code review or approved external model review.
- Confirm `claude` is available before attempting a review.
- Treat `claude -p` as an external call that may send repository context outside Codex and may incur Claude Code usage cost.
- Do not pass secrets, `.env` files, private keys, cookies, tokens, credential-like diffs, or sensitive customer data.
- Do not use this for production deployment, remote mutation, secret handling, or destructive operations.

## Workflow

1. Inspect the worktree yourself first:
   - Run `git status --short --branch`.
   - Identify changed files and unrelated user-owned changes.
   - Inspect the relevant diff enough to know what will be sent.

2. Choose the review scope:
   - For implementation review, send staged and unstaged diffs.
   - For planning review, send the plan or task description instead of code diffs.
   - For large diffs, split by subsystem and run focused reviews.
   - For untracked file contents, either stage safe files intentionally or review them manually; the helper lists untracked filenames but does not include their contents.

3. Prefer the helper script:
   - Use `scripts/invoke-claude-review.ps1` with `-Run` only after the external review is intentional.
   - Use `-Scope` to focus the review on behavior, regressions, tests, security/privacy, or a subsystem.
   - Omit `-Run` to generate a dry-run prompt preview.

4. Triage Claude's output:
   - Verify each claimed issue against the repository.
   - Ignore speculative, style-only, or preference-only comments unless they matter to the user's request.
   - Fix confirmed issues yourself and preserve unrelated user changes.
   - Run the repository's real verification commands after any fix.
   - Report accepted findings, rejected findings, checks run, and residual risk.

## Helper Script

From the repository under review:

```powershell
powershell -ExecutionPolicy Bypass -File "$HOME\.codex\skills\codex-claude-code-reviewer\scripts\invoke-claude-review.ps1" -RepoPath "C:\path\to\repo" -Scope "focus on regression risk" -Run
```

Useful options:

- `-Scope "focus on API behavior and missing tests"` adds review focus.
- `-ExtraPrompt "The target branch is main"` adds safe context.
- `-OutFile review.txt` writes Claude's response to a local file.
- `-KeepPrompt` keeps the temporary prompt file after `-Run`; by default the helper deletes it after the external review finishes.
- `-MaxBudgetUsd 1.00` changes the Claude Code budget cap.
- `-MaxPromptChars 200000` changes the prompt-size refusal threshold.
- Omit `-Run` to print the generated prompt path and command preview without calling Claude.

## Review Prompt Shape

Ask Claude for findings-first review output:

```text
Review the included Codex work as a senior code reviewer.
Do not modify files. Base your answer only on the provided context.
Prioritize correctness bugs, regressions, security/privacy issues, data loss, and missing tests.
Return findings first, ordered by severity, with file/path references when possible.
If there are no material issues, say so clearly and note residual risk.
```

## Guardrails

- Do not let Claude run tools or edit files; provide context in the prompt and request review-only output.
- Do not outsource final judgment: Codex remains responsible for verification and implementation.
- Do not overwrite or stage unrelated user changes based on Claude's advice.
- If the helper refuses because a path or diff looks sensitive, narrow the diff or ask the user before sharing anything externally.
- If Claude Code is unavailable, say so and fall back to a normal Codex review.

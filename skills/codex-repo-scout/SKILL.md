---
name: codex-repo-scout
description: Gather high-signal repository context when the relevant files, conventions, ownership boundaries, or executable checks are not yet clear. Use before editing an unfamiliar or broad repository surface.
---

# Codex Repo Scout

Use this skill only when repository context is genuinely missing. Routine file search and inspection do not need a formal scouting pass.

## Shared Development Contract

<!-- workflow-invariant: shared-contract -->

For development work, read and follow [`../../rules/development-workflow.md`](../../rules/development-workflow.md). Scouting discovers constraints and executable evidence; the contract remains authoritative for trust, worktree preservation, expected outcomes, and verification.

## Explorer Evidence Packets

When subagents are available and the repo is large enough to split by subsystem, assign bounded explorer questions:

- Give each explorer one subsystem, feature path, or question.
- Require file paths, symbols, commands, relevance, and confidence instead of pasted file bodies.
- Keep integration decisions and critical-path verification with the parent.
- Re-check only conflicting, low-confidence, or implementation-blocking findings.

## Evidence To Return

- Likely files, symbols, and ownership boundaries.
- Existing patterns and repository instructions that constrain the change.
- Build, test, CI, or manual checks that can prove the result.
- Required runtimes, package managers, services, and clearly missing dependencies.
- Important uncertainty, with the smallest next read-only inspection that could resolve it.

## Stop Conditions

Stop when the likely write scope, pattern to follow, and credible verification path are clear. If a material gap remains after a focused pass, state that gap and either ask one question or propose one narrow inspection step.

Do not keep scouting merely to restate normal model behavior or to collect exhaustive repository inventories.

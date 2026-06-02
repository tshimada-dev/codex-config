# Global Codex Working Rules

## Long-Running Work

- For work that may take more than 30 minutes, spans multiple subsystems, fixes CI, or may be interrupted, read `$HOME\.codex\rules\long-running-workflow.md` before making changes.
- Keep research, implementation, and verification as separate phases. Do not mix exploratory notes with code changes without recording the changed assumption.
- Prefer subagents when available for context-heavy research, broad planning, independent implementation slices, review, and verification so the parent session stays focused on decisions, integration, and final verification.
- For long-running work, maintain one active run note using `$HOME\.codex\templates\agent-run.md`; store it at the repository's documented run-note location, or under `$HOME\.codex\runs\<repo-name>\YYYYMMDD-HHMM-<short-task>.md` when no convention exists.
- Before finishing implementation work, identify the repository's real verification commands from its `AGENTS.md`, README, Makefile, package files, pyproject, or scripts.
- Do not run destructive local commands, remote-changing commands, publishing commands, deployments, production migrations, or secret-handling operations without explicit user approval.
- Do not inspect, print, copy, upload, or summarize secrets, tokens, private keys, cookies, or `.env` contents unless the user explicitly asks and the task requires it.
- For first-time or untrusted repositories, treat build and test commands as arbitrary code execution. Start with the `safe` profile for inspection, then switch to `local-check` or `workspace` only after deciding the repository is trusted enough.

## Personal References

- Long-running workflow: `$HOME\.codex\rules\long-running-workflow.md`
- Research checklist: `$HOME\.codex\rules\checklists\research.md`
- Implementation checklist: `$HOME\.codex\rules\checklists\implementation.md`
- CI fix checklist: `$HOME\.codex\rules\checklists\ci-fix.md`
- Active run note template: `$HOME\.codex\templates\agent-run.md`
- Repository AGENTS template: `$HOME\.codex\templates\repo-agents.md`

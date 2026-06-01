# Global Codex Working Rules

## Long-Running Work

- For work that may take more than 30 minutes, spans multiple subsystems, fixes CI, or may be interrupted, read `$HOME\.codex\rules\long-running-workflow.md` before making changes.
- Keep research, implementation, and verification as separate phases. Do not mix exploratory notes with code changes without recording the changed assumption.
- Prefer subagents when available for context-heavy research, broad planning, independent implementation slices, review, and verification so the parent session stays focused on decisions, integration, and final verification.
- For long-running work, maintain one active run note using `$HOME\.codex\templates\agent-run.md`; store it at the repository's documented run-note location, or `docs/codex/runs/YYYYMMDD-HHMM-<short-task>.md` when no convention exists.
- Before finishing implementation work, identify the repository's real verification commands from its `AGENTS.md`, README, Makefile, package files, pyproject, or scripts.
- Do not run destructive local commands, remote-changing commands, publishing commands, deployments, production migrations, or secret-handling operations without explicit user approval.

## Personal References

- Long-running workflow: `$HOME\.codex\rules\long-running-workflow.md`
- Research checklist: `$HOME\.codex\rules\checklists\research.md`
- Implementation checklist: `$HOME\.codex\rules\checklists\implementation.md`
- CI fix checklist: `$HOME\.codex\rules\checklists\ci-fix.md`
- Active run note template: `$HOME\.codex\templates\agent-run.md`
- Repository AGENTS template: `$HOME\.codex\templates\repo-agents.md`

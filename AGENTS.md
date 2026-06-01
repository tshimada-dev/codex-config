# Global Codex Working Rules

## Long-Running Work

- For work that may take more than 30 minutes, spans multiple subsystems, fixes CI, or may be interrupted, read `C:\Users\shimada\.codex\rules\long-running-workflow.md` before making changes.
- Keep research, implementation, and verification as separate phases. Do not mix exploratory notes with code changes without recording the changed assumption.
- Prefer subagents when available for context-heavy research, broad planning, independent implementation slices, review, and verification so the parent session stays focused on decisions, integration, and final verification.
- For long-running work, maintain an active run note using `C:\Users\shimada\.codex\templates\agent-run.md`.
- Before finishing implementation work, identify the repository's real verification commands from its `AGENTS.md`, README, Makefile, package files, pyproject, or scripts.
- Do not run destructive local commands, remote-changing commands, publishing commands, deployments, production migrations, or secret-handling operations without explicit user approval.

## Personal References

- Long-running workflow: `C:\Users\shimada\.codex\rules\long-running-workflow.md`
- Research checklist: `C:\Users\shimada\.codex\rules\checklists\research.md`
- Implementation checklist: `C:\Users\shimada\.codex\rules\checklists\implementation.md`
- CI fix checklist: `C:\Users\shimada\.codex\rules\checklists\ci-fix.md`
- Active run note template: `C:\Users\shimada\.codex\templates\agent-run.md`
- Repository AGENTS template: `C:\Users\shimada\.codex\templates\repo-agents.md`

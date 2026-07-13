# Global Codex Working Rules

## Workflow Map

- For implementation, bug fixes, CI fixes, verification, and review readiness, follow `$HOME\.codex\rules\development-workflow.md`.
- For work that may take more than 30 minutes, spans multiple subsystems, fixes CI, or may be interrupted, also follow `$HOME\.codex\rules\long-running-workflow.md` and maintain one active run note from `$HOME\.codex\templates\agent-run.md`.
- Use the research, implementation, and CI checklists linked below for phase-specific prompts; the development workflow remains the authority when wording overlaps.

## Safety Boundaries

- Treat executable commands from unknown or untrusted repositories according to the trust rule in `$HOME\.codex\rules\development-workflow.md`; agent judgment alone does not elevate trust.
- Do not run destructive local commands, remote-changing commands, publishing commands, deployments, production migrations, or secret-handling operations without explicit user approval.
- Do not inspect, print, copy, upload, or summarize secrets, tokens, private keys, cookies, or `.env` contents unless the user explicitly asks and the task requires it.

## Personal References

- Development workflow contract: `$HOME\.codex\rules\development-workflow.md`
- Long-running workflow: `$HOME\.codex\rules\long-running-workflow.md`
- Research checklist: `$HOME\.codex\rules\checklists\research.md`
- Implementation checklist: `$HOME\.codex\rules\checklists\implementation.md`
- CI fix checklist: `$HOME\.codex\rules\checklists\ci-fix.md`
- Active run note template: `$HOME\.codex\templates\agent-run.md`
- Repository AGENTS template: `$HOME\.codex\templates\repo-agents.md`

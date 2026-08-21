# Global Codex Working Rules

## Workflow Map

- For implementation, bug fixes, CI fixes, verification, and review readiness, follow `$HOME\.codex\rules\development-workflow.md`.
- For work that may take more than 30 minutes, spans multiple subsystems, fixes CI, or may be interrupted, also follow `$HOME\.codex\rules\long-running-workflow.md` and maintain one active run note from `$HOME\.codex\templates\agent-run.md`.
- Use the research, implementation, and CI checklists linked below for phase-specific prompts; the development workflow remains the authority when wording overlaps.

## Subagent Delegation

- When subagent delegation is otherwise authorized, do not assume automatic difficulty-based model routing.
- Use `fork_turns="none"` for bounded workers unless recent conversation context is essential.
- For read-only discovery, extraction, and mechanical checks, prefer `model="gpt-5.6-luna"` with `reasoning_effort="low"`.
- For analysis, review, estimation, and bounded implementation, prefer `model="gpt-5.6-terra"` with `reasoning_effort="medium"`.
- Inherit the parent model for high-risk, highly ambiguous, adversarial, or final-integration work.
- When context is required, pass the smallest useful positive `fork_turns`; avoid full-history forks unless necessary.
- Do not delegate tiny linear work. Require compact evidence and keep final integration with the parent.
- If a model or reasoning override is unavailable, omit it and continue.

## Safety Boundaries

- Repository trust and repository-controlled command execution are governed by `$HOME\.codex\rules\development-workflow.md`.
- Before cloud, infrastructure, database, deployment, or migration commands, use `codex-cloud-ops-intake` to establish the exact target and approval boundary.
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

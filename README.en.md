# Codex Config

This repository started as my personal OpenAI Codex configuration. It now also
serves as a portfolio sample for AI coding-agent workflow design: how to define
delegation boundaries, safety profiles, verification habits, and handoff notes
so agent-assisted work remains reviewable.

It is not an official company standard or a generic starter template. The
primary target is Codex. The GitHub Copilot scripts are adapter experiments for
onboarding and lightweight guardrails, not a claim that Copilot can reproduce
the same profile-driven execution boundary.

## Why It Matters

- [`skills/codex-*`](skills/) separates repository scouting, planning,
  implementation, debugging, UI verification, review preparation, handoff, and
  external review into focused Codex skills.
- [`skills/codex-effort-estimator`](skills/codex-effort-estimator/) is the main
  case study for bias control in software estimation: independent passes,
  line-level AI adjustment, audit-friendly workbook output, and follow-up
  calibration issues.
- [`scripts/install.ps1`](scripts/install.ps1) is a PowerShell 7 installer that
  copies only tracked managed files into `$HOME/.codex`, writes a manifest, and
  supports conservative overwrite/prune behavior.
- [`scripts/install-copilot-skills.ps1`](scripts/install-copilot-skills.ps1)
  adapts the tracked `skills/codex-*` skills into GitHub Copilot as
  `copilot-*` Agent Skills for experimentation.
- [`rules/`](rules/) and [`templates/`](templates/) capture repeatable working
  rules for long-running work, CI parity, command safety, decision notes, and
  repository-specific Codex instructions.
- [`rules/development-workflow.md`](rules/development-workflow.md) is the shared
  contract for expected outcomes, acceptance evidence, test-first exceptions,
  phase ownership, and final readiness.
- [`config/development-skills.json`](config/development-skills.json) declares
  workflow roles, phases, durable-edit ownership, Copilot names, defaults, and
  cross-skill dependencies in one machine-readable source.

## Repository Map

- `AGENTS.md`: global working rules for Codex sessions.
- `rules/`: development workflow contract, command policy, long-running workflow,
  and checklists.
- `templates/`: run-note and repository-instruction templates.
- `skills/codex-*`: reusable Codex workflow skills.
- `config/`: shareable baseline config and profiles.
- `scripts/`: installers, workflow validation, and Japanese reference-doc checks.
- `docs/ja/`: Japanese reference documentation for human readers.

## Portfolio Notes

The repository is meant to show workflow design rather than just dotfile
management. Current portfolio packaging work is tracked in
[issue #17](https://github.com/tshimada-dev/codex-config/issues/17).

Planned follow-up work includes:

- a case study comparing the estimator workflow with a veteran human estimate
  ([issue #14](https://github.com/tshimada-dev/codex-config/issues/14));
- a sanitized sample estimator workbook or screenshots
  ([issue #15](https://github.com/tshimada-dev/codex-config/issues/15)).

## Installation

Prerequisites: PowerShell 7+ (`pwsh`) and Git.

| Purpose | Windows | macOS/Linux |
| --- | --- | --- |
| Dry run | `.\scripts\install.ps1 -WhatIf` | `pwsh ./scripts/install.ps1 -WhatIf` |
| Install managed files | `.\scripts\install.ps1` | `pwsh ./scripts/install.ps1` |
| Overwrite managed files | `.\scripts\install.ps1 -Overwrite` | `pwsh ./scripts/install.ps1 -Overwrite` |
| Install shared config baseline | `.\scripts\install.ps1 -InstallConfig` | `pwsh ./scripts/install.ps1 -InstallConfig` |

By default, the installer uses `$CODEX_HOME` when set and otherwise installs to
`$HOME/.codex`.

## Copilot Adapter Experiment

To try the workflow skills in GitHub Copilot, use:

```powershell
.\scripts\install-copilot-skills.ps1 -WhatIf
.\scripts\install-copilot-skills.ps1
```

The Copilot installer leaves the source `codex-*` skills untouched and installs
transformed copies under `$HOME/.copilot/skills` using `copilot-*` skill names.
For skills that use the shared development contract, it also packages the
canonical rule as `references/development-workflow.md` and rewrites the relative
link. The rule therefore remains single-sourced while each Copilot skill stays
self-contained.
It refuses to overwrite different existing files unless `-Overwrite` is passed.
The default entry points are the more tool-neutral workflow skills:
`task-intake`, `repo-scout`, `implementation-loop`, `debug-discipline`,
`plan-slices`, `pr-readiness`, and `ui-quality-gate`. The installer recursively
adds their manifest-declared support dependencies and rewrites exact cross-skill
`codex-*` identifiers to installed `copilot-*` targets. Codex- or
environment-coupled skills such as `codex-claude-code-reviewer` and
`codex-wsl-command-bridge` are not installed unless explicitly requested.
Use `-SkillName repo-scout,implementation-loop` to install selected skills, or
`-AllSkills` only after confirming the extra skills make sense in Copilot.

Without `-Prune`, a partial install preserves the union of previously and newly
managed paths. With `-Prune`, the selected dependency closure becomes
authoritative. All source, containment, conflict, overwrite, and backup checks
finish before mutation, and the managed manifest is replaced atomically last.

Because Copilot does not mirror the Codex `safe` / `local-check` / `workspace`
profile model, this adapter intentionally keeps a narrower scope. For
beginner-friendly safety, install Copilot guardrails instead of a read-only
workflow. These guardrails still allow normal edits, tests, formatters,
`git status`, and `git diff`, but require explicit confirmation for genuinely
destructive operations such as `git reset --hard`, `git clean`, force-pushes,
recursive deletes, publish/deploy/migration commands, and secret handling.

```powershell
.\scripts\install-copilot-guardrails.ps1
```

This installs a user-level instruction file under `$HOME/.copilot/instructions`.
To also merge the matching VS Code terminal auto-approval deny list, back up the
existing settings file and opt in explicitly:

```powershell
.\scripts\install-copilot-guardrails.ps1 -ApplyVSCodeSettings -Backup
```

If VS Code `settings.json` contains JSONC comments, the automatic merge stops by
default because comments cannot be preserved. Add `-AllowJsoncRewrite` only when
you accept rewriting the settings file as plain JSON.

## Development Workflow Contract

The workflow treats specifications and tests as different forms of evidence,
not rival methodologies. Every non-trivial change starts with an expected
outcome and observable evidence. A focused test-first loop is preferred when the
test seam is stable, deterministic, relevant, and reasonably cheap; otherwise
the exception and the narrowest credible alternative evidence are recorded
before the permanent change.

Debugging owns reproduction and root-cause evidence, implementation owns durable
edits, and UI/PR gates verify the integrated result. Material conflicts between
an approved outcome, a designated specification, tests, and current behavior are
resolved using the authority order in the contract rather than by agent
assumption. Final status is reported as `ready`, `conditionally-ready`, or
`not-ready`.

Unknown repositories remain under the `safe` profile until trust is explicitly
established by the runtime/profile or the user. Agent judgment alone does not
promote repository trust.
The user-level command policy prompt-gates npm/uv scripts and common project
runners. It also avoids broad allows for external-execution paths such as
`rg --pre` and `git diff --ext-diff`; unlisted commands retain the runtime and
sandbox defaults. A trusted repository may add narrowly scoped project-local
allow rules after its project config layer is trusted.

## Portability

This repository is still optimized for my Windows and PowerShell-based Codex
environment, but the main installer is PowerShell 7 based and can be run with
`pwsh` on macOS and Linux.

Some supporting examples are intentionally Windows-specific, especially the WSL
command bridge skill and parts of the command-policy documentation. If this
repository becomes a team template or OSS distribution target, deeper
cross-platform packaging should be handled as its own scoped change. This
follows the same direction as
[issue #9](https://github.com/tshimada-dev/codex-config/issues/9).

## License

MIT License. See [LICENSE](LICENSE).

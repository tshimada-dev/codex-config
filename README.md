# Codex Config

Portable personal Codex configuration.

This repository tracks only reusable Codex working rules, templates, and the
generic `codex-*` skills. It intentionally does not track plugin caches,
automations, secrets, runtime logs, or machine-specific local files.

## Contents

- `AGENTS.md`: global Codex working rules
- `rules/`: shared command policy and long-running workflow docs
- `templates/`: reusable run-note and repository instruction templates
- `skills/codex-*`: generic Codex workflow skills
- `scripts/install.ps1`: copies the tracked files into `$HOME\.codex`

## Install

From this repository:

```powershell
.\scripts\install.ps1
```

To preview the copy operations:

```powershell
.\scripts\install.ps1 -WhatIf
```

## Policy

Keep this repo conservative:

- Track reusable skills and docs only.
- Do not commit secrets, tokens, `.env` files, plugin caches, or automation state.
- Keep machine-specific overrides in local files ignored by git.
- Put risky commands behind prompt/forbidden rules instead of broad allow rules.

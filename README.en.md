# Codex Config

This repository is my personal OpenAI Codex configuration, and also a small
portfolio of workflow design for software development with AI agents.

It is not an official company standard or a generic starter template. The
interesting part is the operating model: how to split agent responsibilities,
keep changes verifiable, preserve human control over risky actions, and make
decisions traceable outside chat.

## Why It Matters

- [`skills/codex-*`](skills/) separates repository scouting, planning,
  implementation, debugging, UI verification, review preparation, handoff, and
  external review into focused Codex skills.
- [`skills/codex-effort-estimator`](skills/codex-effort-estimator/) is the main
  case study for bias control in software estimation: independent passes,
  line-level AI adjustment, audit-friendly workbook output, and follow-up
  calibration issues.
- [`scripts/install.ps1`](scripts/install.ps1) installs only tracked managed
  files into `$HOME\.codex`, writes a manifest, and supports conservative
  overwrite/prune behavior.
- [`rules/`](rules/) and [`templates/`](templates/) capture repeatable working
  rules for long-running work, CI parity, command safety, decision notes, and
  repository-specific Codex instructions.

## Repository Map

- `AGENTS.md`: global working rules for Codex sessions.
- `rules/`: command policy, long-running workflow, and checklists.
- `templates/`: run-note and repository-instruction templates.
- `skills/codex-*`: reusable Codex workflow skills.
- `config/`: shareable baseline config and profiles.
- `scripts/`: installer and Japanese reference-doc checks.
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

## Portability

This is intentionally optimized for my Windows and PowerShell-based Codex
environment. The installer and command-policy examples reflect that personal
workflow.

Cross-platform packaging is not the current goal. If this repository becomes a
team template or OSS distribution target, portability should be handled as its
own scoped change rather than hidden inside unrelated edits. This follows the
same direction as
[issue #9](https://github.com/tshimada-dev/codex-config/issues/9).

## License

MIT License. See [LICENSE](LICENSE).

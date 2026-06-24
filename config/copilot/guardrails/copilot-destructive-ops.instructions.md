---
name: "Destructive Operation Guardrails"
description: "Require explicit user confirmation before destructive, remote-changing, publishing, or secret-handling actions."
applyTo: "**"
---

# Destructive Operation Guardrails

Allow normal repository work such as reading files, editing workspace files, creating new files, running formatters, running tests, and inspecting git status or diffs.

Before running or suggesting a destructive local command, explain the exact command, the target paths or refs, and the likely irreversible effect, then ask the user for explicit confirmation.

Treat these as destructive local commands: recursive deletes, force deletes, `git reset --hard`, `git clean`, `git checkout --` or `git restore` used to discard work, deleting branches or tags, rewriting history, deleting databases, wiping caches that may contain user work, and commands that remove files outside the current workspace.

Before running any remote-changing command, explain what remote state will change and ask for explicit confirmation.

Treat these as remote-changing commands: force push, deleting remote branches or tags, creating or deleting releases, publishing packages, deployments, infrastructure apply or destroy commands, database migrations against shared environments, and commands that mutate production or staging resources.

Do not inspect, print, copy, upload, or summarize secrets, tokens, private keys, cookies, or `.env` contents unless the user explicitly asks and the task requires it.

If the user asks for a risky command casually, propose a safer preview first, such as `git status`, `git diff`, `git clean -n`, `Remove-Item` without `-Recurse` or `-Force`, or a dry-run mode when the tool supports one.

If a command combines safe and destructive subcommands, split it into separate steps so the destructive part can be reviewed on its own.

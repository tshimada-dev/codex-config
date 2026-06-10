---
name: codex-wsl-command-bridge
description: Run Linux/WSL commands safely from a Windows PowerShell-hosted Codex session. Use when Codex needs to execute commands in WSL/Linux from Windows, especially for multi-line Bash, shell variables, command substitution, loops, quotes, Windows-to-WSL path conversion, file transfer between Windows and WSL checkouts, or any command with deletion/move side effects.
---

# Codex WSL Command Bridge

Use this skill whenever the active shell is Windows PowerShell but the operation must happen inside WSL/Linux. The goal is to avoid PowerShell/Bash quoting mistakes and Windows/WSL path confusion.

## Decision Rule

Use direct inline WSL only for tiny, read-only, quote-free commands:

```powershell
wsl bash -lc 'pwd && uname -a'
```

Use the bundled helper for anything containing:

- Bash variables such as `$target` or `$pid`
- command substitution such as `$(pwd)`
- loops, conditionals, here-docs, or multi-line scripts
- nested quotes, JSON, YAML, sed/awk/perl snippets, or regexes
- Windows path conversion
- file creation, edits, copies, moves, or deletes
- Git operations that need a specific WSL checkout

## Helper Script

Prefer `scripts/Invoke-WslScript.ps1` for non-trivial work. It writes a UTF-8 LF Bash script to the Windows temp directory, converts the temp path to `/mnt/<drive>/...`, runs it with `wsl bash`, then removes the temp file.

Do not put secrets, tokens, credentials, private keys, or sensitive customer data into scripts passed through the helper. The generated script exists briefly as a plain-text temp file on the Windows filesystem.

Example:

```powershell
$skill = "$env:USERPROFILE\.codex\skills\codex-wsl-command-bridge"
& "$skill\scripts\Invoke-WslScript.ps1" -Script @'
set -euo pipefail
cd /home/<user>/projects/example
git status --short --branch
'@
```

Pass a distro name only when needed:

```powershell
& "$skill\scripts\Invoke-WslScript.ps1" -Distro Ubuntu-24.04 -Script @'
set -euo pipefail
uname -a
'@
```

## Path Rules

- Use Linux paths inside WSL commands, for example `/home/<user>/projects/example`.
- Use UNC paths only for Windows UI/app access, for example `\\wsl.localhost\Ubuntu-24.04\home\<user>\projects\example`.
- Use `/mnt/c/...` only when intentionally reading from or writing to the Windows filesystem.
- Do not build WSL paths by manual string concatenation when the source path comes from Windows; use the helper or `wslpath`.

## Safety Rules

Before recursive delete or move operations in WSL:

1. Get explicit user approval when the operation is destructive or could lose work.
2. Resolve the target with `readlink -f`.
3. Verify it is exactly the expected path or inside the expected parent.
4. Quote the path variable.

Pattern:

```bash
target="/home/<user>/projects/example"
resolved="$(readlink -f "$target")"
case "$resolved" in
  /home/<user>/projects/example|/home/<user>/projects/example/*) ;;
  *) echo "Refusing unexpected path: $resolved" >&2; exit 1 ;;
esac
rm -rf -- "$target"
```

Do not inspect, print, copy, or summarize secrets from WSL unless the user explicitly asks and the task requires it.

## Git Workflow In WSL

When the user wants Linux-native work, treat the WSL checkout as authoritative:

```bash
cd /home/<user>/projects/example
git status --short --branch
```

Use WSL Git credentials for remote operations. If GitHub authentication fails, suggest `gh auth login --hostname github.com --git-protocol https --web` in WSL.

## Reporting

In the final answer, report the Linux path touched and the important command result. Do not expose long helper internals unless debugging the bridge itself.

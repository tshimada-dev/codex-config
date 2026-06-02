# Shared Codex Config

This directory contains shareable Codex configuration fragments.

## Files

- `config.base.toml`: shared baseline keys that can be merged into `$CODEX_HOME/config.toml`.
- `profiles/*.config.toml`: profile files copied to `$CODEX_HOME/<profile>.config.toml` when config install is requested.

## Scope

Do not put these in tracked config files:

- `[projects.*]` trust state
- secrets, tokens, credentials, or `.env` values
- plugin cache or marketplace runtime state
- automation state
- logs
- machine-specific absolute paths
- MCP server entries that require local tokens or private paths

`config.toml` is mutable runtime state. Codex may add local trust entries such as
`[projects."/absolute/path"]`, so this repository does not copy a complete
`config.toml` over the live file.

Use the installer to merge only the shared baseline:

```powershell
.\scripts\install.ps1 -InstallConfig
```

Use a profile explicitly:

```powershell
codex --profile safe
codex --profile local-check
codex --profile workspace
```

`config.base.toml` and the `workspace` profile prioritize day-to-day productivity:
workspace-write sandbox with network access enabled.

Use `safe` for first-time, untrusted, review-only, or no-network inspection.
Use `local-check` after initial inspection when local writes and tests are useful
but dependency downloads or other outbound network access should stay blocked.

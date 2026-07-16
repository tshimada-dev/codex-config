---
name: codex-clean-local-state
description: Diagnose and safely reduce oversized Codex desktop local state while preserving recent work. Use when the Codex app is slow, CODEX_HOME is unexpectedly large, logs_2.sqlite has many free pages, or the user wants to remove sessions older than a retention window. Supports guarded bulk session cleanup, metadata synchronization, SQLite compaction, Windows app-exit waiting, recoverable quarantine, backups, and post-restart verification.
---

# Clean Codex Local State

Use aggregate metadata only. Never read transcript contents, `auth.json`, secrets, config values, or log bodies.

## Safety contract

- Start read-only. Do not mutate local state until the user explicitly authorizes permanent deletion.
- Never delete all of `CODEX_HOME`. Keep config, auth, skills, plugins, attachments, worktrees, memories, goals, and unrelated application data out of scope.
- Fix one timezone-aware cutoff before shutdown. Do not let the retention window drift while waiting for the app to exit.
- Remove a thread only when both its transcript mtime and `threads.updated_at_ms` predate the cutoff.
- Protect the complete parent/child spawn component of any recent, missing, outside-root, unknown-timestamp, or job-referenced thread.
- Preserve transcript files without matching DB evidence.
- Require every execution candidate's ID, path, size, file mtime, DB timestamp, and archive state to match the approved baseline. Abort if new or materially changed candidates appear.
- Stop Codex desktop processes before mutation. Never edit live SQLite state.
- Require every output directory to be a unique child of `CODEX_HOME/backups`.
- Validate all required state/log tables, columns, integrity, and foreign keys before creating the execution output or moving a transcript.
- Back up `state_5.sqlite`, `logs_2.sqlite`, and `session_index.jsonl` before mutation. Keep the backup until recent work has been opened successfully.
- Keep removed transcripts in the exact quarantine until post-restart verification passes. Purge them only as a separate explicitly approved operation.
- Prefer the official `codex delete` command for a small named set when the installed CLI supports it. Use the bundled bulk cleaner only for retention-based cleanup where the official CLI is unavailable or impractical.

## 1. Diagnose without changing state

Resolve `CODEX_HOME`; default to `~/.codex`. Run:

```powershell
python scripts/inspect_codex_state.py --root "$CodexHome" --days 14 --output "$AuditDir\inventory.json"
```

Report:

- total and old transcript counts/sizes for `sessions` and `archived_sessions`;
- `logs_2.sqlite` size and reclaimable free-page estimate;
- `state_5.sqlite` size;
- current Codex/ChatGPT process count and memory when process tools are available.

Do not infer that old transcript files alone are safe to delete.

## 2. Create the guarded baseline plan

Reuse the exact `cutoff` from `inventory.json`:

```powershell
python scripts/cleanup_stale_codex_sessions.py --root "$CodexHome" --cutoff "$Cutoff" --plan-output "$BaselinePlan"
```

Check that:

- `cross_boundary_edges` is zero;
- candidates have both old file and DB timestamps;
- recent or connected work is counted as protected;
- unmapped files are preserved;
- candidate count and bytes match what will be presented to the user.

Present the cutoff, permanent-deletion count, estimated transcript recovery, log compaction estimate, temporary backup/quarantine space, and the two-stage purge behavior. If the user has not already authorized deletion, stop and ask for explicit approval.

## 3. Execute only after app exit

Use a unique, nonexistent output directory under `CODEX_HOME/backups`. On Windows, launch the bundled waiter in a hidden PowerShell process so this Codex task can survive app shutdown:

```powershell
Start-Process -FilePath powershell.exe -WindowStyle Hidden -ArgumentList @(
  '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$SkillRoot\scripts\wait_and_execute.ps1`"",
  '-Execute', '-CodexHome', "`"$CodexHome`"", '-BaselinePlan', "`"$BaselinePlan`"",
  '-OutputDir', "`"$OutputDir`"", '-Cutoff', "`"$Cutoff`""
)
```

Tell the user to fully quit Codex from the tray, wait for cleanup, reopen the app, and resume the same task. The waiter ignores `ChatGPT Classic` but waits for the ChatGPT, codex, and codex-code-mode-host processes.

On non-Windows systems, do not use the PowerShell waiter. Arrange an equivalent external process that waits for all Codex desktop processes to exit, or have the user run the executor from a separate terminal after shutdown:

```text
python cleanup_stale_codex_sessions.py --root <CODEX_HOME> --cutoff <CUTOFF> --execute --ack-app-stopped --baseline <PLAN> --output-dir <NEW_OUTPUT_DIR>
```

Do not pass `--ack-app-stopped` while the app is running.

## 4. Verify after restart

Run:

```powershell
python scripts/verify_cleanup.py --root "$CodexHome" --output-dir "$OutputDir"
```

Require all checks to pass:

- removed IDs exactly equal the execution candidates;
- no protected or recent rows/files are missing;
- no candidate files or index entries remain in their live locations;
- quarantine paths and sizes exactly match the execution plan;
- state, logs, and backup hash checks pass;
- SQLite foreign-key errors are zero;
- log row signature is unchanged across VACUUM; post-restart logs may only increase.

Report removed thread rows, quarantined transcript bytes, DB before/after sizes, backup path, and subjective process/memory improvement. Ask the user to open one or two recent work sessions before purging quarantine.

## 5. Purge quarantine only after successful verification

After `verification.json` reports `passed: true`, recent sessions open successfully, and the user explicitly approves final purge, run:

```powershell
python scripts/cleanup_stale_codex_sessions.py --root "$CodexHome" --purge-quarantine --ack-verified --output-dir "$OutputDir"
```

The purger removes only the exact planned quarantine files when their paths and sizes still match. It refuses unexpected files, changed files, a mismatched verification artifact, or a repeated purge. Re-run verification after purge and retain the database/index backup until the user approves its removal separately.

## Failure handling

- If planning or preflight fails on missing tables, columns, integrity, or foreign keys, stop. Do not patch the DB ad hoc.
- If the waiter reports failure, inspect its status, runner log, `FAILED.json`, backup, and quarantine. Do not start a second run with the same output directory.
- If failure occurs before metadata commit, the cleaner restores moved transcripts and the index automatically.
- If failure occurs after metadata commit, preserve the backup and quarantine. Diagnose before retrying or restoring.
- If purge refuses the quarantine, preserve it and investigate the mismatch; never broaden the delete.
- If the app remains slow after successful cleanup, investigate renderer/process count, app caches, extensions/plugins, and current-version support separately; do not broaden deletion scope automatically.

## Bundled scripts

- `scripts/inspect_codex_state.py`: read-only aggregate inventory and reclaim estimate.
- `scripts/cleanup_stale_codex_sessions.py`: guarded plan, destructive executor, and exact verified purge.
- `scripts/wait_and_execute.ps1`: Windows app-exit waiter and executor launcher.
- `scripts/verify_cleanup.py`: backup-to-current post-restart audit and plan-linked verification artifact.
- `scripts/test_cleanup_stale_codex_sessions.py`: disposable integration tests for preflight, protection, rollback, quarantine, verification, and purge behavior.

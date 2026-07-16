#!/usr/bin/env python3
"""Compare a completed cleanup with its backups, plan, and quarantine."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    temp = path.with_name(f"{path.name}.tmp-{os.getpid()}")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, path)


def resolve_rollout_path(root: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def verify_cleanup(root: Path, output: Path) -> dict[str, Any]:
    root = root.resolve()
    output = output.resolve()
    backups_root = (root / "backups").resolve()
    if output == backups_root or backups_root not in output.parents:
        raise ValueError("output directory must be a child of CODEX_HOME/backups")

    plan_path = output / "execution-plan.json"
    result_path = output / "result.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    result = json.loads(result_path.read_text(encoding="utf-8"))
    candidates = {str(item["id"]): item for item in plan["candidates"]}
    cutoff_ms = int(datetime.fromisoformat(plan["cutoff"]).timestamp() * 1000)
    backup_dir = output / "backup"
    manifest = json.loads((backup_dir / "manifest.json").read_text(encoding="utf-8"))

    backup = sqlite3.connect(f'file:{backup_dir / "state_5.sqlite"}?mode=ro', uri=True)
    current = sqlite3.connect(f'file:{root / "state_5.sqlite"}?mode=ro', uri=True)
    try:
        before = {
            str(row[0]): (row[1], row[2])
            for row in backup.execute("SELECT id, rollout_path, updated_at_ms FROM threads")
        }
        after = {
            str(row[0]): (row[1], row[2])
            for row in current.execute("SELECT id, rollout_path, updated_at_ms FROM threads")
        }
        removed = set(before) - set(after)
        protected = set(before) - set(candidates)
        recent = {
            thread_id
            for thread_id, (_, updated_at_ms) in before.items()
            if updated_at_ms is None or int(updated_at_ms) >= cutoff_ms
        }
        allowed = [(root / "sessions").resolve(), (root / "archived_sessions").resolve()]
        missing_protected_files = []
        for thread_id in protected & set(after):
            path = resolve_rollout_path(root, str(after[thread_id][0]))
            if any(path == base or base in path.parents for base in allowed) and not path.exists():
                missing_protected_files.append(str(path))
        state_integrity = current.execute("PRAGMA integrity_check").fetchone()[0]
        state_fk_errors = len(list(current.execute("PRAGMA foreign_key_check")))
    finally:
        current.close()
        backup.close()

    logs = sqlite3.connect(f'file:{root / "logs_2.sqlite"}?mode=ro', uri=True)
    try:
        logs_integrity = logs.execute("PRAGMA integrity_check").fetchone()[0]
        current_log_rows = logs.execute("SELECT COUNT(*) FROM logs").fetchone()[0]
    finally:
        logs.close()

    index_ids: set[str] = set()
    index_path = root / "session_index.jsonl"
    if index_path.exists():
        with index_path.open("r", encoding="utf-8") as source:
            index_ids = {str(json.loads(line).get("id", "")) for line in source}
    remaining_candidate_files = [
        item["relative_path"] for item in candidates.values() if (root / item["relative_path"]).exists()
    ]

    quarantine = output / "quarantine"
    actual_quarantine = {
        str(path.resolve()).casefold(): path.resolve()
        for path in quarantine.rglob("*")
        if path.is_file()
    } if quarantine.exists() else {}
    expected_quarantine = {
        str((quarantine / item["relative_path"]).resolve()).casefold(): item
        for item in candidates.values()
    }
    purged = bool(result.get("quarantine_purged_at_utc"))
    quarantine_paths_match = not actual_quarantine if purged else set(actual_quarantine) == set(expected_quarantine)
    quarantine_sizes_match = all(
        actual_quarantine[key].stat().st_size == item["size_bytes"]
        for key, item in expected_quarantine.items()
        if key in actual_quarantine
    )

    result_before = result["logs_db"]["before"]["row_signature"]
    result_after = result["logs_db"]["after"]["row_signature"]
    backup_hashes_match = (
        manifest["execution_plan_sha256"] == sha256(plan_path)
        and manifest["state_backup_sha256"] == sha256(backup_dir / "state_5.sqlite")
        and manifest["logs_backup_sha256"] == sha256(backup_dir / "logs_2.sqlite")
        and (
            manifest["session_index_backup_sha256"] is None
            or manifest["session_index_backup_sha256"] == sha256(backup_dir / "session_index.jsonl")
        )
    )
    checks = {
        "result_status_success": result.get("status") == "success",
        "removed_exactly_execution_candidates": removed == set(candidates),
        "removed_count": len(removed),
        "new_threads_after_restart": len(set(after) - set(before)),
        "missing_protected_rows": len(protected - set(after)),
        "missing_recent_rows": len(recent - set(after)),
        "missing_protected_files": len(missing_protected_files),
        "candidate_files_remaining": len(remaining_candidate_files),
        "candidate_index_entries_remaining": len(set(candidates) & index_ids),
        "state_integrity": state_integrity,
        "state_foreign_key_errors": state_fk_errors,
        "logs_integrity": logs_integrity,
        "vacuum_preserved_log_signature": result_before == result_after,
        "current_log_rows_not_less_than_post_vacuum": current_log_rows >= result_after[0],
        "backup_hashes_match": backup_hashes_match,
        "quarantine_paths_match": quarantine_paths_match,
        "quarantine_sizes_match": quarantine_sizes_match,
        "quarantine_mode": "purged" if purged else "retained",
        "execution_plan_sha256": sha256(plan_path),
        "candidate_ids": sorted(candidates),
    }
    checks["passed"] = all(
        (
            checks["result_status_success"],
            checks["removed_exactly_execution_candidates"],
            checks["missing_protected_rows"] == 0,
            checks["missing_recent_rows"] == 0,
            checks["missing_protected_files"] == 0,
            checks["candidate_files_remaining"] == 0,
            checks["candidate_index_entries_remaining"] == 0,
            state_integrity == "ok",
            state_fk_errors == 0,
            logs_integrity == "ok",
            checks["vacuum_preserved_log_signature"],
            checks["current_log_rows_not_less_than_post_vacuum"],
            backup_hashes_match,
            quarantine_paths_match,
            quarantine_sizes_match,
        )
    )
    write_json(output / "verification.json", checks)
    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.home() / ".codex")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    checks = verify_cleanup(args.root, args.output_dir)
    print(json.dumps(checks, ensure_ascii=False, indent=2))
    return 0 if checks["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

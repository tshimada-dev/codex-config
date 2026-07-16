#!/usr/bin/env python3
"""Guarded cleanup for stale local Codex sessions.

Planning uses aggregate metadata only. Execution validates the approved plan,
backs up mutable databases, and retains transcripts in quarantine until a
separate post-verification purge.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sqlite3
import sys
from collections import Counter, defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_TABLES = {
    "threads": {"id", "rollout_path", "updated_at_ms", "archived"},
    "thread_spawn_edges": {"parent_thread_id", "child_thread_id"},
    "agent_job_items": {"assigned_thread_id"},
    "thread_dynamic_tools": {"thread_id"},
}
LOG_TABLES = {"logs": {"id"}}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f"{path.name}.tmp-{os.getpid()}")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, path)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_rollout_path(root: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def is_within(path: Path, roots: list[Path]) -> bool:
    resolved = path.resolve()
    return any(resolved == root or root in resolved.parents for root in roots)


def connect_readonly(path: Path) -> sqlite3.Connection:
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=5)


def require_tables(connection: sqlite3.Connection, requirements: dict[str, set[str]], label: str) -> None:
    for table, required_columns in requirements.items():
        columns = {str(row[1]) for row in connection.execute(f'PRAGMA table_info("{table}")')}
        if not columns:
            raise RuntimeError(f"{label} is missing required table: {table}")
        missing = required_columns - columns
        if missing:
            raise RuntimeError(f"{label}.{table} is missing required columns: {sorted(missing)}")


def validate_database(path: Path, requirements: dict[str, set[str]], label: str) -> None:
    if not path.is_file():
        raise FileNotFoundError(path)
    connection = connect_readonly(path)
    try:
        require_tables(connection, requirements, label)
        quick_check = connection.execute("PRAGMA quick_check").fetchone()[0]
        if quick_check != "ok":
            raise RuntimeError(f"{label} quick_check failed: {quick_check}")
        foreign_key_errors = list(connection.execute("PRAGMA foreign_key_check"))
        if foreign_key_errors:
            raise RuntimeError(f"{label} foreign_key_check failed")
    finally:
        connection.close()


def validate_runtime_state(root: Path) -> None:
    validate_database(root / "state_5.sqlite", STATE_TABLES, "state_5.sqlite")
    validate_database(root / "logs_2.sqlite", LOG_TABLES, "logs_2.sqlite")
    index_path = root / "session_index.jsonl"
    if index_path.exists() and not index_path.is_file():
        raise RuntimeError("session_index.jsonl exists but is not a file")


def validate_output_dir(root: Path, output_dir: Path, *, must_not_exist: bool) -> Path:
    root = root.resolve()
    output = output_dir.resolve()
    backups_root = (root / "backups").resolve()
    if output == backups_root or backups_root not in output.parents:
        raise ValueError("output directory must be a unique child of CODEX_HOME/backups")
    if must_not_exist and output.exists():
        raise FileExistsError(output)
    if not must_not_exist and not output.is_dir():
        raise FileNotFoundError(output)
    return output


def build_plan(root: Path, cutoff: datetime) -> dict[str, Any]:
    root = root.resolve()
    if cutoff.tzinfo is None:
        raise ValueError("cutoff must include a timezone")
    allowed_roots = [(root / "sessions").resolve(), (root / "archived_sessions").resolve()]
    state_path = root / "state_5.sqlite"
    if not state_path.is_file():
        raise FileNotFoundError(state_path)

    cutoff_s = cutoff.timestamp()
    cutoff_ms = int(cutoff_s * 1000)
    connection = connect_readonly(state_path)
    connection.row_factory = sqlite3.Row
    try:
        require_tables(connection, {key: STATE_TABLES[key] for key in ("threads", "thread_spawn_edges", "agent_job_items")}, "state_5.sqlite")
        rows = list(connection.execute("SELECT id, rollout_path, updated_at_ms, archived FROM threads"))
        edges = [tuple(row) for row in connection.execute("SELECT parent_thread_id, child_thread_id FROM thread_spawn_edges")]
        job_refs = {
            str(row[0])
            for row in connection.execute(
                "SELECT assigned_thread_id FROM agent_job_items WHERE assigned_thread_id IS NOT NULL"
            )
        }
    finally:
        connection.close()

    stats: Counter[str] = Counter()
    base_candidates: set[str] = set()
    protected_seeds: set[str] = set()
    row_by_id: dict[str, sqlite3.Row] = {}
    path_by_id: dict[str, Path] = {}

    for row in rows:
        thread_id = str(row["id"])
        row_by_id[thread_id] = row
        raw_path = row["rollout_path"]
        if not raw_path:
            stats["protected_missing_path"] += 1
            protected_seeds.add(thread_id)
            continue
        path = resolve_rollout_path(root, str(raw_path))
        if not is_within(path, allowed_roots) or path.suffix.lower() != ".jsonl":
            stats["protected_outside_allowed_roots"] += 1
            protected_seeds.add(thread_id)
            continue
        if not path.is_file():
            stats["protected_missing_file"] += 1
            protected_seeds.add(thread_id)
            continue
        path_by_id[thread_id] = path
        file_is_old = path.stat().st_mtime < cutoff_s
        updated_at_ms = row["updated_at_ms"]
        db_is_old = updated_at_ms is not None and int(updated_at_ms) < cutoff_ms
        if file_is_old and db_is_old:
            base_candidates.add(thread_id)
        else:
            protected_seeds.add(thread_id)
            stats["protected_recent_or_unknown_signal"] += 1
            if not file_is_old:
                stats["protected_recent_file_signal"] += 1
            if not db_is_old:
                stats["protected_recent_or_unknown_db_signal"] += 1

    protected_seeds.update(job_refs)
    adjacency: dict[str, set[str]] = defaultdict(set)
    for parent_id, child_id in edges:
        adjacency[str(parent_id)].add(str(child_id))
        adjacency[str(child_id)].add(str(parent_id))
    connected_protected = set(protected_seeds)
    queue = deque(protected_seeds)
    while queue:
        thread_id = queue.popleft()
        for neighbor in adjacency.get(thread_id, ()):
            if neighbor not in connected_protected:
                connected_protected.add(neighbor)
                queue.append(neighbor)

    candidate_ids = base_candidates - connected_protected
    candidates: list[dict[str, Any]] = []
    seen_paths: set[str] = set()
    for thread_id in sorted(candidate_ids):
        path = path_by_id[thread_id]
        path_key = str(path).casefold()
        if path_key in seen_paths:
            raise RuntimeError(f"duplicate rollout path detected for candidate {thread_id}")
        seen_paths.add(path_key)
        row = row_by_id[thread_id]
        stat = path.stat()
        candidates.append(
            {
                "id": thread_id,
                "relative_path": str(path.relative_to(root)),
                "size_bytes": stat.st_size,
                "file_mtime_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                "db_updated_at_ms": int(row["updated_at_ms"]),
                "archived": bool(row["archived"]),
            }
        )

    all_files: dict[str, Path] = {}
    for allowed_root in allowed_roots:
        if allowed_root.exists():
            for path in allowed_root.rglob("*.jsonl"):
                all_files[str(path.resolve()).casefold()] = path.resolve()
    mapped_paths = {str(path).casefold() for path in path_by_id.values()}
    unmapped_files = [path for key, path in all_files.items() if key not in mapped_paths]
    cross_boundary_edges = sum(
        (str(parent_id) in candidate_ids) != (str(child_id) in candidate_ids)
        for parent_id, child_id in edges
    )
    if cross_boundary_edges:
        raise RuntimeError("candidate set crosses a protected spawn-tree boundary")

    stats.update(
        {
            "thread_rows": len(rows),
            "base_candidates": len(base_candidates),
            "protected_by_connected_work": len(base_candidates & connected_protected),
            "final_candidates": len(candidates),
            "candidate_bytes": sum(item["size_bytes"] for item in candidates),
            "protected_thread_rows": len(rows) - len(candidates),
            "unmapped_files_preserved": len(unmapped_files),
            "unmapped_old_files_preserved": sum(path.stat().st_mtime < cutoff_s for path in unmapped_files),
            "cross_boundary_edges": cross_boundary_edges,
        }
    )
    return {
        "schema_version": 1,
        "generated_at_utc": utc_now(),
        "root": str(root),
        "cutoff": cutoff.isoformat(),
        "policy": {
            "requires_file_mtime_before_cutoff": True,
            "requires_db_updated_at_before_cutoff": True,
            "protects_connected_spawn_tree": True,
            "protects_agent_job_references": True,
            "preserves_unmapped_files": True,
        },
        "stats": dict(stats),
        "candidates": candidates,
    }


def candidate_identity(item: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(
        item.get(key)
        for key in ("id", "relative_path", "size_bytes", "file_mtime_utc", "db_updated_at_ms", "archived")
    )


def validate_baseline(baseline: dict[str, Any], plan: dict[str, Any], root: Path, cutoff: datetime) -> set[str]:
    if baseline.get("schema_version") != 1:
        raise RuntimeError("baseline uses an unsupported schema_version")
    if Path(str(baseline.get("root", ""))).resolve() != root.resolve():
        raise RuntimeError("baseline root does not match the execution root")
    baseline_cutoff = datetime.fromisoformat(str(baseline.get("cutoff", "")))
    if baseline_cutoff.tzinfo is None or baseline_cutoff.timestamp() != cutoff.timestamp():
        raise RuntimeError("baseline cutoff does not match the execution cutoff")
    baseline_items = {str(item["id"]): item for item in baseline.get("candidates", [])}
    if len(baseline_items) != len(baseline.get("candidates", [])):
        raise RuntimeError("baseline contains duplicate candidate IDs")
    current_items = {str(item["id"]): item for item in plan["candidates"]}
    unexpected = set(current_items) - set(baseline_items)
    if unexpected:
        raise RuntimeError(f"execution plan introduced {len(unexpected)} candidates absent from baseline")
    changed = [
        thread_id
        for thread_id, item in current_items.items()
        if candidate_identity(item) != candidate_identity(baseline_items[thread_id])
    ]
    if changed:
        raise RuntimeError(f"execution candidates changed materially since approval: {len(changed)}")
    return set(baseline_items)


def backup_sqlite(source_path: Path, destination_path: Path) -> None:
    source = connect_readonly(source_path)
    destination = sqlite3.connect(destination_path)
    try:
        source.backup(destination)
    finally:
        destination.close()
        source.close()


def rewrite_session_index(index_path: Path, candidate_ids: set[str]) -> int:
    if not index_path.exists():
        return 0
    temp = index_path.with_name(f"{index_path.name}.tmp-{os.getpid()}")
    removed = 0
    try:
        with index_path.open("r", encoding="utf-8") as source, temp.open("w", encoding="utf-8", newline="\n") as target:
            for line in source:
                item = json.loads(line)
                if str(item.get("id", "")) in candidate_ids:
                    removed += 1
                    continue
                target.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")
        os.replace(temp, index_path)
    finally:
        temp.unlink(missing_ok=True)
    return removed


def remove_empty_parents(path: Path, stop_roots: list[Path]) -> None:
    current = path.resolve()
    stop = {str(root.resolve()).casefold() for root in stop_roots}
    while str(current).casefold() not in stop:
        try:
            current.rmdir()
        except OSError:
            break
        current = current.parent


def sqlite_metrics(path: Path, table: str | None = None) -> dict[str, Any]:
    connection = sqlite3.connect(path, timeout=10)
    try:
        metrics: dict[str, Any] = {
            "file_bytes": path.stat().st_size,
            "page_size": connection.execute("PRAGMA page_size").fetchone()[0],
            "page_count": connection.execute("PRAGMA page_count").fetchone()[0],
            "freelist_count": connection.execute("PRAGMA freelist_count").fetchone()[0],
        }
        if table:
            metrics["row_signature"] = list(
                connection.execute(
                    f'SELECT COUNT(*), COALESCE(MIN(id), 0), COALESCE(MAX(id), 0) FROM "{table}"'
                ).fetchone()
            )
        return metrics
    finally:
        connection.close()


def vacuum_and_check(path: Path, table: str | None = None) -> dict[str, Any]:
    before = sqlite_metrics(path, table)
    connection = sqlite3.connect(path, timeout=30)
    try:
        connection.execute("PRAGMA busy_timeout=30000")
        connection.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
        connection.execute("VACUUM")
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        foreign_key_errors = list(connection.execute("PRAGMA foreign_key_check"))
    finally:
        connection.close()
    after = sqlite_metrics(path, table)
    if integrity != "ok":
        raise RuntimeError(f"integrity_check failed for {path.name}: {integrity}")
    if foreign_key_errors:
        raise RuntimeError(f"foreign_key_check failed for {path.name}")
    if table and before["row_signature"] != after["row_signature"]:
        raise RuntimeError(f"row signature changed during VACUUM for {path.name}")
    return {"before": before, "after": after, "integrity_check": integrity}


def execute_cleanup(root: Path, cutoff: datetime, output_dir: Path, baseline_path: Path) -> dict[str, Any]:
    root = root.resolve()
    output_dir = validate_output_dir(root, output_dir, must_not_exist=True)
    if not baseline_path.is_file():
        raise FileNotFoundError(baseline_path)
    validate_runtime_state(root)
    plan = build_plan(root, cutoff)
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    baseline_ids = validate_baseline(baseline, plan, root, cutoff)

    allowed_roots = [(root / "sessions").resolve(), (root / "archived_sessions").resolve()]
    output_dir.mkdir(parents=True)
    lock_path = output_dir / "cleanup.lock"
    lock_fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.write(lock_fd, f"pid={os.getpid()} started={utc_now()}\n".encode("utf-8"))
    os.close(lock_fd)
    result: dict[str, Any] = {"status": "running", "started_at_utc": utc_now()}
    write_json(output_dir / "result.json", result)
    write_json(output_dir / "execution-plan.json", plan)

    backup_dir = output_dir / "backup"
    backup_dir.mkdir()
    state_path = root / "state_5.sqlite"
    logs_path = root / "logs_2.sqlite"
    index_path = root / "session_index.jsonl"
    state_backup = backup_dir / "state_5.sqlite"
    logs_backup = backup_dir / "logs_2.sqlite"
    backup_sqlite(state_path, state_backup)
    backup_sqlite(logs_path, logs_backup)
    if index_path.exists():
        shutil.copy2(index_path, backup_dir / "session_index.jsonl")
    manifest = {
        "created_at_utc": utc_now(),
        "baseline_sha256": sha256(baseline_path),
        "execution_plan_sha256": sha256(output_dir / "execution-plan.json"),
        "state_backup_sha256": sha256(state_backup),
        "logs_backup_sha256": sha256(logs_backup),
        "session_index_backup_sha256": sha256(backup_dir / "session_index.jsonl")
        if (backup_dir / "session_index.jsonl").exists()
        else None,
        "candidate_count": len(plan["candidates"]),
        "candidate_bytes": plan["stats"]["candidate_bytes"],
    }
    write_json(backup_dir / "manifest.json", manifest)

    candidate_ids = {str(item["id"]) for item in plan["candidates"]}
    quarantine = output_dir / "quarantine"
    moved: list[tuple[Path, Path]] = []
    index_rewritten = False
    db_committed = False
    try:
        for item in plan["candidates"]:
            relative = Path(item["relative_path"])
            source = (root / relative).resolve()
            if not is_within(source, allowed_roots) or source.suffix.lower() != ".jsonl":
                raise RuntimeError(f"unsafe candidate path for {item['id']}")
            current_stat = source.stat()
            current_identity = (
                current_stat.st_size,
                datetime.fromtimestamp(current_stat.st_mtime, timezone.utc).isoformat(),
            )
            approved_identity = (item["size_bytes"], item["file_mtime_utc"])
            if current_identity != approved_identity:
                raise RuntimeError(f"candidate file changed after execution planning: {item['id']}")
            destination = (quarantine / relative).resolve()
            if not is_within(destination, [quarantine.resolve()]):
                raise RuntimeError(f"unsafe quarantine path for {item['id']}")
            destination.parent.mkdir(parents=True, exist_ok=True)
            os.replace(source, destination)
            moved.append((source, destination))

        rewrite_session_index(index_path, candidate_ids)
        index_rewritten = True
        connection = sqlite3.connect(state_path, timeout=10)
        try:
            connection.execute("PRAGMA foreign_keys=ON")
            connection.execute("PRAGMA busy_timeout=10000")
            connection.execute("BEGIN IMMEDIATE")
            connection.execute("CREATE TEMP TABLE cleanup_candidate_ids (id TEXT PRIMARY KEY)")
            connection.executemany("INSERT INTO cleanup_candidate_ids(id) VALUES (?)", [(item,) for item in candidate_ids])
            active_job_refs = connection.execute(
                "SELECT COUNT(*) FROM agent_job_items WHERE assigned_thread_id IN (SELECT id FROM cleanup_candidate_ids)"
            ).fetchone()[0]
            if active_job_refs:
                raise RuntimeError("a cleanup candidate became referenced by an agent job")
            connection.execute(
                "DELETE FROM thread_spawn_edges WHERE parent_thread_id IN (SELECT id FROM cleanup_candidate_ids) "
                "OR child_thread_id IN (SELECT id FROM cleanup_candidate_ids)"
            )
            connection.execute("DELETE FROM thread_dynamic_tools WHERE thread_id IN (SELECT id FROM cleanup_candidate_ids)")
            connection.execute("DELETE FROM threads WHERE id IN (SELECT id FROM cleanup_candidate_ids)")
            deleted_threads = connection.execute("SELECT changes()").fetchone()[0]
            if deleted_threads != len(candidate_ids):
                raise RuntimeError(
                    f"thread deletion count mismatch: expected {len(candidate_ids)}, got {deleted_threads}"
                )
            connection.commit()
            db_committed = True
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
    except Exception:
        if not db_committed:
            if index_rewritten and (backup_dir / "session_index.jsonl").exists():
                shutil.copy2(backup_dir / "session_index.jsonl", index_path)
            for source, destination in reversed(moved):
                if destination.exists() and not source.exists():
                    source.parent.mkdir(parents=True, exist_ok=True)
                    os.replace(destination, source)
        raise

    for source, _ in moved:
        remove_empty_parents(source.parent, allowed_roots)
    state_vacuum = vacuum_and_check(state_path)
    logs_vacuum = vacuum_and_check(logs_path, "logs")
    result = {
        "status": "success",
        "started_at_utc": result["started_at_utc"],
        "finished_at_utc": utc_now(),
        "cutoff": cutoff.isoformat(),
        "removed_thread_rows": len(candidate_ids),
        "quarantined_transcripts": len(moved),
        "transcript_bytes_pending_purge": plan["stats"]["candidate_bytes"],
        "baseline_candidates": len(baseline_ids),
        "protected_since_baseline": len(baseline_ids - candidate_ids),
        "state_db": state_vacuum,
        "logs_db": logs_vacuum,
        "backup_dir": str(backup_dir),
        "quarantine_dir": str(quarantine),
    }
    write_json(output_dir / "result.json", result)
    (output_dir / "SUCCESS").write_text(result["finished_at_utc"] + "\n", encoding="utf-8")
    lock_path.unlink(missing_ok=True)
    return result


def purge_quarantine(root: Path, output_dir: Path) -> dict[str, Any]:
    root = root.resolve()
    output_dir = validate_output_dir(root, output_dir, must_not_exist=False)
    plan_path = output_dir / "execution-plan.json"
    result_path = output_dir / "result.json"
    verification_path = output_dir / "verification.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    result = json.loads(result_path.read_text(encoding="utf-8"))
    verification = json.loads(verification_path.read_text(encoding="utf-8"))
    if result.get("status") != "success" or result.get("quarantine_purged_at_utc"):
        raise RuntimeError("cleanup result is not eligible for quarantine purge")
    if not verification.get("passed"):
        raise RuntimeError("post-restart verification has not passed")
    if verification.get("execution_plan_sha256") != sha256(plan_path):
        raise RuntimeError("verification does not match the execution plan")
    expected_ids = sorted(str(item["id"]) for item in plan["candidates"])
    if verification.get("candidate_ids") != expected_ids or verification.get("quarantine_mode") != "retained":
        raise RuntimeError("verification is not for the retained candidate quarantine")

    quarantine = (output_dir / "quarantine").resolve()
    expected: dict[str, dict[str, Any]] = {}
    for item in plan["candidates"]:
        destination = (quarantine / item["relative_path"]).resolve()
        if not is_within(destination, [quarantine]):
            raise RuntimeError(f"unsafe quarantine path for {item['id']}")
        expected[str(destination).casefold()] = item
    actual_files = [path.resolve() for path in quarantine.rglob("*") if path.is_file()] if quarantine.exists() else []
    if {str(path).casefold() for path in actual_files} != set(expected):
        raise RuntimeError("quarantine contents do not exactly match the verified execution plan")
    purged_bytes = 0
    for path in actual_files:
        item = expected[str(path).casefold()]
        if path.stat().st_size != item["size_bytes"]:
            raise RuntimeError(f"quarantined transcript size changed: {item['id']}")
        purged_bytes += path.stat().st_size
    for path in actual_files:
        path.unlink()
        remove_empty_parents(path.parent, [quarantine])
    if quarantine.exists():
        quarantine.rmdir()

    result["quarantine_purged_at_utc"] = utc_now()
    result["purged_transcript_bytes"] = purged_bytes
    result["transcript_bytes_pending_purge"] = 0
    write_json(result_path, result)
    (output_dir / "PURGED").write_text(result["quarantine_purged_at_utc"] + "\n", encoding="utf-8")
    return result


def parse_cutoff(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise argparse.ArgumentTypeError("cutoff must include an explicit timezone offset")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.home() / ".codex")
    parser.add_argument("--cutoff", type=parse_cutoff)
    parser.add_argument("--plan-output", type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--execute", action="store_true")
    mode.add_argument("--purge-quarantine", action="store_true")
    parser.add_argument("--ack-app-stopped", action="store_true")
    parser.add_argument("--ack-verified", action="store_true")
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()

    if args.purge_quarantine:
        if not args.ack_verified:
            parser.error("--purge-quarantine requires --ack-verified")
        if not args.output_dir:
            parser.error("--purge-quarantine requires --output-dir")
        try:
            result = purge_quarantine(args.root, args.output_dir)
        except Exception as exc:
            print(f"purge failed: {type(exc).__name__}: {exc}", file=sys.stderr)
            return 1
        print(json.dumps({"status": "purged", "purged_transcript_bytes": result["purged_transcript_bytes"]}))
        return 0

    if args.cutoff is None:
        parser.error("--cutoff is required for planning and execution")
    if not args.execute:
        plan = build_plan(args.root, args.cutoff)
        if args.plan_output:
            write_json(args.plan_output, plan)
        print(
            json.dumps(
                {
                    "status": "dry-run",
                    "cutoff": plan["cutoff"],
                    "candidate_count": plan["stats"]["final_candidates"],
                    "candidate_mb": round(plan["stats"]["candidate_bytes"] / 1048576, 2),
                    "protected_thread_rows": plan["stats"]["protected_thread_rows"],
                    "unmapped_files_preserved": plan["stats"]["unmapped_files_preserved"],
                },
                ensure_ascii=False,
            )
        )
        return 0

    if not args.ack_app_stopped:
        parser.error("--execute requires --ack-app-stopped")
    if not args.baseline or not args.output_dir:
        parser.error("--execute requires --baseline and --output-dir")
    try:
        result = execute_cleanup(args.root, args.cutoff, args.output_dir, args.baseline)
    except Exception as exc:
        if args.output_dir and args.output_dir.exists():
            try:
                write_json(
                    args.output_dir / "FAILED.json",
                    {"status": "failed", "finished_at_utc": utc_now(), "error_type": type(exc).__name__, "error": str(exc)},
                )
            except Exception:
                pass
        print(f"cleanup failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "status": result["status"],
                "removed_thread_rows": result["removed_thread_rows"],
                "quarantined_transcripts": result["quarantined_transcripts"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

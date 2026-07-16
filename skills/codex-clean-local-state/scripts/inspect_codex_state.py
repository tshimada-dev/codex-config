#!/usr/bin/env python3
"""Report aggregate Codex local-state size and age without reading contents."""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path


def tree_metrics(path: Path) -> dict[str, int]:
    files = 0
    size = 0
    if path.is_file():
        return {"files": 1, "bytes": path.stat().st_size}
    if not path.exists():
        return {"files": 0, "bytes": 0}
    for root, _, names in os.walk(path):
        for name in names:
            candidate = Path(root) / name
            try:
                size += candidate.stat().st_size
                files += 1
            except OSError:
                continue
    return {"files": files, "bytes": size}


def session_metrics(path: Path, cutoff_s: float) -> dict[str, int]:
    files = list(path.rglob("*.jsonl")) if path.exists() else []
    old = [item for item in files if item.stat().st_mtime < cutoff_s]
    return {
        "files": len(files),
        "bytes": sum(item.stat().st_size for item in files),
        "older_than_cutoff_files": len(old),
        "older_than_cutoff_bytes": sum(item.stat().st_size for item in old),
    }


def sqlite_metrics(path: Path) -> dict[str, int | str]:
    if not path.exists():
        return {"status": "missing"}
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=5)
    try:
        page_size = connection.execute("PRAGMA page_size").fetchone()[0]
        page_count = connection.execute("PRAGMA page_count").fetchone()[0]
        free_pages = connection.execute("PRAGMA freelist_count").fetchone()[0]
        return {
            "status": "ok",
            "file_bytes": path.stat().st_size,
            "page_size": page_size,
            "page_count": page_count,
            "freelist_count": free_pages,
            "reclaimable_bytes_estimate": page_size * free_pages,
            "live_page_bytes_estimate": page_size * (page_count - free_pages),
        }
    finally:
        connection.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.home() / ".codex")
    parser.add_argument("--days", type=float, default=14.0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.days <= 0:
        parser.error("--days must be positive")
    root = args.root.resolve()
    now = datetime.now().astimezone()
    cutoff = now - timedelta(days=args.days)
    top_level = {}
    if root.exists():
        for item in root.iterdir():
            metrics = tree_metrics(item)
            top_level[item.name] = {"type": "dir" if item.is_dir() else "file", **metrics}
    report = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "days": args.days,
        "cutoff": cutoff.isoformat(),
        "top_level": dict(sorted(top_level.items(), key=lambda pair: pair[1]["bytes"], reverse=True)),
        "sessions": session_metrics(root / "sessions", cutoff.timestamp()),
        "archived_sessions": session_metrics(root / "archived_sessions", cutoff.timestamp()),
        "databases": {
            "state_5.sqlite": sqlite_metrics(root / "state_5.sqlite"),
            "logs_2.sqlite": sqlite_metrics(root / "logs_2.sqlite"),
        },
    }
    serialized = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

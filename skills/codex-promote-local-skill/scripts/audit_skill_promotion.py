#!/usr/bin/env python3
"""Create local Skill snapshots and verify promotion before old-Skill removal."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
SKILL_NAME_PATTERN = re.compile(r"^codex-[a-z0-9-]+$")
IGNORED_DIRECTORY_NAMES = {".git", "__pycache__"}
IGNORED_FILE_NAMES = {".DS_Store", "Thumbs.db"}
IGNORED_SUFFIXES = {".pyc", ".pyo"}
SENSITIVE_EXACT_NAMES = {
    ".env",
    "auth.json",
    "credentials.json",
    "secrets.json",
    "id_rsa",
    "id_ed25519",
}
SENSITIVE_SUFFIXES = {".key", ".p12", ".pem", ".pfx"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_ignored(relative_path: Path) -> bool:
    return (
        any(part in IGNORED_DIRECTORY_NAMES for part in relative_path.parts[:-1])
        or relative_path.name in IGNORED_FILE_NAMES
        or relative_path.suffix.casefold() in IGNORED_SUFFIXES
    )


def is_sensitive_looking(relative_path: Path) -> bool:
    name = relative_path.name.casefold()
    return (
        name in SENSITIVE_EXACT_NAMES
        or name.startswith(".env.")
        or relative_path.suffix.casefold() in SENSITIVE_SUFFIXES
    )


def snapshot_tree(path: Path) -> dict[str, Any]:
    root = path.resolve()
    if not root.is_dir():
        raise FileNotFoundError(root)
    files: dict[str, dict[str, Any]] = {}
    sensitive_paths: list[str] = []
    for item in sorted(root.rglob("*")):
        if item.is_symlink() or (hasattr(item, "is_junction") and item.is_junction()):
            raise RuntimeError(f"skill tree contains an unsupported link: {item.relative_to(root)}")
        if not item.is_file():
            continue
        relative = item.relative_to(root)
        if is_ignored(relative):
            continue
        key = relative.as_posix()
        files[key] = {"size_bytes": item.stat().st_size, "sha256": sha256(item)}
        if is_sensitive_looking(relative):
            sensitive_paths.append(key)
    return {
        "schema_version": SCHEMA_VERSION,
        "root": str(root),
        "files": files,
        "sensitive_paths": sorted(sensitive_paths),
    }


def write_json(path: Path, value: Any) -> None:
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f"{path.name}.tmp-{os.getpid()}")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, path)


def write_snapshot(source_path: Path, output_path: Path) -> dict[str, Any]:
    snapshot = snapshot_tree(source_path)
    write_json(output_path, snapshot)
    return snapshot


def run_git(repo_root: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo_root), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"git {' '.join(arguments)} failed: {detail}")
    return result.stdout


def require_direct_child(path: Path, parent: Path, label: str) -> None:
    if path.parent != parent:
        raise ValueError(f"{label} must be a direct child of {parent}")


def compare_snapshots(expected: dict[str, Any], actual: dict[str, Any], label: str) -> None:
    if expected.get("schema_version") != SCHEMA_VERSION:
        raise RuntimeError(f"{label} snapshot uses an unsupported schema_version")
    if expected.get("root") != actual.get("root"):
        raise RuntimeError(f"{label} snapshot root does not match")
    if expected.get("files") != actual.get("files"):
        raise RuntimeError(f"{label} changed after the approved snapshot")
    if expected.get("sensitive_paths") != actual.get("sensitive_paths"):
        raise RuntimeError(f"{label} sensitive-path inventory changed after the approved snapshot")


def verify_installed_skill(
    *,
    repo_root: Path,
    skill_name: str,
    codex_home: Path,
) -> dict[str, Any]:
    if not SKILL_NAME_PATTERN.fullmatch(skill_name):
        raise ValueError("promoted skill name must match codex-[a-z0-9-]+")

    repo_root = repo_root.resolve()
    codex_home = codex_home.resolve()
    repo_skills_root = (repo_root / "skills").resolve()
    installed_skills_root = (codex_home / "skills").resolve()
    repo_skill = (repo_skills_root / skill_name).resolve()
    installed_skill = (installed_skills_root / skill_name).resolve()
    require_direct_child(repo_skill, repo_skills_root, "repository skill")
    require_direct_child(installed_skill, installed_skills_root, "installed skill")
    if not repo_skill.is_dir():
        raise FileNotFoundError(repo_skill)
    if not installed_skill.is_dir():
        raise FileNotFoundError(installed_skill)

    source_commit = run_git(repo_root, "rev-parse", "HEAD").strip()
    relative_skill_root = f"skills/{skill_name}"
    status = run_git(
        repo_root,
        "status",
        "--porcelain",
        "--untracked-files=all",
        "--",
        relative_skill_root,
    ).strip()
    if status:
        raise RuntimeError("repository skill must be fully tracked and committed")

    tracked_paths = sorted(
        line.strip().replace("\\", "/")
        for line in run_git(repo_root, "ls-files", "--", relative_skill_root).splitlines()
        if line.strip()
    )
    if not tracked_paths:
        raise RuntimeError("promoted skill has no tracked repository files")
    tracked_relative = [
        path.removeprefix(relative_skill_root + "/")
        for path in tracked_paths
        if path.startswith(relative_skill_root + "/")
    ]
    repo_snapshot = snapshot_tree(repo_skill)
    if sorted(repo_snapshot["files"]) != tracked_relative:
        raise RuntimeError("repository skill tree does not exactly match tracked repository files")
    if repo_snapshot["sensitive_paths"]:
        raise RuntimeError("repository skill contains sensitive-looking files")

    installed_snapshot = snapshot_tree(installed_skill)
    comparable_repo = {
        "files": repo_snapshot["files"],
        "sensitive_paths": repo_snapshot["sensitive_paths"],
    }
    comparable_installed = {
        "files": installed_snapshot["files"],
        "sensitive_paths": installed_snapshot["sensitive_paths"],
    }
    if comparable_repo != comparable_installed:
        raise RuntimeError("installed skill tree does not exactly match the committed repository skill")

    manifest_path = codex_home / ".codex-config-managed-files"
    if not manifest_path.is_file():
        raise FileNotFoundError(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1:
        raise RuntimeError("managed file manifest uses an unsupported schema_version")
    if manifest.get("source_commit") != source_commit:
        raise RuntimeError("managed file manifest source_commit does not match repository HEAD")
    managed_files = sorted(str(item).replace("\\", "/") for item in manifest.get("managed_files", []))
    if sorted(path for path in managed_files if path.startswith(relative_skill_root + "/")) != tracked_paths:
        raise RuntimeError("managed file manifest does not exactly cover the promoted skill")

    return {
        "status": "verified",
        "installed_skill_verified": True,
        "source_commit": source_commit,
        "skill_name": skill_name,
        "repo_skill": str(repo_skill),
        "installed_skill": str(installed_skill),
        "managed_skill_files": len(tracked_paths),
    }


def verify_promotion(
    *,
    repo_root: Path,
    skill_name: str,
    codex_home: Path,
    old_skill_path: Path,
    source_snapshot_path: Path,
) -> dict[str, Any]:
    codex_home = codex_home.resolve()
    installed_skills_root = (codex_home / "skills").resolve()
    installed_skill = (installed_skills_root / skill_name).resolve()
    old_skill = old_skill_path.resolve()
    require_direct_child(old_skill, installed_skills_root, "old skill")
    if old_skill == installed_skill:
        raise ValueError("old skill path must differ from the promoted installed skill")
    if not old_skill.is_dir():
        raise FileNotFoundError(old_skill)
    if not source_snapshot_path.is_file():
        raise FileNotFoundError(source_snapshot_path)

    expected_old = json.loads(source_snapshot_path.read_text(encoding="utf-8"))
    actual_old = snapshot_tree(old_skill)
    compare_snapshots(expected_old, actual_old, "old skill")
    if expected_old.get("sensitive_paths"):
        raise RuntimeError(
            "old skill contains sensitive-looking files; resolve them explicitly before removal"
        )

    result = verify_installed_skill(
        repo_root=repo_root,
        skill_name=skill_name,
        codex_home=codex_home,
    )
    result.update(
        {
            "ready_for_old_skill_removal": True,
            "old_skill": str(old_skill),
            "old_skill_files": len(expected_old["files"]),
        }
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    snapshot_parser = subparsers.add_parser("snapshot")
    snapshot_parser.add_argument("--path", type=Path, required=True)
    snapshot_parser.add_argument("--output", type=Path, required=True)

    install_parser = subparsers.add_parser("verify-install")
    install_parser.add_argument("--repo-root", type=Path, required=True)
    install_parser.add_argument("--skill-name", required=True)
    install_parser.add_argument("--codex-home", type=Path, required=True)

    removal_parser = subparsers.add_parser("verify-removal")
    removal_parser.add_argument("--repo-root", type=Path, required=True)
    removal_parser.add_argument("--skill-name", required=True)
    removal_parser.add_argument("--codex-home", type=Path, required=True)
    removal_parser.add_argument("--old-skill-path", type=Path, required=True)
    removal_parser.add_argument("--source-snapshot", type=Path, required=True)

    args = parser.parse_args()
    try:
        if args.command == "snapshot":
            result = write_snapshot(args.path, args.output)
            summary = {
                "status": "snapshotted",
                "root": result["root"],
                "file_count": len(result["files"]),
                "sensitive_paths": result["sensitive_paths"],
                "output": str(args.output.resolve()),
            }
        elif args.command == "verify-install":
            summary = verify_installed_skill(
                repo_root=args.repo_root,
                skill_name=args.skill_name,
                codex_home=args.codex_home,
            )
        else:
            summary = verify_promotion(
                repo_root=args.repo_root,
                skill_name=args.skill_name,
                codex_home=args.codex_home,
                old_skill_path=args.old_skill_path,
                source_snapshot_path=args.source_snapshot,
            )
    except Exception as exc:
        print(f"audit failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

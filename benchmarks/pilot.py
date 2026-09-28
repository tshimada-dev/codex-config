from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TASKS = ROOT / "tasks"
SEEDS = ROOT / "seeds"
HIDDEN = ROOT / "hidden"

TASK_IDS = ("INV-001", "DBG-001", "IMP-001", "SAFE-001", "REV-001")


def run(cmd, cwd: Path):
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)


def prepare(task_id: str, dest: Path) -> int:
    if task_id not in TASK_IDS:
        raise SystemExit(f"unknown task: {task_id}")
    if dest.exists() and any(dest.iterdir()):
        raise SystemExit(f"destination is not empty: {dest}")
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SEEDS / task_id, dest, dirs_exist_ok=True)
    shutil.copy2(TASKS / f"{task_id}.md", dest / "TASK.md")
    r = run(["git", "init"], dest)
    if r.returncode:
        print(r.stderr, file=sys.stderr)
        return r.returncode
    for cmd in (
        ["git", "config", "user.email", "benchmark@example.invalid"],
        ["git", "config", "user.name", "Benchmark Harness"],
        ["git", "add", "."],
        ["git", "commit", "-m", "benchmark seed"],
    ):
        r = run(cmd, dest)
        if r.returncode:
            print(r.stdout)
            print(r.stderr, file=sys.stderr)
            return r.returncode
    print(dest)
    return 0


def grade(task_id: str, dest: Path) -> int:
    if task_id not in TASK_IDS:
        raise SystemExit(f"unknown task: {task_id}")
    if not (dest / ".git").exists():
        raise SystemExit("grade target must be created by prepare")

    public = run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], dest)
    hidden_file = HIDDEN / f"test_{task_id.lower().replace('-', '_')}.py"
    hidden = run([sys.executable, str(hidden_file), str(dest.resolve())], ROOT.parent)

    diff = run(["git", "diff", "--name-only", "HEAD"], dest)
    changed = [x.strip() for x in diff.stdout.splitlines() if x.strip()]
    allowed = {
        "INV-001": ("src/", "tests/"),
        "DBG-001": ("src/", "tests/"),
        "IMP-001": ("src/", "tests/"),
        "SAFE-001": ("src/", "tests/"),
        "REV-001": ("src/", "tests/"),
    }[task_id]
    violations = [p for p in changed if not p.startswith(allowed)]

    result = {
        "task_id": task_id,
        "public_tests_passed": public.returncode == 0,
        "hidden_tests_passed": hidden.returncode == 0,
        "scope_passed": not violations,
        "changed_files": changed,
        "scope_violations": violations,
        "passed": public.returncode == 0 and hidden.returncode == 0 and not violations,
        "public_output": public.stdout + public.stderr,
        "hidden_output": hidden.stdout + hidden.stderr,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["passed"] else 1


def gate(results_path: Path) -> int:
    data = json.loads(results_path.read_text(encoding="utf-8"))
    grouped = defaultdict(list)
    for row in data.get("runs", []):
        if row.get("variant") == "baseline":
            grouped[row["task_id"]].append(bool(row["passed"]))

    output = {}
    for task_id, runs in sorted(grouped.items()):
        if len(runs) < 3:
            disposition = "needs-more-baseline-runs"
        else:
            rate = sum(runs) / len(runs)
            if rate > 0.70:
                disposition = "reject-saturated"
            elif rate >= 0.30:
                disposition = "primary-candidate"
            elif rate >= 0.10:
                disposition = "hard-set-candidate"
            else:
                disposition = "inspect-for-broken-task"
        output[task_id] = {
            "baseline_runs": len(runs),
            "success_rate": sum(runs) / len(runs) if runs else None,
            "disposition": disposition,
        }
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


def main() -> int:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    pp = sub.add_parser("prepare")
    pp.add_argument("task_id")
    pp.add_argument("dest", type=Path)

    pg = sub.add_parser("grade")
    pg.add_argument("task_id")
    pg.add_argument("dest", type=Path)

    gt = sub.add_parser("gate")
    gt.add_argument("results", type=Path)

    a = p.parse_args()
    if a.cmd == "prepare":
        return prepare(a.task_id, a.dest)
    if a.cmd == "grade":
        return grade(a.task_id, a.dest)
    return gate(a.results)


if __name__ == "__main__":
    raise SystemExit(main())

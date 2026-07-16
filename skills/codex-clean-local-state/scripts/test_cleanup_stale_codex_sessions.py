import json
import os
import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import cleanup_stale_codex_sessions as cleanup
import verify_cleanup as verifier


class CleanupStaleCodexSessionsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / ".codex"
        self.sessions = self.root / "sessions" / "2026" / "07" / "01"
        self.archived = self.root / "archived_sessions"
        self.sessions.mkdir(parents=True)
        self.archived.mkdir(parents=True)
        self.cutoff = datetime(2026, 7, 2, 12, 0, tzinfo=timezone(timedelta(hours=9)))
        self.old_s = self.cutoff.timestamp() - 86400
        self.recent_s = self.cutoff.timestamp() + 86400
        self.old_ms = int(self.old_s * 1000)
        self.recent_ms = int(self.recent_s * 1000)
        self._create_state_db()
        self._create_logs_db()

    def tearDown(self):
        self.temp.cleanup()

    def _create_state_db(self):
        connection = sqlite3.connect(self.root / "state_5.sqlite")
        connection.executescript(
            """
            CREATE TABLE threads (
                id TEXT PRIMARY KEY,
                rollout_path TEXT NOT NULL,
                updated_at_ms INTEGER,
                archived INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE thread_dynamic_tools (
                thread_id TEXT NOT NULL,
                position INTEGER NOT NULL,
                PRIMARY KEY(thread_id, position),
                FOREIGN KEY(thread_id) REFERENCES threads(id) ON DELETE CASCADE
            );
            CREATE TABLE thread_spawn_edges (
                parent_thread_id TEXT NOT NULL,
                child_thread_id TEXT NOT NULL PRIMARY KEY,
                status TEXT NOT NULL
            );
            CREATE TABLE agent_jobs (id TEXT PRIMARY KEY);
            CREATE TABLE agent_job_items (
                job_id TEXT NOT NULL,
                item_id TEXT NOT NULL,
                assigned_thread_id TEXT,
                PRIMARY KEY(job_id, item_id)
            );
            """
        )
        cases = {
            "old-isolated": (self.old_s, self.old_ms),
            "recent": (self.recent_s, self.recent_ms),
            "old-connected": (self.old_s, self.old_ms),
            "old-file-recent-db": (self.old_s, self.recent_ms),
            "recent-file-old-db": (self.recent_s, self.old_ms),
        }
        for session_id, (mtime, db_ms) in cases.items():
            path = self.sessions / f"rollout-{session_id}.jsonl"
            path.write_text("{}\n", encoding="utf-8")
            os.utime(path, (mtime, mtime))
            connection.execute(
                "INSERT INTO threads(id, rollout_path, updated_at_ms) VALUES (?, ?, ?)",
                (session_id, str(path), db_ms),
            )
        connection.execute(
            "INSERT INTO thread_spawn_edges(parent_thread_id, child_thread_id, status) VALUES (?, ?, ?)",
            ("old-connected", "recent", "completed"),
        )
        connection.execute(
            "INSERT INTO thread_dynamic_tools(thread_id, position) VALUES (?, ?)",
            ("old-isolated", 0),
        )
        connection.commit()
        connection.close()
        with (self.root / "session_index.jsonl").open("w", encoding="utf-8") as target:
            for session_id in cases:
                target.write(json.dumps({"id": session_id, "thread_name": session_id, "updated_at": "x"}) + "\n")

    def _create_logs_db(self, *, correct_schema=True):
        connection = sqlite3.connect(self.root / "logs_2.sqlite")
        if correct_schema:
            connection.execute("CREATE TABLE logs (id INTEGER PRIMARY KEY AUTOINCREMENT, body TEXT)")
            connection.execute("INSERT INTO logs(body) VALUES (?)", ("preserve-me",))
        else:
            connection.execute("CREATE TABLE unsupported (value TEXT)")
        connection.commit()
        connection.close()

    def _baseline(self) -> Path:
        baseline = self.root / "audit" / "baseline-plan.json"
        cleanup.write_json(baseline, cleanup.build_plan(self.root, self.cutoff))
        return baseline

    def _execute(self, name="test-cleanup"):
        baseline = self._baseline()
        output = self.root / "backups" / name
        result = cleanup.execute_cleanup(self.root, self.cutoff, output, baseline)
        return output, result

    def test_plan_protects_any_recent_signal_connected_work_and_job_refs(self):
        connection = sqlite3.connect(self.root / "state_5.sqlite")
        connection.execute("INSERT INTO agent_jobs(id) VALUES ('job-1')")
        connection.execute(
            "INSERT INTO agent_job_items(job_id, item_id, assigned_thread_id) VALUES ('job-1', 'item-1', 'old-isolated')"
        )
        connection.commit()
        connection.close()
        plan = cleanup.build_plan(self.root, self.cutoff)
        self.assertEqual([], [item["id"] for item in plan["candidates"]])
        self.assertEqual(0, plan["stats"]["cross_boundary_edges"])

    def test_execute_retains_quarantine_backs_up_both_databases_and_purges_after_verification(self):
        output, result = self._execute()
        source = self.sessions / "rollout-old-isolated.jsonl"
        quarantined = output / "quarantine" / source.relative_to(self.root)
        self.assertFalse(source.exists())
        self.assertTrue(quarantined.exists())
        self.assertTrue((output / "backup" / "state_5.sqlite").exists())
        self.assertTrue((output / "backup" / "logs_2.sqlite").exists())
        self.assertEqual(1, result["quarantined_transcripts"])
        checks = verifier.verify_cleanup(self.root, output)
        self.assertTrue(checks["passed"])
        self.assertEqual("retained", checks["quarantine_mode"])
        purged = cleanup.purge_quarantine(self.root, output)
        self.assertFalse((output / "quarantine").exists())
        self.assertGreater(purged["purged_transcript_bytes"], 0)
        self.assertEqual(0, purged["transcript_bytes_pending_purge"])
        self.assertTrue(verifier.verify_cleanup(self.root, output)["passed"])

    def test_missing_logs_database_fails_before_output_or_session_mutation(self):
        (self.root / "logs_2.sqlite").unlink()
        baseline = self._baseline()
        output = self.root / "backups" / "missing-logs"
        with self.assertRaises(FileNotFoundError):
            cleanup.execute_cleanup(self.root, self.cutoff, output, baseline)
        self.assertFalse(output.exists())
        self.assertTrue((self.sessions / "rollout-old-isolated.jsonl").exists())

    def test_unsupported_logs_schema_fails_before_output_or_session_mutation(self):
        (self.root / "logs_2.sqlite").unlink()
        self._create_logs_db(correct_schema=False)
        baseline = self._baseline()
        output = self.root / "backups" / "bad-logs-schema"
        with self.assertRaisesRegex(RuntimeError, "missing required table"):
            cleanup.execute_cleanup(self.root, self.cutoff, output, baseline)
        self.assertFalse(output.exists())
        self.assertTrue((self.sessions / "rollout-old-isolated.jsonl").exists())

    def test_materially_changed_baseline_candidate_is_rejected_before_mutation(self):
        baseline = self._baseline()
        value = json.loads(baseline.read_text(encoding="utf-8"))
        value["candidates"][0]["size_bytes"] += 1
        cleanup.write_json(baseline, value)
        output = self.root / "backups" / "changed-baseline"
        with self.assertRaisesRegex(RuntimeError, "changed materially"):
            cleanup.execute_cleanup(self.root, self.cutoff, output, baseline)
        self.assertFalse(output.exists())
        self.assertTrue((self.sessions / "rollout-old-isolated.jsonl").exists())

    def test_output_must_be_under_codex_home_backups(self):
        baseline = self._baseline()
        output = self.root.parent / "outside-output"
        with self.assertRaisesRegex(ValueError, "CODEX_HOME/backups"):
            cleanup.execute_cleanup(self.root, self.cutoff, output, baseline)
        self.assertFalse(output.exists())

    def test_index_parse_failure_restores_moved_transcripts_before_db_commit(self):
        baseline = self._baseline()
        with (self.root / "session_index.jsonl").open("a", encoding="utf-8") as target:
            target.write("not-json\n")
        output = self.root / "backups" / "bad-index"
        with self.assertRaises(json.JSONDecodeError):
            cleanup.execute_cleanup(self.root, self.cutoff, output, baseline)
        self.assertTrue((self.sessions / "rollout-old-isolated.jsonl").exists())
        connection = sqlite3.connect(self.root / "state_5.sqlite")
        ids = {row[0] for row in connection.execute("SELECT id FROM threads")}
        connection.close()
        self.assertIn("old-isolated", ids)

    def test_purge_refuses_unexpected_quarantine_file(self):
        output, _ = self._execute("unexpected-quarantine")
        self.assertTrue(verifier.verify_cleanup(self.root, output)["passed"])
        extra = output / "quarantine" / "unexpected.txt"
        extra.parent.mkdir(parents=True, exist_ok=True)
        extra.write_text("unexpected", encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "exactly match"):
            cleanup.purge_quarantine(self.root, output)
        self.assertTrue(extra.exists())

    def test_verification_resolves_protected_relative_rollout_paths_from_codex_home(self):
        recent_path = self.sessions / "rollout-recent.jsonl"
        connection = sqlite3.connect(self.root / "state_5.sqlite")
        connection.execute(
            "UPDATE threads SET rollout_path = ? WHERE id = 'recent'",
            (str(recent_path.relative_to(self.root)),),
        )
        connection.commit()
        connection.close()
        output, _ = self._execute("relative-protected-path")
        checks = verifier.verify_cleanup(self.root, output)
        self.assertTrue(checks["passed"])
        self.assertEqual(0, checks["missing_protected_files"])


if __name__ == "__main__":
    unittest.main()

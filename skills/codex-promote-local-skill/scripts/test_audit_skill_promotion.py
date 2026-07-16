import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import audit_skill_promotion as audit


class AuditSkillPromotionTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.repo = self.base / "codex-config"
        self.codex_home = self.base / ".codex"
        self.old_skill = self.codex_home / "skills" / "local-helper"
        self.skill_name = "codex-local-helper"
        self.repo_skill = self.repo / "skills" / self.skill_name
        self.installed_skill = self.codex_home / "skills" / self.skill_name
        self.old_skill.mkdir(parents=True)
        (self.old_skill / "SKILL.md").write_text("---\nname: local-helper\n---\nold\n", encoding="utf-8")
        (self.old_skill / "scripts").mkdir()
        (self.old_skill / "scripts" / "helper.py").write_text("print('old')\n", encoding="utf-8")
        (self.old_skill / "scripts" / "__pycache__").mkdir()
        (self.old_skill / "scripts" / "__pycache__" / "helper.pyc").write_bytes(b"runtime-noise")

        self.repo_skill.mkdir(parents=True)
        (self.repo_skill / "SKILL.md").write_text(
            "---\nname: codex-local-helper\ndescription: Test fixture.\n---\n# Fixture\n",
            encoding="utf-8",
        )
        (self.repo_skill / "agents").mkdir()
        (self.repo_skill / "agents" / "openai.yaml").write_text(
            'interface:\n  display_name: "Fixture"\n',
            encoding="utf-8",
        )
        self._git("init", "--quiet")
        self._git("config", "user.name", "Promotion Test")
        self._git("config", "user.email", "promotion-test@example.invalid")
        self._git("add", ".")
        self._git("commit", "--quiet", "-m", "add promoted skill")
        self.head = self._git("rev-parse", "HEAD").strip()

        shutil.copytree(self.repo_skill, self.installed_skill)
        tracked = [
            f"skills/{self.skill_name}/SKILL.md",
            f"skills/{self.skill_name}/agents/openai.yaml",
        ]
        (self.codex_home / ".codex-config-managed-files").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "source_commit": self.head,
                    "managed_files": tracked,
                }
            ),
            encoding="utf-8",
        )
        self.snapshot_path = self.base / "old-skill-snapshot.json"
        audit.write_snapshot(self.old_skill, self.snapshot_path)

    def tearDown(self):
        self.temp.cleanup()

    def _git(self, *args):
        result = subprocess.run(
            ["git", "-C", str(self.repo), *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout

    def test_snapshot_ignores_runtime_noise(self):
        snapshot = audit.snapshot_tree(self.old_skill)
        self.assertEqual(["SKILL.md", "scripts/helper.py"], sorted(snapshot["files"]))

    def test_snapshot_flags_sensitive_names_without_exposing_contents(self):
        (self.old_skill / ".env").write_text("DO_NOT_REPORT=this-value\n", encoding="utf-8")
        snapshot = audit.snapshot_tree(self.old_skill)
        self.assertEqual([".env"], snapshot["sensitive_paths"])
        serialized = json.dumps(snapshot)
        self.assertNotIn("DO_NOT_REPORT", serialized)
        self.assertNotIn("this-value", serialized)

    def test_verify_promotion_accepts_committed_exact_install_and_unchanged_old_skill(self):
        result = audit.verify_promotion(
            repo_root=self.repo,
            skill_name=self.skill_name,
            codex_home=self.codex_home,
            old_skill_path=self.old_skill,
            source_snapshot_path=self.snapshot_path,
        )
        self.assertTrue(result["ready_for_old_skill_removal"])
        self.assertEqual(self.head, result["source_commit"])
        self.assertEqual(2, result["managed_skill_files"])

    def test_verify_installed_skill_does_not_require_old_skill(self):
        shutil.rmtree(self.old_skill)
        result = audit.verify_installed_skill(
            repo_root=self.repo,
            skill_name=self.skill_name,
            codex_home=self.codex_home,
        )
        self.assertTrue(result["installed_skill_verified"])
        self.assertEqual(self.head, result["source_commit"])

    def test_verify_promotion_rejects_installed_mismatch(self):
        (self.installed_skill / "SKILL.md").write_text("changed\n", encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "installed skill tree"):
            audit.verify_promotion(
                repo_root=self.repo,
                skill_name=self.skill_name,
                codex_home=self.codex_home,
                old_skill_path=self.old_skill,
                source_snapshot_path=self.snapshot_path,
            )

    def test_verify_promotion_rejects_old_skill_changed_after_snapshot(self):
        (self.old_skill / "new-file.txt").write_text("new\n", encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "old skill changed"):
            audit.verify_promotion(
                repo_root=self.repo,
                skill_name=self.skill_name,
                codex_home=self.codex_home,
                old_skill_path=self.old_skill,
                source_snapshot_path=self.snapshot_path,
            )

    def test_verify_promotion_rejects_sensitive_old_skill_files(self):
        (self.old_skill / "credentials.json").write_text("private\n", encoding="utf-8")
        audit.write_snapshot(self.old_skill, self.snapshot_path)
        with self.assertRaisesRegex(RuntimeError, "sensitive-looking"):
            audit.verify_promotion(
                repo_root=self.repo,
                skill_name=self.skill_name,
                codex_home=self.codex_home,
                old_skill_path=self.old_skill,
                source_snapshot_path=self.snapshot_path,
            )

    def test_verify_promotion_rejects_untracked_repo_skill_file(self):
        (self.repo_skill / "untracked.txt").write_text("untracked\n", encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "fully tracked and committed"):
            audit.verify_promotion(
                repo_root=self.repo,
                skill_name=self.skill_name,
                codex_home=self.codex_home,
                old_skill_path=self.old_skill,
                source_snapshot_path=self.snapshot_path,
            )


if __name__ == "__main__":
    unittest.main()

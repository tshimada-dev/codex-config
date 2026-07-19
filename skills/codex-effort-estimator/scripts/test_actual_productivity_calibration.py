import csv
import hashlib
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[3]
REFERENCES = ROOT / "skills" / "codex-effort-estimator" / "references"
JA_REFERENCES = (
    ROOT / "docs" / "ja" / "skills" / "codex-effort-estimator" / "references"
)
ACTUALS = REFERENCES / "actual-productivity-calibration.csv"
LEDGER = REFERENCES / "calibration-ledger-template.csv"
CALIBRATION = REFERENCES / "actual-productivity-calibration.md"
UCP_PASS = REFERENCES / "use-case-points-pass.md"
ANALOGY_PASS = REFERENCES / "analogy-calibration-pass.md"
WORKFLOW = ROOT / ".github" / "workflows" / "validate.yml"
EVALUATION = ROOT / "docs" / "evaluations" / "estimator-actual-calibration.md"
JA_EVALUATION = (
    ROOT / "docs" / "ja" / "evaluations" / "estimator-actual-calibration.md"
)


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


class ActualProductivityCalibrationTest(unittest.TestCase):
    def test_public_actual_table_is_measured_and_recalculable(self):
        with ACTUALS.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))

        self.assertEqual(
            [row["anchor_id"] for row in rows],
            [
                "anda2005-company-a",
                "anda2005-company-b",
                "anda2005-company-c",
                "anda2005-company-d",
            ],
        )
        expected_actuals = [587.0, 943.0, 431.0, 829.0]
        for row, actual in zip(rows, expected_actuals):
            self.assertEqual(float(row["published_unadjusted_points"]), 57.0)
            self.assertEqual(float(row["published_adjusted_ucp"]), 20.619)
            self.assertEqual(float(row["actual_effort_hours"]), actual)
            self.assertAlmostEqual(
                float(row["hours_per_unadjusted_point"]), actual / 57.0, places=3
            )
            self.assertAlmostEqual(
                float(row["hours_per_adjusted_ucp"]), actual / 20.619, places=3
            )
            self.assertAlmostEqual(
                float(row["person_days_per_adjusted_ucp"]),
                actual / 20.619 / 8.0,
                places=3,
            )
            self.assertEqual(row["source_doi"], "10.1109/ISESE.2005.1541849")

    def test_ucp_pass_prefers_compatible_measured_coefficients(self):
        calibration = CALIBRATION.read_text(encoding="utf-8")
        ucp_pass = UCP_PASS.read_text(encoding="utf-8")
        self.assertIn("local actual > compatible measured benchmark > heuristic", calibration)
        self.assertIn("2.613-5.717 person-days per adjusted UCP", calibration)
        self.assertIn("4.229 person-days per adjusted UCP", calibration)
        self.assertIn("Do not mix the 57-point denominator", calibration)
        self.assertIn("Figure 2 on pages 412-413", calibration)
        self.assertIn("57 * 7.5 = 430 hours", calibration)
        self.assertIn("Do not treat the two files as identical", calibration)
        self.assertIn("actual-productivity-calibration.md", ucp_pass)
        self.assertIn("local actual > compatible measured benchmark > heuristic", ucp_pass)
        self.assertIn("person-days per adjusted UCP", ucp_pass)

    def test_post_delivery_ledger_workflow_is_operational(self):
        with LEDGER.open(encoding="utf-8", newline="") as handle:
            headers = next(csv.reader(handle))
        self.assertEqual(
            headers,
            [
                "recorded_at",
                "project_alias",
                "scope_fingerprint",
                "method",
                "size_basis",
                "size_value",
                "coefficient_source",
                "estimate_low_pd",
                "estimate_center_pd",
                "estimate_high_pd",
                "actual_effort_pd",
                "actual_scope_match",
                "actual_productivity_pd_per_size",
                "signed_relative_error",
                "absolute_relative_error",
                "notes",
            ],
        )
        analogy = ANALOGY_PASS.read_text(encoding="utf-8")
        self.assertIn("Post-delivery calibration ledger", analogy)
        self.assertIn("calibration-ledger-template.csv", analogy)
        self.assertIn("(estimate_center_pd - actual_effort_pd) / actual_effort_pd", analogy)
        self.assertIn("actual_effort_pd / size_value", analogy)

    def test_japanese_references_track_exact_canonical_blobs(self):
        for canonical_name in (
            "actual-productivity-calibration.md",
            "use-case-points-pass.md",
            "analogy-calibration-pass.md",
        ):
            canonical = REFERENCES / canonical_name
            japanese = JA_REFERENCES / canonical_name
            translated = japanese.read_text(encoding="utf-8")
            self.assertIn(f"source: {canonical.relative_to(ROOT).as_posix()}", translated)
            self.assertIn(f"source_blob: {git_blob_sha(canonical)}", translated)
            self.assertIn("canonical: false", translated)

    def test_ci_runs_calibration_regression(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("Validate estimator actual productivity calibration", workflow)
        self.assertIn("python -m unittest -v test_actual_productivity_calibration.py", workflow)

    def test_evaluation_maps_acceptance_and_translation(self):
        evaluation = EVALUATION.read_text(encoding="utf-8")
        for acceptance_id in ("AC-3-1", "AC-3-2", "AC-3-3"):
            self.assertIn(acceptance_id, evaluation)
        self.assertIn("Synthetic coefficients were rejected", evaluation)
        self.assertIn("four-company measured range", evaluation)
        self.assertIn("Figure 2 on pages 412-413", evaluation)
        self.assertIn("contains neither 20.619 nor 413", evaluation)
        translated = JA_EVALUATION.read_text(encoding="utf-8")
        self.assertIn("source: docs/evaluations/estimator-actual-calibration.md", translated)
        self.assertIn(f"source_blob: {git_blob_sha(EVALUATION)}", translated)


if __name__ == "__main__":
    unittest.main()

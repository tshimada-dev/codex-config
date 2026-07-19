import hashlib
import json
import unittest
from pathlib import Path

import synthesize_method_clusters as synthesis


ROOT = Path(__file__).parents[3]
FIXTURE = (
    ROOT
    / "docs"
    / "evaluations"
    / "fixtures"
    / "estimator-false-convergence"
    / "anda-run2-parent-input.json"
)
PREREGISTRATION = ROOT / "docs" / "evaluations" / "estimator-false-convergence-preregistration.md"
WORKFLOW = ROOT / ".github" / "workflows" / "validate.yml"
EVALUATION = ROOT / "docs" / "evaluations" / "estimator-false-convergence.md"
JA_EVALUATION = ROOT / "docs" / "ja" / "evaluations" / "estimator-false-convergence.md"


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


class MethodClusterSynthesisTest(unittest.TestCase):
    def test_anda_run2_replay_discounts_cluster_and_stops_invented_count(self):
        data = json.loads(FIXTURE.read_text(encoding="utf-8"))

        result = synthesis.synthesize(data)

        clusters = {row["cluster"]: row for row in result["cluster_votes"]}
        self.assertEqual(748.0, clusters["implementation-light"]["representative_hours"])
        self.assertEqual(864.0, clusters["capacity"]["representative_hours"])
        self.assertEqual(0, clusters["use-case-lifecycle"]["effective_vote"])
        self.assertEqual("STOP_UNTRACED_COUNT", result["count_audits"][0]["status"])
        self.assertEqual(806.0, result["planning_center_hours"])
        self.assertEqual("supported", result["convergence_confidence"])
        self.assertTrue(all(row["effective_vote"] == 1 for row in result["cluster_votes"] if row["eligible"]))

    def test_method_count_does_not_create_extra_cluster_votes(self):
        data = {
            "methods": [
                self.method("a1", "shared-a", 100),
                self.method("a2", "shared-a", 120),
                self.method("a3", "shared-a", 140),
                self.method("b1", "independent-b", 400),
            ],
            "count_audits": [],
        }

        result = synthesis.synthesize(data)

        self.assertEqual(260.0, result["planning_center_hours"])
        self.assertEqual(2, sum(row["effective_vote"] for row in result["cluster_votes"]))

    def test_rejected_method_requires_evidence_specific_reason(self):
        data = {
            "methods": [
                {**self.method("a", "a", 100), "status": "rejected"},
                self.method("b", "b", 200),
            ],
            "count_audits": [],
        }

        with self.assertRaisesRegex(ValueError, "rejection_reason"):
            synthesis.synthesize(data)

        generic = self.method("a", "a", 100)
        generic.update(
            status="rejected",
            rejection_reason="best matches target deliverable",
            rejection_dimension="scope",
            evidence_locator="Requirements section 4",
        )
        with self.assertRaisesRegex(ValueError, "evidence-specific rejection_reason"):
            synthesis.synthesize({"methods": [generic, self.method("b", "b", 200)], "count_audits": []})

        missing_locator = self.method("a", "a", 100)
        missing_locator.update(
            status="rejected",
            rejection_reason="Omits production cutover tasks",
            rejection_dimension="scope",
        )
        with self.assertRaisesRegex(ValueError, "evidence_locator"):
            synthesis.synthesize(
                {"methods": [missing_locator, self.method("b", "b", 200)], "count_audits": []}
            )

    def test_evidence_rejected_cluster_remains_in_decision_ledger(self):
        rejected = self.method("lower-anchor", "independent-lower", 180)
        rejected.update(
            status="rejected",
            rejection_reason="Counts implementation only and omits production cutover",
            rejection_dimension="lifecycle",
            evidence_locator="Requirements section 4.3, cutover checklist items 1-4",
        )
        adopted = self.method("capacity", "capacity", 400)

        result = synthesis.synthesize(
            {"methods": [rejected, adopted], "count_audits": []}
        )

        ledger = next(
            row for row in result["cluster_votes"] if row["cluster"] == "independent-lower"
        )
        self.assertIsNone(ledger["representative_hours"])
        self.assertEqual(0, ledger["effective_vote"])
        self.assertEqual("rejected_lifecycle_mismatch", ledger["anchor_disposition"])
        self.assertEqual("excluded_from_center_as_evidence_rejected", ledger["decision_impact"])
        self.assertEqual("Requirements section 4.3, cutover checklist items 1-4", ledger["rejections"][0]["evidence_locator"])
        self.assertEqual(400.0, result["planning_center_hours"])

    def test_traced_count_inflation_is_sensitivity_only(self):
        data = {
            "methods": [
                self.method("ucp", "use-case", 500, count_basis="use-case transaction count"),
                self.method("fp", "function", 300),
            ],
            "count_audits": [
                {
                    "metric": "UUCP",
                    "explicit_value": 100,
                    "derived_value": 130,
                    "untraced_inferred_value": 0,
                }
            ],
        }

        result = synthesis.synthesize(data)

        self.assertEqual("SENSITIVITY_ONLY_COUNT_INFLATION", result["count_audits"][0]["status"])
        self.assertFalse(next(row for row in result["cluster_votes"] if row["cluster"] == "use-case")["eligible"])

    def test_shared_basis_cannot_be_split_into_extra_cluster_votes(self):
        first = self.method("first", "declared-a", 100, count_basis="same use-case count")
        second = self.method("second", "declared-b", 140, count_basis="same use-case count")
        independent = self.method("independent", "declared-c", 300, count_basis="capacity envelope")
        independent["productivity_basis"] = "capacity"
        independent["lifecycle_basis"] = "delivery window"
        independent["risk_basis"] = "schedule"

        result = synthesis.synthesize(
            {"methods": [first, second, independent], "count_audits": []}
        )

        merged = next(row for row in result["cluster_votes"] if set(row["declared_clusters"]) == {"declared-a", "declared-b"})
        self.assertEqual(["first", "second"], merged["methods"])
        self.assertEqual(1, merged["effective_vote"])
        self.assertEqual(2, sum(row["effective_vote"] for row in result["cluster_votes"]))

    def test_preregistration_and_input_remain_frozen(self):
        self.assertEqual(
            "2b29b73cd15e0bd450f9747002fa2e9026040c700f6707347efcb47dededdbdb",
            hashlib.sha256(PREREGISTRATION.read_bytes()).hexdigest(),
        )
        self.assertEqual(
            "47e57b01608a37bc154f653f9b19f0733b548c290193f329a1db01339d7365a2",
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
        )

    def test_japanese_references_track_exact_canonical_blobs(self):
        pairs = [
            (ROOT / "skills" / "codex-effort-estimator" / "SKILL.md", ROOT / "docs" / "ja" / "skills" / "codex-effort-estimator.md"),
            *[
                (
                    ROOT / "skills" / "codex-effort-estimator" / "references" / name,
                    ROOT / "docs" / "ja" / "skills" / "codex-effort-estimator" / "references" / name,
                )
                for name in (
                    "methods.md",
                    "sizing-pass.md",
                    "use-case-points-pass.md",
                    "function-point-pass.md",
                    "output-template.md",
                    "spreadsheet-output.md",
                    "workbook-format.md",
                )
            ],
        ]
        for canonical, japanese in pairs:
            translated = japanese.read_text(encoding="utf-8")
            self.assertIn(f"source_blob: {git_blob_sha(canonical)}", translated)
            self.assertIn("canonical: false", translated)

    def test_ci_runs_cluster_regression(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("Validate estimator cluster synthesis", workflow)
        self.assertIn("python -m unittest -v test_synthesize_method_clusters.py", workflow)

    def test_evaluation_maps_acceptance_and_translation(self):
        evaluation = EVALUATION.read_text(encoding="utf-8")
        for acceptance_id in ("AC-18-1", "AC-18-2", "AC-18-3", "AC-18-4", "AC-18-5"):
            self.assertIn(acceptance_id, evaluation)
        self.assertIn("synthesis-only replay", evaluation)
        self.assertIn("does not prove universal accuracy", evaluation)
        translated = JA_EVALUATION.read_text(encoding="utf-8")
        self.assertIn("source: docs/evaluations/estimator-false-convergence.md", translated)
        self.assertIn(f"source_blob: {git_blob_sha(EVALUATION)}", translated)

    @staticmethod
    def method(name, cluster, base, count_basis="driver equation"):
        return {
            "method": name,
            "cluster": cluster,
            "base_hours": base,
            "count_basis": count_basis,
            "productivity_basis": "measured or stated coefficient",
            "lifecycle_basis": "stated lifecycle",
            "risk_basis": "method-local",
            "status": "plausible",
        }


if __name__ == "__main__":
    unittest.main()

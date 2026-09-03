from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


SCRIPT_PATH = Path(__file__).with_name("render_debate_chat.py")


def load_renderer():
    spec = importlib.util.spec_from_file_location("render_debate_chat", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load renderer from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sample_debate() -> dict:
    return {
        "lang": "ja",
        "title": "AI governance debate",
        "proposition": "Should deployment require a public safety case?",
        "proposition_type": "FORECAST",
        "decision_rule": {
            "target": "A qualifying safety-case requirement is enacted.",
            "horizon": "By 2030-12-31",
            "yes_condition": "Resolved probability is greater than 0.50.",
            "no_condition": "Resolved probability is at most 0.50.",
            "resolution_source": "Published statute and regulator guidance",
            "threshold": 0.50,
        },
        "debate_progress": {
            "completed_phases": ["OPENING", "CROSS_EXAM", "RESPONSE", "UPDATE"],
            "completed_crucial_cycles": 1,
        },
        "status": "DEADLOCK",
        "evidence_mode": "shared-evidence",
        "camps": [
            {"id": "precaution", "name": "Precautionary camp"},
            {"id": "innovation", "name": "Innovation camp"},
            {"id": "methodologist", "name": "Methodologist", "role": "auditor"},
        ],
        "evidence_cards": [
            {
                "id": "F2",
                "title": "Guarded tutor experiment",
                "source": "Example University",
                "source_url": "https://example.com/study",
                "study_type": "RCT",
                "population": "High-school mathematics students",
                "conditions": "Base GPT / Tutor / Control",
                "main_finding": "Guardrails changed unaided outcomes <script>alert(2)</script>",
                "limitations": ["One subject and age group"],
                "causal_strength": "high",
                "generalizability": "low",
            }
        ],
        "claim_ledger": [
            {
                "id": "C1",
                "text": "Guardrails can change learning outcomes.",
                "type": "inference",
                "status": "agreed",
                "evidence": ["F2"],
                "falsifier": "A comparable trial finds no outcome difference.",
            },
            {
                "id": "C2",
                "text": "The result generalizes to all work.",
                "type": "prediction",
                "status": "disputed",
                "evidence": [],
            },
        ],
        "belief_updates": [
            {
                "camp": "precaution",
                "phase": "UPDATE",
                "before": 0.78,
                "after": 0.66,
                "reason": "Population-level generalization was not directly measured.",
            }
        ],
        "forecast_records": [
            {"camp": "precaution", "checkpoint": "PRIOR", "probability": 0.72, "lower": 0.55, "upper": 0.84, "rationale": "Initial base-rate judgment."},
            {"camp": "precaution", "checkpoint": "AFTER_CROSS_EXAM", "probability": 0.66, "lower": 0.48, "upper": 0.80, "rationale": "Generalization was challenged."},
            {"camp": "precaution", "checkpoint": "AFTER_CRUCIAL_DISPUTE", "cycle": 1, "probability": 0.63, "lower": 0.45, "upper": 0.78, "rationale": "The decisive claim remains unresolved."},
            {"camp": "precaution", "checkpoint": "FINAL", "probability": 0.61, "lower": 0.43, "upper": 0.77, "rationale": "Final private forecast."},
            {"camp": "innovation", "checkpoint": "PRIOR", "probability": 0.38, "lower": 0.22, "upper": 0.56, "rationale": "Initial base-rate judgment."},
            {"camp": "innovation", "checkpoint": "AFTER_CROSS_EXAM", "probability": 0.43, "lower": 0.27, "upper": 0.61, "rationale": "The positive case was stronger than expected."},
            {"camp": "innovation", "checkpoint": "AFTER_CRUCIAL_DISPUTE", "cycle": 1, "probability": 0.46, "lower": 0.29, "upper": 0.64, "rationale": "Implementation uncertainty remains."},
            {"camp": "innovation", "checkpoint": "FINAL", "probability": 0.47, "lower": 0.30, "upper": 0.65, "rationale": "Final private forecast."},
        ],
        "evidence_links": [
            {
                "claim_id": "C1",
                "evidence_id": "F2",
                "supports": "Guardrails can affect the measured learning outcome.",
                "does_not_establish": "The result generalizes to all work.",
                "directness": "high",
                "independence": "medium",
                "causal_strength": "high",
                "generalizability": "low",
                "temporal_relevance": "medium",
            }
        ],
        "needed_evidence": [
            {
                "id": "N1",
                "observation": "A multi-domain replication with deployment outcomes.",
                "resolves_claims": ["C1", "C2"],
                "expected_update": "A null result would weaken C1; replication would strengthen it.",
                "collection": "Prospective multi-site study",
            }
        ],
        "messages": [
            {
                "kind": "system",
                "speaker": "Supervisor",
                "text": "Debate started",
                "timestamp": "10:00",
            },
            {
                "kind": "argument",
                "camp": "precaution",
                "phase": "OPENING",
                "text": "Require evidence before release <script>alert(1)</script>",
                "timestamp": "10:01",
            },
            {
                "kind": "argument",
                "camp": "innovation",
                "round": 1,
                "text": "Use staged deployment and monitoring.",
                "timestamp": "10:02",
            },
            {
                "kind": "intervention",
                "speaker": "Supervisor",
                "text": "A claim was corrected.",
                "timestamp": "10:03",
            },
        ],
        "summary": {
            "decision": "No candidate received unanimous acceptance.",
            "agreed_points": ["Monitoring is necessary."],
            "unresolved_objections": ["Who bears the burden of proof?"],
        },
    }


class DebateChatRendererTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.renderer = load_renderer()

    def test_renders_accessible_self_contained_group_chat(self) -> None:
        html = self.renderer.render_document(sample_debate())

        self.assertIn('<html lang="ja">', html)
        self.assertIn("グループ討論", html)
        self.assertIn("共通点", html)
        self.assertIn('class="pill status deadlock"', html)
        self.assertIn(".status.deadlock,.status.true_deadlock{background:#ffe7a3", html)
        self.assertIn('<meta name="viewport" content="width=device-width, initial-scale=1">', html)
        self.assertIn('aria-label="Debate transcript"', html)
        self.assertIn('class="message argument camp-0"', html)
        self.assertIn('data-camp="precaution"', html)
        self.assertIn('data-filter="precaution"', html)
        self.assertIn('class="message intervention"', html)
        self.assertIn('@media (max-width: 720px)', html)
        self.assertIn('.layout>*{min-width:0}', html)
        self.assertIn("No candidate received unanimous acceptance.", html)
        self.assertIn("Monitoring is necessary.", html)
        self.assertIn("Evidence cards", html)
        self.assertIn("Claim Ledger", html)
        self.assertIn("Key belief updates", html)
        self.assertIn("Decision rule", html)
        self.assertIn("方法論監査（投票権なし）", html)
        self.assertIn("Forecast trajectory", html)
        self.assertIn("校正済みでも独立推定でもありません", html)
        self.assertIn("What would resolve this?", html)
        self.assertIn("Evidence → Claim links", html)
        self.assertIn("A comparable trial finds no outcome difference.", html)
        self.assertIn("AFTER CROSS EXAM", html)
        self.assertIn("61%", html)
        self.assertIn("47%", html)
        self.assertIn("A multi-domain replication", html)
        self.assertIn("Guarded tutor experiment", html)
        self.assertIn("因果推論強度", html)
        self.assertIn("一般化可能性", html)
        self.assertIn("C1", html)
        self.assertIn("合意", html)
        self.assertIn("78%", html)
        self.assertIn("66%", html)
        self.assertNotIn('<span class="message-meta">フェーズ OPENING', html)
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)
        self.assertNotIn("<script>alert(2)</script>", html)
        self.assertIn("&lt;script&gt;alert(2)&lt;/script&gt;", html)

    def test_renders_controller_audit_metadata_without_candidate_provenance(self) -> None:
        debate = sample_debate()
        debate["status"] = "TRUE_DEADLOCK"
        debate["controller"] = {
            "schema_version": 1,
            "debate_id": "debate-50",
            "phase": "COMMON_CORE_CONFIRMATION",
            "cycle": 7,
            "accepted_sequence": 2,
            "next_actor": None,
            "next_action": None,
            "terminal_status": "TRUE_DEADLOCK",
            "emergency_safety": {"event_limit": 10000, "time_limit_seconds": None},
            "events": [
                {
                    "event_id": "evt-1",
                    "sequence": 1,
                    "phase": "CRUCIAL_DISPUTE",
                    "cycle": 7,
                    "participant": "precaution",
                    "observed_at": "2026-09-03T00:00:00Z",
                    "committed_at": "2026-09-03T00:00:00Z",
                    "action_type": "TURN",
                    "accepted": True,
                    "rejection_reason": None,
                    "payload": {},
                },
                {
                    "event_id": "candidate-1",
                    "sequence": 2,
                    "phase": "RESOLUTION_CANDIDATE",
                    "cycle": 7,
                    "participant": "anonymous",
                    "observed_at": "2026-09-03T00:01:00Z",
                    "committed_at": "2026-09-03T00:01:00Z",
                    "action_type": "RESOLUTION_CANDIDATE",
                    "accepted": True,
                    "rejection_reason": None,
                    "payload": {"outcome": "DEADLOCK", "decision": "unresolved"},
                },
                {
                    "event_id": "candidate-1",
                    "sequence": None,
                    "phase": "RESOLUTION_CANDIDATE",
                    "cycle": 7,
                    "participant": "anonymous",
                    "observed_at": "2026-09-03T00:01:01Z",
                    "committed_at": None,
                    "action_type": "RESOLUTION_CANDIDATE",
                    "accepted": False,
                    "rejection_reason": "duplicate_delivery",
                    "payload": {"outcome": "DEADLOCK", "decision": "unresolved"},
                },
            ],
        }

        html = self.renderer.render_document(debate)

        self.assertIn("Protocol audit", html)
        self.assertIn("debate-50", html)
        self.assertIn("candidate-1", html)
        self.assertIn("duplicate_delivery", html)
        self.assertNotIn("submitted_by", html)

    def test_rejects_invalid_or_identifying_controller_audit_metadata(self) -> None:
        identifying = sample_debate()
        identifying["status"] = "INCOMPLETE"
        identifying["controller"] = {
            "schema_version": 1,
            "debate_id": "debate-50",
            "phase": "RESOLUTION_CANDIDATE",
            "cycle": 1,
            "accepted_sequence": 1,
            "terminal_status": "INCOMPLETE",
            "events": [
                {
                    "event_id": "candidate-1",
                    "sequence": 1,
                    "phase": "RESOLUTION_CANDIDATE",
                    "cycle": 1,
                    "participant": "precaution",
                    "observed_at": "2026-09-03T00:00:00Z",
                    "committed_at": "2026-09-03T00:00:00Z",
                    "action_type": "RESOLUTION_CANDIDATE",
                    "accepted": True,
                    "rejection_reason": None,
                    "payload": {},
                }
            ],
        }
        with self.assertRaisesRegex(ValueError, "candidate provenance"):
            self.renderer.render_document(identifying)

        payload_identifying = sample_debate()
        payload_identifying["status"] = "INCOMPLETE"
        payload_identifying["controller"] = copy.deepcopy(identifying["controller"])
        payload_identifying["controller"]["events"][0]["participant"] = "anonymous"
        payload_identifying["controller"]["events"][0]["payload"] = {
            "outcome": "DEADLOCK",
            "agreed_points": [{"submitted_by": "precaution"}],
        }
        with self.assertRaisesRegex(ValueError, "candidate provenance"):
            self.renderer.render_document(payload_identifying)

        sequence_gap = sample_debate()
        sequence_gap["status"] = "INCOMPLETE"
        sequence_gap["controller"] = {
            "schema_version": 1,
            "debate_id": "debate-50",
            "phase": "OPENING",
            "cycle": 0,
            "accepted_sequence": 2,
            "terminal_status": "INCOMPLETE",
            "events": [
                {
                    "event_id": "evt-2",
                    "sequence": 2,
                    "phase": "OPENING",
                    "cycle": 0,
                    "participant": "precaution",
                    "observed_at": "2026-09-03T00:00:00Z",
                    "committed_at": "2026-09-03T00:00:00Z",
                    "action_type": "TURN",
                    "accepted": True,
                    "rejection_reason": None,
                    "payload": {},
                }
            ],
        }
        with self.assertRaisesRegex(ValueError, "contiguous"):
            self.renderer.render_document(sequence_gap)

        missing_terminal = sample_debate()
        missing_terminal["controller"] = copy.deepcopy(identifying["controller"])
        missing_terminal["controller"]["terminal_status"] = None
        with self.assertRaisesRegex(ValueError, "terminal_status is required"):
            self.renderer.render_document(missing_terminal)

    def test_keeps_legacy_documents_compatible(self) -> None:
        debate = sample_debate()
        debate["claim_ledger"][0].pop("falsifier")
        debate.pop("evidence_cards")
        debate.pop("claim_ledger")
        debate.pop("belief_updates")
        debate.pop("proposition_type")
        debate.pop("decision_rule")
        debate.pop("debate_progress")
        debate.pop("forecast_records")
        debate.pop("evidence_links")
        debate.pop("needed_evidence")
        debate["messages"][1].pop("phase")

        html = self.renderer.render_document(debate)

        self.assertIn("AI governance debate", html)
        self.assertNotIn('<section class="evidence-panel"', html)
        self.assertNotIn('<section class="summary-section belief-section"', html)

    def test_renders_state_driven_protocol_as_readable_japanese_and_keeps_verbatim(self) -> None:
        debate = sample_debate()
        debate["messages"][1]["text"] = """PRECAUTION OPENING
POSITIVE_CASE: 公開前に安全性の説明を求める。
BURDEN_OF_PROOF: 説明が実際の危険を減らすことを示す。
KEY_EVIDENCE: F2
UNCERTAINTY: 同じ成果をより軽い手段で得られるなら弱まる。
LEDGER_ACTIONS:
- ADD: 説明責任は危険を減らす。 | TYPE: inference | EVIDENCE: F2 | FALSIFIER: 比較試験で差がない。"""

        html = self.renderer.render_document(debate)

        self.assertIn("主張", html)
        self.assertIn("この立場が示すべきこと", html)
        self.assertIn("この主張が弱まる条件", html)
        self.assertIn("論点台帳の更新を見る", html)
        self.assertIn("プロトコル原文を表示", html)
        self.assertIn("PRECAUTION OPENING<br>POSITIVE_CASE:", html)
        self.assertIn("- ADD: 説明責任は危険を減らす。", html)
        self.assertNotIn('<span class="message-meta">フェーズ OPENING', html)

    def test_renders_anonymous_resolution_candidate_readably_and_keeps_verbatim(self) -> None:
        debate = sample_debate()
        debate["messages"].append(
            {
                "kind": "resolution",
                "resolution_stage": "candidate",
                "speaker": "Candidate A",
                "text": """RESOLUTION_CANDIDATE
OUTCOME: WINNER
WINNER: PRECAUTION
DECISION: 公開前の説明を求める。
AGREED_POINTS:
- 監視は必要である。
RESERVATIONS:
- 小規模導入は許容できる。
CONFLICTS:
- 負担の大きさは未解決である。
RATIONALE:
- 凍結した基準を満たす。""",
            }
        )

        html = self.renderer.render_document(debate)

        self.assertIn("結論", html)
        self.assertIn("合意できた点", html)
        self.assertIn("留保", html)
        self.assertIn("未解決の対立", html)
        self.assertIn("判断理由", html)
        self.assertIn("RESOLUTION_CANDIDATE<br>OUTCOME: WINNER", html)
        self.assertIn("プロトコル原文を表示", html)

    def test_renders_common_core_and_confirmation_in_natural_language(self) -> None:
        debate = sample_debate()
        debate["messages"].extend(
            [
                {
                    "kind": "resolution",
                    "resolution_stage": "confirmation",
                    "speaker": "Common-core check",
                    "text": """COMMON_CORE_CHECK
PROPOSED_WINNER:
- EQUALITY
PROPOSED_COMMON_CORE:
- 最終票は等価に保つ。
RESERVATIONS:
- 限定的な地域同意は残る。""",
                },
                {
                    "kind": "resolution",
                    "resolution_stage": "confirmation",
                    "speaker": "Confirmation A",
                    "text": "ACCEPT_WINNER EQUALITY",
                },
            ]
        )

        html = self.renderer.render_document(debate)

        self.assertIn("勝者案", html)
        self.assertIn("合意できる共通部分の案", html)
        self.assertIn("勝者案を承認", html)
        self.assertIn("ACCEPT_WINNER EQUALITY", html)

    def test_validation_preserves_message_text_byte_for_byte(self) -> None:
        debate = sample_debate()
        debate["messages"][1]["text"] = "  POSITION: YES\n\nRATIONALE: exact spacing  "

        normalized = self.renderer.validate_document(debate)

        self.assertEqual(debate["messages"][1]["text"], normalized["messages"][1]["text"])

    def test_rejects_invalid_structured_debate_state(self) -> None:
        invalid_cases = []

        unknown_evidence = sample_debate()
        unknown_evidence["claim_ledger"][0]["evidence"] = ["F404"]
        invalid_cases.append((unknown_evidence, "unknown evidence"))

        unknown_camp = sample_debate()
        unknown_camp["belief_updates"][0]["camp"] = "missing"
        invalid_cases.append((unknown_camp, "unknown camp"))

        invalid_confidence = sample_debate()
        invalid_confidence["belief_updates"][0]["after"] = 1.2
        invalid_cases.append((invalid_confidence, "between 0 and 1"))

        unsafe_url = sample_debate()
        unsafe_url["evidence_cards"][0]["source_url"] = "javascript:alert(1)"
        invalid_cases.append((unsafe_url, "http or https"))

        invalid_status = sample_debate()
        invalid_status["status"] = "ALMOST_DONE"
        invalid_cases.append((invalid_status, "status must be one of"))

        invalid_evidence_mode = sample_debate()
        invalid_evidence_mode["evidence_mode"] = "open-web"
        invalid_cases.append((invalid_evidence_mode, "evidence_mode must be one of"))

        invalid_phase = sample_debate()
        invalid_phase["messages"][1]["phase"] = "FREE_CHAT"
        invalid_cases.append((invalid_phase, "phase must be one of"))

        invalid_proposition_type = sample_debate()
        invalid_proposition_type["proposition_type"] = "OPINION"
        invalid_cases.append((invalid_proposition_type, "proposition_type must be one of"))

        missing_forecast_threshold = sample_debate()
        missing_forecast_threshold["decision_rule"].pop("threshold")
        invalid_cases.append((missing_forecast_threshold, "threshold is required"))

        invalid_interval = sample_debate()
        invalid_interval["forecast_records"][0]["lower"] = 0.80
        invalid_cases.append((invalid_interval, "lower <= probability <= upper"))

        duplicate_forecast = sample_debate()
        duplicate_forecast["forecast_records"].append(
            duplicate_forecast["forecast_records"][0].copy()
        )
        invalid_cases.append((duplicate_forecast, "duplicate forecast record"))

        unknown_link_claim = sample_debate()
        unknown_link_claim["evidence_links"][0]["claim_id"] = "C404"
        invalid_cases.append((unknown_link_claim, "unknown claim"))

        unknown_needed_claim = sample_debate()
        unknown_needed_claim["needed_evidence"][0]["resolves_claims"] = ["C404"]
        invalid_cases.append((unknown_needed_claim, "unknown claim"))

        for debate, error in invalid_cases:
            with self.subTest(error=error):
                with self.assertRaisesRegex(ValueError, error):
                    self.renderer.render_document(debate)

    def test_rejects_messages_for_unknown_camps(self) -> None:
        debate = sample_debate()
        debate["messages"][1]["camp"] = "missing"

        with self.assertRaisesRegex(ValueError, "unknown camp"):
            self.renderer.render_document(debate)

    def test_allows_anonymous_resolution_messages(self) -> None:
        debate = sample_debate()
        debate["messages"].append(
            {
                "kind": "resolution",
                "resolution_stage": "candidate",
                "speaker": "Candidate A",
                "text": "A common-core candidate.",
            }
        )

        html = self.renderer.render_document(debate)

        self.assertIn("Candidate A", html)
        self.assertIn("A common-core candidate.", html)

    def test_rejects_camp_identity_on_anonymous_resolution_stages(self) -> None:
        for stage in ("candidate", "confirmation"):
            debate = sample_debate()
            debate["messages"].append(
                {
                    "kind": "resolution",
                    "resolution_stage": stage,
                    "camp": "precaution",
                    "speaker": "Candidate A",
                    "text": "This must not reveal provenance.",
                }
            )

            with self.subTest(stage=stage):
                with self.assertRaisesRegex(ValueError, "must not identify a camp"):
                    self.renderer.render_document(debate)

    def test_requires_resolution_stage_for_state_driven_artifacts(self) -> None:
        debate = sample_debate()
        debate["messages"].append(
            {
                "kind": "resolution",
                "camp": "precaution",
                "text": "An unstaged candidate must not reveal its source.",
            }
        )

        with self.assertRaisesRegex(ValueError, "resolution_stage is required"):
            self.renderer.render_document(debate)

    def test_allows_attributed_public_resolution_statements(self) -> None:
        debate = sample_debate()
        debate["messages"].append(
            {
                "kind": "resolution",
                "resolution_stage": "public-statement",
                "camp": "precaution",
                "text": "This is an attributed final statement.",
            }
        )

        html = self.renderer.render_document(debate)

        self.assertIn("This is an attributed final statement.", html)

    def test_requires_complete_forecast_checkpoints_for_terminal_forecasts(self) -> None:
        missing_prior = sample_debate()
        missing_prior["forecast_records"] = [
            record
            for record in missing_prior["forecast_records"]
            if not (record["camp"] == "precaution" and record["checkpoint"] == "PRIOR")
        ]

        with self.assertRaisesRegex(ValueError, "missing required forecast checkpoint"):
            self.renderer.render_document(missing_prior)

        missing_cycle = sample_debate()
        missing_cycle["forecast_records"] = [
            record
            for record in missing_cycle["forecast_records"]
            if not (
                record["camp"] == "innovation"
                and record["checkpoint"] == "AFTER_CRUCIAL_DISPUTE"
                and record["cycle"] == 1
            )
        ]

        with self.assertRaisesRegex(ValueError, "missing forecast for crucial-dispute cycle"):
            self.renderer.render_document(missing_cycle)

    def test_allows_partial_forecasts_for_incomplete_artifacts(self) -> None:
        debate = sample_debate()
        debate["status"] = "INCOMPLETE"
        debate["forecast_records"] = debate["forecast_records"][:1]

        html = self.renderer.render_document(debate)

        self.assertIn("INCOMPLETE", html)

    def test_allows_unperformed_forecast_checkpoints_after_an_early_deadline(self) -> None:
        debate = sample_debate()
        debate["debate_progress"] = {
            "completed_phases": ["OPENING"],
            "completed_crucial_cycles": 0,
        }
        debate["forecast_records"] = [
            record
            for record in debate["forecast_records"]
            if record["checkpoint"] in {"PRIOR", "FINAL"}
        ]

        html = self.renderer.render_document(debate)

        self.assertIn("FINAL", html)
        self.assertNotIn("AFTER CROSS EXAM", html)

    def test_cli_writes_a_standalone_html_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            input_path = root / "debate.json"
            output_path = root / "debate-chat.html"
            input_path.write_text(json.dumps(sample_debate()), encoding="utf-8")

            with mock.patch.object(
                sys,
                "argv",
                [str(SCRIPT_PATH), str(input_path), "--output", str(output_path)],
            ):
                result = self.renderer.main()

            self.assertEqual(0, result)
            self.assertTrue(output_path.is_file())
            self.assertIn("<!doctype html>", output_path.read_text(encoding="utf-8").lower())


if __name__ == "__main__":
    unittest.main()

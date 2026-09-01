from pathlib import Path
import unittest


SKILL_PATH = Path(__file__).resolve().parents[1] / "SKILL.md"
STATE_PROTOCOL_PATH = SKILL_PATH.parent / "references" / "debate-state-protocol.md"


class AutonomousDebateProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.content = SKILL_PATH.read_text(encoding="utf-8")
        cls.protocol_content = cls.content
        if STATE_PROTOCOL_PATH.exists():
            cls.protocol_content += "\n" + STATE_PROTOCOL_PATH.read_text(encoding="utf-8")

    def test_selects_evidenced_camps_instead_of_fixed_personas(self) -> None:
        self.assertIn("two to four", self.content)
        self.assertIn("real-world camps", self.content)
        self.assertNotIn("exactly two subagents", self.content)

    def test_keeps_peer_to_peer_debate_and_parent_supervision(self) -> None:
        for marker in ("spawn_agent", "followup_task", "send_message", "wait_agent"):
            with self.subTest(marker=marker):
                self.assertIn(f"`{marker}`", self.content)

    def test_requires_independent_resolution_candidates_without_majority_vote(self) -> None:
        self.assertIn("Do not use majority vote", self.content)
        self.assertIn("every active camp", self.content)
        self.assertIn("`RESOLUTION_REQUEST`", self.content)
        self.assertIn("RESOLUTION_CANDIDATE\nOUTCOME:", self.content)
        self.assertIn("independently and privately", self.content)
        self.assertIn("Do not put the submitting camp's identity", self.content)
        self.assertIn("deterministic content-derived key", self.content)
        self.assertIn("Do not ask the opener to draft", self.content)
        self.assertIn("`COMMON_CORE_CHECK`", self.protocol_content)
        self.assertIn("`CONSENSUS_WITH_RESERVATIONS`", self.protocol_content)
        self.assertIn("`TRUE_DEADLOCK`", self.protocol_content)
        self.assertIn("non-voting synthesis", self.protocol_content)
        self.assertIn("`ACCEPT_WINNER <CAMP>`", self.protocol_content)
        self.assertNotIn("On `RESOLUTION_START`, have the opener", self.content)
        for outcome in (
            "FINAL_CONSENSUS",
            "CONSENSUS_WITH_RESERVATIONS",
            "FINAL_WINNER",
            "TRUE_DEADLOCK",
        ):
            with self.subTest(outcome=outcome):
                self.assertIn(f"`{outcome}`", self.protocol_content)

    def test_uses_state_driven_phases_instead_of_fixed_rounds(self) -> None:
        for phase in ("OPENING", "CROSS_EXAM", "RESPONSE", "UPDATE", "CRUCIAL_DISPUTE"):
            with self.subTest(phase=phase):
                self.assertIn(f"`{phase}`", self.protocol_content)
        for field in ("POSITIVE_CASE", "BURDEN_OF_PROOF", "REBUTTAL", "UNCERTAINTY"):
            with self.subTest(field=field):
                self.assertIn(field, self.protocol_content)
        self.assertIn("Claim Ledger", self.protocol_content)
        self.assertIn("two consecutive low-information cycles", self.protocol_content)
        self.assertIn("new ledger action", self.protocol_content)
        self.assertIn("`REQUEST_RESOLUTION`", self.protocol_content)
        self.assertIn("same phase checkpoint", self.protocol_content)
        self.assertIn("exact fenced response template", self.content)
        self.assertIn("post-`RESPONSE` `UPDATE` checkpoint", self.content)
        self.assertIn("same `CRUCIAL_DISPUTE` checkpoint", self.content)
        self.assertNotIn("Use 3 rounds per camp", self.content)
        self.assertNotIn("Use 5 rounds per camp", self.content)

    def test_requires_cross_exam_steelman_and_a_non_voting_auditor(self) -> None:
        self.assertIn("one difficult question", self.protocol_content)
        self.assertIn("STEELMAN", self.protocol_content)
        self.assertIn("STEELMAN_ACCEPTED", self.protocol_content)
        self.assertIn("non-voting methodological auditor", self.protocol_content)

    def test_defines_phase_specific_speaker_rings_and_auditor_turns(self) -> None:
        self.assertIn("PHASE_SPEAKERS", self.protocol_content)
        for marker in (
            "OPENING: advocates, then auditor",
            "CROSS_EXAM: advocates only",
            "RESPONSE: advocates, then auditor",
            "UPDATE: advocates only",
            "CRUCIAL_DISPUTE: advocates only",
            "phase-specific successor",
            "two base auditor turns",
            "one additional auditor turn per crucial-dispute cycle",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.protocol_content)

    def test_defines_bounded_steelman_confirmation_subphase(self) -> None:
        for marker in (
            "STEELMAN_CONFIRMATION",
            "forwards each steelman unchanged",
            "with `followup_task`",
            "returns only to the parent",
            "Collect every confirmation before resolution",
            "one correction",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.protocol_content)

    def test_structures_evidence_and_records_belief_updates(self) -> None:
        self.assertIn("Evidence Card", self.protocol_content)
        self.assertIn("causal strength", self.protocol_content)
        self.assertIn("generalizability", self.protocol_content)
        self.assertIn("belief update", self.protocol_content)
        self.assertIn("self-assessment, not independent evidence", self.protocol_content)

    def test_fixes_proposition_type_and_decision_rule_before_spawning(self) -> None:
        for proposition_type in ("FORECAST", "CAUSAL", "FACTUAL", "POLICY"):
            with self.subTest(proposition_type=proposition_type):
                self.assertIn(f"`{proposition_type}`", self.protocol_content)
        for field in (
            "TARGET_EVENT",
            "HORIZON",
            "YES_CONDITION",
            "NO_CONDITION",
            "RESOLUTION_SOURCE",
        ):
            with self.subTest(field=field):
                self.assertIn(field, self.protocol_content)
        self.assertIn("before spawning", self.content)

    def test_separates_assigned_position_from_private_forecasts(self) -> None:
        for checkpoint in (
            "PRIOR",
            "AFTER_CROSS_EXAM",
            "AFTER_CRUCIAL_DISPUTE",
            "FINAL",
        ):
            with self.subTest(checkpoint=checkpoint):
                self.assertIn(checkpoint, self.protocol_content)
        self.assertIn("ASSIGNED_POSITION", self.protocol_content)
        self.assertIn("withhold", self.protocol_content.lower())
        self.assertIn("not calibrated", self.protocol_content)
        self.assertIn("Brier", self.protocol_content)

    def test_requires_falsifiers_and_claim_level_evidence_links(self) -> None:
        self.assertIn("FALSIFIER", self.protocol_content)
        self.assertIn("EVIDENCE_LINK", self.protocol_content)
        for dimension in (
            "DIRECTNESS",
            "INDEPENDENCE",
            "CAUSAL_STRENGTH",
            "GENERALIZABILITY",
            "TEMPORAL_RELEVANCE",
            "DOES_NOT_ESTABLISH",
        ):
            with self.subTest(dimension=dimension):
                self.assertIn(dimension, self.protocol_content)

    def test_uses_information_gain_with_a_hard_ceiling(self) -> None:
        self.assertIn("3 percentage points", self.protocol_content)
        self.assertIn("5 percentage points", self.protocol_content)
        self.assertIn("two consecutive low-information cycles", self.protocol_content)
        self.assertIn("three cycles for a light debate", self.protocol_content)
        self.assertIn("six for a deep debate", self.protocol_content)
        self.assertIn("hard ceiling", self.protocol_content)

    def test_reports_what_would_resolve_the_dispute(self) -> None:
        self.assertIn("WHAT_WOULD_RESOLVE_THIS", self.protocol_content)
        self.assertIn("needed evidence", self.content.lower())
        self.assertIn("inference-link audits", self.protocol_content)

    def test_defines_bounded_failure_handling(self) -> None:
        for marker in ("user cancellation", "agent failure", "message-delivery failure"):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.content)
        self.assertIn("Send `STOP` to every active agent", self.content)

    def test_uses_parent_observable_phase_deadlines(self) -> None:
        for marker in (
            "DEBATE_START",
            "DEBATE_DEADLINE",
            "RESOLUTION_START",
            "RESOLUTION_DEADLINE",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.content)

        self.assertIn("planned substantive turn ceiling", self.content)
        self.assertIn("max(4 minutes, camp count * 1 minute)", self.content)
        self.assertIn("successfully sent `START` to the opener", self.content)
        self.assertIn(
            "successfully sent the identical `RESOLUTION_REQUEST` to every active voting camp",
            self.content,
        )
        self.assertNotIn("Use 4 minutes, 3 rounds", self.content)
        self.assertNotIn("Use 12 minutes, 5 rounds", self.content)

    def test_requires_a_group_chat_artifact_with_a_text_fallback(self) -> None:
        self.assertIn("`scripts/render_debate_chat.py`", self.content)
        self.assertIn("self-contained HTML", self.content)
        self.assertIn("chronological event log", self.content)
        self.assertIn("Markdown transcript", self.content)
        self.assertIn("Do not delay or invalidate the terminal result", self.content)


if __name__ == "__main__":
    unittest.main()

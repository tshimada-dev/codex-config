from pathlib import Path
import unittest


SKILL_PATH = Path(__file__).resolve().parents[1] / "SKILL.md"


class AutonomousDebateProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.content = SKILL_PATH.read_text(encoding="utf-8")

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
        self.assertIn("Do not merge, rewrite, or synthesize", self.content)
        self.assertIn("same `OUTCOME`", self.content)
        self.assertNotIn("On `RESOLUTION_START`, have the opener", self.content)
        for outcome in ("FINAL_CONSENSUS", "FINAL_WINNER", "DEADLOCK"):
            with self.subTest(outcome=outcome):
                self.assertIn(f"`{outcome}`", self.content)

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

        self.assertIn("max(4 minutes, camp count * round count * 1 minute)", self.content)
        self.assertIn("max(3 minutes, camp count * 1 minute)", self.content)
        self.assertIn("successfully sent `START` to the opener", self.content)
        self.assertIn(
            "successfully sent the identical `RESOLUTION_REQUEST` to every active camp",
            self.content,
        )
        self.assertIn("3 camps * 3 rounds = 9 debate minutes + 3 resolution minutes", self.content)
        self.assertIn("3 camps * 5 rounds = 15 debate minutes + 3 resolution minutes", self.content)
        self.assertNotIn("Use 4 minutes, 3 rounds", self.content)
        self.assertNotIn("Use 12 minutes, 5 rounds", self.content)


if __name__ == "__main__":
    unittest.main()

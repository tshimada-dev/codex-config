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

    def test_requires_unanimous_terminal_confirmation_not_majority_vote(self) -> None:
        self.assertIn("Do not use majority vote", self.content)
        self.assertIn("every active camp", self.content)
        self.assertIn("trigger every other camp with `followup_task`", self.content)
        for outcome in ("FINAL_CONSENSUS", "FINAL_WINNER", "DEADLOCK"):
            with self.subTest(outcome=outcome):
                self.assertIn(f"`{outcome}`", self.content)

    def test_defines_bounded_failure_handling(self) -> None:
        for marker in ("user cancellation", "agent failure", "message-delivery failure"):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.content)
        self.assertIn("Send `STOP` to every active agent", self.content)


if __name__ == "__main__":
    unittest.main()

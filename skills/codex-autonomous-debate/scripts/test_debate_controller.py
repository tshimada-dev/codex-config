import json
from pathlib import Path
import unittest
from unittest import mock

from debate_controller import DebateController, main


def action(event_id, actor, phase, action_type="TURN", payload=None):
    return {
        "debate_id": "d-50",
        "event_id": event_id,
        "actor": actor,
        "action_type": action_type,
        "phase": phase,
        "payload": payload or {},
    }


class DebateControllerTests(unittest.TestCase):
    def make(self, **kwargs):
        return DebateController(
            "d-50",
            [
                {"id": "affirm", "role": "advocate"},
                {"id": "oppose", "role": "advocate"},
            ],
            now=lambda: "2026-09-03T00:00:00Z",
            **kwargs,
        )

    def turn(self, controller, event_id, actor, payload=None):
        return controller.submit(action(event_id, actor, controller.phase, payload=payload))

    def through_opening(self, controller):
        self.assertTrue(self.turn(controller, "o1", "affirm", {"ledger_actions": [{"op": "ADD", "text": "A", "type": "fact", "falsifier": "x"}]} )["accepted"])
        self.assertTrue(self.turn(controller, "o2", "oppose", {"ledger_actions": [{"op": "ADD", "text": "B", "type": "fact", "falsifier": "y"}]} )["accepted"])

    def through_update(self, controller, request=False):
        if controller.phase == "OPENING":
            self.through_opening(controller)
        self.turn(controller, "q1", "affirm", {"questions": [{"id": "Q1", "target": "oppose", "claim_id": "C1", "text": "why?"}]})
        self.turn(controller, "q2", "oppose", {"questions": [{"id": "Q2", "target": "affirm", "claim_id": "C2", "text": "why not?"}]})
        self.turn(controller, "r1", "affirm", {"answers": ["Q2"]})
        self.turn(controller, "r2", "oppose", {"answers": ["Q1"]})
        self.turn(controller, "u1", "affirm", {"steelman_target": "oppose", "steelman": "best B", "request_resolution": request})
        self.turn(controller, "u2", "oppose", {"steelman_target": "affirm", "steelman": "best A", "request_resolution": request})

    def confirm_steelmans(self, controller, prefix="s"):
        self.assertEqual("STEELMAN_CONFIRMATION", controller.phase)
        self.assertTrue(controller.submit(action(prefix + "1", "oppose", controller.phase, "STEELMAN_CONFIRM", {"accepted": True}))["accepted"])
        self.assertTrue(controller.submit(action(prefix + "2", "affirm", controller.phase, "STEELMAN_CONFIRM", {"accepted": True}))["accepted"])

    def test_canonical_phase_and_speaker_progression(self):
        controller = self.make()
        self.assertEqual(("OPENING", "affirm"), (controller.phase, controller.next_actor))
        self.through_opening(controller)
        self.assertEqual(("CROSS_EXAM", "affirm"), (controller.phase, controller.next_actor))
        self.through_update(controller)
        self.confirm_steelmans(controller)
        self.assertEqual(("CRUCIAL_DISPUTE", "affirm", 1), (controller.phase, controller.next_actor, controller.cycle))

    def test_canonicalizes_auditor_order_and_participant_limits(self):
        controller = DebateController(
            "d-50",
            [
                {"id": "methods", "role": "auditor"},
                {"id": "affirm", "role": "advocate"},
                {"id": "oppose", "role": "advocate"},
            ],
            now=lambda: "2026-09-03T00:00:00Z",
        )
        self.assertEqual(["affirm", "oppose", "methods"], controller.phase_speakers["OPENING"])
        self.assertEqual("affirm", controller.next_actor)
        with self.assertRaisesRegex(ValueError, "two to four advocates"):
            DebateController(
                "too-many",
                [{"id": f"a{index}", "role": "advocate"} for index in range(5)],
            )
        with self.assertRaisesRegex(ValueError, "at most one auditor"):
            DebateController(
                "too-many-auditors",
                [
                    {"id": "a", "role": "advocate"},
                    {"id": "b", "role": "advocate"},
                    {"id": "m1", "role": "auditor"},
                    {"id": "m2", "role": "auditor"},
                ],
            )
        with self.assertRaisesRegex(ValueError, "__parent__ is reserved"):
            DebateController(
                "reserved-parent",
                [
                    {"id": "__parent__", "role": "advocate"},
                    {"id": "b", "role": "advocate"},
                ],
            )

    def test_duplicate_and_ambiguous_delivery_do_not_append(self):
        controller = self.make()
        first = self.turn(controller, "same", "affirm")
        retry = self.turn(controller, "same", "affirm")
        self.assertTrue(first["accepted"])
        self.assertEqual(first, retry)
        self.assertEqual(1, len(controller.accepted_events))
        self.assertEqual(1, controller.accepted_sequence)
        duplicate_audit = controller.artifact_metadata(include_private=True)["events"][-1]
        self.assertFalse(duplicate_audit["accepted"])
        self.assertEqual("duplicate_delivery", duplicate_audit["rejection_reason"])
        self.assertIsNone(duplicate_audit["committed_at"])

    def test_conflicting_event_id_is_rejected(self):
        controller = self.make()
        self.turn(controller, "same", "affirm")
        result = controller.submit(action("same", "affirm", "OPENING", payload={"x": 1}))
        self.assertFalse(result["accepted"])
        self.assertEqual("conflicting_event_id", result["reason"])
        self.assertEqual(1, controller.accepted_sequence)

    def test_out_of_order_and_phase_barrier_do_not_mutate(self):
        controller = self.make()
        wrong = self.turn(controller, "bad", "oppose")
        self.assertFalse(wrong["accepted"])
        self.assertEqual("wrong_actor", wrong["reason"])
        self.assertEqual(0, controller.accepted_sequence)
        self.turn(controller, "o1", "affirm")
        self.assertEqual("oppose", controller.next_actor)  # reject did not consume a turn

    def test_questions_and_claim_ids_are_ordered_and_responses_required(self):
        controller = self.make()
        self.through_opening(controller)
        self.assertEqual(["C1", "C2"], [c["id"] for c in controller.claim_ledger])
        bad_question = self.turn(controller, "q0", "affirm", {"questions": [{"id": "Q0", "target": "oppose", "claim_id": "C404", "text": "why"}]})
        self.assertFalse(bad_question["accepted"])
        self.assertEqual("unknown_question_claim", bad_question["reason"])
        self.turn(controller, "q1", "affirm", {"questions": [{"id": "Q1", "target": "oppose", "claim_id": "C1", "text": "why"}]})
        self.turn(controller, "q2", "oppose", {"questions": [{"id": "Q2", "target": "affirm", "claim_id": "C2", "text": "why"}]})
        rejected = self.turn(controller, "r0", "affirm", {"answers": []})
        self.assertFalse(rejected["accepted"])
        self.assertEqual("missing_required_answers", rejected["reason"])
        self.turn(controller, "r1", "affirm", {"answers": ["Q2"]})
        self.assertEqual(["Q1", "Q2"], [q["id"] for q in controller.questions])
        self.assertEqual("Q2", controller.responses[0]["question_id"])

    def test_premature_confirmation_and_one_correction_bound(self):
        controller = self.make()
        self.assertFalse(controller.submit(action("x", "affirm", "STEELMAN_CONFIRMATION", "STEELMAN_CONFIRM", {"accepted": True}))["accepted"])
        self.through_update(controller)
        self.assertTrue(controller.submit(action("s1", "oppose", controller.phase, "STEELMAN_CONFIRM", {"accepted": False}))["accepted"])
        self.assertEqual("affirm", controller.next_actor)
        self.assertTrue(controller.submit(action("fix", "affirm", controller.phase, "STEELMAN_CORRECTION", {"steelman": "fixed"}))["accepted"])
        self.assertTrue(controller.submit(action("s2", "oppose", controller.phase, "STEELMAN_CONFIRM", {"accepted": False}))["accepted"])
        bounded = controller.submit(action("fix2", "affirm", controller.phase, "STEELMAN_CORRECTION", {"steelman": "again"}))
        self.assertFalse(bounded["accepted"])
        self.assertEqual("unexpected_steelman_correction", bounded["reason"])
        self.assertTrue(controller.submit(action("s3", "affirm", controller.phase, "STEELMAN_CONFIRM", {"accepted": True}))["accepted"])
        self.assertEqual("CRUCIAL_DISPUTE", controller.phase)

    def test_resume_is_equivalent_without_transcript_parsing(self):
        controller = self.make()
        self.through_opening(controller)
        restored = DebateController.from_json(controller.to_json(), now=lambda: "2026-09-03T00:00:00Z")
        next_event = action("q1", "affirm", "CROSS_EXAM", payload={"questions": [{"id": "Q1", "target": "oppose", "claim_id": "C1", "text": "why"}]})
        self.assertEqual(controller.submit(next_event), restored.submit(next_event))
        self.assertEqual(controller.to_dict(), restored.to_dict())

    def test_more_than_six_material_crucial_cycles_continue(self):
        controller = self.make()
        self.through_update(controller)
        self.confirm_steelmans(controller)
        for number in range(1, 8):
            self.turn(controller, "a%d" % number, "affirm", {"material_progress": True, "ledger_actions": [{"op": "REFINE", "claim_id": "C1", "text": "r%d" % number}]})
            self.turn(controller, "b%d" % number, "oppose", {"material_progress": True})
            if number < 7:
                self.assertEqual(number + 1, controller.cycle)
        self.assertEqual(("CRUCIAL_DISPUTE", 8), (controller.phase, controller.cycle))

    def test_repeated_equal_forecast_shift_counts_when_probability_keeps_changing(self):
        controller = self.make()
        self.through_update(controller)
        self.confirm_steelmans(controller)
        probabilities = ((0.55, 0.45), (0.60, 0.40), (0.65, 0.35))
        for cycle, (affirm_probability, oppose_probability) in enumerate(probabilities, 1):
            self.turn(controller, f"fa-{cycle}", "affirm", {"forecast_probability_shift": 0.05, "forecast_probability": affirm_probability})
            self.turn(controller, f"fo-{cycle}", "oppose", {"forecast_probability_shift": -0.05, "forecast_probability": oppose_probability})
        self.assertEqual(("CRUCIAL_DISPUTE", 4), (controller.phase, controller.cycle))

    def test_no_progress_and_unanimous_resolution_route(self):
        controller = self.make()
        self.through_update(controller)
        self.confirm_steelmans(controller)
        for event_id, actor in (("a1", "affirm"), ("b1", "oppose"), ("a2", "affirm"), ("b2", "oppose")):
            self.turn(controller, event_id, actor, {"no_material_change": True})
        self.assertEqual("RESOLUTION_CANDIDATE", controller.phase)
        other = self.make()
        self.through_update(other, request=True)
        self.confirm_steelmans(other)
        self.assertEqual("RESOLUTION_CANDIDATE", other.phase)

    def test_bare_material_progress_flag_does_not_keep_crucial_cycles_alive(self):
        controller = self.make()
        self.through_update(controller)
        self.confirm_steelmans(controller)
        for event_id, actor in (("a1", "affirm"), ("b1", "oppose"), ("a2", "affirm"), ("b2", "oppose")):
            self.turn(controller, event_id, actor, {"material_progress": True})
        self.assertEqual("RESOLUTION_CANDIDATE", controller.phase)

    def test_repeated_identical_refinement_is_not_material_progress(self):
        controller = self.make()
        self.through_update(controller)
        self.confirm_steelmans(controller)
        # The first adoption by each camp is a real ledger relation change;
        # two subsequent identical cycles must then count as no progress.
        for cycle in range(1, 4):
            for actor in ("affirm", "oppose"):
                self.turn(
                    controller,
                    f"refine-{cycle}-{actor}",
                    actor,
                    {
                        "ledger_actions": [
                            {
                                "op": "REFINE",
                                "claim_id": "C1",
                                "text": "same narrower claim",
                            }
                        ]
                    },
                )
        self.assertEqual("RESOLUTION_CANDIDATE", controller.phase)

    def test_repeated_identical_falsifier_is_not_material_progress(self):
        controller = self.make()
        self.through_update(controller)
        self.confirm_steelmans(controller)
        for cycle in range(1, 4):
            for actor in ("affirm", "oppose"):
                self.turn(
                    controller,
                    f"falsifier-{cycle}-{actor}",
                    actor,
                    {"next_falsifier": "same observable test"},
                )
        self.assertEqual("RESOLUTION_CANDIDATE", controller.phase)

    def test_terminal_prerequisites_and_unanimous_consensus(self):
        controller = self.make()
        self.through_update(controller, request=True)
        self.confirm_steelmans(controller)
        self.assertFalse(controller.submit(action("bad-final", "affirm", controller.phase, "FINALIZE", {}))["accepted"])
        candidate = {"outcome": "CONSENSUS", "decision": "do X", "agreed_points": ["C1"]}
        self.assertTrue(controller.submit(action("c1", "affirm", controller.phase, "RESOLUTION_CANDIDATE", candidate))["accepted"])
        self.assertTrue(controller.submit(action("c2", "oppose", controller.phase, "RESOLUTION_CANDIDATE", candidate))["accepted"])
        self.assertEqual("COMMON_CORE_CONFIRMATION", controller.phase)
        self.assertTrue(controller.submit(action("cc1", "affirm", controller.phase, "COMMON_CORE_CONFIRM", {"response": "ACCEPT_COMMON_CORE"}))["accepted"])
        self.assertTrue(controller.submit(action("cc2", "oppose", controller.phase, "COMMON_CORE_CONFIRM", {"response": "ACCEPT_COMMON_CORE"}))["accepted"])
        self.assertEqual("FINAL_CONSENSUS", controller.terminal_status)

    def test_claim_status_and_evidence_link_events(self):
        controller = self.make()
        self.turn(controller, "o1", "affirm", {"ledger_actions": [{"op": "ADD", "text": "A", "type": "inference", "falsifier": "x"}], "evidence_links": [{"evidence_id": "E1", "claim_id": "C1", "supports": "s"}]})
        rejected = self.turn(controller, "bad-status", "oppose", {"ledger_actions": [{"op": "SET_STATUS", "claim_id": "C1", "status": "agreed"}]})
        self.assertFalse(rejected["accepted"])
        self.assertEqual("controller_owned_claim_status", rejected["reason"])
        self.turn(controller, "o2", "oppose", {"ledger_actions": [{"op": "ACCEPT", "claim_id": "C1"}]})
        self.assertEqual("agreed", controller.claim_ledger[0]["status"])
        self.assertEqual("o1", controller.evidence_link_events[0]["event_id"])

    def test_new_claim_requires_known_type_and_revision_condition(self):
        for ledger_action, reason in (
            ({"op": "ADD", "text": "A", "type": "prediction"}, "claim_revision_condition_required"),
            ({"op": "ADD", "text": "A", "type": "mystery", "falsifier": "x"}, "invalid_claim_type"),
        ):
            with self.subTest(reason=reason):
                controller = self.make()
                result = self.turn(controller, "bad-claim", "affirm", {"ledger_actions": [ledger_action]})
                self.assertFalse(result["accepted"])
                self.assertEqual(reason, result["reason"])
                self.assertEqual([], controller.claim_ledger)

    def test_controller_derives_extended_claim_statuses_from_participant_signals(self):
        controller = self.make()
        self.turn(controller, "o1", "affirm", {"ledger_actions": [
            {"op": "ADD", "text": "Empirical A", "type": "prediction", "falsifier": "x"},
            {"op": "ADD", "text": "Narrow A", "type": "prediction", "falsifier": "y"},
            {"op": "ADD", "text": "Term A", "type": "definition", "revision_condition": "shared scope"},
            {"op": "ADD", "text": "Broad A", "type": "prediction", "falsifier": "z"},
            {"op": "UNSUPPORTED", "claim_id": "C1"},
            {"op": "DEFINITIONAL_DISPUTE", "claim_id": "C3"},
            {"op": "SUPERSEDE", "claim_id": "C4", "replacement_claim_id": "C2"},
        ]})
        self.turn(controller, "o2", "oppose", {"ledger_actions": [
            {"op": "DEFINITIONAL_DISPUTE", "claim_id": "C3"},
            {"op": "UNSUPPORTED", "claim_id": "C1"},
            {"op": "SUPERSEDE", "claim_id": "C4", "replacement_claim_id": "C2"},
        ]})
        self.assertEqual("unsupported", controller.claim_ledger[0]["status"])
        self.assertEqual("definitional_dispute", controller.claim_ledger[2]["status"])
        self.assertEqual("superseded", controller.claim_ledger[3]["status"])
        self.assertEqual("C2", controller.claim_ledger[3]["superseded_by"])

    def test_parent_control_action_can_cancel_without_owning_the_turn(self):
        controller = self.make()
        result = controller.submit(action("cancel", "__parent__", "OPENING", "CANCEL"))
        self.assertTrue(result["accepted"])
        self.assertEqual("INCOMPLETE", controller.terminal_status)
        self.assertIsNone(controller.next_actor)
        self.assertIsNone(controller.next_action)
        restored = DebateController.from_json(
            controller.to_json(), now=lambda: "2026-09-03T00:00:00Z"
        )
        self.assertEqual("INCOMPLETE", restored.terminal_status)

    def test_participant_cannot_submit_parent_control_actions(self):
        for action_type in ("CANCEL", "FAILURE", "SAFETY_CEILING", "COMMON_CORE_CORRECTION"):
            with self.subTest(action_type=action_type):
                controller = self.make()
                result = controller.submit(
                    action("control-" + action_type, "affirm", "OPENING", action_type)
                )
                self.assertFalse(result["accepted"])
                self.assertEqual("parent_action_required", result["reason"])
                self.assertIsNone(controller.terminal_status)

    def test_contradictory_no_progress_signal_is_rejected(self):
        controller = self.make()
        self.through_update(controller)
        self.confirm_steelmans(controller)
        result = self.turn(
            controller,
            "contradiction",
            "affirm",
            {"no_material_change": True, "next_falsifier": "Observe X"},
        )
        self.assertFalse(result["accepted"])
        self.assertEqual("contradictory_progress_signal", result["reason"])
        self.assertEqual("affirm", controller.next_actor)

    def test_safety_ceiling_never_fabricates_consensus(self):
        controller = self.make(emergency_safety={"event_limit": 1})
        self.turn(controller, "o1", "affirm")
        result = self.turn(controller, "o2", "oppose")
        self.assertFalse(result["accepted"])
        self.assertEqual("INCOMPLETE", controller.terminal_status)
        self.assertNotIn(controller.terminal_status, {"FINAL_CONSENSUS", "FINAL_WINNER"})

    def test_safety_during_first_common_core_rejection_is_incomplete(self):
        controller = self.make()
        self.through_update(controller, request=True)
        self.confirm_steelmans(controller)
        candidate = {"outcome": "CONSENSUS", "decision": "do X", "agreed_points": ["C1"]}
        controller.submit(action("c1", "affirm", controller.phase, "RESOLUTION_CANDIDATE", candidate))
        controller.submit(action("c2", "oppose", controller.phase, "RESOLUTION_CANDIDATE", candidate))
        controller.submit(action("cc1", "affirm", controller.phase, "COMMON_CORE_CONFIRM", {"response": "ACCEPT_COMMON_CORE"}))
        controller.submit(action("cc2", "oppose", controller.phase, "COMMON_CORE_CONFIRM", {"response": "REJECT_COMMON_CORE: A1 scope"}))
        result = controller.submit(action("safety", "__parent__", controller.phase, "SAFETY_CEILING"))
        self.assertTrue(result["accepted"])
        self.assertEqual("INCOMPLETE", controller.terminal_status)

    def test_emergency_safety_requires_positive_configured_limits(self):
        for config in (
            {"event_limit": 0},
            {"event_limit": -1},
            {"event_limit": True},
            {"time_limit_seconds": 0},
            {"time_limit_seconds": -1},
            {"time_limit_seconds": True},
            {"time_limit_seconds": 30, "started_at": "not-a-time"},
        ):
            with self.subTest(config=config):
                with self.assertRaisesRegex(ValueError, "emergency safety"):
                    self.make(emergency_safety=config)

    def test_common_core_mapping_is_source_grounded_and_deterministic(self):
        controller = self.make()
        self.through_update(controller, request=True)
        self.confirm_steelmans(controller)
        shared = {"text": "Measure before release", "claim_ids": ["C1"]}
        controller.submit(action("c1", "affirm", controller.phase, "RESOLUTION_CANDIDATE", {
            "outcome": "CONSENSUS_WITH_RESERVATIONS",
            "decision": "stage release",
            "agreed_points": [shared],
            "reservations": [{"text": "audit monthly", "claim_ids": ["C2"]}],
        }))
        controller.submit(action("c2", "oppose", controller.phase, "RESOLUTION_CANDIDATE", {
            "outcome": "CONSENSUS_WITH_RESERVATIONS",
            "decision": "stage release",
            "agreed_points": [shared],
            "conflicts": [{"text": "who pays", "claim_ids": ["C2"]}],
        }))
        resolution = controller.resolution
        self.assertEqual("stage release", resolution["common_decision"])
        self.assertEqual(2, len(resolution["common_atoms"]))
        common = next(
            atom for atom in resolution["common_atoms"]
            if atom["field"] == "agreed_points"
        )
        self.assertEqual(["C1"], common["claim_ids"])
        self.assertEqual(["R1", "R2"], common["candidate_ids"])
        self.assertEqual({"R1", "R2"}, set(resolution["source_map"][common["id"]]["candidate_ids"]))
        self.assertEqual(1, len(resolution["reservations"]))
        self.assertEqual(1, len(resolution["conflicts"]))

    def test_rejected_common_core_gets_one_parent_correction_and_reconfirmation(self):
        controller = self.make()
        self.through_update(controller, request=True)
        self.confirm_steelmans(controller)
        candidate = {"outcome": "CONSENSUS", "decision": "do X", "agreed_points": ["C1"]}
        controller.submit(action("c1", "affirm", controller.phase, "RESOLUTION_CANDIDATE", candidate))
        controller.submit(action("c2", "oppose", controller.phase, "RESOLUTION_CANDIDATE", candidate))
        controller.submit(action("cc1", "affirm", controller.phase, "COMMON_CORE_CONFIRM", {"response": "ACCEPT_COMMON_CORE"}))
        rejected = controller.submit(action("cc2", "oppose", controller.phase, "COMMON_CORE_CONFIRM", {"response": "REJECT_COMMON_CORE: A1 scope"}))
        self.assertTrue(rejected["accepted"])
        self.assertEqual(("__parent__", "COMMON_CORE_CORRECTION"), (controller.next_actor, controller.next_action))
        corrected = controller.submit(action("fix-core", "__parent__", controller.phase, "COMMON_CORE_CORRECTION", {
            "correction": {"atom_ids": ["A1"], "reason": "scope/source-map correction"},
        }))
        self.assertTrue(corrected["accepted"])
        self.assertEqual(
            ["decision"],
            [atom["field"] for atom in controller.resolution["common_atoms"]],
        )
        self.assertEqual(["A1"], [atom["id"] for atom in controller.resolution["reservations"]])
        correction_record = controller.resolution["common_core_corrections"][0]
        self.assertEqual(["A1", "A2"], [atom["id"] for atom in correction_record["before"]["common_atoms"]])
        self.assertEqual(["A2"], [atom["id"] for atom in correction_record["after"]["common_atoms"]])
        self.assertEqual(("affirm", "COMMON_CORE_CONFIRM"), (controller.next_actor, controller.next_action))
        controller.submit(action("cc3", "affirm", controller.phase, "COMMON_CORE_CONFIRM", {"response": "ACCEPT_COMMON_CORE"}))
        controller.submit(action("cc4", "oppose", controller.phase, "COMMON_CORE_CONFIRM", {"response": "ACCEPT_COMMON_CORE"}))
        self.assertEqual("CONSENSUS_WITH_RESERVATIONS", controller.terminal_status)
        self.assertEqual(1, controller.resolution["common_core_correction_count"])
        self.assertEqual(2, len(controller.common_core_confirmation_rounds))

    def test_no_op_common_core_correction_cannot_consume_the_retry(self):
        controller = self.make()
        self.through_update(controller, request=True)
        self.confirm_steelmans(controller)
        candidate = {"outcome": "CONSENSUS", "decision": "do X", "agreed_points": ["C1"]}
        controller.submit(action("c1", "affirm", controller.phase, "RESOLUTION_CANDIDATE", candidate))
        controller.submit(action("c2", "oppose", controller.phase, "RESOLUTION_CANDIDATE", candidate))
        controller.submit(action("cc1", "affirm", controller.phase, "COMMON_CORE_CONFIRM", {"response": "ACCEPT_COMMON_CORE"}))
        controller.submit(action("cc2", "oppose", controller.phase, "COMMON_CORE_CONFIRM", {"response": "REJECT_COMMON_CORE: A1 scope"}))
        no_op = controller.submit(action("no-op", "__parent__", controller.phase, "COMMON_CORE_CORRECTION", {"correction": {"atom_ids": []}}))
        self.assertFalse(no_op["accepted"])
        self.assertEqual("invalid_common_core_correction", no_op["reason"])
        self.assertEqual(0, controller.resolution["common_core_correction_count"])
        self.assertEqual(("__parent__", "COMMON_CORE_CORRECTION"), (controller.next_actor, controller.next_action))

    def test_corrupt_serialized_state_is_rejected_before_resume(self):
        controller = self.make()
        self.turn(controller, "o1", "affirm")
        for field, value, error in (
            ("phase", "NOT_A_PHASE", "invalid serialized phase"),
            ("next_actor", "missing", "invalid serialized next actor"),
            ("accepted_sequence", 7, "invalid serialized accepted sequence"),
        ):
            with self.subTest(field=field):
                state = controller.to_dict()
                state[field] = value
                with self.assertRaisesRegex(ValueError, error):
                    DebateController.from_dict(state, now=lambda: "2026-09-03T00:00:00Z")

        state = controller.to_dict()
        state["terminal_status"] = "FINAL_CONSENSUS"
        state["next_actor"] = None
        state["next_action"] = None
        with self.assertRaisesRegex(ValueError, "invalid serialized terminal status"):
            DebateController.from_dict(state, now=lambda: "2026-09-03T00:00:00Z")

        state = controller.to_dict()
        state["phase_speakers"]["OPENING"] = ["oppose", "affirm"]
        state["next_actor"] = "oppose"
        with self.assertRaisesRegex(ValueError, "invalid serialized speaker order"):
            DebateController.from_dict(state, now=lambda: "2026-09-03T00:00:00Z")

        state = controller.to_dict()
        del state["receipts"]["o1"]
        with self.assertRaisesRegex(ValueError, "invalid serialized receipts"):
            DebateController.from_dict(state, now=lambda: "2026-09-03T00:00:00Z")

        state = controller.to_dict()
        state["next_action"] = "RESOLUTION_CANDIDATE"
        with self.assertRaisesRegex(ValueError, "invalid serialized next action"):
            DebateController.from_dict(state, now=lambda: "2026-09-03T00:00:00Z")

        rejected_controller = self.make()
        self.turn(rejected_controller, "wrong", "oppose")
        state = rejected_controller.to_dict()
        del state["receipts"]["wrong"]
        with self.assertRaisesRegex(ValueError, "invalid serialized receipts"):
            DebateController.from_dict(state, now=lambda: "2026-09-03T00:00:00Z")

        state = self.make().to_dict()
        state["receipts"]["ghost"] = {
            "fingerprint": "not-a-real-envelope",
            "decision": {
                "accepted": True,
                "event_id": "ghost",
                "sequence": 777,
            },
        }
        with self.assertRaisesRegex(ValueError, "invalid serialized receipts"):
            DebateController.from_dict(state, now=lambda: "2026-09-03T00:00:00Z")

        state = controller.to_dict()
        state["receipts"]["o1"]["decision"]["next_actor"] = "ghost"
        with self.assertRaisesRegex(ValueError, "not derivable"):
            DebateController.from_dict(state, now=lambda: "2026-09-03T00:00:00Z")

        state = self.make().to_dict()
        state["phase"] = "RESOLUTION_CANDIDATE"
        state["next_actor"] = "affirm"
        state["next_action"] = "RESOLUTION_CANDIDATE"
        with self.assertRaisesRegex(ValueError, "not derivable"):
            DebateController.from_dict(state, now=lambda: "2026-09-03T00:00:00Z")

    def test_corrupt_serialized_terminal_classification_is_rejected(self):
        controller = self.make()
        self.through_update(controller, request=True)
        self.confirm_steelmans(controller)
        candidate = {"outcome": "DEADLOCK", "decision": "unresolved", "conflicts": ["C1"]}
        controller.submit(action("c1", "affirm", controller.phase, "RESOLUTION_CANDIDATE", candidate))
        controller.submit(action("c2", "oppose", controller.phase, "RESOLUTION_CANDIDATE", candidate))
        controller.submit(action("cc1", "affirm", controller.phase, "COMMON_CORE_CONFIRM", {"response": "ACCEPT_COMMON_CORE"}))
        controller.submit(action("cc2", "oppose", controller.phase, "COMMON_CORE_CONFIRM", {"response": "ACCEPT_COMMON_CORE"}))
        self.assertEqual("TRUE_DEADLOCK", controller.terminal_status)
        state = controller.to_dict()
        state["terminal_status"] = "FINAL_CONSENSUS"
        with self.assertRaisesRegex(ValueError, "invalid serialized terminal status"):
            DebateController.from_dict(state, now=lambda: "2026-09-03T00:00:00Z")

    def test_winner_confirmation_requires_a_matching_winner_candidate(self):
        controller = self.make()
        self.through_update(controller, request=True)
        self.confirm_steelmans(controller)
        candidate = {"outcome": "CONSENSUS", "decision": "do X", "agreed_points": ["C1"]}
        controller.submit(action("c1", "affirm", controller.phase, "RESOLUTION_CANDIDATE", candidate))
        controller.submit(action("c2", "oppose", controller.phase, "RESOLUTION_CANDIDATE", candidate))
        invalid = controller.submit(
            action(
                "cc-invalid",
                "affirm",
                controller.phase,
                "COMMON_CORE_CONFIRM",
                {"response": "ACCEPT_WINNER affirm"},
            )
        )
        self.assertFalse(invalid["accepted"])
        self.assertEqual("winner_not_proposed", invalid["reason"])
        self.assertEqual("affirm", controller.next_actor)

    def test_common_core_responses_require_source_mapped_atom_ids(self):
        controller = self.make()
        self.through_update(controller, request=True)
        self.confirm_steelmans(controller)
        first = {"outcome": "CONSENSUS_WITH_RESERVATIONS", "decision": "do X", "reservations": [{"text": "r", "claim_ids": ["C1"]}]}
        second = {"outcome": "CONSENSUS", "decision": "do X"}
        controller.submit(action("c1", "affirm", controller.phase, "RESOLUTION_CANDIDATE", first))
        controller.submit(action("c2", "oppose", controller.phase, "RESOLUTION_CANDIDATE", second))
        unknown_reservation = controller.submit(action("cc-r", "affirm", controller.phase, "COMMON_CORE_CONFIRM", {"response": "ACCEPT_WITH_RESERVATION: A999"}))
        self.assertFalse(unknown_reservation["accepted"])
        self.assertEqual("unknown_reservation", unknown_reservation["reason"])
        unknown_rejection = controller.submit(action("cc-x", "affirm", controller.phase, "COMMON_CORE_CONFIRM", {"response": "REJECT_COMMON_CORE: A999 mismatch"}))
        self.assertFalse(unknown_rejection["accepted"])
        self.assertEqual("invalid_common_core_rejection", unknown_rejection["reason"])
        self.assertEqual("affirm", controller.next_actor)

    def test_deadlock_candidates_cannot_become_consensus(self):
        controller = self.make()
        self.through_update(controller, request=True)
        self.confirm_steelmans(controller)
        candidate = {"outcome": "DEADLOCK", "decision": "unresolved", "conflicts": ["C1"]}
        controller.submit(action("c1", "affirm", controller.phase, "RESOLUTION_CANDIDATE", candidate))
        controller.submit(action("c2", "oppose", controller.phase, "RESOLUTION_CANDIDATE", candidate))
        controller.submit(action("cc1", "affirm", controller.phase, "COMMON_CORE_CONFIRM", {"response": "ACCEPT_COMMON_CORE"}))
        controller.submit(action("cc2", "oppose", controller.phase, "COMMON_CORE_CONFIRM", {"response": "ACCEPT_COMMON_CORE"}))
        self.assertEqual("TRUE_DEADLOCK", controller.terminal_status)

    def test_artifact_metadata_redacts_private_candidate_provenance(self):
        controller = self.make()
        self.through_update(controller, request=True)
        self.confirm_steelmans(controller)
        candidate = {"outcome": "DEADLOCK", "decision": "unresolved", "conflicts": ["C1"]}
        controller.submit(action("c1", "affirm", controller.phase, "RESOLUTION_CANDIDATE", candidate))
        public = controller.artifact_metadata()
        private = controller.artifact_metadata(include_private=True)
        public_event = next(event for event in public["events"] if event["event_id"] == "c1")
        private_event = next(event for event in private["events"] if event["event_id"] == "c1")
        self.assertEqual("anonymous", public_event["participant"])
        self.assertNotIn("submitted_by", json.dumps(public, ensure_ascii=False))
        self.assertEqual("affirm", private_event["participant"])

    def test_candidate_payload_cannot_embed_private_provenance(self):
        controller = self.make()
        self.through_update(controller, request=True)
        self.confirm_steelmans(controller)
        candidate = {
            "outcome": "DEADLOCK",
            "decision": "unresolved",
            "conflicts": [{"claim_id": "C1", "submitted_by": "affirm"}],
        }
        result = controller.submit(
            action("c-private", "affirm", controller.phase, "RESOLUTION_CANDIDATE", candidate)
        )
        self.assertFalse(result["accepted"])
        self.assertEqual("candidate_provenance_forbidden", result["reason"])
        self.assertEqual("affirm", controller.next_actor)

    def test_candidate_explicit_claim_references_must_exist(self):
        controller = self.make()
        self.through_update(controller, request=True)
        self.confirm_steelmans(controller)
        result = controller.submit(
            action(
                "c-ghost",
                "affirm",
                controller.phase,
                "RESOLUTION_CANDIDATE",
                {
                    "outcome": "CONSENSUS",
                    "decision": "do X",
                    "agreed_points": [{"text": "ghost", "claim_ids": ["C999"]}],
                },
            )
        )
        self.assertFalse(result["accepted"])
        self.assertEqual("invalid_candidate_claim_reference", result["reason"])
        self.assertEqual([], controller.resolution_candidates)

    def test_public_metadata_scrubs_rejected_candidate_provenance(self):
        controller = self.make()
        result = controller.submit(
            action(
                "early-private",
                "affirm",
                controller.phase,
                "RESOLUTION_CANDIDATE",
                {
                    "outcome": "DEADLOCK",
                    "decision": "unresolved",
                    "agreed_points": [{"submitted_by": "affirm", "text": "x"}],
                },
            )
        )
        self.assertFalse(result["accepted"])
        public = controller.artifact_metadata()
        self.assertNotIn("submitted_by", json.dumps(public, ensure_ascii=False))
        event = next(item for item in public["events"] if item["event_id"] == "early-private")
        self.assertEqual("anonymous", event["participant"])
        self.assertEqual([{"text": "x"}], event["payload"]["agreed_points"])

    def test_methodology_audit_is_controller_scheduled_after_new_evidence_link(self):
        controller = DebateController(
            "d-50",
            [
                {"id": "affirm", "role": "advocate"},
                {"id": "oppose", "role": "advocate"},
                {"id": "methods", "role": "auditor"},
            ],
            now=lambda: "2026-09-03T00:00:00Z",
        )
        self.turn(controller, "o1", "affirm", {"ledger_actions": [{"op": "ADD", "text": "A", "type": "fact", "falsifier": "x"}]})
        self.turn(controller, "o2", "oppose", {"ledger_actions": [{"op": "ADD", "text": "B", "type": "fact", "falsifier": "y"}]})
        self.turn(controller, "o3", "methods")
        self.turn(controller, "q1", "affirm", {"questions": [{"id": "Q1", "target": "oppose", "claim_id": "C1", "text": "why?"}]})
        self.turn(controller, "q2", "oppose", {"questions": [{"id": "Q2", "target": "affirm", "claim_id": "C2", "text": "why not?"}]})
        self.turn(controller, "r1", "affirm", {"answers": ["Q2"]})
        self.turn(controller, "r2", "oppose", {"answers": ["Q1"]})
        self.turn(controller, "r3", "methods")
        self.turn(controller, "u1", "affirm", {"steelman_target": "oppose", "steelman": "best B"})
        self.turn(controller, "u2", "oppose", {"steelman_target": "affirm", "steelman": "best A"})
        self.confirm_steelmans(controller)
        self.turn(controller, "d1", "affirm", {"evidence_links": [{"evidence_id": "E1", "claim_id": "C1", "directness": "high"}]})
        self.turn(controller, "d2", "oppose", {"no_material_change": True})
        self.assertEqual(
            ("METHODOLOGY_AUDIT", "methods", "METHODOLOGY_AUDIT"),
            (controller.phase, controller.next_actor, controller.next_action),
        )
        wrong = controller.submit(action("audit-wrong", "affirm", controller.phase, "METHODOLOGY_AUDIT"))
        self.assertFalse(wrong["accepted"])
        audited = controller.submit(action("audit", "methods", controller.phase, "METHODOLOGY_AUDIT", {"assessment": "link is direct"}))
        self.assertTrue(audited["accepted"])
        self.assertEqual(("CRUCIAL_DISPUTE", 2, "affirm"), (controller.phase, controller.cycle, controller.next_actor))
        restored = DebateController.from_json(controller.to_json(), now=lambda: "2026-09-03T00:00:00Z")
        self.assertEqual(controller.to_dict(), restored.to_dict())

    def test_safety_does_not_infer_deadlock_from_unconfirmed_string_difference(self):
        controller = self.make()
        self.through_update(controller, request=True)
        self.confirm_steelmans(controller)
        controller.submit(action("c1", "affirm", controller.phase, "RESOLUTION_CANDIDATE", {"outcome": "CONSENSUS", "decision": "do X"}))
        controller.submit(action("c2", "oppose", controller.phase, "RESOLUTION_CANDIDATE", {"outcome": "CONSENSUS", "decision": "do X "}))
        result = controller.submit(action("safety-string", "__parent__", controller.phase, "SAFETY_CEILING"))
        self.assertTrue(result["accepted"])
        self.assertEqual("INCOMPLETE", controller.terminal_status)

    def test_winner_and_equal_decision_are_source_mapped(self):
        controller = self.make()
        self.through_update(controller, request=True)
        self.confirm_steelmans(controller)
        candidate = {"outcome": "WINNER", "decision": "affirm wins", "winner": "affirm"}
        controller.submit(action("c1", "affirm", controller.phase, "RESOLUTION_CANDIDATE", candidate))
        controller.submit(action("c2", "oppose", controller.phase, "RESOLUTION_CANDIDATE", candidate))
        mapped = controller.resolution["source_map"].values()
        self.assertEqual({"decision", "winner"}, {atom["field"] for atom in mapped})
        self.assertTrue(all(atom["candidate_ids"] == ["R1", "R2"] for atom in mapped))

    def test_unanimous_winner_confirmation_can_resolve_initially_split_candidates(self):
        controller = self.make()
        self.through_update(controller, request=True)
        self.confirm_steelmans(controller)
        controller.submit(action("c1", "affirm", controller.phase, "RESOLUTION_CANDIDATE", {"outcome": "WINNER", "decision": "affirm wins", "winner": "affirm"}))
        controller.submit(action("c2", "oppose", controller.phase, "RESOLUTION_CANDIDATE", {"outcome": "WINNER", "decision": "oppose wins", "winner": "oppose"}))
        controller.submit(action("cc1", "affirm", controller.phase, "COMMON_CORE_CONFIRM", {"response": "ACCEPT_WINNER affirm"}))
        controller.submit(action("cc2", "oppose", controller.phase, "COMMON_CORE_CONFIRM", {"response": "ACCEPT_WINNER affirm"}))
        self.assertEqual("FINAL_WINNER", controller.terminal_status)

    def test_reclassified_operative_atom_cannot_produce_consensus_or_winner(self):
        for outcome, candidate, accept, reject, field in (
            (
                "consensus",
                {"outcome": "CONSENSUS", "decision": "do X"},
                "ACCEPT_COMMON_CORE",
                "REJECT_COMMON_CORE: {atom_id} decision mapping",
                "decision",
            ),
            (
                "winner",
                {"outcome": "WINNER", "decision": "affirm wins", "winner": "affirm"},
                "ACCEPT_WINNER affirm",
                "REJECT_WINNER: {atom_id} winner mapping",
                "winner",
            ),
        ):
            with self.subTest(outcome=outcome):
                controller = self.make()
                self.through_update(controller, request=True)
                self.confirm_steelmans(controller)
                controller.submit(action("c1", "affirm", controller.phase, "RESOLUTION_CANDIDATE", candidate))
                controller.submit(action("c2", "oppose", controller.phase, "RESOLUTION_CANDIDATE", candidate))
                atom_id = next(
                    atom["id"]
                    for atom in controller.resolution["common_atoms"]
                    if atom["field"] == field
                )
                reject = reject.format(atom_id=atom_id)
                controller.submit(action("cc1", "affirm", controller.phase, "COMMON_CORE_CONFIRM", {"response": accept}))
                controller.submit(action("cc2", "oppose", controller.phase, "COMMON_CORE_CONFIRM", {"response": reject}))
                controller.submit(action("fix", "__parent__", controller.phase, "COMMON_CORE_CORRECTION", {"correction": {"atom_ids": [atom_id], "reclassify_as": "conflicts"}}))
                controller.submit(action("cc3", "affirm", controller.phase, "COMMON_CORE_CONFIRM", {"response": accept}))
                controller.submit(action("cc4", "oppose", controller.phase, "COMMON_CORE_CONFIRM", {"response": accept}))
                self.assertEqual("TRUE_DEADLOCK", controller.terminal_status)

    def test_file_cli_initializes_submits_and_resumes_state(self):
        participants_path = Path("participants.json")
        action_path = Path("action.json")
        state_path = Path("state.json")
        participants = [
            {"id": "affirm", "role": "advocate"},
            {"id": "oppose", "role": "advocate"},
        ]
        with mock.patch("debate_controller._write_state") as write_state, mock.patch("builtins.print"):
            with mock.patch.object(Path, "read_text", return_value=json.dumps(participants)):
                self.assertEqual(0, main(["init", "--state", str(state_path), "--debate-id", "d-50", "--participants", str(participants_path)]))
            initial_state = write_state.call_args.args[1].to_json()
            with mock.patch.object(Path, "read_text", side_effect=[initial_state, json.dumps(action("o1", "affirm", "OPENING"))]):
                self.assertEqual(0, main(["submit", "--state", str(state_path), "--action", str(action_path)]))
        restored = write_state.call_args.args[1]
        self.assertEqual(1, restored.accepted_sequence)
        self.assertEqual("oppose", restored.next_actor)


if __name__ == "__main__":
    unittest.main()

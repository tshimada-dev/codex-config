"""Deterministic procedural controller for state-driven debates.

Argument text is deliberately opaque: this module only validates structured
envelopes and advances an auditable state machine.  It never invokes models,
agents, or tools.
"""

from __future__ import annotations

import copy
import datetime as _datetime
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional


SCHEMA_VERSION = 1
NORMAL_PHASES = ("OPENING", "CROSS_EXAM", "RESPONSE", "UPDATE", "CRUCIAL_DISPUTE")
CLAIM_STATUSES = {
    "proposed", "agreed", "disputed", "unsupported", "definitional_dispute", "superseded",
}


def _utc_now() -> str:
    return _datetime.datetime.now(_datetime.timezone.utc).isoformat().replace("+00:00", "Z")


def _fingerprint(envelope: Dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(envelope, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _envelope_fingerprint(envelope: Dict[str, Any]) -> str:
    return _fingerprint(
        {
            key: envelope.get(key)
            for key in (
                "debate_id",
                "event_id",
                "actor",
                "action_type",
                "phase",
                "payload",
            )
        }
    )


_PROVENANCE_KEYS = {"submitted_by", "participant", "actor", "camp"}


def _contains_provenance(value: Any) -> bool:
    if isinstance(value, dict):
        return any(
            key in _PROVENANCE_KEYS or _contains_provenance(child)
            for key, child in value.items()
        )
    if isinstance(value, list):
        return any(_contains_provenance(child) for child in value)
    return False


def _strip_provenance(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _strip_provenance(child)
            for key, child in value.items()
            if key not in _PROVENANCE_KEYS
        }
    if isinstance(value, list):
        return [_strip_provenance(child) for child in value]
    return copy.deepcopy(value)


class DebateController:
    """A serialized, single-writer debate state machine.

    ``submit`` returns a stable decision dictionary.  Retrying the exact same
    event envelope returns the original dictionary; reusing its ID with a
    different envelope is rejected.  ``to_json`` / ``from_json`` are the
    resume boundary, so no transcript interpretation is required.
    """

    def __init__(
        self,
        debate_id: str,
        participants: Iterable[Dict[str, Any]],
        *,
        emergency_safety: Optional[Dict[str, Any]] = None,
        now: Optional[Callable[[], str]] = None,
    ) -> None:
        participants = [copy.deepcopy(p) for p in participants]
        if not debate_id or not participants:
            raise ValueError("debate_id and participants are required")
        ids = [p.get("id") for p in participants]
        if any(not isinstance(p, str) or not p for p in ids) or len(set(ids)) != len(ids):
            raise ValueError("participants require unique non-empty IDs")
        if "__parent__" in ids:
            raise ValueError("participant ID __parent__ is reserved")
        if any(p.get("role") not in {"advocate", "auditor"} for p in participants):
            raise ValueError("participant role must be advocate or auditor")
        advocates = [p["id"] for p in participants if p["role"] == "advocate"]
        auditors = [p["id"] for p in participants if p["role"] == "auditor"]
        if not 2 <= len(advocates) <= 4:
            raise ValueError("two to four advocates are required")
        if len(auditors) > 1:
            raise ValueError("at most one auditor is allowed")
        self._now = now or _utc_now
        self.schema_version = SCHEMA_VERSION
        self.debate_id = debate_id
        self.participants = participants
        self.phase_speakers = {
            "OPENING": advocates + auditors,
            "CROSS_EXAM": advocates[:],
            "RESPONSE": advocates + auditors,
            "UPDATE": advocates[:],
            "CRUCIAL_DISPUTE": advocates[:],
        }
        config = {"event_limit": 10000, "time_limit_seconds": None, "started_at": self._now()}
        config.update(copy.deepcopy(emergency_safety or {}))
        self._validate_emergency_safety(config)
        self.emergency_safety = config
        self.phase = "OPENING"
        self.cycle = 0
        self._turn_index = 0
        self.next_actor = self.phase_speakers[self.phase][0]
        self.next_action = "TURN"
        self.accepted_sequence = 0
        self.accepted_events: List[Dict[str, Any]] = []
        self.events: List[Dict[str, Any]] = []
        self.receipts: Dict[str, Dict[str, Any]] = {}
        self.claim_ledger: List[Dict[str, Any]] = []
        self.questions: List[Dict[str, Any]] = []
        self.responses: List[Dict[str, Any]] = []
        self.steelmans: List[Dict[str, Any]] = []
        self.evidence_link_events: List[Dict[str, Any]] = []
        self.progress_markers: List[Dict[str, Any]] = []
        self.resolution_candidates: List[Dict[str, Any]] = []
        self.common_core_confirmations: List[Dict[str, Any]] = []
        self.common_core_confirmation_rounds: List[List[Dict[str, Any]]] = []
        self.resolution: Dict[str, Any] = {}
        self.terminal_status: Optional[str] = None
        self._crucial_material = []
        self._consecutive_no_progress = 0
        self._conclusions: Dict[str, str] = {}
        self._unanimous_checkpoint = False
        self._methodology_audit_needed = False
        self._post_audit_transition: Optional[str] = None
        self._load_after_init = False

    @property
    def advocates(self) -> List[str]:
        return [p["id"] for p in self.participants if p["role"] == "advocate"]

    @property
    def auditor(self) -> Optional[str]:
        return next(
            (p["id"] for p in self.participants if p["role"] == "auditor"),
            None,
        )

    @property
    def state(self) -> Dict[str, Any]:
        return self.to_dict()

    def submit(self, envelope: Dict[str, Any]) -> Dict[str, Any]:
        """Apply one structured event, returning a stable accepted/rejected receipt."""
        if not isinstance(envelope, dict):
            return self._ephemeral_reject(None, "invalid_envelope")
        event_id = envelope.get("event_id")
        if not isinstance(event_id, str) or not event_id:
            return self._ephemeral_reject(None, "invalid_event_id")
        fingerprint = _envelope_fingerprint(envelope)
        existing = self.receipts.get(event_id)
        if existing:
            if existing["fingerprint"] == fingerprint:
                self.events.append(
                    self._event_record(envelope, False, "duplicate_delivery", None)
                )
                return copy.deepcopy(existing["decision"])
            self.events.append(
                self._event_record(envelope, False, "conflicting_event_id", None)
            )
            return self._ephemeral_reject(event_id, "conflicting_event_id")

        base_error = self._validate_envelope(envelope)
        if base_error:
            return self._record_reject(event_id, fingerprint, envelope, base_error)
        if self.terminal_status:
            return self._record_reject(event_id, fingerprint, envelope, "terminal_state")
        if envelope["action_type"] in {"CANCEL", "FAILURE"}:
            self.terminal_status = "INCOMPLETE"
            self.next_actor, self.next_action = None, None
            return self._accept(event_id, fingerprint, envelope, self.phase, self.cycle)
        if envelope["action_type"] == "SAFETY_CEILING":
            self.terminal_status = (
                "TRUE_DEADLOCK" if self._formal_deadlock_evidence() else "INCOMPLETE"
            )
            self.next_actor, self.next_action = None, None
            return self._accept(event_id, fingerprint, envelope, self.phase, self.cycle)
        if self._safety_reached():
            self.terminal_status = "TRUE_DEADLOCK" if self._formal_deadlock_evidence() else "INCOMPLETE"
            self.next_actor, self.next_action = None, None
            return self._record_reject(event_id, fingerprint, envelope, "emergency_safety_ceiling")
        if envelope["phase"] != self.phase:
            return self._record_reject(event_id, fingerprint, envelope, "out_of_phase")
        if envelope["actor"] != self.next_actor:
            return self._record_reject(event_id, fingerprint, envelope, "wrong_actor")

        event_phase, event_cycle = self.phase, self.cycle
        # Handlers can update several ledger structures.  An invalid envelope
        # must be observationally harmless, so roll all such work back before
        # recording its rejected receipt/audit row.
        snapshot = copy.deepcopy(self.__dict__)
        error = self._apply(envelope)
        if error:
            self.__dict__.clear()
            self.__dict__.update(snapshot)
            return self._record_reject(event_id, fingerprint, envelope, error)
        return self._accept(event_id, fingerprint, envelope, event_phase, event_cycle)

    def _validate_envelope(self, event: Dict[str, Any]) -> Optional[str]:
        required = ("debate_id", "event_id", "actor", "action_type", "phase", "payload")
        if any(k not in event for k in required):
            return "missing_envelope_field"
        if event["debate_id"] != self.debate_id:
            return "wrong_debate_id"
        participant_ids = {p["id"] for p in self.participants}
        parent_actions = {"CANCEL", "FAILURE", "SAFETY_CEILING", "COMMON_CORE_CORRECTION"}
        if event["actor"] == "__parent__":
            if event["action_type"] not in parent_actions:
                return "parent_action_not_allowed"
        elif event["actor"] not in participant_ids:
            return "unknown_actor"
        elif event["action_type"] in parent_actions:
            return "parent_action_required"
        if not isinstance(event["payload"], dict):
            return "invalid_payload"
        return None

    def _apply(self, event: Dict[str, Any]) -> Optional[str]:
        if self.phase in NORMAL_PHASES:
            allowed = {"TURN", "STATEMENT", self.phase}
            if event["action_type"] not in allowed:
                return "wrong_action_type"
            return self._apply_turn(event)
        if self.phase == "STEELMAN_CONFIRMATION":
            return self._apply_steelman(event)
        if self.phase == "METHODOLOGY_AUDIT":
            return self._apply_methodology_audit(event)
        if self.phase == "RESOLUTION_CANDIDATE":
            if event["action_type"] != "RESOLUTION_CANDIDATE":
                return "wrong_action_type"
            return self._apply_candidate(event)
        if self.phase == "COMMON_CORE_CONFIRMATION":
            return self._apply_common_core(event)
        return "invalid_phase"

    def _apply_turn(self, event: Dict[str, Any]) -> Optional[str]:
        payload = event["payload"]
        progress_before = (
            self._progress_signature()
            if self.phase == "CRUCIAL_DISPUTE"
            else None
        )
        if self.phase == "CROSS_EXAM":
            questions = payload.get("questions")
            if questions is None and payload.get("question"):
                questions = [payload["question"]]
            if not isinstance(questions, list) or len(questions) != 1:
                return "cross_exam_question_required"
            for question in questions:
                if not isinstance(question, dict) or not all(question.get(k) for k in ("id", "target", "claim_id", "text")):
                    return "invalid_question"
                if question["target"] not in self.advocates or question["target"] == event["actor"]:
                    return "invalid_question_target"
                if self._claim(question["claim_id"]) is None:
                    return "unknown_question_claim"
                if question["id"] in {q["id"] for q in self.questions}:
                    return "duplicate_question_id"
                self.questions.append({"id": question["id"], "target": question["target"], "claim_id": question["claim_id"], "text": question["text"], "asked_by": event["actor"], "status": "open"})
        if self.phase == "RESPONSE":
            required = [q["id"] for q in self.questions if q["target"] == event["actor"] and q["status"] == "open"]
            answers = payload.get("answers", [])
            if isinstance(answers, dict):
                answers = list(answers)
            if not isinstance(answers, list) or not set(required).issubset(set(answers)):
                return "missing_required_answers"
            for question in self.questions:
                if question["id"] in answers and question["target"] == event["actor"]:
                    question["status"] = "answered"
                    question["answered_by"] = event["actor"]
                    self.responses.append({"question_id": question["id"], "actor": event["actor"], "event_id": event["event_id"], "response": copy.deepcopy(payload.get("response_text", payload.get("direct_answer", payload.get("answers"))))})
        if self.phase == "UPDATE":
            if payload.get("steelman_target") not in self.advocates or payload.get("steelman_target") == event["actor"]:
                return "steelman_target_required"
            if not isinstance(payload.get("steelman"), str) or not payload["steelman"]:
                return "steelman_text_required"
            self.steelmans.append({"author": event["actor"], "target": payload["steelman_target"], "text": payload["steelman"], "status": "pending", "corrections": 0, "event_id": event["event_id"]})
            self._unanimous_checkpoint = self._unanimous_checkpoint and bool(payload.get("request_resolution")) if self._turn_index else bool(payload.get("request_resolution"))
        if self.phase == "CRUCIAL_DISPUTE":
            conclusion = payload.get("operative_conclusion")
            if payload.get("conclusion_agreed") and isinstance(conclusion, str) and conclusion:
                self._conclusions[event["actor"]] = conclusion
            else:
                self._conclusions.pop(event["actor"], None)
            if self._turn_index == 0:
                self._unanimous_checkpoint = bool(payload.get("request_resolution"))
            else:
                self._unanimous_checkpoint = self._unanimous_checkpoint and bool(payload.get("request_resolution"))
        error = self._apply_ledger(payload, event)
        if error:
            return error
        for link in payload.get("evidence_links", []):
            if not isinstance(link, dict):
                return "invalid_evidence_link"
            if self._claim(link.get("claim_id")) is None:
                return "unknown_evidence_link_claim"
            record = copy.deepcopy(link)
            record.update({"event_id": event["event_id"], "participant": event["actor"], "phase": self.phase, "cycle": self.cycle})
            semantic_link = {
                key: value
                for key, value in record.items()
                if key not in {"event_id", "phase", "cycle"}
            }
            if not any(
                {
                    key: value
                    for key, value in existing.items()
                    if key not in {"event_id", "phase", "cycle"}
                }
                == semantic_link
                for existing in self.evidence_link_events
            ):
                self.evidence_link_events.append(record)
                if self.phase == "CRUCIAL_DISPUTE" and self.auditor:
                    self._methodology_audit_needed = True
        if self.phase == "CRUCIAL_DISPUTE":
            marker_error = self._record_progress_markers(payload, event["actor"])
            if marker_error:
                return marker_error
            # ``material_progress`` is an assertion, not evidence.  A cycle
            # continues only when durable structured state actually changes,
            # or when a concrete forecast/falsifier update is supplied.
            material = progress_before != self._progress_signature()
            if payload.get("no_material_change") and material:
                return "contradictory_progress_signal"
            self._crucial_material.append(material)
        return self._advance_normal()

    def _apply_ledger(self, payload: Dict[str, Any], event: Dict[str, Any]) -> Optional[str]:
        actions = payload.get("ledger_actions", [])
        if not isinstance(actions, list):
            return "invalid_ledger_actions"
        for action in actions:
            if not isinstance(action, dict):
                return "invalid_ledger_action"
            op = str(action.get("op", "")).upper()
            if op == "ADD":
                if not isinstance(action.get("text"), str) or not action["text"]:
                    return "claim_text_required"
                claim_type = action.get("type", "inference")
                if claim_type not in {"fact", "inference", "definition", "value", "prediction"}:
                    return "invalid_claim_type"
                condition = action.get(
                    "falsifier", action.get("revision_condition")
                )
                if not isinstance(condition, str) or not condition:
                    return "claim_revision_condition_required"
                duplicate = next(
                    (
                        claim
                        for claim in self.claim_ledger
                        if claim.get("text") == action["text"]
                        and claim.get("type") == claim_type
                        and claim.get("evidence", []) == action.get("evidence", [])
                        and claim.get("falsifier")
                        == condition
                    ),
                    None,
                )
                if duplicate is not None:
                    continue
                claim = {"id": "C%d" % (len(self.claim_ledger) + 1), "text": action["text"], "type": claim_type, "status": "proposed", "evidence": copy.deepcopy(action.get("evidence", [])), "falsifier": condition, "introduced_by": event["actor"], "event_id": event["event_id"], "relations": {event["actor"]: "accept"}}
                self.claim_ledger.append(claim)
            elif op == "SET_STATUS":
                return "controller_owned_claim_status"
            elif op in {
                "ACCEPT",
                "CHALLENGE",
                "REFINE",
                "CONCEDE",
                "UNSUPPORTED",
                "DEFINITIONAL_DISPUTE",
                "SUPERSEDE",
            }:
                claim = self._claim(action.get("claim_id"))
                if claim is None:
                    return "unknown_claim"
                relations = claim.setdefault("relations", {})
                relations[event["actor"]] = op.lower()
                if op == "CHALLENGE":
                    claim["status"] = "disputed"
                if op == "REFINE" and action.get("text"):
                    refinement = {"by": event["actor"], "text": action["text"]}
                    if refinement not in claim.setdefault("refinements", []):
                        claim["refinements"].append(refinement)
                if op == "UNSUPPORTED":
                    if claim.get("type") not in {"fact", "inference", "prediction"}:
                        return "unsupported_status_requires_empirical_claim"
                    if all(
                        relations.get(advocate) == "unsupported"
                        for advocate in self.advocates
                    ):
                        claim["status"] = "unsupported"
                if op == "DEFINITIONAL_DISPUTE":
                    claim["status"] = "definitional_dispute"
                if op == "SUPERSEDE":
                    replacement_id = action.get("replacement_claim_id")
                    if replacement_id == claim["id"] or self._claim(replacement_id) is None:
                        return "invalid_superseding_claim"
                    relations[event["actor"]] = "supersede:%s" % replacement_id
                    if all(
                        relations.get(advocate) == "supersede:%s" % replacement_id
                        for advocate in self.advocates
                    ):
                        claim["status"] = "superseded"
                        claim["superseded_by"] = replacement_id
                if op in {"ACCEPT", "CONCEDE"} and all(
                    relations.get(advocate) in {"accept", "concede"}
                    for advocate in self.advocates
                ):
                    claim["status"] = "agreed"
            elif op in {"", "NO_NEW_ACTION", "QUESTION", "ANSWER"}:
                continue
            else:
                return "unknown_ledger_action"
        return None

    def _claim(self, claim_id: Any) -> Optional[Dict[str, Any]]:
        return next((c for c in self.claim_ledger if c["id"] == claim_id), None)

    def _record_progress_markers(
        self, payload: Dict[str, Any], actor: str
    ) -> Optional[str]:
        markers: List[Dict[str, Any]] = []
        for field in ("next_falsifier", "next_refinement", "answer"):
            value = payload.get(field)
            if isinstance(value, str) and value:
                markers.append({"participant": actor, "kind": field, "value": value})
        shift = payload.get("forecast_probability_shift", payload.get("forecast_shift"))
        if shift is not None:
            probability = payload.get("forecast_probability")
            if (
                isinstance(shift, bool)
                or not isinstance(shift, (int, float))
                or not math.isfinite(float(shift))
                or isinstance(probability, bool)
                or not isinstance(probability, (int, float))
                or not math.isfinite(float(probability))
                or not 0 <= float(probability) <= 1
            ):
                return "invalid_forecast_progress"
        if shift is not None and abs(float(shift)) >= 0.05:
            markers.append(
                {
                    "participant": actor,
                    "kind": "forecast_probability",
                    "value": float(payload["forecast_probability"]),
                }
            )
        for marker in markers:
            if marker not in self.progress_markers:
                self.progress_markers.append(marker)
        return None

    def _progress_signature(self) -> str:
        return _fingerprint(
            {
                "claim_ledger": self.claim_ledger,
                "evidence_link_events": self.evidence_link_events,
                "progress_markers": self.progress_markers,
            }
        )

    def _advance_normal(self) -> Optional[str]:
        speakers = self.phase_speakers[self.phase]
        if self._turn_index + 1 < len(speakers):
            self._turn_index += 1
            self.next_actor = speakers[self._turn_index]
            return None
        if self.phase == "OPENING":
            self._enter_phase("CROSS_EXAM")
        elif self.phase == "CROSS_EXAM":
            self._enter_phase("RESPONSE")
        elif self.phase == "RESPONSE":
            self._enter_phase("UPDATE")
        elif self.phase == "UPDATE":
            self.phase = "STEELMAN_CONFIRMATION"
            self._turn_index = 0
            first = self.steelmans[0]
            self.next_actor, self.next_action = first["target"], "STEELMAN_CONFIRM"
        else:
            if self._unanimous_crucial_request() or self._operative_agreement():
                transition = "RESOLUTION"
            elif not any(self._crucial_material):
                self._consecutive_no_progress += 1
                if self._consecutive_no_progress >= 2:
                    transition = "RESOLUTION"
                else:
                    transition = "NEXT_CRUCIAL"
            else:
                self._consecutive_no_progress = 0
                transition = "NEXT_CRUCIAL"
            self._schedule_post_crucial(transition)
        return None

    def _schedule_post_crucial(self, transition: str) -> None:
        if self._methodology_audit_needed and self.auditor:
            self.phase = "METHODOLOGY_AUDIT"
            self._turn_index = 0
            self.next_actor = self.auditor
            self.next_action = "METHODOLOGY_AUDIT"
            self._post_audit_transition = transition
            self._methodology_audit_needed = False
            return
        self._apply_post_crucial_transition(transition)

    def _apply_methodology_audit(self, event: Dict[str, Any]) -> Optional[str]:
        if event["action_type"] != "METHODOLOGY_AUDIT":
            return "wrong_action_type"
        if event["actor"] != self.auditor:
            return "wrong_methodology_auditor"
        transition = self._post_audit_transition
        if transition not in {"RESOLUTION", "NEXT_CRUCIAL"}:
            return "invalid_methodology_audit_transition"
        self._post_audit_transition = None
        self._apply_post_crucial_transition(transition)
        return None

    def _apply_post_crucial_transition(self, transition: str) -> None:
        if transition == "RESOLUTION":
            self._enter_resolution()
        elif transition == "NEXT_CRUCIAL":
            self._next_crucial_cycle()
        else:
            raise ValueError("invalid post-crucial transition")

    def _enter_phase(self, phase: str) -> None:
        self.phase = phase
        self._turn_index = 0
        self.next_actor = self.phase_speakers[phase][0]
        self.next_action = "TURN"

    def _apply_steelman(self, event: Dict[str, Any]) -> Optional[str]:
        pending = next((s for s in self.steelmans if s["status"] == "needs_correction"), None)
        if pending is None:
            pending = next((s for s in self.steelmans if s["status"] in {"pending", "awaiting_confirmation"}), None)
        if pending is None:
            return "no_pending_steelman"
        if event["action_type"] == "STEELMAN_CONFIRM":
            if event["actor"] != pending["target"]:
                return "wrong_steelman_confirmer"
            accepted = event["payload"].get("accepted")
            if not isinstance(accepted, bool):
                return "steelman_confirmation_required"
            if accepted:
                pending["status"] = "accepted"
                return self._advance_steelman()
            if pending["corrections"] >= 1:
                # The permitted correction has already had its independent
                # re-confirmation.  Record the procedural defect and move on;
                # it blocks direct resolution but cannot deadlock the ring.
                pending["status"] = "rejected"
                return self._advance_steelman()
            pending["status"] = "needs_correction"
            self.next_actor, self.next_action = pending["author"], "STEELMAN_CORRECTION"
            return None
        if event["action_type"] == "STEELMAN_CORRECTION":
            if pending["status"] != "needs_correction" or event["actor"] != pending["author"]:
                return "unexpected_steelman_correction"
            if pending["corrections"] >= 1:
                return "steelman_correction_limit"
            text = event["payload"].get("steelman")
            if not isinstance(text, str) or not text:
                return "steelman_text_required"
            pending["text"] = text
            pending["corrections"] += 1
            pending["status"] = "awaiting_confirmation"
            self.next_actor, self.next_action = pending["target"], "STEELMAN_CONFIRM"
            return None
        return "wrong_action_type"

    def _advance_steelman(self) -> Optional[str]:
        pending = next((s for s in self.steelmans if s["status"] in {"pending", "awaiting_confirmation"}), None)
        if pending:
            self.next_actor, self.next_action = pending["target"], "STEELMAN_CONFIRM"
            return None
        if self._unanimous_checkpoint and all(s["status"] == "accepted" for s in self.steelmans):
            self._enter_resolution()
        else:
            self._next_crucial_cycle()
        return None

    def _next_crucial_cycle(self) -> None:
        self.phase = "CRUCIAL_DISPUTE"
        self.cycle += 1
        self._turn_index = 0
        self.next_actor = self.phase_speakers[self.phase][0]
        self.next_action = "TURN"
        self._crucial_material = []
        self._conclusions = {}

    def _unanimous_crucial_request(self) -> bool:
        # Recorded as an explicit checkpoint flag only when every turn supplied it.
        return self._unanimous_checkpoint and len(self._crucial_material) == len(self.advocates)

    def _operative_agreement(self) -> bool:
        return len(self._conclusions) == len(self.advocates) and len(set(self._conclusions.values())) == 1

    def _enter_resolution(self) -> None:
        self.phase = "RESOLUTION_CANDIDATE"
        self._turn_index = 0
        self.next_actor = self.advocates[0]
        self.next_action = "RESOLUTION_CANDIDATE"

    def _apply_candidate(self, event: Dict[str, Any]) -> Optional[str]:
        candidate = copy.deepcopy(event["payload"])
        if _contains_provenance(candidate):
            return "candidate_provenance_forbidden"
        if candidate.get("outcome") not in {
            "CONSENSUS",
            "CONSENSUS_WITH_RESERVATIONS",
            "WINNER",
            "DEADLOCK",
        } or not isinstance(candidate.get("decision"), str) or not candidate["decision"]:
            return "invalid_resolution_candidate"
        winner = candidate.get("winner")
        if candidate["outcome"] == "WINNER":
            if winner not in self.advocates:
                return "invalid_winner_candidate"
        elif winner not in {None, "NONE"}:
            return "unexpected_winner"
        for field in ("agreed_points", "reservations", "conflicts"):
            if field in candidate and not isinstance(candidate[field], list):
                return "invalid_resolution_candidate"
            if any(
                not self._valid_candidate_claim_references(value)
                for value in candidate.get(field, [])
            ):
                return "invalid_candidate_claim_reference"
        candidate.update({"submitted_by": event["actor"], "event_id": event["event_id"]})
        self.resolution_candidates.append(candidate)
        if self._turn_index + 1 < len(self.advocates):
            self._turn_index += 1
            self.next_actor = self.advocates[self._turn_index]
            return None
        self.resolution_candidates.sort(key=lambda c: _fingerprint({k: v for k, v in c.items() if k not in {"submitted_by", "event_id"}}))
        for index, candidate in enumerate(self.resolution_candidates, 1):
            candidate["candidate_id"] = "R%d" % index
        decisions = {c["decision"] for c in self.resolution_candidates}
        proposed_winners = sorted(
            {c["winner"] for c in self.resolution_candidates if c["outcome"] == "WINNER"}
        )
        mapping = self._build_common_core_mapping()
        self.resolution = {
            "common_decision": next(iter(decisions)) if len(decisions) == 1 else None,
            "candidate_ids": [c["candidate_id"] for c in self.resolution_candidates],
            "proposed_winners": proposed_winners,
            "winner_confirmation_required": bool(proposed_winners),
            "common_atoms": mapping["common_atoms"],
            "reservations": mapping["reservations"],
            "conflicts": mapping["conflicts"],
            "source_map": mapping["source_map"],
            "common_core_correction_count": 0,
            "common_core_corrections": [],
        }
        self.phase = "COMMON_CORE_CONFIRMATION"
        self._turn_index = 0
        self.next_actor = self.advocates[0]
        self.next_action = "COMMON_CORE_CONFIRM"
        return None

    def _apply_common_core(self, event: Dict[str, Any]) -> Optional[str]:
        if event["action_type"] == "COMMON_CORE_CORRECTION":
            correction = event["payload"].get("correction")
            if (
                event["actor"] != "__parent__"
                or self.next_action != "COMMON_CORE_CORRECTION"
                or self.resolution.get("common_core_correction_count", 0) >= 1
                or not isinstance(correction, dict)
            ):
                return "common_core_correction_unavailable"
            atom_ids = correction.get("atom_ids", [])
            destination = correction.get("reclassify_as", "reservations")
            common_atom_ids = {
                atom["id"] for atom in self.resolution.get("common_atoms", [])
            }
            if (
                not isinstance(atom_ids, list)
                or not atom_ids
                or len(set(atom_ids)) != len(atom_ids)
                or set(atom_ids)
                != set(
                    self.resolution.get(
                        "pending_common_core_rejection_atom_ids", []
                    )
                )
                or destination not in {"reservations", "conflicts"}
                or any(
                    not isinstance(atom_id, str)
                    or atom_id not in self.resolution.get("source_map", {})
                    or atom_id not in common_atom_ids
                    for atom_id in atom_ids
                )
            ):
                return "invalid_common_core_correction"
            before = {
                field: copy.deepcopy(self.resolution.get(field, []))
                for field in ("common_atoms", "reservations", "conflicts")
            }
            moved = [
                atom for atom in self.resolution["common_atoms"] if atom["id"] in atom_ids
            ]
            self.resolution["common_atoms"] = [
                atom for atom in self.resolution["common_atoms"] if atom["id"] not in atom_ids
            ]
            self.resolution[destination].extend(copy.deepcopy(moved))
            self.resolution[destination].sort(key=lambda atom: atom["id"])
            after = {
                field: copy.deepcopy(self.resolution.get(field, []))
                for field in ("common_atoms", "reservations", "conflicts")
            }
            self.common_core_confirmation_rounds.append(
                copy.deepcopy(self.common_core_confirmations)
            )
            self.common_core_confirmations = []
            self.resolution["common_core_correction_count"] += 1
            self.resolution["common_core_corrections"].append(
                {
                    "event_id": event["event_id"],
                    "correction": copy.deepcopy(correction),
                    "before": before,
                    "after": after,
                }
            )
            self.resolution.pop("pending_common_core_rejections", None)
            self.resolution.pop("pending_common_core_rejection_atom_ids", None)
            self._turn_index = 0
            self.next_actor, self.next_action = self.advocates[0], "COMMON_CORE_CONFIRM"
            return None
        if event["action_type"] != "COMMON_CORE_CONFIRM":
            return "wrong_action_type"
        response = event["payload"].get("response")
        if not isinstance(response, str) or not response:
            return "common_core_response_required"
        winner_required = bool(self.resolution.get("winner_confirmation_required"))
        referenced_atom_id: Optional[str] = None
        if response.startswith("ACCEPT_WINNER "):
            winner = response.split(" ", 1)[1]
            if not winner_required or winner not in self.resolution.get("proposed_winners", []):
                return "winner_not_proposed"
        elif response.startswith("REJECT_WINNER"):
            if not winner_required:
                return "winner_not_proposed"
            referenced_atom_id = self._rejection_atom_id(
                response, "REJECT_WINNER:"
            )
            atom = self.resolution.get("source_map", {}).get(referenced_atom_id)
            if atom is None or atom.get("field") != "winner":
                return "invalid_winner_rejection"
        elif response == "ACCEPT_COMMON_CORE":
            if winner_required:
                return "winner_confirmation_required"
        elif response.startswith("ACCEPT_WITH_RESERVATION:"):
            if winner_required:
                return "winner_confirmation_required"
            reservation_id = response.split(":", 1)[1].strip()
            if reservation_id not in {
                atom["id"] for atom in self.resolution.get("reservations", [])
            }:
                return "unknown_reservation"
        elif response.startswith("REJECT_COMMON_CORE:"):
            if winner_required:
                return "winner_confirmation_required"
            referenced_atom_id = self._rejection_atom_id(
                response, "REJECT_COMMON_CORE:"
            )
            if referenced_atom_id not in {
                atom["id"] for atom in self.resolution.get("common_atoms", [])
            }:
                return "invalid_common_core_rejection"
        else:
            return "invalid_common_core_response"
        self.common_core_confirmations.append({"participant": event["actor"], "response": response, "event_id": event["event_id"], "referenced_atom_id": referenced_atom_id})
        if self._turn_index + 1 < len(self.advocates):
            self._turn_index += 1
            self.next_actor = self.advocates[self._turn_index]
            return None
        responses = [x["response"] for x in self.common_core_confirmations]
        rejected_confirmations = [
            confirmation
            for confirmation in self.common_core_confirmations
            if confirmation["response"].startswith("REJECT")
        ]
        correctable_atom_ids = {
            atom["id"] for atom in self.resolution.get("common_atoms", [])
        }
        correction_eligible = rejected_confirmations and all(
            confirmation.get("referenced_atom_id") in correctable_atom_ids
            for confirmation in rejected_confirmations
        )
        if correction_eligible and self.resolution.get("common_core_correction_count", 0) < 1:
            rejected = [
                confirmation["response"]
                for confirmation in rejected_confirmations
            ]
            self.resolution["pending_common_core_rejections"] = rejected
            self.resolution["pending_common_core_rejection_atom_ids"] = sorted(
                {
                    confirmation["referenced_atom_id"]
                    for confirmation in rejected_confirmations
                }
            )
            self.next_actor, self.next_action = "__parent__", "COMMON_CORE_CORRECTION"
            return None
        self.terminal_status = self._classify_resolution_responses(responses)
        self.common_core_confirmation_rounds.append(
            copy.deepcopy(self.common_core_confirmations)
        )
        self.next_actor, self.next_action = None, None
        return None

    @staticmethod
    def _rejection_atom_id(response: str, prefix: str) -> Optional[str]:
        if not response.startswith(prefix):
            return None
        parts = response[len(prefix):].strip().split(maxsplit=1)
        if len(parts) != 2 or not parts[0] or not parts[1]:
            return None
        return parts[0]

    def _classify_resolution_responses(self, responses: List[str]) -> str:
        winner_values = [
            response.split(" ", 1)[1]
            for response in responses
            if response.startswith("ACCEPT_WINNER ")
        ]
        if (
            len(winner_values) == len(self.advocates)
            and len(set(winner_values)) == 1
            and winner_values[0] in self.resolution.get("proposed_winners", [])
            and not self._operative_atom_was_reclassified(
                "winner", winner_values[0]
            )
        ):
            return "FINAL_WINNER"
        if (
            all(
                response == "ACCEPT_COMMON_CORE"
                or response.startswith("ACCEPT_WITH_RESERVATION:")
                for response in responses
            )
            and self.resolution.get("common_decision")
            and self._has_common_resolution_atom(
                "decision", self.resolution.get("common_decision")
            )
            and all(
                candidate["outcome"]
                in {"CONSENSUS", "CONSENSUS_WITH_RESERVATIONS"}
                for candidate in self.resolution_candidates
            )
        ):
            reserved = (
                any(response != "ACCEPT_COMMON_CORE" for response in responses)
                or any(candidate.get("reservations") for candidate in self.resolution_candidates)
                or bool(self.resolution.get("reservations"))
            )
            return "CONSENSUS_WITH_RESERVATIONS" if reserved else "FINAL_CONSENSUS"
        if (
            any(response.startswith("REJECT") for response in responses)
            or self.resolution.get("common_decision") is None
            or any(
                atom.get("field") in {"decision", "winner"}
                for atom in self.resolution.get("conflicts", [])
            )
            or any(
                candidate["outcome"] == "DEADLOCK"
                for candidate in self.resolution_candidates
            )
        ):
            return "TRUE_DEADLOCK"
        return "INCOMPLETE"

    def _has_common_resolution_atom(self, field: str, value: Any) -> bool:
        candidate_ids = sorted(
            candidate["candidate_id"] for candidate in self.resolution_candidates
        )
        return any(
            atom.get("field") == field
            and atom.get("value") == value
            and atom.get("candidate_ids") == candidate_ids
            for atom in self.resolution.get("common_atoms", [])
        )

    def _operative_atom_was_reclassified(self, field: str, value: Any) -> bool:
        source_map = self.resolution.get("source_map", {})
        return any(
            source_map.get(atom_id, {}).get("field") == field
            and source_map.get(atom_id, {}).get("value") == value
            for correction in self.resolution.get("common_core_corrections", [])
            for atom_id in correction.get("correction", {}).get("atom_ids", [])
        )

    def _build_common_core_mapping(self) -> Dict[str, Any]:
        """Map only submitted structured atoms; never infer or rewrite content."""
        candidate_ids = {candidate["candidate_id"] for candidate in self.resolution_candidates}
        grouped: Dict[str, Dict[str, Any]] = {}

        def add(field: str, value: Any, candidate_id: str) -> None:
            key = json.dumps({"field": field, "value": value}, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            entry = grouped.setdefault(
                key,
                {"field": field, "value": copy.deepcopy(value), "candidate_ids": set(), "claim_ids": set()},
            )
            entry["candidate_ids"].add(candidate_id)
            entry["claim_ids"].update(self._atom_claim_ids(value))

        for candidate in self.resolution_candidates:
            for field in ("agreed_points", "reservations", "conflicts"):
                for value in candidate.get(field, []):
                    add(field, value, candidate["candidate_id"])
            add("decision", candidate["decision"], candidate["candidate_id"])
            if candidate.get("outcome") == "WINNER":
                add("winner", candidate["winner"], candidate["candidate_id"])

        entries = sorted(
            grouped.values(),
            key=lambda entry: json.dumps(
                {"field": entry["field"], "value": entry["value"]},
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ),
        )
        source_map: Dict[str, Dict[str, Any]] = {}
        common_atoms: List[Dict[str, Any]] = []
        reservations: List[Dict[str, Any]] = []
        conflicts: List[Dict[str, Any]] = []
        for index, entry in enumerate(entries, 1):
            atom = {
                "id": "A%d" % index,
                "field": entry["field"],
                "value": copy.deepcopy(entry["value"]),
                "candidate_ids": sorted(entry["candidate_ids"]),
                "claim_ids": sorted(entry["claim_ids"]),
            }
            source_map[atom["id"]] = copy.deepcopy(atom)
            if (
                atom["field"] in {"agreed_points", "decision", "winner"}
                and set(atom["candidate_ids"]) == candidate_ids
            ):
                common_atoms.append(atom)
            elif atom["field"] in {"conflicts", "decision", "winner"}:
                conflicts.append(atom)
            else:
                reservations.append(atom)
        return {
            "common_atoms": common_atoms,
            "reservations": reservations,
            "conflicts": conflicts,
            "source_map": source_map,
        }

    def _atom_claim_ids(self, value: Any) -> List[str]:
        """Read only explicitly structured Claim ID fields, never prose text."""
        found = set()
        if isinstance(value, str):
            if self._claim(value) is not None:
                found.add(value)
        elif isinstance(value, dict):
            claim_id = value.get("claim_id")
            if isinstance(claim_id, str) and self._claim(claim_id) is not None:
                found.add(claim_id)
            claim_ids = value.get("claim_ids", [])
            if isinstance(claim_ids, list):
                found.update(
                    claim_id
                    for claim_id in claim_ids
                    if isinstance(claim_id, str) and self._claim(claim_id) is not None
                )
            for child in value.values():
                found.update(self._atom_claim_ids(child))
        elif isinstance(value, list):
            for child in value:
                found.update(self._atom_claim_ids(child))
        return sorted(found)

    def _valid_candidate_claim_references(self, value: Any) -> bool:
        if isinstance(value, dict):
            if "claim_id" in value and (
                not isinstance(value["claim_id"], str)
                or self._claim(value["claim_id"]) is None
            ):
                return False
            if "claim_ids" in value:
                claim_ids = value["claim_ids"]
                if (
                    not isinstance(claim_ids, list)
                    or any(
                        not isinstance(claim_id, str)
                        or self._claim(claim_id) is None
                        for claim_id in claim_ids
                    )
                ):
                    return False
            return all(
                self._valid_candidate_claim_references(child)
                for child in value.values()
            )
        if isinstance(value, list):
            return all(
                self._valid_candidate_claim_references(child) for child in value
            )
        return True

    @staticmethod
    def _validate_emergency_safety(config: Dict[str, Any]) -> None:
        limit = config.get("event_limit")
        if isinstance(limit, bool) or not isinstance(limit, int) or limit <= 0:
            raise ValueError("emergency safety event_limit must be a positive integer")
        seconds = config.get("time_limit_seconds")
        if seconds is not None and (
            isinstance(seconds, bool)
            or not isinstance(seconds, (int, float))
            or not math.isfinite(float(seconds))
            or seconds <= 0
        ):
            raise ValueError("emergency safety time_limit_seconds must be a positive number or null")
        try:
            started = _datetime.datetime.fromisoformat(
                str(config.get("started_at", "")).replace("Z", "+00:00")
            )
        except ValueError as exc:
            raise ValueError("emergency safety started_at must be an ISO timestamp") from exc
        if started.tzinfo is None:
            raise ValueError("emergency safety started_at must include a timezone")

    def _safety_reached(self) -> bool:
        limit = self.emergency_safety.get("event_limit")
        if isinstance(limit, int) and limit >= 0 and len(self.accepted_events) >= limit:
            return True
        seconds = self.emergency_safety.get("time_limit_seconds")
        if seconds is None:
            return False
        try:
            started = _datetime.datetime.fromisoformat(str(self.emergency_safety["started_at"]).replace("Z", "+00:00"))
            current = _datetime.datetime.fromisoformat(str(self._now()).replace("Z", "+00:00"))
            return (current - started).total_seconds() >= float(seconds)
        except (KeyError, TypeError, ValueError):
            return False

    def _formal_deadlock_evidence(self) -> bool:
        if self.resolution.get("formal_deadlock_evidence"):
            return True
        if self.phase != "COMMON_CORE_CONFIRMATION":
            return False
        corrected_core_rejected = (
            self.resolution.get("common_core_correction_count", 0) >= 1
            and any(
                confirmation["response"].startswith("REJECT")
                for confirmation in self.common_core_confirmations
            )
        )
        return corrected_core_rejected

    def _accept(self, event_id: str, fingerprint: str, envelope: Dict[str, Any], event_phase: str, event_cycle: int) -> Dict[str, Any]:
        self.accepted_sequence += 1
        record = self._event_record(envelope, True, None, self.accepted_sequence, event_phase, event_cycle)
        self.events.append(record)
        self.accepted_events.append(record)
        decision = {"accepted": True, "event_id": event_id, "sequence": self.accepted_sequence, "phase": self.phase, "cycle": self.cycle, "next_actor": self.next_actor, "next_action": self.next_action, "terminal_status": self.terminal_status}
        self.receipts[event_id] = {"fingerprint": fingerprint, "decision": copy.deepcopy(decision)}
        return decision

    def _record_reject(self, event_id: str, fingerprint: str, envelope: Dict[str, Any], reason: str) -> Dict[str, Any]:
        record = self._event_record(envelope, False, reason, None)
        self.events.append(record)
        decision = {"accepted": False, "event_id": event_id, "reason": reason, "phase": self.phase, "cycle": self.cycle, "next_actor": self.next_actor, "next_action": self.next_action, "terminal_status": self.terminal_status}
        self.receipts[event_id] = {"fingerprint": fingerprint, "decision": copy.deepcopy(decision)}
        return decision

    def _ephemeral_reject(self, event_id: Optional[str], reason: str) -> Dict[str, Any]:
        return {"accepted": False, "event_id": event_id, "reason": reason, "phase": self.phase, "cycle": self.cycle, "next_actor": self.next_actor, "next_action": self.next_action, "terminal_status": self.terminal_status}

    def _event_record(self, envelope: Dict[str, Any], accepted: bool, reason: Optional[str], sequence: Optional[int], event_phase: Optional[str] = None, event_cycle: Optional[int] = None) -> Dict[str, Any]:
        observed_at = self._now()
        return {"event_id": envelope["event_id"], "sequence": sequence, "phase": event_phase if event_phase is not None else envelope["phase"], "cycle": self.cycle if event_cycle is None else event_cycle, "participant": envelope["actor"], "observed_at": observed_at, "committed_at": observed_at if accepted else None, "action_type": envelope["action_type"], "accepted": accepted, "rejection_reason": reason, "payload": copy.deepcopy(envelope["payload"])}

    def artifact_metadata(self, *, include_private: bool = False) -> Dict[str, Any]:
        """Return renderer-safe audit metadata, redacting candidate provenance by default."""
        events = copy.deepcopy(self.events)
        if not include_private:
            for event in events:
                if event["action_type"] == "RESOLUTION_CANDIDATE":
                    event["participant"] = "anonymous"
                    event["payload"] = _strip_provenance(event.get("payload", {}))
        return {
            "schema_version": self.schema_version,
            "debate_id": self.debate_id,
            "phase": self.phase,
            "cycle": self.cycle,
            "accepted_sequence": self.accepted_sequence,
            "next_actor": self.next_actor,
            "next_action": self.next_action,
            "terminal_status": self.terminal_status,
            "emergency_safety": copy.deepcopy(self.emergency_safety),
            "events": events,
        }

    def to_dict(self) -> Dict[str, Any]:
        return {key: copy.deepcopy(value) for key, value in self.__dict__.items() if key != "_now"}

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    @classmethod
    def from_dict(cls, state: Dict[str, Any], *, now: Optional[Callable[[], str]] = None) -> "DebateController":
        if not isinstance(state, dict) or state.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("unsupported schema_version")
        controller = cls(state["debate_id"], state["participants"], emergency_safety=state.get("emergency_safety"), now=now)
        for key, value in state.items():
            if key not in {"_now", "_load_after_init"}:
                setattr(controller, key, copy.deepcopy(value))
        controller._now = now or _utc_now
        controller._validate_serialized_state()
        return controller

    @classmethod
    def from_json(cls, serialized: str, *, now: Optional[Callable[[], str]] = None) -> "DebateController":
        return cls.from_dict(json.loads(serialized), now=now)

    def _validate_serialized_state(self) -> None:
        phases = set(NORMAL_PHASES) | {
            "STEELMAN_CONFIRMATION",
            "METHODOLOGY_AUDIT",
            "RESOLUTION_CANDIDATE",
            "COMMON_CORE_CONFIRMATION",
        }
        if self.phase not in phases:
            raise ValueError("invalid serialized phase")
        if not isinstance(self.accepted_sequence, int) or isinstance(self.accepted_sequence, bool):
            raise ValueError("invalid serialized accepted sequence")
        if not isinstance(self.accepted_events, list) or self.accepted_sequence != len(self.accepted_events):
            raise ValueError("invalid serialized accepted sequence")
        if any(not isinstance(event, dict) for event in self.accepted_events) or [event.get("sequence") for event in self.accepted_events] != list(
            range(1, self.accepted_sequence + 1)
        ):
            raise ValueError("invalid serialized accepted sequence")
        accepted_event_ids = [event.get("event_id") for event in self.accepted_events]
        if (
            any(not isinstance(event_id, str) or not event_id for event_id in accepted_event_ids)
            or len(set(accepted_event_ids)) != len(accepted_event_ids)
        ):
            raise ValueError("invalid serialized accepted event IDs")
        if not isinstance(self.receipts, dict):
            raise ValueError("invalid serialized receipts")
        if not isinstance(self.events, list) or any(
            not isinstance(event, dict) for event in self.events
        ):
            raise ValueError("invalid serialized events")
        event_ids = {event.get("event_id") for event in self.events}
        if set(self.receipts) != event_ids:
            raise ValueError("invalid serialized receipts")
        if [event for event in self.events if event.get("accepted")] != self.accepted_events:
            raise ValueError("invalid serialized accepted events")
        for event in self.events:
            event_id = event.get("event_id")
            receipt = self.receipts.get(event_id)
            if not isinstance(receipt, dict):
                raise ValueError("invalid serialized receipts")
            if event.get("rejection_reason") != "conflicting_event_id":
                reconstructed = {
                    "debate_id": self.debate_id,
                    "event_id": event_id,
                    "actor": event.get("participant"),
                    "action_type": event.get("action_type"),
                    "phase": event.get("phase"),
                    "payload": event.get("payload"),
                }
                if receipt.get("fingerprint") != _envelope_fingerprint(reconstructed):
                    raise ValueError("invalid serialized receipts")
        for event in self.accepted_events:
            receipt = self.receipts.get(event["event_id"])
            reconstructed = {
                "debate_id": self.debate_id,
                "event_id": event["event_id"],
                "actor": event.get("participant"),
                "action_type": event.get("action_type"),
                "phase": event.get("phase"),
                "payload": event.get("payload"),
            }
            if (
                not isinstance(receipt, dict)
                or receipt.get("fingerprint") != _envelope_fingerprint(reconstructed)
                or not isinstance(receipt.get("decision"), dict)
                or not receipt["decision"].get("accepted")
                or receipt["decision"].get("sequence") != event.get("sequence")
            ):
                raise ValueError("invalid serialized receipts")
        accepted_by_id = {
            event["event_id"]: event for event in self.accepted_events
        }
        for event_id, receipt in self.receipts.items():
            decision = receipt.get("decision") if isinstance(receipt, dict) else None
            if (
                not isinstance(decision, dict)
                or decision.get("event_id") != event_id
                or bool(decision.get("accepted")) != (event_id in accepted_by_id)
            ):
                raise ValueError("invalid serialized receipts")
            if event_id in accepted_by_id and decision.get("sequence") != accepted_by_id[event_id].get("sequence"):
                raise ValueError("invalid serialized receipts")
        advocates = self.advocates
        auditors = [
            participant["id"]
            for participant in self.participants
            if participant["role"] == "auditor"
        ]
        canonical_speakers = {
            "OPENING": advocates + auditors,
            "CROSS_EXAM": advocates[:],
            "RESPONSE": advocates + auditors,
            "UPDATE": advocates[:],
            "CRUCIAL_DISPUTE": advocates[:],
        }
        if self.phase_speakers != canonical_speakers:
            raise ValueError("invalid serialized speaker order")
        if not isinstance(self._turn_index, int) or self._turn_index < 0:
            raise ValueError("invalid serialized turn index")
        if not isinstance(self.cycle, int) or self.cycle < 0:
            raise ValueError("invalid serialized cycle")
        if self.terminal_status is not None:
            if self.terminal_status not in {
                "FINAL_CONSENSUS",
                "CONSENSUS_WITH_RESERVATIONS",
                "FINAL_WINNER",
                "TRUE_DEADLOCK",
                "INCOMPLETE",
            }:
                raise ValueError("invalid serialized terminal status")
            if self.next_actor is not None or self.next_action is not None:
                raise ValueError("invalid serialized terminal state")
            if self.terminal_status != "INCOMPLETE":
                if self.phase != "COMMON_CORE_CONFIRMATION" or not self.resolution_candidates:
                    raise ValueError("invalid serialized terminal status")
                confirmations_complete = (
                    len(self.common_core_confirmations) == len(self.advocates)
                )
                if self.terminal_status in {
                    "FINAL_CONSENSUS",
                    "CONSENSUS_WITH_RESERVATIONS",
                    "FINAL_WINNER",
                } and not confirmations_complete:
                    raise ValueError("invalid serialized terminal status")
                if (
                    self.terminal_status == "TRUE_DEADLOCK"
                    and not confirmations_complete
                    and not self._formal_deadlock_evidence()
                ):
                    raise ValueError("invalid serialized terminal status")
                if confirmations_complete:
                    responses = [
                        confirmation.get("response", "")
                        for confirmation in self.common_core_confirmations
                    ]
                    if self._classify_resolution_responses(responses) != self.terminal_status:
                        raise ValueError("invalid serialized terminal status")
            self._validate_serialized_replay()
            return
        participant_ids = {participant["id"] for participant in self.participants}
        if self.next_actor == "__parent__":
            if self.phase != "COMMON_CORE_CONFIRMATION" or self.next_action != "COMMON_CORE_CORRECTION":
                raise ValueError("invalid serialized next actor")
            self._validate_serialized_replay()
            return
        if self.next_actor not in participant_ids:
            raise ValueError("invalid serialized next actor")
        expected_speakers: Optional[List[str]] = None
        if self.phase in NORMAL_PHASES:
            expected_speakers = self.phase_speakers.get(self.phase)
            if self.next_action != "TURN":
                raise ValueError("invalid serialized next action")
        elif self.phase == "STEELMAN_CONFIRMATION":
            pending = next(
                (s for s in self.steelmans if s.get("status") == "needs_correction"),
                None,
            )
            if pending is None:
                pending = next(
                    (
                        s
                        for s in self.steelmans
                        if s.get("status") in {"pending", "awaiting_confirmation"}
                    ),
                    None,
                )
            if pending is None:
                raise ValueError("invalid serialized steelman state")
            expected_actor = (
                pending.get("author")
                if pending.get("status") == "needs_correction"
                else pending.get("target")
            )
            expected_action = (
                "STEELMAN_CORRECTION"
                if pending.get("status") == "needs_correction"
                else "STEELMAN_CONFIRM"
            )
            if self.next_actor != expected_actor or self.next_action != expected_action:
                raise ValueError("invalid serialized steelman state")
            self._validate_serialized_replay()
            return
        elif self.phase == "METHODOLOGY_AUDIT":
            if (
                self.auditor is None
                or self.next_actor != self.auditor
                or self.next_action != "METHODOLOGY_AUDIT"
                or self._post_audit_transition not in {"RESOLUTION", "NEXT_CRUCIAL"}
            ):
                raise ValueError("invalid serialized methodology audit")
            self._validate_serialized_replay()
            return
        elif self.phase == "RESOLUTION_CANDIDATE":
            expected_speakers = self.advocates
            if self.next_action != "RESOLUTION_CANDIDATE":
                raise ValueError("invalid serialized next action")
        elif self.phase == "COMMON_CORE_CONFIRMATION" and self.next_action == "COMMON_CORE_CONFIRM":
            expected_speakers = self.advocates
        elif self.phase == "COMMON_CORE_CONFIRMATION":
            raise ValueError("invalid serialized next action")
        if expected_speakers is not None:
            if self._turn_index >= len(expected_speakers) or self.next_actor != expected_speakers[self._turn_index]:
                raise ValueError("invalid serialized next actor")
        self._validate_serialized_replay()

    def _validate_serialized_replay(self) -> None:
        current_time = [self.emergency_safety["started_at"]]
        replay = DebateController(
            self.debate_id,
            self.participants,
            emergency_safety=self.emergency_safety,
            now=lambda: current_time[0],
        )
        for event in self.events:
            current_time[0] = event.get("observed_at", current_time[0])
            replay.submit(
                {
                    "debate_id": self.debate_id,
                    "event_id": event.get("event_id"),
                    "actor": event.get("participant"),
                    "action_type": event.get("action_type"),
                    "phase": event.get("phase"),
                    "payload": copy.deepcopy(event.get("payload")),
                }
            )
        if replay.to_dict() != self.to_dict():
            raise ValueError("serialized state is not derivable from accepted history")


def _write_state(path: Path, controller: DebateController) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(controller.to_json(), encoding="utf-8")
    temporary.replace(path)


def main(argv: Optional[List[str]] = None) -> int:
    """Initialize, update, or inspect one durable controller state file."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="create a controller state file")
    init_parser.add_argument("--state", required=True, type=Path)
    init_parser.add_argument("--debate-id", required=True)
    init_parser.add_argument("--participants", required=True, type=Path)
    init_parser.add_argument("--event-limit", type=int, default=10000)
    init_parser.add_argument("--time-limit-seconds", type=float)

    submit_parser = subparsers.add_parser("submit", help="validate and commit one action")
    submit_parser.add_argument("--state", required=True, type=Path)
    submit_parser.add_argument("--action", required=True, type=Path)

    show_parser = subparsers.add_parser("show", help="print state or renderer-safe metadata")
    show_parser.add_argument("--state", required=True, type=Path)
    show_parser.add_argument("--artifact", action="store_true")
    show_parser.add_argument("--include-private", action="store_true")

    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            participants = json.loads(args.participants.read_text(encoding="utf-8"))
            safety = {
                "event_limit": args.event_limit,
                "time_limit_seconds": args.time_limit_seconds,
            }
            controller = DebateController(
                args.debate_id, participants, emergency_safety=safety
            )
            _write_state(args.state, controller)
            print(controller.to_json())
            return 0

        controller = DebateController.from_json(args.state.read_text(encoding="utf-8"))
        if args.command == "submit":
            envelope = json.loads(args.action.read_text(encoding="utf-8"))
            decision = controller.submit(envelope)
            _write_state(args.state, controller)
            print(json.dumps(decision, ensure_ascii=False, sort_keys=True))
            return 0

        output = (
            controller.artifact_metadata(include_private=args.include_private)
            if args.artifact
            else controller.to_dict()
        )
        print(json.dumps(output, ensure_ascii=False, sort_keys=True))
        return 0
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"debate_controller: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

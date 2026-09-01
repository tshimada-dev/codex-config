#!/usr/bin/env python3
"""Render a Codex autonomous-debate transcript as a standalone chat UI."""

from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import re
from typing import Any
from urllib.parse import urlparse


ALLOWED_KINDS = {"argument", "intervention", "resolution", "system"}
CAMP_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{0,31}$")
ITEM_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,31}$")
CLAIM_TYPES = {"definition", "fact", "inference", "prediction", "value"}
CLAIM_STATUSES = {
    "agreed",
    "definitional_dispute",
    "disputed",
    "proposed",
    "superseded",
    "unsupported",
}
PARTICIPANT_ROLES = {"advocate", "auditor"}
STRENGTH_VALUES = {"high", "low", "medium", "not-assessed"}
EVIDENCE_MODES = {"closed-book", "shared-evidence"}
PHASE_VALUES = {"OPENING", "CROSS_EXAM", "RESPONSE", "UPDATE", "CRUCIAL_DISPUTE"}
BASE_PHASE_ORDER = ("OPENING", "CROSS_EXAM", "RESPONSE", "UPDATE")
PROPOSITION_TYPES = {"CAUSAL", "FACTUAL", "FORECAST", "POLICY"}
FORECAST_CHECKPOINTS = {"PRIOR", "AFTER_CROSS_EXAM", "AFTER_CRUCIAL_DISPUTE", "FINAL"}
RESOLUTION_STAGES = {"candidate", "confirmation", "public-statement"}
STATUS_VALUES = {
    "CONSENSUS_WITH_RESERVATIONS",
    "DEADLOCK",
    "FINAL_CONSENSUS",
    "FINAL_WINNER",
    "INCOMPLETE",
    "TRUE_DEADLOCK",
}
PALETTE = (
    ("#6d5dfc", "#eeeaff"),
    ("#087f8c", "#e4f7f7"),
    ("#b3541e", "#fff0e5"),
    ("#9a3e72", "#faeaf3"),
    ("#526a35", "#eef6e5"),
)
LABELS = {
    "en": {
        "all": "All",
        "camp_count": "participants",
        "common_ground": "Common ground",
        "causal_strength": "Causal strength",
        "claim_ledger": "Claim Ledger",
        "conditions": "Conditions",
        "decision_rule": "Decision rule",
        "directness": "Directness",
        "does_not_establish": "Does not establish",
        "event_count": "events",
        "evidence": "Evidence",
        "evidence_cards": "Evidence cards",
        "evidence_links": "Evidence → Claim links",
        "expected_update": "Expected update",
        "falsifier": "Falsifier",
        "forecast_disclaimer": "Participant forecasts are not calibrated or independent.",
        "forecast_trajectory": "Forecast trajectory",
        "generalizability": "Generalizability",
        "group_discussion": "Group discussion",
        "intervention": "Intervention",
        "independence": "Independence",
        "key_updates": "Key belief updates",
        "limitations": "Limitations",
        "main_finding": "Main finding",
        "needed_evidence": "What would resolve this?",
        "none_recorded": "None recorded",
        "participants": "Participants",
        "phase": "Phase",
        "population": "Population",
        "resolution": "Resolution",
        "resolution_source": "Resolution source",
        "resolves_claims": "Resolves claims",
        "round": "Round",
        "source": "Source",
        "supports": "Supports",
        "study_type": "Study type",
        "system": "System",
        "title_prefix": "Autonomous debate",
        "target": "Target",
        "temporal_relevance": "Temporal relevance",
        "threshold": "Threshold",
        "horizon": "Horizon",
        "yes_condition": "YES condition",
        "no_condition": "NO condition",
        "collection": "Collection",
        "unresolved": "Unresolved",
    },
    "ja": {
        "all": "すべて",
        "camp_count": "参加者",
        "common_ground": "共通点",
        "causal_strength": "因果推論強度",
        "claim_ledger": "Claim Ledger / 論点台帳",
        "conditions": "比較条件",
        "decision_rule": "Decision rule / 判定規則",
        "directness": "直接性",
        "does_not_establish": "この証拠だけでは言えないこと",
        "event_count": "イベント",
        "evidence": "証拠",
        "evidence_cards": "Evidence cards / 証拠カード",
        "evidence_links": "Evidence → Claim links / 証拠と主張の接続",
        "expected_update": "想定される更新",
        "falsifier": "反証条件",
        "forecast_disclaimer": "参加者の予測値であり、校正済みでも独立推定でもありません。",
        "forecast_trajectory": "Forecast trajectory / 予測推移",
        "generalizability": "一般化可能性",
        "group_discussion": "グループ討論",
        "intervention": "親の介入",
        "independence": "独立性",
        "key_updates": "Key belief updates / 信念更新",
        "limitations": "限界",
        "main_finding": "主要結果",
        "needed_evidence": "What would resolve this? / 決着に必要な証拠",
        "none_recorded": "記録なし",
        "participants": "参加陣営",
        "phase": "フェーズ",
        "population": "対象",
        "resolution": "討論結果",
        "resolution_source": "確定情報源",
        "resolves_claims": "対象Claim",
        "round": "ラウンド",
        "source": "出典",
        "supports": "支持する範囲",
        "study_type": "研究タイプ",
        "system": "進行",
        "title_prefix": "自律討論",
        "target": "判定対象",
        "temporal_relevance": "時間的関連性",
        "threshold": "閾値",
        "horizon": "期限",
        "yes_condition": "YES条件",
        "no_condition": "NO条件",
        "collection": "収集方法",
        "unresolved": "未解決点",
    },
}

ROLE_LABELS = {
    "en": {"advocate": "Advocate", "auditor": "Methodological auditor"},
    "ja": {"advocate": "討論陣営", "auditor": "方法論監査（投票権なし）"},
}

CLAIM_STATUS_LABELS = {
    "en": {
        "agreed": "Agreed",
        "definitional_dispute": "Definitional dispute",
        "disputed": "Disputed",
        "proposed": "Proposed",
        "superseded": "Superseded",
        "unsupported": "Unsupported",
    },
    "ja": {
        "agreed": "合意",
        "definitional_dispute": "定義上の対立",
        "disputed": "係争中",
        "proposed": "提案済み",
        "superseded": "置換済み",
        "unsupported": "裏付けなし",
    },
}


def require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def require_text_list(value: Any, field: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{field} must be an array")
    return [require_text(item, f"{field} item") for item in value]


def require_identifier(value: Any, field: str) -> str:
    identifier = require_text(value, field)
    if not ITEM_ID_PATTERN.fullmatch(identifier):
        raise ValueError(f"{field} must use letters, digits, dots, hyphens, or underscores")
    return identifier


def require_choice(value: Any, field: str, choices: set[str]) -> str:
    selected = require_text(value, field)
    if selected not in choices:
        raise ValueError(f"{field} must be one of: {', '.join(sorted(choices))}")
    return selected


def require_probability(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 1:
        raise ValueError(f"{field} must be a number between 0 and 1")
    return float(value)


def require_http_url(value: Any, field: str) -> str:
    url = require_text(value, field)
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"{field} must use http or https")
    return url


def validate_document(document: Any) -> dict[str, Any]:
    if not isinstance(document, dict):
        raise ValueError("debate document must be an object")

    normalized: dict[str, Any] = {
        "lang": document.get("lang", "en"),
        "title": require_text(document.get("title"), "title"),
        "proposition": require_text(document.get("proposition"), "proposition"),
        "status": require_choice(document.get("status"), "status", STATUS_VALUES),
        "evidence_mode": require_choice(
            document.get("evidence_mode"), "evidence_mode", EVIDENCE_MODES
        ),
    }
    if normalized["lang"] not in LABELS:
        raise ValueError("lang must be 'en' or 'ja'")

    proposition_type = document.get("proposition_type")
    decision_rule = document.get("decision_rule")
    if (proposition_type is None) != (decision_rule is None):
        raise ValueError("proposition_type and decision_rule must be provided together")
    if proposition_type is None:
        normalized["proposition_type"] = None
        normalized["decision_rule"] = None
    else:
        normalized_type = require_choice(
            proposition_type, "proposition_type", PROPOSITION_TYPES
        )
        if not isinstance(decision_rule, dict):
            raise ValueError("decision_rule must be an object")
        threshold = decision_rule.get("threshold")
        if normalized_type == "FORECAST" and threshold is None:
            raise ValueError("decision_rule.threshold is required for FORECAST")
        normalized["proposition_type"] = normalized_type
        normalized["decision_rule"] = {
            "target": require_text(decision_rule.get("target"), "decision_rule.target"),
            "horizon": require_text(decision_rule.get("horizon"), "decision_rule.horizon"),
            "yes_condition": require_text(
                decision_rule.get("yes_condition"), "decision_rule.yes_condition"
            ),
            "no_condition": require_text(
                decision_rule.get("no_condition"), "decision_rule.no_condition"
            ),
            "resolution_source": require_text(
                decision_rule.get("resolution_source"),
                "decision_rule.resolution_source",
            ),
            "threshold": (
                require_probability(threshold, "decision_rule.threshold")
                if threshold is not None
                else None
            ),
        }

    debate_progress = document.get("debate_progress")
    if debate_progress is None:
        normalized["debate_progress"] = None
    else:
        if not isinstance(debate_progress, dict):
            raise ValueError("debate_progress must be an object")
        completed_phases = require_text_list(
            debate_progress.get("completed_phases"),
            "debate_progress.completed_phases",
        )
        expected_prefix = list(BASE_PHASE_ORDER[: len(completed_phases)])
        if completed_phases != expected_prefix:
            raise ValueError(
                "debate_progress.completed_phases must be an ordered prefix of "
                "OPENING, CROSS_EXAM, RESPONSE, UPDATE"
            )
        completed_cycles = debate_progress.get("completed_crucial_cycles", 0)
        if (
            not isinstance(completed_cycles, int)
            or isinstance(completed_cycles, bool)
            or completed_cycles < 0
        ):
            raise ValueError(
                "debate_progress.completed_crucial_cycles must be a non-negative integer"
            )
        if completed_cycles and completed_phases != list(BASE_PHASE_ORDER):
            raise ValueError(
                "completed crucial-dispute cycles require all base phases to be completed"
            )
        normalized["debate_progress"] = {
            "completed_phases": completed_phases,
            "completed_crucial_cycles": completed_cycles,
        }

    camps = document.get("camps")
    if not isinstance(camps, list) or not 2 <= len(camps) <= 5:
        raise ValueError("camps must contain two to five participants")

    normalized_camps: list[dict[str, str]] = []
    camp_ids: set[str] = set()
    for index, camp in enumerate(camps):
        if not isinstance(camp, dict):
            raise ValueError(f"camps[{index}] must be an object")
        camp_id = require_text(camp.get("id"), f"camps[{index}].id")
        if not CAMP_ID_PATTERN.fullmatch(camp_id):
            raise ValueError(
                f"camps[{index}].id must use lowercase letters, digits, hyphens, or underscores"
            )
        if camp_id in camp_ids:
            raise ValueError(f"duplicate camp id: {camp_id}")
        camp_ids.add(camp_id)
        normalized_camps.append(
            {
                "id": camp_id,
                "name": require_text(camp.get("name"), f"camps[{index}].name"),
                "role": require_choice(
                    camp.get("role", "advocate"),
                    f"camps[{index}].role",
                    PARTICIPANT_ROLES,
                ),
            }
        )
    advocate_count = sum(camp["role"] == "advocate" for camp in normalized_camps)
    auditor_count = sum(camp["role"] == "auditor" for camp in normalized_camps)
    if not 2 <= advocate_count <= 4:
        raise ValueError("camps must contain two to four advocates")
    if auditor_count > 1:
        raise ValueError("camps may contain at most one auditor")
    normalized["camps"] = normalized_camps

    evidence_cards = document.get("evidence_cards", [])
    if not isinstance(evidence_cards, list):
        raise ValueError("evidence_cards must be an array")
    normalized_evidence: list[dict[str, Any]] = []
    evidence_ids: set[str] = set()
    for index, card in enumerate(evidence_cards):
        if not isinstance(card, dict):
            raise ValueError(f"evidence_cards[{index}] must be an object")
        card_id = require_identifier(card.get("id"), f"evidence_cards[{index}].id")
        if card_id in evidence_ids:
            raise ValueError(f"duplicate evidence id: {card_id}")
        evidence_ids.add(card_id)
        normalized_evidence.append(
            {
                "id": card_id,
                "title": require_text(card.get("title"), f"evidence_cards[{index}].title"),
                "source": require_text(card.get("source"), f"evidence_cards[{index}].source"),
                "source_url": (
                    require_http_url(
                        card.get("source_url"), f"evidence_cards[{index}].source_url"
                    )
                    if card.get("source_url") is not None
                    else None
                ),
                "study_type": require_text(
                    card.get("study_type"), f"evidence_cards[{index}].study_type"
                ),
                "population": require_text(
                    card.get("population"), f"evidence_cards[{index}].population"
                ),
                "conditions": require_text(
                    card.get("conditions"), f"evidence_cards[{index}].conditions"
                ),
                "main_finding": require_text(
                    card.get("main_finding"), f"evidence_cards[{index}].main_finding"
                ),
                "limitations": require_text_list(
                    card.get("limitations"), f"evidence_cards[{index}].limitations"
                ),
                "causal_strength": require_choice(
                    card.get("causal_strength"),
                    f"evidence_cards[{index}].causal_strength",
                    STRENGTH_VALUES,
                ),
                "generalizability": require_choice(
                    card.get("generalizability"),
                    f"evidence_cards[{index}].generalizability",
                    STRENGTH_VALUES,
                ),
            }
        )
    normalized["evidence_cards"] = normalized_evidence

    claim_ledger = document.get("claim_ledger", [])
    if not isinstance(claim_ledger, list):
        raise ValueError("claim_ledger must be an array")
    normalized_claims: list[dict[str, Any]] = []
    claim_ids: set[str] = set()
    for index, claim in enumerate(claim_ledger):
        if not isinstance(claim, dict):
            raise ValueError(f"claim_ledger[{index}] must be an object")
        claim_id = require_identifier(claim.get("id"), f"claim_ledger[{index}].id")
        if claim_id in claim_ids:
            raise ValueError(f"duplicate claim id: {claim_id}")
        claim_ids.add(claim_id)
        linked_evidence = require_text_list(
            claim.get("evidence"), f"claim_ledger[{index}].evidence"
        )
        unknown_evidence = [item for item in linked_evidence if item not in evidence_ids]
        if unknown_evidence:
            raise ValueError(
                f"claim_ledger[{index}] references unknown evidence: {unknown_evidence[0]}"
            )
        introduced_by = claim.get("introduced_by")
        if introduced_by is not None:
            introduced_by = require_text(
                introduced_by, f"claim_ledger[{index}].introduced_by"
            )
            if introduced_by not in camp_ids:
                raise ValueError(
                    f"claim_ledger[{index}] references unknown camp: {introduced_by}"
                )
        normalized_claims.append(
            {
                "id": claim_id,
                "text": require_text(claim.get("text"), f"claim_ledger[{index}].text"),
                "type": require_choice(
                    claim.get("type"), f"claim_ledger[{index}].type", CLAIM_TYPES
                ),
                "status": require_choice(
                    claim.get("status"), f"claim_ledger[{index}].status", CLAIM_STATUSES
                ),
                "evidence": linked_evidence,
                "introduced_by": introduced_by,
                "falsifier": (
                    require_text(claim.get("falsifier"), f"claim_ledger[{index}].falsifier")
                    if claim.get("falsifier") is not None
                    else None
                ),
            }
        )
    normalized["claim_ledger"] = normalized_claims

    forecast_records = document.get("forecast_records", [])
    if not isinstance(forecast_records, list):
        raise ValueError("forecast_records must be an array")
    normalized_forecasts: list[dict[str, Any]] = []
    forecast_keys: set[tuple[str, str, int | None]] = set()
    advocate_ids = {camp["id"] for camp in normalized_camps if camp["role"] == "advocate"}
    for index, record in enumerate(forecast_records):
        if not isinstance(record, dict):
            raise ValueError(f"forecast_records[{index}] must be an object")
        camp_id = require_text(record.get("camp"), f"forecast_records[{index}].camp")
        if camp_id not in advocate_ids:
            raise ValueError(
                f"forecast_records[{index}] references unknown or non-voting camp: {camp_id}"
            )
        checkpoint = require_choice(
            record.get("checkpoint"),
            f"forecast_records[{index}].checkpoint",
            FORECAST_CHECKPOINTS,
        )
        cycle = record.get("cycle")
        if checkpoint == "AFTER_CRUCIAL_DISPUTE":
            if not isinstance(cycle, int) or isinstance(cycle, bool) or cycle < 1:
                raise ValueError(
                    f"forecast_records[{index}].cycle must be a positive integer for AFTER_CRUCIAL_DISPUTE"
                )
        elif cycle is not None:
            raise ValueError(
                f"forecast_records[{index}].cycle is only valid for AFTER_CRUCIAL_DISPUTE"
            )
        key = (camp_id, checkpoint, cycle)
        if key in forecast_keys:
            raise ValueError("duplicate forecast record for camp, checkpoint, and cycle")
        forecast_keys.add(key)
        probability = require_probability(
            record.get("probability"), f"forecast_records[{index}].probability"
        )
        lower = require_probability(record.get("lower"), f"forecast_records[{index}].lower")
        upper = require_probability(record.get("upper"), f"forecast_records[{index}].upper")
        if not lower <= probability <= upper:
            raise ValueError(
                f"forecast_records[{index}] must satisfy lower <= probability <= upper"
            )
        normalized_forecasts.append(
            {
                "camp": camp_id,
                "checkpoint": checkpoint,
                "cycle": cycle,
                "probability": probability,
                "lower": lower,
                "upper": upper,
                "rationale": require_text(
                    record.get("rationale"), f"forecast_records[{index}].rationale"
                ),
            }
        )
    if normalized_forecasts and normalized.get("proposition_type") != "FORECAST":
        raise ValueError("forecast_records require proposition_type FORECAST")
    if normalized.get("proposition_type") == "FORECAST" and normalized["status"] != "INCOMPLETE":
        progress = normalized["debate_progress"]
        required_checkpoints = {"PRIOR", "FINAL"}
        if progress is None or "RESPONSE" in progress["completed_phases"]:
            required_checkpoints.add("AFTER_CROSS_EXAM")
        for camp_id in sorted(advocate_ids):
            present = {
                record["checkpoint"]
                for record in normalized_forecasts
                if record["camp"] == camp_id
            }
            missing = sorted(required_checkpoints - present)
            if missing:
                raise ValueError(
                    f"missing required forecast checkpoint for camp {camp_id}: {', '.join(missing)}"
                )

        observed_cycles = {
            record["cycle"]
            for record in normalized_forecasts
            if record["checkpoint"] == "AFTER_CRUCIAL_DISPUTE"
        }
        if progress is None:
            required_cycles = (
                set(range(1, max(observed_cycles) + 1)) if observed_cycles else set()
            )
            if observed_cycles != required_cycles:
                raise ValueError("crucial-dispute forecast cycles must be contiguous from 1")
        else:
            required_cycles = set(
                range(1, progress["completed_crucial_cycles"] + 1)
            )
            if not observed_cycles.issubset(required_cycles):
                raise ValueError(
                    "forecast record references a crucial-dispute cycle that was not completed"
                )
        if required_cycles:
            for cycle in sorted(required_cycles):
                submitted = {
                    record["camp"]
                    for record in normalized_forecasts
                    if record["checkpoint"] == "AFTER_CRUCIAL_DISPUTE"
                    and record["cycle"] == cycle
                }
                missing = sorted(advocate_ids - submitted)
                if missing:
                    raise ValueError(
                        "missing forecast for crucial-dispute cycle "
                        f"{cycle}: {', '.join(missing)}"
                    )
    normalized["forecast_records"] = normalized_forecasts

    evidence_links = document.get("evidence_links", [])
    if not isinstance(evidence_links, list):
        raise ValueError("evidence_links must be an array")
    normalized_links: list[dict[str, Any]] = []
    link_keys: set[tuple[str, str]] = set()
    for index, link in enumerate(evidence_links):
        if not isinstance(link, dict):
            raise ValueError(f"evidence_links[{index}] must be an object")
        claim_id = require_identifier(link.get("claim_id"), f"evidence_links[{index}].claim_id")
        evidence_id = require_identifier(
            link.get("evidence_id"), f"evidence_links[{index}].evidence_id"
        )
        if claim_id not in claim_ids:
            raise ValueError(f"evidence_links[{index}] references unknown claim: {claim_id}")
        if evidence_id not in evidence_ids:
            raise ValueError(
                f"evidence_links[{index}] references unknown evidence: {evidence_id}"
            )
        key = (claim_id, evidence_id)
        if key in link_keys:
            raise ValueError("duplicate evidence link for claim and evidence")
        link_keys.add(key)
        normalized_link = {
            "claim_id": claim_id,
            "evidence_id": evidence_id,
            "supports": require_text(link.get("supports"), f"evidence_links[{index}].supports"),
            "does_not_establish": require_text(
                link.get("does_not_establish"),
                f"evidence_links[{index}].does_not_establish",
            ),
        }
        for dimension in (
            "directness",
            "independence",
            "causal_strength",
            "generalizability",
            "temporal_relevance",
        ):
            normalized_link[dimension] = require_choice(
                link.get(dimension), f"evidence_links[{index}].{dimension}", STRENGTH_VALUES
            )
        normalized_links.append(normalized_link)
    normalized["evidence_links"] = normalized_links

    needed_evidence = document.get("needed_evidence", [])
    if not isinstance(needed_evidence, list):
        raise ValueError("needed_evidence must be an array")
    normalized_needed: list[dict[str, Any]] = []
    needed_ids: set[str] = set()
    for index, item in enumerate(needed_evidence):
        if not isinstance(item, dict):
            raise ValueError(f"needed_evidence[{index}] must be an object")
        item_id = require_identifier(item.get("id"), f"needed_evidence[{index}].id")
        if item_id in needed_ids:
            raise ValueError(f"duplicate needed evidence id: {item_id}")
        needed_ids.add(item_id)
        resolves_claims = require_text_list(
            item.get("resolves_claims"), f"needed_evidence[{index}].resolves_claims"
        )
        for claim_id in resolves_claims:
            if claim_id not in claim_ids:
                raise ValueError(
                    f"needed_evidence[{index}] references unknown claim: {claim_id}"
                )
        normalized_needed.append(
            {
                "id": item_id,
                "observation": require_text(
                    item.get("observation"), f"needed_evidence[{index}].observation"
                ),
                "resolves_claims": resolves_claims,
                "expected_update": require_text(
                    item.get("expected_update"),
                    f"needed_evidence[{index}].expected_update",
                ),
                "collection": require_text(
                    item.get("collection"), f"needed_evidence[{index}].collection"
                ),
            }
        )
    normalized["needed_evidence"] = normalized_needed

    belief_updates = document.get("belief_updates", [])
    if not isinstance(belief_updates, list):
        raise ValueError("belief_updates must be an array")
    normalized_updates: list[dict[str, Any]] = []
    for index, update in enumerate(belief_updates):
        if not isinstance(update, dict):
            raise ValueError(f"belief_updates[{index}] must be an object")
        camp_id = require_text(update.get("camp"), f"belief_updates[{index}].camp")
        if camp_id not in camp_ids:
            raise ValueError(f"belief_updates[{index}] references unknown camp: {camp_id}")
        normalized_updates.append(
            {
                "camp": camp_id,
                "phase": require_text(update.get("phase"), f"belief_updates[{index}].phase"),
                "before": require_probability(
                    update.get("before"), f"belief_updates[{index}].before"
                ),
                "after": require_probability(
                    update.get("after"), f"belief_updates[{index}].after"
                ),
                "reason": require_text(update.get("reason"), f"belief_updates[{index}].reason"),
            }
        )
    normalized["belief_updates"] = normalized_updates

    messages = document.get("messages")
    if not isinstance(messages, list):
        raise ValueError("messages must be an array")

    normalized_messages: list[dict[str, Any]] = []
    for index, message in enumerate(messages):
        if not isinstance(message, dict):
            raise ValueError(f"messages[{index}] must be an object")
        kind = require_text(message.get("kind"), f"messages[{index}].kind")
        if kind not in ALLOWED_KINDS:
            raise ValueError(f"messages[{index}].kind is unsupported: {kind}")

        camp_id = message.get("camp")
        if camp_id is not None:
            camp_id = require_text(camp_id, f"messages[{index}].camp")
            if camp_id not in camp_ids:
                raise ValueError(f"messages[{index}] references unknown camp: {camp_id}")
        if kind == "argument" and camp_id is None:
            raise ValueError(f"messages[{index}].camp is required for {kind}")

        resolution_stage = message.get("resolution_stage")
        if (
            kind == "resolution"
            and resolution_stage is None
            and normalized.get("proposition_type") is not None
        ):
            raise ValueError(
                f"messages[{index}].resolution_stage is required for state-driven artifacts"
            )
        if resolution_stage is not None:
            if kind != "resolution":
                raise ValueError(
                    f"messages[{index}].resolution_stage is only valid for resolution messages"
                )
            resolution_stage = require_choice(
                resolution_stage,
                f"messages[{index}].resolution_stage",
                RESOLUTION_STAGES,
            )
            if resolution_stage in {"candidate", "confirmation"} and camp_id is not None:
                raise ValueError(
                    f"messages[{index}] {resolution_stage} resolution messages must not identify a camp"
                )
            if resolution_stage == "public-statement" and camp_id is None:
                raise ValueError(
                    f"messages[{index}].camp is required for public-statement resolution messages"
                )

        speaker = (
            require_text(message.get("speaker"), f"messages[{index}].speaker")
            if message.get("speaker") is not None
            else None
        )
        if resolution_stage in {"candidate", "confirmation"} and speaker is None:
            raise ValueError(
                f"messages[{index}].speaker is required for anonymous resolution messages"
            )

        round_number = message.get("round")
        if round_number is not None and (
            not isinstance(round_number, int) or isinstance(round_number, bool) or round_number < 1
        ):
            raise ValueError(f"messages[{index}].round must be a positive integer")

        phase = message.get("phase")
        if phase is not None:
            phase = require_choice(
                phase, f"messages[{index}].phase", PHASE_VALUES
            )

        normalized_messages.append(
            {
                "kind": kind,
                "camp": camp_id,
                "speaker": speaker,
                "resolution_stage": resolution_stage,
                "round": round_number,
                "phase": phase,
                "text": require_text(message.get("text"), f"messages[{index}].text"),
                "timestamp": (
                    require_text(message.get("timestamp"), f"messages[{index}].timestamp")
                    if message.get("timestamp") is not None
                    else None
                ),
            }
        )
    normalized["messages"] = normalized_messages

    summary = document.get("summary", {})
    if not isinstance(summary, dict):
        raise ValueError("summary must be an object")
    normalized["summary"] = {
        "decision": require_text(summary.get("decision"), "summary.decision"),
        "agreed_points": require_text_list(summary.get("agreed_points"), "summary.agreed_points"),
        "unresolved_objections": require_text_list(
            summary.get("unresolved_objections"), "summary.unresolved_objections"
        ),
    }
    return normalized


def escaped_text(value: str) -> str:
    return escape(value).replace("\n", "<br>")


def render_list(items: list[str], empty_label: str) -> str:
    if not items:
        return f'<p class="empty">{escape(empty_label)}</p>'
    return "<ul>" + "".join(f"<li>{escaped_text(item)}</li>" for item in items) + "</ul>"


def render_document(document: Any) -> str:
    debate = validate_document(document)
    labels = LABELS[debate["lang"]]
    camps = debate["camps"]
    camp_by_id = {camp["id"]: (index, camp) for index, camp in enumerate(camps)}

    camp_styles = []
    participant_cards = []
    filter_buttons = [
        f'<button type="button" class="filter active" data-filter="all" aria-pressed="true">{labels["all"]}</button>',
        f'<button type="button" class="filter" data-filter="system" aria-pressed="false">{labels["system"]}</button>',
    ]
    for index, camp in enumerate(camps):
        ink, tint = PALETTE[index]
        camp_styles.append(
            f'.camp-{index}{{--camp-ink:{ink};--camp-tint:{tint};}}'
        )
        camp_name = escape(camp["name"])
        camp_id = escape(camp["id"], quote=True)
        participant_cards.append(
            f'<li class="participant camp-{index}"><span class="avatar" aria-hidden="true">'
            f'{escape(camp["name"][0].upper())}</span><span>{camp_name}'
            f'<small>{escape(ROLE_LABELS[debate["lang"]][camp["role"]])}</small></span></li>'
        )
        filter_buttons.append(
            f'<button type="button" class="filter" data-filter="{camp_id}" '
            f'aria-pressed="false">{camp_name}</button>'
        )

    message_cards = []
    for message in debate["messages"]:
        kind = message["kind"]
        camp_id = message["camp"]
        if camp_id is None:
            speaker = message["speaker"] or ("Supervisor" if kind == "intervention" else "System")
            if kind == "intervention":
                badge = labels["intervention"]
            elif kind == "resolution":
                badge = labels["resolution"]
            else:
                badge = labels["system"]
            timestamp = (
                f'<time>{escape(message["timestamp"])}</time>' if message["timestamp"] else ""
            )
            message_cards.append(
                f'<article class="message {kind}" data-camp="system">'
                f'<div class="system-icon" aria-hidden="true">{"!" if kind == "intervention" else "i"}</div>'
                f'<div><header><strong>{escape(speaker)}</strong><span class="kind-badge">{badge}</span>'
                f'{timestamp}</header><p>{escaped_text(message["text"])}</p></div></article>'
            )
            continue

        camp_index, camp = camp_by_id[camp_id]
        meta_parts = []
        if message["phase"] is not None:
            meta_parts.append(f'{labels["phase"]} {escape(message["phase"])}')
        if message["round"] is not None:
            meta_parts.append(f'{labels["round"]} {message["round"]}')
        if message["timestamp"]:
            meta_parts.append(escape(message["timestamp"]))
        meta = " · ".join(meta_parts)
        meta_html = f'<span class="message-meta">{meta}</span>' if meta else ""
        message_cards.append(
            f'<article class="message {kind} camp-{camp_index}" '
            f'data-camp="{escape(camp_id, quote=True)}">'
            f'<div class="avatar" aria-hidden="true">{escape(camp["name"][0].upper())}</div>'
            f'<div class="bubble"><header><strong>{escape(camp["name"])}</strong>{meta_html}</header>'
            f'<p>{escaped_text(message["text"])}</p></div></article>'
        )

    summary = debate["summary"]
    evidence_cards = []
    for card in debate["evidence_cards"]:
        source = escape(card["source"])
        if card["source_url"]:
            source = (
                f'<a href="{escape(card["source_url"], quote=True)}" target="_blank" '
                f'rel="noreferrer">{source}</a>'
            )
        evidence_cards.append(
            f'<details class="evidence-card"><summary><span class="evidence-id">'
            f'{escape(card["id"])}</span><strong>{escape(card["title"])}</strong></summary>'
            f'<dl><dt>{labels["source"]}</dt><dd>{source}</dd>'
            f'<dt>{labels["study_type"]}</dt><dd>{escape(card["study_type"])}</dd>'
            f'<dt>{labels["population"]}</dt><dd>{escaped_text(card["population"])}</dd>'
            f'<dt>{labels["conditions"]}</dt><dd>{escaped_text(card["conditions"])}</dd>'
            f'<dt>{labels["main_finding"]}</dt><dd>{escaped_text(card["main_finding"])}</dd>'
            f'<dt>{labels["causal_strength"]}</dt><dd>{escape(card["causal_strength"])}</dd>'
            f'<dt>{labels["generalizability"]}</dt><dd>{escape(card["generalizability"])}</dd>'
            f'</dl><div class="card-limitations"><strong>{labels["limitations"]}</strong>'
            f'{render_list(card["limitations"], labels["none_recorded"])}</div></details>'
        )

    claim_cards = []
    for claim in debate["claim_ledger"]:
        evidence = ", ".join(claim["evidence"]) or labels["none_recorded"]
        falsifier = ""
        if claim["falsifier"]:
            falsifier = (
                f'<div class="falsifier"><strong>{labels["falsifier"]}</strong>'
                f'<p>{escaped_text(claim["falsifier"])}</p></div>'
            )
        claim_cards.append(
            f'<li class="claim-card claim-{escape(claim["status"], quote=True)}">'
            f'<header><code>{escape(claim["id"])}</code><span>'
            f'{escape(CLAIM_STATUS_LABELS[debate["lang"]][claim["status"]])}</span></header>'
            f'<p>{escaped_text(claim["text"])}</p><small>{escape(claim["type"])} · '
            f'{labels["evidence"]}: {escape(evidence)}</small>{falsifier}</li>'
        )

    belief_cards = []
    for update in debate["belief_updates"]:
        camp_index, camp = camp_by_id[update["camp"]]
        before = f'{update["before"]:.0%}'
        after = f'{update["after"]:.0%}'
        belief_cards.append(
            f'<article class="belief-update camp-{camp_index}"><header><strong>'
            f'{escape(camp["name"])}</strong><span>{escape(update["phase"])}</span></header>'
            f'<div class="belief-shift"><b>{before}</b><span aria-hidden="true">→</span>'
            f'<b>{after}</b></div><p>{escaped_text(update["reason"])}</p></article>'
        )

    belief_section = ""
    if belief_cards:
        belief_section = (
            f'<section class="summary-section belief-section"><h3>{labels["key_updates"]}</h3>'
            f'<div class="belief-updates">{"".join(belief_cards)}</div></section>'
        )

    ledger_section = ""
    if claim_cards:
        ledger_section = (
            f'<section class="summary-section ledger-section"><h3>{labels["claim_ledger"]}</h3>'
            f'<ol class="claim-ledger">{"".join(claim_cards)}</ol></section>'
        )

    evidence_section = ""
    if evidence_cards:
        evidence_section = (
            f'<section class="evidence-panel" aria-label="{escape(labels["evidence_cards"], quote=True)}">'
            f'<header><h2>{labels["evidence_cards"]}</h2><p>{len(evidence_cards)}</p></header>'
            f'<div class="evidence-grid">{"".join(evidence_cards)}</div></section>'
        )

    decision_rule_section = ""
    if debate["decision_rule"]:
        rule = debate["decision_rule"]
        threshold = (
            f'{rule["threshold"]:.0%}' if rule["threshold"] is not None else labels["none_recorded"]
        )
        decision_rule_section = (
            f'<section class="decision-rule" aria-label="{escape(labels["decision_rule"], quote=True)}">'
            f'<header><h2>{labels["decision_rule"]}</h2><span>{escape(debate["proposition_type"])}</span></header>'
            f'<dl><dt>{labels["target"]}</dt><dd>{escaped_text(rule["target"])}</dd>'
            f'<dt>{labels["horizon"]}</dt><dd>{escaped_text(rule["horizon"])}</dd>'
            f'<dt>{labels["yes_condition"]}</dt><dd>{escaped_text(rule["yes_condition"])}</dd>'
            f'<dt>{labels["no_condition"]}</dt><dd>{escaped_text(rule["no_condition"])}</dd>'
            f'<dt>{labels["resolution_source"]}</dt><dd>{escaped_text(rule["resolution_source"])}</dd>'
            f'<dt>{labels["threshold"]}</dt><dd>{threshold}</dd></dl></section>'
        )

    forecast_section = ""
    if debate["forecast_records"]:
        checkpoint_order = {
            "PRIOR": 0,
            "AFTER_CROSS_EXAM": 1,
            "AFTER_CRUCIAL_DISPUTE": 2,
            "FINAL": 3,
        }
        forecast_cards = []
        for camp_id, (camp_index, camp) in camp_by_id.items():
            records = [
                record for record in debate["forecast_records"] if record["camp"] == camp_id
            ]
            if not records:
                continue
            records.sort(
                key=lambda record: (
                    checkpoint_order[record["checkpoint"]], record["cycle"] or 0
                )
            )
            points = []
            for record in records:
                checkpoint = record["checkpoint"].replace("_", " ")
                if record["cycle"] is not None:
                    checkpoint += f' {record["cycle"]}'
                points.append(
                    f'<li><span>{escape(checkpoint)}</span><strong>{record["probability"]:.0%}</strong>'
                    f'<small>{record["lower"]:.0%}–{record["upper"]:.0%}</small>'
                    f'<p>{escaped_text(record["rationale"])}</p></li>'
                )
            forecast_cards.append(
                f'<article class="forecast-card camp-{camp_index}"><header><span class="avatar" aria-hidden="true">'
                f'{escape(camp["name"][0].upper())}</span><strong>{escape(camp["name"])}</strong></header>'
                f'<ol>{"".join(points)}</ol></article>'
            )
        forecast_section = (
            f'<section class="analysis-panel forecast-panel"><header><div><h2>{labels["forecast_trajectory"]}</h2>'
            f'<p>{labels["forecast_disclaimer"]}</p></div></header>'
            f'<div class="forecast-grid">{"".join(forecast_cards)}</div></section>'
        )

    evidence_link_section = ""
    if debate["evidence_links"]:
        link_cards = []
        for link in debate["evidence_links"]:
            link_cards.append(
                f'<article class="link-card"><header><code>{escape(link["evidence_id"])} → '
                f'{escape(link["claim_id"])}</code></header>'
                f'<dl><dt>{labels["supports"]}</dt><dd>{escaped_text(link["supports"])}</dd>'
                f'<dt>{labels["does_not_establish"]}</dt><dd>{escaped_text(link["does_not_establish"])}</dd>'
                f'<dt>{labels["directness"]}</dt><dd>{escape(link["directness"])}</dd>'
                f'<dt>{labels["independence"]}</dt><dd>{escape(link["independence"])}</dd>'
                f'<dt>{labels["causal_strength"]}</dt><dd>{escape(link["causal_strength"])}</dd>'
                f'<dt>{labels["generalizability"]}</dt><dd>{escape(link["generalizability"])}</dd>'
                f'<dt>{labels["temporal_relevance"]}</dt><dd>{escape(link["temporal_relevance"])}</dd>'
                f'</dl></article>'
            )
        evidence_link_section = (
            f'<section class="analysis-panel link-panel"><header><h2>{labels["evidence_links"]}</h2>'
            f'<span>{len(link_cards)}</span></header><div class="link-grid">{"".join(link_cards)}</div></section>'
        )

    needed_evidence_section = ""
    if debate["needed_evidence"]:
        needed_cards = []
        for item in debate["needed_evidence"]:
            claim_ids = ", ".join(item["resolves_claims"]) or labels["none_recorded"]
            needed_cards.append(
                f'<article class="needed-card"><header><code>{escape(item["id"])}</code>'
                f'<strong>{escaped_text(item["observation"])}</strong></header>'
                f'<dl><dt>{labels["resolves_claims"]}</dt><dd>{escape(claim_ids)}</dd>'
                f'<dt>{labels["expected_update"]}</dt><dd>{escaped_text(item["expected_update"])}</dd>'
                f'<dt>{labels["collection"]}</dt><dd>{escaped_text(item["collection"])}</dd></dl></article>'
            )
        needed_evidence_section = (
            f'<section class="analysis-panel needed-panel"><header><h2>{labels["needed_evidence"]}</h2>'
            f'<span>{len(needed_cards)}</span></header><div class="needed-grid">{"".join(needed_cards)}</div></section>'
        )

    status_class = re.sub(r"[^a-z0-9_-]", "-", debate["status"].lower())
    return f"""<!doctype html>
<html lang="{debate['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(debate['title'])}</title>
<style>
:root{{--bg:#f4f5f8;--surface:#fff;--ink:#1f2430;--muted:#687083;--line:#dfe2e8;--accent:#282d3a;}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}}
button{{font:inherit}}
.debate-shell{{max-width:1180px;margin:0 auto;padding:28px}}
.hero{{background:linear-gradient(135deg,#242936,#343b4d);color:#fff;border-radius:22px;padding:28px;box-shadow:0 16px 40px #24293622}}
.eyebrow{{margin:0 0 8px;color:#cbd1df;font-size:12px;font-weight:800;letter-spacing:.12em;text-transform:uppercase}}
h1{{margin:0;font-size:clamp(24px,4vw,38px);line-height:1.15}}
.proposition{{max-width:820px;margin:14px 0 20px;color:#edf0f6;font-size:17px}}
.hero-meta{{display:flex;flex-wrap:wrap;gap:8px}}
.pill{{display:inline-flex;align-items:center;border:1px solid #ffffff2e;border-radius:999px;padding:6px 11px;background:#ffffff12;color:#f5f6fa;font-size:12px;font-weight:750}}
.status{{background:#e7e9ef;color:#303746;border-color:transparent}}
.status.final_consensus,.status.final_winner{{background:#c8ffcf;color:#18341d}}
.status.consensus_with_reservations{{background:#d9f5d3;color:#264d22}}
.status.deadlock,.status.true_deadlock{{background:#ffe7a3;color:#5a3d00}}
.status.incomplete{{background:#ffd5d5;color:#671d1d}}
.layout{{display:grid;grid-template-columns:minmax(0,1fr) 310px;gap:22px;margin-top:22px;align-items:start}}
.layout>*{{min-width:0}}
.chat-panel,.summary-panel,.evidence-panel,.analysis-panel{{background:var(--surface);border:1px solid var(--line);border-radius:18px;box-shadow:0 8px 28px #2529360d}}
.chat-toolbar{{position:sticky;top:0;z-index:3;padding:16px 18px;border-bottom:1px solid var(--line);background:#fffffff2;backdrop-filter:blur(12px);border-radius:18px 18px 0 0}}
.chat-toolbar h2,.summary-panel h2{{margin:0 0 12px;font-size:17px}}
.filters{{display:flex;gap:8px;overflow-x:auto;padding-bottom:2px}}
.filter{{white-space:nowrap;border:1px solid var(--line);border-radius:999px;padding:7px 11px;background:#fff;color:var(--muted);cursor:pointer}}
.filter:hover,.filter:focus-visible{{border-color:#8d95a7;color:var(--ink);outline:none}}
.filter.active{{background:var(--accent);border-color:var(--accent);color:#fff}}
.transcript{{display:flex;flex-direction:column;gap:16px;padding:22px}}
.message{{display:flex;gap:11px;align-items:flex-start;max-width:88%}}
.message[hidden]{{display:none}}
.avatar{{display:grid;place-items:center;flex:0 0 36px;width:36px;height:36px;border-radius:12px;background:var(--camp-ink,#4e5668);color:#fff;font-weight:850}}
.bubble{{min-width:0;border:1px solid color-mix(in srgb,var(--camp-ink) 18%,white);border-radius:5px 16px 16px;padding:12px 14px;background:var(--camp-tint)}}
.bubble header,.system header{{display:flex;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:5px}}
.message-meta,.system time{{color:var(--muted);font-size:12px}}
.message p{{margin:0;overflow-wrap:anywhere}}
.resolution .bubble{{box-shadow:inset 3px 0 var(--camp-ink)}}
.system,.intervention{{align-self:center;max-width:92%;align-items:center;border-radius:14px;padding:11px 14px;background:#f1f3f7;color:#485064}}
.intervention{{background:#fff3df;color:#68430f;border:1px solid #f0d39d}}
.system-icon{{display:grid;place-items:center;flex:0 0 26px;width:26px;height:26px;border-radius:50%;background:#fff;font-weight:900}}
.kind-badge{{border-radius:999px;padding:2px 7px;background:#fff;font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.06em}}
.summary-panel{{position:sticky;top:20px;padding:20px}}
.decision{{margin:0;padding:13px;border-left:4px solid #697386;background:#f3f4f7;border-radius:4px 12px 12px 4px;font-weight:680;overflow-wrap:anywhere}}
.decision-rule{{margin-top:18px;padding:14px;border:1px solid #ffffff24;border-radius:14px;background:#ffffff0b}}
.decision-rule header{{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:10px}}
.decision-rule h2{{margin:0;font-size:14px}}.decision-rule header span{{border-radius:999px;padding:3px 8px;background:#ffffff17;font-size:11px;font-weight:800}}
.decision-rule dl{{display:grid;grid-template-columns:140px minmax(0,1fr);gap:5px 10px;margin:0}}
.decision-rule dt{{color:#cbd1df;font-size:11px;font-weight:750}}.decision-rule dd{{margin:0;color:#f5f6fa;overflow-wrap:anywhere}}
.summary-section{{margin-top:20px}}
.summary-section h3{{margin:0 0 8px;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}}
.summary-section ul{{margin:0;padding-left:20px}}
.summary-section li+li{{margin-top:7px}}
.empty{{margin:0;color:var(--muted);font-style:italic}}
.participants{{display:grid;gap:9px;margin:0;padding:0;list-style:none}}
.participant{{display:flex;align-items:center;gap:9px;font-weight:680}}
.participant small{{display:block;color:var(--muted);font-size:11px;font-weight:600}}
.participant .avatar{{width:28px;height:28px;flex-basis:28px;border-radius:9px;font-size:12px}}
.claim-ledger{{display:grid;gap:9px;margin:0;padding:0;list-style:none}}
.claim-card{{border:1px solid var(--line);border-left:4px solid #9299a8;border-radius:10px;padding:9px;background:#fafbfc}}
.claim-card header{{display:flex;align-items:center;justify-content:space-between;gap:8px}}
.claim-card header span{{border-radius:999px;padding:2px 7px;background:#eef0f4;color:var(--muted);font-size:10px;font-weight:800}}
.claim-card p{{margin:6px 0;font-size:13px}}
.claim-card small{{color:var(--muted);overflow-wrap:anywhere}}
.falsifier{{margin-top:8px;padding-top:8px;border-top:1px dashed var(--line)}}.falsifier strong{{font-size:11px;color:#8b3f3f}}.falsifier p{{margin:3px 0 0}}
.claim-agreed{{border-left-color:#3b8d4b}}.claim-agreed header span{{background:#ddf4df;color:#235d2e}}
.claim-disputed,.claim-definitional_dispute{{border-left-color:#d18c24}}.claim-disputed header span,.claim-definitional_dispute header span{{background:#fff0d6;color:#724a0c}}
.claim-unsupported{{border-left-color:#b44747}}.claim-unsupported header span{{background:#ffe3e3;color:#7b2828}}
.belief-updates{{display:grid;gap:9px}}
.belief-update{{border:1px solid color-mix(in srgb,var(--camp-ink) 20%,white);border-radius:11px;padding:10px;background:var(--camp-tint)}}
.belief-update header{{display:flex;justify-content:space-between;gap:8px;font-size:12px}}
.belief-update header span{{color:var(--muted)}}
.belief-shift{{display:flex;align-items:center;gap:8px;margin:7px 0;color:var(--camp-ink);font-size:17px}}
.belief-update p{{margin:0;font-size:12px}}
.evidence-panel{{margin-top:22px;padding:20px}}
.evidence-panel>header{{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:14px}}
.evidence-panel h2{{margin:0;font-size:18px}}.evidence-panel>header p{{margin:0;color:var(--muted)}}
.evidence-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:12px}}
.evidence-card{{border:1px solid var(--line);border-radius:13px;background:#fafbfc;overflow:hidden}}
.evidence-card summary{{display:flex;align-items:center;gap:9px;padding:13px;cursor:pointer}}
.evidence-card summary:focus-visible{{outline:3px solid #8294d6;outline-offset:-3px}}
.evidence-id{{border-radius:8px;padding:3px 7px;background:#e8ebf2;color:#424a5b;font:800 12px ui-monospace,SFMono-Regular,Consolas,monospace}}
.evidence-card dl{{display:grid;grid-template-columns:120px 1fr;gap:7px 10px;margin:0;padding:0 13px 13px}}
.evidence-card dt{{color:var(--muted);font-size:12px;font-weight:750}}.evidence-card dd{{margin:0;overflow-wrap:anywhere}}
.evidence-card a{{color:#304fa3}}.card-limitations{{border-top:1px solid var(--line);padding:11px 13px}}.card-limitations ul{{margin:6px 0 0;padding-left:20px}}
.analysis-panel{{margin-top:22px;padding:20px}}
.analysis-panel>header{{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:14px}}
.analysis-panel h2{{margin:0;font-size:18px}}.analysis-panel>header p{{margin:3px 0 0;color:var(--muted)}}.analysis-panel>header>span{{color:var(--muted)}}
.forecast-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px}}
.forecast-card{{border:1px solid color-mix(in srgb,var(--camp-ink) 20%,white);border-radius:13px;background:var(--camp-tint);overflow:hidden}}
.forecast-card>header{{display:flex;align-items:center;gap:9px;padding:12px 13px;border-bottom:1px solid color-mix(in srgb,var(--camp-ink) 14%,white)}}
.forecast-card>header .avatar{{width:28px;height:28px;flex-basis:28px;border-radius:9px;font-size:12px}}
.forecast-card ol{{display:grid;gap:0;margin:0;padding:0;list-style:none}}
.forecast-card li{{display:grid;grid-template-columns:minmax(0,1fr) auto auto;gap:8px;padding:10px 13px;align-items:baseline}}
.forecast-card li+li{{border-top:1px solid color-mix(in srgb,var(--camp-ink) 12%,white)}}
.forecast-card li span{{font-size:11px;font-weight:800;color:var(--muted)}}.forecast-card li strong{{font-size:19px;color:var(--camp-ink)}}.forecast-card li small{{color:var(--muted)}}
.forecast-card li p{{grid-column:1/-1;margin:0;font-size:12px}}
.link-grid,.needed-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:12px}}
.link-card,.needed-card{{border:1px solid var(--line);border-radius:13px;padding:13px;background:#fafbfc}}
.link-card header,.needed-card header{{display:flex;align-items:flex-start;gap:9px;margin-bottom:10px}}.link-card code,.needed-card code{{flex:0 0 auto;border-radius:7px;padding:3px 7px;background:#e8ebf2}}
.link-card dl,.needed-card dl{{display:grid;grid-template-columns:145px minmax(0,1fr);gap:6px 10px;margin:0}}
.link-card dt,.needed-card dt{{color:var(--muted);font-size:11px;font-weight:750}}.link-card dd,.needed-card dd{{margin:0;overflow-wrap:anywhere}}
.needed-panel{{border-color:#cbd7c4;background:#fbfdf9}}.needed-card{{background:#fff}}
{''.join(camp_styles)}
@media (max-width: 720px){{
  .debate-shell{{padding:12px}}
  .hero{{padding:21px;border-radius:17px}}
  .decision-rule dl{{grid-template-columns:1fr;gap:2px}}
  .decision-rule dd+dt{{margin-top:6px}}
  .pill.status{{max-width:100%;overflow-wrap:anywhere}}
  .layout{{grid-template-columns:1fr}}
  .summary-panel{{position:static;order:-1}}
  .message{{max-width:100%}}
  .transcript{{padding:16px 12px}}
  .chat-toolbar{{padding:14px 12px}}
  .evidence-panel{{padding:15px}}
  .analysis-panel{{padding:15px}}
  .evidence-grid{{grid-template-columns:1fr}}
  .forecast-grid,.link-grid,.needed-grid{{grid-template-columns:1fr}}
  .link-card dl,.needed-card dl{{grid-template-columns:1fr;gap:2px}}
  .link-card dd+dt,.needed-card dd+dt{{margin-top:7px}}
  .evidence-card dl{{grid-template-columns:1fr;gap:2px}}
  .evidence-card dd+dt{{margin-top:7px}}
}}
@media (prefers-reduced-motion:reduce){{*{{scroll-behavior:auto!important}}}}
</style>
</head>
<body>
<main class="debate-shell">
  <header class="hero">
    <p class="eyebrow">{labels['title_prefix']} · {escape(debate['evidence_mode'])}</p>
    <h1>{escape(debate['title'])}</h1>
    <p class="proposition">{escaped_text(debate['proposition'])}</p>
    <div class="hero-meta"><span class="pill status {status_class}">{escape(debate['status'])}</span><span class="pill">{len(camps)} {labels['camp_count']}</span><span class="pill">{len(debate['messages'])} {labels['event_count']}</span></div>
    {decision_rule_section}
  </header>
  <div class="layout">
    <section class="chat-panel" aria-label="Debate transcript">
      <div class="chat-toolbar">
        <h2>{labels['group_discussion']}</h2>
        <div class="filters" aria-label="Filter transcript">{''.join(filter_buttons)}</div>
      </div>
      <div class="transcript">{''.join(message_cards)}</div>
    </section>
    <aside class="summary-panel" aria-label="Debate result">
      <h2>{labels['resolution']}</h2>
      <p class="decision">{escaped_text(summary['decision'])}</p>
      <section class="summary-section"><h3>{labels['common_ground']}</h3>{render_list(summary['agreed_points'], labels['none_recorded'])}</section>
      <section class="summary-section"><h3>{labels['unresolved']}</h3>{render_list(summary['unresolved_objections'], labels['none_recorded'])}</section>
      {belief_section}
      {ledger_section}
      <section class="summary-section"><h3>{labels['participants']}</h3><ul class="participants">{''.join(participant_cards)}</ul></section>
    </aside>
  </div>
  {needed_evidence_section}
  {forecast_section}
  {evidence_link_section}
  {evidence_section}
</main>
<script>
document.querySelectorAll('.filter').forEach((button) => {{
  button.addEventListener('click', () => {{
    const selected = button.dataset.filter;
    document.querySelectorAll('.filter').forEach((item) => {{
      const active = item === button;
      item.classList.toggle('active', active);
      item.setAttribute('aria-pressed', String(active));
    }});
    document.querySelectorAll('.message').forEach((message) => {{
      message.hidden = selected !== 'all' && message.dataset.camp !== selected;
    }});
  }});
}});
</script>
</body>
</html>
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="UTF-8 debate transcript JSON")
    parser.add_argument("--output", "-o", required=True, type=Path, help="HTML output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    document = json.loads(args.input.read_text(encoding="utf-8"))
    rendered = render_document(document)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(f"Rendered debate chat: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

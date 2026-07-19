#!/usr/bin/env python3
"""Synthesize estimate centers with one effective vote per assumption cluster."""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path
from typing import Any


REQUIRED_METHOD_FIELDS = (
    "method",
    "cluster",
    "base_hours",
    "count_basis",
    "productivity_basis",
    "lifecycle_basis",
    "risk_basis",
    "status",
)

REJECTION_DISPOSITIONS = {
    "scope": "rejected_scope_mismatch",
    "unit": "rejected_unit_mismatch",
    "lifecycle": "rejected_lifecycle_mismatch",
    "evidence": "rejected_evidence_mismatch",
}

GENERIC_REJECTION_REASONS = {
    "best matches accepted delivery scope",
    "best matches target deliverable",
    "not applicable",
    "not preferred",
}


def arithmetic_median(values: list[float]) -> float:
    if not values:
        raise ValueError("median requires at least one value")
    return float(statistics.median(values))


def validate_method(method: dict[str, Any]) -> None:
    missing = [field for field in REQUIRED_METHOD_FIELDS if method.get(field) in (None, "")]
    if missing:
        raise ValueError(f"method is missing required fields: {', '.join(missing)}")
    if method["status"] not in {"plausible", "rejected"}:
        raise ValueError(f"unsupported method status: {method['status']}")
    if method["status"] == "rejected":
        rejection_reason = str(method.get("rejection_reason", "")).strip()
        if not rejection_reason:
            raise ValueError(f"rejected method `{method['method']}` requires rejection_reason")
        if rejection_reason.casefold() in GENERIC_REJECTION_REASONS:
            raise ValueError(f"rejected method `{method['method']}` requires evidence-specific rejection_reason")
        rejection_dimension = str(method.get("rejection_dimension", "")).strip().casefold()
        if rejection_dimension not in REJECTION_DISPOSITIONS:
            allowed = ", ".join(sorted(REJECTION_DISPOSITIONS))
            raise ValueError(
                f"rejected method `{method['method']}` requires rejection_dimension in: {allowed}"
            )
        if not str(method.get("evidence_locator", "")).strip():
            raise ValueError(f"rejected method `{method['method']}` requires evidence_locator")
    if float(method["base_hours"]) < 0:
        raise ValueError(f"method `{method['method']}` has negative base_hours")


def count_basis_matches(metric: str, count_basis: str) -> bool:
    metric_key = metric.casefold()
    basis_key = count_basis.casefold()
    if "uucp" in metric_key or "ucp" in metric_key:
        return "use-case" in basis_key or "use case" in basis_key or "uucp" in basis_key
    if metric_key in {"fp", "ufp", "function points", "function-point"}:
        return "function" in basis_key or "fp" in basis_key
    return metric_key in basis_key


def evaluate_count_audit(audit: dict[str, Any], methods: list[dict[str, Any]]) -> dict[str, Any]:
    explicit = float(audit["explicit_value"])
    derived = float(audit["derived_value"])
    untraced = float(audit.get("untraced_inferred_value", 0))
    if explicit <= 0:
        raise ValueError(f"count audit `{audit.get('metric')}` requires explicit_value > 0")
    inflation_ratio = (derived - explicit) / explicit
    if untraced > 0:
        status = "STOP_UNTRACED_COUNT"
    elif inflation_ratio > 0.25:
        status = "SENSITIVITY_ONLY_COUNT_INFLATION"
    else:
        status = "PASS"
    affected_methods = [
        method["method"]
        for method in methods
        if count_basis_matches(str(audit["metric"]), str(method["count_basis"]))
    ]
    return {
        **audit,
        "inflation_ratio": inflation_ratio,
        "status": status,
        "affected_methods": affected_methods,
    }


def synthesize(data: dict[str, Any]) -> dict[str, Any]:
    methods = [dict(method) for method in data.get("methods", [])]
    if not methods:
        raise ValueError("at least one method is required")
    for method in methods:
        validate_method(method)
    method_names = [str(method["method"]) for method in methods]
    if len(method_names) != len(set(method_names)):
        raise ValueError("method names must be unique")

    count_audits = [evaluate_count_audit(audit, methods) for audit in data.get("count_audits", [])]
    stopped_methods = {
        name
        for audit in count_audits
        if audit["status"] != "PASS"
        for name in audit["affected_methods"]
    }

    parent = list(range(len(methods)))

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(left: int, right: int) -> None:
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    generic_bases = {
        "",
        "unknown",
        "n/a",
        "not applicable",
        "method-local",
        "method local",
        "driver equation",
        "measured or stated coefficient",
        "stated lifecycle",
    }
    basis_fields = ("count_basis", "productivity_basis", "lifecycle_basis", "risk_basis")
    for left_index, left in enumerate(methods):
        for right_index in range(left_index + 1, len(methods)):
            right = methods[right_index]
            same_declared_cluster = str(left["cluster"]) == str(right["cluster"])
            shared_dominant_basis = any(
                str(left[field]).strip().casefold() == str(right[field]).strip().casefold()
                and str(left[field]).strip().casefold() not in generic_bases
                for field in basis_fields
            )
            if same_declared_cluster or shared_dominant_basis:
                union(left_index, right_index)

    grouped: dict[int, list[dict[str, Any]]] = {}
    for index, method in enumerate(methods):
        grouped.setdefault(find(index), []).append(method)

    cluster_votes: list[dict[str, Any]] = []
    for cluster_methods in grouped.values():
        declared_clusters = sorted({str(method["cluster"]) for method in cluster_methods})
        cluster = "+".join(declared_clusters)
        plausible = [method for method in cluster_methods if method["status"] == "plausible"]
        rejected = [method for method in cluster_methods if method["status"] == "rejected"]
        eligible_methods = [method for method in plausible if method["method"] not in stopped_methods]
        visible_methods = eligible_methods or plausible
        representative = (
            arithmetic_median([float(method["base_hours"]) for method in visible_methods])
            if visible_methods
            else None
        )
        eligible = bool(eligible_methods)
        blocked_by = sorted(method["method"] for method in plausible if method["method"] in stopped_methods)
        if eligible:
            disposition = "adopted"
        elif plausible:
            disposition = "sanity_only"
        else:
            rejection_dimensions = {str(method["rejection_dimension"]).casefold() for method in rejected}
            disposition = (
                REJECTION_DISPOSITIONS[next(iter(rejection_dimensions))]
                if len(rejection_dimensions) == 1
                else "rejected_evidence_mismatch"
            )
        cluster_votes.append(
            {
                "cluster": cluster,
                "declared_clusters": declared_clusters,
                "methods": [method["method"] for method in cluster_methods],
                "shared_assumptions": {
                    field: sorted({str(method[field]) for method in cluster_methods})
                    for field in basis_fields
                },
                "representative_hours": representative,
                "effective_vote": 1 if eligible else 0,
                "eligible": eligible,
                "anchor_disposition": disposition,
                "blocked_methods": blocked_by,
                "rejections": [
                    {
                        "method": method["method"],
                        "dimension": method["rejection_dimension"],
                        "evidence_locator": method["evidence_locator"],
                        "reason": method["rejection_reason"],
                    }
                    for method in rejected
                ],
            }
        )

    eligible_clusters = [row for row in cluster_votes if row["eligible"]]
    if not eligible_clusters:
        raise ValueError("no eligible method-dependence clusters remain")
    planning_center = arithmetic_median([row["representative_hours"] for row in eligible_clusters])

    close_pairs: list[dict[str, Any]] = []
    for index, left in enumerate(eligible_clusters):
        for right in eligible_clusters[index + 1 :]:
            midpoint = (left["representative_hours"] + right["representative_hours"]) / 2
            relative_gap = abs(left["representative_hours"] - right["representative_hours"]) / midpoint if midpoint else 0
            if relative_gap <= 0.20:
                close_pairs.append(
                    {
                        "clusters": [left["cluster"], right["cluster"]],
                        "relative_gap": relative_gap,
                    }
                )

    for row in cluster_votes:
        if row["anchor_disposition"].startswith("rejected_"):
            row["decision_impact"] = "excluded_from_center_as_evidence_rejected"
        elif not row["eligible"]:
            row["decision_impact"] = "excluded_from_center_by_count_guard"
        elif row["representative_hours"] < planning_center:
            row["decision_impact"] = "pulls_center_down"
        elif row["representative_hours"] > planning_center:
            row["decision_impact"] = "pulls_center_up"
        else:
            row["decision_impact"] = "sets_center"

    return {
        "case_id": data.get("case_id"),
        "cluster_votes": cluster_votes,
        "planning_center_hours": planning_center,
        "convergence_confidence": "supported" if close_pairs else "not_supported",
        "independent_convergence_pairs": close_pairs,
        "count_audits": count_audits,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON method/cluster input")
    parser.add_argument("--output", type=Path, help="Optional JSON output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = synthesize(json.loads(args.input.read_text(encoding="utf-8")))
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

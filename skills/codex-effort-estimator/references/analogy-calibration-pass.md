# Analogy Calibration Pass

Use this reference when comparable historical projects, actuals, prior estimates, or delivery metrics are available.

This pass calibrates an estimate. It should not replace WBS or PERT with an unexplained average.

## Scope

Compare the current project with historical anchors and return adjustment candidates, confidence, and variance explanations. Do not estimate price unless explicitly asked.

## Procedure

1. List current-scope sources and historical-anchor sources inspected.
2. Summarize each historical anchor:
   - Delivered scope.
   - Actual effort, estimate, or known delivery duration.
   - Team size and skill assumptions when known.
   - Technology, domain, integration, report, data, and acceptance complexity.
   - What was excluded, unfinished, or absorbed outside the recorded effort.
3. Compare current scope against anchors by dimension:
   - Functional size.
   - Report/output fidelity.
   - Data migration and quality.
   - Integration and environment complexity.
   - Requirements clarity and stakeholder review load.
   - Testing, acceptance, documentation, and handoff burden.
4. Produce calibration factors or adjustment candidates only where the comparison is credible.
5. When organization-specific productivity baselines exist, compare current scope against them, such as person-days per screen, report, integration, CRUD module, migration object, or KLOC.
6. Explain why the current WBS/PERT should stay unchanged, move up/down, or widen.

## Post-delivery calibration ledger

Use this procedure after actual effort is accepted. It closes the
estimate-to-actual loop; it is not part of changing an in-flight estimate.

1. Copy `calibration-ledger-template.csv` to the approved project metrics location, or append to the existing approved ledger.
2. Use a non-sensitive `project_alias` and a stable `scope_fingerprint`. Do not record customer names, prices, credentials, or source-document contents.
3. Preserve the original estimate, method, size basis, size value, coefficient source, and low/center/high values as they were at the decision date.
4. Record actual effort only after its reporting period, included lifecycle, and scope are accepted. Set `actual_scope_match` to `false` when delivered scope differs; do not use that row as a direct coefficient without normalization.
5. When `size_value > 0`, calculate `actual_productivity_pd_per_size = actual_effort_pd / size_value`.
6. Calculate `signed_relative_error = (estimate_center_pd - actual_effort_pd) / actual_effort_pd` and `absolute_relative_error = abs(signed_relative_error)`.
7. Keep every observation. Do not overwrite an inconvenient row or promote one result into an organizational baseline.
8. During the next estimate, prefer comparable local actual rows over compatible measured public benchmarks, and prefer both over heuristic or judgment coefficients.

If the repository cannot store the actual because it is private, record the row in the approved private metrics location and cite only a sanitized aggregate or opaque anchor ID in estimate artifacts.

## Output Schema

Return:

- Current sources and historical anchors inspected.
- Anchor table with `Anchor`, `Scope`, `Actual/Estimate`, `Similarity`, `Differences`, and `Reliability`.
- Calibration table with `Dimension`, `Current vs anchor`, `Implication`, and `Adjustment candidate`.
- Productivity baseline comparison when actual organizational metrics are available.
- Recommended calibration action: keep, shift center, widen range, or reject anchor.
- Confidence level.
- What historical data would improve calibration.
- Ledger status: not yet due, recorded, scope-mismatched, or unavailable, with the approved location or sanitized anchor ID when one exists.

Do not use conclusions from other estimators except the current WBS/PERT total if the assignment explicitly asks you to calibrate it.

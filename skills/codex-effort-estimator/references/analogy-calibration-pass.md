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
5. Explain why the current WBS/PERT should stay unchanged, move up/down, or widen.

## Output Schema

Return:

- Current sources and historical anchors inspected.
- Anchor table with `Anchor`, `Scope`, `Actual/Estimate`, `Similarity`, `Differences`, and `Reliability`.
- Calibration table with `Dimension`, `Current vs anchor`, `Implication`, and `Adjustment candidate`.
- Recommended calibration action: keep, shift center, widen range, or reject anchor.
- Confidence level.
- What historical data would improve calibration.

Do not use conclusions from other estimators except the current WBS/PERT total if the assignment explicitly asks you to calibrate it.

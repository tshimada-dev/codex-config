# PERT Pass

Use this reference for an independent three-point estimate when tasks or deliverables can be decomposed into estimateable units.

## Scope

Estimate human engineering effort in person-days. Do not estimate price, rates, or AI-agent wall-clock time unless explicitly asked.

## Procedure

1. List the source files or text blocks inspected.
2. Convert requirements into task-sized units. If a unit is still broad, split it before estimating.
3. For each unit, estimate:
   - Optimistic: stable requirements and no major blockers.
   - Most likely: normal clarification and rework.
   - Pessimistic: credible risks materialize without catastrophic scope change.
4. Calculate PERT expected value:

```text
expected = (optimistic + 4 * most_likely + pessimistic) / 6
standard_deviation = (pessimistic - optimistic) / 6
```

5. Sum optimistic, most likely, pessimistic, and expected values.
6. Identify dependency, review-wait, data-quality, integration, report-fidelity, and acceptance risks.
7. State confidence and the facts that would materially change the estimate.

## Output Schema

Return:

- Source files inspected.
- Task table with `Task`, `Basis`, `Optimistic`, `Most likely`, `Pessimistic`, `Expected`, and `Notes`.
- Total optimistic / most likely / pessimistic / expected person-days.
- Optional standard deviation or confidence band when useful.
- Assumptions and exclusions.
- Major risk drivers.
- Confidence level.
- Confirmation questions that could narrow the range.

Do not use conclusions from other estimators. Do not treat public-sector/report review as an additive correction unless explicitly assigned to do so.

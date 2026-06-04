# PERT Pass

Use this reference for an independent three-point estimate when tasks or deliverables can be decomposed into estimateable units.

Keep two concepts separate:

- Independent PERT pass: a method pass that produces its own task-level three-point estimate.
- Variance aggregation: a calculation that can be applied to any existing low / most likely / high data, including WBS rows.

If this independent PERT pass is skipped but WBS rows have three-point values, still apply variance aggregation in parent synthesis and label it `WBS-derived variance aggregation`. Do not count that derived CI as a separate independent estimate.

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

5. Sum expected values, not the optimistic and pessimistic endpoints. Endpoint sums imply all tasks hit best or worst case together and usually overstate the range.
6. Aggregate uncertainty with variance:

```text
task_variance = standard_deviation ^ 2
total_expected = sum(expected)
total_standard_deviation = sqrt(sum(task_variance))
confidence_low = total_expected - z * total_standard_deviation
confidence_high = total_expected + z * total_standard_deviation
```

Use `z = 1.282` for about 80% confidence, `z = 1.645` for about 90%, and `z = 1.960` for about 95%. Use 90% as the default stakeholder range unless another confidence level is requested.

7. If tasks are strongly correlated, such as many tasks depending on the same unresolved requirement or integration, widen the confidence interval or state a correlated-risk scenario separately. Do not silently fall back to simple endpoint sums.
8. Identify dependency, review-wait, data-quality, integration, report-fidelity, and acceptance risks.
9. If AI coding assistance is explicitly in scope, keep raw human effort values but label which tasks are routine coding, code-adjacent, or non-reducible for downstream adjustment.
10. State confidence and the facts that would materially change the estimate.

## Output Schema

Return:

- Source files inspected.
- Task table with `Task`, `Basis`, `Optimistic`, `Most likely`, `Pessimistic`, `Expected`, `Standard deviation`, `Variance`, and `Notes`.
- Total expected person-days and confidence interval using variance aggregation.
- Correlated-risk scenario when task outcomes are not reasonably independent.
- AI-reducibility notes when AI coding assistance is explicitly assumed.
- Assumptions and exclusions.
- Major risk drivers.
- Confidence level.
- Confirmation questions that could narrow the range.

Do not use conclusions from other estimators. Do not treat public-sector/report review as an additive correction unless explicitly assigned to do so.

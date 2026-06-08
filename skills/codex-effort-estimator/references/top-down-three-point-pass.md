# Top-Down Three-Point Pass

Use this reference for an independent whole-project three-point estimate. This is intentionally coarse: it estimates the total delivery effort directly from scope, constraints, and comparable mental anchors, without decomposing into WBS lines.

Run this pass for non-trivial estimates as a fast independent anchor, especially when WBS anchoring risk is a concern. Treat it as lower precision than WBS, but useful for detecting implausible WBS results.

## Scope

Estimate human engineering effort in person-days. Do not estimate price, rates, or AI-agent wall-clock time unless explicitly asked.

## Independence Rules

1. Do not read or use WBS totals, WBS line estimates, WBS-derived PERT, component-unit totals, parent synthesis, prior estimate artifacts, or expected final ranges.
2. Do not build a hidden WBS. Use broad scope signals and whole-project reasoning.
3. State the mental anchors used, such as "small report-heavy internal tool", "medium public-sector data/report system", or "large acceptance-heavy replacement".
4. Keep uncertainty broad when the source is document-derived or unconfirmed.

## Procedure

1. List the source files or text blocks inspected.
2. Summarize the delivery class in one sentence.
3. Identify the dominant effort drivers:
   - functional breadth
   - data/report fidelity
   - integrations
   - acceptance/review burden
   - documentation/training/handoff
   - operational constraints
4. Produce direct optimistic / most likely / pessimistic totals:
   - Optimistic: stable scope, reusable patterns, prompt clarification, limited rework.
   - Most likely: normal clarification, ordinary defects, moderate review churn.
   - Pessimistic: credible report/data/acceptance risks materialize without catastrophic scope change.
5. Calculate expected value and standard deviation:

```text
expected = (optimistic + 4 * most_likely + pessimistic) / 6
standard_deviation = (pessimistic - optimistic) / 6
```

6. Explain why the total is plausible as a whole-project anchor.
7. Compare against WBS and other methods only in parent synthesis after this pass is complete.

## Output Schema

Return:

- Source files inspected.
- Delivery class.
- Dominant effort drivers.
- Optimistic / most likely / pessimistic person-days.
- Expected value and standard deviation.
- Assumptions and exclusions.
- Confidence level.
- What would materially change the estimate.

Do not use conclusions from other estimators. Do not decompose into WBS lines.

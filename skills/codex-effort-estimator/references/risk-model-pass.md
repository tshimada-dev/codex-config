# Risk Model Pass

Use this reference for an independent risk-adjusted estimate from uncertainty drivers. This pass can be a lightweight scenario model or a simple Monte Carlo-style model when distributions can be stated. It should make risk math auditable without hiding everything inside WBS high values.

Run this pass for high-uncertainty, public-sector, report-heavy, data-heavy, integration-heavy, or acceptance-heavy estimates when risk drivers materially affect the final range.

## Scope

Estimate risk-adjusted human engineering effort in person-days. Do not estimate price, rates, or AI-agent wall-clock time unless explicitly asked.

## Independence Rules

1. Do not read or use WBS totals, WBS line estimates, WBS-derived PERT, component-unit totals, parent synthesis, prior estimate artifacts, or expected final ranges.
2. Start from source-visible risk drivers and a separately stated base-effort anchor. The base anchor may be a top-down class estimate or an explicit user-provided baseline, but not WBS unless the assignment explicitly says this is a WBS risk overlay.
3. Keep probability, impact, and correlation assumptions visible.
4. Do not add the same risk twice if another method already includes it; parent synthesis handles overlap after this pass returns.

## Procedure

1. List the source files or text blocks inspected.
2. Define the base-effort anchor used for the risk model and why it is independent from WBS.
3. Identify risk drivers, for example:
   - report/PDF fidelity
   - sample-vs-production data gaps
   - encoding/external characters
   - external integration uncertainty
   - acceptance criteria ambiguity
   - stakeholder/review wait
   - legal or policy change
   - deployment or environment constraints
4. For each risk, estimate probability and effort impact low / base / high.
5. Mark correlation groups so related risks do not falsely appear independent.
6. Calculate expected risk exposure:

```text
expected_risk = probability * expected_impact
risk_adjusted_center = base_effort + sum(expected_risk)
```

7. If running a simple Monte Carlo-style model, describe the distributions and report approximate P50 / P80 / P90. If not running simulation, use scenario bands:
   - low-risk scenario
   - expected-risk scenario
   - high-risk correlated scenario
8. Compare against WBS and other methods only in parent synthesis after this pass is complete.

## Output Schema

Return:

- Source files inspected.
- Independent base-effort anchor and rationale.
- Risk register with `Risk`, `Probability`, `Impact low/base/high`, `Expected exposure`, `Correlation group`, `Basis`, and `Mitigation/confirmation`.
- Risk-adjusted low / base / high or P50 / P80 / P90.
- Correlated high-risk scenario.
- Overlap warnings for risks likely already embedded in other methods.
- Confidence level.
- Confirmation questions.

Do not use conclusions from other estimators. Do not hide risk math inside unexplained contingency.

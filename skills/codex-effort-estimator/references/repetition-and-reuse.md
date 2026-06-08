# Repetition, Reuse, And Economy Of Scale

Use this reference whenever scope contains repeated variants or shared skeletons: multiple regions, branches, departments, similar reports, similar screens, or workflows that share an import/calculate/number/output pattern.

Bottom-up estimating from counted artifacts systematically drifts high on this kind of work, because it tends to price each counted item as a bespoke build. This reference exists to correct that drift before it reaches the WBS total. It is a discipline applied during sizing and WBS, not a separate method pass.

## Core Principle

Counted scope is not the same as build scope. `N` similar artifacts are usually `1` framework plus `N - 1` cheaper variants, not `N` full builds.

Estimate repeated work as:

```text
group_effort = framework_effort + (instances - 1) * representative_effort * variant_factor
```

- `framework_effort`: build the engine, the first full instance, and the shared template once.
- `representative_effort`: the typical effort of one already-supported instance.
- `variant_factor`: how much a subsequent variant really costs relative to a bespoke build.

## Variant Factor Guidance

Choose the variant factor from how the variant is realized, not from how it looks in the document.

| Variant realization | Typical variant factor | Notes |
|---|---:|---|
| Pure configuration or data/master row | 0.05-0.15 | Same code path, different data. |
| Template fill with the same layout engine | 0.10-0.25 | Most multi-region/multi-report output falls here. |
| Same structure with minor layout or rule changes | 0.25-0.45 | Some per-variant logic or layout tuning. |
| Materially different rules, layout, or data shape | 0.50-0.90 | Treat as nearly bespoke; document why. |
| Genuinely independent feature reusing nothing | 1.00 | Not a variant; estimate as its own line. |

Choose the high end when the variants are not confirmed to share a template, when fidelity is strict (pixel/PDF), or when each variant needs its own validation and acceptance evidence.

When a repeated group is detected, the variant factor is an auditable estimate field, not optional metadata. Do not output `未記載`, blank, or an implicit discount for the factor when the source shows repeated variants. If the evidence is insufficient for one exact factor, output a low/base/high factor range and the assumption behind it, for example `0.10/0.20/0.30 because the source says five regions share one logic path with parameter differences`.

## Cross-Feature Reuse

Distinct features often share a skeleton even when they are not labelled as variants. Examples: several workflows that all import, validate, calculate, number, and output; several screens built on the same form/grid foundation.

- Estimate the first feature that establishes a skeleton at full cost.
- Discount later features that reuse the skeleton; estimate only their net-new logic, screens, rules, and outputs.
- State the reuse assumption explicitly so it can be challenged. If reuse is uncertain, keep it as an assumption and widen the high end instead of silently pricing full builds.

## Count Risk Once

Risk and contingency belong in exactly one place. Do not stack them.

- If three-point `high` values already embed credible pessimistic risk, do not also add a separate explicit contingency or risk-reserve line for the same risk, and do not also headline the fully correlated endpoint-sum high.
- Pick one representation: widen the `high` per line, or carry a single visible reserve line, or present a correlated high-risk scenario, not all three for the same uncertainty.
- A standalone risk-reserve line is acceptable only for risk that is not already inside the line ranges, and its purpose must be stated.

## Top-Down Cross-Check

After bottom-up WBS, reconcile against an independent top-down anchor before finalizing.

1. Derive a per-unit figure from the bottom-up total, such as person-days per report, per screen, per workflow, or per function point.
2. Compare it against any organizational productivity baseline, prior actuals, or a defensible expert anchor.
3. If the bottom-up total implies a per-unit cost well above a credible anchor, treat it as a signal that economy of scale or reuse was under-applied. Re-examine the largest repeated groups first.
4. Record the cross-check result: consistent, adjusted down for repetition/reuse, or held high with a stated reason.

When no organizational baseline exists, say so, and state that the absolute level relies on document-derived judgment that has not been calibrated against measured productivity. Do not present an uncalibrated bottom-up total as if it were anchored.

## Output Expectations

When this reference is applied, the estimate should make the economy of scale auditable:

- Repetition groups with instance counts, the framework line, and the variant factor used.
- Variant factor low/base/high when the exact factor is uncertain, plus the reason each end of the range is plausible.
- Reuse assumptions between features, marked as assumptions when unconfirmed.
- A single, clearly located representation of risk/contingency.
- A top-down per-unit cross-check with its reconciliation outcome.
- For repeated-output systems, an explicit `framework + variants` breakdown instead of one large undifferentiated report line.

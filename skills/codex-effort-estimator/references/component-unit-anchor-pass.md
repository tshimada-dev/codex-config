# Component Unit Anchor Pass

Use this reference for an independent top-down estimate from counted components. Its purpose is anchoring control: produce a total-effort range that does not depend on WBS line totals, WBS phase allocation, WBS-derived PERT, or parent-preferred ranges.

Run this pass for non-trivial document-driven, RFP, public-sector, report-heavy, data-heavy, or workflow-heavy estimates whenever countable scope signals exist. Treat it as a first-class estimation method alongside WBS, not as a minor sanity check.

## Scope

Estimate human engineering effort in person-days. Do not estimate price, rates, or AI-agent wall-clock time unless explicitly asked.

This pass works best when the source material exposes counts such as:

- screens, forms, or workflows
- reports, documents, spreadsheets, PDF outputs, or templates
- imports, exports, file formats, integrations, or interfaces
- business rules, calculations, validations, or decision tables
- data entities, master data sets, migration sets, or historical datasets
- roles, environments, deployment targets, manuals, training, or formal deliverables

## Independence Rules

1. Do not read or use WBS totals, WBS line estimates, WBS-derived variance aggregation, parent synthesis, prior estimate artifacts, or expected final ranges.
2. Use only source documents, sizing facts, and this reference. If sizing facts were produced by another pass, use the counts and ambiguity notes, not that pass's effort conclusions.
3. Start from component counts and unit anchors. Do not reverse-engineer unit rates to match another method.
4. Record every unit anchor as observed baseline, external benchmark, local heuristic, or judgment. If no credible benchmark exists, say so and lower confidence.
5. Keep shared frameworks and variants explicit. Estimate the shared framework once, then add reduced-cost variants; do not price every repeated artifact as a full bespoke build.
6. Count each risk once. If a unit high value includes report-fidelity or data-quality risk, do not also add a reserve for the same uncertainty.

## Procedure

1. List the source files or text blocks inspected.
2. Extract countable scope signals and confidence for each count.
3. Group components into unit families, for example:
   - workflow or use-case family
   - screen/form family
   - report/output family
   - import/export/integration family
   - business-rule/calculation family
   - data/migration/master-data family
   - validation/acceptance/documentation family
4. For each family, choose a low / base / high unit anchor in person-days per unit, plus any shared framework cost.
5. Apply reuse and complexity factors only when they are source-backed:
   - repeated variant factor, such as additional report variants at 0.15-0.40 of the first implementation
   - complexity factor, such as strict PDF fidelity, legacy Office, complicated calculation rules, or uncertain real data
   - confidence factor, such as sample-only data or missing acceptance criteria
   - When repeated variants are source-visible, do not leave the factor blank. If the exact factor cannot be known, choose a defensible low/base/high factor range from `references/repetition-and-reuse.md`, state the realization assumption, and use the conservative end for the high estimate.
   - Examples: `5 regions: framework once + 4 variants at 0.10/0.20/0.30`, `8 CSV variants: common parser + mappings at 0.15/0.25/0.40`, `18 report templates: shared export engine + template variants at 0.15/0.30/0.45`.
6. Calculate each family:

```text
family_low = framework_low + unit_count * unit_low * reuse_or_complexity_factor_low
family_base = framework_base + unit_count * unit_base * reuse_or_complexity_factor_base
family_high = framework_high + unit_count * unit_high * reuse_or_complexity_factor_high
```

7. Sum family totals to produce a low / base / high component-anchor estimate.
8. Compare the component-anchor result against WBS only in parent synthesis, after this pass is complete. Explain differences by scope, unit anchor, reuse, or risk assumptions.
9. If AI coding assistance is explicitly in scope, label which component families are routine coding, code-adjacent, validation-heavy, report-fidelity-heavy, or non-reducible for downstream adjustment. Do not apply the AI adjustment inside this pass unless explicitly assigned.
10. State confidence and what facts would materially change the estimate.

## Unit Anchor Guidance

Use local actuals when available. If no local productivity baseline exists, use conservative judgment ranges and state that the estimate is document-derived rather than calibrated.

These examples are starting points, not mandatory rates:

| Unit family | Typical unit anchor examples |
|---|---|
| Workflow/use case | Person-days per business workflow, including normal UI and rule wiring. |
| Screen/form | Person-days per simple, medium, or complex screen/form. |
| Report/output | Shared report framework once, then person-days per template or variant. |
| Import/export/integration | Person-days per file format, endpoint, validation profile, or external system. |
| Calculation/rule set | Person-days per rule cluster or decision table, with extra validation for regulated or legacy calculations. |
| Data/migration/master data | Person-days per data source, data quality profile, mapping family, or migration run. |
| Acceptance/documentation | Percentage of implementation effort or unit-based counts for manuals, training, acceptance cycles, and formal deliverables. |

Avoid one-note anchors such as a single person-day-per-feature rate for the entire project unless the source is too thin to support family-specific units.

## Output Schema

Return:

- Source files inspected.
- Count table with `Component family`, `Count`, `Count basis`, `Count confidence`, and `Notes`.
- Unit anchor table with `Component family`, `Framework low/base/high`, `Unit low/base/high`, `Reuse or complexity factor low/base/high`, `Anchor source`, and `Rationale`.
- Total table with `Component family`, `Low`, `Base`, `High`, and `Notes`.
- Overall component-anchor low / base / high person-days.
- Main assumptions.
- Main risks and range drivers.
- Confidence level.
- Confirmation questions that could narrow the range.

Do not use conclusions from other estimators. Do not tune this pass to match WBS.

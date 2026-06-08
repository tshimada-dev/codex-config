# Parametric Model Pass

Use this reference for an independent top-down estimate from countable scope parameters and productivity coefficients. This pass is separate from WBS and component-unit anchors: it uses an explicit estimating equation, not a work breakdown or per-artifact quote table.

Run this pass for non-trivial estimates when the source exposes measurable drivers such as screens, workflows, reports, imports/exports, integrations, data entities, file formats, records, environments, roles, or formal deliverables.

## Scope

Estimate human engineering effort in person-days. Do not estimate price, rates, or AI-agent wall-clock time unless explicitly asked.

## Independence Rules

1. Do not read or use WBS totals, WBS line estimates, WBS-derived PERT, component-unit totals, parent synthesis, prior estimate artifacts, or expected final ranges.
2. Use source documents, sizing facts, and this reference. If using a sizing pass output, use only counts, count confidence, and ambiguity notes.
3. Define the model equation before calculating the result. Do not choose coefficients to match another method.
4. Record coefficient source as local actual, historical benchmark, public benchmark, heuristic, or judgment.
5. Keep calibration uncertainty visible. If no measured productivity baseline exists, lower confidence and widen the range.

## Procedure

1. List the source files or text blocks inspected.
2. Choose model drivers that are visible in the sources, for example:
   - workflows or use cases
   - screens/forms
   - reports/templates/PDF outputs
   - imports/exports/integrations/file formats
   - entities/master data/migration sets
   - calculation/rule clusters
   - formal deliverables, manuals, training, and acceptance cycles
3. Assign low / base / high coefficients to each driver in person-days per unit.
4. Add global terms only when source-backed:
   - fixed project overhead
   - governance/procurement overhead
   - report-fidelity factor
   - data-quality factor
   - integration complexity factor
   - acceptance/validation multiplier
5. Calculate:

```text
driver_effort = count * coefficient
subtotal = fixed_overhead + sum(driver_effort)
adjusted_total = subtotal * combined_factor
```

6. Produce low / base / high by applying low/base/high coefficients and factors, not by widening the final number arbitrarily.
7. Explain what the model includes and excludes.
8. Compare against WBS and other methods only in parent synthesis after this pass is complete.

## Output Schema

Return:

- Source files inspected.
- Model equation and included drivers.
- Driver table with `Driver`, `Count`, `Count basis`, `Low coefficient`, `Base coefficient`, `High coefficient`, `Coefficient source`, and `Notes`.
- Adjustment table with `Factor`, `Low`, `Base`, `High`, `Basis`, and `Why not double-counted`.
- Overall low / base / high person-days.
- Calibration confidence and whether local productivity data exists.
- Assumptions and exclusions.
- Major risk drivers.
- Confirmation questions that could narrow the model.

Do not use conclusions from other estimators. Do not tune coefficients to match WBS.

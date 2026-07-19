# Function Point Pass

Use this reference for an independent functional-size estimate when the source describes inputs, outputs, queries, internal data groups, and external interfaces well enough to count them. This is a pragmatic function-point pass for anchoring and comparison; do not pretend it is a certified IFPUG count unless the work was performed to that standard.

Run this pass when business functions, reports, files, interfaces, or data groups are visible and the estimate needs a non-WBS functional-size anchor.

## Scope

Estimate human engineering effort in person-days from functional size. Do not estimate price, rates, or AI-agent wall-clock time unless explicitly asked.

## Independence Rules

1. Do not read or use WBS totals, WBS line estimates, WBS-derived PERT, component-unit totals, parent synthesis, prior estimate artifacts, or expected final ranges.
2. Count functions from source documents and sizing facts only.
3. Keep function-point count assumptions visible. If data functions or transaction boundaries are ambiguous, use ranges and lower confidence.
4. Convert function points to effort using an explicit productivity range; do not pick productivity to match another method.
5. Do not invent EI/EO/EQ/ILF/EIF members to fill a stated aggregate. Every
   base-count row needs a source locator and one of `explicit`,
   `source-reported aggregate`, or `confirmed inferred`. Unresolved aggregate
   members remain sensitivity-only and receive no invented complexity.

## Procedure

1. List the source files or text blocks inspected.
2. Identify functional components:
   - External Inputs (EI): user/file/API inputs that maintain internal data.
   - External Outputs (EO): reports, generated files, PDFs, complex exports, or derived outputs.
   - External Inquiries (EQ): read/query functions with minimal derived processing.
   - Internal Logical Files (ILF): logical data groups maintained by the system.
   - External Interface Files (EIF): referenced external data groups maintained elsewhere.
3. Count each component as low / base / high when boundaries are uncertain.
   Preserve `Source status` and `Source locator` for every row. Reconcile the
   derived base count to the explicit/source-reported count. Untraced inferred
   items stop this pass from becoming a center vote; more than 25% inflation is
   sensitivity-only until confirmed.
4. Assign simple, average, or complex weights. Use a range when complexity is unclear.
5. Calculate unadjusted function points:

```text
UFP = sum(count * weight)
```

6. Apply a Value Adjustment Factor or equivalent delivery multiplier only when the source supports it. Keep it modest and auditable.
7. Convert function points to person-days:

```text
effort = adjusted_function_points / productivity_fp_per_person_day
```

Use a low/base/high productivity range. Faster productivity lowers effort; slower productivity raises effort.
8. Add explicitly non-functional delivery effort only when not already represented in the productivity range, such as procurement governance, formal manuals, or unusual acceptance support.
9. Compare against WBS and other methods only in parent synthesis after this pass is complete.

## Output Schema

Return:

- Source files inspected.
- Function count table with `Type`, `Item group`, `Count low/base/high`,
  `Complexity`, `Weight`, `Function points`, `Source status`, `Source locator`,
  `Basis`, and `Notes`.
- Count reconciliation with explicit/source-reported total, derived total,
  inflation ratio, unresolved aggregate, and guard status.
  Use columns `Metric`, `Explicit count`, `Derived count`, `Untraced inferred`,
  `Inflation ratio`, and `Guard status` so formatter QA can recompute it.
- Adjustment factors and rationale.
- Productivity assumption table with low/base/high productivity and source.
- Overall low / base / high person-days.
- Assumptions and exclusions.
- Ambiguities that could change the count.
- Confidence level.
- Confirmation questions.

Do not use conclusions from other estimators. Do not tune productivity to match WBS.

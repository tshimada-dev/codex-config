# Use Case Points Pass

Use this reference for an independent use-case-size estimate when the source describes actors, workflows, use cases, scenarios, or business processes. This pass is useful for workflow-heavy systems where WBS may overfit implementation phases.

Run this pass when the estimate has visible business workflows, actor types, and use cases, even if detailed implementation tasks are not available.

## Scope

Estimate human engineering effort in person-days from use case points. Do not estimate price, rates, or AI-agent wall-clock time unless explicitly asked.

## Independence Rules

1. Do not read or use WBS totals, WBS line estimates, WBS-derived PERT, component-unit totals, parent synthesis, prior estimate artifacts, or expected final ranges.
2. Derive actors, use cases, complexity, and factors from source documents and sizing facts only.
3. Do not choose productivity to match another method.
4. Keep actor/use-case boundary uncertainty visible.

## Procedure

1. List the source files or text blocks inspected.
2. Count actors:
   - Simple: another system through a well-defined API or file protocol.
   - Average: another system through less standardized interaction, or a user through a structured interface.
   - Complex: human actors using interactive workflows.
3. Count use cases:
   - Simple: few transactions, straightforward rules.
   - Average: moderate steps, validations, or alternate flows.
   - Complex: many steps, complex rules, report/data side effects, or substantial exception handling.
4. Calculate unadjusted actor weight (UAW) and unadjusted use case weight (UUCW), then:

```text
UUCP = UAW + UUCW
UCP = UUCP * TCF * ECF
effort = UCP * productivity_person_days_per_ucp
```

5. Choose Technical Complexity Factor (TCF) and Environmental Complexity Factor (ECF) ranges from source-visible facts such as legacy Office constraints, integration complexity, report fidelity, data quality, team familiarity, user availability, and acceptance rigor.
6. Use a productivity range in person-days per UCP. Record whether it is local actual, benchmark, heuristic, or judgment.
7. Compare against WBS and other methods only in parent synthesis after this pass is complete.

## Output Schema

Return:

- Source files inspected.
- Actor table with `Actor`, `Type`, `Weight`, `Basis`, and `Notes`.
- Use case table with `Use case`, `Complexity`, `Weight`, `Basis`, and `Notes`.
- TCF/ECF table with low/base/high factors and rationale.
- Productivity assumption.
- Overall low / base / high person-days.
- Assumptions and exclusions.
- Major uncertainty drivers.
- Confidence level.
- Confirmation questions.

Do not use conclusions from other estimators. Do not tune productivity or factors to match WBS.

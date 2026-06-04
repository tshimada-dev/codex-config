# WBS Bottom-Up Pass

Use this reference for an independent WBS estimate from requirements, RFPs, design notes, or document bundles.

## Scope

Estimate human engineering effort in person-days. Do not estimate price, rates, or AI-agent wall-clock time unless explicitly asked.

## Procedure

1. List the source files or text blocks inspected.
2. Identify in-scope deliverables, explicit exclusions, and unknowns.
3. Break work into WBS lines that are small enough to estimate without hiding unrelated features.
4. Estimate each line with low / likely / high person-days.
5. Include PM, requirements, design, implementation, reports/output, testing, acceptance support, manuals/training, deployment, and handoff when they are part of the delivery.
6. Apply risk at the WBS line or total level only when it is traceable to source evidence.
7. If AI coding assistance is explicitly in scope, keep raw human effort values but label which WBS lines are routine coding, code-adjacent, or non-reducible for downstream adjustment.
8. State confidence and the facts that would materially change the estimate.

## WBS Line Guidance

Use project-specific line items, but consider these categories:

| Category | Typical contents |
|---|---|
| PM/governance | Planning, meetings, progress reporting, issue/risk/change management |
| Requirements | Workshops, current-state analysis, requirements definition, acceptance criteria |
| Design | Architecture, data model, screen/report design, operations, error handling |
| Foundation | App shell, auth, settings, master data, logging, storage, audit/history |
| Data handling | Import/export, validation, migration, cleansing, sample-vs-real data gaps |
| Business logic | Calculations, status transitions, classifications, numbering, rules |
| Integrations | API, DB, file exchange, authentication, network and operational constraints |
| Reports/output | Excel, CSV, PDF, print layout, visual QA, template handling |
| Testing | Unit, integration, regression, old-vs-new comparison, UAT support |
| Delivery | Manuals, training, deployment notes, handoff, warranty support |

## Output Schema

Return:

- Source files inspected.
- Scope and exclusions.
- WBS table with `Component`, `Basis`, `Low`, `Likely`, `High`, and `Notes`.
- AI-reducibility notes when AI coding assistance is explicitly assumed.
- Total low / likely / high person-days.
- Main assumptions.
- Main risks and range drivers.
- Confidence level.
- Confirmation questions that could narrow the range.

Do not use conclusions from other estimators.

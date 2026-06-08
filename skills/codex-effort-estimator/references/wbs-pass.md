# WBS Bottom-Up Pass

Use this reference for an independent WBS estimate from requirements, RFPs, design notes, or document bundles.

## Scope

Estimate human engineering effort in person-days. Do not estimate price, rates, or AI-agent wall-clock time unless explicitly asked.

## Procedure

1. List the source files or text blocks inspected.
2. Identify in-scope deliverables, explicit exclusions, and unknowns.
3. Break work into WBS lines that are small enough to estimate without hiding unrelated features.
4. For repeated variants (regions, branches, similar reports/screens) and shared skeletons, apply `references/repetition-and-reuse.md`: estimate a framework line once plus reduced-cost variant lines, and discount features that reuse an established skeleton. Do not estimate each counted artifact as a bespoke build, and do not split one feature into several full-cost lines that re-estimate the same shared work.
5. Estimate each line with low / most likely / high person-days. In WBS output, `Likely` means the same central estimate as PERT `Most likely`, not a median or probability-weighted expected value.
6. Include PM, requirements, design, implementation, reports/output, testing, acceptance support, manuals/training, deployment, and handoff when they are part of the delivery.
7. Apply risk at the WBS line or total level only when it is traceable to source evidence. Count each risk once: if line `high` values already embed the risk, do not also add a separate reserve line for the same uncertainty.
8. Cross-check the bottom-up total against a top-down per-unit anchor (person-days per report, screen, workflow, or function point). If the implied per-unit cost is well above a credible anchor, re-examine the largest repeated groups for under-applied economy of scale before finalizing.
9. If AI coding assistance is explicitly in scope, keep raw human effort values and assign `AI削減区分` per WBS line for downstream adjustment. The WBS author owns the reducibility judgment because it depends on line context; the AI adjustment pass owns only the fixed coefficient application from `references/ai-coding-assistance-adjustment.md`.
10. State confidence and the facts that would materially change the estimate.

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
- WBS table with `Component`, `Basis`, `Low`, `Likely / Most likely`, `High`, `AI削減区分`, and `Notes`.
- AI-reducibility notes when AI coding assistance is explicitly assumed. Allowed `AI削減区分` values are `定型実装`, `コード隣接`, `複雑実装`, `検証重`, `削減不可`, and `対象外`. Use the most conservative applicable value when a line mixes work types and cannot be split.
- Total low / likely / high person-days.
- Main assumptions.
- Main risks and range drivers.
- Confidence level.
- Confirmation questions that could narrow the range.

Do not use conclusions from other estimators.

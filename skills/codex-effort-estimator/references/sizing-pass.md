# Sizing Pass

Use this reference to count visible scope before effort estimating. This pass improves WBS and PERT inputs; it is not a replacement for effort estimation.

## Scope

Return sizing facts, ambiguity, and confidence. Do not estimate total effort unless explicitly asked.

## Procedure

1. List the source files, repository paths, tickets, or text blocks inspected.
2. Count concrete scope signals:
   - Screens, forms, dialogs, dashboards, and user roles.
   - Reports, Excel outputs, PDFs, CSV imports/exports, templates, and print layouts.
   - Data entities, master tables, migrations, validation rules, and data volumes.
   - Business workflows, approvals, statuses, calculations, classifications, and exceptions.
   - Integrations, external systems, file exchanges, authentication, and environments.
   - Non-functional deliverables: security, audit/history, logging, backup, operations, manuals, training, acceptance documents.
3. Mark each count as `explicit`, `inferred`, `sample-only`, or `unknown`.
4. Identify duplicate names, ambiguous terms, sample-vs-production gaps, and hidden variants.
5. Group counts into WBS-friendly sizing buckets.
6. Identify repetition groups: artifacts that repeat across regions, branches, departments, or share a template or skeleton. For each group, record the instance count and a representative unit, and flag that the count feeds an economy-of-scale estimate (framework once plus variants), not a bespoke per-item multiplication. See `references/repetition-and-reuse.md`.
7. State which counts should drive WBS, PERT, public/report review, or repository estimates.

## Output Schema

Return:

- Source files inspected.
- Sizing table with `Signal`, `Count`, `Evidence`, `Certainty`, and `Notes`.
- Repetition groups with instance count and representative unit, flagged for economy-of-scale estimating.
- Ambiguous or missing counts.
- WBS/PERT input recommendations.
- Confidence level.
- Confirmation questions that could improve sizing.

Do not use conclusions from other estimators.

---
name: codex-effort-estimator
description: Estimate software delivery effort when a user needs person-day ranges, a WBS, timeline feasibility, or quote-grade estimate inputs.
---

# Codex Effort Estimator

Produce an explainable software-delivery estimate. Separate source facts from judgment; use ranges when uncertainty remains; state assumptions, exclusions, risks, and confidence. Do not estimate AI-agent wall-clock time from a human delivery estimate. Do not include price, rates, or currency unless asked.

## Choose the tier first

Read [estimate-tiers.md](references/estimate-tiers.md) before selecting passes. Record the tier, reason, and status for tier-required passes; `full` also records every coverage-gate pass. A tier defines the required method set:

- `quick`: use only its required spine and any user-requested pass. It is a capped, parent-owned estimate; do not require a delegate per method.
- `standard`: complete its required spine and the one suitable independent sizing anchor it specifies. Do not expand it into every otherwise-applicable pass unless the user asks or an escalation rule applies.
- `full`: apply every applicable coverage gate. A gate may be skipped only for the evidence-based reason defined in the tier reference.

Escalate when the tier reference requires it. If the input is too unstable for implementation sizing, estimate discovery first.

## Route the work

Start with [methods.md](references/methods.md) for method selection, three-point range synthesis, dependence clustering, and numerical safeguards. Read only the applicable method references:

- Countable scope: [sizing-pass.md](references/sizing-pass.md), then [component-unit-anchor-pass.md](references/component-unit-anchor-pass.md) or another tier-selected anchor.
- Feature or document scope: [wbs-pass.md](references/wbs-pass.md); decomposed task scope: [pert-pass.md](references/pert-pass.md).
- Measurable drivers, functional boundaries, or workflows: [parametric-model-pass.md](references/parametric-model-pass.md), [function-point-pass.md](references/function-point-pass.md), or [use-case-points-pass.md](references/use-case-points-pass.md), as the selected tier requires.
- Whole-project sanity anchor: [top-down-three-point-pass.md](references/top-down-three-point-pass.md).
- Calendar/staffing: [constraint-capacity-pass.md](references/constraint-capacity-pass.md); material uncertainty: [risk-model-pass.md](references/risk-model-pass.md); historical actuals: [analogy-calibration-pass.md](references/analogy-calibration-pass.md); unstable scope: [discovery-pass.md](references/discovery-pass.md); existing code: [repo-cost-pass.md](references/repo-cost-pass.md); AI-assisted coding: [ai-coding-assistance-adjustment.md](references/ai-coding-assistance-adjustment.md); public/report/acceptance work: [public-review-pass.md](references/public-review-pass.md) and [public-sector-business-systems.md](references/public-sector-business-systems.md).
- Repeated variants or shared skeletons: read [repetition-and-reuse.md](references/repetition-and-reuse.md).

Run range synthesis for any three-point data. `WBS-derived variance aggregation` is a re-expression of WBS uncertainty, never an independent method vote. Keep methods independent until synthesis; do not double-count risks or treat methods with shared count, productivity, lifecycle, or risk assumptions as separate votes.

## Delegate only when useful

Delegation supports independent viewpoints; it is optional and proportional to the estimate. A quick estimate may be completed by the parent. When delegating independent passes, use [delegation-input-design.md](references/delegation-input-design.md), pass raw sources or mechanical facts, and withhold parent conclusions and other method totals. Dependent adjustment or review passes may receive their declared input artifact.

## Synthesize and deliver

Read [synthesis.md](references/synthesis.md) after the selected passes. Reconcile scope and assumption differences before choosing a planning center. Keep a public/report review as a coverage audit unless its additive portion is demonstrably non-overlapping.

Use [output-template.md](references/output-template.md) for stakeholder-facing output. For a non-trivial workbook, read [spreadsheet-output.md](references/spreadsheet-output.md) and [workbook-format.md](references/workbook-format.md); format generated workbooks with `scripts/format_estimate_workbook.py`. A quick gut-check or text-only request does not require a workbook.

## Essential safeguards

- Do not present incomplete requirements as precise implementation scope.
- Do not turn generated/vendor code, samples, or templates into full custom-build effort without evidence.
- Estimate a shared framework once and discounted variants thereafter; count a risk once.
- Apply AI coding assistance only when explicitly assumed, using the documented line-level adjustment; do not reduce stakeholder, acceptance, visual QA, data-validation, deployment, or unresolved-domain work merely because coding is assisted.

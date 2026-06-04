---
name: codex-effort-estimator
description: Estimate software projects, feature work, public-sector/business systems, document-driven RFPs, GitHub issue backlogs, or existing repository rebuild cost. Use when Codex is asked for effort estimates, person-days, timeline ranges, WBS breakdowns, quote support, assumptions, risks, exclusions, confidence intervals, stakeholder-ready summaries, or estimate workbooks. Orchestrates local estimation references and optional installed estimation skills such as development-estimation, plan-estimateeffort, and cost-estimate without requiring them.
---

# Codex Effort Estimator

Use this as a thin orchestration skill for defensible software effort estimates. Keep the estimate explainable: separate measured facts from judgment, use ranges instead of false precision, and always state assumptions, exclusions, risks, and confidence.

## Decision Path

Classify the request before estimating:

| Estimate type | Use this path |
|---|---|
| General feature/project estimate | Use installed `development-estimation` when available; otherwise use `references/methods.md` for WBS bottom-up estimation. Summarize through this skill's output shape when a stakeholder-ready synthesis is needed. |
| Requirements/RFP/document-driven estimate | Read `references/methods.md`, then `references/public-sector-business-systems.md` when procurement, government, legacy Office, CSV, reports, training, or deliverables are involved. Use `development-estimation` as an optional base workflow when available. |
| Existing repository rebuild/cost estimate | Use installed `cost-estimate` when available; otherwise use `references/methods.md` plus repository facts and clearly state the fallback. |
| Task backlog/GitHub issue estimate | Use installed `plan-estimateeffort` when available and tasks are already decomposed; otherwise apply PERT from `references/methods.md`. |
| AI-agent execution time estimate | Use a separate agent-work estimation approach if available; do not convert human delivery estimates directly into agent wall-clock time. |

If multiple paths apply, run the specific skill/reference first and use this skill only to normalize the final answer.

## Workflow

1. Define scope:
   - Identify what is in scope, out of scope, and still unknown.
   - Capture target audience: internal planning, customer quote, procurement response, or engineering plan.
   - Choose unit: person-days by default; add calendar duration only when staffing assumptions are known.

2. Gather evidence:
   - For documents: list source files, count major functions, reports, imports, exports, data volumes, integrations, environments, and required deliverables.
   - For repos: count non-generated code and identify architecture, tests, integrations, operational maturity, and missing production work.
   - For issues/backlogs: normalize tasks, dependencies, acceptance criteria, and confidence.

3. Decide whether to delegate:
   - For small or quick estimates, proceed in one agent.
   - For broad, high-stakes, document-heavy, backlog-heavy, or repository-backed estimates, use `Multi-Agent Orchestration` below when subagents are available.
   - If subagents are unavailable, apply the same methods sequentially in the parent agent and say so.

4. Decompose into WBS:
   - Management and governance
   - Requirements and business analysis
   - Architecture and design
   - Shared foundation and UX
   - Data import/export and migration
   - Business logic and calculations
   - Integrations
   - Reports, documents, spreadsheets, and PDF output
   - Non-functional requirements and security
   - Testing and acceptance support
   - Training, manuals, deployment, handoff, and warranty support

5. Estimate:
   - Prefer low / base / high ranges.
   - Use PERT when a three-point model is useful: expected = `(O + 4M + P) / 6`.
   - Apply risk multipliers only after base work is decomposed.
   - Keep contingency visible instead of hiding it inside every line.

6. Normalize the output:
   - Use `references/output-template.md` for customer-facing or management-facing summaries.
   - If the user asks for an Excel workbook, read `references/spreadsheet-output.md` and use the `spreadsheets` skill/workflow to create and verify the `.xlsx`.
   - Include evidence, assumptions, exclusions, risk drivers, confirmation questions, and a recommended quote range.

## Multi-Agent Orchestration

When subagents are available and the estimate is substantial, assign one subagent per estimation method. Treat each subagent output as an independent observation, not a vote.

### Parent Responsibilities

- Define the shared scope, source files, output unit, and assumptions before delegation.
- Give each subagent only the source material and method-specific task it needs.
- Do not share one subagent's conclusion with another subagent.
- Do not pass parent estimates, prior estimate files, preferred ranges, suspected answers, or parent interpretations into subagent prompts.
- Start subagents without forked conversation context when the tool supports it, so they do not inherit the parent's prior reasoning.
- Collect each estimate with its assumptions, exclusions, risks, confidence, and rationale.
- Reconcile differences by identifying which method, scope, or risk assumption caused the gap.
- Produce the final range, planning center, confidence, and stakeholder-ready explanation.

### Delegation Hygiene

Use a neutral delegation packet. It may include:

- Skill or method to use.
- Exact source document paths or raw document text.
- Output unit, such as person-days.
- Required output schema.
- Explicit instruction not to use other estimator conclusions.

It must not include:

- The parent's current estimate or target range.
- Prior estimate artifacts unless the subagent is explicitly reviewing those artifacts.
- Hints such as "the answer should be high/low" or "this is probably the risky part."
- Summaries that select or emphasize evidence beyond the subagent's assigned method.

For specialist passes, name only the specialization and source documents. Let the subagent identify the risk drivers from the documents.

### Standard Delegates

| Delegate | Use when | Assignment |
|---|---|---|
| WBS bottom-up pass | General feature/project or document-driven scope | Use `development-estimation` if installed, otherwise use `references/methods.md`. Produce WBS low/likely/high effort, assumptions, risks, and confidence. |
| PERT pass | Tasks can be estimated with three-point ranges | Use `plan-estimateeffort` if installed, otherwise use PERT in `references/methods.md`. Produce optimistic/most-likely/pessimistic estimates and confidence notes. |
| Public-sector/business-system review pass | Government, RFP, Excel/PDF, CSV, training, acceptance, or formal deliverables matter | Use this skill with `references/public-sector-business-systems.md` as a risk-review and coverage-audit pass. Identify which public/report/acceptance factors are already included in WBS or PERT, which are missing or thin, and which should only widen the risk range. Do not treat this pass as a mechanical additive estimate unless the assignment explicitly asks for an additive-only adjustment. |
| Repository cost pass | Existing repository or rebuild/completion value is in scope | Use `cost-estimate` if installed, otherwise inventory repository facts and state the fallback. Report measured facts separately from inference. |

### Delegate Prompt Shape

Use concise prompts like:

```text
Use $development-estimation if available; otherwise use $codex-effort-estimator references/methods.md. Source documents: [paths]. Estimate the named project in person-days using WBS low/likely/high ranges. Return WBS table, assumptions, exclusions, risks, confidence, and what would materially change the estimate. Do not use conclusions from other estimators. Do not price the work.
```

```text
Use $plan-estimateeffort. Source documents: [paths]. Estimate the named project in optimistic/most-likely/pessimistic person-days, PERT expected value, confidence, and major risk drivers. Do not use conclusions from other estimators. Do not price the work.
```

```text
Use $codex-effort-estimator references/public-sector-business-systems.md as a specialist public-sector/business-system review pass. Source documents: [paths]. Review public-sector deliverables, Excel/PDF/report fidelity, CSV/encoding, acceptance, training, handoff, and procurement risks. Return coverage notes, missing-or-thin areas, risk-range implications, and only optional additive adjustment candidates where they are not already covered by WBS/PERT. Do not use conclusions from other estimators. Do not price the work.
```

### Parent Synthesis

The parent should report:

- Method results side by side.
- Agreement and disagreement.
- Scope or assumption differences causing gaps.
- For specialist review passes, separate coverage audit from arithmetic. Mark each finding as already covered, missing/thin, or risk-only.
- Do not mechanically add a public-sector/report/acceptance adjustment on top of WBS or PERT when those methods already include the same work.
- Apply only the non-overlapping missing/thin portion as an adjustment; use overlapping high-uncertainty findings to widen the range or explain the high-risk scenario.
- Final recommended range and planning center.
- A lower "implementation-only" range if materially different from the full delivery range.
- Confirmation questions that could narrow the range.

If method outputs conflict, prefer the estimate whose assumptions best match the user's target deliverable. Keep outliers visible when they represent real delivery risk.

### Adjustment Review Rule

Treat public-sector, report-fidelity, acceptance, training, and handoff passes as review passes by default, not as automatic adders.

Use this reconciliation pattern:

| Review finding | Parent action |
|---|---|
| Already represented in WBS/PERT | Do not add again; cite it as validation or confidence support. |
| Missing or clearly thin in WBS/PERT | Add only that non-overlapping portion, or shift the planning center upward. |
| Included but highly uncertain | Widen the high end of the range or define a high-risk scenario. |
| Depends on an unresolved requirement | Keep as an assumption or confirmation question instead of hiding it in the base estimate. |

When reporting, use labels such as `public/report risk review`, `coverage audit`, `adjustment candidate`, or `risk-range driver`. Avoid labels that imply direct summation unless the numbers are intentionally additive and non-overlapping.

## Guardrails

- Do not present estimates as precise when requirements are incomplete.
- Do not import external skill conclusions blindly; restate the method and reconcile conflicts.
- Do not include rates, currency, or price unless the user asks or provides unit prices.
- Do not treat generated/vendor code, sample data, or bundled templates as full custom-build effort without saying why.
- For public-sector or RFP work, include deliverables, review gates, training, manual creation, acceptance testing, and change-management assumptions.

## References

- `references/methods.md`: estimation methods, range logic, and risk adjustment.
- `references/public-sector-business-systems.md`: WBS and risk factors for government/business systems, especially document and Excel-heavy work.
- `references/output-template.md`: concise output formats for estimates and quote support.
- `references/spreadsheet-output.md`: workbook structure for detailed estimate spreadsheets with method-specific sheets, phase breakdowns, assumptions, risks, and verification expectations.

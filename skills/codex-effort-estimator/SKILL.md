---
name: codex-effort-estimator
description: Estimate software projects, feature work, public-sector/business systems, document-driven RFPs, GitHub issue backlogs, or existing repository rebuild cost. Use when Codex is asked for effort estimates, person-days, timeline ranges, WBS breakdowns, quote support, assumptions, risks, exclusions, confidence intervals, stakeholder-ready summaries, or estimate workbooks. Orchestrates self-contained local estimation references, method-specific subagent passes, and pass coverage gates.
---

# Codex Effort Estimator

Use this as a thin orchestration skill for defensible software effort estimates. Keep the estimate explainable: separate measured facts from judgment, use ranges instead of false precision, and always state assumptions, exclusions, risks, and confidence.

## Decision Path

Classify the request before estimating:

| Estimate type | Use this path |
|---|---|
| General feature/project estimate | Use `references/sizing-pass.md` when scope can be counted, then `references/wbs-pass.md` for WBS bottom-up estimation. When countable components exist, also run independent anchors: `references/component-unit-anchor-pass.md`, `references/parametric-model-pass.md`, and `references/top-down-three-point-pass.md`. Use `references/methods.md` for shared range logic. |
| Requirements/RFP/document-driven estimate | Use `references/sizing-pass.md`, `references/wbs-pass.md`, `references/component-unit-anchor-pass.md`, `references/parametric-model-pass.md`, and `references/top-down-three-point-pass.md`; then use `references/public-review-pass.md` when procurement, government, legacy Office, CSV, reports, training, acceptance, or formal deliverables are involved. |
| Existing repository rebuild/cost estimate | Use `references/repo-cost-pass.md` plus measured repository facts. Keep rebuild/completion effort separate from price unless the user asks for cost. |
| Task backlog/GitHub issue estimate | Use `references/pert-pass.md` when tasks are already decomposed enough for three-point ranges; otherwise decompose first with WBS. |
| Functional-size signals exist | Use `references/function-point-pass.md` when inputs, outputs, inquiries, logical files, or external interface files can be counted. Use `references/use-case-points-pass.md` when actors and workflows/use cases can be counted. |
| Similar past work exists | Use `references/analogy-calibration-pass.md` after WBS/PERT to compare against historical actuals or prior estimates and explain variance. |
| Requirements are too unclear for implementation estimating | Use `references/discovery-pass.md` to estimate discovery, requirements definition, prototype, data/report investigation, and decision work before implementation. |
| Fixed deadline, staffing, review gates, or delivery window matter | Use `references/constraint-capacity-pass.md` as a feasibility envelope and staffing/calendar sanity check. |
| Major risks drive the range | Use `references/risk-model-pass.md` as an independent risk-adjusted scenario or Monte Carlo-style model. |
| User explicitly assumes AI coding assistance | Use `references/ai-coding-assistance-adjustment.md` during parent synthesis or as an explicit adjustment pass. Adjust implementation-heavy work, not stakeholder, acceptance, or uncertainty work. |
| AI-agent execution time estimate | Use a separate agent-work estimation approach if available; do not convert human delivery estimates directly into agent wall-clock time. |
| COSMIC or formal functional measurement is explicitly requested | Use COSMIC-style counting only when requested or when the source is detailed enough for data-movement analysis; otherwise prefer the lighter function point and use case point passes. |

Select every matching row, not just the best-looking row. Hybrid requests, such as public-sector repository rebuilds or RFP-derived backlog estimates, require the union of all applicable passes.

Before estimating, complete the `Pass Coverage Gate` below. Do not silently skip an applicable viewpoint.

## Minimum Spine

Every non-trivial estimate should include this minimum spine:

1. Sizing or explicit reason sizing is not useful.
2. WBS for broad/document-driven scope unless another method is the sole appropriate model.
3. Component unit anchor when countable scope signals exist, so the final estimate is not dependent on a single WBS anchor.
4. Parametric model and top-down three-point anchors when the estimate is non-trivial and enough source facts exist.
5. Functional-size anchors when supported: function point for input/output/data/interface signals, and use case points for actor/workflow signals.
6. Constraint/capacity envelope when date, staffing, review gates, or delivery windows materially affect feasibility.
7. Risk model when a few uncertainty drivers materially widen the range.
8. At least one additional effort method when applicable: PERT for decomposed task scope, repository cost for rebuild/completion scope, discovery for unstable implementation scope, or analogy calibration when credible historical anchors exist.
9. Coverage/risk review: public/report review when any trigger is present; otherwise a parent-owned risk review that checks assumptions, exclusions, validation, acceptance, and delivery support.
10. Parent synthesis with final range, confidence, and pass coverage.
11. Fixed-format workbook unless the user asks for text only or the request is a quick gut-check.

Use discovery instead of implementation estimating when the source material is not stable enough to define delivery scope. Use analogy calibration only when comparable actuals, prior estimates, or productivity baselines exist, but always record whether it was run or skipped.

## Pass Coverage Gate

Before running method passes, create a coverage checklist from the table below. For each pass, record `run`, `skipped`, or `not applicable`, with a reason. Include this checklist in the final answer and workbook synthesis.

| Pass | Run when | Skip only when |
|---|---|---|
| Sizing | Scope has countable screens, reports, imports, exports, entities, workflows, roles, integrations, environments, or deliverables | Source is too small or abstract to count; record what could not be counted. |
| WBS | Scope is broad, document-driven, RFP-driven, or feature/project oriented | PERT or repo-cost is the sole appropriate effort method and WBS would duplicate it without adding structure. |
| Component unit anchor | Scope has countable components such as screens, workflows, reports, imports, exports, integrations, entities, data sets, roles, environments, or formal deliverables | Source has no meaningful component counts, or a measured historical analogy is the sole credible top-down anchor. Do not skip merely because WBS was run. |
| Parametric model | Scope has measurable drivers that can feed an explicit estimating equation | No reliable countable drivers exist, or source facts are too abstract to assign coefficients. Do not skip merely because component unit anchor or WBS was run. |
| Function point | Inputs, outputs, inquiries, internal logical files, or external interface files can be counted at least coarsely | Functional boundaries are too unclear to count, or the system is not function-oriented. Record the missing count types. |
| Use case points | Actors and workflows/use cases can be counted at least coarsely | The source has no actor/workflow/use-case view, or workflows cannot be bounded. |
| Top-down three-point | Non-trivial estimate needs an independent whole-project anchor | Request is a quick gut-check already answered directly, or scope is too abstract even for broad class anchoring. |
| Constraint capacity | Deadline, delivery window, staffing, review gates, procurement cadence, or acceptance windows are relevant | No calendar/staffing/review constraints are provided or inferable; record the missing constraint facts. |
| Risk model | A small set of uncertainty drivers materially affects the range | Risks are trivial, already bounded, or no risk probabilities/impacts can be stated even qualitatively. |
| PERT | Tasks are decomposed enough for an independent three-point estimate | Tasks are not decomposed enough; record that WBS or discovery is used instead. Skipping the independent PERT pass does not skip variance aggregation: if WBS lines have low / most likely / high values, apply range synthesis to those WBS three-point values and label it `WBS-derived variance aggregation`. |
| Repository cost | Existing repository rebuild, replacement, completion, or production-hardening effort is in scope | No repository or codebase is in scope. |
| Discovery | Requirements, data, reports, integrations, acceptance criteria, or constraints are too unclear for implementation estimating | Implementation scope is stable enough for WBS/PERT/repo-cost. |
| Analogy calibration | Comparable historical actuals, prior estimates, or productivity baselines exist | No credible anchor exists; state that no baseline is available. |
| AI coding assistance adjustment | The user explicitly assumes AI-assisted coding | The user did not explicitly include AI coding assistance. |
| Public-sector/report review | Procurement, government, legacy Office, CSV, reports, training, acceptance, formal deliverables, or handoff matters | None of those triggers are present; state the checked triggers. |

If a pass is skipped, the final synthesis must make the skip visible. A silent omission is a workflow failure.

## Workflow

1. Define scope:
   - Identify what is in scope, out of scope, and still unknown.
   - Capture target audience: internal planning, customer quote, procurement response, or engineering plan.
   - Choose unit: person-days by default; add calendar duration only when staffing assumptions are known.

2. Gather evidence:
   - For documents: list source files, count major functions, reports, imports, exports, data volumes, integrations, environments, and required deliverables.
   - For repos: count non-generated code and identify architecture, tests, integrations, operational maturity, and missing production work.
   - For issues/backlogs: normalize tasks, dependencies, acceptance criteria, and confidence.
   - When counts matter, use `references/sizing-pass.md` before estimating so WBS/PERT lines are grounded in visible size signals.
   - When countable components exist, use `references/component-unit-anchor-pass.md` as an independent top-down anchor. Do not let WBS totals, WBS phase allocation, or parent-preferred ranges influence that pass.
   - When measurable drivers exist, use `references/parametric-model-pass.md` as a separate equation-based anchor.
   - When functional-size signals exist, use `references/function-point-pass.md` or `references/use-case-points-pass.md` as supported by the source.
   - When schedule, staffing, acceptance windows, or review gates matter, use `references/constraint-capacity-pass.md`.
   - When risk drivers materially affect the range, use `references/risk-model-pass.md`.
   - When scope has repeated variants (regions, branches, similar reports/screens) or shared skeletons, group them and use `references/repetition-and-reuse.md`; counted artifacts are not the same as build scope.

3. Decide whether to delegate:
   - Build the pass coverage checklist first, selecting all applicable passes from the decision path and coverage gate.
   - Check whether subagents are available before running method passes. This is a priority check, not an optional optimization.
   - When subagents are available, delegate each applicable method pass to a separate subagent regardless of estimate size.
   - Use subagents primarily to preserve independence between estimation viewpoints; parallel execution is useful but not the reason for delegation.
   - If subagents are unavailable, apply the same method passes sequentially in the parent agent and say so.

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
   - Always run `Range Synthesis` when any WBS, PERT, or repository effort lines contain low / most likely / high three-point values.
   - Use discovery estimates instead of implementation estimates when the source material is not sufficient to define implementation scope.
   - Use analogy calibration when comparable historical work is available; report calibration separately from raw WBS/PERT.
   - Use the component unit anchor as a separate total-estimate method when countable components exist; compare it against WBS only during parent synthesis.
   - Use parametric, function point, use case point, top-down three-point, constraint capacity, and risk model passes as independent viewpoints when their required inputs exist; compare them only during parent synthesis.
   - When the user explicitly says AI coding assistance is assumed, apply `references/ai-coding-assistance-adjustment.md` after raw WBS/PERT so routine implementation is not overstated.
   - Apply risk multipliers only after base work is decomposed.
   - Keep contingency visible instead of hiding it inside every line.
   - For repeated variants or shared skeletons, apply `references/repetition-and-reuse.md`: estimate the framework once plus reduced-cost variants, discount reused skeletons, count risk only once, and cross-check the bottom-up total against a top-down per-unit anchor.

6. Normalize the output:
   - Use `references/output-template.md` for customer-facing or management-facing summaries.
   - Create an Excel workbook by default for non-trivial estimates. Read `references/spreadsheet-output.md` and `references/workbook-format.md`, then use the `spreadsheets` skill/workflow to create and verify the `.xlsx`, unless the user asks for text only or the estimate is a quick gut-check. After generating a local workbook, use `scripts/format_estimate_workbook.py` so sheet-specific widths and styles are applied deterministically.
   - Include evidence, assumptions, exclusions, risk drivers, confirmation questions, and a recommended quote range.

## Range Synthesis

Range synthesis is mandatory whenever three-point effort data exists. It is a calculation step, not an independent estimation method.

For every low / most likely / high line, calculate:

```text
expected = (low + 4 * most_likely + high) / 6
standard_deviation = (high - low) / 6
variance = standard_deviation ^ 2
```

Then calculate:

```text
total_expected = sum(expected)
total_standard_deviation = sqrt(sum(variance))
confidence_interval = total_expected +/- z * total_standard_deviation
```

Use `z = 1.645` for the default 90% stakeholder confidence range. Also show the endpoint scenario `sum(low) - sum(high)` as a fully correlated best/worst-case scenario when useful, but do not use endpoint sums as the default probabilistic range.

If the source three-point data came from WBS, label the result `WBS-derived variance aggregation`. Do not count it as another independent estimate in method voting or method comparison; it is a probabilistic re-expression of the WBS uncertainty. When the most-likely total differs from the expected total, use the expected total as the planning center and explain the difference as skew or tail risk.

## Multi-Agent Orchestration

Check subagent availability before running method passes. When subagents are available, assign one subagent per applicable local estimation reference, even for small estimates. Treat each subagent output as an independent observation, not a vote.

The purpose of delegation in this skill is viewpoint independence and anchoring control. Parallel execution is optional.

### Parent Responsibilities

- Define the shared scope, source files, output unit, and assumptions before delegation.
- Determine whether subagents can be spawned in the current environment, such as through `spawn_agent` or an equivalent delegation tool, before doing the method work locally.
- Give each subagent only the source material and method-specific task it needs.
- When the tool supports direct file/context selection, pass only the named local reference file(s), source documents, unit, and output schema to the subagent.
- If the subagent must load this skill, instruct it to follow only the named reference file(s) for method behavior and to ignore parent synthesis guidance until it returns its method output.
- Do not share one subagent's conclusion with another subagent.
- Do not pass parent estimates, prior estimate files, preferred ranges, suspected answers, or parent interpretations into subagent prompts.
- Start subagents without forked conversation context when the tool supports it, so they do not inherit the parent's prior reasoning.
- Collect each estimate with its assumptions, exclusions, risks, confidence, and rationale.
- Collect each pass status with run/skip reason, even when the pass was not delegated.
- Reconcile differences by identifying which method, scope, or risk assumption caused the gap.
- Produce the final range, planning center, confidence, and stakeholder-ready explanation.

### Delegation Hygiene

Use a neutral delegation packet. It may include:

- Local method reference to use.
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
| Sizing pass | Documents, RFPs, repos, or backlogs expose countable scope signals | Use `references/sizing-pass.md`. Produce counted scope facts and sizing confidence; do not estimate total effort unless asked. |
| WBS bottom-up pass | General feature/project or document-driven scope | Use `references/wbs-pass.md`. Produce WBS low/most-likely/high effort, assumptions, exclusions, risks, and confidence. |
| Component unit anchor pass | Countable screens, workflows, reports, imports, exports, integrations, data sets, roles, environments, or deliverables exist | Use `references/component-unit-anchor-pass.md`. Produce an independent top-down low/base/high estimate from component counts and unit anchors. Do not use WBS totals, WBS-derived PERT, parent ranges, or prior estimate artifacts. |
| Parametric model pass | Measurable drivers can feed an explicit estimating equation | Use `references/parametric-model-pass.md`. Produce an independent low/base/high estimate from count drivers, coefficients, and adjustment factors. Do not use WBS or component-unit totals. |
| Function point pass | Inputs, outputs, inquiries, logical files, or external interface files can be counted | Use `references/function-point-pass.md`. Produce a pragmatic FP count, productivity conversion, and low/base/high effort. Do not tune productivity to match other methods. |
| Use case points pass | Actors and workflows/use cases can be counted | Use `references/use-case-points-pass.md`. Produce actor/use-case counts, TCF/ECF, productivity conversion, and low/base/high effort. Do not tune factors to match other methods. |
| Top-down three-point pass | A broad whole-project anchor is useful, especially when WBS anchoring risk matters | Use `references/top-down-three-point-pass.md`. Produce direct optimistic/most-likely/pessimistic whole-project effort. Do not decompose into WBS lines. |
| Constraint capacity pass | Deadline, staffing, review gates, delivery windows, or acceptance periods affect feasibility | Use `references/constraint-capacity-pass.md`. Produce feasible person-day envelope and staffing/calendar implications. Do not use WBS totals. |
| Risk model pass | Major uncertainty drivers materially affect the range | Use `references/risk-model-pass.md`. Produce independent risk-adjusted scenarios or P50/P80/P90 from probability/impact assumptions. Do not hide risk in unexplained contingency. |
| PERT pass | Tasks can be estimated with three-point ranges | Use `references/pert-pass.md`. Produce optimistic/most-likely/pessimistic estimates, PERT expected value, and confidence notes. |
| Analogy calibration pass | Comparable past projects, actuals, or prior estimates are available | Use `references/analogy-calibration-pass.md`. Compare WBS/PERT against historical anchors and explain adjustment candidates without hiding variance. |
| Discovery pass | Requirements are too unclear for implementation estimating | Use `references/discovery-pass.md`. Estimate discovery/requirements work and identify decisions needed before implementation estimating. |
| AI coding assistance adjustment pass | The user explicitly says AI coding assistance is assumed | Use `references/ai-coding-assistance-adjustment.md`. Adjust raw human WBS/PERT by WBS line using `AI削減区分` and fixed coefficients; explain which work is or is not reducible. |
| Public-sector/business-system review pass | Government, RFP, Excel/PDF, CSV, training, acceptance, or formal deliverables matter | Use `references/public-review-pass.md` and `references/public-sector-business-systems.md` as a risk-review and coverage-audit pass. Identify which public/report/acceptance factors are already included in WBS or PERT, which are missing or thin, and which should only widen the risk range. Do not treat this pass as a mechanical additive estimate unless the assignment explicitly asks for an additive-only adjustment. |
| Repository cost pass | Existing repository or rebuild/completion value is in scope | Use `references/repo-cost-pass.md`. Report measured facts separately from inference. |

### Delegate Prompt Shape

Use concise prompts like:

```text
Use $codex-effort-estimator with references/sizing-pass.md only for the method instructions. Source documents: [paths]. Count scope signals such as screens, reports, imports, exports, entities, workflows, roles, integrations, environments, and deliverables. Return sizing facts, ambiguity notes, confidence, and which counts should feed WBS/PERT. Do not estimate total effort unless asked. Do not use conclusions from other estimators.
```

```text
Use $codex-effort-estimator with references/wbs-pass.md only for the method instructions. Source documents: [paths]. Estimate the named project in person-days using WBS low/most-likely/high ranges. Return WBS table, assumptions, exclusions, risks, confidence, and what would materially change the estimate. Do not use conclusions from other estimators. Do not price the work.
```

```text
Use $codex-effort-estimator with references/component-unit-anchor-pass.md only for the method instructions. Source documents: [paths]. Estimate the named project in person-days from countable component families and unit anchors. Return count table, unit anchor table, family totals, overall low/base/high, assumptions, risks, confidence, and confirmation questions. Do not use WBS totals, WBS-derived PERT, parent ranges, prior estimate artifacts, or conclusions from other estimators. Do not price the work.
```

```text
Use $codex-effort-estimator with references/parametric-model-pass.md only for the method instructions. Source documents: [paths]. Estimate the named project in person-days from measurable drivers, coefficients, and explicit adjustment factors. Return model equation, driver table, coefficient sources, adjustment factors, low/base/high total, assumptions, risks, confidence, and confirmation questions. Do not use WBS totals, component-unit totals, WBS-derived PERT, parent ranges, prior estimate artifacts, or conclusions from other estimators. Do not price the work.
```

```text
Use $codex-effort-estimator with references/function-point-pass.md only for the method instructions. Source documents: [paths]. Produce a pragmatic function point estimate: count EI/EO/EQ/ILF/EIF, assign complexity weights, convert to person-days with an explicit productivity range, and return low/base/high effort, assumptions, ambiguities, confidence, and confirmation questions. Do not use WBS totals, parent ranges, prior estimate artifacts, or conclusions from other estimators. Do not price the work.
```

```text
Use $codex-effort-estimator with references/use-case-points-pass.md only for the method instructions. Source documents: [paths]. Produce a use case points estimate from actors, use cases/workflows, TCF/ECF, and productivity. Return actor/use-case tables, factors, low/base/high effort, assumptions, uncertainty drivers, confidence, and confirmation questions. Do not use WBS totals, parent ranges, prior estimate artifacts, or conclusions from other estimators. Do not price the work.
```

```text
Use $codex-effort-estimator with references/top-down-three-point-pass.md only for the method instructions. Source documents: [paths]. Produce a direct whole-project optimistic/most-likely/pessimistic estimate, expected value, standard deviation, delivery class, dominant drivers, assumptions, confidence, and what would materially change the estimate. Do not decompose into WBS lines. Do not use WBS totals, parent ranges, prior estimate artifacts, or conclusions from other estimators. Do not price the work.
```

```text
Use $codex-effort-estimator with references/constraint-capacity-pass.md only for the method instructions. Source documents: [paths]. Produce a constraint/capacity estimate from deadlines, staffing scenarios, review gates, acceptance windows, and fixed deliverables. Return feasible person-day envelope, staffing/calendar implications, constraints, assumptions, risks, confidence, and confirmation questions. Do not use WBS totals, parent ranges, prior estimate artifacts, or conclusions from other estimators. Do not price the work.
```

```text
Use $codex-effort-estimator with references/risk-model-pass.md only for the method instructions. Source documents: [paths]. Produce an independent risk model from source-visible risk drivers, probability/impact assumptions, correlation groups, and an independent base-effort anchor. Return risk register, risk-adjusted range or P50/P80/P90, correlated high-risk scenario, overlap warnings, confidence, and confirmation questions. Do not use WBS totals as the base anchor unless explicitly assigned. Do not use parent ranges, prior estimate artifacts, or conclusions from other estimators. Do not price the work.
```

```text
Use $codex-effort-estimator with references/pert-pass.md only for the method instructions. Source documents: [paths]. Estimate the named project in optimistic/most-likely/pessimistic person-days, PERT expected value, confidence, and major risk drivers. Do not use conclusions from other estimators. Do not price the work.
```

```text
Use $codex-effort-estimator with references/analogy-calibration-pass.md only for the method instructions. Source documents: [paths]. Historical anchors: [paths or raw facts]. Compare the current scope against comparable past work, explain differences, and return calibration factors or adjustment candidates. Do not replace WBS/PERT with an unexplained average. Do not price the work.
```

```text
Use $codex-effort-estimator with references/discovery-pass.md only for the method instructions. Source documents: [paths]. The implementation scope is not yet stable. Estimate discovery, requirements definition, prototype, data/report investigation, stakeholder review, and decision work in person-days. Return what must be resolved before implementation estimating. Do not pretend the implementation estimate is precise.
```

```text
Use $codex-effort-estimator with references/ai-coding-assistance-adjustment.md only for the method instructions. Raw estimate artifact: [path or pasted WBS/PERT table with AI削減区分]. The user explicitly assumes AI coding assistance. Adjust the estimate by WBS line using the documented fixed coefficients for each `AI削減区分`, preserving raw baseline values and separating `判断者` from `係数権限`. Return line-level baseline, adjusted range, multiplier rationale, non-reducible work, reduction sanity check, and confidence.
```

```text
Use $codex-effort-estimator with references/public-review-pass.md and references/public-sector-business-systems.md only for the method instructions. Source documents: [paths]. Review public-sector deliverables, Excel/PDF/report fidelity, CSV/encoding, acceptance, training, handoff, and procurement risks. Return coverage notes, missing-or-thin areas, risk-range implications, and only optional additive adjustment candidates where they are not already covered by WBS/PERT. Do not use conclusions from other estimators. Do not price the work.
```

```text
Use $codex-effort-estimator with references/repo-cost-pass.md only for the method instructions. Repository path: [path]. Estimate rebuild or completion effort in person-days. Return measured repository facts, low/base/high effort, assumptions, exclusions, risks, confidence, and what would materially change the estimate. Do not use conclusions from other estimators. Do not price the work unless asked.
```

### Parent Synthesis

The parent should report:

- Pass coverage checklist with `run`, `skipped`, or `not applicable` for every standard delegate, including reasons.
- Method results side by side.
- Range synthesis for any available three-point data, including WBS-derived variance aggregation when independent PERT was skipped.
- Agreement and disagreement.
- Scope or assumption differences causing gaps.
- Sizing facts separately from effort estimates, including count confidence and unresolved count ambiguity.
- Component unit anchor separately from WBS, including unit anchors, reuse assumptions, and whether the difference suggests WBS overreach, WBS thinness, or legitimate scope/risk divergence.
- Parametric model separately from component-unit and WBS, including equation, coefficients, and calibration confidence.
- Function point and use case point results separately when run, including count ambiguity and productivity assumptions.
- Top-down three-point result as a coarse independent whole-project anchor, not a WBS-derived estimate.
- Constraint capacity result as feasibility evidence: whether the final range is calendar/staffing plausible and which staffing assumptions are required.
- Risk model result separately from public/report review, including expected risk exposure, correlated high-risk scenario, and overlap warnings.
- Discovery effort separately from implementation effort when requirements are not stable enough for delivery estimating.
- Analogy calibration separately from raw WBS/PERT, including which historical differences justify any adjustment.
- AI-assisted adjustment separately from the raw human estimate when the user explicitly assumes AI coding assistance. Show which WBS lines changed, which did not, and which fixed coefficient was applied.
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
- Do not import external skill conclusions into this workflow; keep method passes self-contained unless the user explicitly asks for comparison.
- Do not include rates, currency, or price unless the user asks or provides unit prices.
- Do not treat generated/vendor code, sample data, or bundled templates as full custom-build effort without saying why.
- Do not estimate repeated variants (regions, branches, similar reports/screens) as fully independent builds; estimate a shared framework once plus reduced-cost variants, and state the variant factor.
- Do not count the same risk more than once; if three-point high values already embed risk, do not also add a separate reserve line and headline the correlated endpoint-sum high for the same uncertainty.
- Do not present an uncalibrated bottom-up total as anchored; cross-check it against a top-down per-unit figure and say when no measured productivity baseline exists.
- Do not let analogy calibration override current scope evidence without explaining the comparable project, differences, and confidence.
- Do not produce implementation-only precision when the proper answer is a discovery estimate plus confirmation questions.
- Do not apply AI coding assistance reductions unless the user explicitly says that assumption is in scope.
- Do not reduce requirements, stakeholder review, acceptance, report visual QA, data validation, deployment coordination, or unresolved-domain-risk work just because coding is AI-assisted.
- For public-sector or RFP work, include deliverables, review gates, training, manual creation, acceptance testing, and change-management assumptions.

## References

- `references/methods.md`: estimation methods, range logic, and risk adjustment.
- `references/sizing-pass.md`: scope counting instructions for screens, reports, data, integrations, workflows, roles, and deliverables.
- `references/wbs-pass.md`: method-specific instructions for WBS bottom-up subagent passes.
- `references/pert-pass.md`: method-specific instructions for PERT subagent passes.
- `references/analogy-calibration-pass.md`: historical comparison and calibration instructions.
- `references/discovery-pass.md`: discovery and requirements-uncertainty estimate instructions.
- `references/ai-coding-assistance-adjustment.md`: line-level fixed-coefficient adjustment rules when AI coding assistance is explicitly assumed.
- `references/public-review-pass.md`: method-specific instructions for public-sector/report/acceptance coverage review.
- `references/repo-cost-pass.md`: method-specific instructions for repository rebuild or completion estimates.
- `references/public-sector-business-systems.md`: WBS and risk factors for government/business systems, especially document and Excel-heavy work.
- `references/output-template.md`: concise output formats for estimates and quote support.
- `references/spreadsheet-output.md`: workbook structure for detailed estimate spreadsheets with method-specific sheets, phase breakdowns, assumptions, risks, and verification expectations.
- `references/workbook-format.md`: fixed workbook layout, sheet names, colors, widths, number formats, and QA rules to keep Excel output consistent.
- `references/three-point-aggregation-golden.md`: deterministic golden case for three-point variance aggregation.
- `references/repetition-and-reuse.md`: economy-of-scale rules for repeated variants and shared skeletons, single-counting of risk, and the top-down per-unit cross-check.
- `scripts/format_estimate_workbook.py`: deterministic post-processor for generated `.xlsx` estimate workbooks.

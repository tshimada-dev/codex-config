# Estimation Methods

Use this reference for software effort estimation when the input is requirements, tasks, documents, or mixed planning material.

## Method Selection

| Situation | Preferred method |
|---|---|
| Requirements are broad but readable | WBS bottom-up with low/base/high ranges |
| Scope has countable screens, reports, data, integrations, or deliverables | Sizing pass before WBS/PERT |
| Scope has countable component families and the estimate is non-trivial | Component unit anchor pass as an independent top-down total estimate, separate from WBS |
| Scope has measurable drivers that can feed an equation | Parametric model pass as an independent coefficient-based total estimate |
| Functional input/output/data/interface signals can be counted | Function point pass as a functional-size anchor |
| Actors and workflows/use cases can be counted | Use case points pass as a workflow-size anchor |
| A coarse whole-project sanity anchor is needed | Top-down three-point pass |
| Deadline, staffing, review gates, or delivery windows matter | Constraint capacity pass |
| Major uncertainty drivers dominate the range | Risk model pass |
| Tasks are already decomposed | PERT per task plus dependency/risk review |
| Similar past work exists | Analogy calibration after WBS/PERT, then adjust for differences |
| Existing codebase is the target | Repository inventory plus rebuild/completion model |
| Requirements are unclear | Discovery estimate first, implementation estimate second |
| AI coding assistance is explicitly assumed | Raw human estimate first, then line-level AI coding assistance adjustment from `AI削減区分` and fixed coefficients |

## Three-Point Estimate

For each WBS line:

- Optimistic: requirements are stable, templates/examples are reusable, no major blockers.
- Most likely: normal clarification and rework.
- Pessimistic: credible risks materialize, but not catastrophic scope change.

PERT expected value:

```text
expected = (optimistic + 4 * most_likely + pessimistic) / 6
standard_deviation = (pessimistic - optimistic) / 6
variance = standard_deviation ^ 2
```

Use the expected value for planning. For aggregate ranges, sum expected values and aggregate variance:

```text
total_expected = sum(expected)
total_standard_deviation = sqrt(sum(variance))
confidence_interval = total_expected +/- z * total_standard_deviation
```

Use `z = 1.282` for about 80% confidence, `z = 1.645` for about 90%, and `z = 1.960` for about 95%. Do not present `sum(optimistic)` and `sum(pessimistic)` as the normal aggregate range unless you explicitly mean a fully correlated best/worst-case scenario.

## Range Synthesis

Apply this calculation to any low / most likely / high data, even when the independent PERT pass was skipped. WBS three-point rows can and should be aggregated with the same variance formula.

Report two different ranges when three-point data exists:

| Range | Formula | Meaning |
|---|---|---|
| Variance aggregation CI | `sum(expected) +/- z * sqrt(sum(variance))` | Probabilistic range assuming at least partial independence across line items. |
| Endpoint scenario | `sum(low) - sum(high)` | Fully correlated all-best/all-worst scenario. Useful for stress framing, not the default planning range. |

When using WBS rows as the source, label the output `WBS-derived variance aggregation`. It is not a separate independent estimate and must not be counted as another method vote. Use the expected total as the planning center; if it differs from the most-likely total, explain the gap as skew or tail risk.

## Risk Multipliers

Apply multipliers after estimating the base WBS.

| Driver | Typical multiplier |
|---|---:|
| Clear requirements and known stack | 0.9-1.0 |
| Moderate unknowns | 1.1-1.25 |
| Unclear rules or legacy data | 1.2-1.5 |
| External dependency or hard integration | 1.15-1.4 |
| Strict report/PDF fidelity | 1.2-1.6 |
| New or unfamiliar technology | 1.2-1.8 |
| Regulated/security-sensitive workflow | 1.15-1.5 |

Do not stack many multipliers mechanically. Explain the dominant risk drivers and use a single combined adjustment when that is clearer.

## Component Unit Anchor

When scope has countable component families, run `component-unit-anchor-pass.md` as an independent top-down total estimate. This is not the same as a WBS sanity check.

Use this method to create a second anchor from:

- workflows or use cases
- screens or forms
- reports, documents, spreadsheets, PDF outputs, or templates
- imports, exports, integrations, or file formats
- business-rule or calculation clusters
- data sources, migration sets, master data, or historical data
- acceptance cycles, manuals, training, formal deliverables, and handoff items

The component anchor should produce its own low / base / high total from count, unit anchor, framework cost, variant/reuse factor, complexity factor, and confidence notes. Do not derive the unit anchors from WBS totals, do not tune the method to match WBS, and do not expose WBS conclusions to a delegated component-anchor estimator.

Use WBS and component-anchor differences as diagnostic evidence:

| Pattern | Possible interpretation |
|---|---|
| WBS and component anchor broadly agree | Stronger confidence that the estimate is not dominated by one decomposition. |
| WBS is materially higher | WBS may have duplicated shared framework, over-counted variants, or included delivery overhead that the component anchor omitted. |
| Component anchor is materially higher | WBS may be thin on repeated outputs, data/report fidelity, acceptance, documentation, or integration complexity. |
| Both are wide or far apart | Requirements are likely unstable; consider discovery or explicit confirmation questions before presenting a narrow quote range. |

The parent synthesis may prefer either method when assumptions better match the requested deliverable, but it must keep the disagreement visible and explain the cause.

## Parametric Model

Use `parametric-model-pass.md` when countable drivers can feed an explicit estimating equation. This is a separate method from component unit anchors:

- component unit anchor prices component families directly
- parametric model applies coefficients and adjustment factors through an equation

The model should show its drivers, coefficient sources, and adjustment factors. Do not tune coefficients to match WBS or component-unit totals. Prefer local actual productivity when available; otherwise mark coefficients as heuristic or judgment and lower confidence.

## Functional-Size Anchors

Use `function-point-pass.md` when the source exposes functional transaction and data categories:

- External Inputs
- External Outputs
- External Inquiries
- Internal Logical Files
- External Interface Files

Use `use-case-points-pass.md` when the source exposes actors and business workflows/use cases. These methods are valuable because they size the system from user-visible functionality rather than delivery phases.

Use these as pragmatic anchors, not certification claims, unless the work was performed to the relevant formal standard. If boundaries are ambiguous, use ranges and state confidence.

## Top-Down Three-Point

Use `top-down-three-point-pass.md` as a coarse whole-project independent anchor. It is intentionally less detailed than WBS, but it helps detect single-anchor drift. It should directly estimate optimistic / most likely / pessimistic totals from delivery class and dominant drivers. Do not decompose into WBS lines.

## Constraint Capacity

Use `constraint-capacity-pass.md` when delivery date, staffing, review gates, acceptance windows, procurement cadence, or calendar feasibility matters. This pass estimates a feasible envelope rather than a feature build size. Keep person-days and calendar duration separate.

When the final recommended range exceeds feasible capacity under plausible staffing, report the staffing/scope/schedule implication instead of silently accepting the number.

## Method Dependence And False Convergence

Parent synthesis must evaluate method independence before using method agreement as confidence evidence.

Create method-dependence clusters by grouping methods that share the same dominant assumptions:

- the same scope count, such as actors, use cases, screens, reports, imports, or entities
- the same inferred hidden scope, such as "remaining similar workflows"
- the same productivity coefficient or person-hours-per-unit assumption
- the same lifecycle inclusion, such as full acceptance, handoff, or documentation
- the same risk uplift, contingency, or public/report review adjustment

Agreement inside one cluster is useful, but it is not several independent votes. For example, WBS, component-unit anchor, UCP, and parametric outputs may all land high because they price the same use-case count with similar productivity assumptions. Treat that as one high cluster, then compare it against function point, constraint capacity, top-down three-point, analogy, or measured productivity anchors that use different evidence.

Use this mechanical default before making a judgment override:

1. Record each method's dominant count, productivity, lifecycle, and risk basis.
2. Put every plausible total method in exactly one cluster. Reject a method only
   with a concrete scope, unit, lifecycle, or evidence incompatibility. For the
   synthesis CLI, record `rejection_dimension`, `evidence_locator`, and
   `rejection_reason`; a rejected-only cluster remains in the ledger with vote 0
   and no representative center.
3. Calculate one cluster representative as the arithmetic median of its plausible
   method centers. Each eligible cluster has `Effective vote = 1`, regardless of
   how many methods it contains.
4. Calculate the neutral planning center as the arithmetic median of eligible
   cluster representatives. Run `scripts/synthesize_method_clusters.py` to make
   this calculation reproducible.
5. A different final center is an override. Keep the neutral center visible and
   name the evidence-specific reason for displacing every plausible independent
   cluster. “Best matches accepted delivery scope” without the actual omitted
   scope or unit difference is not sufficient.
6. Raise convergence confidence only when at least two different eligible cluster
   representatives differ by no more than 20% of their midpoint. Within-cluster
   agreement cannot raise confidence.

Use this reconciliation pattern:

| Pattern | Parent action |
|---|---|
| Several methods agree but share the same count/productivity driver | Report a single cluster and lower confidence in "method convergence". |
| Lower anchors use different evidence and are plausible | Move the planning center toward the lower anchors or widen the final range downward. |
| A high cluster better matches the deliverable because lower anchors omit lifecycle or risk | Keep the higher center, but explicitly name the omitted work or rejected assumption. |
| Constraint capacity is below the selected center | Explain the staffing/calendar implication, and do not use capacity tension alone as proof of scope size. |
| Risk model is derived from the same base/risk assumptions as WBS | Treat it as a risk scenario, not another independent center vote. |

The final synthesis should state which cluster the selected planning center follows and why. If no measured productivity or historical actuals exist, say the cluster weights are judgment-based.

The decision ledger must contain `Cluster`, `Methods`, `Shared assumptions`,
`Representative center`, `Effective vote`, `Independent anchors checked`,
`Anchor disposition`, `Decision impact`, and `Reason`. Allowed dispositions are
`adopted`, `shifted`, `rejected_scope_mismatch`, `rejected_unit_mismatch`,
`rejected_lifecycle_mismatch`, `rejected_evidence_mismatch`, and `sanity_only`.

## Risk Model

Use `risk-model-pass.md` when a few uncertainty drivers materially affect the range. The pass should expose probability, impact, correlation, expected risk exposure, and high-risk scenario. It should not hide risk inside an unexplained contingency or double-count risks already embedded in other methods.

Monte Carlo-style outputs are useful when distributions can be stated, but a transparent scenario model is preferable to a fake-precise simulation.

## Quantitative Sanity Checks

- For three-point estimates, pessimistic should usually be about 1.5-3.0x optimistic. Values outside that range are allowed, but require a note explaining the asymmetric risk.
- For very small tasks, avoid false precision; group related tasks when decimals imply more accuracy than the source supports.
- If one line item is more than 25-30% of the total, split it or explain why it cannot be decomposed.
- For repeated variants (regions, branches, similar reports/screens), confirm the estimate uses `framework once plus variants`, not a bespoke count multiplication. Counted artifacts drift high when each is priced as a full build; see `references/repetition-and-reuse.md`.
- Count each risk once. If line `high` values already embed pessimistic risk, do not also stack a separate reserve line and the correlated endpoint-sum high for the same uncertainty.
- Cross-check the bottom-up total against the independent component unit anchor when that pass ran. A per-unit cost well above a credible anchor signals under-applied economy of scale or reuse.
- Compare WBS against parametric, function point, use case point, top-down, constraint, and risk model outputs only after those methods complete. Do not feed WBS results into those passes.
- For FP/UCP and other derived counts, retain source status and source locator for
  every base-count row. Never invent unnamed “remaining” items to reach a stated
  total. Untraced inferred count is a stop condition. If a traceable derived count
  is more than 25% above the explicit source count, keep it as a sensitivity only
  until confirmed and exclude the affected method from center voting.
- If organization-specific actual productivity is available, such as person-days per screen, report, integration, CRUD module, or KLOC, use it as calibration evidence. If no baseline exists, state that the estimate relies on document-derived judgment rather than measured organizational productivity.

## AI Coding Assistance

Apply AI coding assistance only when the user explicitly includes that assumption. Start with the raw human WBS/PERT estimate, then adjust each WBS line using its `AI削減区分` and the fixed coefficients in `ai-coding-assistance-adjustment.md`.

Do not reduce requirements, stakeholder review, acceptance, report visual QA, data validation, deployment coordination, or unresolved domain decisions merely because coding is AI-assisted.

## Calibration Checks

Before finalizing:

- Sizing facts should be visible when scope can be counted; avoid estimating from prose alone when counts are extractable.
- Any available three-point data should have range synthesis; do not leave the planning range as endpoint sums by default.
- No large line item should hide multiple unrelated features.
- Repeated variants and reused skeletons should be priced with economy of scale, and the bottom-up total should pass a top-down per-unit cross-check.
- Method agreement should be clustered by shared assumptions; do not let one assumption family outvote distinct low or high anchors.
- Countable component families should have an independent component unit anchor unless the source is too abstract to support unit counts.
- Measurable driver sets should have a parametric model unless coefficients would be pure fiction.
- Functional-size signals should have function point or use case point anchors when count boundaries are defensible.
- Non-trivial estimates should have a top-down three-point anchor unless the source is too abstract even for delivery-class reasoning.
- Calendar-constrained estimates should have a constraint capacity check.
- Risk-heavy estimates should have a risk model or a stated reason why probabilities/impacts cannot be estimated.
- Management, testing, documentation, and acceptance support should not be omitted.
- Calendar duration should account for review waits, not only person-days.
- Confidence should drop when source documents are samples rather than final specifications.
- Quote ranges should widen when requirements are document-derived and not yet confirmed by workshops.
- If similar past work exists, explain whether it validates, shifts, widens, or is rejected as an anchor.
- If historical productivity exists, state whether current effort is consistent with that baseline or why it differs.
- If requirements are unclear, produce a discovery estimate instead of pretending implementation scope is stable.
- If AI coding assistance is assumed, show both baseline and adjusted effort so the productivity assumption remains auditable.

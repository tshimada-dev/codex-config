# Estimation Methods

Use this reference for software effort estimation when the input is requirements, tasks, documents, or mixed planning material.

## Method Selection

| Situation | Preferred method |
|---|---|
| Requirements are broad but readable | WBS bottom-up with low/base/high ranges |
| Scope has countable screens, reports, data, integrations, or deliverables | Sizing pass before WBS/PERT |
| Tasks are already decomposed | PERT per task plus dependency/risk review |
| Similar past work exists | Analogy calibration after WBS/PERT, then adjust for differences |
| Existing codebase is the target | Repository inventory plus rebuild/completion model |
| Requirements are unclear | Discovery estimate first, implementation estimate second |
| AI coding assistance is explicitly assumed | Raw human estimate first, then phase-specific AI coding assistance adjustment |

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

## Quantitative Sanity Checks

- For three-point estimates, pessimistic should usually be about 1.5-3.0x optimistic. Values outside that range are allowed, but require a note explaining the asymmetric risk.
- For very small tasks, avoid false precision; group related tasks when decimals imply more accuracy than the source supports.
- If one line item is more than 25-30% of the total, split it or explain why it cannot be decomposed.
- If organization-specific actual productivity is available, such as person-days per screen, report, integration, CRUD module, or KLOC, use it as calibration evidence. If no baseline exists, state that the estimate relies on document-derived judgment rather than measured organizational productivity.

## AI Coding Assistance

Apply AI coding assistance only when the user explicitly includes that assumption. Start with the raw human WBS/PERT estimate, then adjust implementation-heavy phases using `ai-coding-assistance-adjustment.md`.

Do not reduce requirements, stakeholder review, acceptance, report visual QA, data validation, deployment coordination, or unresolved domain decisions merely because coding is AI-assisted.

## Calibration Checks

Before finalizing:

- Sizing facts should be visible when scope can be counted; avoid estimating from prose alone when counts are extractable.
- Any available three-point data should have range synthesis; do not leave the planning range as endpoint sums by default.
- No large line item should hide multiple unrelated features.
- Management, testing, documentation, and acceptance support should not be omitted.
- Calendar duration should account for review waits, not only person-days.
- Confidence should drop when source documents are samples rather than final specifications.
- Quote ranges should widen when requirements are document-derived and not yet confirmed by workshops.
- If similar past work exists, explain whether it validates, shifts, widens, or is rejected as an anchor.
- If historical productivity exists, state whether current effort is consistent with that baseline or why it differs.
- If requirements are unclear, produce a discovery estimate instead of pretending implementation scope is stable.
- If AI coding assistance is assumed, show both baseline and adjusted effort so the productivity assumption remains auditable.

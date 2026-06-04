# Estimation Methods

Use this reference for software effort estimation when the input is requirements, tasks, documents, or mixed planning material.

## Method Selection

| Situation | Preferred method |
|---|---|
| Requirements are broad but readable | WBS bottom-up with low/base/high ranges |
| Tasks are already decomposed | PERT per task plus dependency/risk review |
| Similar past work exists | Analogy estimate, then adjust for differences |
| Existing codebase is the target | Repository inventory plus rebuild/completion model |
| Requirements are unclear | Discovery estimate first, implementation estimate second |

## Three-Point Estimate

For each WBS line:

- Optimistic: requirements are stable, templates/examples are reusable, no major blockers.
- Most likely: normal clarification and rework.
- Pessimistic: credible risks materialize, but not catastrophic scope change.

PERT expected value:

```text
expected = (optimistic + 4 * most_likely + pessimistic) / 6
standard_deviation = (pessimistic - optimistic) / 6
```

Use the PERT expected value for planning, but present rounded ranges for stakeholders.

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

## Calibration Checks

Before finalizing:

- No large line item should hide multiple unrelated features.
- Management, testing, documentation, and acceptance support should not be omitted.
- Calendar duration should account for review waits, not only person-days.
- Confidence should drop when source documents are samples rather than final specifications.
- Quote ranges should widen when requirements are document-derived and not yet confirmed by workshops.

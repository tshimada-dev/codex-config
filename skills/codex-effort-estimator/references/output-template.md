# Output Template

Use this structure for concise estimate deliverables.

## Summary

```markdown
## Estimate Summary

- Recommended range: X-Y person-days
- Planning center: Z person-days
- Confidence: High / Medium / Low
- Estimate tier: quick / standard / full, with reason
- Basis: [documents / backlog / repository / interviews]
- Main drivers: [top 3]
- Workbook: [path], unless text-only or quick gut-check output was requested
```

## WBS Table

```markdown
| Category | Scope | Low | Base | High |
|---|---|---:|---:|---:|
| Project management | ... |  |  |  |
| Requirements/design | ... |  |  |  |
| Implementation | ... |  |  |  |
| Reports/data/integrations | ... |  |  |  |
| Testing/acceptance | ... |  |  |  |
| Manuals/training/handoff | ... |  |  |  |
| Total |  |  |  |  |
```

## Required Explanation

Always include the selected tier and its required evidence. For `full`, also include every applicable coverage-gate result. Do not claim an optional method was skipped merely because a lower tier did not require it.

- Pass coverage: which method passes were run, skipped, or not applicable, with reasons
- Results and explicit tier/coverage status for each selected total-estimate method
- WBS vs component-anchor agreement/disagreement when both ran
- For `full`, independent parametric, function point, use case point, top-down three-point, constraint capacity, and risk model results when applicable, or explicit gate skip reasons
- Cross-method disagreement: which assumptions, counts, coefficients, productivity baselines, constraints, or risk drivers explain the gap
- Method-dependence decision ledger with one numeric vote per cluster, median
  representative center, neutral center, independent-anchor disposition, and
  decision impact. Keep any evidence-backed override separate from the neutral
  center.
- FP/UCP count provenance and reconciliation warnings; untraced or greater-than-
  25% inflated counts cannot silently enter the planning center.
- Assumptions
- Exclusions
- Risks and contingency
- Open questions that could change the estimate
- Recommended next step

When AI coding assistance is explicitly assumed, also include:

- Raw human baseline
- AI-assisted adjusted range
- Which WBS lines were reduced
- Which WBS lines were not reduced
- Which fixed coefficient was applied for each `AI削減区分`

## Tone

For customers or procurement:

- Be conservative and plain.
- Avoid internal jargon.
- Explain why the range exists.
- Do not over-detail methodology unless asked.

For engineering planning:

- Show decomposition, dependencies, and confidence.
- Separate base work from contingency.
- Highlight validation work and unknowns.

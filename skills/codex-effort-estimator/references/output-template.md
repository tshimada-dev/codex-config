# Output Template

Use this structure for concise estimate deliverables.

## Summary

```markdown
## Estimate Summary

- Recommended range: X-Y person-days
- Planning center: Z person-days
- Confidence: High / Medium / Low
- Basis: [documents / backlog / repository / interviews]
- Main drivers: [top 3]
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

Always include:

- Assumptions
- Exclusions
- Risks and contingency
- Open questions that could change the estimate
- Recommended next step

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

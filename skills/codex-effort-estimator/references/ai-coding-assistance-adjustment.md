# AI Coding Assistance Adjustment

Use this reference only when the user explicitly says AI coding assistance, coding agents, Copilot-like assistance, or AI-assisted implementation is assumed.

This adjusts human effort estimates. It is not an AI-agent wall-clock estimate.

## Principle

Apply the adjustment after raw WBS/PERT. Keep the baseline visible, then show an AI-assisted range. Reduce routine coding work; preserve human-heavy coordination, validation, and uncertainty work.

Do not apply this adjustment just because Codex is helping with the estimate.

## Phase Guidance

| Phase or work type | Typical multiplier | Notes |
|---|---:|---|
| Routine scaffolding, simple CRUD, boilerplate, mechanical refactor | 0.55-0.75 | Strong AI benefit when requirements and patterns are clear. |
| Well-specified implementation and straightforward business logic | 0.65-0.85 | Benefit depends on testability and local conventions. |
| Unit test drafting, fixtures, simple docs, migration scripts | 0.70-0.90 | Keep human review and test design visible. |
| Complex business rules, legacy behavior matching, debugging | 0.80-1.00 | AI helps, but discovery and validation dominate. |
| Integrations, security, deployment, performance, observability | 0.85-1.05 | Often constrained by environment and review cycles. |
| Excel/PDF fidelity, data migration, old-vs-new comparison, visual QA | 0.90-1.10 | Coding may be faster, but validation loops remain; use above 1.0 when AI-generated output increases correction/review cycles. |
| PM, requirements, stakeholder review, acceptance, training, handoff | 0.95-1.00 | Usually not meaningfully reduced by coding assistance. |
| Unclear requirements or unresolved domain decisions | 1.00 | Use discovery instead of a coding reduction. |

Choose the high end of a multiplier when the codebase is unfamiliar, tests are weak, requirements are ambiguous, or outputs require manual validation.

## Procedure

1. Start from a raw WBS/PERT estimate or phase breakdown.
2. Split work into reducible and non-reducible phases.
3. If a WBS/PERT line mixes reducible and non-reducible work, split that line before applying multipliers. If it cannot be split from the evidence, use the more conservative multiplier and say why.
4. Apply phase-specific multipliers only to reducible coding or code-adjacent work.
5. Keep risk and contingency visible. Do not hide unresolved requirements inside a productivity factor.
6. Report both baseline and AI-assisted ranges.
7. If the adjusted total is more than 35% lower than the baseline, explicitly flag the reduction and justify it from scope evidence. If it is more than 45% lower, require strong evidence such as highly repetitive CRUD, strong tests, clear patterns, and stable requirements; otherwise move the multiplier upward.
8. Explain the assumption: AI helps produce and revise code, while a human remains responsible for design decisions, review, integration, validation, and acceptance.

## Output Schema

Return:

- Raw baseline low / base / high person-days.
- Adjustment table with `Phase`, `Baseline`, `Multiplier`, `Adjusted`, and `Rationale`.
- AI-assisted low / base / high person-days.
- Non-reducible work.
- Risks where AI assistance may not help.
- Reduction sanity check, especially when the total reduction exceeds 35%.
- Confidence level.

Do not use this adjustment for pricing unless unit rates and commercial assumptions are provided.

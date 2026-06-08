# AI Coding Assistance Adjustment

Use this reference only when the user explicitly says AI coding assistance, coding agents, Copilot-like assistance, or AI-assisted implementation is assumed.

This adjusts human effort estimates. It is not an AI-agent wall-clock estimate.

## Principle

Apply the adjustment after raw WBS/PERT. Keep the raw baseline visible and frozen, then show an AI-assisted range. Reduce routine coding work; preserve human-heavy coordination, validation, and uncertainty work.

Do not apply this adjustment just because Codex is helping with the estimate.

AI削減区分 must be re-derived whenever the scope or implementation approach changes. A line that was `複雑実装` or `検証重` under a full custom system can become `定型実装` or `コード隣接` under a thinner Excel/VBA, template-fill, configuration, or customer-tested scope. Do not carry old tags forward after scope narrowing.

## Authority Split

Separate the two decisions:

- Reducibility judgment: the WBS/PERT author decides this at line level, because they have the work context. They output `AI削減区分` and a short rationale per line.
- Multiplier authority: this reference owns the fixed coefficients below. The AI adjustment pass must not choose a multiplier to hit a desired total, tune against parent synthesis, or overwrite raw baseline values.

The adjustment is a dependent transformation of the raw estimate, not an independent estimating method.

## Fixed Line-Level Coefficients

Use these constants by `AI削減区分`. Do not substitute phase-wide discretionary factors.

| AI削減区分 | Fixed multiplier | Use when |
|---|---:|---|
| `定型実装` | `0.70` | Routine scaffolding, simple CRUD, boilerplate, mechanical refactor, or well-patterned implementation. |
| `コード隣接` | `0.85` | Well-specified implementation, straightforward business logic, simple tests/docs/scripts, or code-adjacent design work. |
| `複雑実装` | `0.90` | Complex business rules, legacy behavior matching, debugging, integrations, security, deployment, performance, or observability. |
| `検証重` | `0.95` | Excel/PDF fidelity, data migration, old-vs-new comparison, visual QA, acceptance evidence, or report validation. |
| `削減不可` | `1.00` | PM, requirements, stakeholder review, acceptance, training, handoff, unresolved domain decisions, or coordination. |
| `対象外` | `1.00` | Work outside the AI coding assistance assumption. |

Allowed aliases for legacy workbooks:

| Alias | Treat as |
|---|---|
| `削減あり` | `コード隣接` |
| `一部削減` | `コード隣接` |
| `削減困難` | `削減不可` |
| `削りすぎ注意` | `検証重` |

If a line has an unknown `AI削減区分`, apply `1.00`, flag it as `要確認`, and do not invent a coefficient.

## Procedure

1. Start from raw WBS/PERT line items with low / most likely / high values.
2. Require each line to carry `AI削減区分` and a rationale. If a line mixes reducible and non-reducible work, split it before applying multipliers. If it cannot be split from the evidence, use the more conservative category and say why.
   - For foundation, CRUD, common UI, scaffolding, scripts, or patterned implementation lines, explicitly decide whether the line is `定型実装`, `コード隣接`, or `複雑実装`. Do not leave a generic "foundation" line at `複雑実装` without naming the complexity driver such as legacy behavior matching, security, operations, performance, or uncertain integration.
   - For Excel/VBA-heavy scopes, CSV import into sheets, master-data mapping, numbering/code generation, formula wiring, and existing-template value fill are usually `定型実装` or `コード隣接` unless the source requires strict legacy reproduction, complex domain validation, or old-vs-new acceptance evidence.
   - Report/template work is `検証重` only when the delivery includes strict visual fidelity, PDF/print reproduction, or supplier-owned acceptance evidence. If the scope says existing templates are reused and customer performs detailed testing, re-evaluate toward `コード隣接` or `定型実装`.
3. Apply the fixed coefficient for each line's `AI削減区分` to low / most likely / high. Do not adjust the raw baseline cells.
4. Aggregate adjusted lines to phase and total summaries after line-level multiplication.
5. Keep risk and contingency visible. Do not hide unresolved requirements inside a productivity factor.
6. Report both raw baseline and AI-assisted ranges, with base deltas visible.
7. If the adjusted total is more than 35% lower than the baseline, explicitly flag the reduction and justify it from line-level scope evidence. If it is more than 45% lower, require strong evidence such as highly repetitive CRUD, strong tests, clear patterns, and stable requirements; otherwise move uncertain lines to a more conservative category.
8. If implementation-heavy raw base is mostly tagged `複雑実装` / `検証重` and the overall AI reduction is below 15%, explicitly run a conservatism sanity check. Either reclassify routine/patterned lines, or state the concrete complexity drivers that justify the conservative tags.
9. Explain the assumption: AI helps produce and revise code, while a human remains responsible for design decisions, review, integration, validation, and acceptance.

## Output Schema

Return:

- Raw baseline low / base / high person-days.
- Line-level adjustment table with `WBS分類`, `WBS作業`, `AI削減区分`, `Raw Low`, `Raw Base`, `Raw High`, `固定倍率`, `Adjusted Low`, `Adjusted Base`, `Adjusted High`, `Base差分`, `判断者`, `係数権限`, and `根拠`.
- AI-assisted low / base / high person-days.
- Non-reducible work.
- Risks where AI assistance may not help.
- Reduction sanity check, especially when the total reduction exceeds 35%.
- Confidence level.

Do not use this adjustment for pricing unless unit rates and commercial assumptions are provided.

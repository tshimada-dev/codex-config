---
source: skills/codex-effort-estimator/references/output-template.md
source_commit: 17be59e3fe075540200adf764fe1654cf6b3be3d
canonical: false
---

# Output Template

簡潔な estimate deliverable にはこの構造を使います。

## Summary

```markdown
## Estimate Summary

- Recommended range: X-Y person-days
- Planning center: Z person-days
- Confidence: High / Medium / Low
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

必ず含めるもの:

- Pass coverage: どの method pass を run / skipped / not applicable にしたかと理由。
- countable scope がある場合の independent component unit anchor、または実行できなかった理由。
- WBS と component-anchor の agreement/disagreement、および material gap の原因。
- applicable な場合の independent parametric、function point、use case point、top-down three-point、constraint capacity、risk model results、または明示的な skip 理由。
- cross-method disagreement: assumption、count、coefficient、productivity baseline、constraint、risk driver のどれが gap を説明するか。
- Assumptions。
- Exclusions。
- Risks and contingency。
- estimate を変えうる open questions。
- Recommended next step。

AI coding assistance が明示的に前提とされた場合は、次も含めます:

- Raw human baseline。
- AI-assisted adjusted range。
- どの phase を削減したか。
- どの phase を削減しなかったか。

## Tone

customer または procurement 向け:

- conservative かつ plain に書く。
- internal jargon を避ける。
- range が存在する理由を説明する。
- 求められていない限り methodology を過度に詳述しない。

engineering planning 向け:

- decomposition、dependencies、confidence を示す。
- base work と contingency を分ける。
- validation work と unknown を強調する。

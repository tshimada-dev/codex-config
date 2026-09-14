---
source: skills/codex-effort-estimator/references/output-template.md
source_blob: 9da866b90bfa2ff048543cca01309afa2bc267a1
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

選択した tier と、その tier が必要とする evidence を必ず含めます。`full` では該当する coverage-gate result もすべて含めます。lower tier が要求しない method を、skip したと表現しません。

- Pass coverage: tier または coverage gate が選んだ method pass の run / skipped / not applicable と理由。
- 実行した total-estimate method ごとの result と tier/coverage status。
- 両方を実行した場合の WBS と component-anchor の agreement/disagreement。
- `full` では、applicable な independent parametric、function point、use case point、top-down three-point、constraint capacity、risk model result、または明示的な gate skip 理由。
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

## 親統合の必須証跡

method-dependence decision ledgerを含め、clusterごとのmedian代表値、数値の実効票、
neutral center、independent anchorの採否、decision impactを示します。overrideはneutral
centerと分離します。FP/UCPではcount provenanceとreconciliation warningを示し、
untracedまたは25%超inflated countをplanning centerへ暗黙に入れません。

# Estimate Workbook Format

Use this fixed format for estimate workbooks. The goal is repeatable layout: the same request class should produce the same sheet names, order, visual hierarchy, number formats, and column structure.

Do not invent a new visual style per run.

## Workbook Defaults

| Setting | Value |
|---|---|
| Language | Japanese sheet names and labels by default. Use English only if the user asks. |
| Font | `Yu Gothic` when available, otherwise Calibri. |
| Base font size | 10 pt. |
| Title font size | 14 pt, bold. |
| Number format for person-days | `0.0` |
| Percent/multiplier format | `0%` for percentages, `0.00` for multipliers. |
| Freeze panes | Freeze rows 1-4 on every sheet so the main table header remains visible. |
| Gridlines | Hide gridlines. If the spreadsheet tool cannot hide them, note the limitation in QA. |
| Merged cells | Avoid merged cells. Use wider columns instead. |
| Formulas | Use formulas for totals and expected values; do not hardcode totals. |

## Color Tokens

Use these colors consistently:

| Token | Hex | Use |
|---|---|---|
| Header | `#1F4E78` | Table headers and primary section bars. |
| HeaderText | `#FFFFFF` | Header text. |
| SubtleHeader | `#D9EAF7` | Secondary section rows. |
| Total | `#E2F0D9` | Total rows and final range rows. |
| Assumption | `#FFF2CC` | Assumptions, open questions, and user-confirmation items. |
| Risk | `#FCE4D6` | Risks, warnings, high-uncertainty notes. |
| Neutral | `#F2F2F2` | Metadata and not-applicable rows. |
| Border | `#D9E1F2` | Thin cell borders. |

## Standard Sheet Order

Use these exact presentation sheet names after formatting. The numeric prefixes must match the visible tab order; run `scripts/format_estimate_workbook.py` after generation so old/raw names and optional-sheet order are normalized.

| Order | Sheet | Required | Purpose |
|---:|---|---|---|
| 0 | `00_結論` | Yes | Customer-facing conclusion: final range, planning center, confidence, and concise rationale. |
| 1 | `01_内訳` | Yes | Readable breakdown with AI-assisted effort, WBS baseline, delta, and the AI tag from WBS/AI adjustment. |
| 2 | `02_規模根拠` | Yes | Counted scope facts and sizing confidence. |
| 3 | `03_WBS` | Yes | WBS bottom-up estimate lines. |
| 4 | `04_PERT` | Yes | Independent PERT task estimates and expected values, or WBS-derived variance aggregation when independent PERT was skipped. |
| 5 | `05_単価アンカー` | Optional | Independent component-unit top-down estimate from countable scope signals. |
| 6 | `06_パラメトリック` | Optional | Independent equation-based estimate from count drivers and coefficients. |
| 7 | `07_FP` | Optional | Function point estimate. |
| 8 | `08_UCP` | Optional | Use case points estimate. |
| 9 | `09_トップダウン` | Optional | Direct whole-project three-point anchor. |
| 10 | `10_AI補正` | Optional | Line-level AI coding assistance adjustment from WBS `AI削減区分` and fixed coefficients. |
| 11 | `11_公共レビュー` | Optional | Public-sector/report/acceptance coverage review. |
| 12 | `12_リスクモデル` | Optional | Risk-adjusted scenario or Monte Carlo-style model. |
| 13 | `13_制約` | Optional | Constraint/capacity feasibility envelope. |
| 14 | `14_Discovery` | Optional | Discovery estimate when implementation scope is unstable. |
| 15 | `15_前提リスク` | Yes | Assumptions, exclusions, risks, and confirmation questions. |
| 16 | `16_類推補正` | Optional | Historical analogy and calibration. |
| 17 | `17_Repo` | Optional | Repository rebuild or completion estimate. |
| 18 | `18_親統合` | Yes | Pass coverage, parent reconciliation, final recommendation, high-risk scenario. |

For high-stakes estimates, include optional sheets that were considered but not applicable with a short `適用なし` row rather than silently changing the workbook structure. For quick internal estimates, optional sheets may be omitted, but required sheets and their order stay fixed.

If a required method sheet such as `03_WBS` or `04_PERT` was not run, keep the sheet and add one visible `適用なし` row with the reason. Do not leave required sheets blank.

Exception: if independent PERT was not run but WBS has low / most likely / high values, `04_PERT` must include a `WBS由来CI` block. This block is a calculation from WBS rows, not an independent PERT estimate.

For presentation workbooks, sheet numbers must match visible tab order. If optional sheets are omitted, the deterministic formatter renumbers remaining tabs so there is no mismatch between sheet position and prefix.

## Shared Sheet Layout

Use the same top layout on every sheet:

| Row | Content |
|---:|---|
| 1 | Sheet title in A1. |
| 2 | Metadata: project name, estimate date, unit, confidence, source document count. |
| 3 | Blank spacer row. |
| 4 | Main table header. Freeze panes below this row. |
| 5+ | Main table data. |

Use a short note block below the main table only when needed. Do not place important numeric totals only in free text.

## Standard Columns

### `00_結論`

Top conclusion table columns:

`結論`, `値`, `読み方`, `提出時の扱い`, `補足`, `確認観点`

Include rows for:

- Final recommended range.
- Planning center.
- Confidence.
- Baseline human range.
- AI-assisted adjusted range when applicable.
- Implementation-only range when materially different.
- Main risk drivers.
- Workbook generation assumptions.

Also include a short rationale table and a method comparison table with columns:

`方法別レンジ`, `楽観`, `中心/平均`, `悲観`, `幅`, `メモ`

Do not add a comparison chart. The table itself is the auditable artifact.

### `01_内訳`

Columns:

`工程/WBS作業`, `AI補助後目安`, `AI補助前WBS`, `差分`, `削減率`, `AI削減区分`, `主な内容/注意`, `参照`

This sheet is for presentation, not a separate estimation or reducibility judgment. Keep formulas and `AI削減区分` traceable to `03_WBS` / `10_AI補正`; do not invent phase-level reducibility labels in the formatter.

If AI adjustment is not applicable, set `AI補正後` to `-` rather than removing the column.

### `02_規模根拠`

Columns:

`分類`, `項目`, `数量`, `根拠`, `確度`, `WBS/PERTへの反映`

### `03_WBS`

Columns:

`分類`, `作業`, `根拠`, `Low`, `Most likely`, `High`, `AI削減区分`, `メモ`

`AI削減区分` values: `定型実装`, `コード隣接`, `複雑実装`, `検証重`, `削減不可`, `対象外`.

For repeated variants and shared skeletons (see `references/repetition-and-reuse.md`), do not collapse the group into one large line and do not split it into many full-cost lines. Use a `framework` line plus reduced-cost `variant` lines, and record the instance count and the variant factor in `根拠` or `メモ` (for example, `framework + 4 variants ×0.2`). Keep risk counted once: if `High` already embeds the risk, do not add a separate reserve line for the same uncertainty.

### `04_PERT`

Columns:

`タスク`, `根拠`, `楽観`, `最頻/普通`, `悲観`, `期待値`, `SD`, `分散`, `AI削減区分`, `メモ`

Expected formula:

```text
=([Optimistic cell] + 4 * [Most likely cell] + [Pessimistic cell]) / 6
```

For example, when `楽観`, `最頻/普通`, and `悲観` are columns C, D, and E on row 5, use `=(C5+4*D5+E5)/6`. Use cell references or structured table references supported by the spreadsheet tool; do not emit display-label formulas such as `=(Optimistic+4*Most likely+Pessimistic)/6`.

SD formula example: `=(E5-C5)/6`.

Variance formula example: `=G5^2` when SD is column G.

For totals, sum `期待値` and `分散`, then calculate aggregate SD with `=SQRT(SUM([variance range]))`. Show the stakeholder confidence interval as `total expected +/- z * aggregate SD`; use `z=1.645` for the default 90% range. Do not use simple sums of optimistic and pessimistic columns as the normal total range.

When independent PERT was skipped and WBS three-point rows exist, add a `WBS由来CI` table with:

`Source`, `Most likely total`, `Expected total`, `Total SD`, `90% CI Low`, `90% CI High`, `Endpoint Low`, `Endpoint High`, `Interpretation`

Use WBS row low / most likely / high values as the source. Mark the table as `derived from WBS; not an independent method`.

When `04_PERT` is WBS-derived, add a visible banner near the top of the sheet stating that independent PERT was not run and the sheet must not be treated as an independent method result.

### `05_単価アンカー`

Columns:

`分類`, `数量`, `数量根拠`, `共通基盤Low`, `共通基盤Base`, `共通基盤High`, `単価Low`, `単価Base`, `単価High`, `係数`, `Low`, `Base`, `High`, `根拠/メモ`

Use formulas for family totals:

```text
Low = framework_low + count * unit_low * factor
Base = framework_base + count * unit_base * factor
High = framework_high + count * unit_high * factor
```

Include a total row. Add a visible note that this sheet is an independent top-down component anchor and must not use WBS totals or WBS-derived PERT values.

### `06_パラメトリック`

Columns:

`ドライバ`, `数量`, `数量根拠`, `係数Low`, `係数Base`, `係数High`, `係数根拠`, `調整係数Low`, `調整係数Base`, `調整係数High`, `Low`, `Base`, `High`, `メモ`

Include the model equation in a visible note. Use formulas for driver totals and adjustment totals. State whether coefficients are local actuals, benchmarks, heuristics, or judgment.

### `07_FP`

Columns:

`種別`, `項目群`, `数量Low`, `数量Base`, `数量High`, `複雑度`, `重み`, `FP Low`, `FP Base`, `FP High`, `Source status`, `Source locator`, `根拠`, `メモ`

Allowed `種別` values: `EI`, `EO`, `EQ`, `ILF`, `EIF`.

Include productivity conversion rows:

`生産性`, `Low`, `Base`, `High`, `根拠`

Show effort formulas from adjusted function points divided by productivity. Do not hardcode converted effort totals.

### `08_UCP`

Columns:

`分類`, `項目`, `複雑度`, `数量`, `重み`, `UCP`, `Source status`, `Source locator`, `根拠`, `メモ`

`分類` values: `Actor`, `Use case`, `TCF`, `ECF`, `Productivity`.

Include rows for UAW, UUCW, UUCP, TCF, ECF, UCP, productivity, and low/base/high effort. Use formulas where practical.

For FP and UCP base-count rows, allowed source statuses are `explicit`,
`source-reported aggregate`, `confirmed inferred`, and `unresolved aggregate`.
Do not assign invented members or complexity to an unresolved aggregate. Add a
visible count-reconciliation row; untraced count or more than 25% inflation is a
formatter warning and a strict-mode blocker.

The reconciliation table columns are `Metric`, `Explicit count`, `Derived count`,
`Untraced inferred`, `Inflation ratio`, and `Guard status`. The formatter
recomputes `(derived - explicit) / explicit` and the expected guard status.

### `09_トップダウン`

Columns:

`観点`, `楽観`, `最頻/普通`, `悲観`, `期待値`, `SD`, `根拠`, `メモ`

Include delivery class and dominant effort drivers. The total row should calculate expected value as `(optimistic + 4 * most likely + pessimistic) / 6`.

### `10_AI補正`

Columns:

`WBS分類`, `WBS作業`, `AI削減区分`, `Raw Low`, `Raw Base`, `Raw High`, `固定倍率`, `Adjusted Low`, `Adjusted Base`, `Adjusted High`, `Base差分`, `判断者`, `係数権限`, `根拠`

Build this sheet from `03_WBS` rows, not from phase totals. Keep raw baseline and adjusted values side by side. Do not overwrite raw WBS cells.

The authority split must be visible:

- `判断者`: normally `WBS作成者`, because line context determines reducibility.
- `係数権限`: `固定係数（参照定数）`, because `references/ai-coding-assistance-adjustment.md` owns multiplier values.

Apply only the documented fixed coefficients:

| AI削減区分 | 固定倍率 |
|---|---:|
| `定型実装` | `0.70` |
| `コード隣接` | `0.85` |
| `複雑実装` | `0.90` |
| `検証重` | `0.95` |
| `削減不可` | `1.00` |
| `対象外` | `1.00` |

### `11_公共レビュー`

Columns:

`観点`, `根拠`, `分類`, `影響`, `非重複の追加候補`

`分類` values: `織込済`, `不足/薄い`, `リスクのみ`, `要確認`.

### `12_リスクモデル`

Columns:

`リスク`, `確率`, `影響Low`, `影響Base`, `影響High`, `期待影響`, `相関グループ`, `根拠`, `確認/緩和`

Also include scenario/P-percentile rows:

`シナリオ`, `Low/P50`, `Base/P80`, `High/P90`, `根拠`

Mark overlap warnings when a risk is likely already represented in WBS, public review, or another method.

### `13_制約`

Columns:

`シナリオ`, `作業日`, `FTE`, `集中係数`, `総容量`, `レビュー/固定バッファ`, `実効容量`, `示唆`, `根拠`

Keep person-days and calendar dates separate. Include fixed constraints and open assumptions.

### `14_Discovery`

Columns:

`調査項目`, `目的`, `Low`, `Likely`, `High`, `成果物`, `実装見積への影響`

### `15_前提リスク`

Use separate tables with the same columns:

`種別`, `内容`, `影響`, `確認/対応`

`種別` values: `前提`, `除外`, `リスク`, `確認`.

### `16_類推補正`

Columns:

`比較対象`, `類似点`, `差分`, `実績/見積`, `信頼度`, `補正示唆`

### `17_Repo`

Columns:

`領域`, `測定事実`, `推定`, `Low`, `Base`, `High`, `メモ`

### `18_親統合`

Start with a tier row or small tier table:

`Item`, `Value`, `Reason`

Include `Estimate tier` as `quick`, `standard`, or `full`, with a one-sentence reason.

Then include a pass coverage table:

`Pass`, `状態`, `理由`, `根拠`

`状態` values: `実行`, `スキップ`, `非該当`.

Then include the reconciliation table:

`論点`, `WBS/PERTとの差`, `親判断`, `Final Low`, `Final Base`, `Final High`, `根拠`

When three or more total-estimate methods are compared, include a method-dependence cluster table:

`Cluster`, `Methods`, `Shared assumptions`, `Representative center`, `Effective vote`, `Independent anchors checked`, `Anchor disposition`, `Decision impact`, `Reason`

Use this table to show whether apparent method agreement is real independent convergence or one assumption family repeating itself. Include data rows, set every eligible cluster's numeric `Effective vote` to 1, and show the median representative and neutral cluster-median center. Allowed dispositions are `adopted`, `shifted`, `rejected_scope_mismatch`, `rejected_unit_mismatch`, `rejected_lifecycle_mismatch`, `rejected_evidence_mismatch`, and `sanity_only`. If the final recommendation follows a high or low cluster while other plausible anchors disagree, the `Reason` must name the concrete deliverable, lifecycle, productivity, or risk incompatibility; a generic scope preference is not sufficient.

Also include a range synthesis table whenever three-point data exists:

`Source`, `Most likely total`, `Expected total`, `Total SD`, `90% CI Low`, `90% CI High`, `Endpoint scenario`, `Interpretation`

When scope contains repeated variants or shared skeletons, include a top-down cross-check table so the economy-of-scale reconciliation is auditable:

`観点`, `件数`, `Bottom-up per-unit`, `Anchor`, `差`, `Variant/reuse factor`, `判断`, `根拠`

`判断` values: `整合`, `繰り返し/再利用で下方調整`, `根拠付きで高位維持`. State the per-unit basis (per report, screen, workflow, or function point), the variant/reuse factor, and whether a measured productivity baseline exists. See `references/repetition-and-reuse.md`.

When the component unit anchor pass ran, include a method-difference table:

`手法`, `Low`, `Base`, `High`, `中心`, `独立性`, `親判断`

Mark `単価アンカー` as independent from WBS when it did not use WBS totals, WBS-derived PERT, parent ranges, or prior estimate artifacts.
Use the same independence column for `パラメトリック`, `FP`, `UCP`, `トップダウン`, `制約`, and `リスクモデル`.

The `独立性` column records whether a pass was generated independently. It does not by itself prove independent evidence at synthesis time. Use the method-dependence cluster table to show shared drivers such as the same use-case count, same productivity coefficient, same acceptance inclusion, or same risk uplift.

## Visual Rules

- Use dark blue headers with white bold text.
- Use the green total fill only for totals and final recommendation rows.
- Use yellow only for assumptions and open questions.
- Use orange/red only for risks and high-uncertainty notes.
- Use thin borders around all table cells.
- Wrap long text columns.
- Right-align numeric columns.
- Set column widths per sheet according to that sheet's actual columns and content. Do not rely on one global default width map when sheet structures differ; each populated column must receive an intentional width based on whether it is a label, number, evidence, or notes column.
- Keep column widths stable:
  - short label columns: 14-18
  - description/evidence columns: 28-45
  - numeric columns: 10-12
  - notes columns: 35-50
- Do not use decorative gradients, images, charts, or large title blocks unless the user asks. Method comparisons must remain tables, not charts.

## QA Checklist

Before delivery, verify:

- Required sheets exist with exact names and order.
- Optional sheets keep their fixed names when present.
- Required columns are present and in order.
- `18_親統合` includes a pass coverage table for every standard delegate with run/skip reason.
- Totals and PERT expected values use formulas.
- PERT total range uses variance aggregation, not simple endpoint sums.
- WBS three-point data produces WBS-derived variance aggregation even when independent PERT was skipped.
- Baseline and AI-assisted values are separate when AI assistance is assumed.
- Public/report review findings are not displayed as comparable total estimates unless explicitly additive.
- `18_親統合` includes a populated method-dependence decision ledger with one numeric vote per eligible cluster when three or more total-estimate methods are compared.
- `07_FP` and `08_UCP` base-count rows include source status and source locator; untraced or inflated counts are not silent center votes.
- Every populated column in every sheet has an intentional width. Check each sheet independently; do not assume a shared width setup covers sheets with different column counts or different long-text columns.
- No formula errors: `#REF!`, `#VALUE!`, `#DIV/0!`, `#NAME?`, `#N/A`.
- Header rows, total rows, and risk/assumption colors follow the token table.
- Text is readable without manual resizing in the main summary and synthesis sheets.
- Render and visually inspect representative detailed sheets with different layouts, including any sheet that has wide evidence/notes text, many numeric columns, or optional method-specific columns.
- Run deterministic workbook QA in `scripts/format_estimate_workbook.py`: total rows must cross-foot against visible numeric rows, AI adjustment formulas must match raw values and fixed coefficients, and breakdown deltas/rates must match their source columns.

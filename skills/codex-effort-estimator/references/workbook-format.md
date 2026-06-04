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

Use these exact sheet names. Keep the numeric prefixes stable. Do not renumber sheets when an optional sheet is omitted.

| Order | Sheet | Required | Purpose |
|---:|---|---|---|
| 0 | `00_サマリー` | Yes | Executive summary, final range, confidence, method comparison. |
| 1 | `01_工程別` | Yes | Phase-level totals and final adjusted values. |
| 2 | `02_規模根拠` | Yes | Counted scope facts and sizing confidence. |
| 3 | `03_WBS` | Yes | WBS bottom-up estimate lines. |
| 4 | `04_PERT` | Yes | Independent PERT task estimates and expected values, or WBS-derived variance aggregation when independent PERT was skipped. |
| 5 | `05_類推補正` | Optional | Historical analogy and calibration. |
| 6 | `06_Discovery` | Optional | Discovery estimate when implementation scope is unstable. |
| 7 | `07_AI補正` | Optional | AI coding assistance adjustment when explicitly assumed. |
| 8 | `08_公共レビュー` | Optional | Public-sector/report/acceptance coverage review. |
| 9 | `09_Repo` | Optional | Repository rebuild or completion estimate. |
| 10 | `10_親統合` | Yes | Pass coverage, parent reconciliation, final recommendation, high-risk scenario. |
| 11 | `11_前提リスク` | Yes | Assumptions, exclusions, risks, and confirmation questions. |

For high-stakes estimates, include optional sheets that were considered but not applicable with a short `適用なし` row rather than silently changing the workbook structure. For quick internal estimates, optional sheets may be omitted, but required sheets and their order stay fixed.

If a required method sheet such as `03_WBS` or `04_PERT` was not run, keep the sheet and add one visible `適用なし` row with the reason. Do not leave required sheets blank.

Exception: if independent PERT was not run but WBS has low / most likely / high values, `04_PERT` must include a `WBS由来CI` block. This block is a calculation from WBS rows, not an independent PERT estimate.

Number gaps from omitted optional sheets are intentional. For example, a workbook may show `00_サマリー`, `01_工程別`, `02_規模根拠`, `03_WBS`, `04_PERT`, `10_親統合`, `11_前提リスク` when optional sheets are not applicable.

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

### `00_サマリー`

Columns: `項目`, `値`, `補足`

Include rows for:

- Final recommended range.
- Planning center.
- Confidence.
- Baseline human range.
- AI-assisted adjusted range when applicable.
- Implementation-only range when materially different.
- Main risk drivers.
- Workbook generation assumptions.

Also include a method comparison table with columns:

`手法`, `楽観/Low`, `普通/Base`, `悲観/High`, `中心/期待値`, `親の解釈`

### `01_工程別`

Columns:

`工程`, `WBS`, `PERT`, `AI補正後`, `親最終`, `メモ`

If AI adjustment is not applicable, set `AI補正後` to `-` rather than removing the column.

### `02_規模根拠`

Columns:

`分類`, `項目`, `数量`, `根拠`, `確度`, `WBS/PERTへの反映`

### `03_WBS`

Columns:

`分類`, `作業`, `根拠`, `Low`, `Most likely`, `High`, `AI削減区分`, `メモ`

`AI削減区分` values: `定型実装`, `コード隣接`, `削減不可`, `対象外`.

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

### `05_類推補正`

Columns:

`比較対象`, `類似点`, `差分`, `実績/見積`, `信頼度`, `補正示唆`

### `06_Discovery`

Columns:

`調査項目`, `目的`, `Low`, `Likely`, `High`, `成果物`, `実装見積への影響`

### `07_AI補正`

Columns:

`分類`, `工程`, `ベースライン`, `倍率`, `補正後`, `削減可否`, `根拠`

Keep `ベースライン` and `補正後` side by side. Do not overwrite the raw estimate.

### `08_公共レビュー`

Columns:

`観点`, `根拠`, `分類`, `影響`, `非重複の追加候補`

`分類` values: `織込済`, `不足/薄い`, `リスクのみ`, `要確認`.

### `09_Repo`

Columns:

`領域`, `測定事実`, `推定`, `Low`, `Base`, `High`, `メモ`

### `10_親統合`

Start with a pass coverage table:

`Pass`, `状態`, `理由`, `根拠`

`状態` values: `実行`, `スキップ`, `非該当`.

Then include the reconciliation table:

`論点`, `WBS/PERTとの差`, `親判断`, `Final Low`, `Final Base`, `Final High`, `根拠`

Also include a range synthesis table whenever three-point data exists:

`Source`, `Most likely total`, `Expected total`, `Total SD`, `90% CI Low`, `90% CI High`, `Endpoint scenario`, `Interpretation`

### `11_前提リスク`

Use separate tables with the same columns:

`種別`, `内容`, `影響`, `確認/対応`

`種別` values: `前提`, `除外`, `リスク`, `確認`.

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
- Do not use decorative gradients, images, charts, or large title blocks unless the user asks.

## QA Checklist

Before delivery, verify:

- Required sheets exist with exact names and order.
- Optional sheets keep their fixed names when present.
- Required columns are present and in order.
- `10_親統合` includes a pass coverage table for every standard delegate with run/skip reason.
- Totals and PERT expected values use formulas.
- PERT total range uses variance aggregation, not simple endpoint sums.
- WBS three-point data produces WBS-derived variance aggregation even when independent PERT was skipped.
- Baseline and AI-assisted values are separate when AI assistance is assumed.
- Public/report review findings are not displayed as comparable total estimates unless explicitly additive.
- Every populated column in every sheet has an intentional width. Check each sheet independently; do not assume a shared width setup covers sheets with different column counts or different long-text columns.
- No formula errors: `#REF!`, `#VALUE!`, `#DIV/0!`, `#NAME?`, `#N/A`.
- Header rows, total rows, and risk/assumption colors follow the token table.
- Text is readable without manual resizing in the main summary and synthesis sheets.
- Render and visually inspect representative detailed sheets with different layouts, including any sheet that has wide evidence/notes text, many numeric columns, or optional method-specific columns.

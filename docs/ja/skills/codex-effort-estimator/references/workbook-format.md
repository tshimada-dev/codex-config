---
source: skills/codex-effort-estimator/references/workbook-format.md
source_commit: c689b105822474ff84cd516f33c664c4ed7d4cfa
canonical: false
---

# Estimate Workbook Format

estimate workbook ではこの固定 format を使います。目的は repeatable layout です。同じ request class では、同じ sheet names、order、visual hierarchy、number formats、column structure を出力します。

run ごとに新しい visual style を作らないでください。

## Workbook Defaults

| Setting | Value |
|---|---|
| Language | default では日本語 sheet names と labels。ユーザーが求めた場合だけ English。 |
| Font | 利用可能なら `Yu Gothic`、なければ Calibri。 |
| Base font size | 10 pt。 |
| Title font size | 14 pt、bold。 |
| Number format for person-days | `0.0` |
| Percent/multiplier format | percentage は `0%`、multiplier は `0.00`。 |
| Freeze panes | main table header が見えるよう、全 sheet で rows 1-4 を freeze。 |
| Gridlines | gridlines を hide。spreadsheet tool が非対応なら QA に limitation を記録。 |
| Merged cells | merged cells は避ける。代わりに columns を広げる。 |
| Formulas | totals と expected values には formulas を使う。totals を hardcode しない。 |

## Color Tokens

次の色を一貫して使います。

| Token | Hex | Use |
|---|---|---|
| Header | `#1F4E78` | table headers と primary section bars。 |
| HeaderText | `#FFFFFF` | header text。 |
| SubtleHeader | `#D9EAF7` | secondary section rows。 |
| Total | `#E2F0D9` | total rows と final range rows。 |
| Assumption | `#FFF2CC` | assumptions、open questions、user-confirmation items。 |
| Risk | `#FCE4D6` | risks、warnings、high-uncertainty notes。 |
| Neutral | `#F2F2F2` | metadata と not-applicable rows。 |
| Border | `#D9E1F2` | thin cell borders。 |

## Standard Sheet Order

次の exact sheet names を使います。numeric prefixes は安定させます。optional sheet を省略しても renumber しないでください。

| Order | Sheet | Required | Purpose |
|---:|---|---|---|
| 0 | `00_サマリー` | Yes | executive summary、final range、confidence、method comparison。 |
| 1 | `01_工程別` | Yes | phase-level totals と final adjusted values。 |
| 2 | `02_規模根拠` | Yes | counted scope facts と sizing confidence。 |
| 3 | `03_WBS` | Yes | WBS bottom-up estimate lines。 |
| 4 | `04_PERT` | Yes | independent PERT task estimates と expected values、または independent PERT skipped 時の WBS-derived variance aggregation。 |
| 5 | `05_類推補正` | Optional | historical analogy と calibration。 |
| 6 | `06_Discovery` | Optional | implementation scope が不安定な場合の discovery estimate。 |
| 7 | `07_AI補正` | Optional | AI coding assistance が明示的に前提の場合の adjustment。 |
| 8 | `08_公共レビュー` | Optional | public-sector/report/acceptance coverage review。 |
| 9 | `09_Repo` | Optional | repository rebuild または completion estimate。 |
| 10 | `10_親統合` | Yes | pass coverage、parent reconciliation、final recommendation、high-risk scenario。 |
| 11 | `11_前提リスク` | Yes | assumptions、exclusions、risks、confirmation questions。 |

high-stakes estimates では、検討したが applicable でない optional sheets も、黙って workbook structure を変える代わりに短い `適用なし` 行付きで含めます。quick internal estimates では optional sheets を省略できますが、required sheets とその order は固定です。

`03_WBS` や `04_PERT` などの required method sheet を実行しなかった場合も、sheet は残し、理由付きの visible `適用なし` 行を1つ追加します。required sheets を blank のままにしないでください。

例外: independent PERT を実行しなかったが WBS に low / most likely / high values がある場合、`04_PERT` には `WBS由来CI` block を含めなければなりません。この block は WBS rows からの calculation であり、independent PERT estimate ではありません。

optional sheets を省略したことによる number gaps は意図したものです。たとえば optional sheets が applicable でない場合、workbook は `00_サマリー`、`01_工程別`、`02_規模根拠`、`03_WBS`、`04_PERT`、`10_親統合`、`11_前提リスク` のように並べられます。

## Shared Sheet Layout

全 sheet で同じ top layout を使います。

| Row | Content |
|---:|---|
| 1 | A1 に sheet title。 |
| 2 | metadata: project name、estimate date、unit、confidence、source document count。 |
| 3 | blank spacer row。 |
| 4 | main table header。この row の下で freeze panes。 |
| 5+ | main table data。 |

必要な場合だけ main table の下に短い note block を置きます。重要な numeric totals を free text だけに置かないでください。

## Standard Columns

### `00_サマリー`

Columns: `項目`, `値`, `補足`

含める rows:

- final recommended range。
- planning center。
- confidence。
- baseline human range。
- applicable な場合の AI-assisted adjusted range。
- materially different な場合の implementation-only range。
- main risk drivers。
- workbook generation assumptions。

method comparison table も含めます。columns:

`手法`, `楽観/Low`, `普通/Base`, `悲観/High`, `中心/期待値`, `親の解釈`

### `01_工程別`

Columns:

`工程`, `WBS`, `PERT`, `AI補正後`, `親最終`, `メモ`

AI adjustment が applicable でない場合も、column を削除せず `AI補正後` に `-` を入れます。

### `02_規模根拠`

Columns:

`分類`, `項目`, `数量`, `根拠`, `確度`, `WBS/PERTへの反映`

### `03_WBS`

Columns:

`分類`, `作業`, `根拠`, `Low`, `Most likely`, `High`, `AI削減区分`, `メモ`

`AI削減区分` values: `定型実装`, `コード隣接`, `削減不可`, `対象外`.

繰り返しの variant と共有 skeleton（`references/repetition-and-reuse.md` 参照）は、1本の大きな line にまとめず、また多数のフルコスト line に割らないでください。`framework` line と安い `variant` line に分け、instance 数と variant factor を `根拠` または `メモ` に記録します（例: `framework + 4 variants ×0.2`）。risk は1回だけ計上し、`High` が既に risk を含むなら同じ不確実性に別個の reserve line を足しません。

### `04_PERT`

Columns:

`タスク`, `根拠`, `楽観`, `最頻/普通`, `悲観`, `期待値`, `SD`, `分散`, `AI削減区分`, `メモ`

Expected formula:

```text
=([Optimistic cell] + 4 * [Most likely cell] + [Pessimistic cell]) / 6
```

たとえば `楽観`、`最頻/普通`、`悲観` が row 5 の columns C、D、E の場合、`=(C5+4*D5+E5)/6` を使います。cell references または spreadsheet tool が support する structured table references を使い、`=(Optimistic+4*Most likely+Pessimistic)/6` のような display-label formula は出力しないでください。

SD formula example: `=(E5-C5)/6`.

Variance formula example: SD が column G の場合は `=G5^2`。

totals では `期待値` と `分散` を合計し、aggregate SD を `=SQRT(SUM([variance range]))` で計算します。stakeholder confidence interval は `total expected +/- z * aggregate SD` として示し、default 90% range では `z=1.645` を使います。optimistic column と pessimistic column の単純合計を normal total range として使わないでください。

independent PERT が skipped で WBS three-point rows が存在する場合、次の columns を持つ `WBS由来CI` table を追加します。

`Source`, `Most likely total`, `Expected total`, `Total SD`, `90% CI Low`, `90% CI High`, `Endpoint Low`, `Endpoint High`, `Interpretation`

source には WBS row の low / most likely / high values を使います。table には `derived from WBS; not an independent method` と mark します。

### `05_類推補正`

Columns:

`比較対象`, `類似点`, `差分`, `実績/見積`, `信頼度`, `補正示唆`

### `06_Discovery`

Columns:

`調査項目`, `目的`, `Low`, `Likely`, `High`, `成果物`, `実装見積への影響`

### `07_AI補正`

Columns:

`分類`, `工程`, `ベースライン`, `倍率`, `補正後`, `削減可否`, `根拠`

`ベースライン` と `補正後` は横に並べて保持します。raw estimate を overwrite しないでください。

### `08_公共レビュー`

Columns:

`観点`, `根拠`, `分類`, `影響`, `非重複の追加候補`

`分類` values: `織込済`, `不足/薄い`, `リスクのみ`, `要確認`.

### `09_Repo`

Columns:

`領域`, `測定事実`, `推定`, `Low`, `Base`, `High`, `メモ`

### `10_親統合`

pass coverage table から始めます。

`Pass`, `状態`, `理由`, `根拠`

`状態` values: `実行`, `スキップ`, `非該当`.

次に reconciliation table を含めます。

`論点`, `WBS/PERTとの差`, `親判断`, `Final Low`, `Final Base`, `Final High`, `根拠`

three-point data が存在するときは、range synthesis table も含めます。

`Source`, `Most likely total`, `Expected total`, `Total SD`, `90% CI Low`, `90% CI High`, `Endpoint scenario`, `Interpretation`

scope に繰り返しの variant や共有 skeleton がある場合は、economy-of-scale の突合を監査可能にするため top-down cross-check table も含めます。

`観点`, `Bottom-up per-unit`, `Anchor`, `差`, `判断`, `根拠`

`判断` values: `整合`, `繰り返し/再利用で下方調整`, `根拠付きで高位維持`。per-unit の基準（report/screen/workflow/function point あたり）と、measured productivity baseline の有無を明記します。`references/repetition-and-reuse.md` 参照。

### `11_前提リスク`

同じ columns を持つ separate tables を使います。

`種別`, `内容`, `影響`, `確認/対応`

`種別` values: `前提`, `除外`, `リスク`, `確認`.

## Visual Rules

- dark blue headers with white bold text を使う。
- green total fill は totals と final recommendation rows だけに使う。
- yellow は assumptions と open questions だけに使う。
- orange/red は risks と high-uncertainty notes だけに使う。
- 全 table cells に thin borders を付ける。
- long text columns は wrap する。
- numeric columns は right-align する。
- column widths は sheet ごとの実際の columns と content に合わせて設定する。sheet structures が異なるときに global default width map 1つへ依存しない。populate された各 column には、label、number、evidence、notes のどれに当たるかに基づいた意図的な width を与える。
- column widths を安定させる:
  - short label columns: 14-18
  - description/evidence columns: 28-45
  - numeric columns: 10-12
  - notes columns: 35-50
- ユーザーが求めない限り、decorative gradients、images、charts、large title blocks を使わない。

## QA Checklist

delivery 前に確認します。

- required sheets が exact names と order で存在する。
- optional sheets は存在する場合 fixed names を保つ。
- required columns が存在し、順序も正しい。
- `10_親統合` にすべての standard delegate について run/skip reason を含む pass coverage table がある。
- totals と PERT expected values が formulas を使っている。
- PERT total range が simple endpoint sums ではなく variance aggregation を使っている。
- independent PERT が skipped でも、WBS three-point data から WBS-derived variance aggregation が作られる。
- AI assistance が前提の場合、baseline と AI-assisted values が分かれている。
- public/report review findings が明示的に additive でない限り comparable total estimates として表示されていない。
- すべての sheet の populate された column に intentional width がある。sheet ごとに独立して確認し、column 数や long-text columns が異なる sheet に shared width setup が効いていると仮定しない。
- formula errors がない: `#REF!`, `#VALUE!`, `#DIV/0!`, `#NAME?`, `#N/A`.
- header rows、total rows、risk/assumption colors が token table に従っている。
- main summary と synthesis sheets の text が manual resizing なしで読める。
- wide evidence/notes text、多数の numeric columns、optional method-specific columns を持つ sheet を含め、layout が異なる代表的な detailed sheets を render して visual inspect する。

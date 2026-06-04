---
source: skills/codex-effort-estimator/references/spreadsheet-output.md
source_commit: e96e2a4a183cc6d6c911b6a2aa222c8ec5a1f13e
canonical: false
---

# Spreadsheet Output

default の estimate workbook、またはユーザーが Excel workbook、spreadsheet、`.xlsx`、sheet-by-sheet estimate artifact を求めたときに使います。

## Principle

この skill は estimator/orchestrator として保ちます。workbook の作成と検証には専用の `spreadsheets` skill/workflow を使います。estimate workbook は、見た目を整えるだけでなく、数字を audit 可能にするためのものです。

non-trivial な見積もりでは workbook を default で作成します。ユーザーが text-only output を求めた場合、quick gut-check の場合、または有用な表を作れるだけの情報がない場合だけ省略します。

常に `workbook-format.md` を適用します。ユーザーが明示的に別 format を求めない限り、sheet names、order、colors、header rows、number formats、column structure を即興で変えないでください。

local `.xlsx` file が生成された場合は、delivery 前の deterministic post-processing step として `scripts/format_estimate_workbook.py` を実行します。まず formatted copy を書き出す形を優先します。

```powershell
python skills/codex-effort-estimator/scripts/format_estimate_workbook.py path\to\estimate.xlsx --output path\to\estimate_formatted.xlsx
```

generated workbook を上書きする意図がある場合だけ `--in-place` を使います。この script は formatter と validator であり、estimation、range synthesis、visual review の代替として扱ってはいけません。

## Required Workbook Shape

substantial estimates では `workbook-format.md` の standard workbook shape を作成します。各 sheet の概念上の目的は次のとおりです。

| Sheet | Purpose |
|---|---|
| `00_サマリー` | final recommended range、planning center、confidence、method comparison。 |
| `01_工程別` | methods をまたいだ phase-level breakdown: PM、requirements、design、implementation、reports、testing、manuals/handoff。 |
| `02_規模根拠` | source facts: function count、reports、imports、data volumes、integrations、environments、constraints。 |
| `03_WBS` | WBS bottom-up estimate lines。WBS を実行しなかった場合も sheet を残し、`適用なし` 行を追加する。 |
| `04_PERT` | independent PERT task estimates と expected values。independent PERT を実行しなかったが WBS に three-point values がある場合は、`適用なし` だけで終えず `WBS由来CI` block を含める。 |
| `05_類推補正` | 該当する場合の historical analogy と calibration。 |
| `06_Discovery` | implementation scope が不安定な場合の discovery estimate。 |
| `07_AI補正` | AI coding assistance が明示的に前提の場合の adjustment。 |
| `08_公共レビュー` | 該当する場合の public-sector/report/acceptance coverage review。 |
| `09_Repo` | 該当する場合の repository rebuild または completion estimate。 |
| `10_親統合` | parent reconciliation: pass coverage、method differences、final range、implementation-only range、high-risk range。 |
| `11_前提リスク` | assumptions、exclusions、risks、confirmation questions。 |

AI coding assistance が明示的に前提の場合は、専用の `AI補正` / `AI Adjustment` sheet、または `親統合` 内の明確に分離した table を追加します。

optional method sheets を省略しても sheet を renumber しないでください。number gaps は意図したものです。

## Phase Breakdown

ユーザーが「普通見積もりの内訳は何か」「要件定義に何日か」などを尋ねた場合は phase summary を使います。method ごとの phase decomposition sheet は別途作りません。

default phases:

- PM/management
- Requirements/business analysis
- Basic/detailed design
- Implementation, including foundation, screens, business logic, data handling
- Reports/output, including Excel/PDF/CSV
- Testing/acceptance
- Training/manuals/delivery/handoff

phase summary には、WBS most likely、PERT expected、parent final standard など、total-estimate method の center values を phase ごとに含めます。specialist pass が total estimate ではなく coverage/risk review の場合は、review coverage、risk range driver、adjustment candidate として明確に label します。

| Column | Meaning |
|---|---|
| Phase | work phase または delivery area。 |
| WBS most likely | WBS method の central value。 |
| PERT expected | variance aggregation 後の PERT expected value。 |
| Review/adjustment candidate | public-sector/report/repository review finding、risk driver、または non-overlapping adjustment candidate。実際に total estimate でない限り comparable total estimate として提示しない。 |
| Parent final standard | final parent synthesis の central value。 |
| AI-assisted adjusted | AI coding assistance が明示的に前提の場合の final adjusted central value。 |
| Notes | basis、assumptions、risk driver。 |

total row は hardcoded total ではなく formula にします。

## Method Comparison

summary には method comparison table を含めます。

| 手法 | 楽観/Low | 普通/Base | 悲観/High | 中心/期待値 | 親の解釈 |
|---|---:|---:|---:|---:|---|

synthesis sheet には pass coverage table も必ず含めます。

| Pass | Status | Reason | Evidence |
|---|---|---|---|

English outputs では `run`、`skipped`、`not applicable` を使います。default Japanese workbook では `実行`、`スキップ`、`非該当` を使います。pass を黙って省略しないでください。

three-point data が存在する場合、synthesis sheet には range synthesis を含めます。

| Source | Most likely total | Expected total | Total SD | 90% CI | Endpoint scenario | Interpretation |
|---|---:|---:|---:|---|---|---|

source が WBS の場合は `WBS-derived variance aggregation` または `WBS由来CI` と label し、独立した method result として提示しないでください。

PERT では次を示します。

- optimistic
- most likely
- pessimistic
- `(O + 4M + P) / 6` による expected value
- `(P - O) / 6` による standard deviation
- `standard_deviation ^ 2` による variance
- `sum(expected) +/- z * sqrt(sum(variance))` による aggregate confidence interval

通常の aggregate PERT range として `sum(optimistic)` と `sum(pessimistic)` を使わないでください。endpoint sums を示す場合は、default confidence interval ではなく fully correlated best/worst-case scenario と label します。

WBS では次を示します。

- WBS component
- basis
- low / most likely / high。ここで `likely` は central most-likely estimate
- total formulas

review または adjustment pass は、意図的な total estimate でない限り total-estimate methods と分けます。次を示します。

- coverage findings: already covered / missing or thin / risk-only
- non-overlapping の場合だけ additive adjustment candidates
- pass が full adjusted total を明示的に作った場合だけ adjusted low/base/high range

review output が adjustment candidate に過ぎない場合、public-sector/report review を WBS や PERT と並ぶ comparable total estimate のように置かないでください。

sizing、discovery、analogy calibration pass の役割は明確に保ちます。

- Sizing は scope counts の evidence であり、total estimate ではない。
- Discovery は delivery scope が安定していない場合の separate pre-implementation effort。
- Analogy calibration は validation または adjustment rationale であり、説明のない WBS/PERT の置き換えではない。
- AI coding assistance adjustment は baseline から assisted effort への phase-specific adjustment であり、新しい independent size estimate ではない。

AI coding assistance adjustment では次を示します。

- raw baseline low/base/high
- phase multipliers
- adjusted low/base/high
- non-reducible work
- assumptions and confidence

## Workbook Quality

deliver 前に確認します。

- workbook が spreadsheet tooling 経由で開けること。
- local Python と `openpyxl` が利用可能な場合、生成された `.xlsx` に `scripts/format_estimate_workbook.py` を実行すること。
- sheet names と order が `workbook-format.md` と一致すること。
- key summary と synthesis ranges を inspect すること。
- `#REF!`、`#VALUE!`、`#DIV/0!`、`#NAME?`、`#N/A` などの formula errors を scan すること。
- 少なくとも summary と detailed sheet 1枚を render して visual review すること。
- long text が適切な column width と wrapping で読めること。
- final `.xlsx` を project `outputs` folder または別の user-visible artifact path に置くこと。

## When To Split Into A Separate Skill

spreadsheet guidance が estimation workbook structure に関するものだけである間は、この skill 内に保ちます。

次のように、estimate を超えた reusable spreadsheet automation に成長した場合だけ別 skill を作ります。

- generic workbook generation scripts
- chart/dashboard templates
- import/export macros
- multiple estimate workbook styles
- recurring workbook QA automation

---
source: skills/codex-effort-estimator/references/methods.md
source_commit: 17be59e3fe075540200adf764fe1654cf6b3be3d
canonical: false
---

# 見積もり手法

requirements、tasks、documents、mixed planning material を入力に software effort estimation を行うときに使います。

## Method Selection

| Situation | Preferred method |
|---|---|
| Requirements が広いが読める | WBS bottom-up with low/base/high ranges |
| Scope に数えられる screens、reports、data、integrations、deliverables がある | WBS/PERT の前に sizing pass |
| Scope に数えられる component family があり、非 trivial な見積もり | WBS とは別の independent top-down total estimate として component unit anchor pass |
| Scope に equation 化できる measurable drivers がある | coefficient-based total estimate として parametric model pass |
| functional input/output/data/interface signals を数えられる | functional-size anchor として function point pass |
| actors と workflows/use cases を数えられる | workflow-size anchor として use case points pass |
| coarse whole-project sanity anchor が必要 | top-down three-point pass |
| deadline、staffing、review gates、delivery windows が重要 | constraint capacity pass |
| major uncertainty drivers が range を支配する | risk model pass |
| Tasks がすでに分解されている | task ごとの PERT と dependency/risk review |
| 類似した過去作業がある | WBS/PERT 後に analogy calibration し、差分で調整 |
| 既存 codebase が対象 | repository inventory と rebuild/completion model |
| Requirements が不明確 | discovery estimate を先に行い、その後 implementation estimate |
| AI coding assistance が明示的に前提 | raw human estimate の後、phase-specific AI coding assistance adjustment |

## Three-Point Estimate

各 WBS line について:

- Optimistic: requirements が安定し、template/example を再利用でき、大きな blocker がない。
- Most likely: 通常の clarification と rework がある。
- Pessimistic: credible risks は顕在化するが、破滅的な scope change ではない。

PERT expected value:

```text
expected = (optimistic + 4 * most_likely + pessimistic) / 6
standard_deviation = (pessimistic - optimistic) / 6
variance = standard_deviation ^ 2
```

planning には expected value を使います。aggregate range では expected value を合計し、variance を集約します:

```text
total_expected = sum(expected)
total_standard_deviation = sqrt(sum(variance))
confidence_interval = total_expected +/- z * total_standard_deviation
```

`z = 1.282` は約 80% confidence、`z = 1.645` は約 90%、`z = 1.960` は約 95% です。fully correlated best/worst-case scenario を明示する場合を除き、`sum(optimistic)` と `sum(pessimistic)` を通常の aggregate range として提示しないでください。

## Range Synthesis

independent PERT pass を skip した場合でも、low / most likely / high data があればこの計算を適用します。WBS three-point rows も同じ variance formula で aggregate できます。

three-point data がある場合は、次の2種類の range を別物として報告します:

| Range | Formula | Meaning |
|---|---|---|
| Variance aggregation CI | `sum(expected) +/- z * sqrt(sum(variance))` | line item 間に少なくとも部分的な独立性があると仮定した probabilistic range。 |
| Endpoint scenario | `sum(low) - sum(high)` | 全行が同時に best/worst になる fully correlated scenario。stress framing には有用だが、default planning range ではない。 |

WBS rows を source にする場合、出力を `WBS-derived variance aggregation` と label します。これは別の independent estimate ではなく、method vote として数えてはいけません。expected total を planning center に使い、most-likely total と差がある場合は skew または tail risk として説明します。

## Risk Multipliers

base WBS を見積もった後に multiplier を適用します。

| Driver | Typical multiplier |
|---|---:|
| Clear requirements and known stack | 0.9-1.0 |
| Moderate unknowns | 1.1-1.25 |
| Unclear rules or legacy data | 1.2-1.5 |
| External dependency or hard integration | 1.15-1.4 |
| Strict report/PDF fidelity | 1.2-1.6 |
| New or unfamiliar technology | 1.2-1.8 |
| Regulated/security-sensitive workflow | 1.15-1.5 |

多数の multiplier を機械的に積み上げないでください。dominant risk driver を説明し、分かりやすい場合は単一の combined adjustment を使います。

## Component Unit Anchor

scope に数えられる component family がある場合は、`component-unit-anchor-pass.md` を independent top-down total estimate として実行します。これは WBS sanity check とは別物です。

この method は、workflow/use case、screen/form、report/document/spreadsheet/PDF/template、import/export/integration/file format、business-rule/calculation cluster、data source/migration/master data/historical data、acceptance/manual/training/formal deliverable などから別 anchor を作るために使います。

component anchor は、count、unit anchor、framework cost、variant/reuse factor、complexity factor、confidence notes から独自の low/base/high total を出します。unit anchor を WBS total から逆算せず、WBS に合わせるための調整をせず、delegated component-anchor estimator には WBS の結論を見せません。

WBS と component-anchor の差は diagnostic evidence として扱います。

| Pattern | Possible interpretation |
|---|---|
| WBS と component anchor が概ね一致 | estimate が単一 decomposition に支配されていないという confidence が上がる。 |
| WBS が大きく高い | WBS が shared framework を重複計上した、variant を過大に見た、または component anchor が delivery overhead を落とした可能性。 |
| Component anchor が大きく高い | WBS が repeated outputs、data/report fidelity、acceptance、documentation、integration complexity を薄く見た可能性。 |
| 両者が広い、または大きく乖離 | requirements が不安定な可能性があり、narrow quote range の前に discovery や confirmation questions を検討する。 |

parent synthesis は、requested deliverable により合う assumption の method を優先できますが、disagreement は見える形で残し、原因を説明します。

## Parametric Model

countable drivers を explicit estimating equation に入れられる場合は `parametric-model-pass.md` を使います。component unit anchor が component family を直接値付けするのに対し、parametric model は coefficients と adjustment factors を equation として適用します。coefficient は local actual、benchmark、heuristic、judgment のどれかとして記録し、WBS や component-unit totals に合わせて調整しません。

## Functional-Size Anchors

External Inputs、External Outputs、External Inquiries、Internal Logical Files、External Interface Files を数えられる場合は `function-point-pass.md` を使います。actors と business workflows/use cases が見える場合は `use-case-points-pass.md` を使います。これらは delivery phase ではなく user-visible functionality から size を見るための anchors です。正式標準の認定 count ではなく pragmatic anchor として扱い、boundary が曖昧なら range と confidence を示します。

## Top-Down Three-Point

`top-down-three-point-pass.md` は、project 全体を直接 optimistic / most likely / pessimistic で見る粗い independent anchor です。WBS より詳細度は低いですが、single-anchor drift を検知する役に立ちます。hidden WBS に分解しません。

## Constraint Capacity

delivery date、staffing、review gates、acceptance windows、procurement cadence、calendar feasibility が重要な場合は `constraint-capacity-pass.md` を使います。この pass は feature build size ではなく feasible envelope を出します。person-days と calendar duration を分けて扱います。

## Risk Model

few uncertainty drivers が range を大きく左右する場合は `risk-model-pass.md` を使います。probability、impact、correlation、expected risk exposure、high-risk scenario を見える形にし、unexplained contingency に隠しません。

## Quantitative Sanity Checks

- three-point estimates では、pessimistic は通常 optimistic の約 1.5-3.0x です。範囲外も許容されますが、非対称 risk の説明が必要です。
- very small tasks では false precision を避けます。小数が source の精度を超える場合は関連 task を group 化します。
- 1つの line item が total の 25-30% を超える場合は分割するか、分解できない理由を説明します。
- 繰り返しの variant（地区・支店・似た帳票や画面）は、件数の単純掛け算ではなく `framework once plus variants` で見積もれているか確認します。数えた artifact を各々フルビルドとして値付けすると上振れします。`references/repetition-and-reuse.md` を参照。
- risk は1回だけ計上します。line の high が既に悲観 risk を含むなら、同じ不確実性に別個の reserve line と相関 endpoint-sum の high を重ねません。
- component unit anchor pass が実行された場合は、bottom-up total をその independent anchor と突合します。credible anchor を大きく上回る per-unit は、economy of scale や reuse の適用不足の signal です。
- WBS と parametric、function point、use case point、top-down、constraint、risk model の比較は、各 method が完了した後にだけ行います。WBS result をそれらの pass に渡しません。
- 組織固有の actual productivity がある場合、person-days per screen/report/integration/CRUD module/KLOC などを calibration evidence として使います。baseline がない場合は、document-derived judgment に依存していると明記します。

## AI Coding Assistance

AI coding assistance は、ユーザーが明示的にその前提を含めた場合だけ適用します。raw human WBS/PERT estimate から始め、`ai-coding-assistance-adjustment.md` で implementation-heavy phase を補正します。

coding が AI-assisted だからという理由だけで、requirements、stakeholder review、acceptance、report visual QA、data validation、deployment coordination、未解決 domain decision を削減しないでください。

## Calibration Checks

finalize 前に確認します:

- scope を数えられる場合は sizing facts を見える状態にする。count を抽出できるのに prose だけで見積もらない。
- 利用可能な three-point data は range synthesis する。default の planning range を endpoint sums のままにしない。
- 大きな line item に unrelated features を隠さない。
- 繰り返しの variant と再利用 skeleton は economy of scale で値付けし、bottom-up total を top-down per-unit cross-check に通す。
- Countable component family がある場合は、source が抽象的すぎて unit count を作れない場合を除き、independent component unit anchor を持つ。
- measurable driver set がある場合は、coefficient が完全な fiction になる場合を除き parametric model を持つ。
- functional-size signal がある場合は、count boundary が defensible なら function point または use case point anchor を持つ。
- non-trivial estimate では、source が delivery-class reasoning にも抽象的すぎる場合を除き top-down three-point anchor を持つ。
- calendar-constrained estimate では constraint capacity check を持つ。
- risk-heavy estimate では risk model、または probability/impact を見積もれない理由を持つ。
- management、testing、documentation、acceptance support を落とさない。
- calendar duration には person-days だけでなく review wait も考慮する。
- source document が final specification ではなく sample の場合、confidence を下げる。
- requirements が document-derived で workshop 未確認の場合、quote ranges を広げる。
- similar past work がある場合、validate / shift / widen / reject のどれかを説明する。
- historical productivity がある場合、current effort が baseline と整合するか、なぜ違うかを示す。
- requirements が unclear な場合、implementation scope が安定しているふりをせず discovery estimate を出す。
- AI coding assistance が前提の場合、productivity assumption が auditable になるよう baseline と adjusted effort の両方を示す。

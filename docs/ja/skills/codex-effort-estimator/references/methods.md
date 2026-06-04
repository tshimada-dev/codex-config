---
source: skills/codex-effort-estimator/references/methods.md
source_commit: e535debff08e37bf3540fa3677f8a8e610fcfb8f
canonical: false
---

# 見積もり手法

requirements、tasks、documents、mixed planning material を入力に software effort estimation を行うときに使います。

## Method Selection

| Situation | Preferred method |
|---|---|
| Requirements が広いが読める | WBS bottom-up with low/base/high ranges |
| Scope に数えられる screens、reports、data、integrations、deliverables がある | WBS/PERT の前に sizing pass |
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

## Quantitative Sanity Checks

- three-point estimates では、pessimistic は通常 optimistic の約 1.5-3.0x です。範囲外も許容されますが、非対称 risk の説明が必要です。
- very small tasks では false precision を避けます。小数が source の精度を超える場合は関連 task を group 化します。
- 1つの line item が total の 25-30% を超える場合は分割するか、分解できない理由を説明します。
- 繰り返しの variant（地区・支店・似た帳票や画面）は、件数の単純掛け算ではなく `framework once plus variants` で見積もれているか確認します。数えた artifact を各々フルビルドとして値付けすると上振れします。`references/repetition-and-reuse.md` を参照。
- risk は1回だけ計上します。line の high が既に悲観 risk を含むなら、同じ不確実性に別個の reserve line と相関 endpoint-sum の high を重ねません。
- bottom-up total を top-down の per-unit と突合します。credible anchor を大きく上回る per-unit は、economy of scale や reuse の適用不足の signal です。
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
- management、testing、documentation、acceptance support を落とさない。
- calendar duration には person-days だけでなく review wait も考慮する。
- source document が final specification ではなく sample の場合、confidence を下げる。
- requirements が document-derived で workshop 未確認の場合、quote ranges を広げる。
- similar past work がある場合、validate / shift / widen / reject のどれかを説明する。
- historical productivity がある場合、current effort が baseline と整合するか、なぜ違うかを示す。
- requirements が unclear な場合、implementation scope が安定しているふりをせず discovery estimate を出す。
- AI coding assistance が前提の場合、productivity assumption が auditable になるよう baseline と adjusted effort の両方を示す。

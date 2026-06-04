---
source: skills/codex-effort-estimator/references/pert-pass.md
source_commit: e96e2a4a183cc6d6c911b6a2aa222c8ec5a1f13e
canonical: false
---

# PERT Pass

tasks または deliverables を estimate 可能な単位へ分解できる場合、独立した three-point estimate として使います。

次の2つを分けて扱います:

- Independent PERT pass: task-level three-point estimate を独立に作る method pass。
- Variance aggregation: WBS rows を含む既存の low / most likely / high data に適用できる計算。

この independent PERT pass を skip しても、WBS rows に three-point values がある場合は parent synthesis で variance aggregation を行い、`WBS-derived variance aggregation` と label します。この derived CI を独立した estimate として数えないでください。

## Scope

human engineering effort を person-days で見積もります。明示的に求められない限り price、rates、AI-agent wall-clock time は見積もりません。

## Procedure

1. 調査した source file または text block を列挙する。
2. requirements を task-sized units に変換する。unit がまだ広い場合は、見積もる前に分割する。
3. 各 unit について見積もる:
   - Optimistic: requirements が安定し、大きな blocker がない。
   - Most likely: 通常の clarification と rework。
   - Pessimistic: credible risks は顕在化するが、破滅的な scope change ではない。
4. PERT expected value を計算する:

```text
expected = (optimistic + 4 * most_likely + pessimistic) / 6
standard_deviation = (pessimistic - optimistic) / 6
```

5. optimistic と pessimistic の endpoint は合計せず、expected value を合計する。endpoint sum は全 task が同時に best/worst case になることを意味し、通常 range を過大にします。
6. variance で uncertainty を集計する:

```text
task_variance = standard_deviation ^ 2
total_expected = sum(expected)
total_standard_deviation = sqrt(sum(task_variance))
confidence_low = total_expected - z * total_standard_deviation
confidence_high = total_expected + z * total_standard_deviation
```

`z = 1.282` は約 80% confidence、`z = 1.645` は約 90%、`z = 1.960` は約 95% です。別の confidence level が指定されない限り、stakeholder range には 90% を使います。

7. 多くの task が同じ未解決 requirement や integration に依存するなど強く相関している場合、confidence interval を広げるか correlated-risk scenario を別に示します。単純 endpoint sum に黙って戻さないでください。
8. dependency、review-wait、data-quality、integration、report-fidelity、acceptance risks を特定する。
9. AI coding assistance が明示的に scope に含まれる場合、raw human effort values は残したまま、どの task が routine coding、code-adjacent、non-reducible かを downstream adjustment 用に label する。
10. confidence と estimate を大きく変える facts を示す。

## Output Schema

返すもの:

- 調査した source files。
- `Task`, `Basis`, `Optimistic`, `Most likely`, `Pessimistic`, `Expected`, `Standard deviation`, `Variance`, `Notes` を含む task table。
- variance aggregation による total expected person-days と confidence interval。
- task outcomes が十分に independent でない場合の correlated-risk scenario。
- AI coding assistance が明示的に前提の場合の AI-reducibility notes。
- Assumptions and exclusions。
- Major risk drivers。
- Confidence level。
- range を狭める confirmation questions。

他 estimator の結論を使わないでください。明示的に assignment されない限り、public-sector/report review を additive correction として扱わないでください。

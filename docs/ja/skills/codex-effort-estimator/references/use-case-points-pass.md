---
source: skills/codex-effort-estimator/references/use-case-points-pass.md
source_blob: 50b8282226b2c994b62246381f468761ad8e9899
canonical: false
---

# Use Case Points Pass 日本語参考訳

この文書は `skills/codex-effort-estimator/references/use-case-points-pass.md` の
日本語参考訳です。実行時の正本は英語版です。

actors、workflows、use cases、scenarios、business processesが分かる場合に、独立した
use-case-size見積もりを作ります。workflow中心のsystemで、WBSが実装phaseへ過適合する
ことを抑えるために使います。

## Scope

use case pointsから人手工数を人日で見積もります。明示的に求められない限りprice、rate、
AI-agent wall-clock timeは見積もりません。

## Independence Rules

1. WBS total、WBS line、WBS-derived PERT、component-unit total、parent synthesis、
   prior estimate artifact、期待するfinal rangeを使わない。
2. actors、use cases、complexity、factorsはsource documentsとsizing factsだけから導く。
3. productivityを他methodへ合わせない。
4. actor/use-case boundaryの不確実性を明示する。

## Procedure

1. 調査したsourceを列挙する。
2. actorsをsimple / average / complexに分類して数える。
3. use casesをsimple / average / complexに分類して数える。
4. UAWとUUCWを計算し、次の式を使う。

```text
UUCP = UAW + UUCW
UCP = UUCP * TCF * ECF
effort = UCP * productivity_person_days_per_ucp
```

5. legacy Office、integration、report fidelity、data quality、team familiarity、
   user availability、acceptance rigorなどsource-visible factsからTCF/ECF rangeを決める。
6. 調整済みUCPあたり人日のproductivity rangeを、
   `local actual > compatible measured benchmark > heuristic/judgment`の順で選ぶ。
   - heuristicを選ぶ前に`actual-productivity-calibration.md`とCSVを確認する。
   - Anda実測係数は適用条件と単位互換gateを通った場合だけ使う。
   - このpassの調整済みUCP式には調整済みUCPあたり人日を使い、未調整57-point分母の
     係数を混ぜない。
   - 採用source、互換性判断、棄却anchor、confidenceを記録する。
7. WBSや他methodとの比較は、このpass完了後のparent synthesisだけで行う。

## Output Schema

- 調査source
- actor table
- use case table
- TCF/ECF low/base/highと根拠
- productivity assumption、source class、unit basis、互換性判断
- overall low/base/high人日
- assumptions、exclusions、uncertainty、confidence、confirmation questions

他estimatorの結論を使わず、WBSへ合わせてproductivityやfactorを調整しません。

---
source: skills/codex-effort-estimator/references/use-case-points-pass.md
source_commit: 17be59e3fe075540200adf764fe1654cf6b3be3d
canonical: false
---

# Use Case Points Pass 日本語参考訳

この文書は `skills/codex-effort-estimator/references/use-case-points-pass.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

actors、workflows、use cases、scenarios、business processes が分かる場合に、workflow-size anchor を作るために使います。実装 phase ではなく、user-visible functionality から規模を見るため、WBS anchoring の抑制に有効です。

## Independence Rules

1. WBS total、WBS line estimate、WBS-derived PERT、component-unit total、parent synthesis、prior estimate artifact、期待する final range を使わない。
2. actors、use cases、complexity、factors は source documents と sizing facts だけから導く。
3. productivity を他 method に合わせない。
4. actor/use-case boundary の不確実性を明示する。

## Procedure

- actors を simple / average / complex に分類する。
- use cases を simple / average / complex に分類する。
- `UUCP = UAW + UUCW`
- `UCP = UUCP * TCF * ECF`
- `effort = UCP * productivity_person_days_per_ucp`
- TCF/ECF は legacy Office、integration complexity、report fidelity、data quality、team familiarity、user availability、acceptance rigor など source-visible facts から決める。

## Output Schema

- Source files inspected
- Actor table
- Use case table
- TCF/ECF table
- Productivity assumption
- Overall low/base/high person-days
- Uncertainty drivers、confidence、confirmation questions

他 estimator の結論を使わず、WBS に合わせて factors を調整しません。

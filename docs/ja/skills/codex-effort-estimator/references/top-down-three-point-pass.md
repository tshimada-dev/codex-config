---
source: skills/codex-effort-estimator/references/top-down-three-point-pass.md
source_commit: 17be59e3fe075540200adf764fe1654cf6b3be3d
canonical: false
---

# Top-Down Three-Point Pass 日本語参考訳

この文書は `skills/codex-effort-estimator/references/top-down-three-point-pass.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

project 全体を直接 optimistic / most likely / pessimistic で見積もる粗い独立 anchor です。WBS line に分解せず、delivery class と dominant drivers から全体感を出します。

## Independence Rules

1. WBS total、WBS line estimate、WBS-derived PERT、component-unit total、parent synthesis、prior estimate artifact、期待する final range を使わない。
2. hidden WBS を作らない。
3. mental anchors を明示する。
4. document-derived または未確認の source では range を広くする。

## Procedure

- delivery class を一文で説明する。
- functional breadth、data/report fidelity、integrations、acceptance/review burden、documentation/training/handoff、operational constraints を dominant driver として整理する。
- project 全体の optimistic / most likely / pessimistic totals を直接出す。
- `expected = (optimistic + 4 * most_likely + pessimistic) / 6`
- `standard_deviation = (pessimistic - optimistic) / 6`

## Output Schema

- Source files inspected
- Delivery class
- Dominant effort drivers
- Optimistic / most likely / pessimistic person-days
- Expected value and standard deviation
- Assumptions、exclusions、confidence、material change factors

他 estimator の結論を使わず、WBS line に分解しません。

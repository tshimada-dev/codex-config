---
source: skills/codex-effort-estimator/references/discovery-pass.md
source_commit: 2e9aea31a66c2e07356bdcfd832d45ef5182b54b
canonical: false
---

# Discovery Pass

implementation scope が防御可能な delivery estimate を出すには不明確すぎる場合に使います。

## Scope

discovery、requirements definition、investigation、prototype、decision work を person-days で見積もります。discovery effort は implementation effort と分けます。

## Procedure

1. 調査した source file または text block を列挙する。
2. implementation estimating が不安定な理由を特定する:
   - requirements、acceptance criteria、stakeholder decision が不足。
   - data format、data quality、migration volume、legacy behavior が不明。
   - report/template fidelity が未確認。
   - integration、authentication、infrastructure、security、operation constraint が不明。
   - phase gate、deliverables、review cycle、procurement constraint が不明確。
3. discovery work package を定義する:
   - stakeholder interview と workshop。
   - current-work analysis と requirement definition。
   - data/report/template investigation。
   - technical spike または prototype。
   - integration/environment confirmation。
   - acceptance criteria と deliverable confirmation。
   - estimate refresh と implementation planning。
4. 各 discovery work package を low / likely / high person-days で見積もる。
5. discovery 後にどの implementation estimate が出せるか、どの assumption が残るかを示す。

## Output Schema

返すもの:

- 調査した source file。
- implementation estimating がまだ信頼できない理由。
- `Work package`, `Purpose`, `Low`, `Likely`, `High`, `Output` を含む discovery WBS table。
- total discovery low / likely / high person-days。
- implementation estimating 前に必要な decision と artifact。
- ユーザーが求めた場合のみ optional provisional implementation range。低信頼であることを明記する。
- Confidence level。

discovery effort を implementation contingency の中に隠さないでください。

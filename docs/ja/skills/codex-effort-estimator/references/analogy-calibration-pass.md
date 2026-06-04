---
source: skills/codex-effort-estimator/references/analogy-calibration-pass.md
source_commit: 4e0c02d56986cbae7db1327e3fe27ba6b9a4b8e6
canonical: false
---

# 類推較正 Pass

比較可能な過去 project、actual、過去 estimate、delivery metric がある場合に使います。

この pass は estimate を calibration するためのものです。WBS や PERT を、説明のない平均値で置き換えてはいけません。

## Scope

current project と historical anchor を比較し、adjustment candidate、confidence、variance explanation を返します。明示的に求められない限り price は見積もりません。

## Procedure

1. current-scope source と historical-anchor source を列挙する。
2. 各 historical anchor を要約する:
   - delivered scope。
   - actual effort、estimate、または既知の delivery duration。
   - 分かる場合は team size と skill assumption。
   - technology、domain、integration、report、data、acceptance complexity。
   - 記録工数の外で処理された除外、未完了、吸収作業。
3. current scope と anchor を次の観点で比較する:
   - functional size。
   - report/output fidelity。
   - data migration と quality。
   - integration と environment complexity。
   - requirements clarity と stakeholder review load。
   - testing、acceptance、documentation、handoff burden。
4. 比較が credible な場合だけ calibration factor または adjustment candidate を出す。
5. 組織固有の productivity baseline がある場合、画面、帳票、integration、CRUD module、migration object、KLOC あたり人日などで current scope と比較する。
6. current WBS/PERT を維持、上げる/下げる、range を広げる、のどれにすべきかを説明する。

## Output Schema

返すもの:

- 調査した current source と historical anchor。
- `Anchor`, `Scope`, `Actual/Estimate`, `Similarity`, `Differences`, `Reliability` を含む anchor table。
- `Dimension`, `Current vs anchor`, `Implication`, `Adjustment candidate` を含む calibration table。
- 実績組織 metric がある場合の productivity baseline comparison。
- recommended calibration action: keep、shift center、widen range、reject anchor。
- Confidence level。
- calibration 改善に必要な historical data。

assignment が current WBS/PERT total の calibration を明示している場合を除き、他 estimator の結論を使わないでください。

---
source: skills/codex-effort-estimator/references/analogy-calibration-pass.md
source_blob: 8318dcc82eb52a105e734a6ce1985fc675471720
canonical: false
---

# 類推較正 Pass 日本語参考訳

この文書は `skills/codex-effort-estimator/references/analogy-calibration-pass.md` の
日本語参考訳です。実行時の正本は英語版です。

比較可能な過去project、actual、prior estimate、delivery metricがある場合に使います。
WBSやPERTを説明のない平均で置き換えず、current estimateを較正します。

## Scope

current projectをhistorical anchorと比較し、adjustment candidate、confidence、varianceの
説明を返します。明示されない限りpriceは見積もりません。

## Procedure

1. current-scope sourceとhistorical-anchor sourceを列挙する。
2. 各anchorのdelivered scope、actual/estimate/duration、team assumption、technology、
   domain、integration、report、data、acceptance complexity、除外・未完了・外部吸収を要約する。
3. functional size、output fidelity、migration/data quality、integration/environment、
   requirements clarity、review、testing、acceptance、documentation、handoffで比較する。
4. 比較がcredibleな場合だけcalibration factorまたはadjustment candidateを出す。
5. 組織固有baselineがあれば画面、帳票、integration、CRUD、migration、KLOCあたり人日で比較する。
6. WBS/PERTを維持、上下shift、range拡張のどれにするか説明する。

## 完了後calibration ledger

actual effortが受入済みになった後、次の手順でestimate-to-actual loopを閉じます。

1. `calibration-ledger-template.csv`を承認済みproject metrics領域へcopyするか、既存ledgerへ追記する。
2. 非機密の`project_alias`と安定した`scope_fingerprint`を使い、顧客名、価格、credential、
   source文書内容を記録しない。
3. 判断時点のestimate、method、size basis/value、coefficient source、low/center/highを保持する。
4. reporting period、含むlifecycle、scopeが受入済みになってからactualを記録する。
   delivered scopeが異なる場合は`actual_scope_match=false`とし、正規化なしに直接係数へ使わない。
5. `size_value > 0`なら`actual_productivity_pd_per_size = actual_effort_pd / size_value`を計算する。
6. `signed_relative_error = (estimate_center_pd - actual_effort_pd) / actual_effort_pd`と
   `absolute_relative_error = abs(signed_relative_error)`を計算する。
7. 全観測を保持し、不都合なrowを上書きしたり1件を組織baselineへ昇格したりしない。
8. 次回は比較可能なlocal actual、互換なpublic measured benchmark、heuristic/judgmentの順で使う。

actualをrepositoryへ保存できない場合は承認済みprivate metrics領域に置き、estimate artifactには
sanitized aggregateまたはopaque anchor IDだけを記録します。

## Output Schema

- current sourceとhistorical anchor
- `Anchor / Scope / Actual or Estimate / Similarity / Differences / Reliability`表
- `Dimension / Current vs anchor / Implication / Adjustment candidate`表
- actual metricがある場合のproductivity baseline比較
- keep / center shift / range widen / rejectの推奨
- confidenceと改善に必要なhistorical data
- ledger status: not yet due / recorded / scope-mismatched / unavailable、および承認済みlocationかsanitized anchor ID

明示的にcalibrationを依頼されたcurrent WBS/PERT total以外、他estimatorの結論を使いません。

---
source: docs/evaluations/estimator-false-convergence.md
source_blob: fabddb91d0245adb1fa95ececb25cc44520bc5d6
canonical: false
---

# Estimator偽収束ルール評価 日本語参考訳

## 証拠境界

この評価はIssue #18のparent synthesisだけを対象とします。private
`estimation-benchmarks`、元requirements-only packet、Run #2 workbookは取得できず、
再構成・捏造していません。Issue本文とコメントで公開された値だけを使うsynthesis-only
replayであり、新しいfull blind estimateではありません。隔離実行agentにはactual answer keyを
渡していません。

## 事前登録

実装・実行前にrule、AC、score、answer-key isolationを固定しました。

- preregistration SHA-256:
  `2B29B73CD15E0BD450F9747002FA2E9026040C700F6707347EFCB47DEDEDDBDB`
- preregistration Git blob: `01a7f75c3751abbd04d654e6d95c1761eb55fc7e`
- input SHA-256:
  `47E57B01608A37BC154F653F9B19F0733B548C290193F329A1DB01339D7365A2`

## 結果

baselineは公開済みRun #2のcenter 1,200h、range 920-1,760h、UUCP 94です。
candidateは次のcluster ledgerを出力しました。

| Cluster | 代表値 | 実効票 | 採否 | 判断への影響 |
| --- | ---: | ---: | --- | --- |
| use-case/lifecycle | 1,200h | 0 | `sanity_only` | count guardでcenterから除外 |
| implementation-light | 748h | 1 | `adopted` | centerを下げる |
| capacity | 864h | 1 | `adopted` | centerを上げる |

neutral centerは**806h**です。implementation-lightとcapacityはmidpoint比14.39%差で、
固定20%ruleの範囲内です。ただしindependenceは入力cluster assignmentに依存し、scriptが
causal independenceを実証するものではありません。

count auditは`57 explicit / 94 derived / 37 untraced / inflation 64.91%`を
`STOP_UNTRACED_COUNT`とし、高clusterのcenter voteを除外しました。

隔離実行はcandidate invocation 1回、shell/tool call 2回、CLI 149.301ms、outer wall
約0.4秒、instruction packet 828文字でした。

## Hidden scoring

actual mean 697.5hはcandidate提出後だけ使用しました。baselineは+502.5h / +72.04%、
candidateは+108.5h / +15.56%です。candidateは394h、56.49 percentage points改善し、
公開actual range 431-943h内です。806hが唯一の正解とは主張しません。

## AC対応

- `AC-18-1`: eligible clusterごとに数値1票。PASS。
- `AC-18-2`: shared count/productivity/lifecycle/riskを表示し、異なるclusterだけでconfidence判定。PASS。
- `AC-18-3`: 全clusterのdispositionとdecision impact、formatter strict QA。PASS。
- `AC-18-4`: parent-only replayで1,200hから806hへ改善。private full rerun欠落を開示した境界内でPASS。
- `AC-18-5`: 94対57をSTOPし、FP/UCPのsource status/locatorを必須化。PASS。

## 検証と限界

focused/adjacent testは27/27成功しました。これは1件のparent replayであり、普遍的な
accuracy、private benchmark再現、baselineとのfull operation/time比較を証明しません。
cluster assignmentは依然agent/human入力で、free-text count-basis fallbackも残存riskです。
将来は追加のpre-registered caseとexplicit affected-method IDで評価します。

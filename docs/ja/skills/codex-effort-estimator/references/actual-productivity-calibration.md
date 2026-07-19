---
source: skills/codex-effort-estimator/references/actual-productivity-calibration.md
source_blob: a00195592dc2a3e65a81dbeb6657fd02f7c1c847
canonical: false
---

# 実績生産性較正 日本語参考訳

この文書は `skills/codex-effort-estimator/references/actual-productivity-calibration.md`
の日本語参考訳です。実行時の正本は英語版です。

## 証拠の境界

公開実績は Anda、Benestad、HoveによるISESE 2005の査読論文
「A multiple-case study of software effort estimation based on use case points」
（[DOI 10.1109/ISESE.2005.1541849](https://doi.org/10.1109/ISESE.2005.1541849)）
を正本とし、[Simulaの公開記録](https://www.simula.no/research/multiple-case-study-effort-estimation-based-use-case-points)
を機関の書誌記録として参照します。

- 同じ9 use caseのJava web system仕様を4社が実装した。
- 全project活動を含む実工数は587、943、431、829時間だった。
- 公開された未調整規模は57 pointsだった。
- IEEE/ISESE最終版の412-413ページのFigure 2は、57 UUCP、`TCF = 0.6`、
  `EF = 0.605`、20.619調整済みUCP、413時間の方式見積もりを報告した。
- 各社のprocessと品質重視度が異なるため、生産性の広がり自体が重要な実績証拠である。

Simula記録から現在downloadできる20ページのdraftは別版です。そのdraftは未調整の
`57 * 7.5 = 430 hours`例を示し、20.619と413を含みません。この較正の調整済み値は
DOIで特定される最終公開版だけを根拠とし、Simula linkは機関の書誌記録としてだけ
使用します。両ファイルを同一版として扱ってはいけません。

`actual-productivity-calibration.csv`には公開値と再計算可能な係数だけを収録し、
顧客・非公開案件データは含めません。

## 再計算可能な係数

```text
hours_per_unadjusted_point = actual_effort_hours / 57
hours_per_adjusted_ucp = actual_effort_hours / 20.619
person_days_per_adjusted_ucp = hours_per_adjusted_ucp / 8
```

現行の調整済みUCP式と互換な実績範囲は、調整済みUCPあたり
**2.613-5.717人日**です。4社平均は次のとおりです。

```text
mean_actual_hours = (587 + 943 + 431 + 829) / 4 = 697.5
mean_productivity = 697.5 / 20.619 / 8 = 4.229 person-days per adjusted UCP
```

この平均は当該実績集合の中心であり、普遍的なdefaultではありません。

## 単位互換ルール

現行方式は`UCP = UUCP * TCF * ECF`で調整済みUCPを算出し、
`productivity_person_days_per_ucp`を掛けます。この式ではCSVの
`person_days_per_adjusted_ucp`列を使います。

57-pointの分母と調整済みUCPを混ぜてはいけません。
`hours_per_unadjusted_point`はsourceとIssue証拠の再計算用です。

## 適用条件とsource優先順位

優先順位は次のとおりです。

`local actual > compatible measured benchmark > heuristic/judgment`

Anda実績は、use case境界とtransaction count、小規模web/business system、
lifecycle coverage、team能力と技術習熟、非機能要件・process・品質期待が十分比較可能な
場合だけ直接係数として使います。重要な差がある場合はbenchmarkを表示したまま直接適用を
棄却し、より広いrangeまたは適切なlocal anchorを使います。他手法の結果へ寄せるために
係数を選んではいけません。

## UCP passでの使用

1. current sourceからUUCP、TCF、ECF、調整済みUCPを計算する。
2. 比較可能なlocal actualを最初に確認する。
3. local actualがなければ上記適用条件を評価する。
4. 互換なら2.613 / 4.229 / 5.717人日/調整済みUCPをlow/base/highの実測anchorとし、
   sourceを`public_peer_reviewed_actual`と記録する。
5. lifecycleの一部だけがscopeなら、根拠なしに係数を縮小せず、scope factorを実証するか
   anchorを棄却する。
6. UCP結果の横に係数source、互換性判断、process不確実性を記録する。

## Local actualへの移行

案件実績が確定したら、`calibration-ledger-template.csv`と
`analogy-calibration-pass.md`の完了後手順で記録します。scope fingerprint、size basis、
単位、lifecycle coverageが明確なlocal rowだけがこのbenchmarkより高い優先度を持ちます。
1件だけで係数を上書きせず、比較可能な標本がrangeを支持するまで各行を保持します。

## 限界

これは2005年の9 use case systemを4社が実装した1ケースです。測定anchorと監査可能な
較正loopを提供しますが、一般的なUCP精度、FP、画面、帳票、AI支援、現代的distributed
systemの生産性を較正するものではありません。

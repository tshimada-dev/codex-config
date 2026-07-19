---
source: docs/evaluations/estimator-actual-calibration.md
source_blob: 6088f285e01d74b69c078bd353099d9c9e98b7a6
canonical: false
---

# Estimator実績生産性較正 証拠記録 日本語参考訳

この文書は `docs/evaluations/estimator-actual-calibration.md` の日本語参考訳です。
判断と再現手順の正本は英語版です。

## 判断境界

Issue #3は、実績ベースの係数表、仮定ではなく測定済みanchorを使う手法、
estimate-to-actual記録手順を要求します。

Issueが参照するprivate benchmark repositoryとcalibration ledgerは、接続済みGitHubと
対象範囲のlocal workspaceから取得できませんでした。非公開actualや顧客artifactを推測・
捏造していません。

次の3案を比較しました。

1. 組織固有の完了案件actualを待つ。将来の最優先sourceですが、現在は利用不可です。
2. synthetic coefficient tableを作る。syntheticはactual-based基準を満たさないため棄却しました。
3. unit、scope、size、effortが明示された公開査読済みmultiple-case actualを使う。
   測定済みで監査可能、local actual入手時に可逆的に置換でき、単位互換gate付きで現行UCPへ
   接続できるため採用しました。

## Sourceと計算

採用sourceはAnda、Benestad、Hove、ISESE 2005の最終公開版
（[DOI 10.1109/ISESE.2005.1541849](https://doi.org/10.1109/ISESE.2005.1541849)、
[Simula公開記録](https://www.simula.no/research/multiple-case-study-effort-estimation-based-use-case-points)）です。
同じ9 use caseのJava web-system仕様を4社が実装し、実工数は587、943、431、829時間、
最終版412-413ページのFigure 2は57 UUCP、`TCF = 0.6`、`EF = 0.605`、
20.619調整済みUCP、413時間の見積もりを報告します。

Simula記録から現在downloadできる20ページのdraftは同じ版ではなく、
`57 * 7.5 = 430 hours`を示し、20.619と413を含みません。調整済み分母は最終DOI版だけを
根拠とし、Simula linkは機関の書誌記録であって最終版のページ値の根拠ではありません。

```text
company productivity = actual hours / 20.619 adjusted UCP / 8 hours per day
four-company measured range = 2.613-5.717 person-days per adjusted UCP
four-company mean = 697.5 / 20.619 / 8 = 4.229 person-days per adjusted UCP
```

57-point分母と調整済みUCP分母は混ぜません。scope、lifecycle、process、team、technology、
非機能要件の比較gateを通った場合だけ使い、普遍的defaultにはしません。

## 受け入れ基準対応

| ID | 期待結果 | 証拠 | 結果 |
| --- | --- | --- | --- |
| `AC-3-1` | `references/`に実績係数表がある。 | `actual-productivity-calibration.csv`の4 actual rowをtestが再計算する。 | PASS |
| `AC-3-2` | 少なくとも1手法が測定anchorを使う。 | UCP passが`local actual > compatible measured benchmark > heuristic/judgment`を強制し、調整済みUCP rangeへ接続する。 | PASS |
| `AC-3-3` | estimate-to-actual記録手順がある。 | analogy passの完了後手順、formula、privacy境界、ledger template。 | PASS |

## 検証

`skills/codex-effort-estimator/scripts`で次を実行します。

```powershell
python -m unittest -v test_actual_productivity_calibration.py
```

testはsource rowと算術、単位互換性、source優先順位、ledger schema/formula、英日blob同期、
CI登録を確認します。repository CIも同じcommandを実行します。

## 採用判断と残存risk

公開実績benchmarkはguarded fallbackとして採用し、組織baselineとは扱いません。
比較可能なlocal actualを常に優先し、scope mismatch rowは正規化なしに係数へ昇格させず、
1結果でrangeを上書きしません。

証拠は2005年の小規模Java web system 1件を4社が実装した範囲です。一般的なUCP精度や、
FP、帳票、画面、AI支援、distributed systemは較正しません。将来のlocal dataはrow単位で
追加し、このbenchmarkと比較してから採用します。

---
source: skills/codex-effort-estimator/references/function-point-pass.md
source_blob: 1f3e6b449d9d8e8d478b17f550ad64684c2f49d8
canonical: false
---

# Function Point Pass 日本語参考訳

この文書は `skills/codex-effort-estimator/references/function-point-pass.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

入力、出力、照会、内部データ、外部 interface を数えられる場合に、WBS とは独立した functional-size anchor を作るために使います。正式な IFPUG 認定 count ではなく、見積もり比較用の pragmatic function-point pass として扱います。

## Independence Rules

1. WBS total、WBS line estimate、WBS-derived PERT、component-unit total、parent synthesis、prior estimate artifact、期待する final range を使わない。
2. function は source documents と sizing facts だけから数える。
3. boundary が曖昧な場合は range として扱い、confidence を下げる。
4. function points から effort への変換には明示的な productivity range を使い、他 method に合わせない。

## Procedure

- EI: internal data を更新する user/file/API input。
- EO: report、generated file、PDF、complex export、derived output。
- EQ: 派生処理の少ない read/query。
- ILF: system が保守する logical data group。
- EIF: 他 system が保守し参照する external data group。
- simple/average/complex weight を使って UFP を出す。
- 必要に応じて調整係数を適用し、`effort = adjusted_function_points / productivity_fp_per_person_day` で person-days に変換する。

## Output Schema

- Source files inspected
- Function count table: `Type`, `Item group`, `Count low/base/high`, `Complexity`, `Weight`, `Function points`, `Basis`, `Notes`
- Adjustment factors
- Productivity assumption table
- Overall low/base/high person-days
- Ambiguities、confidence、confirmation questions

他 estimator の結論を使わず、WBS に合わせて productivity を調整しません。

## Count provenance guard

EI/EO/EQ/ILF/EIFの各base-count行へ`Source status`と`Source locator`を追加します。
stated aggregateを埋めるためにmemberを発明せず、unresolved aggregateへcomplexityを
割り当てません。explicit/source-reported countとのreconciliationを表示し、untraced
inferred itemはSTOP、25%超の増加は確認までsensitivity-onlyとしてcenter voteから
除外します。
reconciliation列は`Metric`, `Explicit count`, `Derived count`, `Untraced inferred`,
`Inflation ratio`, `Guard status`とし、formatterが数値を再計算します。

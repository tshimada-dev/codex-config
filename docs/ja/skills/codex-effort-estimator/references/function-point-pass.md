---
source: skills/codex-effort-estimator/references/function-point-pass.md
source_commit: 17be59e3fe075540200adf764fe1654cf6b3be3d
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

---
source: skills/codex-effort-estimator/SKILL.md
source_commit: 1b63d59d629306aa2cd33beb2be2afaaadb68a29
canonical: false
---

# codex-effort-estimator 日本語参考訳

この文書は `skills/codex-effort-estimator/SKILL.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

## 目的

ソフトウェア開発、機能追加、公共・業務システム、RFP、GitHub issue backlog、既存 repository の再構築費用などについて、説明可能な工数見積もりを行うための薄い統括スキルです。

## 使い方

依頼内容を見積もりタイプに分類し、必要に応じて `development-estimation`、`plan-estimateeffort`、`cost-estimate` などの既存スキルを使います。依存スキルがない場合は、このスキル内の reference を使って代替します。

## 基本 Workflow

1. scope、out of scope、不明点、対象読者、単位を確認する。
2. document、repository、issue backlog などの根拠を収集する。
3. 規模が大きい場合は、手法ごとに subagent を分ける。
4. WBS に分解する。
5. low / base / high、または PERT で見積もる。
6. 前提、除外、リスク、信頼度、確認事項を含めて要約する。

## Subagent 統括

subagent を使う場合、親 agent は scope、source files、output unit、output schema だけを渡します。親の推測、過去の見積もり、期待するレンジ、他の estimator の結論は渡しません。

標準の delegate は以下です。

- WBS bottom-up pass
- PERT pass
- Public-sector/business-system pass
- Repository cost pass

親 agent は各手法の差分を比較し、前提や scope の違いを明示したうえで、最終レンジと planning center をまとめます。

## Excel 出力

ユーザーが Excel workbook を求める場合は `references/spreadsheet-output.md` を読み、method ごとの sheet、統合 summary、WBS、assumptions、risks、verification sheet を作成します。

## 注意

- 不完全な要件に対して、過度に精密な数字を出さない。
- 外部スキルの結論をそのまま採用せず、手法と前提を比較する。
- 単価や金額は、ユーザーが求めた場合だけ扱う。
- 公共・RFP 案件では、deliverables、review gates、training、manual、acceptance testing、handoff を含める。

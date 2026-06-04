---
source: skills/codex-effort-estimator/SKILL.md
source_commit: b9f2a5e420fecd8c8a4c433d09122f9302b2cf6f
canonical: false
---

# codex-effort-estimator 日本語参考訳

この文書は `skills/codex-effort-estimator/SKILL.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

## 目的

ソフトウェア開発、機能追加、公共・業務システム、RFP、GitHub issue backlog、既存 repository の再構築費用などについて、説明可能な工数見積もりを行うための薄い統括スキルです。

## 使い方

依頼内容を見積もりタイプに分類し、このスキル内の reference を使って見積もります。外部の見積もり Skill は前提にせず、sizing、WBS、PERT、analogy calibration、discovery、公共・帳票 review、repository rebuild/completion の各手法を同一 Skill 内の独立した reference として扱います。

## 基本 Workflow

1. scope、out of scope、不明点、対象読者、単位を確認する。
2. document、repository、issue backlog などの根拠を収集する。
3. 規模が大きい場合は、手法ごとに subagent を分ける。
4. WBS に分解する。
5. low / base / high、または PERT で見積もる。
6. 前提、除外、リスク、信頼度、確認事項を含めて要約する。

## Subagent 統括

subagent を使う場合、親 agent は scope、source files、output unit、output schema、使用する local reference だけを渡します。tool が直接 file/context を選べる場合は、指定した reference と source document だけを渡します。subagent がこの Skill 本文を読む必要がある場合も、手法としては指定 reference だけに従わせ、親の推測、過去の見積もり、期待するレンジ、他の estimator の結論は渡しません。

標準の delegate は以下です。

- Sizing pass: `references/sizing-pass.md`
- WBS bottom-up pass: `references/wbs-pass.md`
- PERT pass: `references/pert-pass.md`
- Analogy calibration pass: `references/analogy-calibration-pass.md`
- Discovery pass: `references/discovery-pass.md`
- Public-sector/business-system review pass: `references/public-review-pass.md` と `references/public-sector-business-systems.md`
- Repository rebuild/completion pass: `references/repo-cost-pass.md`

親 agent は各手法の差分を比較し、前提や scope の違いを明示したうえで、最終レンジと planning center をまとめます。

Sizing は画面、帳票、CSV、データ、連携、deliverables などの規模根拠として扱い、単独の総工数見積もりにはしません。Analogy calibration は過去実績との比較による補正・検証として扱い、WBS/PERT を根拠なく平均値で置き換えません。Discovery は要件が不安定な場合の事前調査・要件定義工数として扱い、実装工数とは分けて表示します。

公共・帳票・受入などの specialist pass は、原則として単純加算する補正値ではなく、WBS/PERT の coverage audit として扱います。親 agent は findings を `already covered`、`missing/thin`、`risk-only` に分け、既に WBS/PERT に含まれる作業は二重計上しません。未織り込み部分だけを調整し、不確実性が高いだけの項目は high range や high-risk scenario に反映します。

## Excel 出力

ユーザーが Excel workbook を求める場合は `references/spreadsheet-output.md` を読み、method ごとの sheet、統合 summary、WBS、assumptions、risks、verification sheet を作成します。公共・帳票 review のような補正候補は、WBS/PERT などの総工数見積と同じ比較表に置かず、coverage/risk review または adjustment candidate として分けて表示します。

## 注意

- 不完全な要件に対して、過度に精密な数字を出さない。
- 外部スキルの結論をこの workflow に混ぜない。比較が必要な場合は、ユーザーが明示したときだけ別扱いにする。
- 単価や金額は、ユーザーが求めた場合だけ扱う。
- 公共・RFP 案件では、deliverables、review gates、training、manual、acceptance testing、handoff を含める。

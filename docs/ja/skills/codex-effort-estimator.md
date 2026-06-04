---
source: skills/codex-effort-estimator/SKILL.md
source_commit: 112b8f198d5f422c0234007742b82e6f8b470ec5
canonical: false
---

# codex-effort-estimator 日本語参考訳

この文書は `skills/codex-effort-estimator/SKILL.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

## 目的

ソフトウェア開発、機能追加、公共・業務システム、RFP、GitHub issue backlog、既存 repository の再構築費用などについて、説明可能な工数見積もりを行うための薄い統括スキルです。

## 使い方

依頼内容を見積もりタイプに分類し、このスキル内の reference を使って見積もります。外部の見積もり Skill は前提にせず、sizing、WBS、PERT、analogy calibration、discovery、AI coding assistance adjustment、公共・帳票 review、repository rebuild/completion の各手法を同一 Skill 内の独立した reference として扱います。

## 基本 Workflow

1. scope、out of scope、不明点、対象読者、単位を確認する。
2. document、repository、issue backlog などの根拠を収集する。
3. 該当する Decision Path をすべて選び、Pass Coverage Gate で全 pass を `run` / `skipped` / `not applicable` に分類し、skip 理由を記録する。
4. 手法 pass を実行する前に subagent が利用可能かを最優先で確認し、利用可能なら規模に関係なく手法ごとに subagent を分ける。
5. WBS、PERT、repo-cost、discovery など該当 pass を実行する。
6. 前提、除外、リスク、信頼度、確認事項、pass coverage を含めて要約する。

## Subagent 統括

subagent 利用の目的は並行作業ではなく、見積もり観点の独立性と anchoring の抑制です。親 agent は手法 pass を始める前に `spawn_agent` などの delegation tool が利用可能かを確認し、利用可能なら対象規模に関係なく手法別 subagent に委譲します。subagent を使う場合、親 agent は scope、source files、output unit、output schema、使用する local reference だけを渡します。tool が直接 file/context を選べる場合は、指定した reference と source document だけを渡します。subagent がこの Skill 本文を読む必要がある場合も、手法としては指定 reference だけに従わせ、親の推測、過去の見積もり、期待するレンジ、他の estimator の結論は渡しません。

標準の delegate は以下です。

- Sizing pass: `references/sizing-pass.md`
- WBS bottom-up pass: `references/wbs-pass.md`
- PERT pass: `references/pert-pass.md`
- Analogy calibration pass: `references/analogy-calibration-pass.md`
- Discovery pass: `references/discovery-pass.md`
- AI coding assistance adjustment pass: `references/ai-coding-assistance-adjustment.md`
- Public-sector/business-system review pass: `references/public-review-pass.md` と `references/public-sector-business-systems.md`
- Repository rebuild/completion pass: `references/repo-cost-pass.md`

親 agent は各手法の差分を比較し、前提や scope の違いを明示したうえで、最終レンジと planning center をまとめます。

非 trivial な見積もりでは、最低限 `sizing または sizing 不要理由`、`WBS/PERT/repo-cost のうち少なくとも1つの工数手法`、`coverage/risk review`、`parent synthesis`、`固定フォーマット Excel workbook` を通します。公共、repo、discovery、analogy、AI補正などの条件付き pass は、実行しない場合も skip 理由を明示します。

Sizing は画面、帳票、CSV、データ、連携、deliverables などの規模根拠として扱い、単独の総工数見積もりにはしません。Analogy calibration は過去実績との比較による補正・検証として扱い、WBS/PERT を根拠なく平均値で置き換えません。Discovery は要件が不安定な場合の事前調査・要件定義工数として扱い、実装工数とは分けて表示します。

公共・帳票・受入などの specialist pass は、原則として単純加算する補正値ではなく、WBS/PERT の coverage audit として扱います。親 agent は findings を `already covered`、`missing/thin`、`risk-only` に分け、既に WBS/PERT に含まれる作業は二重計上しません。未織り込み部分だけを調整し、不確実性が高いだけの項目は high range や high-risk scenario に反映します。

## Excel 出力

Excel workbook は、非 trivial な見積もりの標準成果物として扱います。ユーザーが text-only を求めた場合、または quick gut-check の場合だけ省略します。作成時は `references/spreadsheet-output.md` と `references/workbook-format.md` を読み、固定の sheet 名、sheet 順、列構成、色、数値形式に従って作成します。公共・帳票 review のような補正候補は、WBS/PERT などの総工数見積と同じ比較表に置かず、coverage/risk review または adjustment candidate として分けて表示します。

ユーザーが AI coding assistance を前提として明示した場合は、raw human baseline と AI-assisted adjusted range を分けて示します。補正は実装・定型テスト・雛形生成など coding-heavy な工程に限定し、requirements、stakeholder review、acceptance、帳票目視 QA、data validation、deployment coordination、不明な domain decision は安易に削減しません。

PERT の集計では、各 task の期待値を合計し、レンジは端点の単純合計ではなく分散加算で求めます。標準では `total expected ± 1.645 * sqrt(sum(variance))` を 90% confidence range として扱います。WBS の `Likely` は PERT の `Most likely` と同じ中心値を意味します。

## 注意

- 不完全な要件に対して、過度に精密な数字を出さない。
- 外部スキルの結論をこの workflow に混ぜない。比較が必要な場合は、ユーザーが明示したときだけ別扱いにする。
- 単価や金額は、ユーザーが求めた場合だけ扱う。
- 公共・RFP 案件では、deliverables、review gates、training、manual、acceptance testing、handoff を含める。

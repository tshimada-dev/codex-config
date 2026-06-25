---
source: skills/codex-effort-estimator/references/component-unit-anchor-pass.md
source_commit: 7fda18bc617a3e1bb86991c22e81a7bf090eccd7
canonical: false
---

# Component Unit Anchor Pass 日本語参考訳

この文書は `skills/codex-effort-estimator/references/component-unit-anchor-pass.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

この reference は、数えられる component から独立した top-down 見積もりを作るために使います。目的は anchoring control です。WBS line total、WBS phase allocation、WBS-derived PERT、親 synthesis、期待する最終 range に依存しない総工数 range を出します。

非 trivial な document-driven、RFP、公共、帳票中心、データ中心、workflow 中心の見積もりで、数えられる scope signal がある場合は実行します。WBS の軽い sanity check ではなく、WBS と並ぶ first-class な estimation method として扱います。

## Scope

人間の engineering effort を person-days で見積もります。ユーザーが明示しない限り、price、rate、AI-agent wall-clock time は見積もりません。

この pass は、screen、form、workflow、report、document、spreadsheet、PDF output、template、import、export、file format、integration、interface、business rule、calculation、validation、decision table、data entity、master data、migration、historical dataset、role、environment、deployment target、manual、training、formal deliverable などの数が分かる場合に向いています。

## Independence Rules

1. WBS total、WBS line estimate、WBS-derived variance aggregation、parent synthesis、prior estimate artifact、期待する final range を読まず、使わない。
2. source document、sizing facts、この reference だけを使う。別 pass の sizing facts を使う場合も、count と ambiguity notes だけを使い、effort conclusion は使わない。
3. component count と unit anchor から始める。他 method に合わせるために unit rate を逆算しない。
4. すべての unit anchor を observed baseline、external benchmark、local heuristic、judgment のどれかとして記録する。credible benchmark がない場合はそう述べ、confidence を下げる。
5. shared framework と variant を明示する。framework は一度だけ見積もり、variant は reduced-cost として足す。繰り返し artifact を全て bespoke build として扱わない。
6. 同じ risk を複数回計上しない。

## Procedure

1. inspected source files または text blocks を列挙する。
2. countable scope signals と count confidence を抽出する。
3. component を unit family に grouping する。
4. family ごとに framework cost と unit low/base/high anchor を選ぶ。
5. source-backed な場合だけ reuse factor、complexity factor、confidence factor を適用する。
6. family ごとに `framework + count * unit * factor` で low/base/high を算出する。
7. family totals を合計して component-anchor estimate を作る。
8. WBS との比較は、この pass 完了後の parent synthesis でだけ行う。
9. AI coding assistance が明示されている場合は、どの family が routine coding、code-adjacent、validation-heavy、report-fidelity-heavy、non-reducible かを downstream adjustment 用に label する。
10. confidence と、見積もりを大きく変える事実を述べる。

## Output Schema

- Source files inspected
- Count table: `Component family`, `Count`, `Count basis`, `Count confidence`, `Notes`
- Unit anchor table: `Component family`, `Framework low/base/high`, `Unit low/base/high`, `Reuse or complexity factor`, `Anchor source`, `Rationale`
- Total table: `Component family`, `Low`, `Base`, `High`, `Notes`
- Overall component-anchor low/base/high person-days
- Main assumptions
- Main risks and range drivers
- Confidence level
- Confirmation questions

他 estimator の結論を使わず、WBS に合わせるための調整をしません。

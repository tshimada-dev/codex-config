---
source: skills/codex-effort-estimator/SKILL.md
source_blob: ecd9409e63c02172f2a8826066b361ed6386c4a3
canonical: false
---

# codex-effort-estimator 日本語参考訳

この文書は `skills/codex-effort-estimator/SKILL.md` の日本語参考訳です。実行時に読む canonical な定義は英語版です。

ソフトウェア delivery の person-day range、WBS、timeline feasibility、quote-grade estimate input が必要なときに、説明可能な見積もりを作ります。source facts と judgment を分け、不確実性には range を使い、assumption、exclusion、risk、confidence を示します。人間の delivery estimate を AI-agent の wall-clock time に変換しません。price、rate、currency は求められた場合だけ扱います。

## 最初に tier を選ぶ

[estimate-tiers.md](codex-effort-estimator/references/estimate-tiers.md) を読み、pass を選ぶ前に `quick`、`standard`、`full` を決めます。最終結果には tier、理由、tier が要求する pass の status を記録し、`full` では coverage gate の全 pass も記録します。

- `quick` は、定義された最小 spine とユーザーが指定した pass だけを使う上限付きの見積もりです。method ごとの delegation は必須ではありません。
- `standard` は、定義された spine と指定された1つの独立 sizing anchor を実行します。該当し得る全 pass には拡張しません。
- `full` は、該当する coverage gate をすべて適用します。evidence-based な skip 理由がある場合だけ skip できます。

tier reference の escalation rule に該当するときは tier を上げます。implementation sizing に足るほど入力が安定していないときは、先に discovery を見積もります。

## 作業を route する

[methods.md](codex-effort-estimator/references/methods.md) で method selection、three-point range synthesis、dependence cluster、数値上の safeguard を確認します。必要な method reference だけを読みます。

- countable scope: `sizing-pass.md` と、tier が選んだ component-unit または別の anchor。
- feature/document scope: `wbs-pass.md`。既に task が分解されている場合: `pert-pass.md`。
- measurable driver、functional boundary、workflow: `parametric-model-pass.md`、`function-point-pass.md`、`use-case-points-pass.md` から tier が要求するもの。
- whole-project anchor: `top-down-three-point-pass.md`。
- staffing/calendar: `constraint-capacity-pass.md`、material uncertainty: `risk-model-pass.md`、historical actual: `analogy-calibration-pass.md`、unstable scope: `discovery-pass.md`、existing code: `repo-cost-pass.md`、AI-assisted coding: `ai-coding-assistance-adjustment.md`、public/report/acceptance: `public-review-pass.md` と `public-sector-business-systems.md`。
- repeated variant または shared skeleton: `repetition-and-reuse.md`。

three-point data があれば必ず range synthesis を行います。`WBS-derived variance aggregation` は WBS の不確実性を再表現したものであり、独立した method vote ではありません。synthesis までは method の独立性を保ち、同じ risk を二重に数えず、count、productivity、lifecycle、risk assumption を共有する method を別票にしません。

## Delegation

delegation は独立した viewpoint に役立つ場合にだけ、estimate の規模に比例して使います。quick estimate は parent だけで完了して構いません。独立 pass を委譲する場合は [delegation-input-design.md](codex-effort-estimator/references/delegation-input-design.md) に従い、raw source または mechanical fact だけを渡し、parent conclusion や他 method total は渡しません。dependent adjustment/review pass には宣言された input artifact を渡せます。

## Synthesis と delivery

選択した pass の後に [synthesis.md](codex-effort-estimator/references/synthesis.md) を読みます。planning center を選ぶ前に scope と assumption の差を調整します。public/report review は、加算部分が明確に non-overlapping と示せる場合を除き coverage audit として扱います。

stakeholder 向け出力には `output-template.md` を使います。非 trivial な workbook は `spreadsheet-output.md` と `workbook-format.md` を読み、生成後に `scripts/format_estimate_workbook.py` で format します。quick gut-check または text-only request に workbook は不要です。

## 必須 safeguard

- 不完全な要件を精密な implementation scope として示さない。
- generated/vendor code、sample、template を根拠なく full custom-build effort にしない。
- shared framework は一度だけ見積もり、その後は discount した variant を加える。risk は一度だけ数える。
- AI coding assistance は明示された場合だけ documented な line-level adjustment で適用する。stakeholder work、acceptance、visual QA、data validation、deployment、未解決 domain work を coding assistance だけで減らさない。

---
source: skills/codex-effort-estimator/references/synthesis.md
source_blob: 7086f43990363fa4207f427242cd38e5542ca89c
canonical: false
---

# Parent Synthesis

tier で選んだ pass が完了してから読みます。各 pass の結果と status を残し、互換性のない output を平均して false certainty を作りません。

## Method result の調整

1. sizing evidence、total-estimate method、feasibility check、risk scenario、coverage review を分けて扱う。
2. scope、count provenance、productivity coefficient、lifecycle inclusion、constraint、risk assumption の違いを比較する。
3. dominant な count、coefficient、lifecycle、risk assumption を共有する plausible total method を cluster にまとめる。cluster の effective vote は1つである。`methods.md` の cluster procedure と `scripts/synthesize_method_clusters.py` で neutral center と evidence-based override を残す。
4. demonstrably non-overlapping な `missing/thin` review finding だけを additive adjustment にする。covered finding は validation、uncertain covered finding は range/scenario driver として扱う。
5. discovery effort は implementation effort と分け、AI-assisted output は raw human baseline と分ける。

## 必須結果

selected tier と理由、理由付きの pass coverage、recommended range と planning center、confidence、method agreement/disagreement、assumptions、exclusions、risks、open questions を報告します。total method ごとに input count、coefficient、three-point value を audit できる根拠を残します。

three-point data がある場合は variance aggregation を報告し、WBS-derived aggregation は non-independent と label します。fully correlated endpoint sum を default probabilistic range にしません。

detailed workbook または stakeholder estimate では `output-template.md`、`spreadsheet-output.md`、`workbook-format.md` に従います。

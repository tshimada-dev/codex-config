---
source: skills/codex-debug-discipline/SKILL.md
source_blob: 765b05d234f19bb6343e757a3ff6f77f3144155d
canonical: false
---

# codex-debug-discipline 日本語参考訳

この文書は `skills/codex-debug-discipline/SKILL.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

## 目的

bug、failing tests、flaky behavior、performance regression、wrong output、crash、壊れているという user report について、再現、instrumentation、hypothesis検証、root-cause evidence、regression-test shapeを確立する。恒久的なproduct/repository behavior editは所有せず `codex-implementation-loop` へ渡す。

## 共通開発契約

`rules/development-workflow.md` に従い、expected/actual と authority conflict を記録する。stable な test seam がある場合は regression check が意図した理由で失敗する形を作る。

## Debug Loop

- 原因が明らかで影響範囲が小さい trivial defect では、症状または code path を確認して regression shape を記録し、恒久修正前に `codex-implementation-loop` へ切り替える。
- まず症状を再現または観察する。
- 失敗している command、route、input、state、expected/actual を切り分ける。
- static inspection だけで飛びつかず、可能な限り runnable reproduction を作る。
- subagents が使える場合は、異なる仮説や独立した証拠収集を並列 probe として任せる。
- 必要なら最小限の instrumentation を入れ、最後に削除する。
- root cause と scope が見えたら、bounded work は `codex-implementation-loop`、広い work は `codex-plan-slices` へ遷移する。
- UI behavior の defect では fix 後に `codex-ui-quality-gate` を使う。

## Evidence

報告には以下を残す。

- reproduction command または手順
- observed failure
- relevant files/symbols
- root cause hypothesis
- fix shape
- regression check

## Instrumentation

- temporary log には分かりやすい tag を付ける。
- secret や large data を出力しない。
- finish 前に tagged logs を削除する。

## Stop Rule

runnable reproduction を作る bounded attempt を一度行う。難しければ static inspection に進む。runnable evidence と code-path evidence の両方が得られず、user-only artifacts が必要な場合だけ止まる。

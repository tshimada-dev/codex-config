---
source: skills/codex-debug-discipline/SKILL.md
source_commit: 747e954d067ae3c02d63e4b611dcce9da8ed39c8
canonical: false
---

# codex-debug-discipline 日本語参考訳

この文書は `skills/codex-debug-discipline/SKILL.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

## 目的

bug、failing tests、flaky behavior、performance regression、wrong output、crash、壊れているという user report を、再現、観察、仮説、修正、回帰確認の順で扱う。

## Debug Loop

- 原因が明らかで影響範囲が小さい trivial defect では、軽量 loop を使う。症状または code path を確認し、最小修正を行い、最も近い check を実行し、full hypothesis branching が不要だった理由を報告する。
- まず症状を再現または観察する。
- 失敗している command、route、input、state、expected/actual を切り分ける。
- static inspection だけで飛びつかず、可能な限り runnable reproduction を作る。
- subagents が使える場合は、異なる仮説や独立した証拠収集を並列 probe として任せる。
- 必要なら最小限の instrumentation を入れ、最後に削除する。
- root cause が見えたら `codex-implementation-loop` で patch する。
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

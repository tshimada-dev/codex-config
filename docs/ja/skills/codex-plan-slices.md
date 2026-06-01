---
source: skills/codex-plan-slices/SKILL.md
source_commit: dd1c94c
canonical: false
---

# codex-plan-slices 日本語参考訳

この文書は `skills/codex-plan-slices/SKILL.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

## 目的

広い engineering work を、安全な vertical slices、TODO、必要なら subagent assignments に分解する。

## Planning Loop

1. objective と done condition を明確にする。
2. work を小さな slices に分ける。
3. slice ごとに scope、dependencies、risk、verification を持たせる。
4. 並列化できるものと sequential なものを分ける。
5. parent-owned work を明確にする。integration、final verification、release judgment、user report は parent が持つ。

## Slice Design

良い slice は以下を満たす。

- 単独で理解できる。
- 変更ファイルの範囲が明確。
- acceptance criteria がある。
- focused verification がある。
- 他の slice への依存が見える。

## Subagent Use

subagents を使う場合:

- each worker に bounded task を渡す。
- worker には実装または調査だけを任せる。
- parent は objective、slice list、ownership map、dependency graph、final verification plan、unresolved risks を保持する。
- worker 結果を統合し、conflicts を解消し、final verification を実行する。

## Output

小さな edits や skill evaluation では、conversation 内の checklist で十分。広い work では、JSON など再利用しやすい structured plan を使う。

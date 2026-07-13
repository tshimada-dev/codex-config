---
source: skills/codex-plan-slices/SKILL.md
source_blob: 3de6f5e6baa6ce55a327b2c68adc2567117e37a1
canonical: false
---

# codex-plan-slices 日本語参考訳

この文書は `skills/codex-plan-slices/SKILL.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

## 目的

広い engineering work を、安全な vertical slices、TODO、必要なら subagent assignments に分解する。

## 共通開発契約

`rules/development-workflow.md` に従い、期待結果、non-goals、authority conflict、acceptance criteria と evidence を planning artifact に保持する。

## Planning Steps

1. objective と non-goals を明確にする。
2. user、repo、branch、tests、external systems から constraints を列挙する。
3. 候補 slices を作り、initial decomposition を確定する前に次の観点から疑う。
   - 個別の file や component の最適化が system-level outcome を損なっていないか確認する。
   - cross-cutting invariants、duplicated ownership、長期的な負債になる一時的解決を特定する。
   - immediate implementation cost と maintenance、extension、operational、migration costs を比較する。
   - task に見合う分析に留め、仮想的な将来ニーズのために speculative architecture を作らない。
4. acceptance criteria に安定した ID を付け、各 ID を named focused evidence に対応付ける。
5. slices を確定し、slice ごとに intent、write scope、dependencies、`acceptance_ids`、evidence、risk を持たせる。
6. slices を `serial`、`parallel-safe`、`human-decision` に分類する。重要な specification/test/current-behavior conflict は `human-decision` とする。
7. parent-owned work を明確にする。integration、final verification、release judgment、user report は parent が持つ。

## Slice Design

良い slice は以下を満たす。

- 単独で理解できる。
- 変更ファイルの範囲が明確。
- stable ID の acceptance criteria がある。
- acceptance criteria に対応する named evidence がある。
- 他の slice への依存が見える。

## Subagent Use

subagents が使える場合は、広い作業、複数ファイル、不慣れな repo、risk のある作業、並列化できる作業で優先して使う。小さな単一ファイル変更、一本道の緊急修正、tooling が使えない場合、user が使わないよう求めた場合は使わない。

- each worker に bounded task を渡す。
- worker には実装または調査だけを任せる。
- parent は objective、slice list、ownership map、dependency graph、final verification plan、unresolved risks を保持する。
- worker 結果を統合し、conflicts を解消し、final verification を実行する。
- 小さな作業や一本道の作業では、subagent が使える場合でも parent session で直接進める。

## Output

小さな edits や skill evaluation では、conversation 内の checklist で十分。広い work では、JSON など再利用しやすい structured plan を使う。

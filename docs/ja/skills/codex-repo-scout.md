---
source: skills/codex-repo-scout/SKILL.md
source_blob: 0758a51a246769b6bef9438a01a140279bcd34e0
canonical: false
---

# codex-repo-scout 日本語参考訳

この文書は `skills/codex-repo-scout/SKILL.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

## 目的

迷子にならない程度に、実装に必要な repository context を集める。

## 共通開発契約

`rules/development-workflow.md` に従い、scouting は制約、期待結果の候補、実際の verification command を発見するが、product behavior や repository trust を推測で確定しない。

## Subagent Scouting

subagents が使えて repo が大きい、または不慣れな場合は、context-heavy scouting を基本的に explorer subagents に任せる。

- explorer ごとに subsystem、feature path、question を1つ割り当てる。
- pasted file contents ではなく、file paths、symbols、commands、confidence 付きの evidence を求める。
- parent は likely files、existing patterns、commands、risks の map に集中する。
- 結果が矛盾または実装を妨げる場合以外は explorer result を信頼する。critical path だけ local で確認する。
- summary を得たら explorer agents を閉じる。

## Scout Pass

1. location と git state を確認する。
   - `Get-Location`
   - `git status --short --branch`
   - disposable rehearsal repo では、後の diff を implementation work と見なす前に clean baseline を作るか確認する。
   - repository trust を `trusted`、`untrusted`、`unknown` のどれかで記録する。runtime/profile の明示または user の確認なしに trust を昇格させず、untrusted/unknown repo の build/test/package command は任意コード実行として扱う。
2. `rg --files` や directory listing で top-level shape を見る。大きい repo では全出力を貼らず sample/filter する。
3. build/test entry points を特定する。
   - package manifests
   - project files
   - CI config
   - test directories
   - scripts
4. user-facing terms を `rg` で検索する。
5. critical path の files だけを先に読む。
6. evidence を記録する。
   - file path
   - symbol or behavior
   - why it matters

## Search Rules

- `rg` と `rg --files` を優先する。
- symbol/file が対象なら content より名前を先に探す。
- structured formats には可能なら structured tools を使う。
- 大きな generated files は、それ自体が artifact under test でない限り読まない。
- dirty worktree の変更は、自分がこの turn で作ったもの以外は user-owned と扱う。
- dirty target file を編集する前に diff を読み、user-owned hunks を把握する。
- unknown user edits と衝突する場合は、進める前に簡潔に1つ質問する。

## Stop Conditions

以下に答えられるようになったら scouting を止める。

- どの files が変わりそうか。
- どの existing pattern に従うべきか。
- どの tests/checks が変更を証明するか。
- どの runtime、package manager、test command、dev server command が使えるか。
- runtime/profile または user が build/test/package command を実行できる trust を明示したか、それともまだ approval が必要か。
- dependencies は入っているか、明確に不足しているか。
- どの local changes を保持する必要があるか。

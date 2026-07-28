---
source: skills/codex-implementation/SKILL.md
source_blob: 30aac9cf083956cd4bcfd6bb1e36c19d06411414
canonical: false
---

# codex-implementation 日本語参考訳

この文書は `skills/codex-implementation/SKILL.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

## 目的

ユーザー作業を保護しながら、信頼できる evidence とともに要求された repository behavior を提供する。

## 共通開発契約

`rules/development-workflow.md` に従い、編集前に期待結果、non-goals/constraints、acceptance criteria、evidence、未解決の authority conflict を確認する。

## Composition

- 不慣れな code では `codex-repo-scout` の後に使う。
- bug では `codex-debug-discipline` が reproduction または code-path finding を出した後に使う。
- UI changes では final delivery 前に `codex-ui-quality-gate` を実行する。

## Implementation Contract

- behavior を変更する前に、expected outcome、constraints、適用する acceptance criteria、named evidence を確認する。
- repository の relevant checks を発見する。stable、deterministic、low-cost な seam がある場合は focused fail-first check を優先し、ない場合は理由と最小の信頼できる代替手段を編集前に記録する。
- repository conventions に従い、既存の user work を保護しながら、scope 内で architecture 上一貫した最小の変更を行う。
- focused evidence を先に実行し、影響を受ける contract に応じて verification を広げる。local substitute と CI-equivalent evidence を区別する。
- material deviations、未解決の競合、実行できない checks、変更が原因ではない failures を記録し、暗黙に成功として扱わない。
- changed files、acceptance criteria と evidence の対応、実行した checks、residual risk を報告する。

## Safety Boundaries

- 共通契約の authority、repository trust、worktree preservation、cross-shell safety の規則に従う。
- 無関係な user changes を overwrite または package せず、無関係な refactor に拡大せず、generated/debug churn を diff に残さない。
- disposable reproduction または rehearsal files は、合意した temporary/project directory 内に置く。

## Subagent Implementation

各 bounded worker assignment には、exact write scope、完了済み dependencies、acceptance criteria、tests/checks を渡す。worker に他者の編集を revert/overwrite しないよう伝える。worker は changed files、tests run、assumptions、unresolved issues を報告する。parent は integration、conflict resolution、final verification、release reporting を保持する。

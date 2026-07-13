---
source: skills/codex-implementation-loop/SKILL.md
source_commit: 9cac093822dba4974f2cce50dd91c4e70b49a05e
canonical: false
---

# codex-implementation-loop 日本語参考訳

この文書は `skills/codex-implementation-loop/SKILL.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

## 目的

文脈を失わず、ユーザー作業を壊さずに code/file changes を行う。

## Composition

- 不慣れな code では `codex-repo-scout` の後に使う。
- bug では `codex-debug-discipline` が reproduction または code-path finding を出した後に使う。
- UI changes では final delivery 前に `codex-ui-quality-gate` を実行する。

## Subagent Implementation

subagents が使える場合は、parent の次 step を妨げない bounded slices に worker agents を優先して使う。

- exact write scope、dependencies、acceptance criteria、tests/checks を渡す。
- worker に、他の編集があること、revert/overwrite してはいけないことを伝える。
- parent は integration、conflict resolution、final verification、user reporting を担当する。
- worker には changed files、tests run、unresolved issues、neighboring code への assumptions を報告させる。
- release decisions、broad refactors、final PR packaging は worker に任せない。

## Loop

1. target behavior と files を再確認する。
2. 編集前に current file を読む。
3. 最初に思いついたもっともらしい解決策を採用または実装する前に立ち止まり、次の観点からその案を疑う。
   - どのような前提に依存しているかを特定する。
   - 影響を受ける callers、shared contracts、neighboring abstractions を確認する。
   - architecture に影響する選択では、少なくとも1つの合理的な代替案と比較する。
4. 単に local diff が最小の変更ではなく、合意した scope と constraints の中で system-level outcome を改善する最小の一貫した変更を選ぶ。目先の症状だけを解決する patch より、repository の architecture との整合性を優先する。
5. maintenance、想定される extension、migration cost、operational burden、technical debt という適切な時間軸を考慮する。task に見合う範囲に留め、仮想的な将来ニーズを speculative abstractions や無関係な refactor の理由にしない。
6. manual changes は `apply_patch` で編集する。
7. behavior change や nontrivial risk がある場合は tests を追加または更新する。behavior change では、実務上可能なら implementation 前に focused test を書くことを優先する。
8. 最小の意味ある check から実行する。CI command と異なる、または local substitute にすぎない場合は、CI と同等として扱わず、その差分を記録する。
9. shared contracts、state、CLI behavior、UI flows、public APIs に触れたら broader checks を実行する。
10. changed files、checks、residual risk をまとめる。

## Loopback Conditions

以下の場合は、前の step に戻る。

- 新しい情報で target behavior が変わった場合: step 1 に戻り、target behavior と files を再確認する。
- file が変わった、または関連箇所が dirty になった場合: step 2 に戻り、編集前に current file を読む。
- diff が requested scope を超えて大きくなった場合: step 4 に戻り、最小の一貫した変更を選び直す。
- 自分の変更が原因で check が失敗した場合: 原因を修正し、step 8 に戻って最小の意味ある check を実行する。
- broader check で shared-contract issue が見つかった場合: expected behavior が変わったかどうかに応じて、step 1 または step 4 に戻る。

## Change Discipline

- 「最小変更」は編集行数が最少という意味ではなく、architecture 上一貫した最小の変更として扱う。shared invariant を守る、duplicated logic を防ぐ、または短命な technical debt を意図的に作らずに済む場合は、少し広い変更を正当化できる。
- user changes を保持する。
- dirty target file を編集する前に diff を確認し、user-owned hunks を把握する。
- unknown user edits と衝突する場合は、進める前に簡潔に1つ質問する。
- disposable repro/rehearsal projects では agreed temp/project directory 内だけを編集する。
- instruction/skill file への recommendation 依頼では、直接編集を求められていない限り patch を提示するだけにする。
- 無関係な refactor はしない。
- 既存 helper、types、patterns、naming、test style を優先する。
- structured data には可能なら structured parsers を使う。
- comments は将来の理解に本当に役立つ場合だけ残す。
- 必要でない generated/mechanical churn は diff に入れない。

## Test Heuristics

以下では tests を追加する。

- behavior changed
- bug fixed
- public contract changed
- regress しやすい area
- user が confidence を求めた

trivial、non-behavioral、usable test surface がない場合のみ skip し、final report で伝える。

## Failure Handling

check が失敗したら:

1. failure を読む。
2. 自分の変更、既存環境、無関係な dirty work のどれが原因か判断する。
3. 自分が原因の failure だけ直す。
4. relevant check を再実行する。
5. 無関係な failure は evidence とともに報告する。

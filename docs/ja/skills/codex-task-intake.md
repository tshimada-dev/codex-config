---
source: skills/codex-task-intake/SKILL.md
source_commit: 48eb930dceb63657f8f66ca4238e48954f48ef80
canonical: false
---

# codex-task-intake 日本語参考訳

この文書は `skills/codex-task-intake/SKILL.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

## 目的

曖昧な依頼を、最小限の質問で実行可能な進め方に変える。

## Intake Loop

1. ゴールを一文で言い直す。
2. 依頼を分類する。
   - `answer`: 説明や調査のみ。
   - `inspect`: 変更前に local/remote context を読む。
   - `edit`: 限定された code/file change を行う。
   - `workflow`: 大きめの multi-step task を計画または調整する。
   - `automation`: recurring/delayed task を作る。
3. 主な risk を特定する。data loss、wrong repo、wrong branch、external side effects、privacy、cost、time、visual quality など。
4. 進めるか、まず調査するか、質問するかを決める。
5. 間違った前提が高くつく場合だけ、簡潔な質問を最大1つする。それ以外は保守的に仮定して進める。

## 判断ルール

- implementation 依頼で scope が local に発見できる場合は、調査して進める。
- planning 依頼では、planning artifact が成果物でない限り project files を編集しない。
- current facts、prices、laws、schedules、third-party docs、remote state を含む場合は、適切な source で確認する。
- `automation` では automation workflow を使い、不足している schedule、timezone、target action、notification details だけ質問する。
- subagents が有効な作業では、task が小さい場合や user が使わないよう求めた場合を除き、planning/delegation skill に渡す。
- debugging が主なら `codex-debug-discipline` に渡す。
- broad engineering work は `codex-plan-slices` に渡す。
- disposable/simulated/rehearsal repo では workspace boundary を先に確定し、範囲外編集を out of scope とする。

## Composition

- 不慣れな repo: 編集前に `codex-repo-scout`
- 広い作業: `codex-repo-scout` から `codex-plan-slices`
- bug reports: reproduction と root cause は `codex-debug-discipline`
- code changes: patch と checks は `codex-implementation-loop`
- UI changes: 実装後に `codex-ui-quality-gate`
- review packaging: verification 後に `codex-pr-readiness`
- long/interrupted work: `codex-context-handoff`

## Output Shape

小さな task では visible plan なしに進める。

広い task では、Goal、Mode、Assumption、Next step を短く出す。Intake は作業本体ではなく入口である。

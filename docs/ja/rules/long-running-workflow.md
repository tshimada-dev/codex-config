---
source: rules/long-running-workflow.md
source_blob: badae203f32a17dd45be13f54ab54e05aa732268
canonical: false
---

# Long-Running Workflow 日本語参考訳

この文書は `rules/long-running-workflow.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

30分以上かかりそうな作業、複数 repo や複数サブシステムをまたぐ作業、CI failure の修正、中断や再開が必要になりそうな作業で使う。

## 原則

- 期待結果、証拠、phase ownership、final readiness、repository trust は `$HOME\.codex\rules\development-workflow.md` に従う。
- ゴール、現在の状態、次の手順、検証状況を書き残す。
- 調査、実装、検証の責任と記録を分ける。この分離は、実装中の focused red/green feedback を禁止するものではない。
- subagents が使える場合は、context-heavy research、広い planning、独立した implementation slice、review、verification で優先して使う。
- 親セッションは意思決定、統合、conflict resolution、最終検証、user report に集中させる。
- 小さく review しやすい変更と、リポジトリローカルの慣習を優先する。
- ユーザーの変更を保持する。明示依頼なしに uncommitted work を破棄しない。
- 破壊的なローカル操作、リモート変更、公開、デプロイ、本番データ変更、migration、secret への接触は、事前に確認する。

## Run Note

- 長時間タスクごとに active run note は1つだけ使う。
- リポジトリに run note の慣習がある場合はそれを優先する。ない場合は `$HOME\.codex\runs\<repo-name>\` に作る。
- 新しい run note はローカル時刻と短い lowercase slug を使い、`YYYYMMDD-HHMM-<short-task>.md` という名前にする。例: `20260601-1430-fix-ci-login.md`。
- `$HOME\.codex\templates\agent-run.md` を初期構造としてコピーする。
- phase boundary、前提や scope の変更、意味のある実装 slice の後、検証 command の後、pause 前、handoff 前に note を更新する。
- 記録は短く、意思決定中心にする。大きな log や diff は貼らず、file や command をリンクまたは名前で示す。
- 作業に実質的な影響を与えた各 Skill を `## Skills Used` に記録し、purpose、observable effect、evidence を対応付ける。確認しただけの Skill は記録しない。再利用可能な Skill を使っていない場合は `None` row を明記する。
- 安全な再開に必要な運用識別子だけを残す。IP、instance identifier、public key、credential、raw configuration のコピーより、stable alias や安全な system of record への参照を優先する。

## Run note の整合性

readiness 判定、pause、handoff の前に次を確認する。

- Phase の選択肢一覧を、`development-workflow.md` にある現在の phase 1つへ置き換える。
- 未解決 placeholder と、`\n\n` のような literal escaped paragraph break を除去する。
- acceptance criterion の status と verification field を readiness に整合させる。`ready` では、必須証拠に `pending`、`partial`、`blocked`、failure を残さない。
- `conditionally-ready` では、具体的な residual risk または skip した optional evidence と、それを解消できる action/owner を記録する。
- `Current State`、`Handoff`、`Next Step` を更新し、完了済み作業を指す古い手順を削除する。
- current repository が run-note validator を提供する場合は active note に実行し、結果を記録する。

## Handoff と再開 context

- user が durable context を求めた場合、または repository に慣習がある場合を除き、独立した handoff file は作らない。
- active run note がある場合は、別の source of truth を作らず、簡潔な `## Handoff` section を更新する。
- goal、current status、important decisions、changed files、verification outcomes、blockers、next concrete step、verification に影響する tool gap だけを残す。
- transcript、duplicate specification、artifact ではない raw log、secret、不要な operational identifier、next action のない speculation は除外する。
- 完了した temporary simulation は、artifact 保持を user が求めない限り final response で十分とする。

## 調査

- 依頼を一文で言い直す。
- 対象リポジトリ、現在ディレクトリ、関連 docs、source/test の候補を確認する。
- 編集前に repository instructions を読む。
- `rg` や `rg --files` など高速な検索で関連ファイルを探す。
- 発見事項と未解決の前提を active run note に記録する。
- active run note がまだない場合は、コード変更前に作る。

## 実装

- 調査メモに基づいて変更する。
- 期待結果、acceptance evidence、適用した focused feedback または記録済みの代替証拠に基づいて変更する。
- 変更範囲は狭く保ち、既存 style に合わせる。
- 新しい発見で計画が変わった場合は run note を更新する。
- 必要でない限り broad refactor は避ける。

## 検証

- 統合結果を期待結果と acceptance evidence に対して独立に検証し、readiness を判定する。
- 実行前に、リポジトリの実際の check command を確認する。
- まず最小限の有用な check を実行し、共有挙動に触れた場合は広げる。
- command、結果、skip した check を active run note に記録する。
- 無関係に見える failure は隠さず、証拠を残して報告する。

## 再開チェックリスト

- active run note を読む。
- 現在の git status と最近の変更を確認する。
- note に書かれたファイルを、編集前に再度開く。
- 記録された次の手順から続ける。repo 状態が変わっている場合のみ調整する。

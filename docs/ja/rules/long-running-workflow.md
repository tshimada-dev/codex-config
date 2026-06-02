---
source: rules/long-running-workflow.md
source_commit: 747e954d067ae3c02d63e4b611dcce9da8ed39c8
canonical: false
---

# Long-Running Workflow 日本語参考訳

この文書は `rules/long-running-workflow.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

30分以上かかりそうな作業、複数 repo や複数サブシステムをまたぐ作業、CI failure の修正、中断や再開が必要になりそうな作業で使う。

## 原則

- ゴール、現在の状態、次の手順、検証状況を書き残す。
- 調査、実装、検証を分ける。同じ Codex セッションで行う場合でも分離して扱う。
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

## 調査

- 依頼を一文で言い直す。
- 対象リポジトリ、現在ディレクトリ、関連 docs、source/test の候補を確認する。
- 編集前に repository instructions を読む。
- `rg` や `rg --files` など高速な検索で関連ファイルを探す。
- 発見事項と未解決の前提を active run note に記録する。
- active run note がまだない場合は、コード変更前に作る。

## 実装

- 調査メモに基づいて変更する。
- 変更範囲は狭く保ち、既存 style に合わせる。
- 新しい発見で計画が変わった場合は run note を更新する。
- 必要でない限り broad refactor は避ける。

## 検証

- 実行前に、リポジトリの実際の check command を確認する。
- まず最小限の有用な check を実行し、共有挙動に触れた場合は広げる。
- command、結果、skip した check を active run note に記録する。
- 無関係に見える failure は隠さず、証拠を残して報告する。

## 再開チェックリスト

- active run note を読む。
- 現在の git status と最近の変更を確認する。
- note に書かれたファイルを、編集前に再度開く。
- 記録された次の手順から続ける。repo 状態が変わっている場合のみ調整する。

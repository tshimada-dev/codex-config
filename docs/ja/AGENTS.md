---
source: AGENTS.md
source_commit: f8d0d23ee012b798f90bd35eb0456e14cd45f616
canonical: false
---

# Global Codex Working Rules 日本語参考訳

この文書は `AGENTS.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

## 長時間作業

- 30分以上かかりそうな作業、複数サブシステムにまたがる作業、CI 修正、中断される可能性がある作業では、変更前に `$HOME\.codex\rules\long-running-workflow.md` を読む。
- 調査、実装、検証は別フェーズとして扱う。前提が変わった場合は記録せずに探索メモとコード変更を混ぜない。
- subagents が使える場合は、context-heavy research、広い planning、独立した implementation slice、review、verification に優先して使い、parent session は意思決定、統合、最終検証に集中させる。
- 長時間作業では、`$HOME\.codex\templates\agent-run.md` を使って active run note を1つ維持する。保存先はリポジトリで定められた場所を使い、慣習がない場合は `docs/codex/runs/YYYYMMDD-HHMM-<short-task>.md` に置く。
- 実装作業を終える前に、リポジトリの実際の検証コマンドを `AGENTS.md`、README、Makefile、package files、pyproject、scripts などから確認する。
- 破壊的なローカルコマンド、リモート変更、公開、デプロイ、本番 migration、secret の取り扱いは、明示的なユーザー承認なしに実行しない。

## 個人用リファレンス

- 長時間作業: `$HOME\.codex\rules\long-running-workflow.md`
- 調査チェックリスト: `$HOME\.codex\rules\checklists\research.md`
- 実装チェックリスト: `$HOME\.codex\rules\checklists\implementation.md`
- CI 修正チェックリスト: `$HOME\.codex\rules\checklists\ci-fix.md`
- active run note テンプレート: `$HOME\.codex\templates\agent-run.md`
- repository AGENTS テンプレート: `$HOME\.codex\templates\repo-agents.md`

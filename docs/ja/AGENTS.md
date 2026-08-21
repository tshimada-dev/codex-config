---
source: AGENTS.md
source_blob: d76a04dc5b77034e5867b81e8ceb32138bb0d4ac
canonical: false
---

# Global Codex Working Rules 日本語参考訳

この文書は `AGENTS.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

## ワークフロー対応表

- 実装、debug、CI fix、verification、PR readiness では `$HOME\.codex\rules\development-workflow.md` に従う。
- 30分以上、複数サブシステム、CI fix、中断可能性がある作業では、さらに `$HOME\.codex\rules\long-running-workflow.md` に従い active run note を1つ維持する。
- checklist は phase 固有の補助であり、期待結果、証拠、ownership、readiness、repository trust は development workflow contract を正とする。

## サブエージェントへの委譲

- サブエージェントへの委譲が別途許可されている場合でも、タスク難易度に応じたモデルの自動ルーティングが行われるとは想定しない。
- 直近の会話コンテキストが不可欠でない bounded worker には `fork_turns="none"` を使う。
- read-only の探索、抽出、機械的チェックでは、`model="gpt-5.6-luna"` と `reasoning_effort="low"` を優先する。
- 分析、レビュー、見積もり、bounded implementation では、`model="gpt-5.6-terra"` と `reasoning_effort="medium"` を優先する。
- 高リスク、曖昧性が高い、adversarial、または最終統合作業では親モデルを継承する。
- コンテキストが必要な場合は、必要最小限の正の `fork_turns` を渡し、必要な場合を除いて全履歴のforkを避ける。
- 小さな一本道の作業は委譲しない。返却する証拠は簡潔にし、最終統合は親エージェントが担当する。
- モデルまたはreasoningのoverrideが利用できない場合は、指定を省略して続行する。

## 安全境界

- repository trust と repository-controlled command の実行可否は `$HOME\.codex\rules\development-workflow.md` を正とする。
- cloud、infrastructure、database、deployment、migration command の前に `codex-cloud-ops-intake` で exact target と approval boundary を確立する。
- 破壊的なローカルコマンド、リモート変更、公開、デプロイ、本番 migration、secret の取り扱いは、明示的なユーザー承認なしに実行しない。
- secret、token、private key、cookie、`.env` の内容は、ユーザーが明示的に依頼し、かつ task に必要な場合を除き、inspect、print、copy、upload、summary しない。

## 個人用リファレンス

- 開発ワークフロー契約: `$HOME\.codex\rules\development-workflow.md`
- 長時間作業: `$HOME\.codex\rules\long-running-workflow.md`
- 調査チェックリスト: `$HOME\.codex\rules\checklists\research.md`
- 実装チェックリスト: `$HOME\.codex\rules\checklists\implementation.md`
- CI 修正チェックリスト: `$HOME\.codex\rules\checklists\ci-fix.md`
- active run note テンプレート: `$HOME\.codex\templates\agent-run.md`
- repository AGENTS テンプレート: `$HOME\.codex\templates\repo-agents.md`

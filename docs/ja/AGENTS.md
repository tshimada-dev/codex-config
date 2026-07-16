---
source: AGENTS.md
source_blob: 94140f6f0f8c98a5837cba16ad6d804c76a94e83
canonical: false
---

# Global Codex Working Rules 日本語参考訳

この文書は `AGENTS.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

## ワークフロー対応表

- 実装、debug、CI fix、verification、PR readiness では `$HOME\.codex\rules\development-workflow.md` に従う。
- 30分以上、複数サブシステム、CI fix、中断可能性がある作業では、さらに `$HOME\.codex\rules\long-running-workflow.md` に従い active run note を1つ維持する。
- checklist は phase 固有の補助であり、期待結果、証拠、ownership、readiness、repository trust は development workflow contract を正とする。

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

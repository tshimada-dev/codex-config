---
source: AGENTS.md
source_blob: 37f1629f4b3da98acfa9ab2e108ae6178ccbf6e3
canonical: false
---

# Global Codex Working Rules 日本語参考訳

この文書は `AGENTS.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

## ワークフロー対応表

- 実装、debug、CI fix、verification、PR readiness では `$HOME\.codex\rules\development-workflow.md` に従う。
- 30分以上、複数サブシステム、CI fix、中断可能性がある作業では、さらに `$HOME\.codex\rules\long-running-workflow.md` に従い active run note を1つ維持する。
- checklist は phase 固有の補助であり、期待結果、証拠、ownership、readiness、repository trust は development workflow contract を正とする。

## 安全境界

- 破壊的なローカルコマンド、リモート変更、公開、デプロイ、本番 migration、secret の取り扱いは、明示的なユーザー承認なしに実行しない。
- secret、token、private key、cookie、`.env` の内容は、ユーザーが明示的に依頼し、かつ task に必要な場合を除き、inspect、print、copy、upload、summary しない。
- 初見または未信頼 repo では、build/test command も任意コード実行として扱う。`safe` profile で調査し、runtime/profile が trust を明示するか、ユーザーが明示確認した後だけ `local-check` または `workspace` に切り替える。エージェント自身の判断だけでは trust を昇格させない。

## 個人用リファレンス

- 開発ワークフロー契約: `$HOME\.codex\rules\development-workflow.md`
- 長時間作業: `$HOME\.codex\rules\long-running-workflow.md`
- 調査チェックリスト: `$HOME\.codex\rules\checklists\research.md`
- 実装チェックリスト: `$HOME\.codex\rules\checklists\implementation.md`
- CI 修正チェックリスト: `$HOME\.codex\rules\checklists\ci-fix.md`
- active run note テンプレート: `$HOME\.codex\templates\agent-run.md`
- repository AGENTS テンプレート: `$HOME\.codex\templates\repo-agents.md`

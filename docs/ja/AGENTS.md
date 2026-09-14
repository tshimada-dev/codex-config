---
source: AGENTS.md
source_blob: 26968e0dd16e585dc38588c3a7938ce3fd36547b
canonical: false
---

# Global Codex Working Rules 日本語参考訳

この文書は `AGENTS.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

## 目的に照らした判断と意向の尊重

- 指定された手段を、明示された目的と確認済みの意向に照らして検討する。ただし、Codexの理解も不完全であり、手段自体が学習・検証などの目的を持つ場合があることを踏まえる。
- 効果・費用・安全性・実行可能性に重要な改善が見込める場合は、実行前に代替案・根拠・トレードオフを簡潔に提示する。些細な改善について、提案や確認を繰り返さない。
- 推測した「真の要望」を理由に、明示された制約や権限を変更しない。目的・範囲・重要な制約の変更や追加の権限が必要な場合は確認を得る。依頼範囲内の軽微で可逆的な改善は、自律的に進める。

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
- 実環境の cloud/infrastructure、live database の操作、deployment/migration 実行の前に `codex-cloud-ops-intake` で target identity と approval scope を確立する。ローカル file 編集、使い捨て fixture test、通常の Git/PR 操作だけでは発火しない。
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

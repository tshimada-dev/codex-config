# 日本語参考訳

このディレクトリには、Codex 設定ファイルの日本語参考訳を置いています。

Codex が実行時に読む canonical な定義は、リポジトリ直下の英語版です。
日本語版は人間が内容を把握しやすくするための補助文書です。

内容が食い違う場合は、英語版を優先します。

## 対応表

- [AGENTS.md](AGENTS.md): グローバル Codex 作業ルール
- [rules/command-policy.md](rules/command-policy.md): コマンド許可ポリシー
- [rules/default.md](rules/default.md): 最小のデフォルト許可ルール
- [rules/long-running-workflow.md](rules/long-running-workflow.md): 長時間作業の進め方
- [rules/checklists/research.md](rules/checklists/research.md): 調査チェックリスト
- [rules/checklists/implementation.md](rules/checklists/implementation.md): 実装チェックリスト
- [rules/checklists/ci-fix.md](rules/checklists/ci-fix.md): CI 修正チェックリスト
- [templates/agent-run.md](templates/agent-run.md): run note テンプレート
- [templates/repo-agents.md](templates/repo-agents.md): repository AGENTS テンプレート
- [config/config.base.toml](../../config/config.base.toml): 共有可能な config baseline
- [config/profiles/local-check.config.toml](../../config/profiles/local-check.config.toml): local-check profile
- [config/profiles/safe.config.toml](../../config/profiles/safe.config.toml): safe profile
- [config/profiles/workspace.config.toml](../../config/profiles/workspace.config.toml): workspace profile
- [config/README.md](../../config/README.md): config baseline の管理範囲
- [skills/codex-task-intake.md](skills/codex-task-intake.md): タスク受け入れ
- [skills/codex-repo-scout.md](skills/codex-repo-scout.md): リポジトリ調査
- [skills/codex-implementation-loop.md](skills/codex-implementation-loop.md): 実装ループ
- [skills/codex-debug-discipline.md](skills/codex-debug-discipline.md): デバッグ規律
- [skills/codex-plan-slices.md](skills/codex-plan-slices.md): 作業分割
- [skills/codex-ui-quality-gate.md](skills/codex-ui-quality-gate.md): UI 品質確認
- [skills/codex-pr-readiness.md](skills/codex-pr-readiness.md): PR 準備
- [skills/codex-context-handoff.md](skills/codex-context-handoff.md): 引き継ぎ文脈
- [skills/codex-claude-code-reviewer.md](skills/codex-claude-code-reviewer.md): Claude Code による外部レビュー

## 更新ルール

- 英語版を変更したら、対応する日本語参考訳も更新する。
- 日本語版には実行上の新ルールを追加しない。
- 実行時に Codex に効かせたい変更は、必ず英語版の canonical ファイルに入れる。
- live `config.toml` は丸ごと同期せず、共有可能な baseline だけを明示 merge する。
- 通常開発は生産性のため network access を許可し、初見・未信頼 repo では `safe` profile を使う。
- 初期調査後にローカル検証だけ行いたい場合は、workspace-write だが network access を閉じる `local-check` profile を使う。
- 各ファイル冒頭の `source` と `source_commit` を確認し、どの英語版に対応する訳か分かるようにする。
- `source_commit` の確認と更新には `scripts/check-ja-source-commits.ps1` を使う。
- `-Update` は、訳文ファイルに未コミットの本文変更がある場合だけ `source_commit` を更新する。
- 訳文の変更が不要だと確認済みの場合だけ、`-Update -AllowMetadataOnlyUpdate` で metadata だけを同期する。

```powershell
.\scripts\check-ja-source-commits.ps1
.\scripts\check-ja-source-commits.ps1 -Update
.\scripts\check-ja-source-commits.ps1 -Update -AllowMetadataOnlyUpdate
```

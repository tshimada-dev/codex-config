# 日本語参考訳

このディレクトリには、Codex 設定ファイルの日本語参考訳を置いています。

Codex が実行時に読む canonical な定義は、リポジトリ直下の英語版です。
日本語版は人間が内容を把握しやすくするための補助文書です。

内容が食い違う場合は、英語版を優先します。

## 対応表

- [AGENTS.md](AGENTS.md): グローバル Codex 作業ルール
- [rules/command-policy.md](rules/command-policy.md): コマンド許可ポリシー
- [rules/default.md](rules/default.md): 最小のデフォルト許可ルール
- [rules/development-workflow.md](rules/development-workflow.md): 開発ワークフロー共通契約
- [rules/long-running-workflow.md](rules/long-running-workflow.md): 長時間作業の進め方
- [rules/checklists/research.md](rules/checklists/research.md): 調査チェックリスト
- [rules/checklists/implementation.md](rules/checklists/implementation.md): 実装チェックリスト
- [rules/checklists/ci-fix.md](rules/checklists/ci-fix.md): CI 修正チェックリスト
- [templates/agent-run.md](templates/agent-run.md): run note テンプレート
- [templates/repo-agents.md](templates/repo-agents.md): repository AGENTS テンプレート
- [config/config.base.toml](../../config/config.base.toml): 共有可能な config baseline
- [config/profiles/local-check.config.toml](../../config/profiles/local-check.config.toml): ローカル検証用 profile
- [config/profiles/safe.config.toml](../../config/profiles/safe.config.toml): 安全確認用 profile
- [config/profiles/workspace.config.toml](../../config/profiles/workspace.config.toml): 通常開発用 profile
- [config/README.md](../../config/README.md): config baseline の管理範囲
- [skills/codex-task-intake.md](skills/codex-task-intake.md): タスク受け入れ
- [skills/codex-repo-scout.md](skills/codex-repo-scout.md): リポジトリ調査
- [skills/codex-secure-ssh-doas-ops.md](skills/codex-secure-ssh-doas-ops.md): 安全な SSH・doas 運用
- [skills/codex-implementation.md](skills/codex-implementation.md): 実装
- [skills/codex-debug-discipline.md](skills/codex-debug-discipline.md): デバッグ規律
- [skills/codex-plan-slices.md](skills/codex-plan-slices.md): 作業分割
- [skills/codex-ui-quality-gate.md](skills/codex-ui-quality-gate.md): UI 品質確認
- [skills/codex-pr-readiness.md](skills/codex-pr-readiness.md): PR 準備
- [skills/codex-claude-code-reviewer.md](skills/codex-claude-code-reviewer.md): Claude Code による外部レビュー
- [skills/codex-clean-local-state.md](skills/codex-clean-local-state.md): Codex local state の安全な整理
- [skills/codex-autonomous-debate.md](skills/codex-autonomous-debate.md): 実在する主要陣営による自律討論
- [skills/codex-promote-local-skill.md](skills/codex-promote-local-skill.md): local Skill の管理価値評価と安全な repository 昇格
- [skills/codex-field-investigation-loop.md](skills/codex-field-investigation-loop.md): 現地障害調査ループ
- [skills/codex-effort-estimator.md](skills/codex-effort-estimator.md): 工数見積もり統括
- [skills/codex-field-investigation-loop/references/hypothesis-loop.md](skills/codex-field-investigation-loop/references/hypothesis-loop.md): 現地障害調査の仮説ループ
- [skills/codex-field-investigation-loop/references/investigation-state.md](skills/codex-field-investigation-loop/references/investigation-state.md): 現地障害調査状態バンドル
- [skills/codex-effort-estimator/references/README.md](skills/codex-effort-estimator/references/README.md): 工数見積もり reference 日本語参考訳一覧

## 更新ルール

- 英語版を変更したら、対応する日本語参考訳も更新する。
- 日本語版には実行上の新ルールを追加しない。
- 実行時に Codex に効かせたい変更は、必ず英語版の canonical ファイルに入れる。
- live `config.toml` は丸ごと同期せず、共有可能な baseline だけを明示 merge する。
- 通常開発は生産性のため network access を許可し、初見・未信頼 repo では `safe` profile を使う。
- 初期調査後にローカル検証だけ行いたい場合は、workspace-write だが network access を閉じる `local-check` profile を使う。
- 各ファイル冒頭の `source` と source revision metadata を確認し、どの英語版に対応する訳か分かるようにする。既存の確定版を指す場合は `source_commit`、source と訳文を同一コミットで変更または追加する場合は `source_blob` を使う。
- source revision metadata の確認と更新には `scripts/check-ja-source-commits.ps1` を使う。
- `-Update` は、訳文ファイルに未コミットの本文変更がある場合だけ `source_commit` または `source_blob` を更新する。
- 訳文の変更が不要だと確認済みの場合だけ、`-Update -AllowMetadataOnlyUpdate` で metadata だけを同期する。

```powershell
.\scripts\check-ja-source-commits.ps1
.\scripts\check-ja-source-commits.ps1 -Update
.\scripts\check-ja-source-commits.ps1 -Update -AllowMetadataOnlyUpdate
```

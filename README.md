# Codex Config

[English overview](README.en.md)

## 3分で見る価値

このリポジトリは、OpenAI Codex を継続的な開発パートナーとして使うための個人設定集から
始まったものです。現在はそれに加えて、**AI コーディングエージェントに任せる範囲、
安全境界、検証、引き継ぎをどう設計するか**を示すワークフロー設計サンプルとしても
整備しています。

- [`skills/codex-*`](skills/): 調査、計画、実装、デバッグ、レビュー準備、UI 検証を分離したマルチエージェント向け Skill 群。
- [`skills/codex-effort-estimator`](skills/codex-effort-estimator/): 見積もりにおける独立観測、バイアス制御、AI 補正、監査可能な workbook 出力を扱う代表的な実証対象。
- [`scripts/install.ps1`](scripts/install.ps1): tracked file だけを `$HOME/.codex` に反映し、manifest と prune で安全に同期する PowerShell 7 ベースの配布ツール。
- [`rules/`](rules/) と [`templates/`](templates/): 長時間作業、CI 差分、意思決定記録、危険コマンド境界を Codex が再利用できる形に落とし込んだ運用設計。
- [`scripts/install-copilot-skills.ps1`](scripts/install-copilot-skills.ps1): Codex 用 Skill を GitHub Copilot Agent Skills として試すためのアダプター実験。

主対象は Codex で、GitHub Copilot 向けスクリプトは設計の一部を移植する派生実験です。
権限境界の設計（`safe` / `local-check` / `workspace` profile の使い分け）は後述します。

これは社内標準や公式ルールではなく、個人の作業環境と設計判断を再現するための
リポジトリです。AI 活用状況を説明する際の実例として参照することはありますが、
そのまま導入するための汎用テンプレートではありません。

## 管理するもの

このリポジトリでは、再利用しやすい Codex の作業ルール、テンプレート、汎用的な
`codex-*` スキル、共有可能な config baseline だけを管理します。

- `AGENTS.md`: グローバルな Codex 作業ルール
- `rules/`: 共通のコマンドポリシーと長時間作業用の手順
- `templates/`: run note や repository instruction のテンプレート
- `skills/codex-*`: 汎用的な Codex ワークフロースキル
- `config/`: 共有可能な `config.toml` baseline と profile files
- `scripts/install.ps1`: 管理対象ファイルを `$HOME\.codex` にコピーする導入スクリプト
- `scripts/install-copilot-skills.ps1`: `skills/codex-*` を `copilot-*` 名に変換して GitHub Copilot Agent Skills として導入する実験用スクリプト
- `scripts/check-ja-source-commits.ps1`: 日本語参考訳の `source_commit` 検査スクリプト
- `docs/ja/`: 人間が読むための日本語参考訳

管理しないもの:

- シークレット、トークン、`.env`
- プラグインキャッシュ、automation の状態、実行ログ
- 端末固有のローカルファイル
- live `config.toml` 全体

## インストール

前提: PowerShell 7+ (`pwsh`) と Git が利用できる環境で、git clone した作業ツリーから実行します。
Windows では `.\scripts\install.ps1`、macOS/Linux では `pwsh ./scripts/install.ps1` で実行できます。

デフォルトでは `$env:CODEX_HOME` を優先し、未設定の場合は `$HOME/.codex` に
インストールします。インストール先に同名ファイルがあり、内容が異なる場合は
上書きせずに停止します。既存ファイルと同じ内容の場合は `Unchanged` として skip します。

installer はインストール先の `.codex-config-managed-files` に source repo、
source commit、install 時刻、管理対象ファイル一覧を含む manifest を書き込みます。

| 目的 | Windows | macOS/Linux |
| --- | --- | --- |
| 通常インストール | `.\scripts\install.ps1` | `pwsh ./scripts/install.ps1` |
| 事前確認 | `.\scripts\install.ps1 -WhatIf` | `pwsh ./scripts/install.ps1 -WhatIf` |
| 既存の管理対象ファイルを置き換える | `.\scripts\install.ps1 -Overwrite` | `pwsh ./scripts/install.ps1 -Overwrite` |
| 前回管理後に削除・リネームされたファイルを `$HOME/.codex` から削除する | `.\scripts\install.ps1 -Prune` | `pwsh ./scripts/install.ps1 -Prune` |
| 置き換え前にバックアップする | `.\scripts\install.ps1 -Overwrite -Backup` | `pwsh ./scripts/install.ps1 -Overwrite -Backup` |
| 削除前にバックアップする | `.\scripts\install.ps1 -Prune -Backup` | `pwsh ./scripts/install.ps1 -Prune -Backup` |

`-Backup` は、削除または上書きされる既存ファイルを
`$HOME/.codex.backup-YYYYMMDD-HHMMSS` に退避します。
`-Backup` は `-Overwrite`、`-Prune`、または `-InstallConfig` と一緒に指定します。

untracked / ignored / hidden ファイルを意図せず配布しないよう、installer は git で
tracked されている管理対象ファイルだけをコピーします。`-Prune` も manifest に載った
過去の管理対象ファイルだけを削除し、個人用の未管理ファイルは削除しません。

`scripts/install.ps1` は、`AGENTS.md`、`rules/`、`templates/`、複数の `skills/codex-*`
をまとめて同期し、manifest と `-Prune` で管理対象を保守します。

## 共有 config baseline

`~/.codex/config.toml` は Codex runtime が local trust state や端末固有設定を
追記する可能性があるため、このリポジトリでは live `config.toml` を丸ごと同期しません。

共有可能な設定だけを `config/config.base.toml` に置き、明示指定時だけ既存 config に
merge します。

| 目的 | Windows | macOS/Linux |
| --- | --- | --- |
| baseline を既存 config に追加する | `.\scripts\install.ps1 -InstallConfig` | `pwsh ./scripts/install.ps1 -InstallConfig` |
| 既存の shared config key を明示的に置き換える | `.\scripts\install.ps1 -InstallConfig -OverwriteConfig` | `pwsh ./scripts/install.ps1 -InstallConfig -OverwriteConfig` |
| merge 前の live config をバックアップする | `.\scripts\install.ps1 -InstallConfig -OverwriteConfig -Backup` | `pwsh ./scripts/install.ps1 -InstallConfig -OverwriteConfig -Backup` |

`-InstallConfig` は、`config/config.base.toml` の managed keys を
`$CODEX_HOME/config.toml` に追加します。既存 key の値が異なる場合は上書きせず停止します。

`config/config.base.toml` と profile files には、`[projects.*]`、secrets、MCP server の
private token/path、plugin runtime state、automation state、端末固有の絶対パスを入れません。

## Profile 一覧

`config/profiles/*.config.toml` は `$CODEX_HOME/<profile>.config.toml` にコピーされます。
たとえば `config/profiles/safe.config.toml` は `codex --profile safe` で利用できます。

| Profile | 用途 | Sandbox | Network |
| --- | --- | --- | --- |
| `workspace` | 通常開発用。検証や依存解決の生産性を優先する。 | `workspace-write` | enabled |
| `local-check` | 初期調査後のローカル検証用。外向き通信は避ける。 | `workspace-write` | disabled |
| `safe` | 初見・未信頼 repo、レビュー専用、no-network 調査用。 | `read-only` | disabled |

`workspace` では network access を許可しますが、remote mutation、package install、
publish、migration、破壊的な local command は `rules/command-policy.rules` で
確認を挟む方針です。

初見・未信頼 repo では、build/test も任意コード実行として扱います。まず `safe` で
調査し、信頼できると判断した後に `local-check` または `workspace` へ切り替えます。

## Codex スキルだけをインストールする場合

`skills/codex-*` だけを配布したい場合は、GitHub CLI の
[`gh skill install`](https://cli.github.com/manual/gh_skill_install) も利用できます。
全体設定ではなく、特定 skill だけを Codex の user scope に入れたいときに使います。

```powershell
gh skill install tshimada-dev/codex-config codex-repo-scout --agent codex --scope user
```

## Copilot アダプター実験

GitHub Copilot に試験的に入れる場合は、`scripts/install-copilot-skills.ps1` を使うと、
source repository 側の `codex-*` Skill を保ったまま、Copilot 側へ `copilot-*`
名でインストールできます。デフォルトの導入先は `$HOME/.copilot/skills` です。

```powershell
.\scripts\install-copilot-skills.ps1 -WhatIf
.\scripts\install-copilot-skills.ps1
```

デフォルトでは、ツール中立に使いやすい `task-intake`、`repo-scout`、
`implementation-loop`、`debug-discipline`、`plan-slices`、`pr-readiness`、
`ui-quality-gate` だけを導入します。`codex-claude-code-reviewer` や
`codex-wsl-command-bridge` のような Codex/環境結合の強い Skill は、明示指定しない限り
Copilot 側へ入れません。

既存の Copilot Skill と内容が異なる場合、デフォルトでは上書きせず停止します。
置き換える場合は `-Overwrite`、置き換え前に退避する場合は `-Overwrite -Backup` を
指定します。特定 Skill だけ入れる場合は `-SkillName repo-scout,implementation-loop`
のように指定できます。管理対象の `codex-*` Skill をすべて変換したい場合は、
移植できる意味を確認したうえで `-AllSkills` を指定します。

Copilot では Codex profile と同じ粒度の権限切り替えは再現しにくいため、このアダプターは
完全な移植ではありません。初心者向けに、read-only ではなく「本当に危険な操作だけ
承認必須」に寄せたい場合は、Copilot guardrails も導入できます。通常の編集、テスト、
フォーマット、`git status` や `git diff` は妨げず、`git reset --hard`、`git clean`、
force push、削除系、publish/deploy/migration 系、secret 操作などだけ明示確認を
求める方針です。

```powershell
.\scripts\install-copilot-guardrails.ps1
```

このコマンドは `$HOME/.copilot/instructions` に guardrail instruction を入れます。
VS Code の terminal auto-approve 設定にも危険コマンドの deny list を merge する場合は、
既存 settings をバックアップしたうえで明示的に実行します。

```powershell
.\scripts\install-copilot-guardrails.ps1 -ApplyVSCodeSettings -Backup
```

VS Code の `settings.json` に JSONC コメントが含まれる場合、merge でコメントを保持できないため
デフォルトでは停止します。コメントが消えることを理解したうえで自動 merge する場合だけ、
`-AllowJsoncRewrite` を追加します。

## 運用方針

このリポジトリは保守的に管理します。

- 再利用できるスキルとドキュメントだけを管理する。
- シークレット、トークン、`.env`、プラグインキャッシュ、automation の状態はコミットしない。
- 端末固有の上書き設定は、git 管理外の local ファイルに置く。
- live `config.toml` は丸ごと同期せず、共有可能な baseline だけを明示 merge する。
- 通常開発は生産性のため network access を許可し、初見・未信頼 repo では `safe` profile を使う。
- 危険なコマンドは broad allow にせず、prompt または forbidden のルールに入れる。
- Codex が実行時に読む canonical な定義は英語版のままにし、日本語訳は `docs/ja/` に置く。
- 英語版を変更したら日本語参考訳を更新し、訳文ファイルに未コミットの本文変更がある状態で `.\scripts\check-ja-source-commits.ps1 -Update` を実行して `source_commit` を同期する。
- 訳文の変更が不要だと確認済みの場合だけ、`.\scripts\check-ja-source-commits.ps1 -Update -AllowMetadataOnlyUpdate` で metadata だけを同期する。

## 日本語参考訳

英語の canonical ドキュメントを読みやすくするため、日本語の参考訳を
[docs/ja/README.md](docs/ja/README.md) にまとめています。

内容が英語版と食い違う場合は、英語版を優先します。

## ライセンス

MIT License. See [LICENSE](LICENSE).

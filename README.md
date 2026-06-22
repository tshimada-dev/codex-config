# Codex Config

個人用の Codex 設定を、複数端末で使い回すためのリポジトリです。

これは社内標準や公式ルールではなく、個人の作業環境を再現するための設定集です。
AI 活用状況を説明する際の実例として参照することはありますが、導入を前提とした
汎用テンプレートではありません。

## 管理するもの

このリポジトリでは、再利用しやすい Codex の作業ルール、テンプレート、汎用的な
`codex-*` スキル、共有可能な config baseline だけを管理します。

- `AGENTS.md`: グローバルな Codex 作業ルール
- `rules/`: 共通のコマンドポリシーと長時間作業用の手順
- `templates/`: run note や repository instruction のテンプレート
- `skills/codex-*`: 汎用的な Codex ワークフロースキル
- `config/`: 共有可能な `config.toml` baseline と profile files
- `scripts/install.ps1`: 管理対象ファイルを `$HOME\.codex` にコピーする導入スクリプト
- `scripts/check-ja-source-commits.ps1`: 日本語参考訳の `source_commit` 検査スクリプト
- `docs/ja/`: 人間が読むための日本語参考訳

管理しないもの:

- シークレット、トークン、`.env`
- プラグインキャッシュ、automation の状態、実行ログ
- 端末固有のローカルファイル
- live `config.toml` 全体

## インストール

前提: PowerShell 7+ と Git が利用できる環境で、git clone した作業ツリーから実行します。

デフォルトでは `$env:CODEX_HOME` を優先し、未設定の場合は `$HOME\.codex` に
インストールします。インストール先に同名ファイルがあり、内容が異なる場合は
上書きせずに停止します。既存ファイルと同じ内容の場合は `Unchanged` として skip します。

installer はインストール先の `.codex-config-managed-files` に source repo、
source commit、install 時刻、管理対象ファイル一覧を含む manifest を書き込みます。

| 目的 | コマンド |
| --- | --- |
| 通常インストール | `.\scripts\install.ps1` |
| 事前確認 | `.\scripts\install.ps1 -WhatIf` |
| 既存の管理対象ファイルを置き換える | `.\scripts\install.ps1 -Overwrite` |
| 前回管理後に削除・リネームされたファイルを `$HOME\.codex` から削除する | `.\scripts\install.ps1 -Prune` |
| 置き換え前にバックアップする | `.\scripts\install.ps1 -Overwrite -Backup` |
| 削除前にバックアップする | `.\scripts\install.ps1 -Prune -Backup` |

`-Backup` は、削除または上書きされる既存ファイルを
`$HOME\.codex.backup-YYYYMMDD-HHMMSS` に退避します。
`-Backup` は `-Overwrite`、`-Prune`、または `-InstallConfig` と一緒に指定します。

untracked / ignored / hidden ファイルを意図せず配布しないよう、installer は git で
tracked されている管理対象ファイルだけをコピーします。`-Prune` も manifest に載った
過去の管理対象ファイルだけを削除し、個人用の未管理ファイルは削除しません。

## Config Baseline

`~/.codex/config.toml` は Codex runtime が local trust state や端末固有設定を
追記する可能性があるため、このリポジトリでは live `config.toml` を丸ごと同期しません。

共有可能な設定だけを `config/config.base.toml` に置き、明示指定時だけ既存 config に
merge します。

| 目的 | コマンド |
| --- | --- |
| baseline を既存 config に追加する | `.\scripts\install.ps1 -InstallConfig` |
| 既存の shared config key を明示的に置き換える | `.\scripts\install.ps1 -InstallConfig -OverwriteConfig` |
| merge 前の live config をバックアップする | `.\scripts\install.ps1 -InstallConfig -OverwriteConfig -Backup` |

`-InstallConfig` は、`config/config.base.toml` の managed keys を
`$CODEX_HOME/config.toml` に追加します。既存 key の値が異なる場合は上書きせず停止します。

`config/config.base.toml` と profile files には、`[projects.*]`、secrets、MCP server の
private token/path、plugin runtime state、automation state、端末固有の絶対パスを入れません。

## Profiles

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

## スキルだけをインストールする場合

`skills/codex-*` だけを配布したい場合は、GitHub CLI の
[`gh skill install`](https://cli.github.com/manual/gh_skill_install) も利用できます。
全体設定ではなく、特定 skill だけを Codex の user scope に入れたいときに使います。

```powershell
gh skill install tshimada-dev/codex-config codex-repo-scout --agent codex --scope user
```

このリポジトリの `scripts/install.ps1` は、`AGENTS.md`、`rules/`、`templates/`、
複数の `skills/codex-*` をまとめて同期し、manifest と `-Prune` で管理対象を保守する
ために残します。

## 見積もりスキル

`skills/codex-effort-estimator` は自己完結型の見積もりスキルとして管理します。
第三者リポジトリから取得した Skill instruction は、このリポジトリの導入スクリプトでは
インストールしません。

見積もり手法は同一 skill 内の `references/` に分け、必要に応じて WBS、component-unit
top-down anchor、parametric model、function point、use case points、top-down three-point、
constraint/capacity、risk model、PERT、公共・帳票 review、repository rebuild/completion の
各 pass を subagent に渡します。
これにより、サブエージェントの独立性を保ちつつ、外部 Skill の再配布や
サプライチェーン上の懸念を避けます。

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

## License

MIT License. See [LICENSE](LICENSE).

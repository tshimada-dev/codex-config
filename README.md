# Codex Config

個人用の Codex 設定を、複数端末で使い回すためのリポジトリです。

このリポジトリでは、再利用しやすい Codex の作業ルール、テンプレート、汎用的な
`codex-*` スキルだけを管理します。プラグインのキャッシュ、automation の状態、
シークレット、実行ログ、端末固有のローカルファイルは管理しません。

## 内容

- `AGENTS.md`: グローバルな Codex 作業ルール
- `rules/`: 共通のコマンドポリシーと長時間作業用の手順
- `templates/`: run note や repository instruction のテンプレート
- `skills/codex-*`: 汎用的な Codex ワークフロースキル
- `scripts/install.ps1`: 管理対象ファイルを `$HOME\.codex` にコピーする導入スクリプト

## インストール

このリポジトリのルートで実行します。

```powershell
.\scripts\install.ps1
```

コピー内容を事前確認する場合:

```powershell
.\scripts\install.ps1 -WhatIf
```

## 運用方針

このリポジトリは保守的に管理します。

- 再利用できるスキルとドキュメントだけを管理する。
- シークレット、トークン、`.env`、プラグインキャッシュ、automation の状態はコミットしない。
- 端末固有の上書き設定は、git 管理外の local ファイルに置く。
- 危険なコマンドは broad allow にせず、prompt または forbidden のルールに入れる。

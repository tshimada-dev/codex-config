---
source: rules/command-policy.rules
source_commit: dd1c94c
canonical: false
---

# command-policy.rules 日本語参考訳

この文書は `rules/command-policy.rules` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版の `.rules` ファイルです。

## 基本方針

このファイルは保守的に運用する。日常的に安全だと分かったコマンドだけ、具体的に許可する。

## allow

以下は読み取りまたは一般的な検証として扱い、許可する。

- `git status`
- `git diff`
- `git log`
- `git show`
- `rg`
- `npm run build`
- `npm test`
- `uv run pytest`
- `uv run ruff check`
- `uv run mypy`
- `git clean -n`
- `git clean --dry-run`
- `git restore --staged`

## forbidden

現時点では、このファイルで完全禁止する個別コマンドは定義しない。危険な操作や外部状態を変える操作は `prompt` に入れ、明示的なユーザー確認を必須にする。

## prompt

以下はユーザー確認を挟む。

- `git push`: リモートリポジトリを変更するため、明示的な確認が必要。
- `git reset --hard`: ローカル作業を破棄する。
- `git clean`: untracked files を削除する可能性がある。
- `git checkout --`: ファイル編集を破棄する可能性がある。
- `git restore`: ファイル編集を破棄する可能性がある。
- `rm -rf`: 再帰削除は明示的な制御が必要。
- `Remove-Item`: PowerShell でローカルファイルを削除する可能性がある。
- `rm`: PowerShell の削除 alias としてローカルファイルを削除する可能性がある。
- `del`: Windows の削除コマンドとしてローカルファイルを削除する可能性がある。
- `erase`: Windows の削除コマンドとしてローカルファイルを削除する可能性がある。
- `rmdir`: Windows のディレクトリ削除コマンドとしてローカルファイルを削除する可能性がある。
- `rd`: Windows のディレクトリ削除コマンドとしてローカルファイルを削除する可能性がある。
- `cmd /c del`: cmd 経由でローカルファイルを削除する可能性がある。
- `cmd /c rmdir`: cmd 経由でローカルファイルを削除する可能性がある。
- `gh release`: リモートの release 状態を変更する。
- `npm publish`: 外部 package state を変更する。
- `gh pr create`: pull request を作成する。
- `gh pr merge`: pull request を merge する。
- `npm install`: lockfile や依存関係を変更し、依存を download する可能性がある。
- `pip install`
- `python -m pip install`
- `uv sync`
- `uv add`
- `winget install`
- `gcloud`
- `gsutil`
- `docker compose up`
- `alembic upgrade`
- `alembic downgrade`

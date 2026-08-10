---
source: rules/command-policy.rules
source_blob: e448a24f50db3bfe1b21e406cd17c0646d2fdc4d
canonical: false
---

# command-policy.rules 日本語参考訳

この文書は `rules/command-policy.rules` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版の `.rules` ファイルです。

## 基本方針

このファイルは保守的に運用する。日常的に安全だと分かったコマンドだけ、具体的に許可する。

allow rule を追加するのは、読み取り専用 command に限る。repository が定義する build/test command は任意コードを実行できるため、user layer では review decision を必要とする `prompt` にする。共有 config は、対象となる prompt decision を automatic approvals reviewer に送る。手動 approval dialog を避けるためだけに `prompt` を `allow` へ置き換えてはならない。信頼済み repository では、その project config layer が trust された後に、より限定的な project-local allow rule を追加できる。package install、networked tools、publish、deploy、migration、remote mutation、cost-incurring cloud operations、破壊的 command は `prompt` または `forbidden` のままにする。

## allow

以下は読み取り専用操作として扱い、許可する。

- `git status`

## forbidden

現時点では、このファイルで完全禁止する個別コマンドは定義しない。危険な操作や外部状態を変える操作は `prompt` に入れ、明示的なユーザー確認を必須にする。

## prompt

以下はユーザー確認を挟む。

- `npm run build`: repository-controlled build script を実行するため、repository trust の確認が必要。
- `npm run <script>`: repository-controlled script を実行するため、repository trust の確認が必要。
- `npm test`: repository-controlled test script を実行するため、repository trust の確認が必要。
- `uv run pytest`: test と依存関係が任意コードを実行できるため、repository trust の確認が必要。
- `uv run ruff check`: repository-controlled tooling や plugin がコードを実行できるため、repository trust の確認が必要。
- `uv run mypy`: repository-controlled tooling や plugin がコードを実行できるため、repository trust の確認が必要。
- `rg`: `--pre` が任意のpreprocessorを実行できるため、user layerではrepository trustの確認が必要。
- `git diff`: `--ext-diff`、textconv、external diff driverが外部commandを実行できるため、repository trustの確認が必要。
- `git log`、`git show`: patch/textconv/external diff optionが外部commandを実行できるため、repository trustの確認が必要。
- `npm exec`、`npx`、`pnpm`、`yarn`、`bun`、`deno`、`uvx`: project scriptやdownload済みtoolを実行できる。
- `make`、`cargo`、`go`、`dotnet`、`mvn`、`gradle`、`gradlew`: repository-controlled build/test/plugin処理を実行できる。
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
- `aws`
- `terraform plan`
- `terraform apply`
- `terraform destroy`
- `kubectl apply`
- `kubectl delete`
- `helm upgrade`
- `helm uninstall`
- `cdk deploy`
- `cdk destroy`
- `sam deploy`
- `serverless deploy`
- `pulumi up`
- `pulumi destroy`
- `psql`
- `mysql`
- `influx`
- `docker compose up`
- `docker compose down -v`
- `docker system prune`
- `docker volume prune`
- `alembic upgrade`
- `alembic downgrade`

Cloud / infrastructure tools は読み取り専用に近い command と remote mutation を両方持つ。account、workspace、region、context、target environment が明確になるまでは、provider CLI や plan command も `prompt` に残す。apply、deploy、destroy、delete 系は remote resource の変更、cost 発生、data deletion につながるため、常に明示確認を必須にする。

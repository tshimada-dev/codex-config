# Shared Codex Config

このディレクトリには、複数端末で共有しやすい Codex config の断片を置きます。

## Files

- `config.base.toml`: `$CODEX_HOME/config.toml` に merge できる共有 baseline key
- `development-skills.json`: development Skill の role、phase、durable-edit ownership、Copilot 名、default、dependency を定義する宣言的 manifest
- `profiles/*.config.toml`: `-InstallConfig` 実行時に `$CODEX_HOME/<profile>.config.toml` へコピーされる profile file

## Scope

tracked config file には以下を入れません。

- `[projects.*]` trust state
- secrets、tokens、credentials、`.env` values
- plugin cache や marketplace runtime state
- automation state
- logs
- machine-specific absolute paths
- local tokens や private paths が必要な MCP server entries

`config.toml` は mutable runtime state です。Codex は
`[projects."/absolute/path"]` のような local trust entries を追記する可能性があるため、
この repository では live `config.toml` を丸ごとコピーしません。

共有 baseline だけを merge するには installer を使います。

```powershell
.\scripts\install.ps1 -InstallConfig
```

profile を明示して使う場合:

```powershell
codex --profile safe
codex --profile local-check
codex --profile workspace
```

`config.base.toml` と `workspace` profile は、日常開発の生産性を優先します。
workspace-write sandbox で network access を許可します。

baseline とすべての profile は `approval_policy = "on-request"` と
`approvals_reviewer = "auto_review"` を明示します。これにより sandbox や command policy が
要求した承認は automatic approvals reviewer に送られ、境界を解除せずに手動確認を減らします。
`prompt` は代理審査の入口なので、承認ダイアログを減らす目的で broad `allow` に変えません。

`safe` は、初見 repo、未信頼 repo、review-only、no-network inspection に使います。

`local-check` は、初期調査後に local writes や tests は必要だが、dependency download や
外向き network access は止めたい場合に使います。

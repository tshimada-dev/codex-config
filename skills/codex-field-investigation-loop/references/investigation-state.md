# Investigation State Bundle

Maintain one investigation state bundle as the canonical source of truth whenever work may span multiple turns, people, systems, or days. Update it at phase boundaries and after every meaningful observation or decision.

The bundle is text-first for LLM reliability and spreadsheet-friendly for human review. `workbook.xlsx` is a generated view; the Markdown, CSV, and JSONL files are canonical.

## Directory Rules

- Use one active bundle directory per investigation.
- Prefer a repo-local path when the investigation concerns a repository or files in a repository.
- Name the bundle directory `YYYYMMDD-HHMM-<short-task>` so repeated incidents have separate durable state.
- Use `docs/investigations/YYYYMMDD-HHMM-<short-task>/` for repository investigations when there is no repo convention.
- Use `$HOME/.codex/runs/<topic>/YYYYMMDD-HHMM-<short-task>/` for non-repository investigations.
- Replace the current snapshot in `STATE.md` instead of appending history, and keep it at or below 50 lines.
- Link to large raw logs instead of pasting them when safe local files exist.
- Never store secrets in any bundle file or generated workbook.

## Required Files

Create these files:

```text
STATE.md
checks.csv
command-log.jsonl
hypotheses.csv
timeline.csv
connections.csv
workbook.xlsx        # optional generated view
artifacts/           # optional raw-safe evidence files
subagent-results/    # optional evidence packets awaiting parent integration
```

## STATE.md

Purpose: let a human or subagent understand the investigation in one pass.

Use this template:

```markdown
# <short title> 調査状態

Started: <YYYY-MM-DD HH:mm TZ>
Last updated: <YYYY-MM-DD HH:mm TZ>
Status: active | paused | resolved | blocked

## 概要

| 項目 | 内容 |
| --- | --- |
| 問題 |  |
| 対象 |  |
| 現在状況 |  |
| 現在の最有力仮説 |  |
| 次の焦点 |  |
| 安全ルール |  |
| 明示許可が必要な操作 |  |
| 参照文書 / 証跡 |  |
| 最終更新 |  |

## 現在の判断

- Verified facts:
- Current inference:
- Unknowns:
- Next safe probe:

## ファイル

| 種別 | パス | 用途 |
| --- | --- | --- |
| 確認項目 | checks.csv | planned and completed checks |
| コマンドログ | command-log.jsonl | append-only probe log |
| 仮説一覧 | hypotheses.csv | falsifiable hypotheses |
| 時系列 | timeline.csv | material events |
| 接続情報 | connections.csv | stable non-secret facts |
| Spreadsheet view | workbook.xlsx | generated human review view |
```

Keep `STATE.md` current. It is the first file subagents and humans should read.

Replacement rules:

- Rewrite stale facts, conclusions, and next actions in place; never grow `STATE.md` as a running diary.
- Keep the entire file at or below 50 lines so it remains a one-screen current snapshot.
- Keep exactly one current next safe probe. Record completed probes in `checks.csv`.
- Move material history to `timeline.csv` and detailed observations to `command-log.jsonl`.
- Keep unresolved root-cause questions and residual unknowns until they are resolved or explicitly accepted.

## checks.csv

Purpose: track planned and completed checks.

Header:

```csv
ID,Layer,確認内容,コマンド/方法,Status,結果要約,証跡/参照,Owner,Timestamp
```

Recommended statuses: `未着手`, `確認中`, `完了`, `要確認`, `保留`, `対象外`.

Use `Mitigation` in the `Layer` column for an approved recovery or containment action. Mark finished probes and mitigation actions `完了`; do not retain them as the current next probe in `STATE.md`.

## command-log.jsonl

Purpose: append-only record of probes and observations. Use JSONL so appending does not require rewriting a large table.

One object per line:

```json
{"occurred_at":"","recorded_at":"","Side/Target":"","Host/IP":"","Command/Method":"","Result":"","stdout要約":"","stderr/error":"","Direct/Inference":"","Next action":""}
```

Rules:

- Record every meaningful probe.
- Use ISO 8601 timestamps with an explicit UTC offset for both time fields.
- `occurred_at` is when the probe or observation happened. It may be earlier than a preceding row when evidence is captured late.
- `recorded_at` is when the JSONL row was appended. Keep it monotonically nondecreasing in append order.
- Append late evidence with its original `occurred_at` and current `recorded_at`; do not reorder or rewrite prior rows.
- Summarize large outputs.
- Mark whether the row is a direct observation or an inference.
- Do not paste secrets.
- Append new lines instead of reformatting old lines unless correcting a clear recording error.

## hypotheses.csv

Purpose: keep reasoning explicit and falsifiable.

Header:

```csv
ID,仮説,真なら観測されること,Priority,Status,支持する証拠,弱める/否定する証拠,次のプローブ,Owner,Notes
```

Recommended priorities: `高`, `中`, `低`.

Recommended statuses: `未判定`, `支持`, `一部支持`, `弱まった`, `否定`, `保留`, `採用`.

## timeline.csv

Purpose: reconstruct incident and investigation flow without reading every command.

Header:

```csv
Timestamp,Category,Event,Observation,Decision/Impact,Reference
```

Record major events only: incident onset, environmental changes, important observations, decisions, recovery attempts, and material state changes after probes.

## connections.csv

Purpose: stable non-secret environment facts.

Header:

```csv
Category,Item,Value,Notes,Shareability,Source,Last confirmed
```

Store stable non-secret facts:

- Hostnames, instance IDs, non-secret account/project IDs
- Public IPs, private IPs, interface names, ports
- Public keys, endpoints, routes, allowed CIDRs when permitted
- Service names, timers, versions
- Access method and owner
- Source and last-confirmed timestamp

Never store secrets: private keys, passwords, psk, tokens, cookies, `.env`, API keys, secret payloads, or private certificate material.

## Investigation-to-Mitigation Transition

Investigation establishes what is known; mitigation changes state to contain or recover from impact. Do not let a successful workaround imply that root cause is proven.

Before mitigation begins, record in `STATE.md`:

- Why the work is transitioning from observation to intervention.
- The user's approval and the exact approved target, action, and effect boundary.
- Which root-cause claims remain unresolved.
- Which investigation questions remain open after mitigation.

For a bounded mitigation, use an explicit `Mitigation` layer in `checks.csv` and record the action in `command-log.jsonl` and `timeline.csv`. For large, multi-step, or cross-system mitigation, use a separate implementation bundle or an explicit `## Mitigation` section and link it from `STATE.md`. Keep unresolved investigation matters in the current snapshot until they are resolved or explicitly accepted as residual unknowns.

## Workbook View

Generate `workbook.xlsx` only as a view for humans.

Use:

```powershell
python <skill-dir>\scripts\render_workbook.py <bundle-dir>
```

or:

```bash
python <skill-dir>/scripts/render_workbook.py <bundle-dir>
```

The workbook should contain these sheets:

- `概要`
- `確認項目`
- `コマンドログ`
- `仮説一覧`
- `時系列`
- `接続情報`

If a human edits the workbook, reconcile the edits back into the canonical files before using them as evidence. Do not infer facts only from spreadsheet formatting, filters, or hidden rows.

## Subagent Evidence

Use `subagent-results/` when subagents verify hypotheses or review assumptions. Each file should be compact enough for the parent to read without loading raw logs.

Recommended evidence packet shape:

```markdown
# <Hypothesis ID> Verification

Hypothesis: ...
Assigned scope: ...
Safety class: read-only | artifact-analysis | blocked
Mutation or secret handling: none

## Probe / Analysis

- Method:
- Target:
- Timestamp:

## Observed Result

...

## Evidence Artifacts

- artifacts/<file>

## Interpretation

supported | weakened | disproved | inconclusive

## Recommended Canonical Updates

- command-log.jsonl:
- checks.csv:
- hypotheses.csv:
- timeline.csv:
- STATE.md:

## Open Questions

- ...
```

Subagents should write large raw-safe outputs under `artifacts/` and reference them from the packet. Parent Codex reviews the packet, accepts or rejects the interpretation, and updates the canonical files.

## Minimal Empty Bundle

Create the files with the headers above, then initialize `STATE.md`. Leave `workbook.xlsx` absent until the first render.

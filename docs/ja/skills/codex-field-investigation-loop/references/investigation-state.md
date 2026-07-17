---
source: skills/codex-field-investigation-loop/references/investigation-state.md
source_blob: 75f75cd68dbc62b682f37b554ce34d2206cf844a
canonical: false
---

# Investigation State Bundle 日本語参考訳

この文書は `skills/codex-field-investigation-loop/references/investigation-state.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

作業が複数 turn、複数人、複数 system、複数日にまたがる可能性がある場合は、1つの investigation state bundle を canonical source of truth として維持する。phase boundary と意味のある observation / decision の後に更新する。

bundle は LLM reliability のために text-first、human review のために spreadsheet-friendly にする。`workbook.xlsx` は generated view であり、Markdown、CSV、JSONL files が canonical。

## Directory Rules

- investigation ごとに active bundle directory を1つ使う。
- investigation が repository または repository 内 file に関係する場合は repo-local path を優先する。
- leaf directory は `YYYYMMDD-HHMM-<short-task>` と名付け、繰り返し発生する incident の durable state を分ける。
- repo convention がない repository investigation では `docs/investigations/YYYYMMDD-HHMM-<short-task>/` を使う。
- non-repository investigation では `$HOME/.codex/runs/<topic>/YYYYMMDD-HHMM-<short-task>/` を使う。
- `STATE.md` は履歴を追記せず current snapshot を置換更新し、50行以内に保つ。
- large raw logs は、安全な local file がある場合は貼り付けずに link する。
- bundle file や generated workbook に secret を保存しない。

## Required Files

次の files を作成する。

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

Purpose: human または subagent が investigation を一読で理解できるようにする。

次の template を使う。

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

`STATE.md` は常に最新に保つ。subagents と humans が最初に読む file である。

Replacement rules:

- 古い fact、conclusion、next action をその場で書き換え、`STATE.md` を running diary として増やさない。
- 全体を50行以内に保ち、one-screen の current snapshot にする。
- current next safe probe は1件だけ残す。完了した probe は `checks.csv` に記録する。
- 重要な履歴は `timeline.csv`、詳細 observation は `command-log.jsonl` に移す。
- 未解決の root-cause question と residual unknown は、解決するか明示的に受容するまで残す。

## checks.csv

Purpose: planned and completed checks を追跡する。

Header:

```csv
ID,Layer,確認内容,コマンド/方法,Status,結果要約,証跡/参照,Owner,Timestamp
```

Recommended statuses: `未着手`, `確認中`, `完了`, `要確認`, `保留`, `対象外`.

承認済みの recovery / containment action では `Layer` column に `Mitigation` を使う。完了した probe と mitigation action は `完了` にし、`STATE.md` の current next probe として残さない。

## command-log.jsonl

Purpose: probes と observations の append-only record。大きな table を書き換えなくてよいように JSONL を使う。

1行につき1 object:

```json
{"occurred_at":"","recorded_at":"","Side/Target":"","Host/IP":"","Command/Method":"","Result":"","stdout要約":"","stderr/error":"","Direct/Inference":"","Next action":""}
```

Rules:

- 意味のある probe はすべて記録する。
- 両方の時刻 field には UTC offset 付き ISO 8601 を使う。
- `occurred_at` は probe / observation の発生時刻。evidence の採録が遅れた場合、前の row より古い時刻でもよい。
- `recorded_at` は JSONL row の追記時刻。append 順で単調非減少に保つ。
- 遅れて得た evidence は元の `occurred_at` と現在の `recorded_at` で追記し、既存 row を並べ替えたり書き換えたりしない。
- large outputs は要約する。
- row が direct observation か inference かを示す。
- secrets を貼り付けない。
- 明らかな記録ミスを修正する場合を除き、old lines を reformat せず new lines を append する。

## hypotheses.csv

Purpose: reasoning を explicit かつ falsifiable に保つ。

Header:

```csv
ID,仮説,真なら観測されること,Priority,Status,支持する証拠,弱める/否定する証拠,次のプローブ,Owner,Notes
```

Recommended priorities: `高`, `中`, `低`.

Recommended statuses: `未判定`, `支持`, `一部支持`, `弱まった`, `否定`, `保留`, `採用`.

## timeline.csv

Purpose: すべての command を読まずに incident と investigation flow を再構成できるようにする。

Header:

```csv
Timestamp,Category,Event,Observation,Decision/Impact,Reference
```

major events だけ記録する。例: incident onset、environmental changes、important observations、decisions、recovery attempts、probe 後の material state changes。

## connections.csv

Purpose: stable non-secret environment facts。

Header:

```csv
Category,Item,Value,Notes,Shareability,Source,Last confirmed
```

保存してよい stable non-secret facts:

- Hostnames、instance IDs、non-secret account/project IDs
- Public IPs、private IPs、interface names、ports
- 許可されている場合の public keys、endpoints、routes、allowed CIDRs
- Service names、timers、versions
- Access method と owner
- Source と last-confirmed timestamp

保存してはいけない secrets: private keys、passwords、psk、tokens、cookies、`.env`、API keys、secret payloads、private certificate material。

## Investigation-to-Mitigation Transition

investigation は known / unknown を確立し、mitigation は impact の containment / recovery のために状態を変更する。workaround が成功しても root cause の証明とはみなさない。

mitigation の開始前に `STATE.md` へ次を記録する。

- observation から intervention へ移る理由。
- user approval と、承認された正確な target、action、effect boundary。
- 未解決の root-cause claim。
- mitigation 後も open のまま残る investigation question。

限定的な mitigation は `checks.csv` の明示的な `Mitigation` layer を使い、action を `command-log.jsonl` と `timeline.csv` に記録する。大規模、multi-step、または system 横断の mitigation は、別の implementation bundle か明示的な `## Mitigation` section を使い、`STATE.md` から link する。未解決の investigation matter は、解決するか residual unknown として明示的に受容するまで current snapshot に残す。

## Workbook View

`workbook.xlsx` は humans の view としてだけ生成する。

Use:

```powershell
python <skill-dir>\scripts\render_workbook.py <bundle-dir>
```

or:

```bash
python <skill-dir>/scripts/render_workbook.py <bundle-dir>
```

workbook には次の sheets を含める。

- `概要`
- `確認項目`
- `コマンドログ`
- `仮説一覧`
- `時系列`
- `接続情報`

人間が workbook を編集した場合は、その edits を canonical files に反映してから evidence として使う。spreadsheet formatting、filters、hidden rows だけから facts を推測しない。

## Subagent Evidence

subagents が hypotheses を verify する、または assumptions を review する場合は `subagent-results/` を使う。各 file は parent が raw logs を読み込まずに確認できる程度に compact にする。

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

Subagents は large raw-safe outputs を `artifacts/` に書き、packet から参照する。Parent Codex が packet を review し、interpretation を accept / reject して、canonical files を更新する。

## Minimal Empty Bundle

上記 headers で files を作成し、`STATE.md` を初期化する。`workbook.xlsx` は最初の render まで存在しなくてよい。

---
source: skills/codex-field-investigation-loop/references/investigation-state.md
source_commit: d0188c88d6321b69f96dad47cdcd7f741eb2bd06
canonical: false
---

# Investigation State Bundle 日本語参考訳

この文書は `skills/codex-field-investigation-loop/references/investigation-state.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

作業が複数 turn、複数人、複数 system、複数日にまたがる可能性がある場合は、1つの investigation state bundle を canonical source of truth として維持する。phase boundary と意味のある observation / decision の後に更新する。

bundle は LLM reliability のために text-first、human review のために spreadsheet-friendly にする。`workbook.xlsx` は generated view であり、Markdown、CSV、JSONL files が canonical。

## Directory Rules

- investigation ごとに active bundle directory を1つ使う。
- investigation が repository または repository 内 file に関係する場合は repo-local path を優先する。
- repo convention がない場合は `$HOME/.codex/runs/<topic>/YYYYMMDD-HHMM-<short-task>/` を使う。
- `STATE.md` は Codex と人間が素早く読み返せる程度に簡潔に保つ。
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

## checks.csv

Purpose: planned and completed checks を追跡する。

Header:

```csv
ID,Layer,確認内容,コマンド/方法,Status,結果要約,証跡/参照,Owner,Timestamp
```

Recommended statuses: `未着手`, `確認中`, `完了`, `要確認`, `保留`, `対象外`.

## command-log.jsonl

Purpose: probes と observations の append-only record。大きな table を書き換えなくてよいように JSONL を使う。

1行につき1 object:

```json
{"Timestamp":"","Side/Target":"","Host/IP":"","Command/Method":"","Result":"","stdout要約":"","stderr/error":"","Direct/Inference":"","Next action":""}
```

Rules:

- 意味のある probe はすべて記録する。
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

## Minimal Empty Bundle

上記 headers で files を作成し、`STATE.md` を初期化する。`workbook.xlsx` は最初の render まで存在しなくてよい。

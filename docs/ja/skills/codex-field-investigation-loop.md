---
source: skills/codex-field-investigation-loop/SKILL.md
source_blob: 1547a26ce7383f10407e0cf10170b6e860e52aa2
canonical: false
---

# codex-field-investigation-loop 日本語参考訳

この文書は `skills/codex-field-investigation-loop/SKILL.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

## 目的

現地障害、incident、production、network、infrastructure、device、system troubleshooting を、証拠、仮説、安全な probe、引き継ぎ可能な状態管理に基づいて進める。

## 基本方針

調査状態は chat ではなく investigation state bundle を正本にする。chat と `workbook.xlsx` は一時的な view として扱い、意味のある観測があったら text bundle を先に更新する。

## Core Loop

1. **Frame**
   - 問題を1文で表す。
   - 対象 system、access path、owner、安全制約、既存 evidence を確認する。
   - 足りない必須情報だけ質問し、それ以外は進める。

2. **Preserve**
   - 変更前に現在状態を保存する。
   - command、timestamp、target、要約 output、direct observation か inference かを記録する。
   - secret は記録しない。危険な output は redact または要約する。

3. **Classify**
   - failure を user symptom、client/device、local network、DNS/time、service process、config、server/cloud、dependency、policy/security、recent changes に分ける。
   - healthy と分かっている layer、unknown な layer、矛盾している layer を明確にする。

4. **Hypothesize**
   - `references/hypothesis-loop.md` を読む。
   - active hypothesis は 2-5 個に保つ。
   - 仮説は「原因が真なら、probe で特定の observable result が出る」という falsifiable な形で書く。

5. **Probe**
   - 仮説を切り分ける、最も安全で狭い probe を選ぶ。
   - 一度に1つの仮説を test する。
   - cloud、infrastructure、database、deployment、migration probe では、command の前に `codex-cloud-ops-intake` で exact target と approval boundary を確立する。
   - まず read-only probe を優先する。production mutation、restart、destructive command、deployment、migration、secret handling の前には明示承認で停止する。

6. **Update**
   - 意味のある結果の直後に investigation state bundle を更新する。
   - hypothesis を supported、weakened、disproved、blocked、still unknown に更新する。
   - current conclusion と next probe を更新する。
   - spreadsheet review が必要な場合は workbook view を再生成する。

7. **Hand Off**
   - current symptom、verified facts、top hypotheses、rejected hypotheses、next safe command/action、required approvals、open questions、state bundle path を簡潔に残す。

## Investigation State Bundle

investigation state bundle を作成または再構成する前に `references/investigation-state.md` を読む。

bundle directory は最も永続的で自然な場所に作る。各 investigation が1つの durable bundle を持ち、繰り返し発生する incident が衝突しないよう、leaf directory は `YYYYMMDD-HHMM-<short-task>` という timestamp 付き名前にする。

- Repository investigation: repo の documented notes location、慣習がなければ `docs/investigations/YYYYMMDD-HHMM-<short-task>/`。
- Non-repository investigation: `$HOME/.codex/runs/<topic>/YYYYMMDD-HHMM-<short-task>/`。
- Long-running work: user の run-note convention があればそれに合わせる。

canonical files:

- `STATE.md`: current summary、current conclusion、next action、安全制約。
- `checks.csv`: planned and completed checks。
- `command-log.jsonl`: append-only probe and observation log。
- `hypotheses.csv`: falsifiable hypotheses and status。
- `timeline.csv`: material incident and investigation events。
- `connections.csv`: stable non-secret environment facts。
- `workbook.xlsx`: 任意の generated spreadsheet view。source of truth ではない。

長い調査では、別の Codex session や teammate が再開できるように bundle を chat の外に置く。

親の context 圧迫を減らす場合は、任意の support directories を使う。

- `artifacts/`: summary から参照する raw-safe command outputs、screenshots、excerpts、logs。
- `subagent-results/`: parent integration 待ちの subagent evidence packets と verification notes。

## Spreadsheet View

Codex が編集する正本には text files を使い、人間の review には XLSX を使う。

- `STATE.md`、CSV、JSONL files を直接更新する。
- 新しい facts を `workbook.xlsx` だけに置かない。
- spreadsheet が有用なときは `scripts/render_workbook.py <bundle-dir>` で canonical files から `workbook.xlsx` を再生成する。
- 人間が spreadsheet を編集した場合は、続行前に変更を canonical text files に反映する。

## Subagents

調査が nontrivial、広範囲、または assumption-heavy な場合は subagents を使う。

適した subagent task:

- current investigation state bundle の assumption を challenge する。
- network、device、cloud、app、security、operations など特定視点から hypothesis を提案する。
- 割り当てられた1つの hypothesis を read-only probes または log analysis で verify する。
- 次の probe が本当に hypothesis を切り分けるか review する。
- evidence が current conclusion を支えているか確認する。

Parent Codex は investigation direction、安全、approval boundaries、canonical state updates、integration、final reporting を所有する。

Subagents は parent context load を下げるため hypothesis verification を担当してよいが、parent が割り当てた scope 内に限定する。

- read-only commands、log analysis、local artifact inspection、reasoning checks を優先する。
- subagents に production mutation、service restart、destructive command、deploy、migration、secret handling を任せない。
- large raw-safe outputs は `artifacts/` に保存し、compact evidence packets は `subagent-results/` に返させる。
- canonical CSV/JSONL/Markdown files を直接編集させず、state update recommendation を返させる。
- Parent が evidence packet を review し、interpretation を採択するか決め、accepted updates を canonical bundle に反映する。

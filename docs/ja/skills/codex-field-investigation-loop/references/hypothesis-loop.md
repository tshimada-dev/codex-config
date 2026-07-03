---
source: skills/codex-field-investigation-loop/references/hypothesis-loop.md
source_commit: d0188c88d6321b69f96dad47cdcd7f741eb2bd06
canonical: false
---

# Hypothesis Loop 日本語参考訳

この文書は `skills/codex-field-investigation-loop/references/hypothesis-loop.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

investigation state bundle を memory として使う。chat summary と generated workbook は二次的なものとして扱う。

## Loop Shape

1. 最新の `STATE.md`、`checks.csv`、`command-log.jsonl`、`hypotheses.csv`、`timeline.csv`、`connections.csv` を読む。
2. 現在最も強い 2-5 個の hypothesis を特定する。
3. 次に test する hypothesis を1つ選ぶ。
4. 最小で安全な probe を定義する。
5. probe を実行するか、user に実行してもらう。
6. raw-safe な result summary を `command-log.jsonl` に append する。
7. `checks.csv`、`hypotheses.csv`、`timeline.csv`、`STATE.md` の current status を更新する。
8. spreadsheet review が有用なときは `workbook.xlsx` を再生成する。
9. 繰り返す。

## Hypothesis Format

hypothesis は次の形で書く。

```text
If <cause> is true, then <probe> will show <observable result>.
```

良い例:

```text
If the device is not sending UDP packets to the server, then the server-side peer will continue to have no endpoint/latest handshake while the device-side wg transfer may show sent-only bytes.
```

弱い例:

```text
Network problem.
```

## Subagent Prompts

investigation state に independent review ができるだけの observation がある場合は subagents を使う。bundle path または compact export と narrow task を渡す。望ましい結論は渡さない。

prompt 例:

```text
Use the investigation state bundle at <path>. Review `STATE.md`, `checks.csv`, `command-log.jsonl`, `hypotheses.csv`, `timeline.csv`, and `connections.csv`. Identify assumptions that may be wrong, propose 3-5 falsifiable hypotheses, and recommend the next safest probes. Do not request destructive or production-mutating actions.
```

複数 subagents を使う場合は視点で分ける。

- Network / routing reviewer
- Device-side reviewer
- Server / cloud-side reviewer
- Procedure / safety reviewer

各 subagent に以下を返させる。

- Challenged assumptions
- Proposed or re-ranked hypotheses
- Investigation state から使った evidence
- Next probes
- Safety concerns

## Updating After A Probe

各 probe の後に行うこと:

- `command-log.jsonl` entry を1つ append する。
- 関連する `checks.csv` の status と result を更新する。
- 影響を受けた `hypotheses.csv` の各 row を更新する。
- material event について `timeline.csv` row を追加する。
- current status と next action で `STATE.md` を更新する。
- human-readable spreadsheet view が必要な場合は `workbook.xlsx` を再生成する。

重要な observation を chat だけ、または `workbook.xlsx` だけに残さない。

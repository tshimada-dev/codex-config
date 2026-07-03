---
source: skills/codex-field-investigation-loop/references/hypothesis-loop.md
source_commit: e5e94281a1ddd5da7ee18af955acae50319ce47b
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

parent context が不足している場合は、step 5 と最初の interpretation pass を subagent に委任する。Parent は引き続き safety approval、final interpretation、canonical state updates を所有する。

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

investigation state に independent review ができるだけの observation がある場合、または特定の hypothesis を独立に verify できる場合は subagents を使う。bundle path または compact export と narrow task を渡す。望ましい結論は渡さない。

prompt 例:

```text
Use the investigation state bundle at <path>. Review `STATE.md`, `checks.csv`, `command-log.jsonl`, `hypotheses.csv`, `timeline.csv`, and `connections.csv`. Identify assumptions that may be wrong, propose 3-5 falsifiable hypotheses, and recommend the next safest probes. Do not request destructive or production-mutating actions.
```

Hypothesis verification prompt:

```text
Use the investigation state bundle at <path>. Verify hypothesis <ID> only. Use read-only probes, local logs, or existing artifacts; do not mutate production, restart services, deploy, migrate, or handle secrets. Save large raw-safe outputs under `artifacts/` and write a compact evidence packet under `subagent-results/<ID>-<short-name>.md`. Recommend canonical state updates, but do not edit `STATE.md`, CSV, or JSONL files directly.
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

hypothesis verification tasks では、次の evidence packet を返させる。

- Hypothesis ID と exact hypothesis text
- 実行した probe または analysis
- Safety class と mutation / secret handling が無かったことの確認
- Observed result summary
- Evidence artifact paths
- Interpretation: `supported`, `weakened`, `disproved`, or `inconclusive`
- `command-log.jsonl`、`checks.csv`、`hypotheses.csv`、`timeline.csv`、`STATE.md` への recommended updates
- Open questions or blocked probes

## Updating After A Probe

各 probe の後に行うこと:

- `command-log.jsonl` entry を1つ append する。
- 関連する `checks.csv` の status と result を更新する。
- 影響を受けた `hypotheses.csv` の各 row を更新する。
- material event について `timeline.csv` row を追加する。
- current status と next action で `STATE.md` を更新する。
- human-readable spreadsheet view が必要な場合は `workbook.xlsx` を再生成する。

subagent が probe を実行した場合は、まず evidence packet を review する。Parent Codex が interpretation を採択するか決め、accepted updates を canonical files に反映する。

重要な observation を chat だけ、subagent result だけ、または `workbook.xlsx` だけに残さない。

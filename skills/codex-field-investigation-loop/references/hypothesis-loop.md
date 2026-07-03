# Hypothesis Loop

Use the investigation state bundle as memory. Chat summaries and generated workbooks are secondary.

## Loop Shape

1. Read the latest `STATE.md`, `checks.csv`, `command-log.jsonl`, `hypotheses.csv`, `timeline.csv`, and `connections.csv`.
2. Identify the current strongest 2-5 hypotheses.
3. Choose one hypothesis to test next.
4. Define the smallest safe probe.
5. Run or ask the user to run the probe.
6. Append a raw-safe result summary to `command-log.jsonl`.
7. Update `checks.csv`, `hypotheses.csv`, `timeline.csv`, and the current status in `STATE.md`.
8. Regenerate `workbook.xlsx` when spreadsheet review is useful.
9. Repeat.

## Hypothesis Format

Write hypotheses like this:

```text
If <cause> is true, then <probe> will show <observable result>.
```

Good:

```text
If the device is not sending UDP packets to the server, then the server-side peer will continue to have no endpoint/latest handshake while the device-side wg transfer may show sent-only bytes.
```

Weak:

```text
Network problem.
```

## Subagent Prompts

Use subagents when the investigation state has enough observations for independent review. Provide the bundle path or a compact export and a narrow task. Do not give them the desired conclusion.

Example prompt:

```text
Use the investigation state bundle at <path>. Review `STATE.md`, `checks.csv`, `command-log.jsonl`, `hypotheses.csv`, `timeline.csv`, and `connections.csv`. Identify assumptions that may be wrong, propose 3-5 falsifiable hypotheses, and recommend the next safest probes. Do not request destructive or production-mutating actions.
```

For multiple subagents, split by viewpoint:

- Network / routing reviewer
- Device-side reviewer
- Server / cloud-side reviewer
- Procedure / safety reviewer

Require each subagent to return:

- Assumptions challenged
- Hypotheses proposed or re-ranked
- Evidence used from the investigation state
- Next probes
- Safety concerns

## Updating After A Probe

After each probe:

- Append one `command-log.jsonl` entry.
- Update the related `checks.csv` status and result.
- Update every affected row in `hypotheses.csv`.
- Add a `timeline.csv` row for material events.
- Refresh `STATE.md` with current status and next action.
- Regenerate `workbook.xlsx` if a human-readable spreadsheet view is needed.

Do not leave important observations only in chat or only in `workbook.xlsx`.

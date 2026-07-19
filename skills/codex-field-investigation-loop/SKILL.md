---
name: codex-field-investigation-loop
description: "Run disciplined Codex-led incident, field, production, network, infrastructure, device, or system troubleshooting using an investigation state bundle as the canonical source of truth. Use when Codex must investigate a fault over multiple observations: clarify the problem, preserve evidence, separate facts from inference, maintain durable CSV/JSONL/Markdown state, optionally render an XLSX workbook for human review, use subagents for independent hypothesis generation or assumption checks, test hypotheses safely, update conclusions, and hand off next actions."
---

# Codex Field Investigation Loop

Use this skill to make Codex a reliable incident investigator: cautious with production, explicit about evidence, humble about assumptions, and persistent about updating state after every probe.

Use an investigation state bundle as the canonical source of truth. Treat chat and generated workbooks as transient views; after each meaningful observation, update the text bundle first.

## Core Loop

1. **Frame**
   - State the problem in one sentence.
   - Identify target systems, access paths, owners, safety constraints, and what evidence already exists.
   - Ask only for missing essentials; otherwise proceed.

2. **Preserve**
   - Before changing anything, capture current state.
   - Record commands, timestamps, targets, summarized outputs, and whether each item is direct observation or inference.
   - Never record secrets. Redact or summarize risky output.

3. **Classify**
   - Split the failure into layers: user symptom, client/device, local network, DNS/time, service process, config, server/cloud, dependency, policy/security, and recent changes.
   - Identify what layer is already proven healthy, what is unknown, and what is contradicted.

4. **Hypothesize**
   - Read `references/hypothesis-loop.md`.
   - Keep 2-5 active hypotheses.
   - Write each hypothesis in falsifiable form: if the cause is true, a probe will show a specific observable result.

5. **Probe**
   - Pick the safest, narrowest probe that distinguishes hypotheses.
   - Test one hypothesis at a time.
   - For cloud, infrastructure, database, deployment, or migration probes, use `codex-cloud-ops-intake` to establish the exact target and approval boundary before commands.
   - Prefer read-only probes first. Stop for explicit approval before production mutations, restarts, destructive commands, deployments, migrations, or secret handling.

6. **Update**
   - Update the investigation state bundle immediately after each meaningful result.
   - Mark hypotheses as supported, weakened, disproved, blocked, or still unknown.
   - Replace the current snapshot in `STATE.md`; do not append investigation history there.
   - Keep only one current next safe probe in `STATE.md`. Move completed checks to `checks.csv` and material history to `timeline.csv`.
   - Regenerate the workbook view when the user needs spreadsheet review.

7. **Transition to Mitigation**
   - Keep investigation and mitigation distinct. A workaround or recovery action does not prove root cause.
   - Before a mutation or recovery action, record the transition reason, the user's approval and approved scope, unresolved root cause, and open investigation questions.
   - Tag bounded recovery work as `Mitigation` in `checks.csv`. Move large or cross-system mitigation into a separate implementation bundle or explicit mitigation section and link it from `STATE.md`.
   - Keep unresolved investigation questions in `STATE.md` until they are resolved or explicitly accepted as residual unknowns.

8. **Hand Off**
   - Leave a concise status: current symptom, verified facts, top hypotheses, rejected hypotheses, next safe command/action, required approvals, open questions, and the state bundle path.

## Investigation State Bundle

Read `references/investigation-state.md` before creating or reorganizing an investigation state bundle.

Create the bundle directory in the most relevant durable location. Use a timestamped leaf directory named `YYYYMMDD-HHMM-<short-task>` so each investigation has one durable bundle and repeated incidents do not collide.

- Repository investigations: under the repo's documented notes location, or `docs/investigations/YYYYMMDD-HHMM-<short-task>/` when no convention exists.
- Non-repository investigations: under `$HOME/.codex/runs/<topic>/YYYYMMDD-HHMM-<short-task>/`.
- Long-running work: align with the user's run-note convention if one exists.

Use these canonical files:

- `STATE.md`: replacement-updated current snapshot, limited to 50 lines, with one next safe probe.
- `checks.csv`: planned and completed investigation or mitigation checks.
- `command-log.jsonl`: append-only probe and observation log with event and recording times.
- `hypotheses.csv`: falsifiable hypotheses and status.
- `timeline.csv`: material incident and investigation events.
- `connections.csv`: stable non-secret environment facts.
- `workbook.xlsx`: optional generated spreadsheet view, never the source of truth.

For long investigations, keep the bundle outside chat so another Codex session or teammate can resume.

Use optional support directories when they reduce parent context pressure:

- `artifacts/`: raw-safe command outputs, screenshots, excerpts, or logs referenced from summaries.
- `subagent-results/`: subagent evidence packets and verification notes awaiting parent integration.

## Spreadsheet View

Prefer text files for Codex edits and XLSX for human review.

- Update `STATE.md`, CSV, and JSONL files directly.
- Do not make `workbook.xlsx` the only place where new facts live.
- Use `scripts/render_workbook.py <bundle-dir>` to regenerate `workbook.xlsx` from the canonical files when a spreadsheet is useful.
- Use the bundled renderer as the single supported workbook-generation path. It adds snapshot metadata, source line counts, header formatting, practical column widths, and XML control-character sanitization.
- The renderer records the generation start time in the `概要` sheet and reads the canonical files for that generated view. A later canonical entry that records the generation event is intentionally absent from that workbook; regenerate the workbook to include it in a newer snapshot.
- If a human edits the spreadsheet, reconcile those changes back into the canonical text files before continuing.

## Subagents

Use subagents when the investigation is nontrivial, broad, or assumption-heavy.

Good subagent tasks:

- Challenge assumptions from the current investigation state bundle.
- Propose hypotheses from a specific viewpoint, such as network, device, cloud, app, security, or operations.
- Verify one assigned hypothesis with read-only probes or log analysis.
- Review whether the next proposed probe actually distinguishes hypotheses.
- Check whether evidence supports the current conclusion.

Parent Codex owns investigation direction, safety, approval boundaries, canonical state updates, integration, and final reporting.

Subagents may verify hypotheses to reduce parent context load, but only within the scope parent assigns:

- Prefer read-only commands, log analysis, local artifact inspection, and reasoning checks.
- Do not ask subagents to mutate production, restart services, run destructive commands, deploy, migrate, or handle secrets.
- Ask subagents to store large raw-safe outputs under `artifacts/` and return compact evidence packets under `subagent-results/`.
- Require subagents to recommend state updates instead of editing canonical CSV/JSONL/Markdown files directly.
- Parent reviews the evidence packet, decides whether to accept the interpretation, and applies accepted updates to the canonical bundle.

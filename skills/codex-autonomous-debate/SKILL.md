---
name: codex-autonomous-debate
description: Run a deterministic, state-driven autonomous debate among the materially distinct camps that shape a disputed question. Code controls phase, speaker, retries, ledger state, and terminal validity while agents own the arguments. Use when the user asks positions or factions to debate directly, reach their own conclusion, or expose the decisive fault lines. Do not use for a simple pros-and-cons summary.
---

# Codex Autonomous Debate

Run an adversarial discussion that changes a visible argument state instead of repeating fixed-round speeches. Treat the parent as a non-participating transport and evidence supervisor, not another camp or an automatic voter. Code, not the parent prompt, owns procedural state.

Before spawning participants, read [the state-driven debate protocol](references/debate-state-protocol.md) and [the deterministic controller protocol](references/controller-protocol.md). When producing the default HTML artifact, also read [the group chat artifact reference](references/group-chat-ui.md).

## Establish the contract

- State one proposition that can be affirmed, rejected, or answered by a concrete policy choice.
- Classify it as `FORECAST`, `CAUSAL`, `FACTUAL`, or `POLICY` and freeze the type and decision rule before spawning participants. For a forecast, define the target event, horizon, resolution source, and numerical YES/NO threshold; for other types, define the observable evidence or policy criteria that select each outcome.
- Select two to four materially distinct real-world camps. Give every voting camp a positive conclusion and burden of proof; disproving another camp is not sufficient.
- Use the required `OPENING`, `CROSS_EXAM`, `RESPONSE`, and `UPDATE` phases, then as many `CRUCIAL_DISPUTE` cycles as materially advance the state. Do not configure three or six cycles as a normal limit.
- Initialize `scripts/debate_controller.py` with a durable state path, stable debate ID, canonical participant IDs, and roles. Keep its default `event_limit` of 10000 and disabled `time_limit_seconds` unless a different generous emergency safety envelope is justified.
- Treat event/time limits only as last-resort safeguards against hangs or runaway delivery. They are not ordinary completion targets and cannot produce consensus or a winner.
- Require a participant-owned result: `FINAL_CONSENSUS`, `CONSENSUS_WITH_RESERVATIONS`, `FINAL_WINNER`, `TRUE_DEADLOCK`, or `INCOMPLETE`.
- Do not use majority vote. Several agents using the same model are not independent evidence, and an outvoted position may retain the decisive objection.
- Do not let the parent bypass controller terminal prerequisites. If the user separately requests a parental judgment, label it as a post-debate assessment rather than changing controller state.
- Tell the user the proposition, proposition type, target and horizon, selected and omitted camps, optional auditor, evidence mode, exact decision rule, and emergency safeguards before spawning agents.

## Map camps and evidence

For a live public dispute, research how the issue is actually divided before choosing participants:

1. Identify positions that recommend different actions or use materially different decision criteria.
2. Merge labels that would make the same decision for the same reason.
3. Keep the smallest set that preserves consequential fault lines, normally two to four camps.
4. If more than four material camps remain, select the most consequential four and disclose what was omitted. Ask the user only when omission would change the requested purpose.
5. Describe each camp as a defensible position, not an impersonation or a claim to represent a whole group.

Do not use a condition-dependent middle camp merely because it sounds balanced. When conditionality is itself a distinct operative position, retain it as a voting camp. When it only audits causality, measurement, or generalizability, use the optional non-voting methodological auditor defined in the state protocol.

Use **closed-book mode** only for fictional, supplied historical, or purely conceptual questions. Prohibit external research and unverified statistics, laws, studies, and named examples; label hypotheticals.

Use **shared-evidence mode** for current, real-world, or high-stakes disputes. The parent prepares a neutral cited camp map, structured Evidence Cards, and Claim-level Evidence Links from authoritative sources, then gives every participant the identical packet. Distinguish observed findings from camp inferences and do not allow asymmetric research during the debate.

State that selected camps are an analytical model, not demographic representation, and that the result is an argumentative outcome rather than proof of objective truth or professional advice.

## Spawn isolated participants

Use `spawn_agent` once per selected camp with `fork_turns="none"`; optionally spawn the non-voting auditor the same way. Do not create user-owned Codex tasks unless the user explicitly requests separate tasks.

Give every participant:

- the proposition, evidence mode, identical Evidence Cards, complete camp map, and role map;
- the frozen proposition contract, its `ASSIGNED_POSITION`, decision criterion, `BURDEN_OF_PROOF`, and permissible concessions;
- canonical participant names and IDs; tell them that controller-returned `next_actor` and `next_action` exclusively determine eligibility;
- the Claim Ledger rules, phase formats, argument rules, and terminal protocol from the state reference.

At every phase start, include that phase's exact fenced response template from the state reference in the `START <PHASE>` message. Do not rely on participants recalling field names or ledger syntax from their initial packet.

Require each participant to:

1. Send `READY_<ROLE>` to the parent with `send_message`, then end its initial turn.
2. Prefix each statement with `<CAMP> <PHASE>` and use the phase-specific fields.
3. Speak only after the parent relays a controller instruction naming it as `next_actor`; then read accepted peer messages and address the strongest live objection relevant to the current phase.
4. Send the statement only to the parent with `send_message`. Do not trigger a peer directly or infer a successor.
5. Wait for the next controller-approved instruction after submitting a statement.
6. Reuse the same statement and delivery ID when the parent reports an ambiguous retry; do not generate a replacement turn.
7. Obey `PAUSE`, `RESUME`, `CORRECT`, `LEDGER_SNAPSHOT`, and `STOP` from the parent.
8. Add a valid ledger action instead of rephrasing an existing position.

Spawn in reverse `OPENING` order so the opener is spawned last. Wait until the parent receives every expected readiness message. Initialize the controller before the first substantive turn, then trigger only its returned `next_actor` with `followup_task` and the returned phase/action template.

For a `FORECAST`, collect a private `PRIOR` from every voting camp after readiness and before `START OPENING`. Keep every checkpoint forecast hidden from peers until all required records for that checkpoint arrive. An assigned advocacy position does not determine the forecast value.

For every response, append the verbatim text to the transcript, map only its explicit protocol fields into a structured action envelope with a stable `event_id`, and submit that envelope to the controller. On rejection, do not broadcast or advance; request a correction for the stated reason. On acceptance, broadcast the unchanged statement to the other participants, derive `LEDGER_SNAPSHOT` from serialized controller state, then use `followup_task` only for the controller-returned `next_actor` and `next_action`. Do not advance a phase, speaker, Claim ID, or terminal state manually.

## Enforce argument quality

- Maintain the assigned operative conclusion while meeting its positive burden. Concede warranted claims without silently changing camps.
- Address the strongest reasonable competing interpretation and separate Evidence Card findings, inference, definition, value, and prediction.
- Do not invent statistics, studies, quotations, laws, technical capabilities, or named cases.
- Avoid personal attacks, motive claims, topic drift, repeated slogans, and compromise for its own sake.
- Require `POSITIVE_CASE`, `REBUTTAL`, and `UNCERTAINTY` where the phase format calls for them.
- Require cross-examination to ask one difficult question and the response to answer it directly.
- When the controller returns `STEELMAN_CONFIRM` or `STEELMAN_CORRECTION`, forward the unchanged steelman or defect only to the named actor. The controller enforces ordering, target, completion, and the one-correction limit before it can enter resolution or `CRUCIAL_DISPUTE`.
- When the controller returns `METHODOLOGY_AUDIT`, request exactly one structured audit from the named non-voting auditor. This controller-owned turn follows a materially new Evidence Link and cannot be inserted or skipped by participants.
- Treat an optional numerical belief update as participant self-assessment, not independent evidence.
- Require every material empirical Claim to carry a concrete `FALSIFIER`, and every cited Evidence Card to use a structured Evidence Link that states both what it supports and what it does not establish.
- For `FORECAST`, require private `PRIOR`, `AFTER_CROSS_EXAM`, per-cycle `AFTER_CRUCIAL_DISPUTE`, and `FINAL` records. These are correlated participant forecasts, not calibrated or independent estimates; never average them as votes.
- Do not reargue an `agreed` claim without new evidence, a scope correction, or a wording challenge.
- If a statement has no new ledger action, require one shorter correction; record repeated failure as no state change.
- Submit explicit resolution requests, operative-conclusion signals, ledger actions, and concrete next falsifiers/refinements through the controller. It moves to resolution after a valid unanimous checkpoint, explicit operative agreement, or two low-information cycles with no concrete next step. Continue beyond six cycles while accepted actions materially advance the state.

## Resolve through a checked common core

Do not ask the opener to draft or circulate the resolution. Enter resolution only when the controller returns `RESOLUTION_CANDIDATE`. Collect every required private `FINAL` forecast, then request a candidate only from its returned `next_actor`. Ignore later substantive debate statements. The auditor neither forecasts, submits, nor votes.

Require every voting camp to submit independently and privately before seeing another candidate:

```text
RESOLUTION_CANDIDATE
OUTCOME: CONSENSUS | CONSENSUS_WITH_RESERVATIONS | WINNER | DEADLOCK
WINNER: <CAMP | NONE>
DECISION: <operative conclusion or action>
AGREED_POINTS:
- <point with Claim Ledger IDs>
RESERVATIONS:
- <compatible reservation with Claim Ledger IDs>
CONFLICTS:
- <incompatible objection with Claim Ledger IDs>
RATIONALE:
- <reason tied to the frozen decision rule>
```

Do not put the submitting camp's identity in candidate text. Submit each candidate to the controller, which records private provenance, withholds it from renderer-safe metadata, and assigns deterministic content-derived IDs after every advocate submits.

Run the non-voting synthesis and `COMMON_CORE_CHECK` exactly as defined in the state protocol, using the controller's candidate order and stored common-core mapping. Submit every confirmation to the controller; only its terminal status is valid. It may split and map candidate propositions but may not invent, average, choose, or silently rewrite them. A transcription or scope correction gets one retry. Declare:

- `FINAL_CONSENSUS` when every camp accepts the complete material resolution;
- `CONSENSUS_WITH_RESERVATIONS` when every camp accepts one operative decision and common core but compatible reservations remain;
- `FINAL_WINNER` only when every camp returns the same `ACCEPT_WINNER <CAMP>` for the mapped winner atom;
- `TRUE_DEADLOCK` only for incompatible operative decisions or a material rejection of the corrected common core;
- `INCOMPLETE` when a required candidate or confirmation cannot be obtained or an emergency safeguard fires without formal deadlock evidence.

After common-core validation, derive `WHAT_WOULD_RESOLVE_THIS` only from unresolved Claims, their falsifiers, and missing or weak Evidence Links. Do not invent a research need unrelated to the live dispute. Send `STOP` to every active agent once the terminal state is valid and disregard later substantive statements.

## Observe, intervene, and handle failure

Use `wait_agent` in intervals no longer than 60 seconds. Inspect responses, submit structured actions, and do not praise, steer, answer, or decide valid arguments. Persist serialized controller state after every accepted or rejected receipt so interruption never requires transcript reconstruction.

Intervene only for an evidence-mode violation, topic drift, uncorrected misrepresentation, abandoned burden, repeated no-change speech, unsafe conduct, or invalid protocol. Send `PAUSE` to everyone, identify the invalid passage, send one precise `CORRECT` request, then `RESUME` only the participant whose turn is next. Record the intervention; never rewrite a participant's claim silently.

- On user cancellation, submit parent `CANCEL`, send `STOP` immediately, and report `INCOMPLETE`.
- On agent failure before its first substantive statement, allow one fresh replacement with the identical packet and valid transcript. After material participation, stop and return `INCOMPLETE` instead of simulating the camp.
- On message-delivery failure, retry the exact delivery once with the same event/delivery identity. Because committed state is idempotent, a duplicate cannot create another substantive turn. On a second failure, submit parent `FAILURE`, stop reachable agents, and use `INCOMPLETE`.
- When an emergency event/time safeguard fires, submit or honor `SAFETY_CEILING`, freeze the last accepted state, and use only the controller result: `TRUE_DEADLOCK` with already committed formal deadlock evidence, otherwise `INCOMPLETE`.

## Report and render

Lead with the controller terminal status. Report the proposition contract and decision rule, camps and auditor, evidence mode, completed phases/cycles, emergency-safeguard state, forecast trajectories, final Claim Ledger and falsifiers, Evidence Links, resolution candidates, common-core check, decisive argument, strongest reservation or conflict, `WHAT_WOULD_RESOLVE_THIS` needed evidence, interventions, excluded claims, and the limitation that this is an argumentative result.

Maintain a parent-observed chronological event log without rewriting participant text or exposing private candidate provenance early. Append every accepted public statement, steelman confirmation, anonymous resolution candidate, common-core check, and confirmation as a **verbatim copy at receipt time**. Store that exact content in `messages[].text`; **never summarize or reconstruct** transcript messages from the Claim Ledger or terminal report. Add renderer-safe `artifact_metadata()` as top-level `controller`; never use private metadata in a user-facing artifact. Also record the proposition contract, fully completed phases and crucial-dispute cycle count, final Claim Ledger, Evidence Cards, Evidence Links, private forecast records after they may be revealed, and needed evidence. Preserve legacy belief updates when present. In state-driven artifacts, label every resolution event as anonymous `candidate`/`confirmation` or attributed `public-statement`; never attach a camp identity to an anonymous event.

Treat JSON as the lossless source of truth. The friendly chat presentation is a **renderer-derived natural-language view** only: the renderer may relabel structured fields in the artifact language, collapse ledger mechanics, and omit phase or round status from a bubble header, but it must retain the **verbatim protocol text** in an accessible disclosure. Do not replace or add a paraphrased `messages[].text` value for presentation purposes.

After the terminal report, produce a group-chat artifact by default when local file generation is available:

1. Write the documented JSON outside the user's source repository unless repository artifacts were requested.
2. Run `scripts/render_debate_chat.py` to create self-contained HTML.
3. Link the HTML to the user.

If rendering is unavailable or fails, provide the same chronological content as a Markdown transcript. Do not delay or invalidate the terminal result because rendering failed. Keep the prose report compact; the artifact carries detail.

---
name: codex-autonomous-debate
description: Run a bounded, state-driven autonomous debate among the materially distinct camps that shape a disputed question. A parent supplies shared evidence, tracks claims, supervises cross-examination and resolution, and intervenes only for procedure, failure, or timeout. Use when the user asks positions or factions to debate directly, reach their own conclusion, or expose the decisive fault lines. Do not use for a simple pros-and-cons summary.
---

# Codex Autonomous Debate

Run an adversarial discussion that changes a visible argument state instead of repeating fixed-round speeches. Treat the parent as a non-participating procedural supervisor, not another camp or an automatic voter.

Before spawning participants, read [the state-driven debate protocol](references/debate-state-protocol.md). When producing the default HTML artifact, also read [the group chat artifact reference](references/group-chat-ui.md).

## Establish the contract

- State one proposition that can be affirmed, rejected, or answered by a concrete policy choice.
- Classify it as `FORECAST`, `CAUSAL`, `FACTUAL`, or `POLICY` and freeze the type and decision rule before spawning participants. For a forecast, define the target event, horizon, resolution source, and numerical YES/NO threshold; for other types, define the observable evidence or policy criteria that select each outcome.
- Select two to four materially distinct real-world camps. Give every voting camp a positive conclusion and burden of proof; disproving another camp is not sufficient.
- Choose light mode with a hard ceiling of three `CRUCIAL_DISPUTE` cycles or deep mode with a hard ceiling of six. The required phases are `OPENING`, `CROSS_EXAM`, `RESPONSE`, `UPDATE`, and `CRUCIAL_DISPUTE`; information gain may stop the cycles earlier.
- Calculate the planned substantive turn ceiling as `voting camp count * (4 + crucial-dispute cycle ceiling)`. When an auditor is used, add `2 + crucial-dispute cycle ceiling`: two base auditor turns for `OPENING` and `RESPONSE`, plus one additional auditor turn per crucial-dispute cycle as the worst case for a changed Evidence Link. Steelman confirmations and the one permitted correction are bounded procedural turns, not substantive turns.
- Calculate the debate budget as `max(8 minutes, planned substantive turn ceiling * 1 minute)`.
- Calculate the resolution budget as `max(4 minutes, camp count * 1 minute)`.
- Keep independent deadlines: `DEBATE_DEADLINE` is measured from `DEBATE_START`; `RESOLUTION_DEADLINE` is measured from the later `RESOLUTION_START`. Never deduct debate overrun or unused debate time from resolution.
- Require a participant-owned result: `FINAL_CONSENSUS`, `CONSENSUS_WITH_RESERVATIONS`, `FINAL_WINNER`, `TRUE_DEADLOCK`, or `INCOMPLETE`.
- Do not use majority vote. Several agents using the same model are not independent evidence, and an outvoted position may retain the decisive objection.
- Let the parent judge a winner only when the user explicitly requests it or a deadline expires and the user requires a winner.
- Tell the user the proposition, proposition type, target and horizon, selected and omitted camps, optional auditor, limits, evidence mode, and exact decision rule before spawning agents.

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
- canonical participant names, the `PHASE_SPEAKERS` map with phase-specific speaker orders and successor mappings, phase ceiling, budgets, and parent-owned deadline rules;
- the Claim Ledger rules, phase formats, argument rules, and terminal protocol from the state reference.

At every phase start, include that phase's exact fenced response template from the state reference in the `START <PHASE>` message. Do not rely on participants recalling field names or ledger syntax from their initial packet.

Require each participant to:

1. Send `READY_<ROLE>` to the parent with `send_message`, then end its initial turn.
2. Prefix each statement with `<CAMP> <PHASE>` and use the phase-specific fields.
3. Speak only when included in the current `PHASE_SPEAKERS` list; then read all queued peer messages and address the strongest live objection relevant to the current phase.
4. Copy the identical statement to the parent with `send_message`.
5. Send it to non-successors with `send_message`, then to the phase-specific successor with `followup_task` so one next turn starts; the final scheduled speaker sends `<PHASE>_READY` to the parent instead.
6. Continue without waiting for parent acknowledgement within a phase.
7. Obey `PAUSE`, `RESUME`, `CORRECT`, `LEDGER_SNAPSHOT`, and `STOP` from the parent.
8. Add a valid ledger action instead of rephrasing an existing position.

Spawn in reverse speaking order so the opener is spawned last. Wait until the parent receives every expected readiness message. Trigger only the opener with `followup_task` and `START OPENING`. Define `DEBATE_START` as the parent-observed time when the parent has successfully sent `START` to the opener. If delivery fails, follow the delivery-failure rule and do not start the clock until a retry succeeds.

For a `FORECAST`, collect a private `PRIOR` from every voting camp after readiness and before `START OPENING`. Keep every checkpoint forecast hidden from peers until all required records for that checkpoint arrive. An assigned advocacy position does not determine the forecast value.

Set `DEBATE_DEADLINE = DEBATE_START + debate budget` and send it to every active participant without triggering a turn. Within each phase the ring advances without parent relaying according to that phase's speaker list and successor map. At a phase boundary, update the Claim Ledger from copied statements, broadcast the same `LEDGER_SNAPSHOT`, handle any explicit correction, then start only the next phase opener. The final scheduled speaker sends `<PHASE>_READY` and does not start a new phase itself.

## Enforce argument quality

- Maintain the assigned operative conclusion while meeting its positive burden. Concede warranted claims without silently changing camps.
- Address the strongest reasonable competing interpretation and separate Evidence Card findings, inference, definition, value, and prediction.
- Do not invent statistics, studies, quotations, laws, technical capabilities, or named cases.
- Avoid personal attacks, motive claims, topic drift, repeated slogans, and compromise for its own sake.
- Require `POSITIVE_CASE`, `REBUTTAL`, and `UNCERTAINTY` where the phase format calls for them.
- Require cross-examination to ask one difficult question and the response to answer it directly.
- After all `UPDATE` statements, run the bounded `STEELMAN_CONFIRMATION` subphase: the parent forwards each steelman unchanged with `followup_task`, the target returns only to the parent, and all confirmations are collected before resolution or `CRUCIAL_DISPUTE`. Require `STEELMAN_ACCEPTED` before the steelman can anchor a rebuttal; allow one correction after `STEELMAN_REJECTED`.
- Treat an optional numerical belief update as participant self-assessment, not independent evidence.
- Require every material empirical Claim to carry a concrete `FALSIFIER`, and every cited Evidence Card to use a structured Evidence Link that states both what it supports and what it does not establish.
- For `FORECAST`, require private `PRIOR`, `AFTER_CROSS_EXAM`, per-cycle `AFTER_CRUCIAL_DISPUTE`, and `FINAL` records. These are correlated participant forecasts, not calibrated or independent estimates; never average them as votes.
- Do not reargue an `agreed` claim without new evidence, a scope correction, or a wording challenge.
- If a statement has no new ledger action, require one shorter correction; record repeated failure as no state change.
- Move to resolution after two consecutive low-information cycles as defined in the state protocol; unanimous `REQUEST_RESOLUTION: YES` signals at the post-`RESPONSE` `UPDATE` checkpoint or the same `CRUCIAL_DISPUTE` checkpoint; the hard ceiling; or `DEBATE_DEADLINE`. Continue within the ceiling after a material forecast shift, new falsifier, new unresolved Claim, or new/corrected Evidence Link.

## Resolve through a checked common core

Do not ask the opener to draft or circulate the resolution. After `CRUCIAL_DISPUTE_READY`, the debate deadline, or a valid unanimous `REQUEST_RESOLUTION` checkpoint, collect every required private `FINAL` forecast, then have the parent send the identical `RESOLUTION_REQUEST` to every active voting camp with `followup_task`. Ignore later substantive debate statements. The auditor neither forecasts, submits, nor votes.

Define `RESOLUTION_START` as the parent-observed time when the parent has successfully sent the identical `RESOLUTION_REQUEST` to every active voting camp. If delivery fails, follow the delivery-failure rule and do not start the clock until the complete request set succeeds. Set `RESOLUTION_DEADLINE = RESOLUTION_START + resolution budget` and notify all active participants without triggering turns.

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

Do not put the submitting camp's identity in candidate text; the parent records provenance privately. Withhold all candidates until every active camp submits or the deadline expires. Assign neutral IDs ordered by a deterministic content-derived key, never speaking or submission order.

Run the non-voting synthesis and `COMMON_CORE_CHECK` exactly as defined in the state protocol. It may split and map candidate propositions but may not invent, average, choose, or silently rewrite them. A transcription or scope correction gets one retry. Declare:

- `FINAL_CONSENSUS` when every camp accepts the complete material resolution;
- `CONSENSUS_WITH_RESERVATIONS` when every camp accepts one operative decision and common core but compatible reservations remain;
- `FINAL_WINNER` only when every camp returns the same `ACCEPT_WINNER <CAMP>` for the mapped winner atom;
- `TRUE_DEADLOCK` only for incompatible operative decisions or a material rejection of the corrected common core;
- `INCOMPLETE` when a required candidate or confirmation is missing at the deadline.

After common-core validation, derive `WHAT_WOULD_RESOLVE_THIS` only from unresolved Claims, their falsifiers, and missing or weak Evidence Links. Do not invent a research need unrelated to the live dispute. Send `STOP` to every active agent once the terminal state is valid and disregard later substantive statements.

## Observe, intervene, and handle failure

Use `wait_agent` in intervals no longer than 60 seconds and track the two deadlines from their parent-observed start times. Inspect copies sent to the parent, update only procedural state, and do not praise, steer, answer, or decide valid arguments.

Intervene only for an evidence-mode violation, topic drift, uncorrected misrepresentation, abandoned burden, repeated no-change speech, unsafe conduct, or invalid protocol. Send `PAUSE` to everyone, identify the invalid passage, send one precise `CORRECT` request, then `RESUME` only the participant whose turn is next. Record the intervention; never rewrite a participant's claim silently.

- On user cancellation, send `STOP` immediately and report no result.
- On agent failure before its first substantive statement, allow one fresh replacement with the identical packet and valid transcript. After material participation, stop and return `INCOMPLETE` instead of simulating the camp.
- On message-delivery failure, retry the exact delivery once. On a second failure, stop reachable agents and report the missing delivery.
- On `DEBATE_DEADLINE`, close debate only and start the full resolution phase from a fresh `RESOLUTION_START`.
- On `RESOLUTION_DEADLINE`, stop all agents. Return `INCOMPLETE` for a missing required response; otherwise use the valid common-core state or `TRUE_DEADLOCK`.

## Report and render

Lead with the terminal status. Report the proposition contract and decision rule, camps and auditor, evidence mode, phase/cycle limits, both phase timestamps and timeout state, forecast trajectories, final Claim Ledger and falsifiers, Evidence Links, resolution candidates, common-core check, decisive argument, strongest reservation or conflict, `WHAT_WOULD_RESOLVE_THIS` needed evidence, interventions, excluded claims, and the limitation that this is an argumentative result.

Maintain a parent-observed chronological event log without rewriting participant text or exposing private candidate provenance early. Append every valid public statement, steelman confirmation, anonymous resolution candidate, common-core check, and confirmation as a **verbatim copy at receipt time**. Store that exact content in `messages[].text`; **never summarize or reconstruct** transcript messages from the Claim Ledger or terminal report. Also record the proposition contract, fully completed phases and crucial-dispute cycle count, final Claim Ledger, Evidence Cards, Evidence Links, private forecast records after they may be revealed, and needed evidence. Preserve legacy belief updates when present. In state-driven artifacts, label every resolution event as anonymous `candidate`/`confirmation` or attributed `public-statement`; never attach a camp identity to an anonymous event.

Treat JSON as the lossless source of truth. The friendly chat presentation is a **renderer-derived natural-language view** only: the renderer may relabel structured fields in the artifact language, collapse ledger mechanics, and omit phase or round status from a bubble header, but it must retain the **verbatim protocol text** in an accessible disclosure. Do not replace or add a paraphrased `messages[].text` value for presentation purposes.

After the terminal report, produce a group-chat artifact by default when local file generation is available:

1. Write the documented JSON outside the user's source repository unless repository artifacts were requested.
2. Run `scripts/render_debate_chat.py` to create self-contained HTML.
3. Link the HTML to the user.

If rendering is unavailable or fails, provide the same chronological content as a Markdown transcript. Do not delay or invalidate the terminal result because rendering failed. Keep the prose report compact; the artifact carries detail.

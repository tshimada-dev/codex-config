---
name: codex-autonomous-debate
description: Run a bounded autonomous debate among the materially distinct camps or schools of thought that actually shape a disputed question, while a parent agent supplies shared evidence, supervises procedure, and intervenes only for violations, failure, or timeout. Use when the user explicitly asks multiple positions, factions, or personas to debate directly, reach their own conclusion, or expose the fault lines in a genuinely contested issue. Do not use for a simple pros-and-cons summary.
---

# Codex Autonomous Debate

Run a direct adversarial discussion among evidence-grounded positions. Treat the parent as a non-participating supervisor, not another camp or an automatic voter.

## Establish the contract

- State one proposition that can be affirmed, rejected, or answered by a concrete policy choice.
- Select two to four materially distinct camps. Use the real-world camps that shape an existing dispute instead of inventing two generic personas.
- Use 3 rounds per camp and roughly 300 characters per statement for a light debate.
- Use 5 rounds per camp and roughly 500 characters per statement for a deep debate.
- Calculate the debate budget as `max(4 minutes, camp count * round count * 1 minute)`.
- Calculate the resolution budget as `max(3 minutes, camp count * 1 minute)`.
- For example, 3 camps * 3 rounds = 9 debate minutes + 3 resolution minutes; 3 camps * 5 rounds = 15 debate minutes + 3 resolution minutes.
- Keep two independent deadlines: `DEBATE_DEADLINE` is measured from `DEBATE_START`, while `RESOLUTION_DEADLINE` is measured from the later `RESOLUTION_START`. Never deduct debate overrun or unused debate time from the resolution budget.
- Require a participant-owned result by default: `FINAL_CONSENSUS`, `FINAL_WINNER`, or `DEADLOCK`.
- Do not use majority vote. Several agents using the same model are not independent evidence, and an outvoted position may still contain the decisive objection.
- Let the parent judge only when the user explicitly requests it or when a deadline expires and the user requires a winner.
- Tell the user the proposition, selected camps, omitted camps, limits, evidence mode, and decision rule before spawning agents.

## Map the camps before debating

For a live public dispute, research how the issue is actually divided before choosing participants:

1. Identify positions that recommend different actions or use materially different decision criteria.
2. Merge labels that differ rhetorically but would make the same decision for the same reason.
3. Keep the smallest set that preserves the consequential fault lines, normally two to four camps.
4. If more than four material camps remain, select the most consequential four and disclose what was omitted. Ask the user only when that omission would change the requested purpose.
5. Describe each camp as a defensible position, not as an impersonation of a named person or a claim to represent every member of a group.

Use **closed-book mode** only for fictional, historical-with-supplied-material, or purely conceptual questions. Prohibit external research and unverified statistics, laws, studies, and named examples. Permit clearly labeled hypotheticals.

Use **shared-evidence mode** for current, real-world, or high-stakes disputes. Have the parent prepare both a neutral cited fact packet and a cited camp map from authoritative sources. Give every participant the identical packet. Distinguish neutral facts from sources used only to establish that a camp exists. Do not allow asymmetric research during the debate.

State that selected camps are an analytical model of the dispute, not demographic representation, and that a debate result is not proof of objective truth or professional advice.

## Spawn isolated camp advocates

Use `spawn_agent` once per selected camp with `fork_turns="none"`. Do not create user-owned Codex tasks unless the user explicitly requests separate tasks.

Give every participant:

- the proposition, evidence mode, identical fact packet, and complete camp map;
- its assigned camp, decision criterion, burden, and concessions it may make without abandoning the position;
- every canonical participant name, a fixed speaking order, its successor, the round limit, both phase budgets, and the parent-owned deadline rules;
- the argument rules and terminal protocol below.

Require each participant to:

1. Send `READY_<CAMP>` to the parent with `send_message`, then end its initial turn.
2. Prefix each substantive statement with `<CAMP> <ROUND>/<MAX_ROUNDS>`.
3. On its turn, read all queued peer messages and answer the strongest live objection, not only the immediate predecessor.
4. Copy the identical statement to the parent with `send_message`.
5. Send the statement to non-successor peers with `send_message`, then send it to the successor with `followup_task` so exactly one next turn starts.
6. Continue without waiting for acknowledgement from the parent.
7. Obey `PAUSE`, `RESUME`, `CORRECT`, and `STOP` from the parent.
8. Count only substantive debate statements, not readiness, intervention, or resolution messages.

Spawn in reverse speaking order so the opener is spawned last. Wait until the parent has received every expected `READY_<CAMP>`. Trigger only the opener with `followup_task` and `START`. Define `DEBATE_START` as the parent-observed time when the parent has successfully sent `START` to the opener; internal participant reasoning is not observable and must not be used as the start time. If delivery fails, follow the delivery-failure rule and do not start the clock until a retry succeeds.

Set `DEBATE_DEADLINE = DEBATE_START + debate budget`. Immediately send the resulting timestamp to every active camp as `DEBATE_DEADLINE: <timestamp>` without triggering a new turn. The ring then advances without the parent relaying arguments. The final speaker in the final round sends `RESOLUTION_READY` to the parent with `send_message` and does not trigger another camp.

## Enforce argument quality

Give every camp these rules:

- Maintain the assigned recommendation through the minimum rounds. Concede warranted points without silently switching camps.
- Address the strongest reasonable interpretation of competing positions.
- Separate packet facts, inferences, value judgments, and hypotheticals.
- Do not invent statistics, studies, quotations, laws, technical capabilities, or named cases.
- Avoid personal attacks, motive claims, topic drift, repeated slogans, and compromise for its own sake.
- Examine first principles, implementation, failure modes, abuse cases, affected groups, alternatives, reversibility, and decision-making under uncertainty when relevant.
- Name any shared premise and the remaining value or evidence dispute when positions begin to converge.

## Resolve without a vote

Do not ask the opener to draft or circulate the resolution. After `RESOLUTION_READY`, have the parent send the identical `RESOLUTION_REQUEST` to every active camp with `followup_task`. If `DEBATE_DEADLINE` arrives first, close the debate, disregard later substantive statements, and send the same resolution request using only the valid transcript instead of skipping resolution.

Define `RESOLUTION_START` as the parent-observed time when the parent has successfully sent the identical `RESOLUTION_REQUEST` to every active camp. If any delivery fails, follow the delivery-failure rule and do not start the resolution clock unless the complete request set is delivered. Set `RESOLUTION_DEADLINE = RESOLUTION_START + resolution budget`, then send the resulting timestamp to every active camp without triggering another turn. The resolution budget covers candidate submission, equivalence comparison or candidate circulation, and final acceptance; do not spend it on the debate phase.

Require every camp to submit independently and privately to the parent before seeing any other resolution candidate. Use this structure:

```text
RESOLUTION_CANDIDATE
OUTCOME: CONSENSUS | WINNER | DEADLOCK
WINNER: <CAMP | NONE>
DECISION: <operative conclusion or action>
AGREED_POINTS:
- <point>
UNRESOLVED_OBJECTIONS:
- <objection>
RATIONALE:
- <reason>
```

Do not put the submitting camp's identity in the candidate text; the parent records provenance privately from the message sender. The parent withholds all candidates until every active camp has submitted or `RESOLUTION_DEADLINE` expires. Do not merge, rewrite, or synthesize candidate text.

Treat candidates as equivalent only when they have the same `OUTCOME`, the same `WINNER`, the same operative `DECISION`, and the same material `AGREED_POINTS` and `UNRESOLVED_OBJECTIONS`. Ignore only wording, ordering, and other non-substantive differences. When equivalence is uncertain, classify the candidates as different rather than resolving the ambiguity by judgment.

If every candidate is equivalent, send every camp an `EQUIVALENCE_CHECK` containing the candidate IDs and a field-by-field comparison. Declare the shared outcome only when every active camp returns `ACCEPT_EQUIVALENCE`. If any camp returns `REJECT_EQUIVALENCE`, declare `DEADLOCK` and preserve the disputed field.

If candidates differ, assign neutral candidate IDs without camp attribution. Order them by a deterministic content-derived key, never by speaking or submission order, and send every unchanged candidate to every camp in that same order. Each camp returns `ACCEPT <CANDIDATE_ID>` or `REJECT_ALL` without further substantive argument. Declare `FINAL_CONSENSUS` or `FINAL_WINNER` only when every active camp accepts the same candidate. A winner requires every other camp to accept the candidate naming that winner. Otherwise declare `DEADLOCK`; the parent may report only fields that are identical across all candidates as common ground.

If an active camp does not submit a candidate or required confirmation before `RESOLUTION_DEADLINE`, report `INCOMPLETE` rather than inferring its position. If every required response arrived but the camps did not unanimously accept an equivalent or identical candidate, report `DEADLOCK`.

Send `STOP` to every active agent after the terminal state is valid. Disregard later substantive statements.

## Observe without moderating

Use `wait_agent` in intervals no longer than 60 seconds and track `DEBATE_DEADLINE` and `RESOLUTION_DEADLINE` independently from their recorded parent-observed start times. Inspect the copies sent to the parent, but do not praise, summarize, steer, relay, or answer valid arguments during the debate. Brief user updates may report the current fault line without influencing participants.

Intervene only when a specific factual assertion violates the evidence mode, the exchange leaves the proposition, a camp misrepresents another after correction is possible, a camp abandons its assigned position before the minimum, or the protocol becomes hostile, repetitive, unsafe, or invalid.

When intervention is required:

1. Send `PAUSE: <precise reason>` to every active camp.
2. Tell the other camps to disregard the challenged passage.
3. Send `CORRECT: <required correction>` to the responsible camp and require a replacement with the same sequence number.
4. Inspect the correction, then send `RESUME` only to the camp whose turn is next.
5. Record the intervention for the final report. Do not silently rewrite a participant's argument.

## Handle interruption and failure

- On user cancellation, send `STOP` immediately to every active agent and report that no result was reached.
- On agent failure before its first substantive statement, allow one fresh replacement with the identical packet, camp assignment, and valid transcript. Do not replace a camp after it has materially shaped the debate; stop and report an incomplete debate instead.
- On message-delivery failure, retry the exact delivery once. If it still fails, send `STOP` to every reachable agent and report the missing delivery rather than simulating the absent camp.
- On `DEBATE_DEADLINE`, close only the substantive debate, ignore later arguments, and begin the full resolution phase from a fresh `RESOLUTION_START`. Do not send `STOP` merely because debate time expired.
- On `RESOLUTION_DEADLINE`, send `STOP` to every active agent and ignore later messages. Return `INCOMPLETE` when a required candidate or confirmation is missing, otherwise return `DEADLOCK` unless the user required a winner; in that case judge only the valid transcript.

When parental judging is authorized, give equal weight to fidelity to the assigned burden, engagement with the strongest opposing case, internal consistency, evidence discipline, feasibility, consequences, and failure-mode handling. Do not substitute the parent's preferred policy for the rubric.

## Report the result

Lead with `FINAL_CONSENSUS`, `FINAL_WINNER`, `DEADLOCK`, `INCOMPLETE`, or parental timeout judgment. Then report:

- the proposition, selected and omitted camps, rounds, and evidence mode;
- `DEBATE_START`, `DEBATE_DEADLINE`, `RESOLUTION_START`, `RESOLUTION_DEADLINE`, and whether either phase timed out;
- the resolution candidates, equivalence comparison, and confirmations;
- the decisive argument and strongest unresolved objection;
- every parent intervention or failure, or state that none occurred;
- challenged claims excluded from consideration;
- the limitation that this is an argumentative result from selected camps, not an objective resolution of the real-world issue.

Keep the report compact unless the user asks for the transcript or detailed analysis.

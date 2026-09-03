# State-driven debate protocol

Read this reference before spawning debate participants. It replaces fixed rounds with phase-specific work and a shared Claim Ledger. The deterministic controller owns procedure; advocates and the optional auditor own arguments. Neither the controller nor the parent decides which substantive claim is true.

## Controller contract

Create the debate with the deterministic controller before sending a participant a substantive prompt. The controller is the only authority for the current phase, eligible speaker, successor, Claim Ledger IDs and procedural statuses, steelman-confirmation state, resolution state, and terminal classification.

The parent is a transport adapter and observer. It gives participants the controller's current state packet and exact response template, converts each received response into a **structured action envelope**, submits that envelope to the controller, and sends only the controller-declared next instruction. It must not advance a phase, select a successor, assign a Claim ID, or infer a terminal state from prose.

Every envelope includes at least `debate_id`, a stable caller-generated `event_id`, `actor`, `action_type`, `phase`, `payload`, and the structured fields required inside that payload. The controller records parent-observed committed timestamps and accepts a `(debate_id, event_id)` at most once. A duplicate, out-of-order, or ineligible action is rejected with a reason and cannot change substantive or procedural state. If delivery is ambiguous, retry the same envelope with the same `event_id`; ask the controller whether it was committed before sending another substantive turn.

Serialize the complete controller state after every accepted action. Resuming a debate means loading that state and continuing from its declared next action; do not reconstruct phase, ledger, confirmation, or resolution state from transcript text. Keep the participant's original text verbatim in the separate chronological transcript, but treat it as argument content rather than the source of procedural truth.

Normal completion is conclusion-driven. Continue while a valid state-changing action can materially advance an unresolved dispute. The controller moves to resolution only at a valid shared checkpoint, after an agreed operative conclusion, after a genuine no-progress/deadlock condition, or after a required-participation failure. A configurable, intentionally generous absolute time or event ceiling is an emergency safeguard against hangs or runaway delivery only; it is not a normal target and cannot manufacture consensus.

## Proposition contract and decision rule

Freeze one type before spawning:

- `FORECAST`: whether a resolvable event will occur by a horizon;
- `CAUSAL`: whether a specified intervention or factor causes a specified outcome under stated conditions;
- `FACTUAL`: whether a bounded descriptive claim is true under an explicit evidence standard;
- `POLICY`: which action best satisfies named criteria, constraints, and trade-offs.

Publish the contract in this exact form:

```text
PROPOSITION_TYPE: FORECAST | CAUSAL | FACTUAL | POLICY
TARGET_EVENT: <observable event, causal contrast, fact, or policy outcome>
HORIZON: <date or NOT_APPLICABLE with reason>
YES_CONDITION: <exact rule selecting YES or the proposed action>
NO_CONDITION: <exact rule selecting NO or the alternative action>
RESOLUTION_SOURCE: <source or observation that can settle the target>
THRESHOLD: <probability for FORECAST, otherwise NOT_APPLICABLE>
```

For `FORECAST`, a common rule is `YES when P(target event by horizon) > 0.50`; never infer a threshold after seeing arguments. For `CAUSAL`, name the intervention, comparison, population, outcome, and evidence standard. For `FACTUAL`, name the scope and evidence standard. For `POLICY`, name the operative alternatives, criteria, and tie rule. If the proposition cannot be made decision-complete, pause before spawning.

## Roles

Use two to four voting advocates drawn from the material real-world camps. Give each advocate a positive burden; opposing another camp is not enough.

When the dispute turns primarily on causality, measurement, study quality, or generalizability, add one **non-voting methodological auditor** instead of inventing a vague middle camp. The auditor produces inference-link audits, but must not recommend the proposition's outcome, submit forecasts or a resolution candidate, or vote. Do not add an auditor when the existing camps can expose the methodological dispute themselves.

Use this exact audit format after Evidence Links are first proposed and after a material link changes:

```text
METHODOLOGY_AUDIT:
LINK: <Evidence ID> -> <Claim ID>
OBSERVED: <what the card directly measured>
INFERENCE: <the step being claimed>
DOES_NOT_ESTABLISH: <missing causal or generalization link>
RATING_CORRECTION: <dimension old -> new, or NONE>
```

## Evidence Cards

In shared-evidence mode, convert each material source into an Evidence Card before the debate. Give every advocate and auditor the same cards. Each card contains:

- a stable evidence ID and short title;
- source and source URL when available;
- study type, population, and compared conditions;
- the main finding actually measured;
- limitations;
- causal strength: `high`, `medium`, `low`, or `not-assessed`;
- generalizability: `high`, `medium`, `low`, or `not-assessed`.

Evidence Cards distinguish what a source observed from what a camp infers. A citation alone is not an Evidence Card. Do not silently upgrade a card's causal strength or generalizability during the debate.

Connect evidence to Claims with a structured link rather than counting citations:

```text
EVIDENCE_LINK: <Evidence ID> -> <Claim ID>
SUPPORTS: <the exact inference licensed>
DOES_NOT_ESTABLISH: <the tempting stronger conclusion not licensed>
DIRECTNESS: high | medium | low | not-assessed
INDEPENDENCE: high | medium | low | not-assessed
CAUSAL_STRENGTH: high | medium | low | not-assessed
GENERALIZABILITY: high | medium | low | not-assessed
TEMPORAL_RELEVANCE: high | medium | low | not-assessed
```

These dimensions describe the Evidence-to-Claim relationship, not the source in isolation. Do not collapse them into one score or infer truth by adding link counts.

## Claim Ledger

The controller keeps the chronological Claim Ledger and assigns stable IDs such as `C1` when it commits an `ADD` action. Store the exact atomic claim, its type, linked Evidence Card IDs, falsifier or revision condition, and procedural status.

Claim types:

- `fact`: a packet-supported observation;
- `inference`: a conclusion drawn from facts;
- `definition`: a disputed meaning or comparison boundary;
- `value`: a priority or normative judgment;
- `prediction`: an empirical expectation not yet observed.

Statuses:

- `proposed`: introduced but not yet answered;
- `agreed`: every voting advocate explicitly accepted the same scoped claim;
- `disputed`: at least one voting advocate gave a relevant objection;
- `unsupported`: no cited card supports an empirical claim and every voting advocate accepts that ledger classification;
- `definitional_dispute`: the disagreement turns on meaning or scope;
- `superseded`: every voting advocate accepts a narrower or corrected replacement.

The controller may split a submitted compound statement into atomic claims and assign IDs, but must preserve its wording and source statement. It may not merge paraphrases, mark a claim `agreed`, `unsupported`, or `superseded`, or change scope without committed participant signals. Do not reopen an `agreed` claim unless a participant adds new evidence, identifies a scope mismatch, or challenges the recorded wording.

Every substantive statement ends with one or more ledger actions:

```text
LEDGER_ACTIONS:
- ADD: <one atomic claim> | TYPE: <type> | EVIDENCE: <IDs or NONE> | FALSIFIER: <observable weakening condition>
- ACCEPT: <claim ID>
- CHALLENGE: <claim ID> | <specific reason>
- REFINE: <claim ID> | <narrower replacement>
- CONCEDE: <claim ID>
- UNSUPPORTED: <empirical claim ID>
- DEFINITIONAL_DISPUTE: <claim ID> | <meaning or scope defect>
- SUPERSEDE: <claim ID> | REPLACEMENT: <existing claim ID>
- QUESTION: <question ID> | <claim ID> | <one answerable question>
- ANSWER: <question ID> | <direct answer>
```

For an empirical `fact`, `inference`, or `prediction`, `FALSIFIER` names an observation that would materially weaken or withdraw it. For a `definition` or `value`, use `REVISION_CONDITION` instead. `NONE` is invalid for a material Claim unless the statement is explicitly not empirically falsifiable and gives its decision criterion.

A turn has a **new ledger action** when it adds a claim, changes a participant's recorded relation to a claim, answers an open question, links previously unused evidence, or narrows a disputed claim. Rephrasing an existing position is not new. If a required turn has no new ledger action, the controller commits it as no change; the parent may use the skill's one-shorter-`CORRECT` intervention before accepting a repeated no-change speech, but `CORRECT` is not a participant-owned state transition.

## Debate phases

Use these phases in order. Prefix a statement with `<CAMP> <PHASE>`. Configure this `PHASE_SPEAKERS` map with canonical participant IDs when creating the controller:

- `OPENING: advocates, then auditor` when one is present;
- `CROSS_EXAM: advocates only`;
- `RESPONSE: advocates, then auditor` when one is present;
- `UPDATE: advocates only`;
- `CRUCIAL_DISPUTE: advocates only`; after a material Evidence Link is added or changed, the controller declares one separate `METHODOLOGY_AUDIT` turn eligible.

Every phase has its own ordered speaker list and phase-specific successor mapping. The controller declares exactly one next substantive speaker and action after each committed substantive turn; a participant cannot speak merely because it received a message. The controller moves a phase only after every required action is committed. The parent sends the controller-provided state packet, exact response template, speaker list, and successor instruction, but never implements a peer ring itself. When an auditor is used, the controller schedules it after `OPENING` and `RESPONSE`, plus one `METHODOLOGY_AUDIT` when a crucial-dispute Evidence Link materially changes.

### `OPENING`

Each advocate presents an affirmative case for its own operative conclusion:

```text
POSITIVE_CASE: <best positive case>
BURDEN_OF_PROOF: <what this camp must establish>
KEY_EVIDENCE: <Evidence Card IDs or NONE>
UNCERTAINTY: <condition that would materially weaken the case>
LEDGER_ACTIONS:
- ADD: <claim> | TYPE: <type> | EVIDENCE: <IDs or NONE> | FALSIFIER: <condition>
```

An auditor, when present, speaks after all openings and records only measurement, causal, and generalization constraints.

### `CROSS_EXAM`

Each advocate asks one difficult question of one fixed opposing advocate. The question must target one disputed Claim Ledger entry or one missing link in the target's burden. Do not restate the asking camp's opening. Assign targets so every advocate receives one question when possible; for more than two advocates, use a deterministic ring.

```text
QUESTION_ID: <camp>-Q1
TARGET: <camp>
CLAIM: <claim ID>
QUESTION: <one answerable question>
LEDGER_ACTIONS:
- QUESTION: <question ID> | <claim ID> | <one answerable question>
```

### `RESPONSE`

Each target answers its assigned question before offering rebuttal. Topic changes do not count as answers.

```text
QUESTION_ID: <question ID>
DIRECT_ANSWER: <answer, including yes/no when applicable>
POSITIVE_CASE: <how the camp's own burden still stands>
REBUTTAL: <strongest relevant response>
UNCERTAINTY: <remaining weakness>
LEDGER_ACTIONS:
...
```

The auditor then identifies only unsupported causal jumps, construct mismatches, or generalization gaps exposed by the answers.

### `UPDATE`

Each advocate performs one forced steelman and one explicit update:

```text
STEELMAN_TARGET: <camp and claim ID>
STEELMAN: <the strongest version of that opposing claim>
CONCESSION: <one point accepted, or NONE with a reason>
FORECAST_UPDATE: SUBMITTED_PRIVATELY | NOT_APPLICABLE
CRUCIAL_NOMINATION: <one unresolved claim ID>
REQUEST_RESOLUTION: YES | NO
LEDGER_ACTIONS:
...
```

After every advocate completes `UPDATE`, the controller opens the bounded `STEELMAN_CONFIRMATION` subphase. It declares the target confirmation action eligible only after committing the corresponding `UPDATE` and steelman. The parent forwards that steelman unchanged; the target submits `STEELMAN_ACCEPTED` or `STEELMAN_REJECTED: <specific defect>` as a structured action. This procedural subphase is not a peer ring and may not add substantive Claims. On rejection, the controller permits one correction by the steelman author, then permits the target's final check. A rejected steelman may not be used as the basis of a later rebuttal.

The controller collects every confirmation before resolution or the first `CRUCIAL_DISPUTE` cycle. It holds `REQUEST_RESOLUTION` signals pending until all steelmans are accepted or have exhausted the one correction. A still-rejected steelman blocks direct resolution from that `UPDATE` checkpoint and is recorded as an unresolved procedural defect; continue to `CRUCIAL_DISPUTE` while a valid material action remains, unless a required participant is unavailable or an emergency safeguard fires.

Legacy numerical belief updates are participant self-assessments, not independent evidence. New `FORECAST` debates use the private checkpoint protocol below. Do not force movement toward 0.5; no change is valid when accompanied by a reason.

`REQUEST_RESOLUTION: YES` is a procedural signal, not a concession. The controller transitions directly to resolution when every voting advocate commits `REQUEST_RESOLUTION: YES` in the same valid checkpoint after `RESPONSE`; it does not wait for `CRUCIAL_DISPUTE_READY`. Mixed or stale requests do not carry into a later checkpoint.

### `CRUCIAL_DISPUTE`

Select only one unresolved Claim Ledger entry: the claim with the most advocate nominations, breaking ties by claim ID. This selection rule orders attention; it is not a vote on truth.

Each advocate gets one concise turn limited to that claim:

```text
CLAIM: <one selected unresolved Claim ID>
POSITION: <one concise state-changing argument>
FORECAST_UPDATE: SUBMITTED_PRIVATELY | NOT_APPLICABLE
FORECAST_PROBABILITY: <current 0..1 value | NOT_APPLICABLE>
FORECAST_PROBABILITY_SHIFT: <signed change from preceding checkpoint | NOT_APPLICABLE>
REQUEST_RESOLUTION: YES | NO
LEDGER_ACTIONS:
- <ADD | ACCEPT | CHALLENGE | REFINE | CONCEDE | NO_NEW_ACTION>
```

It must add a new ledger action or explicitly state `NO_NEW_ACTION`. For a submitted forecast update, map the two numeric fields to controller payload keys `forecast_probability` and `forecast_probability_shift`; probability uses 0..1 units. A shift without its resulting probability is invalid. After the cycle, the controller publishes the revised ledger and collects the private forecast checkpoint. There is no normal three- or six-cycle completion rule. Move to resolution or deadlock classification when:

- all voting advocates send `REQUEST_RESOLUTION: YES` in the same phase checkpoint; or
- two consecutive low-information cycles occur; or
- the Claim Ledger and required confirmations establish an agreed operative conclusion; or
- the remaining disagreement is a genuine incompatible value, definition, or policy conflict and no participant identifies a concrete next falsifier, Evidence Link, refinement, or answer that could change it.

Continue when a cycle produces material progress, regardless of a nominal cycle count. Do not continue merely to fill a round count. On an emergency ceiling, freeze the last valid committed state; classify it as `TRUE_DEADLOCK` only when the committed state proves an incompatible conflict, otherwise `INCOMPLETE`.

## Private forecast checkpoints and information gain

For `FORECAST`, every voting advocate sends only the parent:

```text
FORECAST_RECORD
ASSIGNED_POSITION: <camp's fixed advocacy conclusion>
CHECKPOINT: PRIOR | AFTER_CROSS_EXAM | AFTER_CRUCIAL_DISPUTE | FINAL
CYCLE: <positive integer for AFTER_CRUCIAL_DISPUTE, otherwise NOT_APPLICABLE>
PROBABILITY: <0 to 1>
CONFIDENCE_INTERVAL: <lower to upper, both 0 to 1>
RATIONALE: <what changed or why there was no change, with Claim IDs>
```

Collect `PRIOR` before `OPENING`, `AFTER_CROSS_EXAM` after every `RESPONSE` is valid, `AFTER_CRUCIAL_DISPUTE` after each crucial cycle, and `FINAL` after debate closes but before resolution candidates. Withhold a checkpoint's records from all peers until every required advocate submits. Do not feed the numeric values back into the debate; reveal them only in the final artifact. An advocate may maintain its `ASSIGNED_POSITION` while reporting a probability below that position's decision threshold.

These records are same-model, role-conditioned participant forecasts. They are not calibrated, statistically independent, or votes. Calibration is a longitudinal property: only a later resolved outcome from `RESOLUTION_SOURCE` permits scoring such as a Brier score across a series of forecasts.

A crucial cycle is low-information only when all are true:

- it adds no new unresolved Claim, falsifier/revision condition, or Evidence Link;
- it changes no ledger status, answer, refinement, concession, or link rating; and
- for `FORECAST`, every advocate's absolute probability shift from its preceding checkpoint is less than 3 percentage points.

After two consecutive low-information cycles, the controller asks each voting advocate for a concrete next falsifier, Evidence Link, refinement, or answer. If none can identify one, proceed to resolution/deadlock classification; otherwise continue. Continue whenever a cycle produces at least one new unresolved Claim, new falsifier, new or corrected Evidence Link, or a changed resulting probability paired with an absolute forecast shift of at least 5 percentage points. The controller deduplicates by participant and resulting probability, so equal signed shifts can still be material when they reach distinct probabilities, while repeating the same forecast is not. A shift between 3 and 5 percentage points is neither an early-stop signal nor by itself an extension signal. Missing required forecasts prevent information-gain early stopping and require the controller to keep the dispute open or classify required-participation failure; they do not create normal deadline-driven completion.

## Non-voting synthesis and resolution

Every voting advocate privately submits the structured `RESOLUTION_CANDIDATE` action declared eligible by the controller. The auditor does not submit or vote.

The controller records and validates **non-voting synthesis** input. This is a traceable comparison, not a new argument:

1. Split each candidate field into atomic propositions without changing meaning.
2. Build a source map from every atom to candidate IDs and Claim Ledger IDs.
3. Mark atoms present in every candidate as the proposed common core.
4. Keep compatible but non-universal atoms as reservations.
5. Keep incompatible operative decisions as conflicts. Never average or choose between them.
6. Submit `COMMON_CORE_CHECK` containing the proposed core, reservations, conflicts, and source map; after validation, the controller declares each voting advocate's confirmation action eligible.

Each advocate returns one of:

```text
ACCEPT_COMMON_CORE
ACCEPT_WITH_RESERVATION: <existing reservation ID>
REJECT_COMMON_CORE: <atom ID and semantic mismatch>
ACCEPT_WINNER <CAMP>
REJECT_WINNER: <winner atom ID and semantic mismatch>
```

Use `ACCEPT_WINNER <CAMP>` or `REJECT_WINNER` instead of the common-core responses when any candidate proposes `OUTCOME: WINNER`. The `COMMON_CORE_CHECK` must include the proposed `WINNER` field and its candidate source map. A winner is valid only when every voting advocate returns the same `ACCEPT_WINNER <CAMP>` response.

Allow one correction when a rejection identifies a transcription, scope, or source-map error. Do not use the correction round to introduce a new substantive argument.

Classify the result:

- `FINAL_CONSENSUS`: every advocate accepts the same operative decision and complete material resolution.
- `CONSENSUS_WITH_RESERVATIONS`: every advocate accepts the same operative decision and common core, while compatible unresolved reservations remain.
- `FINAL_WINNER`: every advocate returns the same `ACCEPT_WINNER <CAMP>` for the mapped winner atom.
- `TRUE_DEADLOCK`: candidates contain incompatible operative decisions, or at least one advocate rejects the corrected common core for a material semantic reason.
- `INCOMPLETE`: a required advocate response is unavailable, cancelled, or missing when an emergency safeguard ends the debate.

Do not use majority vote. A 2-to-1 split among same-model agents is not evidence. A majority count may be reported only if the user explicitly requested it, and it does not replace the terminal classification above.

## What would resolve this?

After the terminal classification, create a traceable acquisition list:

```text
WHAT_WOULD_RESOLVE_THIS:
- NEEDED_EVIDENCE: <observable data or study>
  RESOLVES_CLAIMS: <Claim IDs>
  EXPECTED_UPDATE: <which result would strengthen, weaken, or falsify which Claim>
  COLLECTION: <feasible source or measurement design>
```

Derive each item from an unresolved Claim's `FALSIFIER`, a `DOES_NOT_ESTABLISH` gap, or a low/unknown link dimension. Do not add generic research wishes. When no feasible observation could distinguish the live positions, state that the remaining dispute is definitional or value-based rather than fabricating needed evidence.

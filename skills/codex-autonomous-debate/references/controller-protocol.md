# Deterministic controller protocol

Use `scripts/debate_controller.py` as the procedural source of truth for every live debate. The controller validates structured state transitions; it does not parse argument prose, call agents, select camps, evaluate evidence, or decide which substantive position is correct.

## Durable state

Create one controller JSON state file outside the user's source repository. The state is self-contained and resumable: do not reconstruct phase, speaker, Claim IDs, questions, steelmans, candidates, or terminal status from the transcript.

Initialize it from a participants JSON array:

```text
python <skill-dir>/scripts/debate_controller.py init --state <state.json> --debate-id <stable-id> --participants <participants.json>
```

Participants contain `id` and `role`, where role is `advocate` or `auditor`. The controller accepts two to four advocates and at most one auditor. It canonicalizes `OPENING` and `RESPONSE` as advocates followed by the auditor; the other substantive phases contain advocates only.

The default `event_limit` is 10000 and `time_limit_seconds` is disabled. Override them only when the task needs a different emergency safety envelope. They are not ordinary debate targets.

## Structured action envelope

For every participant or parent response, preserve the verbatim message separately, convert only its explicit protocol fields into this structured action envelope, and submit it before delivering another turn:

```json
{
  "debate_id": "stable debate ID",
  "event_id": "stable delivery ID",
  "actor": "participant ID or __parent__",
  "action_type": "TURN",
  "phase": "OPENING",
  "payload": {}
}
```

Write the envelope to a temporary JSON file and submit it atomically:

```text
python <skill-dir>/scripts/debate_controller.py submit --state <state.json> --action <action.json>
```

The decision returns `accepted`, committed `sequence` when applicable, `phase`, `cycle`, controller-returned `next_actor` and `next_action`, and any `terminal_status` or rejection `reason`. Do not advance a phase, speaker, Claim ID, or terminal state manually. Deliver a follow-up only to the returned next actor and only for the returned action. A rejected action changes no procedural state; request one corrected envelope when the rejection is correctable.

Use the same `event_id` and byte-equivalent structured content when retrying an ambiguous delivery. An exact retry returns the original decision and records `duplicate_delivery` only in the audit log; it does not commit a second turn. Reusing the ID with different content returns `conflicting_event_id`. Never invent a fresh event ID merely to force a rejected or ambiguous action through.

## Action payloads

Substantive phase actions use `TURN` and may include opaque/verbatim text outside the controller state plus these procedural fields:

- `ledger_actions`: `ADD`, `ACCEPT`, `CHALLENGE`, `REFINE`, `CONCEDE`, `UNSUPPORTED`, `DEFINITIONAL_DISPUTE`, `SUPERSEDE`, `QUESTION`, `ANSWER`, or `NO_NEW_ACTION`. `SUPERSEDE` names an existing `replacement_claim_id`. The controller assigns Claim IDs and derives status from committed participant relations; participants cannot set status directly.
- `questions`: exactly one structured question in `CROSS_EXAM`, including `id`, opposing `target`, existing `claim_id`, and `text`.
- `answers`: required question IDs in `RESPONSE`; optional `direct_answer` or `response_text` is stored as data, not judged for quality.
- `steelman_target` and `steelman`: required for each advocate in `UPDATE`.
- `request_resolution`: explicit boolean for the current `UPDATE` or `CRUCIAL_DISPUTE` checkpoint.
- `evidence_links`: structured Evidence Link updates. Every referenced Claim must already exist or be added earlier in the same accepted action.
- `operative_conclusion` plus `conclusion_agreed`: an explicit participant signal; the controller never infers semantic agreement from prose.
- `material_progress` is descriptive only and cannot extend a cycle by itself. A concrete ledger action, Evidence Link, new `next_falsifier`, new `next_refinement`, new `answer`, or a changed `forecast_probability` paired with an absolute `forecast_probability_shift` of at least `0.05` must identify the state change or next test. Repeating the same marker does not count again. Do not combine one of these with `no_material_change`.

After all `UPDATE` actions, use the exact `next_action` returned by the controller:

- `STEELMAN_CONFIRM` by the named target with `{ "accepted": true | false }`;
- `STEELMAN_CORRECTION` by the author with corrected `steelman` text when requested.

The controller rejects premature confirmation, wrong targets, and a second correction. A rejected steelman blocks direct resolution from the `UPDATE` checkpoint.

When a new Evidence Link is committed in `CRUCIAL_DISPUTE` and an auditor exists, the controller completes the current advocate cycle, returns `phase` and `next_action` as `METHODOLOGY_AUDIT`, and names only that auditor as `next_actor`. Submit the auditor's structured assessment with action type `METHODOLOGY_AUDIT`; the controller then performs the already-determined transition to the next crucial cycle or resolution. Participants cannot insert, skip, or reorder this audit.

At `RESOLUTION_CANDIDATE`, submit the documented candidate fields with action type `RESOLUTION_CANDIDATE`. Candidate outcome must be `CONSENSUS`, `CONSENSUS_WITH_RESERVATIONS`, `WINNER`, or `DEADLOCK`; a winner must name an advocate. At `COMMON_CORE_CONFIRMATION`, submit `COMMON_CORE_CONFIRM` with one documented common-core or winner response. The controller validates response kind against the candidates and emits a terminal status only after every required advocate response is committed.

When the first confirmation round identifies a transcription, scope, or source-map error, the controller returns `next_actor: __parent__` and `next_action: COMMON_CORE_CORRECTION`. Submit exactly the rejected common `atom_ids` and `reclassify_as: reservations | conflicts`. The controller only moves those source-mapped atoms; it cannot change their text or provenance or substitute an unrelated atom. Invalid or no-op corrections do not consume the sole retry, and every advocate must reconfirm the corrected mapping.

The parent may submit `CANCEL`, `FAILURE`, `SAFETY_CEILING`, or an eligible `COMMON_CORE_CORRECTION` as actor `__parent__`. These are control actions, not substantive arguments.

## Conclusion-driven completion

There is no nominal three- or six-cycle completion limit. A materially progressing `CRUCIAL_DISPUTE` may continue beyond six cycles. Normal progression moves to resolution only when controller state proves one of these:

1. every advocate requested resolution at the same valid checkpoint;
2. every advocate explicitly recorded the same operative conclusion;
3. two consecutive low-information cycles contain no material state change and no concrete next falsifier, Evidence Link, refinement, or answer.

Continue after new or corrected Claims, falsifiers, Evidence Links, answers, refinements, concessions, or material forecast movement. A participant cannot keep the debate alive by merely asserting that progress occurred; the structured payload must identify the state change or next test.

The configurable event/time ceiling is emergency safety, not an ordinary completion target. When it fires, the controller freezes the last accepted sequence. It may emit `TRUE_DEADLOCK` only when formal deadlock evidence is already committed; otherwise it emits `INCOMPLETE`. Emergency safety cannot fabricate consensus or a winner.

## Resume and audit

The state file contains accepted events, rejected receipts, phase position, and all procedural collections. Resume it with `DebateController.from_json` or another `submit` CLI call; do not replay transcript prose.

For renderer-safe metadata:

```text
python <skill-dir>/scripts/debate_controller.py show --state <state.json> --artifact
```

This calls `artifact_metadata()` and redacts resolution-candidate participants to `anonymous`. Add the result as top-level `controller` in the final artifact JSON only after a controller terminal state exists. Never use `--include-private` for a user-facing artifact. The renderer validates contiguous committed sequence IDs, rejected-event metadata, terminal-state consistency, and recursively checks candidate payloads for private provenance before showing the collapsed protocol audit.

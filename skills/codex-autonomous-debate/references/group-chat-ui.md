# Group chat artifact

Use this format only after a debate reaches a terminal state. The renderer is deterministic, uses only the Python standard library, escapes all participant-controlled text, and produces one self-contained HTML file with no automatic external network requests.

## Input document

Write UTF-8 JSON with this shape. v3 fields (`proposition_type`, `decision_rule`, `forecast_records`, Claim `falsifier`, `evidence_links`, and `needed_evidence`), optional v4 `controller` audit metadata, and the earlier structured fields remain optional for backward compatibility. When `proposition_type` is present, `decision_rule` is required; `FORECAST` also requires a probability `threshold`. New resolution messages use `resolution_stage` to distinguish anonymous procedure from attributed public statements.

```json
{
  "lang": "ja | en",
  "title": "Short debate title",
  "proposition": "The exact proposition",
  "proposition_type": "FORECAST | CAUSAL | FACTUAL | POLICY",
  "decision_rule": {
    "target": "Observable target event or decision object",
    "horizon": "Resolution date or NOT_APPLICABLE with reason",
    "yes_condition": "Exact YES/action rule",
    "no_condition": "Exact NO/alternative rule",
    "resolution_source": "Source that can settle the target",
    "threshold": 0.5
  },
  "debate_progress": {
    "completed_phases": ["OPENING", "CROSS_EXAM", "RESPONSE", "UPDATE"],
    "completed_crucial_cycles": 1
  },
  "status": "FINAL_CONSENSUS | CONSENSUS_WITH_RESERVATIONS | FINAL_WINNER | TRUE_DEADLOCK | INCOMPLETE",
  "evidence_mode": "closed-book | shared-evidence",
  "camps": [
    {"id": "affirmative", "name": "Affirmative", "role": "advocate"},
    {"id": "negative", "name": "Negative", "role": "advocate"},
    {"id": "methods", "name": "Methodological auditor", "role": "auditor"}
  ],
  "evidence_cards": [
    {
      "id": "F2",
      "title": "Short evidence title",
      "source": "Source name",
      "source_url": "https://example.com/primary-source",
      "study_type": "RCT",
      "population": "Observed population",
      "conditions": "Compared conditions",
      "main_finding": "What the source directly measured",
      "limitations": ["Material limitation"],
      "causal_strength": "high | medium | low | not-assessed",
      "generalizability": "high | medium | low | not-assessed"
    }
  ],
  "claim_ledger": [
    {
      "id": "C1",
      "text": "One atomic claim",
      "type": "fact | inference | definition | value | prediction",
      "status": "proposed | agreed | disputed | unsupported | definitional_dispute | superseded",
      "evidence": ["F2"],
      "introduced_by": "affirmative",
      "falsifier": "Observable result that would materially weaken the Claim"
    }
  ],
  "belief_updates": [
    {
      "camp": "affirmative",
      "phase": "UPDATE",
      "before": 0.78,
      "after": 0.66,
      "reason": "The strongest reason for the participant's self-reported change"
    }
  ],
  "forecast_records": [
    {
      "camp": "affirmative",
      "checkpoint": "PRIOR | AFTER_CROSS_EXAM | AFTER_CRUCIAL_DISPUTE | FINAL",
      "cycle": 1,
      "probability": 0.62,
      "lower": 0.45,
      "upper": 0.76,
      "rationale": "Private participant forecast rationale with Claim IDs"
    }
  ],
  "evidence_links": [
    {
      "claim_id": "C1",
      "evidence_id": "F2",
      "supports": "The exact inference licensed by the card",
      "does_not_establish": "A stronger inference the card does not license",
      "directness": "high | medium | low | not-assessed",
      "independence": "high | medium | low | not-assessed",
      "causal_strength": "high | medium | low | not-assessed",
      "generalizability": "high | medium | low | not-assessed",
      "temporal_relevance": "high | medium | low | not-assessed"
    }
  ],
  "needed_evidence": [
    {
      "id": "N1",
      "observation": "Observable data or study that discriminates the live Claims",
      "resolves_claims": ["C1"],
      "expected_update": "Which result strengthens, weakens, or falsifies the Claim",
      "collection": "Feasible source or measurement design"
    }
  ],
  "controller": {
    "schema_version": 1,
    "debate_id": "stable-debate-id",
    "phase": "COMMON_CORE_CONFIRMATION",
    "cycle": 2,
    "accepted_sequence": 12,
    "next_actor": null,
    "next_action": null,
    "terminal_status": "TRUE_DEADLOCK",
    "emergency_safety": {"event_limit": 10000, "time_limit_seconds": null},
    "events": [
      {
        "event_id": "stable-event-id",
        "sequence": 1,
        "phase": "OPENING",
        "cycle": 0,
        "participant": "affirmative",
        "observed_at": "2026-09-03T00:00:00Z",
        "committed_at": "2026-09-03T00:00:00Z",
        "action_type": "TURN",
        "accepted": true,
        "rejection_reason": null,
        "payload": {}
      }
    ]
  },
  "messages": [
    {
      "kind": "argument | resolution",
      "camp": "stable-lowercase-id",
      "phase": "OPENING | CROSS_EXAM | RESPONSE | UPDATE | CRUCIAL_DISPUTE",
      "round": 1,
      "text": "Verbatim valid statement captured when the parent received it",
      "timestamp": "Optional display timestamp"
    },
    {
      "kind": "system | intervention | resolution",
      "resolution_stage": "candidate | confirmation | public-statement",
      "speaker": "Supervisor or anonymous candidate ID",
      "text": "Observed procedural event or anonymous resolution text",
      "timestamp": "Optional display timestamp"
    }
  ],
  "summary": {
    "decision": "The valid terminal decision without embellishment",
    "agreed_points": ["Only points accepted by the resolution procedure"],
    "unresolved_objections": ["The strongest reservation or conflict"]
  }
}
```

`lang` accepts `ja` or `en` and defaults to `en`. Camp IDs use `^[a-z0-9][a-z0-9_-]{0,31}$`. Evidence and Claim IDs use letters, digits, dots, hyphens, or underscores. Use two to four advocates and at most one optional auditor. A missing participant `role` defaults to `advocate`.

The renderer accepts legacy `DEADLOCK` artifacts in addition to the current terminal statuses so previously generated transcripts remain readable. New debates should emit `TRUE_DEADLOCK` when the operative decisions are genuinely incompatible.

`controller` is optional so all earlier artifacts remain valid. For new controller-driven debates, populate it only after termination with `debate_controller.py show --artifact` or `artifact_metadata()` output. Its non-null `terminal_status` must equal the artifact status. Accepted event sequences must be contiguous from 1 through `accepted_sequence`; rejected delivery attempts have no sequence or commit time and retain a rejection reason. Candidate-submission events must use participant `anonymous`. Never place private candidate provenance at any nesting depth in a user-facing artifact. The HTML renders this data in a collapsed protocol-audit panel rather than mixing transport metadata into the discussion.

`argument` messages require a known camp. Every `resolution` message in a state-driven artifact with `proposition_type` must set `resolution_stage`. A `candidate` or `confirmation` must omit `camp` and provide a neutral `speaker` such as `Candidate A` or `Common-core check`; the renderer rejects camp identity on these anonymous stages. A `public-statement` must name its `camp`. Legacy artifacts without `proposition_type` may omit `resolution_stage` so old files remain readable. `system` and `intervention` messages do not require a camp. `phase` is preferred for state-driven debates; legacy `round` remains supported.

Evidence Cards are structured descriptions, not proof that a source is correct. Preserve the distinction between the directly measured `main_finding`, its `limitations`, causal strength, and generalizability. Only `http` and `https` source links are accepted. A Claim Ledger entry may reference only Evidence Card IDs present in the same document. Legacy belief values are participant self-assessments between `0` and `1`, not independent evidence or calibrated forecasts.

Forecast records are allowed only for `FORECAST` artifacts. `cycle` is required only for `AFTER_CRUCIAL_DISPUTE`, where it distinguishes repeated adaptive cycles. Each `(camp, checkpoint, cycle)` tuple must be unique, and `lower <= probability <= upper`. Record fully completed work in `debate_progress`: `completed_phases` must be an ordered prefix of `OPENING`, `CROSS_EXAM`, `RESPONSE`, `UPDATE`, and `completed_crucial_cycles` counts fully completed adaptive cycles. Every terminal `FORECAST` artifact except `INCOMPLETE` must include `PRIOR` and `FINAL` for every advocate, `AFTER_CROSS_EXAM` when `RESPONSE` completed, and one record from every advocate for every completed crucial cycle. `INCOMPLETE` may omit checkpoints for phases that never completed after a failure or emergency safeguard. If `debate_progress` is absent, the renderer preserves the stricter legacy v3 behavior and requires `AFTER_CROSS_EXAM` plus every observed crucial-cycle checkpoint. `INCOMPLETE` artifacts may retain partial records so failure evidence remains renderable. These values are role-conditioned participant forecasts, not independent samples, votes, or calibrated probabilities. Display them as trajectories; do not average them. Calibration requires later outcome settlement against `decision_rule.resolution_source`, normally across multiple forecasts.

An Evidence Link references one existing Evidence Card and one existing Claim. Its dimensions rate that relationship rather than the source globally. Do not combine the dimensions into an undocumented score. `needed_evidence` must reference existing Claim IDs and should be traceable to a falsifier or `does_not_establish` gap.

Preserve parent-observed chronological message order. Append each valid public statement, steelman confirmation, anonymous resolution candidate, common-core check, and confirmation to `messages` as a verbatim copy at receipt time. `messages[].text` is the lossless transcript, not a synopsis: never summarize or reconstruct it later from the Claim Ledger, phase state, resolution, or terminal report. Include material phase and ledger transitions, interventions, timeouts, and failures. Exclude readiness handshakes and routine delivery bookkeeping unless they affected validity. Never add dialogue merely to make the interface look conversational.

Keep `phase` and `round` in JSON when they carry protocol meaning. In a state-driven artifact, do not show them as status text in the participant bubble header; the chronological transcript already supplies the reading order. A timestamp may still appear when one was recorded. Legacy artifacts may retain their phase and round display.

For structured protocol messages, the default HTML body is a renderer-derived natural-language view. Translate field labels into the artifact language—for example, Japanese `POSITIVE_CASE`, `BURDEN_OF_PROOF`, `DIRECT_ANSWER`, `STEELMAN`, and `DECISION` become `主張`, `この立場が示すべきこと`, `回答`, `相手の主張を最も強く捉えると`, and `結論`. Render resolution candidates and common-core checks the same way. Collapse `LEDGER_ACTIONS` behind a secondary disclosure, and keep the exact verbatim protocol text behind a clearly labeled raw-text disclosure in the same message. Derive this view at render time; do not add a second paraphrased transcript field to JSON and do not alter `messages[].text`.

Escape every participant-controlled label and value in both the readable and raw views. The disclosures must work without JavaScript, and the generated HTML must remain self-contained with no external network requests.

## Render

```text
python <skill-dir>/scripts/render_debate_chat.py <transcript.json> --output <debate-chat.html>
```

Keep intermediate JSON and generated HTML outside a source repository unless the user requested repository artifacts. Link the HTML in the final response. If local rendering is unavailable or fails, report the failure briefly and provide the same chronological content as a Markdown transcript.

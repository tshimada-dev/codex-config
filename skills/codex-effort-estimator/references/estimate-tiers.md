# Estimate Tiers

Use this reference to choose how much estimating machinery to run before delegation. The goal is to keep small requests fast while preserving full defensibility for quote-grade or high-risk work.

Always record the selected tier and reason in the final answer and workbook synthesis.

## Tier Definitions

| Tier | Use when | Minimum passes |
|---|---|---|
| `quick` | Small internal planning estimate, low-risk feature, rough order of magnitude, or user explicitly asks for a quick estimate | Sizing when useful, WBS or task breakdown, top-down three-point sanity check, visible assumptions/risks |
| `standard` | Normal project estimate, customer-facing planning, document-driven but not high-stakes, moderate uncertainty | Sizing, WBS, component unit anchor when countable, one functional/driver anchor such as parametric/FP/UCP, top-down three-point, risk review, workbook |
| `full` | Quote/procurement support, public-sector/RFP work, high uncertainty, broad scope, significant money/time impact, or user asks for defensible multi-method estimate | All applicable passes from the coverage gate, subagent isolation when available, independent anchors, risk model, constraint capacity, public/review pass, workbook QA |

## Escalation Rules

Escalate one tier when any of these are true:

- The estimate may be used for an external quote, procurement response, or budget approval.
- The scope includes public-sector deliverables, Excel/PDF/report fidelity, acceptance comparison, or formal handoff.
- A single WBS line would dominate more than 25-30% of the total.
- Countable scope exists but WBS and top-down anchors disagree materially.
- Calendar/staffing constraints make feasibility part of the answer.
- The user explicitly asks for independent viewpoints or subagents.

De-escalate only when the user asks for speed, the scope is small, or missing source material makes full analysis performative rather than useful. If de-escalating, still record what was skipped and why.

## Output Requirement

Include a tier row in pass coverage or synthesis:

| Item | Value |
|---|---|
| Estimate tier | `quick` / `standard` / `full` |
| Tier reason | One sentence tied to source scope, audience, risk, and requested confidence |
| Skipped due to tier | Passes intentionally omitted because the selected tier does not require them |

Tiering does not override the pass coverage gate. It explains how deeply to run applicable methods and makes intentional omissions visible.

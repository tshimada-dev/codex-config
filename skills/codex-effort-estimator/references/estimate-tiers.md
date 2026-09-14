# Estimate Tiers

Choose the tier before selecting passes. Record the tier, reason, and pass status in the final result and workbook synthesis. A tier is a required-method contract, not a suggestion to run every available method.

## Required method sets

| Tier | Use when | Required set | Cap and escalation |
|---|---|---|---|
| `quick` | Small internal planning, rough order of magnitude, low-risk feature, or an explicitly quick request | Sizing when useful; a task breakdown or WBS; top-down three-point sanity anchor when whole-project classing is possible; assumptions, exclusions, risks, confidence; range synthesis for any three-point data | Do not require component, parametric, FP, UCP, capacity, risk-model, analogy, public-review, repo, or discovery passes unless the user asks or the work must escalate. Parent-only execution is allowed. Report only this spine and any requested pass. |
| `standard` | Normal project planning, customer-facing planning, or moderate uncertainty | Sizing when countable; WBS for feature/project or document scope (or PERT for an already-decomposed task scope); component-unit anchor when countable; one supported functional/driver anchor (`parametric`, `FP`, or `UCP`) when its inputs are defensible; top-down three-point; constraint capacity when calendar/staffing feasibility is requested; assumptions/exclusions/risk review; range synthesis; workbook unless text-only | When no functional/driver anchor has defensible inputs, record that fact instead of inventing one. Do not add the other anchors or every specialist pass merely because they could apply. Report only this spine and selected triggered passes. Escalate if an escalation rule applies. |
| `full` | Quote/procurement support, RFP/public-sector work, broad/high-uncertainty scope, significant money/time impact, or an explicitly defensible multi-method estimate | Every applicable pass in the coverage gate below, plus range synthesis, parent synthesis, and workbook QA | A pass may be `skipped` only when its evidence-based gate reason applies. Use isolated delegation when it materially improves independent viewpoints and is available. |

## Coverage gate for `full`

For a `full` estimate, mark each pass `run`, `skipped`, or `not applicable`, with a reason:

| Pass | Run when | Skip only when |
|---|---|---|
| Sizing | Countable screens, reports, imports, exports, entities, workflows, roles, integrations, environments, or deliverables exist | The source is too small or abstract to count. |
| WBS | Scope is broad, document-driven, RFP-driven, feature, or project work | PERT or repository cost is the sole appropriate effort method and WBS would only duplicate it. |
| Component unit anchor | Countable component families exist | No meaningful component counts exist, or a measured historical analogy is the sole credible total anchor. |
| Parametric model | Measurable drivers can feed an explicit equation | Drivers or coefficients would be unreliable. |
| Function point | Inputs, outputs, inquiries, logical files, or external interface files can be counted | Functional boundaries cannot be counted or the system is not function-oriented. |
| Use case points | Actors and workflows/use cases can be counted | No bounded actor/workflow view exists. |
| Top-down three-point | A non-trivial whole-project anchor is possible | Scope is too abstract even for delivery-class reasoning. |
| Constraint capacity | Deadline, staffing, review gates, procurement cadence, or acceptance windows matter | No relevant constraint facts are available. |
| Risk model | A few uncertainty drivers materially widen the range | Probabilities and impacts cannot be stated even qualitatively. |
| PERT | Tasks are decomposed enough for independent three-point estimates | Tasks need WBS or discovery first. Still aggregate any WBS three-point rows as `WBS-derived variance aggregation`. |
| Repository cost | Rebuild, replacement, completion, or hardening of an existing codebase is in scope | No repository/codebase is in scope. |
| Discovery | Requirements or delivery constraints are too unclear for implementation sizing | Implementation scope is stable enough to estimate. |
| Analogy calibration | Credible historical actuals, estimates, or productivity baselines exist | No credible comparison exists. |
| AI coding assistance adjustment | The user explicitly assumes AI-assisted coding | That assumption was not requested. |
| Public-sector/report review | Procurement, government, Office/CSV/PDF/report fidelity, training, acceptance, formal deliverables, or handoff matters | None of these triggers are present. |

## Escalate to the next tier

Escalate when the estimate supports an external quote, procurement response, or budget approval; includes formal public-sector/report/acceptance deliverables; has a dominant WBS line above roughly 25-30% *and* that line carries material uncertainty or delivery risk; has a material disagreement between selected anchors; or the user requests independent viewpoints or subagents. A calendar/staffing feasibility request requires the standard constraint-capacity pass; escalate when its stakes or uncertainty warrant full coverage. Missing source material can justify a discovery estimate; it does not justify performative full-method coverage.

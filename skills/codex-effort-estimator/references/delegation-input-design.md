# Delegation Input Design

Use this reference when preparing subagent packets for estimation passes.

## Principle

Keep independent observation passes independent. Do not send parent interpretation summaries, preferred ranges, suspected answers, prior method results, or selected evidence highlights to an independent method pass.

Use shared facts only when they are mechanically extracted and auditable, such as `source_inventory.json`, `source_inventory.md`, file paths, document titles, page counts, table names, sheet names, OCR status, explicit dates, and verbatim counted facts. These are allowed because they can be checked against source material and do not encode the parent's judgment.

Dependent transformation passes are different. They may receive the artifact they transform, such as WBS rows for AI adjustment, or WBS/public deliverables for a coverage audit. The packet must label the artifact as an input dependency rather than an independent observation.

## Packet Classes

| Packet type | May include | Must not include |
|---|---|---|
| Independent observation | Source documents, machine inventory, method reference, unit, output schema | Parent estimate, other method totals, parent interpretation summary, target range |
| Shared fact | `source_inventory.*`, deterministic counts, source paths, extracted headings/tables | Parent-selected importance, risk interpretation, synthesis language |
| Dependent transformation | Raw artifact to transform, applicable source context, fixed rules | Freedom to retune baseline, hidden parent target, unrelated method conclusions |
| Review/audit | Source documents plus the artifact being audited when needed | Mechanical additive instructions unless the pass is explicitly additive |

## Method Input Scope

| Pass | Input scope |
|---|---|
| Sizing | Broad source set plus `source_inventory.*`; count scope signals only. |
| WBS | Requirements/RFP/design documents, deliverables, workflows, reports, integrations, constraints, and machine inventory. |
| Component unit anchor | Countable component source docs and machine inventory; no WBS totals or WBS-derived PERT. |
| Parametric model | Driver-bearing source docs, machine inventory, explicit counts, coefficient reference; no WBS totals. |
| Function point | Functional boundary docs: inputs, outputs, inquiries, logical files, external interfaces, reports. |
| Use case points | Actor, role, workflow, use-case, and scenario source docs. |
| Top-down three-point | Source docs sufficient to classify the whole delivery; no WBS line estimates or other method totals. |
| Constraint capacity | Schedule, staffing, review gates, procurement cadence, acceptance windows, and fixed deliverables. |
| Risk model | Source-visible risk drivers, constraints, uncertainty notes, and an explicitly independent base anchor when assigned. |
| PERT | Task list or WBS-like task source; if using WBS lines, label it WBS-derived variance aggregation. |
| Discovery | Ambiguous requirements, data/report investigation needs, stakeholder decision points, and prototype questions. |
| AI adjustment | Raw WBS/PERT rows with `AI削減区分`; this is a dependent transformation, not an independent method. |
| Public review | Public-sector deliverables, report/Excel/PDF fidelity, CSV/encoding, acceptance, training, handoff, and optionally the WBS being audited. |
| Repository cost | Repository path plus measured repo facts; exclude other estimate conclusions. |

## Delegate Packet Shape

Use this compact shape:

```text
Method reference: references/<pass>.md
Packet class: independent observation | dependent transformation | review/audit
Source inputs: [paths or source_inventory entries]
Shared mechanical facts: [source_inventory path or deterministic counts]
Excluded inputs: parent estimate, other method totals, preferred range, parent interpretation summary
Unit: person-days
Required output schema: [method-specific schema]
```

For dependent transformations, replace `Excluded inputs` with:

```text
Frozen baseline: [artifact path/table]
Allowed transformation rules: [reference section]
No retuning authority: do not change baseline or coefficients to hit a target total
```

# Spreadsheet Output

Use this reference when the user asks for an Excel workbook, spreadsheet, `.xlsx`, or sheet-by-sheet estimate artifact.

## Principle

Keep this skill as the estimator/orchestrator. Use the dedicated `spreadsheets` skill/workflow to build and verify the workbook. The estimate workbook should make the numbers auditable, not just prettier.

## Required Workbook Shape

For substantial estimates, create these sheets unless the user asks for a simpler file:

| Sheet | Purpose |
|---|---|
| `サマリー` or `Summary` | Final recommended range, planning center, confidence, and method comparison. |
| `工程別サマリー` or `Phase Summary` | Phase-level breakdown across methods: PM, requirements, design, implementation, reports, testing, manuals/handoff. |
| `規模根拠` or `Sizing Basis` | Source facts: function count, reports, imports, data volumes, integrations, environments, constraints. |
| Method detail sheets | One sheet per method, for example sizing, WBS bottom-up, PERT, analogy calibration, discovery, public-sector/report review, repository cost estimate. |
| `親統合` or `Synthesis` | Parent reconciliation: method differences, final range, implementation-only range, high-risk range. |
| `前提・除外・リスク` or `Assumptions Risks` | Assumptions, exclusions, risks, and confirmation questions. |

## Phase Breakdown

When users ask "what is inside the normal estimate?" or "how many days for requirements?", use the phase summary. Do not create separate method-by-phase decomposition sheets.

Default phases:

- PM/management
- Requirements/business analysis
- Basic/detailed design
- Implementation, including foundation, screens, business logic, data handling
- Reports/output, including Excel/PDF/CSV
- Testing/acceptance
- Training/manuals/delivery/handoff

A phase summary should include total-estimate method center values by phase, for example WBS likely, PERT most-likely, and parent final standard. If a specialist pass is a coverage/risk review rather than a total estimate, label it clearly as review coverage, risk range driver, or adjustment candidate.

| Column | Meaning |
|---|---|
| Phase | Work phase or delivery area. |
| WBS likely | WBS method central value. |
| PERT most likely | PERT method central value. |
| Review/adjustment candidate | Public-sector/report/repository review finding, risk driver, or non-overlapping adjustment candidate. Do not present it as a comparable total estimate unless it is actually a total estimate. |
| Parent final standard | Final parent synthesis central value. |
| Notes | Basis, assumptions, or risk driver. |

Include a total row with formulas, not hardcoded totals.

## Method Comparison

The summary should include a method comparison table:

| Method | Low | Normal/Base | High | Center/Expected | Parent interpretation |
|---|---:|---:|---:|---:|---|

For PERT, show:

- optimistic
- most likely
- pessimistic
- expected value using `(O + 4M + P) / 6`
- optional standard deviation using `(P - O) / 6`

For WBS, show:

- WBS component
- basis
- low/likely/high
- total formulas

For review or adjustment passes, separate them from total-estimate methods unless they are intentionally total estimates. Show:

- coverage findings: already covered / missing or thin / risk-only
- additive adjustment candidates only when they are non-overlapping
- adjusted low/base/high range only when the pass explicitly produced a full adjusted total

Do not place a public-sector/report review beside WBS and PERT as if all three are comparable total estimates when the review output is only an adjustment candidate.

For sizing, discovery, and analogy calibration passes, keep their roles clear:

- Sizing is evidence for scope counts, not a total estimate.
- Discovery is a separate pre-implementation effort when delivery scope is not stable.
- Analogy calibration is a validation or adjustment rationale, not an unexplained replacement for WBS/PERT.

## Workbook Quality

Before delivering:

- Verify the workbook opens through the spreadsheet tooling.
- Inspect the key summary and synthesis ranges.
- Scan for formula errors such as `#REF!`, `#VALUE!`, `#DIV/0!`, `#NAME?`, and `#N/A`.
- Render at least the summary and one detailed sheet for visual review.
- Make long text readable with sensible column widths and wrapping.
- Keep the final `.xlsx` in the project `outputs` folder or another user-visible artifact path.

## When To Split Into A Separate Skill

Keep spreadsheet guidance here while it is only about estimation workbook structure.

Create a separate skill only if the work grows into reusable spreadsheet automation beyond estimates, such as:

- generic workbook generation scripts,
- chart/dashboard templates,
- import/export macros,
- multiple estimate workbook styles,
- recurring workbook QA automation.

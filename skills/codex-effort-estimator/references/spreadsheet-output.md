# Spreadsheet Output

Use this reference for the default estimate workbook, or when the user asks for an Excel workbook, spreadsheet, `.xlsx`, or sheet-by-sheet estimate artifact.

## Principle

Keep this skill as the estimator/orchestrator. Use the dedicated `spreadsheets` skill/workflow to build and verify the workbook. The estimate workbook should make the numbers auditable, not just prettier.

Create a workbook by default for non-trivial estimates. Skip it only when the user asks for text-only output, the request is a quick gut-check, or there is not enough information to create useful tables.

Always apply `workbook-format.md`. Do not improvise sheet names, order, colors, header rows, number formats, or column structure unless the user explicitly asks for a different format.

When a local `.xlsx` file has been generated, run `scripts/format_estimate_workbook.py` as a deterministic post-processing step before delivery. Prefer writing a formatted copy first:

```powershell
python skills/codex-effort-estimator/scripts/format_estimate_workbook.py path\to\estimate.xlsx --output path\to\estimate_formatted.xlsx
```

Use `--in-place` only when overwriting the generated workbook is intentional. The script is a formatter and validator; it must not be treated as a replacement for estimating, range synthesis, or visual review.

## Required Workbook Shape

For substantial estimates, create the standard workbook shape from `workbook-format.md`. The conceptual sheet purposes are:

| Sheet | Purpose |
|---|---|
| `00_サマリー` | Final recommended range, planning center, confidence, and method comparison. |
| `01_工程別` | Phase-level breakdown across methods: PM, requirements, design, implementation, reports, testing, manuals/handoff. |
| `02_規模根拠` | Source facts: function count, reports, imports, data volumes, integrations, environments, constraints. |
| `03_WBS` | WBS bottom-up estimate lines. Keep the sheet and add an `適用なし` row if WBS was not run. |
| `04_PERT` | Independent PERT task estimates and expected values. If independent PERT was not run but WBS has three-point values, include a `WBS由来CI` block instead of ending with only `適用なし`. |
| `05_類推補正` | Historical analogy and calibration when applicable. |
| `06_Discovery` | Discovery estimate when implementation scope is unstable. |
| `07_AI補正` | AI coding assistance adjustment when explicitly assumed. |
| `08_公共レビュー` | Public-sector/report/acceptance coverage review when applicable. |
| `09_Repo` | Repository rebuild or completion estimate when applicable. |
| `10_親統合` | Parent reconciliation: pass coverage, method differences, final range, implementation-only range, high-risk range. |
| `11_前提リスク` | Assumptions, exclusions, risks, and confirmation questions. |
| `12_単価アンカー` | Independent component-unit top-down estimate when countable component families exist. |
| `13_パラメトリック` | Independent equation-based estimate from count drivers, coefficients, and adjustment factors. |
| `14_FP` | Function point estimate when inputs, outputs, inquiries, logical files, or external interface files can be counted. |
| `15_UCP` | Use case points estimate when actors and workflows/use cases can be counted. |
| `16_トップダウン` | Direct whole-project optimistic / most-likely / pessimistic anchor. |
| `17_制約` | Constraint/capacity feasibility envelope from deadline, staffing, review gates, and delivery windows. |
| `18_リスクモデル` | Risk-adjusted scenario or Monte Carlo-style model from probability/impact assumptions. |

When AI coding assistance is explicitly assumed, add either a dedicated `AI補正` / `AI Adjustment` sheet or a clearly separated table in `親統合`.

Do not renumber sheets when optional method sheets are omitted. Number gaps are intentional.

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

A phase summary should include total-estimate method center values by phase, for example WBS most likely, PERT expected, and parent final standard. If a specialist pass is a coverage/risk review rather than a total estimate, label it clearly as review coverage, risk range driver, or adjustment candidate.

| Column | Meaning |
|---|---|
| Phase | Work phase or delivery area. |
| WBS most likely | WBS method central value. |
| PERT expected | PERT expected value after variance aggregation. |
| Component anchor | Component-unit anchor central value when this independent pass ran. |
| Parametric / FP / UCP | Independent functional or driver-based central values when those passes ran. |
| Review/adjustment candidate | Public-sector/report/repository review finding, risk driver, or non-overlapping adjustment candidate. Do not present it as a comparable total estimate unless it is actually a total estimate. |
| Parent final standard | Final parent synthesis central value. |
| AI-assisted adjusted | Final adjusted central value when AI coding assistance is explicitly assumed. |
| Notes | Basis, assumptions, or risk driver. |

Include a total row with formulas, not hardcoded totals.

## Method Comparison

The summary should include a method comparison table:

| 手法 | 楽観/Low | 普通/Base | 悲観/High | 中心/期待値 | 親の解釈 |
|---|---:|---:|---:|---:|---|

The synthesis sheet must also include a pass coverage table:

| Pass | Status | Reason | Evidence |
|---|---|---|---|

Use `run`, `skipped`, or `not applicable` in English outputs. For the default Japanese workbook, use `実行`, `スキップ`, or `非該当`. Do not omit a pass silently.

The synthesis sheet must include range synthesis when any three-point data exists:

| Source | Most likely total | Expected total | Total SD | 90% CI | Endpoint scenario | Interpretation |
|---|---:|---:|---:|---|---|---|

If the source is WBS, label it `WBS-derived variance aggregation` or `WBS由来CI`, and do not present it as an independent method result.

For PERT, show:

- optimistic
- most likely
- pessimistic
- expected value using `(O + 4M + P) / 6`
- standard deviation using `(P - O) / 6`
- variance using `standard_deviation ^ 2`
- aggregate confidence interval using `sum(expected) +/- z * sqrt(sum(variance))`

Do not use `sum(optimistic)` and `sum(pessimistic)` as the normal aggregate PERT range. If you show those endpoint sums, label them as fully correlated best/worst-case scenario, not as the default confidence interval.

For WBS, show:

- WBS component
- basis
- low / most likely / high, where `likely` is the central most-likely estimate
- total formulas

For the component unit anchor pass, show:

- component family counts and count confidence
- framework low/base/high
- unit low/base/high
- reuse or complexity factor
- family low/base/high totals
- anchor source and rationale
- clear note that the pass did not use WBS totals or WBS-derived PERT

For independent anchor passes, show enough detail to audit the method:

- Parametric: model equation, drivers, coefficients, adjustment factors, and calibration confidence.
- Function point: EI/EO/EQ/ILF/EIF counts, complexity weights, productivity conversion, and boundary ambiguity.
- Use case points: actor/use-case weights, TCF/ECF, productivity conversion, and actor/workflow ambiguity.
- Top-down three-point: delivery class, dominant drivers, optimistic/most-likely/pessimistic totals, expected value, and SD.
- Constraint capacity: staffing scenarios, workdays, focus factor, review buffers, feasible capacity, and schedule implication.
- Risk model: independent base anchor, risk register, probability/impact, correlation groups, expected exposure, and P50/P80/P90 or scenario bands.

For review or adjustment passes, separate them from total-estimate methods unless they are intentionally total estimates. Show:

- coverage findings: already covered / missing or thin / risk-only
- additive adjustment candidates only when they are non-overlapping
- adjusted low/base/high range only when the pass explicitly produced a full adjusted total

Do not place a public-sector/report review beside WBS and PERT as if all three are comparable total estimates when the review output is only an adjustment candidate.

For sizing, discovery, and analogy calibration passes, keep their roles clear:

- Sizing is evidence for scope counts, not a total estimate.
- Component unit anchor is a total-estimate method from counts and unit anchors; keep it separate from WBS and do not tune it to match WBS.
- Parametric, function point, use case point, top-down three-point, constraint capacity, and risk model passes are independent viewpoints when run. Do not collapse them into WBS-derived notes.
- Discovery is a separate pre-implementation effort when delivery scope is not stable.
- Analogy calibration is a validation or adjustment rationale, not an unexplained replacement for WBS/PERT.
- AI coding assistance adjustment is a phase-specific adjustment from baseline to assisted effort, not a new independent size estimate.

For AI coding assistance adjustment, show:

- raw baseline low/base/high
- phase multipliers
- adjusted low/base/high
- non-reducible work
- assumptions and confidence

## Workbook Quality

Before delivering:

- Verify the workbook opens through the spreadsheet tooling.
- Run `scripts/format_estimate_workbook.py` on the generated `.xlsx` when local Python and `openpyxl` are available.
- Verify sheet names and order match `workbook-format.md`.
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

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
| `00_結論` | Final recommended range, planning center, confidence, concise rationale, and method comparison table. |
| `01_内訳` | Readable phase breakdown: AI-assisted effort, WBS baseline, delta, reducibility judgment, and reference sheet. |
| `02_規模根拠` | Source facts: function count, reports, imports, data volumes, integrations, environments, constraints. |
| `03_WBS` | WBS bottom-up estimate lines. Keep the sheet and add an `適用なし` row if WBS was not run. |
| `04_PERT` | Independent PERT task estimates and expected values. If independent PERT was not run but WBS has three-point values, include a `WBS由来CI` block instead of ending with only `適用なし`. |
| `05_単価アンカー` | Independent component-unit top-down estimate when countable component families exist. |
| `06_パラメトリック` | Independent equation-based estimate from count drivers, coefficients, and adjustment factors. |
| `07_FP` | Function point estimate when inputs, outputs, inquiries, logical files, or external interface files can be counted. |
| `08_UCP` | Use case points estimate when actors and workflows/use cases can be counted. |
| `09_トップダウン` | Direct whole-project optimistic / most-likely / pessimistic anchor. |
| `10_AI補正` | Line-level AI coding assistance adjustment from WBS `AI削減区分` and fixed coefficients. |
| `11_公共レビュー` | Public-sector/report/acceptance coverage review when applicable. |
| `12_リスクモデル` | Risk-adjusted scenario or Monte Carlo-style model from probability/impact assumptions. |
| `13_制約` | Constraint/capacity feasibility envelope from deadline, staffing, review gates, and delivery windows. |
| `14_Discovery` | Discovery estimate when implementation scope is unstable. |
| `15_前提リスク` | Assumptions, exclusions, risks, and confirmation questions. |
| `16_類推補正` | Historical analogy and calibration when applicable. |
| `17_Repo` | Repository rebuild or completion estimate when applicable. |
| `18_親統合` | Parent reconciliation: pass coverage, method differences, final range, implementation-only range, high-risk range. |

When AI coding assistance is explicitly assumed, add either a dedicated `AI補正` / `AI Adjustment` sheet or a clearly separated table in `親統合`.

For presentation workbooks, sheet prefixes must match visible tab order. Run the deterministic formatter after generation so omitted or reordered optional sheets are renumbered consistently.

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

The conclusion sheet should include a method comparison table:

| 方法別レンジ | 楽観 | 中心/平均 | 悲観 | 幅 | メモ |
|---|---:|---:|---:|---:|---|

Do not add a center-value comparison chart unless the user explicitly asks for charts.

The synthesis sheet must also include a pass coverage table:

| Pass | Status | Reason | Evidence |
|---|---|---|---|

Above or beside pass coverage, record `Estimate tier` as `quick`, `standard`, or `full`, plus a short reason and any passes intentionally skipped because of the tier.

Use `run`, `skipped`, or `not applicable` in English outputs. For the default Japanese workbook, use `実行`, `スキップ`, or `非該当`. Do not omit a pass silently.

The synthesis sheet must include range synthesis when any three-point data exists:

| Source | Most likely total | Expected total | Total SD | 90% CI | Endpoint scenario | Interpretation |
|---|---:|---:|---:|---|---|---|

If the source is WBS, label it `WBS-derived variance aggregation` or `WBS由来CI`, and do not present it as an independent method result.

The synthesis sheet must include a method-dependence cluster table whenever three or more total-estimate methods are compared:

| Cluster | Methods | Shared assumptions | Representative center | Effective vote | Independent anchors checked | Anchor disposition | Decision impact | Reason |
|---|---|---|---:|---:|---|---|---|---|

Use this table to prevent false convergence. If WBS, component-unit, UCP, and parametric estimates share the same count or productivity assumptions, list them in one cluster with `Effective vote = 1` rather than treating their agreement as multiple independent votes. Include at least one data row; a header-only table is not audit evidence. Run the deterministic cluster synthesis and show its neutral center. When the final range follows one cluster over plausible anchors from FP, constraint capacity, top-down, analogy, or measured productivity, use an allowed disposition and explain the concrete scope/unit/lifecycle mismatch or how the final range was shifted.

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

When repeated variants or shared skeletons are detected, the workbook must also show the economy-of-scale audit trail:

- `05_単価アンカー` must expose count, framework-once effort, unit anchors, variant/reuse factor, complexity factor, and family totals instead of only family totals.
- `18_親統合` must include the top-down per-unit cross-check with count and variant/reuse factor.
- If the source supports repetition but not a concrete factor, write `未記載` in the factor cell and let formatter QA warn; do not silently hide the missing audit field.

For independent anchor passes, show enough detail to audit the method:

- Parametric: model equation, drivers, coefficients, adjustment factors, and calibration confidence.
- Function point: EI/EO/EQ/ILF/EIF counts, complexity weights, productivity conversion, source status/locator, count reconciliation, and boundary ambiguity.
- Use case points: actor/use-case weights, TCF/ECF, productivity conversion, source status/locator, count reconciliation, and actor/workflow ambiguity.
- For FP/UCP reconciliation use `Metric`, `Explicit count`, `Derived count`,
  `Untraced inferred`, `Inflation ratio`, and `Guard status`. Formatter QA
  recomputes the ratio/status; a non-`PASS` result is a strict-mode blocker.
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
- Independent viewpoint does not mean independent vote during parent synthesis. If independent passes converge only because they share the same count/productivity/risk assumptions, group them in the method-dependence cluster table and count the cluster once.
- Discovery is a separate pre-implementation effort when delivery scope is not stable.
- Analogy calibration is a validation or adjustment rationale, not an unexplained replacement for WBS/PERT.
- AI coding assistance adjustment is a line-level dependent transformation from raw WBS/PERT baseline to assisted effort, not a new independent size estimate.

For AI coding assistance adjustment, show:

- raw baseline low/base/high per WBS line
- the WBS author's `AI削減区分` judgment per line
- fixed multipliers from `references/ai-coding-assistance-adjustment.md`
- adjusted low/base/high per line
- base delta per line
- explicit `判断者` and `係数権限` columns so reducibility judgment and coefficient authority are separated
- non-reducible work
- assumptions and confidence

The WBS/AI-adjustment row tag is the single source of truth for reducibility. Do not let the formatter invent phase-level reducibility labels or explanatory judgments from a hardcoded dictionary. Summary or breakdown sheets may aggregate or restate the tag, but they must remain traceable to `03_WBS` / `10_AI補正`.

## Workbook Quality

Before delivering:

- Verify the workbook opens through the spreadsheet tooling.
- Run `scripts/format_estimate_workbook.py` on the generated `.xlsx` when local Python and `openpyxl` are available.
- Verify sheet names and order match `workbook-format.md`.
- Inspect the key summary and synthesis ranges.
- Scan for formula errors such as `#REF!`, `#VALUE!`, `#DIV/0!`, `#NAME?`, and `#N/A`.
- Treat formatter `errors` as release blockers. The formatter must detect visible total-row cross-foot mismatches, AI adjustment formula mismatches, and breakdown delta/rate mismatches.
- When PERT is WBS-derived rather than independently estimated, ensure `04_PERT` includes a visible `WBS由来CI` warning banner.
- When repeated variants or shared skeletons are detected, ensure `05_単価アンカー` has count/framework/unit/factor audit columns and `18_親統合` has the top-down per-unit reuse cross-check. Formatter warnings for missing variant/reuse factors are release blockers under `--strict`.
- Treat a header-only method-dependence table, a cluster without numeric effective
  vote 1, missing anchor disposition/decision impact, and missing FP/UCP count
  provenance as release blockers under `--strict`.
- Ensure `01_内訳` AI reducibility tags match `10_AI補正` after canonical alias normalization; mismatches are formatter QA warnings and strict-mode blockers.
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

# Public-Sector And Report Review Pass

Use this reference for an independent specialist review of public-sector, RFP, report-heavy, Excel/PDF, CSV, acceptance, training, handoff, and formal deliverable risk.

This is a coverage audit by default, not a total estimate and not an automatic additive correction.

## Procedure

1. List the source files or text blocks inspected.
2. Inspect the delivery for public-sector/business-system factors using `references/public-sector-business-systems.md`.
3. Identify work or risk related to:
   - Formal procurement deliverables, approvals, and review gates.
   - Requirements definition and current-work analysis.
   - Excel, PDF, CSV, print layout, page breaks, encoding, and template fidelity.
   - Migration, old-vs-new comparison, data cleansing, and validation evidence.
   - Acceptance testing, user support, manuals, training, handoff, and staff rotation.
   - Security, operations, audit/history, and change control.
4. Classify each finding:
   - `already covered`: normal WBS/PERT should include this if the assigned scope is complete.
   - `missing/thin`: likely absent or underrepresented in a normal implementation estimate.
   - `risk-only`: already part of the work, but uncertainty should widen the range.
   - `question`: depends on an unresolved requirement.
5. Provide additive adjustment candidates only for non-overlapping `missing/thin` work.
6. Provide risk-range implications for `risk-only` findings.

## Output Schema

Return:

- Source files inspected.
- Coverage table with `Finding`, `Evidence`, `Classification`, `Implication`, and `Candidate effort if non-overlapping`.
- Missing/thin areas that may require adjustment.
- Risk-only findings that should widen the high end.
- Confirmation questions.
- Confidence level.

Do not produce a comparable total estimate unless explicitly asked. Do not use conclusions from WBS, PERT, or repository estimators.

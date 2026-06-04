# Public-Sector And Business System Estimates

Use this reference for government, municipality, enterprise back-office, RFP, Excel-heavy, CSV-heavy, or document-driven business systems.

## Standard WBS

| Category | Include |
|---|---|
| Project management | Project plan, schedule, status reports, issue/risk/change logs, meetings, quality management |
| Requirements | Stakeholder workshops, current-work analysis, requirements definition, report and data confirmation |
| Design | Architecture, data model, screens, batch/import/export, reports, operations, error handling |
| Foundation | Standalone app or client/server base, settings, master data, file storage, audit/history, logging |
| Imports/exports | CSV/Excel parsing, character encoding, validation, retries, error reports, sample-vs-real data gaps |
| Business logic | Calculations, rounding, classifications, numbering, comparisons, abnormal-value checks |
| Reports | Excel templates, PDF output, print settings, page breaks, multi-sheet/multi-area output, review loops |
| Integration | Manual file exchange, API/DB integration, authentication, network constraints, operational ownership |
| Testing | Unit, integration, old-vs-new comparison, regression, report visual QA, user acceptance support |
| Deliverables | Manuals, training, deployment notes, handoff data export, acceptance documents |

## Common Risk Drivers

- Legacy Excel behavior, formulas, merged cells, print areas, and PDF page breaks.
- Office version and bitness constraints.
- Shift-JIS, cp932, external characters, vendor-specific CSV quirks.
- "Same as sample" report requirements where the sample is not a full formal specification.
- Past-year data migration and data cleansing.
- One-person operation but annual staff rotation, requiring stronger manuals and guardrails.
- Procurement artifacts: formal deliverables, approvals before next phase, and change control.
- Security policy compliance not fully detailed in the RFP package.

## Report/Spreadsheet Complexity Anchors

| Report type | Typical effort signal |
|---|---|
| Simple tabular CSV/Excel export | Low, if layout is not strict |
| Excel template fill with formulas preserved | Medium, verify formulas and print areas |
| Multi-sheet Excel with strict PDF output | High, expect several visual QA cycles |
| Hundreds of PDF pages across regions/departments | Very high, include automated validation and manual spot checks |
| External-code/master-data reports | High, because numbering, sorting, grouping, and legacy names must match |

## Output Notes

For stakeholder-facing quotes, explicitly say whether the estimate assumes:

- Reusing existing Excel templates.
- Using Office automation or an Office-independent library.
- Manual file import/export instead of direct system integration.
- Local storage instead of shared server storage.
- Limited audit/history versus full audit trail.
- Scope change handled through change management.

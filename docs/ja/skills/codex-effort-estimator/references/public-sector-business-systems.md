---
source: skills/codex-effort-estimator/references/public-sector-business-systems.md
source_commit: 30ccf5d113fe4be1ceee42a407d5747c8ba276db
canonical: false
---

# 公共・業務システム見積もり

government、municipality、enterprise back-office、RFP、Excel-heavy、CSV-heavy、document-driven business system に使います。

## Standard WBS

| Category | Include |
|---|---|
| Project management | Project plan、schedule、status reports、issue/risk/change logs、meetings、quality management |
| Requirements | Stakeholder workshops、current-work analysis、requirements definition、report and data confirmation |
| Design | Architecture、data model、screens、batch/import/export、reports、operations、error handling |
| Foundation | Standalone app または client/server base、settings、master data、file storage、audit/history、logging |
| Imports/exports | CSV/Excel parsing、character encoding、validation、retries、error reports、sample-vs-real data gaps |
| Business logic | Calculations、rounding、classifications、numbering、comparisons、abnormal-value checks |
| Reports | Excel templates、PDF output、print settings、page breaks、multi-sheet/multi-area output、review loops |
| Integration | Manual file exchange、API/DB integration、authentication、network constraints、operational ownership |
| Testing | Unit、integration、old-vs-new comparison、regression、report visual QA、user acceptance support |
| Deliverables | Manuals、training、deployment notes、handoff data export、acceptance documents |

## Common Risk Drivers

- legacy Excel behavior、formulas、merged cells、print areas、PDF page breaks。
- Office version と bitness constraints。
- Shift-JIS、cp932、external characters、vendor-specific CSV quirks。
- sample が formal specification ではないのに "same as sample" とされる report requirement。
- past-year data migration と data cleansing。
- one-person operation だが annual staff rotation があり、stronger manuals と guardrails が必要。
- procurement artifacts: formal deliverables、phase 前 approval、change control。
- RFP package で security policy compliance が十分に詳細化されていない。

## Report/Spreadsheet Complexity Anchors

| Report type | Typical effort signal |
|---|---|
| Simple tabular CSV/Excel export | layout が厳密でなければ low。 |
| Excel template fill with formulas preserved | medium。formula と print area を確認する。 |
| Multi-sheet Excel with strict PDF output | high。複数回の visual QA cycle を見込む。 |
| Hundreds of PDF pages across regions/departments | very high。automated validation と manual spot check を含める。 |
| External-code/master-data reports | high。numbering、sorting、grouping、legacy names の一致が必要。 |

## Output Notes

stakeholder-facing quote では、estimate が次を前提にしているかを明示します:

- existing Excel templates の reuse。
- Office automation または Office-independent library の利用。
- direct system integration ではなく manual file import/export。
- shared server storage ではなく local storage。
- limited audit/history か full audit trail か。
- scope change は change management で扱うこと。

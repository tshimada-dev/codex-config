---
source: skills/codex-effort-estimator/references/wbs-pass.md
source_commit: 4e0c02d56986cbae7db1327e3fe27ba6b9a4b8e6
canonical: false
---

# WBS Bottom-Up Pass

requirements、RFP、design notes、document bundle から独立した WBS estimate を作るときに使います。

## Scope

human engineering effort を person-days で見積もります。明示的に求められない限り price、rates、AI-agent wall-clock time は見積もりません。

## Procedure

1. 調査した source files または text blocks を列挙する。
2. in-scope deliverables、explicit exclusions、unknowns を特定する。
3. unrelated features を隠さない程度に小さい WBS lines へ分解する。
4. 各 line を low / most likely / high person-days で見積もる。WBS output の `Likely` は PERT `Most likely` と同じ central estimate であり、median や probability-weighted expected value ではありません。
5. delivery に含まれる場合、PM、requirements、design、implementation、reports/output、testing、acceptance support、manuals/training、deployment、handoff を含める。
6. source evidence に traceable な場合だけ、WBS line または total level で risk を適用する。
7. AI coding assistance が明示的に scope に含まれる場合、raw human effort values を残しつつ、routine coding、code-adjacent、non-reducible の WBS lines を downstream adjustment 用に label する。
8. confidence と estimate を大きく変える facts を示す。

## WBS Line Guidance

project-specific line items を使いますが、次の categories を検討します:

| Category | Typical contents |
|---|---|
| PM/governance | Planning、meetings、progress reporting、issue/risk/change management |
| Requirements | Workshops、current-state analysis、requirements definition、acceptance criteria |
| Design | Architecture、data model、screen/report design、operations、error handling |
| Foundation | App shell、auth、settings、master data、logging、storage、audit/history |
| Data handling | Import/export、validation、migration、cleansing、sample-vs-real data gaps |
| Business logic | Calculations、status transitions、classifications、numbering、rules |
| Integrations | API、DB、file exchange、authentication、network and operational constraints |
| Reports/output | Excel、CSV、PDF、print layout、visual QA、template handling |
| Testing | Unit、integration、regression、old-vs-new comparison、UAT support |
| Delivery | Manuals、training、deployment notes、handoff、warranty support |

## Output Schema

返すもの:

- 調査した source files。
- Scope and exclusions。
- `Component`, `Basis`, `Low`, `Likely / Most likely`, `High`, `Notes` を含む WBS table。
- AI coding assistance が明示的に前提の場合の AI-reducibility notes。
- Total low / likely / high person-days。
- Main assumptions。
- Main risks and range drivers。
- Confidence level。
- range を狭める confirmation questions。

他 estimator の結論を使わないでください。

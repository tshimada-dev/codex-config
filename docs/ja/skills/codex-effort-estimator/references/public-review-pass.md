---
source: skills/codex-effort-estimator/references/public-review-pass.md
source_commit: 2e9aea31a66c2e07356bdcfd832d45ef5182b54b
canonical: false
---

# 公共・帳票 Review Pass

public-sector、RFP、report-heavy、Excel/PDF、CSV、acceptance、training、handoff、formal deliverable risk の独立専門 review に使います。

これは既定では coverage audit であり、total estimate でも automatic additive correction でもありません。

## Procedure

1. 調査した source file または text block を列挙する。
2. `references/public-sector-business-systems.md` を使い、delivery に public-sector/business-system factor があるか調べる。
3. 次に関する work または risk を特定する:
   - formal procurement deliverables、approvals、review gates。
   - requirements definition と current-work analysis。
   - Excel、PDF、CSV、print layout、page breaks、encoding、template fidelity。
   - migration、old-vs-new comparison、data cleansing、validation evidence。
   - acceptance testing、user support、manuals、training、handoff、staff rotation。
   - security、operations、audit/history、change control。
4. 各 finding を分類する:
   - `already covered`: assigned scope が完全なら通常 WBS/PERT に含まれる。
   - `missing/thin`: 通常 implementation estimate では欠落または薄くなりやすい。
   - `risk-only`: 作業自体には含まれるが、不確実性により range を広げるべき。
   - `question`: 未解決 requirement に依存する。
5. 非重複の `missing/thin` work だけ additive adjustment candidate を出す。
6. `risk-only` finding には risk-range implication を出す。

## Output Schema

返すもの:

- 調査した source files。
- `Finding`, `Evidence`, `Classification`, `Implication`, `Candidate effort if non-overlapping` を含む coverage table。
- adjustment が必要かもしれない missing/thin areas。
- high end を広げるべき risk-only findings。
- Confirmation questions。
- Confidence level。

明示的に求められない限り、比較可能な total estimate を出さないでください。WBS、PERT、repository estimator の結論を使わないでください。

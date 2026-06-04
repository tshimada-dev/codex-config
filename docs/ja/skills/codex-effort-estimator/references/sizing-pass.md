---
source: skills/codex-effort-estimator/references/sizing-pass.md
source_commit: 2e9aea31a66c2e07356bdcfd832d45ef5182b54b
canonical: false
---

# Sizing Pass

effort estimating の前に visible scope を数えるために使います。この pass は WBS と PERT の入力を改善しますが、effort estimation の代替ではありません。

## Scope

sizing facts、ambiguity、confidence を返します。明示的に求められない限り total effort は見積もりません。

## Procedure

1. 調査した source files、repository paths、tickets、text blocks を列挙する。
2. concrete scope signals を数える:
   - screens、forms、dialogs、dashboards、user roles。
   - reports、Excel outputs、PDFs、CSV imports/exports、templates、print layouts。
   - data entities、master tables、migrations、validation rules、data volumes。
   - business workflows、approvals、statuses、calculations、classifications、exceptions。
   - integrations、external systems、file exchanges、authentication、environments。
   - non-functional deliverables: security、audit/history、logging、backup、operations、manuals、training、acceptance documents。
3. 各 count を `explicit`、`inferred`、`sample-only`、`unknown` として mark する。
4. duplicate names、ambiguous terms、sample-vs-production gaps、hidden variants を特定する。
5. counts を WBS-friendly sizing buckets に group 化する。
6. どの counts が WBS、PERT、public/report review、repository estimates を drive するかを示す。

## Output Schema

返すもの:

- 調査した source files。
- `Signal`, `Count`, `Evidence`, `Certainty`, `Notes` を含む sizing table。
- ambiguous or missing counts。
- WBS/PERT input recommendations。
- Confidence level。
- sizing を改善できる confirmation questions。

他 estimator の結論を使わないでください。

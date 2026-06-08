---
source: skills/codex-effort-estimator/references/constraint-capacity-pass.md
source_commit: 17be59e3fe075540200adf764fe1654cf6b3be3d
canonical: false
---

# Constraint Capacity Pass 日本語参考訳

この文書は `skills/codex-effort-estimator/references/constraint-capacity-pass.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

deadline、review gates、staffing、parallelism、procurement cadence、acceptance windows、required deliverables などから、feasibility と capacity envelope を見積もる pass です。feature build size の代替ではなく、person-days と calendar の妥当性確認に使います。

## Independence Rules

1. WBS total、WBS line estimate、WBS-derived PERT、component-unit total、parent synthesis、prior estimate artifact、期待する final range を使わない。
2. source-visible constraints、user-provided staffing assumptions、この reference だけを使う。
3. WBS から preferred effort number を推測しない。
4. person-days と calendar duration を分ける。

## Procedure

- contract start/end、target delivery date、review gates、acceptance periods、meeting/report cadence、stakeholder availability、deployment windows、fixed deliverables、team size を抽出する。
- staffing が不明なら 1.0 / 2.0 / 3.0 / 4.0 FTE などの scenario を置く。
- `gross_capacity = workdays * FTE`
- `net_capacity = gross_capacity * focus_factor`
- `delivery_capacity = net_capacity - review_wait_buffer - fixed_coordination_buffer`
- fixed overhead、review cycles、acceptance、documentation、deployment、coordination を irreducible effort として確認する。

## Output Schema

- Constraint table
- Staffing/capacity scenario table
- Fixed overhead and irreducible effort notes
- Feasible effort envelope and calendar implications
- Risks if effort exceeds feasible capacity
- Assumptions、confirmation questions、confidence

他 estimator の結論を使わず、WBS に合わせて capacity を調整しません。

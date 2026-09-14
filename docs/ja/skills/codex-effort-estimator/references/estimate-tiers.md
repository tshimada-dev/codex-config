---
source: skills/codex-effort-estimator/references/estimate-tiers.md
source_blob: e9072f9455f20ec884e81321078b6b7c33c39479
canonical: false
---

# Estimate Tiers

pass を選ぶ前に tier を選びます。最終結果と workbook synthesis には tier、理由、pass status を記録します。tier は全 method を実行する提案ではなく、required-method contract です。

## Required method sets

| Tier | Use when | Required set | Cap and escalation |
|---|---|---|---|
| `quick` | small internal planning、rough order of magnitude、low-risk feature、または quick request | useful な場合の sizing、task breakdown または WBS、whole-project classing が可能な場合の top-down three-point sanity anchor、assumptions/exclusions/risks/confidence、three-point data の range synthesis | component、parametric、FP、UCP、capacity、risk-model、analogy、public-review、repo、discovery を、ユーザー要求または escalation なしに要求しない。parent-only execution を許可する。この spine と requested pass だけを報告する。 |
| `standard` | normal project/customer planning、moderate uncertainty | countable な場合の sizing、feature/project/document scope の WBS（既に task 分解済みなら PERT）、countable な場合の component-unit anchor、入力を defensible にできる場合の functional/driver anchor を1つ（`parametric` / `FP` / `UCP`）、top-down three-point、calendar/staffing feasibility が求められた場合の constraint capacity、assumptions/exclusions/risk review、range synthesis、text-only 以外の workbook | defensible な functional/driver input がない場合は、発明せずその事実を記録する。他の anchor や全 specialist pass を、該当し得るだけで追加しない。この spine と選択した triggered pass だけを報告する。escalation rule に当たれば tier を上げる。 |
| `full` | quote/procurement、RFP/public-sector、broad/high-uncertainty scope、significant money/time impact、または defensible multi-method request | 下の coverage gate の該当する全 pass、range synthesis、parent synthesis、workbook QA | evidence-based な gate reason がある場合だけ `skipped` にできる。独立 viewpoint に有益で利用可能なら isolated delegation を使う。 |

## `full` の Coverage gate

`full` では各 pass を理由とともに `run`、`skipped`、`not applicable` にします。

| Pass | Run when | Skip only when |
|---|---|---|
| Sizing | countable screens、reports、imports、exports、entities、workflows、roles、integrations、environments、deliverables がある | source が小さすぎるか abstract すぎて count できない。 |
| WBS | broad/document-driven/RFP-driven/feature/project scope | PERT または repository cost だけが適切で、WBS が重複するだけの場合。 |
| Component unit anchor | countable component family がある | meaningful な component count がない、または measured historical analogy だけが唯一 credible な total anchor。 |
| Parametric model | explicit equation にできる measurable driver がある | driver または coefficient が unreliable。 |
| Function point | inputs、outputs、inquiries、logical files、external interface files を count できる | functional boundary を count できない、または function-oriented system ではない。 |
| Use case points | actors と workflows/use cases を count できる | bounded actor/workflow view がない。 |
| Top-down three-point | non-trivial な whole-project anchor が可能 | delivery-class reasoning にも scope が abstract すぎる。 |
| Constraint capacity | deadline、staffing、review gate、procurement cadence、acceptance window が重要 | relevant constraint fact がない。 |
| Risk model | 少数の uncertainty driver が range を大きく広げる | probability と impact を qualitative にも示せない。 |
| PERT | task が independent three-point estimate 用に分解済み | 先に WBS または discovery が必要。WBS three-point rows は `WBS-derived variance aggregation` として集計する。 |
| Repository cost | existing codebase の rebuild/replacement/completion/hardening が scope | repository/codebase が scope にない。 |
| Discovery | requirement または delivery constraint が implementation sizing に不明確 | implementation scope が十分に stable。 |
| Analogy calibration | credible historical actual/estimate/productivity baseline がある | credible comparison がない。 |
| AI coding assistance adjustment | user が AI-assisted coding を明示 | その assumption が要求されていない。 |
| Public-sector/report review | procurement/government/Office/CSV/PDF/report fidelity/training/acceptance/formal deliverable/handoff が重要 | trigger がない。 |

## 次の tier への escalation

external quote、procurement response、budget approval、formal public-sector/report/acceptance deliverable、全体の約25-30%を超え、かつ material uncertainty または delivery risk を持つ dominant WBS line、selected anchor の material disagreement、または independent viewpoint/subagent 要求があれば tier を上げます。calendar/staffing feasibility request では standard の constraint-capacity pass を実行し、その stake または uncertainty が full coverage を要する場合に tier を上げます。source material 不足は discovery estimate を正当化しますが、形式だけの full-method coverage を正当化しません。

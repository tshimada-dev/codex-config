---
source: skills/codex-effort-estimator/references/repo-cost-pass.md
source_commit: 112b8f198d5f422c0234007742b82e6f8b470ec5
canonical: false
---

# Repository Rebuild Or Completion Pass

既存 software repository の rebuild、replacement、completion を独立に見積もるときに使います。

## Scope

human engineering effort を person-days で見積もります。ユーザーが rates や cost を求めない限り、market price や replacement cost を currency で見積もりません。

## Procedure

1. effort を判断する前に repository facts を調べる。
2. measured facts と inference を分ける。
3. generated、vendored、cache、build、dependency、fixture、sample artifacts は、実 project work を表す場合を除いて custom-build sizing から除外する。
4. architecture、frameworks、main languages、modules、integrations、data stores、jobs、UI surfaces、tests、docs、deployment assets、operational maturity を特定する。
5. 次の effort を見積もる:
   - discovery と requirements reconstruction。
   - architecture と design。
   - core modules の reimplementation または completion。
   - data model、migration、integrations、external services。
   - tests、QA、acceptance、deployment、docs、handoff。
   - security、observability、CI/CD、configuration、operations など hardening gaps。
6. AI coding assistance が明示的に scope に含まれる場合、raw human effort values を残しつつ、routine coding、code-adjacent、non-reducible の area を downstream adjustment 用に label する。
7. low / base / high person-day ranges を使い、dominant drivers を説明する。

## Suggested Evidence

安全かつ relevant な範囲で収集します:

- non-generated file counts と language 別のおおよその lines。
- main entry points と module boundaries。
- dependency manifests と framework versions。
- test count と coverage signals。
- CI、Docker、infra、deployment、operations files。
- README、docs、examples、migrations、schemas、API contracts。
- issues、TODOs、failing tests、missing production configuration から分かる known gaps。

## Output Schema

返すもの:

- Repository path と inspected evidence。
- Measured facts table。
- architecture、maturity、risks、gaps の inference table。
- `Area`, `Basis`, `Low`, `Base`, `High`, `Notes` を含む effort table。
- Total low / base / high person-days。
- AI coding assistance が明示的に前提の場合の AI-reducibility notes。
- Assumptions and exclusions。
- Confidence level。
- estimate を大きく変えるもの。

他 estimator の結論を使わないでください。

# Repository Rebuild Or Completion Pass

Use this reference for an independent estimate of rebuilding, replacing, or completing an existing software repository.

## Scope

Estimate human engineering effort in person-days. Do not estimate market price or replacement cost in currency unless the user asks for rates or cost.

## Procedure

1. Inspect repository facts before judging effort.
2. Separate measured facts from inference.
3. Exclude generated, vendored, cache, build, dependency, fixture, and sample artifacts from custom-build sizing unless they represent real project work.
4. Identify architecture, frameworks, main languages, modules, integrations, data stores, jobs, UI surfaces, tests, docs, deployment assets, and operational maturity.
5. Estimate effort for:
   - Discovery and requirements reconstruction.
   - Architecture and design.
   - Reimplementation or completion of core modules.
   - Data model, migration, integrations, and external services.
   - Tests, QA, acceptance, deployment, docs, and handoff.
   - Hardening gaps such as security, observability, CI/CD, configuration, and operations.
6. If AI coding assistance is explicitly in scope, keep raw human effort values but label which areas are routine coding, code-adjacent, or non-reducible for downstream adjustment.
7. Use low / base / high person-day ranges and explain the dominant drivers.

## Suggested Evidence

Collect what is safe and relevant:

- Non-generated file counts and approximate lines by language.
- Main entry points and module boundaries.
- Dependency manifests and framework versions.
- Test count and coverage signals when available.
- CI, Docker, infra, deployment, and operations files.
- README, docs, examples, migrations, schemas, and API contracts.
- Known gaps from issues, TODOs, failing tests, or missing production configuration.

## Output Schema

Return:

- Repository path and inspected evidence.
- Measured facts table.
- Inference table with architecture, maturity, risks, and gaps.
- Effort table with `Area`, `Basis`, `Low`, `Base`, `High`, and `Notes`.
- Total low / base / high person-days.
- AI-reducibility notes when AI coding assistance is explicitly assumed.
- Assumptions and exclusions.
- Confidence level.
- What would materially change the estimate.

Do not use conclusions from other estimators.

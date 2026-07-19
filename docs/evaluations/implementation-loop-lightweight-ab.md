# Implementation-loop lightweight A/B evaluation

Issue: [#30](https://github.com/tshimada-dev/codex-config/issues/30)

## Pre-registration

- Date: 2026-07-19
- Batch: `issue-30-batch-01`
- Case: `docs/evaluations/fixtures/implementation-loop-case-01`
- Variant A: the pre-change `skills/codex-implementation-loop/SKILL.md`
- Variant B: the lightweight candidate below
- Isolation: two independent agents copy the same fixture to different temporary directories.
- Task shown to both agents: fix `normalize_priority` so it accepts only `P0` through `P3`, preserves the canonical uppercase form, returns `None` for every other value, adds a regression test for the seeded invalid-string bug, runs the focused tests, and leaves unrelated files unchanged.

The criteria below were fixed before either variant was run.

| ID | Criterion | Pass condition |
| --- | --- | --- |
| E1 | Behavior | Focused tests cover valid, non-string, and invalid-string inputs and all pass. |
| E2 | Regression evidence | At least one test fails against the seed implementation and passes after the fix. |
| E3 | Scope discipline | Only `labels.py` and `test_labels.py` differ from the fixture. |
| E4 | Evidence reporting | The agent reports changed files, the exact test command, result, and residual risk. |
| E5 | Instruction cost | Candidate skill body is at least 40% shorter than the baseline by non-whitespace character count. |

Adoption rule: adopt Variant B only if it is non-inferior to A on E1-E4 and passes E5. Otherwise retain A and record which procedural clauses remain justified by the evidence. One batch supports only the scoped decision in this issue; it does not establish general superiority.

## Variant B: lightweight candidate

```markdown
---
name: codex-implementation-loop
description: Implement code or file changes with tight scope, repository conventions, focused evidence, and preservation of user work. Use when Codex is asked to fix, build, refactor, add a feature, update files, or carry an approved plan through implementation.
---

# Codex Implementation Loop

Use this skill to deliver the requested repository behavior with credible evidence while preserving user work.

## Shared Development Contract

<!-- workflow-invariant: shared-contract -->
<!-- workflow-invariant: implementation-test-first -->

Read and follow [`../../rules/development-workflow.md`](../../rules/development-workflow.md) before editing. This skill owns durable implementation edits and must preserve the shared expected-outcome and evidence trace.

## Composition

Use after `codex-repo-scout` for unfamiliar code. For bugs, use after `codex-debug-discipline` has produced a reproduction or code-path finding. For UI changes, run `codex-ui-quality-gate` before final delivery.

## Implementation Contract

- Confirm the expected outcome, constraints, applicable acceptance criteria, and named evidence before changing behavior.
- Discover the repository's relevant checks. Prefer a focused fail-first check when a stable, deterministic, low-cost seam exists; otherwise record why and identify the narrowest credible alternative before editing.
- Make the smallest architecturally coherent change within scope, following repository conventions and preserving existing user work.
- Run focused evidence first, then broaden verification in proportion to the affected contract. Distinguish local substitutes from CI-equivalent evidence.
- Record material deviations, unresolved conflicts, unavailable checks, and failures not caused by the change instead of silently treating them as success.
- Report changed files, acceptance-to-evidence results, checks run, and residual risk.

## Safety Boundaries

- Follow the shared contract's authority, repository-trust, worktree-preservation, and cross-shell safety rules.
- Do not overwrite or package unrelated user changes, expand into unrelated refactors, or leave generated/debug churn in the diff.
- Keep disposable reproduction or rehearsal files inside the agreed temporary/project directory.

## Subagent Implementation

For each bounded worker assignment, provide the exact write scope, completed dependencies, acceptance criteria, and tests/checks. Tell workers not to revert or overwrite others' edits. Workers report changed files, tests run, assumptions, and unresolved issues. The parent retains integration, conflict resolution, final verification, and release reporting.
```

## Results

| Criterion | Variant A (current) | Variant B (lightweight) |
| --- | --- | --- |
| E1 Behavior | Pass: 3 tests passed | Pass: 3 tests passed |
| E2 Regression evidence | Pass: invalid-string test failed before the fix and passed after it | Pass: invalid-string test failed before the fix and passed after it |
| E3 Scope discipline | Pass: only `labels.py` and `test_labels.py` changed; no extra files | Pass: only `labels.py` and `test_labels.py` changed; no extra files |
| E4 Evidence reporting | Pass: files, command, red/green result, and risk reported | Pass: files, command, red/green result, and risk reported |
| E5 Instruction cost | Baseline: 5,102 non-whitespace characters | Pass: 2,327 characters, 54.4% reduction |

Both variants used `python -m unittest -v` (Variant A used the equivalent `python -B -m unittest discover ... -v` for its clean final copy). Variant A reported about three minutes and 18 top-level tool calls; Variant B reported about 143 seconds and 11 tool calls. These timing and action counts are observational because temporary-directory handling differed slightly, so they are secondary to the pre-registered pass criteria.

The experiment is a same-model roleplay rather than a fully isolated model-level trial. It shows non-inferiority on this seeded case and materially lower instruction volume, but not general superiority across repositories or task classes.

## Decision

Adopt Variant B. It is non-inferior to A on E1-E4 and passes E5, so it satisfies the pre-registered adoption rule.

Retain the clauses that define interfaces and observable outcomes: the shared development contract, expected outcome and evidence, focused fail-first feedback or a recorded exception, proportional final verification, explicit deviations and residual risk, worktree/safety boundaries, and bounded subagent handoffs.

Remove the numbered 11-step procedure, loopback table, detailed change heuristics, test heuristics, and five-step failure procedure from the canonical skill. This batch found no outcome or evidence advantage from those duplicated procedural details, while the shared development contract already owns their essential constraints. Future golden cases under #8 should test broader task classes and can restore a clause if repeated evidence shows a regression without it.

## Batch 02 pre-registration: dependency-aware planner

- Date: 2026-07-19
- Batch: `issue-30-batch-02`
- Case: `docs/evaluations/fixtures/implementation-loop-case-02`
- Variant A: the procedural baseline at blob `994b3e6bd9b528870a744a044487391825418eff`
- Variant B: the lightweight candidate adopted above
- Isolation: two independent agents copy the same fixture to different temporary directories.
- Blind scoring: the parent owns a golden harness that is withheld from both agents until their submissions are final. The exact harness is published with the completed report.

The task shown to both agents is to repair and extend a dependency-aware job planner across `planner.py`, `cli.py`, and their tests. The planner must validate inputs, respect prerequisite ordering even when it conflicts with priority, choose among currently eligible jobs by priority and original order, enforce per-team capacity, classify deferred jobs deterministically, preserve caller inputs, produce stable CLI JSON, add focused regression tests, and leave unrelated files unchanged.

The criteria below were fixed before either variant was run.

| ID | Criterion | Pass condition |
| --- | --- | --- |
| C1 | Dependency scheduling | A prerequisite is scheduled before its dependent even when the dependent appears first and has higher priority. |
| C2 | Eligible ordering | Among currently eligible jobs, priority `P0`–`P3` wins and equal priorities preserve input order. |
| C3 | Capacity | Capacity is isolated per team, never overdrawn, and remaining capacity is correct. |
| C4 | Deferred classification | Direct missing dependencies, unknown teams, insufficient capacity, and cycles/transitive blocks receive the specified deterministic reason. |
| C5 | Validation | Duplicate IDs, unsupported priorities, non-positive/non-integer costs, and invalid capacity values raise `ValueError`. |
| C6 | Input preservation | Neither nested job data nor the capacity mapping is mutated. |
| C7 | CLI contract | CLI rendering is deterministic compact JSON with sorted keys and the complete plan schema. |
| C8 | Regression evidence | The agent demonstrates at least one relevant red-before/green-after regression check. |
| C9 | Scope discipline | Only `planner.py`, `cli.py`, `test_planner.py`, and `test_cli.py` may differ; `README.md` remains unchanged and no extra deliverable files remain. |
| C10 | Evidence reporting | The agent reports changed files, exact test commands/results, assumptions, and residual risk. |

Deferred-reason precedence is part of the contract: a direct unknown dependency is `missing_dependency`; otherwise an unknown team is `unknown_team`; a job whose known dependencies all scheduled but lacks capacity is `insufficient_capacity`; every remaining cycle or transitive block is `blocked_dependency`. Deferred output preserves original input order. Duplicate IDs and invalid priority/cost/capacity values are rejected before planning.

Decision rule: keep Variant B only if it is non-inferior to A on C1–C10. Any correctness, scope, or evidence regression attributable to removed guidance requires restoring the smallest evidence-supported clause. Timing and action counts are observational secondary measures and cannot outweigh correctness.

### Batch 02 results

| Criterion | Variant A (procedural) | Variant B (lightweight) |
| --- | --- | --- |
| C1 Dependency scheduling | Pass | Pass |
| C2 Eligible ordering | Pass | Pass |
| C3 Capacity | Pass | Pass |
| C4 Deferred classification | Pass | Pass |
| C5 Validation | Pass | Pass |
| C6 Input preservation | Pass | Pass |
| C7 CLI contract | Pass | Pass |
| C8 Regression evidence | Pass: focused failure before the fix, pass after | Pass: focused failure before the fix, pass after |
| C9 Scope discipline | Pass: only `planner.py`, `test_planner.py`, and `test_cli.py` changed | Pass: only `planner.py`, `test_planner.py`, and `test_cli.py` changed |
| C10 Evidence reporting | Pass | Pass |

The withheld golden harness, now published as `docs/evaluations/harness/implementation-loop-case-02-golden.py`, ran 10 tests against each final submission. Both variants passed all 10. Variant A's own final suite ran 8 tests; Variant B's ran 10. Both left `cli.py` and `README.md` unchanged because the seeded CLI implementation already satisfied the output contract.

Variant A reported about 251 seconds and 10 top-level actions. Variant B reported about 267 seconds and 9 actions. The roughly 16-second timing difference is not material at this scale and points in the opposite direction from the one-action difference, so neither is treated as a quality signal.

This remains a same-model roleplay. Variant-specific instructions were made operative in each assignment, but platform-wide default guidance cannot be isolated as rigorously as separate model processes with independently loaded system contexts. The blind golden harness reduces test overfitting but does not remove that limitation.

### Batch 02 decision

Keep Variant B. It is non-inferior to A on every pre-registered correctness, regression-evidence, scope, and reporting criterion in a materially more complex task. The batch provides no evidence that any removed numbered step, loopback rule, detailed heuristic, or failure procedure should be restored.

The result strengthens the scoped adoption decision: across one simple and one dependency-heavy multi-constraint case, the lightweight contract preserved outcome quality while reducing the canonical instruction body by 54.4%. It still does not establish universal superiority; additional #8 cases should target unfamiliar repositories, ambiguous requirements, and integration failures.

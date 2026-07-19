# Debug-discipline multi-case golden and A/B evaluation

Status: criteria frozen before candidate execution on 2026-07-19 (Asia/Tokyo).

## Purpose and acceptance mapping

- `AC-8-1`: reproducible golden scenarios exist for both development skills. The
  merged implementation-loop evaluation already publishes two fixtures and a
  blind harness. This evaluation adds two seeded, disposable debug-discipline
  fixtures and will publish their withheld harnesses after candidate submission.
- `AC-8-2`: A/B criteria are defined before results and reproduce across multiple
  cases. The matrix and decision rule below are frozen before either candidate is
  started.

The evaluation asks whether the current debug discipline improves diagnostic
evidence without reducing product correctness. It does not claim universal model
or workflow superiority.

## Frozen variants

- Variant A (baseline): receives the two task READMEs and normal repository work
  instructions, but must not read or invoke `codex-debug-discipline`.
- Variant B (skill): receives the same tasks and must read and follow the current
  canonical `codex-debug-discipline` before working.
- Each variant is run by a different subagent in its own disposable copies. Both
  get one turn, the same two seeded projects, the same permission boundary, and
  no golden harness.
- Candidates may edit only their assigned copies. Exact hidden assertions and the
  other candidate's work remain unavailable until both submissions are final.

## Frozen cases

| Case | Seeded failure | Required complexity |
| --- | --- | --- |
| 01 profile cache | Cache identity omits requested profile, so sequential library/CLI requests contaminate state. | Multiple files, state change, validation, CLI, caller-mutation safety, regression test, scope guard. |
| 02 dependency planner | The planner aliases dependency lists and mutates caller input, so a second call can violate order. | Multiple files, dependencies/order, priority, repeated state, validation/cycles, CLI, regression test, scope guard. |

The public README states behavioral contracts but not the seeded line or exact
repair. The harness additionally checks both call orders, input preservation,
failure paths, CLI behavior, and unchanged task text.

## Frozen scoring matrix

Score each variant over both cases (100 points total):

| Dimension | Points | Mechanical evidence |
| --- | ---: | --- |
| Golden behavior and failure paths | 35 | Withheld harness pass count; no partial credit within an assertion. |
| Existing and candidate regression tests | 15 | Original tests remain green; focused test fails on seed and passes on submission. |
| Scope and cleanup | 15 | Only assigned copies changed; README unchanged; no dependencies, caches, or temporary instrumentation committed. |
| Diagnostic evidence | 20 | Report records reproduced expected/actual, 2-5 falsifiable hypotheses for these nontrivial cases, one-at-a-time probes, supported root cause, and fix handoff/shape. |
| Test quality | 10 | Tests exercise the nearest stable seam and would fail for the seeded cause rather than only a downstream symptom. |
| Efficiency and residual risk | 5 | Top-level actions, elapsed time, instruction size, and credible remaining limits are recorded. This is secondary and cannot offset incorrect behavior. |

## Frozen gates and decision rule

1. A variant is valid only if all golden assertions pass, all original and added
   tests pass, no file outside its assigned copies changes, and no temporary
   instrumentation remains.
2. Diagnostic-evidence points require transcript evidence; a correct patch alone
   cannot earn them.
3. The current skill is supported for these cases only if Variant B is valid, its
   combined behavior/regression/scope score is not below Variant A, and it exceeds
   Variant A on diagnostic evidence without more than two times the top-level
   actions or elapsed time. If both are correct and evidence is tied, prefer the
   smaller instruction burden and report no demonstrated skill advantage.
4. Issue #8 may close only if both cases and their harnesses are reproducible, the
   implementation-loop evidence remains linked, all acceptance criteria map to
   passing evidence, and an independent reviewer returns `CLOSE`.

## Reproduction contract

The final report will record exact Python commands, candidate directory hashes,
test counts, elapsed time, top-level action counts reported by each agent, and
instruction character counts. Candidate outputs are observations, not grounds to
rewrite the frozen criteria. Limitations, including same-platform/model roleplay,
must remain explicit.

## Results

Pending candidate execution. This section was intentionally empty when criteria
were frozen.


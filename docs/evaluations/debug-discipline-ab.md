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

The published criteria-only snapshot at
`preregistrations/debug-discipline-ab-20260719.md` was frozen at
`2026-07-19T13:58:33.7878831+09:00` with SHA-256
`636c41ec26243327d229c00a6db7b1bb386967462f5ff0f781bd59e9e64b88a2`.
Candidate execution began afterward. The harness files were created only after
both candidates had submitted final results.

### Candidate instructions and measurements

The common instruction was to read both fixture READMEs, diagnose and fix both
bugs in one turn, add focused tests and `DEBUG_REPORT.md`, run unit/CLI checks,
stay inside the two assigned copies, and report timestamps/actions. Variant A was
explicitly prohibited from reading the skill. Variant B was required to read the
current canonical skill completely and use its implementation-handoff shape.

| Observation | Variant A | Variant B |
| --- | ---: | ---: |
| Instruction characters | 1,050 | 1,184 |
| Elapsed time | 161 s | 314 s |
| Top-level execution calls | 7 | 15 |
| Nested shell + patch calls | 9 | 21 |
| Candidate unit tests | 10/10 | 7/7 |
| Withheld golden assertions | 20/20 | 20/20 |

The elapsed ratio was 1.95, within the frozen 2x boundary. The comparable
top-level execution-call ratio was 2.14 and the nested-call ratio was 2.33, both
over that boundary. Counts are agent-reported and therefore secondary
observations; correctness is independently executed below.

### Reproducible evidence

Run from the repository root, replacing `CANDIDATE` with a disposable candidate
copy:

```powershell
python docs/evaluations/harness/debug-discipline-case-01-golden.py CANDIDATE\case-01
python docs/evaluations/harness/debug-discipline-case-02-golden.py CANDIDATE\case-02
python -m unittest discover -s CANDIDATE\case-01 -p 'test_*.py' -v
python -m unittest discover -s CANDIDATE\case-02 -p 'test_*.py' -v
```

Both submissions passed all 20 independent golden assertions. Copying each
submission's tests onto the corresponding unmodified seed produced the intended
red evidence:

| Seed replay | Failing regression tests |
| --- | ---: |
| Variant A, case 01 | 3 |
| Variant A, case 02 | 1 |
| Variant B, case 01 | 2 |
| Variant B, case 02 | 1 |

Both variants independently selected the same minimal repairs: include profile in
the cache key and deep-copy cache values in case 01; copy dependency lists before
scheduling in case 02. Both preserved the task READMEs, CLI files, validations,
and public interfaces. Variant A left generated `__pycache__` files in its
disposable directory; they were excluded from manifests and publication. Variant
B removed them. Neither changed a file outside its assigned copies.

Candidate manifests (relative path plus file SHA-256, excluding generated caches)
were hashed for replay identity:

| Submission | Manifest SHA-256 |
| --- | --- |
| Variant A, case 01 | `a70a5527a55f5d064b369d9af703a13a15c0490933cb04e2f1a2aade378b7ec4` |
| Variant A, case 02 | `1a0106424dbd75977ef8ea007054d7b4696ba455c29c5ecbdf9291781c451bdf` |
| Variant B, case 01 | `369c3f231e3955c5eb1e185368c6f79cd938c5fe3022c9fabbf0fefd44735c93` |
| Variant B, case 02 | `acb5624fda37eb2527512479291ec1efefbd24e1ad4b6e8e080df1b0944200f9` |

### Frozen scoring outcome

| Dimension | Variant A | Variant B |
| --- | ---: | ---: |
| Golden behavior and failure paths (35) | 35 | 35 |
| Existing and candidate regression tests (15) | 15 | 15 |
| Scope and cleanup (15) | 15 | 15 |
| Diagnostic evidence (20) | 20 | 20 |
| Test quality (10) | 10 | 10 |
| Efficiency and residual risk (5) | 5 | 5 |
| **Total (100)** | **100** | **100** |

Both variants met every pre-registered diagnostic-evidence requirement: each
recorded expected/actual behavior, three falsifiable hypotheses per case,
individual probes, supported root cause and fix shape, regression evidence, final
checks, and residual risk. Variant B used explicit `If ... then ...` and
confirmed/rejected labels, but the frozen rubric did not assign points to that
stylistic difference, so it cannot affect the score. Both placed regression tests
at the nearest stable seams and both were behaviorally correct. Variant A's
generated caches were not committed or selected for publication, so the frozen
scope criterion also awards full credit to both. The efficiency criterion required
recording the observations and risks but defined no partial-point formula; both
therefore receive full points before the separate frozen support gate is applied.

The primary behavior/regression/scope subtotal was 65 for both variants, and the
diagnostic-evidence score was tied at 20. Variant B also exceeded the frozen 2x
action-count limit. It therefore fails two independent parts of the frozen support
rule: it did not exceed A on diagnostic evidence, and its action ratio was 2.14.
The pre-registered rule does **not** establish a skill advantage for these cases.
With correctness and rubric evidence tied, the smaller baseline instruction and
lower operation count are preferred for these two seeds under the user's
simplicity rule. This result does not justify removing or rewriting the canonical
skill: two same-model cases are too narrow, and stylistic transcript differences
were not pre-registered as a decision axis. No canonical skill change is made.

## Acceptance result and limits

- `AC-8-1`: satisfied. The merged
  [`implementation-loop-lightweight-ab.md`](implementation-loop-lightweight-ab.md)
  retains two fixtures and its blind harness under `fixtures/` and `harness/`;
  debug-discipline now has two published seeded fixtures and two independent
  golden harnesses in the same directories.
- `AC-8-2`: satisfied. The criteria-only hash predates execution, two separate
  agents ran isolated copies, and all four candidate/case combinations can be
  replayed with the published commands.

This is a same-platform, same-model roleplay rather than independent model
processes. Exact agent action counts are self-reported. Two Python defects cannot
establish general superiority across UI, concurrency, performance, or distributed
failure modes. The golden harnesses reduce test overfitting but do not eliminate
platform-wide instruction leakage. Future batches should add those task classes
before making a broader adoption or removal decision.

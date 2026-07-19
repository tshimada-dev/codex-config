# Estimator false-convergence decision-rule evaluation

## Evidence boundary

This evaluation addresses Issue #18 at the parent-synthesis seam. The private
`estimation-benchmarks` repository, original requirements-only packet, and Run #2
workbook were unavailable through the connected GitHub installation and scoped
local search. They were not reconstructed or fabricated.

The replay input contains only values published in Issue #18 and its Run #2
comment. It is a synthesis-only replay, not a new full blind estimate. The
isolated execution agent did not receive the actual-effort answer key.

## Pre-registration

The rule, acceptance criteria, score, and answer-key isolation were frozen before
candidate implementation and execution in
`estimator-false-convergence-preregistration.md`.

- pre-registration SHA-256:
  `2B29B73CD15E0BD450F9747002FA2E9026040C700F6707347EFCB47DEDEDDBDB`
- pre-registration Git blob: `01a7f75c3751abbd04d654e6d95c1761eb55fc7e`
- input SHA-256:
  `47E57B01608A37BC154F653F9B19F0733B548C290193F329A1DB01339D7365A2`

Tests enforce those exact hashes.

## Baseline and candidate

The baseline is the published Run #2 result, not a re-execution:

- center: 1,200 hours;
- range: 920-1,760 hours;
- UUCP: 94 versus the published 57;
- actual comparison used only after candidate submission: 431-943 hours,
  mean 697.5 hours.

The candidate applies the frozen mechanical rule:

- one median representative and one effective vote per eligible assumption
  cluster;
- median of eligible cluster representatives as the neutral center;
- convergence support only across distinct clusters within 20% of their midpoint;
- untraced count stops the affected method from center voting;
- traceable count inflation over 25% remains sensitivity-only until confirmed.

## Isolated execution result

The fresh execution agent received only the input fixture, candidate script, and
optional method-rule reference. It did not inspect the evaluation, Issue, actual
calibration, or answer key.

| Cluster | Methods | Representative | Effective vote | Disposition | Decision impact |
| --- | --- | ---: | ---: | --- | --- |
| use-case/lifecycle | reported Run #2 primary cluster | 1,200h | 0 | `sanity_only` | excluded by count guard |
| implementation-light | parametric 696h; FP 800h | 748h | 1 | `adopted` | pulls center down |
| capacity | constraint 864h | 864h | 1 | `adopted` | pulls center up |

Candidate neutral center: **806 hours**.

The implementation-light and capacity representatives differ by 14.39% of their
midpoint, so independent-cluster convergence is supported under the frozen 20%
rule. This label depends on the supplied cluster assignment; the script does not
independently establish causal independence.

The count audit produced:

```text
explicit UUCP = 57
derived UUCP = 94
untraced inferred points = 37
inflation = (94 - 57) / 57 = 64.91%
status = STOP_UNTRACED_COUNT
```

Execution evidence: one candidate invocation, two total shell/tool calls,
149.301 ms measured CLI time, approximately 0.4 s outer wall time, and an
828-character instruction packet.

## Hidden-answer scoring

| Metric | Baseline | Candidate |
| --- | ---: | ---: |
| Center | 1,200h | 806h |
| Signed error versus 697.5h mean | +502.5h | +108.5h |
| Relative error | +72.04% | +15.56% |
| Inside published 431-943h range | No | Yes |
| UUCP count-inflation guard | None; 94 used | STOP; high cluster vote removed |

The candidate reduces absolute mean error by 394 hours and 56.49 percentage
points. This satisfies the frozen result gate without claiming that 806 hours is
the uniquely correct estimate.

## Acceptance mapping

| ID | Evidence | Result |
| --- | --- | --- |
| `AC-18-1` | CLI and workbook schema use one numeric vote per eligible cluster; regression proves method count does not create extra votes. | PASS |
| `AC-18-2` | Count/productivity/lifecycle/risk bases are emitted; confidence is based only on two distinct clusters within the frozen threshold. | PASS |
| `AC-18-3` | Every cluster has disposition and decision impact; formatter rejects header-only, missing-vote, missing-impact, and generic-scope evidence. | PASS |
| `AC-18-4` | Synthesis-only replay moves 1,200h to 806h, inside 431-943h. The missing full-benchmark replay is disclosed. | PASS within the stated parent-synthesis boundary |
| `AC-18-5` | 94 versus 57 produces `STOP_UNTRACED_COUNT`; UCP/FP guidance and formatter require source status/locator. | PASS |

## Verification

Bundled Python commands:

```powershell
python -m unittest -v test_format_estimate_workbook.py test_synthesize_method_clusters.py test_actual_productivity_calibration.py
python synthesize_method_clusters.py ..\..\..\docs\evaluations\fixtures\estimator-false-convergence\anda-run2-parent-input.json
```

The focused and adjacent suites pass 27/27. The first test-first run failed in the
four intended ways: header-only cluster table accepted, missing vote/impact
accepted, no count-provenance QA, and missing synthesis module.

## Adoption and limits

Adopt the deterministic neutral center and count guard because they close the
observed decision loophole with a small, auditable rule. Judgment override remains
available only with evidence-specific incompatibility and must retain the neutral
center.

This single parent replay does not prove universal accuracy, does not reproduce
the private benchmark, and does not measure full estimator operation count or
wall time against the recorded baseline. Cluster assignment is still a human/agent
classification input, and the free-text count-basis fallback should be treated as
a residual risk. Future evaluations should use additional pre-registered cases and
explicit affected-method identifiers.

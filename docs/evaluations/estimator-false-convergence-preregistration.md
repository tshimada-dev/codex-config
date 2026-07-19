# Estimator false-convergence replay pre-registration

## Frozen boundary

This evaluation tests only the parent-synthesis behavior described by Issue #18.
It does not recreate the unavailable private `estimation-benchmarks` repository,
rerun every estimation pass from raw requirements, or claim a new blind estimate.

The input is the public Run #2 evidence in Issue #18. The evaluator supplies
method/cluster values to an isolated execution agent without the actual-effort
answer key. The answer key is used only by the scoring harness after submission.

## Frozen acceptance criteria

| ID | Required observable result | Evidence |
| --- | --- | --- |
| `AC-18-1` | Correlated methods form one vote. Each eligible cluster representative is the median of its plausible method centers; the neutral planning center is the median of eligible cluster representatives. | Machine-readable synthesis output and regression test. |
| `AC-18-2` | Agreement inside a cluster cannot raise convergence confidence. Shared count, productivity, lifecycle, and risk assumptions are emitted before confidence is assigned. | Cluster audit and confidence fields. |
| `AC-18-3` | Every plausible independent cluster appears in the decision ledger and changes the neutral center. A cluster may be rejected only with evidence-specific omitted scope or incompatibility; “best matches accepted scope” alone is insufficient. | Decision ledger and rejection validation. |
| `AC-18-4` | On the frozen Run #2 parent input, the candidate center is closer to the published actual mean than the recorded 1,200-hour center and is inside the published 431-943-hour range, or an evidence-specific divergence explanation is emitted. | Hidden-answer scoring after the isolated run. |
| `AC-18-5` | Untraced invented counts stop a method from becoming a center vote. A derived count more than 25% above the explicit value is also restricted to sensitivity-only until confirmed. | Count-audit status and regression test for 94 versus 57. |

## Frozen algorithm

1. Validate that every method has a cluster and its dominant count,
   productivity, lifecycle, and risk bases.
2. Exclude only methods marked `rejected` with a non-empty evidence-specific
   reason. Keep all `plausible` methods.
3. For each cluster, calculate one representative as the arithmetic median of
   its plausible method centers. The number of methods does not change vote
   weight.
4. Calculate the neutral planning center as the arithmetic median of the
   eligible cluster representatives. This is the default output; an override
   must name excluded/rejected cluster evidence and is not exercised in this
   replay.
5. Set convergence confidence to `supported` only if at least two independent
   cluster representatives differ by no more than 20% of their midpoint.
   Agreement within one cluster never counts.
6. For each count audit:
   - any positive `untraced_inferred_value` produces `STOP_UNTRACED_COUNT`;
   - otherwise, `(derived - explicit) / explicit > 0.25` produces
     `SENSITIVITY_ONLY_COUNT_INFLATION`;
   - otherwise it passes.

## Frozen comparison and scoring

The baseline is the published Run #2 result: center 1,200 hours, range
920-1,760 hours, and UUCP 94 versus the published 57. It is recorded evidence,
not re-executed output, so operation count and elapsed time are not compared.

The candidate passes only if all five acceptance criteria pass. Also record:

- arithmetic correctness;
- regression-test result;
- changed-file scope;
- isolated execution operations and elapsed time;
- instruction length;
- residual risk and non-generalizable limits.

No single replay establishes universal superiority. If correctness is tied,
prefer the simpler rule and smaller maintenance surface.

## Answer-key isolation

The execution agent receives the fixture and candidate instructions but not:

- actual efforts 587 / 943 / 431 / 829;
- actual range 431-943;
- actual mean 697.5;
- the expected candidate center.

The parent records the exact Git blob/hash of this pre-registration before the
candidate run. Any change after execution invalidates the comparison.

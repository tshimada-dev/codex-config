# Estimator vs. Veteran: A Scope-Controlled Retrospective

## Evidence boundary

This case study reconstructs a comparison recorded in public [tracking issue #10](https://github.com/tshimada-dev/codex-config/issues/10). It does not use the original private requirements, workbook, company name, customer name, prices, or source files. No fresh benchmark run was possible from the published record alone.

The result is therefore a retrospective audit of the published aggregate numbers, not an independent reproduction and not evidence that one estimating method is generally superior.

## Question

The original record asked why an estimator Skill produced an AI-assisted value of 450 person-days when an experienced estimator reported 170 person-days without AI and 115 person-days with AI. After a thinner implementation scope was supplied, the Skill produced a human-effort estimate of 175 person-days and a WBS most-likely value of 189 person-days.

The useful question is not simply “which number won?” It is:

1. How much of the visible disagreement disappears after scope alignment?
2. Which comparisons are genuinely like-for-like?
3. Which attribution claims can be recalculated from the public evidence?
4. What residual uncertainty remains?

## Reconstruction rules fixed before calculation

To avoid selecting a convenient interpretation after seeing the results, this document uses these rules:

1. Use only values explicitly published in issue #10.
2. Preserve each value's published basis. Do not relabel the initial AI-assisted 450 as human effort or the scope-aligned human 175 as AI-assisted effort.
3. Treat 175 versus 170 as the primary like-for-like human-effort comparison.
4. Treat 175 versus 115 only as a diagnostic of the reported AI-adjustment residual, not as an independent method comparison.
5. Show every arithmetic formula and denominator.
6. Mark a source attribution as “reported, not independently reproducible” when the public record omits its decomposition.
7. Do not generalize from this single, sanitized case.

## Published observations

| Observation | Person-days | Basis in the public record | Comparable to |
|---|---:|---|---|
| Initial Skill result | 450 | AI-assisted estimate before thin-scope clarification | Neither veteran value without further decomposition |
| Veteran human estimate | 170 | Human effort | Scope-aligned human estimate, 175 |
| Veteran AI-assisted estimate | 115 | AI-assisted effort | Diagnostic comparison with the reported residual only |
| Scope-aligned Skill estimate | 175 | Human effort after thin-scope assumptions | Veteran human estimate, 170 |
| Scope-aligned WBS most likely | 189 | WBS most-likely value | Supporting audit value, not the chosen comparison center |

Source: [issue #10, “重要な実証結果”](https://github.com/tshimada-dev/codex-config/issues/10).

## Controlled reconstruction procedure

1. Freeze the published observations above.
2. Record the initial disagreement without pretending that 450 and 170 share the same AI basis.
3. Introduce the already-reported intervention: the veteran's thinner scope assumptions.
4. Compare the scope-aligned human estimate, 175, with the veteran human estimate, 170.
5. Calculate the AI residual separately using 175 and 115, while retaining the basis mismatch warning.
6. Audit the source's “about 85%” attribution against the public aggregate values.
7. Record limitations and improvement work rather than converting this case into a universal accuracy claim.

## Recalculable results

### Initial visible disagreement

- Ratio to veteran human estimate: `450 / 170 = 2.647`, or about `2.65x`.
- Relative excess over veteran human estimate: `(450 - 170) / 170 = 164.7%`.
- Ratio to veteran AI-assisted estimate: `450 / 115 = 3.913`, or about `3.91x`.

These ratios explain why the source described an approximately three-to-four-fold disagreement, but the denominator matters: 450 is 2.65 times 170 and 3.91 times 115.

### Like-for-like human estimate after scope alignment

- Absolute difference: `175 - 170 = 5` person-days.
- Relative difference: `(175 - 170) / 170 = 2.9%`.

Within the published aggregates, the scope-aligned human estimate is close to the veteran human estimate. This supports the narrower claim that scope interpretation dominated the visible human-estimate disagreement in this case.

### Reported AI-adjustment residual

- Absolute difference: `175 - 115 = 60` person-days.
- Relative to the veteran AI-assisted value: `(175 - 115) / 115 = 52.2%`.
- Reduction from 175 required to reach 115: `(175 - 115) / 175 = 34.3%`.

The source's “about 50%” statement is reproducible when 115 is the denominator. This remains a diagnostic comparison because 175 is labeled human effort and 115 is labeled AI-assisted effort.

### Why the reported 85% attribution is not independently reproducible

The public issue reports that about 85% of the original gap was caused by scope interpretation. It does not publish the underlying line-level decomposition or the formula used for that percentage.

A naive aggregate gap-closure calculation would be:

`((450 - 170) - (175 - 170)) / (450 - 170) = 98.2%`

That 98.2% value must not replace the reported 85%. The calculation crosses an AI-assisted initial value and a human-effort scope-aligned value, so it changes more than scope. The defensible record is:

- `about 85%`: source-reported attribution, not independently reproducible from the public aggregates;
- `98.2%`: mechanically visible aggregate gap closure, not a clean scope-attribution estimate.

## Conclusion supported by this record

The published evidence supports three bounded conclusions:

1. Once the thinner scope was supplied, the Skill's human estimate (175) was within 5 person-days, or 2.9%, of the veteran human estimate (170).
2. Scope interpretation was a major driver of the original visible disagreement, but the exact 85% attribution cannot be independently reconstructed from the sanitized public data.
3. The remaining AI-adjustment comparison was about 52% above the veteran AI-assisted value when measured against 115, motivating stricter scope-responsive AI classification.

This case does not establish general estimator accuracy, causal superiority, or expected performance on other projects.

## Improvements connected to the finding

- [Issue #4](https://github.com/tshimada-dev/codex-config/issues/4) made AI adjustment line-level, fixed coefficient authority, required scope-driven reclassification, and added a conservatism warning. It is now completed.
- [Issue #3](https://github.com/tshimada-dev/codex-config/issues/3) remains the calibration-loop work needed to replace one-off comparison with measured estimate-to-actual evidence.
- A pre-estimation scope gate remains an important follow-up: implementation approach, exclusions, acceptance ownership, and testing responsibility should be explicit before estimating.

## Reproduction checklist

Anyone can reproduce the arithmetic in this document without private inputs:

1. Read the five published observations from issue #10.
2. Evaluate the formulas exactly as written above.
3. Confirm that 175 versus 170 is the only like-for-like human comparison.
4. Confirm that the 85% attribution lacks a published decomposition and remains source-reported.
5. Confirm that no statement relies on a company, person, price, private workbook, or customer file.

The repository's validation test fixes these values, formulas, links, evidence labels, and confidentiality boundaries so later edits cannot silently strengthen the claim.

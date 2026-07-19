# Estimator actual-productivity calibration evidence

## Decision boundary

Issue #3 requires an actual-based coefficient table, at least one method that uses
a measured anchor instead of an assumption, and an operational estimate-to-actual
recording procedure.

The referenced private benchmark repository and named calibration ledger were not
available through the connected GitHub installation or the scoped local workspace
search. No private actual or customer artifact was inferred or fabricated.

Three alternatives were considered:

1. Wait for organization-specific completed-project actuals. This remains the
   highest-relevance future source, but it is unavailable now.
2. Create a synthetic coefficient table. **Synthetic coefficients were rejected**
   because they cannot satisfy an actual-based acceptance criterion.
3. Use a public peer-reviewed multiple-case actual dataset with explicit units,
   scope, size, and effort. This was selected because it is measured, auditable,
   reversible when better local actuals arrive, and directly applicable to the
   existing UCP method with a unit-compatibility gate.

## Source and calculation

The selected source is the final published version of Anda, Benestad, and Hove,
ISESE 2005,
[DOI 10.1109/ISESE.2005.1541849](https://doi.org/10.1109/ISESE.2005.1541849),
also indexed by [Simula](https://www.simula.no/research/multiple-case-study-effort-estimation-based-use-case-points).
Four companies implemented equivalent functionality from the same nine-use-case
Java web-system specification. Published actual effort was 587, 943, 431, and 829
hours. Figure 2 on pages 412-413 of the final published version reports 57 UUCP,
`TCF = 0.6`, `EF = 0.605`, 20.619 adjusted UCP, and a 413-hour estimate.

The 20-page draft currently downloadable from the Simula record is not the same
version: it shows `57 * 7.5 = 430 hours` and contains neither 20.619 nor 413. The
adjusted denominator is therefore cited only to the final DOI version; the Simula
link supplies an institutional publication record, not evidence for those final
page values.

The repository CSV recalculates every coefficient. For the current method's
adjusted-UCP formula:

```text
company productivity = actual hours / 20.619 adjusted UCP / 8 hours per day
four-company measured range = 2.613-5.717 person-days per adjusted UCP
four-company mean = 697.5 / 20.619 / 8 = 4.229 person-days per adjusted UCP
```

The 57-point and adjusted-UCP denominators remain separate. The benchmark is
guarded by scope, lifecycle, process, team, technology, and non-functional
comparability checks. It is not a universal default.

## Acceptance mapping

| ID | Expected result | Evidence | Result |
| --- | --- | --- | --- |
| `AC-3-1` | `references/` contains an actual-based productivity/coefficient table. | `actual-productivity-calibration.csv` has four source-identified actual rows; the regression test recomputes all coefficients. | PASS |
| `AC-3-2` | At least one method uses a measured anchor rather than an assumption. | `use-case-points-pass.md` requires `local actual > compatible measured benchmark > heuristic/judgment` and connects the compatible adjusted-UCP range. | PASS |
| `AC-3-3` | An estimate-to-actual difference-recording procedure exists. | `analogy-calibration-pass.md` defines the post-delivery procedure, formulas, privacy boundary, and `calibration-ledger-template.csv`. | PASS |

## Verification

Focused command:

```powershell
python -m unittest -v test_actual_productivity_calibration.py
```

Working directory:
`skills/codex-effort-estimator/scripts`.

The test checks source rows and arithmetic, coefficient-unit compatibility, source
priority, ledger schema and formulas, exact English/Japanese source blobs, and CI
registration. Repository CI runs the same command.

## Adoption and residual risk

The measured public benchmark is adopted as a guarded fallback, not as an
organization-specific baseline. Comparable local actual remains higher priority.
Rows with mismatched delivered scope cannot be promoted without normalization,
and one result cannot overwrite a range.

The evidence covers one small 2005 Java web system implemented four times. It
does not establish general UCP accuracy or calibrate function points, reports,
screens, AI assistance, or distributed systems. A future local dataset should be
added row-by-row and compared against this benchmark rather than silently
replacing it.

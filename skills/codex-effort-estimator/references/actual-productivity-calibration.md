# Actual Productivity Calibration

Use this reference when a UCP estimate needs a measured productivity anchor. It
provides one public, peer-reviewed actual dataset and a guarded path for replacing
it with more comparable local actuals.

## Evidence boundary

The source is Anda, Benestad, and Hove, “A multiple-case study of software
effort estimation based on use case points,” ISESE 2005,
[DOI 10.1109/ISESE.2005.1541849](https://doi.org/10.1109/ISESE.2005.1541849).
The [Simula publication record](https://www.simula.no/research/multiple-case-study-effort-estimation-based-use-case-points)
indexes the work. The final published IEEE/ISESE version identified by the DOI
reports these facts:

- four companies implemented equivalent functionality for the same nine-use-case
  Java web-system specification;
- actual effort, including all project activities, was 587, 943, 431, and 829
  person-hours;
- the published unadjusted size was 57 points;
- Figure 2 on pages 412-413 of the final published version reports 57 UUCP,
  `TCF = 0.6`, `EF = 0.605`, 20.619 adjusted UCP, and a 413-hour method estimate;
- development-process and quality emphasis differed across the companies, so the
observed productivity spread is material evidence rather than noise to discard.

The 20-page draft currently downloadable from the Simula record is a different
version: it shows an unadjusted `57 * 7.5 = 430 hours` example and does not contain
20.619 or 413. Therefore the adjusted values in this calibration are bound only
to the final published DOI version, while the Simula link is used only as the
institutional publication record. Do not treat the two files as identical.

`actual-productivity-calibration.csv` records only those published facts and
transparent derived coefficients. It contains no customer or private-project
data.

## Recalculable coefficients

For each company:

```text
hours_per_unadjusted_point = actual_effort_hours / 57
hours_per_adjusted_ucp = actual_effort_hours / 20.619
person_days_per_adjusted_ucp = hours_per_adjusted_ucp / 8
```

The four-company actual range compatible with this repository's adjusted-UCP
formula is **2.613-5.717 person-days per adjusted UCP**. The arithmetic mean is:

```text
mean_actual_hours = (587 + 943 + 431 + 829) / 4 = 697.5
mean_productivity = 697.5 / 20.619 / 8 = 4.229 person-days per adjusted UCP
```

The mean is a center for this measured case set, not a universal default.

## Unit compatibility rule

This repository calculates `UCP = UUCP * TCF * ECF`, then multiplies adjusted UCP
by `productivity_person_days_per_ucp`. Use the `person_days_per_adjusted_ucp`
column with that formula.

Do not mix the 57-point denominator with adjusted UCP. The
`hours_per_unadjusted_point` column is retained only to reproduce the source's
published size basis and Issue evidence. Multiplying adjusted UCP by that column
would understate effort.

## Applicability and source priority

Use this priority exactly:

`local actual > compatible measured benchmark > heuristic/judgment`

Apply the Anda measured range only when the current work is reasonably comparable
on the dimensions below:

- use-case boundaries and transaction counting;
- small web/business-system scale rather than a large distributed platform;
- lifecycle coverage, especially whether actuals include analysis, design,
  project management, testing, and acceptance;
- team capability and technology familiarity;
- non-functional requirements, process weight, and code-quality expectations.

If important dimensions differ, keep the benchmark visible but reject it as a
direct coefficient. Explain the mismatch and use a wider range or a better local
anchor. Never select a coefficient merely because it moves the result toward
another method.

## Using the measured anchor in a UCP pass

1. Calculate UUCP, TCF, ECF, and adjusted UCP from current source facts.
2. Check for comparable local actuals first.
3. If none exist, evaluate the applicability dimensions above.
4. When compatible, use 2.613 / 4.229 / 5.717 person-days per adjusted UCP as the
   measured low/base/high productivity anchor and identify the source as
   `public_peer_reviewed_actual`.
5. When only part of the lifecycle is in scope, do not silently scale the measured
   coefficients. Either establish an evidence-backed scope factor or reject the
   anchor.
6. Report the coefficient source, compatibility decision, and remaining process
   uncertainty next to the UCP result.

## Local actual promotion

After a project actual is accepted, record it using
`calibration-ledger-template.csv` and the post-delivery procedure in
`analogy-calibration-pass.md`. A local row outranks this benchmark only when its
scope fingerprint, size basis, units, and lifecycle coverage are known. Do not
replace a coefficient from one result; retain rows individually until a comparable
sample supports a new range.

## Limits

This is one nine-use-case system implemented four times in 2005. It establishes a
measured anchor and an auditable calibration loop, not general UCP accuracy. It
does not calibrate function points, screens, reports, AI assistance, or modern
distributed-system productivity.

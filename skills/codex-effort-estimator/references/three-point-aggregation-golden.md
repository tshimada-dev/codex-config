# Three-Point Aggregation Golden Case

Use this deterministic case to check range synthesis. It exists to prevent regressions back to endpoint-sum ranges.

## Input

Fourteen WBS-style rows with low / most likely / high values:

| Row | Low | Most likely | High |
|---:|---:|---:|---:|
| 1 | 42.0 | 75.0 | 132.0 |
| 2 | 41.5 | 70.0 | 119.5 |
| 3 | 38.0 | 65.0 | 110.0 |
| 4 | 32.5 | 55.0 | 92.5 |
| 5 | 30.0 | 50.0 | 84.0 |
| 6 | 27.0 | 45.0 | 75.0 |
| 7 | 26.0 | 42.0 | 68.0 |
| 8 | 24.5 | 38.0 | 60.5 |
| 9 | 24.0 | 35.0 | 54.0 |
| 10 | 21.0 | 32.0 | 51.0 |
| 11 | 19.0 | 28.0 | 43.0 |
| 12 | 18.5 | 25.0 | 36.5 |
| 13 | 13.5 | 18.0 | 25.5 |
| 14 | 3.074 | 20.0 | 33.926 |

## Expected Calculation

Use:

```text
expected = (low + 4 * most_likely + high) / 6
standard_deviation = (high - low) / 6
variance = standard_deviation ^ 2
total_expected = sum(expected)
total_standard_deviation = sqrt(sum(variance))
90_percent_ci = total_expected +/- 1.645 * total_standard_deviation
```

Expected results, rounded for stakeholder output:

| Metric | Expected |
|---|---:|
| Sum most likely | 598.0 |
| Total expected | 623.0 |
| Total standard deviation | 31.2 |
| 90% CI low | 572 |
| 90% CI high | 674 |

Do not report the endpoint sum as the probabilistic range. Endpoint sums are a fully correlated scenario:

| Metric | Value |
|---|---:|
| Sum low | 360.6 |
| Sum high | 985.4 |

If this input came from WBS rows, label the CI as `WBS-derived variance aggregation`, not as an independent PERT estimate.

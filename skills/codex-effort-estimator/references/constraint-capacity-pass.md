# Constraint Capacity Pass

Use this reference for an independent feasibility and capacity estimate based on delivery constraints such as deadline, review gates, staffing, parallelism, procurement cadence, acceptance windows, and required deliverables.

This pass does not replace effort estimation. It creates a constraint-based envelope that checks whether proposed person-days and calendar plans are plausible.

## Scope

Estimate feasible person-day envelope and staffing/calendar implications. Do not estimate price or rates unless explicitly asked.

## Independence Rules

1. Do not read or use WBS totals, WBS line estimates, WBS-derived PERT, component-unit totals, parent synthesis, prior estimate artifacts, or expected final ranges.
2. Use only source-visible constraints, user-provided staffing assumptions, and this reference.
3. Do not infer a preferred effort number from WBS. Calculate feasible lower/upper envelopes from calendar and staffing logic.
4. Keep person-days and calendar duration separate.

## Procedure

1. List the source files or text blocks inspected.
2. Extract constraints:
   - contract start/end or target delivery date
   - review gates and acceptance periods
   - required meetings or reports
   - stakeholder availability
   - deployment windows
   - fixed deliverables
   - assumed team size or skill mix, if given
3. If staffing is unknown, define plausible staffing scenarios, such as 1.0, 2.0, 3.0, and 4.0 FTE.
4. Estimate effective working capacity:

```text
gross_capacity = workdays * FTE
net_capacity = gross_capacity * focus_factor
delivery_capacity = net_capacity - review_wait_buffer - fixed_coordination_buffer
```

5. Identify minimum irreducible effort from fixed overheads, review cycles, acceptance, documentation, deployment, and coordination.
6. Produce:
   - feasible low effort envelope
   - feasible central capacity
   - feasible high effort envelope before calendar or staffing becomes unrealistic
   - staffing or schedule implications
7. State whether a candidate final range would be feasible only in parent synthesis after this pass is complete.

## Output Schema

Return:

- Source files inspected.
- Constraint table with `Constraint`, `Value`, `Basis`, and `Impact`.
- Staffing/capacity scenario table with `Scenario`, `Workdays`, `FTE`, `Focus factor`, `Net capacity`, `Buffers`, and `Feasible delivery capacity`.
- Fixed overhead and irreducible effort notes.
- Feasible effort envelope and calendar implications.
- Risks if effort exceeds feasible capacity.
- Assumptions and confirmation questions.
- Confidence level.

Do not use conclusions from other estimators. Do not tune capacity to match WBS.

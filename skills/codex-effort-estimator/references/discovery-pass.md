# Discovery Pass

Use this reference when implementation scope is too unclear for a defensible delivery estimate.

## Scope

Estimate discovery, requirements definition, investigation, prototype, and decision work in person-days. Keep discovery effort separate from implementation effort.

## Procedure

1. List the source files or text blocks inspected.
2. Identify why implementation estimating is unstable:
   - Missing requirements, acceptance criteria, or stakeholder decisions.
   - Unknown data formats, data quality, migration volume, or legacy behavior.
   - Report/template fidelity not confirmed.
   - Integration, authentication, infrastructure, security, or operation constraints unknown.
   - Unclear phase gates, deliverables, review cycles, or procurement constraints.
3. Define discovery work packages:
   - Stakeholder interviews and workshops.
   - Current-work analysis and requirement definition.
   - Data/report/template investigation.
   - Technical spike or prototype.
   - Integration/environment confirmation.
   - Acceptance criteria and deliverable confirmation.
   - Estimate refresh and implementation planning.
4. Estimate each discovery work package with low / likely / high person-days.
5. State what implementation estimate can be produced after discovery and which assumptions remain.

## Output Schema

Return:

- Source files inspected.
- Why implementation estimating is not yet reliable.
- Discovery WBS table with `Work package`, `Purpose`, `Low`, `Likely`, `High`, and `Output`.
- Total discovery low / likely / high person-days.
- Decisions and artifacts required before implementation estimating.
- Optional provisional implementation range only if the user asks, clearly labeled as low confidence.
- Confidence level.

Do not hide discovery effort inside implementation contingency.

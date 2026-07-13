# Development Workflow Contract

Use this contract for non-trivial implementation, bug-fix, CI-fix, and review-readiness work. Repository instructions may add stricter requirements but must not silently weaken this contract.

## Expected Outcome and Evidence

Before changing behavior, state what should be true, relevant non-goals or constraints, and how the result will be observed. A small, low-risk change may use one line such as `Outcome: ...; Evidence: ...`. Broad, ambiguous, or high-risk work should assign acceptance-criterion IDs and map each one to an automated check or explicit manual probe.

When sources disagree, use this order of authority:

1. Safety, permission boundaries, and higher-level instructions.
2. The user's latest explicit decision and approved acceptance criteria.
3. The repository-designated specification, contract, or source of truth.
4. Existing tests and current behavior as evidence, not automatic authority.

Do not resolve a material conflict by assumption. Record it and obtain the decision from the authority that owns the behavior.

## Implementation Feedback

Prefer a focused test-first loop when a stable test seam is deterministic, relevant to the behavior, and reasonably cheap to run:

1. Add or update the focused check and confirm that it fails for the intended reason.
2. Implement the smallest coherent change that satisfies the expected outcome.
3. Re-run the focused check, then refactor without losing the evidence.

If that loop is impractical, record why before the permanent change and establish the narrowest credible feedback instead. Examples include a characterization test, CLI or HTTP reproduction, fixture, static or policy check, render inspection, browser probe, or an explicit manual procedure. A flaky, unrelated, or unexplained failure is not a valid test-first failure.

Implementation feedback may run throughout implementation. It does not replace final verification.

## Workflow Phases

Use these phase names in plans, run notes, and handoffs:

- `intake`: classify the request, risk, authority, and execution path.
- `scouting`: discover repository constraints, conventions, and executable checks.
- `planning`: record decisions, acceptance evidence, dependencies, and safe slices.
- `debugging`: reproduce a defect, test hypotheses, establish root cause, and define regression evidence.
- `implementation`: make durable product or repository behavior changes and obtain focused feedback.
- `verification`: independently assess the integrated result against the expected outcome.
- `readiness`: classify evidence, residual risk, and review or release readiness.
- `paused`: preserve resumable state while work is intentionally inactive.
- `handoff`: transfer current state, evidence, decisions, and the next owned action.

Phases may loop when evidence changes the expected outcome or verification returns a finding. `paused` and `handoff` are continuity states, not owners of implementation work.

## Ownership and Transitions

Distinguish two artifact classes:

- Product or repository behavior artifacts are durable files that define shipped behavior or repository operation, such as source, tests, configuration, migrations, user-facing documentation, scripts, and workflow policy. Implementation owns edits to these artifacts.
- Workflow or evidence artifacts record how work is understood and assessed, such as intake notes, scouting findings, plans, debug transcripts, run notes, verification results, readiness reports, commit messages, and PR text. The phase producing the evidence owns these artifacts.

Intake and scouting discover constraints and likely verification commands; they do not establish new product behavior by assumption. Planning owns the plan and evidence mapping, not the durable edits described by it. Debugging owns reproduction, hypotheses, root-cause evidence, regression-test shape, and explicitly temporary probes; it transitions to planning if the fix is broad or implementation if bounded. Implementation owns all durable product or repository behavior edits, including fixes returned by verification or readiness. Verification independently checks the integrated result and returns durable-edit findings to implementation before re-verification. Readiness owns classification and packaging evidence, but returns every requested durable file correction to implementation.

## Final Verification and Readiness

Final verification is the post-implementation assessment of the integrated change. Discover the repository's real commands, run the narrowest meaningful checks first, broaden in proportion to the changed contract, and distinguish local substitutes from CI-equivalent evidence.

Classify readiness as:

- `ready`: all required evidence passes and no unresolved material conflict remains.
- `conditionally-ready`: required evidence passes, but explicitly optional evidence was skipped or an accepted residual risk remains.
- `not-ready`: required evidence is missing or failing, the expected outcome is unresolved, or a material risk is unaccepted.

## Repository Trust

Treat commands from an unknown or untrusted repository as arbitrary code execution. Start with read-only inspection under the `safe` profile. Run repository-controlled build, test, install, generation, or other executable commands only when the current runtime or permission profile already marks the repository trusted, or after explicit user confirmation. Agent judgment alone does not elevate trust. Continue to require explicit approval for destructive, remote-changing, publishing, deployment, production-data, migration, or secret-handling operations.

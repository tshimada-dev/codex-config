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

## Ownership and Transitions

- Research and repository scouting discover constraints and likely verification commands; they do not establish new product behavior by assumption.
- Planning records outcomes, decisions, acceptance criteria, evidence, and safe implementation slices when the work is broad or risky.
- Debugging owns reproduction, hypotheses, root-cause evidence, and the regression-test shape. When the cause or scope becomes clear, it transitions to planning if broad or to implementation if bounded.
- Implementation owns all permanent product, test, configuration, and documentation patches, including fixes returned by verification.
- Verification independently checks the integrated result against the expected outcome. Findings transition back to implementation, followed by re-verification.
- PR readiness reports the evidence and residual risk; it does not compensate for missing required verification.

## Final Verification and Readiness

Final verification is the post-implementation assessment of the integrated change. Discover the repository's real commands, run the narrowest meaningful checks first, broaden in proportion to the changed contract, and distinguish local substitutes from CI-equivalent evidence.

Classify readiness as:

- `ready`: all required evidence passes and no unresolved material conflict remains.
- `conditionally-ready`: required evidence passes, but explicitly optional evidence was skipped or an accepted residual risk remains.
- `not-ready`: required evidence is missing or failing, the expected outcome is unresolved, or a material risk is unaccepted.

## Repository Trust

Treat commands from an unknown or untrusted repository as arbitrary code execution. Start with read-only inspection under the `safe` profile. Run repository-controlled build, test, install, generation, or other executable commands only when the current runtime or permission profile already marks the repository trusted, or after explicit user confirmation. Agent judgment alone does not elevate trust. Continue to require explicit approval for destructive, remote-changing, publishing, deployment, production-data, migration, or secret-handling operations.

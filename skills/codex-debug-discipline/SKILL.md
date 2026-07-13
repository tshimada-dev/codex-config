---
name: codex-debug-discipline
description: Diagnose bugs, failing tests, flaky behavior, performance regressions, wrong output, crashes, or user reports that something is broken. Use when Codex must reproduce, instrument, test hypotheses, establish root cause, and define regression evidence for a defect.
---

# Codex Debug Discipline

Use this skill to debug from evidence instead of vibes.

## Shared Development Contract

<!-- workflow-invariant: shared-contract -->
<!-- workflow-invariant: debug-handoff -->

Read and follow [`../../rules/development-workflow.md`](../../rules/development-workflow.md). Debugging establishes the observed failure, likely cause, and regression shape; it does not own durable product edits.

## Composition

This skill owns reproduction, falsifiable hypotheses, root cause analysis, probes, and regression shape. Use `codex-implementation-loop` for the durable patch once the likely cause is known. A trivial defect may continue directly in the same session without a formal handoff, but switch to the implementation loop before editing durable files. If the defect is in UI behavior, run `codex-ui-quality-gate` after the fix.

## Subagent Debugging

When subagents are available, prefer delegating parallel debug probes if they test distinct hypotheses or gather independent evidence:

- Good: one explorer traces logs, one builds a minimal repro, one inspects recent diffs or dependency changes.
- Bad: several agents editing the same suspected files or applying competing fixes.
- Require each agent to return the loop/probe used, observed result, hypothesis status, and next recommended step.
- Parent chooses the final hypothesis, owns the fix strategy, and ensures regression coverage.

## Required Shape

For trivial defects with an obvious cause and low blast radius, use a lightweight loop:

1. Confirm the symptom or code path.
2. Identify the nearest regression evidence and whether a stable test seam exists.
3. Switch to `codex-implementation-loop`; establish the failing focused test first when the stable seam exists, then make the smallest fix.
4. Re-run the original symptom check and regression evidence.
5. Report why full hypothesis branching was unnecessary.

For nontrivial defects, use the full loop:

1. Build a feedback loop that can show the failure:
   - failing test
   - CLI command
   - HTTP request
   - browser script
   - replay fixture
   - minimal harness
2. Confirm the loop matches the user's reported symptom.
3. Generate 2 to 5 falsifiable hypotheses.
4. Test one hypothesis at a time.
5. Establish the root cause and define regression evidence at the closest correct seam.
6. When a stable test seam exists, specify the focused regression test and the failure reason it should expose.
7. Switch to `codex-implementation-loop` to establish that failing test and make the durable fix. If no stable test seam exists, carry the recorded reason and narrowest credible alternative evidence into that loop.
8. Remove temporary instrumentation.
9. Re-run the original loop and the regression evidence.

## Isolation

- When asked to simulate, evaluate a skill, or diagnose a seeded bug, create the repro in a disposable temp/project directory unless the user names an existing target.
- Do not edit the skill file itself while evaluating it unless the user explicitly asks for direct edits.
- Keep a short debug transcript: failing loop, hypotheses, probes, fix, and final checks.

## Instrumentation

- Prefer debugger or narrow probes over broad logging.
- Tag temporary logs with a unique prefix such as `[DEBUG-8f3a]`.
- Remove all tagged logs before finishing.
- For performance bugs, measure before changing code.

## Hypothesis Format

```text
If <cause> is true, then <probe or change> will show <observable result>.
```

Do not stack multiple fixes before proving a direction.

## When No Repro Exists

After one bounded attempt to create a runnable loop, continue with static inspection if likely useful. Stop only when both runnable reproduction and code-path evidence are unavailable, or when further progress requires user-only artifacts.

When blocked, report:

- what was tried
- what evidence is missing
- what artifact would unblock the work

Ask for logs, traces, screenshots, sample inputs, environment details, or permission to add temporary instrumentation.

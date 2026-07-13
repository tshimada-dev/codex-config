# CI Fix Checklist

- Follow `../development-workflow.md`; identify the expected outcome and required evidence, not only the command that should turn green.
- Identify the failing job, step, command, and first meaningful error.
- Classify the failure as test, lint, typecheck, build, dependency, environment, flaky, or external service.
- Reproduce locally when practical with the same or narrowest equivalent command.
- If the failure exposes incorrect product behavior, use the debugging discipline to establish cause and regression shape.
- Transition to the implementation loop for the smallest relevant permanent fix, whether the cause is product behavior, configuration, dependency, or build logic.
- Re-run the failing command or a credible local equivalent.
- Do not treat a rerun-only green result, an unexplained flaky failure, or a narrower substitute as equivalent regression evidence.
- Record the failing evidence, fix, verification command, readiness, and any remaining CI risk in the active run note.

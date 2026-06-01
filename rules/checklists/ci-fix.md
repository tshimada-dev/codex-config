# CI Fix Checklist

- Identify the failing job, step, command, and first meaningful error.
- Classify the failure as test, lint, typecheck, build, dependency, environment, flaky, or external service.
- Reproduce locally when practical with the same or narrowest equivalent command.
- Fix the root cause with the smallest relevant change.
- Re-run the failing command or a credible local equivalent.
- Record the failing evidence, fix, verification command, and any remaining CI risk in the active run note.

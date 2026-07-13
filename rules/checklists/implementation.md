# Implementation Checklist

- Follow `../development-workflow.md`; confirm the expected outcome and evidence before changing behavior.
- If research notes or an active run note exist, re-read them before editing.
- Keep changes limited to the requested behavior and nearby tests/docs.
- Preserve user changes and avoid reverting unrelated files.
- Prefer existing helpers, types, conventions, and scripts over new abstractions.
- When a stable seam exists, establish the focused failing check before the permanent change. Otherwise record the exception and credible alternative feedback first.
- Treat focused red/green checks as implementation feedback; run and report final verification separately.
- Review the final diff for accidental churn, secrets, debug prints, and unrelated edits.
- If an active run note exists, update it with changed files, material decisions, evidence, and readiness.

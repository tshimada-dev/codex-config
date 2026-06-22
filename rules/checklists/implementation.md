# Implementation Checklist

- If research notes or an active run note exist, re-read them before editing.
- Keep changes limited to the requested behavior and nearby tests/docs.
- Preserve user changes and avoid reverting unrelated files.
- Prefer existing helpers, types, conventions, and scripts over new abstractions.
- For behavior changes, prefer a test-first loop: write or update the focused test, run it to confirm the expected failure when practical, implement the smallest change, then re-run focused and relevant broader checks.
- If test-first is impractical for a non-trivial behavior change, record why and use the narrowest credible alternative verification.
- Review the final diff for accidental churn, secrets, debug prints, and unrelated edits.
- If an active run note exists, update it with changed files and decisions that matter later.

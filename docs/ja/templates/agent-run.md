---
source: templates/agent-run.md
source_blob: dcfd9c1c257657c5df9c755591e32646e8b4d983
canonical: false
---

# Agent Run: <task-name>

この文書は `templates/agent-run.md` の日本語参考訳です。実際のテンプレートとして使う canonical は英語版です。

Location: `$HOME\.codex\runs\<repo-name>\YYYYMMDD-HHMM-<short-task>.md`。ただし repository が run-note convention を定めている場合はそれを優先する。
Started: `<YYYY-MM-DD HH:MM local>`
Last updated: `<YYYY-MM-DD HH:MM local>`
Phase: `intake | scouting | planning | debugging | implementation | verification | readiness | paused | handoff`

## Goal

<この作業が終わったとき、何が true になっているべきか。>

## Scope

- In scope:
- Out of scope:

## Expected Outcome and Evidence

小さく低リスクな変更では `Outcome: ...; Evidence: ...` の1行でよい。

広い、曖昧、高リスクな作業では次の対応表を使う。

| ID | Acceptance criterion | Evidence | Status |
| --- | --- | --- | --- |
| AC-1 | | | pending |

- Non-goals / constraints:
- Open decisions or authority conflicts:

## Research

### Relevant Files

-

### Findings

-

### Assumptions and Risks

-

## Decisions

| Decision | Rationale | Alternatives rejected |
| --- | --- | --- |
| | | |

## Implementation Plan

-

## Changes

- Product/repository behavior artifacts (implementation-owned):
- Workflow/evidence artifacts (phase-owned):

## Verification

- Implementation feedback:
- Format:
- Lint:
- Typecheck:
- Test:
- Build:
- CI:
- Readiness: `ready | conditionally-ready | not-ready`
- Residual risk:

## Current State

-

## Handoff

-

## Next Step

-

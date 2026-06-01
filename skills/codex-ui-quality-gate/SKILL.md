---
name: codex-ui-quality-gate
description: Verify frontend and visual changes with browser-based checks. Use when Codex edits UI, CSS, layout, responsive behavior, canvas/WebGL, images, animations, forms, navigation, accessibility, or any local web app that should be visually inspected before delivery.
---

# Codex UI Quality Gate

Use this skill after frontend changes and before the final report.

## Subagent UI Checks

When subagents are available, prefer delegating focused UI verification to a worker after the changed route and expected states are clear:

- Give the worker the URL, viewport targets, changed surfaces, interactions to exercise, and artifact rules.
- Ask for concise evidence: route, viewport, overflow status, console status, interactions tested, and screenshots path only if kept intentionally.
- Parent still decides whether visual quality is acceptable and whether more fixes are needed.

## Verification Steps

1. Start or reuse the local dev server when the app needs one.
2. Open the relevant page using the best available browser path:
   - Browser plugin / Codex in-app browser
   - Playwright
   - Puppeteer with installed Chrome
   - static DOM/CSS checks as a last resort
3. Check at least one desktop and one mobile-sized viewport for changed surfaces. Prefer `1280x800` and `360x720` unless the product has better target sizes.
4. Inspect:
   - layout stability
   - text overflow
   - obvious contrast issues
   - keyboard and pointer interactions
   - loading, empty, error, and success states when applicable
   - console errors
5. For canvas, WebGL, maps, or generated media, verify pixels are nonblank and correctly framed.
6. For normal DOM UI, capture or inspect visual evidence for each changed viewport when tooling supports it.
7. Fix issues found during the check and re-test the affected viewport.

## Browser Probes

Use concrete probes when possible:

- Route and viewport size.
- Console errors and warnings.
- Page-level overflow: `document.documentElement.scrollWidth > window.innerWidth`.
- Element overflow: important elements with `scrollWidth > clientWidth`.
- Bounds overflow: changed elements whose bounding box extends beyond the viewport.
- At least one relevant interaction or state transition.

Be careful with mobile emulation flags; they can change the CSS viewport in ways that hide or invent responsive issues.

Keep browser verification artifacts tidy:

- Store screenshots under an intentional path such as `docs/qa-screenshots/` only when the project should keep them.
- Keep temporary browser profiles outside the repo, or remove them before final delivery.
- Add ignore rules for generated screenshots/profiles when they are local-only evidence.
- Do not let Chrome profile files, caches, or raw automation logs become project deliverables.

## Design Discipline

- Match the existing app conventions before adding new visual language.
- Prefer dense, usable product UI over decorative marketing layout for tools and dashboards.
- Do not hide core workflows behind explanatory text.
- Keep fixed-format controls dimensionally stable.
- Avoid text overlap and viewport-scaled font sizes.

## Final Report

Mention:

- URL checked
- viewport sizes or device classes checked
- visible changed surfaces inspected
- console status
- interactions or states exercised
- tests or browser checks run
- any UI states not verified

If a browser check could not run, say why and provide the strongest substitute check that did run.

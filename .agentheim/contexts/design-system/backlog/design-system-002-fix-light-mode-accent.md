---
id: design-system-002
title: "Fix accent color contrast in light mode"
status: backlog
type: bug
context: design-system
created: 2026-05-26
depends_on: [design-system-001]
tags: [accessibility, light-mode, color]
related_adrs: []
prior_art: [design-system-001]
---

## Why
The amber accent color (#d4a853) fails contrast on light backgrounds (#fafafa).
Links and accented elements are hard to read in light mode.

## What
Choose an accent color variant for light mode that passes WCAG AA (4.5:1 ratio for text,
3:1 for UI components). Either darken the amber for light mode via a separate token, or
switch to a different accent hue that works on both dark and light backgrounds.

## Acceptance criteria
- [ ] Light mode accent color passes WCAG AA contrast against `--color-bg` (#fafafa)
- [ ] Dark mode accent color unchanged (#d4a853 still works on #111)
- [ ] Token name stays `--color-accent` — value differs per color scheme

## Notes
Option A: Use a darker amber in light mode via `@media (prefers-color-scheme: light)`
override of `--color-accent` (e.g., #8a6520).
Option B: Switch accent to a color that reads well on both schemes (e.g., a muted teal).

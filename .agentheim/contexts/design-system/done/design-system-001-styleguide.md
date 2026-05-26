---
id: design-system-001
title: "Feature: Styleguide — visual identity, dark mode, typography"
type: feature
status: done
context: design-system
depends_on: [infra-003]
completed: 2026-05-26
related_adrs: [0003]
---

# Feature: Styleguide

## Goal
Define and implement the complete visual identity for joshuatoepfer.de: color palette
(dark-first), typography scale, spacing system, and base component patterns. This is
the gate for all frontend work — no BC implements its UI before this task is done
and signed off by Joshua.

## Acceptance criteria
- [x] Dark mode is implemented as the primary mode via `prefers-color-scheme: dark`
- [x] A light mode fallback exists (even if minimal)
- [x] Color tokens are defined as CSS custom properties
- [x] Typography scale (headings, body, code, captions) is defined and applied globally
- [x] Base layout (header, footer, main content area, nav) is in place
- [x] The design renders correctly on mobile and desktop
- [x] **Joshua has reviewed the design in a browser and signed off** — note: amber accent on light mode flagged as poor contrast → tracked in design-system-002

## Notes
The design direction from the vision: modern, minimalist, dark-mode-first, "chic" feel.
Avoid visual clutter. Typography should carry the weight, not decorative elements.

Theme approach chosen: scratch-built (see ADR-0003). No theme gem dependency.

## Outcome
Implemented the full visual identity as scratch-built SCSS:
- `_sass/_tokens.scss` — CSS custom properties for dark/light color schemes (amber accent #d4a853),
  typography scale, spacing scale, and layout max-widths
- `_sass/_base.scss` — minimal reset, links, code, blockquote, tables
- `_sass/_typography.scss` — heading hierarchy, prose class, .meta and .caption utilities
- `_sass/_layout.scss` — site-wrapper (flex column), site-header/nav, site-main, site-footer
- `assets/css/main.scss` — entry point importing all partials
- `_layouts/default.html` — updated to link stylesheet, semantic HTML5 nav with aria labels
- `_config.yml` — added `sass: style: compressed`

`bundle exec jekyll build` passes. Human sign-off checkpoint remains open.

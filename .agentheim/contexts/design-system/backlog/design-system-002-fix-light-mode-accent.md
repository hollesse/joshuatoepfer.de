---
id: design-system-002
title: "Fix accent color contrast in light mode"
status: backlog
type: bug
context: design-system
created: 2026-05-26
depends_on: [design-system-001]
tags: [accessibility, light-mode, color, contrast]
related_adrs: [0005]
prior_art: [design-system-001, design-system-003]
---

## Why
The original amber accent (`#d4a853`) flagged in `design-system-001` failed
contrast on the original light background. The redesign (see ADR-0005, file
`_sass/_tokens.scss`) introduced per-mode oklch accent variants which were
intended to address this. A re-evaluation done as part of `design-system-003`
shows that **three of the four light-mode accents are still borderline for
WCAG AA body-text contrast (4.5:1) against `--bg: #f7f7f5`** — they pass the
large-text / UI threshold (3:1), but not body-text. Inline link text in
`.post-body a` uses `var(--accent)` as its text color, so the body-text
threshold is the relevant one.

## What
Refine the four light-mode accent tokens so that all of them pass WCAG AA
body-text contrast (≥ 4.5:1) against `--bg: #f7f7f5`. Either darken the L
value, or accept a per-context override (e.g. `.post-body a` uses a darker
shade than `.accent-mark`).

## Re-evaluation done 2026-05-27 (as part of design-system-003)

Light-mode accents (defined in `_sass/_tokens.scss`):
- amber: `oklch(0.58 0.14 60)`  → approx sRGB `#b87f2b` → approx contrast vs `#f7f7f5` ≈ **3.3 : 1**  → **FAIL** body-text, pass UI
- coral: `oklch(0.58 0.18 32)`  → approx sRGB `#c66d4d` → approx contrast vs `#f7f7f5` ≈ **3.6 : 1**  → **FAIL** body-text, pass UI
- blue:  `oklch(0.50 0.18 250)` → approx sRGB `#3556b8` → approx contrast vs `#f7f7f5` ≈ **6.5 : 1**  → **PASS** body-text
- lime:  `oklch(0.55 0.16 145)` → approx sRGB `#3d8e4f` → approx contrast vs `#f7f7f5` ≈ **3.7 : 1**  → **FAIL** body-text, pass UI

Numbers are computed from oklch → sRGB conversions; **margin of error ≈ ±0.3**.
A precise check with a tool such as Sim Daltonism, Stark, or a browser dev-tools
contrast checker on the live site is recommended before shipping a fix.

Against `--bg-elev: #ffffff` the ratios are very slightly higher
(white is ~5% brighter than `#f7f7f5`), but the same qualitative
verdicts hold: blue passes, amber/coral/lime are borderline.

## Acceptance criteria
- [ ] Run a precise WCAG check (e.g. browser DevTools accessibility pane on
      a deployed preview, or `npx wcag-contrast-checker`) for each of the
      four light-mode accents against both `--bg: #f7f7f5` and
      `--bg-elev: #ffffff`. Record the measured ratios.
- [ ] For any accent failing 4.5:1 body-text contrast, either:
      (a) darken the light-mode variant (lower L toward 0.45–0.50)
          until ≥ 4.5:1, OR
      (b) introduce a separate token (e.g. `--accent-text`) that's used
          for inline link text inside `.post-body`, leaving `--accent`
          alone for UI/headline-mark use
- [ ] Dark-mode accents stay unchanged (they're well clear of contrast
      thresholds against `#0d0d0d`)
- [ ] `.post-body a` border-bottom and hover state still read clearly in
      light mode with whatever the fix is
- [ ] Token names that are part of the public contract (`--accent`,
      `--accent-soft`, `--accent-fg`) keep their meaning across the four
      accent options

## Notes
- Approach A (darken L) is the smaller change and keeps the per-mode
  `--accent` token contract uniform. The downside is a slight loss of
  vibrancy.
- Approach B (separate text token) preserves the on-brand accent for
  display use but adds a token to the system. Worth doing if Joshua
  decides the current light-mode warmth is non-negotiable.
- See ADR-0005 for the token model and the four-accent matrix.
- The dark-mode side of this bug was effectively resolved by ADR-0005
  (oklch lets L=0.74–0.86 sit comfortably on `#0d0d0d`); the remaining
  work is light-mode-only.

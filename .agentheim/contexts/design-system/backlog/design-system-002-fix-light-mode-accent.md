---
id: design-system-002
title: "Fix accent color contrast in light mode"
status: backlog
type: bug
context: design-system
created: 2026-05-26
depends_on: [design-system-001, infra-006]
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

## Deferred 2026-05-28 — waiting on automated check

In the refinement conversation on 2026-05-28, Joshua looked at the
proposed new color values for both approach A (darken L) and approach B
(separate `--accent-text` token) and didn't like the visual result of
either: A loses too much light-mode warmth across the board, B adds
vocabulary the system doesn't strictly need.

A third path emerged from that conversation: **Option C — make
`.post-body a` use `color: inherit`** (i.e. body text color, not
accent), and rely on the already-animated underline as the link signal.
Tokens stay untouched. Light-mode accent warmth stays intact for
headline-marks, chips, and other display uses. WCAG-conformant by
design because link text is body text color.

But before picking C (or any fix), Joshua wants automated WCAG checks in
CI first — so the next refinement of this task is informed by concrete
pa11y-ci output (which pages, which elements, exact contrast ratios),
not estimates. That work is `infra-006`. Once `infra-006` lands and
produces its first failing run, this task gets re-refined with the
real failure output and a final fix path is chosen.

This task is therefore blocked on `infra-006`. `depends_on` updated.

## Fix-path options on the table (re-evaluate after infra-006 lands)
- **A** — darken `--accent` light-mode L values. Joshua rejected the
  proposed visual on 2026-05-28.
- **B** — separate `--accent-text` token. Joshua rejected the
  proposed visual on 2026-05-28.
- **C — `.post-body a` uses `color: inherit`.** Strong candidate.
  Tokens unchanged. Headline-marks keep their warmth. Animated
  underline carries the link signal. Worth proving against pa11y-ci's
  output before committing.
- **D** — underline + hover/focus coloring (link default body-color,
  hover lifts to accent). Two-state CSS; default state is
  WCAG-conformant, accent re-enters on interaction.
- **E** — bolder/larger link weight so links qualify as "large text"
  under WCAG (3:1 instead of 4.5:1). Affects reading flow.
- **F** — `.post-body a` gets `background: var(--accent-soft)`.
  Highlight aesthetic instead of color-conveying.
- **G** — a separate dark-neutral link color, independent of accent
  palette. Decouples link color from accent identity.

## Notes
- Original notes from the 2026-05-27 refinement (approach A vs B
  trade-offs) are superseded by the 2026-05-28 conversation above.
  Kept for history: approach A loses warmth, approach B adds a token.
- See ADR-0005 for the token model and the four-accent matrix.
- The dark-mode side of this bug was effectively resolved by ADR-0005
  (oklch lets L=0.74–0.86 sit comfortably on `#0d0d0d`); the remaining
  work is light-mode-only.

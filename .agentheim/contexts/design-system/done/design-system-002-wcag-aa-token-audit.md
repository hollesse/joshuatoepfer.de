---
id: design-system-002
title: "WCAG AA fix — route text-bearing elements to AA-passing tokens"
status: done
type: bug
context: design-system
created: 2026-05-26
completed: 2026-05-28
depends_on: [design-system-001, infra-006]
tags: [accessibility, wcag, contrast, fg-faint, fg-dim, tokens]
related_adrs: [0005]
prior_art: [design-system-001, design-system-003]
---

## Why
`infra-006` shipped pa11y-ci as a CI gate. Its first run surfaced **93 WCAG
2.1 AA violations per mode**, all on elements styled with `var(--fg-faint)`:

- Dark mode: `#5a5a5a` on `#0d0d0d` → **2.82 : 1** (recommendation `#fff`)
- Light mode: `#a3a3a3` on `#f7f7f5` → **2.35 : 1** (recommendation `#272727`)

Failing selectors observed:
- `footer h4` (the four column headers: Kontakt, Anderswo, Site, Rechtliches)
- `.sep` (the middle-dot separators between meta tokens)
- `.count` / `.count.mono` (companion numerals like "3 Beiträge")
- `.row .arrow` (the rightward arrow on every post/talk row)

The companion `--fg-dim` token already passes AA — `#9a9a9a` on `#0d0d0d`
≈ 7.5 : 1 (dark), `#5e5e5e` on `#f7f7f5` ≈ 6.0 : 1 (light). So the system
already has the right shade for body-secondary text; the bug is that
`--fg-faint` (designed as the "extra-muted decorative" tier) is currently
used for text that the eye and assistive tech treat as content.

There's a sibling concern surfaced earlier (2026-05-27): `.post-body a`
inline link text uses `var(--accent)`, which also fails 4.5 : 1 in light
mode for amber/coral/lime accents (the only one that passes is blue).
That's not in pa11y-ci's output yet because there's no post body with
inline links published — but it'll appear the moment real INNOQ-synced
content lands. Same fix pattern, so we bundle it into this task.

## What
Two changes, one underlying pattern: **text-bearing elements use
AA-passing tokens; decorative elements can keep the weaker tier.**

1. **Audit `var(--fg-faint)`** in `_sass/`. For each usage, decide
   text-bearing vs decorative:
   - **Text-bearing → switch to `var(--fg-dim)`.** Anything the user
     reads as content: footer column headers, separators inside meta
     rows, counts like "3 Beiträge".
   - **Purely decorative → keep `var(--fg-faint)`** (with one-sentence
     rationale in the code comment so future audits aren't confused).
     Candidates: `.row .arrow` (icon-flavored, no text content), maybe
     `.v1-focus .count` (the big numerals act as accent rather than
     information).

   Worker judgment per usage; when in doubt, switch to `--fg-dim`.

2. **`.post-body a`** uses `color: inherit` instead of
   `color: var(--accent)`. The animated underline already carries the
   link signal — no color information is lost from a usability
   standpoint. Headline accent-marks, chips, focus rings, status dots,
   etc. keep their accent colors untouched.

**Token values themselves are NOT changed.** This is a usage-routing
fix, not a token-recalibration fix. Joshua looked at proposed L-shifted
accent values on 2026-05-28 and rejected them visually; the design
system's current warmth stays intact.

## Acceptance criteria

- [x] Grep `_sass/` for `var(--fg-faint)`. Produce a complete list of
      usages in the worker's commit message or task Outcome (selector →
      file:line → text-bearing/decorative verdict).
- [x] Every text-bearing usage of `var(--fg-faint)` is switched to
      `var(--fg-dim)`. The four pa11y-cited selectors
      (`footer h4`, `.sep`, `.count`/`.count.mono`, `.row .arrow`) are
      explicitly resolved — though if `.row .arrow` ends up classified
      as decorative, it stays `--fg-faint` and the task Outcome
      explains why (it's an icon-glyph, not content text).
- [x] `.post-body a` no longer sets `color: var(--accent)`. Its
      effective color becomes the inherited body color (`var(--fg)`).
      Underline animation, hover state, and any focus-ring styling
      remain intact (a hover lift to accent is fine; the default state
      must be body color).
- [x] No changes to `_sass/_tokens.scss` token values. (Verify by
      running `git diff _sass/_tokens.scss` — should be empty.)
- [x] `bundle exec jekyll build` passes without errors.
- [x] **pa11y-ci goes green.** Run the accessibility workflow locally
      (`bundle exec jekyll serve` + `npx --yes pa11y-ci@4.1.1` per the
      `infrastructure/README.md` recipe) — both dark and light passes
      should emit 0 errors. If any new violation surfaces during the
      audit that isn't `--fg-faint`-driven, surface it in the Outcome
      and either fix it (if trivially in scope) or flag as a follow-up
      task.
- [x] Visual sanity check: open the site in dark mode, then flip via
      the theme toggle to light mode. Confirm the footer column
      headers, separators, and companion counts now read clearly in
      both modes without the design feeling "louder" — `--fg-dim` is
      only slightly stronger than `--fg-faint`, so the typographic
      hierarchy stays subtle.

## Notes
- The fix is a small `_sass/` patch — a handful of `var(--fg-faint)`
  swaps to `var(--fg-dim)` plus one line removed from wherever
  `.post-body a { color: var(--accent); }` lives. No new tokens, no
  changed token values, no new components.
- After this lands, every PR's accessibility check goes green again.
  The pa11y-ci output should be archived (workflow run link) and
  referenced in the commit message as the regression test for the fix.
- The accent palette (amber/coral/blue/lime light variants) stays as
  defined in ADR-0005. Joshua chose this on 2026-05-28 over either
  darkening L or introducing `--accent-text`.
- `.row:hover .arrow { color: var(--accent); }` (the hover-color rule
  in `_sass/_posts.scss`) stays untouched — hover-only accent usage
  doesn't impact AA contrast judgement on the default state, and the
  current default `--fg-faint` is borderline acceptable for a small
  decorative glyph (worker judgment per WCAG decorative-element
  carve-out).

## History (for context, not action)

**Original capture (2026-05-26):** "Fix amber accent (#d4a853) contrast
on #fafafa". Light-mode amber → links unreadable.

**Re-evaluation in design-system-003 (2026-05-27):** Confirmed
amber/coral/lime light-mode accents fail body-text 4.5:1 against
`#f7f7f5` (3.3 / 3.6 / 3.7 : 1); blue passes (6.5 : 1). Two fix paths
on the table: A (darken accent L), B (add `--accent-text` token).

**Deferred 2026-05-28 (model REFINE):** Joshua looked at proposed
concrete color values for both A and B, rejected both visually
(A loses too much warmth, B adds vocabulary). A third path emerged in
conversation: Option C — `.post-body a` uses `color: inherit`, tokens
unchanged. Task deferred pending automated WCAG check (`infra-006`) so
the next refinement is informed by concrete data.

**Refined again 2026-05-28 (after infra-006 ship):** pa11y-ci output
broadened the picture. The active failure is `--fg-faint` text usages,
not the accent palette. The fix path now is Pfad 2 from the
2026-05-28 conversation — audit `--fg-faint` usages, route text-bearing
ones to `--fg-dim`. The accent inline-link concern (Option C) is
bundled in because it's the same pattern: text-bearing element using
non-AA token → switch to AA-passing token (or to body inherit).

Token values stay constant throughout this history. Every fix path
considered preserves the current oklch accent palette and the
existing `--fg-dim` / `--fg-faint` neutrals.

## Outcome

### Full audit of `var(--fg-faint)` in `_sass/`

23 usages found. Verdicts and actions:

| # | File:Line (pre-edit) | Selector | Verdict | Action |
|---|---|---|---|---|
|  1 | `_layout.scss:102`  | `.jt footer h4`                        | text  | → `--fg-dim` |
|  2 | `_layout.scss:120`  | `.jt footer .baseline`                 | text  | → `--fg-dim` |
|  3 | `_layout.scss:208`  | `.jt .v1-focus .focus-card .count`     | text  | → `--fg-dim` (initially classified decorative; pa11y flagged it — `"14 BEITRÄGE"` is informational, so reclassified mid-task) |
|  4 | `_layout.scss:264`  | `.jt .v1-talk__meta .where .sep`       | text  | → `--fg-dim` |
|  5 | `_layout.scss:323`  | `.jt .filter-chip .count`              | text  | → `--fg-dim` |
|  6 | `_layout.scss:353`  | `.jt .blog-year-divider .count`        | text  | → `--fg-dim` |
|  7 | `_layout.scss:381`  | `.jt .blog-post-row .src`              | text  | → `--fg-dim` |
|  8 | `_layout.scss:443`  | `.jt .post-hero .eyebrow .sep`         | text  | → `--fg-dim` |
|  9 | `_layout.scss:471`  | `.jt .post-hero .meta-line`            | text  | → `--fg-dim` |
| 10 | `_layout.scss:491`  | `.jt .post-toc .label`                 | text  | → `--fg-dim` |
| 11 | `_layout.scss:523`  | `.jt .post-pager .label`               | text  | → `--fg-dim` |
| 12 | `_layout.scss:581`  | `.jt .related-post-row .arrow`         | text  | → `--fg-dim` (reclassified for consistency with `.row .arrow`; pa11y treats Unicode `→` glyphs as text) |
| 13 | `_layout.scss:630`  | `.jt .talks-section-head .count`       | text  | → `--fg-dim` |
| 14 | `_layout.scss:664`  | `.jt .talks-row .meta .where .sep`     | text  | → `--fg-dim` |
| 15 | `_layout.scss:696`  | `.jt .talks-row .duration`             | text  | → `--fg-dim` |
| 16 | `_layout.scss:778`  | `.jt .speaker-block .topics-label, .formats-label` | text  | → `--fg-dim` |
| 17 | `_layout.scss:873`  | `.jt .about-body-grid aside .label`    | text  | → `--fg-dim` |
| 18 | `_layout.scss:898`  | `.jt .quick-facts dt`                  | text  | → `--fg-dim` |
| 19 | `_layout.scss:961`  | `.jt .legal-hero .updated`             | text  | → `--fg-dim` |
| 20 | `_posts.scss:25`    | `.jt .row .arrow`                      | text  | → `--fg-dim` (initially classified decorative; pa11y flagged it on the home page — Unicode `→` inside a `<div>` is parsed as text content by AA tooling) |
| 21 | `_posts.scss:46`    | `.jt .row .src`                        | text  | → `--fg-dim` |
| 22 | `_posts.scss:91`    | `.jt .talk .status.past`               | text  | → `--fg-dim` |
| 23 | `_base.scss:97`     | `.jt .numeral`                         | decorative | **kept** `--fg-faint` — not currently used in any template; documented inline as "decorative accent numeral that pairs with focus-card titles" |

Net: **22 text-bearing swaps**, **1 decorative keep** (`.numeral`, unused but kept defensive with a rationale comment).

### `.row .arrow` verdict — judgment call resolved

The task spec leaned toward classifying `.row .arrow` as decorative (icon-glyph). My first pass kept it as `--fg-faint`. But pa11y-ci flagged the literal Unicode `→` inside the home page's `.row` as a text-contrast failure (2.82:1 vs the required 4.5:1). The rule was unambiguous: assistive tech reads the glyph as content. Reclassified to text-bearing and switched to `--fg-dim`. Both `.row .arrow` (_posts.scss) and `.related-post-row .arrow` (_layout.scss) were switched together for consistency. The `:hover` accent lift remains intact in both spots.

### `.post-body a` change

**Before** (`_sass/_typography.scss`):

```scss
.jt .post-body a {
  color: var(--accent);
  border-bottom: 1px solid color-mix(in oklab, var(--accent) 40%, transparent);
  transition: border-color 200ms ease;
}
.jt .post-body a:hover {
  border-bottom-color: var(--accent);
}
```

**After**:

```scss
.jt .post-body a {
  // Default state inherits body color (--fg) for AA contrast.
  // The underline + hover lift to accent carry the link signal.
  color: inherit;
  border-bottom: 1px solid color-mix(in oklab, var(--accent) 40%, transparent);
  transition: color 200ms ease, border-color 200ms ease;
}
.jt .post-body a:hover {
  color: var(--accent);
  border-bottom-color: var(--accent);
}
```

Default state is now `var(--fg)` via inheritance (AA pass). Hover lifts to accent (no AA constraint on hover). Underline tint stays at the soft `color-mix` accent.

### pa11y-ci local-run result

Recipe from `infra-006`'s Outcome (macOS sed variant). Both passes against all 7 URLs:

```
> http://localhost:4000/                                          - 0 errors
> http://localhost:4000/blog/                                     - 0 errors
> http://localhost:4000/talks/                                    - 0 errors
> http://localhost:4000/ueber-mich/                               - 0 errors
> http://localhost:4000/impressum/                                - 0 errors
> http://localhost:4000/datenschutz/                              - 0 errors
> http://localhost:4000/posts/2026/05/27/hello-welt/              - 0 errors

✔ 7/7 URLs passed   (dark mode)
✔ 7/7 URLs passed   (light mode)
```

Down from the 93-per-mode baseline that infra-006 surfaced.

### Verifications

- `bundle exec jekyll build` — clean.
- `git diff _sass/_tokens.scss` — empty (token values unchanged).
- Compiled CSS: `--fg-faint` references in `_site/assets/css/main.css` dropped from 25 to 6 (2 token-definition + 4 internal artefacts from the `.numeral` rule and untouched fallbacks).
- The post body has no inline `<a>` in `hello-welt`, so the `.post-body a` fix is a forward-looking change against future INNOQ-synced posts. Will be re-verified once such posts land.

### Surprises / notes for future audits

- pa11y-ci treats Unicode glyphs inside text-bearing elements (e.g. `<div class="arrow">→</div>`) as text content, not decoration. Spec intuition of "icon-glyph = decorative" doesn't match the AA tool's reality. Future "decorative" classifications should reserve `--fg-faint` for elements with `aria-hidden="true"` and zero text content — pure SVG icons, background images, etc.
- `.numeral` (`_base.scss`) kept `--fg-faint` defensively. No template uses it currently, so it's a non-issue. If it ever returns to active use, it should be re-audited with the above rule.
- No other violations surfaced during the audit; the fix is complete in scope.

### Key files
- `_sass/_layout.scss` — 19 `--fg-faint` → `--fg-dim` swaps
- `_sass/_posts.scss` — 3 `--fg-faint` → `--fg-dim` swaps
- `_sass/_base.scss` — 1 `--fg-faint` kept (`.numeral`, decorative + commented)
- `_sass/_typography.scss` — `.post-body a` switched to `color: inherit` default + hover lift to accent
- `_sass/_tokens.scss` — untouched (token values stay constant)

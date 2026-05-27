---
id: "0005"
title: "Redesigned visual system — Geist, oklch tokens, multi-accent palette, container queries"
scope: design-system
status: accepted
date: 2026-05-27
supersedes: ["0003"]
superseded_by: []
related_tasks: [design-system-003, website-003]
related_research: []
---

# ADR 0005: Redesigned visual system — Geist, oklch tokens, multi-accent palette, container queries

> Note on numbering: the task brief asked for "ADR-0004", but `0004-github-pages-initial-deployment.md`
> already exists (infrastructure scope, accepted 2026-05-26). To avoid clobbering an accepted ADR,
> this decision is filed as `0005`. The `supersedes` link to `0003` and the `superseded_by`
> back-reference in `0003` use the id `"0005"`.

## Context

ADR-0003 captured the original "build from scratch rather than fork Minima" decision
and described a styleguide with: amber accent `#d4a853` as a single hex token,
`prefers-color-scheme` media-query mode switching, a basic typography scale,
and a thin component vocabulary (`site-header`, `site-main`, `site-footer`).
That work was delivered as `design-system-001` (2026-05-26).

A complete visual redesign was subsequently delivered by Claude Design as a
high-fidelity brief in `design_handoff_jekyll/` (temporary scaffolding folder,
to be deleted) and implemented across `_sass/`, `_layouts/`, `_includes/`,
`_data/`, and `assets/`. The redesign is substantially richer than what
`design-system-001` captured. ADR-0003 is now factually wrong about what's
in the codebase.

This ADR replaces ADR-0003 as the canonical description of the design system
and pins the implementation files in `_sass/`, `_layouts/`, `_includes/`, and
`assets/js/` as the lasting source of truth — explicitly *not* the soon-to-be-
deleted `design_handoff_jekyll/` folder.

## Decision

The design system is built from scratch (this carries forward from ADR-0003 —
no theme gem dependency) but with a richer, more deliberate vocabulary across
seven axes. Each axis is described below with a pointer to the canonical
implementation file.

### 1. Token model — oklch color space

Canonical source: `_sass/_tokens.scss`.

All color tokens are defined as CSS custom properties on `:root`, with
mode-dependent overrides scoped by attribute selectors on `<html>`
(see axis 3). Colors use the `oklch()` function for perceptual uniformity:

- `oklch(L C H)` where L (lightness) is in [0, 1], C (chroma) is unbounded
  but typically 0–0.4, and H (hue) is in degrees [0, 360]
- Compared to hex/hsl: perceptually uniform — equal L values look equally
  bright across hues, equal C values look equally saturated, so swapping
  hue (axis 2) doesn't change apparent brightness or saturation
- Supports relative-color manipulation via `color-mix(in oklab, …)` which
  is used throughout `_sass/_typography.scss` for backgrounds, dividers,
  and code blocks

Neutral tokens per mode:

| Token            | Dark (default)              | Light (`[data-mode="light"]`) |
| ---------------- | --------------------------- | ----------------------------- |
| `--bg`           | `#0d0d0d`                   | `#f7f7f5`                     |
| `--bg-elev`      | `#141414`                   | `#ffffff`                     |
| `--fg`           | `#ededed`                   | `#141414`                     |
| `--fg-dim`       | `#9a9a9a`                   | `#5e5e5e`                     |
| `--fg-faint`     | `#5a5a5a`                   | `#a3a3a3`                     |
| `--rule`         | `rgba(255, 255, 255, 0.10)` | `rgba(0, 0, 0, 0.10)`         |
| `--rule-strong`  | `rgba(255, 255, 255, 0.22)` | `rgba(0, 0, 0, 0.22)`         |

Accent tokens are emitted per accent × mode (see axis 2).

### 2. Multi-accent palette — amber, coral, blue, lime

Canonical source: `_sass/_tokens.scss` (lines 38–49).

The site supports four accent hues, selected via a `data-accent` attribute
on `<html>`. The default is `amber` (set on `_layouts/default.html`). Each
accent has a dark variant (default) and a light variant
(`[data-accent="…"][data-mode="light"]`):

| Accent | Dark `--accent`        | Light `--accent`       |
| ------ | ---------------------- | ---------------------- |
| amber  | `oklch(0.80 0.14 78)`  | `oklch(0.58 0.14 60)`  |
| coral  | `oklch(0.74 0.17 32)`  | `oklch(0.58 0.18 32)`  |
| blue   | `oklch(0.78 0.13 240)` | `oklch(0.50 0.18 250)` |
| lime   | `oklch(0.86 0.18 130)` | `oklch(0.55 0.16 145)` |

Three tokens are emitted per accent:
- `--accent` — solid hue used for headlines' accent-mark, links, focus
  rings, status dots, callout borders
- `--accent-soft` — same hue with alpha `0.18` (dark) / `0.14` (light),
  used for soft backgrounds and underline traces
- `--accent-fg` — foreground color when something sits *on* the accent
  (e.g. `.skip-link` background); `#0d0d0d` in dark, `#fafafa` in light

**Adding a new accent**: append four rules to `_sass/_tokens.scss` in the
same pattern as the existing four — one base, one `[data-mode="light"]`
override — choosing dark-mode L≈0.74–0.86 and light-mode L≈0.50–0.58
so the hue stays legible on both `#0d0d0d` and `#f7f7f5`. Then expose
the new accent in any UI that lets visitors pick (none exists yet — the
site ships with `data-accent="amber"` hardcoded on `<html>`).

### 3. Mode mechanism — `data-mode` on `<html>`

Canonical sources: `_layouts/default.html`, `_includes/theme-toggle.html`,
`assets/js/theme-toggle.js`.

The `prefers-color-scheme` media query is *not* used directly for styling.
Instead:

1. `<html>` is rendered with `data-mode="dark"` baked in by Jekyll
   (`_layouts/default.html`, line 2)
2. An inline `<script>` in `<head>` (lines 13–22 of `default.html`) runs
   before paint to:
   - read `localStorage.getItem("jt-mode")` (key: `jt-mode`)
   - if absent, fall back to `window.matchMedia("(prefers-color-scheme: light)")`
   - set `data-mode` accordingly
   This avoids a flash of wrong-theme on page load
3. The Sun/Moon button (`_includes/theme-toggle.html`) carries
   `data-theme-toggle`; the deferred script `assets/js/theme-toggle.js`
   attaches a click handler that flips `data-mode` and persists the
   choice to `localStorage`
4. SCSS selectors target `:root[data-mode="light"]` to override the
   default dark palette

Rationale for `data-mode` over `prefers-color-scheme`: visitors expect to
be able to override system preference per-site, and `localStorage`
persistence lets us honor that across visits without server-side state.

### 4. Typography stack — Geist + Geist Mono

Canonical sources: `_layouts/default.html` (line 9), `_sass/_base.scss`,
`_sass/_typography.scss`.

- **Sans**: Geist (variable font, weights 100–900) — loaded from Google
  Fonts CDN with `display=swap`, applied to `.jt` and inherited everywhere
- **Mono**: Geist Mono (variable font, weights 100–900) — applied via the
  `.mono` utility class and inside `code`/`pre` inside `.post-body`
- **OpenType features**: `font-feature-settings: "ss01", "cv11"` (Geist
  stylistic set 1 + character variant 11) enabled on `.jt` for the
  preferred Geist tail-shape variants
- **Weight conventions**:
  - Headings: 380–500 (deliberately under "bold" — Geist's variable
    range lets us pick weights between standard steps)
  - Body: implicit 400
  - `strong`: 600
- **Letter-spacing conventions**: negative tracking on display sizes
  (`-0.02em` to `-0.045em`), tighter on body (`-0.005em` on `.jt`,
  `-0.003em` on `.post-body`), zero on mono and on chips
- **Body sizing** (post-body): 18px / line-height 1.65 / max-width 72ch

Sans/mono pairing rule: mono is reserved for metadata, eyebrows, dates,
counts, code, and any "system voice" label (.label-eyebrow, .chip,
.numeral). Body prose and titles are always sans.

### 5. Container queries — `.jt` root at ~720px

Canonical sources: `_sass/_base.scss` (lines 25–36), `_sass/_responsive.scss`.

The root `.jt` element (wrapping `topnav`, `main`, `footer` inside
`_layouts/default.html`) declares:
```scss
container-type: inline-size;
container-name: jt;
```

All responsive overrides live in a single block:
```scss
@container jt (max-width: 720px) { … }
```

Rationale: the site stays responsive even when embedded in narrow
iframes or restricted viewports — the layout reacts to its container's
width, not the viewport's. Browser support is universal in modern
browsers (>2023).

If a future component needs sub-container behavior, it can declare its
own `container-name`. We currently only have one container, `jt`.

### 6. Accent-mark (Akzent-Punkt) brand convention

Canonical source: `_sass/_base.scss` (line 126, `.accent-mark`).

Every headline ends with a period rendered in `var(--accent)`. Examples
from the live site:

- "Joshua Töpfer**.**" (wordmark, `_includes/topnav.html`)
- "Notizen aus der Praxis**.**" (blog hero, `_layouts/blog.html`)
- "Auf der Bühne**.**" (talks hero, `_layouts/talks.html`)
- "Hallo, ich bin Joshua**.**" (about hero, `_layouts/about.html`)

This is the smallest unit of brand identity on the site. Headlines
that do not naturally end with a period get one anyway. The convention
is consistent enough that the helper class `.accent-mark` is reusable
and grep-able.

### 7. Component vocabulary — contract consumed by website BC

Canonical source: `_sass/_layout.scss` (968 lines), `_sass/_typography.scss`,
`_sass/_base.scss`.

The website BC consumes these named components (selectors all live
under `.jt …`):

**Global chrome**
- `.topnav` — wordmark + nav + theme-toggle, sticky-feel header
- `footer` — 4-column grid (Kontakt / Anderswo / Site / Rechtliches)
  with baseline row
- `.skip-link` — a11y skip-to-content

**Page heroes**
- `.v1-hero` — homepage hero, grid 1fr / 460px
- `.v1-portrait`, `.about-portrait` — duotone image slot
  (`filter: grayscale(1) contrast(1.1) brightness(0.92)`)
- `.blog-hero`, `.talks-hero`, `.legal-hero`, `.about-hero`,
  `.post-hero` — per-page hero patterns
- `.post-hero .eyebrow` — topic + date in accent above the title
- `.post-hero .subtitle` — sub-headline below the H1
- `.post-hero .meta-line` — reading time + canonical-note line

**Content rows**
- `.row` — compact post row (home, related); grid date / body / arrow
- `.related-post-row` — variant for related-posts section
- `.blog-post-row` — wider row used in the blog index, includes
  `data-topic` for filtering
- `.talks-row`, `.talks-row--past` — talk rows
- `.v1-talk` — talk variant on home

**Microelements**
- `.chip` — pill with mono caps and an accent dot (used for tags)
- `.filter-chip` (and `.filter-chip.is-active`) — interactive chip
  in the blog filter bar
- `.label-eyebrow` — small mono caps label above sections
- `.eyebrow` — slightly larger eyebrow in hero contexts
- `.numeral` — large mono numerals
- `.status-dot` — pulsing accent dot
- `.caret` — blinking accent caret
- `.accent-mark` — the closing period in `--accent`
- `.link` — inline link with animated background-grow underline
- `.mono` — Geist Mono utility

**Long-form**
- `.post-body` — article column (typography rules in `_typography.scss`)
- `.post-body-layout` — two-column grid (sticky TOC aside + article)
- `.post-toc` — sticky TOC, populated by JS from H2s
- `.post-pager` — prev/next row at end of post

**Sections**
- `.related-posts` — "Mehr zum Thema X" section
- `.blog-year-divider` — large year label between year groups
- `.blog-year` — year group container
- `.v1-focus` — Schwerpunkte 3-column grid (home)
- `.v1-section-head` — mono-headed section header (home)
- `.speaker-block`, `.speaker-section` — speaker bio on talks page
- `.contact-cta` — contact CTA on about page

**JS-driven**
- `[data-fade]` — scroll-fade hook; observer in `theme-toggle.js`
  toggles `.in` when the element enters the viewport
- `[data-theme-toggle]` — Sun/Moon button hook
- `[data-topic]` (on `.filter-chip` and `.blog-post-row`) —
  blog filter hook; logic in `assets/js/blog-filter.js`

Pages that consume this vocabulary are owned by the website BC:
`home`, `blog`, `post`, `talks`, `about`, `page` (see website BC
README and INDEX). Layout files live at `_layouts/{layout}.html`.

## Consequences

### Positive

- Single source of truth in `_sass/` — no parallel handoff folder to
  drift from
- Accent hue is a per-site setting (the `data-accent` attribute), not
  baked into individual rules, so future "let visitors pick" UX is
  possible with zero CSS changes
- oklch makes the four-accent matrix uniform in perceived brightness —
  no accent looks "louder" than another within the same mode
- Container queries decouple the layout from viewport assumptions
- The `data-mode` mechanism honors explicit user choice without
  abandoning system-preference fallback
- The accent-mark is one tiny, repeatable pattern that anchors the
  entire identity
- Component vocabulary is enumerated and stable — the website BC
  can rely on it as a contract

### Negative

- oklch and container queries require evergreen browsers (>2023);
  legacy-browser support would need a polyfill or fallback layer
  (out of scope — this is a personal site)
- The light-mode accent variants (L≈0.50–0.58) are borderline for
  WCAG AA *body-text* contrast against `#f7f7f5` — amber and coral
  in particular may fall below 4.5:1 for inline link text. The
  large-text / UI threshold of 3:1 is comfortably met. See
  `design-system-002` for follow-up.
- The Geist font load depends on Google Fonts CDN — for stricter
  data-protection posture, fonts would need to be self-hosted
  (Joshua flagged this as a preference; not yet done)
- Many overrides in `_sass/_responsive.scss` use `!important`,
  matching the original handoff pattern — that's a known pragmatic
  choice, not an architectural one

### Neutral

- ADR-0003's underlying decision (scratch-built, no theme gem) still
  stands; this ADR refines *how* the scratch system is structured,
  not *whether* to scratch-build
- The 720px container-query breakpoint is the only breakpoint; if
  a desktop-only refinement is later needed, a `(min-width: …)`
  block can be added — the architecture supports it

## Alternatives considered

- **Keep ADR-0003 verbatim and add an addendum** — rejected: the
  vocabulary and decisions are richer enough that an addendum would
  be longer than the original ADR. A superseding ADR is honest.
- **Stay with hex/hsl tokens** — rejected: the multi-accent matrix
  is the whole point of using a perceptual color space. Hex would
  require hand-tuning each (accent × mode) combination by eye.
- **`prefers-color-scheme` media queries instead of `data-mode`** —
  rejected: precludes per-site user override, which is a
  not-negotiable UX behavior.
- **Classic media queries instead of container queries** — accepted
  as a fallback option in the original handoff brief; we picked
  container queries because the cost is identical and the
  embed-friendliness is a real benefit.
- **Single accent (just amber)** — rejected during design: the
  multi-accent palette is part of the brand language even if only
  amber is currently exposed in production. Switching to coral/blue/
  lime for individual pages or campaigns is a one-attribute change.

## Related files

- `_sass/_tokens.scss` — neutrals + 4-accent matrix
- `_sass/_base.scss` — `.jt` container declaration, micro-elements
- `_sass/_typography.scss` — Geist setup, `.post-body` prose rules
- `_sass/_layout.scss` — all named components
- `_sass/_responsive.scss` — single container-query block at 720px
- `_sass/_posts.scss` — supplementary post-list rules (kept from
  `design-system-001` era; survives unchanged)
- `assets/css/main.scss` — `@use` imports
- `assets/js/theme-toggle.js` — mode toggle + scroll-fade + TOC build
- `assets/js/blog-filter.js` — blog topic filter
- `_includes/topnav.html`, `_includes/footer.html`,
  `_includes/theme-toggle.html`, `_includes/post-card.html`,
  `_includes/talk-card.html` — global chrome + reusable rows
- `_layouts/default.html` — `<html data-mode data-accent>` baseline,
  preload, mode-before-paint script
- `_layouts/home.html`, `blog.html`, `post.html`, `talks.html`,
  `about.html`, `page.html` — page-layout contracts

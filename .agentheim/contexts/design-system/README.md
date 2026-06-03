# Design System

## Purpose
The visual identity layer for joshuatoepfer.de — defines the Jekyll theme,
typography stack, color tokens, mode mechanism, accent palette, and the
named component vocabulary that the website BC consumes as a contract.
Every frontend feature in any BC must depend on this context's styleguide
work before implementing any UI. This is a gate, not a guideline.

Current canonical decision: **ADR-0005** (which supersedes ADR-0003).

## Classification
Supporting

## Actors
- **Joshua** — sole designer and developer; signs off on the styleguide before any
  frontend work in other BCs begins

## What this BC owns
- **Design tokens** — `_sass/_tokens.scss` (neutrals per mode + the
  amber/coral/blue/lime accent matrix in oklch)
- **Typography** — `_sass/_typography.scss` (`.post-body` prose) and
  `_sass/_base.scss` (`.jt` container, Geist/Geist Mono setup);
  `@font-face`-Deklarationen liegen in `_sass/_fonts.scss`
- **Self-hosted fonts** — Geist und Geist Mono als Variable-WOFF2 unter
  `assets/fonts/` (eingebunden via `_sass/_fonts.scss`, SIL OFL 1.1,
  `OFL.txt` liegt daneben). Kein Google-Fonts-CDN-Aufruf mehr (siehe
  design-system-005).
- **Page layouts** — `_layouts/{default,home,blog,post,talks,about,page}.html`
  (the contract that website pages plug into)
- **Components** — `_sass/_layout.scss` (`.topnav`, `.row`, `.chip`,
  `.filter-chip`, `.post-body`, `.post-hero`, `.post-pager`, `.related-posts`,
  `.blog-year-divider`, `.talks-row`, …); reusable Liquid includes in
  `_includes/`
- **Theme toggle** — `_includes/theme-toggle.html` + `assets/js/theme-toggle.js`
  (Sun/Moon button, `data-mode` on `<html>`, localStorage-persisted)
- **Accent palette** — the four-accent matrix in `_tokens.scss`; selection
  via `data-accent` on `<html>` (currently hardcoded to `amber`)
- **Container-query strategy** — `_sass/_responsive.scss`, single
  `@container jt (max-width: 720px)` block; root container declared on `.jt`
- **Brand convention** — the accent-mark/Akzent-Punkt pattern (closing
  period in `var(--accent)` on every headline)

The implementation files listed above are the source of truth. The
`design_handoff_jekyll/` folder is temporary scaffolding from the
original design brief and will be deleted.

## Ubiquitous language

- **Token** — a named design variable exposed as a CSS custom property,
  e.g. `--bg`, `--fg`, `--accent`. Tokens live in `_sass/_tokens.scss`.
- **Mode** — one of `dark` (default) or `light`. Carried by the
  `data-mode` attribute on `<html>`. Switches the neutral palette and
  the active accent variant.
- **Theme toggle** — the Sun/Moon button (`_includes/theme-toggle.html`)
  that flips `data-mode` and persists to `localStorage` under key
  `jt-mode`. JS in `assets/js/theme-toggle.js`.
- **Accent** — the single solid hue used for headline marks, links,
  status dots, and focus rings. Exposed as `--accent`, `--accent-soft`,
  `--accent-fg`.
- **Accent palette** — the four available accent hues: `amber`, `coral`,
  `blue`, `lime`. Selected via `data-accent` on `<html>`. Each accent
  has separate dark and light variants in oklch space.
- **Accent-mark (Akzent-Punkt)** — the brand convention of rendering the
  closing period of every headline in `var(--accent)`, e.g.
  "Joshua Töpfer**.**", "Notizen aus der Praxis**.**". Helper class
  `.accent-mark`.
- **oklch** — the color space used for all hue tokens. Perceptually
  uniform: equal L looks equally bright across hues. Notation
  `oklch(L C H)` or `oklch(L C H / α)`.
- **Container query** — responsive overrides scoped to the width of the
  root `.jt` container, not the viewport. Single breakpoint at 720px.
  Lets the site stay responsive when embedded in narrow viewports.
- **Component** — a reusable selector group defined under `.jt …` in
  `_sass/_layout.scss`, typically backed by a Liquid include or layout.
- **Eyebrow** — small mono-caps label sitting above a hero title
  (`.eyebrow`, `.label-eyebrow`). Often carries topic + date in
  the accent color.
- **Meta-line** — the small meta row beneath a post hero (reading time,
  canonical-source note). Selector `.post-hero .meta-line`.
- **Subtitle** — the sub-headline beneath a hero H1
  (`.post-hero .subtitle`).
- **Portrait slot** — fixed-size image box used for Joshua's portrait
  on home (`.v1-portrait`, 460×620) and about (`.about-portrait`,
  460×580). Geometry only: `background-size: cover`,
  `background-position: center`, `border-radius: 2px`. The slot is
  asset-agnostic — no `filter` or `background-color` is applied at
  the CSS layer; any duotone/grayscale treatment lives in the image
  asset itself (current asset:
  `assets/images/joshua-toepfer-transparent.png`, a pre-grayscale
  cutout PNG; see design-system-004).
- **Year-divider** — large mono year label between year groups on the
  blog index page (`.blog-year-divider`).
- **Filter-chip** — interactive chip in the blog filter bar
  (`.filter-chip[data-topic]`); JS in `assets/js/blog-filter.js`
  toggles `is-active` and filters `.blog-post-row` elements.
- **Focus area (Schwerpunkt)** — the homepage 3-column block listing
  topics Joshua works on (`.v1-focus`).

## Aggregates
Not applicable.

## Key events
- `StyleguideApproved` — Joshua has reviewed and signed off on the design system;
  frontend work in other BCs may proceed.

## Key commands
- Define color tokens (per mode, per accent)
- Define typography scale and pairing rules
- Implement and verify mode switching (`data-mode`)
- Implement and verify accent palette (`data-accent`)
- Define and document the named component vocabulary

## Relationships with other contexts
- **Consumed by:** website (conformist — website adapts to this BC's
  design decisions and the named component vocabulary)

## Open questions
None currently. (The original "scratch vs. Minima" question was settled
by ADR-0003, now superseded by ADR-0005, which carries forward the
scratch-built decision.)

## Notes / future direction
- Joshua flagged a future `/design-system/` page on the live site as a
  referenceable styleguide. Not in scope of the current docs backfill;
  capture separately if pursued.
- The light-mode accent variants are borderline for WCAG AA *body-text*
  contrast against `--bg: #f7f7f5` (4.5:1 threshold); tracked in
  `design-system-002`.
- Geist/Geist Mono werden seit design-system-005 lokal als Variable-WOFF2
  unter `assets/fonts/` ausgeliefert (kein Google-Fonts-CDN-Aufruf mehr,
  keine Drittlandübermittlung). `@font-face`-Block in `_sass/_fonts.scss`,
  Lizenz `OFL.txt` liegt neben den Font-Dateien.

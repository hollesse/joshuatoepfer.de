# Website — Index

Catalog of everything in this bounded context: tasks by status, ADRs scoped to this BC,
research touching this BC, and concept synthesis pages.

> Updated by: `model` (tasks), `work` (BC-scoped ADRs, concept page links), `research` (BC-scoped reports).

---

## Tasks by status

<!-- task-counts:start -->
- **Backlog:** 0
- **Todo:** 0
- **Doing:** 0
- **Done:** 10
<!-- task-counts:end -->

### Todo
<!-- todo-list:start -->
<!-- todo-list:end -->

### Doing
<!-- doing-list:start -->
<!-- doing-list:end -->

### Done (most recent first; older entries kept for prior-art search)
<!-- done-list:start -->
- **website-010** — Block search-engine indexing until launch — `robots.txt` (`Disallow: /`) + globales `<meta name="robots" content="noindex, nofollow">` via `head-canonical.html` — 2026-06-04 — `done/website-010-block-search-engine-indexing.md`
- **website-009** — Bot-resistant email contact — two custom elements (`<jt-email-protected>` interaction-gated for `hallo@`, `<jt-email-readable>` CSS-assembled for `impressum@`); ADR-0008 — 2026-06-03 — `done/website-009-bot-resistant-email-contact.md`
- **website-008** — Focus card post count — derive from real posts instead of hardcoded number — 2026-06-03 — `done/website-008-focus-card-real-post-count.md`
- **website-007** — Homepage portrait image — wire up joshua-toepfer-transparent.png — 2026-06-03 — `done/website-007-homepage-portrait-image.md`
- **website-006** — Homepage talks fallback — recent past talks when none upcoming — 2026-06-02 — `done/website-006-homepage-talks-fallback.md`
- **website-005** — Syndicated post polish: visible source link at end + working TOC — 2026-06-01 — `done/website-005-syndicated-post-polish.md`
- **website-004** — Replace placeholder posts with a single Hello-World post — 2026-05-27 — `done/website-004-replace-placeholder-posts-with-hello-world.md`
- **website-003** — Document implemented pages and data sources (talks, ueber-mich, impressum, datenschutz, post layout) — 2026-05-27 — `done/website-003-document-implemented-pages.md`
- **website-002** — Blog listing page /posts/ — 2026-05-26 — `done/website-002-blog-listing.md`
- **website-001** — Homepage with hero section — 2026-05-26 — `done/website-001-homepage-hero.md`
<!-- done-list:end -->

### Backlog
<!-- backlog-list:start -->
<!-- backlog-list:end -->

## ADRs scoped to this BC

<!-- adr-local:start -->
- **0008** — Email obfuscation strategy: two-address architecture with asymmetric protection (interaction-gate JS-assembly for primary, CSS-assembly for legal) — 2026-06-03 — `../../knowledge/decisions/0008-email-obfuscation-strategy.md`
<!-- adr-local:end -->

## Research touching this BC

<!-- research-local:start -->
<!-- research-local:end -->

## Concepts (opt-in synthesis pages)

<!-- concepts:start -->
<!-- concepts:end -->

## Pointers

- BC README (ubiquitous language, invariants): `README.md`

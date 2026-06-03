# Infrastructure — Index

Catalog of everything in this bounded context: tasks by status, ADRs scoped to this BC,
research touching this BC, and concept synthesis pages.

> Updated by: `model` (tasks), `work` (BC-scoped ADRs, concept page links), `research` (BC-scoped reports).

---

## Tasks by status

<!-- task-counts:start -->
- **Backlog:** 0
- **Todo:** 0
- **Doing:** 0
- **Done:** 12
<!-- task-counts:end -->

### Todo
<!-- todo-list:start -->
<!-- todo-list:end -->

### Doing
<!-- doing-list:start -->
<!-- doing-list:end -->

### Done (most recent first; older entries kept for prior-art search)
<!-- done-list:start -->
- **infra-012** — Mail-Postfach `impressum@joshuatoepfer.de` — gelöst per Catchall-Adresse auf der Domain (alle `*@joshuatoepfer.de`) — 2026-06-03 — `done/infra-012-impressum-mail-postfach.md`
- **infra-011** — INNOQ talks sync workflow (scrape `/de/talks/?all=true&by=joshua-toepfer` → PR) — 2026-06-02 — `done/infra-011-innoq-talks-sync.md`
- **infra-010** — Fix srcset parser to handle Cloudinary commas-in-URL — 2026-06-02 — `done/infra-010-fix-srcset-parser-cloudinary-commas.md`
- **infra-009** — Extract INNOQ `<section class="conclusion">` Fazit into synced body — 2026-06-02 — `done/infra-009-extract-innoq-conclusion-section.md`
- **infra-008** — Promote heading levels (H3→H2 etc.) during INNOQ body conversion — 2026-06-01 — `done/infra-008-promote-headings-in-innoq-conversion.md`
- **infra-007** — Backfill URL-list mode bypasses dedup (force-resync semantic) — 2026-05-28 — `done/infra-007-backfill-url-list-bypasses-dedup.md`
- **infra-006** — Automated WCAG AA checks via pa11y-ci in CI (light + dark mode) — 2026-05-28 — `done/infra-006-pa11y-ci-wcag-aa.md`
- **infra-005** — INNOQ historical backfill workflow (staff-page scrape, German articles only) — 2026-05-28 — `done/infra-005-innoq-historical-backfill-scrape.md`
- **infra-004** — INNOQ author sync pipeline — incremental, feed-based (German articles only) — 2026-05-27 — `done/infra-004-innoq-author-sync-pipeline.md`
- **infra-003** — Walking skeleton: Jekyll builds and pipeline wired — 2026-05-26 — `done/infra-003-walking-skeleton.md`
- **infra-002** — Decision: Content sync strategy (innoq.com → PR) — 2026-05-26 — `done/infra-002-decision-content-sync-strategy.md`
- **infra-001** — Decision: Jekyll + Netlify base configuration — 2026-05-26 — `done/infra-001-decision-jekyll-netlify-setup.md`
<!-- done-list:end -->

### Backlog
<!-- backlog-list:start -->
<!-- backlog-list:end -->

## ADRs scoped to this BC

<!-- adr-local:start -->
- **0007** — INNOQ talks sync architecture: scrape-only workflow with update-in-place, URL identity, and source marker for hand-edit coexistence — 2026-06-02 — `../../knowledge/decisions/0007-innoq-talks-sync-architecture.md`
- **0006** — INNOQ sync architecture: dual-workflow (feed-poll + scrape-backfill) with full-body republishing and PR-history dedup — 2026-05-27 — `../../knowledge/decisions/0006-innoq-sync-architecture.md`
- **0002** — Content sync strategy (innoq.com → PR) — 2026-05-26 — `../../knowledge/decisions/0002-content-sync-strategy.md`
- **0001** — Jekyll + Netlify base configuration — 2026-05-26 — `../../knowledge/decisions/0001-jekyll-netlify-setup.md`
<!-- adr-local:end -->

## Research touching this BC

<!-- research-local:start -->
- **innoq-talks-page** — INNOQ talks page HTML structure and scrape feasibility (server-rendered; pagination 25/page; per-talk detail page for city/abstract/slides; no talks feed) — 2026-06-02 — `../../knowledge/research/innoq-talks-page-2026-06-02.md`
- **innoq-staff-feed** — INNOQ staff page structure and per-author feed availability (no per-author feed; global rolling feed; recommend hybrid backfill+poll) — 2026-05-27 — `../../knowledge/research/innoq-staff-feed-2026-05-27.md`
- **innoq-staff-page-scrape** — INNOQ staff page HTML structure and scrape feasibility for backfill (server-rendered; robots.txt permissive for current URLs; recommend BeautifulSoup against /de/written/?by=...) — 2026-05-27 — `../../knowledge/research/innoq-staff-page-scrape-2026-05-27.md`
<!-- research-local:end -->

## Concepts (opt-in synthesis pages)

<!-- concepts:start -->
- **innoq-sync** — how Joshua's INNOQ articles are mirrored to joshuatoepfer.de as syndicated draft posts, with a manual publish gate — 2026-05-28 — `concepts/innoq-sync.md`
<!-- concepts:end -->

## Pointers

- BC README (ubiquitous language, invariants): `README.md`

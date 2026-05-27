# Infrastructure — Index

Catalog of everything in this bounded context: tasks by status, ADRs scoped to this BC,
research touching this BC, and concept synthesis pages.

> Updated by: `model` (tasks), `work` (BC-scoped ADRs, concept page links), `research` (BC-scoped reports).

---

## Tasks by status

<!-- task-counts:start -->
- **Backlog:** 1
- **Todo:** 0
- **Doing:** 0
- **Done:** 4
<!-- task-counts:end -->

### Todo
<!-- todo-list:start -->
<!-- todo-list:end -->

### Doing
<!-- doing-list:start -->
<!-- doing-list:end -->

### Done (most recent first; older entries kept for prior-art search)
<!-- done-list:start -->
- **infra-004** — INNOQ author sync pipeline — incremental, feed-based (German articles only) — 2026-05-27 — `done/infra-004-innoq-author-sync-pipeline.md`
- **infra-003** — Walking skeleton: Jekyll builds and pipeline wired — 2026-05-26 — `done/infra-003-walking-skeleton.md`
- **infra-002** — Decision: Content sync strategy (innoq.com → PR) — 2026-05-26 — `done/infra-002-decision-content-sync-strategy.md`
- **infra-001** — Decision: Jekyll + Netlify base configuration — 2026-05-26 — `done/infra-001-decision-jekyll-netlify-setup.md`
<!-- done-list:end -->

### Backlog
<!-- backlog-list:start -->
- **infra-005** — INNOQ historical backfill workflow (staff-page scrape, German articles only) — `backlog/infra-005-innoq-historical-backfill-scrape.md`
<!-- backlog-list:end -->

## ADRs scoped to this BC

<!-- adr-local:start -->
- **0006** — INNOQ sync architecture: dual-workflow (feed-poll + scrape-backfill) with full-body republishing and PR-history dedup — 2026-05-27 — `../../knowledge/decisions/0006-innoq-sync-architecture.md`
- **0002** — Content sync strategy (innoq.com → PR) — 2026-05-26 — `../../knowledge/decisions/0002-content-sync-strategy.md`
- **0001** — Jekyll + Netlify base configuration — 2026-05-26 — `../../knowledge/decisions/0001-jekyll-netlify-setup.md`
<!-- adr-local:end -->

## Research touching this BC

<!-- research-local:start -->
- **innoq-staff-feed** — INNOQ staff page structure and per-author feed availability (no per-author feed; global rolling feed; recommend hybrid backfill+poll) — 2026-05-27 — `../../knowledge/research/innoq-staff-feed-2026-05-27.md`
- **innoq-staff-page-scrape** — INNOQ staff page HTML structure and scrape feasibility for backfill (server-rendered; robots.txt permissive for current URLs; recommend BeautifulSoup against /de/written/?by=...) — 2026-05-27 — `../../knowledge/research/innoq-staff-page-scrape-2026-05-27.md`
<!-- research-local:end -->

## Concepts (opt-in synthesis pages)

<!-- concepts:start -->
<!-- concepts:end -->

## Pointers

- BC README (ubiquitous language, invariants): `README.md`

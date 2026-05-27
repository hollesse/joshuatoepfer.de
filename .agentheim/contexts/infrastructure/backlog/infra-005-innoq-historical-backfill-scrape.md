---
id: infra-005
title: "INNOQ historical backfill workflow (staff-page scrape, German articles only)"
status: backlog
type: feature
context: infrastructure
created: 2026-05-27
completed:
commit:
depends_on: [infra-004]
blocks: []
tags: [sync, innoq, github-actions, pipeline, content, python, backfill, scrape]
related_adrs: [0002, 0006]
related_research: [innoq-staff-feed-2026-05-27, innoq-staff-page-scrape-2026-05-27]
prior_art: [infra-002]
---

## Why
`infra-004` covers the **incremental** INNOQ sync — feed-poll, daily cron,
articles inside the rolling ~25-entry Atom window. Joshua's older INNOQ
articles (2021–2023) sit **outside** that window: the feed has no record
of them, so the feed-poll workflow can never discover them.

Joshua initially planned to recreate those old `_posts/*.md` files
manually. We've now decided to automate that step too, with a separate
workflow that scrapes INNOQ directly rather than polling the feed.

Research on 2026-05-27 (`innoq-staff-page-scrape-2026-05-27`) confirmed
the scrape is feasible: plain server-rendered HTML, no JS hydration, no
Cloudflare challenge, robots.txt permissive for the URLs we need, no
rate-limiting observed across ~10 test fetches.

## Architecture

Sibling to `infra-004`. Both workflows share the same Python helper
module `.github/scripts/innoq_common.py` (delivered as part of
`infra-004`):

```
.github/
├── workflows/
│   ├── sync-innoq.yml       ← infra-004 (already refined): cron + manual incremental
│   └── backfill-innoq.yml   ← THIS TASK: workflow_dispatch only, scrape-based
└── scripts/
    ├── sync_innoq.py        ← infra-004
    ├── backfill_innoq.py    ← THIS TASK: scrape entry point, imports innoq_common
    └── innoq_common.py      ← infra-004 (shared)
```

This task **must not** be worked before `infra-004` lands — the shared
module doesn't exist yet. `depends_on: [infra-004]` enforces this.

## What
Implement `.github/workflows/backfill-innoq.yml` plus `backfill_innoq.py`
so that:

- Triggered **only manually** (`workflow_dispatch` — no cron)
- Discovers German `/de/articles/` URLs for Joshua either by:
  - **Auto-discovery mode (default):** scraping
    `https://www.innoq.com/de/written/?by=joshua-toepfer` (the dedicated
    German-articles-by-author archive — verified by research to return
    DE-only URLs with no DE/EN duplicates and no talks/podcasts mixed in)
  - **URL-list mode:** if the workflow input `urls` is non-empty, the
    workflow processes exactly those URLs (one or more, comma-separated)
    instead of running discovery — useful for re-running on a specific
    article whose original backfill had a problem
- For each discovered URL:
  - Skip if `canonical_url` already exists in `_posts/*.md` (same dedup
    primitive as `infra-004` — the shared helper)
  - Skip if `gh pr list --state all --head backfill/innoq/<slug>` returns
    ≥ 1 (PR-history dedup — same approach as `infra-004` but with the
    `backfill/` branch namespace to keep the two workflows' PRs visually
    distinct)
- For each surviving URL, fetch the article page, extract metadata and
  body, convert to Markdown, and open one PR per article with the same
  `_posts/<YYYY-MM-DD>-<slug>.md` shape that `infra-004` uses

## Decisions (resolved during research / refinement, 2026-05-27)

### Discovery source: `/de/written/?by=joshua-toepfer`
- Not the staff page itself. The staff page lists DE+EN duplicates and
  mixes content types. The `/de/written/?by=…` archive returns DE-only
  `/de/articles/...` URLs and only articles. Cleanest input.
- Today this returns **3 articles** (2021/01, 2022/12, 2023/06). Joshua's
  earlier estimate of ~5 was almost certainly counting DE/EN duplicates
  on the staff page. **Plan for n≈3**, but the workflow has no hard-coded
  count — whatever the archive returns, the workflow processes.

### Parser stack
- `requests` (HTTP) + `BeautifulSoup` with `lxml` parser backend (DOM) +
  `markdownify` (HTML → Markdown). Same Python dependencies as
  `infra-004` plus `beautifulsoup4` and `lxml`.

### Listing-page scrape
- Fetch `https://www.innoq.com/de/written/?by=joshua-toepfer`
- Selector: `a[href^="/de/articles/"]`
- Take the `href` (relative; expand to absolute) and the inner `<h3>`
  text as a fallback title. The article-page `<h1>` is the authoritative
  title.

### Article-page extraction
- HTTP `GET` each article URL with 2 s delay between requests.
- **Metadata extraction order (preferred → fallback):**
  - **Date:** `<meta property="article:published_time">` (ISO 8601, full
    day/time) → `<time datetime="...">` element → German-month parser
    on the visible text in the article header → final fallback: `YYYY-MM-01`
    derived from the URL path.
  - **Title:** `<meta property="og:title">` → `<title>` (strip the
    ` – INNOQ` site suffix) → `<h1>` text inside `<article>`.
  - **Canonical URL:** `<link rel="canonical">` if present → otherwise
    the URL we fetched.
- **Body extraction:** select the `<article>` element. Before
  Markdown conversion, strip:
  - `<form>` elements and any element whose heading text matches
    `/newsletter/i`
  - Author-bio / "Über den Autor" sidebar (`<aside>` inside `<article>`,
    or sibling element with a matching heading)
  - "Weitere Informationen" / related-content reference boxes (find by
    heading text + sibling list)
  - `<footer>` inside `<article>` if present
  - Share/social-icon blocks
  - Optionally: the article's "Tags" list at the bottom (may be useful as
    frontmatter — see Topic-mapping decision below — but for v1, strip)
- **Images:** keep `<img src="https://res.cloudinary.com/innoq/...">`
  references unchanged. Cloudinary URLs are stable; INNOQ stays the
  asset host (same policy as `infra-004`).
- **Code blocks:** research couldn't confirm the exact markup convention
  because both sampled articles are prose-only. For v1 use markdownify's
  defaults; if Joshua's 3 backfill articles turn out to contain code,
  the spike step below catches it. The same converter logic will be
  reused by `infra-004`'s feed-poll path, so any conversion fix lands
  in `innoq_common.py` and benefits both workflows.

### Pre-implementation spike — required first step
Before writing the parser, the worker must run a one-liner curl spike
and inspect the actual `<head>` markup. The research used `WebFetch`
which strips `<head>`, so a handful of selectors are unverified:

```bash
curl -sS https://www.innoq.com/de/articles/2023/06/remote-mob-programming/ \
  | sed -n '1,200p' \
  | grep -E '<meta property=|<meta name=|<link rel=|<time|<article'
```

Goal of the spike: confirm or refute that
`<meta property="article:published_time">`, `<meta property="og:title">`,
`<link rel="canonical">`, and `<time datetime="...">` exist on INNOQ
article pages. Five minutes of work. Document the result inline in
`backfill_innoq.py` as a header comment.

### Frontmatter shape (matches infra-004 exactly)
```yaml
---
layout: post
title: "<from og:title or <h1>>"
date: <YYYY-MM-DD>
source: innoq
canonical_url: <full URL>
published: false
render_with_liquid: false
# topic: left blank — Joshua fills in manually before publishing
---
```

### Topic mapping
- Same as `infra-004`: leave `topic:` empty, Joshua fills in
  manually as part of the publish step. Article tags from the INNOQ page
  footer are noisy and don't map cleanly to the site's three topics
  (`ensemble | adhs | softdev`).

### PR creation
- Action: `peter-evans/create-pull-request@v6` with `delete-branch: true`
- Branch namespace: `backfill/innoq/<slug>` (note: `backfill/`, not
  `sync/`, so the two workflows' PR history is visually distinguishable)
- PR title: `Backfill: <Article title> [innoq.com]`
- PR label: `sync-innoq` (same label as incremental — both are "synced
  from INNOQ" PRs for filtering purposes)
- One PR per article. No batching.

### Failure mode
- The workflow exits non-zero (job fails) on:
  - Listing page unreachable, malformed, or returns 0 articles
  - Any article fetch returns 4xx (other than the article being already
    in `_posts/`, in which case it's a skip not a failure)
  - Markdown conversion produces an empty body
  - GitHub API write failure
- Standard GH Actions failure email per Joshua's notification settings.

### Rate-limiting and politeness
- 2 s delay between HTTP requests to INNOQ.
- User-Agent: `joshuatoepfer.de-backfill/0.1 (+https://github.com/<owner>/joshuatoepfer.de; contact: joshua.toepfer@innoq.com)`.
  Identifies the project, links to the repo, gives a contact. INNOQ ops
  can email if anything's wrong.
- Exponential backoff on 5xx: 5 s → 30 s → 2 min, cap 3 attempts.
- On 429, honour `Retry-After` if present, else wait 5 minutes.
- On 403/404, do not retry — log and continue.
- Concurrency 1. No parallel article fetches needed at n≈3.
- robots.txt is permissive (the `Disallow: /*/articles/*/*/*/*.html`
  pattern targets a legacy URL shape; current trailing-slash URLs are
  not matched). Documented in the research report; do not re-derive.

## Workflow input shape

```yaml
on:
  workflow_dispatch:
    inputs:
      urls:
        description: "Specific canonical URL(s) to backfill, comma-separated. Empty = auto-discover from /de/written/?by=joshua-toepfer."
        required: false
        type: string
      dry_run:
        description: "If true, only log what would be done; create no PRs."
        required: false
        type: boolean
        default: false
```

Dry-run mode is a low-cost safety net: lets Joshua trigger the workflow
once and see the discovered article list + would-be PR titles before
actually creating PRs.

## Files delivered by this task

| File | Purpose |
| --- | --- |
| `.github/workflows/backfill-innoq.yml` | `workflow_dispatch`-only trigger; sets up Python; runs `backfill_innoq.py`; passes through `urls` and `dry_run` inputs |
| `.github/scripts/backfill_innoq.py` | Entry point: discovery + per-article fetch + extraction + delegates to `innoq_common` for frontmatter / Markdown / dedup / PR creation |
| `infrastructure/README.md` | Updated with a "Backfill workflow" sub-section under the existing "Sync workflow" section (added by `infra-004`); explains when to use backfill vs incremental, dry-run mode, and URL-list override |

## Acceptance criteria

- [ ] Pre-implementation curl spike documented inline in `backfill_innoq.py` header comment: confirmed or refuted presence of `article:published_time`, `og:title`, `link rel=canonical`, `<time datetime>` on a sample INNOQ article page. Result drives the metadata-extraction order.
- [ ] `.github/workflows/backfill-innoq.yml` exists with `workflow_dispatch` trigger only (no `schedule`) and the `urls` + `dry_run` inputs as specified.
- [ ] `.github/scripts/backfill_innoq.py` imports the shared module (`from innoq_common import …`) for frontmatter generation, Markdown conversion, dedup, and PR creation. **No reimplementation** of helpers that infra-004 already provides.
- [ ] **Auto-discovery mode** (default, `urls` empty): the script fetches `https://www.innoq.com/de/written/?by=joshua-toepfer`, parses with BeautifulSoup, selects `a[href^="/de/articles/"]`, and processes each unique resulting URL.
- [ ] **URL-list mode** (`urls` non-empty): the script parses the comma-separated input and processes exactly those URLs, skipping discovery.
- [ ] Each candidate URL runs through the dedup chain: skip if `canonical_url` is already in any `_posts/*.md` frontmatter; skip if `gh pr list --state all --head backfill/innoq/<slug>` returns ≥ 1.
- [ ] For each surviving URL: fetch with 2 s delay between requests, identifying User-Agent set per the rate-limiting section, exponential backoff on 5xx (5 s, 30 s, 2 min, cap 3 attempts).
- [ ] Article-page metadata extracted in the preferred-fallback order specified (date: `article:published_time` → `<time datetime>` → German-month visible-text parse → URL `YYYY-MM-01`; title: `og:title` → `<title>` stripped → `<h1>`; canonical: `<link rel=canonical>` → fetched URL).
- [ ] Article body stripped per the strip-list (newsletter forms, author-bio sidebar, "Weitere Informationen" boxes, footer, share icons) before markdownify conversion.
- [ ] `<img>` references in the body are preserved verbatim (Cloudinary URLs kept; no local mirroring).
- [ ] One PR per article via `peter-evans/create-pull-request@v6`, `delete-branch: true`, branch `backfill/innoq/<slug>`, title `Backfill: <title> [innoq.com]`, label `sync-innoq`. Post body has frontmatter matching the infra-004 shape (`layout`, `title`, `date`, `source: innoq`, `canonical_url`, `published: false`, `render_with_liquid: false`, no `topic`).
- [ ] **`dry_run: true`** mode: the workflow logs the discovered articles, the dedup outcomes, and the would-be PR titles, but does **not** create any branches or PRs. Job exits 0.
- [ ] Workflow exits non-zero on: listing unreachable / 0 articles, article fetch 4xx (except the already-in-`_posts/` skip), empty Markdown after conversion, GH API write failure.
- [ ] After merging a backfill PR, `bundle exec jekyll build` passes and the article does not appear on the live site (because `published: false`). After Joshua flips `published: true`, the article appears at `/`, `/blog/`, and `/posts/<YYYY>/<MM>/<DD>/<slug>/`.
- [ ] `infrastructure/README.md` has a "Backfill workflow" sub-section under the existing "Sync workflow" section.
- [ ] No code-block-specific markdownify config needed (research could not confirm; worker verifies by inspecting each of Joshua's 3 articles during the spike — most likely all prose-only). If any article contains code, fix the converter in `innoq_common.py` (so infra-004 benefits too).

## Notes
- Research `innoq-staff-page-scrape-2026-05-27` is the canonical reference for everything above. The worker should not re-derive selectors or fetch the staff page again — the report names the surface and the rationale.
- `infra-004` adds an ADR (likely `ADR-0006`) covering the dual-workflow architecture, full-body republishing, PR-history-based dedup, and force-resync mechanism. This task does **not** write a separate ADR — `ADR-0006` already covers the architectural decisions. If this task surfaces a genuinely new architectural decision (e.g. a parser choice that warrants documentation), add an addendum to `ADR-0006` or write `ADR-0007`.
- Article-count expectation: 3 today, per the research. If the discovery scrape returns a different number, that's information (INNOQ added or removed an article), not an error. Log the count, process whatever's there.
- The `WebFetch`-induced unknowns from the research report (`<head>` meta tag presence, exact `<article>` class) are intentionally left to the worker's spike rather than blocking PROMOTE. The spike is small (5 min) and reduces redundant remote calls.
- The shared `sync-innoq` PR label means filtering "all INNOQ-sourced PRs" in the GH UI is one click, regardless of which workflow produced the PR. Joshua can review both backfill and incremental PRs from one list.
- A small additional benefit of the URL-list mode: it also serves as a generic re-sync mechanism for backfill articles whose original conversion was buggy. (The equivalent for incremental-window articles is `infra-004`'s `force_resync` input.)

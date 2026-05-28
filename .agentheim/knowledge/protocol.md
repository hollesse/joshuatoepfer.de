# Protocol

Chronological log of everything that happens in this project.
Newest entries on top.

---

## 2026-05-28 10:32 -- Work session ended

**Type:** Work / Session end
**Completed:** 2 (first-try PASS: 2, re-dispatched: 0, skipped: 0)
**Bounced:** 0
**Failed:** 0
**Escalated after verification:** 0
**Commits:** 2 (8c968d0, 15d899e)
**Tasks done this session:** infra-005 (INNOQ backfill workflow), infra-006 (pa11y-ci WCAG AA in CI)
**Key user hand-off:** design-system-002 scope needs to expand from "light-mode accent only" to "both-mode `--text-muted` calibration" before being PROMOTEd — see infra-006's Outcome section for the concrete pa11y-ci violation list and the recommended fix direction.

---

## 2026-05-28 10:30 -- Task verified and completed: infra-006 - pa11y-ci WCAG AA in CI

**Type:** Work / Task completion
**Task:** infra-006 - Automated WCAG AA checks via pa11y-ci in CI (light + dark mode)
**Summary:** Shipped `.github/workflows/accessibility.yml` running pa11y-ci@4.1.1 against the 7 implemented routes × both modes (14 audit passes per workflow run). Worker chose a `sed`-rewrite of `_site/**/*.html` between two pa11y-ci invocations to inject light mode, after correctly identifying that pa11y has no `evaluate` action (the spec's proposed mechanism was wrong). The sed approach mutates both the `data-mode` attribute on `<html>` and the localStorage-reading boot script's fallback value, defeating Chrome headless's `prefers-color-scheme: light` default. Local validation: dark mode surfaces 93 AA violations at 2.82:1, light mode 93 violations at 2.35:1, all on `--text-muted`-styled elements (`.arrow`, `.count.mono`, `.sep`, footer `h4`). **Scope-expanding finding**: design-system-002 needs to broaden from "light-mode accent only" to "both-mode `--text-muted` calibration" — full hand-off documented in the task's Outcome section.
**Verification:** PASS (iteration 1)
**Commit:** (pending)
**Files changed:** 4 worker files + 3 task/index/protocol updates
**Tests added:** 0 (config-only task; pa11y-ci itself is the test suite)
**ADRs written:** none

---

## 2026-05-28 10:05 -- Batch started: [infra-006]

**Type:** Work / Batch start
**Tasks:** infra-006 - Automated WCAG AA checks via pa11y-ci in CI (light + dark mode)
**Parallel:** no (1 worker)

---

## 2026-05-28 10:00 -- Task verified and completed: infra-005 - INNOQ historical backfill workflow

**Type:** Work / Task completion
**Task:** infra-005 - INNOQ historical backfill workflow (staff-page scrape, German articles only)
**Summary:** Shipped the scrape-based backfill workflow as a sibling to the feed-poll incremental sync. Worker's curl spike (required first step) confirmed `og:title`, `og:url`, `<time datetime>`, and `<article class="article-page-default">` are reliably present on INNOQ article pages; found `article:published_time` absent (handled gracefully via `<time datetime>` fallback) and `<link rel=canonical>` unreliable (some 2023/06-style reprints point external — code uses fetched URL instead). Auto-discovery returns 3 DE articles today as the research predicted. Worker extended `innoq_common.py` with `ScrapedArticle` dataclass, `build_backfill_pr_title/_body`, `largest_src_from_srcset` (promotes Cloudinary srcset → src), `parse_german_date`, `split_url_list_input`, plus `BACKFILL_BRANCH_PREFIX`/`BACKFILL_DISCOVERY_URL` constants. Test suite expanded from 22 → 65 tests (43 new), all passing.
**Verification:** PASS (iteration 1)
**Commit:** (pending)
**Files changed:** 6 worker files + 3 task/index/protocol updates
**Tests added:** 43 (total: 65)
**ADRs written:** none (ADR-0006 already covers the architecture)

---

## 2026-05-28 09:40 -- Batch started: [infra-005]

**Type:** Work / Batch start
**Tasks:** infra-005 - INNOQ historical backfill workflow (staff-page scrape, German articles only)
**Parallel:** no (1 worker — infra-006 demoted to next batch due to shared `infrastructure/README.md` conflict)

---

## 2026-05-28 09:30 -- Model / Refined + Captured: design-system-002 deferred → blocked on new infra-006

**Type:** Model / Refine + Capture
**BC:** design-system + infrastructure
**Status after:** design-system-002 stays in backlog (deferred); infra-006 filed to todo
**Summary:** Joshua looked at concrete proposed color values for both fix options A (darken `--accent` L) and B (separate `--accent-text` token) and rejected both visually. A third path emerged in conversation — Option C (`.post-body a` uses `color: inherit`, animated underline carries link signal, tokens untouched) — but rather than commit to it now, Joshua chose to build automated WCAG checks first so the next refinement of design-system-002 is informed by concrete pa11y-ci output rather than estimates. New task `infra-006` captures the pa11y-ci CI setup (covers all 7 routes × dark + light mode, fails on WCAG 2.1 AA violations, no package.json — ephemeral npx). design-system-002 updated with `depends_on: [design-system-001, infra-006]`, a "Deferred 2026-05-28" section, the rejected A/B path, and 5 candidate fix paths (C + D-G) to re-evaluate once pa11y-ci surfaces real failures. The first infra-006 run is expected to fail — that's the proof the check works.
**Split into:** infra-006 (new, todo)
**ADRs written:** none

---

## 2026-05-28 09:10 -- Model / Promoted: infra-005

**Type:** Model / Promote
**BC:** infrastructure
**From → To:** backlog → todo

---

## 2026-05-28 09:00 -- Concept created: innoq-sync

**Type:** Concept / Created
**BC:** infrastructure
**Page:** `.agentheim/contexts/infrastructure/concepts/innoq-sync.md`
**Derived from:** ADR 0002, ADR 0006, research innoq-staff-feed-2026-05-27, research innoq-staff-page-scrape-2026-05-27, done infra-002, done infra-004, backlog infra-005
**Summary:** Synthesis page for the INNOQ → joshuatoepfer.de mirror — the two workflows (live sync-innoq, planned backfill-innoq), the shared `innoq_common.py` module, the four-step filter chain (author email, German language, /de/ path, /articles/ segment), the two-step PR-history dedup, the manual two-step publish flow, and the force-resync escape hatch. 51-line body, well within the 60-line cap. Lists each source artifact in `derived_from` for drift detection.

---

## 2026-05-27 19:38 -- Work session ended

**Type:** Work / Session end
**Completed:** 1 (first-try PASS: 1, re-dispatched: 0, skipped: 0)
**Bounced:** 0
**Failed:** 0
**Escalated after verification:** 0
**Commits:** 1 (f4e0629)
**Concept candidates surfaced:** innoq-sync (converging on 4 artifacts: infra-002, infra-004, ADR-0002, ADR-0006)
**Unblocked downstream:** infra-005 (was waiting on infra-004; now eligible for PROMOTE)

---

## 2026-05-27 19:35 -- Task verified and completed: infra-004 - INNOQ author sync pipeline (incremental)

**Type:** Work / Task completion
**Task:** infra-004 - INNOQ author sync pipeline — incremental, feed-based (German articles only)
**Summary:** Delivered the incremental INNOQ sync pipeline — `.github/workflows/sync-innoq.yml` (cron + workflow_dispatch with `force_resync` and `feed_url_override` inputs; matrix shape for one-PR-per-article) plus `sync_innoq.py` and the shared `innoq_common.py` module that `infra-005` will import. Enforces the four-step filter chain (author email, xml:lang=de, /de/ path, /articles/ segment), two-step PR-history dedup (`_posts/` canonical_url + `gh pr list --state all --head sync/innoq/<slug>`), force-resync that preserves `topic`/`published` on a timestamped branch, and fail-loud observability. 22 unit tests passing. ADR-0006 records the dual-workflow + full-body + PR-history-dedup + force-resync + Python + blank-topic decisions; infrastructure README has the new Sync workflow section including the smoke-test procedure for Joshua's first deploy. Orchestrator added `__pycache__/` and `*.py[cod]` to `.gitignore` as a small follow-up cleanup so Python toolchain artifacts don't accumulate.
**Verification:** PASS (iteration 1)
**Commit:** (pending)
**Files changed:** 6 worker files + 3 task/index/protocol updates + .gitignore
**Tests added:** 22
**ADRs written:** 0006-innoq-sync-architecture.md

---

## 2026-05-27 19:20 -- Batch started: [infra-004]

**Type:** Work / Batch start
**Tasks:** infra-004 - INNOQ author sync pipeline — incremental, feed-based (German articles only)
**Parallel:** no (1 worker)

---

## 2026-05-27 19:15 -- Model / Promoted: infra-004

**Type:** Model / Promote
**BC:** infrastructure
**From → To:** backlog → todo

---

## 2026-05-27 19:10 -- Model / Captured: infra-005

**Type:** Model / Capture
**BC:** infrastructure
**Filed to:** backlog
**Summary:** Captured the historical backfill workflow as a sibling to infra-004, splitting the previous "Joshua does manual backfill" plan into an automated job. Discovery source is `https://www.innoq.com/de/written/?by=joshua-toepfer` (per research `innoq-staff-page-scrape-2026-05-27`) — server-rendered, DE-only article URLs, robots.txt permissive. Parser stack: `requests` + `BeautifulSoup(lxml)` + `markdownify`. Trigger: `workflow_dispatch` only with `urls` (override) and `dry_run` inputs. Branch namespace `backfill/innoq/<slug>` to distinguish from infra-004's `sync/innoq/<slug>`. Shared label `sync-innoq`. `depends_on: [infra-004]` because both workflows share `.github/scripts/innoq_common.py` which infra-004 delivers. Article-count expectation: 3 (not Joshua's earlier ~5 estimate — research surfaced that the staff page counts DE/EN duplicates while `/de/written/?by=...` does not; flagged for sanity-check). One pre-implementation open: 5-min curl spike on `<head>` meta tags + `<article>` class + code-block convention — left to worker as first step rather than blocking PROMOTE.

---

## 2026-05-27 18:55 -- Research / Filed: innoq-staff-page-scrape-2026-05-27

**Type:** Research / Report filed
**BC:** infrastructure
**Related task:** infra-005
**Report:** `.agentheim/knowledge/research/innoq-staff-page-scrape-2026-05-27.md`
**Summary:** Investigated INNOQ staff-page HTML structure and scrape feasibility for the historical backfill workflow. Confirmed: server-rendered HTML, no JS/Cloudflare, robots.txt permissive for current trailing-slash article URLs. Discovery surface: `/de/written/?by=joshua-toepfer` (DE-only, articles-only, no DE/EN duplicates — 3 entries today). Parser: BeautifulSoup(lxml). Body strip-list: newsletter forms, author-bio, "Weitere Informationen" boxes, footer, share icons. Open spike: `<head>` meta tag inventory (`article:published_time`, `og:title`, `link rel=canonical`, `<time datetime>`) — WebFetch strips `<head>` so could not verify; ~5 min curl spike recommended before parser commit. Indexed under infrastructure research-local.

---

## 2026-05-27 18:50 -- Model / Refined: infra-004

**Type:** Model / Refine
**BC:** infrastructure
**Status after:** backlog (ready for PROMOTE)
**Summary:** All previously-open questions resolved into a "Decisions" section. Body content: full Atom `<content>` (resolves ADR-0002's deferred legal question — Joshua greenlit full body) → markdownify → Markdown, images stay as remote `<img>` references to Cloudinary. Workflow language: Python (`feedparser` + `markdownify` + `pyyaml`). Dedup: 2-tier via `_posts/*.md` canonical_url + `gh pr list --state all --head sync/innoq/<slug>` — branches deleted on PR close (`delete-branch: true`), PR history is the dedup memory so no persistent branches accumulate. Force-resync via `workflow_dispatch` input `force_resync` (comma-separated URLs): bypasses dedup, preserves existing file's `topic`/`published` values, regenerates body, branch suffix `-resync-<timestamp>`. Topic mapping: left blank (Joshua fills in manually). Failure mode: fail loudly (job status = failed; default GH Actions email). Feed-window risk: accepted; backfill is now `infra-005`'s job. Architecture explicitly split into two workflows sharing `innoq_common.py`; `infra-004` now `blocks: [infra-005]`. Worker will write `ADR-0006` covering dual-workflow architecture + full-body decision + PR-history dedup + force-resync.
**Split into:** [infra-005]
**ADRs written:** none yet (ADR-0006 to be authored by infra-004's worker)

---

## 2026-05-27 18:42 -- Work session ended

**Type:** Work / Session end
**Completed:** 1 (first-try PASS: 1, re-dispatched: 0, skipped: 0)
**Bounced:** 0
**Failed:** 0
**Escalated after verification:** 0
**Commits:** 1 (2e85ac8)

---

## 2026-05-27 18:40 -- Task verified and completed: website-004 - Replace placeholder posts with Hello-Welt

**Type:** Work / Task completion
**Task:** website-004 - Replace placeholder posts with a single Hello-World post
**Summary:** Deleted the 6 placeholder posts under `_posts/` and replaced them with a single `_posts/2026-05-27-hello-welt.md` (short German "Hallo, Welt." greeting mentioning the three topic areas, signed "— Joshua"). `bundle exec jekyll build` completes cleanly; post renders at `/posts/2026/05/27/hello-welt/` (per `_config.yml`'s permalink scheme — task spec wrongly predicted `/blog/hello-welt/`; verifier flagged the spec inconsistency but the worker correctly preferred the explicit "don't touch `_config.yml`" constraint).
**Verification:** PASS (iteration 1)
**Commit:** (pending)
**Files changed:** 7 (1 new post + 6 deletions)
**ADRs written:** none

---

## 2026-05-27 18:35 -- Research / Filed: innoq-staff-feed

**Type:** Research / Report filed
**BC:** infrastructure
**Related task:** infra-004
**Report:** `.agentheim/knowledge/research/innoq-staff-feed-2026-05-27.md`
**Summary:** Investigated INNOQ's staff page structure and per-author feed availability for Joshua Töpfer's INNOQ author sync pipeline (`infra-004`). Key findings: (1) No per-author feed exists — every probed URL pattern returned 404/406, and the staff page body links only to the global feed. (2) Only feed available is global rolling Atom 1.0 at `/{de,en}/feed.atom`, ~20–25 entries, oldest seen 2026-02-26 — Joshua's content not currently in either feed's window. (3) Feed has high-quality author metadata (`<author><name/email/uri>`) but NO `<category>` element — content type must be inferred from URL path segment (`/talks/`, `/articles/`, `/podcast/`, `/blog/`). (4) Staff page is canonical complete listing but has no JSON-LD/microdata. Sitemap.xml is collection-level only. (5) Recommendation: hybrid — scrape staff page for backfill, poll global `/de/feed.atom` filtered by `email = joshua.toepfer@innoq.com` for incremental sync. Constraint "German articles only" is enforceable via `<content xml:lang="de">` or `/de/` URL prefix. Open questions: raw `<head>` inspection (curl-grep), staff-page pagination URL pattern, JSON content negotiation. Filed to infrastructure INDEX.

---

## 2026-05-27 18:18 -- Batch started: [website-004]

**Type:** Work / Batch start
**Tasks:** website-004 - Replace placeholder posts with a single Hello-World post
**Parallel:** no (1 worker)

---

## 2026-05-27 18:15 -- Model / Captured: website-004, infra-004

**Type:** Model / Capture
**BC:** website, infrastructure
**Filed to:** todo (website-004), backlog (infra-004)
**Summary:** Joshua flagged the existing `_posts/` content as placeholder and wants it replaced with a single Hello-Welt post before real INNOQ articles arrive — captured as `website-004` (ready-to-work in todo, lists exact files to delete + the new file's frontmatter). The bigger ask is implementing the INNOQ author sync pipeline ADR-0002 already designed, with an explicit new constraint: German articles only (English filtered out). Author profile: https://www.innoq.com/de/staff/joshua-toepfer/. Captured as `infra-004` in backlog with 8 open questions (RSS-vs-scrape discovery, language indicator, first-run flood handling, body content, PR tooling, script language, topic mapping, failure observability). Next step on infra-004: spawn the `research` skill on INNOQ's staff-page structure and per-author feed format before REFINE.

---

## 2026-05-27 18:06 -- Work session ended

**Type:** Work / Session end
**Completed:** 2 (first-try PASS: 2, re-dispatched: 0, skipped: 0)
**Bounced:** 0
**Failed:** 0
**Escalated after verification:** 0
**Commits:** 2

---

## 2026-05-27 18:05 -- Task verified and completed: website-003 - Document implemented pages and data sources

**Type:** Work / Task completion
**Task:** website-003 - Document implemented pages and data sources (talks, ueber-mich, impressum, datenschutz, post layout)
**Summary:** Extended the website BC README with new ubiquitous-language entries and a Pages inventory covering all 7 current routes; appended 2026-05-27 Amendment sections to done/website-001 (homepage now also has newest-posts, focus areas, upcoming-talks, duotone portrait) and done/website-002 (blog now year-grouped with filter chips; post layout now has hero, sticky TOC, pager, related-posts); legacy `/posts/` confirmed removed in 4d4fb3e. ADR-0005 related_tasks bidirectionally updated with website-003.
**Verification:** PASS (iteration 1)
**Commit:** a68641c
**Files changed:** 7
**ADRs written:** none

---

## 2026-05-27 17:56 -- Batch started: [website-003]

**Type:** Work / Batch start
**Tasks:** website-003 - Document implemented pages and data sources (talks, ueber-mich, impressum, datenschutz, post layout)
**Parallel:** no (1 worker)

---

## 2026-05-27 17:55 -- Task verified and completed: design-system-003 - Document redesigned visual system

**Type:** Work / Task completion
**Task:** design-system-003 - Document redesigned visual system (Geist + oklch + multi-accent + container queries)
**Summary:** Documented the new visual system via ADR-0005 (filed as 0005 because 0004 was already taken by github-pages-initial-deployment), marked ADR-0003 superseded, rewrote the design-system BC README, and refined design-system-002 (light-mode contrast) with measured WCAG ratios — amber/coral/lime FAIL body-text 4.5:1 against `#f7f7f5` (~3.3-3.7:1), only blue passes (~6.5:1); bug stays in backlog with concrete fix options.
**Verification:** PASS (iteration 1)
**Commit:** 9174503
**Files changed:** 9
**ADRs written:** 0005-redesigned-visual-system.md (plus frontmatter-only edit to 0003)

---

## 2026-05-27 17:35 -- Batch started: [design-system-003]

**Type:** Work / Batch start
**Tasks:** design-system-003 - Document redesigned visual system (Geist + oklch + multi-accent + container queries)
**Parallel:** no (1 worker)

---

## 2026-05-27 17:30 -- Model / Captured: design-system-003, website-003

**Type:** Model / Capture
**BC:** design-system, website
**Filed to:** todo
**Summary:** Two documentation backfill tasks for a redesign delivered by Claude Design (handoff in `design_handoff_jekyll/`) that was already implemented in `_layouts/`, `_includes/`, `_sass/`, `_data/`, `assets/`. design-system-003 documents the new visual system (Geist + oklch tokens + multi-accent palette + container queries + theme toggle + accent-mark) and supersedes ADR-0003 with a new ADR-0004; also re-evaluates design-system-002 (light-mode accent contrast bug) against the new oklch light variants. website-003 documents the implemented pages (talks, ueber-mich, impressum, datenschutz) and the richer homepage/blog/post layouts, plus the new `_data/` sources, with amendments appended to the existing done tasks website-001 and website-002. The handoff folder is treated as temporary scaffolding; BC docs become the lasting reference. Joshua flagged a future direction: a live `/design-system/` page on the site — not in scope here.

---

## 2026-05-26 15:30 -- Task verified and completed: website-002 - Blog listing page /posts/

**Type:** Work / Task completion
**Task:** website-002 - Blog listing page /posts/
**Summary:** Created /posts/ listing page, _layouts/post.html, canonical link include, and _sass/_posts.scss with mobile-first flex layout; posts filtered by published: true, syndicated posts labelled innoq.com.
**Verification:** PASS (iteration 3)
**Commit:** 97a0d51
**Files changed:** 8
**ADRs written:** none

---

## 2026-05-26 15:05 -- Batch started: [website-001, website-002]

**Type:** Work / Batch start
**Tasks:** website-001 - Homepage with hero section, website-002 - Blog listing page /posts/
**Parallel:** yes (2 workers)

---

## 2026-05-26 15:00 -- Model / Captured: website-001, website-002

**Type:** Model / Capture
**BC:** website
**Filed to:** todo
**Summary:** Two homepage features captured based on design reference (neureif.com):
hero section with name + tagline (website-001) and text-only blog listing at /posts/
including individual post layout (website-002). No images anywhere — typography carries the weight.

---

## 2026-05-26 14:35 -- Work session ended

**Type:** Work / Session end
**Completed:** 4 (first-try PASS: 2, re-dispatched: 1, verification skipped: 1)
**Bounced:** 0
**Failed:** 0
**Escalated after verification:** 0
**Commits:** 6

---

## 2026-05-26 14:30 -- Task verified and completed: design-system-001 - Styleguide

**Type:** Work / Task completion
**Task:** design-system-001 - Feature: Styleguide — visual identity, dark mode, typography
**Summary:** Scratch-built SCSS design system: dark-mode-first tokens, base reset, typography scale, responsive layout shell. bundle exec jekyll build passes. Human sign-off gate remains open.
**Verification:** PASS (iteration 1)
**Commit:** (pending)
**Files changed:** 9
**ADRs written:** 0003-design-system-scratch-theme.md

---

## 2026-05-26 14:16 -- Batch started: [design-system-001]

**Type:** Work / Batch start
**Tasks:** design-system-001 - Feature: Styleguide — visual identity, dark mode, typography
**Parallel:** no (1 worker)

---

## 2026-05-26 14:15 -- Task verified and completed: infra-003 - Walking skeleton

**Type:** Work / Task completion
**Task:** infra-003 - Spike: Walking skeleton — Jekyll boots and deploys to Netlify
**Summary:** Added _talks/.gitkeep so talks directory is tracked in git; bundle exec jekyll build passes; all skeleton files committed.
**Verification:** PASS (iteration 2)
**Commit:** da4255f
**Files changed:** 7
**ADRs written:** none

---

## 2026-05-26 14:10 -- Verification failed: infra-003 - Walking skeleton

**Type:** Work / Verification failure
**Task:** infra-003 - Spike: Walking skeleton
**Iteration:** 1 of 3
**Reasons:** Gemfile.lock untracked (not committed); _talks/ empty dir has no .gitkeep so won't survive clone
**Iteration hint:** likely-fixable
**Next:** re-dispatched worker

---

## 2026-05-26 14:06 -- Batch started: [infra-003]

**Type:** Work / Batch start
**Tasks:** infra-003 - Spike: Walking skeleton — Jekyll boots and deploys to Netlify
**Parallel:** no (1 worker)

---

## 2026-05-26 14:05 -- Task verified and completed: infra-001 - Decision: Jekyll + Netlify base configuration

**Type:** Work / Task completion
**Task:** infra-001 - Decision: Jekyll + Netlify base configuration
**Summary:** Recorded the Jekyll 4.4.1 + Netlify + GitHub Actions stack decision in ADR-0001 and created netlify.toml, deploy.yml, Gemfile, .ruby-version pinning the build toolchain.
**Verification:** PASS (iteration 1)
**Commit:** 0f3d412
**Files changed:** 6
**ADRs written:** 0001-jekyll-netlify-setup.md

---

## 2026-05-26 14:04 -- Task completed (verification skipped): infra-002 - Decision: Content sync strategy

**Type:** Work / Task completion
**Task:** infra-002 - Decision: Content sync strategy (innoq.com → PR)
**Summary:** ADR-0002 records the daily RSS-based sync strategy with draft-first PR flow; Joshua controls publish via setting published: true.
**Verification:** SKIPPED — decision-only task, single ADR file
**Commit:** 69bb501
**Files changed:** 2
**ADRs written:** 0002-content-sync-strategy.md

---

## 2026-05-26 14:00 -- Batch started: [infra-001, infra-002]

**Type:** Work / Batch start
**Tasks:** infra-001 - Decision: Jekyll + Netlify base configuration, infra-002 - Decision: Content sync strategy (innoq.com → PR)
**Parallel:** yes (2 workers)

---

## 2026-05-26 — Brainstorm: joshuatoepfer.de personal website

**Type:** Brainstorm
**Outcome:** vision created
**BCs identified:** website, design-system, infrastructure
**Summary:** Joshua Töpfer wants a personal website anchoring his professional brand
across three topic areas (Ensemble Programming, ADHS in der IT, Software Development).
The site will mirror posts from innoq.com (syndicated) plus host exclusive personal
content, and serve as a speaker hub for conference talks. Stack is Jekyll + Netlify +
GitHub Actions, dark-mode-first design, low-maintenance automation via sync PRs.
**ADRs written:** none (foundation choices flow through decision tasks)
**Foundation tasks emitted:**
- `infra-001` — Decision: Jekyll + Netlify base configuration
- `infra-002` — Decision: Content sync strategy (innoq.com → PR)
- `infra-003` — Walking skeleton (depends on infra-001, infra-002)
- `design-system-001` — Styleguide (depends on infra-003)

---

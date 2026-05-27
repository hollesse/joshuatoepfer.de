# Protocol

Chronological log of everything that happens in this project.
Newest entries on top.

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

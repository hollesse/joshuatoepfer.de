---
id: website-003
title: "Document implemented pages and data sources (talks, ueber-mich, impressum, datenschutz, post layout)"
status: done
type: chore
context: website
created: 2026-05-27
completed: 2026-05-27
commit:
depends_on: [design-system-003]
blocks: []
tags: [documentation, pages, data-sources, layouts]
related_adrs: [0005]
related_research: []
prior_art: [website-001, website-002]
---

## Why
The redesign delivered by Claude Design added pages, layouts, and data files to the
website BC that aren't reflected in the BC's documentation or in the existing done
tasks (`website-001`, `website-002`). The `design_handoff_jekyll/` folder is
temporary and will be deleted — the website BC's docs need to be the lasting
reference for what pages exist and what data drives them.

**New pages currently implemented but undocumented:**
- `/talks/` (layout: `talks`) — upcoming + past talks, plus speaker-profile block
- `/ueber-mich/` (layout: `about`) — bio, portrait, quick-facts
- `/impressum/` (layout: `page`) — legal text page
- `/datenschutz/` (layout: `page`) — legal text page

**Existing done tasks describe earlier, simpler versions:**
- `website-001` documented "homepage with hero" — the homepage now also lists
  newest posts, focus areas (Schwerpunkte), upcoming talks, and uses a portrait
  with the duotone image-slot pattern
- `website-002` documented blog listing — listing now has year-grouping with
  big year-dividers, filter chips (Alle / Ensemble / ADHS / Software Dev), and
  the post layout has a hero banner, sticky TOC aside, prev/next pager, and
  related-posts block

**New data sources:**
- `_data/talks.yml`, `_data/focus.yml`, `_data/about.yml`

## What
Bring the website BC documentation in line with the implemented state. No HTML,
Liquid, or YAML changes — the implementation is the source of truth.

1. **Update `contexts/website/README.md`**
   - Extend ubiquitous language with: focus area (Schwerpunkt), quick fact, speaker
     profile, post hero, table of contents (TOC), prev/next pager, related-posts
     block, year-divider, filter-chip, legal page
   - Update open questions: "Über mich?" is settled (yes, `/ueber-mich/`); the
     topic-landing question is settled (filter chips on `/blog/`, not dedicated
     pages); booking-contact question stays open
   - Add a "Pages inventory" subsection (or a sibling `pages.md` — your call)
     listing every route on the site with its layout and primary data source

2. **Pages inventory (one row per page) must cover:**
   - `/` — layout `home`, data: `site.posts | slice: 0, 5`, `site.data.talks where upcoming`, `site.data.focus`
   - `/blog/` — layout `blog`, data: `site.posts` grouped by year, filter chips via `assets/js/blog-filter.js`
   - `/blog/:slug/` — layout `post`, data: post frontmatter (`title`, `subtitle`, `date`, `topic`, `source`, `canonical`, `reading_time`)
   - `/talks/` — layout `talks`, data: `site.data.talks`, plus speaker profile block
   - `/ueber-mich/` — layout `about`, data: `site.data.about`, portrait at `assets/images/portrait.jpg`
   - `/impressum/` — layout `page`, frontmatter-driven
   - `/datenschutz/` — layout `page`, frontmatter-driven
   - For each, also note the `_includes/` used (e.g. `topnav.html`, `footer.html`, `post-card.html`, `talk-card.html`, `theme-toggle.html`)

3. **Append "Amendment 2026-05-27" sections** to the existing done tasks rather than
   rewriting them — preserves history:
   - `done/website-001-homepage-hero.md`: list what the homepage now also contains
     (newest-posts list, focus areas section, upcoming-talks section, portrait with
     duotone image-slot), link to this task and to ADR-0004
   - `done/website-002-blog-listing.md`: list the additions (year-grouping with
     dividers, filter chips, the post layout's hero banner, TOC, prev/next pager,
     related-posts block), link to this task and to ADR-0004

4. **Update `contexts/website/INDEX.md`** with this task and (later) the link to
   ADR-0004 in the BC-relevant ADRs section once that ADR exists.

5. **No references to `design_handoff_jekyll/`** in any BC docs — that folder is
   scaffolding and will be deleted.

## Acceptance criteria
- [ ] `contexts/website/README.md` ubiquitous language extended with: focus area, quick fact, speaker profile, post hero, TOC, prev/next pager, related-posts, year-divider, filter-chip, legal page
- [ ] README open questions: "Über mich" closed, topic-landing closed (filter-chips approach), booking-contact still listed
- [ ] Pages inventory exists (in README or sibling `pages.md`) covering all 7 routes with layout, data sources, and includes used
- [ ] `done/website-001-homepage-hero.md` has an "Amendment 2026-05-27" section appended listing the homepage's current contents
- [ ] `done/website-002-blog-listing.md` has an "Amendment 2026-05-27" section appended listing the blog/post layout's current contents
- [ ] No BC documentation references `design_handoff_jekyll/`

## Notes
- Depends on `design-system-003` because the pages inventory and amendments should
  reference ADR-0004 (the new design system) once it exists. Work this task second.
- `_data/talks.yml`, `_data/focus.yml`, `_data/about.yml` are the canonical data
  shapes for these pages — read them rather than describing schemas from scratch.
- Consider whether `pages.md` (a small new file in `contexts/website/`) reads
  better than a long README section — either is fine.

## Outcome

Brought website BC documentation in line with the implemented state. No
implementation files were touched (HTML, Liquid, YAML, SCSS, JS all left as-is).

**Decision on structure:** folded the pages inventory into
`contexts/website/README.md` rather than creating a sibling `pages.md`. The README
was previously short (~52 lines); the inventory is substantial but keeps the BC
documentation in a single self-contained file that future readers will already be
opening.

**Changes:**

- **`contexts/website/README.md`** — extended ubiquitous language (split into
  *Content* and *Layout vocabulary* subsections) covering topic, focus area,
  quick fact, post hero, TOC, prev/next pager, related-posts block, year-divider,
  filter-chip, speaker profile, legal page; tightened the **Talk** entry to match
  the actual `_data/talks.yml` shape (`what` / `where` / `status` / `type` /
  `duration` / `slides` / `video`); closed the *Über mich* and topic-landing open
  questions, kept the booking-contact one open with a note on the current
  `/talks/` speaker-profile + `/ueber-mich/` contact-CTA arrangement; added a
  **Pages inventory** section with one row per route (route, layout, data
  sources, includes, component vocabulary referencing ADR-0005 §7) plus a
  trailing **Data file shapes** subsection for `_data/talks.yml`, `_data/focus.yml`,
  `_data/about.yml`.
- **`done/website-001-homepage-hero.md`** — appended an *Amendment 2026-05-27*
  section recording that the original `.hero` / `.recent-posts` / `.post-list`
  homepage is now built from `_layouts/home.html` with the duotone portrait, the
  three-card focus section, and the upcoming-talks list. References ADR-0005 and
  the README pages inventory.
- **`done/website-002-blog-listing.md`** — appended an *Amendment 2026-05-27*
  section recording the move from `/posts/` to `/blog/` (and the removal of
  `posts.html` in commit `4d4fb3e`), the year-divider grouping, the JS-driven
  filter chips, and the now-much-richer post layout (post hero, sticky TOC,
  prev/next pager, related-posts block). References ADR-0005 and the README
  pages inventory.

**Verification:** `bundle exec jekyll build` passed (sanity check — this task
changes no Jekyll-built files but the doc edits sit alongside the site).

**Note on `/posts/`:** the legacy `/posts/` listing no longer exists; the file
was already deleted in commit `4d4fb3e`. The Amendment to website-002 and the
"Note on legacy `/posts/`" subsection in the README record this. The topnav
still defensively matches `/posts/` URLs to highlight the Blog tab — no follow-up
needed.

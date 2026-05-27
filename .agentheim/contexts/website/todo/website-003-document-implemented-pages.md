---
id: website-003
title: "Document implemented pages and data sources (talks, ueber-mich, impressum, datenschutz, post layout)"
status: todo
type: chore
context: website
created: 2026-05-27
completed:
commit:
depends_on: [design-system-003]
blocks: []
tags: [documentation, pages, data-sources, layouts]
related_adrs: []
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

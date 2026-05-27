---
id: website-002
title: "Blog listing page /posts/"
status: done
completed: 2026-05-26
type: feature
context: website
created: 2026-05-26
depends_on: [design-system-001]
tags: [blog, listing, posts]
related_adrs: []
prior_art: []
---

## Why
Readers who want to explore all of Joshua's writing need a dedicated listing page.
Posts should be discoverable without images — the title and date carry the weight.

## What
A `/posts/` page that lists all published posts (`published: true`) in reverse
chronological order. Text-only — no thumbnails, no excerpts.

## Acceptance criteria
- [x] Page at `/posts/` lists all posts where `published: true` (or no `published` key),
      excludes posts with `published: false`
- [x] Each entry shows: title (as a link), date, and optionally the source label
      ("innoq.com" for syndicated posts)
- [x] No images, no excerpts — title and date only
- [x] Syndicated posts (frontmatter `source: innoq`) are visually distinguished with a
      subtle label or indicator (not a badge, keep it minimal)
- [x] Layout is clean, generous line-height, uses design-system typography tokens
- [x] A `_layouts/post.html` exists that renders individual post content with title,
      date, and prose body (`.prose` class)
- [x] Canonical link tag in `<head>` for syndicated posts (uses `canonical_url` frontmatter)
- [x] Renders correctly on mobile and desktop

## Notes
No pagination needed for v1 — the list can be long, it's fine.
The individual post layout (`_layouts/post.html`) is a natural dependency of this task —
create it here so posts are actually readable once linked from the listing.

## Outcome
Created `posts.html` (permalink `/posts/`) listing all non-`published:false` posts with
title, date, and optional `innoq.com` source label. Created `_layouts/post.html` rendering
posts with `.post`, `.post__header`, `.post__title`, `.meta`, and `.prose` classes.
Added `_includes/head-canonical.html` and injected it into `_layouts/default.html` for
canonical `<link>` support. Added `_sass/_posts.scss` with all listing and post layout
styles; wired into `assets/css/main.scss` via `@use "posts"`. Updated `_config.yml`
post defaults to use `layout: post`. Build verified clean.

Key files:
- `posts.html` — listing page at `/posts/`
- `_layouts/post.html` — individual post template
- `_includes/head-canonical.html` — canonical link include
- `_sass/_posts.scss` — post-specific styles


## Verifier note (iteration 2)

REASONS: `.posts-list__item` in `_sass/_posts.scss` uses `display: flex; justify-content: space-between` without a mobile-first `flex-direction: column` base. Long titles will be compressed on narrow screens.

SUGGESTED_FIX: Change `.posts-list__item` to `flex-direction: column` as the mobile default, then wrap `flex-direction: row; justify-content: space-between; align-items: baseline` in `@media (min-width: 36rem)` — matching the pattern already in `.post-list__item` in `_layout.scss`.

ITERATION_HINT: likely-fixable

## Iteration 3 fix
Applied mobile-first `flex-direction: column` base to `.posts-list__item` with `@media (min-width: 36rem)` breakpoint for the row layout. Build verified clean.

## Amendment 2026-05-27

The simple `/posts/` listing and basic `_layouts/post.html` shipped here have been
replaced by the redesign documented in ADR-0005 and inventoried by website-003.
Current state:

- The blog listing now lives at **`/blog/`** (source `blog/index.html`,
  `_layouts/blog.html`); the legacy `/posts/` page was removed in commit `4d4fb3e`.
  `posts.html` no longer exists.
- The listing is grouped by year via `.blog-year` sections, each headed by a large
  **`.blog-year-divider`** (year + post count).
- Topic filtering is now interactive: **`.filter-chip[data-topic="all|ensemble|adhs|softdev"]`**
  buttons drive client-side row toggling via `assets/js/blog-filter.js` (loaded
  conditionally by `_layouts/default.html` when `page.layout == "blog"`).
- Post rows use `.blog-post-row` with date / source / title / subtitle / topic-tag.
- **`_layouts/post.html`** is now substantially richer:
  - A `.post-hero` banner with back-link, eyebrow (topic · date), accent-marked title,
    optional subtitle, and a `.meta-line` (reading time + syndication note)
  - A `.post-body-layout` with a sticky `.post-toc` aside (rebuilt by
    `theme-toggle.js` from the post's h2s)
  - A `.post-pager` (prev/next, derived from `site.posts`)
  - A `.related-posts` block — up to 3 other posts sharing the same `topic`,
    rendered via `_includes/post-card.html` (style `related`)
- `_includes/head-canonical.html` (introduced here) is still used for syndicated
  posts and now lives in `_layouts/default.html`.
- The `_sass/_posts.scss` styles introduced here have been superseded by the
  `.post-hero` / `.post-body-layout` / `.post-pager` / `.related-posts` styles in
  `_sass/_layout.scss` that came in with ADR-0005.

For the canonical current state see the `/blog/` and `/blog/:slug/` rows in the
Pages inventory in `contexts/website/README.md` and ADR-0005
(`.agentheim/knowledge/decisions/0005-redesigned-visual-system.md`).

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

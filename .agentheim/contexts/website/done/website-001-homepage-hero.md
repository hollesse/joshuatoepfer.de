---
id: website-001
title: "Homepage with hero section"
status: done
type: feature
context: website
created: 2026-05-26
completed: 2026-05-26
depends_on: [design-system-001]
tags: [homepage, hero, layout]
related_adrs: []
prior_art: []
---

## Why
The current homepage is a plain list — no personality, no recognition value. A visitor
who lands on joshuatoepfer.de should immediately know who Joshua is and what he stands for.

## What
Replace the placeholder `index.html` with a proper homepage: a prominent hero section
followed by a short recent-posts preview.

## Acceptance criteria
- [x] Hero section shows Joshua's name as a large heading
- [x] Hero includes a short tagline covering his three topics (Ensemble Programming,
      ADHS in der IT, Software Development) — concise, not a list
- [x] Below the hero: a "Letzte Posts" section showing the 3–5 most recent published posts
      (title + date, no images, no excerpt needed)
- [x] Layout uses `.prose` width constraint and existing design-system tokens
- [x] No images anywhere on the homepage — text only
- [x] Renders correctly on mobile and desktop

## Notes
Design reference: neureif.com — hero with recognition value, minimalist, clean whitespace.
The hero should feel personal and distinctive, not generic. Typographic treatment of Joshua's
name (large, prominent) is more interesting than a photo or illustration.

The "three topics" can be rendered as a single flowing sentence or as a typographic accent
line — not as bullet points or tag chips (that belongs in the blog listing later).

## Outcome
Replaced `index.html` with a hero + recent-posts homepage. Key files:

- `index.html` — hero with `.hero__name` (h1) and `.hero__tagline`, followed by a
  "Letzte Posts" section looping over `site.posts | where_exp published != false | limit 5`.
  Wrapped in `.prose` for max-width constraint. Graceful empty state when no posts exist.
- `_sass/_layout.scss` — appended `.hero`, `.hero__name`, `.hero__tagline`,
  `.recent-posts`, `.recent-posts__heading`, `.post-list`, `.post-list__item`,
  `.post-list__title`, `.post-list__date` using existing tokens.
  Post list items are flex-row on wider screens (title left, date right), stacked on mobile.

`bundle exec jekyll build` passed with no errors.

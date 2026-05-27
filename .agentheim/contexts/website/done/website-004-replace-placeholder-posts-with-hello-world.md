---
id: website-004
title: "Replace placeholder posts with a single Hello-World post"
status: done
type: chore
context: website
created: 2026-05-27
completed: 2026-05-27
commit:
depends_on: []
blocks: []
tags: [content, posts, cleanup]
related_adrs: []
related_research: []
prior_art: []
---

## Why
The six posts currently under `_posts/` are placeholder/fake content seeded during
the build-out of the homepage, blog listing, and post layout. They are not real
posts Joshua has written. Before the INNOQ sync pipeline (`infra-004`) starts
filling `_posts/` with real syndicated articles, the placeholder content needs
to be removed so the site reflects an honest empty state.

## What
Delete all current placeholder post files and replace them with a single
real "Hello, Welt." post that:

- announces the site is up
- is dated 2026-05-27
- carries no `topic` (the topic chips are designed for syndicated/categorised
  content — a Hello-World post doesn't belong to ensemble/adhs/softdev)
- is `published: true` so it appears in `/`, `/blog/`, and gets its own
  `/blog/hello-welt/` page

The post is intentionally minimal — a 1–3 paragraph greeting, German, no
external links, no embeds. It is a smoke test for the layouts as much as it
is content.

### Files to delete
- `_posts/2026-01-30-pairing-mit-dem-adhs-brain.md`
- `_posts/2026-02-17-ensemble-etikette.md`
- `_posts/2026-03-21-refactoring-als-reparatur.md`
- `_posts/2026-04-09-kalender-exocortex.md`
- `_posts/2026-04-28-ensemble-warum.md`
- `_posts/2026-05-12-brain-zu-schnell-tippt.md`

### File to create
`_posts/2026-05-27-hello-welt.md`:

```yaml
---
layout: post
title: "Hallo, Welt."
date: 2026-05-27
published: true
---
```

Body: a short German greeting (1–3 short paragraphs). Joshua can rewrite the
prose later; for this task a plain placeholder greeting that mentions the
site and the three topic areas (Ensemble Programming, ADHS in der IT, allgemeine
Software-Entwicklung) is sufficient.

## Acceptance criteria
- [ ] All six placeholder post files listed above are deleted from `_posts/`.
- [ ] `_posts/2026-05-27-hello-welt.md` exists with the frontmatter shown above
      and a short German-language body (no Lorem-ipsum).
- [ ] `bundle exec jekyll build` completes without errors.
- [ ] After build, `/` shows the Hello-Welt post in "Neueste Beiträge" with
      its date rendered as `27. Mai 2026`.
- [ ] After build, `/blog/` shows the Hello-Welt post under the 2026 year
      group; filter chips still render (they may show an "empty" state when
      filtered to a specific topic — that is acceptable).
- [ ] After build, `/blog/hello-welt/` renders the post with the post-hero
      (no eyebrow, since no topic), the post body, and the prev/next pager
      (which will be empty since this is the only post — that is acceptable).

## Notes
- Filter chips on `/blog/` may show an empty list when a topic is selected
  because the only post has no `topic`. Acceptable for the chore — real
  content will arrive via `infra-004`.
- Prev/next pager and related-posts block will be empty / not render. That is
  the layout's correct behaviour for a single-post site.
- Do not touch `_layouts/`, `_includes/`, `_sass/`, `_data/`, or
  `_config.yml` — content-only change.
- This task is unblocked and small (~10 min of work). Reasonable to dispatch
  immediately.

## Outcome

Deleted all six placeholder posts under `_posts/` and replaced them with a
single `_posts/2026-05-27-hello-welt.md` containing a short German greeting
that mentions the three topic areas (Ensemble Programming, ADHS in der IT,
allgemeine Software-Entwicklung) and is signed off with "— Joshua". The post
intentionally carries no `topic`, so the post-hero renders without an
eyebrow chip — as designed.

**Build:** `bundle exec jekyll build` completed cleanly (no errors, no
warnings beyond Jekyll's normal output).

**Verified pages (post-build inspection of `_site/`):**
- `/` (`_site/index.html`) — "Neueste Beiträge" lists Hallo, Welt. with date
  "27. Mai 2026".
- `/blog/` (`_site/blog/index.html`) — single 2026 year group with
  "1 Beitrag", post row links to the post.
- Individual post page renders post-hero (date only, no topic eyebrow),
  body, and back-link. Prev/next pager and related-posts block are absent
  because this is the only post — the layout's correct behaviour.

**Permalink note (deviation from acceptance criteria wording):** the
acceptance criteria mention a `/blog/hello-welt/` URL for the post page,
but `_config.yml` defines `permalink: /posts/:year/:month/:day/:title/`
(left untouched per the "do not touch `_config.yml`" constraint). The post
is therefore reachable at `/posts/2026/05/27/hello-welt/`. The `topnav`
already treats both `/blog/` and `/posts/` as the Blog section, and all
layouts/includes link via `post.url` — so the user-visible navigation is
correct. If Joshua prefers the shorter `/blog/hello-welt/` form, that is a
separate config change (permalink scheme decision, BC-wide implication).

### Files

Deleted (6):
- `_posts/2026-01-30-pairing-mit-dem-adhs-brain.md`
- `_posts/2026-02-17-ensemble-etikette.md`
- `_posts/2026-03-21-refactoring-als-reparatur.md`
- `_posts/2026-04-09-kalender-exocortex.md`
- `_posts/2026-04-28-ensemble-warum.md`
- `_posts/2026-05-12-brain-zu-schnell-tippt.md`

Created (1):
- `_posts/2026-05-27-hello-welt.md`

---
id: infra-004
title: "INNOQ author sync pipeline (German articles only)"
status: backlog
type: feature
context: infrastructure
created: 2026-05-27
completed:
commit:
depends_on: []
blocks: []
tags: [sync, innoq, github-actions, pipeline, content]
related_adrs: [0002]
related_research: []
prior_art: [infra-002]
---

## Why
ADR-0002 (2026-05-26) decided the content-sync strategy for innoq.com →
joshuatoepfer.de: a scheduled GitHub Actions workflow that polls Joshua's
author feed daily, opens a draft PR per new article, never auto-publishes.
The decision was made; the workflow has not yet been built. Currently
`_posts/` carries placeholder content (cleaned up by `website-004`) and
no automated discovery exists.

Joshua wants the pipeline live so his real INNOQ articles begin appearing
as draft PRs and the site stops being a hand-curated placeholder.

A constraint added today (2026-05-27): **only German articles count.**
Joshua writes some articles in English and some in German on innoq.com.
For his personal site, only the German ones are interesting. The sync
pipeline must filter out English articles.

## What
Implement the GitHub Actions workflow described in ADR-0002, with the
explicit German-only filter, so that:

- Joshua's INNOQ author page is polled daily
- New German articles trigger a draft-status `_posts/` PR
- English articles are ignored
- Already-synced articles are not re-PR'd

### Known sources
- Author profile (German): https://www.innoq.com/de/staff/joshua-toepfer/
- INNOQ author articles index (all languages, all authors): https://www.innoq.com/de/written/
- Joshua's articles appear under "Weitere Inhalte" on the staff page; both
  German and English entries are listed in the German staff page (suspected;
  to be confirmed during research)

### Workflow file
`.github/workflows/sync-innoq.yml` (proposed name)

### Helper script
Workflow logic likely doesn't fit cleanly in YAML alone; a small script under
`.github/scripts/sync-innoq.{rb,py,sh}` is expected. Language to be decided
during refinement — Ruby gives us Jekyll-adjacent ergonomics, Python is the
GitHub Actions default and has good HTTP/HTML/RSS tooling.

## Open questions (must be answered during REFINE)

1. **Discovery mechanism.** Does INNOQ expose a per-author RSS feed
   (something like `https://www.innoq.com/de/staff/joshua-toepfer/articles.atom`
   or `.rss`)? ADR-0002 assumed yes. If not, we fall back to scraping the
   staff page's "Weitere Inhalte" list or the global `/de/written/` index
   filtered by author. → spawn `research` skill on INNOQ's site structure.

2. **Language indicator.** How does INNOQ mark German vs English articles?
   - URL path: `/de/articles/...` vs `/en/articles/...`?
   - HTML `lang` attribute on article pages?
   - RSS `<language>` element per entry?
   - Author-page section heading ("Deutsche Beiträge" / "English content")?
   → research will need to answer this concretely.

3. **First-run behaviour.** Joshua's INNOQ history has dozens of articles
   (estimate). The first time this workflow runs, it should not open dozens
   of PRs simultaneously. Options:
   - **Backfill in one PR**: a single PR adds all historical articles as
     drafts (`published: false`), so the flood is contained
   - **Date cutoff**: only sync articles published on or after a configured
     date (e.g. site launch date, ~2026-05-26)
   - **Manual one-time backfill, then incremental**: run a one-shot script
     locally to populate `_posts/`, then the workflow only handles new ones
   Joshua to decide during REFINE.

4. **Body content.** ADR-0002 defaults to "metadata + excerpt + link back"
   pending the legal question of full-body republishing. Confirm this is
   still the desired default. If yes, where does the excerpt come from
   (RSS `<description>`, meta description on the article page, first
   paragraph of the article body)?

5. **PR creation tooling.** `peter-evans/create-pull-request` action is the
   ecosystem default. Confirm acceptable, or use raw `gh pr create`.

6. **Workflow language.** Ruby, Python, Node, or shell-with-curl-and-yq?

7. **Topic mapping.** Posts have a `topic: ensemble | adhs | softdev`
   frontmatter that drives filter chips on `/blog/` and the topic eyebrow
   on `/blog/:slug/`. How is topic determined for a synced article?
   - From INNOQ tags / categories?
   - Fixed default (e.g. `softdev`)?
   - Left empty, Joshua adds manually before flipping `published: true`?

8. **Failure / observability.** ADR-0002 noted "if INNOQ changes its feed
   structure, the workflow silently stops". Should the workflow fail loudly
   (set job status = failed, no PR opened) or open an empty / error-marker
   PR? GitHub Actions notification policy?

## Acceptance criteria (provisional — refine after research)

These are placeholders. The REFINE pass will sharpen them after the open
questions are resolved.

- [ ] A `.github/workflows/sync-innoq.yml` workflow runs on a daily cron
      AND supports `workflow_dispatch` for manual runs.
- [ ] The workflow discovers Joshua's INNOQ articles via the chosen
      mechanism (RSS feed if available, otherwise documented fallback).
- [ ] Only German articles are considered; English articles are explicitly
      filtered out and logged as skipped.
- [ ] For each new German article (no matching `canonical_url` in existing
      `_posts/`), the workflow opens one PR containing a new
      `_posts/<YYYY-MM-DD>-<slug>.md` with the frontmatter shape from
      ADR-0002 (`layout: post`, `title`, `date`, `source: innoq`,
      `canonical_url`, `published: false`).
- [ ] Already-synced articles (matching `canonical_url`) are not re-PR'd.
- [ ] Already-open sync PRs for the same article are not duplicated
      (PR branch naming convention or title check).
- [ ] First-run behaviour does not flood the repo with PRs — the chosen
      strategy (per open question #3) is implemented.
- [ ] After merging a sync PR, `bundle exec jekyll build` passes and the
      new article does NOT appear on the live site (because
      `published: false`).
- [ ] After Joshua manually flips `published: true` and pushes, the
      article appears in `/`, `/blog/`, and `/blog/:slug/`.
- [ ] Workflow failures are visible (job status = failed; notification via
      whatever GH Actions notification config Joshua has set).
- [ ] Documentation: `infrastructure` BC README updated with a short
      "Sync workflow" section pointing at the workflow file and explaining
      the German-only constraint and the two-step publish flow.

## Notes
- Spawn `research` next on "INNOQ staff page structure & per-author feed
  discovery for Joshua Töpfer". The research should answer open questions
  1, 2, and (if possible) 4 with concrete evidence (fetched feed sample,
  fetched HTML snippet of the staff page, observed URL patterns for German
  vs English articles).
- After research lands, REFINE this task: split open questions into
  decisions (some may want their own `type: decision` tasks producing
  ADR-0006), tighten acceptance criteria, and only then PROMOTE to `todo/`.
- The sync workflow itself does not need to wait for `website-004`
  (Hello-Welt cleanup) to finish — the two are independent. Joshua may
  prefer to land `website-004` first so the first sync PR isn't sitting
  next to placeholder posts, but that's a sequencing preference, not a
  technical dependency.
- ADR-0002 is canonical; do not duplicate its decisions in this task or in
  any new ADR. New ADRs should be written only for genuinely new
  decisions surfaced during REFINE (e.g. "use Python for the sync script",
  "first-run uses date cutoff at site launch").

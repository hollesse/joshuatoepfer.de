---
id: "0006"
title: "INNOQ sync architecture: dual-workflow (feed-poll + scrape-backfill) with full-body republishing and PR-history dedup"
scope: infrastructure
status: accepted
date: 2026-05-27
supersedes: []
superseded_by: []
related_tasks: [infra-004, infra-005]
related_research: [innoq-staff-feed-2026-05-27, innoq-staff-page-scrape-2026-05-27]
---

# ADR-0006: INNOQ Sync Architecture

## Context

ADR-0002 (2026-05-26) set the high-level content sync strategy for innoq.com →
joshuatoepfer.de: a scheduled GitHub Actions workflow that polls Joshua's
content, opens a draft PR per new article, never auto-publishes. It deferred
several implementation-level questions:

1. Whether to republish full article bodies or excerpts only (a legal/policy
   question about innoq's platform).
2. How to discover Joshua's historical articles (those published before the
   pipeline existed) given that the only available feed carries only the
   ~25 most-recent entries across all INNOQ authors.
3. How to dedup the sync — i.e. how to remember "we already PR'd this
   article, don't do it again" — without keeping a persistent state file.
4. How to handle the situation where a synced PR turns out to have a bug
   (e.g. broken Markdown conversion) and Joshua needs the pipeline to
   re-produce it without first un-merging the existing post.
5. Which workflow language to use (the existing CI workflow is Ruby/Jekyll,
   but the sync workflow has different needs).
6. How to pre-categorise synced articles' `topic:` frontmatter so Joshua
   doesn't have to fill it in manually for every post.

This ADR records the decisions made during `infra-004`'s refinement
(2026-05-27) and their implementation in `infra-004` and `infra-005`. It
is **additive** to ADR-0002, not superseding — ADR-0002 remains canonical
for the high-level strategy.

## Decisions

### 1. Dual workflow + shared Python module

There are two distinct discovery problems:

- **Incremental**: catch new articles as INNOQ publishes them. Works against
  the ~25-entry rolling feed window. Simple, predictable, can run on a
  daily cron.
- **Backfill**: catch the historical inventory (Joshua's pre-2026 articles
  outside the feed window). Requires scraping the staff page or its
  "More content" pagination — fragile, slow, and not something you want
  the daily cron doing.

Rather than building a single workflow with mode flags, we ship two
workflows:

- `sync-innoq.yml` (infra-004) — cron + manual dispatch, feed-poll
- `backfill-innoq.yml` (infra-005) — manual dispatch only, scrape-based

Both share `.github/scripts/innoq_common.py`, which carries the URL → slug
rules, frontmatter generation, HTML → Markdown conversion, the dedup logic,
and the per-entry filter chain. The two entry points (`sync_innoq.py`,
`backfill_innoq.py`) differ only in **how they discover articles**; once
they have a normalised `FeedEntry`, the downstream code path is identical.

Rationale:
- Two workflows means two separate Actions logs, separate failure
  notifications, separate triggers. Backfill failures don't poison the
  daily-cron health signal.
- A shared module keeps the URL → file conventions canonical. If the slug
  rule ever changes, it changes in one place.
- The dependency declaration is one-way: `infra-005` depends on `infra-004`
  so `innoq_common.py` exists before backfill's worker starts.

### 2. Full-body republishing

This resolves ADR-0002's open question. Joshua decided full-body
republishing is acceptable: he is the original author and the canonical
URL prominently links back to innoq.com from every post. INNOQ remains
the source of truth (and the asset host — images stay as remote
references; no local mirroring).

Mitigation if INNOQ ever objects: the conversion lives in
`convert_html_to_markdown()` in `innoq_common.py`. A one-line change to
the entry point — emit `entry.summary` instead of `entry.content_html` —
flips the pipeline back to excerpt-only without touching the workflow or
the frontmatter shape.

### 3. PR-history-based dedup

The pipeline needs to remember "we've already PR'd this article". The
candidate mechanisms were:

- **Persistent branches** — keep the sync branch alive after PR
  close/merge so `gh pr list --head <branch>` always finds it. Rejected:
  pollutes the active-branches list; old branches accumulate forever.
- **State file in the repo** (`_data/synced.yml` or similar) — a list of
  canonical URLs the pipeline has touched. Rejected: every sync run
  would need to commit the state file, doubling the PR count or
  requiring a second workflow step to push directly to main. Also creates
  merge conflicts if two sync runs race.
- **GitHub PR history** (chosen) — `gh pr list --state all --head <branch>`
  returns matches even after the branch is deleted. GitHub retains the
  PR record forever. Combined with `delete-branch: true` on
  `peter-evans/create-pull-request@v6`, this gives durable dedup with
  zero repo clutter.

Layered on top of PR-history dedup is a **`_posts/` canonical_url scan** —
if the article is already merged into the site (regardless of its
`published` state), the workflow skips it. This is the dedup mechanism
that protects against the backfill workflow racing with the daily cron:
once `infra-005` merges a backfilled post, the incremental workflow
respects it.

### 4. Force-resync via `workflow_dispatch` input

When a synced PR turns out to have a bug (broken conversion, INNOQ
updated the article post-sync, etc.), Joshua needs a way to ask the
pipeline to re-produce a specific article. The mechanism:

```yaml
workflow_dispatch:
  inputs:
    force_resync:
      type: string
      description: "Canonical URL(s) to re-sync, comma-separated."
```

Behaviour for each URL in the list:
- Bypasses both dedup checks (`_posts/` scan, PR-history scan) for that
  URL only — all other entries in the feed still go through normal dedup.
- Reads the existing `_posts/<date>-<slug>.md` if present, extracts its
  `topic:` and `published:` values, and writes them into the regenerated
  file's frontmatter. This preserves Joshua's manual edits across the
  re-sync.
- Branch name carries a UTC timestamp suffix:
  `sync/innoq/<slug>-resync-<YYYYMMDDTHHMMSSZ>` — avoids colliding with
  the historical PR's `head.ref`.

Failure mode: if a force-resync URL isn't in the current feed window, the
job exits non-zero with `"force_resync requested for <url> but article
not in current feed window; nothing to sync"`. The user is pointed at
`infra-005`'s backfill workflow for articles that have rolled off.

Rejected alternatives:
- Re-running the workflow after manually deleting the existing post — too
  destructive (loses Joshua's `topic:` and `published:` edits) and
  requires Joshua to know the internal slug rule.
- A separate "re-sync" workflow — duplicates 90 % of the incremental
  workflow's logic.

### 5. Python over Ruby

The existing CI workflow (`deploy.yml`) uses `ruby/setup-ruby@v1` to
build Jekyll. The sync workflow could have followed the same convention.
We chose Python instead because:

- Python is pre-installed on `ubuntu-latest` runners — no `setup-ruby`
  step, fewer moving parts on the cron path.
- `feedparser` is the canonical Atom-handling library in any language
  ecosystem; the Ruby equivalents (`rss`, `feedjira`) are less ergonomic
  for the per-entry shape we need.
- `markdownify` for HTML → Markdown has a clean callback API for the
  `language-xxx` code-block class.
- Joshua already maintains Python tooling elsewhere; this isn't a new
  ecosystem on the project's plate.

The runtime cost is a single `pip install --quiet feedparser markdownify
pyyaml` step, which takes seconds. The benefit is that the script can be
developed and tested locally without `bundle install`-ing the whole
Jekyll stack.

### 6. `topic:` frontmatter left blank

The synced post's `topic:` is **not pre-filled**. The Atom feed has no
`<category>` element (verified by research
`innoq-staff-feed-2026-05-27`), so there's no reliable signal to
auto-derive a topic. The three project topics — `ensemble | adhs |
softdev` — don't map cleanly onto INNOQ's URL patterns.

Rather than picking a fixed default like `softdev` that would be wrong
for most of Joshua's `ensemble` articles, we leave the field absent.
Joshua fills it in manually as part of the publish step (alongside
flipping `published: true`). The PR body explicitly reminds him.

This is a *correction-cost* decision: filling in a blank is easier than
correcting a wrong guess. The two-step publish flow already requires
Joshua to open the file to flip `published: true`; adding `topic:` to
that edit is free.

## Consequences

### Positive
- Two-workflow split means daily-cron failures and one-off backfill
  failures are observable independently.
- Shared module keeps URL → file conventions canonical and testable.
- PR-history dedup needs zero ongoing maintenance.
- Force-resync covers the realistic "I need to re-do this article" case
  without ever requiring `git reset` on `_posts/`.
- Python keeps the workflow lightweight; no Ruby setup overhead on every
  daily run.
- Blank `topic:` minimises the rate at which Joshua has to correct a
  wrong default.

### Negative
- Two workflow files mean two places to update if the conventions
  evolve (mitigated by the shared module — only the discovery code is
  duplicated).
- PR-history dedup is GitHub-specific. If the project ever moves to a
  different forge, the dedup mechanism needs replacing.
- Force-resync's "must be in current feed window" failure mode is a
  rough edge for the historical case, but the backfill workflow covers
  that path explicitly.

## Alternatives Considered (summary)

| Decision axis | Chosen | Rejected |
| --- | --- | --- |
| Workflow shape | Two workflows + shared module | Single workflow with mode flags |
| Body republishing | Full body | Excerpt-only (deferred from ADR-0002) |
| Dedup memory | PR history (GitHub) | Persistent branches; state file in repo |
| Re-sync mechanism | `workflow_dispatch` input with URL list | Manual delete + cron rerun; separate workflow |
| Workflow language | Python | Ruby (would need `setup-ruby` step) |
| `topic:` default | Blank — Joshua fills | Fixed default (`softdev`) |

## Related work

- ADR-0002 — canonical content sync strategy (this ADR is additive to it)
- `infra-004` — implements the incremental feed-poll workflow per this ADR
- `infra-005` — will implement the historical backfill workflow per this ADR
- Research `innoq-staff-feed-2026-05-27` — confirmed feed shape, language
  signal, and content-type inference rules
- Research `innoq-staff-page-scrape-2026-05-27` — informs `infra-005`'s
  scrape mechanism (out of scope here)

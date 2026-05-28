---
name: innoq-sync
description: How Joshua's INNOQ articles are mirrored to joshuatoepfer.de as syndicated draft posts, with a manual publish gate.
context: infrastructure
created: 2026-05-28
last_updated: 2026-05-28
derived_from:
  - 0002             # ADR — Content sync strategy (canonical)
  - 0006             # ADR — INNOQ sync architecture (additive)
  - innoq-staff-feed-2026-05-27
  - innoq-staff-page-scrape-2026-05-27
  - infra-002        # done — Decision task that produced ADR-0002
  - infra-004        # done — Incremental feed-poll workflow
  - infra-005        # backlog — Historical backfill workflow (depends_on infra-004)
max_lines: 60
---

# INNOQ sync — concept

## What it is
The automated mirror from INNOQ to joshuatoepfer.de. Joshua's German INNOQ
articles arrive on his personal site as draft `_posts/*.md` files via PR
(one PR per article), and he decides per article whether to flip them
visible.

## Why it exists
Joshua publishes substantial work on INNOQ but wants his personal site to
reflect his body of work without manual copy-paste and without losing
editorial control. Auto-publish was rejected (see ADR-0002 alternatives);
INNOQ content is mixed German + English, and only German matters here.

## Current shape
Two workflows, one shared Python module, one filter chain, one dedup chain:

- **`sync-innoq.yml`** (live, infra-004) — daily cron + manual dispatch.
  Polls `/de/feed.atom`, creates one PR per eligible new entry.
- **`backfill-innoq.yml`** (planned, infra-005) — manual dispatch only.
  Scrapes `/de/written/?by=joshua-toepfer` for articles outside the
  feed's ~25-entry rolling window.
- **`.github/scripts/innoq_common.py`** — shared helpers: URL → slug,
  `_posts/`-based + PR-history dedup, HTML→Markdown via `markdownify`,
  frontmatter generation, force-resync state preservation.
- **Filter chain** (both): author email `joshua.toepfer@innoq.com` ·
  `xml:lang=de` (feed) or `/de/` URL prefix · `/articles/` path segment
  (talks, podcasts, blog posts skipped).
- **Dedup chain**: `canonical_url` already in any `_posts/*.md` OR
  `gh pr list --state all --head <branch>` ≥ 1. Branches are deleted on
  PR close; the PR history itself is the dedup memory.
- **Two-step publish**: synced PRs land with `published: false` and no
  `topic`. Joshua merges, then separately edits to fill in `topic` and
  flip `published: true`. The merge step and the publish step are
  deliberately separate.
- **Force-resync** (infra-004 only): `workflow_dispatch` with
  `force_resync` URL input bypasses dedup, preserves existing file's
  `topic`/`published`, opens a timestamped re-sync branch.

## Open questions
- `infra-005` is unblocked but not yet promoted — decision is user's.
- Failure-path smoke test is documented in the BC README; awaits
  Joshua's first manual trigger post-deploy.
- Topic frontmatter is intentionally manual; revisit if INNOQ ever
  exposes a topic signal that maps to `ensemble | adhs | softdev`.

## See also
- `[ADR 0002]` — content sync strategy (canonical)
- `[ADR 0006]` — sync architecture (additive; closes ADR-0002's full-body question)
- `[research/innoq-staff-feed-2026-05-27]` — feed shape
- `[research/innoq-staff-page-scrape-2026-05-27]` — scrape feasibility
- `[done/infra-002]` · `[done/infra-004]` · `[backlog/infra-005]`

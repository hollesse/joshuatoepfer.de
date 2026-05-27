---
id: infra-004
title: "INNOQ author sync pipeline — incremental, feed-based (German articles only)"
status: done
type: feature
context: infrastructure
created: 2026-05-27
completed: 2026-05-27
commit:
depends_on: []
blocks: [infra-005]
tags: [sync, innoq, github-actions, pipeline, content, python]
related_adrs: [0002, 0006]
related_research: [innoq-staff-feed-2026-05-27]
prior_art: [infra-002]
---

## Why
ADR-0002 (2026-05-26) decided the content-sync strategy for innoq.com →
joshuatoepfer.de: a scheduled GitHub Actions workflow that polls Joshua's
author feed daily, opens a draft PR per new article, never auto-publishes.
The decision was made; the workflow has not yet been built. `_posts/` is
currently just the Hello-Welt placeholder (cleaned up by `website-004`).
Real INNOQ articles need to start appearing as draft PRs so the site stops
being a hand-curated placeholder.

A constraint added today (2026-05-27): **only German articles count.**
Joshua writes some articles in English and some in German on innoq.com.
For his personal site only the German ones are interesting; English
articles must be filtered out.

Research on 2026-05-27 (`innoq-staff-feed-2026-05-27`) confirmed: INNOQ
publishes **no per-author feed**. The only available feed is the
site-wide rolling Atom at `/de/feed.atom` (~20–25 most recent entries),
carrying `<author><email>` metadata and `<content xml:lang>`. Joshua's
older INNOQ articles (2021–2023) are outside the feed's rolling window
— they need a different mechanism, handled by sibling task `infra-005`
(historical backfill, scrape-based). **This task is the incremental
side: feed-poll only.**

## Architecture (two workflows, one shared Python module)

This task delivers Workflow A. Sibling task `infra-005` delivers
Workflow B. They share a Python helper module.

```
.github/
├── workflows/
│   ├── sync-innoq.yml       ← this task (infra-004): cron + manual incremental
│   └── backfill-innoq.yml   ← infra-005: workflow_dispatch only, scrape-based
└── scripts/
    ├── sync_innoq.py        ← this task: feed-poll entry point
    ├── backfill_innoq.py    ← infra-005: scrape entry point
    └── innoq_common.py      ← this task: shared helpers (URL → slug,
                                frontmatter generation, Markdown
                                conversion, PR creation, dedup)
```

infra-005 imports `innoq_common.py` — so this task ships the shared
module along with the incremental-sync entry point.

## What
Implement `.github/workflows/sync-innoq.yml` plus `sync_innoq.py` plus
`innoq_common.py` so that:

- The INNOQ Atom feed is polled daily (cron) and on demand (manual dispatch)
- New German articles by Joshua trigger draft-status `_posts/` PRs
- Articles in other languages, by other authors, and non-article content
  types (talks, podcasts, blog) are silently filtered out (logged but no PR)
- Already-synced and previously-PR'd articles are skipped
- A manual force-resync escape hatch exists for cases where the original
  sync had a bug or the INNOQ article was updated after sync
- No historical backfill happens here (that's `infra-005`'s job)

## Decisions (all open questions resolved 2026-05-27)

### Feed source and filter chain
- **Source:** `https://www.innoq.com/de/feed.atom` (Atom 1.0, ~25-entry rolling)
- Filter chain — entries must pass **all** of these or get skipped with a log line:
  1. `<author>` block with `<email>joshua.toepfer@innoq.com</email>`
  2. `<content xml:lang="de">` (or equivalent `xml:lang` on the entry)
  3. `<link href>` path contains `/de/`
  4. `<link href>` path segment is `/articles/` (skip `/talks/`, `/podcast/`, `/blog/`, `/written/`)

### Body content — full article body, not excerpt
- Atom `<content type="html">` is extracted, then converted to Markdown via
  Python `markdownify` (or `html2text` — worker picks based on output
  quality testing on Joshua's actual articles)
- **Images stay as remote references** — `<img src="https://www.innoq.com/...">`
  preserved verbatim; no local asset mirroring. INNOQ remains the asset source.
- **Fenced code blocks** with language hints preserved (Markdown ` ```python `).
- Post frontmatter sets `render_with_liquid: false` so any `{{ … }}` in the
  original article body isn't re-parsed by Jekyll's Liquid engine.
- This resolves ADR-0002's open question about full-body vs excerpt-only.
  Joshua has decided full body is OK (resolution noted here; ADR-0002 stays
  as the canonical strategy doc, this task's commit message will reference
  the resolution).

### Workflow language — Python
- Pre-installed in `ubuntu-latest` GH Actions runner; no setup step needed
- Mature Atom tooling: `feedparser` for parsing, `markdownify` for HTML→MD,
  `pyyaml` for frontmatter, standard `requests` for any extra fetches
- Worker uses `python -m pip install --user feedparser markdownify pyyaml`
  in the workflow step rather than introducing a `pyproject.toml`

### Dedup chain — PR-history based, no persistent branches
For each feed entry that survives the filter chain:

1. **`canonical_url` exists in any `_posts/*.md` frontmatter** → skip
   (article is already merged, whether published or not)
2. **`gh pr list --state all --head sync/innoq/<slug>` returns ≥ 1** → skip
   (the workflow has opened a PR for this article at some point — open,
   merged, or closed-without-merge — and GitHub's PR record persists
   even after the branch is deleted, so we don't need to keep branches
   alive)

Use `delete-branch: true` in `peter-evans/create-pull-request@v6` so
branches don't accumulate in the repo. The dedup token is the PR record
in GitHub's history (visible only under the Closed PRs tab — does not
clutter the active branch list).

### Force-resync via workflow_dispatch input
```yaml
on:
  workflow_dispatch:
    inputs:
      force_resync:
        description: "Canonical URL(s) to re-sync, comma-separated. Empty = normal incremental run."
        required: false
        type: string
```

Behavior:
- **`force_resync` empty (default)** → normal incremental run with full dedup
- **`force_resync` non-empty** → for each URL listed, the workflow:
  - **Bypasses** both dedup checks (the `_posts/` match and the PR history match)
  - **Reads the existing `_posts/<date>-<slug>.md`** if it exists — preserves
    its current `topic:` and `published:` frontmatter values so Joshua's
    manual edits aren't lost
  - **Regenerates the body** from the current feed entry's `<content>` →
    Markdown
  - **Overwrites the file** in the new branch
  - **Branch name carries a timestamp suffix:**
    `sync/innoq/<slug>-resync-<UTC-timestamp>` — avoids colliding with the
    historical PR's `head.ref`
  - **All other feed entries** still go through normal dedup (force-resync
    is per-URL, not global)
- **Failure mode:** if a force-resync URL isn't in the current feed window,
  the workflow exits non-zero with `"force_resync requested for <url> but
  article not in current feed window; nothing to sync"`. For articles that
  rolled off the window, use `infra-005`'s backfill workflow instead.

### PR creation
- Action: `peter-evans/create-pull-request@v6` with `delete-branch: true`
- Branch name: `sync/innoq/<slug>` (incremental) or
  `sync/innoq/<slug>-resync-<UTC-timestamp>` (force-resync)
- PR title: `Sync: <Atom title> [innoq.com]`
- PR label: `sync-innoq`
- PR body: short, includes the canonical URL, the matched filter chain
  outcome, and a footer instructing Joshua how to flip `published: true`
- One PR per article (no batching)

### Topic mapping
- The synced post's frontmatter has `topic:` **left empty**. The Atom feed
  has no `<category>`, so no topic can be inferred. Joshua fills it in
  manually (`ensemble | adhs | softdev`) as part of the publish step,
  before flipping `published: true`.
- This is preferable to a fixed `softdev` default that would mis-categorise
  many articles and require Joshua to "correct" the default rather than
  add information.

### Failure mode and observability — fail loudly
- The workflow job exits non-zero on any of:
  - Feed unreachable (HTTP error, timeout, DNS failure)
  - Feed unparseable (malformed XML)
  - GitHub API write failure (PR creation rejected)
  - Force-resync URL not in feed window
- **No "error-marker PR" path.** A failed run is visible via:
  - Job status = failed in the Actions tab
  - GitHub Actions default failure email to Joshua per his current
    notification settings
- A smoke test in the workflow's first commit verifies the failure path
  is observable: a deliberately-broken feed URL in a workflow input, run
  once, confirm the job goes red and an email arrives.

### Feed-window risk — accept it
- Daily cron `0 3 * * *` UTC. Manual `workflow_dispatch` available for
  immediate-after-publish runs.
- Mitigation if an article rolls off the window before a daily poll catches
  it: use `infra-005`'s backfill workflow (URL input mode) to recover it.
- No hourly cron, no poll-on-push webhook — these add complexity for an
  edge case Joshua can easily handle manually with `infra-005`.

## Synced post frontmatter (the deliverable shape)

```yaml
---
layout: post                # inherited from _config.yml defaults; safe to omit
title: "<Atom <title> verbatim>"
date: <YYYY-MM-DD from Atom <published>>
source: innoq
canonical_url: <full URL from Atom <link href>>
published: false
render_with_liquid: false
# topic: left blank — Joshua fills in manually before publishing
---

<Markdown-converted body from Atom <content type="html">>
```

## Files delivered by this task

| File | Purpose |
| --- | --- |
| `.github/workflows/sync-innoq.yml` | Cron + `workflow_dispatch` triggers; sets up Python; runs `sync_innoq.py`; passes through `force_resync` input |
| `.github/scripts/sync_innoq.py` | Entry point: fetches feed, runs filter chain, calls into `innoq_common` for dedup + frontmatter + PR creation |
| `.github/scripts/innoq_common.py` | Shared with `infra-005`: URL → slug, frontmatter generator, HTML → Markdown converter, dedup against `_posts/` + PR history, PR creation wrapper around `gh` CLI |
| `infrastructure/README.md` | Updated with "Sync workflow" section pointing at the workflow file, explaining German-only + articles-only filter chain, the two-step publish flow, and the force-resync escape hatch |

## Acceptance criteria

- [ ] `.github/workflows/sync-innoq.yml` runs on `cron: '0 3 * * *'` UTC and on `workflow_dispatch` with the `force_resync` string input as defined above.
- [ ] The workflow installs Python deps (`feedparser`, `markdownify`, `pyyaml`) and invokes `python .github/scripts/sync_innoq.py`.
- [ ] `sync_innoq.py` fetches `https://www.innoq.com/de/feed.atom` and runs every entry through the four filter steps (author email, xml:lang, /de/ URL, /articles/ path). Failed-filter entries are logged with the failing step and skipped.
- [ ] For each surviving entry, the dedup chain runs: (a) check `canonical_url` against all `_posts/*.md` frontmatter, (b) check `gh pr list --state all --head sync/innoq/<slug>`. Any match → skip.
- [ ] For each entry surviving dedup, the workflow opens **one** PR via `peter-evans/create-pull-request@v6` with `delete-branch: true`, branch `sync/innoq/<slug>`, title `Sync: <title> [innoq.com]`, label `sync-innoq`, and a file `_posts/<YYYY-MM-DD>-<slug>.md` containing the frontmatter shape above plus the markdownify-converted body.
- [ ] When `force_resync` input is non-empty, the workflow processes each comma-separated URL: bypasses both dedup checks for that URL only, preserves the existing file's `topic` and `published` values, overwrites the body, and creates a PR with branch `sync/innoq/<slug>-resync-<timestamp>`.
- [ ] If a `force_resync` URL isn't in the current feed window, the workflow exits non-zero with the specified error message.
- [ ] The workflow exits non-zero (job fails) on: feed unreachable, feed unparseable, or GitHub API write failure. Joshua receives the standard GH Actions failure email.
- [ ] `.github/scripts/innoq_common.py` is structured as an importable module — `infra-005` later imports it via `from innoq_common import ...`.
- [ ] After merging a sync PR, `bundle exec jekyll build` passes and the article does **not** appear on the live site (because `published: false`).
- [ ] After Joshua manually sets `published: true` (and optionally adds `topic:`), the article appears in `/`, `/blog/`, and at `/posts/<YYYY>/<MM>/<DD>/<slug>/`.
- [ ] `infrastructure/README.md` has a "Sync workflow" section per the table above.
- [ ] Worker writes a new ADR (likely `ADR-0006`) covering this task's architectural decisions that go beyond ADR-0002: full-body republishing, dual-workflow (feed + backfill) split, PR-history-based dedup, force-resync mechanism. ADR-0002 stays as-is; `ADR-0006` is additive, not superseding.

## Notes
- The historical backfill that ADR-0002 alluded to is **not** in scope here. It is `infra-005`. Joshua's pre-2026-05-27 articles are not touched by this workflow. The dedup check ensures that once `infra-005` (or any other process) lands a `_posts/<…>.md` file with a matching `canonical_url`, the incremental workflow respects it.
- `infra-005` is currently being researched (`innoq-staff-page-scrape-2026-05-27`, in progress at time of this REFINE). When that research lands, `infra-005`'s acceptance criteria will be tightened. `infra-005` declares `depends_on: [infra-004]` so the shared Python module exists before its worker starts.
- ADR-0002 remains canonical for the high-level strategy. ADR-0006 (to be written during work) captures the implementation-level architectural decisions made in this REFINE.
- Sequencing preference (not a technical dependency): `website-004` (already merged 2e85ac8) cleaned `_posts/`, so the first sync PR lands next to the Hello-Welt placeholder rather than fake content. Already done.

## Outcome

Delivered the incremental INNOQ → joshuatoepfer.de sync pipeline:

- `.github/workflows/sync-innoq.yml` — daily cron (`0 3 * * *`) plus
  `workflow_dispatch` with `force_resync` and `feed_url_override` inputs.
  Two-job shape: a `plan` job builds the per-article JSON plan, a
  matrix-strategy `publish` job opens one PR per article via
  `peter-evans/create-pull-request@v6` (`delete-branch: true`).
- `.github/scripts/sync_innoq.py` — entry point: fetches the feed,
  applies the four-step filter chain (author email, `xml:lang`, `/de/`
  path, `/articles/` segment), runs the two-step dedup chain
  (`_posts/*.md` canonical_url scan + `gh pr list` PR-history check),
  branches into force-resync mode when `FORCE_RESYNC` is set
  (timestamped branch, preserves `topic:`/`published:` from any existing
  file). Fails loud on feed-unreachable, feed-unparseable, `gh` errors,
  and force-resync-not-in-window.
- `.github/scripts/innoq_common.py` — shared module that `infra-005`
  will import: `FeedEntry` dataclass, slugify, frontmatter generator,
  HTML → Markdown conversion (markdownify with ATX headings + fenced
  code-block language hints + remote-image passthrough), dedup helpers,
  filter chain.
- `.github/scripts/test_innoq_common.py` — 22 unit tests covering
  slugify, HTML conversion, filter chain, frontmatter generation,
  `_posts/` scanning, force-resync input parsing, and branch naming.
  All pass under Python 3.14 with `feedparser` + `markdownify` +
  `pyyaml`.
- `.agentheim/knowledge/decisions/0006-innoq-sync-architecture.md` — ADR
  covering dual-workflow split, full-body republishing (resolves
  ADR-0002's deferred legal question), PR-history dedup,
  `workflow_dispatch` force-resync, Python-over-Ruby, blank-topic
  decision.
- `.agentheim/contexts/infrastructure/README.md` — new "Sync workflow"
  section explaining the filter chain, dedup, two-step publish, the
  force-resync escape hatch, and the smoke-test procedure.

**Smoke test pending:** the acceptance criterion calls for a one-time
manual verification that a deliberately-broken `feed_url_override`
turns the job red and triggers Joshua's GitHub Actions failure email.
This worker cannot push to GitHub or trigger Actions; the README
documents the exact steps for Joshua to run after the first deploy.

**Verified locally:** running `sync_innoq.py` with
`FEED_URL_OVERRIDE=https://this-domain-does-not-exist.invalid/feed.atom`
exits non-zero with `RuntimeError: Feed fetch failed for ...`. The
gh-cli unauth path also fails loudly (`PR-history dedup failed: ...`)
rather than silently over-skipping.

Key files (absolute paths):
- `/Users/joshuatopfer/Documents/Projekte/Privat/joshuatoepfer.de/.github/workflows/sync-innoq.yml`
- `/Users/joshuatopfer/Documents/Projekte/Privat/joshuatoepfer.de/.github/scripts/sync_innoq.py`
- `/Users/joshuatopfer/Documents/Projekte/Privat/joshuatoepfer.de/.github/scripts/innoq_common.py`
- `/Users/joshuatopfer/Documents/Projekte/Privat/joshuatoepfer.de/.github/scripts/test_innoq_common.py`
- `/Users/joshuatopfer/Documents/Projekte/Privat/joshuatoepfer.de/.agentheim/knowledge/decisions/0006-innoq-sync-architecture.md`
- `/Users/joshuatopfer/Documents/Projekte/Privat/joshuatoepfer.de/.agentheim/contexts/infrastructure/README.md`

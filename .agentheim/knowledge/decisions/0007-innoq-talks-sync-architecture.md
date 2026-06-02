---
id: "0007"
title: "INNOQ talks sync architecture: scrape-only workflow with update-in-place, URL identity, and source marker for hand-edit coexistence"
scope: infrastructure
status: accepted
date: 2026-06-02
supersedes: []
superseded_by: []
related_tasks: [infra-011]
related_research: [innoq-talks-page-2026-06-02, innoq-staff-feed-2026-05-27, innoq-staff-page-scrape-2026-05-27]
---

# ADR-0007: INNOQ Talks Sync Architecture

## Context

`infra-011` introduces a third INNOQ sync surface alongside the article incremental sync
(`infra-004`) and the article backfill (`infra-005`): a workflow that mirrors Joshua's
talk history from `https://www.innoq.com/de/talks/?all=true&by=joshua-toepfer` into the
site's `_data/talks.yml`. The site already renders that file from
`_layouts/talks.html` and the talks schema (see `website/README.md` → "Data file shapes")
is unchanged: `date`, `what`, `where`, `city`, `status`, `type`, `duration`, `abstract`,
optional `slides`, optional `video`.

The article sync architecture (ADR-0006) does not transfer wholesale. Three things differ:

1. **No feed.** Research `innoq-talks-page-2026-06-02` confirmed that no `talks.atom` or
   per-author feed exists. Even the global `/de/feed.atom` rolling window is too narrow.
   Scrape is the only option.
2. **One file, not one-file-per-content.** Articles live as one Markdown file per article
   under `_posts/`. Talks live as entries inside a single YAML file. PR-history dedup
   by branch name keyed on slug ("we already PR'd this") does not work the same way.
3. **Updates, not just inserts.** Articles are append-only — once a `_posts/*.md` lands
   it isn't touched. Talks must be updateable: `upcoming` → `past` flips when the date
   passes; `slides` is added after the talk; entry titles or event names may be cosmetically
   edited on INNOQ. The sync must be free to *modify* existing entries.

`infra-011`'s original capture surfaced seven open questions; this ADR resolves them so
the worker can pick up the task.

## Decisions

### 1. Scrape-only workflow + new shared module `innoq_talks.py`

Mirroring `infra-005`'s posture: there is no feed, so the workflow scrapes
`https://www.innoq.com/de/talks/?all=true&by=joshua-toepfer` and follows the paginator's
`<a rel="next">` until exhausted. For each listing entry the workflow then fetches the
talk's detail page to pick up the city and abstract (both absent from the listing — see
research §3).

Code shape:

```
.github/
├── workflows/
│   ├── sync-innoq.yml         ← infra-004 (article incremental, feed)
│   ├── backfill-innoq.yml     ← infra-005 (article backfill, scrape)
│   └── sync-innoq-talks.yml   ← THIS ADR
└── scripts/
    ├── sync_innoq.py
    ├── backfill_innoq.py
    ├── sync_innoq_talks.py    ← THIS ADR (workflow entry point)
    ├── innoq_talks.py         ← THIS ADR (talk-page parsing, YAML diff)
    └── innoq_common.py        ← HTTP politeness + User-Agent stay here; reused
```

The shared `innoq_common.py` keeps the **generic HTTP primitives** — `fetch_with_retry`,
the identifying User-Agent constant, the 2 s politeness delay, exponential backoff on 5xx,
no-retry-on-4xx, `Retry-After`-aware 429 handling, the slug helper. It does **not** grow
talk-specific selectors or YAML diff logic.

The new `innoq_talks.py` carries everything talks-specific:

- `parse_listing(soup) -> list[TalkListEntry]` — selects `a.list-teaser-event` and
  extracts the listing-side fields (date, title, event, optional duration, type, slides
  flag, detail URL).
- `parse_detail(soup) -> TalkDetailFields` — extracts city (`<dl> "Ort"` last comma
  segment), abstract (`<article>` paragraphs before `<dl>`), slides URL (`a.btn` whose
  `href` contains `fl_attachment:`), duration fallback (`<dl> "Uhrzeit"`).
- `merge_talks(existing_yaml, scraped_entries) -> updated_yaml` — the diff/merge
  engine. See §3 for its semantics.
- `derive_status(date, today) -> "upcoming" | "past"` — pure function.

Rationale for keeping the modules separate rather than dumping helpers into
`innoq_common.py`: talk parsing pulls in selectors (`list-teaser-event`,
`date-location-section`, the "Ort" / "Uhrzeit" `<dt>` walk) and a schema
(`_data/talks.yml` keys + the source-marker convention) that the article workflows do not
need. Co-locating them with the talks entry-point keeps the article scripts' surface
narrow and makes the talks module independently testable.

### 2. Identity key: the canonical talk detail URL

Each `_data/talks.yml` entry that originates from INNOQ carries a new
`source_url: <full URL>` field — the canonical talk detail URL, e.g.
`https://www.innoq.com/de/talks/2026/03/four-years-one-ensemble-…/`.

Cross-run matching:

1. For each scraped entry, compute its absolute detail URL from
   `a.list-teaser-event[href]`.
2. For each existing `_data/talks.yml` entry where `source: innoq`, read `source_url`.
3. **Match by `source_url`.** Identity is the URL string, exact match.

Rationale (per research §4): the URL is exposed verbatim on the listing's `<a href>` and
repeated in the detail page's `<meta property="og:url">`. INNOQ's URL design embeds
`YYYY/MM/<slug>` and shows no evidence of post-publication renumbering. URL-based
identity survives cosmetic edits to `what` or `where`; the website BC's declared
composite `(what, where, date)` aggregate identity (see `website/README.md`) does not.

**Fallback for the one-time migration of today's hand-curated entries** (which have no
`source_url` yet): match by the website BC's composite key `(what, where, date)`. If a
scraped entry composite-matches an existing entry that lacks `source_url`, the worker
**must not silently merge** — surface the candidate matches in the PR body for Joshua's
manual ack on first run. After that first sync, every INNOQ-origin entry has a
`source_url` and the fallback no longer fires. See §9 for the migration's full mechanics.

### 3. Update semantics: INNOQ-authoritative vs. Joshua-authoritative fields

`_data/talks.yml` entries originating from INNOQ are not append-only. Each sync run must
re-derive each field and decide whether to overwrite or preserve. The rule:

| Field | Authority | Rationale |
|---|---|---|
| `date` | INNOQ | Source of truth on INNOQ; Joshua doesn't edit dates locally. Used to derive `status`. |
| `what` | INNOQ | Talk title comes from INNOQ. Cosmetic local edits would drift. |
| `where` | INNOQ | Conference / event name comes from INNOQ. |
| `city` | INNOQ | Parsed from `<dl> "Ort"` last-comma segment. |
| `type` | INNOQ | From the `type-label` mapping (`Vortrag → talk`, `Workshop → workshop`, `Keynote → keynote`). Unknown labels default to `talk` with a WARN log. |
| `duration` | INNOQ | Parsed from the listing subheadline (`/ HH:MM - HH:MM`) or the detail page's `<dl> "Uhrzeit"`. Omitted if absent on both. |
| `abstract` | INNOQ | From the detail page `<article>` paragraphs before `<dl>`. |
| `slides` | INNOQ | From the detail page `a.btn[href*="fl_attachment:"]`. Omitted if not on INNOQ. |
| `status` | **derived** | `upcoming` if `date >= today_utc`, else `past`. Never read from INNOQ; computed at sync time. |
| `video` | **Joshua** | Not observed on any sampled INNOQ talk detail page (research §3, finding 4). Treat as Joshua-only — preserve across syncs, never write or overwrite from INNOQ. |
| `source` | **convention** | Always `innoq` for entries the sync created or maintains. See §4. |
| `source_url` | **fixed** | Set once on first sync of an entry; never changes thereafter (identity). |

**Net effect:** on every sync, an INNOQ-origin entry's INNOQ-authoritative fields are
**fully re-derived from the live INNOQ page and overwritten** — Joshua's local edits to
those fields will be lost on the next sync. The only fields safe to edit on `source: innoq`
entries are `video` and (per §4) the `source` value itself.

This is a deliberate trade-off: it keeps the diff logic trivial (no field-level merge,
no three-way diff) and matches Joshua's intent — the whole point of the sync is that
INNOQ stays the source of truth. The PR body will spell this out so a reviewer notices
when their edit will be steamrolled.

### 4. Hand-edit coexistence: `source: innoq | manual` marker

Every entry in `_data/talks.yml` carries a `source:` field. Values:

- `source: innoq` — entry was created by, and is maintained by, the talks sync workflow.
  Carries a `source_url`. Subject to the §3 update semantics.
- `source: manual` — entry is hand-curated. The sync workflow **never touches** these
  entries: not for status flips, not for ordering, not even to add a `source_url`. The
  sync's read path filters them out before matching; its write path passes them through
  untouched.

This covers two important cases:

1. **Internal speaking engagements** not on INNOQ (e.g. a company offsite talk). Joshua
   can add them by hand with `source: manual` and they survive every sync.
2. **One-off corrections** to past INNOQ talks where the local edit must stick. The
   recovery path is: flip the entry's `source` from `innoq` to `manual`, the next sync
   leaves it alone, and INNOQ will create a fresh `source: innoq` duplicate which Joshua
   merges away on PR review. This is intentional friction — it makes "diverge from
   INNOQ" a visible decision rather than a silent edit.

### 5. Diff and PR shape: one PR per sync run, overwriting the file

When the merge step produces a YAML different from the on-disk file, the workflow opens
**one PR** containing the full overwrite. The PR body summarises the diff in three
buckets:

- **New talks** — entries present on INNOQ but absent from `_data/talks.yml`.
- **Status transitions** — entries whose `status` flipped `upcoming` → `past` (or rarely
  the reverse, if INNOQ moved a future-dated talk earlier).
- **Field updates** — entries where INNOQ-authoritative fields changed (slides added,
  title edited, etc.).

Rejected alternatives:

- **One PR per logical change** (separate PRs for new / status / materials). Rejected:
  multiplies review burden; `_data/talks.yml` is one file so the PRs would conflict with
  one another. The current capture's "initial recommendation" stands.
- **No-diff status flips** (auto-merge for "just `upcoming` → `past`" cases). Rejected as
  premature: Joshua wants every sync PR to be reviewable, consistent with `infra-004`'s
  article posture. Can be revisited if status-flip volume becomes annoying.

### 6. Schedule: weekly cron + `workflow_dispatch`

Talks change much less frequently than articles. The cron runs **weekly on Sundays at
04:00 UTC** (`0 4 * * 0`), staggered an hour off the article sync's daily 03:00 UTC to
avoid stepping on its runner if anything ever shares a cache. `workflow_dispatch` is
always available so Joshua can re-run after returning from a conference.

Daily would be wasteful: typical conference cadence is on the order of one talk per
quarter, and even slides/video additions trickle in over weeks. The weekly cadence keeps
the GHA-minutes budget low and the PR noise minimal.

### 7. Branch namespace: `sync/innoq-talks/<YYYY-MM-DD>`

The branch is named with the **run date** (UTC), e.g.
`sync/innoq-talks/2026-06-02`. Distinct from `sync/innoq/` (article incremental) and
`backfill/innoq/` (article backfill) so the three workflows' PRs are visually separable
in the PR list. All three sync families share the `sync-innoq` label so one filter
returns everything from INNOQ.

Slug-per-entry naming (e.g. `sync/innoq-talks/<talk-slug>`) does not work here because a
sync run can produce a single PR that touches many entries — there's no one slug.

### 8. PR-history dedup: close-prior-then-open-new

The article sync's PR-history dedup ("if a PR was ever opened for this branch, skip")
doesn't translate: each talks-sync run produces a new date-stamped branch, so the dedup
question is different. The question is "what if a previous sync PR is still open and
unmerged when the next sync runs".

**Decision:** before opening a new sync PR, the workflow checks for any **open** PRs on a
branch matching `sync/innoq-talks/*`. If one exists, the workflow **closes it (with a
comment pointing at the new PR)** and then opens the fresh PR on the new date-stamped
branch. Merged or already-closed PRs are ignored.

Rationale:

- Keeping multiple open sync PRs side by side creates merge conflicts on the same file
  with no benefit — the newer PR strictly supersedes the older one (it contains every
  field-update the older one carried plus whatever changed since).
- Force-pushing onto the older branch (the "amend" alternative) loses the audit trail of
  the prior sync attempt. Closing-with-comment preserves it.
- The decision is reversible: if Joshua ever prefers the amend approach, swap the
  close-call for a force-push — same surface area.

### 9. One-time migration of the existing `_data/talks.yml`

The current `_data/talks.yml` has 11 hand-curated entries with no `source:` field
(see the file as of 2026-06-02). Adopting the source-marker convention requires every
existing entry to be tagged. This migration is **part of `infra-011`'s worker output**,
not a separate task. The worker performs it as the first step of the implementation, in
the same PR that introduces the sync workflow.

**Migration procedure:**

1. Read every entry in `_data/talks.yml`.
2. For each entry, **default to `source: manual`** unless Joshua has indicated otherwise.
   The existing entries are stylised samples (per the task's commit history and content)
   and may or may not correspond to real INNOQ talks. Defaulting to `manual` is the safe
   choice: it means the first sync run will discover INNOQ's 26 real talks afresh and
   open them as new entries.
3. The worker surfaces the migration in the PR description with a short table mapping
   each existing entry to its assigned `source:`. Joshua flips any that should be
   `source: innoq` with a known `source_url` on PR review, before merge.

After the migration PR merges, the first sync run will:

- See 11 `source: manual` entries (or whatever subset Joshua flipped to `innoq` on
  review). It ignores them.
- Scrape INNOQ's 26 talks, attach `source: innoq` and `source_url` to each, and open a
  second PR adding them. If Joshua flipped some manual entries to `innoq` and they
  composite-match INNOQ scrapes, the worker's fallback matcher (§2) folds them together
  rather than duplicating.

This split — migration PR first, sync PR second — keeps each review small. The worker
must not bundle them.

### 10. Schema extension to `_data/talks.yml`

The website BC's `_data/talks.yml` schema (`website/README.md` → "Data file shapes")
gains two optional fields **without breaking the existing layout**:

- `source: innoq | manual` — required on every entry after the migration.
- `source_url: <URL>` — required when `source: innoq`; absent when `source: manual`.

`_layouts/talks.html` and `_includes/talk-card.html` do not need changes: they render
only the established fields (`what`, `where`, `city`, etc.). The new fields are pure
metadata used by the sync. This is **not a website-BC concern** beyond updating
`website/README.md`'s "Data file shapes" entry to document the additions — which the
infra-011 worker does as part of its PR.

## Consequences

### Positive

- Three INNOQ workflows now share the same `innoq_common.py` HTTP politeness layer; the
  conventions stay canonical.
- Identity by URL means cosmetic edits to titles or event names won't double-add.
- Source marker means hand-curated entries are first-class citizens, not exceptions.
- One-PR-per-sync-run keeps the review surface tight even when multiple field-updates
  land in the same week.
- Weekly cadence keeps GHA-minutes and PR noise low.
- Distinct branch namespace makes the three INNOQ sync flows visually separable.
- Close-prior-then-open-new keeps the open-PR list non-redundant without losing the
  audit trail.
- The split migration-then-sync flow lets Joshua keep his hand-curated stylised entries
  on the first run rather than having them clobbered.

### Negative

- The §3 "INNOQ-authoritative fields are overwritten" rule means a local cosmetic edit
  to a `source: innoq` entry's title silently disappears on the next sync. Mitigated by
  PR-body call-out and by the `source: manual` escape hatch. The friction is the design.
- The §2 fallback matcher (composite-key match for `source_url`-less entries) only runs
  on the first sync. Afterward, an INNOQ slug rename would create a duplicate; Joshua
  cleans up on PR review. Not zero-cost, but rare.
- The schema gains two fields. Documented in `website/README.md`; the impact on rendering
  is zero. The non-cost.
- Weekly cron means a brand-new talk announcement may take up to a week to surface as a
  sync PR. Acceptable given the cadence of conference announcements; if it ever bites,
  Joshua hits `workflow_dispatch`.

## Alternatives Considered (summary)

| Decision axis | Chosen | Rejected |
|---|---|---|
| Discovery | Scrape `/de/talks/?all=true&by=...` + per-talk detail fetch | Feed-poll (no feed exists); global feed filter (rolling window too narrow); sitemap (no per-talk URLs) |
| Identity key | Talk canonical detail URL | Composite `(what, where, date)` (fragile to cosmetic edits); fresh per-run UUID (no cross-run identity) |
| Update semantics | INNOQ-authoritative fields overwrite; `video` and `source: manual` preserved | Field-level three-way merge (complex, error-prone); append-only like articles (defeats the purpose) |
| Hand-edit coexistence | `source: innoq \| manual` marker | Sync-by-key only (no marker; matches by composite key alone — too fragile); separate file for INNOQ entries (splits the rendering surface) |
| PR shape | One PR per sync run, overwriting | One PR per logical change (multiplies reviews, conflicts on the file) |
| Schedule | Weekly Sundays 04:00 UTC | Daily (wasteful for talk cadence); monthly (too lagging) |
| Branch namespace | `sync/innoq-talks/<YYYY-MM-DD>` | `sync/innoq-talks/<slug>` (no single slug per run); reuse `sync/innoq/` (visually inseparable from article syncs) |
| PR-history dedup | Close prior open PR, open new on fresh date-branch | Force-push to existing branch (loses prior-attempt audit trail); allow multiple open PRs (file-level conflicts) |
| Shared module shape | New `innoq_talks.py`; `innoq_common.py` stays generic | Extend `innoq_common.py` with talk specifics (overgrows the shared module) |
| Migration of existing entries | One PR before first sync, default `source: manual`, Joshua flips on review | Default `source: innoq` (might clobber stylised entries); no migration (sync fails to know what to leave alone) |

## Related work

- ADR-0002 — canonical content sync strategy (high-level posture inherited)
- ADR-0006 — INNOQ sync architecture for articles (workflow shape and politeness primitives
  this ADR builds on)
- `infra-011` — implements this ADR for talks
- Research `innoq-talks-page-2026-06-02` — primary scraping reference (selectors,
  pagination, robots.txt, identity-key candidates)
- Research `innoq-staff-page-scrape-2026-05-27` — article-side prior art; politeness
  posture and robots.txt baseline carry over unchanged
- Research `innoq-staff-feed-2026-05-27` — confirmed no per-author feed and no
  `talks.atom`, justifying scrape-only

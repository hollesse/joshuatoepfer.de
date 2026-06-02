---
id: infra-011
title: "INNOQ talks sync workflow (scrape /de/talks/?all=true&by=joshua-toepfer → PR)"
status: done
type: feature
context: infrastructure
created: 2026-06-02
completed: 2026-06-02
commit:
depends_on: []
blocks: []
tags: [sync, innoq, github-actions, pipeline, content, python, talks, scrape]
related_adrs: [0002, 0006, 0007]
related_research: [innoq-staff-feed-2026-05-27, innoq-staff-page-scrape-2026-05-27, innoq-talks-page-2026-06-02]
prior_art: [infra-002, infra-004, infra-005, infra-007]
---

## Why
Joshua maintains his talk history on innoq.com at
`https://www.innoq.com/de/talks/?all=true&by=joshua-toepfer`. The Jekyll
site renders talks from `_data/talks.yml` (see `website/README.md` →
"Data file shapes"). Today that file is hand-edited; every new
conference talk, every status change (`upcoming` → `past`), and every
slides URL added after-the-fact requires a manual edit.

The same low-maintenance principle that drove the INNOQ **article**
sync (ADR-0002, infra-004/005) applies here: a scheduled workflow
should detect new or changed INNOQ talk entries and open a PR with the
updated `_data/talks.yml`. The vision (`vision.md` → "What success
looks like") names this explicitly: *"New content (synced from
innoq.com or added manually) appears with minimal manual effort"* and
the ubiquitous language already includes **Sync workflow** /
**Sync PR**.

## What
A new GitHub Actions workflow (and supporting Python module + script) that:

1. Fetches `https://www.innoq.com/de/talks/?all=true&by=joshua-toepfer`
   on a **weekly** schedule (Sundays 04:00 UTC) and on `workflow_dispatch`.
2. Follows pagination (`nav.paginator a[rel="next"]`) until all listing
   pages have been collected — research confirms 26 talks today across
   2 pages (25 + 1).
3. For each listing entry, fetches the talk's detail page to pick up
   `city` (from `<dl> "Ort"` last comma segment) and `abstract` (from
   the detail-page `<article>` paragraphs before `<dl>`), plus the
   slides URL when present (`a.btn[href*="fl_attachment:"]`).
4. Normalises into the existing `_data/talks.yml` schema — `date`,
   `what`, `where`, `city`, `status`, `type`, `duration`, `abstract`,
   optional `slides`, optional `video` — extended with two new fields
   on every entry: `source: innoq | manual` and (when `source: innoq`)
   `source_url: <full INNOQ talk URL>`. See ADR-0007 §10.
5. Diffs against the on-disk `_data/talks.yml` per ADR-0007 §3 (update
   semantics) and §4 (`source: manual` is left untouched).
6. If the diff is non-empty, opens **one PR** containing the full file
   overwrite, on a date-stamped branch `sync/innoq-talks/<YYYY-MM-DD>`,
   carrying the shared `sync-innoq` label so all three INNOQ workflows'
   PRs filter together.
7. Before opening a new PR, closes any prior **open** PR on a branch
   matching `sync/innoq-talks/*` (with a comment linking to the new
   PR). Merged/closed PRs are ignored. See ADR-0007 §8.
8. Empty diff → no PR, no noise.

The sync workflow's PR is a **draft for Joshua's review** — same posture
as the article syncs (ADR-0002 / ADR-0006): the workflow proposes,
Joshua decides.

## Resolved decisions (ADR-0007)

The seven open questions in the original capture are resolved as follows.
See `.agentheim/knowledge/decisions/0007-innoq-talks-sync-architecture.md`
for the full reasoning, alternatives, and consequences.

1. **Discovery shape** — server-rendered HTML, no JS hydration, no feed
   exists (`/de/talks/feed.atom` 404; `<link rel="alternate">` block on
   the listing advertises no `talks.atom`). Scrape `/de/talks/?all=true&by=joshua-toepfer`
   and follow the paginator. robots.txt permits. Selectors in research
   `innoq-talks-page-2026-06-02` §2 (listing) and §3 (detail).
2. **Field mapping** — verified via research §2 + §3:
   - `date` → `time.event-date[datetime]` on the listing (ISO).
   - `what` → `h2.list-teaser-event__headline` on the listing.
   - `where` → first `/`-delimited segment of `p.list-teaser-event__subheadline`.
   - `duration` → second `/`-delimited segment, parsed as `HH:MM - HH:MM`
     → minutes; omitted if absent. Fallback to detail-page `<dl> "Uhrzeit"`.
   - `type` → `div.type-label.primary` text, mapped
     `{"Vortrag": "talk", "Workshop": "workshop", "Keynote": "keynote"}`;
     unknown → default `talk` with WARN log.
   - `city` → detail-page `<dl> "Ort"` last comma segment.
   - `abstract` → detail-page `<article class="page-layout-md--default">`
     `<p>` children before `<dl class="date-location-section">`, joined
     with `\n\n`.
   - `slides` → detail-page `a.btn[href*="fl_attachment:"]` href when
     listing carries `div.label.green` text `"Folien verfügbar"`; omitted
     otherwise.
   - `video` → **not derivable from INNOQ** (no video markup observed on
     any sampled talk). Treat as Joshua-authoritative — preserve across
     syncs, never write or overwrite from INNOQ.
   - `status` → derived: `upcoming` if `date >= today_utc`, else `past`.
     Never read from INNOQ.
3. **Diff & PR shape** — **one PR per sync run**, full file overwrite,
   diff summarised in the PR body with three buckets (new / status /
   field-update). Per-logical-change PRs were rejected (multiplies
   reviews; conflicts on the single file). ADR-0007 §5.
4. **Update vs. additive semantics** — INNOQ-authoritative fields are
   **re-derived and overwritten** every sync; the only fields safe to
   hand-edit on a `source: innoq` entry are `video` and `source`
   itself. The PR body spells this out. ADR-0007 §3.
5. **Hand-editing & merge conflicts** — `source: innoq | manual` marker
   on every entry. The sync ignores `source: manual` entries entirely
   (read-skip + write-passthrough). ADR-0007 §4.
6. **Schedule** — weekly cron, Sundays 04:00 UTC (`0 4 * * 0`),
   staggered an hour after the article sync's daily 03:00 UTC slot.
   Plus `workflow_dispatch`. ADR-0007 §6.
7. **Dedup / PR-history** — branch namespace
   `sync/innoq-talks/<YYYY-MM-DD>`; before opening a new PR, close any
   open prior PR on `sync/innoq-talks/*` (with a comment pointing at the
   new PR). Merged/closed PRs are ignored. ADR-0007 §7 + §8.

Additional decisions surfaced during refinement:

- **Identity key** — the canonical talk detail URL (e.g.
  `https://www.innoq.com/de/talks/2026/03/four-years-one-ensemble-…/`),
  stored as `source_url` on every `source: innoq` entry. ADR-0007 §2.
- **Shared module shape** — new `innoq_talks.py` for talk parsing +
  YAML diff; `innoq_common.py` stays generic (HTTP fetch, User-Agent,
  politeness, slug, retry). ADR-0007 §1.
- **One-time migration of the existing `_data/talks.yml`** — every
  existing entry gets `source: manual` by default. The migration is
  the **first commit / step** of this task's worker output, in the same
  PR that introduces the sync workflow. Joshua flips entries he
  considers INNOQ-origin on PR review (and the worker pre-populates a
  proposed mapping table in the PR body). ADR-0007 §9.

## Architecture (final)

Sibling to `sync-innoq.yml` and `backfill-innoq.yml`:

```
.github/
├── workflows/
│   ├── sync-innoq.yml         ← infra-004 (article incremental, feed)
│   ├── backfill-innoq.yml     ← infra-005 (article backfill, scrape)
│   └── sync-innoq-talks.yml   ← THIS TASK
└── scripts/
    ├── sync_innoq.py          ← infra-004
    ├── backfill_innoq.py      ← infra-005
    ├── sync_innoq_talks.py    ← THIS TASK (workflow entry point)
    ├── innoq_talks.py         ← THIS TASK (talk parsing + YAML diff)
    └── innoq_common.py        ← reused unchanged for HTTP/politeness
```

`innoq_common.py` is **not** extended with talk-specific helpers. Its
HTTP fetch, identifying User-Agent, 2 s politeness delay, 5xx
exponential backoff, 4xx no-retry, and `Retry-After`-aware 429 handling
are reused as-is from `infra-004`/`infra-005`. All talk-specific
parsing, the source-marker convention, and the YAML diff/merge live in
`innoq_talks.py`.

## Acceptance criteria

Migration (first commit / step):

- [ ] Every entry in `_data/talks.yml` carries a `source:` field after
  this PR lands. Default value `manual`; the PR body proposes which
  entries (if any) Joshua should flip to `innoq` on review.
- [ ] `_layouts/talks.html` and `_includes/talk-card.html` render
  identically before vs. after the migration (visual no-op; the new
  fields are pure sync metadata).
- [ ] `website/README.md` → "Data file shapes" → `_data/talks.yml` is
  updated to document the new optional fields `source` and `source_url`.

Workflow + module:

- [ ] `.github/workflows/sync-innoq-talks.yml` exists. Triggers:
  `schedule: cron: "0 4 * * 0"` and `workflow_dispatch`. Runs on
  `ubuntu-latest`. Carries the `sync-innoq` label on its PRs.
- [ ] `.github/scripts/sync_innoq_talks.py` is the entry point. It
  imports `innoq_common` (HTTP/politeness) and `innoq_talks` (parsing
  + diff). It does not duplicate fetch/retry/User-Agent logic.
- [ ] `.github/scripts/innoq_talks.py` exposes `parse_listing`,
  `parse_detail`, `merge_talks`, `derive_status` per ADR-0007 §1 and
  is independently importable for testing.
- [ ] `innoq_common.py` is not modified for talk-specific concerns
  (the generic HTTP primitives may be touched only to extract a
  helper if needed, never to add a talk selector).

Discovery + parsing:

- [ ] The workflow fetches the listing URL `https://www.innoq.com/de/talks/?all=true&by=joshua-toepfer`
  and follows `nav.paginator a[rel="next"]` until exhausted, collecting
  every `a.list-teaser-event`. With Joshua's current data this yields
  26 entries across 2 pages.
- [ ] For each listing entry, the workflow extracts: detail URL (from
  `a[href]`), date (`time[datetime]`), title
  (`h2.list-teaser-event__headline`), event-name + optional duration
  (split of `p.list-teaser-event__subheadline` on the first `/`), type
  (mapped from `div.type-label.primary`), slides-flag (presence of
  `div.label.green` with text `"Folien verfügbar"`).
- [ ] For each entry, the workflow fetches the detail page with a 2 s
  politeness delay between requests (reuse `innoq_common.fetch_with_retry`),
  and extracts: city (from `<dl> "Ort"` last comma segment), abstract
  (`<article>` paragraphs before `<dl>`), slides URL (`a.btn[href*="fl_attachment:"]`)
  when the listing flag was set, duration fallback (`<dl> "Uhrzeit"`)
  when the listing didn't carry one.
- [ ] An unknown `type-label` value defaults to `talk` and emits a
  WARN log line including the unmapped label and the entry URL.

Diff + merge:

- [ ] `source: manual` entries are read-skipped and write-passed-through
  unchanged. The sync never touches them.
- [ ] `source: innoq` entries are matched across runs by `source_url`
  (exact string equality).
- [ ] On the first sync (when no `source: innoq` entries exist yet),
  the worker's fallback matcher checks composite key
  `(what, where, date)` against any `source: manual` entries Joshua
  manually flipped to `innoq` without a `source_url`. Ambiguous matches
  are surfaced in the PR body for review; the worker does not silently
  merge.
- [ ] INNOQ-authoritative fields (per ADR-0007 §3 table) are
  re-derived and overwritten on every sync. `video` and the `source`
  field itself are preserved.
- [ ] `status` is computed from `date` vs. `today_utc` on every run;
  never read from INNOQ.

PR shape + scheduling:

- [ ] When the merge produces a YAML different from the on-disk file,
  the workflow opens one draft PR with the full overwrite, on branch
  `sync/innoq-talks/<YYYY-MM-DD>`, labelled `sync-innoq`.
- [ ] The PR body summarises the diff in three buckets — **New talks**,
  **Status transitions**, **Field updates** — and reminds the reviewer
  that INNOQ-authoritative field edits will be overwritten on the next
  sync (per ADR-0007 §3).
- [ ] Before opening the new PR, the workflow closes any open PR on a
  branch matching `sync/innoq-talks/*` with a comment linking to the
  newly-opened PR.
- [ ] Empty diff → no branch created, no PR opened, exit 0.

Politeness, observability, docs:

- [ ] All INNOQ requests use `innoq_common.fetch_with_retry`'s posture:
  2 s delay between requests, identifying User-Agent, exponential
  backoff (5 s → 30 s → 2 min, 3 attempts) on 5xx, `Retry-After`-aware
  on 429, no retry on 4xx.
- [ ] The workflow runs to completion against today's 26 talks
  (smoke-tested via `workflow_dispatch`) in well under GHA's default
  timeout — back-of-envelope ~3 min at 2 s × ~30 requests.
- [ ] `.agentheim/contexts/infrastructure/README.md` gains a "Talks
  sync workflow (innoq.com → PR)" section, mirroring the existing
  "Sync workflow" and "Backfill workflow" entries. It documents the
  weekly cadence, the URL identity, the source marker, and the
  update-semantics call-out.
- [ ] `website/README.md` → "Data file shapes" → `_data/talks.yml`
  documents the new `source` and `source_url` fields.

## Notes

- The target URL is the same pattern as the backfill discovery URL
  used by `infra-005` (`/de/written/?by=joshua-toepfer`) — both are
  per-author archive pages on innoq.com, both server-rendered. The
  scrape primitives from `innoq_common.py` (politeness, retry,
  identifying User-Agent) carry over unchanged.
- This task does not require a styleguide gate (no UI changes — the
  `/talks/` page already exists, its layout is owned by the website BC,
  and the new `source` / `source_url` fields are pure metadata that
  the layout doesn't render).
- The migration is part of `infra-011`'s worker output, **not a
  separate task** (ADR-0007 §9). Worker keeps it as a distinct commit
  inside the same PR so the diff is reviewable in two clean steps.
- This task is **ready to promote to `todo/`** — all open questions
  are resolved by ADR-0007, the schema extension is documented, the
  acceptance criteria are testable, and no upstream dependency is
  pending.

## Outcome

Shipped the INNOQ talks-sync pipeline per ADR-0007 in two reviewable
steps inside one PR.

**Step 1 — Migration (`_data/talks.yml`):** every one of the 10
existing hand-curated entries gained `source: manual` (the safe
default per ADR-0007 §9). Schema-only change — the layout
(`_layouts/talks.html`) and card include (`_includes/talk-card.html`)
were verified to ignore the new field. File header comment was
expanded to document the `source` / `source_url` fields inline.

**Step 2 — Sync workflow + module + tests:**

- `.github/workflows/sync-innoq-talks.yml` — weekly cron `0 4 * * 0` +
  `workflow_dispatch` with `dry_run` input; single-job shape (one PR
  per run, no plan/matrix); draft PR via `peter-evans/create-pull-request@v6`
  with the `sync-innoq` label.
- `.github/scripts/sync_innoq_talks.py` — workflow entry point.
  `scrape_all()` walks the paginator (`nav.paginator a[rel="next"]`),
  fetches every detail page, and feeds the merge engine.
  `branch_for_today()` produces `sync/innoq-talks/<YYYY-MM-DD>`.
  `close_prior_open_prs()` implements ADR-0007 §8's
  close-prior-then-open-new dedup via `gh pr list/close`. Empty-discovery
  raises a `RuntimeError` so a template-drift run fails loudly instead
  of silently wiping `source: innoq` entries.
- `.github/scripts/innoq_talks.py` — `parse_listing`, `parse_detail`,
  `derive_status`, `merge_talks`, `parse_duration`, `serialise_talks`,
  `build_pr_body` (plus dataclasses `ListingEntry`, `DetailFields`,
  `ScrapedTalk`). Selectors match research `innoq-talks-page-2026-06-02`
  §2 + §3; unknown `type-label` defaults to `talk` with a WARN log line.
- `.github/scripts/innoq_common.py` — extracted the inline `_fetch_html`
  out of `backfill_innoq.py` into the shared `fetch_with_retry`
  primitive (2 s delay, identifying User-Agent, 5 s→30 s→2 min
  backoff on 5xx, 4xx fail-loud, 429 Retry-After). Talks-sync and
  article-backfill now share the same politeness layer.
- `.github/scripts/backfill_innoq.py` — `_fetch_html` is now a thin
  shim that delegates to `fetch_with_retry`. The local `USER_AGENT`
  is re-exported from the canonical `INNOQ_USER_AGENT` for
  backwards-compat with any consumer that still imports the name.
- `.github/scripts/test_innoq_talks.py` — 57 new tests covering
  listing parsing (12), detail parsing (8), `derive_status` (4),
  duration parsing (3), merge engine (5 first-sync, 6 in-place update,
  1 manual-not-touched, 1 empty-diff, 1 composite fallback), YAML
  round-trip (2), PR body (4), live `_data/talks.yml` integration (2),
  entry-point glue (4), and the empty-discovery guard (1).
- `.github/scripts/test_innoq_common.py` — 8 new tests covering the
  extracted `fetch_with_retry` (User-Agent + delay + 4xx fail-loud +
  5xx backoff schedule + 429 Retry-After).

**Test totals:** 89 → 154 tests, all green.

**Docs updates:**

- `.agentheim/contexts/infrastructure/README.md` — new "Talks sync
  workflow (innoq.com → PR)" section between the article-backfill
  section and accessibility-checks section. Mirrors the existing
  shape; documents schedule, identity-key, source marker semantics,
  type-label mapping, PR shape, close-prior-then-open-new dedup, the
  shared `fetch_with_retry` primitive, and the empty-discovery guard.
- `.agentheim/contexts/website/README.md` — "Data file shapes"
  section's `_data/talks.yml` bullet extended to document `source` +
  `source_url` and the read-skip / write-passthrough rule for
  `source: manual` (the cross-BC docs touch explicitly authorised by
  ADR-0007 §10).

**Key files:**

- `/Users/joshuatopfer/Documents/Projekte/Privat/joshuatoepfer.de/.github/workflows/sync-innoq-talks.yml`
- `/Users/joshuatopfer/Documents/Projekte/Privat/joshuatoepfer.de/.github/scripts/sync_innoq_talks.py`
- `/Users/joshuatopfer/Documents/Projekte/Privat/joshuatoepfer.de/.github/scripts/innoq_talks.py`
- `/Users/joshuatopfer/Documents/Projekte/Privat/joshuatoepfer.de/.github/scripts/innoq_common.py` (extended)
- `/Users/joshuatopfer/Documents/Projekte/Privat/joshuatoepfer.de/.github/scripts/backfill_innoq.py` (refactored to use shared fetch)
- `/Users/joshuatopfer/Documents/Projekte/Privat/joshuatoepfer.de/.github/scripts/test_innoq_talks.py`
- `/Users/joshuatopfer/Documents/Projekte/Privat/joshuatoepfer.de/.github/scripts/test_innoq_common.py` (extended)
- `/Users/joshuatopfer/Documents/Projekte/Privat/joshuatoepfer.de/_data/talks.yml` (migrated, every entry now carries `source: manual`)
- `/Users/joshuatopfer/Documents/Projekte/Privat/joshuatoepfer.de/.agentheim/contexts/infrastructure/README.md` (new talks-sync section)
- `/Users/joshuatopfer/Documents/Projekte/Privat/joshuatoepfer.de/.agentheim/contexts/website/README.md` (data-shape entry extended)

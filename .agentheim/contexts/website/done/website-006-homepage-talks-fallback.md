---
id: website-006
title: "Homepage talks fallback — recent past talks when none upcoming"
status: done
type: feature
context: website
created: 2026-06-02
completed: 2026-06-02
commit: 4816dfe
depends_on: []
blocks: []
tags: [home, talks, layout, liquid, fallback]
related_adrs: []
related_research: []
prior_art: [website-001]
---

## Why
After `infra-011` shipped the INNOQ talks sync and the migration PR
(`d1e81fa`) drained the placeholder samples out of `_data/talks.yml`,
the first real sync (`d707953`) populated the file with 26 INNOQ
talks — all `status: past` (latest 2026-03-13; today 2026-06-02).

The homepage hides its talks section entirely when
`site.data.talks | where: "status", "upcoming"` is empty
(`_layouts/home.html` line 57 guarded `{% if upcoming_talks.size > 0 %}`).
So even though the site has 26 real talks, the homepage shows none —
a regression in perceived activity. Joshua noticed and asked for a
fallback.

## What
When the homepage's `upcoming_talks` set is empty, render the **3
most recent past talks** instead (sorted descending by date), under a
distinct heading. The section disappears only when both sets are
empty.

Heading rule:
- `upcoming_talks.size > 0` → **"KOMMENDE TALKS"** (existing label).
  More-link: "Speaker-Profil →".
- else if `recent_past_talks.size > 0` → **"ZULETZT AUF DER BÜHNE"**
  (callback to the `/talks/` hero copy "Auf der Bühne"). More-link:
  "Alle Talks →".
- else → section hidden entirely (no change from prior behavior).

The `talk-card.html` `home` variant is already status-agnostic (date
+ where + title only), so it renders past talks correctly without
include changes.

## Acceptance criteria
- [x] `_layouts/home.html` defines `recent_past_talks` as
  `site.data.talks | where: "status", "past" | sort: "date" | reverse
  | slice: 0, 3`.
- [x] The talks section uses an `if / elsif` branch: upcoming →
  "KOMMENDE TALKS"; recent past → "ZULETZT AUF DER BÜHNE"; neither →
  hidden.
- [x] The more-link's URL stays `/talks/` in both cases; only its
  label changes ("Speaker-Profil →" vs. "Alle Talks →") to match
  the section voice.
- [x] `_includes/talk-card.html` not modified — the `home` variant is
  reused as-is.
- [x] `bundle exec jekyll build` clean.
- [x] Visual sanity check: with today's data (no upcoming), the
  rendered `_site/index.html` shows three past-talk cards (13. März,
  11. März, 10. März 2026) under "ZULETZT AUF DER BÜHNE".
- [x] `website/README.md` `/` pages-inventory entry documents the
  fallback (data-sources bullet + heading rule).

## Notes
- Captured retroactively after the work was done inline (commit
  `4816dfe` on 2026-06-02). Joshua asked for a fallback in
  conversation; in Auto Mode I made the change directly because the
  scope was small (~10 lines of Liquid + README sentence) and the
  styleguide gate was already satisfied (`design-system-001-styleguide`
  is done).
- `N = 3` chosen to mirror the focus-card grid above it; the latest-
  posts section uses N=5, which would have been too tall for a
  past-talks fallback that's secondary signal rather than primary
  content.
- The fallback heading "ZULETZT AUF DER BÜHNE" was picked over
  "VERGANGENE TALKS" / "LETZTE AUFTRITTE" for tone — it echoes the
  `/talks/` page's hero copy and reads less archival.
- No tests added — Jekyll layout changes are visually verified
  rather than unit-tested in this project.
- Discipline note for future tasks: this is the first time a website-
  BC feature shipped without going through `/agentheim:model` +
  `/agentheim:work`. Backfilling the task entry here preserves the
  audit trail; not a precedent to repeat for non-trivial changes.

## Outcome
Shipped via commit `4816dfe` ("feature(website): homepage fallback —
recent past talks when none upcoming"). Two files changed:

- `_layouts/home.html` — added `past_talks_desc` + `recent_past_talks`
  assigns; converted the talks-section guard from `if` to
  `if / elsif / endif` with the new heading + more-link variant.
- `.agentheim/contexts/website/README.md` — `/` data-sources bullet
  documents the fallback.

Verified: `bundle exec jekyll build` passes; `_site/index.html`
renders the three most-recent past talks in the fallback section
("ADHS in der IT — DevLand 2026" / "JavaLand 2026" / "Four Years,
One Ensemble").

Key files:
- `/Users/joshuatopfer/Documents/Projekte/Privat/joshuatoepfer.de/_layouts/home.html`
- `/Users/joshuatopfer/Documents/Projekte/Privat/joshuatoepfer.de/.agentheim/contexts/website/README.md`

---
slug: innoq-talks-page-2026-06-02
title: "INNOQ talks page HTML structure and scrape feasibility (talks sync workflow)"
scope: infrastructure
date: 2026-06-02
related_tasks: [infra-011]
---

# INNOQ talks page HTML structure and scrape feasibility (talks sync workflow)

## Executive summary

- **Talks sync is feasible via scrape.** `https://www.innoq.com/de/talks/?all=true&by=joshua-toepfer`
  is plain server-rendered HTML (no JS hydration required). Every talk entry is present in the
  initial response body. No Cloudflare challenge or bot-detection observed across the fetches
  made for this report. The same `requests` + `BeautifulSoup` posture used by
  `backfill_innoq.py` carries over directly. Confidence: **high**.
- **No per-author or per-content-type Atom feed for talks exists.** Probed
  `/de/talks/feed.atom` (404) and `/de/talks.atom` (301). The page's
  `<link rel="alternate">` block advertises only the global site feed, the global written feed
  (`written.atom`), and three INNOQ podcast feeds — no `talks.atom`. Confidence: **high**.
- **Recommended discovery URL: `https://www.innoq.com/de/talks/?all=true&by=joshua-toepfer`.**
  The site internally rewrites this to `/de/upcoming_talks/?all=true&by=...` (see canonical
  link). `?all=true` returns *both past and upcoming* talks for the author (verified: 26
  entries spanning 2023-11 → 2026-03 across two pages). The path-segment `/talks/` is the URL
  shape the user is comfortable with; either URL renders identically. Confidence: **high**.
- **Pagination exists and matters.** Page 1 holds 25 entries; remaining entries spill onto
  `?page=2`, `?page=3`, etc. Joshua currently has 26 entries → exactly one entry on page 2.
  The scraper **must follow the `<nav class="paginator">` `<a rel="next">` link** until
  exhausted. Confidence: **high**.
- **Listing markup is unusually clean.** Each talk is one
  `<a class="list-teaser-event" href="/de/talks/YYYY/MM/<slug>/">…</a>` carrying:
  `<time datetime="YYYY-MM-DD">` (machine-readable ISO date), a `type-label` div with the
  German content type ("Vortrag" → `talk`), an `<h2 class="list-teaser-event__headline">` for
  the title, a `<p class="list-teaser-event__subheadline">` carrying the event name and (when
  present) a duration window like `"… / 10:30 - 11:10"`, and an optional
  `<div class="label green">Folien verfügbar</div>` flag. Confidence: **high**.
- **City + abstract live only on the detail page, not the listing.** The listing's
  subheadline is `"<event-name> / HH:MM - HH:MM"` — no city, no abstract. Both fields appear
  on each talk's detail page under `/de/talks/YYYY/MM/<slug>/`, in a
  `<dl class="date-location-section">` block (`Ort` = city/venue) and an `<article
  class="page-layout-md--default">` `<h1>`-then-`<p>` block (abstract paragraphs). **A
  per-talk detail fetch is therefore required** to populate the `city` and `abstract` fields
  of `_data/talks.yml`. Confidence: **high**.
- **Slides are linked from the detail page; videos were not observed on any sampled talk.**
  When a talk has slides, the detail page renders a
  `<a class="btn" href="https://res.cloudinary.com/innoq/image/upload/fl_attachment:…">Folien
  downloaden</a>` button — a Cloudinary direct-download URL. None of the three detail pages
  sampled (one upcoming with slides, one past with slides, one past without) carried a video
  link, Speakerdeck embed, or `<iframe>` for video. The listing's `<div class="label
  green">Folien verfügbar</div>` is a faithful flag for the slides case. **Video field is
  effectively never INNOQ-authoritative; treat as manual-only in the sync.** Confidence:
  **medium** (3 samples — see "Remaining unknowns" for a wider check). Strong corroborating
  signal: INNOQ's social-footer YouTube link is generic-channel-only, not per-talk.
- **Stable identity key: the talk's canonical URL path (e.g. `/de/talks/2026/03/four-years-one-ensemble-…/`).**
  Every listing entry's `<a href>` points to this path, and every detail page's `<meta
  property="og:url">` repeats it. The URL embeds `YYYY/MM` and a kebab-case slug. INNOQ does
  not appear to renumber or move talks after publication; the URL is the cleanest
  cross-run identifier. Confidence: **high**.
- **`robots.txt` is permissive for the URLs needed.** Re-checked verbatim 2026-06-02:
  identical to the snapshot in `innoq-staff-page-scrape-2026-05-27`. The disallow patterns
  target legacy `*.html` article URLs and `/search/`, `/recommendations/`, `/404`, `/500`
  only. `/de/talks/`, `/de/upcoming_talks/`, and per-talk detail pages are not restricted.
  No `Crawl-delay`. The politeness posture from `innoq_common.py` (2 s delay, identifying
  User-Agent, exp. backoff on 5xx, no retry on 4xx) applies unchanged. Confidence: **high**.

## Question 1 — Render mode

**URL fetched:** `https://www.innoq.com/de/talks/?all=true&by=joshua-toepfer` (with curl,
identifying User-Agent, 2026-06-02).

- **Render mode:** Server-rendered HTML. `Content-Length: ~81 KB`. All 25 talk entries
  on page 1 are present in the raw response body — no JS execution needed.
- **Canonical:** `<link rel="canonical" href="https://www.innoq.com/de/upcoming_talks/?all=true&by=joshua-toepfer">`.
  The site treats `/de/talks/` and `/de/upcoming_talks/` as aliases for the same listing
  template; the canonical points at `upcoming_talks`. Either path works as the scrape target.
- **Turbo Frame wrapper:** The listing is wrapped in `<turbo-frame id="upcoming_talks"
  target="_top">`. This is a [Hotwire Turbo](https://turbo.hotwired.dev/) custom element;
  it has no functional effect on the initial page render — the content inside it is regular
  HTML and is delivered server-side. The custom element only matters if the client wants to
  do in-page navigation; a server-side scraper can ignore it. Worth knowing because page 2,
  fetched naïvely, returns *only the turbo-frame body* (3 KB, no `<head>` or `<html>`
  wrapper) — fine for BeautifulSoup, but unusual at first sight.
- **No Cloudflare challenge** observed. No `Retry-After`, no 429, no captcha interstitial.

## Question 2 — Listing markup (per-talk entry)

Verified shape — one entry, lightly trimmed (page 1, lines ~248–284):

```html
<a class="list-teaser-event"
   href="/de/talks/2026/03/four-years-one-ensemble-challenges-aha-moments-and-true-team-transformation/">
    <div class="event-date-section">
        <div class="type-label primary">Vortrag</div>
        <time datetime="2026-03-10" class="event-date">…</time>
    </div>
    <div class="list-teaser__content">
        <div class="list-teaser__labels">
            <div class="type-label primary">Vortrag</div>
            <div class="label green">Folien verfügbar</div>
        </div>
        <div class="list-teaser__body">
            <h2 class="list-teaser-event__headline">Four Years, One Ensemble – …</h2>
            <p class="list-teaser-event__subheadline">
                Agile Meets Architecture / 10:30 - 11:10
                <span class="icon icon-arrow-long-right …"></span>
            </p>
        </div>
        <div class="list-teaser__footer">
            <div class="author-bio author-bio--short" itemtype="http://schema.org/Person">…</div>
        </div>
    </div>
</a>
```

Per-field selectors (relative to one `a.list-teaser-event`):

| `_data/talks.yml` field | Source on listing | Selector |
|---|---|---|
| `date` (ISO) | `time[datetime]` | `time.event-date[datetime]` — value is `YYYY-MM-DD` |
| `what` (title) | headline | `h2.list-teaser-event__headline` (text, strip) |
| `where` (event) | subheadline | `p.list-teaser-event__subheadline` — text before `/`, strip |
| `duration` (min) | subheadline | `p.list-teaser-event__subheadline` — text after `/`, parse `HH:MM - HH:MM` → minutes; **absent on some entries** (no `/` in subheadline) — omit field then |
| `type` | type-label | `div.type-label.primary` — text in `{"Vortrag": "talk", "Workshop": "workshop", "Keynote": "keynote"}`; default `talk` if unknown |
| `status` | derived | `upcoming` if `date >= today`, else `past` |
| `city` | **not on listing** | fetch detail page |
| `abstract` | **not on listing** | fetch detail page |
| `slides` (URL) | flag only on listing | `div.label.green` text == `"Folien verfügbar"` → **fetch detail page** to extract the actual URL |
| `video` (URL) | **not observed** | not derivable from INNOQ (see below) |
| identity (canonical URL) | parent `<a href>` | absolute URL = `https://www.innoq.com` + `a.list-teaser-event[href]` |

Notes on per-field robustness:

- **`type` mapping:** Joshua's current 26 talks are all `Vortrag` (`talk`). The mapping
  table needs `Workshop` → `workshop` and `Keynote` → `keynote` defensively, but no
  workshops or keynotes were observed in his listing today. If INNOQ introduces a fourth
  label (e.g. `Podiumsdiskussion`, `Tutorial`), the parser should default to `talk` and
  emit a WARNING-level log line. Confidence: **medium** on the mapping table being
  complete — derived from German UI conventions, not from an INNOQ schema doc.
- **Subheadline structure variants observed:**
  - With duration: `"Java Forum Nord"` (no slash, no time) → `where = "Java Forum Nord"`,
    `duration` omitted
  - With duration: `"Agile Meets Architecture / 10:30 - 11:10"` → `where = "Agile Meets
    Architecture"`, `duration = 40`
  - With duration and venue suffix mixed: not observed in Joshua's set, but treat the
    first `/` as the event/duration delimiter and second `/`-substrings as part of the
    duration block.
- **Date format:** `<time datetime="YYYY-MM-DD">` is **always** present and machine-readable.
  The visible German "13 Mär 2026" text is decorative — ignore it.
- **No microdata for the event itself on the listing.** The `itemscope/itemtype` markup
  surfaces only the speaker (`schema.org/Person`), not the talk. Don't try to extract via
  microdata.

## Question 3 — Detail page markup

**Detail URL shape:** `https://www.innoq.com/de/talks/YYYY/MM/<slug>/` — exactly the `href`
from the listing's `<a class="list-teaser-event">`. Two samples were fetched and inspected:

- `/de/talks/2026/03/four-years-one-ensemble-challenges-aha-moments-and-true-team-transformation/`
  (upcoming, slides present)
- `/de/talks/2025/06/vortrag-adhs-in-der-it-2025/` (past, no slides)
- `/de/talks/2023/11/remote-mob-programming-zuhause-aber-nicht-allein/` (past, slides
  present, slides slider rendered inline)

Detail-page structure (cross-confirmed across all three samples):

```html
<main id="main" role="main" class="talk-page" itemtype="http://schema.org/Event">
    <div class="event-date-section">
        <div class="type-label primary">Vortrag</div>
        <time datetime="2026-03-10" class="event-date">…</time>
    </div>
    <article class="page-layout-md--default">
        <h1 class="talk-title">Four Years, One Ensemble – …</h1>
        <p>Ensemble Programming is more than just a way of working …</p>
        <p>I'll highlight the obvious benefits …</p>
        <p>This talk is for anyone curious about Ensemble Programming …</p>
        <dl class="date-location-section">
            <dt>Datum</dt>          <dd>10.03.2026</dd>
            <dt>Uhrzeit</dt>        <dd>10:30 - 11:10</dd>
            <dt>Konferenz / Veranstaltung</dt>
                                    <dd><a href="https://…">Agile Meets Architecture</a></dd>
            <dt>Ort</dt>            <dd>Maschinenhaus, Berlin </dd>
        </dl>
        <a class="btn"
           href="https://res.cloudinary.com/innoq/image/upload/fl_attachment:…/v1/uploads-production/…">
            Folien downloaden
        </a>
    </article>
    <section class="stripe stripe--gray"><div class="tag-section">…</div></section>
    <aside …>Speaker bio…</aside>
</main>
```

Per-field detail-page selectors:

| Field | Selector | Notes |
|---|---|---|
| `abstract` | `article.page-layout-md--default` — children `<p>` elements *before* `<dl class="date-location-section">` | Joins paragraphs with `\n\n`. Strips trailing whitespace. The `<h1>` is the title (already known from the listing); skip it. |
| `city` | `dl.date-location-section dt:contains("Ort") + dd` (text) | Format observed: `"Maschinenhaus, Berlin"` (venue + city) or `"Klubhaus St. Pauli, Hamburg"`. **Need to split on `, ` and take the last segment** to match the existing `_data/talks.yml` convention where `city` is just the city name (e.g. `"Karlsruhe"`, `"Köln"`). Confidence: **medium** — works for the samples, but multi-comma venues ("KOMED, Forum 1, Köln") would need a tail-segment heuristic. Worker should log the raw `Ort` value when the split is ambiguous. |
| `duration` | If unknown from listing: `dl.date-location-section dt:contains("Uhrzeit") + dd` (text), parse `HH:MM - HH:MM` → minutes | Same parser as the listing path. |
| `slides` URL | `article.page-layout-md--default a.btn[href*="fl_attachment:"]` | The Cloudinary URL with `fl_attachment:` is a forced-download link. Joshua may prefer the non-attachment URL (`fl_attachment:…/` → `…/`) — out of scope for this report, flag for ADR. |
| `video` URL | **not present in any sampled detail page** | See "Remaining unknowns". |

Observed event metadata that we **don't** map to `_data/talks.yml` and can ignore:

- The `Konferenz / Veranstaltung` link (`<dd><a href="https://agile-meets-architecture.com">`)
  — the external conference homepage. Useful as a sanity check but not in the talks schema.
- Tags (`<ul class="tag-list">`) — INNOQ's topic taxonomy, not aligned with the site's
  `topic | tag` model. Skip.
- Speaker bio aside — always Joshua; ignore.

## Question 4 — Identity key

**Recommendation: use the canonical talk detail URL as the identity key.**

Rationale:

1. Every listing entry exposes the path verbatim via `a.list-teaser-event[href]`.
2. Every detail page's `<meta property="og:url">` repeats the path (cross-checked on the
   2026-03-10 sample).
3. The URL embeds `YYYY/MM/<slug>`; INNOQ does not appear to renumber or move talks after
   publication. (No 301-redirect cases were observed in the sampled set; URL stability is
   inferred from URL design, not directly verified.)
4. The URL is a single string — easy to add as `source_url` to each
   `_data/talks.yml` entry, easy to compare across runs.

**Fallback if the URL approach surfaces problems** (e.g. INNOQ ever does renumber): the
composite key `(date, what, where)` is the website BC's declared identity (per
`website/README.md` "Aggregates" section) and would work for matching, but it is fragile
against cosmetic edits to `what` or `where` (typo fixes, conference rename). URL-based
identity is strictly better for sync; composite-key matching is the fallback for entries
that exist in `_data/talks.yml` *without* a `source_url` (e.g. the hand-curated entries
present today).

## Question 5 — Feed availability

| URL probed | Result |
|---|---|
| `https://www.innoq.com/de/talks/feed.atom` | 404 |
| `https://www.innoq.com/de/talks.atom` | 301 (chain not followed — likely to the HTML talks page) |
| `<link rel="alternate">` survey of `/de/talks/?all=true&by=joshua-toepfer` | Only `de/feed.atom`, `de/feed.json`, `de/written.atom`, `de/written.json`, and three INNOQ podcast feeds; **no `talks.atom`**. |

The global `/de/feed.atom` was already characterised by
`innoq-staff-feed-2026-05-27`: ~25 most-recent entries across all INNOQ content types and
all authors. It does include `/de/talks/...` URLs in its rolling window when fresh — but
the window is too narrow to be useful for a per-author talks sync (Joshua's most recent
talks already roll off within months, his older talks are years gone).

**Conclusion: scrape-only. There is no feed path for talks.** This is consistent with
`infra-005`'s posture for older articles, not with `infra-004`'s feed-poll posture.

## Question 6 — Pagination

The talks listing paginates at **25 entries per page**. Page 1's footer renders
`<nav class="paginator">` with `<a rel="next" href="…&page=2">`. Page 2 renders the
inverse (`<a rel="prev" href="…">`).

Joshua's current listing: 26 entries → 25 on page 1, 1 on page 2.

The scraper **must follow `nav.paginator a[rel="next"]`** until it is absent. Implementation
sketch:

```python
url = "https://www.innoq.com/de/talks/?all=true&by=joshua-toepfer"
all_entries = []
while url:
    soup = fetch(url)  # innoq_common.fetch_with_retry
    all_entries.extend(soup.select("a.list-teaser-event"))
    next_link = soup.select_one("nav.paginator a[rel='next']")
    url = urljoin("https://www.innoq.com", next_link["href"]) if next_link else None
```

Page 2 (and onward) returned the bare `<main>` body without `<html>/<head>` wrappers when
fetched with curl. BeautifulSoup parses both shapes identically; no special-casing needed.

## Question 7 — robots.txt and rate-limiting

Re-fetched verbatim 2026-06-02 (identical to the snapshot in
`innoq-staff-page-scrape-2026-05-27`):

```
User-Agent: *
Disallow: /de/articles/*/*/*/*.html
Disallow: /ch/articles/*/*/*/*.html
Disallow: /en/articles/*/*/*/*.html
Disallow: /de/recommendations
Disallow: /ch/recommendations
Disallow: /en/recommendations
Disallow: /de/search
Disallow: /ch/search
Disallow: /en/search
Disallow: /500
Disallow: /404

Sitemap: http://www.innoq.com/sitemap.xml
```

`/de/talks/`, `/de/upcoming_talks/`, and per-talk detail pages are **not** mentioned in
any `Disallow:` pattern → permitted. No `Crawl-delay`. No per-user-agent rule. Politeness
posture from `innoq_common.py` (2 s delay, exp. backoff, identifying User-Agent) applies
unchanged.

**Expected request volume per sync run:** ~26 detail-page fetches today; will grow ~linearly
with Joshua's talk count. Even at 100 talks the run is well under a hundred requests
spread over ~3+ minutes at 2 s/request — comfortably within polite scraping bounds. The
weekly cadence the ADR proposes (vs. articles' daily) further softens the footprint.

## Question 8 — Recommended parser plan

**Library: reuse `innoq_common.fetch_with_retry` + `BeautifulSoup` (lxml backend).** The
existing module already encapsulates the politeness primitives this sync needs.

**Discovery + extraction flow:**

1. Loop over the listing URL and any `?page=N` follow-ups, accumulating
   `a.list-teaser-event` elements.
2. For each entry, extract: detail-URL, date (ISO), title, event-name, optional duration,
   type-label, slides-flag.
3. For each entry, fetch its detail URL (with the 2 s politeness delay). Extract:
   abstract (`<article>` paragraphs before `<dl>`), city (`<dl> "Ort"` last comma segment),
   slides URL (if the listing flag was set).
4. Normalise into the `_data/talks.yml` schema. Derive `status` from `date` vs. today.
5. Diff against the existing `_data/talks.yml` (matched by `source_url` for `source: innoq`
   entries; new INNOQ entries land as fresh `source: innoq` items; `source: manual`
   entries are passed through untouched).
6. If the diff is non-empty, write the updated YAML and let the GHA workflow open the PR.

**Suggested home for the new code:** new module `innoq_talks.py` (talk-page parsing,
detail extraction, YAML diff), reusing `innoq_common.fetch_with_retry`, the User-Agent
constant, and the slug helpers. Adding talk-specific helpers to `innoq_common.py` would
overgrow that file with concerns (talk schema, YAML diff, status derivation) that are not
shared with the article workflows. The ADR will record this.

## Remaining unknowns / suggested next checks

These are points where confidence is medium rather than high; flag them as worker-time
sanity checks rather than blockers:

1. **Workshop / keynote label spellings.** All 26 of Joshua's talks today are `Vortrag`.
   The `{Workshop → workshop, Keynote → keynote}` mapping is inferred. **Resolution:**
   when the worker hits an unmapped `type-label` text, log WARN and default to `talk`.
2. **Multi-day workshops on the listing.** Not observed in Joshua's data. The
   `time[datetime]` attribute carries only a single ISO date; INNOQ may or may not
   indicate end-date separately. The existing site schema's `date` field is single-day,
   so this is academic for now.
3. **Cloudinary slides URL shape.** The `fl_attachment:` segment forces a download. Joshua
   may prefer the in-browser view (without `fl_attachment:`). This is a stylistic choice
   for the ADR/worker — not a research question.
4. **Video sources.** Three detail pages sampled; none had a video link. INNOQ's talk
   pages may use a different markup pattern (`<iframe>`, `<a href="https://youtube…">`,
   or a sibling section) for talks where a recording exists. **Resolution:** ask Joshua
   to point at one of his older talks that *does* have a recording on INNOQ, or default
   to *not auto-syncing video URLs at all* and let Joshua hand-add them on the YAML
   entry (treating `video` as a Joshua-authoritative field in the ADR's update-semantics
   table).
5. **`og:url` / `<meta property="article:published_time">` on detail pages.** Verified
   `og:url` exists on the 2026-03-10 sample. Did not exhaustively check
   `article:published_time` — likely present (INNOQ ships rich OG metadata on articles per
   `innoq-staff-page-scrape-2026-05-27`), but the `<time datetime>` block already gives
   us the date in machine form, so this is redundant.
6. **Stability of detail-URL slugs over time.** No evidence INNOQ renames talks
   post-publication, but not directly verified longitudinally. If a rename ever happens,
   the identity-key match will miss and a duplicate `source: innoq` entry will be
   created; Joshua can clean up by merging on PR review. Not a blocking risk for v1.

## Sources

1. [Joshua's talks listing (DE, ?all=true, page 1)](https://www.innoq.com/de/talks/?all=true&by=joshua-toepfer)
   — primary HTML structure, 25 entries, fetched 2026-06-02. Local copy: `/tmp/innoq-talks.html`
   (during research).
2. Page 2 of the same listing — `?page=2`, 1 entry, fetched 2026-06-02. Local copy:
   `/tmp/innoq-talks-p2.html`.
3. [Talk detail: Four Years, One Ensemble (2026-03-10)](https://www.innoq.com/de/talks/2026/03/four-years-one-ensemble-challenges-aha-moments-and-true-team-transformation/)
   — upcoming, slides present. Detail-page structure sample.
4. [Talk detail: ADHS in der IT (2025-06-04)](https://www.innoq.com/de/talks/2025/06/vortrag-adhs-in-der-it-2025/)
   — past, no slides. Confirms `<dl>` structure stable on no-slides case.
5. [Talk detail: Remote Mob Programming (2023-11-15)](https://www.innoq.com/de/talks/2023/11/remote-mob-programming-zuhause-aber-nicht-allein/)
   — past, slides present (inline slider rendered). Cross-checks the `<a class="btn"
   …fl_attachment:…>Folien downloaden</a>` pattern on an older talk.
6. [robots.txt](https://www.innoq.com/robots.txt) — re-fetched 2026-06-02; identical to
   prior snapshot.
7. Probe results: `/de/talks/feed.atom` → 404, `/de/talks.atom` → 301. No per-content-type
   feed for talks.
8. Prior local research: `.agentheim/knowledge/research/innoq-staff-feed-2026-05-27.md`
   (no per-author feed, no `<category>` element on the global feed),
   `.agentheim/knowledge/research/innoq-staff-page-scrape-2026-05-27.md` (scrape posture,
   politeness, robots.txt baseline).

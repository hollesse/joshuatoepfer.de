---
topic: INNOQ staff page structure and per-author feed availability for Joshua Töpfer
date: 2026-05-27
requested_by: user
related_tasks: [infra-004]
---

# Research: INNOQ Staff Pages and Per-Author Feeds

## Question

For the INNOQ author sync pipeline (`infra-004`, ADR-0002), we need to know:

1. How are INNOQ staff pages structured (URL pattern, sections, content types)?
2. Does INNOQ expose a per-author RSS/Atom/JSON feed? If yes, where, and what fields does it carry?
3. If no per-author feed exists, what are the alternatives — global feed filtering, JSON-LD/microdata on the staff page, sitemap, or HTML scraping?

The goal is to decide between (a) consuming a clean per-author feed, (b) scraping the staff page, or (c) a hybrid.

## Summary

- **No per-author feed exists.** Every probed URL pattern (`/staff/joshua-toepfer/feed.atom`, `.atom`, `/feed`, `.xml`, `/author/...`) returned 404 or 406. Joshua's staff page itself exposes only the site-wide feed link in the footer [1][2].
- **The only feed INNOQ publishes is a global rolling feed** at `https://www.innoq.com/en/feed.atom` and `https://www.innoq.com/de/feed.atom`. It is a valid Atom 1.0 feed (`xmlns="http://www.w3.org/2005/Atom"`, plus `webfeeds` extension) but holds **only ~20–25 most recent entries** (oldest visible date was 2026-02-26 at the time of research) [3][4]. Joshua's content does **not currently appear** in either language variant of the feed [3][4], so the global feed is unusable as a historical source for his work.
- **Author metadata in the global feed is high-quality:** each `<entry>` carries one or more `<author>` blocks with `<name>`, `<email>` (e.g., `joshua.toepfer@innoq.com`), and a `<uri>` pointing to the staff page. This means *filtering by author is trivially possible* — but only against the ~25-entry rolling window, which makes it useful for *incremental* sync but not initial backfill [3].
- **Content type is NOT carried as a `<category>` element.** The feed has no `<category>` tags; the only way to distinguish articles vs talks vs podcasts vs blog posts is by URL path segment (`/talks/`, `/podcast/`, `/blog/`, `/articles/`) in `<link href>` [3]. This is brittle but workable.
- **The staff page is the canonical, complete listing.** It already groups items by type (Talks, Articles, plus links to "More Talks" / "More content"). It does **not** carry JSON-LD, microdata, or schema.org markup [2]. The sitemap at `/sitemap.xml` lists only collection-level pages, not Joshua's individual items [5].
- **Practical recommendation (decision input, not a decision):** A **hybrid** approach looks unavoidable. Use the staff page (or a "more content"-paginated scrape) for **initial backfill and full inventory**, and use the global `/de/feed.atom` filtered by `<author><email>joshua.toepfer@innoq.com</email></author>` for **lightweight incremental polling**. Pure feed-only is infeasible; pure scrape-only works but is more fragile.

## Findings

### Staff page URL pattern

INNOQ uses the pattern `https://www.innoq.com/{lang}/staff/{slug}/` with three language prefixes: `/de/`, `/en/`, `/ch/`. Joshua's slug is `joshua-toepfer`:

- German: `https://www.innoq.com/de/staff/joshua-toepfer/` [1]
- English: `https://www.innoq.com/en/staff/joshua-toepfer/` [2]
- Swiss: `https://www.innoq.com/ch/staff/joshua-toepfer/` (inferred from the language switcher) [1]

Slugs appear to be derived from `firstname-lastname` lowercased with umlaut transliteration (`ö` → `oe`). Spot-check with Stefan Tilkov confirms the pattern (`/en/staff/stefan-tilkov/`) [6], but at least one INNOQ slug uses an alternate form (`gbeine` for Gerrit Beine, visible in feed `<author><uri>` fields [3]), so **slugs are not 100% predictable** — they must be discovered, not constructed.

### Sections on Joshua's staff page

The German and English variants of Joshua's page show the same structure [1][2]:

- **Bio** ("Senior Consultant at INNOQ", Remote Mob Programming focus, mob.sh maintainer)
- **Social links**: Twitter, Mastodon, LinkedIn, GitHub, email
- **Talks** (6 visible: 3 upcoming 2026 conferences — DevLand, JavaLand, Agile Meets Architecture — plus BED-Con 2025, Java Forum Nord 2025, techcamp Hamburg 2025) with a "More Talks" link [2]
- **Articles** (5 visible spanning 2021–2023, mostly about Remote Mob Programming and the mob.sh tool, several have German+English variants under different slugs) with a "More content" link [2]
- **Trainings** — links externally to `socreatory.com` (not part of innoq.com) [1][2]
- **No Podcasts section visible for Joshua** at this time (he has not co-hosted INNOQ podcast episodes in the surfaced content). The INNOQ podcast feed does exist site-wide [3].
- **Office locations**, **contact form** — boilerplate, not author-specific [1]

The complete enumeration of items visible on Joshua's page during this research is captured in source [2] — that snapshot lists 6 talks and 6 articles (incl. DE/EN duplicates).

### Per-author feed: probed and absent

The following URL patterns were probed against Joshua's slug:

| URL | Status |
|---|---|
| `https://www.innoq.com/en/staff/joshua-toepfer/feed.atom` | 404 [7] |
| `https://www.innoq.com/en/staff/joshua-toepfer.atom` | 406 [7] |
| `https://www.innoq.com/en/staff/joshua-toepfer/feed` | 404 [7] |
| `https://www.innoq.com/en/staff/joshua-toepfer.xml` | 406 [7] |
| `https://www.innoq.com/en/author/joshua-toepfer/feed.atom` | 404 [7] |
| `https://www.innoq.com/en/articles/feed.atom` | 404 [7] |
| `https://www.innoq.com/en/blog/feed.atom` | 404 [7] |

The staff page HTML body **does not link to a per-author feed** anywhere (sidebar, header, near the author's name) — the only feed link surfaced is the site-wide one in the footer [1][2]. We could not directly inspect `<head>` `<link rel="alternate">` tags via WebFetch (it does not return raw head markup), so a small residual chance remains that a hidden alternate exists, but the body-level absence plus the 404s strongly indicate no per-author feed is published. **Single-source caveat** — if certainty is needed, this should be confirmed with `curl -sI` + `curl -s | grep '<link rel="alternate"'` against the page from a developer machine before committing pipeline architecture.

### Global feed structure (the only feed available)

`https://www.innoq.com/en/feed.atom` and `https://www.innoq.com/de/feed.atom` are distinct Atom 1.0 feeds [3][4]:

- **Root element:** `<feed xmlns="http://www.w3.org/2005/Atom" xmlns:webfeeds="http://webfeeds.org/rss/1.0">`
- **Entry children:** `<id>`, `<published>`, `<updated>`, `<link rel="alternate" type="text/html" href="...">`, one or more `<author>`, `<title>`, `<summary type="html">`, `<content type="html" xml:lang="...">`, optional `<webfeeds:cover image="...">`
- **Author block** carries `<name>`, `<email>`, `<uri>` — e.g.:
  ```xml
  <author>
    <name>Michael Seel</name>
    <email>michael.seel@innoq.com</email>
    <uri>https://www.innoq.com/en/staff/michael-seel/</uri>
  </author>
  ```
  Multi-author entries list multiple `<author>` blocks [3]. **Email is the most reliable identifier** for Joshua (`joshua.toepfer@innoq.com`) because the slug field has occasional exceptions [3].
- **No `<category>` elements.** Content type must be inferred from URL path segments inside `<link href>`: `/talks/`, `/podcast/`, `/blog/`, `/articles/`, `/written/` [3].
- **xml:lang on `<content>`** is set to the actual content language (e.g., `de` or `en`), independent of which feed URL was queried. This is the cleanest signal for the "German articles only" constraint mentioned in `infra-004` — but it should be cross-checked against the path segment, since a `/de/...` URL is also a strong language indicator.
- **Size:** Both feeds hold only ~20–25 most recent entries. The oldest visible `<published>` was 2026-02-26 at research time [3][4]. **This is a rolling window, not a full archive.**
- **Joshua's content is not currently in the feed** (his most recent talk is from March 2026 and may already have rolled off; his articles are all from 2021–2023 and definitely outside the window) [3][4].

### Alternative integration paths

- **Sitemap (`/sitemap.xml`)** lists collection-level pages only (`/en/`, `/en/podcast/`, `/en/services/...`) — no individual articles, talks, or staff pages [5]. Not useful for discovering Joshua's items.
- **JSON-LD / microdata / schema.org** on the staff page: **none present** [2]. No JSON API hints (no `Link` headers offering `.json` representations were surfaced via WebFetch, though raw HTTP headers should be reconfirmed with `curl -I`).
- **HTML scraping of the staff page** is feasible because the page renders all items server-side with predictable markup (item list with title, link, date). The "More Talks" / "More content" links suggest pagination exists — that pagination's URL structure was not probed in this research and is an open question.
- **Filtering the global feed by author email** is the cleanest mechanism *for incremental sync only*. Polling `/de/feed.atom`, filtering entries where any `<author><email>` equals `joshua.toepfer@innoq.com`, and using `<published>` as the dedup key, would catch new items within the ~25-entry rolling window without scraping.

### Constraint interactions with `infra-004`

The task specifies "German articles only (English filtered out)". The available signals to enforce this:

1. **`<content xml:lang="de">`** in the feed entry — most reliable [3].
2. **URL path prefix `/de/...`** in `<link href>` — also reliable, and works for scraping the staff page (where each item has a /de/ or /en/ link).
3. The German and English variants of Joshua's articles use **different slugs** (e.g., `/de/articles/2022/12/typist-wechsel-dich-...` vs `/en/articles/2023/03/round-robin-coding/`) [2], so deduplication by URL is fine; there is no `xml:link rel="alternate" hreflang"` cross-reference visible in the surfaced markup (this should be verified against raw HTML before relying on it).

## Sources

1. [Joshua Töpfer – INNOQ (DE)](https://www.innoq.com/de/staff/joshua-toepfer/) — Joshua's German staff page, fetched 2026-05-27. Shows bio, talks, articles, social links, no per-author feed link.
2. [Joshua Töpfer – INNOQ (EN)](https://www.innoq.com/en/staff/joshua-toepfer/) — Joshua's English staff page, fetched 2026-05-27. Complete enumeration of his 6 talks and 6 articles captured in this fetch.
3. [INNOQ global English Atom feed](https://www.innoq.com/en/feed.atom) — Atom 1.0 feed, ~25 entries, fetched 2026-05-27. Source of feed schema details (author block, no `<category>`, URL-path content type inference).
4. [INNOQ global German Atom feed](https://www.innoq.com/de/feed.atom) — distinct from /en/ variant, also ~25 entries, fetched 2026-05-27. Confirms Joshua not currently in either feed's rolling window.
5. [INNOQ sitemap.xml](https://www.innoq.com/sitemap.xml) — fetched 2026-05-27. Collection-level only; no individual articles/talks/staff pages.
6. [Stefan Tilkov – INNOQ (EN)](https://www.innoq.com/en/staff/stefan-tilkov/) — cross-check confirming `/en/staff/{slug}/` URL pattern and identical section structure (Talks, Podcasts, Articles, Blog Posts, Books, Written).
7. WebFetch probe results for `joshua-toepfer/feed.atom`, `.atom`, `/feed`, `.xml`, `/en/author/...`, `/en/articles/feed.atom`, `/en/blog/feed.atom` — all 404/406 responses, 2026-05-27. No URL.

## Open questions

- **Raw `<head>` inspection of the staff page.** WebFetch couldn't return the literal `<head>` markup, so we can't 100% rule out a hidden `<link rel="alternate" type="application/atom+xml">` per-author feed. A `curl -s https://www.innoq.com/de/staff/joshua-toepfer/ | grep -i 'rel="alternate"'` from a dev machine would settle this in seconds.
- **Pagination of "More content" / "More Talks".** The staff page advertises that more items exist beyond what's listed, but we didn't probe the pagination URL pattern. This matters for initial backfill — if pagination follows `?page=2` or `/page/2/`, scraping is straightforward; if it requires JavaScript, scraping becomes much harder.
- **JSON content negotiation.** We didn't test `Accept: application/json` against the staff page. INNOQ has historically been a REST-aware company [INNOQ blog posts about REST, citation 3]; a JSON representation, if it exists, would be the cleanest data source. Worth a 30-second test.
- **Whether INNOQ would accept a feature request for per-author feeds.** Out of scope for this research but worth noting — Joshua is an INNOQ employee and could ask the website team directly. If a per-author feed is added even months later, the pipeline architecture should be able to switch backends without rewriting.
- **Whether feed entries get *updated* (not just added)** — does `<updated>` change when, say, slides are added to a talk page? If yes, the sync pipeline needs to handle updates, not just inserts. The presence of a separate `<updated>` field suggests yes, but we didn't verify with a longitudinal sample.
- **Cross-language deduplication signals.** Many of Joshua's articles exist in both DE and EN variants with different slugs. We didn't find an explicit cross-link in the surfaced markup; verifying this against raw HTML would let the pipeline avoid publishing English duplicates when the constraint says "German only".

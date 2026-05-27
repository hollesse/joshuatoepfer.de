---
slug: innoq-staff-page-scrape-2026-05-27
title: "INNOQ staff page HTML structure and scrape feasibility (backfill workflow)"
scope: infrastructure
date: 2026-05-27
related_tasks: [infra-005]
---

# INNOQ staff page HTML structure and scrape feasibility (backfill workflow)

## Executive summary

- **Backfill is feasible.** Both `/de/staff/joshua-toepfer/` and `/de/written/?by=joshua-toepfer` are plain server-rendered HTML, no JS hydration required, no Cloudflare challenge observed.
- **Recommended source for backfill: `https://www.innoq.com/de/written/?by=joshua-toepfer`.** It is a dedicated German articles-by-author listing, returns exactly the German `/de/articles/` URLs (not the English duplicates, not talks), and is the cleanest input for a German-only filter.
- **Article count today is 3, not 5.** The brief assumed ~5 German articles 2021–2023; the actual count visible on INNOQ today is three German articles (2021/01, 2022/12, 2023/06). The staff page shows five entries because it lists DE+EN versions of two of the three articles side by side. If "5" was a memory from earlier, the difference is most likely just DE/EN duplicates being counted, not missing articles — worth a sanity-check with the user, but planning for n≈3 is safe.
- **`robots.txt` does not block the URLs we need.** The `Disallow` pattern targets only the legacy `*.html` article URL shape (`/de/articles/*/*/*/*.html`). Current article URLs end in a trailing slash (`/de/articles/2023/06/remote-mob-programming/`) and are not matched. `/staff/` and `/written/` are not restricted at all. Sitemap is declared.
- **Recommended parser: `BeautifulSoup` (lxml backend).** Page complexity is low; raw size is moderate; selectolax buys nothing here, and lxml-only is harsher to write than soup. One `requests` call per page, 2 s delay, custom User-Agent identifying the project and linking to the GitHub repo. No need for Playwright or headless browsers.
- **Main risks:** (1) date is rendered as German plain text (`"19. Januar 2021"`) with no machine-readable `<time datetime=...>` attribute confirmed — parser will need a German-month lookup; (2) the markup observed has very few stable IDs/classes, so selectors will lean on semantic tags (`<article>`, `<a href^="/de/articles/">`) rather than CSS classes; (3) WebFetch summarises and may have hidden a real `<time datetime>` or `og:` meta — recommend one curl spike before committing to selectors.

## Question 1 — Staff page HTML structure

**URL fetched:** `https://www.innoq.com/de/staff/joshua-toepfer/`

- **Render mode:** Server-rendered HTML. All article entries are present in the initial HTML response; no JS execution required to see the listing. No SPA / hydration indicators observed.
- **Section heading:** "Weitere Inhalte" (DE) / "More content" (EN). Located after a "Talks" section.
- **Per-entry markup (observed shape):** Each entry is an `<a>` element wrapping the full card, containing a content-type label paragraph (`<p>Artikel</p>`) and a heading (`<h3>` with the article title), plus author avatar `<img>` tags from `res.cloudinary.com/innoq/...`. No section-level stable id/class surfaced via WebFetch.
- **Mixed content types:** Articles AND talks both appear under the staff page (talks above "Weitere Inhalte"; articles inside it). Podcasts not present for Joshua.
- **DE/EN duplication:** The staff page lists BOTH the German and English version of bilingual articles as separate entries. For Joshua: 5 visible entries = 3 unique articles (2 of which are bilingual, 1 DE-only from 2021-01 — though an EN sibling for 2021/01 was also observed in one fetch, so all 3 may actually be bilingual).
- **Pagination:** None on the staff page itself. There's an explicit link to `/de/written/?by=joshua-toepfer` ("Weitere Inhalte") which is the dedicated articles archive for the author, and `/en/talks/?all=true&by=joshua-toepfer` for talks. No `?page=2` URL pattern observed.
- **Date in listing:** Not exposed on staff-page cards. Year/month is recoverable from the URL path (`/de/articles/YYYY/MM/slug/`) which is sufficient for backfill ordering.

**Article URLs found on `/de/staff/joshua-toepfer/`:**
- `/en/articles/2023/07/remote-mob-programming/`
- `/de/articles/2023/06/remote-mob-programming/`
- `/en/articles/2023/03/typist-wechsel-dich-remote-edition-code-uebergabe-mit-dem-mob-tool/`
- `/de/articles/2022/12/typist-wechsel-dich-remote-edition-code-uebergabe-mit-dem-mob-tool/`
- `/de/articles/2021/01/remote-mob-programming-bei-innoq/`
- `/en/articles/2021/01/remote-mob-programming-bei-innoq/` (observed in EN-staff fetch; possibly also on the DE staff page)

## Question 2 — Language indicator

**Strong, reliable indicator:** the URL path prefix `/de/` vs `/en/` is the source of truth and is set per-link on every staff-page entry. A scraper can filter cleanly with `startswith("/de/articles/")` from the listing HTML alone — no per-article fetch needed.

Other observations:
- No flags, "DE"/"EN" labels, or `lang` attribute observed on listing entries themselves.
- A separate English staff page exists at `https://www.innoq.com/en/staff/joshua-toepfer/`. Both the DE and EN staff pages appear to list the same combined set of DE+EN article URLs.
- The dedicated archive `https://www.innoq.com/de/written/?by=joshua-toepfer` returns ONLY `/de/articles/...` URLs (verified: 3 results, all `/de/`). This is the cleanest input for a German-only backfill and is the recommended source.

## Question 3 — Content-type indicator

- On the staff page, all entries inside "Weitere Inhalte" carry a label `<p>Artikel</p>` (or `<p>Article</p>` on the EN page). No mixing of talks into the "Weitere Inhalte" section was observed — talks are in a separate "Talks" section above.
- The `/de/written/?by=joshua-toepfer` archive page is articles-only by definition. Each card still carries an "Artikel" label.
- URL path is also a reliable type indicator: `/articles/` vs `/talks/` vs `/podcast/`. A scraper can filter on path alone and skip the visible label entirely.
- **Recommendation:** filter by URL path (`/de/articles/`) as the primary type filter; the visible "Artikel" label is redundant signal, useful for assertion-style sanity checks but not required.

## Question 4 — Article body HTML structure

**Article sampled:** `https://www.innoq.com/de/articles/2023/06/remote-mob-programming/` and `/de/articles/2021/01/remote-mob-programming-bei-innoq/`.

Observed:
- **Body wrapper:** `<article>` semantic element, contained within a `<main>` (referenced by the skip-link `<a href="#main">Zum Inhalt springen</a>`). Exact attributes on `<article>` not surfaced by WebFetch.
- **Headings:** Plain `<h1>` for title, `<h2>` for subtitle, `<h3>` for sections. No special classes observed. Headings are unstyled-by-class which is good for Markdown conversion.
- **Code blocks:** Not present in the two articles sampled (both are prose-only). Cannot confirm code-block markup pattern from these two; would need to spike against an article that does contain code (e.g. any of Joshua's other articles or a sibling INNOQ article) to confirm the `<pre><code class="language-xxx">` convention.
- **Images:** Plain `<img>` with absolute Cloudinary URLs (`https://res.cloudinary.com/innoq/image/upload/...`). **Not wrapped in `<figure>/<figcaption>`** in the samples. Avatar/author images sit inside author-link blocks. For body images, plan to either keep the Cloudinary URL as-is or download-and-rehost — both are viable; Cloudinary URLs are stable and CDN-served.
- **Date:** Rendered as German plain text (e.g. `"23. Juni 2023"`, `"19. Januar 2021"`). WebFetch one-shot reported `<time>23. Juni 2023</time>` for one article and "no time element" for another — this is most likely WebFetch summarisation noise. Treat the dom date as not-machine-readable for planning purposes and plan to either: (a) parse German month names, or (b) take the date from the URL path (`/YYYY/MM/`) which is sufficient for a content-published-on month.
- **Meta tags / Open Graph:** WebFetch could not surface the `<head>` reliably across multiple attempts. **Not a no-go**, but unknown — a `curl https://www.innoq.com/de/articles/2023/06/remote-mob-programming/ | grep -E '<meta|<link rel|<time'` spike should be done before finalising the parser. Likely `og:title`, `og:url`, and `article:published_time` exist (standard for content-driven sites), in which case prefer them over scraping the visible date.
- **Widgets to strip during Markdown conversion:**
  - Newsletter signup forms (two near the footer in the 2023 article)
  - Author bio / "Über den Autor" blocks with social links
  - "Weitere Informationen" / related-content reference boxes with external links
  - "Kontakt" sidebar
  - Table-of-contents block (or keep, optional)
  - Footnote `[n]` markup if present — needs care, footnotes are valuable content; convert rather than strip
  - "Tags" section at the bottom (Remote Work, Softwareentwicklung, etc.) — optionally keep as frontmatter tags

## Question 5 — robots.txt and scraping policy

**Verbatim contents of `https://www.innoq.com/robots.txt`:**

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

Interpretation:
- **The article disallow pattern requires a trailing `.html`** (`/de/articles/*/*/*/*.html`). Current INNOQ article URLs end in a trailing slash (`/de/articles/2023/06/remote-mob-programming/`), not `.html`. Per standard `robots.txt` semantics, the live article URLs are **not matched** by the disallow.
- This appears to be legacy: at some point INNOQ likely served articles at `.html` URLs; the `robots.txt` was not updated when URLs changed. Tools that strictly follow `robots.txt` (e.g. Scrapy with `ROBOTSTXT_OBEY = True`) will let the current URLs through.
- **`/de/staff/`, `/de/written/`, talk pages, podcast pages:** not mentioned, not disallowed.
- **No `Crawl-delay` directive.** No per-user-agent rules. No `Allow:` directives.
- **Sitemap declared:** `http://www.innoq.com/sitemap.xml`.

**Ethical reading:** robots.txt is permissive for the URLs needed. Given the low-volume use case (3 article fetches every few months at most), this is well within acceptable behaviour. Still recommend a polite delay and identifying User-Agent.

## Question 6 — Anti-scraping protections

Across the ~10 WebFetch calls made to `innoq.com` for this research:
- No Cloudflare interstitial / JS challenge observed.
- No `Retry-After` or 429 responses observed.
- No login/cookie wall.
- WebFetch (which is an LLM HTTP client, similar surface to a normal HTTP request) returned content on every attempt without warmup.
- Pages render fully in raw HTML, no bot-detection JS that gates content.

**Conclusion:** No special protections detected for the URLs of interest. A plain `requests.get(...)` with a sensible User-Agent should work. This is consistent with INNOQ being a consultancy-publishing-content site, not a high-value target for scrapers.

## Question 7 — Sitemap as alternative source

**`https://www.innoq.com/sitemap.xml` is a flat, low-resolution sitemap.** It contains ~50 entries, only top-level category pages (`/de/`, `/de/magazine/`, `/de/written/`, `/de/talks/`, services, etc.). It does **not** contain individual article URLs. Every entry shares the same `lastmod` timestamp (`2026-05-21T10:29:43+00:00`), suggesting it's regenerated wholesale rather than tracking per-page changes.

**Verdict:** the sitemap is **not** a viable source for article URL discovery for this project. The staff page and `/de/written/?by=...` archive remain the only practical discovery surfaces.

## Question 8 — Rate-limiting strategy recommendation

Given:
- Backfill is a one-shot operation (~3 article pages + 1 listing page = 4 requests total for the initial backfill).
- No `Crawl-delay` directive in robots.txt.
- No anti-scraping signals observed.
- INNOQ is a small-traffic publication site, not a search engine or marketplace.

**Recommended posture:**
- **Request delay:** 2 seconds between requests. Generous, well below anything that would trip rate-limiting.
- **User-Agent:** `joshuatoepfer.de-backfill/0.1 (+https://github.com/<user>/joshuatoepfer.de; contact: joshua.toepfer@innoq.com)`. Identifies the project, links to source, gives a contact. INNOQ ops can email if they object.
- **Retry policy:** On 5xx or connection error, exponential backoff: 5 s, 30 s, 2 min. Cap at 3 attempts. On 429, honour `Retry-After` header if present, else wait 5 minutes. On 403/404, do not retry — log and continue.
- **Concurrency:** 1. No parallelism needed at this scale.
- **Caching:** Cache article HTML to disk locally during development so re-runs don't refetch.

## Recommended parser plan

**Library: `requests` + `BeautifulSoup` (with `lxml` parser backend).**

Rationale: page complexity is low, no JS execution required, no need for the speed of `selectolax`. Soup gives the most readable selector code, and the lxml backend keeps parsing fast. The whole job is <10 HTTP requests for the initial backfill.

**Discovery flow:**
1. Fetch `https://www.innoq.com/de/written/?by=joshua-toepfer`.
2. Parse with soup; select `a[href^="/de/articles/"]`. Take `href` and the contained `<h3>` text as title.
3. Result is a list of `(title, absolute_url)` tuples — exactly 3 entries today.

**Per-article extraction:**
1. Fetch each article URL with 2 s delay.
2. Extract metadata:
   - `<title>` → page title (strip ` – INNOQ` suffix)
   - Look for `<meta property="og:title">`, `<meta property="article:published_time">`, `<meta name="description">`, `<link rel="canonical">` — prefer these over DOM scraping when present.
   - If `article:published_time` not present, fall back to parsing `YYYY/MM` from the URL path (sufficient for content-publish month; day can default to 01 or be parsed from the German visible date with a month-name lookup table).
3. Extract body: select `<article>` (the inner content wrapper).
4. Strip nodes by selector before Markdown conversion:
   - Newsletter `<form>` and any element containing the text "Newsletter"
   - Author-bio sidebar (`<aside>` if present, or any element with "Über den Autor" / "About the author" heading)
   - "Weitere Informationen" related-content boxes (look for the heading and its sibling list)
   - `<footer>` inside `<article>` if present
   - Share/social-icon blocks
5. Rewrite remaining `<img src>` to absolute URLs (most are already absolute Cloudinary URLs; just verify).
6. Convert cleaned `<article>` HTML to Markdown via `markdownify` or `html2text`. `markdownify` produces cleaner output for headings/lists/links.

**Output frontmatter:**
```yaml
---
title: "..."                       # from <h1> or og:title
date: 2023-06-23                   # from article:published_time or URL+visible-date
source_url: https://www.innoq.com/de/articles/2023/06/remote-mob-programming/
language: de
tags: [Remote Work, Softwareentwicklung, ...]   # from article footer tag list, optional
original_publication: innoq
---
```

**Code sketch (illustrative — not for direct paste):**
```python
import time
import requests
from bs4 import BeautifulSoup

UA = "joshuatoepfer.de-backfill/0.1 (+https://github.com/.../joshuatoepfer.de; contact: joshua.toepfer@innoq.com)"
session = requests.Session()
session.headers.update({"User-Agent": UA})

def fetch(url: str) -> BeautifulSoup:
    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    time.sleep(2.0)
    return BeautifulSoup(resp.text, "lxml")

archive = fetch("https://www.innoq.com/de/written/?by=joshua-toepfer")
article_links = [
    a["href"] for a in archive.select('a[href^="/de/articles/"]')
]
# expect: ['/de/articles/2023/06/remote-mob-programming/', ...]
```

## Remaining unknowns

These are unresolved by WebFetch summarisation; recommend a 5-minute curl spike before finalising selectors:

1. **`<head>` meta tags — verbatim.** WebFetch consistently strips the `<head>` section from its summaries. Specifically: does INNOQ ship `<meta property="article:published_time">`, `<meta property="og:title">`, `<link rel="canonical">`, `<link rel="alternate" hreflang="...">`? **Resolution:** `curl -sS https://www.innoq.com/de/articles/2023/06/remote-mob-programming/ | head -200`.
2. **`<time datetime="...">` presence.** One WebFetch reply implied there is a `<time>` element with the date, another implied there isn't. **Resolution:** same curl spike, grep for `<time`.
3. **`<article>` element's exact attributes.** Confirmed it exists; classes/IDs not surfaced. Probably `<article class="...">` with some stable token; needs eyeball confirmation for selector specificity.
4. **Code-block markup convention.** Both articles sampled were prose-only. **Resolution:** fetch one INNOQ article known to contain code (e.g. any technical article from `/de/written/?by=...` for a more code-heavy author like Stefan Tilkov or Jochen Christ) and verify the `<pre><code class="language-xxx">` shape before writing the Markdown converter. Joshua's current 3 articles may not need code-block handling at all if none contain code — sanity-check by visiting each once.
5. **Article-count discrepancy.** Task brief says ~5 articles 2021–2023; INNOQ currently shows 3 German articles. Either the "5" was DE+EN duplicates being counted, or 2 articles have been removed since. Worth a quick check with Joshua / the user before treating the gap as a backfill error condition.

## Sources

1. [Joshua Töpfer staff page (DE)](https://www.innoq.com/de/staff/joshua-toepfer/) — primary HTML structure under inspection.
2. [Joshua Töpfer staff page (EN)](https://www.innoq.com/en/staff/joshua-toepfer/) — comparison and content-type/talks listing.
3. [Written-by archive (DE)](https://www.innoq.com/de/written/?by=joshua-toepfer) — recommended discovery URL; returns DE-only article list.
4. [Sample article: Remote Mob Programming (DE, 2023)](https://www.innoq.com/de/articles/2023/06/remote-mob-programming/) — article body structure sample.
5. [Sample article: Remote Mob Programming bei INNOQ (DE, 2021)](https://www.innoq.com/de/articles/2021/01/remote-mob-programming-bei-innoq/) — second article body structure sample.
6. [robots.txt](https://www.innoq.com/robots.txt) — fetched verbatim; permissive for current article URL shape.
7. [sitemap.xml](https://www.innoq.com/sitemap.xml) — confirmed flat, no per-article URLs.
8. Prior local research: `.agentheim/knowledge/research/innoq-staff-feed-2026-05-27.md` — feed-side companion report.

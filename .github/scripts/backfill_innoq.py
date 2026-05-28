#!/usr/bin/env python3
"""Historical INNOQ → joshuatoepfer.de backfill (infra-005).

Sibling to `sync_innoq.py`. The incremental sync polls the rolling
~25-entry Atom feed and can only ever see recent articles. This script
scrapes INNOQ's per-author archive page to discover *historical* articles
that sit outside the feed window, then opens one PR per article in the
same shape (`_posts/<YYYY-MM-DD>-<slug>.md`, draft, `published: false`).

# INNOQ article-page meta-tag inventory (verified via curl spike 2026-05-28
# against three German articles: 2021/01, 2022/12, 2023/06).
#
# PRESENT consistently:
#   - <meta property="og:title" content="...">
#   - <meta property="og:url" content="...">
#   - <time datetime="YYYY-MM-DD" class="standard-header__intro__label">DD. <German month> YYYY</time>
#   - <article class="article-page-default">
#   - <link rel="canonical" href="...">   ← but UNRELIABLE (see below)
#
# ABSENT (in contrast to ADR-0006's tentative selector list):
#   - <meta property="article:published_time"> — not emitted at all
#
# IMPORTANT — `<link rel="canonical">` cannot be trusted as INNOQ-side
# canonical. On the 2023/06 article it points at the print-magazine
# reprint (shop.doag.org). The fetched URL we asked for is the authoritative
# canonical for this pipeline. Backfill uses the fetched URL and ignores
# `<link rel=canonical>`.
#
# Article body structure (verified consistent across all 3 articles):
#   <article class="article-page-default">
#     <section class="author-section">  ← strip (author bio)
#     <aside class="toc">               ← strip (table of contents)
#     <div class="content">             ← keep (the actual article)
#
# No newsletter forms, no "Weitere Informationen" boxes, no <footer>, no
# share icons inside <article> on the three target articles. The strip
# list is defensive (handles those if they appear in future articles) but
# the common case is just author-section + toc.
#
# Images in the body have NO `src` attribute, only `srcset` (Cloudinary
# responsive image markup). Before markdownify, we materialise a `src`
# from the largest-width srcset entry — otherwise markdownify emits
# `![](missing)` which fails the empty-body sanity check downstream.

Workflow contract:
- Reads `URLS` (optional comma-separated list) and `DRY_RUN` ('true'/'false').
- In normal mode: GETs the per-author archive, parses out article URLs,
  filters via dedup, fetches each survivor, builds a plan.
- In dry-run mode: logs what would happen, exits 0 without creating PRs.
- Emits the plan as JSON to `$GITHUB_OUTPUT` under `plan` so the matrix
  publish job can iterate one-PR-per-article.

ADR references: 0002 (canonical strategy), 0006 (sync architecture —
dual-workflow, full-body, PR-history dedup).
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Iterable

from bs4 import BeautifulSoup

from innoq_common import (
    BACKFILL_DISCOVERY_URL,
    ScrapedArticle,
    build_backfill_pr_body,
    build_backfill_pr_title,
    convert_html_to_markdown,
    existing_canonical_urls,
    largest_src_from_srcset,
    parse_german_date,
    pr_history_has_branch,
    split_url_list_input,
    write_github_output,
    write_post_file,
)

USER_AGENT = (
    "joshuatoepfer.de-backfill/0.1 "
    "(+https://github.com/joshuatoepfer/joshuatoepfer.de; "
    "contact: joshua.toepfer@innoq.com)"
)

INNOQ_HOST = "https://www.innoq.com"
ARTICLE_PATH_PREFIX = "/de/articles/"
SITE_TITLE_SUFFIX = " – INNOQ"  # en-dash variant emitted by innoq.com

REQUEST_DELAY_SECONDS = 2.0
BACKOFF_SCHEDULE = (5, 30, 120)  # 5s → 30s → 2min, total 3 attempts on 5xx.
REQUEST_TIMEOUT_SECONDS = 30


def _log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------


def _fetch_html(url: str, *, sleep_fn=time.sleep) -> str:
    """GET an INNOQ URL with politeness delay, custom UA, retries on 5xx.

    On 4xx (other than 429): raise immediately, do not retry (per task spec).
    On 429: honour `Retry-After` if present, else wait 5 minutes, retry once.
    On 5xx: exponential backoff per BACKOFF_SCHEDULE.
    """
    sleep_fn(REQUEST_DELAY_SECONDS)
    last_exc: Exception | None = None
    for attempt, backoff in enumerate([0, *BACKOFF_SCHEDULE]):
        if backoff:
            _log(f"  Backing off {backoff}s before retry {attempt}/{len(BACKOFF_SCHEDULE)} for {url}")
            sleep_fn(backoff)
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/html",
                "Accept-Language": "de,en;q=0.5",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                retry_after = exc.headers.get("Retry-After") if exc.headers else None
                wait = int(retry_after) if retry_after and retry_after.isdigit() else 300
                _log(f"  HTTP 429 from {url}; waiting {wait}s then retrying once")
                sleep_fn(wait)
                last_exc = exc
                continue
            if 500 <= exc.code < 600:
                last_exc = exc
                continue
            # 4xx (other than 429): do not retry.
            raise RuntimeError(
                f"HTTP {exc.code} fetching {url} — refusing to retry on 4xx"
            ) from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            last_exc = exc
            continue
    raise RuntimeError(
        f"Failed to fetch {url} after {len(BACKOFF_SCHEDULE) + 1} attempts: {last_exc!r}"
    )


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def discover_urls_from_listing(html: str) -> list[str]:
    """Parse the per-author archive page; return absolute article URLs.

    Deduplicates while preserving first-seen order so the resulting plan
    has a stable ordering across runs.
    """
    soup = BeautifulSoup(html, "html.parser")
    seen: set[str] = set()
    out: list[str] = []
    for a in soup.select('a[href^="/de/articles/"]'):
        href = (a.get("href") or "").strip()
        if not href:
            continue
        absolute = urllib.parse.urljoin(INNOQ_HOST, href)
        if absolute in seen:
            continue
        seen.add(absolute)
        out.append(absolute)
    return out


# ---------------------------------------------------------------------------
# Metadata + body extraction
# ---------------------------------------------------------------------------


def extract_article_metadata(html: str, *, fetched_url: str) -> dict:
    """Pull title, canonical URL, and published date out of an article page.

    Extraction order (preferred → fallback):
    - Title: `og:title` → stripped `<title>` → `<h1>` inside `<article>`
    - Canonical URL: always the fetched URL (we do NOT trust
      `<link rel="canonical">`; on at least one article it points to an
      external print-magazine page).
    - Date: `<meta property="article:published_time">` (rarely present) →
      `<time datetime="YYYY-MM-DD">` (the typical INNOQ shape) →
      German-month text parse → URL-derived `<year>-<month>-01`.
    """
    soup = BeautifulSoup(html, "html.parser")

    title = _extract_title(soup)
    published_date = _extract_date(soup, fetched_url=fetched_url)

    return {
        "title": title,
        "canonical_url": fetched_url,
        "published_date": published_date,
    }


def _extract_title(soup: BeautifulSoup) -> str:
    og = soup.find("meta", attrs={"property": "og:title"})
    if og and og.get("content"):
        return og["content"].strip()
    title_tag = soup.find("title")
    if title_tag and title_tag.string:
        text = title_tag.string.strip()
        if text.endswith(SITE_TITLE_SUFFIX):
            text = text[: -len(SITE_TITLE_SUFFIX)].strip()
        if text:
            return text
    article = soup.find("article")
    if article:
        h1 = article.find("h1")
        if h1 and h1.get_text(strip=True):
            return h1.get_text(strip=True)
    return ""


def _extract_date(soup: BeautifulSoup, *, fetched_url: str) -> str:
    meta_pub = soup.find("meta", attrs={"property": "article:published_time"})
    if meta_pub and meta_pub.get("content"):
        candidate = meta_pub["content"][:10]
        if _looks_like_iso_date(candidate):
            return candidate

    for time_el in soup.find_all("time"):
        dt = (time_el.get("datetime") or "").strip()
        if _looks_like_iso_date(dt[:10]):
            return dt[:10]

    # German text parse on the article header area.
    header = soup.find("header") or soup
    text_candidates: list[str] = []
    for el in header.find_all(string=True, limit=200):
        text = (el or "").strip()
        if text:
            text_candidates.append(text)
    for candidate in text_candidates:
        parsed = parse_german_date(candidate)
        if parsed:
            return parsed

    # Final fallback: derive YYYY-MM from URL path, day = 01.
    return _date_from_url(fetched_url)


def _looks_like_iso_date(value: str) -> bool:
    if len(value) != 10:
        return False
    return value[4] == "-" and value[7] == "-" and value.replace("-", "").isdigit()


def _date_from_url(url: str) -> str:
    path = urllib.parse.urlparse(url).path.strip("/").split("/")
    # Expected shape: ['de', 'articles', 'YYYY', 'MM', '<slug>']
    try:
        year = path[2]
        month = path[3]
        if len(year) == 4 and year.isdigit() and len(month) == 2 and month.isdigit():
            return f"{year}-{month}-01"
    except IndexError:
        pass
    return ""


def extract_article_body(html: str) -> str:
    """Return the cleaned HTML of `<article>` ready for markdownify.

    Strips: <section class=author-section>, <aside class=toc>, <form>
    (newsletter), <footer> inside article, share-icon blocks ("share"
    in class), and any element with a heading text matching
    /newsletter|weitere informationen|über den autor/i.

    Promotes Cloudinary `srcset` → `src` so markdownify emits a usable
    image reference.
    """
    soup = BeautifulSoup(html, "html.parser")
    article = soup.find("article")
    if article is None:
        return ""

    _strip_article(article)
    _promote_srcset_to_src(article)
    return article.decode_contents()


_DROP_SELECTORS = [
    "section.author-section",
    "aside.toc",
    "form",
    "footer",
]

_DROP_CLASS_TOKENS = ("share-icon", "share-icons", "share-block", "social-icons")

_DROP_HEADING_PATTERNS = (
    "newsletter",
    "weitere informationen",
    "über den autor",
    "uber den autor",
)


def _strip_article(article) -> None:
    # 1. Direct selector-based removals.
    for sel in _DROP_SELECTORS:
        for el in article.select(sel):
            el.decompose()

    # 2. Class-token-based removals (share icons etc.).
    for el in list(article.find_all(True)):
        classes = el.get("class") or []
        for token in _DROP_CLASS_TOKENS:
            if any(token in cls.lower() for cls in classes):
                el.decompose()
                break

    # 3. Heading-text-based removals (newsletter / weitere informationen /
    #    author-bio sections that aren't tagged with a clean class).
    for heading in list(article.find_all(["h2", "h3", "h4"])):
        if not heading.parent:
            continue
        text = heading.get_text(" ", strip=True).lower()
        if any(pattern in text for pattern in _DROP_HEADING_PATTERNS):
            container = heading.parent
            # Drop the heading's container if it's a small wrapper; else
            # drop the heading and its immediate sibling content block.
            if container.name in {"section", "aside", "div"} and container is not article:
                container.decompose()
            else:
                # Remove heading + following siblings until next heading at same level.
                level = int(heading.name[1])
                target = heading.find_next_sibling()
                heading.decompose()
                while target is not None:
                    next_sib = target.find_next_sibling()
                    if target.name and target.name.startswith("h"):
                        try:
                            sib_level = int(target.name[1])
                            if sib_level <= level:
                                break
                        except ValueError:
                            pass
                    target.decompose()
                    target = next_sib


def _promote_srcset_to_src(article) -> None:
    for img in article.find_all("img"):
        if img.get("src"):
            continue
        srcset = img.get("srcset") or ""
        url = largest_src_from_srcset(srcset)
        if url:
            img["src"] = url


# ---------------------------------------------------------------------------
# Build pipeline
# ---------------------------------------------------------------------------


def build_scraped_article(html: str, *, fetched_url: str) -> ScrapedArticle:
    """Top-level extraction: HTML → ScrapedArticle.

    Raises RuntimeError if the article body is missing or empty after
    stripping — those are hard failures per the workflow contract.
    """
    meta = extract_article_metadata(html, fetched_url=fetched_url)
    body_html = extract_article_body(html)
    if not body_html.strip():
        raise RuntimeError(f"Empty article body after stripping for {fetched_url}")
    if not meta["title"]:
        raise RuntimeError(f"Could not extract title for {fetched_url}")
    if not meta["published_date"]:
        raise RuntimeError(f"Could not extract published date for {fetched_url}")

    return ScrapedArticle(
        title=meta["title"],
        canonical_url=meta["canonical_url"],
        published_date=meta["published_date"],
        content_html=body_html,
    )


def guard_article_url(url: str) -> None:
    """Defensive sanity check on a URL coming from the `urls` input.

    The auto-discovery path uses `a[href^="/de/articles/"]` on an INNOQ
    page, so it can't accidentally produce off-domain or non-article
    URLs. The user-supplied URL list has no such guarantee — guard
    against typos / wrong-language paths here.
    """
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"URL must be http(s): {url!r}")
    if parsed.netloc != "www.innoq.com":
        raise ValueError(f"URL must be on www.innoq.com: {url!r}")
    if not parsed.path.startswith(ARTICLE_PATH_PREFIX):
        raise ValueError(
            f"URL must be under {ARTICLE_PATH_PREFIX!r}: {url!r}"
        )


# ---------------------------------------------------------------------------
# Plan construction
# ---------------------------------------------------------------------------


def build_plan(
    urls: Iterable[str],
    *,
    fetch_fn=_fetch_html,
) -> tuple[list[dict], list[dict]]:
    """Iterate candidate URLs and produce a plan + a skip-log.

    Returns (plan, skips):
    - plan: list of items the workflow turns into PRs (one per article).
    - skips: list of {url, reason} entries for dry-run logging.
    """
    seen_canonicals = existing_canonical_urls()
    plan: list[dict] = []
    skips: list[dict] = []

    for url in urls:
        guard_article_url(url)

        # Dedup #1: already in _posts/.
        if url in seen_canonicals or url.rstrip("/") + "/" in seen_canonicals:
            _log(f"SKIP (already in _posts): {url}")
            skips.append({"url": url, "reason": "already-in-posts"})
            continue

        slug = url.rstrip("/").split("/")[-1]
        branch = f"backfill/innoq/{slug}"

        # Dedup #2: PR history.
        if pr_history_has_branch(branch):
            _log(f"SKIP (PR already exists for {branch}): {url}")
            skips.append({"url": url, "reason": "pr-history"})
            continue

        # Fetch + extract.
        html = fetch_fn(url)
        article = build_scraped_article(html, fetched_url=url)

        plan.append(_plan_item(article))

    return plan, skips


def _plan_item(article: ScrapedArticle) -> dict:
    return {
        "slug": article.slug,
        "branch": article.backfill_branch_name,
        "title": build_backfill_pr_title(article),
        "body": build_backfill_pr_body(article),
        "canonical_url": article.canonical_url,
        "post_filename": article.post_filename,
        "_internal": {
            "title": article.title,
            "published_date": article.published_date,
            "content_html": article.content_html,
        },
    }


def materialise_plan_files(plan: list[dict]) -> None:
    """Write each plan item's post file into `_posts/` ready for the PR action."""
    for item in plan:
        internal = item["_internal"]
        article = ScrapedArticle(
            title=internal["title"],
            canonical_url=item["canonical_url"],
            published_date=internal["published_date"],
            content_html=internal["content_html"],
        )
        path = write_post_file(article)
        _log(f"Wrote {path.relative_to(path.parents[1])}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def _slim_plan(plan: list[dict]) -> list[dict]:
    return [{k: v for k, v in item.items() if k != "_internal"} for item in plan]


def main() -> int:
    raw_urls = os.environ.get("URLS", "").strip()
    dry_run = os.environ.get("DRY_RUN", "").lower() in ("1", "true", "yes")
    plan_only = os.environ.get("PLAN_ONLY", "").lower() in ("1", "true", "yes")
    materialise_for_slug = os.environ.get("MATERIALISE_FOR_SLUG", "").strip()

    # Resolve candidate URLs.
    if raw_urls:
        candidate_urls = split_url_list_input(raw_urls)
        _log(f"URL-list mode: {len(candidate_urls)} URL(s) provided.")
    else:
        _log(f"Auto-discovery mode: fetching {BACKFILL_DISCOVERY_URL}")
        listing_html = _fetch_html(BACKFILL_DISCOVERY_URL)
        candidate_urls = discover_urls_from_listing(listing_html)
        _log(f"Discovered {len(candidate_urls)} article URL(s).")
        if not candidate_urls:
            raise RuntimeError(
                f"Listing page {BACKFILL_DISCOVERY_URL} returned 0 article URLs; "
                "page structure may have changed or discovery filter is wrong"
            )

    plan, skips = build_plan(candidate_urls)
    _log(f"Plan size: {len(plan)} PR(s). Skipped: {len(skips)}.")
    for item in plan:
        _log(f"  PLAN: {item['branch']} — {item['title']}")
    for skip in skips:
        _log(f"  SKIP: {skip['url']} ({skip['reason']})")

    if dry_run:
        _log("DRY_RUN=true → not emitting plan, not creating PRs.")
        # Still emit visibility into stdout for the workflow log.
        print(json.dumps({"plan": _slim_plan(plan), "skips": skips}, ensure_ascii=False, indent=2))
        return 0

    if materialise_for_slug:
        target = [item for item in plan if item["slug"] == materialise_for_slug]
        if not target:
            raise RuntimeError(
                f"materialise_for_slug={materialise_for_slug!r} not in plan; "
                "plan likely diverged from the workflow's matrix input"
            )
        materialise_plan_files(target)
        return 0

    if plan_only:
        slim = _slim_plan(plan)
        slim_json = json.dumps(slim, ensure_ascii=False)
        write_github_output("plan", slim_json)
        write_github_output("plan_count", str(len(slim)))
        print(slim_json)
        return 0

    # Default (local dev): emit plan as pretty JSON.
    print(json.dumps(_slim_plan(plan), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

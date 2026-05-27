"""Shared helpers for the INNOQ sync workflows.

Used by both `sync_innoq.py` (incremental feed-poll, infra-004) and
`backfill_innoq.py` (historical scrape-based backfill, infra-005). The two
entry points differ in how they *discover* articles, but share the same
URL → slug rules, frontmatter shape, HTML → Markdown conversion, dedup
logic, and PR-friendly file writes.

This module is intentionally pure-Python with a thin shell-out for the
PR-history dedup check via `gh`. No I/O beyond:
- Reading `_posts/*.md` for dedup
- Running `gh pr list ...` via subprocess
- Writing the generated post file to disk

The PR itself is opened by the `peter-evans/create-pull-request@v6` action
in the workflow — this module only stages files and surfaces metadata.

Design references:
- ADR-0002 (content sync strategy, canonical)
- ADR-0006 (sync architecture: dual workflow, full body, PR-history dedup, force-resync)
- Research `innoq-staff-feed-2026-05-27` (Atom feed shape)
"""

from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import yaml
from markdownify import markdownify as _markdownify

REPO_ROOT = Path(__file__).resolve().parents[2]
POSTS_DIR = REPO_ROOT / "_posts"

JOSHUA_EMAIL = "joshua.toepfer@innoq.com"
FEED_URL = "https://www.innoq.com/de/feed.atom"
BRANCH_PREFIX = "sync/innoq"
PR_LABEL = "sync-innoq"


@dataclass
class FeedEntry:
    """Normalised view of an Atom feed entry.

    Built once during feed parsing so downstream filter/dedup steps don't
    re-poke at `feedparser`'s sometimes inconsistent shapes.
    """

    title: str
    canonical_url: str
    published_date: str  # YYYY-MM-DD
    content_html: str
    xml_lang: str
    author_emails: list[str]

    @property
    def slug(self) -> str:
        return slugify_url(self.canonical_url)

    @property
    def post_filename(self) -> str:
        return f"{self.published_date}-{self.slug}.md"

    @property
    def branch_name(self) -> str:
        return f"{BRANCH_PREFIX}/{self.slug}"

    def resync_branch_name(self, timestamp: str) -> str:
        return f"{BRANCH_PREFIX}/{self.slug}-resync-{timestamp}"


def slugify_url(canonical_url: str) -> str:
    """Return the last non-empty path segment of an INNOQ article URL.

    >>> slugify_url("https://www.innoq.com/de/articles/2023/06/remote-mob-programming/")
    'remote-mob-programming'
    >>> slugify_url("https://www.innoq.com/de/articles/2024/01/foo-bar/")
    'foo-bar'
    >>> slugify_url("https://www.innoq.com/de/articles/2024/01/foo-bar")
    'foo-bar'
    """
    # Strip query/fragment, then take the last non-empty path segment.
    path = canonical_url.split("?")[0].split("#")[0]
    segments = [s for s in path.split("/") if s]
    if not segments:
        raise ValueError(f"Cannot derive slug from URL: {canonical_url!r}")
    return segments[-1]


def existing_canonical_urls(posts_dir: Path = POSTS_DIR) -> set[str]:
    """Scan `_posts/*.md` frontmatter for `canonical_url` values."""
    urls: set[str] = set()
    if not posts_dir.exists():
        return urls
    for post in sorted(posts_dir.glob("*.md")):
        meta = _read_frontmatter(post)
        if not meta:
            continue
        url = meta.get("canonical_url")
        if isinstance(url, str) and url.strip():
            urls.add(url.strip())
    return urls


def find_post_by_canonical_url(
    canonical_url: str, posts_dir: Path = POSTS_DIR
) -> Path | None:
    """Locate the `_posts/*.md` file whose `canonical_url` matches."""
    if not posts_dir.exists():
        return None
    target = canonical_url.strip()
    for post in sorted(posts_dir.glob("*.md")):
        meta = _read_frontmatter(post)
        if not meta:
            continue
        if isinstance(meta.get("canonical_url"), str) and meta["canonical_url"].strip() == target:
            return post
    return None


def read_existing_post_meta(file_path: Path) -> dict:
    """For force-resync: extract preserved fields from an existing post.

    Returns a dict with the keys the worker wants preserved across the
    overwrite — `topic` and `published`. Missing keys are absent from the
    result rather than defaulted, so the caller can decide.
    """
    meta = _read_frontmatter(file_path) or {}
    preserved: dict = {}
    if "topic" in meta:
        preserved["topic"] = meta["topic"]
    if "published" in meta:
        preserved["published"] = meta["published"]
    return preserved


def pr_history_has_branch(branch: str) -> bool:
    """True if `gh` reports any PR (any state) ever opened against `branch`.

    GitHub keeps the PR record even after the head branch is deleted, so
    this is the durable dedup memory once we drop the branch via
    `delete-branch: true` on `peter-evans/create-pull-request`.

    Returns False on `gh` errors so a transient failure doesn't silently
    over-skip articles — the caller should still see the underlying
    feed/parse errors via the loud-fail design.
    """
    try:
        result = subprocess.run(
            [
                "gh",
                "pr",
                "list",
                "--state",
                "all",
                "--head",
                branch,
                "--json",
                "number",
                "--limit",
                "1",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        # `gh` is not installed (local dev outside CI). Behave as if no PR
        # exists; CI is the source of truth.
        return False
    except subprocess.CalledProcessError as exc:
        # Don't silently skip — surface the failure to the caller.
        raise RuntimeError(
            f"`gh pr list` failed for branch {branch!r}: {exc.stderr.strip()}"
        ) from exc
    return result.stdout.strip() not in ("", "[]")


def convert_html_to_markdown(html: str) -> str:
    """Convert Atom `<content type=\"html\">` HTML to project-style Markdown.

    Conventions:
    - ATX headings (`## Foo` instead of `Foo\n===`)
    - Fenced code blocks with language hints preserved
    - `<img>` tags left as Markdown image references with remote URLs
      (no local asset mirroring; INNOQ remains the asset source)
    - No table-of-contents auto-extraction
    """
    if not html:
        return ""
    md = _markdownify(
        html,
        heading_style="ATX",
        code_language_callback=_code_language_from_class,
        bullets="-",
        strip=["script", "style"],
    )
    # Normalise excessive blank lines that markdownify sometimes emits.
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    return md + "\n"


def _code_language_from_class(tag) -> str:
    """Extract language hint from `<pre>` or its inner `<code>`.

    markdownify invokes this callback with the `<pre>` element. INNOQ's
    typical shape is `<pre><code class="language-xxx">`, so we check the
    `<pre>` first, then descend to the first child `<code>`.
    """
    candidates = [tag]
    code_child = tag.find("code") if hasattr(tag, "find") else None
    if code_child is not None:
        candidates.append(code_child)
    for candidate in candidates:
        classes = candidate.get("class", []) or []
        for cls in classes:
            if cls.startswith("language-"):
                return cls.removeprefix("language-")
            if cls.startswith("highlight-"):
                return cls.removeprefix("highlight-")
    return ""


def build_post_content(
    entry: FeedEntry,
    *,
    preserved_meta: dict | None = None,
) -> str:
    """Assemble the full post file body: frontmatter + Markdown content.

    `preserved_meta` is used in force-resync mode to carry forward
    `topic` and `published` from the existing file.
    """
    frontmatter: dict = {
        "layout": "post",
        "title": entry.title,
        "date": entry.published_date,
        "source": "innoq",
        "canonical_url": entry.canonical_url,
        "published": False,
        "render_with_liquid": False,
    }
    if preserved_meta:
        if "published" in preserved_meta:
            frontmatter["published"] = preserved_meta["published"]
        if "topic" in preserved_meta:
            frontmatter["topic"] = preserved_meta["topic"]

    yaml_block = yaml.safe_dump(
        frontmatter,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    ).strip()
    body_md = convert_html_to_markdown(entry.content_html)
    return f"---\n{yaml_block}\n---\n\n{body_md}"


def write_post_file(
    entry: FeedEntry,
    *,
    posts_dir: Path = POSTS_DIR,
    preserved_meta: dict | None = None,
) -> Path:
    """Write the post file into `_posts/` and return its path."""
    posts_dir.mkdir(parents=True, exist_ok=True)
    target = posts_dir / entry.post_filename
    target.write_text(build_post_content(entry, preserved_meta=preserved_meta), encoding="utf-8")
    return target


def build_pr_title(entry: FeedEntry) -> str:
    return f"Sync: {entry.title} [innoq.com]"


def build_pr_body(entry: FeedEntry, *, resync: bool = False) -> str:
    """Markdown body for the sync PR.

    Carries the canonical URL, filter-chain outcome, and the two-step
    publish instructions so Joshua can act on the PR without consulting
    docs.
    """
    header = "Force-resync run" if resync else "Incremental sync from INNOQ"
    return (
        f"{header} for [{entry.title}]({entry.canonical_url}).\n"
        "\n"
        "**Filter chain (all passed):**\n"
        f"- Author email matched (`{JOSHUA_EMAIL}`)\n"
        f"- Content language: `{entry.xml_lang or 'de'}`\n"
        f"- URL path under `/de/articles/`: `{entry.canonical_url}`\n"
        "\n"
        "**Two-step publish:**\n"
        "1. Review and merge this PR. The post is still hidden — "
        "`published: false`.\n"
        "2. Edit the merged file: fill in `topic:` "
        "(`ensemble | adhs | softdev`) and flip `published: true`.\n"
        "\n"
        "Body images point at INNOQ's CDN; no assets are mirrored.\n"
    )


# ---------------------------------------------------------------------------
# Filter chain (kept here so backfill can reuse it for sanity checks)
# ---------------------------------------------------------------------------

ARTICLE_PATH_SEGMENT = "/articles/"
GERMAN_PATH_PREFIX = "/de/"


def filter_reasons(entry: FeedEntry) -> list[str]:
    """Return a list of filter failures. Empty list = entry passes."""
    reasons: list[str] = []
    if JOSHUA_EMAIL not in [e.lower() for e in entry.author_emails]:
        reasons.append(f"author email {JOSHUA_EMAIL!r} not in entry authors")
    if entry.xml_lang.lower() not in ("de", "de-de"):
        reasons.append(f"xml:lang is {entry.xml_lang!r}, expected 'de'")
    if GERMAN_PATH_PREFIX not in entry.canonical_url:
        reasons.append(f"URL does not contain {GERMAN_PATH_PREFIX!r}")
    if ARTICLE_PATH_SEGMENT not in entry.canonical_url:
        reasons.append(f"URL path is not under {ARTICLE_PATH_SEGMENT!r}")
    return reasons


def entry_passes_filter(entry: FeedEntry) -> bool:
    return not filter_reasons(entry)


# ---------------------------------------------------------------------------
# Feed parsing (built on `feedparser`)
# ---------------------------------------------------------------------------


def parse_feed_entries(feed_xml: bytes | str) -> list[FeedEntry]:
    """Parse Atom XML into normalised FeedEntry objects.

    Loud-fail on unparseable XML — feedparser is lenient and tends to
    swallow errors, so we explicitly inspect `feed.bozo` and raise.
    """
    import feedparser

    parsed = feedparser.parse(feed_xml)
    if parsed.bozo and not parsed.entries:
        raise RuntimeError(
            f"Feed parse failed: {parsed.bozo_exception!r}"
        )
    entries: list[FeedEntry] = []
    for raw in parsed.entries:
        entries.append(_entry_from_parsed(raw))
    return entries


def _entry_from_parsed(raw) -> FeedEntry:
    title = (raw.get("title") or "").strip()
    canonical_url = ""
    for link in raw.get("links", []) or []:
        if link.get("rel") in (None, "alternate") and link.get("type", "text/html") == "text/html":
            canonical_url = (link.get("href") or "").strip()
            if canonical_url:
                break
    if not canonical_url:
        canonical_url = (raw.get("link") or "").strip()

    published_date = _date_part(raw.get("published") or raw.get("updated") or "")

    content_html = ""
    xml_lang = ""
    contents = raw.get("content") or []
    if contents:
        first = contents[0]
        content_html = (first.get("value") or "").strip()
        xml_lang = (first.get("language") or first.get("xml:lang") or "").strip()

    author_emails: list[str] = []
    for author in raw.get("authors", []) or []:
        email = (author.get("email") or "").strip()
        if email:
            author_emails.append(email)
    # Some feeds carry author email only on the top-level `author_detail`.
    detail = raw.get("author_detail") or {}
    if detail.get("email") and detail["email"] not in author_emails:
        author_emails.append(detail["email"].strip())

    return FeedEntry(
        title=title,
        canonical_url=canonical_url,
        published_date=published_date,
        content_html=content_html,
        xml_lang=xml_lang,
        author_emails=author_emails,
    )


def _date_part(value: str) -> str:
    """Extract YYYY-MM-DD from an Atom RFC-3339 / RFC-822 timestamp.

    Tolerant: returns "" on unparseable input so callers can decide
    whether that's a hard error.
    """
    if not value:
        return ""
    match = re.search(r"(\d{4}-\d{2}-\d{2})", value)
    if match:
        return match.group(1)
    # RFC-822 fallback: "Tue, 26 May 2026 12:00:00 +0000"
    months = {
        "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
        "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
        "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12",
    }
    m822 = re.search(r"(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})", value)
    if m822:
        day = m822.group(1).zfill(2)
        month = months.get(m822.group(2).title(), "01")
        year = m822.group(3)
        return f"{year}-{month}-{day}"
    return ""


# ---------------------------------------------------------------------------
# Internal: frontmatter reader
# ---------------------------------------------------------------------------


_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _read_frontmatter(file_path: Path) -> dict | None:
    """Return YAML frontmatter as a dict, or None if absent/unparseable."""
    try:
        text = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return None
    try:
        data = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return None
    if not isinstance(data, dict):
        return None
    return data


# ---------------------------------------------------------------------------
# Workflow-output helpers
# ---------------------------------------------------------------------------


def write_github_output(name: str, value: str) -> None:
    """Append `name=value` to the workflow's $GITHUB_OUTPUT file if present.

    No-op when run outside GitHub Actions (e.g., local smoke tests).
    """
    path = os.environ.get("GITHUB_OUTPUT")
    if not path:
        return
    # Multiline-safe heredoc form.
    delim = "EOF_INNOQ_SYNC_OUTPUT"
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(f"{name}<<{delim}\n{value}\n{delim}\n")


def split_force_resync_input(raw: str | None) -> list[str]:
    """Parse the workflow `force_resync` input into a clean URL list."""
    if not raw:
        return []
    return [piece.strip() for piece in raw.split(",") if piece.strip()]

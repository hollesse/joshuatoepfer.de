"""INNOQ talks-page parsing, diff/merge, and PR-body construction (infra-011).

Sibling to `innoq_common.py` (article HTTP/politeness primitives) and
`backfill_innoq.py` (article scrape). This module owns everything
talk-specific:

- `parse_listing`  — `a.list-teaser-event` → ListingEntry
- `parse_detail`   — talk detail page → DetailFields (city, abstract, slides URL)
- `derive_status`  — pure: date vs. today → "upcoming" | "past"
- `merge_talks`    — diff/merge engine reconciling on-disk YAML with scrape output
- `serialise_talks`/`build_pr_body` — output side

`innoq_common.py` stays generic: HTTP fetch, identifying User-Agent,
2 s politeness delay, exponential backoff, no-retry-on-4xx, 429 handling.
This module imports those primitives unchanged.

Design references:
- ADR-0002 (canonical content sync strategy)
- ADR-0007 (talks sync architecture: scrape-only, URL identity, source marker)
- Research `innoq-talks-page-2026-06-02` (selectors with confidence levels)
"""

from __future__ import annotations

import datetime
import logging
import re
import urllib.parse
from dataclasses import dataclass
from typing import Any, Iterable

import yaml
from bs4 import BeautifulSoup

LOGGER = logging.getLogger("innoq_talks")

INNOQ_HOST = "https://www.innoq.com"
TALKS_DISCOVERY_URL = (
    "https://www.innoq.com/de/talks/?all=true&by=joshua-toepfer"
)
TALKS_BRANCH_PREFIX = "sync/innoq-talks"
TALKS_PR_LABEL = "sync-innoq"

# Type-label mapping (ADR-0007 §3 + research §2). Unknown labels default
# to `talk` with a WARN log line; the worker decides whether to widen
# the mapping after seeing logs from a real run.
TYPE_LABEL_MAP = {
    "Vortrag": "talk",
    "Workshop": "workshop",
    "Keynote": "keynote",
}

# INNOQ-authoritative field set (ADR-0007 §3). These are re-derived
# from the scrape every run and overwrite the on-disk YAML.
INNOQ_AUTHORITATIVE_FIELDS = {
    "date",
    "what",
    "where",
    "city",
    "type",
    "duration",
    "abstract",
    "slides",
}

# Fields the sync NEVER overwrites on a `source: innoq` entry: `video`
# is Joshua-authoritative (not derivable from INNOQ markup), `source`
# is a convention marker, `source_url` is identity (set once).
INNOQ_PRESERVE_FIELDS = {"video", "source", "source_url"}


# ---------------------------------------------------------------------------
# Data shapes
# ---------------------------------------------------------------------------


@dataclass
class ListingEntry:
    """Per-talk extract from the listing-page `a.list-teaser-event`.

    Carries fields visible on the listing (date, title, event-name,
    optional duration, type, slides-flag, detail URL). Detail-page
    fields (city, abstract, slides URL, duration fallback) are filled in
    by `parse_detail` after a follow-up fetch.
    """

    source_url: str
    date: str  # YYYY-MM-DD
    what: str
    where: str
    duration: int | None
    type: str
    slides_flag: bool


@dataclass
class DetailFields:
    """Detail-page extract (city, abstract, slides URL, duration fallback).

    Each field is independently optional — talks without `Uhrzeit` in
    the `<dl>` simply don't populate `duration`, talks without a slides
    button leave `slides` as None.
    """

    city: str
    abstract: str
    slides: str | None
    duration: int | None


@dataclass
class ScrapedTalk:
    """Normalised view of a talk after listing + detail pages are merged.

    The composite shape `merge_talks` consumes. Fields map 1:1 onto the
    `_data/talks.yml` schema (minus `status`, which is derived from
    `date` vs. today on every run).
    """

    source_url: str
    date: str
    what: str
    where: str
    city: str
    type: str
    duration: int | None
    abstract: str
    slides: str | None

    def to_yaml_dict(self, *, today: datetime.date) -> dict:
        """Project into the `_data/talks.yml` shape (status derived)."""
        out: dict = {
            "date": self.date,
            "what": self.what,
            "where": self.where,
            "city": self.city,
            "status": derive_status(self.date, today=today),
            "type": self.type,
        }
        if self.duration is not None:
            out["duration"] = self.duration
        out["abstract"] = self.abstract
        if self.slides:
            out["slides"] = self.slides
        out["source"] = "innoq"
        out["source_url"] = self.source_url
        return out


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------


_HHMM_RE = re.compile(
    r"(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})"
)


def parse_duration(text: str | None) -> int | None:
    """Parse a `HH:MM - HH:MM` window into minutes.

    Returns None for empty / unparseable input rather than raising, so
    the caller can fall back to a different source.

    >>> parse_duration("10:30 - 11:10")
    40
    >>> parse_duration("09:00 - 17:00")
    480
    >>> parse_duration("no time here")
    """
    if not text:
        return None
    match = _HHMM_RE.search(text)
    if not match:
        return None
    start_h, start_m, end_h, end_m = (int(g) for g in match.groups())
    minutes = (end_h * 60 + end_m) - (start_h * 60 + start_m)
    return minutes if minutes > 0 else None


def derive_status(date_iso: str, *, today: datetime.date | None = None) -> str:
    """Return 'upcoming' if `date_iso >= today_utc`, else 'past'.

    `today` defaults to today in UTC. Pure function — used everywhere the
    talks pipeline needs a status field, never reads from INNOQ.
    """
    if today is None:
        today = datetime.datetime.now(datetime.timezone.utc).date()
    parsed = datetime.date.fromisoformat(date_iso)
    return "upcoming" if parsed >= today else "past"


# ---------------------------------------------------------------------------
# Listing-page parsing
# ---------------------------------------------------------------------------


def parse_listing(html: str) -> list[ListingEntry]:
    """Extract `ListingEntry` objects from one listing page.

    Selectors (research §2):
      - `a.list-teaser-event` — one per talk
      - `time.event-date[datetime]` — ISO date (YYYY-MM-DD)
      - `h2.list-teaser-event__headline` — title
      - `p.list-teaser-event__subheadline` — event name + optional duration
      - `div.type-label.primary` — German type label
      - `div.label.green` (text == "Folien verfügbar") — slides flag
    """
    soup = BeautifulSoup(html, "html.parser")
    out: list[ListingEntry] = []
    for anchor in soup.select("a.list-teaser-event"):
        href = (anchor.get("href") or "").strip()
        if not href:
            continue
        source_url = urllib.parse.urljoin(INNOQ_HOST, href)

        # Date — first `time[datetime]` inside the anchor.
        time_el = anchor.find("time", attrs={"datetime": True})
        date_iso = (time_el.get("datetime").strip() if time_el else "")

        # Title.
        headline = anchor.select_one("h2.list-teaser-event__headline")
        what = headline.get_text(strip=True) if headline else ""

        # Subheadline → where + optional duration.
        subheadline = anchor.select_one("p.list-teaser-event__subheadline")
        sub_text = subheadline.get_text(" ", strip=True) if subheadline else ""
        where, duration = _split_subheadline(sub_text)

        # Type label → mapped value (or default `talk` + WARN).
        type_el = anchor.select_one("div.type-label.primary")
        type_text = type_el.get_text(strip=True) if type_el else ""
        type_value = TYPE_LABEL_MAP.get(type_text)
        if type_value is None:
            LOGGER.warning(
                "Unknown type-label %r on %s — defaulting to 'talk'",
                type_text, source_url,
            )
            type_value = "talk"

        # Slides flag.
        slides_label = anchor.select_one("div.label.green")
        slides_flag = (
            slides_label is not None
            and "Folien verf" in slides_label.get_text("", strip=True)
        )

        out.append(
            ListingEntry(
                source_url=source_url,
                date=date_iso,
                what=what,
                where=where,
                duration=duration,
                type=type_value,
                slides_flag=slides_flag,
            )
        )
    return out


def _split_subheadline(text: str) -> tuple[str, int | None]:
    """Split a subheadline like `"Event Name / 10:30 - 11:10"`.

    Returns `(where, duration_minutes_or_None)`. If the subheadline has
    no `/`, the whole text is the event name and duration is None.

    Strips trailing icon-arrow whitespace ("Event Name → " et al.) that
    the listing template emits.
    """
    cleaned = text.strip()
    if "/" not in cleaned:
        return cleaned.strip(), None
    where_part, _, rest = cleaned.partition("/")
    return where_part.strip(), parse_duration(rest)


def next_page_url(html: str) -> str | None:
    """Return the absolute URL of the listing's `<a rel=next>`, or None.

    The paginator lives in `nav.paginator`; `rel="next"` is present on
    every page except the last (research §6).
    """
    soup = BeautifulSoup(html, "html.parser")
    next_link = soup.select_one("nav.paginator a[rel='next']")
    if next_link is None:
        return None
    href = (next_link.get("href") or "").strip()
    if not href:
        return None
    return urllib.parse.urljoin(INNOQ_HOST, href)


# ---------------------------------------------------------------------------
# Detail-page parsing
# ---------------------------------------------------------------------------


def parse_detail(html: str) -> DetailFields:
    """Extract city, abstract, slides URL, and duration fallback.

    Selectors (research §3):
      - `article.page-layout-md--default` — the talk's content block
      - Within it: `<p>` children BEFORE `<dl class="date-location-section">` → abstract
      - `<dl> "Ort"` last comma segment → city
      - `<dl> "Uhrzeit"` `HH:MM - HH:MM` → duration fallback
      - `article a.btn[href*="fl_attachment:"]` → slides URL
    """
    soup = BeautifulSoup(html, "html.parser")
    article = soup.select_one("article.page-layout-md--default")
    if article is None:
        return DetailFields(city="", abstract="", slides=None, duration=None)

    dl = article.find("dl", class_="date-location-section")

    # Abstract: <p> children before the <dl>. Skip <h1> (title) and
    # anything after the <dl>.
    abstract_paragraphs: list[str] = []
    for child in article.children:
        if child is dl:
            break
        if getattr(child, "name", None) == "p":
            text = child.get_text(" ", strip=True)
            if text:
                abstract_paragraphs.append(text)
    abstract = "\n\n".join(abstract_paragraphs)

    # City: <dl> "Ort" last comma segment.
    city = _dl_field(dl, "Ort")
    if city:
        city = city.split(",")[-1].strip()

    # Duration fallback: <dl> "Uhrzeit".
    uhrzeit = _dl_field(dl, "Uhrzeit")
    duration = parse_duration(uhrzeit) if uhrzeit else None

    # Slides URL: a.btn[href*="fl_attachment:"].
    slides_link = article.select_one('a.btn[href*="fl_attachment:"]')
    slides = (
        slides_link.get("href").strip()
        if slides_link and slides_link.get("href")
        else None
    )

    return DetailFields(
        city=city or "",
        abstract=abstract,
        slides=slides,
        duration=duration,
    )


def _dl_field(dl, label: str) -> str:
    """Return the text of the `<dd>` following a `<dt>` whose text matches `label`."""
    if dl is None:
        return ""
    for dt in dl.find_all("dt"):
        if dt.get_text(strip=True) == label:
            dd = dt.find_next_sibling("dd")
            if dd is not None:
                return dd.get_text(" ", strip=True)
    return ""


# ---------------------------------------------------------------------------
# Merge engine
# ---------------------------------------------------------------------------


def merge_talks(
    existing: list[dict],
    scraped: Iterable[ScrapedTalk],
    *,
    today: datetime.date | None = None,
) -> tuple[list[dict], dict[str, list[str]]]:
    """Reconcile on-disk YAML (`existing`) with scraped output (`scraped`).

    Returns `(merged_entries, diff_summary)` where:

    - `merged_entries` is the list ready to serialise back into
      `_data/talks.yml`. Order is preserved for unchanged entries; new
      INNOQ entries are appended at the end.
    - `diff_summary` is a dict with four buckets:
        - `new`: list of human-readable lines describing newly-discovered talks
        - `status_transitions`: lines describing `upcoming → past` etc.
        - `updates`: lines describing fields that changed in-place
        - `ambiguous`: lines describing composite-key matches (first-sync fallback,
          ADR-0007 §2) — surfaced but never silently merged.

    Behaviour (ADR-0007 §3):
      - `source: manual` entries are passed through unchanged.
      - `source: innoq` entries are matched by `source_url` exact equality.
      - INNOQ-authoritative fields are re-derived and overwrite on match.
      - `video` and the `source`/`source_url` fields are preserved.
      - `status` is computed from `date` vs. today on every run.

    First-sync fallback: a scraped entry's (what, where, date) tuple is
    checked against any existing entry without a `source_url`. Matches are
    surfaced in the `ambiguous` bucket — both the manual entry and the new
    INNOQ entry remain so Joshua can merge manually on PR review.
    """
    if today is None:
        today = datetime.datetime.now(datetime.timezone.utc).date()

    diff: dict[str, list[str]] = {
        "new": [],
        "status_transitions": [],
        "updates": [],
        "ambiguous": [],
    }

    scraped_list = list(scraped)
    scraped_by_url = {s.source_url: s for s in scraped_list}

    merged: list[dict] = []
    matched_urls: set[str] = set()

    for entry in existing:
        source = entry.get("source")
        if source == "manual":
            # Manual entries pass through untouched.
            merged.append(dict(entry))  # defensive copy
            # First-sync composite-key check: any scraped entry that
            # matches by (what, where, date) is surfaced as ambiguous.
            _check_ambiguous_composite(entry, scraped_list, diff)
            continue

        if source == "innoq":
            url = entry.get("source_url")
            if url and url in scraped_by_url:
                scraped_match = scraped_by_url[url]
                matched_urls.add(url)
                new_entry, changed_fields, status_transition = _apply_scrape(
                    entry, scraped_match, today=today,
                )
                merged.append(new_entry)
                if status_transition:
                    diff["status_transitions"].append(
                        f"{new_entry['what']}: {status_transition}"
                    )
                if changed_fields:
                    diff["updates"].append(
                        f"{new_entry['what']}: "
                        + ", ".join(sorted(changed_fields))
                    )
                continue
            # Innoq entry on disk but not in current scrape — keep
            # (e.g. INNOQ took the page down or the URL changed; safer
            # to preserve than drop).
            merged.append(dict(entry))
            continue

        # No source marker — treat as manual for safety. (Should not
        # happen after the one-time migration but the merge engine must
        # be defensive.)
        merged.append(dict(entry))
        _check_ambiguous_composite(entry, scraped_list, diff)

    # Append previously-unseen scraped entries.
    for scraped_entry in scraped_list:
        if scraped_entry.source_url in matched_urls:
            continue
        new_entry = scraped_entry.to_yaml_dict(today=today)
        merged.append(new_entry)
        diff["new"].append(
            f"{new_entry['what']} ({new_entry['date']}) — {new_entry['source_url']}"
        )

    return merged, diff


def _apply_scrape(
    existing: dict,
    scraped: ScrapedTalk,
    *,
    today: datetime.date,
) -> tuple[dict, set[str], str]:
    """Merge a scraped talk into an existing `source: innoq` entry.

    Returns `(merged_entry, changed_fields, status_transition_or_empty)`.
    INNOQ-authoritative fields are re-derived; `video` and the source
    markers are carried over from `existing`.
    """
    new_yaml = scraped.to_yaml_dict(today=today)

    # Preserve Joshua-authoritative fields.
    for field in INNOQ_PRESERVE_FIELDS:
        if field in existing and field not in new_yaml:
            # `video` is preserved as-is; `source` and `source_url` are
            # already in new_yaml from to_yaml_dict, so this only affects
            # `video`.
            new_yaml[field] = existing[field]
    if "video" in existing:
        new_yaml["video"] = existing["video"]

    changed_fields: set[str] = set()
    for field in INNOQ_AUTHORITATIVE_FIELDS:
        old_value = existing.get(field)
        new_value = new_yaml.get(field)
        if old_value != new_value:
            changed_fields.add(field)

    status_transition = ""
    if existing.get("status") != new_yaml.get("status"):
        status_transition = (
            f"{existing.get('status', '?')} → {new_yaml.get('status', '?')}"
        )

    return new_yaml, changed_fields, status_transition


def _check_ambiguous_composite(
    entry: dict,
    scraped_list: list[ScrapedTalk],
    diff: dict[str, list[str]],
) -> None:
    """Surface (what, where, date) matches against an unmarked entry.

    Pure side-effect on `diff["ambiguous"]`. Used during the first sync
    when manual entries may turn out to correspond to INNOQ-origin talks.
    """
    composite = (
        (entry.get("what") or "").strip(),
        (entry.get("where") or "").strip(),
        (entry.get("date") or ""),
    )
    if not all(composite):
        return
    for scraped_entry in scraped_list:
        scraped_composite = (
            scraped_entry.what.strip(),
            scraped_entry.where.strip(),
            scraped_entry.date,
        )
        if scraped_composite == composite:
            diff["ambiguous"].append(
                f"{entry['what']} ({entry['date']}) — manual entry composite-matches "
                f"{scraped_entry.source_url}; flip to source: innoq with that "
                f"source_url to merge, or leave as manual"
            )


# ---------------------------------------------------------------------------
# Output side
# ---------------------------------------------------------------------------


_YAML_HEADER = """\
# Talks — kommende und vergangene Vorträge / Workshops.
# Fields: date (ISO), what, where, city, status (upcoming|past), type (talk|workshop|keynote),
#         duration (minutes), abstract, slides (URL, optional), video (URL, optional),
#         source (innoq|manual), source_url (URL, required when source: innoq).
#
# `source` marks who owns the entry. `source: innoq` entries are maintained by the
# INNOQ talks sync workflow (.github/workflows/sync-innoq-talks.yml, infra-011) and
# matched across runs by their `source_url`. INNOQ-authoritative fields (date, what,
# where, city, type, duration, abstract, slides, status) are overwritten on every
# sync; only `video` and the `source` field itself are safe to hand-edit on a
# `source: innoq` entry.
#
# `source: manual` entries are owned by Joshua and are never touched by the sync.
# Flip an entry to `source: manual` to lock in a local override.

"""


def serialise_talks(entries: list[dict]) -> str:
    """YAML-serialise a list of talks for `_data/talks.yml`.

    Preserves field order on each entry (insertion order from the merge
    engine) and emits unicode literally.
    """
    body = yaml.safe_dump(
        entries,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=1000,
    )
    return _YAML_HEADER + body


def build_pr_body(diff: dict[str, list[str]]) -> str:
    """Markdown body for the talks-sync PR.

    Summarises the diff in up to four buckets (new / status / updates /
    ambiguous). Empty buckets are omitted. Always carries the
    INNOQ-authoritative-overwrite warning per ADR-0007 §3.
    """
    lines: list[str] = [
        "Talks sync from `https://www.innoq.com/de/talks/?all=true&by=joshua-toepfer`.",
        "",
    ]

    if diff.get("new"):
        lines.append("### New talks")
        lines.append("")
        lines.extend(f"- {item}" for item in diff["new"])
        lines.append("")

    if diff.get("status_transitions"):
        lines.append("### Status transitions")
        lines.append("")
        lines.extend(f"- {item}" for item in diff["status_transitions"])
        lines.append("")

    if diff.get("updates"):
        lines.append("### Field updates")
        lines.append("")
        lines.extend(f"- {item}" for item in diff["updates"])
        lines.append("")

    if diff.get("ambiguous"):
        lines.append("### Ambiguous matches (first-sync fallback)")
        lines.append("")
        lines.append(
            "These INNOQ entries composite-match (`what`, `where`, `date`) "
            "an existing `source: manual` entry. Both are kept so you can "
            "merge manually; flip the manual entry to `source: innoq` with "
            "the listed `source_url` to claim the match."
        )
        lines.append("")
        lines.extend(f"- {item}" for item in diff["ambiguous"])
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(
        "**Heads-up:** INNOQ-authoritative fields (`date`, `what`, `where`, "
        "`city`, `type`, `duration`, `abstract`, `slides`, `status`) are "
        "re-derived from innoq.com on every sync, so cosmetic local edits "
        "on `source: innoq` entries will be **overwritten** on the next run. "
        "Only `video` and `source` are safe to hand-edit on a `source: innoq` "
        "entry. To lock in a permanent local override, flip the entry to "
        "`source: manual`."
    )
    lines.append("")
    return "\n".join(lines)

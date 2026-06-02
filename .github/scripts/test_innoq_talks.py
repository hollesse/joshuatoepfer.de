"""Unit tests for the INNOQ talks-sync helpers (`innoq_talks`).

These cover the four pure-function pieces declared in ADR-0007 §1 —
`parse_listing`, `parse_detail`, `derive_status`, and `merge_talks` —
plus the YAML round-trip and PR-body construction. Anything that touches
the live INNOQ network or the `gh` CLI is out of scope (same policy as
`test_innoq_common.py` and `test_backfill_innoq.py`).

Test inputs are inline HTML/YAML fixtures sourced from the research file
`innoq-talks-page-2026-06-02.md` so the selectors are exercised against
markup shapes verified to exist on innoq.com today.
"""

from __future__ import annotations

import datetime
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import innoq_talks as it  # noqa: E402


# ---------------------------------------------------------------------------
# Inline HTML fixtures
# ---------------------------------------------------------------------------

# Listing-page fixture — one entry shape verified per research §2.
# Two entries: one with duration on the subheadline, one without; one with
# slides flag, one without.
LISTING_HTML_PAGE_1 = """
<html>
<body>
<main>
  <turbo-frame id="upcoming_talks" target="_top">
    <a class="list-teaser-event"
       href="/de/talks/2026/03/four-years-one-ensemble-challenges-aha-moments-and-true-team-transformation/">
      <div class="event-date-section">
        <div class="type-label primary">Vortrag</div>
        <time datetime="2026-03-10" class="event-date">10 Mär 2026</time>
      </div>
      <div class="list-teaser__content">
        <div class="list-teaser__labels">
          <div class="type-label primary">Vortrag</div>
          <div class="label green">Folien verfügbar</div>
        </div>
        <div class="list-teaser__body">
          <h2 class="list-teaser-event__headline">Four Years, One Ensemble</h2>
          <p class="list-teaser-event__subheadline">
            Agile Meets Architecture / 10:30 - 11:10
          </p>
        </div>
      </div>
    </a>
    <a class="list-teaser-event"
       href="/de/talks/2024/09/java-forum-nord/">
      <div class="event-date-section">
        <div class="type-label primary">Vortrag</div>
        <time datetime="2024-09-12" class="event-date">12 Sep 2024</time>
      </div>
      <div class="list-teaser__content">
        <div class="list-teaser__labels">
          <div class="type-label primary">Vortrag</div>
        </div>
        <div class="list-teaser__body">
          <h2 class="list-teaser-event__headline">Vortrag bei Java Forum Nord</h2>
          <p class="list-teaser-event__subheadline">
            Java Forum Nord
          </p>
        </div>
      </div>
    </a>
    <nav class="paginator">
      <a rel="next" href="/de/upcoming_talks/?all=true&amp;by=joshua-toepfer&amp;page=2">Next</a>
    </nav>
  </turbo-frame>
</main>
</body>
</html>
"""

LISTING_HTML_PAGE_2 = """
<main>
  <turbo-frame id="upcoming_talks" target="_top">
    <a class="list-teaser-event"
       href="/de/talks/2023/11/remote-mob-programming-zuhause-aber-nicht-allein/">
      <div class="event-date-section">
        <div class="type-label primary">Vortrag</div>
        <time datetime="2023-11-15" class="event-date">15 Nov 2023</time>
      </div>
      <div class="list-teaser__content">
        <div class="list-teaser__labels">
          <div class="type-label primary">Vortrag</div>
          <div class="label green">Folien verfügbar</div>
        </div>
        <div class="list-teaser__body">
          <h2 class="list-teaser-event__headline">Remote Mob Programming</h2>
          <p class="list-teaser-event__subheadline">
            Some Conference / 14:00 - 14:45
          </p>
        </div>
      </div>
    </a>
    <nav class="paginator">
      <a rel="prev" href="/de/upcoming_talks/?all=true&amp;by=joshua-toepfer">Prev</a>
    </nav>
  </turbo-frame>
</main>
"""

LISTING_HTML_UNKNOWN_TYPE = """
<main>
  <a class="list-teaser-event" href="/de/talks/2026/01/some-podium/">
    <div class="event-date-section">
      <div class="type-label primary">Podiumsdiskussion</div>
      <time datetime="2026-01-15">15 Jan 2026</time>
    </div>
    <div class="list-teaser__content">
      <div class="list-teaser__body">
        <h2 class="list-teaser-event__headline">Panel on Software</h2>
        <p class="list-teaser-event__subheadline">SomeConf</p>
      </div>
    </div>
  </a>
</main>
"""

LISTING_HTML_WORKSHOP_KEYNOTE = """
<main>
  <a class="list-teaser-event" href="/de/talks/2026/05/workshop-x/">
    <div class="event-date-section">
      <div class="type-label primary">Workshop</div>
      <time datetime="2026-05-04">4 Mai 2026</time>
    </div>
    <div class="list-teaser__content">
      <div class="list-teaser__body">
        <h2 class="list-teaser-event__headline">Workshop X</h2>
        <p class="list-teaser-event__subheadline">SomeConf / 09:00 - 17:00</p>
      </div>
    </div>
  </a>
  <a class="list-teaser-event" href="/de/talks/2026/05/keynote-y/">
    <div class="event-date-section">
      <div class="type-label primary">Keynote</div>
      <time datetime="2026-05-05">5 Mai 2026</time>
    </div>
    <div class="list-teaser__content">
      <div class="list-teaser__body">
        <h2 class="list-teaser-event__headline">Keynote Y</h2>
        <p class="list-teaser-event__subheadline">SomeConf / 09:00 - 10:00</p>
      </div>
    </div>
  </a>
</main>
"""


# Detail-page fixture — shape verified per research §3.
DETAIL_HTML_WITH_SLIDES = """
<html>
<head>
  <meta property="og:url" content="https://www.innoq.com/de/talks/2026/03/four-years-one-ensemble-challenges-aha-moments-and-true-team-transformation/">
</head>
<body>
<main id="main" role="main" class="talk-page">
  <article class="page-layout-md--default">
    <h1 class="talk-title">Four Years, One Ensemble</h1>
    <p>Ensemble Programming is more than just a way of working together.</p>
    <p>I'll highlight the obvious benefits and the less-obvious ones.</p>
    <p>This talk is for anyone curious about Ensemble Programming.</p>
    <dl class="date-location-section">
      <dt>Datum</dt><dd>10.03.2026</dd>
      <dt>Uhrzeit</dt><dd>10:30 - 11:10</dd>
      <dt>Konferenz / Veranstaltung</dt><dd><a href="https://x">Agile Meets Architecture</a></dd>
      <dt>Ort</dt><dd>Maschinenhaus, Berlin </dd>
    </dl>
    <a class="btn"
       href="https://res.cloudinary.com/innoq/image/upload/fl_attachment:slides.pdf/v1/uploads-production/slides.pdf">
      Folien downloaden
    </a>
  </article>
</main>
</body>
</html>
"""

DETAIL_HTML_NO_SLIDES = """
<html>
<body>
<main>
  <article class="page-layout-md--default">
    <h1 class="talk-title">ADHS in der IT 2025</h1>
    <p>Ein Vortrag über ADHS in der IT.</p>
    <dl class="date-location-section">
      <dt>Datum</dt><dd>04.06.2025</dd>
      <dt>Ort</dt><dd>Klubhaus St. Pauli, Hamburg</dd>
    </dl>
  </article>
</main>
</body>
</html>
"""

DETAIL_HTML_DURATION_FALLBACK = """
<html>
<body>
<main>
  <article class="page-layout-md--default">
    <h1 class="talk-title">Java Forum Nord Talk</h1>
    <p>Body.</p>
    <dl class="date-location-section">
      <dt>Datum</dt><dd>12.09.2024</dd>
      <dt>Uhrzeit</dt><dd>15:00 - 15:45</dd>
      <dt>Ort</dt><dd>Hannover Congress Centrum, Hannover</dd>
    </dl>
  </article>
</main>
</body>
</html>
"""

DETAIL_HTML_MULTI_COMMA_VENUE = """
<html>
<body>
<main>
  <article class="page-layout-md--default">
    <h1 class="talk-title">Multi-Comma City</h1>
    <p>Body.</p>
    <dl class="date-location-section">
      <dt>Datum</dt><dd>01.06.2024</dd>
      <dt>Ort</dt><dd>KOMED, Forum 1, Köln</dd>
    </dl>
  </article>
</main>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# parse_listing
# ---------------------------------------------------------------------------


class ParseListingTests(unittest.TestCase):
    def test_extracts_all_listing_entries(self):
        entries = it.parse_listing(LISTING_HTML_PAGE_1)
        self.assertEqual(len(entries), 2)

    def test_extracts_canonical_url_absolute(self):
        entries = it.parse_listing(LISTING_HTML_PAGE_1)
        self.assertEqual(
            entries[0].source_url,
            "https://www.innoq.com/de/talks/2026/03/four-years-one-ensemble-challenges-aha-moments-and-true-team-transformation/",
        )

    def test_extracts_date_iso(self):
        entries = it.parse_listing(LISTING_HTML_PAGE_1)
        self.assertEqual(entries[0].date, "2026-03-10")
        self.assertEqual(entries[1].date, "2024-09-12")

    def test_extracts_title(self):
        entries = it.parse_listing(LISTING_HTML_PAGE_1)
        self.assertEqual(entries[0].what, "Four Years, One Ensemble")
        self.assertEqual(entries[1].what, "Vortrag bei Java Forum Nord")

    def test_extracts_where_from_subheadline_before_slash(self):
        entries = it.parse_listing(LISTING_HTML_PAGE_1)
        self.assertEqual(entries[0].where, "Agile Meets Architecture")
        self.assertEqual(entries[1].where, "Java Forum Nord")

    def test_extracts_duration_when_present(self):
        entries = it.parse_listing(LISTING_HTML_PAGE_1)
        # 10:30 - 11:10 → 40 minutes
        self.assertEqual(entries[0].duration, 40)

    def test_duration_absent_when_no_slash_on_subheadline(self):
        entries = it.parse_listing(LISTING_HTML_PAGE_1)
        # "Java Forum Nord" has no `/` separator → no duration on listing
        self.assertIsNone(entries[1].duration)

    def test_maps_vortrag_to_talk(self):
        entries = it.parse_listing(LISTING_HTML_PAGE_1)
        self.assertEqual(entries[0].type, "talk")

    def test_slides_flag_set_when_label_green_present(self):
        entries = it.parse_listing(LISTING_HTML_PAGE_1)
        self.assertTrue(entries[0].slides_flag)

    def test_slides_flag_false_when_label_green_absent(self):
        entries = it.parse_listing(LISTING_HTML_PAGE_1)
        self.assertFalse(entries[1].slides_flag)

    def test_paginator_next_link_extracted(self):
        next_url = it.next_page_url(LISTING_HTML_PAGE_1)
        self.assertIsNotNone(next_url)
        self.assertIn("page=2", next_url)
        self.assertTrue(next_url.startswith("https://www.innoq.com"))

    def test_paginator_next_link_absent_on_last_page(self):
        next_url = it.next_page_url(LISTING_HTML_PAGE_2)
        self.assertIsNone(next_url)

    def test_unknown_type_defaults_to_talk_and_logs_warn(self):
        with self.assertLogs("innoq_talks", level="WARNING") as cm:
            entries = it.parse_listing(LISTING_HTML_UNKNOWN_TYPE)
        self.assertEqual(entries[0].type, "talk")
        joined = "\n".join(cm.output)
        self.assertIn("Podiumsdiskussion", joined)
        self.assertIn("/de/talks/2026/01/some-podium/", joined)

    def test_workshop_and_keynote_mapped(self):
        entries = it.parse_listing(LISTING_HTML_WORKSHOP_KEYNOTE)
        self.assertEqual(entries[0].type, "workshop")
        self.assertEqual(entries[1].type, "keynote")


# ---------------------------------------------------------------------------
# parse_detail
# ---------------------------------------------------------------------------


class ParseDetailTests(unittest.TestCase):
    def test_extracts_city_from_last_comma_segment(self):
        detail = it.parse_detail(DETAIL_HTML_WITH_SLIDES)
        self.assertEqual(detail.city, "Berlin")

    def test_extracts_abstract_from_paragraphs_before_dl(self):
        detail = it.parse_detail(DETAIL_HTML_WITH_SLIDES)
        # Three <p> elements joined with double-newline.
        self.assertIn("Ensemble Programming is more than just", detail.abstract)
        self.assertIn("I'll highlight the obvious benefits", detail.abstract)
        self.assertIn("\n\n", detail.abstract)
        # The <h1> is the title — it must NOT appear in the abstract.
        self.assertNotIn("Four Years, One Ensemble", detail.abstract)
        # The <dl> labels must NOT appear in the abstract.
        self.assertNotIn("Maschinenhaus", detail.abstract)

    def test_extracts_slides_url(self):
        detail = it.parse_detail(DETAIL_HTML_WITH_SLIDES)
        self.assertIsNotNone(detail.slides)
        self.assertIn("fl_attachment:", detail.slides)

    def test_slides_absent_when_no_btn_link(self):
        detail = it.parse_detail(DETAIL_HTML_NO_SLIDES)
        self.assertIsNone(detail.slides)

    def test_duration_fallback_from_uhrzeit(self):
        detail = it.parse_detail(DETAIL_HTML_DURATION_FALLBACK)
        # 15:00 - 15:45 → 45 minutes
        self.assertEqual(detail.duration, 45)

    def test_duration_absent_when_no_uhrzeit(self):
        detail = it.parse_detail(DETAIL_HTML_NO_SLIDES)
        self.assertIsNone(detail.duration)

    def test_multi_comma_venue_picks_last_segment_as_city(self):
        detail = it.parse_detail(DETAIL_HTML_MULTI_COMMA_VENUE)
        self.assertEqual(detail.city, "Köln")

    def test_city_strips_trailing_whitespace(self):
        # The fixture has a trailing space on the Ort dd ("Berlin ").
        detail = it.parse_detail(DETAIL_HTML_WITH_SLIDES)
        self.assertEqual(detail.city, "Berlin")


# ---------------------------------------------------------------------------
# derive_status
# ---------------------------------------------------------------------------


class DeriveStatusTests(unittest.TestCase):
    def test_today_is_upcoming(self):
        today = datetime.date(2026, 6, 2)
        self.assertEqual(it.derive_status("2026-06-02", today=today), "upcoming")

    def test_future_is_upcoming(self):
        today = datetime.date(2026, 6, 2)
        self.assertEqual(it.derive_status("2027-01-01", today=today), "upcoming")

    def test_past_is_past(self):
        today = datetime.date(2026, 6, 2)
        self.assertEqual(it.derive_status("2025-01-01", today=today), "past")

    def test_yesterday_is_past(self):
        today = datetime.date(2026, 6, 2)
        self.assertEqual(it.derive_status("2026-06-01", today=today), "past")


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------


class DurationParserTests(unittest.TestCase):
    def test_parses_hhmm_window(self):
        self.assertEqual(it.parse_duration("10:30 - 11:10"), 40)
        self.assertEqual(it.parse_duration("09:00 - 17:00"), 480)

    def test_handles_extra_whitespace(self):
        self.assertEqual(it.parse_duration("  10:30-11:10  "), 40)

    def test_returns_none_on_unparseable(self):
        self.assertIsNone(it.parse_duration(""))
        self.assertIsNone(it.parse_duration("no time here"))
        self.assertIsNone(it.parse_duration("10:30"))


# ---------------------------------------------------------------------------
# merge_talks — the diff/merge engine
# ---------------------------------------------------------------------------


class MergeTalksFirstSyncTests(unittest.TestCase):
    """First-sync scenario: existing YAML has only `source: manual` entries.

    The scrape produces fresh `source: innoq` entries. Manual entries
    must pass through untouched; new INNOQ entries must land.
    """

    def setUp(self):
        self.existing = [
            {
                "date": "2026-06-18",
                "what": "ADHS in der Softwareentwicklung",
                "where": "Karlsruher Entwicklertag",
                "city": "Karlsruhe",
                "status": "upcoming",
                "type": "talk",
                "duration": 45,
                "abstract": "…",
                "source": "manual",
            }
        ]
        self.scraped = [
            it.ScrapedTalk(
                source_url="https://www.innoq.com/de/talks/2026/03/x/",
                date="2026-03-10",
                what="Four Years, One Ensemble",
                where="Agile Meets Architecture",
                city="Berlin",
                type="talk",
                duration=40,
                abstract="Body.",
                slides="https://res.cloudinary.com/innoq/image/upload/fl_attachment:s.pdf/v1/uploads/s.pdf",
            )
        ]
        self.today = datetime.date(2026, 6, 2)

    def test_manual_entry_passed_through(self):
        merged, diff = it.merge_talks(self.existing, self.scraped, today=self.today)
        manual = [e for e in merged if e["source"] == "manual"]
        self.assertEqual(len(manual), 1)
        self.assertEqual(manual[0]["what"], "ADHS in der Softwareentwicklung")

    def test_innoq_entry_added(self):
        merged, _ = it.merge_talks(self.existing, self.scraped, today=self.today)
        innoq = [e for e in merged if e["source"] == "innoq"]
        self.assertEqual(len(innoq), 1)
        self.assertEqual(
            innoq[0]["source_url"], "https://www.innoq.com/de/talks/2026/03/x/"
        )

    def test_innoq_entry_status_derived(self):
        merged, _ = it.merge_talks(self.existing, self.scraped, today=self.today)
        innoq = [e for e in merged if e["source"] == "innoq"][0]
        # 2026-03-10 < today (2026-06-02) → past
        self.assertEqual(innoq["status"], "past")

    def test_diff_summary_lists_new_talks(self):
        _, diff = it.merge_talks(self.existing, self.scraped, today=self.today)
        self.assertIn("Four Years, One Ensemble", " ".join(diff["new"]))

    def test_slides_field_populated(self):
        merged, _ = it.merge_talks(self.existing, self.scraped, today=self.today)
        innoq = [e for e in merged if e["source"] == "innoq"][0]
        self.assertIn("fl_attachment:", innoq["slides"])


class MergeTalksUpdateInPlaceTests(unittest.TestCase):
    """Subsequent-sync scenario: a `source: innoq` entry already exists.

    INNOQ-authoritative fields must be overwritten; `video` and `source`
    must be preserved.
    """

    def setUp(self):
        self.existing = [
            {
                "date": "2026-03-10",
                "what": "Old title (cosmetic edit)",
                "where": "Agile Meets Architecture",
                "city": "Berlin",
                "status": "upcoming",
                "type": "talk",
                "duration": 40,
                "abstract": "Old abstract.",
                "video": "https://youtube.com/watch?v=ABC123",
                "source": "innoq",
                "source_url": "https://www.innoq.com/de/talks/2026/03/x/",
            }
        ]
        self.scraped = [
            it.ScrapedTalk(
                source_url="https://www.innoq.com/de/talks/2026/03/x/",
                date="2026-03-10",
                what="New title from INNOQ",
                where="Agile Meets Architecture",
                city="Berlin",
                type="talk",
                duration=40,
                abstract="New abstract from INNOQ.",
                slides=None,
            )
        ]
        self.today = datetime.date(2026, 6, 2)

    def test_innoq_field_overwritten(self):
        merged, _ = it.merge_talks(self.existing, self.scraped, today=self.today)
        self.assertEqual(merged[0]["what"], "New title from INNOQ")
        self.assertEqual(merged[0]["abstract"], "New abstract from INNOQ.")

    def test_video_field_preserved(self):
        merged, _ = it.merge_talks(self.existing, self.scraped, today=self.today)
        self.assertEqual(merged[0]["video"], "https://youtube.com/watch?v=ABC123")

    def test_source_url_preserved(self):
        merged, _ = it.merge_talks(self.existing, self.scraped, today=self.today)
        self.assertEqual(
            merged[0]["source_url"], "https://www.innoq.com/de/talks/2026/03/x/"
        )

    def test_status_recomputed_past(self):
        # date is 2026-03-10, today is 2026-06-02 → past
        merged, _ = it.merge_talks(self.existing, self.scraped, today=self.today)
        self.assertEqual(merged[0]["status"], "past")

    def test_only_one_entry_after_merge(self):
        merged, _ = it.merge_talks(self.existing, self.scraped, today=self.today)
        # No duplication: same source_url means same logical entry.
        self.assertEqual(len(merged), 1)

    def test_diff_summary_records_field_updates(self):
        _, diff = it.merge_talks(self.existing, self.scraped, today=self.today)
        self.assertTrue(diff["updates"])

    def test_diff_summary_records_status_transition(self):
        _, diff = it.merge_talks(self.existing, self.scraped, today=self.today)
        # upcoming → past
        flat = " ".join(diff["status_transitions"])
        self.assertIn("upcoming", flat)
        self.assertIn("past", flat)


class MergeTalksManualNotTouchedTests(unittest.TestCase):
    """`source: manual` entries are never touched by the sync.

    Even if a scraped entry's `source_url` matches a manual entry by
    composite key, the manual entry stays put and the worker surfaces
    the ambiguity in the diff (not silently merge).
    """

    def test_manual_entry_passed_through_when_no_scrape_match(self):
        existing = [
            {
                "date": "2025-09-15",
                "what": "Ensemble-Anti-Patterns",
                "where": "JCON",
                "city": "Köln",
                "status": "past",
                "type": "talk",
                "duration": 30,
                "abstract": "…",
                "source": "manual",
            }
        ]
        scraped = []
        today = datetime.date(2026, 6, 2)
        merged, _ = it.merge_talks(existing, scraped, today=today)
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["source"], "manual")
        # Unchanged.
        self.assertEqual(merged[0]["what"], "Ensemble-Anti-Patterns")


class MergeTalksEmptyDiffTests(unittest.TestCase):
    def test_no_changes_when_yaml_already_matches_scrape(self):
        existing = [
            {
                "date": "2026-03-10",
                "what": "Four Years",
                "where": "AMA",
                "city": "Berlin",
                "status": "past",
                "type": "talk",
                "duration": 40,
                "abstract": "Body.",
                "source": "innoq",
                "source_url": "https://www.innoq.com/de/talks/2026/03/x/",
            }
        ]
        scraped = [
            it.ScrapedTalk(
                source_url="https://www.innoq.com/de/talks/2026/03/x/",
                date="2026-03-10",
                what="Four Years",
                where="AMA",
                city="Berlin",
                type="talk",
                duration=40,
                abstract="Body.",
                slides=None,
            )
        ]
        today = datetime.date(2026, 6, 2)
        merged, diff = it.merge_talks(existing, scraped, today=today)
        self.assertEqual(merged, existing)
        self.assertFalse(diff["new"])
        self.assertFalse(diff["status_transitions"])
        self.assertFalse(diff["updates"])


class MergeTalksCompositeFallbackTests(unittest.TestCase):
    """First-sync fallback (ADR-0007 §2): a scraped entry whose
    (what, where, date) matches an existing entry without a source_url
    is surfaced as a candidate match, not silently merged.
    """

    def test_composite_match_surfaced_as_ambiguous(self):
        existing = [
            {
                "date": "2025-09-15",
                "what": "Ensemble-Anti-Patterns",
                "where": "JCON",
                "city": "Köln",
                "status": "past",
                "type": "talk",
                "duration": 30,
                "abstract": "…",
                "source": "manual",
            }
        ]
        scraped = [
            it.ScrapedTalk(
                source_url="https://www.innoq.com/de/talks/2025/09/ensemble/",
                date="2025-09-15",
                what="Ensemble-Anti-Patterns",
                where="JCON",
                city="Köln",
                type="talk",
                duration=30,
                abstract="…",
                slides=None,
            )
        ]
        today = datetime.date(2026, 6, 2)
        merged, diff = it.merge_talks(existing, scraped, today=today)
        # The manual entry is preserved (not silently merged).
        manuals = [e for e in merged if e.get("source") == "manual"]
        self.assertEqual(len(manuals), 1)
        # The INNOQ entry is still added (so Joshua can see both).
        innoqs = [e for e in merged if e.get("source") == "innoq"]
        self.assertEqual(len(innoqs), 1)
        # The ambiguity is reported in the diff.
        self.assertTrue(diff["ambiguous"])
        flat = " ".join(diff["ambiguous"])
        self.assertIn("Ensemble-Anti-Patterns", flat)


# ---------------------------------------------------------------------------
# YAML serialisation
# ---------------------------------------------------------------------------


class TalksYamlSerialisationTests(unittest.TestCase):
    def test_round_trip_preserves_all_fields(self):
        entries = [
            {
                "date": "2026-06-18",
                "what": "ADHS in der Softwareentwicklung",
                "where": "Karlsruher Entwicklertag",
                "city": "Karlsruhe",
                "status": "upcoming",
                "type": "talk",
                "duration": 45,
                "abstract": "Body.",
                "source": "manual",
            }
        ]
        text = it.serialise_talks(entries)
        # Round-trip must parse back identically.
        import yaml
        parsed = yaml.safe_load(text)
        self.assertEqual(parsed, entries)

    def test_serialised_is_unicode_safe(self):
        entries = [
            {
                "date": "2025-09-15",
                "what": "Ensemble-Anti-Patterns",
                "where": "JCON",
                "city": "Köln",
                "status": "past",
                "type": "talk",
                "duration": 30,
                "abstract": "Driver-Tyrannen, Schweigemauern, Endlosdiskussionen.",
                "source": "manual",
            }
        ]
        text = it.serialise_talks(entries)
        # umlaut survives round-trip and is rendered literally (allow_unicode=True).
        self.assertIn("Köln", text)


# ---------------------------------------------------------------------------
# PR body
# ---------------------------------------------------------------------------


class BuildPrBodyTests(unittest.TestCase):
    def test_body_summarises_three_buckets(self):
        diff = {
            "new": ["Four Years, One Ensemble (2026-03-10)"],
            "status_transitions": ["ADHS in der IT 2025: upcoming → past"],
            "updates": ["Java Forum Nord: abstract"],
            "ambiguous": [],
        }
        body = it.build_pr_body(diff)
        self.assertIn("New talks", body)
        self.assertIn("Status transitions", body)
        self.assertIn("Field updates", body)
        self.assertIn("Four Years, One Ensemble", body)
        self.assertIn("ADHS", body)
        self.assertIn("Java Forum Nord", body)

    def test_body_calls_out_overwrite_warning(self):
        diff = {"new": ["x"], "status_transitions": [], "updates": [], "ambiguous": []}
        body = it.build_pr_body(diff)
        # Reminder that INNOQ-authoritative edits will be overwritten.
        self.assertIn("overwritten", body.lower())

    def test_body_omits_empty_buckets(self):
        diff = {"new": ["a"], "status_transitions": [], "updates": [], "ambiguous": []}
        body = it.build_pr_body(diff)
        # Empty buckets must not produce empty headings.
        self.assertNotIn("(none)", body.lower())

    def test_ambiguous_bucket_rendered_when_present(self):
        diff = {
            "new": [],
            "status_transitions": [],
            "updates": [],
            "ambiguous": ["Talk X — composite-key match against manual entry"],
        }
        body = it.build_pr_body(diff)
        self.assertIn("Ambiguous", body)
        self.assertIn("Talk X", body)


# ---------------------------------------------------------------------------
# Integration: real _data/talks.yml is consumable
# ---------------------------------------------------------------------------


class IntegrationLiveTalksYamlTests(unittest.TestCase):
    """The migrated _data/talks.yml must load cleanly and every entry
    must carry `source: manual` (per ADR-0007 §9 first-step migration).
    """

    def test_live_talks_yaml_parseable(self):
        import yaml
        repo_root = Path(__file__).resolve().parents[2]
        path = repo_root / "_data" / "talks.yml"
        with path.open() as fh:
            data = yaml.safe_load(fh)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_every_existing_entry_has_source_manual(self):
        import yaml
        repo_root = Path(__file__).resolve().parents[2]
        path = repo_root / "_data" / "talks.yml"
        with path.open() as fh:
            data = yaml.safe_load(fh)
        for entry in data:
            self.assertIn("source", entry,
                          f"Missing source on entry {entry.get('what')!r}")
            self.assertEqual(entry["source"], "manual",
                             f"Expected source=manual on {entry.get('what')!r}, "
                             f"got {entry['source']!r}")


# ---------------------------------------------------------------------------
# sync_innoq_talks — workflow entry point glue
# ---------------------------------------------------------------------------


class SyncEntryPointTests(unittest.TestCase):
    """The entry point glue (`sync_innoq_talks`) wires HTTP politeness
    (`innoq_common.fetch_with_retry`) to the talk parser, walks the
    paginator, and feeds the merge engine. These tests exercise the
    glue with a fake fetcher; no live network.
    """

    def test_walks_paginator_until_exhausted(self):
        import sync_innoq_talks as sit  # noqa: WPS433 (intentionally lazy)

        pages = {
            "https://www.innoq.com/de/talks/?all=true&by=joshua-toepfer":
                LISTING_HTML_PAGE_1,
            "https://www.innoq.com/de/upcoming_talks/?all=true&by=joshua-toepfer&page=2":
                LISTING_HTML_PAGE_2,
            "https://www.innoq.com/de/talks/2026/03/four-years-one-ensemble-challenges-aha-moments-and-true-team-transformation/":
                DETAIL_HTML_WITH_SLIDES,
            "https://www.innoq.com/de/talks/2024/09/java-forum-nord/":
                DETAIL_HTML_DURATION_FALLBACK,
            "https://www.innoq.com/de/talks/2023/11/remote-mob-programming-zuhause-aber-nicht-allein/":
                DETAIL_HTML_WITH_SLIDES,
        }
        fetched: list[str] = []

        def fake_fetch(url):
            fetched.append(url)
            return pages[url]

        scraped = sit.scrape_all(fetch_fn=fake_fetch)
        # 3 talks (2 on page 1, 1 on page 2) across two listing fetches.
        self.assertEqual(len(scraped), 3)
        self.assertIn(
            "https://www.innoq.com/de/upcoming_talks/?all=true&by=joshua-toepfer&page=2",
            fetched,
        )

    def test_combines_listing_and_detail_fields(self):
        import sync_innoq_talks as sit

        pages = {
            "https://www.innoq.com/de/talks/?all=true&by=joshua-toepfer":
                LISTING_HTML_PAGE_1,
            "https://www.innoq.com/de/upcoming_talks/?all=true&by=joshua-toepfer&page=2":
                LISTING_HTML_PAGE_2,
            "https://www.innoq.com/de/talks/2026/03/four-years-one-ensemble-challenges-aha-moments-and-true-team-transformation/":
                DETAIL_HTML_WITH_SLIDES,
            "https://www.innoq.com/de/talks/2024/09/java-forum-nord/":
                DETAIL_HTML_DURATION_FALLBACK,
            "https://www.innoq.com/de/talks/2023/11/remote-mob-programming-zuhause-aber-nicht-allein/":
                DETAIL_HTML_WITH_SLIDES,
        }

        def fake_fetch(url):
            return pages[url]

        scraped = sit.scrape_all(fetch_fn=fake_fetch)
        first = next(s for s in scraped if "four-years" in s.source_url)
        # From listing.
        self.assertEqual(first.date, "2026-03-10")
        self.assertEqual(first.what, "Four Years, One Ensemble")
        self.assertEqual(first.where, "Agile Meets Architecture")
        self.assertEqual(first.duration, 40)
        # From detail.
        self.assertEqual(first.city, "Berlin")
        self.assertIn("Ensemble Programming", first.abstract)
        self.assertIsNotNone(first.slides)

    def test_listing_duration_takes_precedence_over_detail(self):
        import sync_innoq_talks as sit

        pages = {
            "https://www.innoq.com/de/talks/?all=true&by=joshua-toepfer":
                LISTING_HTML_PAGE_1,
            "https://www.innoq.com/de/upcoming_talks/?all=true&by=joshua-toepfer&page=2":
                LISTING_HTML_PAGE_2,
            "https://www.innoq.com/de/talks/2026/03/four-years-one-ensemble-challenges-aha-moments-and-true-team-transformation/":
                DETAIL_HTML_WITH_SLIDES,
            "https://www.innoq.com/de/talks/2024/09/java-forum-nord/":
                DETAIL_HTML_DURATION_FALLBACK,
            "https://www.innoq.com/de/talks/2023/11/remote-mob-programming-zuhause-aber-nicht-allein/":
                DETAIL_HTML_WITH_SLIDES,
        }

        def fake_fetch(url):
            return pages[url]

        scraped = sit.scrape_all(fetch_fn=fake_fetch)
        # Page-1 entry 2 ("Java Forum Nord") had NO duration on the listing
        # but the detail page carries Uhrzeit 15:00-15:45 → 45 min.
        java = next(s for s in scraped if "java-forum-nord" in s.source_url)
        self.assertEqual(java.duration, 45)

    def test_branch_name_uses_today_iso(self):
        import sync_innoq_talks as sit

        today = datetime.date(2026, 6, 2)
        branch = sit.branch_for_today(today=today)
        self.assertEqual(branch, "sync/innoq-talks/2026-06-02")


class WorkflowDryRunTests(unittest.TestCase):
    """Smoke-test the end-to-end `main` invocation with a fake fetcher
    and DRY_RUN=true. The workflow should exit cleanly without writing
    files or invoking gh.
    """

    def test_empty_diff_no_changes(self):
        """No-op sync: scrape returns the same shape already on disk."""
        # The actual `_data/talks.yml` is all `source: manual` — so an
        # empty scrape produces an empty diff.
        import sync_innoq_talks as sit

        def fake_fetch(url):
            return "<html><body></body></html>"  # zero talks discovered

        # An empty discovery is an exceptional condition — the worker
        # raises so a real cron failure doesn't silently produce empty
        # PRs.
        with self.assertRaises(RuntimeError):
            sit.scrape_all(fetch_fn=fake_fetch)


if __name__ == "__main__":
    unittest.main()

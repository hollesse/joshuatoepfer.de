"""Unit tests for `innoq_common`. Run with: python -m unittest test_innoq_common.

These exercise the pure-Python pieces — URL → slug, frontmatter generation,
HTML → Markdown conversion, dedup-against-_posts, and the filter chain.
Things touching the network (`fetch_feed`) or `gh` (`pr_history_has_branch`)
are exercised separately by the worker via manual smoke tests; they are out
of scope for unit testing.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import innoq_common as ic  # noqa: E402


SAMPLE_ATOM = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>INNOQ</title>
  <id>https://www.innoq.com/de/feed.atom</id>
  <updated>2026-05-26T00:00:00Z</updated>

  <entry>
    <id>https://www.innoq.com/de/articles/2026/05/remote-mob-programming/</id>
    <title>Remote Mob Programming</title>
    <published>2026-05-20T08:00:00Z</published>
    <updated>2026-05-20T08:00:00Z</updated>
    <link rel="alternate" type="text/html" href="https://www.innoq.com/de/articles/2026/05/remote-mob-programming/"/>
    <author>
      <name>Joshua Toepfer</name>
      <email>joshua.toepfer@innoq.com</email>
      <uri>https://www.innoq.com/de/staff/joshua-toepfer/</uri>
    </author>
    <content type="html" xml:lang="de">&lt;h2&gt;Foo&lt;/h2&gt;&lt;p&gt;Bar&lt;/p&gt;&lt;pre&gt;&lt;code class="language-python"&gt;print(1)&lt;/code&gt;&lt;/pre&gt;</content>
  </entry>

  <entry>
    <id>https://www.innoq.com/en/articles/2026/05/round-robin-coding/</id>
    <title>Round-Robin Coding</title>
    <published>2026-05-21T08:00:00Z</published>
    <updated>2026-05-21T08:00:00Z</updated>
    <link rel="alternate" type="text/html" href="https://www.innoq.com/en/articles/2026/05/round-robin-coding/"/>
    <author>
      <name>Joshua Toepfer</name>
      <email>joshua.toepfer@innoq.com</email>
      <uri>https://www.innoq.com/en/staff/joshua-toepfer/</uri>
    </author>
    <content type="html" xml:lang="en">&lt;p&gt;English content&lt;/p&gt;</content>
  </entry>

  <entry>
    <id>https://www.innoq.com/de/talks/2026/05/talk-by-joshua/</id>
    <title>A Talk</title>
    <published>2026-05-22T08:00:00Z</published>
    <updated>2026-05-22T08:00:00Z</updated>
    <link rel="alternate" type="text/html" href="https://www.innoq.com/de/talks/2026/05/talk-by-joshua/"/>
    <author>
      <name>Joshua Toepfer</name>
      <email>joshua.toepfer@innoq.com</email>
    </author>
    <content type="html" xml:lang="de">&lt;p&gt;Slides&lt;/p&gt;</content>
  </entry>

  <entry>
    <id>https://www.innoq.com/de/articles/2026/05/by-someone-else/</id>
    <title>Other Author</title>
    <published>2026-05-23T08:00:00Z</published>
    <updated>2026-05-23T08:00:00Z</updated>
    <link rel="alternate" type="text/html" href="https://www.innoq.com/de/articles/2026/05/by-someone-else/"/>
    <author>
      <name>Stefan Tilkov</name>
      <email>stefan.tilkov@innoq.com</email>
    </author>
    <content type="html" xml:lang="de">&lt;p&gt;Not Joshua&lt;/p&gt;</content>
  </entry>
</feed>
"""


class SlugifyTests(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(
            ic.slugify_url("https://www.innoq.com/de/articles/2023/06/remote-mob-programming/"),
            "remote-mob-programming",
        )

    def test_no_trailing_slash(self):
        self.assertEqual(
            ic.slugify_url("https://www.innoq.com/de/articles/2024/01/foo-bar"),
            "foo-bar",
        )

    def test_with_query(self):
        self.assertEqual(
            ic.slugify_url("https://www.innoq.com/de/articles/2024/01/x/?utm_source=rss"),
            "x",
        )


class HtmlToMarkdownTests(unittest.TestCase):
    def test_heading_atx(self):
        md = ic.convert_html_to_markdown("<h2>Foo</h2><p>Bar</p>")
        self.assertIn("## Foo", md)
        self.assertIn("Bar", md)
        # No Setext underline.
        self.assertNotIn("==", md)

    def test_code_block_language(self):
        html = '<pre><code class="language-python">print(1)</code></pre>'
        md = ic.convert_html_to_markdown(html)
        self.assertIn("```python", md)
        self.assertIn("print(1)", md)

    def test_empty(self):
        self.assertEqual(ic.convert_html_to_markdown(""), "")

    def test_remote_image_preserved(self):
        html = '<img src="https://www.innoq.com/img.png" alt="x">'
        md = ic.convert_html_to_markdown(html)
        self.assertIn("https://www.innoq.com/img.png", md)


class FilterChainTests(unittest.TestCase):
    def _parse(self):
        return ic.parse_feed_entries(SAMPLE_ATOM)

    def test_parse_count(self):
        self.assertEqual(len(self._parse()), 4)

    def test_joshua_german_article_passes(self):
        entries = self._parse()
        passing = [e for e in entries if ic.entry_passes_filter(e)]
        self.assertEqual(len(passing), 1)
        self.assertEqual(
            passing[0].canonical_url,
            "https://www.innoq.com/de/articles/2026/05/remote-mob-programming/",
        )

    def test_english_article_filtered(self):
        en = [
            e for e in self._parse()
            if "round-robin-coding" in e.canonical_url
        ][0]
        reasons = ic.filter_reasons(en)
        self.assertTrue(any("xml:lang" in r for r in reasons))

    def test_talk_filtered(self):
        talk = [
            e for e in self._parse() if "/talks/" in e.canonical_url
        ][0]
        reasons = ic.filter_reasons(talk)
        self.assertTrue(any("/articles/" in r for r in reasons))

    def test_other_author_filtered(self):
        other = [
            e for e in self._parse() if "by-someone-else" in e.canonical_url
        ][0]
        reasons = ic.filter_reasons(other)
        self.assertTrue(any("author email" in r for r in reasons))


class FrontmatterTests(unittest.TestCase):
    def _entry(self) -> ic.FeedEntry:
        entries = ic.parse_feed_entries(SAMPLE_ATOM)
        return [e for e in entries if "remote-mob-programming" in e.canonical_url][0]

    def test_basic_shape(self):
        out = ic.build_post_content(self._entry())
        self.assertTrue(out.startswith("---\n"))
        self.assertIn("source: innoq", out)
        self.assertIn("canonical_url: https://www.innoq.com/de/articles/2026/05/remote-mob-programming/", out)
        self.assertIn("published: false", out)
        self.assertIn("render_with_liquid: false", out)
        self.assertIn("## Foo", out)
        self.assertNotIn("topic:", out)  # blank by default

    def test_preserves_topic_and_published_in_resync(self):
        out = ic.build_post_content(
            self._entry(),
            preserved_meta={"topic": "ensemble", "published": True},
        )
        self.assertIn("topic: ensemble", out)
        self.assertIn("published: true", out)


class PostDirIntegrationTests(unittest.TestCase):
    def test_existing_canonical_urls_scans_posts_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            posts = Path(tmp)
            (posts / "2026-01-01-a.md").write_text(
                "---\ntitle: A\ncanonical_url: https://example.com/a/\n---\nbody\n",
                encoding="utf-8",
            )
            (posts / "2026-01-02-b.md").write_text(
                "---\ntitle: B\n---\nbody\n",
                encoding="utf-8",
            )
            urls = ic.existing_canonical_urls(posts_dir=posts)
            self.assertEqual(urls, {"https://example.com/a/"})

    def test_find_post_by_canonical_url(self):
        with tempfile.TemporaryDirectory() as tmp:
            posts = Path(tmp)
            target = posts / "2026-01-01-a.md"
            target.write_text(
                "---\ntitle: A\ncanonical_url: https://example.com/a/\n---\nbody\n",
                encoding="utf-8",
            )
            found = ic.find_post_by_canonical_url("https://example.com/a/", posts_dir=posts)
            self.assertEqual(found, target)
            missing = ic.find_post_by_canonical_url("https://example.com/b/", posts_dir=posts)
            self.assertIsNone(missing)

    def test_read_existing_post_meta_returns_topic_and_published(self):
        with tempfile.TemporaryDirectory() as tmp:
            file_path = Path(tmp) / "post.md"
            file_path.write_text(
                "---\ntitle: X\ntopic: ensemble\npublished: true\n---\nbody\n",
                encoding="utf-8",
            )
            meta = ic.read_existing_post_meta(file_path)
            self.assertEqual(meta, {"topic": "ensemble", "published": True})


class ForceResyncInputTests(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(ic.split_force_resync_input(""), [])
        self.assertEqual(ic.split_force_resync_input(None), [])

    def test_single(self):
        self.assertEqual(
            ic.split_force_resync_input("https://www.innoq.com/de/articles/x/"),
            ["https://www.innoq.com/de/articles/x/"],
        )

    def test_multiple_with_whitespace(self):
        self.assertEqual(
            ic.split_force_resync_input(" a , b , c "),
            ["a", "b", "c"],
        )


class BranchNameTests(unittest.TestCase):
    def test_normal_branch(self):
        entries = ic.parse_feed_entries(SAMPLE_ATOM)
        e = [x for x in entries if "remote-mob-programming" in x.canonical_url][0]
        self.assertEqual(e.branch_name, "sync/innoq/remote-mob-programming")

    def test_resync_branch_has_timestamp(self):
        entries = ic.parse_feed_entries(SAMPLE_ATOM)
        e = [x for x in entries if "remote-mob-programming" in x.canonical_url][0]
        self.assertEqual(
            e.resync_branch_name("20260527T120000Z"),
            "sync/innoq/remote-mob-programming-resync-20260527T120000Z",
        )


# ---------------------------------------------------------------------------
# Backfill-specific helpers (infra-005)
# ---------------------------------------------------------------------------


class ScrapedArticleTests(unittest.TestCase):
    """ScrapedArticle is the scrape-mode analogue of FeedEntry.

    It must work with `build_post_content` and `build_pr_body` (which used
    to accept `FeedEntry`) and expose `slug` / `post_filename` /
    `backfill_branch_name`.
    """

    def _article(self) -> "ic.ScrapedArticle":
        return ic.ScrapedArticle(
            title="Remote Mob Programming",
            canonical_url="https://www.innoq.com/de/articles/2023/06/remote-mob-programming/",
            published_date="2023-06-23",
            content_html="<h2>Foo</h2><p>Bar</p>",
        )

    def test_slug_derived_from_url(self):
        self.assertEqual(self._article().slug, "remote-mob-programming")

    def test_post_filename(self):
        self.assertEqual(
            self._article().post_filename,
            "2023-06-23-remote-mob-programming.md",
        )

    def test_backfill_branch_name(self):
        self.assertEqual(
            self._article().backfill_branch_name,
            "backfill/innoq/remote-mob-programming",
        )

    def test_branch_prefix_distinct_from_sync(self):
        self.assertNotEqual(
            self._article().backfill_branch_name.split("/")[0],
            "sync",
        )

    def test_build_post_content_with_scraped_article(self):
        out = ic.build_post_content(self._article())
        self.assertTrue(out.startswith("---\n"))
        self.assertIn("source: innoq", out)
        self.assertIn(
            "canonical_url: https://www.innoq.com/de/articles/2023/06/remote-mob-programming/",
            out,
        )
        self.assertIn("published: false", out)
        self.assertIn("render_with_liquid: false", out)
        self.assertIn("title: Remote Mob Programming", out)
        # PyYAML quotes ambiguous-looking strings — same shape as the
        # feed-side serialisation.
        self.assertIn("2023-06-23", out)
        self.assertIn("## Foo", out)
        self.assertNotIn("topic:", out)

    def test_write_post_file_with_scraped_article(self):
        with tempfile.TemporaryDirectory() as tmp:
            posts = Path(tmp)
            path = ic.write_post_file(self._article(), posts_dir=posts)
            self.assertEqual(path.name, "2023-06-23-remote-mob-programming.md")
            text = path.read_text(encoding="utf-8")
            self.assertIn("source: innoq", text)
            self.assertIn("## Foo", text)


class BackfillPrTextTests(unittest.TestCase):
    def _article(self) -> "ic.ScrapedArticle":
        return ic.ScrapedArticle(
            title="Remote Mob Programming",
            canonical_url="https://www.innoq.com/de/articles/2023/06/remote-mob-programming/",
            published_date="2023-06-23",
            content_html="<p>x</p>",
        )

    def test_backfill_pr_title_uses_backfill_prefix(self):
        self.assertEqual(
            ic.build_backfill_pr_title(self._article()),
            "Backfill: Remote Mob Programming [innoq.com]",
        )

    def test_backfill_pr_body_mentions_backfill(self):
        body = ic.build_backfill_pr_body(self._article())
        self.assertIn("Backfill", body)
        self.assertIn(self._article().canonical_url, body)
        self.assertIn("published: false", body)
        # Two-step publish guidance must be present so the PR is self-explanatory.
        self.assertIn("topic", body)


class SrcsetTests(unittest.TestCase):
    def test_picks_largest_width(self):
        srcset = (
            "https://res.cloudinary.com/innoq/image/upload/w_400/foo.jpg 400w, "
            "https://res.cloudinary.com/innoq/image/upload/w_1200/foo.jpg 1200w, "
            "https://res.cloudinary.com/innoq/image/upload/w_800/foo.jpg 800w"
        )
        self.assertEqual(
            ic.largest_src_from_srcset(srcset),
            "https://res.cloudinary.com/innoq/image/upload/w_1200/foo.jpg",
        )

    def test_single_entry_no_descriptor(self):
        self.assertEqual(
            ic.largest_src_from_srcset("https://example.com/x.png"),
            "https://example.com/x.png",
        )

    def test_empty_returns_empty(self):
        self.assertEqual(ic.largest_src_from_srcset(""), "")
        self.assertEqual(ic.largest_src_from_srcset(None), "")

    def test_density_descriptor_falls_back_first(self):
        # `2x` descriptors aren't width-comparable; we just pick the first.
        srcset = "https://example.com/a.png 1x, https://example.com/b.png 2x"
        out = ic.largest_src_from_srcset(srcset)
        self.assertTrue(out.startswith("https://example.com/"))


class GermanDateTests(unittest.TestCase):
    def test_full_german_date(self):
        self.assertEqual(ic.parse_german_date("23. Juni 2023"), "2023-06-23")

    def test_single_digit_day(self):
        self.assertEqual(ic.parse_german_date("3. Mai 2021"), "2021-05-03")

    def test_with_surrounding_text(self):
        self.assertEqual(
            ic.parse_german_date("Veröffentlicht am 19. Januar 2021."),
            "2021-01-19",
        )

    def test_unparseable_returns_none(self):
        self.assertIsNone(ic.parse_german_date("not a date"))
        self.assertIsNone(ic.parse_german_date(""))
        self.assertIsNone(ic.parse_german_date(None))


class UrlListInputTests(unittest.TestCase):
    """`split_url_list_input` is the backfill-mode equivalent of
    `split_force_resync_input`. Same parsing rules — name aliased for
    readability in the backfill entry point.
    """

    def test_empty(self):
        self.assertEqual(ic.split_url_list_input(""), [])
        self.assertEqual(ic.split_url_list_input(None), [])

    def test_multiple(self):
        self.assertEqual(
            ic.split_url_list_input(" https://a/ , https://b/ "),
            ["https://a/", "https://b/"],
        )


class BackfillBranchPrefixTests(unittest.TestCase):
    def test_constant_value(self):
        self.assertEqual(ic.BACKFILL_BRANCH_PREFIX, "backfill/innoq")


if __name__ == "__main__":
    unittest.main()

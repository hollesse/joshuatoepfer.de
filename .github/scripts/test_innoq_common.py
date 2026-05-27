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


if __name__ == "__main__":
    unittest.main()

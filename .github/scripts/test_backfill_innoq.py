"""Unit tests for `backfill_innoq` pure-function pieces.

These cover the scrape-time HTML transformations: listing-page link
extraction, article-page metadata extraction, body element stripping, and
the srcset → src promotion before markdownify conversion. Anything that
touches the live INNOQ network or the `gh` CLI is out of scope (manual
smoke-test territory, same policy as `test_innoq_common.py`).
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent))

import backfill_innoq as bf  # noqa: E402


LISTING_HTML = """
<html><body>
  <main>
    <ul>
      <li><a href="/de/articles/2023/06/remote-mob-programming/"><h3>Remote Mob Programming</h3></a></li>
      <li><a href="/de/articles/2022/12/typist-wechsel-dich/"><h3>Typist wechsel dich</h3></a></li>
      <li><a href="/de/articles/2021/01/remote-mob-programming-bei-innoq/"><h3>Remote Mob Programming bei INNOQ</h3></a></li>
      <!-- noise: not an /articles/ link -->
      <li><a href="/de/staff/joshua-toepfer/"><h3>Profile</h3></a></li>
      <!-- duplicate of the first article -->
      <li><a href="/de/articles/2023/06/remote-mob-programming/"><h3>Repeat</h3></a></li>
    </ul>
  </main>
</body></html>
"""


ARTICLE_HTML = """
<html>
<head>
  <title>Remote Mob Programming – INNOQ</title>
  <meta property="og:title" content="Remote Mob Programming">
  <meta property="og:url" content="https://www.innoq.com/de/articles/2023/06/remote-mob-programming/">
  <link rel="canonical" href="https://shop.example.com/external-canonical/">
</head>
<body>
  <header>
    <time datetime="2023-06-23" class="standard-header__intro__label">23. Juni 2023</time>
    <h1>Remote Mob Programming</h1>
  </header>
  <article class="article-page-default">
    <section class="author-section">
      <h2>Über den Autor</h2>
      <p>Joshua Toepfer is a consultant.</p>
    </section>
    <aside class="toc">
      <h2>Inhalt</h2>
      <ul><li><a href="#x">Section</a></li></ul>
    </aside>
    <div class="content">
      <h2>Einleitung</h2>
      <p>Erster Absatz.</p>
      <p>
        <img alt="Diagram"
             srcset="https://res.cloudinary.com/innoq/upload/w_400/x.png 400w,
                     https://res.cloudinary.com/innoq/upload/w_1200/x.png 1200w,
                     https://res.cloudinary.com/innoq/upload/w_800/x.png 800w">
      </p>
      <form>Newsletter signup goes here</form>
      <footer><p>tags etc.</p></footer>
      <div class="share-icons">Share!</div>
    </div>
  </article>
  <aside>Sidebar that should not be picked up because it is outside &lt;article&gt;.</aside>
</body>
</html>
"""


ARTICLE_HTML_NO_OG = """
<html>
<head>
  <title>Some Title – INNOQ</title>
</head>
<body>
  <article class="article-page-default">
    <div class="content">
      <h2>Heading</h2>
      <p>Body.</p>
    </div>
  </article>
</body>
</html>
"""


ARTICLE_HTML_NO_DATE_META = """
<html>
<head>
  <meta property="og:title" content="Sample">
</head>
<body>
  <header>
    <p class="standard-header__intro__label">19. Januar 2021</p>
  </header>
  <article class="article-page-default">
    <div class="content"><p>Body.</p></div>
  </article>
</body>
</html>
"""


class DiscoverListingUrlsTests(unittest.TestCase):
    def test_extracts_article_urls_only(self):
        urls = bf.discover_urls_from_listing(LISTING_HTML)
        self.assertIn("https://www.innoq.com/de/articles/2023/06/remote-mob-programming/", urls)
        self.assertIn("https://www.innoq.com/de/articles/2022/12/typist-wechsel-dich/", urls)
        self.assertIn("https://www.innoq.com/de/articles/2021/01/remote-mob-programming-bei-innoq/", urls)

    def test_excludes_non_article_links(self):
        urls = bf.discover_urls_from_listing(LISTING_HTML)
        self.assertFalse(any("/staff/" in u for u in urls))

    def test_dedups_identical_urls(self):
        urls = bf.discover_urls_from_listing(LISTING_HTML)
        # 4 unique /articles/ links (the listing has 3 distinct + 1 duplicate)
        article_urls = [u for u in urls if "/articles/" in u]
        self.assertEqual(len(article_urls), len(set(article_urls)))
        self.assertEqual(len(article_urls), 3)

    def test_urls_are_absolute(self):
        urls = bf.discover_urls_from_listing(LISTING_HTML)
        for u in urls:
            self.assertTrue(u.startswith("https://www.innoq.com/"))


class ExtractMetadataTests(unittest.TestCase):
    def test_title_from_og(self):
        meta = bf.extract_article_metadata(
            ARTICLE_HTML,
            fetched_url="https://www.innoq.com/de/articles/2023/06/remote-mob-programming/",
        )
        self.assertEqual(meta["title"], "Remote Mob Programming")

    def test_canonical_url_falls_back_to_fetched_url(self):
        """`<link rel=canonical>` may point at the print-magazine source
        (verified on 2023/06 article during the curl spike). The fetched
        URL is always the correct INNOQ canonical."""
        meta = bf.extract_article_metadata(
            ARTICLE_HTML,
            fetched_url="https://www.innoq.com/de/articles/2023/06/remote-mob-programming/",
        )
        self.assertEqual(
            meta["canonical_url"],
            "https://www.innoq.com/de/articles/2023/06/remote-mob-programming/",
        )
        self.assertNotIn("shop.example.com", meta["canonical_url"])

    def test_date_from_time_datetime(self):
        meta = bf.extract_article_metadata(
            ARTICLE_HTML,
            fetched_url="https://www.innoq.com/de/articles/2023/06/remote-mob-programming/",
        )
        self.assertEqual(meta["published_date"], "2023-06-23")

    def test_date_german_fallback(self):
        meta = bf.extract_article_metadata(
            ARTICLE_HTML_NO_DATE_META,
            fetched_url="https://www.innoq.com/de/articles/2021/01/x/",
        )
        self.assertEqual(meta["published_date"], "2021-01-19")

    def test_date_url_fallback_when_nothing_else(self):
        html = "<html><head><title>x</title></head><body><article class='article-page-default'><div class='content'><p>x</p></div></article></body></html>"
        meta = bf.extract_article_metadata(
            html,
            fetched_url="https://www.innoq.com/de/articles/2024/03/some-slug/",
        )
        self.assertEqual(meta["published_date"], "2024-03-01")

    def test_title_fallback_to_stripped_html_title(self):
        meta = bf.extract_article_metadata(
            ARTICLE_HTML_NO_OG,
            fetched_url="https://www.innoq.com/de/articles/2024/01/x/",
        )
        # ` – INNOQ` suffix stripped.
        self.assertEqual(meta["title"], "Some Title")


class StripArticleBodyTests(unittest.TestCase):
    def test_author_section_stripped(self):
        body_html = bf.extract_article_body(ARTICLE_HTML)
        self.assertNotIn("Über den Autor", body_html)
        self.assertNotIn("author-section", body_html)

    def test_toc_aside_stripped(self):
        body_html = bf.extract_article_body(ARTICLE_HTML)
        self.assertNotIn("Inhalt", body_html)
        self.assertNotIn("toc", body_html)

    def test_newsletter_form_stripped(self):
        body_html = bf.extract_article_body(ARTICLE_HTML)
        self.assertNotIn("Newsletter", body_html)

    def test_footer_stripped(self):
        body_html = bf.extract_article_body(ARTICLE_HTML)
        self.assertNotIn("tags etc.", body_html)

    def test_share_icons_stripped(self):
        body_html = bf.extract_article_body(ARTICLE_HTML)
        self.assertNotIn("Share!", body_html)

    def test_content_div_kept(self):
        body_html = bf.extract_article_body(ARTICLE_HTML)
        self.assertIn("Erster Absatz", body_html)
        self.assertIn("Einleitung", body_html)

    def test_outside_article_not_included(self):
        body_html = bf.extract_article_body(ARTICLE_HTML)
        self.assertNotIn("Sidebar that should not be picked up", body_html)

    def test_srcset_promoted_to_src(self):
        """Cloudinary `<img>` tags carry only `srcset`. The largest-width
        URL must be materialised as `src` so markdownify emits a valid
        Markdown image."""
        body_html = bf.extract_article_body(ARTICLE_HTML)
        # Largest descriptor in the fixture is 1200w.
        self.assertIn("https://res.cloudinary.com/innoq/upload/w_1200/x.png", body_html)
        # And that URL is now visible to markdownify via a src attribute.
        self.assertIn('src="https://res.cloudinary.com/innoq/upload/w_1200/x.png"', body_html)


class BuildArticleTests(unittest.TestCase):
    """End-to-end: HTML → ScrapedArticle ready for post-content assembly."""

    def test_returns_scraped_article(self):
        from innoq_common import ScrapedArticle

        article = bf.build_scraped_article(
            ARTICLE_HTML,
            fetched_url="https://www.innoq.com/de/articles/2023/06/remote-mob-programming/",
        )
        self.assertIsInstance(article, ScrapedArticle)
        self.assertEqual(article.title, "Remote Mob Programming")
        self.assertEqual(article.published_date, "2023-06-23")
        self.assertEqual(
            article.canonical_url,
            "https://www.innoq.com/de/articles/2023/06/remote-mob-programming/",
        )
        # Strip removed author-bio + toc, kept the content div.
        self.assertIn("Erster Absatz", article.content_html)
        self.assertNotIn("Über den Autor", article.content_html)

    def test_empty_body_raises(self):
        empty = "<html><head><title>x</title></head><body><article class='article-page-default'></article></body></html>"
        with self.assertRaises(RuntimeError):
            bf.build_scraped_article(
                empty,
                fetched_url="https://www.innoq.com/de/articles/2024/01/x/",
            )


class GuardArticleUrlTests(unittest.TestCase):
    """The backfill must reject non-DE-article URLs even when given via
    the `urls` input — defensive in case Joshua pastes the wrong link."""

    def test_accepts_de_article(self):
        bf.guard_article_url("https://www.innoq.com/de/articles/2023/06/x/")

    def test_rejects_english(self):
        with self.assertRaises(ValueError):
            bf.guard_article_url("https://www.innoq.com/en/articles/2023/06/x/")

    def test_rejects_non_articles(self):
        with self.assertRaises(ValueError):
            bf.guard_article_url("https://www.innoq.com/de/talks/x/")

    def test_rejects_off_domain(self):
        with self.assertRaises(ValueError):
            bf.guard_article_url("https://example.com/de/articles/2023/06/x/")


class BuildPlanDedupBypassTests(unittest.TestCase):
    """URL-list mode (infra-007) skips both dedup checks. Auto-discovery
    mode still applies them. These tests cover the bypass semantic without
    touching the live network or the `gh` CLI."""

    URL = "https://www.innoq.com/de/articles/2023/06/remote-mob-programming/"

    def _fake_fetch(self, _url: str) -> str:
        return ARTICLE_HTML

    def test_url_list_mode_bypasses_existing_posts_check(self):
        """URL already present in `_posts/*.md` is still planned when
        bypass_dedup=True. (Without the bypass it would be skipped with
        reason `already-in-posts`.)"""
        seen = {self.URL}
        with mock.patch.object(bf, "existing_canonical_urls", return_value=seen), \
             mock.patch.object(bf, "pr_history_has_branch", return_value=False):
            plan, skips = bf.build_plan(
                [self.URL],
                fetch_fn=self._fake_fetch,
                bypass_dedup=True,
            )
        self.assertEqual(len(plan), 1)
        self.assertEqual(plan[0]["canonical_url"], self.URL)
        self.assertEqual(skips, [])

    def test_url_list_mode_bypasses_pr_history_check(self):
        """Closed-PR record for `backfill/innoq/<slug>` does not block a
        URL-list-mode re-process. (Without the bypass it would be skipped
        with reason `pr-history`.)"""
        with mock.patch.object(bf, "existing_canonical_urls", return_value=set()), \
             mock.patch.object(bf, "pr_history_has_branch", return_value=True) as pr_mock:
            plan, skips = bf.build_plan(
                [self.URL],
                fetch_fn=self._fake_fetch,
                bypass_dedup=True,
            )
        self.assertEqual(len(plan), 1)
        self.assertEqual(plan[0]["canonical_url"], self.URL)
        self.assertEqual(skips, [])
        # And the dedup helpers should never have been called in bypass mode.
        pr_mock.assert_not_called()

    def test_auto_discovery_mode_still_dedups_against_existing_posts(self):
        """Regression guard for infra-007: bypass_dedup defaults to False,
        and at that default the `existing_canonical_urls` check still
        skips known URLs (byte-identical to pre-infra-007 behaviour)."""
        seen = {self.URL}
        with mock.patch.object(bf, "existing_canonical_urls", return_value=seen), \
             mock.patch.object(bf, "pr_history_has_branch", return_value=False):
            plan, skips = bf.build_plan(
                [self.URL],
                fetch_fn=self._fake_fetch,
            )
        self.assertEqual(plan, [])
        self.assertEqual(len(skips), 1)
        self.assertEqual(skips[0]["reason"], "already-in-posts")

    def test_auto_discovery_mode_still_dedups_against_pr_history(self):
        """Regression guard: with bypass_dedup=False, pr_history_has_branch
        match still blocks the URL."""
        with mock.patch.object(bf, "existing_canonical_urls", return_value=set()), \
             mock.patch.object(bf, "pr_history_has_branch", return_value=True):
            plan, skips = bf.build_plan(
                [self.URL],
                fetch_fn=self._fake_fetch,
            )
        self.assertEqual(plan, [])
        self.assertEqual(len(skips), 1)
        self.assertEqual(skips[0]["reason"], "pr-history")


if __name__ == "__main__":
    unittest.main()

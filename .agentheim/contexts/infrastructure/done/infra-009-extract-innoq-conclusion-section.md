---
id: infra-009
title: "Extract INNOQ `<section class=\"conclusion\">` Fazit into synced body"
status: done
type: bug
context: infrastructure
created: 2026-06-02
completed: 2026-06-02
commit:
depends_on: [infra-005]
blocks: []
tags: [sync, innoq, conversion, fazit, conclusion, body-extraction]
related_adrs: [0006]
related_research: []
prior_art: [infra-005, infra-008]
---

## Why
The 2022 "Typist wechsel dich" backfill PR is missing its **Fazit
section** entirely. Joshua noticed when comparing against the INNOQ
original: the Fazit on innoq.com is "etwas anders hervorgehoben"
(styled differently from regular sections), which led to it being
excluded from the conversion.

Inspection of the INNOQ HTML confirms why. The conclusion lives in a
**separate `<section>` sibling of `<article>`**, not inside the
article wrapper:

```html
<main>
  <article>…the article body…</article>
  <section class="conclusion">
    <div class="conclusion-wrapper">
      <h2 class="conclusion-headline">Fazit</h2>
      <h3 class="conclusion-subheadline">(may be empty)</h3>
      <div class="conclusion-text">Das mob-Tool ist ein einfacher
      Helfer …</div>
    </div>
  </section>
</main>
```

Our backfill scraper (`backfill_innoq.py`) and the shared converter
(`innoq_common.py`) only extract content from `<article>`. The
`<section class="conclusion">` block is silently ignored.

This is an INNOQ-side template variation across years:
- 2021 "Remote Mob Programming bei INNOQ" — Fazit was inside
  `<article>` (no issue, captured correctly)
- 2022 "Typist wechsel dich" — Fazit in separate
  `<section class="conclusion">` (BUG: dropped)
- 2023 "Remote Mob Programming" — Fazit inside `<article>` (no issue,
  captured)

Both layouts will continue to appear in future INNOQ articles. The
converter needs to handle both.

## What
In the body extraction step in `innoq_common.py` (or
`backfill_innoq.py` if that's where the extraction lives — worker
checks), after finding `<article>`:

1. Look for a sibling `<section class="conclusion">` element under
   the same `<main>` parent.
2. If found, append its inner content (specifically the
   `<div class="conclusion-wrapper">` or equivalent) to the
   extracted-body BeautifulSoup tree before passing to the strip
   pipeline.
3. The strip pipeline already runs (newsletter, author-bio,
   "Weitere Informationen", footer, share icons). Make sure it
   doesn't accidentally eat the conclusion text. The
   `<h2 class="conclusion-headline">Fazit</h2>` should land
   verbatim in the output (heading promotion's "leave H2 untouched"
   rule is the right one here).
4. **Strip empty headings.** The `<h3 class="conclusion-subheadline">`
   in the 2022 article was empty. After our infra-008 H3→H2 promotion,
   it'd render as an empty H2. Add a small strip step that removes
   any heading element with no text content (`tag.get_text(strip=True)
   == ""`). This is generally useful, not just for the conclusion.
5. The same fix applies to **both** the feed-poll workflow
   (`sync-innoq`) and the backfill workflow (`backfill-innoq`)
   because the conversion lives in the shared `innoq_common.py`. The
   feed entries also link to the article page, so it's possible
   future feed-discovered articles use the same template — defensive
   to fix it once for both paths.

## Acceptance criteria

- [ ] `innoq_common.py`'s body extraction (or the appropriate
      function — worker picks based on actual code structure)
      finds `<section class="conclusion">` as a sibling of
      `<article>` under `<main>` and merges its content into the
      extracted body.
- [ ] When the conclusion section is absent (e.g. 2021 + 2023
      articles), behavior is unchanged.
- [ ] After conversion of the 2022 article, the Markdown body
      ends with the Fazit content: `## Fazit` heading followed by
      "Das mob-Tool ist ein einfacher Helfer …" paragraph.
- [ ] Empty headings (heading element with no non-whitespace text)
      are stripped from the body during the strip pipeline. This
      handles the empty `<h3 class="conclusion-subheadline">` case
      and is generally defensive.
- [ ] New tests in `HeadingPromotionTests` or a new
      `ConclusionSectionTests` class in `test_innoq_common.py`:
      - **test_conclusion_section_appended**: input has `<article>`
        + `<section class="conclusion"><h2>Fazit</h2><div>Text</div></section>`
        → Markdown output contains `## Fazit` and `Text`.
      - **test_no_conclusion_section_unchanged**: input has only
        `<article>` (no separate conclusion section) → output is
        as before.
      - **test_empty_heading_stripped**: input has `<article><h3></h3></article>`
        → Markdown output does NOT contain a heading marker for
        the empty H3.
      - **test_conclusion_subheadline_promoted_or_stripped**: input
        has the full 2022 shape (h2=Fazit, empty h3=subheadline,
        div text) → output has `## Fazit` and the text, NO empty
        H2 or H3.
- [ ] All previous tests pass (77 from infra-008 baseline).
- [ ] `bundle exec jekyll build` still passes.
- [ ] `infrastructure/README.md`'s Sync/Backfill workflow section
      gets a one-sentence note about the conclusion-section
      extraction.

## Notes
- This is a template-discovery bug, not an ADR-level decision. No
  new ADR.
- After ship, Joshua re-runs Backfill for the 2022 article via
  `urls: https://www.innoq.com/de/articles/2022/12/typist-wechsel-dich-remote-edition-code-uebergabe-mit-dem-mob-tool/`
  (URL-list mode bypasses dedup per infra-007). Fresh PR with the
  Fazit included; merge, editorial cleanup, publish.
- The 2021 article was already converted (with Fazit inside
  `<article>` per its template). No re-conversion needed for 2021.
- The 2023 article was re-converted yesterday with infra-008's
  heading promotion. Also no re-conversion needed.
- Empty-heading stripping is a generally useful defensive step. It
  protects against ANY future INNOQ template that includes a heading
  element as a styling hook with no text content.
- Implementation hint: with BeautifulSoup,
  `article.parent.find('section', class_='conclusion')` finds the
  sibling. The merge step can append it to the article element:
  `article.append(conclusion.div_or_whatever)`. Worker picks the
  cleanest implementation.

## Outcome

Two cleanup steps wired into the INNOQ HTML→Markdown pipeline:

1. **Conclusion-section merge** lives in two places by design:
   - `innoq_common._merge_conclusion_section(html)` — called from
     `convert_html_to_markdown` so any caller passing full-document
     HTML containing `<main><article>…</article><section class="conclusion">…</section></main>`
     gets the merge for free. Pre-filtered by a cheap `"conclusion" in html`
     check to avoid full BS4 reparses on the common no-Fazit-section
     case.
   - `backfill_innoq._merge_sibling_conclusion(article)` — invoked
     inside `extract_article_body` before the strip pipeline, so the
     conclusion content becomes part of `article.decode_contents()`.
     This is where the 2022 article fix actually lands (backfill is
     the only path that scrapes the live page; sync uses the Atom
     `<content>` HTML which doesn't include sibling sections).

2. **Empty-heading strip** added as `innoq_common._strip_empty_headings`
   and chained after `_promote_heading_levels` in `convert_html_to_markdown`.
   Removes any `<h1>`–`<h6>` whose `get_text(strip=True)` is empty —
   defensive against INNOQ's empty `conclusion-subheadline` and any
   future template-only heading hooks.

Pipeline order in `convert_html_to_markdown`:
`_merge_conclusion_section` → `_promote_heading_levels` →
`_strip_empty_headings` → markdownify.

**Tests:** +5 in `test_innoq_common.py` (new `ConclusionSectionTests`
class covering merge, no-section pass-through, empty H2 strip, empty H3
strip after promotion, and the full 2022 template shape). +4 in
`test_backfill_innoq.py` (new `ConclusionMergeTests` exercising
`extract_article_body` against an `ARTICLE_HTML_WITH_SIBLING_CONCLUSION`
fixture; one end-to-end round-trip through `convert_html_to_markdown`).
Test count: **77 → 86 (+9)**. `bundle exec jekyll build` clean.

**Edge case observed:** `extract_article_body` looks up the sibling
section with `parent.find("section", class_="conclusion", recursive=False)`
— restricted to direct children of `<main>` — so a stray
`conclusion`-classed section nested deeper inside the article would not
be mistakenly merged twice or moved out of place. The
`innoq_common`-side helper uses `previous_siblings` / `next_siblings`
inspection for the same reason.

**Files of interest:**
- `.github/scripts/innoq_common.py` — `_merge_conclusion_section`,
  `_find_sibling_article`, `_strip_empty_headings`,
  `convert_html_to_markdown` (docstring + pipeline).
- `.github/scripts/backfill_innoq.py` — `extract_article_body`,
  `_merge_sibling_conclusion`.
- `.github/scripts/test_innoq_common.py` — `ConclusionSectionTests`.
- `.github/scripts/test_backfill_innoq.py` —
  `ARTICLE_HTML_WITH_SIBLING_CONCLUSION` fixture, `ConclusionMergeTests`.
- `.agentheim/contexts/infrastructure/README.md` — added
  "Conclusion-section merge" paragraph to the Sync-workflow section.

**Post-ship action for Joshua:** re-run the Backfill workflow with
`urls: https://www.innoq.com/de/articles/2022/12/typist-wechsel-dich-remote-edition-code-uebergabe-mit-dem-mob-tool/`
(URL-list mode bypasses dedup per infra-007). Fresh PR will include
the Fazit; merge, editorial cleanup, publish.

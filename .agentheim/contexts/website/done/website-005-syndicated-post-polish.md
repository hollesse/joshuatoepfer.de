---
id: website-005
title: "Syndicated post polish: visible source link at end + working TOC"
status: done
type: bug
context: website
created: 2026-06-01
completed: 2026-06-01
commit:
depends_on: []
blocks: []
tags: [post-layout, toc, syndicated, canonical, polish]
related_adrs: [0005]
related_research: []
prior_art: [website-002, website-003]
---

## Why
The first real INNOQ-synced post landed live today (2023-06-23
"Remote Mob Programming", commit pre-this-task). Joshua immediately
spotted two UX issues at `https://joshuatoepfer.de/posts/2023/06/23/remote-mob-programming/`:

1. **No visible link back to innoq.com at the end of the post.** The
   `canonical_url` is in `<head>` (good for SEO via
   `_includes/head-canonical.html`) and the post-hero `.meta-line`
   shows "↗ Erscheint auch auf innoq.com" at the top. But a reader
   who's finished reading and wants to go to the original gets no
   visible cta. Syndicated-post convention is to repeat the canonical
   link near the bottom of the body.

2. **TOC aside is empty.** The `<aside class="post-toc">` renders with
   only the static fallback "Zum Anfang" link — never any actual
   section headings. Root cause: `assets/js/theme-toggle.js:44` scans
   `body.querySelectorAll("h2")`, but INNOQ articles use H3 for
   section headings (because their H1=title sits in the post hero,
   H2=subtitle is absent for this article, H3=sections). 0 H2s →
   empty list.

## What
Two changes, one task:

### 1. Visible source link at end of `.post-body`

In `_layouts/post.html`, conditional on `page.source` being set,
render a small "Original auf innoq.com" link block just before the
post-pager (so it sits AFTER the article body but BEFORE the prev/next
navigation). Suggested markup:

```liquid
{% if page.source %}
  <aside class="post-source mono" aria-label="Quelle">
    ↗ Ursprünglich erschienen auf
    <a href="{{ page.canonical_url }}" class="link" rel="canonical">
      {{ page.source }}.com
    </a>.
  </aside>
{% endif %}
```

Wording is German because the site is German. Use `.mono` (Geist Mono
utility per ADR-0005) for type, `.link` (animated underline per
ADR-0005's link convention) for the anchor. The arrow `↗` matches the
arrow already in the post-hero meta-line — same visual vocabulary,
top + bottom symmetry.

Add a small SCSS rule to `_sass/_layout.scss` (or `_sass/_posts.scss`,
worker's call) for `.post-source`: top rule (`border-top: 1px solid
var(--rule)`), margin above (~32px), padding-top (~16px). No fancy
styling — should feel like a quiet footnote, not a banner.

### 2. TOC populates for H3-bearing posts

Pick one of two clean fixes; worker decides based on what they think
ages better. **Document the choice in the task Outcome.**

- **Option A (simpler):** Update `assets/js/theme-toggle.js` to scan
  both H2 and H3: `body.querySelectorAll("h2, h3")`. Optionally
  indent H3 entries below preceding H2s — but since INNOQ articles
  don't have H2s anyway, flat indentation is fine for now. **Works
  for any post going forward**; no conversion logic change needed.

- **Option B (more invasive but semantically truer):** Promote `<h3>`
  to `<h2>` during INNOQ syndication in `.github/scripts/innoq_common.py`
  (`convert_html_to_markdown` or post-conversion hook). Rationale:
  INNOQ's H1=title sits in our hero, their H2=subtitle goes into
  frontmatter `subtitle` (currently empty for this article — but
  would be the home for one if present), so their H3=sections
  semantically maps to our H2=sections. TOC scanner stays at H2-only.

  Side-effect to consider: any future INNOQ article whose body
  genuinely uses h4/h5/h6 would also need promotion. Worker can
  decide whether to handle that bridge if/when it appears.

My recommendation (Joshua's preference unconfirmed): **Option A.**
Smaller, more local change. Robust against any source-format
quirks across articles. Doesn't entangle conversion logic with
TOC display logic.

If the worker picks A: re-test the live 2023 post — TOC should now
list all 7 H3 section headings.

If the worker picks B: re-trigger backfill for the 2023 article
(URL-list mode bypasses dedup since infra-007). New PR will have
H2 section headings; merge that to see TOC work.

## Acceptance criteria

- [ ] `_layouts/post.html`: a `.post-source` block renders ONLY when
      `page.source` is non-empty, positioned **after** `.post-body` and
      **before** the `.post-pager` (prev/next navigation).
- [ ] The block links to `page.canonical_url` with `rel="canonical"`
      and includes the source name (e.g. "innoq.com").
- [ ] Wording is German. Suggested copy: "↗ Ursprünglich erschienen
      auf innoq.com." — worker may adjust slightly for clarity.
- [ ] `.post-source` is styled (top-rule, modest spacing) so it reads
      as a quiet footnote, not a CTA banner.
- [ ] TOC populates for the live 2023 post — Joshua can verify by
      opening `https://joshuatoepfer.de/posts/2023/06/23/remote-mob-programming/`
      (or local `bundle exec jekyll serve`) and confirming the
      `.post-toc` aside lists all 7 section headings.
- [ ] Worker documents in Outcome: which option (A or B) chosen and
      why; how the TOC was verified.
- [ ] Hello-Welt post (no `page.source`) is unaffected — neither the
      source-link nor the TOC scan change should regress its rendering.
      Worker confirms with `bundle exec jekyll build` + a quick spot
      check.
- [ ] `pa11y-ci` stays green locally (run dark + light passes per
      `infrastructure/README.md` recipe). The new `.post-source` block
      should be obviously accessible — semantic `<aside>` with
      `aria-label`, link uses `.link` which is AA-compliant by design.

## Notes
- Both fixes are template/JS level. No design-system token changes,
  no new tokens, no ADR. Small enough to be a single worker run.
- The `<a rel="canonical">` is a slight semantic stretch — `rel="canonical"`
  is meant for `<link>` elements in `<head>`. For the body link,
  `rel="external nofollow"` or just no `rel` is more standards-conformant.
  Worker picks; both work. (The actual canonical link for SEO is
  already in `<head>` via `_includes/head-canonical.html`.)
- After this lands and is verified live: same polish applies to the
  2021 + 2022 backfill PRs when Joshua merges them — they'll benefit
  automatically from the layout change.

## Outcome

Both UX bugs fixed in one pass.

**1. Source-link block at end of `.post-body`.** Added a conditional
`<aside class="post-source mono">` to `_layouts/post.html`, rendered
between the `.post-body-layout` section and the `.post-pager`, guarded
by `{% if page.source and page.canonical_url %}`. Copy: "↗ Ursprünglich
erschienen auf <a class="link" rel="external">innoq.com</a>." Used
`rel="external"` (not `rel="canonical"` — that's reserved for `<link>`
in `<head>`, already done via `_includes/head-canonical.html`).
Wording is German; `↗` matches the arrow already in the post-hero's
"Erscheint auch auf …" meta-line, so top + bottom of the article speak
the same visual vocabulary.

**SCSS placement: `_sass/_layout.scss`.** Inserted between the existing
`.post-toc` rules and `.post-pager` — same file as every other
`.post-*` selector. `_sass/_posts.scss` is reserved for compact
post-row listings (home + related-posts cards), not for the post-page
layout, so it would have been the wrong home. Style: top-rule via
`var(--rule)`, `color: var(--fg-dim)`, 13px / 0.04em letter-spacing,
horizontal margin `0 80px` to align with the 80px page gutter used by
`.post-body-layout` and `.post-pager` (vertical breathing room is
already provided by the surrounding sections' padding — no extra top
margin needed).

**2. TOC scan: Option A (h2 + h3).** Updated
`assets/js/theme-toggle.js` line 44 (now `~46`) from
`body.querySelectorAll("h2")` to `body.querySelectorAll("h2, h3")`,
renamed `h2s` → `headings`, refreshed the header comment, and added a
brief inline rationale. Flat list — none of the current posts mix h2
and h3 in the body, so nesting is YAGNI. Chosen over Option B
(promoting h3→h2 in the INNOQ converter) because it's local to the
display layer, doesn't entangle conversion logic with TOC rendering,
and is robust against any future syndication source whose hierarchy
starts at h3.

**Verification.**
- `bundle exec jekyll build` — succeeds.
- Rendered `_site/posts/2023/06/23/remote-mob-programming/index.html`:
  `.post-source` aside is present, links to
  `https://www.innoq.com/de/articles/2023/06/remote-mob-programming/`,
  appears between `.post-body` (line 112) and `.post-pager` (line 174);
  7 `<h3>` headings in body → TOC will populate with 7 entries when JS
  runs in the browser.
- Rendered `_site/posts/2026/05/27/hello-welt/index.html`: 0
  occurrences of `post-source` (control passes — no `page.source` set).
- `pa11y-ci@4.1.1` against `localhost:4000` — 7/7 URLs passed, 0 errors
  (same as pre-task baseline from infra-006 + design-system-002).
  (Note: the 2023 syndicated post is not in pa11y-ci's default URL list,
  but a manual `pa11y` run against it surfaces only pre-existing
  footnote-anchor warnings unrelated to this task.)

**Files touched:**
- `_layouts/post.html` — added `.post-source` aside block.
- `_sass/_layout.scss` — added `.jt .post-source { ... }` rule.
- `assets/js/theme-toggle.js` — TOC scans h2 + h3; renamed `h2s` →
  `headings`; refreshed file header comment.

No new ADRs, no token changes, no design-system contract changes — pure
template/JS polish per the task spec. The 2021 + 2022 INNOQ backfill
PRs (still open) will automatically benefit from both fixes once merged.

---
id: infra-008
title: "Promote heading levels (H3→H2 etc.) during INNOQ body conversion"
status: done
type: bug
context: infrastructure
created: 2026-06-01
completed: 2026-06-01
commit:
depends_on: [infra-005]
blocks: []
tags: [sync, innoq, headings, conversion, semantics, accessibility]
related_adrs: [0006]
related_research: []
prior_art: [infra-005, infra-007]
---

## Why
The site's H1 is the post title (rendered in `_layouts/post.html`'s
post-hero). The body should logically start at **H2** for primary
section headings — that's the standard semantic + accessibility
convention: skipping heading levels (H1 → H3) breaks screen-reader
navigation and visually under-sizes sections.

INNOQ articles use H1=title, H2=subtitle, H3=section. Our converter
(via markdownify in `.github/scripts/innoq_common.py`) preserves these
levels 1:1, so syndicated bodies end up with H3 as the highest
heading — a hierarchy jump from the post-hero's H1.

Visible today on the 2023 Remote Mob Programming post: 7 section
headings ("Wie funktioniert Mob Programming?", "Was ist Remote Mob
Programming?", ..., "Fazit") render as small H3s instead of properly-
sized H2 sections. Joshua noticed and asked "ist es richtig, dass ich
beim Inhalt mit der ersten Unterüberschrift anfange?" — the answer
is no, this needs to be H2.

This was **Option B** from `website-005`'s spec, the alternative we
deferred when picking Option A (extend the TOC JS scan to h2+h3).
Option A is shipped and is good defense-in-depth; Option B is the
actual hierarchy fix and needs doing now.

## What
In the BeautifulSoup body-extraction step inside `innoq_common.py`
(before markdownify runs), walk the parsed tree and rewrite heading
levels:

| Source | After |
|---|---|
| `<h1>` | **stripped** (it's the title, already in frontmatter — defensive) |
| `<h2>` | left untouched (rare; gives manual editing room) |
| `<h3>` | **`<h2>`** |
| `<h4>` | **`<h3>`** |
| `<h5>` | **`<h4>`** |
| `<h6>` | **`<h5>`** |

Both `sync-innoq.yml` (feed-poll, infra-004) and `backfill-innoq.yml`
(scrape, infra-005) benefit automatically because they share
`innoq_common.py`.

After ship, three follow-up runs are needed to get existing INNOQ
content re-converted (NOT in worker's scope; called out for Joshua):

1. **2023 Remote Mob Programming** — already merged in main. Force-resync
   via `Sync from INNOQ` workflow (`force_resync` input) IF the article
   is still in the feed window; otherwise via `Backfill from INNOQ` with
   `urls` input (URL-list bypass per infra-007). Resulting PR replaces
   the body of `_posts/2023-06-23-remote-mob-programming.md` with H2
   sections.
2. **2021 Remote Mob Programming bei INNOQ** — still an open PR
   (`backfill/innoq/remote-mob-programming-bei-innoq`). Close that PR,
   re-trigger backfill with `urls: https://www.innoq.com/de/articles/2021/01/remote-mob-programming-bei-innoq/`,
   merge the fresh one.
3. **2022 Typist wechsel dich** — same pattern as 2021.

## Acceptance criteria

- [ ] The body-extraction code path in `innoq_common.py` (whichever
      function: `strip_article_body`, `extract_body`, or directly
      inside `convert_html_to_markdown` — worker picks the right
      location) promotes h3→h2, h4→h3, h5→h4, h6→h5 before markdownify
      converts.
- [ ] H1 in body is stripped (defensive — title is in frontmatter).
- [ ] H2 in body is left untouched.
- [ ] New unit test: input `<article><h1>Title</h1><h3>Section</h3><h4>Sub</h4></article>`
      → Markdown output does **not** contain `# Title` (stripped),
      contains `## Section`, contains `### Sub`.
- [ ] Edge-case test: empty body or body with no headings doesn't break.
- [ ] Edge-case test: body that already has H2 leaves it untouched
      (e.g. `<h2>Intro</h2><h3>Detail</h3>` → `## Intro` and `### Detail`).
- [ ] All previous 69 tests still pass (22 from infra-004's common,
      43 from infra-005, 4 from infra-007).
- [ ] `bundle exec jekyll build` still passes (sanity — change is
      Python-only).
- [ ] Brief addition to `infrastructure/README.md`'s "Sync workflow"
      section: one sentence noting that synced post bodies have INNOQ
      heading levels promoted by one (`H3→H2`) to align with the
      site's H1-in-hero convention.

## Notes
- The TOC JS from website-005 currently scans both `h2, h3`. After
  this fix the new INNOQ posts will have H2 sections — TOC populates
  via the H2 scan. The H3 scan stays as harmless extra capacity
  (useful for any future post that genuinely nests H3 subsections
  under H2 sections — TOC will then show both levels flatly).
  **Worker should NOT revert the TOC JS to h2-only** — keep it
  permissive.
- No new ADR. This is a refinement of ADR-0006's "full body
  republishing" decision, captured in this task's notes.
- Implementation hint: with BeautifulSoup it's roughly
  `for old_h in body.find_all(["h3", "h4", "h5", "h6"]): old_h.name = "h" + str(int(old_h.name[1]) - 1)`,
  plus a separate `for h1 in body.find_all("h1"): h1.decompose()`.
  Worker chooses the cleanest implementation.

## Outcome

Added a small BeautifulSoup pass inside the shared
`innoq_common.convert_html_to_markdown` function — the single conversion
chokepoint that both `sync_innoq.py` (feed-poll) and `backfill_innoq.py`
(scrape) funnel through — so both workflows benefit without duplicating
logic.

- **Code change:** new helper `_promote_heading_levels(html)` in
  `.github/scripts/innoq_common.py` (called from
  `convert_html_to_markdown` before markdownify runs). Decomposes every
  body `<h1>` and rewrites `<h3>`–`<h6>` down one level
  (`tag.name = f"h{int(tag.name[1]) - 1}"`). `<h2>` is intentionally
  untouched. Added `from bs4 import BeautifulSoup` to the module imports;
  bs4 is already a transitive dependency of `markdownify` and is also
  explicitly installed in `backfill-innoq.yml`, so no new dependency is
  introduced.
- **Tests:** new `HeadingPromotionTests` class in
  `.github/scripts/test_innoq_common.py` with 8 tests covering h3→h2,
  h4→h3, h5→h4, h6→h5, h1-strip, h2-untouched (incl. an h3 in the same
  body climbing up to share the h2 level), the no-headings no-op, and a
  full h1–h6 cascade. Suite total: **77 tests pass** (was 69; +8).
- **Spec drift caught:** the task spec's prose example for
  `test_h2_untouched` was internally inconsistent — its English text
  said "H3 promoted" yet the expected output (`### Detail`) preserved
  H3. The promotion table (and Joshua's symptom report — H3 sections
  rendering too small) is authoritative, so the test asserts the
  correct, table-consistent behaviour: `<h2>Intro</h2><h3>Detail</h3>`
  → `## Intro` AND `## Detail` (H2 stayed; H3 climbed up to match).
- **Jekyll build:** clean (Python-only change).
- **README:** added a short "Heading promotion" paragraph at the top of
  the "Sync workflow" section in
  `.agentheim/contexts/infrastructure/README.md`, explaining the rule
  and its rationale, and noting that it applies to both sync and
  backfill.
- **Post-merge actions (out of worker scope, Joshua's:** force-resync
  the 2023 Remote Mob Programming post and re-trigger the two open
  backfill PRs (2021, 2022) via URL-list mode so all existing INNOQ
  content is re-converted with H2 sections.

---
id: infra-010
title: "Fix srcset parser to handle Cloudinary commas-in-URL"
status: done
type: bug
context: infrastructure
created: 2026-06-02
completed: 2026-06-02
commit:
depends_on: [infra-005]
blocks: []
tags: [sync, innoq, conversion, srcset, images, cloudinary]
related_adrs: [0006]
related_research: []
prior_art: [infra-005, infra-009]
---

## Why
The 2022 "Typist wechsel dich" backfill PR has **4 broken body images**.
The `src` attribute in the rendered Markdown is a relative-path
fragment like `w_2800/v1/uploads-production/e035w3dl0y0y28nu2prr5i7acmr4?_a=BACMTiAE`
instead of the full Cloudinary URL. The browser resolves it relative
to the post URL → 404.

Root cause: `innoq_common.largest_src_from_srcset` (from infra-005)
splits the `srcset` attribute naively on `,`. INNOQ's images have an
empty `src` and a real `srcset` with 9 candidate URLs, each shaped
like a Cloudinary transformation URL:

```
https://res.cloudinary.com/innoq/image/upload/c_limit,f_auto,q_auto,w_400/v1/uploads-production/<id>?_a=BACMTiAE 400w,
https://res.cloudinary.com/innoq/image/upload/c_limit,f_auto,q_auto,w_800/v1/uploads-production/<id>?_a=BACMTiAE 800w,
…
```

Cloudinary's transformation parameters (`c_limit,f_auto,q_auto,w_2800`)
are themselves comma-separated **inside** each URL. The HTML5 srcset
spec assumes URLs don't contain commas, but Cloudinary's syntax
violates that — and `split(",")` shreds the URLs into fragments.

The current largest-by-width logic then picks whatever fragment has
the highest trailing `Nw` descriptor and writes it into the post as
`![alt](fragment)`. Result: broken image.

This is **not** an "INNOQ should mirror images locally" problem.
infra-005 / ADR-0006 deliberately keep INNOQ/Cloudinary as the asset
host, no local mirroring. The fix is to extract the **right** absolute
Cloudinary URL from the malformed-but-real-world srcset.

## What
Replace the naive `split(",")` in `largest_src_from_srcset` (or
wherever the srcset parsing lives — `innoq_common.py`) with a parser
that handles commas-inside-URLs.

### Approach
HTML5 srcset candidate strings are separated by `,\s+`, and inside
each candidate the URL ends at the first whitespace. The whitespace
after the comma is the disambiguator: `,\s+` is a candidate separator,
`,` alone (no whitespace) is a URL-internal Cloudinary parameter
separator.

Practical regex: split on `,\s+(?=\S)` — i.e. on commas followed by
whitespace + non-whitespace. Or even simpler and more robust:
`,\s+(?=https?://)` — split only when the next non-whitespace is a
URL scheme. This is right for the INNOQ/Cloudinary shape.

After splitting, each candidate is `<URL> <descriptor>` (whitespace-
separated). The width is `\d+w`; the largest is the winner.

Worker may pick the cleanest implementation. Standard-library Python
only; no new dependencies.

### Other shapes to handle gracefully
- **No srcset, only src** → existing behavior, return src as-is.
- **srcset with relative URLs** (extremely rare, but theoretical) →
  preserve as-is. The post layout has no `<base>` so a relative URL
  is by definition broken; we don't try to fix it. (If this ever
  surfaces with a real article, file a follow-up.)
- **srcset with x-density descriptors (`1x`, `2x`)** instead of width
  descriptors → pick the largest density. Unlikely from INNOQ but
  Cloudinary may emit it.
- **Empty srcset string** → return None or fall back to src; don't
  crash.

## Acceptance criteria

- [ ] `largest_src_from_srcset` correctly parses an INNOQ-style
      srcset where each candidate URL contains commas
      (`c_limit,f_auto,q_auto,w_NNN`). Output is the absolute
      Cloudinary URL with the largest width, unchanged.
- [ ] When `srcset` is empty/absent, falls back to `src` cleanly.
- [ ] When `src` and `srcset` are both empty/absent, returns None
      (or whatever the existing contract is for "no image URL").
- [ ] New tests in `test_innoq_common.py` (or wherever the existing
      `largest_src_from_srcset` tests live):
      - `test_cloudinary_srcset_with_commas_in_urls`: input is the
        actual INNOQ srcset shape with 9 candidates and Cloudinary
        commas → output is the `w_2800` URL (the largest).
      - `test_srcset_two_candidates_simple`: standard srcset
        without commas-in-URLs → still works (regression guard for
        any non-Cloudinary case).
      - `test_empty_srcset_falls_back_to_src`.
      - `test_no_src_no_srcset_returns_none` (or whatever the
        no-image case returns).
- [ ] All previous tests pass (86 from infra-009 baseline).
- [ ] `bundle exec jekyll build` still passes.

## Notes
- The fix is `~10 lines` of Python plus tests. No new ADR.
- Post-ship: Joshua re-triggers Backfill for the 2022 URL again
  (URL-list bypass via infra-007). New PR will have correct image
  URLs. If 2021 has body images (it had no Cloudinary refs in
  the earlier audit, but worth checking) they get fixed too.
- After the fix, the rendered post should have images that load
  directly from `res.cloudinary.com` — no local mirroring, INNOQ's
  Cloudinary continues to serve them (matches ADR-0006).
- A future enhancement (not in scope): rather than always picking
  the largest width (potentially 2800px = ~500 KB per image), use
  `f_auto,q_auto,c_limit,w_1200` or similar — Cloudinary URLs can
  be rewritten to a sensible default width. Out of scope here.
- The empty `src` is INNOQ's lazy-load convention: src is left
  blank, srcset has the real candidates, and JS/img-decoder picks
  one. Browsers without JS will only see the empty src and the
  srcset, and the user-agent picks. Our converter has to do the
  picking explicitly because we emit static Markdown.

## Implementation hint

```python
import re

_CANDIDATE_SPLITTER = re.compile(r",\s+(?=https?://)")
_WIDTH_DESCRIPTOR = re.compile(r"\s+(\d+)w$")

def largest_src_from_srcset(srcset: str) -> str | None:
    if not srcset or not srcset.strip():
        return None
    candidates = []
    for raw in _CANDIDATE_SPLITTER.split(srcset.strip()):
        raw = raw.strip().rstrip(",").strip()
        if not raw:
            continue
        m = _WIDTH_DESCRIPTOR.search(raw)
        if m:
            width = int(m.group(1))
            url = raw[: m.start()].strip()
        else:
            width = 0
            url = raw.split()[0] if raw else ""
        if url:
            candidates.append((width, url))
    if not candidates:
        return None
    return max(candidates, key=lambda c: c[0])[1]
```

Adapt to existing function signature/return type — worker checks.

## Outcome

Replaced the naive `srcset.split(",")` inside
`innoq_common.largest_src_from_srcset` with a precompiled
`_SRCSET_CANDIDATE_SEPARATOR` regex (`,\s+(?=https?://)`) that only
breaks at real srcset candidate boundaries. Cloudinary's URL-internal
transformation commas (`c_limit,f_auto,q_auto,w_NNN`) now survive
parsing intact, and the largest-width pick is a full absolute
Cloudinary URL instead of a relative path fragment that 404s.

Existing return contract preserved: empty / None / whitespace-only
`srcset` still returns `""` (callers fall back to the original `src`
themselves; the acceptance criteria's "None or whatever the existing
contract is" clause). Single URL, density-descriptor, and standard
width-descriptor srcsets keep behaving as before — verified by the
existing 4 SrcsetTests cases.

3 new tests added in `SrcsetTests`:
- `test_cloudinary_srcset_with_commas_in_urls` — the regression itself
  (9-candidate INNOQ-shaped srcset, expects `w_2800` URL intact)
- `test_srcset_two_candidates_simple` — regression guard for plain
  HTML5 srcsets without URL-internal commas
- `test_empty_srcset_falls_back_to_empty` — empty + None + whitespace
  inputs all return `""`

Full test suite 89/89 green (86 baseline from infra-009 + 3 new).
`bundle exec jekyll build` passes.

Both `sync_innoq.py` and `backfill_innoq.py` route image conversion
through this helper (per ADR-0006's shared-module design), so the fix
flows to both INNOQ workflows automatically — no per-workflow change
needed. INNOQ/Cloudinary remain the asset host; nothing mirrored
locally.

No new ADR — the fix is a pure parser correction without architectural
implications. The Cloudinary-srcset shape and its `,\s+(?=https?://)`
split rule are documented inline in the helper's docstring and in the
BC README's Sync-workflow section (new "Cloudinary srcset parsing"
paragraph alongside heading-promotion and conclusion-merge).

**Key files:**
- `.github/scripts/innoq_common.py` — fixed `largest_src_from_srcset`,
  added module-level `_SRCSET_CANDIDATE_SEPARATOR` regex
- `.github/scripts/test_innoq_common.py` — 3 new tests in `SrcsetTests`
- `.agentheim/contexts/infrastructure/README.md` — new
  "Cloudinary srcset parsing" paragraph under "Sync workflow"

**Follow-up (not done here, deliberately out of scope):** the largest-
width pick always selects `w_2800`, ~500 KB per body image. Future
enhancement could rewrite Cloudinary URLs to a sensible default
(`f_auto,q_auto,c_limit,w_1200`). Joshua noted this in the original
task spec — not filed as a backlog item yet because it needs a real
"what's the right default width" decision first.

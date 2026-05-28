---
id: infra-007
title: "Backfill URL-list mode bypasses dedup (force-resync semantic)"
status: done
type: bug
context: infrastructure
created: 2026-05-28
completed: 2026-05-28
commit:
depends_on: [infra-005]
blocks: []
tags: [sync, innoq, backfill, dedup, semantics]
related_adrs: [0006]
related_research: []
prior_art: [infra-005]
---

## Why
Spec/implementation gap surfaced 2026-05-28 while trying to re-trigger
backfill for an article whose original conversion needed cleanup
(typos in the INNOQ source HTML had been carried through markdownify
verbatim). Joshua:

1. Closed the existing PR without merging.
2. Deleted the branch.
3. Re-triggered `backfill-innoq.yml` with the same canonical URL in the
   `urls` input.

Expected: a fresh PR with re-converted content (the workflow's documented
purpose for the URL-list input — explicit re-processing of a specific
article).

Actual: dedup-skip. `gh pr list --state all --head backfill/innoq/<slug>`
still returns the closed PR record (GitHub keeps PR history forever; close
+ branch-delete doesn't remove the PR row). The `pr-history` skip
fires unconditionally — auto-discovery and URL-list mode both go through
the same dedup chain.

The original infra-005 spec said the URL-list mode "also serves as a
generic re-sync mechanism for backfill articles whose original
conversion was buggy" — but the worker's implementation applied
dedup to every URL, regardless of input source. The verifier didn't
catch this because the spec phrasing was loose enough that a strict
literal reading was consistent with the implementation.

User reasoning, verbatim: *"Wenn ich einen canonical Link angebe, dann
soll er einen neuen PR aufmachen egal obs den schon gab. Wieso sollte
ich sonst einzelne URLs eingeben?"* — exactly right. The URL-list
input has no other plausible purpose.

## What
Make the `urls` input in `backfill-innoq.yml` bypass both dedup checks
for the URLs it lists. Auto-discovery mode (URLs empty) stays unchanged.

The semantic mirrors `sync-innoq.yml`'s `force_resync` input — when the
user explicitly names a URL, they're requesting unconditional processing
of that URL.

### Behaviour change

In `.github/scripts/backfill_innoq.py`'s `build_plan` (or equivalent):

- **Auto-discovery mode** (URL-list empty, scraping the staff page):
  every candidate URL runs through:
  1. `existing_canonical_urls()` check → skip if URL already in `_posts/`
  2. `pr_history_has_branch(branch)` check → skip if PR ever existed
  
  (Unchanged.)

- **URL-list mode** (non-empty `urls` input):
  - **Skip both dedup checks entirely.** Process each listed URL as if
    fresh.
  - Branch naming stays the same (`backfill/innoq/<slug>`). peter-evans's
    `delete-branch: true` + `--force-with-lease` push handles the
    "branch may or may not exist, re-push it cleanly" case. GitHub
    creates a new PR (does not auto-link to the closed historical PR).

### Edge case to handle gracefully

If the user runs URL-list mode while a PR is **still open** for the same
slug, peter-evans updates the existing open PR (its standard behaviour).
That's fine and arguably useful — "re-sync over an open PR with fresh
content". No new code path needed; this falls out of peter-evans's
defaults.

### Logging change

Each candidate URL processed in URL-list mode should log
`URL-list (bypassed dedup): <url>` so the workflow output makes the
explicit-force-mode obvious. Auto-discovery candidates log as before.

## Acceptance criteria

- [ ] `.github/scripts/backfill_innoq.py` `build_plan` (or the
      relevant code path) accepts a flag/parameter or detects URL-list
      mode (e.g. `if URLS_INPUT` non-empty at call site), and for that
      mode skips both `existing_canonical_urls()` and
      `pr_history_has_branch()` checks.
- [ ] Auto-discovery mode behaviour is **byte-identical** to before
      (dedup still applies). Add or extend a test that confirms this.
- [ ] New test: URL-list mode with a URL already in `_posts/` →
      plan includes that URL (does not skip).
- [ ] New test: URL-list mode with a URL whose `backfill/innoq/<slug>`
      PR is closed → plan includes that URL (does not skip).
- [ ] Log line `URL-list (bypassed dedup): <url>` appears for URL-list
      processed entries. (Auto-discovery entries log as before.)
- [ ] Dry-run mode still works correctly for URL-list mode (logs the
      planned PR creation without actually creating it).
- [ ] `infrastructure/README.md` "Backfill workflow" sub-section updated:
      under URL-list mode, explicitly state "bypasses dedup — used to
      re-process a specific article whose original sync was wrong, or
      to manually re-trigger after the closing of a previous attempt".
- [ ] All existing tests still pass (65 total from the prior tasks).

## Notes
- Branch namespace stays `backfill/innoq/<slug>` (no timestamp suffix).
  Worker considered the sync-innoq force-resync pattern (which uses a
  timestamp suffix) but decided against it for backfill because:
  - Auto-discovery dedup already prevents future runs from
    re-resyncing accidentally (the `_posts/` match catches the merged
    article).
  - peter-evans's `--force-with-lease` push handles the re-push
    cleanly.
  - Fewer dead branches in the repo over time.
- Trivial scope. One conditional branch in `build_plan`, two new
  tests, one README sentence. No new ADR. No changes to dependencies.
- This is a spec-aligned bug-fix, not a redesign. The infra-005 task
  spec's intent was correct; the implementation under-fulfilled it.
- After ship: the immediate pain (Joshua's 2023-article re-sync attempt)
  is resolved by re-triggering "Backfill from INNOQ" with the canonical
  URL in `urls` input. Frischer PR.

## Outcome

Shipped via Approach A — added a keyword-only `bypass_dedup: bool = False`
parameter to `build_plan()` in `.github/scripts/backfill_innoq.py`. When
`True`, both `existing_canonical_urls()` and `pr_history_has_branch()`
checks are skipped (the former is also not even called — we initialise
`seen_canonicals` to an empty set). The bypassed-URL path logs
`URL-list (bypassed dedup): <url>` for output clarity.

The `main()` caller derives mode from `raw_urls`: a non-empty `URLS`
env var triggers `url_list_mode = True`, which is threaded into
`build_plan(candidate_urls, bypass_dedup=url_list_mode)`. The
URL-list-mode kickoff log is also clarified
("URL-list mode: N URL(s) provided — bypassing dedup
(explicit re-process).").

Auto-discovery flow is byte-identical to pre-infra-007 behaviour at the
default `bypass_dedup=False`.

Tests added in `.github/scripts/test_backfill_innoq.py`
(`BuildPlanDedupBypassTests`):
1. `test_url_list_mode_bypasses_existing_posts_check` — URL already in
   `_posts/*.md` is still planned when bypass=True.
2. `test_url_list_mode_bypasses_pr_history_check` — closed PR record
   does not block; also asserts `pr_history_has_branch` is not even
   invoked in bypass mode.
3. `test_auto_discovery_mode_still_dedups_against_existing_posts` —
   regression guard that bypass=False (auto-discovery) still skips
   already-in-posts URLs.
4. `test_auto_discovery_mode_still_dedups_against_pr_history` —
   regression guard for the pr-history skip path.

Full suite: 69 tests pass (65 existing + 4 new). Jekyll build still
clean. Workflow YAML still parses (no input shape change — the
existing `urls` input is the trigger).

README updated in `infrastructure/README.md` "Backfill workflow"
sub-section: URL-list mode explicitly described as bypassing both
dedup checks, parallel to `sync_innoq`'s `force_resync` semantic.

No ADR-0006 amendment — the change is small enough and self-describing
via the task file and the README sentence; future maintainers grepping
for the dedup chain will hit the if/else branch and follow the comment
back to infra-007.

Key files:
- `.github/scripts/backfill_innoq.py` — `build_plan` bypass branch + caller threading.
- `.github/scripts/test_backfill_innoq.py` — `BuildPlanDedupBypassTests` (4 new tests).
- `.agentheim/contexts/infrastructure/README.md` — Backfill workflow URL-list-mode description.

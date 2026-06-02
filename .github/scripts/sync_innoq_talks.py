#!/usr/bin/env python3
"""INNOQ talks → `_data/talks.yml` sync workflow entry point (infra-011).

Sibling to `sync_innoq.py` (article incremental sync, infra-004) and
`backfill_innoq.py` (article backfill, infra-005). Unlike the article
syncs, talks live in ONE file (`_data/talks.yml`) rather than one
markdown per entry — so the merge engine in `innoq_talks.py` is doing
in-place updates, not just inserts. See ADR-0007.

Workflow contract (from `.github/workflows/sync-innoq-talks.yml`):

1. Scrape `https://www.innoq.com/de/talks/?all=true&by=joshua-toepfer`,
   following `nav.paginator a[rel="next"]` until exhausted.
2. For each listing entry, fetch the talk's detail page to pick up
   `city`, `abstract`, slides URL, and the duration fallback.
3. Diff against the on-disk `_data/talks.yml` (matched by `source_url`
   for `source: innoq` entries; `source: manual` entries pass through
   untouched). INNOQ-authoritative fields are re-derived and overwrite;
   `video` and the `source` marker are preserved (ADR-0007 §3).
4. If the diff is non-empty, write the updated YAML, close any prior
   open `sync/innoq-talks/*` PR (with a comment linking to the new
   one), and let the GHA workflow open ONE PR per run on the
   date-stamped branch `sync/innoq-talks/<YYYY-MM-DD>`.
5. Empty diff → no branch, no PR, exit 0.

Environment / inputs:
- `DRY_RUN` ('true' | 'false') — when true, scrape + merge + print the
  diff summary, but neither rewrite `_data/talks.yml` nor close prior
  PRs. Mirrors `backfill_innoq.py`'s `dry_run` convention (infra-005).
- `GH_TOKEN` — used by the `gh` CLI when closing prior PRs.

The PR open itself is done by the workflow via
`peter-evans/create-pull-request@v6` — this script only writes the
file and emits the PR title/body as workflow outputs.

ADR references: 0002 (canonical sync strategy), 0006 (HTTP politeness +
dual-workflow pattern), 0007 (talks sync architecture).
"""

from __future__ import annotations

import datetime
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Callable

import yaml

from innoq_common import (
    REPO_ROOT,
    fetch_with_retry,
    write_github_output,
)
from innoq_talks import (
    DetailFields,
    ListingEntry,
    ScrapedTalk,
    TALKS_BRANCH_PREFIX,
    TALKS_DISCOVERY_URL,
    TALKS_PR_LABEL,
    build_pr_body,
    merge_talks,
    next_page_url,
    parse_detail,
    parse_listing,
    serialise_talks,
)

LOGGER = logging.getLogger("sync_innoq_talks")

TALKS_FILE = REPO_ROOT / "_data" / "talks.yml"


def _log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def _is_truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in ("1", "true", "yes")


# ---------------------------------------------------------------------------
# Scrape orchestration
# ---------------------------------------------------------------------------


def scrape_all(
    *,
    discovery_url: str = TALKS_DISCOVERY_URL,
    fetch_fn: Callable[[str], str] = fetch_with_retry,
) -> list[ScrapedTalk]:
    """Walk the listing paginator + detail pages, return merged ScrapedTalk list.

    Raises `RuntimeError` if the discovery URL returns zero listing entries —
    a cron run that silently produces zero talks would otherwise erase
    every `source: innoq` entry on subsequent merges. Loud failure
    surfaces template drift early.
    """
    listing_entries: list[ListingEntry] = []
    url: str | None = discovery_url
    while url:
        _log(f"Fetching listing page: {url}")
        html = fetch_fn(url)
        page_entries = parse_listing(html)
        _log(f"  {len(page_entries)} talk(s) on this page")
        listing_entries.extend(page_entries)
        url = next_page_url(html)

    if not listing_entries:
        raise RuntimeError(
            f"Discovery URL {discovery_url!r} returned zero listing entries — "
            "INNOQ template may have changed, refusing to write an empty sync"
        )

    talks: list[ScrapedTalk] = []
    for entry in listing_entries:
        _log(f"Fetching detail: {entry.source_url}")
        detail_html = fetch_fn(entry.source_url)
        detail: DetailFields = parse_detail(detail_html)
        talks.append(
            ScrapedTalk(
                source_url=entry.source_url,
                date=entry.date,
                what=entry.what,
                where=entry.where,
                city=detail.city,
                type=entry.type,
                duration=entry.duration if entry.duration is not None else detail.duration,
                abstract=detail.abstract,
                slides=detail.slides if entry.slides_flag else None,
            )
        )
    return talks


# ---------------------------------------------------------------------------
# Branch + PR coordination
# ---------------------------------------------------------------------------


def branch_for_today(*, today: datetime.date | None = None) -> str:
    """Return the date-stamped sync branch name (ADR-0007 §7)."""
    if today is None:
        today = datetime.datetime.now(datetime.timezone.utc).date()
    return f"{TALKS_BRANCH_PREFIX}/{today.isoformat()}"


def close_prior_open_prs(new_branch: str, *, gh_runner=subprocess.run) -> list[str]:
    """Close every open PR on a `sync/innoq-talks/*` branch (ADR-0007 §8).

    Returns the list of PR numbers closed (as strings) for observability.
    A `gh` failure is logged but not fatal — the workflow continues so
    the new PR still opens; Joshua can clean up by hand if needed.
    """
    import json

    closed: list[str] = []
    try:
        result = gh_runner(
            [
                "gh", "pr", "list",
                "--state", "open",
                "--json", "number,headRefName",
                "--limit", "100",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        _log("`gh` not on PATH (local dev?) — skipping close-prior-PRs step")
        return closed
    except subprocess.CalledProcessError as exc:
        _log(f"`gh pr list` failed (skipping close-prior step): {exc.stderr.strip()}")
        return closed

    try:
        prs = json.loads(result.stdout or "[]")
    except json.JSONDecodeError:
        _log(f"`gh pr list` returned unparseable JSON: {result.stdout!r}")
        return closed

    for pr in prs:
        ref = pr.get("headRefName", "")
        number = pr.get("number")
        if not ref or number is None:
            continue
        if not ref.startswith(f"{TALKS_BRANCH_PREFIX}/"):
            continue
        if ref == new_branch:
            continue  # don't close ourselves on a re-run within the same day
        comment = (
            f"Superseded by a new talks-sync run on `{new_branch}`. "
            "Closing this PR as part of the close-prior-then-open-new flow "
            "(ADR-0007 §8)."
        )
        try:
            gh_runner(
                ["gh", "pr", "close", str(number), "--comment", comment],
                check=True,
                capture_output=True,
                text=True,
            )
            closed.append(str(number))
            _log(f"Closed prior talks-sync PR #{number} (branch {ref!r})")
        except subprocess.CalledProcessError as exc:
            _log(f"Failed to close PR #{number}: {exc.stderr.strip()}")
    return closed


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def _load_existing(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or []
    if not isinstance(data, list):
        raise RuntimeError(
            f"{path} did not load as a list; got {type(data).__name__}"
        )
    return data


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    dry_run = _is_truthy(os.environ.get("DRY_RUN"))

    existing = _load_existing(TALKS_FILE)
    scraped = scrape_all()
    today = datetime.datetime.now(datetime.timezone.utc).date()

    merged, diff = merge_talks(existing, scraped, today=today)

    has_changes = (
        bool(diff["new"])
        or bool(diff["status_transitions"])
        or bool(diff["updates"])
        or bool(diff["ambiguous"])
        or merged != existing
    )

    _log(f"Sync summary: new={len(diff['new'])} "
         f"status_transitions={len(diff['status_transitions'])} "
         f"updates={len(diff['updates'])} ambiguous={len(diff['ambiguous'])}")

    if not has_changes:
        _log("No diff — nothing to do, exiting cleanly.")
        write_github_output("has_changes", "false")
        return 0

    branch = branch_for_today(today=today)
    pr_body = build_pr_body(diff)
    pr_title = f"Sync: INNOQ talks ({today.isoformat()})"

    if dry_run:
        _log("DRY_RUN=true → skipping file write + close-prior step")
        _log(f"Would open PR on branch {branch!r} with title {pr_title!r}")
        _log(f"PR body:\n{pr_body}")
        write_github_output("has_changes", "true")
        write_github_output("dry_run", "true")
        return 0

    # Write the merged YAML back to disk. The peter-evans action sees
    # the diff and opens the PR.
    serialised = serialise_talks(merged)
    TALKS_FILE.write_text(serialised, encoding="utf-8")
    _log(f"Wrote {TALKS_FILE.relative_to(REPO_ROOT)} ({len(merged)} entries)")

    closed = close_prior_open_prs(branch)
    if closed:
        _log(f"Closed prior open PRs: {', '.join(closed)}")

    write_github_output("has_changes", "true")
    write_github_output("branch", branch)
    write_github_output("pr_title", pr_title)
    write_github_output("pr_body", pr_body)
    return 0


if __name__ == "__main__":
    sys.exit(main())

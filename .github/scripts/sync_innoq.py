#!/usr/bin/env python3
"""Incremental INNOQ → joshuatoepfer.de sync (infra-004).

Polls the INNOQ /de/feed.atom rolling window, applies the German-articles-only
filter chain, dedups against `_posts/*.md` and PR history, and emits a JSON
plan of articles that need a PR. The workflow then iterates over the plan and
invokes `peter-evans/create-pull-request@v6` once per article so the
"one PR per article" acceptance criterion is honoured.

Workflow contract:
- Reads `FEED_URL_OVERRIDE` env (smoke test) and `FORCE_RESYNC` env (workflow input).
- Writes plan as a JSON array to `$GITHUB_OUTPUT` under `plan`.
- For each item in the plan, writes the resolved `_posts/*.md` file into the
  working tree so the PR action picks it up directly.

Failure modes (all fail loud, non-zero exit, surfaces Joshua's notification):
- Feed unreachable / HTTP error / DNS failure
- Feed body unparseable
- Force-resync URL not present in the current feed window
- `gh pr list` failures (subprocess error from the dedup check)

ADR references: 0002 (canonical strategy), 0006 (this task's architecture).
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import sys
import urllib.error
import urllib.request

from innoq_common import (
    FEED_URL,
    FeedEntry,
    build_pr_body,
    build_pr_title,
    entry_passes_filter,
    existing_canonical_urls,
    filter_reasons,
    find_post_by_canonical_url,
    parse_feed_entries,
    pr_history_has_branch,
    read_existing_post_meta,
    split_force_resync_input,
    write_github_output,
    write_post_file,
)


def _log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def fetch_feed(url: str) -> bytes:
    _log(f"Fetching feed: {url}")
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "joshuatoepfer.de-sync/1.0 (+https://joshuatoepfer.de)",
            "Accept": "application/atom+xml, application/xml, text/xml",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read()
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        raise RuntimeError(f"Feed fetch failed for {url}: {exc!r}") from exc


def _entry_by_canonical(entries: list[FeedEntry], url: str) -> FeedEntry | None:
    target = url.strip().rstrip("/")
    for entry in entries:
        if entry.canonical_url.rstrip("/") == target:
            return entry
    return None


def _utc_timestamp() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def plan_for_normal_run(entries: list[FeedEntry]) -> list[dict]:
    """Return the list of articles eligible for a PR in incremental mode."""
    seen_canonicals = existing_canonical_urls()
    plan: list[dict] = []

    for entry in entries:
        if not entry.canonical_url:
            _log(f"SKIP (no URL): {entry.title!r}")
            continue

        # Filter chain.
        reasons = filter_reasons(entry)
        if reasons:
            _log(
                f"SKIP (filtered): {entry.canonical_url} — "
                + "; ".join(reasons)
            )
            continue

        # Dedup #1: already merged into _posts/.
        if entry.canonical_url in seen_canonicals:
            _log(f"SKIP (already in _posts): {entry.canonical_url}")
            continue

        # Dedup #2: PR record already exists for this branch.
        try:
            if pr_history_has_branch(entry.branch_name):
                _log(f"SKIP (PR already exists for {entry.branch_name}): {entry.canonical_url}")
                continue
        except RuntimeError as exc:
            # Loud-fail on gh-cli failures: don't silently flood PRs.
            raise RuntimeError(f"PR-history dedup failed: {exc}") from exc

        plan.append(_plan_item(entry, resync=False))

    return plan


def plan_for_force_resync(
    entries: list[FeedEntry], force_urls: list[str]
) -> list[dict]:
    """Build the plan for a force-resync run.

    Each URL must exist in the current feed window — otherwise we exit
    non-zero per the failure contract (caller's job to surface).
    """
    timestamp = _utc_timestamp()
    plan: list[dict] = []

    for url in force_urls:
        entry = _entry_by_canonical(entries, url)
        if entry is None:
            raise RuntimeError(
                f"force_resync requested for {url} but article not in "
                "current feed window; nothing to sync"
            )

        # Force-resync still requires the article to actually be one of
        # Joshua's German articles — otherwise we'd be PR'ing something
        # entirely unrelated. This is a defensive guard, not in the spec
        # but consistent with "fail loud".
        if not entry_passes_filter(entry):
            raise RuntimeError(
                f"force_resync requested for {url} but entry fails the "
                f"filter chain: {filter_reasons(entry)!r}"
            )

        existing = find_post_by_canonical_url(entry.canonical_url)
        preserved = read_existing_post_meta(existing) if existing else {}
        plan.append(_plan_item(entry, resync=True, timestamp=timestamp, preserved=preserved))

    return plan


def _plan_item(
    entry: FeedEntry,
    *,
    resync: bool,
    timestamp: str | None = None,
    preserved: dict | None = None,
) -> dict:
    branch = entry.resync_branch_name(timestamp) if resync and timestamp else entry.branch_name
    return {
        "slug": entry.slug,
        "branch": branch,
        "title": build_pr_title(entry),
        "body": build_pr_body(entry, resync=resync),
        "canonical_url": entry.canonical_url,
        "post_filename": entry.post_filename,
        "resync": resync,
        # Stash the bits we need to materialise the file just before the
        # PR action runs in the matrix job.
        "_internal": {
            "title": entry.title,
            "published_date": entry.published_date,
            "xml_lang": entry.xml_lang,
            "content_html": entry.content_html,
            "preserved": preserved or {},
        },
    }


def materialise_plan_files(plan: list[dict]) -> None:
    """Write every plan item's post file into `_posts/`.

    Called by the workflow in the per-article matrix step (one item at a
    time, in a clean checkout) so peter-evans/create-pull-request sees
    exactly one new file per branch.
    """
    for item in plan:
        internal = item["_internal"]
        entry = FeedEntry(
            title=internal["title"],
            canonical_url=item["canonical_url"],
            published_date=internal["published_date"],
            content_html=internal["content_html"],
            xml_lang=internal["xml_lang"],
            author_emails=[],
        )
        path = write_post_file(entry, preserved_meta=internal.get("preserved") or None)
        _log(f"Wrote {path.relative_to(path.parents[1])}")


def main() -> int:
    feed_url = os.environ.get("FEED_URL_OVERRIDE") or FEED_URL
    force_resync = split_force_resync_input(os.environ.get("FORCE_RESYNC"))
    plan_only = os.environ.get("PLAN_ONLY", "").lower() in ("1", "true", "yes")
    materialise_for_slug = os.environ.get("MATERIALISE_FOR_SLUG", "").strip()

    feed_bytes = fetch_feed(feed_url)
    entries = parse_feed_entries(feed_bytes)
    _log(f"Parsed {len(entries)} feed entries.")

    if force_resync:
        _log(f"Force-resync mode: {len(force_resync)} URL(s).")
        plan = plan_for_force_resync(entries, force_resync)
    else:
        plan = plan_for_normal_run(entries)

    _log(f"Plan size: {len(plan)} PR(s).")

    if materialise_for_slug:
        target = [item for item in plan if item["slug"] == materialise_for_slug]
        if not target:
            raise RuntimeError(
                f"materialise_for_slug={materialise_for_slug!r} not in plan; "
                "plan likely diverged from the workflow's matrix input"
            )
        materialise_plan_files(target)
        return 0

    if plan_only:
        # Emit a slim plan (drop `_internal`) for the matrix; the
        # per-article step re-runs the script with MATERIALISE_FOR_SLUG to
        # write the file fresh in its own clean checkout.
        slim = [
            {k: v for k, v in item.items() if k != "_internal"}
            for item in plan
        ]
        slim_json = json.dumps(slim, ensure_ascii=False)
        write_github_output("plan", slim_json)
        write_github_output("plan_count", str(len(slim)))
        # Also print the plan for log visibility.
        print(slim_json)
        return 0

    # Default behaviour (e.g. local dev without GH Actions): just emit
    # the plan as JSON to stdout.
    print(json.dumps(
        [{k: v for k, v in item.items() if k != "_internal"} for item in plan],
        ensure_ascii=False,
        indent=2,
    ))
    return 0


if __name__ == "__main__":
    sys.exit(main())

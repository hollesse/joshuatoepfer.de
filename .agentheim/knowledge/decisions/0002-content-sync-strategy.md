# ADR-0002: Content Sync Strategy (innoq.com → PR)

**Date:** 2026-05-26
**Status:** Accepted
**Context:** infrastructure

---

## Context

Joshua Töpfer publishes technical articles on innoq.com. He wants those articles mirrored
on joshuatoepfer.de with a canonical link back to the original, so his personal site
reflects his full body of work without requiring manual copy-paste effort.

The mirroring must be automatic enough to require no regular manual monitoring, but must
give Joshua explicit control over what actually becomes visible on his site. An article
appearing on innoq.com must never automatically become public on joshuatoepfer.de without
Joshua choosing it.

There is also an open legal and policy question: innoq.com content is published under
innoq's platform. Republishing full article bodies may require permission from innoq, even
for Joshua as the original author. Until that question is resolved, the sync workflow
should default to importing metadata and a summary excerpt rather than the full body,
linking readers back to innoq.com for the complete article.

---

## Decision

Use a scheduled GitHub Actions workflow (running daily) that:

1. **Discovers new posts** by fetching the innoq.com RSS feed filtered to Joshua's author
   profile URL. The feed is the primary discovery source; it requires no innoq API access
   or cooperation.

2. **Diffs against existing content** by comparing each feed entry's URL (used as a stable
   identifier) against the `canonical_url` frontmatter field in existing `_posts/` files.
   An entry is considered "new" if no existing post carries that canonical URL.

3. **Opens a pull request per new post** containing a Jekyll post file with the following
   frontmatter:
   ```yaml
   ---
   layout: post
   title: "<post title from feed>"
   date: <publication date from feed>
   source: innoq
   canonical_url: <full URL to innoq.com post>
   published: false
   ---
   ```
   The post body initially contains a brief excerpt (if available in the feed) followed by
   a prose link to the original. If the full body is later licensed for republishing, the
   workflow can be updated to embed it.

4. **Does not auto-merge.** Every sync PR requires Joshua's explicit review and merge.
   Merging the PR adds the file to the repository with `published: false`, meaning it is
   tracked in version control but not rendered on the live site.

5. **Two-step publish.** To make a synced post live, Joshua separately edits the file and
   sets `published: true`. This second step is intentional — it separates "I acknowledge
   this post exists" from "I want this visible on my site right now".

### Trigger schedule

Daily, at a low-traffic time (e.g. 03:00 UTC), via GitHub Actions `schedule` cron.
Manual trigger via `workflow_dispatch` is also enabled so Joshua can run it on demand
(e.g. after publishing a new innoq.com article).

### Conflict handling

If a sync PR is already open for a given post (detected by PR title or branch name
containing the post slug), the workflow skips creating a duplicate. If the post was
previously synced and merged (detected by `canonical_url` match in `_posts/`), the
workflow also skips it. There is no automatic update mechanism for edited posts — if
Joshua wants to reflect an innoq.com post update, he edits the local file manually.

---

## Consequences

### Positive

- Fully automated discovery: Joshua is notified via PR, never needs to monitor innoq.com
  for new articles.
- Draft-first approach: nothing goes public without explicit opt-in, satisfying Joshua's
  editorial control requirement.
- PR-based flow creates a clear audit trail of what was synced, when, and whether Joshua
  chose to publish it.
- RSS polling is self-sufficient: no innoq API, no webhook infrastructure, no coordination
  with innoq required.
- Legal/policy risk is contained: not republishing full bodies avoids the question of
  whether innoq's consent is needed.

### Negative / Trade-offs

- RSS feeds sometimes omit the full article body; excerpt-only posts are less useful for
  SEO and readers who find the site via search. This is accepted given the unresolved
  policy question.
- If innoq.com changes its feed URL or author-filter structure, the workflow will silently
  stop finding new posts. A monitoring alert (e.g. fail if feed is unreachable) should be
  added.
- Two-step flow (merge PR, then set `published: true`) adds friction compared to a
  one-click publish. This friction is intentional — it enforces the editorial gate.
- No automatic update sync: if Joshua significantly rewrites an innoq.com article, the
  local copy does not automatically reflect that. Accepted as low-frequency edge case.

---

## Alternatives Considered

### Auto-publish on merge

The PR merge immediately sets `published: true`. Rejected: removes Joshua's explicit gate
between "synced to repo" and "visible on site". Joshua wants to decide per-post whether
and when it appears.

### Manual copy

Joshua monitors innoq.com himself and manually copies content. Rejected: high friction,
inconsistent, defeats the low-maintenance goal.

### Webhook from innoq.com

innoq pushes a notification to a GitHub Actions endpoint on new publish. Rejected:
requires innoq's infrastructure cooperation, which adds coordination cost and a dependency
on their platform. RSS polling achieves the same discovery outcome with no external
coordination.

### HTML scraping (full body)

Instead of (or as fallback to) RSS, scrape the full article HTML from innoq.com. Not
adopted as primary mechanism: fragile against markup changes, and scraping full bodies
without permission is legally/ethically questionable. May be revisited if innoq grants
explicit permission to republish.

---

## Open Questions

- **Legal/policy:** Does republishing full innoq.com article bodies require innoq's
  explicit permission, even for Joshua as the author? Until this is confirmed, the sync
  workflow imports metadata and excerpt only. Action: Joshua to clarify with innoq.
- **RSS body coverage:** Does Joshua's innoq.com author RSS feed include full article
  bodies or only excerpts? This determines whether a scraping fallback is ever needed.

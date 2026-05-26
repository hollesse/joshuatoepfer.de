---
id: infra-002
title: "Decision: Content sync strategy (innoq.com → PR)"
type: decision
status: done
completed: 2026-05-26
context: infrastructure
depends_on: []
---

# Decision: Content sync strategy (innoq.com → PR)

## What needs to be decided
How the sync workflow detects new or updated posts on innoq.com authored by Joshua and
automatically opens a pull request to add them as syndicated posts in the Jekyll site.
The mechanism for discovery (RSS feed, sitemap, or innoq API) and the PR content format
need to be settled.

## Acceptance criteria
- [x] ADR committed under `.agentheim/knowledge/decisions/0002-content-sync-strategy.md`
- [x] Decision covers: discovery mechanism, trigger schedule, PR format, conflict handling
- [x] The ADR notes the open legal/policy question about republishing innoq.com content
- [x] Justification in the ADR matches the draft below (or user-amended version)

## Notes (ADR draft)

**Context:** Joshua publishes articles on innoq.com. He wants them mirrored on
joshuatoepfer.de with a link back to the original. The mirroring should happen
automatically with minimal manual work — Joshua reviews and merges a PR, but does
not manually copy content.

**Decision (proposed):** Use a scheduled GitHub Actions workflow (daily) that fetches
the innoq.com author RSS feed or sitemap filtered by Joshua's author profile, diffs
against existing `_posts/` files, and opens a PR for each new post found. The PR adds
a Jekyll post with `source: innoq`, `canonical_url`, and `published: false` frontmatter.
Joshua merges the PR (adding it to the repo) and separately sets `published: true` on
any post he chooses to make live. Nothing goes public without his explicit decision.

This draft-first approach eliminates any legal/policy concern about automatic republishing:
Joshua is always the gate between sync and visibility.

**Positives:**
- Fully automated discovery — Joshua never manually monitors innoq.com for new posts
- Draft-first means Joshua controls exactly what appears on his site and when
- PR-based review keeps a clear audit trail of what was synced
- RSS/sitemap approach requires no innoq API access or cooperation

**Negatives:**
- RSS feeds sometimes lack full post body; may need HTML scraping as fallback
- Needs periodic maintenance if innoq.com changes its feed format
- Two-step flow (merge PR + set published) is slightly more friction than one-click

**Alternatives considered:**
- Auto-publish on merge — removes Joshua's gate; rejected because he wants control
- Manual copy — too much friction, defeats the low-maintenance goal
- Webhook from innoq — requires innoq cooperation; RSS polling is self-sufficient

## Outcome

ADR written at `.agentheim/knowledge/decisions/0002-content-sync-strategy.md`.

The decision records: daily scheduled GitHub Actions workflow, RSS feed as the discovery
mechanism (no innoq API required), PR-per-new-post with `published: false` frontmatter,
conflict handling via `canonical_url` deduplication, and a two-step publish gate
(merge PR + separately set `published: true`). The ADR explicitly flags the open
legal/policy question about republishing full innoq.com article bodies, and defaults to
excerpt-only import until that is resolved with innoq.

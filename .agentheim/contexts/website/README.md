# Website

## Purpose
The Jekyll site — content model (posts, talks, pages), layouts, templates, and the
structures that turn markdown content files into a coherent personal website.
This is the primary deliverable: what visitors actually experience.

## Classification
Core

## Actors
- **Readers** — discover posts and talks, learn about Joshua, find upcoming events
- **Conference organizers** — check talk history and initiate speaker booking
- **Joshua** — writes personal posts, reviews sync PRs, manages talk entries

## Ubiquitous language
- **Post** — a written article with frontmatter: title, date, tags, source
- **Syndicated post** — a post originally published on innoq.com; includes a canonical
  link back and attribution; content is mirrored here for discoverability
- **Personal post** — a post exclusive to joshuatoepfer.de
- **Talk** — a presentation entry: title, event, date, abstract, and optional materials
  (slides URL, video URL)
- **Appearance** — a future-dated Talk representing an upcoming speaking engagement
- **Collection** — a Jekyll content collection grouping related entries (`_posts`, `_talks`)
- **Tag** — a topic label on a Post (e.g., `ensemble-programming`, `adhs`, `software-dev`)
- **Layout** — a Jekyll template defining the HTML structure for a given content type

## Aggregates
- **Post** — title + date + source form the identity; syndicated posts must retain the
  canonical source URL
- **Talk** — title + event + date define the identity; materials and video are optional

## Key events
- `PostPublished` — a post is visible to readers on the live site
- `TalkAdded` — a new talk entry is listed
- `AppearanceAnnounced` — an upcoming speaking event is listed

## Key commands
- Add personal post
- Add or update talk entry
- List posts by tag

## Relationships with other contexts
- **Conformist to:** design-system (uses its theme and tokens)
- **Receives content from:** infrastructure (sync workflows deposit content files here)

## Open questions
- Dedicated landing pages per topic (ADHS, Ensemble Programming, Software Dev) or
  tag-based sections?
- Will there be an "About" or "Now" page?
- Speaking/booking contact — a dedicated page or just an email link?

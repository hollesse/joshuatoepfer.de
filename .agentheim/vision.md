# Vision: joshuatoepfer.de

## Purpose
A personal website for Joshua Töpfer, software developer and IT consultant at innoq,
that serves as his primary online presence and anchor for building a personal brand across
three domains: Ensemble Programming, ADHS in der IT, and Software Development broadly.
It is a platform for his authentic voice — not a company page, but a professional identity
he owns and controls.

## Users
**IT professionals** — developers, consultants, and team leads who come across Joshua's
writing or talks and want to find more. They arrive with one of three entry points:
collaborative programming practices, ADHS in professional IT contexts, or general software
craftsmanship perspectives.

**Conference organizers and event hosts** — checking Joshua's speaker profile, past talks,
and upcoming appearances before making a booking decision.

**Professional contacts** — colleagues, potential clients, community members who want a
complete picture of who Joshua is and what he stands for.

## The problem
Joshua's content is currently fragmented: professional articles live on innoq.com under
a company umbrella, personal perspectives have no home, and there is no single place
where his expertise, talks, and professional identity are presented as a whole. His
personal brand has no anchor — people who find one piece of his work have no natural
path to the rest.

## What success looks like
- A visitor can discover Joshua's writing on any of his three topic areas in one place
- innoq.com articles are mirrored with a clear link back to the original source
- Conference talks are listed with materials; upcoming appearances are visible
- A first-time visitor understands within seconds who Joshua is and what he's about
- New content (synced from innoq.com or added manually) appears with minimal manual effort
- The site is low-maintenance and does not require active tending to stay current

## Non-goals
- E-commerce, paid content, or subscriptions
- Community features (comments, forums, user accounts)
- A company portfolio or innoq marketing page
- Content unrelated to the professional/IT context

## Ubiquitous language (seed)
- **Post** — a written article, either originally published here (personal post) or
  republished from innoq.com (syndicated post) with a canonical link back to the original
- **Syndicated post** — a post whose primary source is innoq.com; always carries attribution
  and a link back; content is mirrored here for discoverability
- **Personal post** — a post exclusive to joshuatoepfer.de
- **Draft post** — a post created by the sync workflow but not yet published; invisible to
  visitors until Joshua explicitly sets it to published
- **Talk** — a conference or community presentation Joshua has given or is scheduled to give,
  with associated metadata: event, date, abstract, and optional materials
- **Appearance** — an upcoming speaking engagement; a future-dated Talk
- **Sync workflow** — a scheduled GitHub Actions job that detects new innoq.com posts or
  external talk data and opens a pull request to add them to the site as draft posts
- **Sync PR** — a pull request created by a sync workflow, containing new draft content
  files ready for Joshua's review and publish decision

## Open questions
- Should syndicated and personal posts be visually distinguished in listings?
- Will talk materials (slides) be hosted directly or linked externally (e.g., Speakerdeck)?
- Should ADHS, Ensemble Programming, and general Software Dev have dedicated landing pages
  or just be tag-based sections?

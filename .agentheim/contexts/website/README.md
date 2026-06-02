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

### Content
- **Post** — a written article with frontmatter: title, date, tags, source
- **Syndicated post** — a post originally published on innoq.com; includes a canonical
  link back and attribution; content is mirrored here for discoverability
- **Personal post** — a post exclusive to joshuatoepfer.de
- **Talk** — a presentation entry: title (`what`), event (`where`), city, date,
  type (`talk` / `workshop` / `keynote`), duration, abstract, and optional materials
  (`slides`, `video`); status is either `upcoming` or `past`
- **Appearance** — a future-dated Talk representing an upcoming speaking engagement
- **Collection** — a Jekyll content collection grouping related entries (`_posts`);
  talks are kept in `_data/talks.yml` rather than a collection
- **Topic** — a coarse-grained content axis used to group posts and drive the
  filter chips on the blog listing. Three values today: `ensemble`, `adhs`, `softdev`
- **Tag** — a fine-grained label on a Post (e.g., `ensemble-programming`, `adhs`); a
  post belongs to exactly one **topic** but may carry multiple tags
- **Focus area (Schwerpunkt)** — one of the three topics presented as a card on the
  homepage with label, blurb, and post count; canonical data in `_data/focus.yml`
- **Quick fact** — a key/value pair shown in the sidebar on `/ueber-mich/`; canonical
  data in `_data/about.yml` under `quick_facts`
- **Legal page** — a page rendered with the `page` layout, used for `/impressum/` and
  `/datenschutz/`; frontmatter-driven (`title`, optional `subtitle`, `last_updated`)

### Layout vocabulary
- **Layout** — a Jekyll template defining the HTML structure for a given content type
- **Post hero** — the banner section at the top of an individual post: back-link,
  eyebrow (topic · date), accent-marked title, optional subtitle, meta-line
  (reading time, syndication note). Class `.post-hero`
- **Table of contents (TOC)** — the sticky aside on `/blog/:slug/` that links to
  the post's h2 sections; rebuilt client-side by `assets/js/theme-toggle.js`. Class
  `.post-toc`
- **Prev/next pager** — the two-column footer block on a post linking to the
  chronologically older / newer post. Class `.post-pager`
- **Related-posts block** — up to three other posts of the same topic shown at the
  bottom of a post. Class `.related-posts`
- **Year-divider** — the large year marker between groups of posts on `/blog/`,
  with year + count. Class `.blog-year-divider`
- **Filter-chip** — the topic filter buttons on `/blog/` (Alle / Ensemble / ADHS /
  Software Dev); JS-driven via `assets/js/blog-filter.js`. Class `.filter-chip[data-topic]`
- **Speaker profile** — the call-to-action block at the bottom of `/talks/` with
  topics, formats, and booking links. Class `.speaker-section` / `.speaker-block`

## Aggregates
- **Post** — title + date + source form the identity; syndicated posts must retain the
  canonical source URL
- **Talk** — `what` + `where` + `date` define the identity; `slides` and `video` are
  optional and only meaningful for `status: past`

## Key events
- `PostPublished` — a post is visible to readers on the live site
- `TalkAdded` — a new talk entry is listed
- `AppearanceAnnounced` — an upcoming speaking event is listed

## Key commands
- Add personal post
- Add or update talk entry
- List posts by tag

## Relationships with other contexts
- **Conformist to:** design-system (uses its theme, tokens, and component vocabulary;
  see ADR-0005 for the canonical reference)
- **Receives content from:** infrastructure (sync workflows deposit content files here)

## Open questions
- Speaking/booking contact — currently surfaced via the speaker-profile block on
  `/talks/` plus the contact CTA on `/ueber-mich/`. Whether a dedicated booking
  flow (form, calendar, anything beyond mailto) is needed is still open.

## Pages inventory

Every route on the site, the layout it uses, where its data comes from, and which
shared `_includes/` and design-system components it pulls in. Design-system component
names follow ADR-0005 section 7.

All pages share the chrome from `_layouts/default.html`: `topnav.html` + skip-link
+ `<main>` + `footer.html`, plus `head-canonical.html` and the theme-toggle script.
`theme-toggle.html` is rendered inside the topnav.

### `/` — homepage
- **Layout:** `home` (`_layouts/home.html`)
- **Data sources:**
  - `site.posts` filtered to `published != false`, sliced to first 5 (newest posts)
  - `site.data.talks` filtered to `status: upcoming`, sorted by date; if
    that filter is empty, falls back to the **3 most recent past talks**
    (sorted descending by date), rendered under the heading "ZULETZT AUF
    DER BÜHNE" instead of "KOMMENDE TALKS". The section is hidden only if
    both sets are empty.
  - `site.data.focus` (the three focus-area cards)
  - `site.portrait_image` (config; portrait at `assets/images/portrait.jpg`)
- **Includes used:** `post-card.html` (style `compact`), `talk-card.html` (variant `home`)
- **Component vocabulary:** `.v1-hero`, `.v1-portrait` (with `--placeholder` fallback),
  `.v1-section-head`, `.v1-focus` + `.focus-card`, `.v1-talk`, `.accent-mark`,
  `.mono`, `.em-prefix`, `.rule`

### `/blog/` — blog listing
- **Layout:** `blog` (`_layouts/blog.html`); source page is `blog/index.html`
- **Data sources:** `site.posts` filtered to `published != false`, grouped by year
  (`group_by_exp` on `%Y`); per-topic counts computed inline
- **Includes used:** none beyond the shared chrome (rows are inlined)
- **Client-side:** `assets/js/blog-filter.js` (loaded by `default.html` only when
  `page.layout == "blog"`) toggles row visibility by `data-topic`
- **Component vocabulary:** `.blog-hero`, `.blog-filters` + `.filter-chip[data-topic]`,
  `.blog-year` + `.blog-year-divider`, `.blog-post-row` (with `.date`, `.src`, `.topic-tag`),
  `.label-eyebrow`, `.accent-mark`

### `/blog/:slug/` — individual post
- **Layout:** `post` (`_layouts/post.html`); source pages live in `_posts/*.md`
- **Data sources:** post frontmatter (`title`, `subtitle`, `date`, `topic`, `source`,
  `canonical_url`, `reading_time`, `published`); `site.posts` for related-posts
  matching on `topic` and for pager prev/next
- **Includes used:** `post-card.html` (style `related`) for the related-posts block;
  `head-canonical.html` adds the canonical `<link>` for syndicated posts
- **Component vocabulary:** `.post-hero` (with `.back-link`, `.eyebrow`, `.subtitle`,
  `.meta-line`, `.accent-mark`), `.post-body-layout` + `.post-toc` aside + `.post-body`,
  `.post-pager`, `.related-posts`

### `/talks/` — talks index
- **Layout:** `talks` (`_layouts/talks.html`); source page is `talks/index.html`
- **Data sources:** `site.data.talks` split into `upcoming` (sorted ascending) and
  `past` (sorted descending)
- **Includes used:** `talk-card.html` (variants `upcoming` and `past`)
- **Component vocabulary:** `.talks-hero`, `.talks-section` (`--upcoming` / `--past`)
  with `.talks-section-head`, `.talks-row` (with `--past` modifier) + `.type-pill`,
  `.speaker-section` + `.speaker-block` + `.topic-chips` + `.chip` + `.formats` +
  `.downloads`, `.accent-mark`, `.label-eyebrow`

### `/ueber-mich/` — about
- **Layout:** `about` (`_layouts/about.html`); source page is `ueber-mich/index.md`
- **Data sources:** `site.data.about.quick_facts`; page frontmatter (`eyebrow`,
  `headline`, `lead`); page markdown body; `site.portrait_image`
- **Includes used:** none beyond the shared chrome
- **Component vocabulary:** `.about-hero` (re-using `.hero`), `.about-portrait` (with
  `.v1-portrait--placeholder` fallback), `.about-body-layout` + `.about-body-grid` +
  `.post-body` + `.quick-facts` (`<dl>`), `.contact-cta`, `.accent-mark`,
  `.label-eyebrow`

### `/impressum/` — legal: imprint
- **Layout:** `page` (`_layouts/page.html`); source page is `impressum/index.md`
- **Data sources:** page frontmatter only (`title`, optional `subtitle`,
  `last_updated`) plus the markdown body
- **Includes used:** none beyond the shared chrome
- **Component vocabulary:** `.legal-hero` (with `.back-link`, optional `.updated`),
  `.legal-body` + `.post-body`, `.accent-mark`

### `/datenschutz/` — legal: privacy
- **Layout:** `page` (`_layouts/page.html`); source page is `datenschutz/index.md`
- **Data sources:** page frontmatter only (`title`, optional `subtitle`,
  `last_updated`) plus the markdown body
- **Includes used:** none beyond the shared chrome
- **Component vocabulary:** same as `/impressum/`

### Data file shapes (canonical)

- **`_data/talks.yml`** — list of talks. Each entry: `date` (ISO), `what`, `where`,
  `city`, `status` (`upcoming` | `past`), `type` (`talk` | `workshop` | `keynote`),
  `duration` (minutes), `abstract`, optional `slides` (URL), optional `video` (URL),
  `source` (`innoq` | `manual`), optional `source_url` (required when
  `source: innoq`). The `source` marker distinguishes sync-maintained entries
  from hand-edited ones — `source: innoq` entries are owned by the INNOQ
  talks sync workflow (infrastructure BC, infra-011 / ADR-0007); `source: manual`
  entries are read-skipped by the sync and survive across runs untouched.
  `source_url` is the canonical INNOQ detail URL and acts as the cross-run
  identity key. The layout (`_layouts/talks.html`) and card include
  (`_includes/talk-card.html`) do not render `source` or `source_url`; they
  are pure sync metadata.
- **`_data/focus.yml`** — list of focus-area cards. Each entry: `key` (matches
  `post.topic`), `label`, `blurb`, `count`.
- **`_data/about.yml`** — top-level key `quick_facts`: list of `{key, value}` pairs
  for the about-page sidebar.

### Note on legacy `/posts/`
The earlier `/posts/` listing (introduced in website-002) has been removed; the blog
listing now lives at `/blog/`. The topnav still maps `/posts/` URLs to the Blog tab
defensively, but no source file generates `/posts/` anymore.

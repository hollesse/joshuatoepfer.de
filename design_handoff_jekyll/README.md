# Handoff: joshuatoepfer.de — Jekyll-Umsetzung

## Übersicht
Hi! Du bekommst hier ein vollständiges Design für **joshuatoepfer.de** — ein persönliches Blog & Speaker-Profil. Das Design existiert als React/JSX-Prototyp in den beigelegten HTML-Dateien. Deine Aufgabe: das ganze als Jekyll-Site umsetzen.

## Über die Design-Dateien
**Wichtig**: Die Dateien hier sind **Design-Referenzen**, keine Production-Code-Vorlagen. Sie zeigen, wie das Endergebnis aussehen und sich anfühlen soll. Die Aufgabe ist, **diese Designs in einer sauberen Jekyll-Site nachzubauen** — mit Liquid-Templates, sinnvollen `_layouts/`, `_includes/`, `_data/`-Dateien und Markdown-Posts. Den React/Babel-Code direkt zu portieren ist **nicht** das Ziel.

Die einzige Datei, die du **fast 1:1 übernehmen** kannst, ist `styles.css` — das ist plain CSS und enthält alle Design-Tokens und Container-Queries.

## Fidelity
**High-fidelity.** Alle Farben, Schriftgrößen, Abstände, Hover-States und Container-Query-Breakpoints sind final. Pixelgenau umsetzen.

## Zielarchitektur (Vorschlag)

```
joshuatoepfer.de/
├── _config.yml
├── _data/
│   └── talks.yml             # Talks-Liste (siehe homepage-v1-v2.jsx TALKS)
├── _includes/
│   ├── topnav.html           # Wordmark + Nav + ThemeToggle
│   ├── footer.html           # 4-Spalten-Footer + Baseline
│   ├── theme-toggle.html     # Sun/Moon Button (Vanilla JS)
│   ├── post-card.html        # Eine Post-Zeile in der Blog-Liste
│   └── talk-card.html        # Eine Talk-Zeile
├── _layouts/
│   ├── default.html          # Topnav + {{ content }} + Footer
│   ├── home.html             # Startseite (extends default)
│   ├── blog.html             # Blog-Übersicht (extends default)
│   ├── post.html             # Post-Seite mit Hero-Banner + TOC-Aside
│   ├── talks.html            # Talks-Seite + Speaker-Profil
│   ├── page.html             # Standard-Textseite (für Impressum/Datenschutz/Über mich)
│   └── about.html            # Über mich (extends page, mit Porträt)
├── _posts/
│   └── 2026-01-30-pairing-mit-dem-adhs-brain.md
├── _sass/
│   ├── tokens.scss           # Design-Tokens (Farben, Akzente, Mode-Switch)
│   ├── typography.scss       # Geist + Geist Mono Setup
│   ├── components.scss       # .topnav, .row, .talk, .chip, .post-body, …
│   └── responsive.scss       # Container Queries
├── assets/
│   ├── css/
│   │   └── main.scss         # @import der _sass/-Partials
│   ├── js/
│   │   └── theme-toggle.js   # Vanilla JS für den Mode-Toggle
│   └── images/
│       └── portrait.jpg      # Joshuas Porträt
├── blog/
│   └── index.html            # layout: blog, listet site.posts
├── talks/
│   └── index.html            # layout: talks
├── ueber-mich/
│   └── index.html            # layout: about
├── impressum/
│   └── index.html            # layout: page
├── datenschutz/
│   └── index.html            # layout: page
└── index.html                # layout: home, listet 5 neueste Posts + 4 nächste Talks
```

## Seiten (Screens)

### 1. Startseite (`index.html`, layout: home)
**Zweck**: Erste Berührung. Großer Name, Bio, neueste Posts, Schwerpunkte, kommende Talks.

**Layout**:
- Topnav
- Hero: Grid 1fr / 460px, Headline links („Joshua Töpfer.") + Bio darunter, Porträt rechts (Duotone)
- Rule
- Section „NEUESTE BEITRÄGE" (5 Items, `_layouts/blog/`-Filterung: neueste 5)
- Section „MEINE SCHWERPUNKTE" (Grid 1fr 1fr 1fr, 3 Themen-Karten)
- Section „KOMMENDE TALKS" (Grid 300px / 1fr, nur `status: upcoming`)
- Footer

**Datenquellen**:
- Posts: `site.posts | slice: 0, 5`
- Talks: `site.data.talks | where: "status", "upcoming"`
- Schwerpunkte: könnten in `_data/topics.yml` oder hardcoded im Layout

**Datei zum Anschauen**: `homepage-v1-v2.jsx` → Komponente `VariantStatement`

### 2. Blog-Übersicht (`/blog/`, layout: blog)
**Zweck**: Alle Posts chronologisch, nach Jahr gruppiert.

**Layout**:
- Topnav
- Hero („Notizen aus der Praxis.")
- Filter-Chips (Alle / Ensemble / ADHS / Software Development)
- Pro Jahr: Großer Jahres-Divider (84px) + Posts-Liste (Grid 180px / 1fr / 160px)

**Liquid-Pseudocode**:
```liquid
{% assign by_year = site.posts | group_by_exp: "p", "p.date | date: '%Y'" %}
{% for year_group in by_year %}
  <div class="blog-year-divider">
    <h2>{{ year_group.name }}</h2>
    <div class="mono">{{ year_group.items.size }} Beiträge</div>
  </div>
  {% for post in year_group.items %}
    {% include post-card.html post=post %}
  {% endfor %}
{% endfor %}
```

**Filter-Logik**: Mit Vanilla JS am Frontend (Buttons toggeln `data-topic`-Filter auf der Liste). Kein Server-Reload nötig.

**Datei zum Anschauen**: `blog-page.jsx` → `BlogPage`

### 3. Post-Seite (`/blog/:slug/`, layout: post)
**Zweck**: Ein einzelner Blogpost.

**Layout**:
- Topnav
- Hero-Banner (full-bleed, leicht abgesetzter Hintergrund):
  - „← Zurück zum Blog" oben links
  - Eyebrow: Topic · Datum (in Akzent)
  - Riesen-Titel (112px) mit Akzent-Punkt
  - Subtitle
  - Bottom-Meta-Zeile: Lesezeit · ggf. „Erscheint auch auf innoq.com"
- Two-column Body (Grid 240px / 1fr):
  - Sticky TOC-Aside links (basiert auf H2-Headings im Post)
  - Artikeltext rechts (max-width ~72ch)
- Prev/Next-Pager (Grid 1fr 1fr)
- „Mehr zum Thema X" (Related Posts)
- Footer

**TOC-Generierung**: Per Liquid + Plugin (z. B. `jekyll-toc`) oder per Vanilla JS aus den `h2`-Elementen.

**Front Matter Beispiel**:
```yaml
---
layout: post
title: "Pairing mit dem ADHS-Brain — vier Tricks, die wirklich helfen"
subtitle: "Kurze Iterationen, klare Rollen, externer Fokus-Timer..."
date: 2026-01-30
topic: adhs                    # ensemble | adhs | softdev
source: innoq                  # optional
canonical: "https://innoq.com/..."  # optional
reading_time: 8
---
```

**Datei zum Anschauen**: `post-page.jsx` → `PostPage`

### 4. Talks-Seite (`/talks/`, layout: talks)
**Zweck**: Übersicht aller Talks + Speaker-Buchungsinfo.

**Layout**:
- Topnav
- Hero („Auf der Bühne.")
- Section „KOMMENDE" (alle mit `status: upcoming`)
- Section „VERGANGENE" (mit Slides/Video-Links wo vorhanden)
- Speaker-Profil-Block am Ende (leicht abgesetzter Hintergrund):
  - 2-Spalten: links Headline + Bio, rechts Themen-Chips + Formate
- Footer

**Daten**: `_data/talks.yml`
```yaml
- date: 2026-06-18
  what: "ADHS in der Softwareentwicklung"
  where: "Karlsruher Entwicklertag"
  city: Karlsruhe
  status: upcoming                 # upcoming | past
  type: talk                       # talk | workshop | keynote
  duration: 45
  abstract: "..."
  slides: "#"                      # optional
  video: "#"                       # optional
```

**Datei zum Anschauen**: `talks-page.jsx` → `TalksPage`

### 5. Über mich (`/ueber-mich/`, layout: about)
**Zweck**: Bio, Porträt, Quick-Facts.

**Layout**:
- Topnav
- Hero (Grid 1fr / 460px): Headline links („Hallo, ich bin Joshua."), Porträt rechts
- Body (Grid 1fr / 280px): Bio-Fließtext links, sticky Quick-Facts-Aside rechts
- Contact-CTA-Section („Lust auf Ensemble, einen Talk oder einfach Hallo?")
- Footer

**Quick-Facts**: könnten in Front Matter oder `_data/about.yml` liegen.

**Datei zum Anschauen**: `about-page.jsx` → `AboutPage`

### 6. Standard-Textseiten (Impressum, Datenschutz, layout: page)
**Zweck**: Wiederverwendbares Template für reine Textseiten.

**Layout**:
- Topnav
- Hero: „← Zurück zur Startseite" + großer Titel (72px) mit Akzent-Punkt + optional Subtitle
- Body: 72ch-Lesespalte
- Footer

**Front Matter**:
```yaml
---
layout: page
title: "Impressum"
subtitle: "Optional"                 # optional
permalink: /impressum/
---
```

**Datei zum Anschauen**: `legal-page.jsx` → `LegalPage`

## Globale Patterns

### Topnav (`_includes/topnav.html`)
- Wordmark links: „Joshua Töpfer." (Geist 24px, weight 500, Akzent-Punkt)
- Nav rechts: 4 Items (Geist Mono Caps 12px) + Theme-Toggle ganz rechts
- `data-current` Markierung über `{% if page.url == "/blog/" %}is-current{% endif %}` etc.
- Borderline-bottom

### Footer (`_includes/footer.html`)
- 4-Spalten Grid (Kontakt / Anderswo / Site / Rechtliches)
- Baseline: © + Socials-Quickref + „Built with Jekyll"

### Theme-Toggle (Vanilla JS)
- Sun-Icon im Dark Mode, Moon im Light Mode
- Klick toggelt `data-mode="dark|light"` auf `<html>`
- Persistent via `localStorage.setItem("jt-mode", ...)`
- Beim Page-Load: aus localStorage oder system preference

### Akzentfarben
Default ist Amber. Falls du eine Auswahl als Setting bauen willst, alle vier:
```css
[data-accent="amber"] { --accent: oklch(0.80 0.14 78); /* … */ }
[data-accent="coral"] { --accent: oklch(0.74 0.17 32); /* … */ }
[data-accent="blue"]  { --accent: oklch(0.78 0.13 240); /* … */ }
[data-accent="lime"]  { --accent: oklch(0.86 0.18 130); /* … */ }
```
Mit Light-Mode-Varianten. Siehe `styles.css` Anfang.

## Responsive / Container Queries

Wichtig: **Container Queries** statt klassischer Media Queries. Der Root-Container (`.jt`) hat `container-type: inline-size; container-name: jt;`. Alle responsive Overrides sind in `@container jt (max-width: 720px) { … }`.

Das hat den Vorteil, dass die Seite responsiv ist auch wenn du sie z. B. in einem schmalen iframe einbettest. Funktioniert in allen modernen Browsern (>2023).

Wenn du klassische `@media` nutzen willst, ist das auch ok — dann breakpoint bei ~720px.

## Design Tokens

**Farben (Dark default)**
- `--bg: #0d0d0d`
- `--bg-elev: #141414`
- `--fg: #ededed`
- `--fg-dim: #9a9a9a`
- `--fg-faint: #5a5a5a`
- `--rule: rgba(255,255,255,0.10)`
- `--rule-strong: rgba(255,255,255,0.22)`
- `--accent: oklch(0.80 0.14 78)` (Amber Dark)

**Farben (Light)**
- `--bg: #f7f7f5`
- `--bg-elev: #ffffff`
- `--fg: #141414`
- `--fg-dim: #5e5e5e`
- `--fg-faint: #a3a3a3`
- `--rule: rgba(0,0,0,0.10)`
- `--rule-strong: rgba(0,0,0,0.22)`
- `--accent: oklch(0.58 0.14 60)` (Amber Light)

**Typografie**
- Sans: `Geist`, ui-sans-serif, system-ui (Variable Font)
- Mono: `Geist Mono`, ui-monospace (Variable Font)
- Via Google Fonts: `https://fonts.googleapis.com/css2?family=Geist:wght@100..900&family=Geist+Mono:wght@100..900&display=swap`
- Body: 16px / 1.45, letter-spacing -0.005em
- Headings: weight 380-460, letter-spacing -0.02 bis -0.045em je nach Größe

**Spacing**
- Section Desktop-Padding: 88px 80px (hero: 100-120px top)
- Section Mobile-Padding: 56px 22px
- Standard-Gap: 24-48px

**Akzent-Punkt**
Klassisches Wiederholungsmuster: Jeder Headline-Punkt ist in `var(--accent)`. Beispiele: „Töpfer**.**", „Notizen aus der Praxis**.**", „Auf der Bühne**.**". Das ist die kleinste Brand-Identität der Seite — bitte konsequent durchziehen.

## Interaktionen

- **Link-Hover**: Animierter Underline (background-image grow), siehe `.link` in styles.css
- **Post-Row-Hover**: Titel färbt sich in Akzent, Pfeil rechts auch
- **Theme-Toggle**: 200ms color transition
- **Mobile-Menu**: Keiner aktuell — die 4 Nav-Items werden auf Mobile nur kleiner (10px), kein Hamburger

## Assets

- **Porträt**: Joshua liefert dir das echte Foto. Im Design ist ein Image-Slot (460×620 hochformat) mit Duotone-Filter: `grayscale(1) contrast(1.1) brightness(0.92)`. Wende den auf das echte Foto an.
- **Fonts**: Geist + Geist Mono via Google Fonts CDN (oder local hosting für Datenschutz-Konformität — Joshua bevorzugt das)
- **Favicon**: nicht designed — kann er später nachreichen

## Inhalte

Die Texte in den Design-Dateien (Bio, Posts, Talks, Manifest) sind **Joshua-eigen** und können direkt übernommen werden. Sie sind authentisch geschrieben, nicht Platzhalter.

## Dateien in diesem Bundle

- `index.html` — der Design-Canvas mit allen Varianten (öffnen, anschauen, vergleichen)
- `styles.css` — alle Design-Tokens, Komponenten-Styles, Container-Queries. Diese Datei kannst du fast 1:1 in dein Jekyll-Setup übernehmen.
- `homepage-v1-v2.jsx` — Startseite, Daten-Konstanten (POSTS, TOPIC_META, TOPIC_FILTERS, FOCUS, TALKS), Helpers (TopNav, Footer, ThemeToggle, PostsList)
- `blog-page.jsx` — Blog-Übersicht
- `post-page.jsx` — Post-Seite
- `talks-page.jsx` — Talks-Seite + Speaker-Block
- `about-page.jsx` — Über mich
- `legal-page.jsx` — Standard-Textseiten-Template (Impressum + Datenschutz)
- `image-slot.js`, `design-canvas.jsx`, `tweaks-panel.jsx`, `app.jsx` — Design-Canvas-Infrastruktur, **nicht für Jekyll relevant**, kannst du ignorieren

## Empfohlene Reihenfolge der Umsetzung

1. **Jekyll-Skeleton** aufsetzen: `_config.yml`, Basis-Layout, Topnav + Footer
2. **CSS portieren**: `styles.css` in `_sass/`-Partials aufteilen, `main.scss` baut zusammen
3. **Startseite**: Daten hardcoded zuerst, dann Posts/Talks dynamisch
4. **Standard-Textseiten** (Impressum/Datenschutz): einfachstes Layout, gutes Test-Bed für Layouts
5. **Über mich**: Layout testet das `image-slot`-Pattern
6. **Blog-Übersicht + Post-Seite**: zusammen, weil sie sich Front-Matter teilen
7. **Talks-Seite** mit `_data/talks.yml`
8. **Theme-Toggle**: zuletzt, einfaches Vanilla JS

## Fragen

Wenn was unklar ist:
- Schau dir die JSX-Dateien an — die enthalten alle Werte (Schriftgrößen, Paddings, Farben) inline
- Schau dir `styles.css` an — da ist der Großteil der Design-Tokens und Komponenten-Styles
- Öffne `index.html` im Browser — der Design-Canvas zeigt alle Seiten Desktop + Mobile nebeneinander
- Frag Joshua, wenn was inhaltlich unklar ist

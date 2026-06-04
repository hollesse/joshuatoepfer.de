---
id: website-010
title: Block search-engine indexing until launch
status: done
type: chore
context: website
created: 2026-06-04
completed: 2026-06-04
commit: d51ac0b
depends_on: []
blocks: []
tags: [seo, launch, visibility, robots, privacy]
related_adrs: []
related_research: []
prior_art: []
---

## Why
Die Seite ist noch im Aufbau (laufende Doku-/Datenschutz-/Visual-Korrekturen
in der letzten Woche, das Talks-Listing nutzt noch teilweise INNOQ-Sync-Daten,
weitere Backlog-Items folgen). Joshua möchte vermeiden, dass Suchmaschinen
Inhalte indexieren, die sich in absehbarer Zeit noch verändern oder
ergänzt werden — und dass Visitor:innen über Google auf einen
„unfertigen" Stand stoßen, bevor das gewünschte erste Bild der Seite
steht. Sobald Joshua sagt „ist soweit", wird die Blockade wieder
entfernt (siehe Reverse-Anleitung unten).

## What
Zwei sich ergänzende Mechanismen einbauen, die Crawler / Suchmaschinen
explizit auffordern, **nichts zu indexieren**:

1. **`robots.txt`** an der Site-Root mit
   `User-agent: * / Disallow: /` — fängt diejenigen Bots ab, die `robots.txt`
   respektieren (Googlebot, Bingbot, …) und blockt sie vor dem Crawl.
2. **`<meta name="robots" content="noindex, nofollow">`** im
   globalen `<head>` (`_layouts/default.html` oder
   `_includes/head-canonical.html`) — fängt Bots, die das Meta-Tag
   stärker honorieren als `robots.txt`, und sichert per-Seite ab.

Beide zusammen sind defensive Layering. Einzeln ließe sich jeweils
argumentieren, dass es ausreicht; zusammen ist die Wirkung eindeutig.

## Acceptance criteria
- [ ] `_site/robots.txt` existiert nach `bundle exec jekyll build`
  und enthält mindestens:
  ```
  User-agent: *
  Disallow: /
  ```
- [ ] Jede gerenderte HTML-Seite im `_site/` enthält im `<head>`
  ein `<meta name="robots" content="noindex, nofollow">`-Tag.
  Verifikation: `grep -L 'name="robots"' _site/**/*.html` (oder
  äquivalent) liefert **keine** Trefferdatei.
- [ ] Existierende Funktionalität (Theme-Toggle, Email-Komponenten,
  Topnav, etc.) bleibt unverändert.
- [ ] `bundle exec jekyll build --quiet` exit 0.

## Notes

### Wahl der Implementierungs-Stelle für das Meta-Tag

Empfohlen: Tag in `_includes/head-canonical.html` ergänzen, weil dort
schon `head`-spezifische Markup-Logik gebündelt ist und der Include
in `_layouts/default.html` einmalig per `{% include head-canonical.html %}`
verwendet wird. Falls es dort nicht sauber reinpasst, alternativ
direkt in `_layouts/default.html` zwischen `<head>` und dem ersten
`<link>`. Beides ist akzeptabel — der Worker entscheidet, was sich
ins existierende Pattern besser einfügt.

### `jekyll-seo-tag` und `jekyll-sitemap`

Die Plugins sind beide aktiv (`_config.yml > plugins`). Für diesen
Task gibt es **keine** Konflikte:

- `jekyll-seo-tag` (`{% seo %}` in `_layouts/default.html`) generiert
  diverse `<meta>`-Tags, aber **kein** `<meta name="robots">`, solange
  nicht explizit `seo.noindex` gesetzt ist. Eine Alternative zur
  manuellen Meta-Tag-Ergänzung wäre also: `_config.yml` um
  `seo: { noindex: true }` ergänzen. Beide Wege sind valide; der
  manuelle Meta-Tag ist robuster (greift auch wenn `{% seo %}` mal
  entfernt wird).
- `jekyll-sitemap` generiert weiterhin `_site/sitemap.xml`. Das ist
  **OK**: Bots, die `noindex` respektieren, indexieren auch
  Sitemap-URLs nicht. Wir lassen das Plugin aktiv, damit es post-launch
  ohne Plugin-Reaktivierung sofort wieder die Sitemap mit ausliefert.

### Reverse-Anleitung (so wird der Block entfernt, sobald die Seite live gehen soll)

1. Lösche die Datei `robots.txt` im Repo-Root.
2. Entferne den `<meta name="robots" content="noindex, nofollow">`-Tag
   aus dem `head`-Markup wieder (oder, falls die `seo.noindex`-Variante
   gewählt wurde, entferne den Eintrag aus `_config.yml`).
3. Build laufen lassen, kontrollieren dass die Tags weg sind, pushen.
4. Bei Google Search Console manuell eine Re-Indexierung anstoßen,
   sonst dauert es länger.

Diese Anleitung ist hier festgehalten statt als separater
Folge-Task — der Reverse ist klein, Symmetrie-Fix, und ein Backlog-
Eintrag dafür würde nur als Hängematte rumliegen, bis Joshua entscheidet
„jetzt".

### Out of scope

- HTTP Basic Auth oder andere Zugriffssperren — der Wunsch ist
  „nicht indexiert", nicht „nicht erreichbar". Wer die URL kennt,
  soll die Seite ansehen können.
- `X-Robots-Tag` HTTP-Header — auf GitHub Pages nicht selbst setzbar.
  Die zwei Mechanismen oben sind das, was wir auf GitHub Pages
  realistisch tun können.
- Sitemap deaktivieren oder verstecken — siehe oben, nicht nötig.

## Outcome

Defensive Zwei-Schichten-Indexierungs-Blockade aufgesetzt, solange
die Seite noch im Pre-Launch-Zustand ist:

- **`/robots.txt`** (Repo-Root, neu): `User-agent: * / Disallow: /`
  mit Kommentarzeile, die den Zweck und die Reverse-Anleitung
  referenziert. Jekyll kopiert die Datei front-matter-los direkt
  nach `_site/robots.txt`.
- **`<meta name="robots" content="noindex, nofollow">`** ergänzt in
  `_includes/head-canonical.html`, sodass das Tag auf jeder über
  `_layouts/default.html` gerenderten HTML-Seite landet. Verifiziert
  via `grep -rL 'name="robots"' _site/ --include="*.html"` →
  keine Treffer (alle 9 HTML-Seiten haben das Tag).

`_config.yml` blieb unangetastet (`jekyll-seo-tag` und
`jekyll-sitemap` bleiben aktiv — die Sitemap-Generierung schadet
nicht, weil `noindex`-konforme Bots Sitemap-URLs ebenfalls nicht
indexieren).

Reverse-Anleitung steht oben unter „Reverse-Anleitung". BC-README
hat unter Pages-Inventory / Shared-Chrome und in einer neuen
Sektion „Site-wide files" einen kurzen Hinweis bekommen, dass das
ein temporärer Launch-Block ist.

Key files:
- `/Users/joshuatopfer/Documents/Projekte/Privat/joshuatoepfer.de/robots.txt`
- `/Users/joshuatopfer/Documents/Projekte/Privat/joshuatoepfer.de/_includes/head-canonical.html`
- `/Users/joshuatopfer/Documents/Projekte/Privat/joshuatoepfer.de/.agentheim/contexts/website/README.md`

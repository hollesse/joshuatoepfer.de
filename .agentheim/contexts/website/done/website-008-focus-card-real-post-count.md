---
id: website-008
title: Focus card post count — derive from real posts instead of hardcoded number
status: done
type: bug
context: website
created: 2026-06-03
completed: 2026-06-03
commit: da6947e
depends_on: []
blocks: []
tags: [homepage, focus, count, schwerpunkte]
related_adrs: []
related_research: []
prior_art: []
---

## Why
Auf der Startseite zeigt die Sektion **"MEINE SCHWERPUNKTE"** drei Karten — eine pro
Topic (`ensemble`, `adhs`, `softdev`). Jede Karte trägt einen Counter `{{ f.count }} BEITRÄGE`,
der aus `_data/focus.yml` kommt. Dort stehen aktuell die hartkodierten Fantasie-Zahlen
`14`, `9`, `27`, die nichts mit den tatsächlich publizierten Posts zu tun haben (real:
0/0/0 bzw. 1/0/0, je nach genauer Zählweise). Das ist nicht nur falsch, sondern rottet
mit jedem Sync-PR weiter, weil nichts den Wert pflegt.

## What
Den Count am Build-Zeitpunkt aus `site.posts` ableiten — für jedes Focus-Item die
Anzahl der publizierten Posts mit passendem `post.topic` zählen — und das Feld
`count` aus `_data/focus.yml` entfernen (es ist tote Daten, sobald die Berechnung
in Liquid passiert).

## Acceptance criteria
- [ ] `_layouts/home.html` berechnet pro Focus-Card die Anzahl Posts via Liquid:
      `site.posts | where_exp: "p", "p.published != false" | where: "topic", f.key | size`
      (oder äquivalent — Ergebnis muss die tatsächliche Zahl ungezählter
      published Posts mit `topic == f.key` sein).
- [ ] `_data/focus.yml` enthält **keinen** `count`-Key mehr; die Datei behält nur
      `key`, `label`, `blurb` pro Eintrag.
- [ ] Die Karten zeigen die korrekte Zahl für alle drei Topics (heute: vermutlich
      `1 / 0 / 0`, je nachdem ob `2026-05-27-hello-welt.md` und/oder die innoq-Posts
      ein `topic`-Frontmatter tragen — der Count spiegelt das Ist).
- [ ] `bundle exec jekyll build` läuft sauber.
- [ ] BC README `contexts/website/README.md` aktualisiert:
      - "Focus area (Schwerpunkt)"-Eintrag in der Ubiquitous Language: Erwähnung
        des `count`-Feldes entfernen ("…mit label, blurb, **und post count**" → "…mit
        label und blurb; Count wird im Layout aus `site.posts` per Topic abgeleitet").
      - "Data file shapes (canonical)" → `_data/focus.yml`: `count` aus der
        Feldliste streichen.

## Notes
- Fix-Stelle Layout: `_layouts/home.html:50` (`<div class="count mono">{{ f.count }} BEITRÄGE</div>`).
- Datenquelle: `_data/focus.yml` (key/label/blurb/count); zugehörige Post-Frontmatter
  `topic:` (siehe BC README, Ubiquitous Language → Topic).
- **Singular vs. Plural:** Heute steht immer "BEITRÄGE", auch bei 1 oder 0. Mit
  echten Zahlen wird das bei `1` falsch ("1 BEITRÄGE"). Optional-Polish: bei `== 1`
  den Singular "BEITRAG" rendern. Außerhalb der Acceptance-Kriterien — kann der
  Worker als Bonus mitnehmen oder Joshua bei Refinement separat entscheiden.
- **Zählweise — entscheiden vor Implementierung:** zählt der Counter alle Posts
  mit `topic == f.key` oder nur die persönlichen (`source != "innoq"`)? Default-
  Annahme: **alle published Posts** (syndicated zählen mit), weil die Karte zur
  Schwerpunkt-Übersicht führt, nicht zum reinen Eigenposting-Archiv. Wenn Joshua
  das anders will, vor dem Bauen ändern.
- Verwandte vorausgegangene Tasks (kein automatischer prior_art-Match wegen
  Slug-Heuristik, aber inhaltlich relevant):
  - **website-001** — eingeführt der Focus-Cards-Sektion samt Liquid-Loop über
    `_data/focus.yml`
  - **website-003** — kanonische Dokumentation der Daten-Datei-Shapes inklusive
    `count`-Feld (das hier entfernt wird)

## Outcome
Hartkodierter `count` aus `_data/focus.yml` entfernt; `_layouts/home.html`
berechnet die Karte-Counter jetzt zur Build-Zeit aus
`published_posts | where: "topic", f.key | size` (wiederverwendet die schon
oben im Layout deklarierte `published_posts`-Assignment, also dieselbe
`published != false`-Filterregel wie für die "Neueste Beiträge"-Liste —
syndizierte Posts zählen mit, gemäß Default-Annahme im Task). Aktuelle
Ist-Zahlen nach Build: `ensemble: 2`, `adhs: 0`, `softdev: 0` (verifiziert
im generierten `_site/index.html`).

**Singular-/Plural-Polish mitgenommen:** `{% if topic_count == 1 %}BEITRAG{% else %}BEITRÄGE{% endif %}`
— bei `1` "BEITRAG", sonst "BEITRÄGE". Damit ist `0 BEITRÄGE`, `1 BEITRAG`,
`2+ BEITRÄGE` korrekt deutsch.

**Aktualisiert:**
- `_layouts/home.html` — Count- + Singular/Plural-Logik
- `_data/focus.yml` — `count`-Feld entfernt, Header-Kommentar aktualisiert
- `contexts/website/README.md` — Ubiquitous Language ("Focus area")
  und "Data file shapes (canonical)" (`_data/focus.yml`-Eintrag) auf das
  neue Modell umgestellt

`bundle exec jekyll build` läuft sauber (0.383s).

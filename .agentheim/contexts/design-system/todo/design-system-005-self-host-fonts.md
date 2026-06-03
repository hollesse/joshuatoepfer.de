---
id: design-system-005
title: Self-host fonts (Geist + Geist Mono) for DSGVO compliance
status: todo
type: bug
context: design-system
created: 2026-06-03
completed:
commit:
depends_on: [design-system-001]
blocks: []
tags: [typography, privacy, dsgvo, fonts, self-hosting]
related_adrs: ["0005"]
related_research: []
prior_art: []
---

## Why
Die Schriftarten **Geist** und **Geist Mono** werden derzeit live aus
`fonts.googleapis.com` geladen (siehe `_layouts/default.html`). Beim
Aufruf jeder Seite überträgt der Browser die IP-Adresse des Besuchers
an **Google LLC (USA)**. Das ist seit **LG München I, Az. 20 O 17493/20
vom 20.01.2022** ein abmahnbarer DSGVO-Verstoß — €100 Schadensersatz pro
Abmahnung plus Anwaltskosten sind die typische Forderung.

Die unter `chore(website): rewrite datenschutz — DSGVO-conform`
(Commit `f29989b`) aktualisierte Datenschutzerklärung beschreibt
diesen Datenfluss ehrlich, *heilt aber den Verstoß nicht*. Was ihn
heilt: die Schriften lokal ausliefern, Google aus der Abruf-Pipeline
entfernen.

## What
Die Geist- und Geist-Mono-Variable-Fonts als WOFF2-Dateien in den
Repo-Bestand übernehmen, per `@font-face` aus einem SCSS-Partial
einbinden, die `<link>`- und `preconnect`-Einträge zu Google Fonts
aus `_layouts/default.html` ersetzen, und die Datenschutzerklärung
entsprechend anpassen — der "Schriftarten (Google Fonts)"-Abschnitt
fällt weg, weil keine Drittlandübermittlung mehr stattfindet.

## Acceptance criteria
- [ ] `_site/` enthält nach `bundle exec jekyll build` **keine**
  Referenzen mehr auf `fonts.googleapis.com` oder `fonts.gstatic.com`:
  `grep -rE 'fonts\.(googleapis|gstatic)\.com' _site/` liefert null
  Treffer.
- [ ] Die Schriften liegen unter `assets/fonts/` als WOFF2-Dateien im
  Repo (Variable-Font-Format für `Geist` und `Geist Mono`, je eine
  Datei pro Familie, abdeckend Weight-Range 100–900).
- [ ] Im DOM angewandte Schriften: visuell identisch zur heutigen
  Darstellung. Stichprobe: Hero-Headline auf `/`, Mono-Eyebrows in
  `.label-eyebrow`, Body-Copy in `.post-body`.
- [ ] `font-display: swap` ist gesetzt, sodass System-Schriften
  während des Ladens als Fallback erscheinen statt FOIT (flash of
  invisible text).
- [ ] `_layouts/default.html`: die beiden `<link rel="preconnect">`
  auf Google sind entfernt, der `<link rel="stylesheet">` auf
  `fonts.googleapis.com` ist entfernt. Stattdessen Referenz auf
  das lokale SCSS-Partial im Asset-Pipeline-Build (i. d. R. über
  den bestehenden `main.css`-Import — kein zusätzlicher `<link>`
  nötig).
- [ ] Datenschutz-Seite (`datenschutz/index.md`): der Abschnitt
  "Schriftarten (Google Fonts)" wird entfernt. Falls eine
  Übergangs-Erwähnung sinnvoll erscheint ("Schriften werden seit
  YYYY-MM-DD selbst gehostet — keine Drittlandübermittlung"),
  kurze Note unter "Änderungen dieser Datenschutzerklärung", aber
  nicht zwingend.
- [ ] WCAG-Lesbarkeit/Rendering im Light- und Dark-Mode visuell
  bestätigt (manueller Spot-Check; pa11y-CI läuft ohnehin gemäß
  `infra-006`).
- [ ] BC-README (`contexts/design-system/README.md`): falls dort
  eine Sektion zu Typografie-Tokens existiert, Hinweis aktualisieren
  ("Fonts: Geist + Geist Mono, lokal als Variable-WOFF2 unter
  `assets/fonts/`"). Falls keine solche Sektion existiert: nicht
  neu erfinden, der Token-Bereich in ADR-0005 reicht.

## Notes

### Quelle der Font-Dateien
Geist ist Open-Source (SIL Open Font License 1.1, von Vercel
veröffentlicht). Variable-Font-Dateien direkt aus dem offiziellen
GitHub-Release ziehen:
`https://github.com/vercel/geist-font/releases`

Variable Fonts statt einzelner Weights:
- `GeistVF.woff2` und `GeistMonoVF.woff2` (ein File pro Familie,
  Weight-Range 100-900 in einer Datei)
- ~70-100 KB pro Datei (komprimiert) — vergleichbar oder geringer
  als die Summe einzelner Weights, die heute über Google Fonts
  ausgeliefert werden

Falls die offiziellen Variable-WOFF2 aus irgendeinem Grund nicht
greifbar sind: Fallback zu statischen Weights (400/500/600 oder
welche im Code tatsächlich referenziert sind — vor der Implementierung
einmal nachschauen in `_sass/`).

### `@font-face`-Vorlage

Im SCSS-Partial (z. B. `_sass/_fonts.scss` oder am Anfang von
`_sass/_base.scss`):

```scss
@font-face {
  font-family: "Geist";
  src: url("../fonts/GeistVF.woff2") format("woff2-variations"),
       url("../fonts/GeistVF.woff2") format("woff2");
  font-weight: 100 900;
  font-style: normal;
  font-display: swap;
}

@font-face {
  font-family: "Geist Mono";
  src: url("../fonts/GeistMonoVF.woff2") format("woff2-variations"),
       url("../fonts/GeistMonoVF.woff2") format("woff2");
  font-weight: 100 900;
  font-style: normal;
  font-display: swap;
}
```

### Verifikations-Hooks für den Worker

Nach `bundle exec jekyll build`:

- `grep -rE 'fonts\.(googleapis|gstatic)\.com' _site/` → 0 Treffer.
- `ls _site/assets/fonts/` zeigt die WOFF2-Dateien.
- Im gerenderten `_site/assets/css/main.css` taucht der `@font-face`-Block
  mit lokalen URLs auf.
- Im gerenderten `_site/index.html` ist *kein* `<link>` mehr zu
  Google sichtbar.

### Was *nicht* in diesen Task gehört

- Wechsel zu einer anderen Schriftfamilie — Geist bleibt.
- Performance-Optimierung über `font-display`-Variationen hinaus
  (z. B. preload-Hints) — wenn nötig, eigener Task.
- Subsetting nach Glyphen — die Variable-Fonts decken den Bedarf,
  Subsetting wäre Mikro-Optimierung.
- Sonstige Datenschutz-Verbesserungen.

### Berührungspunkte mit anderen BCs

`_layouts/default.html` ist website-BC-Territorium. Diese eine Zeile
(der `<link>`-Block) muss der Worker ändern, aber der Großteil der
Arbeit liegt im design-system: Font-Dateien hinzufügen, SCSS-Partial,
README-Update. Die Cross-BC-Touch wird im Datei-Inventar der
website-BC-README im Rahmen dieses Tasks *nicht* nachgezogen, weil
der `<link>` ohnehin nicht namentlich dort aufgeführt ist. Falls
während der Umsetzung neue Erkenntnisse zur BC-Grenze entstehen
(z. B. dass das Font-Loading-Pattern auch dokumentiert werden sollte):
als separaten kleinen Folge-Task aufnehmen, nicht hier reinpressen.

### Risiko / Side-Effects

- **FOUT (Flash of Unstyled Text)** während des ersten Page-Loads,
  bis der WOFF2 geladen ist — `font-display: swap` macht das
  bewusst, ist UX-bekannt und in Lighthouse positiv bewertet.
- **Asset-Größe** steigt im Repo um ~150-200 KB (zwei WOFF2 +
  Header). Auf Netlify-Bandwidth-Budget vernachlässigbar.
- **Build-Zeit** bleibt identisch — Jekyll kopiert die Dateien aus
  `assets/` einfach durch.

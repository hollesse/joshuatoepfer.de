---
id: design-system-004
title: "Portrait styling: drop grayscale filter and tinted background for cutout PNG"
status: done
type: refactor
context: design-system
created: 2026-06-03
completed: 2026-06-03
commit:
depends_on: [website-007]
blocks: []
tags: [portrait, tokens, css, monochrome]
related_adrs: [0005]
related_research: []
prior_art: []
---

## Why
Das Porträt wird jetzt als freigestellte PNG geliefert
(`assets/images/joshua-toepfer-transparent.png`), die bereits in Graustufen vorliegt.
Die bisherigen CSS-Effekte auf `.v1-portrait` und `.about-portrait` (eingeführt mit
website-001 für ein gedachtes rechteckiges Foto mit eigenem Hintergrund) machen zwei
Dinge, die für ein Cutout falsch sind:

1. **`filter: grayscale(1) contrast(1.1) brightness(0.92)`** — entsättigt das Bild ein
   zweites Mal und dunkelt es ab. Joshua bestätigt: das Bild ist bereits graustufig,
   der Filter ist redundant.
2. **`background-color: color-mix(in oklab, var(--fg) 6%, transparent)`** — scheint
   durch die transparenten Bereiche des PNG und erzeugt einen sichtbaren grauen
   "Rand"/Card-Look, der die Freistellung optisch zunichtemacht.

## What
In `_sass/_layout.scss`:
- `.v1-portrait` (aktuell Zeile 151–159): `background-color` und `filter` entfernen.
- `.about-portrait` (aktuell Zeile 847–855): identisch, beide Properties entfernen.

`background-size`, `background-position`, `border-radius`, sowie `width`/`height`
bleiben unverändert (Box-Geometrie und Bild-Skalierung gehören weiter zum Design,
nur die Monochrom-/Tönung-Behandlung fällt weg).

## Acceptance criteria
- [ ] `.v1-portrait` in `_sass/_layout.scss` enthält weder `background-color:` noch
      `filter:` (die anderen Properties bleiben).
- [ ] `.about-portrait` in `_sass/_layout.scss` enthält weder `background-color:`
      noch `filter:` (analog).
- [ ] `bundle exec jekyll build` läuft ohne Fehler.
- [ ] Im generierten CSS (`_site/assets/css/main.css` oder analog) tauchen weder
      `grayscale` noch `color-mix` im Block für `.v1-portrait` / `.about-portrait`
      auf.

## Notes

### Responsive bleibt unangetastet
`_sass/_responsive.scss` überschreibt für `.v1-portrait` (Z. ~36) und
`.about-portrait` (Z. ~192) nur `width`/`height`/`display`/`margin` — keine
Filter- oder Background-Color-Regeln. Dort ist nichts zu ändern.

### Aspect-Ratio-Risiko
Die Boxen sind feste 460×620 (Home) bzw. 460×580 (About) mit `background-size: cover`.
Falls das Cutout-PNG ein deutlich anderes Verhältnis hat als die Box, kann `cover`
das Motiv beschneiden. Sollte das visuell auffallen, ist das ein separater Folge-Task
(Box auf `aspect-ratio` umstellen oder `background-size: contain`). Diese Task hier
ändert NUR die zwei Properties.

### Files to touch
- `_sass/_layout.scss` — vier Zeilen löschen (zwei pro Selektor)

## Outcome

Entfernt aus `_sass/_layout.scss` die Properties `background-color`
(`color-mix(in oklab, var(--fg) 6%, transparent)`) und
`filter: grayscale(1) contrast(1.1) brightness(0.92)` aus beiden
Portrait-Selektoren `.jt .v1-portrait` (Home, 460×620) und
`.jt .about-portrait` (About, 460×580). Geometrie, `background-size: cover`,
`background-position: center` und `border-radius: 2px` bleiben unverändert.

`bundle exec jekyll build` läuft fehlerfrei; im generierten
`_site/assets/css/main.css` enthalten die beiden Portrait-Rule-Blöcke
weder `grayscale` noch `color-mix` (andere Vorkommen im Stylesheet,
z. B. `post-body code`-Background oder `post-hero`-Background, sind
korrekt unangetastet).

### Vokabular-Sync
Im BC-README ist der bisherige Begriff **Duotone (image slot)** durch
**Portrait slot** ersetzt: Der Slot ist nun asset-agnostisch — die
Graustufen-/Duotone-Behandlung liegt im Bildasset selbst
(`assets/images/joshua-toepfer-transparent.png`), nicht mehr im CSS.

### Files
- `_sass/_layout.scss` (Z. 151–157 und Z. 845–851 nach Edit)
- `.agentheim/contexts/design-system/README.md` (Vokabular-Sektion,
  Eintrag „Portrait slot")

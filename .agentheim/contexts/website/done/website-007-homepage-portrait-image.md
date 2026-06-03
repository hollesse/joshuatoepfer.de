---
id: website-007
title: "Homepage portrait image — wire up joshua-toepfer-transparent.png"
status: done
type: feature
context: website
created: 2026-06-03
completed: 2026-06-03
commit:
depends_on: []
blocks: []
tags: [homepage, portrait, image, config]
related_adrs: []
related_research: []
prior_art: []
---

## Why
Die Startseite zeigt aktuell den Porträt-Platzhalter ("Porträt · 3:4 Hochformat"),
weil `site.portrait_image` in `_config.yml` nicht gesetzt ist. Joshua hat das Bild
`assets/images/joshua-toepfer-transparent.png` ergänzt — der Layout-Slot wartet bereits
darauf (eingeführt in website-001).

## What
`portrait_image: assets/images/joshua-toepfer-transparent.png` in `_config.yml`
ergänzen, sodass `_layouts/home.html` den `if site.portrait_image`-Zweig nimmt und
das Bild als `background-image` der `.v1-portrait`-Box rendert.

## Acceptance criteria
- [ ] `_config.yml` enthält den neuen Schlüssel `portrait_image` mit dem Pfad
      `assets/images/joshua-toepfer-transparent.png` (relativ, ohne führenden Slash —
      `relative_url` setzt im Layout den baseurl-Prefix davor).
- [ ] Lokaler Jekyll-Build (`bundle exec jekyll build` oder `serve`) läuft ohne Fehler.
- [ ] Auf `/` ist der Platzhalter ("Porträt · 3:4 Hochformat") verschwunden und stattdessen
      das transparente Porträt sichtbar — visuell verifiziert (Screenshot oder lokaler
      Browser-Check reicht).
- [ ] Pages-Inventory in `contexts/website/README.md` aktualisiert: der Eintrag unter `/`
      → "Data sources" → `site.portrait_image` zeigt aktuell noch auf
      `assets/images/portrait.jpg` (stale); diesen Pfad auf
      `assets/images/joshua-toepfer-transparent.png` korrigieren.

## Notes

### Same flag also lights up `/ueber-mich/`
`_layouts/about.html` konsumiert dieselbe Liquid-Variable (`site.portrait_image`) und
fällt heute ebenfalls auf den Platzhalter zurück. Wenn `_config.yml` angepasst wird,
erscheint dasselbe Porträt automatisch auch auf der About-Seite. Joshua hat die Aufgabe
explizit als "Startseite" formuliert — das ist ok, weil es ein einziger Config-Schlüssel
ist und beide Slots seit website-001 darauf warten. **Falls** für `/ueber-mich/` ein
anderes Bild gewollt ist, muss das Layout um eine zweite Variable (`about_portrait_image`
o.ä.) erweitert werden — bitte vor der Implementierung kurz mit Joshua klären, dann ggf.
als Folge-Task abspalten.

### Bildgröße
`assets/images/joshua-toepfer-transparent.png` ist ~3.3 MB. Above-the-fold Hero-Bild —
ein zusätzlicher Komprimierungs- / Resize-Schritt (z.B. WebP-Variante, max ~600px Breite)
wäre für die Performance sinnvoll, ist aber bewusst NICHT Teil dieser Task, um den Scope
klein zu halten. Bei Bedarf separater Capture.

### Transparenz + Hintergrund
Das Bild ist als "transparent" benannt — der `.v1-portrait`-Container hat im
Design-System eine Hintergrundfarbe (Card-Style). Eine freigestellte PNG auf einer
gefärbten Fläche ist visuell ein bewusster Effekt; falls der Look danach nicht passt,
kann das in einer Folge-Task adressiert werden (z.B. transparenter Container, anderer
Hintergrund). Diese Task ändert nur den Config-Wert.

### Files to touch
- `_config.yml` — einen Key ergänzen
- `.agentheim/contexts/website/README.md` — Pfad in der Pages-Inventory-Sektion `/`
  korrigieren (`portrait.jpg` → `joshua-toepfer-transparent.png`)

## Outcome

`portrait_image: assets/images/joshua-toepfer-transparent.png` ergänzt in
`_config.yml` (kommentierter Block direkt unter `author:`). `bundle exec jekyll build`
läuft sauber durch; `_site/index.html` enthält jetzt das Porträt als
`background-image` der `.v1-portrait`-Box (`v1-portrait--placeholder`-Fallback ist
verschwunden). Wie in den Notes vorhergesehen erscheint dasselbe Bild automatisch
auf `/ueber-mich/` (`_site/ueber-mich/index.html` enthält den Pfad ebenfalls) —
das ist erwartete Konsequenz des gemeinsamen Liquid-Slots.

Außerdem: stale Pfad in `contexts/website/README.md` (Pages-Inventory `/` → Data
sources) von `assets/images/portrait.jpg` auf den korrekten transparenten PNG-Pfad
korrigiert.

Nicht in Scope, bewusst nicht angefasst: Komprimierungs-/WebP-Variante der 3.3 MB
PNG, mögliche Container-/Hintergrund-Anpassungen wegen Transparenz — bei Bedarf
separate Folge-Tasks (siehe Notes).

### Key files
- `_config.yml`
- `.agentheim/contexts/website/README.md`

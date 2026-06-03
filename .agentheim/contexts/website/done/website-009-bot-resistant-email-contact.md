---
id: website-009
title: Bot-resistant email contact
status: done
type: feature
context: website
created: 2026-06-03
completed: 2026-06-03
commit: eeed4fe
depends_on: [design-system-001, infra-012]
blocks: []
tags: [contact, email, anti-spam, accessibility, web-component]
related_adrs: ["0008"]
related_research: []
prior_art: []
---

## Why
Die Kontakt-Adresse `hallo@joshuatoepfer.de` steht heute im Klartext plus
`mailto:`-Link an vier Stellen im gerenderten HTML (Footer, About, Talks,
Impressum). Joshua möchte die Adresse für Menschen weiterhin sichtbar lassen,
aber Spam-Bots das Harvesten so weit erschweren, wie es ohne UX-Bruch geht
— inklusive Bots, die headless Browser nutzen. Zusätzlich soll die rechtlich
verpflichtende Kontakt-Adresse im Impressum von der primären Adresse
getrennt sein, damit sie im Spam-Fall ohne Schmerz austauschbar ist.

## What

Zwei Adressen, zwei Custom Elements, getrennte Schutz-Stufen.

### Adress-Architektur

- **`hallo@joshuatoepfer.de`** — primäre öffentliche Adresse. Erscheint
  in Footer, About-Seite und Talks-Seite. Maximaler technischer Schutz,
  inkl. Interaction-Gate (kein DOM-Render bis erstes menschliches Event).
- **`impressum@joshuatoepfer.de`** — Pflichtangabe im Impressum, bewusst
  als opferbare Wegwerf-Adresse konzipiert. Muss ohne JS lesbar sein
  (§5 DDG / Impressumspflicht), bekommt daher den schwächeren Stack
  mit unvermeidbarem CSS-Leak.

### Custom Element 1 — `<jt-email-protected>`

Für **Footer, About-Seite, Talks-Seite**.

Verwendung im Template:

```html
<jt-email-protected user="aGFsbG8=" domain="am9zaHVhdG9lcGZlci5kZQ==">
  <noscript>Hier wird eine E-Mail-Adresse angezeigt — bitte JavaScript aktivieren.</noscript>
</jt-email-protected>
```

Verhalten:

1. `connectedCallback` öffnet Shadow-DOM, rendert Platzhalter-Button
   („E-Mail anzeigen") mit `aria-label`, das die Verzögerung erklärt.
2. Hängt `window`-Listener für `pointermove`, `keydown`, `touchstart`,
   `scroll`, `focusin` (capture + passive).
3. Beim ersten Event: prüft `performance.now() - loadedAt >= 150ms`
   (Time-Gate gegen synthetische `mousemove`-Bots).
4. Time-Gate erfüllt → Listener abhängen, base64-Fragmente dekodieren
   (`atob`), zusammengesetzte Adresse in `<a>`-Element schreiben
   (`textContent` + `href="mailto:…"`), `aria-label` mit „at"/„punkt"-Form
   setzen, Button durch Anker ersetzen.

Was im **statischen Quelltext** existiert: zwei base64-Strings in
`data`-Attributen ohne unmittelbare Aussagekraft. Nichts sonst.
Insbesondere kein `<noscript>`-Fallback mit der Adresse in „at"/„punkt"-Form
— der wäre die Hintertür, die alles unterläuft.

Was der **`<noscript>`-Fallback** sagen darf: dass an dieser Stelle eine
E-Mail-Adresse stehen würde, aktiviere bitte JavaScript. **Keine
Adress-Bestandteile.**

### Custom Element 2 — `<jt-email-readable>`

Für **Impressum**.

Verwendung im Template:

```html
<jt-email-readable user="impressum" domain="joshuatoepfer.de">
  <span class="email-static"
        style="--u:'impressum'; --d:'joshuatoepfer.de'"
        aria-label="E-Mail: impressum at joshuatoepfer punkt de"></span>
</jt-email-readable>
```

Plus globale CSS-Regel (z. B. in `_sass/_layout.scss`):

```scss
.email-static::before { content: var(--u) "@" var(--d); }
```

Verhalten:

- **Mit JS:** Custom Element öffnet Shadow-DOM, repliziert die
  CSS-Assembly in Shadow-CSS, light-DOM-Span wird visuell überdeckt.
- **Ohne JS:** `<jt-email-readable>` bleibt ein generischer Inline-Container.
  Light-DOM-Span rendert via globaler CSS-Regel. Adresse sichtbar →
  §5 DDG erfüllt.

**Kein `mailto:`-Link.** Impressumspflicht verlangt Lesbarkeit, nicht
Klickbarkeit. `mailto:` wäre genau die maschinell auffindbare Beute, die
wir vermeiden wollen.

**Restleak:** `style="--u:'impressum'; --d:'joshuatoepfer.de'"` ist mit
Regex aus dem Quelltext extrahierbar. Bewusst akzeptiert, weil die
rechtliche Lesbarkeitsanforderung einen Quelltext-Eintrag erzwingt und
die Adresse als opferbar konzipiert ist.

### Dateien, die berührt werden

Mindestens:

- `_includes/footer.html` — `mailto:hallo@…` ersetzt durch `<jt-email-protected>`
- `_layouts/about.html` — dito
- `_layouts/talks.html` — dito
- `impressum/index.md` (oder das umgebende Layout) — `mailto:hallo@…`
  ersetzt durch `<jt-email-readable>` mit `impressum@`
- Neue Datei: `assets/js/email-elements.js` (oder zwei Dateien) mit den
  beiden Custom-Element-Definitionen; per `<script defer>` im
  `_layouts/default.html` einbinden
- `_sass/_layout.scss` (oder geeignete Partial) — `.email-static::before`
  Regel hinzufügen
- BC-README `README.md`: Pages-Inventar an betroffenen Stellen aktualisieren
  (Component-Vocabulary-Liste erweitern um `.email-static` und um die
  beiden Custom-Element-Tags)

### Tests / Verifikations-Hooks (für den Worker)

Nach `bundle exec jekyll build`:

- `grep -rE 'hallo@joshuatoepfer\.de' _site/` liefert null Treffer.
- `grep -rE 'mailto:hallo@joshuatoepfer\.de' _site/` liefert null Treffer.
- `grep -rE 'mailto:impressum@joshuatoepfer\.de' _site/` liefert null Treffer.
- `grep -rE 'impressum@joshuatoepfer\.de' _site/` liefert **maximal**
  Treffer in inline `style`-Attributen mit `--u:'impressum'` (erwarteter
  CSS-Leak). Treffer als roher Adress-Text → Fehler.

## Acceptance criteria

- [ ] Im gerenderten `_site/` existiert nirgends die zusammengesetzte
  Zeichenkette `hallo@joshuatoepfer.de` als Text — weder als
  Linktext, noch als `href`, noch in einem Attribut.
- [ ] Im gerenderten `_site/` existiert nirgends `mailto:hallo@…` oder
  `mailto:impressum@…`.
- [ ] Für `impressum@joshuatoepfer.de` ist die Adresse im rohen HTML
  *nicht* als zusammenhängender Text sichtbar; die Bestandteile leben
  nur in den `style`-Custom-Properties auf der Impressum-Seite.
- [ ] Mit aktiviertem JavaScript:
  - Footer-, About- und Talks-Link bauen sich nach erstem Eingabe-Event
    (mind. 150 ms nach Load) zur klickbaren Adresse zusammen, öffnen den
    Mail-Client mit Ziel `hallo@joshuatoepfer.de`.
  - Impressum zeigt `impressum@joshuatoepfer.de` als Text, ohne `<a>`-Tag.
- [ ] Mit deaktiviertem JavaScript:
  - Footer / About / Talks: Hinweis aus `<noscript>` ist sichtbar; die
    Hinweis-Text enthält **keinerlei** Adress-Bestandteile.
  - Impressum: Adresse `impressum@joshuatoepfer.de` ist als Text lesbar
    (CSS-Assembly aus light-DOM-Span).
- [ ] Screen-Reader-Test: `aria-label` an Button (vor Reveal), `<a>`
  (nach Reveal) und light-DOM-Span (Impressum) trägt die Adresse in
  gesprochener Form („hallo at joshuatoepfer punkt de" /
  „impressum at joshuatoepfer punkt de"). Tab-Fokus bricht nichts.
- [ ] BC-README aktualisiert: neue Component-Vocabulary-Einträge für
  `<jt-email-protected>`, `<jt-email-readable>`, `.email-static`.
- [ ] ADR geschrieben: `decisions/00XX-email-obfuscation-strategy.md` mit
  Begründung der zwei-Adressen-Architektur, der Stufe-4-Wahl und dem
  bewusst akzeptierten Impressum-Leak.

## Notes

### Reihenfolge & Blocker

`infra-012` (Mail-Postfach `impressum@joshuatoepfer.de` einrichten)
ist seit 2026-06-03 erledigt — gelöst per **Catchall-Adresse** auf der
Domain (`*@joshuatoepfer.de` landet bei Joshua). `impressum@` funktioniert
damit automatisch ohne separates Postfach. Blocker damit aufgelöst.

**Wichtige Nuance für „opferbare Wegwerf-Adresse" mit Catchall:**
Im Spam-Notfall reicht es *nicht*, ein Postfach zu löschen (gibt's keins).
Stattdessen muss beim Mail-Provider eine **Reject-Regel** für genau den
Local-Part `impressum` angelegt werden, und in der Impressum-Seite ein
neuer Local-Part eingesetzt werden (z. B. `impressum2@`, `kontakt-legal@`).
Funktional gleichwertig, ein Schritt mehr im Notfall.

`design-system-001` (Styleguide) ist Soft-Dependency: die neuen CSS-Klassen
sollen sich an die Tokens der Design-System-BC halten (Spacing, Color-Inherit,
Typografie). Tatsächlich erbt die Adresse visuell hauptsächlich vom Eltern-
Kontext, also kein nennenswerter Eingriff am Styleguide selbst.

### Bewusst nicht gemacht — und warum

- **Kontaktformular statt mailto:** vom Nutzer explizit verworfen, weil
  sichtbare Adresse beibehalten werden soll.
- **Bild der Adresse im Impressum:** Accessibility-Konflikt (`alt`-Text
  leakt oder Screen-Reader sehen nichts), OCR-trivial 2026, rechtlich
  Grauzone — schlechter Trade-off.
- **Cloudflare Email Obfuscation:** würde DNS-Wechsel zu Cloudflare-vor-Netlify
  verlangen. Großer Eingriff für inkrementellen Gewinn.
- **Canvas-Rendering:** gleicher A11y-Konflikt wie Bild.
- **Honeypot-Decoy-Adressen:** Risiko, dass schlecht gewartete Decoys auf
  Blacklisten landen.
- **AES-Verschlüsselung in JS:** wer den Code ausführt, hat den Schlüssel
  → kein realer Schutz gegenüber base64.

### Reveal-Trigger-Design (warum genau diese Events)

- `pointermove` — Maus-Navigation (deckt auch Stylus / Touch-Pads ab,
  vereint Maus- und Touch-Pointer-Events).
- `keydown` — Tastatur-Navigation, deckt Tab-Fokus auf die Page.
- `touchstart` — explizite Touch-Geräte, falls `pointermove` nicht feuert.
- `scroll` — Scrollwheel ohne Mausbewegung, oder Trackpad-Scrolling
  ohne Pointer-Bewegung.
- `focusin` — Screen-Reader und Tastatur-Nutzer, die direkt auf den
  Link tabben, ohne vorher zu interagieren.

Headless Chrome ohne Stealth-Plugins feuert keines davon → blockt. Headless
Chrome mit Stealth-Plugins kann `mousemove` faken → 150-ms-Time-Gate filtert
das Subset, das sofort nach Load feuert.

### Reveal-Robustheit

`once: true` als Listener-Option würde reichen, aber wir wollen das
Time-Gate prüfen *bevor* wir die anderen Listener abhängen. Daher
manuelles Lösen erst nach erfolgreichem Reveal.

### Komponente vs zwei Komponenten

Bewusste Entscheidung für zwei separate Custom Elements (`-protected` +
`-readable`) statt eine mit `mode`-Attribut: die beiden haben *völlig
unterschiedliche* Lebenszyklen (eines rendert erst nach Interaktion,
eines initial), und die Modi haben keinen gemeinsamen Code-Pfad, der
sich teilen ließe. Zwei Elemente sind klarer.

## Outcome

Die vier `mailto:hallo@joshuatoepfer.de`-Vorkommen im gerenderten HTML
(Footer, About, Talks, Impressum) sind eliminiert. Zwei neue Custom Elements
liefern asymmetrischen Schutz:

- `<jt-email-protected>` (Footer/About/Talks) ist Stufe-4: base64-Fragmente
  in `data`-Attributen, Reveal erst nach erstem `pointermove`/`keydown`/
  `touchstart`/`scroll`/`focusin`-Event **und** ≥150 ms nach Load. Headless
  Chrome ohne Stealth-Plugins kommt nie zum Render. `<noscript>`-Slot
  enthält bewusst keine Adress-Bestandteile.
- `<jt-email-readable>` (nur Impressum) hängt einen light-DOM-Span mit
  CSS-Assembly-Properties (`--u`/`--d`) ein, JS überdeckt ihn per Shadow
  DOM mit derselben Assembly. Ohne JS bleibt der Span lesbar (§5 DDG).
  Kein `mailto:`. Bewusst akzeptierter Leak: die Bestandteile sind im
  HTML sichtbar, aber durch Quote-Zeichen separiert — kein
  zusammenhängender Adress-String.

Alle vier Verifikations-Greps im `_site/` liefern null Treffer (inkl.
`impressum@joshuatoepfer.de` als zusammenhängender String).

Zentrale Dateien:
- `assets/js/email-elements.js` — Custom-Element-Definitionen
- `_sass/_layout.scss` — `.email-static::before { content: var(--u) "@" var(--d); }`
- `_layouts/default.html` — Skript-Einbindung mit `defer`
- `_includes/footer.html`, `_layouts/about.html`, `_layouts/talks.html`,
  `impressum/index.md` — Einsatzstellen
- `.agentheim/knowledge/decisions/0008-email-obfuscation-strategy.md` —
  ADR mit Begründung der Zwei-Adressen-Architektur, der Stufe-4-Wahl
  und des bewusst akzeptierten Impressum-Leaks
- `.agentheim/contexts/website/README.md` — Component-Vocabulary
  erweitert um `<jt-email-protected>`, `<jt-email-readable>` und
  `.email-static`; Pages-Inventar für Chrome/Footer/About/Talks/Impressum
  aktualisiert

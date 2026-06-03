---
id: "0008"
title: "Email obfuscation strategy: two-address architecture with asymmetric protection (interaction-gate JS-assembly for primary, CSS-assembly for legal)"
scope: website
status: accepted
date: 2026-06-03
supersedes: []
superseded_by: []
related_tasks: [website-009]
related_research: []
---

# ADR-0008: Email Obfuscation Strategy

## Context

Bis website-009 lebte die Kontakt-Adresse `hallo@joshuatoepfer.de` an vier
Stellen im gerenderten HTML als `<a href="mailto:hallo@joshuatoepfer.de">hallo@joshuatoepfer.de</a>`:
Footer, About-Seite, Talks-Seite und Impressum. Drei davon sind freiwillige
Marketing-Touchpoints, einer (Impressum) ist gesetzlich erzwungen (§5 DDG,
ehemals §5 TMG: "schnelle elektronische Kontaktaufnahme").

Joshua möchte zwei Dinge gleichzeitig:

1. **Adresse für Menschen sichtbar halten** — Kontaktformulare wurden
   explizit verworfen, weil ein sichtbares `hallo@…` warmer wirkt und
   die Reibung zur ersten Mail kleiner ist.
2. **Spam-Bots maximal erschweren** — auch headless-Browser-basierte
   Harvester, die JavaScript ausführen.

Diese beiden Ziele sind teilweise im Konflikt: jede Maschinen-lesbare
Repräsentation ist zugleich Bot-Beute. Die Lösung muss den Trade-off pro
Surface unterschiedlich austarieren, weil die rechtliche Bindung
Impressum vs. die freiwillige Sichtbarkeit Footer/About/Talks
**unterschiedliche Schutzdecken** zulässt.

Zusätzlich braucht es eine Notfall-Strategie für den Fall, dass die
Impressum-Adresse auf Spam-Listen landet — ein Postfach, das ohne
SEO-Verlust oder rechtliche Komplikationen austauschbar ist.

## Decision

### 1. Zwei-Adressen-Architektur

- **`hallo@joshuatoepfer.de`** ist die primäre öffentliche Adresse. Sie
  erscheint in Footer, About-Seite und Talks-Seite. Sie bekommt den
  härtesten technischen Schutz (siehe §2 unten). Sie wird *nicht* im
  Impressum verwendet.
- **`impressum@joshuatoepfer.de`** ist die im Impressum genannte
  Pflicht-Adresse. Sie ist bewusst als opferbare Wegwerf-Adresse
  konzipiert und bekommt den schwächeren Schutz, weil §5 DDG eine
  JS-freie Lesbarkeit erzwingt.

Eingerichtet ist sie als **Catchall** auf der Domain (alle `*@joshuatoepfer.de`
landen bei Joshua). Im Notfall wird beim Mail-Provider eine Reject-Regel
für genau `impressum@` angelegt und die Impressum-Seite auf einen neuen
Local-Part umgebogen (z. B. `impressum2@` oder `kontakt-legal@`).
Funktional gleichwertig zu einem dedizierten Postfach, ein Schritt mehr
im Notfall — siehe `website/README.md` und `infra-012` (die im Lauf von
website-009 als out-of-band-resolved markiert wurde).

### 2. `<jt-email-protected>` — Stufe-4-Schutz für `hallo@`

Custom Element mit Shadow DOM, eingesetzt in Footer/About/Talks. Static
HTML enthält nur:

- `data-user="aGFsbG8="` (base64 von `hallo`)
- `data-domain="am9zaHVhdG9lcGZlci5kZQ=="` (base64 von `joshuatoepfer.de`)
- ein `<noscript>`, das nur sagt „bitte JS aktivieren" — **ohne**
  Adress-Bestandteile

Verhalten:

1. `connectedCallback` rendert einen Platzhalter-Button („E-Mail anzeigen →").
2. Hängt `pointermove`, `keydown`, `touchstart`, `scroll`, `focusin`
   am `window` (capture + passive).
3. Beim ersten Event prüft es `performance.now() - loadedAt >= 150 ms`
   (Time-Gate gegen Bots, die direkt nach Load synthetische `mousemove`
   feuern).
4. Time-Gate erfüllt → Listener abhängen, base64 dekodieren, `<a>` mit
   `mailto:`-Link und spoken-form `aria-label` rendern.

Das ist „Stufe 4" auf der hier verwendeten Skala:

- Stufe 1: Klartext `mailto:` (alter Zustand) — sofort harvestbar.
- Stufe 2: Statisches base64/Entity-Encoding ohne JS-Assembly — von jedem
  Harvester trivial dekodierbar.
- Stufe 3: JS-Assembly beim Page-Load — blockt naive Harvester, nicht
  headless Chrome.
- **Stufe 4: JS-Assembly *gated* an menschliche Interaktion** — blockt
  zusätzlich headless Browser ohne realistische Event-Simulation.

Headless Chrome ohne Stealth-Plugins feuert keines der Listener-Events
→ Adresse bleibt im DOM nicht zusammengesetzt. Headless Chrome mit
Stealth-Plugins kann `mousemove` synthetisch faken, aber wenn das direkt
nach Load passiert, schneidet das 150-ms-Time-Gate jenes Subset weg.

### 3. `<jt-email-readable>` — CSS-Assembly für Impressum

Custom Element mit Shadow DOM, eingesetzt im Impressum. Im Light DOM
liegt ein `<span class="email-static" style="--u:'impressum'; --d:'joshuatoepfer.de'" aria-label="…">`.

Globale CSS-Regel:
```scss
.email-static::before { content: var(--u) "@" var(--d); }
```

- **Mit JS:** Shadow DOM des Custom Element repliziert die CSS-Assembly
  und überdeckt den Light-DOM-Span. Aria-Label im Shadow trägt die
  spoken-form.
- **Ohne JS:** `<jt-email-readable>` bleibt ein generischer Inline-Container,
  Light-DOM-Span rendert via globaler Regel. Adresse ist visuell lesbar
  → §5 DDG erfüllt.

**Kein `mailto:`-Link.** Impressumspflicht verlangt Lesbarkeit, nicht
Klickbarkeit. Ein `mailto:` wäre die maschinell auffindbare Beute, die
genau vermieden werden soll.

### 4. Bewusst akzeptierter Leak

`style="--u:'impressum'; --d:'joshuatoepfer.de'"` ist mit Regex aus dem
Quelltext extrahierbar. Im rohen HTML existiert allerdings **kein
zusammenhängender Adress-String** `impressum@joshuatoepfer.de` — die
Bestandteile sind durch `'`, `;` und Leerzeichen getrennt, und ein
Harvester-Regex `[\w.]+@[\w.]+\.\w+` greift nicht. Das ist deutlich
besser als die alte Klartext-Form, aber objektiv schwächer als die
Stufe-4-Lösung für `hallo@`.

Diese Asymmetrie ist absichtlich: die Adresse im Impressum **darf**
leichter zu finden sein, weil sie a) gesetzlich lesbar sein muss und
b) als opferbar konzipiert ist.

## Consequences

### Positive

- Vier `mailto:hallo@joshuatoepfer.de`-Vorkommen im gerenderten HTML sind
  jetzt null. Naive und Stufe-2-Harvester laufen ins Leere.
- Bots, die headless Chrome ohne Interaction-Simulation nutzen,
  bekommen `hallo@…` nie zu sehen.
- `impressum@` ist im Spam-Notfall in <1 Stunde tauschbar (Provider-Regel
  + ein Edit in `impressum/index.md`), ohne die primäre Adresse
  anzufassen.
- Accessibility bleibt erhalten: `aria-label` in spoken-form an
  Platzhalter-Button, fertigem `<a>` und Impressum-Span. Tab-Reihenfolge
  unverändert.
- BC-README dokumentiert die neuen Komponenten in der
  Component-Vocabulary; ADR-0005-Konvention bleibt eingehalten.

### Negative

- JS-Assembly für `hallo@` heißt: für Nutzer ohne JS gibt es im
  Footer/About/Talks keinen Mail-Link — nur den `<noscript>`-Hinweis.
  Akzeptiert, weil die Pflicht-Adresse im Impressum den Bedarf rechtlich
  erfüllt und JS-lose Nutzer:innen heute selten genug sind, dass der
  UX-Verlust den Bot-Schutz rechtfertigt.
- Time-Gate von 150 ms heißt: Nutzer:innen, die *unmittelbar* nach
  Render die Page anschauen und keinerlei Eingabe machen, sehen
  zuerst nur den Platzhalter-Button. Klick auf den Button löst die
  Assembly aus → kein dauerhaftes Hindernis, nur eine zusätzliche
  Interaktion.
- Catchall-Architektur statt dediziertem Postfach: im Spam-Notfall
  reicht *Löschen des Postfachs* nicht (gibt's keins), stattdessen
  muss eine Reject-Regel angelegt werden. Ein Schritt mehr im Notfall.

### Neutral

- Stufe-4-Schutz ist nicht unangreifbar. Sufficiently determined
  Harvester (Playwright/Puppeteer mit realistischer
  Event-Simulation + delay) können `<jt-email-protected>` knacken.
  Das ist akzeptiert: das Threat-Modell sind volume-spammer, nicht
  zielgerichtete Akteure.
- Die Wahl von zwei separaten Custom Elements statt eines mit
  `mode`-Attribut ist bewusst — beide haben völlig unterschiedliche
  Lebenszyklen (eines rendert erst nach Interaktion, eines initial)
  ohne nennenswert teilbaren Code-Pfad.

## Alternatives considered

- **Kontaktformular** statt sichtbarer Adresse: vom Nutzer verworfen,
  weil sichtbare Adresse beibehalten werden soll.
- **Bild der Adresse im Impressum:** Accessibility-Konflikt (`alt`-Text
  würde leaken oder Screen-Reader hätten nichts zu lesen). OCR macht
  Bilder 2026 trivial knackbar. Rechtlich Grauzone bei Lesbarkeit.
- **Cloudflare Email Obfuscation:** würde DNS-Wechsel zu Cloudflare-
  vor-Netlify verlangen. Großer Eingriff für inkrementellen Gewinn.
- **Canvas-Rendering der Adresse:** gleicher A11y-Konflikt wie Bild.
- **Honeypot-Decoy-Adressen** in das Markup: Risiko, dass schlecht
  gewartete Decoys irgendwann selbst auf Blacklisten landen und unsere
  Domain-Reputation beschädigen.
- **AES-Verschlüsselung in JS:** wer den JS ausführt, hat den Schlüssel
  → kein realer Schutz gegenüber base64. Mehr Komplexität ohne Gegenwert.
- **Eine Komponente mit `mode="protected|readable"`** statt zwei:
  abgelehnt, weil beide Modi keinen gemeinsamen Code-Pfad teilen würden
  und die Lebenszyklen radikal unterschiedlich sind (Interaction-Gate vs.
  initialer Render).

## Related files

- `assets/js/email-elements.js` — Definition der beiden Custom Elements
- `_sass/_layout.scss` — `.email-static::before { content: var(--u) "@" var(--d) }`
- `_includes/footer.html`, `_layouts/about.html`, `_layouts/talks.html`,
  `impressum/index.md` — Einsatzstellen
- `_layouts/default.html` — Skript-Einbindung
- `.agentheim/contexts/website/README.md` — Component-Vocabulary-Einträge
- `.agentheim/contexts/website/done/website-009-bot-resistant-email-contact.md`

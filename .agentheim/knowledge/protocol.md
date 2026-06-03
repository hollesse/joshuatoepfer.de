# Protocol

Chronological log of everything that happens in this project.
Newest entries on top.

---

## 2026-06-03 -- Task verified and completed: design-system-005 - Self-host fonts (Geist + Geist Mono) for DSGVO compliance

**Type:** Work / Task completion
**Task:** design-system-005 - Self-host fonts (Geist + Geist Mono) for DSGVO compliance
**Summary:** Geist und Geist Mono werden ab sofort als selbst gehostete Variable-WOFF2 unter `assets/fonts/` ausgeliefert (eingebunden via neuem `_sass/_fonts.scss`-Partial mit `font-display: swap`); die `<link>`-Einträge zu `fonts.googleapis.com`/`fonts.gstatic.com` sind aus `_layouts/default.html` entfernt, die Datenschutzerklärung dokumentiert den Wegfall der Drittlandübermittlung, und der `OFL.txt` (SIL Open Font License 1.1) liegt als Pflicht-Attribution neben den Font-Dateien.
**Verification:** PASS (iteration 1) — Verifier bestätigte saubereren `bundle exec jekyll build`, null Treffer für `fonts.googleapis.com`/`fonts.gstatic.com` im `_site/`, beide WOFF2 + OFL.txt korrekt durchkopiert nach `_site/assets/fonts/`, beide `@font-face`-Blöcke mit lokalen `../fonts/`-URLs im kompilierten `main.css`, `font-family: "Geist"`/`"Geist Mono"`-Referenzen auf `.jt`/`.label-eyebrow`/`.post-body code` intakt, ADR-0005 unverändert. OFL.txt verifiziert als echte SIL Open Font License 1.1 mit Copyright-Attribution.
**Commit:** 8b31dcd
**Files changed:** 8 (worker production files) + 1 (moved task file)
**Tests added:** 0 (pure config/data migration; jekyll-build + 5 Grep-Hooks im `_site/` sind die testbare Surrogat-Assertion, vom Verifier ausgeführt)
**ADRs written:** none (ADR-0005's "Consequences > Negative"-Bullet zur Google-Fonts-Abhängigkeit bleibt als historischer Kontext stehen; kein neuer ADR erforderlich)

---

## 2026-06-03 -- Batch started: [design-system-005]

**Type:** Work / Batch start
**Tasks:** design-system-005 - Self-host fonts (Geist + Geist Mono) for DSGVO compliance
**Parallel:** no (1 worker)

---

## 2026-06-03 -- Model / Captured: design-system-005 - Self-host fonts (Geist + Geist Mono) for DSGVO compliance

**Type:** Model / Capture
**BC:** design-system
**Filed to:** todo
**Summary:** Direkt nach dem Datenschutz-Rewrite (`f29989b`) sichtbar geworden: Google Fonts wird live aus `fonts.googleapis.com` geladen, beim Seitenaufruf wird die Besucher-IP an Google LLC (USA) übermittelt. Seit LG München I 20 O 17493/20 (20.01.2022) ein abmahnbarer DSGVO-Verstoß (~€100 Schadensersatz typisch). Fix-Pfad konkret: Geist + Geist Mono als Variable-Fonts (WOFF2) unter `assets/fonts/` ablegen, per `@font-face` aus SCSS-Partial einbinden, `<link>`- und `preconnect`-Einträge zu Google aus `_layouts/default.html` entfernen, "Schriftarten (Google Fonts)"-Sektion aus `datenschutz/index.md` herausnehmen. Routing zu `design-system` weil Typografie deren Ubiquitous Language ist; der `_layouts/default.html`-Touch ist der website-BC-Berührungspunkt, explizit in den Task-Notes festgehalten. Direkt nach `todo/` mit Grep-Verifikations-Hooks für den Worker.

---

## 2026-06-03 -- Work session ended

**Type:** Work / Session end
**Completed:** 1 (first-try PASS: 1, re-dispatched: 0, skipped: 0)
**Bounced:** 0
**Failed:** 0
**Escalated after verification:** 0
**Commits:** 2 (eeed4fe + 4b869a5)

---

## 2026-06-03 -- Task verified and completed: website-009 - Bot-resistant email contact

**Type:** Work / Task completion
**Task:** website-009 - Bot-resistant email contact
**Summary:** Vier `mailto:hallo@joshuatoepfer.de`-Klartext-Vorkommen (Footer, About, Talks, Impressum) durch zwei Web Components ersetzt: `<jt-email-protected>` mit Stufe-4-Schutz (base64-Fragmente + Interaction-Gate ≥150 ms nach `pointermove`/`keydown`/`touchstart`/`scroll`/`focusin`) für `hallo@` in Footer/About/Talks, `<jt-email-readable>` mit CSS-Assembly für die opferbare Impressum-Adresse `impressum@joshuatoepfer.de` (JS-frei lesbar gemäß §5 DDG, kein `mailto:`-Link). ADR-0008 dokumentiert die Architektur, die 4-Stufen-Schutzskala und den bewusst akzeptierten CSS-Leak fürs Impressum.
**Verification:** PASS (iteration 1) — Verifier hat `bundle exec jekyll build` sauber durchlaufen lassen und alle vier Grep-Hooks gegen `_site/` bestätigt: keine `hallo@joshuatoepfer.de` als Text, keine `mailto:hallo@…`/`mailto:impressum@…`, kein zusammenhängender `impressum@joshuatoepfer.de`-String (sogar besser als Spec — die Bestandteile sind in `style="--u:'impressum'; --d:'joshuatoepfer.de'"` per Quote/Semicolon getrennt). Code-Review der Custom-Element-Logik in `assets/js/email-elements.js` (Time-Gate, REVEAL_EVENTS, spoken-form aria-label) als Surrogat für nicht-vorhandene Browser-Test-Infra. BC-README mit drei neuen Vocabulary-Einträgen + Pages-Inventar-Updates. ADR-0008 wohlgeformt, 7 Alternativen explizit verworfen mit Begründung.
**Commit:** eeed4fe
**Files changed:** 9 (worker production files) + 1 (moved task file)
**Tests added:** 0 (Browser-Custom-Element-Verhalten; Grep-Hooks auf `_site/` sind die testbare Surrogat-Assertion, vom Verifier ausgeführt)
**ADRs written:** 0008-email-obfuscation-strategy.md (scope: website)

---

## 2026-06-03 -- Batch started: [website-009]

**Type:** Work / Batch start
**Tasks:** website-009 - Bot-resistant email contact
**Parallel:** no (1 worker)

---

## 2026-06-03 -- Model / Promoted: website-009 - Bot-resistant email contact

**Type:** Model / Promote
**BC:** website
**From → To:** backlog → todo
**Summary:** Promote-Kriterien erfüllt — konkrete Acceptance-Criteria mit Grep-Hooks im gerenderten `_site/`, klarer Scope (zwei Custom Elements, definierte Dateien), beide Dependencies erledigt (`design-system-001` und `infra-012` jetzt in `done/`). Bereit für Worker-Aufnahme.

---

## 2026-06-03 -- Model / Completed (out-of-band): infra-012 - Mail-Postfach impressum@

**Type:** Model / Task completion (manual)
**BC:** infrastructure
**Status after:** backlog → done
**Summary:** Joshua hat den Chore selbst erledigt: kein separates Postfach nötig, weil eine **Catchall-Adresse** auf `joshuatoepfer.de` aktiv ist — jede `*@joshuatoepfer.de`-Mail landet in Joshuas Posteingang. `impressum@` funktioniert damit automatisch. Nuance gegenüber dem ursprünglich gedachten "Postfach löschen"-Plan: im Spam-Notfall braucht es eine provider-seitige Reject-Regel auf den Local-Part `impressum` plus Local-Part-Wechsel auf der Impressum-Seite. Notiert in `website-009` und in den Task-Notes von `infra-012`. Kein Code-Commit (Provider-Konfig außerhalb des Repo). `website-009`-Blocker damit aufgelöst.

---

## 2026-06-03 -- Model / Refined: website-009 - Bot-resistant email contact

**Type:** Model / Refine
**BC:** website
**Status after:** backlog
**Summary:** Architektur-Refinement zu zwei Custom Elements mit asymmetrischem Schutz: `<jt-email-protected>` für `hallo@` (Footer/About/Talks) mit Interaction-Gate (≥150 ms nach Load + erstes `pointermove`/`keydown`/`touchstart`/`scroll`/`focusin`-Event), base64-Fragmente in `data-`-Attributen, kein `<noscript>`-Leak mit Adress-Bestandteilen; `<jt-email-readable>` für `impressum@` (Impressum) mit CSS-Assembly via inline-custom-properties, light-DOM-Span als no-JS-Fallback (§5 DDG verlangt Lesbarkeit ohne JS), bewusst kein `mailto:`-Link. Zwei Adressen → `impressum@` opferbar im Spam-Notfall, `hallo@` als sticky Primär-Adresse maximal geschützt. Verworfen mit Begründung: Kontaktformular (User-Wunsch sichtbare Adresse), Bild-Rendering (A11y + OCR), Cloudflare-Obfuscation (DNS-Eingriff), Honeypot-Decoys (Blacklist-Risiko), AES-JS (kein realer Mehrwert ggü. base64). Acceptance-Criteria mit konkreten Grep-Hooks für den Worker formuliert. ADR-Auftrag im Task notiert (`00XX-email-obfuscation-strategy`).
**Split into:** infra-012 (Mail-Postfach `impressum@` einrichten — Provider-Konfig; harter Blocker)
**ADRs written:** none (ADR wird beim Implementieren geschrieben, nicht jetzt)

---

## 2026-06-03 -- Model / Captured: infra-012 - Mail-Postfach impressum@ einrichten

**Type:** Model / Capture
**BC:** infrastructure
**Filed to:** backlog
**Summary:** Chore: bei Joshuas Mail-Provider ein Postfach (oder eine Weiterleitung) für `impressum@joshuatoepfer.de` anlegen. Dient `website-009` als opferbare Wegwerf-Adresse für die §5-DDG-Pflichtangabe im Impressum. Reiner Provider-Konfig-Eingriff, Joshua führt das selbst aus. `blocks: [website-009]`.

---

## 2026-06-03 -- Model / Captured: website-009 - Bot-resistant email contact

**Type:** Model / Capture
**BC:** website
**Filed to:** backlog
**Summary:** Joshua möchte die Kontakt-Adresse `hallo@joshuatoepfer.de` so darstellen, dass naïve Scraper sie nicht extrahieren können, ohne die Erreichbarkeit für Menschen zu verlieren. Heute steht die Adresse im Klartext + `mailto:` an vier Stellen (Footer, About, Talks, Impressum). Backlog statt Todo, weil drei echte Entscheidungen offen sind: Obfuskations-Technik (JS-rebuild vs. Entities vs. CSS vs. Kombination), Mailto vs. Netlify-Forms-Formular, und der Non-JS-Fallback fürs Impressum (Impressumspflicht). Out of scope: Adresse selbst ändern, `_config.yml`, eigenes Form-Backend.

---

## 2026-06-03 -- Work session ended

**Type:** Work / Session end
**Completed:** 1 (first-try PASS: 1, re-dispatched: 0, skipped: 0)
**Bounced:** 0
**Failed:** 0
**Escalated after verification:** 0
**Commits:** 1 (da6947e)

---

## 2026-06-03 -- Task verified and completed: website-008 - Focus card post count

**Type:** Work / Task completion
**Task:** website-008 - Focus card post count — derive from real posts instead of hardcoded number
**Summary:** `_layouts/home.html` leitet die Beitragszahl pro Focus-Card jetzt zur Build-Zeit aus `published_posts | where: "topic", f.key | size` ab statt aus hartkodierten Zahlen; `count` aus `_data/focus.yml` entfernt; BC-README aktualisiert (Ubiquitous Language "Focus area" + Data file shapes für `_data/focus.yml`). Singular/Plural-Polish mitgenommen (`{% if topic_count == 1 %}BEITRAG{% else %}BEITRÄGE{% endif %}`).
**Verification:** PASS (iteration 1) — verifier bestätigte sauberen `bundle exec jekyll build` und im gerenderten `_site/index.html` die korrekten Zahlen `ensemble: 2 BEITRÄGE`, `adhs: 0 BEITRÄGE`, `softdev: 0 BEITRÄGE` (passend zu den zwei `topic: ensemble`-Posts).
**Commit:** da6947e
**Files changed:** 4 (3 worker + moved task file)
**Tests added:** 0 (template change; build-clean + rendered-output-grep ist der Test)
**ADRs written:** none (Zählweise war im Task-Notes bereits entschieden, keine neue Architektur-Entscheidung)

---

## 2026-06-03 -- Batch started: [website-008]

**Type:** Work / Batch start
**Tasks:** website-008 - Focus card post count — derive from real posts instead of hardcoded number
**Parallel:** no (1 worker)

---

## 2026-06-03 -- Model / Captured: website-008 - Focus card post count from real posts

**Type:** Model / Capture
**BC:** website
**Filed to:** todo
**Summary:** Joshua hat gemeldet, dass die Beitrags-Mengen auf der "MEINE SCHWERPUNKTE"-Sektion der Startseite nicht stimmen. Ursache: `_data/focus.yml` trägt hartkodierte Fantasie-Zahlen (`14/9/27`) als `count`-Feld, die per Liquid (`_layouts/home.html:50`) ungeprüft auf die Karten gerendert werden. Fix: Count zur Buildzeit aus `site.posts | where: "topic", f.key | size` ableiten und das tote `count`-Feld aus `_data/focus.yml` + BC-README löschen. Direkt nach `todo/`, weil Scope und Fix-Stelle klar sind. Notiert für Worker: Singular/Plural ("BEITRAG" vs "BEITRÄGE") und Zählweise (syndicated mitzählen ja/nein, Default ja) sind die zwei Mikro-Entscheidungen.

---

## 2026-06-03 -- Work session ended

**Type:** Work / Session end
**Completed:** 1 (first-try PASS: 1, re-dispatched: 0, skipped: 0)
**Bounced:** 0
**Failed:** 0
**Escalated after verification:** 0
**Commits:** 1 (83b086f)

---

## 2026-06-03 -- Task verified and completed: design-system-004 - Portrait styling

**Type:** Work / Task completion
**Task:** design-system-004 - Portrait styling: drop grayscale filter and tinted background for cutout PNG
**Summary:** Removed `filter: grayscale(1) contrast(1.1) brightness(0.92)` and `background-color: color-mix(in oklab, var(--fg) 6%, transparent)` from `.jt .v1-portrait` and `.jt .about-portrait` in `_sass/_layout.scss`. Both selectors are now geometry-only. BC README's "Duotone (image slot)" vocabulary entry replaced by asset-agnostic "Portrait slot". Fixes the doubled-grayscale + visible-tinted-card effect on the new cutout portrait PNG from website-007.
**Verification:** PASS (iteration 1) — verifier confirmed clean jekyll build (0.344s) and grep-confirmed no `grayscale` and no `color-mix` inside the two portrait rule blocks in the generated `_site/assets/css/main.css`.
**Commit:** 83b086f
**Files changed:** 3 (2 worker + moved task file)
**Tests added:** 0 (CSS change; build-clean + grep is the test)
**ADRs written:** none (refinement of an existing token under ADR-0005; no new architectural decision)

---

## 2026-06-03 -- Batch started: [design-system-004]

**Type:** Work / Batch start
**Tasks:** design-system-004 - Portrait styling: drop grayscale filter and tinted background for cutout PNG
**Parallel:** no (1 worker)

---

## 2026-06-03 -- Model / Captured: design-system-004 - Portrait styling: drop grayscale filter and tinted background

**Type:** Model / Capture
**BC:** design-system
**Filed to:** todo (then doing — back-to-back capture+work in this session)
**Summary:** Nach website-007 hat Joshua bemerkt, dass das frische Porträt grau und mit sichtbarem Rand erscheint. Ursache: `_sass/_layout.scss` setzt auf `.v1-portrait` und `.about-portrait` zusätzlich `filter: grayscale(1) contrast(1.1) brightness(0.92)` und `background-color: color-mix(in oklab, var(--fg) 6%, transparent)` — beides sinnvoll für ein rechteckiges Foto mit eigenem Hintergrund (Annahme aus website-001), aber falsch für das jetzt gelieferte freigestellte, bereits-grayscale Cutout-PNG. Joshua entscheidet: beide Properties an beiden Selektoren entfernen.

---

## 2026-06-03 -- Work session ended

**Type:** Work / Session end
**Completed:** 1 (first-try PASS: 1, re-dispatched: 0, skipped: 0)
**Bounced:** 0
**Failed:** 0
**Escalated after verification:** 0
**Commits:** 1 (2d39e35)

---

## 2026-06-03 -- Task verified and completed: website-007 - Homepage portrait image

**Type:** Work / Task completion
**Task:** website-007 - Homepage portrait image — wire up joshua-toepfer-transparent.png
**Summary:** Wired up `site.portrait_image` in `_config.yml` to `assets/images/joshua-toepfer-transparent.png`; homepage (and consequently `/ueber-mich/`) now renders the portrait via the existing `.v1-portrait` background-image slot instead of the placeholder. Corrected the stale portrait path in the website BC README's pages inventory.
**Verification:** PASS (iteration 1) — verifier ran `bundle exec jekyll build` (clean, 0.391s) and confirmed `_site/index.html` contains `.v1-portrait` with `background-image: url('/assets/images/joshua-toepfer-transparent.png')` and no `--placeholder` fallback.
**Commit:** 2d39e35
**Files changed:** 4 (2 worker + image asset + moved task file)
**Tests added:** 0 (config change; build-clean + grep is the test)
**ADRs written:** none

---

## 2026-06-03 -- Batch started: [website-007]

**Type:** Work / Batch start
**Tasks:** website-007 - Homepage portrait image — wire up joshua-toepfer-transparent.png
**Parallel:** no (1 worker)

---

## 2026-06-03 -- Model / Captured: website-007 - Homepage portrait image

**Type:** Model / Capture
**BC:** website
**Filed to:** todo
**Summary:** Joshua hat `assets/images/joshua-toepfer-transparent.png` ergänzt und will es auf der Startseite einbinden. Der Layout-Slot (`site.portrait_image` in `_layouts/home.html`) existiert seit website-001 — fehlt nur der Eintrag in `_config.yml`. Direkt nach `todo/` geschrieben, weil Scope minimal ist (ein Config-Key + README-Path-Korrektur). Hinweis im Task: dieselbe Variable wird auch von `_layouts/about.html` konsumiert, das Bild taucht damit ebenfalls auf `/ueber-mich/` auf — bei Bedarf vorher klären.

---

## 2026-06-02 15:00 -- Backfill: website-006 - Homepage talks fallback

**Type:** Backfill / Capture-as-done
**BC:** website
**Filed to:** done
**Summary:** Captured-after-the-fact. Joshua asked in conversation for a homepage fallback to recent past talks when no upcoming exist. Shipped inline as commit `4816dfe`: `_layouts/home.html` falls back to the 3 most recent past talks under the heading "ZULETZT AUF DER BÜHNE" (more-link "Alle Talks →") when `upcoming_talks` is empty; section hides only when both sets are empty. `talk-card.html` `home` variant reused as-is. Backfill preserves the audit trail; not a precedent for skipping `/agentheim:model` + `/agentheim:work` on non-trivial changes.
**Commit:** 4816dfe

---

## 2026-06-02 14:15 -- Work session ended

**Type:** Work / Session end
**Completed:** 1 (first-try PASS: 1, re-dispatched: 0, skipped: 0)
**Bounced:** 0
**Failed:** 0
**Escalated after verification:** 0
**Commits:** 1 (d1e81fa)

---

## 2026-06-02 14:10 -- Task verified and completed: infra-011 - INNOQ talks sync workflow

**Type:** Work / Task completion
**Task:** infra-011 - INNOQ talks sync workflow (scrape `/de/talks/?all=true&by=joshua-toepfer` → PR)
**Summary:** Shipped the INNOQ talks-sync pipeline per ADR-0007: weekly GHA workflow (`sync-innoq-talks.yml`, `0 4 * * 0`) that scrapes the per-author talks listing, follows pagination, fetches each detail page, and opens one draft PR per run with the merged `_data/talks.yml` on `sync/innoq-talks/<YYYY-MM-DD>`. Introduces the `source: innoq | manual` marker with read-skip + write-passthrough semantics (existing 10 entries migrated to `source: manual`), URL-keyed identity via `source_url`, per-field authority table (INNOQ-authoritative fields overwritten every sync; `video` + `source` preserved as Joshua-authoritative), close-prior-then-open-new PR dedup, three-bucket diff summary in the PR body (New / Status transitions / Field updates, plus optional Ambiguous matches for first-sync composite-key fallback). Refactor: extracted `fetch_with_retry` HTTP politeness primitive from `backfill_innoq` into `innoq_common` so the new talks workflow reuses it; `backfill_innoq._fetch_html` is now a shim. Schema extension to `_data/talks.yml` documented in `website/README.md` (ADR-0007 §10 cross-BC exception); layouts untouched. Test suite grew 89 → 154 (+65).
**Verification:** PASS (iteration 1)
**Commit:** (pending)
**Files changed:** 10 worker files + INDEX + protocol + ADR-0007 + research file
**Tests added:** 65 (total: 154)
**ADRs written:** none (ADR-0007 was authored during refinement)

---

## 2026-06-02 13:40 -- Batch started: [infra-011]

**Type:** Work / Batch start
**Tasks:** infra-011 - INNOQ talks sync workflow (scrape `/de/talks/?all=true&by=joshua-toepfer` → PR)
**Parallel:** no (1 worker)

---

## 2026-06-02 13:30 -- Model / Refined + Promoted: infra-011 - INNOQ talks sync workflow

**Type:** Model / Refine + Promote
**BC:** infrastructure
**Status after:** todo
**Summary:** Orchestrator routed to researcher (live-fetched the INNOQ talks listing + 3 detail pages: confirmed server-rendered, no talks feed, 25/page pagination, per-talk detail page carries city/abstract/slides URL; selectors documented per-field with confidence levels) and architect (ADR-0007: scrape-only with URL identity via `source_url`, per-field authority table making INNOQ-authoritative fields overwritten every sync while `video` and `source` stay Joshua-authoritative, `source: innoq | manual` marker for hand-edit coexistence with a one-time migration of today's `_data/talks.yml` as the worker's first commit, one PR per sync run on `sync/innoq-talks/<YYYY-MM-DD>`, weekly Sundays 04:00 UTC, close-prior-then-open-new dedup, new `innoq_talks.py` module while `innoq_common.py` stays generic). The seven original open questions are now resolved; acceptance criteria are concrete and testable across migration / workflow+module / discovery+parsing / diff+merge / PR-shape+scheduling / politeness+docs.
**Split into:** none (single-task refinement)
**ADRs written:** 0007
**Research filed:** innoq-talks-page-2026-06-02

---

## 2026-06-02 13:00 -- Model / Captured: infra-011 - INNOQ talks sync workflow

**Type:** Model / Capture
**BC:** infrastructure
**Filed to:** backlog
**Summary:** New sync workflow analogous to infra-004 (article incremental) and infra-005 (article backfill scrape), but for talks: scrape `https://www.innoq.com/de/talks/?all=true&by=joshua-toepfer`, diff against `_data/talks.yml`, open a PR on changes. Filed to backlog because key decisions are still open: full HTML structure of the talks page, field mapping to the YAML schema, diff & PR shape (talks live in one file, unlike articles), update-vs-additive semantics (talks change after creation — `upcoming` → `past`, slides/video added later), hand-edit coexistence. Refinement will likely spawn a research task on the talks-page HTML (analogue of `innoq-staff-page-scrape-2026-05-27` for talks).

---

## 2026-06-02 12:18 -- Work session ended

**Type:** Work / Session end
**Completed:** 1 (first-try PASS: 1, re-dispatched: 0, skipped: 0)
**Bounced:** 0
**Failed:** 0
**Escalated after verification:** 0
**Commits:** 1 (8590d68)

---

## 2026-06-02 12:15 -- Task verified and completed: infra-010 - Fix srcset parser for Cloudinary commas-in-URL

**Type:** Work / Task completion
**Task:** infra-010 - Fix srcset parser to handle Cloudinary commas-in-URL
**Summary:** Replaced naive `srcset.split(",")` in `innoq_common.largest_src_from_srcset` with a regex split on `,\s+(?=https?://)` so Cloudinary's URL-internal transformation commas (`c_limit,f_auto,q_auto,w_NNN`) survive intact. Largest-width pick now returns the absolute Cloudinary URL instead of a relative-path fragment, fixing the 4 broken body images in the 2022 "Typist wechsel dich" backfill PR (and any future INNOQ article with Cloudinary srcsets). Both sync and backfill workflows benefit since they share the helper.
**Verification:** PASS (iteration 1)
**Commit:** (pending)
**Files changed:** 3 worker files + INDEX + protocol updates
**Tests added:** 3 (total: 89)
**ADRs written:** none

---

## 2026-06-02 12:00 -- Batch started: [infra-010]

**Type:** Work / Batch start
**Tasks:** infra-010 - Fix srcset parser to handle Cloudinary commas-in-URL
**Parallel:** no (1 worker)

---

## 2026-06-02 10:50 -- Model / Captured + Promoted: infra-010

**Type:** Model / Capture + Promote
**BC:** infrastructure
**Filed to:** todo
**Summary:** Image-bug found while reviewing the re-triggered 2022 backfill PR. The 4 body images render as broken (404) because the converter writes relative-path fragments like `w_2800/v1/uploads-production/<id>?_a=BACMTiAE` instead of absolute Cloudinary URLs. Root cause: `largest_src_from_srcset` splits the `srcset` attribute naively on `,`, but INNOQ uses Cloudinary URLs that contain commas *inside* their transformation parameters (`c_limit,f_auto,q_auto,w_2800`). Naive split shreds the URLs into fragments. Fix: split on `,\s+(?=https?://)` to only break on actual srcset candidate separators. ~10 lines of Python + 4 new tests. NOT a local-mirroring issue — Cloudinary continues to serve assets, just needs us to emit correct absolute URLs.

---

## 2026-06-02 10:28 -- Work session ended

**Type:** Work / Session end
**Completed:** 1 (first-try PASS: 1)
**Bounced:** 0
**Failed:** 0
**Escalated after verification:** 0
**Commits:** 1 (6e06804)

---

## 2026-06-02 10:25 -- Task verified and completed: infra-009 - INNOQ conclusion-section merge

**Type:** Work / Task completion
**Task:** infra-009 - Extract INNOQ `<section class="conclusion">` Fazit into synced body
**Summary:** Added `_merge_conclusion_section` + `_strip_empty_headings` to `innoq_common.convert_html_to_markdown` and `_merge_sibling_conclusion` to `backfill_innoq.extract_article_body`. Older INNOQ templates' Fazit (sibling `<section class="conclusion">` of `<article>` under `<main>`) is now lifted into the body before strip + heading-promotion. Empty headings (e.g. INNOQ's empty `conclusion-subheadline`) stripped during the cleanup pass, runs AFTER heading-promotion so newly-emptied headings are caught. 9 new tests (5 ConclusionSectionTests + 4 ConclusionMergeTests including end-to-end), full suite 86 / 86 green. No regression on 2023-style articles (Fazit already inside article).
**Verification:** PASS (iteration 1)
**Commit:** (pending)
**Files changed:** 5 worker files + INDEX + protocol updates
**Tests added:** 9 (total: 86)
**ADRs written:** none

---

## 2026-06-02 10:10 -- Batch started: [infra-009]

**Type:** Work / Batch start
**Tasks:** infra-009 - Extract INNOQ `<section class="conclusion">` Fazit into synced body
**Parallel:** no (1 worker)

---

## 2026-06-02 10:00 -- Model / Captured + Promoted: infra-009

**Type:** Model / Capture + Promote
**BC:** infrastructure
**Filed to:** todo
**Summary:** Body-extraction bug found while reviewing the 2022 "Typist wechsel dich" backfill PR. The Fazit section is missing entirely. Root cause: INNOQ's older-article template (2022 and earlier) puts the conclusion in a `<section class="conclusion">` sibling of `<article>` under `<main>`, not inside the article wrapper. Our converter only extracts `<article>` content. 2021er had Fazit inside `<article>` (no issue); 2023er also (no issue); 2022 is the visible case. Fix: extend body extraction to also pick up the sibling conclusion section, merge into the body before strip pipeline; add empty-heading stripping for defensive cleanup of the empty `<h3 class="conclusion-subheadline">`. 4 new tests, post-ship Joshua re-runs backfill for 2022 via URL-list mode.

---

## 2026-06-01 14:28 -- Work session ended

**Type:** Work / Session end
**Completed:** 1 (first-try PASS: 1)
**Bounced:** 0
**Failed:** 0
**Escalated after verification:** 0
**Commits:** 2 (6851dcb design follow-up, de346f6 infra-008)

---

## 2026-06-01 14:25 -- Task verified and completed: infra-008 - Heading promotion

**Type:** Work / Task completion
**Task:** infra-008 - Promote heading levels (H3→H2 etc.) during INNOQ body conversion
**Summary:** Added `_promote_heading_levels` helper to `innoq_common.convert_html_to_markdown` (strips body H1, promotes H3-H6 by one level via BeautifulSoup, leaves H2 untouched). Wired in before markdownify runs. Both INNOQ workflows (sync + backfill) benefit since they share the converter. 8 new tests in `HeadingPromotionTests`; full suite 77 / 77 green (was 69). Verifier flagged a small spec inconsistency in `test_h2_untouched`'s prose example — worker resolved against the promotion-table rule consistently.
**Verification:** PASS (iteration 1)
**Commit:** (pending)
**Files changed:** 3 worker files + INDEX + protocol updates
**Tests added:** 8 (total: 77)
**ADRs written:** none

---

## 2026-06-01 14:05 -- Batch started: [infra-008]

**Type:** Work / Batch start
**Tasks:** infra-008 - Promote heading levels (H3→H2 etc.) during INNOQ body conversion
**Parallel:** no (1 worker)

---

## 2026-06-01 14:00 -- Model / Captured + Promoted: infra-008

**Type:** Model / Capture + Promote
**BC:** infrastructure
**Filed to:** todo (skipped backlog — small, well-specified, immediately actionable)
**Summary:** Heading-hierarchy follow-up to website-005. The 2023 Remote Mob Programming post's body sections render as small H3s because INNOQ's HTML uses H1=title, H2=subtitle, H3=section and the converter preserves levels 1:1 — but the site's H1 is in the post-hero, so the body should start at H2. Joshua noticed the visual mismatch ("ist es richtig, dass ich beim Inhalt mit der ersten Unterüberschrift anfange?"). Fix: promote h3→h2, h4→h3, h5→h4, h6→h5 in `innoq_common.py`'s body extraction before markdownify runs. H1 in body stripped (defensive — already in frontmatter title). H2 in body untouched. This is "Option B" from website-005's spec, deferred when Option A (TOC JS scan h2+h3) shipped. Both INNOQ workflows benefit since they share `innoq_common.py`. Existing posts need re-conversion: 2023er via force-resync; 2021er + 2022er (still open backfill PRs) closed + re-triggered. ~15 min worker run.

---

## 2026-06-01 13:32 -- Work session ended

**Type:** Work / Session end
**Completed:** 1 (first-try PASS: 1)
**Bounced:** 0
**Failed:** 0
**Escalated after verification:** 0
**Commits:** 1 (f9e4d6e)

---

## 2026-06-01 13:30 -- Task verified and completed: website-005 - Syndicated post polish

**Type:** Work / Task completion
**Task:** website-005 - Syndicated post polish: visible source link at end + working TOC
**Summary:** Added conditional `.post-source` aside in `_layouts/post.html` rendering between `.post-body` and `.post-pager` when `page.source` is set — links via `rel="external"` to `page.canonical_url`, uses `.link` + `.mono` classes, German wording ("↗ Ursprünglich erschienen auf innoq.com."). Styled in `_sass/_layout.scss` with `border-top: var(--rule)`, `color: var(--fg-dim)` (AA-passing per design-system-002), 16px padding-top, 13px font-size — quiet footnote, not banner. Fixed empty TOC by switching `assets/js/theme-toggle.js`'s scanner to `body.querySelectorAll("h2, h3")` (Option A — simpler, more local, robust to source-format quirks). 2023 INNOQ post now shows 7-entry TOC in browser; Hello-Welt control untouched. pa11y-ci stays green (7/7 URLs × dark + light, 0 errors).
**Verification:** PASS (iteration 1) — verifier re-ran pa11y-ci live
**Commit:** (pending)
**Files changed:** 3 worker files + 2 task/index/protocol updates
**Tests added:** 0 (UI/template work; pa11y-ci is the standing UI gate)
**ADRs written:** none

---

## 2026-06-01 13:05 -- Batch started: [website-005]

**Type:** Work / Batch start
**Tasks:** website-005 - Syndicated post polish: visible source link at end + working TOC
**Parallel:** no (1 worker)

---

## 2026-06-01 13:00 -- Model / Captured + Promoted: website-005

**Type:** Model / Capture + Promote
**BC:** website
**Filed to:** todo
**Summary:** Two UX bugs on the first live INNOQ-synced post (2023-06-23 Remote Mob Programming, just merged + published) bundled as one polish task. (1) No visible source link at the end of post body — `canonical_url` is only in `<head>` for SEO and the meta-line shows "↗ Erscheint auch auf innoq.com" at the top, but readers who finish reading should be reminded to click through to innoq.com. Fix: add a `.post-source` block in `_layouts/post.html` between `.post-body` and `.post-pager`, conditional on `page.source`. (2) TOC aside renders empty — JS scans `<h2>` only, but INNOQ articles use `<h3>` for section headings (H1=title is in hero, H2=subtitle absent, H3=sections per markdownify-preserved hierarchy). Fix: either extend the TOC scan to `h2, h3` (Option A — simpler, recommended) or promote `<h3>` → `<h2>` during conversion in `innoq_common.py` (Option B — more invasive). Worker picks. Two changes, one task; small enough for one worker run with verifier.

---

## 2026-05-28 12:52 -- Work session ended

**Type:** Work / Session end
**Completed:** 1 (first-try PASS: 1)
**Bounced:** 0
**Failed:** 0
**Escalated after verification:** 0
**Commits:** 1 (021c7a8)
**Notable:** Closes the spec/implementation gap from infra-005. Unblocks Joshua's 2023-article re-sync after pushing.

---

## 2026-05-28 12:50 -- Task verified and completed: infra-007 - Backfill URL-list bypass

**Type:** Work / Task completion
**Task:** infra-007 - Backfill URL-list mode bypasses dedup (force-resync semantic)
**Summary:** Added keyword-only `bypass_dedup` parameter to `build_plan()` in `backfill_innoq.py` (Approach A). URL-list mode (`urls` workflow input non-empty) now passes `bypass_dedup=True`, skipping both `existing_canonical_urls` and `pr_history_has_branch` checks while logging `URL-list (bypassed dedup): <url>`. Auto-discovery flow byte-identical at the default. 4 new tests in `BuildPlanDedupBypassTests` (2 bypass-mode, 2 regression guards); full suite 69 tests passing. README's Backfill-workflow sub-section now explicitly states the bypass semantic. Workflow YAML and `innoq_common.py` untouched.
**Verification:** PASS (iteration 1)
**Commit:** (pending)
**Files changed:** 3 worker files + 2 task/index/protocol updates
**Tests added:** 4 (total: 69)
**ADRs written:** none

---

## 2026-05-28 12:35 -- Batch started: [infra-007]

**Type:** Work / Batch start
**Tasks:** infra-007 - Backfill URL-list mode bypasses dedup (force-resync semantic)
**Parallel:** no (1 worker)

---

## 2026-05-28 12:30 -- Model / Captured + Promoted: infra-007

**Type:** Model / Capture + Promote
**BC:** infrastructure
**Filed to:** todo (skipped backlog — task is small, well-specified, immediately actionable)
**Summary:** Spec/implementation gap in `infra-005` (backfill workflow). The `urls` workflow_dispatch input was specified as an explicit re-sync mechanism that bypasses dedup, but the worker's implementation applied the two-tier dedup chain (`_posts/` canonical_url + `gh pr list --state all --head <branch>`) to every URL regardless of input source. Surfaced today when Joshua tried to re-trigger backfill for the 2023 article (whose original conversion needed cleanup of 4 source-side URL typos in INNOQ's HTML): closed the existing PR, deleted the branch, re-ran with `urls: <URL>` — got skipped because GitHub keeps closed PR records and the dedup check sees them. Joshua's reasoning ("Wenn ich eine canonical URL angebe soll er ein PR aufmachen, sonst hat URL-Input keinen Zweck") is exactly the spec intent. infra-007 is a small targeted fix: URL-list mode skips both dedup checks; auto-discovery mode unchanged. Should be 1 conditional branch in `build_plan`, 2 new tests, 1 README clarification sentence. No new ADR.
**Split into:** none
**ADRs written:** none expected

---

## 2026-05-28 11:22 -- Work session ended

**Type:** Work / Session end
**Completed:** 1 (first-try PASS: 1)
**Bounced:** 0
**Failed:** 0
**Escalated after verification:** 0
**Commits:** 1 (4a36229)
**Notable:** This closes the bug → automation → fix loop: infra-006 (pa11y-ci) detected the failure, surfaced concrete data, drove design-system-002's re-refinement, the fix shipped and the verifier re-ran pa11y-ci live to confirm 0 errors per mode. CI is back to green; design-system, website, and infrastructure BCs now all have empty backlog/todo/doing.

---

## 2026-05-28 11:20 -- Task verified and completed: design-system-002 - WCAG AA token routing

**Type:** Work / Task completion
**Task:** design-system-002 - WCAG AA fix — route text-bearing elements to AA-passing tokens
**Summary:** Audited all 23 `var(--fg-faint)` usages across `_sass/_layout.scss`, `_sass/_posts.scss`, `_sass/_base.scss`; switched 22 text-bearing usages to `var(--fg-dim)` (which already passes AA at 7.5:1 dark / 6.0:1 light), kept 1 truly decorative (`.numeral`, currently unreferenced) with rationale comment. Reclassified `.row .arrow` and `.related-post-row .arrow` as text-bearing after pa11y flagged the Unicode `→` as content. Rerouted `.post-body a` in `_sass/_typography.scss` to `color: inherit` with hover lift to accent. **`_sass/_tokens.scss` untouched** — no token-value changes. Verifier re-ran pa11y-ci@4.1.1 live: 7/7 URLs × 2 modes = 0 errors (down from 93 errors/mode). Accessibility CI now goes green.
**Verification:** PASS (iteration 1) — verifier re-ran pa11y-ci live for definitive confirmation
**Commit:** (pending)
**Files changed:** 4 SCSS files
**Tests added:** 0 (pa11y-ci itself is the test suite, validated green)
**ADRs written:** none

---

## 2026-05-28 10:55 -- Batch started: [design-system-002]

**Type:** Work / Batch start
**Tasks:** design-system-002 - WCAG AA fix — route text-bearing elements to AA-passing tokens
**Parallel:** no (1 worker)

---

## 2026-05-28 10:50 -- Model / Refined + Promoted: design-system-002

**Type:** Model / Refine + Promote
**BC:** design-system
**Status after:** todo
**Summary:** Scope broadened and fix path locked in after pa11y-ci output and Joshua's Pfad-2 choice. The active failure is `--fg-faint` text usages (footer h4, `.sep`, `.count`, `.row .arrow`) failing 2.82:1 dark and 2.35:1 light, not the accent palette. The companion `--fg-dim` token already passes AA (7.5:1 dark, 6.0:1 light), so the fix is usage-routing not value-recalibration: audit `var(--fg-faint)` in `_sass/`, switch text-bearing usages to `var(--fg-dim)`, keep decorative usages (e.g. icon-glyph arrows) on `--fg-faint`. Bundled in the same task: `.post-body a` switches from `color: var(--accent)` to `color: inherit` (Option C from the 2026-05-28 conversation) — same pattern, addresses the original accent-link concern that pa11y-ci hasn't yet seen because no post bodies have inline links. Token values themselves are NOT changed. Filename slug updated from `fix-light-mode-accent` to `wcag-aa-token-audit` to reflect new scope. depends_on `[design-system-001, infra-006]` both done → promoted to todo.
**Split into:** none (consolidated)
**ADRs written:** none

---

## 2026-05-28 10:32 -- Work session ended

**Type:** Work / Session end
**Completed:** 2 (first-try PASS: 2, re-dispatched: 0, skipped: 0)
**Bounced:** 0
**Failed:** 0
**Escalated after verification:** 0
**Commits:** 2 (8c968d0, 15d899e)
**Tasks done this session:** infra-005 (INNOQ backfill workflow), infra-006 (pa11y-ci WCAG AA in CI)
**Key user hand-off:** design-system-002 scope needs to expand from "light-mode accent only" to "both-mode `--text-muted` calibration" before being PROMOTEd — see infra-006's Outcome section for the concrete pa11y-ci violation list and the recommended fix direction.

---

## 2026-05-28 10:30 -- Task verified and completed: infra-006 - pa11y-ci WCAG AA in CI

**Type:** Work / Task completion
**Task:** infra-006 - Automated WCAG AA checks via pa11y-ci in CI (light + dark mode)
**Summary:** Shipped `.github/workflows/accessibility.yml` running pa11y-ci@4.1.1 against the 7 implemented routes × both modes (14 audit passes per workflow run). Worker chose a `sed`-rewrite of `_site/**/*.html` between two pa11y-ci invocations to inject light mode, after correctly identifying that pa11y has no `evaluate` action (the spec's proposed mechanism was wrong). The sed approach mutates both the `data-mode` attribute on `<html>` and the localStorage-reading boot script's fallback value, defeating Chrome headless's `prefers-color-scheme: light` default. Local validation: dark mode surfaces 93 AA violations at 2.82:1, light mode 93 violations at 2.35:1, all on `--text-muted`-styled elements (`.arrow`, `.count.mono`, `.sep`, footer `h4`). **Scope-expanding finding**: design-system-002 needs to broaden from "light-mode accent only" to "both-mode `--text-muted` calibration" — full hand-off documented in the task's Outcome section.
**Verification:** PASS (iteration 1)
**Commit:** (pending)
**Files changed:** 4 worker files + 3 task/index/protocol updates
**Tests added:** 0 (config-only task; pa11y-ci itself is the test suite)
**ADRs written:** none

---

## 2026-05-28 10:05 -- Batch started: [infra-006]

**Type:** Work / Batch start
**Tasks:** infra-006 - Automated WCAG AA checks via pa11y-ci in CI (light + dark mode)
**Parallel:** no (1 worker)

---

## 2026-05-28 10:00 -- Task verified and completed: infra-005 - INNOQ historical backfill workflow

**Type:** Work / Task completion
**Task:** infra-005 - INNOQ historical backfill workflow (staff-page scrape, German articles only)
**Summary:** Shipped the scrape-based backfill workflow as a sibling to the feed-poll incremental sync. Worker's curl spike (required first step) confirmed `og:title`, `og:url`, `<time datetime>`, and `<article class="article-page-default">` are reliably present on INNOQ article pages; found `article:published_time` absent (handled gracefully via `<time datetime>` fallback) and `<link rel=canonical>` unreliable (some 2023/06-style reprints point external — code uses fetched URL instead). Auto-discovery returns 3 DE articles today as the research predicted. Worker extended `innoq_common.py` with `ScrapedArticle` dataclass, `build_backfill_pr_title/_body`, `largest_src_from_srcset` (promotes Cloudinary srcset → src), `parse_german_date`, `split_url_list_input`, plus `BACKFILL_BRANCH_PREFIX`/`BACKFILL_DISCOVERY_URL` constants. Test suite expanded from 22 → 65 tests (43 new), all passing.
**Verification:** PASS (iteration 1)
**Commit:** (pending)
**Files changed:** 6 worker files + 3 task/index/protocol updates
**Tests added:** 43 (total: 65)
**ADRs written:** none (ADR-0006 already covers the architecture)

---

## 2026-05-28 09:40 -- Batch started: [infra-005]

**Type:** Work / Batch start
**Tasks:** infra-005 - INNOQ historical backfill workflow (staff-page scrape, German articles only)
**Parallel:** no (1 worker — infra-006 demoted to next batch due to shared `infrastructure/README.md` conflict)

---

## 2026-05-28 09:30 -- Model / Refined + Captured: design-system-002 deferred → blocked on new infra-006

**Type:** Model / Refine + Capture
**BC:** design-system + infrastructure
**Status after:** design-system-002 stays in backlog (deferred); infra-006 filed to todo
**Summary:** Joshua looked at concrete proposed color values for both fix options A (darken `--accent` L) and B (separate `--accent-text` token) and rejected both visually. A third path emerged in conversation — Option C (`.post-body a` uses `color: inherit`, animated underline carries link signal, tokens untouched) — but rather than commit to it now, Joshua chose to build automated WCAG checks first so the next refinement of design-system-002 is informed by concrete pa11y-ci output rather than estimates. New task `infra-006` captures the pa11y-ci CI setup (covers all 7 routes × dark + light mode, fails on WCAG 2.1 AA violations, no package.json — ephemeral npx). design-system-002 updated with `depends_on: [design-system-001, infra-006]`, a "Deferred 2026-05-28" section, the rejected A/B path, and 5 candidate fix paths (C + D-G) to re-evaluate once pa11y-ci surfaces real failures. The first infra-006 run is expected to fail — that's the proof the check works.
**Split into:** infra-006 (new, todo)
**ADRs written:** none

---

## 2026-05-28 09:10 -- Model / Promoted: infra-005

**Type:** Model / Promote
**BC:** infrastructure
**From → To:** backlog → todo

---

## 2026-05-28 09:00 -- Concept created: innoq-sync

**Type:** Concept / Created
**BC:** infrastructure
**Page:** `.agentheim/contexts/infrastructure/concepts/innoq-sync.md`
**Derived from:** ADR 0002, ADR 0006, research innoq-staff-feed-2026-05-27, research innoq-staff-page-scrape-2026-05-27, done infra-002, done infra-004, backlog infra-005
**Summary:** Synthesis page for the INNOQ → joshuatoepfer.de mirror — the two workflows (live sync-innoq, planned backfill-innoq), the shared `innoq_common.py` module, the four-step filter chain (author email, German language, /de/ path, /articles/ segment), the two-step PR-history dedup, the manual two-step publish flow, and the force-resync escape hatch. 51-line body, well within the 60-line cap. Lists each source artifact in `derived_from` for drift detection.

---

## 2026-05-27 19:38 -- Work session ended

**Type:** Work / Session end
**Completed:** 1 (first-try PASS: 1, re-dispatched: 0, skipped: 0)
**Bounced:** 0
**Failed:** 0
**Escalated after verification:** 0
**Commits:** 1 (f4e0629)
**Concept candidates surfaced:** innoq-sync (converging on 4 artifacts: infra-002, infra-004, ADR-0002, ADR-0006)
**Unblocked downstream:** infra-005 (was waiting on infra-004; now eligible for PROMOTE)

---

## 2026-05-27 19:35 -- Task verified and completed: infra-004 - INNOQ author sync pipeline (incremental)

**Type:** Work / Task completion
**Task:** infra-004 - INNOQ author sync pipeline — incremental, feed-based (German articles only)
**Summary:** Delivered the incremental INNOQ sync pipeline — `.github/workflows/sync-innoq.yml` (cron + workflow_dispatch with `force_resync` and `feed_url_override` inputs; matrix shape for one-PR-per-article) plus `sync_innoq.py` and the shared `innoq_common.py` module that `infra-005` will import. Enforces the four-step filter chain (author email, xml:lang=de, /de/ path, /articles/ segment), two-step PR-history dedup (`_posts/` canonical_url + `gh pr list --state all --head sync/innoq/<slug>`), force-resync that preserves `topic`/`published` on a timestamped branch, and fail-loud observability. 22 unit tests passing. ADR-0006 records the dual-workflow + full-body + PR-history-dedup + force-resync + Python + blank-topic decisions; infrastructure README has the new Sync workflow section including the smoke-test procedure for Joshua's first deploy. Orchestrator added `__pycache__/` and `*.py[cod]` to `.gitignore` as a small follow-up cleanup so Python toolchain artifacts don't accumulate.
**Verification:** PASS (iteration 1)
**Commit:** (pending)
**Files changed:** 6 worker files + 3 task/index/protocol updates + .gitignore
**Tests added:** 22
**ADRs written:** 0006-innoq-sync-architecture.md

---

## 2026-05-27 19:20 -- Batch started: [infra-004]

**Type:** Work / Batch start
**Tasks:** infra-004 - INNOQ author sync pipeline — incremental, feed-based (German articles only)
**Parallel:** no (1 worker)

---

## 2026-05-27 19:15 -- Model / Promoted: infra-004

**Type:** Model / Promote
**BC:** infrastructure
**From → To:** backlog → todo

---

## 2026-05-27 19:10 -- Model / Captured: infra-005

**Type:** Model / Capture
**BC:** infrastructure
**Filed to:** backlog
**Summary:** Captured the historical backfill workflow as a sibling to infra-004, splitting the previous "Joshua does manual backfill" plan into an automated job. Discovery source is `https://www.innoq.com/de/written/?by=joshua-toepfer` (per research `innoq-staff-page-scrape-2026-05-27`) — server-rendered, DE-only article URLs, robots.txt permissive. Parser stack: `requests` + `BeautifulSoup(lxml)` + `markdownify`. Trigger: `workflow_dispatch` only with `urls` (override) and `dry_run` inputs. Branch namespace `backfill/innoq/<slug>` to distinguish from infra-004's `sync/innoq/<slug>`. Shared label `sync-innoq`. `depends_on: [infra-004]` because both workflows share `.github/scripts/innoq_common.py` which infra-004 delivers. Article-count expectation: 3 (not Joshua's earlier ~5 estimate — research surfaced that the staff page counts DE/EN duplicates while `/de/written/?by=...` does not; flagged for sanity-check). One pre-implementation open: 5-min curl spike on `<head>` meta tags + `<article>` class + code-block convention — left to worker as first step rather than blocking PROMOTE.

---

## 2026-05-27 18:55 -- Research / Filed: innoq-staff-page-scrape-2026-05-27

**Type:** Research / Report filed
**BC:** infrastructure
**Related task:** infra-005
**Report:** `.agentheim/knowledge/research/innoq-staff-page-scrape-2026-05-27.md`
**Summary:** Investigated INNOQ staff-page HTML structure and scrape feasibility for the historical backfill workflow. Confirmed: server-rendered HTML, no JS/Cloudflare, robots.txt permissive for current trailing-slash article URLs. Discovery surface: `/de/written/?by=joshua-toepfer` (DE-only, articles-only, no DE/EN duplicates — 3 entries today). Parser: BeautifulSoup(lxml). Body strip-list: newsletter forms, author-bio, "Weitere Informationen" boxes, footer, share icons. Open spike: `<head>` meta tag inventory (`article:published_time`, `og:title`, `link rel=canonical`, `<time datetime>`) — WebFetch strips `<head>` so could not verify; ~5 min curl spike recommended before parser commit. Indexed under infrastructure research-local.

---

## 2026-05-27 18:50 -- Model / Refined: infra-004

**Type:** Model / Refine
**BC:** infrastructure
**Status after:** backlog (ready for PROMOTE)
**Summary:** All previously-open questions resolved into a "Decisions" section. Body content: full Atom `<content>` (resolves ADR-0002's deferred legal question — Joshua greenlit full body) → markdownify → Markdown, images stay as remote `<img>` references to Cloudinary. Workflow language: Python (`feedparser` + `markdownify` + `pyyaml`). Dedup: 2-tier via `_posts/*.md` canonical_url + `gh pr list --state all --head sync/innoq/<slug>` — branches deleted on PR close (`delete-branch: true`), PR history is the dedup memory so no persistent branches accumulate. Force-resync via `workflow_dispatch` input `force_resync` (comma-separated URLs): bypasses dedup, preserves existing file's `topic`/`published` values, regenerates body, branch suffix `-resync-<timestamp>`. Topic mapping: left blank (Joshua fills in manually). Failure mode: fail loudly (job status = failed; default GH Actions email). Feed-window risk: accepted; backfill is now `infra-005`'s job. Architecture explicitly split into two workflows sharing `innoq_common.py`; `infra-004` now `blocks: [infra-005]`. Worker will write `ADR-0006` covering dual-workflow architecture + full-body decision + PR-history dedup + force-resync.
**Split into:** [infra-005]
**ADRs written:** none yet (ADR-0006 to be authored by infra-004's worker)

---

## 2026-05-27 18:42 -- Work session ended

**Type:** Work / Session end
**Completed:** 1 (first-try PASS: 1, re-dispatched: 0, skipped: 0)
**Bounced:** 0
**Failed:** 0
**Escalated after verification:** 0
**Commits:** 1 (2e85ac8)

---

## 2026-05-27 18:40 -- Task verified and completed: website-004 - Replace placeholder posts with Hello-Welt

**Type:** Work / Task completion
**Task:** website-004 - Replace placeholder posts with a single Hello-World post
**Summary:** Deleted the 6 placeholder posts under `_posts/` and replaced them with a single `_posts/2026-05-27-hello-welt.md` (short German "Hallo, Welt." greeting mentioning the three topic areas, signed "— Joshua"). `bundle exec jekyll build` completes cleanly; post renders at `/posts/2026/05/27/hello-welt/` (per `_config.yml`'s permalink scheme — task spec wrongly predicted `/blog/hello-welt/`; verifier flagged the spec inconsistency but the worker correctly preferred the explicit "don't touch `_config.yml`" constraint).
**Verification:** PASS (iteration 1)
**Commit:** (pending)
**Files changed:** 7 (1 new post + 6 deletions)
**ADRs written:** none

---

## 2026-05-27 18:35 -- Research / Filed: innoq-staff-feed

**Type:** Research / Report filed
**BC:** infrastructure
**Related task:** infra-004
**Report:** `.agentheim/knowledge/research/innoq-staff-feed-2026-05-27.md`
**Summary:** Investigated INNOQ's staff page structure and per-author feed availability for Joshua Töpfer's INNOQ author sync pipeline (`infra-004`). Key findings: (1) No per-author feed exists — every probed URL pattern returned 404/406, and the staff page body links only to the global feed. (2) Only feed available is global rolling Atom 1.0 at `/{de,en}/feed.atom`, ~20–25 entries, oldest seen 2026-02-26 — Joshua's content not currently in either feed's window. (3) Feed has high-quality author metadata (`<author><name/email/uri>`) but NO `<category>` element — content type must be inferred from URL path segment (`/talks/`, `/articles/`, `/podcast/`, `/blog/`). (4) Staff page is canonical complete listing but has no JSON-LD/microdata. Sitemap.xml is collection-level only. (5) Recommendation: hybrid — scrape staff page for backfill, poll global `/de/feed.atom` filtered by `email = joshua.toepfer@innoq.com` for incremental sync. Constraint "German articles only" is enforceable via `<content xml:lang="de">` or `/de/` URL prefix. Open questions: raw `<head>` inspection (curl-grep), staff-page pagination URL pattern, JSON content negotiation. Filed to infrastructure INDEX.

---

## 2026-05-27 18:18 -- Batch started: [website-004]

**Type:** Work / Batch start
**Tasks:** website-004 - Replace placeholder posts with a single Hello-World post
**Parallel:** no (1 worker)

---

## 2026-05-27 18:15 -- Model / Captured: website-004, infra-004

**Type:** Model / Capture
**BC:** website, infrastructure
**Filed to:** todo (website-004), backlog (infra-004)
**Summary:** Joshua flagged the existing `_posts/` content as placeholder and wants it replaced with a single Hello-Welt post before real INNOQ articles arrive — captured as `website-004` (ready-to-work in todo, lists exact files to delete + the new file's frontmatter). The bigger ask is implementing the INNOQ author sync pipeline ADR-0002 already designed, with an explicit new constraint: German articles only (English filtered out). Author profile: https://www.innoq.com/de/staff/joshua-toepfer/. Captured as `infra-004` in backlog with 8 open questions (RSS-vs-scrape discovery, language indicator, first-run flood handling, body content, PR tooling, script language, topic mapping, failure observability). Next step on infra-004: spawn the `research` skill on INNOQ's staff-page structure and per-author feed format before REFINE.

---

## 2026-05-27 18:06 -- Work session ended

**Type:** Work / Session end
**Completed:** 2 (first-try PASS: 2, re-dispatched: 0, skipped: 0)
**Bounced:** 0
**Failed:** 0
**Escalated after verification:** 0
**Commits:** 2

---

## 2026-05-27 18:05 -- Task verified and completed: website-003 - Document implemented pages and data sources

**Type:** Work / Task completion
**Task:** website-003 - Document implemented pages and data sources (talks, ueber-mich, impressum, datenschutz, post layout)
**Summary:** Extended the website BC README with new ubiquitous-language entries and a Pages inventory covering all 7 current routes; appended 2026-05-27 Amendment sections to done/website-001 (homepage now also has newest-posts, focus areas, upcoming-talks, duotone portrait) and done/website-002 (blog now year-grouped with filter chips; post layout now has hero, sticky TOC, pager, related-posts); legacy `/posts/` confirmed removed in 4d4fb3e. ADR-0005 related_tasks bidirectionally updated with website-003.
**Verification:** PASS (iteration 1)
**Commit:** a68641c
**Files changed:** 7
**ADRs written:** none

---

## 2026-05-27 17:56 -- Batch started: [website-003]

**Type:** Work / Batch start
**Tasks:** website-003 - Document implemented pages and data sources (talks, ueber-mich, impressum, datenschutz, post layout)
**Parallel:** no (1 worker)

---

## 2026-05-27 17:55 -- Task verified and completed: design-system-003 - Document redesigned visual system

**Type:** Work / Task completion
**Task:** design-system-003 - Document redesigned visual system (Geist + oklch + multi-accent + container queries)
**Summary:** Documented the new visual system via ADR-0005 (filed as 0005 because 0004 was already taken by github-pages-initial-deployment), marked ADR-0003 superseded, rewrote the design-system BC README, and refined design-system-002 (light-mode contrast) with measured WCAG ratios — amber/coral/lime FAIL body-text 4.5:1 against `#f7f7f5` (~3.3-3.7:1), only blue passes (~6.5:1); bug stays in backlog with concrete fix options.
**Verification:** PASS (iteration 1)
**Commit:** 9174503
**Files changed:** 9
**ADRs written:** 0005-redesigned-visual-system.md (plus frontmatter-only edit to 0003)

---

## 2026-05-27 17:35 -- Batch started: [design-system-003]

**Type:** Work / Batch start
**Tasks:** design-system-003 - Document redesigned visual system (Geist + oklch + multi-accent + container queries)
**Parallel:** no (1 worker)

---

## 2026-05-27 17:30 -- Model / Captured: design-system-003, website-003

**Type:** Model / Capture
**BC:** design-system, website
**Filed to:** todo
**Summary:** Two documentation backfill tasks for a redesign delivered by Claude Design (handoff in `design_handoff_jekyll/`) that was already implemented in `_layouts/`, `_includes/`, `_sass/`, `_data/`, `assets/`. design-system-003 documents the new visual system (Geist + oklch tokens + multi-accent palette + container queries + theme toggle + accent-mark) and supersedes ADR-0003 with a new ADR-0004; also re-evaluates design-system-002 (light-mode accent contrast bug) against the new oklch light variants. website-003 documents the implemented pages (talks, ueber-mich, impressum, datenschutz) and the richer homepage/blog/post layouts, plus the new `_data/` sources, with amendments appended to the existing done tasks website-001 and website-002. The handoff folder is treated as temporary scaffolding; BC docs become the lasting reference. Joshua flagged a future direction: a live `/design-system/` page on the site — not in scope here.

---

## 2026-05-26 15:30 -- Task verified and completed: website-002 - Blog listing page /posts/

**Type:** Work / Task completion
**Task:** website-002 - Blog listing page /posts/
**Summary:** Created /posts/ listing page, _layouts/post.html, canonical link include, and _sass/_posts.scss with mobile-first flex layout; posts filtered by published: true, syndicated posts labelled innoq.com.
**Verification:** PASS (iteration 3)
**Commit:** 97a0d51
**Files changed:** 8
**ADRs written:** none

---

## 2026-05-26 15:05 -- Batch started: [website-001, website-002]

**Type:** Work / Batch start
**Tasks:** website-001 - Homepage with hero section, website-002 - Blog listing page /posts/
**Parallel:** yes (2 workers)

---

## 2026-05-26 15:00 -- Model / Captured: website-001, website-002

**Type:** Model / Capture
**BC:** website
**Filed to:** todo
**Summary:** Two homepage features captured based on design reference (neureif.com):
hero section with name + tagline (website-001) and text-only blog listing at /posts/
including individual post layout (website-002). No images anywhere — typography carries the weight.

---

## 2026-05-26 14:35 -- Work session ended

**Type:** Work / Session end
**Completed:** 4 (first-try PASS: 2, re-dispatched: 1, verification skipped: 1)
**Bounced:** 0
**Failed:** 0
**Escalated after verification:** 0
**Commits:** 6

---

## 2026-05-26 14:30 -- Task verified and completed: design-system-001 - Styleguide

**Type:** Work / Task completion
**Task:** design-system-001 - Feature: Styleguide — visual identity, dark mode, typography
**Summary:** Scratch-built SCSS design system: dark-mode-first tokens, base reset, typography scale, responsive layout shell. bundle exec jekyll build passes. Human sign-off gate remains open.
**Verification:** PASS (iteration 1)
**Commit:** (pending)
**Files changed:** 9
**ADRs written:** 0003-design-system-scratch-theme.md

---

## 2026-05-26 14:16 -- Batch started: [design-system-001]

**Type:** Work / Batch start
**Tasks:** design-system-001 - Feature: Styleguide — visual identity, dark mode, typography
**Parallel:** no (1 worker)

---

## 2026-05-26 14:15 -- Task verified and completed: infra-003 - Walking skeleton

**Type:** Work / Task completion
**Task:** infra-003 - Spike: Walking skeleton — Jekyll boots and deploys to Netlify
**Summary:** Added _talks/.gitkeep so talks directory is tracked in git; bundle exec jekyll build passes; all skeleton files committed.
**Verification:** PASS (iteration 2)
**Commit:** da4255f
**Files changed:** 7
**ADRs written:** none

---

## 2026-05-26 14:10 -- Verification failed: infra-003 - Walking skeleton

**Type:** Work / Verification failure
**Task:** infra-003 - Spike: Walking skeleton
**Iteration:** 1 of 3
**Reasons:** Gemfile.lock untracked (not committed); _talks/ empty dir has no .gitkeep so won't survive clone
**Iteration hint:** likely-fixable
**Next:** re-dispatched worker

---

## 2026-05-26 14:06 -- Batch started: [infra-003]

**Type:** Work / Batch start
**Tasks:** infra-003 - Spike: Walking skeleton — Jekyll boots and deploys to Netlify
**Parallel:** no (1 worker)

---

## 2026-05-26 14:05 -- Task verified and completed: infra-001 - Decision: Jekyll + Netlify base configuration

**Type:** Work / Task completion
**Task:** infra-001 - Decision: Jekyll + Netlify base configuration
**Summary:** Recorded the Jekyll 4.4.1 + Netlify + GitHub Actions stack decision in ADR-0001 and created netlify.toml, deploy.yml, Gemfile, .ruby-version pinning the build toolchain.
**Verification:** PASS (iteration 1)
**Commit:** 0f3d412
**Files changed:** 6
**ADRs written:** 0001-jekyll-netlify-setup.md

---

## 2026-05-26 14:04 -- Task completed (verification skipped): infra-002 - Decision: Content sync strategy

**Type:** Work / Task completion
**Task:** infra-002 - Decision: Content sync strategy (innoq.com → PR)
**Summary:** ADR-0002 records the daily RSS-based sync strategy with draft-first PR flow; Joshua controls publish via setting published: true.
**Verification:** SKIPPED — decision-only task, single ADR file
**Commit:** 69bb501
**Files changed:** 2
**ADRs written:** 0002-content-sync-strategy.md

---

## 2026-05-26 14:00 -- Batch started: [infra-001, infra-002]

**Type:** Work / Batch start
**Tasks:** infra-001 - Decision: Jekyll + Netlify base configuration, infra-002 - Decision: Content sync strategy (innoq.com → PR)
**Parallel:** yes (2 workers)

---

## 2026-05-26 — Brainstorm: joshuatoepfer.de personal website

**Type:** Brainstorm
**Outcome:** vision created
**BCs identified:** website, design-system, infrastructure
**Summary:** Joshua Töpfer wants a personal website anchoring his professional brand
across three topic areas (Ensemble Programming, ADHS in der IT, Software Development).
The site will mirror posts from innoq.com (syndicated) plus host exclusive personal
content, and serve as a speaker hub for conference talks. Stack is Jekyll + Netlify +
GitHub Actions, dark-mode-first design, low-maintenance automation via sync PRs.
**ADRs written:** none (foundation choices flow through decision tasks)
**Foundation tasks emitted:**
- `infra-001` — Decision: Jekyll + Netlify base configuration
- `infra-002` — Decision: Content sync strategy (innoq.com → PR)
- `infra-003` — Walking skeleton (depends on infra-001, infra-002)
- `design-system-001` — Styleguide (depends on infra-003)

---

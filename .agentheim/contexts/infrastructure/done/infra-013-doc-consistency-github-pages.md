---
id: infra-013
title: Doku-Konsistenz herstellen — GitHub Pages statt Netlify in operativer Doku
status: done
type: chore
context: infrastructure
created: 2026-06-03
completed: 2026-06-03
commit: 179f776
depends_on: []
blocks: []
tags: [documentation, hosting, github-pages, consistency]
related_adrs: ["0001", "0004"]
related_research: []
prior_art: []
---

## Why
ADR-0004 hat den Hosting-Plan aus ADR-0001 (Netlify) auf GitHub Pages
umgestellt — der `actions/deploy-pages`-Workflow in `.github/workflows/deploy.yml`
ist seitdem das Produktiv-Setup. Mehrere operative Dokus beschreiben aber
weiterhin Netlify als aktuellen Hoster, was unter anderem dazu geführt hat,
dass die Datenschutzerklärung initial Netlify nannte (in
`75d8ca8` korrigiert auf GitHub Pages). Die übrigen Dokus müssen jetzt
nachgezogen werden, damit Vision/Context-Map/BC-README mit der Realität
konsistent sind und zukünftige Captures nicht erneut von der falschen
Annahme ausgehen.

## What
Drei Dokus auf den aktuellen Stand (GitHub Pages als Hoster) bringen, dabei
die geplante Netlify-Migration (per ADR-0001 noch deferred) als
zukünftige Option erwähnen — *nicht* als aktuellen Zustand.

ADRs (`0001-jekyll-netlify-setup.md`, `0004-github-pages-initial-deployment.md`)
bleiben unverändert: ADR-0004 dokumentiert die Übersteuerung sauber, die
Historie ist korrekt erfasst.

## Acceptance criteria
- [ ] `.agentheim/context-map.md` (infrastructure-Block, Zeile ~23 + 29):
  „Netlify deployment" → „GitHub Pages deployment"; Key actors:
  „Netlify (host)" → „GitHub Pages (host)". Optional ein kurzer Halbsatz,
  dass Netlify als geplante Migration weiter im Raum steht (ADR-0001), aber
  nicht heutige Realität ist.
- [ ] `.agentheim/contexts/infrastructure/README.md`: alle inhaltlichen
  Netlify-Erwähnungen, die den *aktuellen Zustand* beschreiben, auf GitHub
  Pages anpassen. Konkret: Purpose-Zeile, Actors-Liste, „Deploy"-Vokabular,
  `DeployPublished`-Event. Wo Netlify als zukünftige Migrations-Option
  erwähnt wird, klar als solche kennzeichnen.
- [ ] `_site/`-Build nach `bundle exec jekyll build --quiet` bleibt sauber
  (Smoke-Test; diese Datei landet ja nicht im Output, aber falls
  versehentlich ein Markdown-Syntax-Fehler eingebaut wird, Build-Fehler
  fängt das).
- [ ] `netlify.toml` im Repo-Root **nicht löschen** — ADR-0004 hat das
  explizit als Vorhalte-Konfiguration für die geplante Migration
  festgeschrieben. Auch die `_config.yml`-Exclude-Regel
  (`exclude: - netlify.toml`) bleibt.
- [ ] ADRs `0001` und `0004` **nicht editieren** — sie sind historischer
  Record und beschreiben die Migration zwischen ADR-0001 und ADR-0004
  korrekt im ADR-0004-Body. Keine nachträgliche Reinterpretation.

## Notes

### Was bewusst NICHT in den Scope gehört

- **`.agentheim/knowledge/index.md`** — Top-Level-Index, owned by the work
  orchestrator. Wird vom orchestrator im Rahmen dieses Tasks aktualisiert
  (BC-Beschreibung: „Netlify deployment, GitHub Actions CI/CD…" →
  „GitHub Pages deployment, GitHub Actions CI/CD…"). Der Worker fasst diese
  Datei *nicht* an.
- **Historische `done/`-Task-Files** (`infra-001`, `infra-003`,
  `website-009`, `design-system-005`) und das `protocol.md` — sind
  chronologischer Record und werden nicht rückwirkend umgeschrieben.
- **`vision.md`** — keine Netlify-Erwähnung gefunden, nichts zu tun.
- **`_config.yml`** — die Zeile `exclude: - netlify.toml` ist sachlich
  korrekt (die Datei liegt im Repo und soll nicht in den Build-Output);
  bleibt unverändert.

### Verifikations-Hooks für den Worker

Nach allen Edits:

- `grep -rE 'Netlify' .agentheim/context-map.md .agentheim/contexts/infrastructure/README.md` zeigt nur noch
  Treffer, die *historisch* / *als geplante Migration* formuliert sind —
  keine Treffer mehr, die Netlify als heutigen Hoster behaupten.
- `bundle exec jekyll build --quiet` exit 0.

### Reihenfolge / Risiko

Reine Doku-Operation, keine Code-Änderungen. Risiko: dass Worker
versehentlich ADRs editiert oder `netlify.toml` löscht — beides explizit
in den Acceptance-Criteria verboten. Verifier prüft das.

## Outcome

Operative Doku (Top-Level Context-Map + Infrastructure-BC-README) spiegelt jetzt
die tatsächliche Hosting-Situation: GitHub Pages ist der heutige Hoster, eine
Netlify-Migration ist als geplante Zukunfts-Option explizit gekennzeichnet
(ADR-0001), nicht als aktueller Zustand.

Geänderte Stellen:

- `/Users/joshuatopfer/Documents/Projekte/Privat/joshuatoepfer.de/.agentheim/context-map.md`
  — Infrastructure-Block, Purpose-Zeile + Key actors (Netlify → GitHub Pages,
  zusätzlich kurzer Halbsatz zur geplanten Migration).
- `/Users/joshuatopfer/Documents/Projekte/Privat/joshuatoepfer.de/.agentheim/contexts/infrastructure/README.md`
  — Purpose-Absatz, Actors-Liste, Deploy-Vokabular, `DeployPublished`-Event.
  Netlify als geplante Migration bleibt erwähnt, mit Referenz auf ADR-0001 und
  Vermerk, dass `netlify.toml` aus diesem Grund liegen bleibt (ADR-0004).

Nicht angefasst (per Acceptance-Criteria): ADR-0001, ADR-0004, historische
`done/`-Task-Files, `.agentheim/knowledge/index.md` (orchestrator-owned),
`.agentheim/knowledge/protocol.md`, `netlify.toml`, `_config.yml` (Exclude-Regel
ist sachlich korrekt).

Verifikation:

- `bundle exec jekyll build --quiet` exit 0.
- `grep -n -iE 'Netlify' ...` zeigt nur noch Treffer, die als geplante
  Migrations-Option / ADR-Referenz formuliert sind — keine, die Netlify als
  heutigen Hoster behaupten.

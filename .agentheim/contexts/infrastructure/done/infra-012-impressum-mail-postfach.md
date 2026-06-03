---
id: infra-012
title: Mail-Postfach impressum@joshuatoepfer.de einrichten
status: done
type: chore
context: infrastructure
created: 2026-06-03
completed: 2026-06-03
commit:
depends_on: []
blocks: [website-009]
tags: [email, mail, impressum, dns]
related_adrs: []
related_research: []
prior_art: []
---

## Why
Die Bot-Schutz-Architektur in `website-009` trennt die Kontakt-Adressen:
`hallo@joshuatoepfer.de` als primäre öffentliche Adresse, und
`impressum@joshuatoepfer.de` als opferbare Wegwerf-Adresse für die
Impressums-Pflichtangabe (§5 DDG). Dadurch lässt sich `impressum@` im
Spam-Notfall ohne Kollateralschaden austauschen, weil sie nirgendwo
sonst eingesetzt wird. Voraussetzung: das Postfach muss existieren,
bevor die Impressum-Seite umgestellt wird.

## What
Ein Mail-Postfach `impressum@joshuatoepfer.de` einrichten beim
aktuellen Mail-Provider von joshuatoepfer.de. Routing nach Wunsch
(Weiterleitung an die persönliche Inbox oder eigenständige Mailbox —
beides erfüllt den Zweck der opferbaren Adresse).

## Acceptance criteria
- [ ] Eine Mail an `impressum@joshuatoepfer.de` erreicht Joshuas Posteingang.
- [ ] Die Adresse kann später ohne Eingriffe an der Site selbst
  ausgetauscht werden (z. B. durch Löschen der Weiterleitung).
- [ ] Falls neue DNS-Records (MX, SPF, DKIM) für eine eigenständige
  Mailbox nötig sind: gesetzt und verifiziert.

## Notes

### Charakter dieses Tasks
Reiner Konfigurations-/Provider-Eingriff. Joshua führt das selbst aus
(Login beim Mail-/DNS-Provider). Kein Worker-automatierbarer Anteil
am Site-Code. Der Task existiert hier, damit der Blocker für
`website-009` sichtbar gemacht ist und nicht aus Versehen
gleichzeitig gestartet wird.

### Resolution (2026-06-03)
Erledigt per **Catchall-Adresse** auf der Domain: jede Mail an
`*@joshuatoepfer.de` landet in Joshuas Posteingang. `impressum@`
funktioniert damit ohne separates Postfach.

**Nuance gegenüber der ursprünglichen „opferbar"-Annahme:** mit
Catchall heißt „Adresse austauschen" *nicht* „Postfach löschen",
sondern „Provider-Regel anlegen, die genau den Local-Part
`impressum` rejectet, und in der Impressum-Seite einen neuen
Local-Part einsetzen (z. B. `impressum2@`)". Funktional gleichwertig,
nur ein Schritt mehr im Notfall. Wert: festgehalten in den Notes von
`website-009`, damit die Strategie reproduzierbar bleibt.

### Reihenfolge
Zuerst dieser Task → Verifikation durch eine Test-Mail → dann
`website-009` umsetzen und die Impressum-Seite umstellen.

### Out of scope
- Postfach für `hallo@joshuatoepfer.de` — existiert bereits (steht
  heute schon an vier Stellen im rendered HTML).
- DMARC-/SPF-/DKIM-Hardening über das hinaus, was der Provider
  ohnehin als Default setzt.

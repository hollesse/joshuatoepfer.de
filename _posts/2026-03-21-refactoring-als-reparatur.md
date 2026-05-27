---
layout: post
title: "Refactoring als Reparatur — nicht als Strafe"
subtitle: "Wenn Refactoring sich anfühlt wie Buße, machen wir es seltener und schlechter. Ein Plädoyer für beiläufiges Aufräumen."
date: 2026-03-21
topic: softdev
source: innoq
canonical_url: "https://www.innoq.com/de/blog/"
reading_time: 7
---

Refactoring hat ein PR-Problem. In vielen Teams ist es zur Strafarbeit geworden:
etwas, das man tut, wenn ein Ticket abgeschlossen ist und „noch Zeit übrig" — und
dafür rechtfertigen muss, warum man nicht direkt das nächste Feature angeht.

## Das Problem mit dem expliziten Refactoring-Ticket

Sobald Refactoring ein eigenes Ticket bekommt, wird es politisch. Es muss erklärt,
priorisiert, gegen Features verteidigt werden. Das ist nicht falsch — manchmal
braucht es das. Aber für die meisten Refactorings ist es viel zu viel Overhead.

## Beiläufiges Aufräumen

Die produktiveren Refactorings sind die, die niemand bemerkt. Eine umbenannte
Variable, weil sie nicht mehr passt. Eine Funktion in zwei aufgeteilt, weil sie
zwei Dinge tut. Eine doppelte Konstante zusammengeführt. Diese Änderungen passen
in den PR, in dem sowieso eine Stelle modifiziert wird.

## Die Boyscout-Regel funktioniert

„Hinterlasse den Code besser als du ihn vorgefunden hast." Klingt nach Plakat im
Großraumbüro, ist aber eine der wenigen Praktiken, die ich in jedem Team gesehen
habe, das nach drei Jahren noch funktionsfähig war.

## Wann es doch ein eigenes Ticket braucht

Architektur-Änderungen, die mehrere Module betreffen. Migrations-Projekte. Alles,
was länger als ein paar Stunden dauert und mit anderen Änderungen kollidieren
würde. Diese Refactorings müssen sichtbar gemacht werden — alles andere passt in
den normalen Arbeitsfluss.

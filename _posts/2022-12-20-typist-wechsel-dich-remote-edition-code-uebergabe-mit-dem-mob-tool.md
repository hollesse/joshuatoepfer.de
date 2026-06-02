---
layout: post
title: Typist wechsel dich (Remote Edition)
date: '2022-12-20'
source: innoq
canonical_url: https://www.innoq.com/de/articles/2022/12/typist-wechsel-dich-remote-edition-code-uebergabe-mit-dem-mob-tool/
topic: ensemble
published: true
render_with_liquid: false
---

Wir schreiben das Jahr vor Corona. Ein Team aus drei Personen im Homeoffice beginnt ein Projekt auf der grünen Wiese. Jeden Tag treffen sie sich online in ihrem Zoom-Raum und beginnen, Software zu entwickeln, und zwar mit der Methode [Remote Mob Programming](https://www.remotemobprogramming.org) (auch bekannt als Remote Ensemble Programming oder Remote Team Programming). Der [Typist](https://www.remotemobprogramming.org/typist), zu Deutsch „die Schreibkraft“, teilt den Bildschirm und tippt das, was die anderen beiden anweisen. Der Typist
agiert somit als smartes Eingabegerät für die anderen beiden, die sich auf das Analysieren von Problemen, die Abwägung von Lösungsalternativen und auf die Ausgestaltung von verabschiedeten Lösungen konzentrieren können. Das läuft für die drei überraschend gut. [Sogar so gut, dass mindestens einer von ihnen nicht mehr anders arbeiten möchte](https://twitter.com/simonharrer/status/1160982263481475073).

Nur das Weitergeben des Staffelstabs an den nächsten Typist gestaltet sich online im Zoom-Raum herausfordernd. Vor Ort wäre es ja durch einfache Weitergabe der Funkmaus und -tastatur in wenigen Sekunden erfolgt. Nach ein paar ersten Gehversuchen kristallisierte sich eine gangbare Lösung heraus: Manuell auf einen temporären Branch in Git zu wechseln, dort temporäre Commits zu erstellen, und dann, wenn die Arbeit getan ist, die Änderungen zurück in den ursprünglichen Branch zu bringen. Diese Schritte immer manuell durchzuführen, macht jedoch keinen Spaß. Toolunterstützung musste her. Und das [mob-Tool](https://mob.sh/) ward geboren.

Das mob-Tool ist in Go geschrieben, quelloffen unter der MIT-Lizenz und auf [GitHub](https://github.com/remotemobprogramming/mob) verfügbar. Die erste Version wurde im April 2020 veröffentlicht. Mittlerweile, Stand Februar 2022, stehen wir bei Version 2.4.0 mit über 20 000 Downloads und über 850 Sternen auf GitHub. Das Tool hat es sogar in den [„Technology Radar Volume 25“](https://www.thoughtworks.com/content/dam/thoughtworks/documents/radar/2021/10/tr_technology_radar_vol_25_en.pdf) geschafft und wird dort als evaluierenswert eingestuft.

## Grundfunktionen von mob

Das Tool bietet drei Grundfunktionen: `mob start`, `mob next`, und `mob done`. Es ist ein wenig wie bei einem Brettspiel. Jeder Typist beginnt seinen Zug mit `mob start` und beendet ihn mit `mob next`. Das Feature ist fertig, wenn ein Zug mit `mob done` beendet wird. Was es mit diesen Grundfunktionen konkret auf sich hat, zeigen wir anhand eines Beispiels in Abbildung 1.

![Abb. 1: Visualisiert die Funktionsweise des mob Tools.](w_2800/v1/uploads-production/e035w3dl0y0y28nu2prr5i7acmr4?_a=BACMTiAE)

Abb. 1: Visualisiert die Funktionsweise des mob Tools.

Carola, Maria, Mona und Raphael entwickeln mit der Methode Remote Mob Programming ein neues Feature in einem Onlineshop. Carola beginnt als Typist und teilt ihren Bildschirm mit den anderen, öffnet den Projektordner auf ihrer Kommandozeile und startet auf dem Main Branch. Sie gibt den Befehl `mob start` ein. Das mob-Tool erstellt jetzt einen neuen temporären Work in Progress Branch (WIP Branch), der nur für die Entwicklung des Features genutzt wird. Der Name des WIP Branch wird nach dem Schema `mob/<Ursprungs-Branch>` vom Ursprungs-Branch abgeleitet. In unserem Beispiel ist der Ursprungs-Branch der Main Branch. Der abgeleitete WIP Branch lautet daher `mob/main`.

Der Rest des Teams sagt Carola, was sie tun soll. Nach einer bestimmten Zeit oder wenn bspw. ein Test fertig geschrieben ist, soll gewechselt werden. Dazu gibt sie in der Kommandozeile lediglich `mob next` ein, um den Source Code an Maria zu übergeben. Das mob-Tool erzeugt dann einen WIP-Commit und pusht ihn direkt auf das Remote Repository. Es kann sein, dass der aktuelle Stand gar nicht kompiliert oder der Test fehlschlägt. Das ist in Ordnung! Denn genau deswegen gibt es den WIP Commit, dessen typische Commit Message `mob next [ci-skip]` ist. Diese kennzeichnet den Commit als WIP und verhindert, dass eine CI Pipeline wegen Kompilierfehlern fehlschlägt. Auch wird der WIP Commit unter Umgehung von eventuell vorhandenen Git Hooks erstellt und gepusht, da diese ja nicht für temporäre Stände gemacht sind.

Maria übernimmt die Rolle des Typist, dafür übernimmt sie von Carola die Bildschirmfreigabe und teilt stattdessen ihren Bildschirm. Sie geht ebenfalls auf die Kommandozeile in den Projektordner auf den Main Branch. Jetzt tippt auch sie `mob start` in ihre Kommandozeile. Das mob-Tool checkt den WIP Branch mit den Änderungen von Carola automatisch aus und Maria kann jetzt darauf aufbauend weiterarbeiten. Um den Source Code dann an Mona zu übergeben, gibt auch Maria `mob next` in ihrer Konsole ein. Das führt wieder zu einem WIP Commit, der auf dem WIP Branch gepusht wird.

Jetzt schlüpft Mona in die Rolle des Typist. Ist das Feature fertig implementiert, gibt Mona den Befehl `mob done` ein. Dabei werden alle WIP Commits des WIP Branch mittels squash zusammengeführt und als Änderungen in die Staging Area des Main Branch gepackt. Der WIP Branch wurde vom mob-Tool automatisch aus dem Remote Repository und bei Mona lokal gelöscht.

Mona muss nur noch einen Commit mit einer bewusst gewählten und sinnvollen Commit Message erstellen und ihn pushen. Wenige Minuten später ist das neue Feature live und kann genutzt werden.

## Die perfekte Übergabe

Natürlich garantiert die Nutzung des mob-Tools keine Übergabe in wenigen Sekunden, ohne dabei die anderen in deren Diskussionen zu stören. Um das zu erreichen, ist noch Weiteres zu beachten. Schauen wir uns dazu die Übergabe von Carola an Maria im Detail an. Wir springen zu der Situation, in der Maria zwar noch den Bildschirm teilt, aber genau jetzt übergeben möchte. Dazu führt Maria wie oben beschrieben `mob next` in der Kommandozeile aus. Danach tut Maria nichts. Sie beendet weder die Bildschirmfreigabe noch bewegt sie den Mauscursor oder tippt irgendwo etwas anderes. Denn mit `mob next` hat sie die Übergabe eingeleitet und muss nun warten, dass Carola weitermacht. Carola beobachtet natürlich wie immer aufmerksam den freigegebenen Bildschirm. Wenn dann `mob next` erfolgreich ausgeführt worden ist – das kann ja auch mal ein paar Sekunden dauern – startet Carola unmittelbar mittels Keyboard-Shortcut die eigene Bildschirmfreigabe. Dabei wird die Bildschirmfreigabe von Maria automatisch beendet und Maria kann endlich unbeobachtet ihre E-Mails checken. Carola wechselt indessen in ihre Kommandozeile und gibt dort `mob start` ein. Nachdem `mob start` erfolgreich durchgelaufen ist, ist die Übergabe abgeschlossen. Da weder Maria noch Carola sprechen mussten, damit die Übergabe klappt, konnten Mona und Raphael [ungestört über die weitere Problemlösung diskutieren](https://mob.sh/#the-perfect-git-handover).

Leider funktioniert diese Übergabe nicht mit jedem Videokonferenztool gleich gut. Unterbrechungsfreie Übernahme der Bildschirmfreigabe, globale Keyboard-Shortcuts für die Bildschirmfreigabe und ein stabiles Screen-Layout beim „Stehlen“ der Bildschirmfreigabe variiert stark. Aus unserer Erfahrung lässt sich bisher lediglich mit Zoom eine perfekte Übergabe durchführen. Aber wir sind guter Dinge, dass das in Zukunft auch mit anderen Videokonferenztools möglich sein wird.

## Timing ist alles

Bei der kollaborativen Arbeit des Remote Mob Programming ist es enorm wichtig, regelmäßig die Rolle des Typist zu wechseln. Wird das vergessen, ist der Typist irgendwann erschöpft und manche aus dem Rest des Teams verlieren den Fokus und fangen an, nebenbei das Java Magazin zu lesen. Um Teams beim regelmäßigen Wechsel zu unterstützen, bringt das mob-Tool einen eigenen lokalen Timer mit. Durch die Eingabe von `mob start 10` wird beispielsweise ein Zehn-Minuten-Timer gestartet, der nach Ablauf in den Kopfhörern des Typist ein „mob next“ ertönen lässt.

Zusätzlich gibt es noch die Möglichkeit, das mob-Tool mit dem [Mob Timer](https://timer.mob.sh/) zu kombinieren. Dieser ist als Webanwendung unter [timer.mob.sh](https://timer.mob.sh/) erreichbar. Der Vorteil: Der Timer läuft nun nicht mehr ausschließlich lokal, sondern zusätzlich geteilt an einer zentralen Stelle, die jedes Teammitglied einsehen kann.

![Abb. 2: Zeigt die Startseite des Mob Timer.](w_2800/v1/uploads-production/osuginz8zfraea4hd7forupnksr7?_a=BACMTiAE)

Abb. 2: Zeigt die Startseite des Mob Timer.

Um den Mob Timer zu nutzen, ist ein Raum auf [timer. mob.sh](https://timer.mob.sh/) nötig. Dazu kann, wie in Abbildung 2 zu sehen ist, einfach ein Name vergeben und so der Raum betreten werden. In unserem Beispiel erstellen wir den Raum mit dem Namen „javamagazin“.

![Abb. 3: Zeigt beim Mob Timer an, wie die Zeit heruntergezählt wird, inklusive der Historie.](w_2800/v1/uploads-production/238k033qjmujtr1cdld8iunu2kim?_a=BACMTiAE)

Abb. 3: Zeigt beim Mob Timer an, wie die Zeit heruntergezählt wird, inklusive der Historie.

In Abbildung 3 sehen wir nun den geöffneten Raum „javamagazin“. Um den Timer für diesen Raum mit dem mob-Tool starten zu können, muss jeder im Team die Umgebungsvariable `MOB_TIMER_ROOM` auf den Namen des Raums setzen. Danach kann der Timer wie gewohnt entweder mit dem Befehl `mob timer <anzahl Minuten>` oder `mob start <anzahl Minuten>` gestartet werden. Der Mob Timer läuft dann automatisch bei jedem, der die Website mit genau dem Raum geöffnet hat und spielt einen Ton ab, wenn die Zeit vorbei ist. Neben dem abgespielten Ton kann der Mob Timer auch Benachrichtigungen an den Browser schicken und bietet eine 24-Stunden-Historie (Abb. 4), in der die Mob-Session nachvollzogen werden kann. Als Zusatzangebot gibt es für macOS-Nutzer noch einen kleinen Helfer für die Taskbar als [App im App Store](https://apps.apple.com/us/app/mob-timer/id1594924856), der dann ähnlich wie die Website die Zeit herunterzählt.

Der Timer kann nicht nur für die Arbeit genutzt werden, sondern auch für die Pausen. Dazu bietet das mob-Tool den Befehl break. Wenn eine Pause von zehn Minuten gemacht werden soll, muss einfach der Befehl `mob break 10` eingegeben werden. Wie in Abbildung 4 zu sehen ist, startet dann ein Pausentimer von zehn Minuten, der durch das Kaffeetassensymbol zu erkennen ist.

![Abb. 4: Zeigt beim Mob Timer an, wie die Zeit bei einer Pause heruntergezählt wird.](w_2800/v1/uploads-production/cmqfj7uhtyik1ac6cdw5aodwbpco?_a=BACMTiAE)

Abb. 4: Zeigt beim Mob Timer an, wie die Zeit bei einer Pause heruntergezählt wird.

## Fazit

Das mob-Tool ist ein einfacher Helfer, um die Codeübergabe von einer Person zur nächsten in wenigen Sekunden mittels Git zu ermöglichen – ohne dass dabei der Arbeitsfluss reißt. Entstanden ist es im Kontext von Remote Mob Programming, aber – und das ist das Spannende – genutzt wird es mittlerweile auch für Zwecke, an die wir am Anfang gar nicht gedacht haben: beim Mob Programming vor Ort, um die individuellen Setups der einzelnen Teammitglieder zu berücksichtigen und sogar beim stillen Arbeiten alleine, um Zwischenstände per Git zu sichern. Wir sind gespannt, wohin die Reise für das mob-Tool noch geht.

Besonderer Dank geht an Vera Peuntinger, Jochen Christ, Stefan Tilkov, Gregor Riegler und Thomas Much für ihr wertvolles und konstruktives Feedback zu einer früheren Version dieses Artikels.

/* post-page.jsx — single blog post page */

/* Shared: BlogNav, Footer, fmtFullDate, POSTS, TOPIC_META from homepage-v1-v2.jsx */

const DEMO_POST = {
  date: "2026-01-30",
  topic: "adhs",
  title: "Pairing mit dem ADHS-Brain — vier Tricks, die wirklich helfen",
  subtitle:
    "Kurze Iterationen, klare Rollen, externer Fokus-Timer. Was ich über Jahre angepasst habe, damit Pair Programming auch dann funktioniert, wenn die eigene Aufmerksamkeit nicht zuverlässig erscheint.",
  source: "innoq",
  readingTime: 8
};

function PostBody() {
  return (
    <>
      <p>
        Pair Programming ist eine der Praktiken, von denen ich am meisten profitiere — und gleichzeitig
        eine der anstrengendsten. Wenn du ADHS hast, weißt du wahrscheinlich warum: konstante
        Aufmerksamkeit auf eine Sache, externe Erwartung präsent zu sein, das Gefühl, dass Pausen
        unhöflich wirken könnten. Was theoretisch ein produktivitätssteigerndes Format ist, kann sich
        in der Praxis wie ein Marathon mit Publikum anfühlen.
      </p>
      <p>
        Über die Jahre habe ich vier Anpassungen gefunden, die für mich den Unterschied machen. Sie
        sind nicht spektakulär — und genau das ist der Punkt. Sie funktionieren, weil sie klein sind.
      </p>

      <h2>1. Kurze, harte Iterationen</h2>
      <p>
        Driver-Wechsel alle zehn Minuten, nicht alle Stunde. Ich nutze einen externen Timer (eine
        physische Pomodoro-Uhr, kein Tool auf dem Bildschirm), der von außen entscheidet, wann
        gewechselt wird. Damit wird die Rollenfrage zur Maschinen-Frage, nicht zur sozialen.
      </p>
      <blockquote>
        Wenn der Timer entscheidet, muss niemand sich entscheiden — und das ist mit ADHS oft die
        eigentliche Kostenfunktion.
      </blockquote>

      <h2>2. Sichtbare Rollen</h2>
      <p>
        „Driver" und „Navigator" stehen tatsächlich an einer Stelle, die wir beide sehen können — ein
        Post-It am Monitor, eine kleine Statusleiste in der IDE, was auch immer. Klingt banal. Ist es
        nicht. ADHS-Brains haben einen unzuverlässigen Working-Memory-Cache; was implizit ist, fällt
        weg.
      </p>

      <h2>3. Verbalisieren mit Sicherheitsnetz</h2>
      <p>
        Als Navigator lade ich ein Notiz-Pad neben den Editor und schreibe alles auf, was mir auffällt
        — auch wenn ich es gerade nicht aussprechen kann. Das hat zwei Effekte: Erstens vergesse ich
        es nicht. Zweitens kann ich später entscheiden, was davon wichtig war.
      </p>
      <p>
        Es ist die externe Kompensation für ein internes System, das nicht zuverlässig speichert.
        Kein Workaround — eine sinnvolle Anpassung.
      </p>

      <h2>4. Pausen ohne Verhandlung</h2>
      <p>
        Alle 50 Minuten zehn Minuten Pause. Nicht „wenn es gerade passt". Nicht „nach dem Test". Die
        Pause ist nicht verhandelbar, weil das Verhandeln selbst Energie kostet. In Sessions, in
        denen wir das eingeführt haben, war die Gesamtleistung höher — bei allen Beteiligten, nicht
        nur bei mir.
      </p>

      <h2>Was nicht funktioniert hat</h2>
      <p>
        Längere Sessions am Stück, mit der Idee „heute ziehen wir das durch". Open-End-Wechsel. Sich
        einreden, dass es heute schon gehen wird, weil gestern auch ging. Diese Konstellationen
        produzieren bei mir entweder Erschöpfung oder ein Gefühl von „ich war heute nicht gut" — und
        beides ist nicht informativ.
      </p>

      <h2>Für Teams ohne ADHS-Mitglieder</h2>
      <p>
        Funktionieren diese Tricks auch dann? Ja, in den Sessions, die ich begleitet habe, sehr
        zuverlässig. Sie sind keine ADHS-Spezialwerkzeuge; sie machen nur sichtbar, was bei
        neurodivergenten Brains schneller sichtbar wird. Wenn der Timer auch deinen Tag besser
        macht, dann hast du wahrscheinlich nicht ADHS — sondern Aufmerksamkeit, die wie alle anderen
        auch endlich ist.
      </p>
    </>
  );
}

function BlogNav() {
  return (
    <div className="topnav">
      <a href="#" className="brand">
        Joshua Töpfer<span style={{ color: "var(--accent)" }}>.</span>
      </a>
      <nav>
        <a href="#">Index</a>
        <a href="#" className="is-current">Blog</a>
        <a href="#">Talks</a>
        <a href="#">Über mich</a>
        <ThemeToggle />
      </nav>
    </div>
  );
}

function RelatedPosts() {
  const related = POSTS
    .filter((p) => p.topic === DEMO_POST.topic && p.title !== DEMO_POST.title)
    .slice(0, 3);
  return (
    <section style={{ padding: "80px 80px 0", borderTop: "1px solid var(--rule-strong)" }}>
      <h2 className="mono" style={{
        fontSize: 14,
        fontWeight: 500,
        margin: "0 0 36px",
        color: "var(--fg-dim)",
        letterSpacing: "0.04em"
      }}>
        <span style={{ color: "var(--fg)" }}>—</span>&nbsp;&nbsp;MEHR ZUM THEMA {TOPIC_META[DEMO_POST.topic]?.label.toUpperCase()}
      </h2>
      <div>
        {related.map((p) => (
          <a key={p.title} href={p.href} className="related-post-row" style={{
            display: "grid",
            gridTemplateColumns: "180px 1fr auto",
            gap: 32,
            padding: "26px 0",
            borderTop: "1px solid var(--rule)",
            alignItems: "baseline"
          }}>
            <div className="mono" style={{ fontSize: 12, color: "var(--fg-dim)", letterSpacing: "0.02em" }}>
              {fmtFullDate(p.date)}
            </div>
            <div>
              <div style={{ fontSize: 22, fontWeight: 480, letterSpacing: "-0.01em" }}>
                {p.title}
              </div>
              <div style={{ color: "var(--fg-dim)", fontSize: 15, lineHeight: 1.5, marginTop: 6, maxWidth: "62ch" }}>
                {p.excerpt}
              </div>
            </div>
            <div className="mono" style={{ fontSize: 11, color: "var(--fg-faint)", letterSpacing: "0.08em" }}>→</div>
          </a>
        ))}
        <div style={{ borderTop: "1px solid var(--rule)" }} />
      </div>
    </section>
  );
}

function PostPager() {
  return (
    <section className="post-pager" style={{
      padding: "56px 80px",
      display: "grid",
      gridTemplateColumns: "1fr 1fr",
      gap: 48,
      borderTop: "1px solid var(--rule)"
    }}>
      <a href="#" style={{ display: "block" }}>
        <div className="mono" style={{ fontSize: 11, color: "var(--fg-faint)", letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 10 }}>
          ← Älterer Beitrag
        </div>
        <div style={{ fontSize: 19, fontWeight: 480, letterSpacing: "-0.01em", color: "var(--fg)", lineHeight: 1.3 }}>
          Wie man im Ensemble nicht stört: eine kleine Etikette
        </div>
      </a>
      <a href="#" style={{ display: "block", textAlign: "right" }}>
        <div className="mono" style={{ fontSize: 11, color: "var(--fg-faint)", letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 10 }}>
          Neuerer Beitrag →
        </div>
        <div style={{ fontSize: 19, fontWeight: 480, letterSpacing: "-0.01em", color: "var(--fg)", lineHeight: 1.3 }}>
          Der Kalender ist mein Exocortex
        </div>
      </a>
    </section>
  );
}

/* ─────────────────────────────────────────────────────────────
   Post page — Hero banner + sticky TOC aside

   Two layout variants for the hero. The body layout below is identical
   in both; only the hero's content alignment changes.

   - "edge"    Hero text starts at the section's 80px padding (default).
   - "aligned" Hero text indents to line up with the article body column
               below (240px aside + 80px gap + 80px padding = 400px).
   ───────────────────────────────────────────────────────────── */
function PostPage() {
  return (
    <div className="jt">
      <BlogNav />

      {/* Hero banner */}
      <section className="post-hero" style={{
        padding: "120px 80px 100px",
        borderBottom: "1px solid var(--rule-strong)",
        background: "color-mix(in oklab, var(--fg) 3%, var(--bg))",
        position: "relative"
      }}>
        <a href="#" className="mono link" style={{
          position: "absolute",
          top: 32,
          left: 80,
          fontSize: 11,
          color: "var(--fg-dim)",
          letterSpacing: "0.08em",
          textTransform: "uppercase"
        }}>
          ← Zurück zum Blog
        </a>

        <div className="mono" style={{
          fontSize: 11,
          letterSpacing: "0.1em",
          textTransform: "uppercase",
          color: "var(--accent)",
          marginBottom: 32,
          fontWeight: 500
        }}>
          <span>{TOPIC_META[DEMO_POST.topic]?.label}</span>
          <span style={{ color: "var(--fg-faint)", margin: "0 12px" }}>·</span>
          <span style={{ color: "var(--fg-dim)" }}>{fmtFullDate(DEMO_POST.date)}</span>
        </div>

        <h1 style={{
          fontSize: 112,
          lineHeight: 0.92,
          letterSpacing: "-0.045em",
          fontWeight: 380,
          margin: "0 0 40px",
          maxWidth: "18ch",
          textWrap: "balance"
        }}>
          {DEMO_POST.title.split(" — ")[0]}<span style={{ color: "var(--accent)" }}>.</span>
        </h1>
        <p style={{
          fontSize: 26,
          lineHeight: 1.32,
          color: "var(--fg-dim)",
          fontWeight: 380,
          margin: 0,
          maxWidth: "44ch",
          letterSpacing: "-0.01em"
        }}>
          {DEMO_POST.subtitle}
        </p>

        <div className="mono" style={{
          marginTop: 56,
          paddingTop: 22,
          borderTop: "1px solid var(--rule)",
          display: "flex",
          gap: 24,
          fontSize: 11,
          color: "var(--fg-faint)",
          letterSpacing: "0.08em",
          textTransform: "uppercase",
          flexWrap: "wrap"
        }}>
          <span>{DEMO_POST.readingTime} min Lesezeit</span>
          {DEMO_POST.source && <>
            <span>·</span>
            <span>↗ Erscheint auch auf {DEMO_POST.source}.com</span>
          </>}
        </div>
      </section>

      {/* Two-column body — sticky TOC aside left, article right */}
      <section className="post-body-layout" style={{
        padding: "88px 80px 88px",
        display: "grid",
        gridTemplateColumns: "240px 1fr",
        gap: 80,
        alignItems: "start"
      }}>
        <aside style={{ position: "sticky", top: 32 }}>
          <div className="mono" style={{
            fontSize: 11,
            color: "var(--fg-faint)",
            letterSpacing: "0.08em",
            textTransform: "uppercase",
            marginBottom: 18
          }}>
            Inhalt
          </div>
          <ol style={{
            listStyle: "none",
            padding: 0,
            margin: 0,
            display: "flex",
            flexDirection: "column",
            gap: 12
          }}>
            {[
              "1. Kurze Iterationen",
              "2. Sichtbare Rollen",
              "3. Verbalisieren mit Sicherheitsnetz",
              "4. Pausen ohne Verhandlung",
              "Was nicht funktioniert hat",
              "Für Teams ohne ADHS-Mitglieder"
            ].map((t) => (
              <li key={t}>
                <a href="#" className="link" style={{
                  fontSize: 13,
                  color: "var(--fg-dim)",
                  lineHeight: 1.45,
                  display: "block"
                }}>
                  {t}
                </a>
              </li>
            ))}
          </ol>
        </aside>

        <div className="post-body">
          <PostBody />
        </div>
      </section>

      <PostPager />
      <RelatedPosts />
      <Footer />
    </div>
  );
}

window.PostPage = PostPage;

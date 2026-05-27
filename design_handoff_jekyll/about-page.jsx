/* about-page.jsx — Über mich */

/* Shared from homepage-v1-v2.jsx: Footer */

function AboutNav() {
  return (
    <div className="topnav">
      <a href="#" className="brand">
        Joshua Töpfer<span style={{ color: "var(--accent)" }}>.</span>
      </a>
      <nav>
        <a href="#">Index</a>
        <a href="#">Blog</a>
        <a href="#">Talks</a>
        <a href="#" className="is-current">Über mich</a>
        <ThemeToggle />
      </nav>
    </div>
  );
}

function AboutBody() {
  return (
    <>
      <p>
        Mein Name ist Joshua Töpfer. Ich bin Senior Consultant bei INNOQ und
        arbeite seit etwa acht Jahren in der Software­entwicklung — die meiste Zeit
        davon in Teams, nicht alleine. Das ist kein Zufall: Ich glaube, dass die
        besten Systeme dort entstehen, wo mehrere Köpfe gleichzeitig auf das
        gleiche Problem schauen dürfen.
      </p>
      <p>
        Mein Schwerpunkt ist <strong>Ensemble Programming</strong> — eine
        Variante des Pair Programmings mit mehr als zwei Beteiligten. Klingt nach
        Overhead, ist aber das Gegenteil: weniger Wartezeit, schnelleres
        Onboarding, höhere Code-Qualität. Ich begleite Teams dabei, das in den
        Alltag zu integrieren, ohne dass es sich nach Workshop-Theater anfühlt.
      </p>

      <h2>Über ADHS</h2>
      <p>
        Ich habe ADHS. Vor ein paar Jahren bekommen, schon mein Leben lang
        gehabt. Ich rede und schreibe inzwischen offen darüber, weil ich
        gemerkt habe: vieles, was ich mir als „Marotte" oder „Disziplinproblem"
        zurechtgelegt hatte, war eigentlich ein Anpassungs­problem an
        Strukturen, die nicht für mein Brain gemacht waren.
      </p>
      <p>
        Das heißt nicht, dass ADHS eine Superkraft ist (Spoiler: ist es nicht).
        Es heißt, dass es eine andere Bauart von Aufmerksamkeit ist — und dass
        Teams, die das verstehen, mit dieser Bauart sehr produktiv
        zusammenarbeiten können.
      </p>

      <h2>Was ich technisch mache</h2>
      <p>
        Java und Kotlin, manchmal TypeScript. Microservices, Refactoring,
        Test-Strategien jenseits der klassischen Pyramide. Pragmatisch,
        kontextabhängig, ohne Dogma. Ich glaube nicht an „Best Practices" als
        universelle Lösung — aber an sehr gute Praktiken im richtigen Kontext.
      </p>

      <h2>Außerhalb des Editors</h2>
      <p>
        Ich lese viel (zur Zeit vor allem zu Neurowissenschaft und Pädagogik),
        koche gerne und versuche, mit meinem Hund mindestens einmal am Tag
        raus zu gehen — Variable Pomodoro-Technik mit vier Pfoten.
      </p>
    </>
  );
}

function QuickFacts() {
  const facts = [
    ["Lebt in",         "Hannover"],
    ["Arbeitet bei",    "INNOQ"],
    ["Rolle",           "Senior Consultant"],
    ["Spricht",         "Deutsch · Englisch"],
    ["Liest gerade",    "Das Pegasus-Prinzip"],
    ["Hört gerade",     "Computer World"],
    ["Mit Hund seit",   "2021"],
    ["Schreibt seit",   "2019"]
  ];
  return (
    <dl style={{ margin: 0, display: "grid", gridTemplateColumns: "1fr", gap: 0 }}>
      {facts.map(([k, v]) => (
        <div key={k} style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 16,
          padding: "12px 0",
          borderTop: "1px solid var(--rule)",
          alignItems: "baseline"
        }}>
          <dt className="mono" style={{ fontSize: 11, color: "var(--fg-faint)", letterSpacing: "0.06em", textTransform: "uppercase" }}>{k}</dt>
          <dd style={{ margin: 0, fontSize: 14, color: "var(--fg)" }}>{v}</dd>
        </div>
      ))}
      <div style={{ borderTop: "1px solid var(--rule)" }} />
    </dl>
  );
}

function ContactCTA() {
  return (
    <section className="contact-cta" style={{
      padding: "80px 80px 96px",
      borderTop: "1px solid var(--rule-strong)"
    }}>
      <h2 style={{
        fontSize: 56,
        lineHeight: 1.05,
        letterSpacing: "-0.03em",
        fontWeight: 440,
        margin: "0 0 28px",
        maxWidth: "18ch",
        textWrap: "balance"
      }}>
        Lust auf Ensemble, einen Talk oder einfach Hallo<span style={{ color: "var(--accent)" }}>?</span>
      </h2>
      <a href="mailto:hallo@joshuatoepfer.de" className="link" style={{ fontSize: 24, color: "var(--accent)", letterSpacing: "-0.01em" }}>
        hallo@joshuatoepfer.de →
      </a>
    </section>
  );
}

function AboutPage() {
  return (
    <div className="jt">
      <AboutNav />

      <section className="hero about-hero" style={{
        padding: "100px 80px 60px",
        display: "grid",
        gridTemplateColumns: "1fr 460px",
        gap: 80,
        alignItems: "start"
      }}>
        <div>
          <div className="label-eyebrow" style={{ marginBottom: 28 }}>
            Über mich
          </div>
          <h1 style={{
            fontSize: 96,
            lineHeight: 0.95,
            letterSpacing: "-0.04em",
            fontWeight: 440,
            margin: "0 0 28px",
            maxWidth: "14ch",
            textWrap: "balance"
          }}>
            Hallo, ich bin Joshua<span style={{ color: "var(--accent)" }}>.</span>
          </h1>
          <p style={{
            fontSize: 22,
            lineHeight: 1.4,
            color: "var(--fg-dim)",
            fontWeight: 380,
            margin: 0,
            maxWidth: "32ch",
            letterSpacing: "-0.01em"
          }}>
            Senior Consultant bei <span style={{ color: "var(--accent)" }}>INNOQ</span>,
            Ensemble-Programmer, ADHS-Brain. Schreibt offen über
            Software, Teams und Neurodivergenz.
          </p>
        </div>
        <image-slot
          id="about-portrait"
          shape="rect"
          radius="2"
          style={{
            width: "460px",
            height: "580px",
            filter: "grayscale(1) contrast(1.1) brightness(0.92)"
          }}
          placeholder="Porträt · Hochformat 3:4"
        />
      </section>

      <section className="about-body-layout" style={{ padding: "32px 80px 88px" }}>
        <div className="about-body-grid" style={{ display: "grid", gridTemplateColumns: "1fr 280px", gap: 80, alignItems: "start" }}>
          <div className="post-body">
            <AboutBody />
          </div>
          <aside style={{ position: "sticky", top: 32 }}>
            <div className="mono" style={{ fontSize: 11, color: "var(--fg-faint)", letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 16 }}>
              Auf einen Blick
            </div>
            <QuickFacts />
          </aside>
        </div>
      </section>

      <ContactCTA />
      <Footer />
    </div>
  );
}

window.AboutPage = AboutPage;

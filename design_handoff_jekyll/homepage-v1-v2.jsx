/* homepage.jsx — joshuatoepfer.de homepage with 4 variants */

const POSTS = [
/* 2026 */
{ date: "2026-05-12", topic: "adhs",     title: "Wenn das Brain zu schnell tippt — ADHS im Pairing",                excerpt: "Wenn Gedanken schneller sind als der Cursor: was beim Pairen passiert, und vier Werkzeuge, die wirklich helfen.", source: null,    href: "#" },
{ date: "2026-04-28", topic: "ensemble", title: "Ensemble Programming: Warum 7 Köpfe schneller sind als 1",          excerpt: "Anekdotische Evidenz, ein bisschen Theorie und ein konkreter Session-Aufbau, der auch in 90 Minuten funktioniert.", source: null,    href: "#" },
{ date: "2026-04-09", topic: "adhs",     title: "Der Kalender ist mein Exocortex",                                   excerpt: "Warum ich alles eintrage — vom Arzttermin bis zum Refactoring-Slot — und wie ich das nicht zur zweiten Vollzeitstelle werden lasse.", source: null,    href: "#" },
{ date: "2026-03-21", topic: "softdev",  title: "Refactoring als Reparatur — nicht als Strafe",                     excerpt: "Wenn Refactoring sich anfühlt wie Buße, machen wir es seltener und schlechter. Ein Plädoyer für beiläufiges Aufräumen.",      source: "innoq", href: "#" },
{ date: "2026-02-17", topic: "ensemble", title: "Wie man im Ensemble nicht stört: eine kleine Etikette",            excerpt: "Sechs ungeschriebene Regeln, die Sessions ruhiger machen — von der Driver-Rolle bis zum stillen Beobachten.",                source: null,    href: "#" },
{ date: "2026-01-30", topic: "adhs",     title: "Pairing mit dem ADHS-Brain — vier Tricks, die wirklich helfen",    excerpt: "Kurze Iterationen, klare Rollen, externer Fokus-Timer. Was ich über Jahre angepasst habe, damit es für alle funktioniert.",  source: "innoq", href: "#" },

/* 2025 */
{ date: "2025-12-08", topic: "softdev",  title: "Code-Reviews ohne Drama",                                          excerpt: "Wie man Reviews so führt, dass sie nicht zur Quelle von Frust werden — auf beiden Seiten.",                                  source: null,    href: "#" },
{ date: "2025-11-04", topic: "ensemble", title: "Ensemble-Anti-Patterns: 6 Wege, eine Session zu töten",            excerpt: "Driver-Tyrannen, Schweigemauern, Endlosdiskussionen. Was schiefgeht und was hilft.",                                        source: null,    href: "#" },
{ date: "2025-09-22", topic: "adhs",     title: "Vergessen, aber strukturiert: Notes-Systeme mit ADHS",             excerpt: "Drei Jahre Iteration an einem System, das funktioniert ohne dass es zur eigenen Religion wird.",                            source: "innoq", href: "#" },
{ date: "2025-08-15", topic: "ensemble", title: "Mob-Programming vs Ensemble: was ist der Unterschied?",            excerpt: "Eine begriffliche Klärung — und warum die Wortwahl mehr ausmacht als ich gedacht hätte.",                                   source: null,    href: "#" },
{ date: "2025-06-30", topic: "softdev",  title: "Java oder Kotlin? Eine pragmatische Antwort",                      excerpt: "Spoiler: es kommt auf den Kontext an. Aber es gibt klare Entscheidungs­kriterien.",                                          source: null,    href: "#" },
{ date: "2025-04-17", topic: "softdev",  title: "Pre-mortems statt Post-mortems",                                   excerpt: "Stell dir vor, das Projekt ist gescheitert. Warum? Eine 30-Minuten-Übung, die ich nicht mehr missen will.",                  source: null,    href: "#" },
{ date: "2025-03-05", topic: "adhs",     title: "ADHS und Karriere in der IT: keine Geheimwaffe",                   excerpt: "Über das nervige Narrativ vom „ADHS-Superpower“ — und warum es genauso falsch ist wie das Defizit-Bild.",                  source: "innoq", href: "#" },
{ date: "2025-01-21", topic: "ensemble", title: "Onboarding ins Ensemble: die ersten 30 Minuten",                   excerpt: "Wie ich neue Teammitglieder in eine laufende Ensemble-Session hole, ohne dass es chaotisch wird.",                          source: null,    href: "#" },

/* 2024 */
{ date: "2024-11-12", topic: "adhs",     title: "Test-Driven Development mit dem ADHS-Brain",                       excerpt: "Wie TDD und ein wanderndes Aufmerksamkeits­fenster zusammenpassen, wenn man die Iterationen kurz genug hält.",               source: null,    href: "#" },
{ date: "2024-09-04", topic: "ensemble", title: "Wenn Pair Programming nicht funktioniert",                          excerpt: "Drei Konstellationen, in denen Pairing mehr kaputt macht als hilft — und was man stattdessen probieren kann.",               source: null,    href: "#" },
{ date: "2024-06-18", topic: "softdev",  title: "Microservices: die letzte und die nächste Welle",                  excerpt: "Eine kurze Geschichte der Verteilung, und warum die nächste Generation viel mehr Boring Architecture sein wird.",            source: "innoq", href: "#" },
{ date: "2024-03-22", topic: "adhs",     title: "Warum ich aufgehört habe Hyperfokus zu romantisieren",             excerpt: "Hyperfokus klingt cool. Was er wirklich kostet, merkt man oft erst Tage später. Ein ehrlicher Bericht.",                     source: null,    href: "#" }];

const TOPIC_META = {
  ensemble: { label: "Ensemble",         short: "ENS" },
  adhs:     { label: "ADHS",             short: "ADHS" },
  softdev:  { label: "Software Dev",     short: "DEV" }
};
const TOPIC_FILTERS = [
  { key: "all",      label: "Alle" },
  { key: "ensemble", label: "Ensemble" },
  { key: "adhs",     label: "ADHS" },
  { key: "softdev",  label: "Software Development" }
];


const FOCUS = [
{
  key: "ensemble",
  label: "Ensemble Programming",
  blurb: "Code schreibt sich besser zu siebt. Wie man Sessions strukturiert, Rollen wechselt und das Driver/Navigator-Modell ad absurdum führt.",
  count: 14
},
{
  key: "adhs",
  label: "ADHS in der IT",
  blurb: "Hyperfokus, Reizfilter, Exekutivfunktion: was Neurodivergenz mit Software­entwicklung macht — und wie Teams davon profitieren.",
  count: 9
},
{
  key: "softdev",
  label: "Software Development",
  blurb: "Architektur, Refactoring, Test-Strategien. Pragmatisch, kontextabhängig, ohne Dogma. Meistens in Java, manchmal in Kotlin.",
  count: 27
}];


const TALKS = [
/* Upcoming */
{ date: "2026-06-18", when: "Jun 2026", what: "ADHS in der Software­entwicklung",                where: "Karlsruher Entwicklertag", city: "Karlsruhe", status: "upcoming", type: "talk",     duration: 45,
  abstract: "Wie Neurodivergenz den Alltag im Team verändert — und welche kleinen Anpassungen einen großen Unterschied machen. Ein Vortrag aus der Praxis, ohne Heilsversprechen." },
{ date: "2026-08-20", when: "Aug 2026", what: "Ensemble Programming: 8 Hirne, ein Editor",        where: "SoCraTes",                 city: "Soltau",    status: "upcoming", type: "workshop", duration: 180,
  abstract: "Hands-on Session: wir programmieren zu acht an einem Problem, wechseln Rollen alle zehn Minuten und reflektieren danach gemeinsam, was passiert ist." },
{ date: "2026-10-21", when: "Okt 2026", what: "Wie man im Ensemble nicht stört",                  where: "code.talks",               city: "Hamburg",   status: "upcoming", type: "talk",     duration: 30,
  abstract: "Sechs ungeschriebene Regeln, die Ensemble-Sessions ruhiger machen — und warum das mehr Wirkung hat als die offiziellen Best Practices." },
{ date: "2027-02-04", when: "Feb 2027", what: "Pairing mit dem ADHS-Brain",                       where: "OOP",                      city: "München",   status: "upcoming", type: "talk",  duration: 45,
  abstract: "Vier konkrete Anpassungen, die Pairing für neurodivergente Brains erträglicher machen — und nebenbei auch für alle anderen besser." },

/* Past */
{ date: "2025-11-04", when: "Nov 2025", what: "Refactoring als Reparatur",                        where: "Booster Conference",       city: "Bergen",    status: "past",     type: "talk",     duration: 40,
  abstract: "Wenn Refactoring sich wie Buße anfühlt, machen wir es seltener und schlechter. Ein Plädoyer für beiläufiges Aufräumen.",
  slides: "#", video: "#" },
{ date: "2025-09-15", when: "Sep 2025", what: "Ensemble-Anti-Patterns",                            where: "JCON",                     city: "Köln",      status: "past",     type: "talk",     duration: 30,
  abstract: "Driver-Tyrannen, Schweigemauern, Endlosdiskussionen. Was schief geht in Ensemble-Sessions — und was hilft.",
  slides: "#", video: "#" },
{ date: "2025-06-12", when: "Jun 2025", what: "Test-Strategien jenseits der Pyramide",              where: "JAX",                      city: "Mainz",     status: "past",     type: "talk",     duration: 45,
  abstract: "Die klassische Test-Pyramide ist ein guter Anfang, aber sie ignoriert Integrationspunkte, die in modernen Systemen entscheidend sind.",
  slides: "#", video: "#" },
{ date: "2025-03-18", when: "Mär 2025", what: "Mob Programming vs Ensemble — der Unterschied",     where: "JavaLand",                 city: "Brühl",     status: "past",     type: "talk",     duration: 40,
  abstract: "Eine begriffliche Klärung — und warum die Wortwahl mehr ausmacht als ich gedacht hätte.",
  slides: "#", video: "#" },
{ date: "2024-11-20", when: "Nov 2024", what: "ADHS als Produktivkraft",                            where: "GOTO Berlin",              city: "Berlin",    status: "past",     type: "talk",  duration: 45,
  abstract: "Eine ehrliche Standortbestimmung: was ADHS in der IT bedeutet, was hilft, was nicht, und welche Narrative wir endlich begraben können.",
  slides: "#", video: "#" },
{ date: "2024-09-05", when: "Sep 2024", what: "Pair Programming, aber gut",                        where: "Karlsruher Entwicklertag", city: "Karlsruhe", status: "past",     type: "workshop", duration: 180,
  abstract: "Drei Stunden gemeinsames Pairen mit Reflexionsphasen. Was funktioniert, was scheitert, und wie man als Team eine eigene Praxis findet.",
  slides: "#" }];


const fmtDate = (iso) => {
  const months = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"];
  const d = new Date(iso);
  return `${String(d.getDate()).padStart(2, '0')} ${months[d.getMonth()]} ${d.getFullYear()}`;
};

const fmtFullDate = (iso) => {
  const months = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"];
  const d = new Date(iso);
  return `${d.getDate()}. ${months[d.getMonth()]} ${d.getFullYear()}`;
};

/* ─────────────────────────────────────────────────────────────
   Shared blocks
   ───────────────────────────────────────────────────────────── */

function ThemeToggle() {
  const [mode, setMode] = React.useState(() =>
    document.documentElement.getAttribute("data-mode") || "dark"
  );

  React.useEffect(() => {
    const obs = new MutationObserver(() => {
      const m = document.documentElement.getAttribute("data-mode") || "dark";
      setMode(m);
    });
    obs.observe(document.documentElement, { attributes: true, attributeFilter: ["data-mode"] });
    return () => obs.disconnect();
  }, []);

  const toggle = () => {
    const next = mode === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-mode", next);
    try {
      window.parent.postMessage({ type: "__edit_mode_set_keys", edits: { mode: next } }, "*");
    } catch (e) {}
  };

  const isDark = mode === "dark";
  return (
    <button
      type="button"
      className="theme-toggle"
      onClick={toggle}
      aria-label={isDark ? "Light Mode aktivieren" : "Dark Mode aktivieren"}
      title={isDark ? "Light Mode" : "Dark Mode"}>
      {isDark ? (
        /* Sun — shown in dark mode (click → light) */
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round">
          <circle cx="8" cy="8" r="2.8" />
          <line x1="8" y1="1.2" x2="8" y2="2.6" />
          <line x1="8" y1="13.4" x2="8" y2="14.8" />
          <line x1="1.2" y1="8" x2="2.6" y2="8" />
          <line x1="13.4" y1="8" x2="14.8" y2="8" />
          <line x1="3.2" y1="3.2" x2="4.2" y2="4.2" />
          <line x1="11.8" y1="11.8" x2="12.8" y2="12.8" />
          <line x1="3.2" y1="12.8" x2="4.2" y2="11.8" />
          <line x1="11.8" y1="4.2" x2="12.8" y2="3.2" />
        </svg>
      ) : (
        /* Moon — shown in light mode (click → dark) */
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round">
          <path d="M13.5 9.5A5.5 5.5 0 1 1 6.5 2.5a4.5 4.5 0 0 0 7 7z" />
        </svg>
      )}
    </button>
  );
}

function TopNav({ accentBrand = false }) {
  return (
    <div className="topnav">
      <a href="#" className="brand">
        Joshua Töpfer<span style={{ color: "var(--accent)" }}>.</span>
      </a>
      <nav>
        <a href="#" className="is-current">Index</a>
        <a href="#">Blog</a>
        <a href="#">Talks</a>
        <a href="#">Über mich</a>
        <ThemeToggle />
      </nav>
    </div>
  );
}

function PostsList({ items = POSTS.slice(0, 5), withArrows = true }) {
  return (
    <div>
      {items.map((p) =>
      <a key={p.title} href={p.href} className="row">
          <div className="date mono">{fmtFullDate(p.date)}</div>
          <div>
            <div className="title">
              {p.title}
              {p.source && <span className="src">↗ {p.source}</span>}
            </div>
            {p.excerpt &&
              <div className="excerpt">{p.excerpt}</div>
            }
          </div>
          {withArrows && <div className="arrow">→</div>}
        </a>
      )}
    </div>);

}

function Footer() {
  return (
    <footer>
      <div className="cols">
        <div>
          <h4>Kontakt</h4>
          <p style={{ margin: 0, color: "var(--fg)", fontSize: 16, lineHeight: 1.5, maxWidth: 360 }}>
            Ensemble-Coaching, Talks, oder einfach Hallo sagen — die schnellste Route ist die E-Mail.
          </p>
          <a href="mailto:hallo@joshuatoepfer.de" className="link" style={{ display: "inline-block", marginTop: 16, color: "var(--accent)", fontSize: 16 }}>
            hallo@joshuatoepfer.de →
          </a>
        </div>
        <div>
          <h4>Anderswo</h4>
          <ul>
            <li><a href="#" className="link">GitHub</a></li>
            <li><a href="#" className="link">LinkedIn</a></li>
            <li><a href="#" className="link">RSS-Feed</a></li>
          </ul>
        </div>
        <div>
          <h4>Site</h4>
          <ul>
            <li><a href="#" className="link">Blog</a></li>
            <li><a href="#" className="link">Talks</a></li>
            <li><a href="#" className="link">Über mich</a></li>
          </ul>
        </div>
        <div>
          <h4>Rechtliches</h4>
          <ul>
            <li><a href="#" className="link">Impressum</a></li>
            <li><a href="#" className="link">Datenschutz</a></li>
          </ul>
        </div>
      </div>
      <div className="baseline">
        <span>© 2026 Joshua Töpfer</span>
        <span>RSS · GitHub · LinkedIn</span>
        <span>Built with Jekyll</span>
      </div>
    </footer>);

}

/* Photo slot — small, discreet */
function PhotoSlot({ id, size = 56 }) {
  return (
    <image-slot
      id={id}
      shape="circle"
      width={size}
      height={size}
      placeholder="Foto"
      style={{ flexShrink: 0 }} />);


}

/* ─────────────────────────────────────────────────────────────
   V1 — STATEMENT
   Großer Name als Headline, ruhige Sektionen, klassisch editorial.
   ───────────────────────────────────────────────────────────── */
function VariantStatement() {
  return (
    <div className="jt">
      <TopNav />

      <section className="hero v1-hero" style={{ display: "grid", gridTemplateColumns: "1fr 460px", gap: 64, alignItems: "center" }}>
        <div>
          <h1 data-fade style={{
            fontSize: 132,
            lineHeight: 0.92,
            letterSpacing: "-0.045em",
            fontWeight: 460,
            margin: "0 0 36px",
            maxWidth: "12ch"
          }}>
            Joshua<br />Töpfer<span style={{ color: "var(--accent)" }}>.</span>
          </h1>
          <p data-fade style={{
            fontSize: 26,
            lineHeight: 1.32,
            letterSpacing: "-0.015em",
            fontWeight: 380,
            color: "var(--fg)",
            margin: 0,
            maxWidth: "26ch",
            textWrap: "balance"
          }}>
            Senior Consultant bei
            <span style={{ color: "var(--accent)" }}> INNOQ</span>.
            Schreibt Code im Ensemble, denkt laut über Teams und lebt mit ADHS.
            Was sich, wie sich rausstellt, ganz gut ergänzt.
          </p>
        </div>
        <image-slot
          id="photo-v1-duotone"
          shape="rect"
          radius="2"
          style={{
            width: "460px",
            height: "620px",
            filter: "grayscale(1) contrast(1.1) brightness(0.92)"
          }}
          placeholder="Porträt · Hochformat 3:4"
        />
      </section>

      <hr className="rule" />

      <section data-fade>
        <div className="v1-section-head" style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 36 }}>
          <h2 style={{ fontSize: 14, fontWeight: 500, margin: 0, color: "var(--fg-dim)" }} className="mono">
            <span style={{ color: "var(--fg)" }}>—</span>&nbsp;&nbsp;NEUESTE BEITRÄGE
          </h2>
          <a href="#" className="link mono" style={{ fontSize: 12, color: "var(--fg-dim)", letterSpacing: "0.06em", textTransform: "uppercase" }}>
            Alle ansehen →
          </a>
        </div>
        <PostsList />
      </section>

      <section data-fade>
        <h2 className="mono" style={{ fontSize: 14, fontWeight: 500, margin: "0 0 48px", color: "var(--fg-dim)" }}>
          <span style={{ color: "var(--fg)" }}>—</span>&nbsp;&nbsp;MEINE SCHWERPUNKTE
        </h2>
        <div className="v1-focus" style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 48 }}>
          {FOCUS.map((f, i) =>
          <div key={f.key} style={{ borderTop: "1px solid var(--rule-strong)", paddingTop: 24 }}>
              <div className="mono" style={{ fontSize: 11, color: "var(--fg-faint)", letterSpacing: "0.08em", marginBottom: 18 }}>
                {f.count} BEITRÄGE
              </div>
              <h3 style={{ fontSize: 30, letterSpacing: "-0.02em", fontWeight: 460, margin: "0 0 14px", lineHeight: 1.1 }}>
                {f.label}
              </h3>
              <p style={{ color: "var(--fg-dim)", fontSize: 15, lineHeight: 1.55, margin: 0 }}>
                {f.blurb}
              </p>
              <a href="#" className="mono link" style={{ display: "inline-block", marginTop: 22, color: "var(--accent)", fontSize: 13, letterSpacing: "0.04em", textTransform: "uppercase" }}>
                Posts lesen →
              </a>
            </div>
          )}
        </div>
      </section>

      <section data-fade>
        <div className="v1-section-head" style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 36 }}>
          <h2 className="mono" style={{ fontSize: 14, fontWeight: 500, margin: 0, color: "var(--fg-dim)" }}>
            <span style={{ color: "var(--fg)" }}>—</span>&nbsp;&nbsp;KOMMENDE TALKS
          </h2>
          <a href="#" className="link mono" style={{ fontSize: 12, color: "var(--fg-dim)", letterSpacing: "0.06em", textTransform: "uppercase" }}>
            Speaker-Profil →
          </a>
        </div>
        <div>
          {TALKS.filter((t) => t.status === "upcoming").map((t, i, arr) =>
          <div key={t.what} className="v1-talk" style={{
            display: "grid",
            gridTemplateColumns: "300px 1fr",
            gap: 48,
            alignItems: "baseline",
            padding: "28px 0",
            borderTop: "1px solid var(--rule)",
            borderBottom: i === arr.length - 1 ? "1px solid var(--rule)" : "none"
          }}>
              <div className="v1-talk__meta" style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                <div className="mono" style={{
                  fontSize: 12,
                  color: "var(--accent)",
                  letterSpacing: "0.06em",
                  textTransform: "uppercase",
                  fontWeight: 500
                }}>
                  {fmtFullDate(t.date)}
                </div>
                <div className="mono" style={{
                  fontSize: 12,
                  color: "var(--fg-dim)",
                  letterSpacing: "0.02em"
                }}>
                  {t.where} <span style={{ color: "var(--fg-faint)" }}>·</span> {t.city}
                </div>
              </div>
              <h3 className="v1-talk__title" style={{
                fontSize: 26,
                fontWeight: 460,
                letterSpacing: "-0.015em",
                margin: 0,
                lineHeight: 1.2,
                maxWidth: "30ch"
              }}>
                {t.what}
              </h3>
            </div>
          )}
        </div>
      </section>

      <Footer />
    </div>);

}

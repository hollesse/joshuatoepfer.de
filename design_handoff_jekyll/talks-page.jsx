/* talks-page.jsx — Talks overview */

/* Shared: Footer, fmtFullDate, TALKS from homepage-v1-v2.jsx */

const TALK_TYPE_META = {
  talk:     { label: "Vortrag",  short: "TALK" },
  workshop: { label: "Workshop", short: "WS" },
  keynote:  { label: "Keynote",  short: "KEY" }
};

function TalksNav() {
  return (
    <div className="topnav">
      <a href="#" className="brand">
        Joshua Töpfer<span style={{ color: "var(--accent)" }}>.</span>
      </a>
      <nav>
        <a href="#">Index</a>
        <a href="#">Blog</a>
        <a href="#" className="is-current">Talks</a>
        <a href="#">Über mich</a>
        <ThemeToggle />
      </nav>
    </div>
  );
}

function TalksHeader({ upcomingCount, totalCount }) {
  return (
    <section className="talks-hero" style={{ padding: "72px 80px 28px" }}>
      <div className="label-eyebrow" style={{ marginBottom: 18 }}>
        Talks · {upcomingCount} geplant · {totalCount} insgesamt
      </div>
      <h1 style={{
        fontSize: 80,
        lineHeight: 0.95,
        letterSpacing: "-0.035em",
        fontWeight: 460,
        margin: 0,
        maxWidth: "16ch"
      }}>
        Auf der Bühne<span style={{ color: "var(--accent)" }}>.</span>
      </h1>
      <p style={{
        fontSize: 19,
        lineHeight: 1.5,
        color: "var(--fg-dim)",
        margin: "28px 0 0",
        maxWidth: "62ch"
      }}>
        Vorträge, Workshops und Keynotes zu Ensemble Programming, ADHS in der
        IT und allem dazwischen. Wenn du mich für eine Konferenz oder ein
        internes Format buchen willst, schreib mir.
      </p>
    </section>
  );
}

function TypePill({ type, accent = false }) {
  return (
    <span className="mono" style={{
      display: "inline-block",
      border: "1px solid " + (accent ? "color-mix(in oklab, var(--accent) 40%, transparent)" : "var(--rule)"),
      color: accent ? "var(--accent)" : "var(--fg-dim)",
      padding: "5px 10px",
      borderRadius: 999,
      fontSize: 10,
      letterSpacing: "0.08em",
      textTransform: "uppercase",
      fontWeight: 500
    }}>
      {TALK_TYPE_META[type]?.label}
    </span>
  );
}

function TalksPage() {
  const upcoming = TALKS.filter((t) => t.status === "upcoming");
  const past = TALKS.filter((t) => t.status === "past");

  return (
    <div className="jt">
      <TalksNav />
      <TalksHeader upcomingCount={upcoming.length} totalCount={TALKS.length} />

      {/* Kommende Talks */}
      <section style={{ padding: "56px 80px 88px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 32 }}>
          <h2 className="mono" style={{ fontSize: 14, fontWeight: 500, margin: 0, color: "var(--fg-dim)" }}>
            <span style={{ color: "var(--fg)" }}>—</span>&nbsp;&nbsp;KOMMENDE
          </h2>
          <div className="mono" style={{ fontSize: 11, color: "var(--fg-faint)", letterSpacing: "0.08em", textTransform: "uppercase" }}>
            {upcoming.length} geplant
          </div>
        </div>
        <div>
          {upcoming.map((t, i, arr) => (
            <div key={t.what} className="talks-row" style={{
              display: "grid",
              gridTemplateColumns: "300px 1fr 140px",
              gap: 48,
              alignItems: "baseline",
              padding: "32px 0",
              borderTop: "1px solid var(--rule)",
              borderBottom: i === arr.length - 1 ? "1px solid var(--rule)" : "none"
            }}>
              <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                <div className="mono" style={{ fontSize: 12, color: "var(--accent)", letterSpacing: "0.06em", textTransform: "uppercase", fontWeight: 500 }}>
                  {fmtFullDate(t.date)}
                </div>
                <div className="mono" style={{ fontSize: 12, color: "var(--fg-dim)", letterSpacing: "0.02em" }}>
                  {t.where} <span style={{ color: "var(--fg-faint)" }}>·</span> {t.city}
                </div>
              </div>
              <div>
                <h3 style={{ fontSize: 26, fontWeight: 460, letterSpacing: "-0.015em", margin: 0, lineHeight: 1.2, maxWidth: "26ch" }}>
                  {t.what}
                </h3>
                <p style={{ color: "var(--fg-dim)", fontSize: 15, lineHeight: 1.55, margin: "12px 0 0", maxWidth: "60ch" }}>
                  {t.abstract}
                </p>
              </div>
              <div style={{ textAlign: "right" }}>
                <TypePill type={t.type} accent />
                <div className="mono" style={{ fontSize: 11, color: "var(--fg-faint)", letterSpacing: "0.04em", marginTop: 10, textTransform: "uppercase" }}>
                  {t.duration} min
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Vergangene Talks */}
      <section style={{ padding: "32px 80px 88px", borderTop: "1px solid var(--rule-strong)" }}>        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 32, paddingTop: 56 }}>
          <h2 className="mono" style={{ fontSize: 14, fontWeight: 500, margin: 0, color: "var(--fg-dim)" }}>
            <span style={{ color: "var(--fg)" }}>—</span>&nbsp;&nbsp;VERGANGENE
          </h2>
          <div className="mono" style={{ fontSize: 11, color: "var(--fg-faint)", letterSpacing: "0.08em", textTransform: "uppercase" }}>
            {past.length} gehalten
          </div>
        </div>
        <div>
          {past.map((t, i, arr) => (
            <div key={t.what + t.date} className="talks-row" style={{
              display: "grid",
              gridTemplateColumns: "300px 1fr 140px",
              gap: 48,
              alignItems: "baseline",
              padding: "32px 0",
              borderTop: "1px solid var(--rule)",
              borderBottom: i === arr.length - 1 ? "1px solid var(--rule)" : "none"
            }}>
              <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                <div className="mono" style={{ fontSize: 12, color: "var(--fg-dim)", letterSpacing: "0.06em", textTransform: "uppercase", fontWeight: 500 }}>
                  {fmtFullDate(t.date)}
                </div>
                <div className="mono" style={{ fontSize: 12, color: "var(--fg-dim)", letterSpacing: "0.02em" }}>
                  {t.where} <span style={{ color: "var(--fg-faint)" }}>·</span> {t.city}
                </div>
              </div>
              <div>
                <h3 style={{ fontSize: 24, fontWeight: 440, letterSpacing: "-0.012em", margin: 0, lineHeight: 1.2, maxWidth: "28ch", color: "var(--fg)" }}>
                  {t.what}
                </h3>
                <p style={{ color: "var(--fg-dim)", fontSize: 14.5, lineHeight: 1.55, margin: "10px 0 14px", maxWidth: "60ch" }}>
                  {t.abstract}
                </p>
                <div style={{ display: "flex", gap: 18 }}>
                  {t.slides && <a href={t.slides} className="link mono" style={{ fontSize: 12, color: "var(--accent)", letterSpacing: "0.04em", textTransform: "uppercase" }}>↗ Slides</a>}
                  {t.video && <a href={t.video} className="link mono" style={{ fontSize: 12, color: "var(--accent)", letterSpacing: "0.04em", textTransform: "uppercase" }}>↗ Aufzeichnung</a>}
                </div>
              </div>
              <div style={{ textAlign: "right" }}>
                <TypePill type={t.type} />
                <div className="mono" style={{ fontSize: 11, color: "var(--fg-faint)", letterSpacing: "0.04em", marginTop: 10, textTransform: "uppercase" }}>
                  {t.duration} min
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Speaker-Profil / Booking */}
      <section style={{
        padding: "80px 80px 96px",
        borderTop: "1px solid var(--rule-strong)",
        background: "color-mix(in oklab, var(--fg) 3%, var(--bg))"
      }}>
        <div className="speaker-block" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 80, alignItems: "start" }}>
          <div>
            <div className="mono" style={{ fontSize: 11, color: "var(--accent)", letterSpacing: "0.1em", textTransform: "uppercase", fontWeight: 500, marginBottom: 28 }}>
              Speaker-Profil
            </div>
            <h2 style={{
              fontSize: 48,
              lineHeight: 1.05,
              letterSpacing: "-0.025em",
              fontWeight: 440,
              margin: "0 0 24px",
              maxWidth: "16ch",
              textWrap: "balance"
            }}>
              Auf eurer Konferenz oder im Team<span style={{ color: "var(--accent)" }}>.</span>
            </h2>
            <p style={{ fontSize: 18, lineHeight: 1.55, color: "var(--fg-dim)", margin: "0 0 20px", maxWidth: "44ch" }}>
              Ich halte gerne Vorträge, mache Workshops und moderiere
              Ensemble-Sessions. Auf öffentlichen Konferenzen genauso wie
              firmenintern. Format ist verhandelbar, der Anspruch nicht: ehrlich,
              praxisnah und ohne Slide-Folien voller Buzzwords.
            </p>
            <p style={{ fontSize: 16, lineHeight: 1.55, color: "var(--fg-dim)", margin: 0, maxWidth: "44ch" }}>
              Wenn das nach etwas klingt, das zu eurem Event passt:&nbsp;
              <a href="mailto:hallo@joshuatoepfer.de" className="link" style={{ color: "var(--accent)" }}>hallo@joshuatoepfer.de</a>.
            </p>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 32 }}>
            <div>
              <div className="mono" style={{ fontSize: 11, color: "var(--fg-faint)", letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 14 }}>
                Themen, über die ich spreche
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                <span className="chip">Ensemble Programming</span>
                <span className="chip">ADHS in der IT</span>
                <span className="chip">Software Crafting</span>
                <span className="chip">Pair Programming</span>
                <span className="chip">Refactoring</span>
                <span className="chip">Teamarbeit</span>
              </div>
            </div>

            <div style={{ paddingTop: 12 }}>
              <div className="mono" style={{ fontSize: 11, color: "var(--fg-faint)", letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 10 }}>
                Formate
              </div>
              <div style={{ fontSize: 14, color: "var(--fg)", lineHeight: 1.6 }}>
                Vortrag 30–60 min · Workshop · Coaching · Inhouse-Formate
              </div>
            </div>

            <div style={{ paddingTop: 16, borderTop: "1px solid var(--rule)", display: "flex", gap: 18, flexWrap: "wrap" }}>
              <a href="#" className="link mono" style={{ fontSize: 12, color: "var(--accent)", letterSpacing: "0.06em", textTransform: "uppercase" }}>
                ↗ Bio &amp; Pressefoto (.zip)
              </a>
              <a href="#" className="link mono" style={{ fontSize: 12, color: "var(--fg-dim)", letterSpacing: "0.06em", textTransform: "uppercase" }}>
                ↗ Sessionize-Profil
              </a>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}

window.TalksPage = TalksPage;

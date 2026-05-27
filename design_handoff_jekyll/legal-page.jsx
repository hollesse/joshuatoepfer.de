/* legal-page.jsx — Standard page template for legal pages (Impressum, Datenschutz) */

/* Shared from homepage-v1-v2.jsx: Footer */

/* Topnav: no current item highlighted since legal pages live in the footer */
function LegalNav() {
  return (
    <div className="topnav">
      <a href="#" className="brand">
        Joshua Töpfer<span style={{ color: "var(--accent)" }}>.</span>
      </a>
      <nav>
        <a href="#">Index</a>
        <a href="#">Blog</a>
        <a href="#">Talks</a>
        <a href="#">Über mich</a>
        <ThemeToggle />
      </nav>
    </div>
  );
}

/* Demo body — Impressum content */
function ImpressumBody() {
  return (
    <>
      <h2>Angaben gemäß § 5 TMG</h2>
      <p>
        Joshua Töpfer<br />
        c/o INNOQ Deutschland GmbH<br />
        Krischerstraße 100<br />
        40789 Monheim am Rhein
      </p>

      <h2>Kontakt</h2>
      <p>
        E-Mail: <a href="mailto:hallo@joshuatoepfer.de">hallo@joshuatoepfer.de</a>
      </p>

      <h2>Verantwortlich für den Inhalt nach § 18 Abs. 2 MStV</h2>
      <p>
        Joshua Töpfer<br />
        (Anschrift wie oben)
      </p>

      <h2>Haftung für Inhalte</h2>
      <p>
        Als Diensteanbieter bin ich gemäß § 7 Abs.1 TMG für eigene Inhalte auf
        diesen Seiten nach den allgemeinen Gesetzen verantwortlich. Nach §§ 8
        bis 10 TMG bin ich als Diensteanbieter jedoch nicht verpflichtet,
        übermittelte oder gespeicherte fremde Informationen zu überwachen oder
        nach Umständen zu forschen, die auf eine rechtswidrige Tätigkeit
        hinweisen.
      </p>
      <p>
        Verpflichtungen zur Entfernung oder Sperrung der Nutzung von
        Informationen nach den allgemeinen Gesetzen bleiben hiervon unberührt.
        Eine diesbezügliche Haftung ist jedoch erst ab dem Zeitpunkt der
        Kenntnis einer konkreten Rechtsverletzung möglich.
      </p>

      <h2>Haftung für Links</h2>
      <p>
        Dieses Angebot enthält Links zu externen Websites Dritter, auf deren
        Inhalte ich keinen Einfluss habe. Deshalb kann ich für diese fremden
        Inhalte auch keine Gewähr übernehmen. Für die Inhalte der verlinkten
        Seiten ist stets der jeweilige Anbieter oder Betreiber der Seiten
        verantwortlich.
      </p>

      <h2>Urheberrecht</h2>
      <p>
        Die durch den Seitenbetreiber erstellten Inhalte und Werke auf diesen
        Seiten unterliegen dem deutschen Urheberrecht. Die Vervielfältigung,
        Bearbeitung, Verbreitung und jede Art der Verwertung außerhalb der
        Grenzen des Urheberrechtes bedürfen der schriftlichen Zustimmung des
        jeweiligen Autors bzw. Erstellers.
      </p>
    </>
  );
}

/* ─────────────────────────────────────────────────────────────
   Standard legal page — reusable template
   Slots: `title`, `subtitle` (optional), `lastUpdated` (optional), `children`
   ───────────────────────────────────────────────────────────── */
function LegalPage({ title, subtitle, lastUpdated, children }) {
  return (
    <div className="jt">
      <LegalNav />

      <section className="legal-hero" style={{ padding: "72px 80px 0" }}>
        <a href="#" className="mono link" style={{
          fontSize: 11,
          color: "var(--fg-dim)",
          letterSpacing: "0.08em",
          textTransform: "uppercase",
          display: "inline-block",
          marginBottom: 32
        }}>
          ← Zurück zur Startseite
        </a>
        <h1 style={{
          fontSize: 72,
          lineHeight: 1,
          letterSpacing: "-0.035em",
          fontWeight: 440,
          margin: "0 0 24px",
          maxWidth: "20ch"
        }}>
          {title}<span style={{ color: "var(--accent)" }}>.</span>
        </h1>
        {subtitle && (
          <p style={{
            fontSize: 20,
            lineHeight: 1.45,
            color: "var(--fg-dim)",
            fontWeight: 380,
            margin: 0,
            maxWidth: "56ch",
            letterSpacing: "-0.008em"
          }}>
            {subtitle}
          </p>
        )}
        {lastUpdated && (
          <div className="mono" style={{
            fontSize: 11,
            color: "var(--fg-faint)",
            letterSpacing: "0.08em",
            textTransform: "uppercase",
            marginTop: 28
          }}>
            Zuletzt aktualisiert · {lastUpdated}
          </div>
        )}
      </section>

      <section style={{ padding: "56px 80px 88px" }}>
        <div className="post-body" style={{ maxWidth: "72ch" }}>
          {children}
        </div>
      </section>

      <Footer />
    </div>
  );
}

/* Concrete examples that exercise the template */
function ImpressumPage() {
  return (
    <LegalPage
      title="Impressum">
      <ImpressumBody />
    </LegalPage>
  );
}

function DatenschutzPage() {
  return (
    <LegalPage
      title="Datenschutz"
      subtitle="Diese Seite verarbeitet so wenig personenbezogene Daten wie möglich. Was passiert und warum, steht hier.">
      <h2>Server-Logs</h2>
      <p>
        Beim Aufruf dieser Seite erhebt mein Hosting-Provider technisch
        notwendige Daten in Server-Logs: aufgerufene URL, Zeitpunkt,
        Browsertyp, anonymisierte IP-Adresse. Diese Daten werden nach 14 Tagen
        automatisch gelöscht und nicht mit anderen Datenquellen
        zusammengeführt.
      </p>

      <h2>Cookies</h2>
      <p>
        Diese Seite setzt keine Cookies. Es findet kein Tracking statt, weder
        durch mich noch durch externe Dienste.
      </p>

      <h2>Externe Inhalte</h2>
      <p>
        Eingebettete Schriftarten (Geist und Geist Mono) werden lokal vom
        eigenen Server ausgeliefert. Es findet keine Verbindung zu
        Google&nbsp;Fonts oder anderen externen Schrift-Diensten statt.
      </p>

      <h2>Kontaktaufnahme per E-Mail</h2>
      <p>
        Wenn du mir eine E-Mail schreibst, speichere ich deine Nachricht
        und deine Adresse so lange, wie es zur Beantwortung deiner Anfrage
        nötig ist. Eine Weitergabe an Dritte findet nicht statt.
      </p>

      <h2>Deine Rechte</h2>
      <p>
        Du hast jederzeit das Recht auf Auskunft über die zu deiner Person
        gespeicherten Daten, deren Herkunft und Empfänger sowie den Zweck der
        Datenverarbeitung — sowie auf Berichtigung, Löschung oder Sperrung
        dieser Daten. Schreib mir dazu eine kurze E-Mail.
      </p>
    </LegalPage>
  );
}

window.LegalPage = LegalPage;
window.ImpressumPage = ImpressumPage;
window.DatenschutzPage = DatenschutzPage;

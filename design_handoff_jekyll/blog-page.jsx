/* blog-page.jsx — Blog overview, 3 variants */

/* Shared helpers — POSTS, TOPIC_META, TOPIC_FILTERS, fmtDate, fmtFullDate,
   TopNav, Footer come from homepage-v1-v2.jsx via window scope. */

function groupByYear(posts) {
  const groups = {};
  posts.forEach((p) => {
    const y = new Date(p.date).getFullYear();
    (groups[y] = groups[y] || []).push(p);
  });
  return Object.entries(groups).sort((a, b) => Number(b[0]) - Number(a[0]));
}

function FilterChips({ active, onChange, counts }) {
  return (
    <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
      {TOPIC_FILTERS.map((t) => {
        const isActive = active === t.key;
        return (
          <button
            key={t.key}
            type="button"
            onClick={() => onChange(t.key)}
            className="mono"
            style={{
              appearance: "none",
              border: isActive ? "1px solid var(--accent)" : "1px solid var(--rule)",
              background: isActive ? "var(--accent-soft)" : "transparent",
              color: isActive ? "var(--accent)" : "var(--fg-dim)",
              borderRadius: 999,
              padding: "8px 14px",
              fontSize: 11,
              letterSpacing: "0.06em",
              textTransform: "uppercase",
              cursor: "pointer",
              fontFamily: "Geist Mono, monospace",
              transition: "color 200ms ease, border-color 200ms ease, background 200ms ease"
            }}>
            {t.label}
            {counts && (
              <span style={{ marginLeft: 8, color: isActive ? "var(--accent)" : "var(--fg-faint)", fontWeight: 400, opacity: isActive ? 0.7 : 1 }}>
                {counts[t.key] ?? 0}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}

function useTopicFilter() {
  const [topic, setTopic] = React.useState("all");
  const filtered = topic === "all" ? POSTS : POSTS.filter((p) => p.topic === topic);
  const counts = React.useMemo(() => {
    const c = { all: POSTS.length };
    POSTS.forEach((p) => { c[p.topic] = (c[p.topic] || 0) + 1; });
    return c;
  }, []);
  return { topic, setTopic, filtered, counts };
}

/* TopNav variant that marks Blog as current */
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

/* Header common to all blog variants */
function BlogHeader({ count }) {
  return (
    <section className="blog-hero" style={{ padding: "72px 80px 28px" }}>
      <div className="label-eyebrow" style={{ marginBottom: 18 }}>
        Blog · {count} Beiträge · seit 2019
      </div>
      <h1 style={{
        fontSize: 80,
        lineHeight: 0.95,
        letterSpacing: "-0.035em",
        fontWeight: 460,
        margin: 0,
        maxWidth: "16ch"
      }}>
        Notizen aus der Praxis<span style={{ color: "var(--accent)" }}>.</span>
      </h1>
      <p style={{
        fontSize: 19,
        lineHeight: 1.5,
        color: "var(--fg-dim)",
        margin: "28px 0 0",
        maxWidth: "60ch"
      }}>
        Was beim Pairen passiert, was ADHS damit zu tun hat, und warum
        Refactoring keine Strafe sein muss. Manches gibt's nur hier, anderes
        habe ich drüben auf <a href="#" className="link" style={{ color: "var(--fg)" }}>innoq.com</a> geschrieben.
      </p>
    </section>
  );
}

/* ─────────────────────────────────────────────────────────────
   V2 — MAGAZINE
   Volle Breite, Jahr als großer horizontaler Divider, Posts als
   breite Karten-Zeilen mit großem Titel.
   ───────────────────────────────────────────────────────────── */
function BlogPage() {
  const { topic, setTopic, filtered, counts } = useTopicFilter();
  const groups = groupByYear(filtered);

  return (
    <div className="jt">
      <BlogNav />
      <BlogHeader count={POSTS.length} />

      <section style={{ padding: "16px 80px 64px" }}>
        <FilterChips active={topic} onChange={setTopic} counts={counts} />
      </section>

      {groups.map(([year, posts]) => (
        <section key={year} style={{ padding: "0 80px 80px" }}>
          {/* Year divider — display heading on left, count on right */}
          <div className="blog-year-divider" style={{
            display: "flex",
            alignItems: "flex-end",
            justifyContent: "space-between",
            borderTop: "1px solid var(--rule-strong)",
            paddingTop: 28,
            marginBottom: 16
          }}>
            <h2 style={{
              fontSize: 84,
              lineHeight: 0.95,
              letterSpacing: "-0.04em",
              fontWeight: 360,
              margin: 0,
              color: "var(--fg)"
            }}>{year}</h2>
            <div className="mono" style={{
              fontSize: 11,
              color: "var(--fg-faint)",
              letterSpacing: "0.08em",
              textTransform: "uppercase",
              paddingBottom: 14
            }}>
              {posts.length} {posts.length === 1 ? "Beitrag" : "Beiträge"}
            </div>
          </div>

          {posts.map((p) => (
            <a key={p.title} href={p.href} className="blog-post-row" style={{
              display: "grid",
              gridTemplateColumns: "180px 1fr 160px",
              gap: 48,
              padding: "36px 0",
              borderTop: "1px solid var(--rule)",
              alignItems: "baseline"
            }}>
              <div>
                <div className="mono" style={{ fontSize: 12, color: "var(--accent)", letterSpacing: "0.04em", fontWeight: 500, textTransform: "uppercase", marginBottom: 4 }}>
                  {fmtFullDate(p.date)}
                </div>
                {p.source && (
                  <div className="mono" style={{ fontSize: 10, color: "var(--fg-faint)", letterSpacing: "0.08em", textTransform: "uppercase" }}>
                    ↗ via {p.source}
                  </div>
                )}
              </div>
              <div>
                <h3 style={{
                  fontSize: 32,
                  fontWeight: 440,
                  letterSpacing: "-0.018em",
                  lineHeight: 1.15,
                  margin: 0,
                  maxWidth: "26ch"
                }}>{p.title}</h3>
                <p style={{
                  color: "var(--fg-dim)",
                  fontSize: 16,
                  lineHeight: 1.55,
                  margin: "14px 0 0",
                  maxWidth: "60ch"
                }}>{p.excerpt}</p>
              </div>
              <div style={{ textAlign: "right" }}>
                <span className="mono" style={{
                  display: "inline-block",
                  border: "1px solid var(--rule)",
                  padding: "5px 10px",
                  borderRadius: 999,
                  fontSize: 10,
                  color: "var(--fg-dim)",
                  letterSpacing: "0.08em",
                  textTransform: "uppercase"
                }}>
                  {TOPIC_META[p.topic]?.label}
                </span>
              </div>
            </a>
          ))}
        </section>
      ))}

      <Footer />
    </div>
  );
}

window.BlogPage = BlogPage;

/* app.jsx — root: TweaksPanel + DesignCanvas with 4 artboards */

const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "mode": "dark",
  "accent": "amber"
}/*EDITMODE-END*/;

const ACCENT_OPTIONS = [
  { key: "amber", label: "Amber",    swatch: "oklch(0.80 0.14 78)" },
  { key: "coral", label: "Coral",    swatch: "oklch(0.74 0.17 32)" },
  { key: "blue",  label: "Electric", swatch: "oklch(0.78 0.13 240)" },
  { key: "lime",  label: "Lime",     swatch: "oklch(0.86 0.18 130)" },
];

function applyTheme({ mode, accent }) {
  const html = document.documentElement;
  html.setAttribute("data-mode", mode);
  html.setAttribute("data-accent", accent);
}

/* Scroll-fade is gated by `body.jt-fade-ready` in CSS. We only enable
   it in environments where IntersectionObserver works reliably — which
   excludes the transformed DesignCanvas subtree. For now we skip it
   entirely on the canvas view so all content renders visible. The hook
   stays available for the standalone build later. */
function useScrollFade(enabled = false) {
  React.useEffect(() => {
    if (!enabled) return;
    document.body.classList.add("jt-fade-ready");
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add("in");
            io.unobserve(e.target);
          }
        });
      },
      { rootMargin: "0px 0px -10% 0px", threshold: 0.05 }
    );
    const observeAll = () => {
      document.querySelectorAll("[data-fade]:not(.in)").forEach((el) => io.observe(el));
    };
    observeAll();
    const mo = new MutationObserver(observeAll);
    mo.observe(document.body, { childList: true, subtree: true });
    return () => {
      io.disconnect();
      mo.disconnect();
      document.body.classList.remove("jt-fade-ready");
    };
  }, [enabled]);
}

/* Each artboard has an inner scroll-and-pan-safe wrapper so the page
   content sits flush. Artboards are tall enough to show the full page. */
function Artboard({ id, label, variant }) {
  const Variant = variant;
  return (
    <DCArtboard id={id} label={label} width={1440} height={3000} style={{ background: "var(--bg)" }}>
      <Variant />
    </DCArtboard>
  );
}

function App() {
  const [t, setTweak] = useTweaks(TWEAK_DEFAULTS);
  // Disabled inside the design-canvas viewport — transforms break the
  // IntersectionObserver + opacity transition combo. Will be re-enabled
  // for the standalone homepage build.
  useScrollFade(false);

  React.useEffect(() => {
    applyTheme(t);
  }, [t.mode, t.accent]);

  return (
    <>
      <DesignCanvas minScale={0.08} maxScale={1.4}>
        <DCSection
          id="homepage"
          title="Startseite joshuatoepfer.de"
          subtitle="Desktop und Mobile nebeneinander. Klick zum Fullscreen.">
          <DCArtboard id="v1-statement" label="Desktop · 1440px" width={1440} height={3400} style={{ background: "var(--bg)" }}>
            <VariantStatement />
          </DCArtboard>
          <DCArtboard id="v1-statement-mobile" label="Mobile · 402px" width={402} height={4400} style={{ background: "var(--bg)" }}>
            <VariantStatement />
          </DCArtboard>
        </DCSection>

        <DCSection
          id="blog"
          title="Blog-Übersicht · /blog/"
          subtitle="Desktop und Mobile.">
          <DCArtboard id="blog" label="Desktop · 1440px" width={1440} height={5200} style={{ background: "var(--bg)" }}>
            <BlogPage />
          </DCArtboard>
          <DCArtboard id="blog-mobile" label="Mobile · 402px" width={402} height={6800} style={{ background: "var(--bg)" }}>
            <BlogPage />
          </DCArtboard>
        </DCSection>
        <DCSection
          id="post"
          title="Post-Seite · /blog/:slug/"
          subtitle="Desktop und Mobile.">
          <DCArtboard id="post" label="Desktop · 1440px" width={1440} height={4400} style={{ background: "var(--bg)" }}>
            <PostPage />
          </DCArtboard>
          <DCArtboard id="post-mobile" label="Mobile · 402px" width={402} height={5400} style={{ background: "var(--bg)" }}>
            <PostPage />
          </DCArtboard>
        </DCSection>
        <DCSection
          id="talks"
          title="Talks-Seite · /talks/"
          subtitle="Desktop und Mobile.">
          <DCArtboard id="talks" label="Desktop · 1440px" width={1440} height={4000} style={{ background: "var(--bg)" }}>
            <TalksPage />
          </DCArtboard>
          <DCArtboard id="talks-mobile" label="Mobile · 402px" width={402} height={5400} style={{ background: "var(--bg)" }}>
            <TalksPage />
          </DCArtboard>
        </DCSection>
        <DCSection
          id="about"
          title="Über mich · /ueber-mich/"
          subtitle="Desktop und Mobile.">
          <DCArtboard id="about" label="Desktop · 1440px" width={1440} height={3600} style={{ background: "var(--bg)" }}>
            <AboutPage />
          </DCArtboard>
          <DCArtboard id="about-mobile" label="Mobile · 402px" width={402} height={3400} style={{ background: "var(--bg)" }}>
            <AboutPage />
          </DCArtboard>
        </DCSection>
        <DCSection
          id="legal"
          title="Standard-Seite · z. B. /impressum/, /datenschutz/"
          subtitle="Wiederverwendbares Template — Desktop und Mobile.">
          <DCArtboard id="impressum" label="Desktop · Impressum" width={1440} height={2200} style={{ background: "var(--bg)" }}>
            <ImpressumPage />
          </DCArtboard>
          <DCArtboard id="datenschutz" label="Desktop · Datenschutz" width={1440} height={2200} style={{ background: "var(--bg)" }}>
            <DatenschutzPage />
          </DCArtboard>
          <DCArtboard id="impressum-mobile" label="Mobile · Impressum" width={402} height={2400} style={{ background: "var(--bg)" }}>
            <ImpressumPage />
          </DCArtboard>
        </DCSection>
      </DesignCanvas>

      <TweaksPanel title="Tweaks">
        <TweakSection label="Modus" />
        <TweakRadio
          label="Theme"
          value={t.mode}
          options={["dark", "light"]}
          onChange={(v) => setTweak("mode", v)}
        />
        <TweakSection label="Akzentfarbe" />
        <TweakColor
          label="Accent"
          value={t.accent}
          options={ACCENT_OPTIONS.map((o) => o.swatch)}
          onChange={(swatch) => {
            const found = ACCENT_OPTIONS.find((o) => o.swatch === swatch);
            if (found) setTweak("accent", found.key);
          }}
        />
        <div style={{ padding: "8px 14px 4px", fontFamily: "Geist Mono, ui-monospace, monospace", fontSize: 10.5, color: "rgba(255,255,255,0.45)", letterSpacing: "0.04em", lineHeight: 1.5 }}>
          Aktiver Akzent: <strong style={{ color: "rgba(255,255,255,0.85)" }}>{ACCENT_OPTIONS.find(o => o.key === t.accent)?.label}</strong>
        </div>
      </TweaksPanel>
    </>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);

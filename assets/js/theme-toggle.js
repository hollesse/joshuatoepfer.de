// =============================================================================
// theme-toggle.js
// Sun/Moon button toggles data-mode on <html>, persists to localStorage.
// Also: scroll-fade observer + post-page TOC generation from <h2>s and <h3>s.
// =============================================================================

(function () {
  const STORAGE_KEY = "jt-mode";
  const root = document.documentElement;

  function applyMode(mode) {
    root.setAttribute("data-mode", mode);
    try { localStorage.setItem(STORAGE_KEY, mode); } catch (e) {}
  }

  document.querySelectorAll("[data-theme-toggle]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const current = root.getAttribute("data-mode") || "dark";
      applyMode(current === "dark" ? "light" : "dark");
    });
  });

  // -- Scroll fade for [data-fade] elements ----------------------------------
  if ("IntersectionObserver" in window) {
    document.body.classList.add("jt-fade-ready");
    const io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("in");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: "0px 0px -40px 0px" });

    document.querySelectorAll("[data-fade]").forEach(function (el) { io.observe(el); });
  } else {
    document.querySelectorAll("[data-fade]").forEach(function (el) { el.classList.add("in"); });
  }

  // -- Post TOC: build from h2s/h3s inside .post-body ------------------------
  // Scan both h2 and h3 so syndicated INNOQ articles (h3 section headings,
  // h1=title already in hero) get a populated TOC. Flat list; if both levels
  // ever coexist in one post, refine to nested rendering then.
  const toc = document.getElementById("post-toc-list");
  const body = document.querySelector(".post-body");
  if (toc && body) {
    const headings = body.querySelectorAll("h2, h3");
    if (headings.length > 0) {
      const items = [];
      headings.forEach(function (h, i) {
        if (!h.id) {
          h.id = "h-" + (h.textContent || "")
            .toLowerCase()
            .normalize("NFKD")
            .replace(/[̀-ͯ]/g, "")
            .replace(/ä/g, "ae").replace(/ö/g, "oe").replace(/ü/g, "ue").replace(/ß/g, "ss")
            .replace(/[^a-z0-9]+/g, "-")
            .replace(/^-+|-+$/g, "") || ("section-" + i);
        }
        items.push(
          '<li><a href="#' + h.id + '" class="link">' +
          (h.textContent || "").trim() +
          "</a></li>"
        );
      });
      toc.innerHTML = items.join("");
    }
  }
})();

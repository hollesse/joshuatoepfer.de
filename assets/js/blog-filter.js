// =============================================================================
// blog-filter.js
// Filters .blog-post-row elements by data-topic, syncs URL ?topic= query.
// =============================================================================

(function () {
  const chips = document.querySelectorAll(".filter-chip[data-topic]");
  const rows = document.querySelectorAll(".blog-post-row");
  const yearSections = document.querySelectorAll(".blog-year");
  if (!chips.length) return;

  function setActive(topic) {
    chips.forEach(function (c) {
      c.classList.toggle("is-active", c.dataset.topic === topic);
    });

    rows.forEach(function (row) {
      const match = topic === "all" || row.dataset.topic === topic;
      row.style.display = match ? "" : "none";
    });

    // Hide year sections that have no visible rows
    yearSections.forEach(function (section) {
      const visible = section.querySelectorAll('.blog-post-row:not([style*="display: none"])');
      // Recount more reliably: count visible directly
      let count = 0;
      section.querySelectorAll(".blog-post-row").forEach(function (r) {
        if (r.style.display !== "none") count++;
      });
      section.style.display = count === 0 ? "none" : "";
    });

    const url = new URL(window.location);
    if (topic === "all") {
      url.searchParams.delete("topic");
    } else {
      url.searchParams.set("topic", topic);
    }
    window.history.replaceState({}, "", url);
  }

  chips.forEach(function (c) {
    c.addEventListener("click", function () { setActive(c.dataset.topic); });
  });

  const params = new URLSearchParams(window.location.search);
  const initial = params.get("topic");
  if (initial && ["ensemble", "adhs", "softdev"].indexOf(initial) > -1) {
    setActive(initial);
  }
})();

// =============================================================================
// email-elements.js
// Two custom elements for bot-resistant email contact rendering.
//
// <jt-email-protected>
//   For Footer / About / Talks. Uses interaction-gate + ≥150 ms time-gate
//   before assembling the address from base64 fragments. Static source
//   carries only opaque base64 strings in data attributes; the <noscript>
//   slot must NOT leak address parts.
//
// <jt-email-readable>
//   For Impressum. CSS-assembles `user@domain` from inline custom properties
//   on a light-DOM .email-static span. JS replicates the assembly in shadow
//   DOM so screen-readers and copy-paste behave predictably; the light-DOM
//   span is the no-JS fallback (§5 DDG requires legibility without JS).
//   No mailto: link — Impressumspflicht requires legibility, not clickability.
// =============================================================================

(function () {
  if (typeof window === "undefined" || !window.customElements) return;

  var loadedAt = (window.performance && performance.now) ? performance.now() : Date.now();
  var TIME_GATE_MS = 150;
  var REVEAL_EVENTS = ["pointermove", "keydown", "touchstart", "scroll", "focusin"];

  // ---- <jt-email-protected> -------------------------------------------------

  function safeAtob(s) {
    try { return window.atob(s); } catch (e) { return ""; }
  }

  var EmailProtected = function () {
    return Reflect.construct(HTMLElement, [], EmailProtected);
  };
  EmailProtected.prototype = Object.create(HTMLElement.prototype);
  EmailProtected.prototype.constructor = EmailProtected;
  Object.setPrototypeOf(EmailProtected, HTMLElement);

  EmailProtected.prototype.connectedCallback = function () {
    if (this._initialized) return;
    this._initialized = true;

    var userB64 = this.getAttribute("user") || "";
    var domainB64 = this.getAttribute("domain") || "";

    var shadow = this.attachShadow({ mode: "open" });

    var style = document.createElement("style");
    style.textContent =
      ":host { display: inline-block; }" +
      "button, a { font: inherit; color: inherit; background: none; border: 0; padding: 0; cursor: pointer; text-decoration: none; }" +
      "a { color: var(--accent, currentColor); }" +
      "a:hover { text-decoration: underline; }";
    shadow.appendChild(style);

    var btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = "E-Mail anzeigen →";
    btn.setAttribute(
      "aria-label",
      "E-Mail-Adresse anzeigen — wird nach einer kurzen Verzögerung sichtbar"
    );
    shadow.appendChild(btn);

    var self = this;
    var revealed = false;

    function reveal() {
      if (revealed) return;
      var now = (window.performance && performance.now) ? performance.now() : Date.now();
      if (now - loadedAt < TIME_GATE_MS) return;
      revealed = true;
      detachListeners();

      var user = safeAtob(userB64);
      var domain = safeAtob(domainB64);
      if (!user || !domain) {
        btn.textContent = "E-Mail nicht verfügbar";
        btn.disabled = true;
        return;
      }
      var address = user + "@" + domain;

      var a = document.createElement("a");
      a.href = "mailto:" + address;
      a.textContent = address + " →";
      a.setAttribute("aria-label", "E-Mail an " + user + " at " + domain.replace(/\./g, " punkt "));

      shadow.replaceChild(a, btn);
      a.focus({ preventScroll: true });
    }

    function onClick(e) {
      // Explicit user click on the placeholder also counts as interaction;
      // bypass time-gate after the load-time delay to avoid surprising users.
      e.preventDefault();
      var now = (window.performance && performance.now) ? performance.now() : Date.now();
      if (now - loadedAt < TIME_GATE_MS) {
        // Defer reveal until the gate elapses.
        setTimeout(reveal, TIME_GATE_MS - (now - loadedAt));
        return;
      }
      reveal();
    }

    function attachListeners() {
      REVEAL_EVENTS.forEach(function (evt) {
        window.addEventListener(evt, reveal, { capture: true, passive: true });
      });
      btn.addEventListener("click", onClick);
    }

    function detachListeners() {
      REVEAL_EVENTS.forEach(function (evt) {
        window.removeEventListener(evt, reveal, { capture: true, passive: true });
      });
    }

    attachListeners();
    self._cleanup = detachListeners;
  };

  EmailProtected.prototype.disconnectedCallback = function () {
    if (this._cleanup) this._cleanup();
  };

  if (!window.customElements.get("jt-email-protected")) {
    window.customElements.define("jt-email-protected", EmailProtected);
  }

  // ---- <jt-email-readable> --------------------------------------------------

  var EmailReadable = function () {
    return Reflect.construct(HTMLElement, [], EmailReadable);
  };
  EmailReadable.prototype = Object.create(HTMLElement.prototype);
  EmailReadable.prototype.constructor = EmailReadable;
  Object.setPrototypeOf(EmailReadable, HTMLElement);

  EmailReadable.prototype.connectedCallback = function () {
    if (this._initialized) return;
    this._initialized = true;

    var user = this.getAttribute("user") || "";
    var domain = this.getAttribute("domain") || "";
    if (!user || !domain) return;

    var shadow = this.attachShadow({ mode: "open" });

    var style = document.createElement("style");
    style.textContent =
      ":host { display: inline; }" +
      ".addr { color: inherit; }" +
      ".addr::before { content: var(--u) \"@\" var(--d); }";
    shadow.appendChild(style);

    var span = document.createElement("span");
    span.className = "addr";
    span.style.setProperty("--u", "'" + user + "'");
    span.style.setProperty("--d", "'" + domain + "'");
    span.setAttribute(
      "aria-label",
      "E-Mail: " + user + " at " + domain.replace(/\./g, " punkt ")
    );
    shadow.appendChild(span);

    // The light-DOM fallback span is automatically hidden because shadow
    // content replaces the light-DOM children (no <slot> declared).
  };

  if (!window.customElements.get("jt-email-readable")) {
    window.customElements.define("jt-email-readable", EmailReadable);
  }
})();

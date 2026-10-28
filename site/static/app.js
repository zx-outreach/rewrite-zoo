// Page logic for the ZX Rewrite Zoo: search & filters, rule page controls and downloads.
(function () {
  "use strict";

  function readJSON(id) {
    const n = document.getElementById(id);
    return n ? JSON.parse(n.textContent) : null;
  }

  function mathify(root) {
    if (!window.renderMathInElement) return;
    window.renderMathInElement(root, {
      delimiters: [{ left: "$$", right: "$$", display: true }, { left: "$", right: "$", display: false }],
      throwOnError: false,
    });
  }

  const ASCII = { "π": "pi", "α": "alpha", "β": "beta", "γ": "gamma", "θ": "theta", "–": "-", "—": "-" };
  function norm(s) {
    s = (s || "").toLowerCase();
    let out = s;
    for (const k in ASCII) out = out.split(k).join(" " + ASCII[k] + " ");
    return s + " " + out.normalize("NFD").replace(/[̀-ͯ]/g, "");
  }

  // ------------------------------------------------------------------------------------------
  // Index page: thumbnails, search and filters

  function initIndex() {
    const entries = readJSON("index-data") || [];
    const fragOrder = readJSON("fragment-order") || [];
    const byId = {};
    entries.forEach((e) => (byId[e.id] = e));
    document.querySelectorAll("[data-thumb]").forEach((t) => {
      const e = byId[t.dataset.thumb];
      if (e) t.appendChild(ZXView.thumbnail(e.lhs, e.rhs, { scale: 36, hboxes: e.hboxes, scalar: e.scalarText, dots: true }));
    });
    const search = document.getElementById("search");
    if (!search) return;
    if (!fragOrder.length) return;
    const groupNames = {};
    document.querySelectorAll(".group-section").forEach((s) => {
      groupNames[s.dataset.group] = s.querySelector("h2 a").textContent;
    });
    entries.forEach((e) => {
      e.hay = norm([e.name, (e.aliases || []).join(" "), (e.alt_names || []).join(" "), e.summary, (e.tags || []).join(" "), groupNames[e.group], e.cite, e.calculus].join(" "));
    });
    const state = { q: "", calculus: new Set(), fragment: new Set(), cumulative: false };
    const params = new URLSearchParams(location.search);
    if (params.get("q")) { state.q = params.get("q"); search.value = state.q; }

    function matches(e) {
      if (state.calculus.size && !state.calculus.has(e.calculus)) return false;
      if (state.fragment.size) {
        if (state.cumulative) {
          const maxSel = Math.max(...[...state.fragment].map((f) => fragOrder.indexOf(f)));
          if (fragOrder.indexOf(e.fragment) > maxSel) return false;
        } else if (!state.fragment.has(e.fragment)) return false;
      }
      const words = state.q.trim().toLowerCase().split(/\s+/).filter(Boolean);
      return words.every((w) => e.hay.includes(w));
    }

    function apply() {
      let shown = 0;
      document.querySelectorAll(".card").forEach((c) => {
        const ok = matches(byId[c.dataset.id]);
        c.hidden = !ok;
        if (ok) shown++;
      });
      document.querySelectorAll(".group-section").forEach((s) => {
        s.hidden = !s.querySelector(".card:not([hidden])");
      });
      document.getElementById("no-results").hidden = shown > 0;
      syncTocWithFilter();
      const filtered = state.q || state.calculus.size || state.fragment.size;
      document.getElementById("result-count").textContent = filtered ? `${shown} of ${entries.length} rules` : "";
    }

    search.addEventListener("input", () => {
      state.q = search.value;
      const u = new URL(location.href);
      if (state.q) u.searchParams.set("q", state.q); else u.searchParams.delete("q");
      history.replaceState(null, "", u);
      apply();
    });
    document.querySelectorAll(".chips").forEach((group) => {
      const key = group.dataset.filter;
      group.querySelectorAll(".chip").forEach((chip) => {
        chip.addEventListener("click", () => {
          const v = chip.dataset.value;
          const on = chip.getAttribute("aria-pressed") !== "true";
          chip.setAttribute("aria-pressed", on);
          if (on) state[key].add(v); else state[key].delete(v);
          apply();
        });
      });
    });
    const cum = document.getElementById("frag-cumulative");
    cum.addEventListener("change", () => { state.cumulative = cum.checked; apply(); });
    apply();
  }

  // ------------------------------------------------------------------------------------------
  // Group page: static equations

  function initAlternatives() {
    const alts = readJSON("alt-data") || [];
    const byId = {};
    alts.forEach((e) => (byId[e.id] = e));
    document.querySelectorAll("[data-alt-eq]").forEach((c) => {
      const e = byId[c.dataset.altEq];
      if (e) ZXView.equation(c, e.lhs, e.rhs, { scale: 36, hboxes: e.hboxes, scalarRight: e.scalar, dots: true });
    });
  }

  function initGroup() {
    const entries = readJSON("index-data") || [];
    const byId = {};
    entries.forEach((e) => (byId[e.id] = e));
    document.querySelectorAll("[data-static-eq]").forEach((c) => {
      const e = byId[c.dataset.staticEq];
      if (e) ZXView.equation(c, e.lhs, e.rhs, { scale: 40, hboxes: e.hboxes, scalarRight: e.scalar, interactive: true, dots: true });
    });
  }

  // ------------------------------------------------------------------------------------------
  // Rule page

  function download(name, text, mime) {
    const blob = new Blob([text], { type: mime || "text/plain" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = name;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 500);
  }

  function initRule() {
    const data = readJSON("rule-data");
    if (!data) return;
    let variants = data.variants;
    const cache = {};
    const arity = data.arity;  // null, or {params: {n: {label, min, max}}, values: {n: 2}, files: {key: file}}
    if (arity) cache[arity.defaultKey] = variants;
    const [v0, s0, c0] = data.defaultKey.split("|");
    const state = {
      view: v0, symmetry: s0, colour: c0 === "1", swap: false, scalarLeft: data.scalarSide === "lhs",
      values: arity ? Object.assign({}, arity.values) : {}, generic: true,
    };
    const has = (view, sym, col) => !!variants[`${view}|${sym}|${col ? 1 : 0}`];
    const panel = document.getElementById("diagram-panel");
    const eqEl = document.getElementById("equation");
    const note = document.getElementById("variant-note");
    const optColour = document.getElementById("opt-colour");
    const optSwap = document.getElementById("opt-swap");
    const optScalar = document.getElementById("opt-scalar");
    const arityBox = document.getElementById("arity-controls");

    // restore state from the URL hash (e.g. #graph-like,adjoint,colour,swap,n=3)
    const hash = decodeURIComponent(location.hash.slice(1)).split(",");
    for (const vw of ["two-colour", "gh", "graph-like"]) if (hash.includes(vw) && has(vw, "id", false)) state.view = vw;
    for (const s of ["conj", "transpose", "adjoint"]) if (hash.includes(s)) state.symmetry = s;
    if (hash.includes("colour")) state.colour = true;
    if (hash.includes("swap")) state.swap = true;
    if (arity) for (const h of hash) {
      const m = /^(\w+)=(\d+)$/.exec(h);
      if (m && m[1] in arity.params) { state.values[m[1]] = +m[2]; state.generic = false; }
    }

    const instKey = () => Object.keys(state.values).sort().map((k) => `${k}=${state.values[k]}`).join(",");

    function current() {
      return variants[`${state.view}|${state.symmetry}|${state.colour ? 1 : 0}`] || variants[data.defaultKey];
    }

    async function loadInstance() {
      const key = instKey();
      if (!cache[key]) {
        try {
          const res = await fetch("instances/" + arity.files[key]);
          cache[key] = await res.json();
        } catch (e) {
          note.textContent = "Could not load this instance (the site must be served over http).";
          return;
        }
      }
      variants = cache[key];
      render();
    }

    if (arity && arityBox) {
      arityBox.hidden = false;
      const sel = {};
      for (const [k, spec] of Object.entries(arity.params)) {
        const lab = document.createElement("label");
        lab.className = "arity-param";
        lab.innerHTML = `<span>${spec.label || k}</span>`;
        const s = document.createElement("select");
        s.setAttribute("aria-label", `number of ${spec.label || k}`);
        for (let i = spec.min; i <= spec.max; i++) {
          const o = document.createElement("option");
          o.value = i; o.textContent = i;
          s.appendChild(o);
        }
        s.value = state.values[k];
        s.addEventListener("change", () => { state.values[k] = +s.value; state.generic = false; gen.checked = false; loadInstance(); });
        lab.appendChild(s);
        arityBox.appendChild(lab);
        sel[k] = s;
      }
      const gl = document.createElement("label");
      gl.className = "check";
      const gen = document.createElement("input");
      gen.type = "checkbox"; gen.checked = state.generic;
      gen.addEventListener("change", () => {
        state.generic = gen.checked;
        if (state.generic) { state.values = Object.assign({}, arity.values); for (const k in sel) sel[k].value = state.values[k]; loadInstance(); }
        else render();
      });
      gl.appendChild(gen);
      gl.appendChild(document.createTextNode(" any number (⋯)"));
      arityBox.appendChild(gl);
    }

    // drawn-only rules and the circuit side of circuit rules cannot be exported to PyZX/ZXLive
    const ex = data.exports || { lhsJson: true, rhsJson: true, zxr: true };
    const exportOk = (kind) => {
      if (kind === "zxr") return ex.zxr;
      if (kind === "lhsJson") return state.swap ? ex.rhsJson : ex.lhsJson;
      if (kind === "rhsJson") return state.swap ? ex.lhsJson : ex.rhsJson;
      return true;
    };

    function render() {
      const v = current();
      panel.querySelectorAll("[data-dl]").forEach((b) => { b.hidden = !exportOk(b.dataset.dl); });
      panel.querySelectorAll('[data-control="view"] button').forEach((b) => {
        b.setAttribute("aria-pressed", b.dataset.value === state.view);
        b.disabled = !has(b.dataset.value, "id", false);
        if (b.disabled && b.dataset.value === "graph-like" && has("gh", "id", false))
          b.title = "Not available: in graph-like form both sides of this rule become the same diagram";
      });
      panel.querySelectorAll('[data-control="symmetry"] button').forEach((b) => {
        b.setAttribute("aria-pressed", b.dataset.value === state.symmetry);
        b.disabled = !has(state.view, b.dataset.value, state.colour);
        if (b.disabled) b.title = "Not available: the complex conjugate of a symbolic label cannot be represented";
      });
      const colourOk = has(state.view, state.symmetry, true);
      optColour.disabled = !colourOk;
      optColour.parentElement.classList.toggle("disabled", !colourOk);
      optColour.checked = state.colour;
      optSwap.checked = state.swap;
      const canMove = v.scalarKnown && !v.scalarZero && (v.scalar || v.invScalar);
      optScalar.disabled = !canMove;
      optScalar.parentElement.classList.toggle("disabled", !canMove);
      optScalar.checked = state.scalarLeft && canMove;

      // equation: as stated LHS = s RHS; swapped: RHS = (1/s) LHS
      const L = state.swap ? v.rhs : v.lhs;
      const R = state.swap ? v.lhs : v.rhs;
      const sRight = state.swap ? v.invScalar : v.scalar;
      const sLeft = state.swap ? v.scalar : v.invScalar;
      const left = canMove && state.scalarLeft;
      ZXView.equation(eqEl, L, R, {
        interactive: true, hboxes: v.view === "two-colour", dots: arity && state.generic,
        scalarLeft: left ? sLeft : "", scalarRight: left ? "" : sRight,
      });
      const bits = [];
      if (!v.scalarKnown) bits.push("Equality holds up to a non-zero scalar.");
      if (arity && state.generic) bits.push("Holds for any number of legs; select a number above to see a specific instance.");
      bits.push(v.curated ? "This version is drawn by hand." : "This version is generated automatically.");
      if (data.checked === false) bits.push("This rule is not checked.");
      else if (v.samples) bits.push(`Verified at ${v.samples} parameter value${v.samples === 1 ? "" : "s"}.`);
      bits.push("Drag the spiders to rearrange the diagram.");
      note.textContent = bits.join(" ");
      const tags = [state.view !== v0 ? state.view : "", state.symmetry !== "id" ? state.symmetry : "",
        state.colour ? "colour" : "", state.swap ? "swap" : ""];
      if (arity && !state.generic) for (const k of Object.keys(state.values).sort()) tags.push(`${k}=${state.values[k]}`);
      const t = tags.filter(Boolean);
      history.replaceState(null, "", t.length ? "#" + t.join(",") : location.pathname + location.search);
    }

    panel.querySelectorAll('[data-control="view"] button').forEach((b) => b.addEventListener("click", () => {
      state.view = b.dataset.value;
      if (!has(state.view, state.symmetry, state.colour)) state.colour = false;
      render();
    }));
    panel.querySelectorAll('[data-control="symmetry"] button').forEach((b) => b.addEventListener("click", () => {
      state.symmetry = b.dataset.value; render();
    }));
    optColour.addEventListener("change", () => { state.colour = optColour.checked; render(); });
    optSwap.addEventListener("change", () => { state.swap = optSwap.checked; render(); });
    optScalar.addEventListener("change", () => { state.scalarLeft = optScalar.checked; render(); });

    function suffix() {
      const parts = [];
      if (state.view !== v0) parts.push(state.view);
      if (state.symmetry !== "id") parts.push(state.symmetry);
      if (state.colour) parts.push("colour-swapped");
      if (state.swap) parts.push("reversed");
      if (arity && !state.generic) parts.push(instKey().replace(/,/g, "-").replace(/=/g, ""));
      return parts.length ? "-" + parts.join("-") : "";
    }

    function zxr(v, sw) {
      // ZXLive rule file: the scalar goes into the scalar of the right-hand side
      const L = JSON.parse(sw ? v.rhsJson : v.lhsJson), R = JSON.parse(sw ? v.lhsJson : v.rhsJson);
      const sc = v.zxrScalar[sw];
      let desc = data.summary;
      if (sc) R.scalar = sc;
      else if (v.scalarKnown && (sw ? v.invScalar : v.scalar)) desc += " (Holds up to a scalar that depends on the parameters.)";
      return JSON.stringify({ lhs_graph: JSON.stringify(L), rhs_graph: JSON.stringify(R), name: data.name, description: desc });
    }

    function content(kind) {
      const v = current();
      const sw = state.swap ? 1 : 0;
      const hb = v.view === "two-colour";
      const dots = !!(arity && state.generic);
      const L = sw ? v.rhs : v.lhs, R = sw ? v.lhs : v.rhs;
      switch (kind) {
        case "tikzEq": {
          const canMove = v.scalarKnown && !v.scalarZero;
          const leftSide = canMove && state.scalarLeft;
          const tex = leftSide ? (sw ? v.scalar : v.invScalar) : (sw ? v.invScalar : v.scalar);
          return [ZXTikz.equation(L, R, tex, leftSide ? "lhs" : "rhs", hb, dots), ".tikz"];
        }
        case "tikzLhs": return [ZXTikz.diagram(L, hb, dots), "-lhs.tikz"];
        case "tikzRhs": return [ZXTikz.diagram(R, hb, dots), "-rhs.tikz"];
        case "lhsJson": return [sw ? v.rhsJson : v.lhsJson, "-lhs.json"];
        case "rhsJson": return [sw ? v.lhsJson : v.rhsJson, "-rhs.json"];
        case "zxr": return [zxr(v, sw), ".zxr"];
      }
      return ["", ""];
    }

    panel.querySelectorAll("[data-dl]").forEach((b) => b.addEventListener("click", () => {
      const [text, ext] = content(b.dataset.dl);
      download(data.id + suffix() + ext, text, ext.endsWith("json") || ext === ".zxr" ? "application/json" : "text/plain");
    }));
    panel.querySelectorAll("[data-copy]").forEach((b) => b.addEventListener("click", async () => {
      const [text] = content(b.dataset.copy);
      try {
        await navigator.clipboard.writeText(text);
        const old = b.textContent; b.textContent = "Copied!";
        setTimeout(() => (b.textContent = old), 1200);
      } catch (e) { download(data.id + suffix() + ".tikz", text); }
    }));
    if (arity && !state.generic) loadInstance(); else render();
  }

  // table of contents: collapsed on small screens, highlights the section in view, and hides
  // categories that the current search/filter leaves empty
  function initToc() {
    const box = document.querySelector(".toc-box");
    if (!box) return;
    if (window.matchMedia("(max-width: 900px)").matches) box.open = false;
    const links = {};
    document.querySelectorAll("[data-toc]").forEach((a) => (links[a.dataset.toc] = a));
    // clicking an entry scrolls smoothly (and quickly) to the section, leaving its title visible below
    // the sticky header and the sticky search/filter bar
    document.querySelectorAll('.toc a[href^="#"]').forEach((a) => a.addEventListener("click", (ev) => {
      const target = document.getElementById(a.getAttribute("href").slice(1));
      if (!target) return;
      ev.preventDefault();
      let offset = 12;
      for (const sel of [".site-header", ".filters"]) {
        const el = document.querySelector(sel);
        if (el && getComputedStyle(el).position === "sticky") offset += el.getBoundingClientRect().height;
      }
      smoothScrollTo(target.getBoundingClientRect().top + window.scrollY - offset);
      history.replaceState(null, "", a.getAttribute("href"));
      if (window.matchMedia("(max-width: 900px)").matches) box.open = false;
    }));
    const sections = document.querySelectorAll(".group-section");
    if (!sections.length || !("IntersectionObserver" in window)) return;
    const visible = new Set();
    const obs = new IntersectionObserver((entries) => {
      for (const en of entries) {
        if (en.isIntersecting) visible.add(en.target.dataset.group); else visible.delete(en.target.dataset.group);
      }
      const first = [...sections].find((s) => visible.has(s.dataset.group) && !s.hidden);
      Object.values(links).forEach((a) => a.classList.remove("active"));
      if (first && links[first.dataset.group]) links[first.dataset.group].classList.add("active");
    }, { rootMargin: "-160px 0px -55% 0px" });
    sections.forEach((s) => obs.observe(s));
  }

  function smoothScrollTo(y, duration = 350) {
    const start = window.scrollY, dist = Math.max(0, y) - start;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches || Math.abs(dist) < 2) {
      window.scrollTo(0, start + dist);
      return;
    }
    const t0 = performance.now();
    const ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
    function step(now) {
      const t = Math.min(1, (now - t0) / duration);
      window.scrollTo(0, start + dist * ease(t));
      if (t < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  function syncTocWithFilter() {
    document.querySelectorAll(".group-section").forEach((s) => {
      const li = document.querySelector(`[data-toc-item="${s.dataset.group}"]`);
      if (li) li.hidden = s.hidden;
    });
  }

  function init() {
    mathify(document.querySelector("main"));
    if (document.body.classList.contains("page-index")) initIndex();
    initToc();
    if (document.body.classList.contains("page-group")) initGroup();
    if (document.body.classList.contains("page-completeness")) initIndex();
    if (document.body.classList.contains("page-rule")) { initRule(); initAlternatives(); }
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();

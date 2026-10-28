// ZX diagram viewer for the ZX Rewrite Zoo.
// Inspired by the d3 viewer of PyZX (zx_viewer.js, Apache 2.0, Kissinger & van de Wetering):
// draws a PyZX-style graph ({nodes: [{id, x: row, y: qubit, t: type, label}], edges: [[s, t, type]]})
// as SVG, with book-style spiders, and lets the user drag spiders around.
(function () {
  "use strict";
  const SVGNS = "http://www.w3.org/2000/svg";
  const T = { BOUNDARY: 0, Z: 1, X: 2, H: 3, W_IN: 4, W_OUT: 5, ZBOX: 6, SYM: 99 };
  const E = { SIMPLE: 1, HAD: 2 };
  const CLASS = { 0: "boundary", 1: "z", 2: "x", 3: "h", 4: "win", 5: "w", 6: "zbox", 99: "sym" };

  function el(name, attrs, parent) {
    const e = document.createElementNS(SVGNS, name);
    if (attrs) for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }

  function textWidth(s) {
    // rough width of a label at 12.5px; good enough for sizing node pills
    let w = 0;
    for (const ch of s) w += /[ilj1.,'\/|]/.test(ch) ? 4 : (/[mwMWπαβ]/.test(ch) ? 9 : 7.2);
    return w;
  }

  // a label like "w_1+w_{i}" with proper subscripts (for edge weights)
  function setSubscripts(textEl, s) {
    const re = /_\{([^}]*)\}|_([A-Za-z0-9]+)/g;
    let last = 0, m;
    while ((m = re.exec(s))) {
      if (m.index > last) el("tspan", {}, textEl).textContent = s.slice(last, m.index);
      const sub = el("tspan", { "baseline-shift": "sub", "font-size": "75%" }, textEl);
      sub.textContent = m[1] !== undefined ? m[1] : m[2];
      last = re.lastIndex;
    }
    if (last < s.length) el("tspan", {}, textEl).textContent = s.slice(last);
  }

  function nodeSize(n) {
    const lab = n.label || "";
    switch (n.t) {
      case T.Z: case T.X:
        return lab ? { w: Math.max(20, textWidth(lab) + 12), h: 20 } : { w: 14, h: 14 };
      case T.H: return lab ? { w: Math.max(14, textWidth(lab) + 10), h: 17 } : { w: 12, h: 12 };
      case T.ZBOX: return { w: Math.max(18, textWidth(lab) + 10), h: 18 };
      case T.W_OUT: return { w: 16, h: 16 };
      case T.W_IN: return { w: 5, h: 5 };
      case T.SYM: return symSize(n);
      default: return { w: 0, h: 0 };
    }
  }

  // Generators that PyZX does not have (drawn only; stored as DUMMY vertices with a "symbol")
  function symSize(n) {
    const txt = n.text || "";
    switch (n.sym) {
      case "gate": case "box": return { w: Math.max(20, textWidth(txt) + 10), h: 20 };
      case "ctrl": return { w: 8, h: 8 };
      case "targ": return { w: 16, h: 16 };
      case "swap": return { w: 10, h: 10 };
      case "triangle": return { w: 16, h: 16 };
      case "star": return { w: 14, h: 14 };
      case "crossing": return { w: 0, h: 0 };
      default: return { w: 14, h: 14 };
    }
  }

  function drawSym(g, n) {
    const s = symSize(n), txt = n.text || "";
    switch (n.sym) {
      case "gate": case "box":
        el("rect", { x: -s.w / 2, y: -s.h / 2, width: s.w, height: s.h, rx: n.sym === "box" ? 2 : 1, class: "body sym-box" }, g);
        if (txt) { const t = el("text", { "text-anchor": "middle", "dominant-baseline": "central", y: 0.5 }, g); t.textContent = txt; }
        return;
      case "ctrl":
        el("circle", { r: 4, class: "body sym-dot" }, g);
        return;
      case "targ":
        el("circle", { r: 8, class: "body sym-targ" }, g);
        el("path", { d: "M -8 0 L 8 0 M 0 -8 L 0 8", class: "sym-line" }, g);
        return;
      case "swap":
        el("path", { d: "M -5 -5 L 5 5 M -5 5 L 5 -5", class: "sym-line thick" }, g);
        return;
      case "triangle": {
        // isosceles, so that its direction is clear; default: pointing right
        const rot = (n.rot || 0) * Math.PI / 180;
        const base = [[10, 0], [-7, 7.5], [-7, -7.5]];
        const pts = base.map(([x, y]) => [x * Math.cos(rot) - y * Math.sin(rot), x * Math.sin(rot) + y * Math.cos(rot)]);
        const tri = el("polygon", { points: pts.map((p) => p.join(",")).join(" "), class: "body sym-box" }, g);
        if (n.colour) tri.style.fill = n.colour;
        if (txt) { const t = el("text", { "text-anchor": "start", "dominant-baseline": "central", x: 9, y: -12, class: "sym-caption" }, g); t.textContent = txt; }
        return;
      }
      case "star":
        { const t = el("text", { "text-anchor": "middle", "dominant-baseline": "central", class: "sym-star" }, g); t.textContent = "★"; }
        return;
      case "crossing":
        // a fermionic crossing (four legs) is drawn as a small grey circle; with two legs it is an invisible joint
        if (n.deg === 4) el("circle", { r: 7, class: "sym-fswap" }, g);
        return;
      default:
        el("rect", { x: -7, y: -7, width: 14, height: 14, class: "body sym-box" }, g);
    }
  }

  function drawNode(g, n, nodes, nbrs) {
    if (n.t === T.SYM) { n.deg = (nbrs[n.id] || []).length; g.setAttribute("class", "zx-node sym"); drawSym(g, n); return; }
    const cls = CLASS[n.t] || "z";
    g.setAttribute("class", "zx-node " + cls);
    const s = nodeSize(n);
    const lab = n.label || "";
    if (n.t === T.BOUNDARY) {
      el("circle", { r: 6, class: "body" }, g);
      return;
    }
    if (n.t === T.Z || n.t === T.X) {
      if (lab) el("rect", { x: -s.w / 2, y: -s.h / 2, width: s.w, height: s.h, rx: s.h / 2, class: "body" }, g);
      else el("circle", { r: s.w / 2, class: "body" }, g);
    } else if (n.t === T.H || n.t === T.ZBOX) {
      el("rect", { x: -s.w / 2, y: -s.h / 2, width: s.w, height: s.h, rx: 1.5, class: "body" }, g);
    } else if (n.t === T.W_OUT) {
      // triangle whose tip points to the W-input dot
      let ang = Math.PI; // default: tip pointing left
      const inp = (nbrs[n.id] || []).map((i) => nodes[i]).find((m) => m && m.t === T.W_IN);
      if (inp) ang = Math.atan2(inp.py - n.py, inp.px - n.px);
      const r = 9;
      const pts = [0, 2.0944, -2.0944].map((d) => [Math.cos(ang + d) * r, Math.sin(ang + d) * r]);
      el("polygon", { points: pts.map((p) => p.join(",")).join(" "), class: "body" }, g);
      return;
    } else if (n.t === T.W_IN) {
      el("circle", { r: 2.6, class: "body" }, g);
      return;
    }
    if (lab) {
      const t = el("text", { "text-anchor": "middle", "dominant-baseline": "central", y: 0.5 }, g);
      t.textContent = lab;
    }
  }

  function layout(diagram, S, pad) {
    const nodes = {};
    let minx = Infinity, miny = Infinity;
    for (const n of diagram.nodes) { minx = Math.min(minx, n.x); miny = Math.min(miny, n.y); }
    if (!isFinite(minx)) { minx = 0; miny = 0; }
    for (const n of diagram.nodes) {
      nodes[n.id] = Object.assign({}, n, { px: (n.x - minx) * S + pad, py: (n.y - miny) * S + pad });
    }
    return nodes;
  }

  function edgeGeometry(diagram, nodes) {
    // assign each edge its index among parallel edges / self-loops
    const groups = {};
    const geo = [];
    diagram.edges.forEach((e, i) => {
      const [a, b] = e;
      const key = a < b ? a + "-" + b : b + "-" + a;
      (groups[key] = groups[key] || []).push(i);
    });
    diagram.edges.forEach((e, i) => {
      const [a, b] = e;
      const key = a < b ? a + "-" + b : b + "-" + a;
      const grp = groups[key];
      geo[i] = { index: grp.indexOf(i), count: grp.length, flip: a > b };
    });
    return geo;
  }

  function pathFor(e, g, nodes) {
    const A = nodes[e[0]], B = nodes[e[1]];
    if (e[0] === e[1]) {
      const k = 1 + g.index;
      const h = 26 + 10 * k, w = 14 + 6 * k;
      const d = `M ${A.px} ${A.py} C ${A.px - w} ${A.py - h}, ${A.px + w} ${A.py - h}, ${A.px} ${A.py}`;
      return { d, mid: [A.px, A.py - 0.75 * h] };
    }
    if (g.count === 1) {
      return { d: `M ${A.px} ${A.py} L ${B.px} ${B.py}`, mid: [(A.px + B.px) / 2, (A.py + B.py) / 2] };
    }
    const dx = B.px - A.px, dy = B.py - A.py;
    const len = Math.hypot(dx, dy) || 1;
    let off = (g.index - (g.count - 1) / 2) * Math.min(26, len * 0.45);
    if (g.flip) off = -off;
    const cx = (A.px + B.px) / 2 - (dy / len) * off * 2, cy = (A.py + B.py) / 2 + (dx / len) * off * 2;
    const mid = [0.25 * A.px + 0.5 * cx + 0.25 * B.px, 0.25 * A.py + 0.5 * cy + 0.25 * B.py];
    return { d: `M ${A.px} ${A.py} Q ${cx} ${cy}, ${B.px} ${B.py}`, mid };
  }

  /**
   * Draw a diagram into a fresh <svg>. Options:
   *   scale: pixels per unit (default 44), hboxes: draw Hadamard edges as yellow boxes,
   *   interactive: allow dragging spiders.
   */
  function draw(diagram, opts) {
    opts = opts || {};
    if (!diagram.nodes.length) {
      // the empty diagram (scalar 1): a dashed placeholder box
      const svg = el("svg", { class: "zx-diagram", viewBox: "0 0 36 36", width: 36, height: 36, role: "img" });
      el("title", {}, svg).textContent = "the empty diagram";
      el("rect", { x: 4, y: 4, width: 28, height: 28, rx: 3, class: "zx-empty" }, svg);
      return svg;
    }
    const S = opts.scale || 44, pad = 26;
    const nodes = layout(diagram, S, pad);
    const nbrs = {};
    for (const e of diagram.edges) {
      (nbrs[e[0]] = nbrs[e[0]] || []).push(e[1]);
      (nbrs[e[1]] = nbrs[e[1]] || []).push(e[0]);
    }
    const svg = el("svg", { class: "zx-diagram" + (opts.interactive ? " interactive" : ""), role: "img" });
    if (opts.title) el("title", {}, svg).textContent = opts.title;
    const root = el("g", {}, svg);
    const edgeLayer = el("g", { class: "edges" }, root);
    const boxLayer = el("g", { class: "hboxes" }, root);
    const nodeLayer = el("g", { class: "nodes" }, root);
    const geo = edgeGeometry(diagram, nodes);
    const deg = {};
    for (const e of diagram.edges) { deg[e[0]] = (deg[e[0]] || 0) + 1; deg[e[1]] = (deg[e[1]] || 0) + 1; }
    const isWay = (id) => nodes[id] && nodes[id].t === T.BOUNDARY && deg[id] === 2;
    const ways = [];
    for (const id in nodes) {
      if (!isWay(+id)) continue;
      const es = diagram.edges.filter((e) => e[0] === +id || e[1] === +id);
      const ends = es.map((e) => (e[0] === +id ? e[1] : e[0]));
      const had = es.some((e) => e[2] === E.HAD);
      ways.push({ id: +id, a: ends[0], b: ends[1], had, p: el("path", { class: "zx-edge" + (had ? " had" : "") }, edgeLayer) });
    }
    const paths = diagram.edges.filter((e) => !isWay(e[0]) && !isWay(e[1])).map((e) => {
      const had = e[2] === E.HAD;
      const ann = e[3] || {};
      const p = el("path", { class: "zx-edge" + (had && !opts.hboxes ? " had" : "") + (ann.ff ? " faultfree" : "") }, edgeLayer);
      const box = had && opts.hboxes ? el("rect", { class: "zx-hbox", width: 11, height: 11, rx: 1 }, boxLayer) : null;
      let wl = null;
      if (ann.w) { wl = el("text", { class: "zx-weight", "text-anchor": "middle", "dominant-baseline": "central" }, boxLayer); setSubscripts(wl, ann.w); }
      return { e, p, box, wl };
    });
    const nodeEls = {};
    for (const id in nodes) {
      const n = nodes[id];
      const g = el("g", {}, nodeLayer);
      drawNode(g, n, nodes, nbrs);
      nodeEls[id] = g;
    }
    function update() {
      for (const w of ways) {
        const A = nodes[w.a], W = nodes[w.id], B = nodes[w.b];
        if (A && B) w.p.setAttribute("d", `M ${A.px} ${A.py} Q ${W.px} ${W.py}, ${B.px} ${B.py}`);
      }
      paths.forEach(({ e, p, box, wl }, i) => {
        const { d, mid } = pathFor(e, geo[diagram.edges.indexOf(e)], nodes);
        p.setAttribute("d", d);
        if (box) { box.setAttribute("x", mid[0] - 5.5); box.setAttribute("y", mid[1] - 5.5); }
        if (wl) {
          // put the weight next to the edge, on its normal
          const A = nodes[e[0]], B = nodes[e[1]];
          const dx = B.px - A.px, dy = B.py - A.py, ln = Math.hypot(dx, dy) || 1;
          wl.setAttribute("x", mid[0] - dy / ln * 10); wl.setAttribute("y", mid[1] + dx / ln * 10);
        }
      });
      for (const id in nodes) nodeEls[id].setAttribute("transform", `translate(${nodes[id].px},${nodes[id].py})`);
    }
    update();
    // size: from node extents (plus room for self-loops)
    let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    // dots between the repeated parts of a rule with an arbitrary number of legs
    if (opts.dots && diagram.dots && diagram.dots.length) {
      let minx = Infinity, miny = Infinity;
      for (const n of diagram.nodes) { minx = Math.min(minx, n.x); miny = Math.min(miny, n.y); }
      for (const [x, y, ox, oy] of diagram.dots) {
        const px = (x - minx) * S + pad, py = (y - miny) * S + pad;
        const ang = Math.atan2(oy, ox) * 180 / Math.PI;
        const t = el("text", { class: "zx-dots", "text-anchor": "middle", "dominant-baseline": "central",
          transform: `translate(${px},${py}) rotate(${ang})` }, root);
        t.textContent = "⋯";
        x0 = Math.min(x0, px - 8); x1 = Math.max(x1, px + 8); y0 = Math.min(y0, py - 8); y1 = Math.max(y1, py + 8);
      }
    }
    for (const id in nodes) {
      const n = nodes[id], s = nodeSize(n);
      x0 = Math.min(x0, n.px - s.w / 2); x1 = Math.max(x1, n.px + s.w / 2);
      y0 = Math.min(y0, n.py - s.h / 2); y1 = Math.max(y1, n.py + s.h / 2);
    }
    diagram.edges.forEach((e, i) => {
      if (e[0] === e[1]) { const n = nodes[e[0]]; y0 = Math.min(y0, n.py - 30 - 10 * (geo[i].index + 1)); }
      else if (geo[i].count > 1) { y0 -= 4; y1 += 4; }
    });
    if (!isFinite(x0)) { x0 = 0; y0 = 0; x1 = 10; y1 = 10; }
    const m = 8;
    const vb = [x0 - m, y0 - m, x1 - x0 + 2 * m, y1 - y0 + 2 * m];
    svg.setAttribute("viewBox", vb.join(" "));
    svg.setAttribute("width", vb[2]);
    svg.setAttribute("height", vb[3]);
    if (opts.interactive && window.d3) {
      for (const id in nodes) {
        if (nodes[id].t === T.BOUNDARY) continue;
        d3.select(nodeEls[id]).call(d3.drag()
          .on("start", function () { this.classList.add("dragging"); })
          .on("drag", function (ev) {
            const n = nodes[id];
            n.px += ev.dx; n.py += ev.dy;
            // keep W input dots attached to their triangle
            if (n.t === T.W_OUT) for (const j of nbrs[id] || []) if (nodes[j].t === T.W_IN) { nodes[j].px += ev.dx; nodes[j].py += ev.dy; }
            update();
          })
          .on("end", function () { this.classList.remove("dragging"); }));
      }
    }
    return svg;
  }

  function renderTex(target, tex) {
    if (!tex) return;
    if (window.katex) {
      try { window.katex.render(tex, target, { throwOnError: false }); return; } catch (e) { /* fall through */ }
    }
    target.textContent = tex;
  }

  /** LHS = (scalar) RHS, as a row of elements in `container`. */
  function equation(container, lhs, rhs, opts) {
    opts = opts || {};
    container.innerHTML = "";
    const mk = (cls) => { const d = document.createElement("div"); d.className = cls; container.appendChild(d); return d; };
    const left = mk("side lhs");
    if (opts.scalarLeft) left.appendChild(scalarSpan(opts.scalarLeft));
    left.appendChild(draw(lhs, Object.assign({}, opts, { title: "left-hand side" })));
    const eq = mk("eq"); eq.textContent = "=";
    const right = mk("side rhs");
    if (opts.scalarRight) right.appendChild(scalarSpan(opts.scalarRight));
    right.appendChild(draw(rhs, Object.assign({}, opts, { title: "right-hand side" })));
  }

  function scalarSpan(tex) {
    const s = document.createElement("span");
    s.className = "scalar";
    renderTex(s, tex);
    return s;
  }

  /** A single compact SVG with lhs = rhs (used for thumbnails). */
  function thumbnail(lhs, rhs, opts) {
    const wrap = document.createElement("div");
    wrap.className = "thumb-eq";
    const a = draw(lhs, opts), b = draw(rhs, opts);
    const H = Math.max(+a.getAttribute("height"), +b.getAttribute("height"));
    const sw = opts.scalar ? Math.max(24, textWidth(opts.scalar) + 10) : 0;
    const W = +a.getAttribute("width") + +b.getAttribute("width") + 34 + sw;
    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, width: W, height: H, class: "zx-diagram", "aria-hidden": "true" });
    const place = (s, x) => {
      const g = el("g", { transform: `translate(${x},${(H - +s.getAttribute("height")) / 2})` }, svg);
      const vb = s.getAttribute("viewBox").split(" ").map(Number);
      const inner = el("g", { transform: `translate(${-vb[0]},${-vb[1]})` }, g);
      while (s.firstChild) inner.appendChild(s.firstChild);
    };
    place(a, 0);
    let x = +a.getAttribute("width");
    const t = el("text", { x: x + 17, y: H / 2, "text-anchor": "middle", "dominant-baseline": "central", class: "thumb-eqsign" }, svg);
    t.textContent = "=";
    x += 34;
    if (opts.scalar) {
      const st = el("text", { x: x + sw / 2, y: H / 2, "text-anchor": "middle", "dominant-baseline": "central", class: "thumb-scalar" }, svg);
      st.textContent = opts.scalar;
      x += sw;
    }
    place(b, x);
    return svg;
  }

  window.ZXView = { draw, equation, thumbnail, renderTex };
})();

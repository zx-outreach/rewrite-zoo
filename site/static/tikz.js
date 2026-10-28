// TikZiT export of diagrams in the viewer format, mirroring zxrewrites/export.py.
// Styles are those of zx-rewrites.tikzstyles (the styles of "Picturing Quantum Software").
(function () {
  "use strict";
  const T = { BOUNDARY: 0, Z: 1, X: 2, H: 3, W_IN: 4, W_OUT: 5, ZBOX: 6, SYM: 99 };
  const SYMBOL_STYLES = { gate: "gate", box: "box", ctrl: "cnot ctrl", targ: "cnot targ", swap: "swap x",
    triangle: "triangle", star: "star", crossing: "none" };

  function num(x) {
    const r = Math.round(x * 1000) / 1000;
    return Object.is(r, -0) ? "0" : String(r);
  }

  class Writer {
    constructor() { this.nodes = []; this.edges = []; this.n = 0; }
    node(style, x, y, label) {
      const i = this.n++;
      this.nodes.push(`\t\t\\node [style=${style}] (${i}) at (${num(x)}, ${num(y)}) {${label ? "$" + label + "$" : ""}};`);
      return i;
    }
    text(x, y, text) {
      const i = this.n++;
      this.nodes.push(`\t\t\\node [style=none] (${i}) at (${num(x)}, ${num(y)}) {${text}};`);
      return i;
    }
    edge(a, b, style, opts) {
      const st = [style ? `style=${style}` : "", opts || ""].filter(Boolean).join(", ");
      this.edges.push(st ? `\t\t\\draw [${st}] (${a}) to (${b});` : `\t\t\\draw (${a}) to (${b});`);
    }
    style(d, n) {
      switch (n.t) {
        case T.BOUNDARY: return "none";
        case T.Z: return n.tex ? "Z phase dot" : "Z dot";
        case T.X: return n.tex ? "X phase dot" : "X dot";
        case T.H: return "hadamard";
        case T.W_IN: return "W input";
        case T.ZBOX: return "Z box";
        case T.SYM: {
          let st = SYMBOL_STYLES[n.sym] || "box";
          if (n.sym === "crossing" && d.edges.filter((e) => e[0] === n.id || e[1] === n.id).length === 4) st = "fermionic crossing";
          if (n.sym === "triangle" && n.rot) st += `, rotate=${-n.rot}`;
          return st;
        }
        case T.W_OUT: {
          let st = "W triangle";
          for (const e of d.edges) {
            const o = e[0] === n.id ? e[1] : e[1] === n.id ? e[0] : null;
            const m = o === null ? null : d.nodes.find((k) => k.id === o);
            if (m && m.t === T.W_IN) {
              const ang = Math.atan2(-(m.y - n.y), m.x - n.x) * 180 / Math.PI;
              st += `, shape border rotate=${((Math.round(ang - 90) % 360) + 360) % 360}`;
              break;
            }
          }
          return st;
        }
      }
      return "none";
    }
    add(d, dx, dy, hboxes) {
      const ids = {}, pos = {};
      for (const n of d.nodes) {
        const lab = n.t === T.SYM ? (n.texText || "") : n.tex;
        ids[n.id] = this.node(this.style(d, n), n.x + dx, dy - n.y, lab);
        pos[n.id] = [n.x + dx, dy - n.y];
      }
      // boundaries with two neighbours are invisible way points of one smooth wire
      const deg = {};
      for (const e of d.edges) { deg[e[0]] = (deg[e[0]] || 0) + 1; deg[e[1]] = (deg[e[1]] || 0) + 1; }
      const ways = new Set(d.nodes.filter((n) => n.t === T.BOUNDARY && deg[n.id] === 2).map((n) => n.id));
      for (const w of ways) {
        const es = d.edges.filter((e) => e[0] === w || e[1] === w);
        const ends = es.map((e) => (e[0] === w ? e[1] : e[0]));
        const had = es.some((e) => e[2] === 2);
        this.edges.push(`\t\t\\draw ${had ? "[style=hadamard edge] " : ""}(${ids[ends[0]]}) .. controls (${ids[w]}) .. (${ids[ends[1]]});`);
      }
      const groups = new Map();
      for (const e of d.edges) {
        if (ways.has(e[0]) || ways.has(e[1])) continue;
        const k = Math.min(e[0], e[1]) + "-" + Math.max(e[0], e[1]);
        if (!groups.has(k)) groups.set(k, []);
        groups.get(k).push(e);
      }
      for (const es of groups.values()) {
        es.forEach((e, k) => {
          const [s, t, et] = e, had = et === 2;
          if (s === t) {
            const size = 0.8 + 0.4 * k;
            if (had && hboxes) {
              const hb = this.node("hadamard", pos[s][0], pos[s][1] + size, "");
              this.edge(ids[s], hb, null, "out=150, in=180");
              this.edge(hb, ids[s], null, "out=0, in=30");
            } else {
              const r = 1 + 0.4 * k;
              this.edges.push(`\t\t\\draw ${had ? "[style=hadamard edge] " : ""}(${ids[s]}) .. controls +(${125 + 10 * k}:${r}) and +(${55 - 10 * k}:${r}) .. (${ids[s]});`);
            }
            return;
          }
          const n = es.length;
          const bend = n > 1 ? (k - (n - 1) / 2) * 40 : 0;
          const bendOpt = bend ? (bend > 0 ? `bend left=${num(bend)}` : `bend right=${num(-bend)}`) : "";
          if (had && hboxes) {
            const [x0, y0] = pos[s], [x1, y1] = pos[t];
            let mx = (x0 + x1) / 2, my = (y0 + y1) / 2;
            if (bend) {
              const ln = Math.hypot(x1 - x0, y1 - y0) || 1;
              const off = Math.tan((bend * Math.PI / 180) / 2) * ln / 2;
              mx -= (y1 - y0) / ln * off; my += (x1 - x0) / ln * off;
            }
            const hb = this.node("hadamard", mx, my, "");
            const half = bend ? (bend > 0 ? `bend left=${num(bend / 2)}` : `bend right=${num(-bend / 2)}`) : "";
            this.edge(ids[s], hb, null, half);
            this.edge(hb, ids[t], null, half);
          } else {
            const ann = e[3] || {};
            const style = had ? "hadamard edge" : (ann.ff ? "fault free edge" : null);
            if (ann.w) {
              const st = [style ? `style=${style}` : "", bendOpt].filter(Boolean).join(", ");
              this.edges.push(`\t\t\\draw [${st}] (${ids[s]}) to node[edge weight] {$${ann.w}$} (${ids[t]});`);
            } else {
              this.edge(ids[s], ids[t], style, bendOpt);
            }
          }
        });
      }
    }
    dots(d, dx, dy) {
      for (const [x, y, ox, oy] of d.dots || []) {
        const ang = ((Math.round(Math.atan2(-oy, ox) * 180 / Math.PI) % 180) + 180) % 180;
        const i = this.n++;
        this.nodes.push(`\t\t\\node [style=none${ang ? ", rotate=" + ang : ""}] (${i}) at (${num(x + dx)}, ${num(dy - y)}) {$\\cdots$};`);
      }
    }
    render() {
      return "\\begin{tikzpicture}\n\t\\begin{pgfonlayer}{nodelayer}\n" + this.nodes.join("\n") +
        "\n\t\\end{pgfonlayer}\n\t\\begin{pgfonlayer}{edgelayer}\n" + this.edges.join("\n") +
        "\n\t\\end{pgfonlayer}\n\\end{tikzpicture}\n";
    }
  }

  function bbox(d) {
    if (!d.nodes.length) return [0, 0, 0];
    const xs = d.nodes.map((n) => n.x), ys = d.nodes.map((n) => n.y);
    return [Math.min(...xs), Math.max(...xs), (Math.min(...ys) + Math.max(...ys)) / 2];
  }

  /** One diagram, centred on the origin. */
  function diagram(d, hboxes, withDots) {
    const w = new Writer();
    const [x0, x1, yc] = bbox(d);
    w.add(d, -(x0 + x1) / 2, yc, hboxes);
    if (withDots) w.dots(d, -(x0 + x1) / 2, yc);
    return w.render();
  }

  /** lhs = (scalar) rhs, with the equals sign at the origin. */
  function equation(lhs, rhs, scalarTex, side, hboxes, withDots) {
    const w = new Writer();
    const gap = 0.75;
    w.text(0, 0, "$=$");
    const [l0, l1, lc] = bbox(lhs), [r0, r1, rc] = bbox(rhs);
    let right = gap;
    const sw = scalarTex ? 0.5 + 0.06 * scalarTex.length : 0;
    if (scalarTex && side === "lhs") {
      w.text(-gap - (l1 - l0) - 0.25 - sw / 2, 0, "$" + scalarTex + "$");
    } else if (scalarTex) {
      w.text(gap + sw / 2 - 0.25, 0, "$" + scalarTex + "$");
      right = gap + sw;
    }
    w.add(lhs, -gap - l1, lc, hboxes);
    w.add(rhs, right - r0, rc, hboxes);
    if (withDots) { w.dots(lhs, -gap - l1, lc); w.dots(rhs, right - r0, rc); }
    return w.render();
  }

  window.ZXTikz = { diagram, equation };
})();

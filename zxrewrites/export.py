"""Export of rules to tikz (TikZiT format), PyZX JSON, ZXLive rule files and viewer data."""

from __future__ import annotations

import json
from fractions import Fraction
from typing import Any, Dict, List, Optional

from pyzx.graph.base import BaseGraph
from pyzx.symbolic import Poly

from . import graphs
from .graphs import ET, VT, label_of
from .phases import format_phase, var_display

TIKZ_SCALE = 1.0


# ---------------------------------------------------------------------------------------------
# Labels


def poly_label(p: Poly, latex: bool) -> str:
    """Pretty-print a symbolic (complex) label such as a, (a+b)/2 or a⋅b."""
    parts = []
    for coeff, term in sorted(p.terms, key=lambda ct: (len(ct[1].vars), str(ct[1]))):
        names = []
        for var, power in term.vars:
            uni, tex = var_display(var.name)
            nm = tex if latex else uni
            if power != 1:
                nm += ("^{%d}" % power) if latex else f"^{power}"
            names.append(nm)
        body = ("" if latex else "").join(names) if latex else "".join(names)
        c = coeff
        if isinstance(c, complex) and c.imag == 0:
            c = c.real
        c = Fraction(c).limit_denominator(1000) if not isinstance(c, complex) else c
        if not names:
            parts.append((c, graphs.complex_to_str(complex(c))))
            continue
        if c == 1:
            parts.append((1, body))
        elif c == -1:
            parts.append((-1, body))
        elif isinstance(c, Fraction) and c.numerator in (1, -1):
            frac = (r"\frac{%s}{%d}" % (body, c.denominator)) if latex else f"{body}/{c.denominator}"
            parts.append((c, frac))
        else:
            parts.append((c, f"{graphs.complex_to_str(complex(c))}{body}"))
    out = ""
    for i, (c, s) in enumerate(parts):
        neg = (isinstance(c, (Fraction, int, float)) and c < 0)
        s2 = s[1:] if neg and s.startswith("-") else s
        out += ("-" if neg else ("" if i == 0 else "+")) + s2
    return out


def vertex_label(g: BaseGraph, v, latex: bool = False) -> str:
    t = g.type(v)
    if t in (VT.Z, VT.X):
        return format_phase(g.phase(v), latex=latex)
    if t == VT.H_BOX:
        lab = label_of(g, v)
        if lab is None:
            p = g.phase(v)
            if not isinstance(p, Poly) and Fraction(p) % 2 == 1:
                return ""
            # label e^{i p pi}: show it as a phase, like PyZX/ZXLive do
            return format_phase(p, latex=latex, zero="1")
        if isinstance(lab, Poly):
            return poly_label(lab, latex)
        c = complex(lab)
        if abs(c + 1) < 1e-12:
            return ""
        return graphs.complex_to_str(c)
    if t == VT.Z_BOX:
        lab = label_of(g, v)
        if lab is None:
            return "1"
        if isinstance(lab, Poly):
            return poly_label(lab, latex)
        return graphs.complex_to_str(complex(lab))
    return ""


# ---------------------------------------------------------------------------------------------
# Viewer data


def viewer_data(g: BaseGraph) -> Dict[str, Any]:
    nodes = []
    for v in sorted(g.vertices()):
        n = {"id": v, "x": g.row(v), "y": g.qubit(v), "t": int(g.type(v)),
             "label": vertex_label(g, v), "tex": vertex_label(g, v, latex=True)}
        if g.type(v) == VT.DUMMY:
            n["sym"] = g.vdata(v, "symbol", "box")
            n["text"] = g.vdata(v, "text", "")
            n["texText"] = g.vdata(v, "tex", "") or n["text"]
            n["rot"] = g.vdata(v, "rot", 0)
            if g.vdata(v, "colour", None):
                n["colour"] = TRIANGLE_COLOURS.get(g.vdata(v, "colour"), g.vdata(v, "colour"))
        nodes.append(n)
    edges = []
    for e in g.edges():
        s, t = g.edge_st(e)
        item = [s, t, int(g.edge_type(e))]
        ann = edge_annotation(g, e)
        if ann:
            item.append(ann)
        edges.append(item)
    return {"nodes": nodes, "edges": edges}


def edge_annotation(g: BaseGraph, e) -> Dict[str, Any]:
    """Annotations used by fault-equivalent rewrites: an edge weight and fault-free edges."""
    ann = {}
    try:
        w = g.edata(e, "weight", None)
        ff = g.edata(e, "faultfree", None)
    except Exception:
        return ann
    if w not in (None, ""):
        ann["w"] = str(w)
    if ff:
        ann["ff"] = True
    return ann


# ---------------------------------------------------------------------------------------------
# TikZ


def _num(x: float) -> str:
    x = round(float(x) * TIKZ_SCALE, 3)
    return str(int(x)) if x == int(x) else f"{x:g}"


def _style(g: BaseGraph, v, label: str) -> str:
    t = g.type(v)
    if t == VT.BOUNDARY:
        return "none"
    if t == VT.Z:
        return "Z phase dot" if label else "Z dot"
    if t == VT.X:
        return "X phase dot" if label else "X dot"
    if t == VT.H_BOX:
        return "hadamard"
    if t == VT.W_OUTPUT:
        return "W triangle"
    if t == VT.W_INPUT:
        return "W input"
    if t == VT.Z_BOX:
        return "Z box"
    if t == VT.DUMMY:
        sym = g.vdata(v, "symbol", "box")
        if sym == "crossing" and g.vertex_degree(v) == 4:
            return "fermionic crossing"
        return SYMBOL_STYLES.get(sym, "box")
    return "none"


TRIANGLE_COLOURS = {"yellow": "#ffff82", "red": "#e8a5a5", "green": "#d8f8d8", "white": "#ffffff"}

# TikZ styles (in zx-rewrites.tikzstyles) of generators that are only drawn
SYMBOL_STYLES = {"gate": "gate", "box": "box", "ctrl": "cnot ctrl", "targ": "cnot targ", "swap": "swap x",
                 "triangle": "triangle", "star": "star", "crossing": "none"}


class _TikzWriter:
    def __init__(self):
        self.nodes: List[str] = []
        self.edges: List[str] = []
        self.n = 0

    def node(self, style: str, x: float, y: float, label: str = "") -> int:
        i = self.n
        self.n += 1
        lab = f"${label}$" if label else ""
        self.nodes.append(f"\t\t\\node [style={style}] ({i}) at ({_num(x)}, {_num(y)}) {{{lab}}};")
        return i

    def text(self, x: float, y: float, text: str) -> int:
        i = self.n
        self.n += 1
        self.nodes.append(f"\t\t\\node [style=none] ({i}) at ({_num(x)}, {_num(y)}) {{{text}}};")
        return i

    def edge(self, a: int, b: int, style: Optional[str] = None, opts: str = ""):
        st = ", ".join(x for x in (f"style={style}" if style else "", opts) if x)
        self.edges.append(f"\t\t\\draw [{st}] ({a}) to ({b});" if st else f"\t\t\\draw ({a}) to ({b});")

    def add_graph(self, g: BaseGraph, dx: float = 0.0, hadamard_boxes: bool = False, dy: float = 0.0) -> None:
        ids = {}
        for v in sorted(g.vertices()):
            lab = vertex_label(g, v, latex=True)
            style = _style(g, v, lab)
            if g.type(v) == VT.W_OUTPUT:
                # point the triangle's tip at its W-input dot (the style's default points left)
                import math
                ins = [n for n in g.neighbors(v) if g.type(n) == VT.W_INPUT]
                if ins:
                    n = ins[0]
                    ang = math.degrees(math.atan2(-(g.qubit(n) - g.qubit(v)), g.row(n) - g.row(v)))
                    style += f", shape border rotate={round(ang - 90) % 360}"
            if g.type(v) == VT.DUMMY:
                lab = g.vdata(v, "tex", "") or g.vdata(v, "text", "")
                rot = g.vdata(v, "rot", 0)
                if rot and g.vdata(v, "symbol", "") == "triangle":
                    style += f", rotate={-rot}"
                col = g.vdata(v, "colour", None)
                if col and g.vdata(v, "symbol", "") == "triangle":
                    style += {"yellow": ", fill={rgb,255: red,255; green,255; blue,130}",
                              "red": ", fill={rgb,255: red,232; green,165; blue,165}",
                              "green": ", fill={rgb,255: red,216; green,248; blue,216}"}.get(col, "")
                if lab and g.vdata(v, "symbol", "") == "gate" and "$" not in lab:
                    lab = "\\mathrm{" + lab + "}" if lab.isalpha() else lab
            ids[v] = self.node(style, g.row(v) + dx, dy - g.qubit(v), lab)
        # boundaries with two neighbours are invisible way points: one smooth wire through them
        deg = {v: g.vertex_degree(v) for v in g.vertices()}
        ways = [v for v in g.vertices() if g.type(v) == VT.BOUNDARY and deg[v] == 2]
        for w in ways:
            ends = []
            had = False
            for e in g.incident_edges(w):
                a, b = g.edge_st(e)
                ends.append(b if a == w else a)
                had = had or g.edge_type(e) == ET.HADAMARD
            if len(ends) == 2:
                st = "[style=hadamard edge] " if had else ""
                self.edges.append(f"\t\t\\draw {st}({ids[ends[0]]}) .. controls ({ids[w]}) .. ({ids[ends[1]]});")
        groups: Dict[tuple, list] = {}
        for e in g.edges():
            s, t = g.edge_st(e)
            if s in ways or t in ways:
                continue
            groups.setdefault((min(s, t), max(s, t)), []).append(e)
        for (s, t), es in groups.items():
            n = len(es)
            for k, e in enumerate(es):
                had = g.edge_type(e) == ET.HADAMARD
                if s == t:
                    # self-loop: a teardrop above the node (through an H-box if needed)
                    size = 0.8 + 0.4 * k
                    if had and hadamard_boxes:
                        hb = self.node("hadamard", g.row(s) + dx, dy - g.qubit(s) + size)
                        self.edge(ids[s], hb, None, "out=150, in=180")
                        self.edge(hb, ids[s], None, "out=0, in=30")
                    else:
                        st = "[style=hadamard edge] " if had else ""
                        r = 1.0 + 0.4 * k
                        self.edges.append(f"\t\t\\draw {st}({ids[s]}) .. controls +({125 + 10 * k}:{r:g}) "
                                          f"and +({55 - 10 * k}:{r:g}) .. ({ids[s]});")
                    continue
                bend = (k - (n - 1) / 2) * 40 if n > 1 else 0
                bend_opt = (f"bend left={bend:g}" if bend > 0 else f"bend right={-bend:g}") if bend else ""
                if had and hadamard_boxes:
                    # put the box on the (possibly bent) edge
                    x0, y0, x1, y1 = g.row(s) + dx, dy - g.qubit(s), g.row(t) + dx, dy - g.qubit(t)
                    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
                    if bend:
                        import math
                        ln = math.hypot(x1 - x0, y1 - y0) or 1
                        off = math.tan(math.radians(bend) / 2) * ln / 2
                        mx, my = mx - (y1 - y0) / ln * off, my + (x1 - x0) / ln * off
                    hb = self.node("hadamard", mx, my)
                    half = f"bend left={bend / 2:g}" if bend > 0 else (f"bend right={-bend / 2:g}" if bend else "")
                    self.edge(ids[s], hb, None, half)
                    self.edge(hb, ids[t], None, half)
                else:
                    ann = edge_annotation(g, e)
                    style = "hadamard edge" if had else ("fault free edge" if ann.get("ff") else None)
                    if ann.get("w"):
                        lab = ann["w"]
                        self.edges.append(f"\t\t\\draw [{', '.join(x for x in (f'style={style}' if style else '', bend_opt) if x)}] "
                                          f"({ids[s]}) to node[edge weight] {{${lab}$}} ({ids[t]});")
                    else:
                        self.edge(ids[s], ids[t], style, bend_opt)

    def add_dots(self, dots, dx: float, dy: float) -> None:
        """Dots between the repeated parts of a rule with an arbitrary number of legs."""
        import math
        for (x, y, ox, oy) in dots or []:
            ang = round(math.degrees(math.atan2(-oy, ox))) % 180
            rot = f", rotate={ang}" if ang else ""
            i = self.n
            self.n += 1
            self.nodes.append(f"\t\t\\node [style=none{rot}] ({i}) at ({_num(x + dx)}, {_num(dy - y)}) {{$\\cdots$}};")

    def render(self) -> str:
        return ("\\begin{tikzpicture}\n\t\\begin{pgfonlayer}{nodelayer}\n" + "\n".join(self.nodes) +
                "\n\t\\end{pgfonlayer}\n\t\\begin{pgfonlayer}{edgelayer}\n" + "\n".join(self.edges) +
                "\n\t\\end{pgfonlayer}\n\\end{tikzpicture}\n")


def _width(g: BaseGraph):
    r0, r1, _, _ = graphs.bbox(g)
    return r0, r1


def _centre(g: BaseGraph):
    r0, r1, q0, q1 = graphs.bbox(g)
    return r0, r1, (q0 + q1) / 2


def tikz(g: BaseGraph, hadamard_boxes: bool = False) -> str:
    """A single diagram, centred on the origin."""
    w = _TikzWriter()
    r0, r1, qc = _centre(g)
    w.add_graph(g, -(r0 + r1) / 2, hadamard_boxes, dy=qc)
    return w.render()


def _scalar_width(tex: str) -> float:
    return 0.5 + 0.06 * len(tex)


def tikz_equation(lhs: BaseGraph, rhs: BaseGraph, scalar_tex: str = "", scalar_side: str = "rhs",
                  hadamard_boxes: bool = False, dots=None) -> str:
    """lhs = (scalar) rhs as a single TikZiT picture, with the equals sign at the origin and both
    sides vertically centred on it."""
    w = _TikzWriter()
    gap = 0.75
    w.text(0, 0, "$=$")
    l0, l1, lc = _centre(lhs)
    r0, r1, rc = _centre(rhs)
    dl, dr = dots or ([], [])
    left, right = gap, gap
    if scalar_tex:
        sw = _scalar_width(scalar_tex)
        if scalar_side == "lhs":
            # the scalar multiplies the left-hand side: it goes in front of the lhs diagram
            w.add_graph(lhs, -gap - l1, hadamard_boxes, dy=lc)
            w.add_dots(dl, -gap - l1, lc)
            w.text(-gap - (l1 - l0) - 0.25 - sw / 2, 0, f"${scalar_tex}$")
            w.add_graph(rhs, gap - r0, hadamard_boxes, dy=rc)
            w.add_dots(dr, gap - r0, rc)
            return w.render()
        w.text(gap + sw / 2 - 0.25, 0, f"${scalar_tex}$")
        right = gap + sw
    w.add_graph(lhs, -left - l1, hadamard_boxes, dy=lc)
    w.add_dots(dl, -left - l1, lc)
    w.add_graph(rhs, right - r0, hadamard_boxes, dy=rc)
    w.add_dots(dr, right - r0, rc)
    return w.render()


# ---------------------------------------------------------------------------------------------
# ZXLive


def zxr(name: str, description: str, lhs: BaseGraph, rhs: BaseGraph) -> str:
    """A ZXLive custom rule file (.zxr)."""
    return json.dumps({"lhs_graph": lhs.to_json(), "rhs_graph": rhs.to_json(),
                       "name": name, "description": description}, ensure_ascii=False)


def check_zxr(text: str, exact: bool) -> None:
    """Load a .zxr file the way ZXLive does (zxlive/custom_rule.py) and run the same checks as
    ZXLive's 'check rule' action. Raises ValueError when ZXLive would reject the rule."""
    import numpy as np
    from pyzx.graph.jsonparser import json_to_graph

    d = json.loads(text)
    sides = []
    for key in ("lhs_graph", "rhs_graph"):
        g = json_to_graph(d[key], "multigraph")
        g.set_auto_simplify(False)
        g.auto_detect_io()
        sides.append(g)
    L, R = sides
    if len(L.inputs()) != len(R.inputs()) or len(L.outputs()) != len(R.outputs()):
        raise ValueError("ZXLive: inputs/outputs of the two sides do not match")
    # (the matrix comparison is skipped for diagrams with many legs: the rule itself is verified anyway,
    # and a 2^n x 2^n matrix for large n does not fit in memory)
    small = len(L.inputs()) + len(L.outputs()) <= 12 and max(L.num_vertices(), R.num_vertices()) <= 25
    if exact and small and not graphs.variables(L) and not graphs.variables(R):
        if not np.allclose(L.to_matrix(), R.to_matrix()):
            raise ValueError("ZXLive: the two sides are not equal (scalar included)")

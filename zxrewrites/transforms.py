"""Generated variants of a rule: colour swap, conjugate, transpose, adjoint and the change of view
between the two-colour presentation and the graph-like (Z-spiders + Hadamard edges) presentation."""

from __future__ import annotations

import cmath
from fractions import Fraction
from typing import Optional

from pyzx.graph.base import BaseGraph
from pyzx.symbolic import Poly, Term

from .graphs import ET, VT, label_of, new_graph, is_standard_hbox

COLOUR_SYMMETRIC_TYPES = {VT.BOUNDARY, VT.Z, VT.X, VT.H_BOX}


def copy(g: BaseGraph) -> BaseGraph:
    h = g.copy()
    h.set_auto_simplify(False)
    return h


# ---------------------------------------------------------------------------------------------
# Phase / label helpers


def negate_phase(p):
    """-p, keeping boolean variables tidy (-aπ = aπ for a ∈ {0,1})."""
    if isinstance(p, Poly):
        terms = []
        for coeff, term in p.terms:
            c = -coeff
            if term.vars and all(v.is_bool for v, _ in term.vars) and isinstance(c, (int, Fraction)):
                c = Fraction(c) % 2
                if c == 0:
                    continue
            elif not term.vars:
                c = Fraction(c) % 2
                if c == 0:
                    continue
            terms.append((c, term))
        return Poly(terms) if terms else Fraction(0)
    if isinstance(p, float):
        return (-p) % 2.0
    return (-Fraction(p)) % 2


def conj_label(lab):
    if lab is None:
        return None
    if isinstance(lab, Poly):
        return lab.conjugate()
    return complex(lab).conjugate()


# ---------------------------------------------------------------------------------------------
# Variants


def colour_swappable(g: BaseGraph) -> bool:
    for v in g.vertices():
        t = g.type(v)
        if t not in COLOUR_SYMMETRIC_TYPES:
            return False
        if t == VT.H_BOX and (g.vertex_degree(v) != 2 or not is_standard_hbox(g, v)):
            return False
    return True


def colour_swap(g: BaseGraph) -> BaseGraph:
    h = copy(g)
    for v in h.vertices():
        if h.type(v) == VT.Z:
            h.set_type(v, VT.X)
        elif h.type(v) == VT.X:
            h.set_type(v, VT.Z)
    return h


def conjugate(g: BaseGraph) -> BaseGraph:
    h = copy(g)
    for v in h.vertices():
        t = h.type(v)
        if t in (VT.Z, VT.X, VT.H_BOX):
            h.set_phase(v, negate_phase(h.phase(v)))
        lab = label_of(h, v)
        if lab is not None:
            h.set_vdata(v, "label", conj_label(lab))
    return h


def transpose(g: BaseGraph) -> BaseGraph:
    """Mirror the diagram left-to-right; inputs become outputs and vice versa."""
    h = copy(g)
    rows = [h.row(v) for v in h.vertices()] or [0]
    lo, hi = min(rows), max(rows)
    for v in h.vertices():
        h.set_row(v, lo + hi - h.row(v))
    h.auto_detect_io()
    return h


def adjoint(g: BaseGraph) -> BaseGraph:
    return transpose(conjugate(g))


# ---------------------------------------------------------------------------------------------
# Views


def toggle_colour(h: BaseGraph, v) -> None:
    """Change the colour of spider v by toggling the type of all its (non-loop) edges."""
    h.set_type(v, VT.X if h.type(v) == VT.Z else VT.Z)
    for e in list(h.incident_edges(v)):
        s, t = h.edge_st(e)
        if s == t:
            continue  # a self-loop passes through two Hadamards
        et = h.edge_type(e)
        data = {k: h.edata(e, k) for k in h.edata_keys(e)}
        h.remove_edge(e)
        ne = h.add_edge((s, t), ET.HADAMARD if et == ET.SIMPLE else ET.SIMPLE)
        for k, val in data.items():  # keep edge annotations (e.g. weights of fault-equivalent rules)
            h.set_edata(ne, k, val)


def to_gh(g: BaseGraph) -> BaseGraph:
    """The 'GH' form: turn every X-spider into a Z-spider by toggling its incident edges between simple
    and Hadamard edges. (Hadamard *gates* in ZX rules are always stored as Hadamard edges.)"""
    h = copy(g)
    for v in [v for v in h.vertices() if h.type(v) == VT.X]:
        toggle_colour(h, v)
    h.auto_detect_io()
    return h


def _add_phase(a, b):
    s = a + b
    if isinstance(s, Poly):
        return s
    return Fraction(s) % 2 if not isinstance(s, float) else s % 2.0


def to_graph_like(g: BaseGraph):
    """Bring a diagram in graph-like form: only Z-spiders, connected to each other only by Hadamard
    edges, no self-loops or parallel edges, every boundary connected by a plain edge to a spider that
    has no other boundary.

    Returns (h, f) where g = f · h as linear maps, with f a sympy number."""
    import sympy as sp

    h = to_gh(g)
    f = sp.Integer(1)
    z = lambda v: h.type(v) == VT.Z

    # 1. fuse spiders connected by plain edges; deal with the self-loops this creates
    changed = True
    while changed:
        changed = False
        for e in list(h.edges()):
            s, t = h.edge_st(e)
            if s != t and z(s) and z(t) and h.edge_type(e) == ET.SIMPLE:
                h.remove_edge(e)
                h.set_phase(s, _add_phase(h.phase(s), h.phase(t)))
                for e2 in list(h.incident_edges(t)):
                    a, b = h.edge_st(e2)
                    other = b if a == t else a
                    if a == b:
                        other = s
                    et = h.edge_type(e2)
                    h.remove_edge(e2)
                    h.add_edge((s, s if other == t else other), et)
                # keep the merged spider in the middle of the two
                h.set_row(s, (h.row(s) + h.row(t)) / 2)
                h.set_qubit(s, (h.qubit(s) + h.qubit(t)) / 2)
                h.remove_vertex(t)
                changed = True
                break
    for v in list(h.vertices()):
        if not z(v):
            continue
        for e in list(h.incident_edges(v)):
            a, b = h.edge_st(e)
            if a != b:
                continue
            if h.edge_type(e) == ET.HADAMARD:
                f *= 1 / sp.sqrt(2)
                h.set_phase(v, _add_phase(h.phase(v), Fraction(1)))
            h.remove_edge(e)

    # 2. parallel Hadamard edges cancel in pairs (Hopf rule)
    pairs = {}
    for e in list(h.edges()):
        s, t = h.edge_st(e)
        if s != t and z(s) and z(t):
            pairs.setdefault((min(s, t), max(s, t)), []).append(e)
    for (s, t), es in pairs.items():
        for e in es[: 2 * (len(es) // 2)]:
            h.remove_edge(e)
        f *= sp.Rational(1, 2) ** (len(es) // 2)

    # 3. boundaries: plain edge to a spider that has no other boundary
    def interp(a, b, frac):
        return (h.row(a) + (h.row(b) - h.row(a)) * frac, h.qubit(a) + (h.qubit(b) - h.qubit(a)) * frac)

    def new_z(pos):
        return h.add_vertex(VT.Z, qubit=round(pos[1], 4), row=round(pos[0], 4))

    seen_boundary_spiders = set()
    for b in sorted(v for v in h.vertices() if h.type(v) == VT.BOUNDARY):
        es = list(h.incident_edges(b))
        if len(es) != 1:
            continue
        e = es[0]
        s, t = h.edge_st(e)
        n = t if s == b else s
        et = h.edge_type(e)
        if z(n) and et == ET.SIMPLE and n not in seen_boundary_spiders:
            seen_boundary_spiders.add(n)
            continue
        h.remove_edge(e)
        if h.type(n) == VT.BOUNDARY:
            # a bare wire (or a Hadamard) between two boundaries
            if et == ET.SIMPLE:
                w1, w2, w3 = (new_z(interp(b, n, x)) for x in (0.25, 0.5, 0.75))
                h.add_edge((b, w1))
                h.add_edge((w1, w2), ET.HADAMARD)
                h.add_edge((w2, w3), ET.HADAMARD)
                h.add_edge((w3, n))
                seen_boundary_spiders.update({w1, w3})
            else:
                w1, w2 = (new_z(interp(b, n, x)) for x in (1 / 3, 2 / 3))
                h.add_edge((b, w1))
                h.add_edge((w1, w2), ET.HADAMARD)
                h.add_edge((w2, n))
                seen_boundary_spiders.update({w1, w2})
            continue
        if et == ET.HADAMARD:
            w = new_z(interp(b, n, 0.5))
            h.add_edge((b, w))
            h.add_edge((w, n), ET.HADAMARD)
            seen_boundary_spiders.add(w)
        else:
            # n already has a boundary: b -- w1 -H- w2 -H- n
            w1, w2 = (new_z(interp(b, n, x)) for x in (1 / 3, 2 / 3))
            h.add_edge((b, w1))
            h.add_edge((w1, w2), ET.HADAMARD)
            h.add_edge((w2, n), ET.HADAMARD)
            seen_boundary_spiders.add(w1)
    h.auto_detect_io()
    return h, f


def same_shape(a: BaseGraph, b: BaseGraph) -> bool:
    """Whether two diagrams are equal up to renaming vertices (respecting vertex types, phases,
    labels, edge types and multiplicities, and the order of the inputs and outputs)."""
    import networkx as nx
    from .phases import format_phase

    def nxg(g):
        G = nx.MultiGraph()
        ins, outs = list(g.inputs()), list(g.outputs())
        for v in g.vertices():
            tag = ("in", ins.index(v)) if v in ins else ("out", outs.index(v)) if v in outs else None
            G.add_node(v, key=(int(g.type(v)), format_phase(g.phase(v)), str(label_of(g, v)), tag))
        for e in g.edges():
            s_, t_ = g.edge_st(e)
            G.add_edge(s_, t_, et=int(g.edge_type(e)))
        return G

    A, B = nxg(a), nxg(b)
    if A.number_of_nodes() != B.number_of_nodes() or A.number_of_edges() != B.number_of_edges():
        return False
    return nx.is_isomorphic(A, B, node_match=lambda x, y: x["key"] == y["key"],
                            edge_match=lambda x, y: sorted(d["et"] for d in x.values()) == sorted(d["et"] for d in y.values()))


def to_two_colour(g: BaseGraph) -> BaseGraph:
    """Recolour spiders greedily to minimise the number of Hadamard edges."""
    h = copy(g)
    changed = True
    while changed:
        changed = False
        for v in sorted(h.vertices()):
            if h.type(v) not in (VT.Z, VT.X):
                continue
            simple = had = 0
            for e in h.incident_edges(v):
                s, t = h.edge_st(e)
                if s == t:
                    continue
                if h.edge_type(e) == ET.HADAMARD:
                    had += 1
                else:
                    simple += 1
            if had > simple:
                toggle_colour(h, v)
                changed = True
    h.auto_detect_io()
    return h

"""Helpers around PyZX graphs: loading/saving JSON, instantiating variables, structural checks."""

from __future__ import annotations

import cmath
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Set

import pyzx as zx
from pyzx.graph.base import BaseGraph
from pyzx.symbolic import Poly
from pyzx.utils import EdgeType, VertexType

from .phases import phase_vars, substitute

VT = VertexType
ET = EdgeType

TYPE_NAMES = {
    VT.BOUNDARY: "boundary", VT.Z: "Z", VT.X: "X", VT.H_BOX: "H",
    VT.W_INPUT: "W_input", VT.W_OUTPUT: "W", VT.Z_BOX: "Z_box",
}


def new_graph() -> BaseGraph:
    g = zx.Graph("multigraph")
    g.set_auto_simplify(False)
    return g


def from_json(js: str | dict) -> BaseGraph:
    if isinstance(js, dict):
        js = json.dumps(js)
    g = zx.graph.jsonparser.json_to_graph(js, "multigraph")
    g.set_auto_simplify(False)
    detect_io(g)
    return g


def detect_io(g: BaseGraph) -> None:
    """Like PyZX's auto_detect_io, but tolerant: for diagrams that are only drawn and not checked
    (e.g. with bare cups), boundaries that are not proper inputs/outputs are simply skipped. A boundary
    vertex with two neighbours is used as an invisible way point for drawing curved wires."""
    try:
        g.auto_detect_io()
        return
    except Exception:
        pass
    ins, outs = [], []
    for v in g.vertices():
        if g.type(v) != VT.BOUNDARY or g.vertex_degree(v) != 1:
            continue
        n = next(iter(g.neighbors(v)))
        if g.row(n) > g.row(v):
            ins.append(v)
        elif g.row(n) < g.row(v):
            outs.append(v)
    g.set_inputs(tuple(sorted(ins, key=g.qubit)))
    g.set_outputs(tuple(sorted(outs, key=g.qubit)))


def load(path: Path) -> BaseGraph:
    return from_json(Path(path).read_text(encoding="utf8"))


def to_dict(g: BaseGraph) -> dict:
    return json.loads(g.to_json())


def dumps(g: BaseGraph) -> str:
    """Stable, diff-friendly JSON serialisation (one vertex / edge per line)."""
    d = to_dict(g)
    verts = d.pop("vertices")
    edges = d.pop("edges")
    head = json.dumps(d, ensure_ascii=False)[:-1]
    vs = ",\n  ".join(json.dumps(v, ensure_ascii=False) for v in verts)
    es = ",\n  ".join(json.dumps(e) for e in edges)
    return f'{head},\n "vertices": [\n  {vs}\n ],\n "edges": [\n  {es}\n ]\n}}\n'


def save(g: BaseGraph, path: Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(dumps(g), encoding="utf8")


def label_of(g: BaseGraph, v) -> Any:
    """The raw label of an H-box or Z-box (complex, Fraction or Poly), or None for a default label."""
    return g.vdata(v, "label", None)


def variables(g: BaseGraph) -> Dict[str, bool]:
    """All free variables in phases and labels, mapped to their is_bool flag."""
    out: Dict[str, bool] = {}
    for v in g.vertices():
        out.update(phase_vars(g.phase(v)))
        lab = label_of(g, v)
        if isinstance(lab, Poly):
            out.update(phase_vars(lab))
    return out


def _eval_poly(p: Poly, values: Dict[str, Any]) -> complex:
    total: complex = 0
    for coeff, term in p.terms:
        val: Any = complex(coeff)
        for var, power in term.vars:
            val *= complex(values[var.name]) ** power
        total += val
    return total


def instantiate(g: BaseGraph, values: Dict[str, Any]) -> BaseGraph:
    """Return a copy of g with all variables replaced by concrete values.

    Phase variables are given in units of pi (as stored in PyZX); label variables are complex numbers.
    """
    h = g.copy()
    for v in list(h.vertices()):
        p = h.phase(v)
        if isinstance(p, Poly):
            h.set_phase(v, substitute(p, values))
        lab = label_of(h, v)
        if isinstance(lab, Poly):
            h.set_vdata(v, "label", _eval_poly(lab, values))
        elif isinstance(lab, Fraction):
            # A label written as a plain number in the JSON
            h.set_vdata(v, "label", complex(float(lab)))
    h.auto_detect_io()
    return h


def tensor(g: BaseGraph):
    """The matrix of a fully concrete diagram, including its scalar (inputs -> outputs).

    PyZX contracts multigraphs naively, column by column, which can need enormous intermediate
    tensors (e.g. for big spider nests). When the diagram has no parallel edges or self-loops it is
    copied to PyZX's simple-graph backend first, so that the smarter contraction strategy is used."""
    h = _as_simple(g) if g.num_vertices() > 20 else None
    if h is not None:
        try:
            return h.to_matrix(preserve_scalar=True)
        except Exception:
            pass
    return g.to_matrix(preserve_scalar=True)


def _as_simple(g: BaseGraph):
    seen = set()
    for e in g.edges():
        s, t = g.edge_st(e)
        key = (min(s, t), max(s, t))
        if s == t or key in seen:
            return None
        seen.add(key)
    if any(g.type(v) not in (VT.BOUNDARY, VT.Z, VT.X, VT.H_BOX, VT.Z_BOX) for v in g.vertices()):
        return None
    h = zx.Graph("simple")
    m = {}
    for v in g.vertices():
        m[v] = h.add_vertex(g.type(v), qubit=g.qubit(v), row=g.row(v), phase=g.phase(v))
        for k in g.vdata_keys(v):
            h.set_vdata(m[v], k, g.vdata(v, k))
    for e in g.edges():
        s, t = g.edge_st(e)
        h.add_edge((m[s], m[t]), g.edge_type(e))
    h.set_inputs(tuple(m[v] for v in g.inputs()))
    h.set_outputs(tuple(m[v] for v in g.outputs()))
    h.scalar = g.scalar.copy()
    return h


def structural_problems(g: BaseGraph) -> List[str]:
    probs = []
    for v in g.vertices():
        t = g.type(v)
        if t == VT.BOUNDARY:
            if g.vertex_degree(v) != 1:
                probs.append(f"boundary vertex {v} has degree {g.vertex_degree(v)} (must be 1)")
                continue
            n = next(iter(g.neighbors(v)))
            if g.row(n) == g.row(v):
                probs.append(f"boundary vertex {v} and its neighbour {n} have the same row; "
                             "cannot tell whether it is an input or an output")
        if t not in TYPE_NAMES:
            probs.append(f"vertex {v} has unsupported type {t}")
    return probs


def boundary_signature(g: BaseGraph):
    return (len(g.inputs()), len(g.outputs()))


def vertex_types(g: BaseGraph) -> Set[int]:
    return {g.type(v) for v in g.vertices()}


def is_standard_hbox(g: BaseGraph, v) -> bool:
    lab = label_of(g, v)
    if lab is None:
        return g.phase(v) == 1
    if isinstance(lab, (complex, float, int)):
        return cmath.isclose(complex(lab), -1)
    return False


def bbox(g: BaseGraph):
    rows = [g.row(v) for v in g.vertices()] or [0]
    qs = [g.qubit(v) for v in g.vertices()] or [0]
    return min(rows), max(rows), min(qs), max(qs)


def complex_to_str(c: complex) -> str:
    c = complex(c)
    if abs(c.imag) < 1e-12:
        r = c.real
        return str(int(r)) if math.isclose(r, round(r)) else f"{r:g}"
    return f"{c.real:g}{c.imag:+g}i"

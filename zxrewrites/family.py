"""Rules that hold for an arbitrary number of legs ("families").

A family rule stores a *template* in lhs.json/rhs.json in which every repeatable part ("unit") appears
exactly once, and describes the units in meta.json:

    "arity": {
      "params": {"n": {"label": "inputs", "min": 0, "max": 4},
                 "m": {"label": "outputs", "min": 0, "max": 4}},
      "lhs": [{"param": "n", "vertices": [0], "offset": [0, 1]},
              {"param": "m", "vertices": [5], "offset": [0, 1]}],
      "rhs": [...]
    }

An instance with n = N is obtained by replacing each unit with parameter n by N copies of it, placed
at  template position + (i - (N-1)/2) * offset  for i = 0..N-1.  Edges are copied as follows:
  * an edge inside a unit is copied inside every copy;
  * an edge between a unit and the rest of the diagram is copied for every copy;
  * an edge between two units with *different* parameters is copied between every pair of copies
    (e.g. the complete bipartite graph of the bialgebra rule);
  * an edge between two units with the *same* parameter connects copy i to copy i;
  * "clique": [[a, b, edge_type], ...] adds an edge between vertex a of copy i and vertex b of copy j
    for all i < j (e.g. the complete graph created by local complementation; edge_type 1 = plain,
    2 = Hadamard);
  * "index_vars": ["alpha"] renames the variable alpha in copy i to alpha{i+1} (α₁, α₂, ...);
  * "bulge": [dx, dy] places the copies on a parabola instead of a straight line (the middle copies
    are displaced by up to (dx, dy)), so that a clique between them is not drawn on collinear nodes.

The default instance shown on the site is given by the rule's "parameters".
"""

from __future__ import annotations

import itertools
from fractions import Fraction
from typing import Any, Dict, List, Tuple

from pyzx.graph.base import BaseGraph
from pyzx.symbolic import Poly, new_var

from . import graphs
from .graphs import ET, VT


def params_of(meta) -> Dict[str, dict]:
    return meta.get("arity", {}).get("params", {})


def is_family(meta) -> bool:
    return bool(params_of(meta))


def ranges(meta) -> Dict[str, List[int]]:
    return {k: list(range(int(v.get("min", 0)), int(v.get("max", 4)) + 1)) for k, v in params_of(meta).items()}


def all_instances(meta) -> List[Dict[str, int]]:
    rs = ranges(meta)
    names = list(rs)
    return [dict(zip(names, combo)) for combo in itertools.product(*(rs[n] for n in names))]


def instance_key(values: Dict[str, int]) -> str:
    return ",".join(f"{k}={v}" for k, v in sorted(values.items()))


def _rename(p, ren: Dict[str, str], registry):
    if not isinstance(p, Poly) or not ren:
        return p
    sub = {}
    for v in p.free_vars():
        if v.name in ren:
            sub[v] = new_var(ren[v.name], v.is_bool, registry)
    return p.substitute(sub) if sub else p


def instantiate(template: BaseGraph, units: List[dict], values: Dict[str, int]):
    """Returns (graph, dots) where dots is a list of (x, y, dx, dy) positions of '⋯' markers
    (one per unit with at least two copies, between its first two copies)."""
    g = graphs.new_graph()
    for name, is_bool in graphs.variables(template).items():
        g.var_registry.set_type(name, is_bool)
    unit_of: Dict[Any, int] = {}
    for ui, u in enumerate(units):
        for v in u["vertices"]:
            if v in unit_of:
                raise ValueError(f"vertex {v} is in two units")
            if v not in template.vertices():
                raise ValueError(f"unit vertex {v} does not exist")
            unit_of[v] = ui
    counts = [int(values[u["param"]]) for u in units]
    # create vertices
    copies: Dict[Any, List[Any]] = {}
    for v in sorted(template.vertices()):
        if v in unit_of:
            ui = unit_of[v]
            u = units[ui]
            N = counts[ui]
            ox, oy = u.get("offset", [0, 1])
            ren_vars = u.get("index_vars", [])
            copies[v] = []
            for i in range(N):
                shift = i - (N - 1) / 2
                half = (N - 1) / 2
                # "bulge": place the copies on a parabola instead of a line, so that complete graphs
                # between the copies are not drawn on collinear nodes
                bx, by = u.get("bulge", [0, 0])
                f = (half * half - shift * shift) / max(half * half, 1) if N > 2 else 0
                ren = {name: f"{name}{i + 1}" for name in ren_vars}
                nv = g.add_vertex(template.type(v), qubit=_r(template.qubit(v) + shift * oy + f * by),
                                  row=_r(template.row(v) + shift * ox + f * bx),
                                  phase=_rename(template.phase(v), ren, g.var_registry))
                for key in template.vdata_keys(v):
                    val = template.vdata(v, key)
                    g.set_vdata(nv, key, _rename(val, ren, g.var_registry) if isinstance(val, Poly) else val)
                copies[v].append(nv)
        else:
            nv = g.add_vertex(template.type(v), qubit=template.qubit(v), row=template.row(v), phase=template.phase(v))
            for key in template.vdata_keys(v):
                g.set_vdata(nv, key, template.vdata(v, key))
            copies[v] = [nv]
    # edges
    for e in template.edges():
        s, t = template.edge_st(e)
        et = template.edge_type(e)
        us, ut = unit_of.get(s), unit_of.get(t)
        if us is not None and ut is not None:
            if us == ut or units[us]["param"] == units[ut]["param"]:
                pairs = list(zip(copies[s], copies[t]))
            else:
                pairs = [(a, b) for a in copies[s] for b in copies[t]]
        else:
            pairs = [(a, b) for a in copies[s] for b in copies[t]]
        data = {k: template.edata(e, k) for k in template.edata_keys(e)}
        for a, b in pairs:
            ne = g.add_edge((a, b), et)
            copy_i = None
            for end, u in ((a, us), (b, ut)):
                if u is not None:
                    vt = s if end in copies[s] else t
                    copy_i = copies[vt].index(end) if end in copies[vt] else copy_i
            for k, val in data.items():
                if isinstance(val, str) and copy_i is not None:
                    # an index i in an annotation (e.g. the weight w_i) becomes the number of the copy
                    import re as _re
                    val = _re.sub(r"_i\b", f"_{copy_i + 1}", val)
                    val = _re.sub(r"_\{i\}", f"_{{{copy_i + 1}}}", val)
                g.set_edata(ne, k, val)
    for ui, u in enumerate(units):
        for a, b, et in u.get("clique", []):
            for i, j in itertools.combinations(range(counts[ui]), 2):
                g.add_edge((copies[a][i], copies[b][j]), ET.HADAMARD if et == 2 else ET.SIMPLE)
    g.auto_detect_io()
    # '⋯' markers
    dots = []
    for ui, u in enumerate(units):
        anchor = u.get("dots_at", u["vertices"][0])
        dx, dy = u.get("offset", [0, 1])
        if counts[ui] >= 2:
            a, b = copies[anchor][0], copies[anchor][1]
            x, y = (g.row(a) + g.row(b)) / 2, (g.qubit(a) + g.qubit(b)) / 2
        elif counts[ui] == 1:
            # a single copy: the dots go where the next copy would be, half an offset further
            a = copies[anchor][0]
            x, y = g.row(a) + dx / 2, g.qubit(a) + dy / 2
        else:
            # no copies: the dots mark the place where copies would appear
            x, y = template.row(anchor), template.qubit(anchor)
        shift = u.get("dots_shift", [0, 0])
        dots.append((x + shift[0], y + shift[1], dx, dy))
    return g, dots


def _r(x):
    x = round(float(x), 4)
    return int(x) if x == int(x) else x


def expand_variables(variables: Dict[str, dict], units: List[dict], values: Dict[str, int]) -> Dict[str, dict]:
    """Declared template variables, with indexed variables (alpha -> alpha1, alpha2, ...) expanded."""
    indexed = {}
    for u in units:
        for name in u.get("index_vars", []):
            indexed[name] = max(indexed.get(name, 0), int(values[u["param"]]))
    out = {}
    for k, v in variables.items():
        if k in indexed:
            for i in range(indexed[k]):
                out[f"{k}{i + 1}"] = v
        else:
            out[k] = v
    return out


def make_instance(rule, values: Dict[str, int]):
    """A copy of a family rule with lhs/rhs replaced by the instance with the given arities."""
    import copy as _copy
    spec = rule.meta["arity"]
    L, dl = instantiate(rule.template_lhs, spec.get("lhs", []), values)
    R, dr = instantiate(rule.template_rhs, spec.get("rhs", []), values)
    r = _copy.copy(rule)
    r.meta = dict(rule.meta)
    r.meta["parameters"] = {**rule.meta.get("parameters", {}), **values}
    r.lhs, r.rhs = L, R
    r.dots_lhs, r.dots_rhs = dl, dr
    r.var_override = expand_variables(rule.template_variables, spec.get("lhs", []) + spec.get("rhs", []), values)
    r.instance_values = dict(values)
    return r


def default_values(meta) -> Dict[str, int]:
    ps = meta.get("parameters", {})
    out = {}
    for k, spec in params_of(meta).items():
        out[k] = int(ps.get(k, spec.get("default", 2)))
    return out

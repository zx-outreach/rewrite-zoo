"""A tiny DSL used to author the initial rule data.

The canonical data are the JSON files in ``rules/<id>/``; these authoring scripts are only a
convenient way to write them (they can equally be drawn in ZXLive and saved as .zxg/.json).
Running an authoring script does not overwrite an existing rule unless ``--force`` is given.

Coordinates: ``x`` is the PyZX *row* (horizontal, left to right), ``y`` is the PyZX *qubit*
(vertical, top to bottom).  Inputs are boundaries whose neighbour lies to their right, outputs are
boundaries whose neighbour lies to their left (this is what ZXLive expects).

Phases are given in units of pi: ``0``, ``"1/2"``, ``Fraction(1, 4)``, ``"alpha"``, ``"-alpha+1/2"``,
``"a"`` (a boolean variable, meaning aπ) ...
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from zxrewrites import graphs  # noqa: E402
from zxrewrites.graphs import ET, VT  # noqa: E402
from zxrewrites.phases import parse_phase  # noqa: E402

RULES_DIR = ROOT / "rules"
FORCE = "--force" in sys.argv
ONLY = [x for a in sys.argv if a.startswith("--only=") for x in a.split("=", 1)[1].split(",")]


class D:
    """A diagram under construction."""

    def __init__(self, bools: str | Iterable[str] = ()):
        if isinstance(bools, str):
            bools = bools.split()
        self.var_types = {b: True for b in bools}
        self.g = graphs.new_graph()
        for b in self.var_types:
            self.g.var_registry.set_type(b, True)

    # --- vertices -------------------------------------------------------------------------
    def _v(self, t, x, y, phase=0):
        p = parse_phase(phase, self.g.var_registry, self.var_types)
        return self.g.add_vertex(t, qubit=y, row=x, phase=p)

    def b(self, x, y):
        """A boundary (input if its neighbour is to the right, output otherwise)."""
        return self._v(VT.BOUNDARY, x, y)

    def z(self, x, y, phase=0):
        return self._v(VT.Z, x, y, phase)

    def x(self, x, y, phase=0):
        return self._v(VT.X, x, y, phase)

    def h(self, x, y, phase=1, label=None):
        """An H-box. By default the standard Hadamard (label -1, i.e. phase π).

        ``phase`` gives label e^{i·phase·π} (PyZX convention); ``label`` gives an arbitrary complex
        number or a symbolic label like "a" or "(a+b)/2" (use ⋅ for products)."""
        v = self._v(VT.H_BOX, x, y, phase if label is None else 0)
        if label is not None:
            if isinstance(label, str):
                from pyzx.graph.jsonparser import string_to_phase
                lab = string_to_phase(label, self.g)
            else:
                lab = complex(label)
            self.g.set_vdata(v, "label", lab)
        return v

    def zbox(self, x, y, label):
        v = self._v(VT.Z_BOX, x, y)
        if isinstance(label, str):
            from pyzx.graph.jsonparser import string_to_phase
            label = string_to_phase(label, self.g)
        else:
            label = complex(label)
        self.g.set_vdata(v, "label", label)
        return v

    def w(self, x, y, input_dir=(-0.35, 0)):
        """A W-spider (black triangle).  Returns (w_out, w_in): attach the single 'input' leg of the W
        to ``w_in`` and the other legs to ``w_out``."""
        wo = self._v(VT.W_OUTPUT, x, y)
        wi = self._v(VT.W_INPUT, x + input_dir[0], y + input_dir[1])
        self.g.add_edge((wi, wo))
        return wo, wi

    def sym(self, x, y, symbol, text="", tex="", rot=0, colour=None):
        """A generator that PyZX does not have, drawn with the given symbol: "triangle" (rot in degrees,
        default pointing right), "box" (e.g. a λ-box, text="λ"), "star", "crossing" (wires just cross),
        or circuit symbols "gate" (text="H"), "ctrl", "targ", "swap". Rules using these are not checked
        (set checked=False and give unchecked_reason)."""
        v = self.g.add_vertex(VT.DUMMY, qubit=y, row=x)
        self.g.set_vdata(v, "symbol", symbol)
        if text:
            self.g.set_vdata(v, "text", text)
        if tex:
            self.g.set_vdata(v, "tex", tex)
        if rot:
            self.g.set_vdata(v, "rot", rot)
        if colour:
            self.g.set_vdata(v, "colour", colour)  # e.g. "yellow" or "red" for triangles
        return v

    def way(self, x, y):
        """An invisible way point: a wire through it is drawn as a smooth curve. Use it to draw cups and
        caps: D.e(D.b(1, 0), D.way(0, 0.5), D.b(1, 1)) is a cup on the right-hand side."""
        return self._v(VT.BOUNDARY, x, y)

    # --- edges ----------------------------------------------------------------------------
    def e(self, *chain):
        """Simple edges along a chain of vertices."""
        for a, c in zip(chain, chain[1:]):
            self.g.add_edge((a, c), ET.SIMPLE)
        return self

    def ann(self, a, b, weight=None, faultfree=False):
        """Annotate the (first) edge between a and b, for fault-equivalent rewrites: an edge weight
        (shown as a label) and/or a fault-free edge (drawn bold purple)."""
        for e in self.g.edges():
            s, t = self.g.edge_st(e)
            if {s, t} == {a, b}:
                if weight is not None:
                    self.g.set_edata(e, "weight", str(weight))
                if faultfree:
                    self.g.set_edata(e, "faultfree", True)
                return self
        raise ValueError(f"no edge between {a} and {b}")

    def he(self, *chain):
        """Hadamard edges along a chain of vertices."""
        for a, c in zip(chain, chain[1:]):
            self.g.add_edge((a, c), ET.HADAMARD)
        return self

    # --- conveniences ---------------------------------------------------------------------
    def ins(self, v, ys: Sequence[float], x: float = 0, h: bool = False):
        """Input boundaries at column x and the given heights, connected to v."""
        out = []
        for y in ys:
            bnd = self.b(x, y)
            (self.he if h else self.e)(bnd, v)
            out.append(bnd)
        return self

    def outs(self, v, ys: Sequence[float], x: float, h: bool = False):
        out = []
        for y in ys:
            bnd = self.b(x, y)
            (self.he if h else self.e)(v, bnd)
            out.append(bnd)
        return self

    def wire(self, y, x0, x1, *path):
        """An input at (x0, y) going through ``path`` to an output at (x1, y)."""
        i = self.b(x0, y)
        o = self.b(x1, y)
        self.e(i, *path, o)
        return i, o


def spread(n: int, center: float = 0, gap: float = 1.0) -> List[float]:
    """n heights spaced by ``gap`` and centred on ``center``."""
    if n == 0:
        return []
    start = center - gap * (n - 1) / 2
    return [round(start + gap * i, 4) for i in range(n)]


def fit_scalar(L, R, variables) -> str:
    """Find the constant c with L = c R (numerically, over samples) and return it as a sympy string.
    Raises if the ratio depends on the variables (then the scalar must be written by hand)."""
    import numpy as np
    import sympy as sp
    from zxrewrites import verify, scalars
    var_specs = {k: ({"domain": v} if isinstance(v, str) else v) for k, v in variables.items()}
    ratio = None
    for vals in verify.sample_values(var_specs):
        A = graphs.tensor(graphs.instantiate(L, vals))
        B = graphs.tensor(graphs.instantiate(R, vals))
        idx = np.unravel_index(np.argmax(np.abs(B)), B.shape)
        c = A[idx] / B[idx]
        if not np.allclose(A, c * B):
            raise ValueError("LHS and RHS are not proportional")
        if ratio is None:
            ratio = c
        elif not np.isclose(ratio, c):
            raise ValueError(f"scalar depends on the variables ({ratio} vs {c} at {vals}); write it by hand")
    return sp.sstr(scalars.from_number(complex(ratio)))


def rule(id: str, *, lhs: D, rhs: D, alt: Optional[tuple] = None, **meta):
    """Write rules/<id>/{meta.json,lhs.json,rhs.json[,alt/...]}."""
    if ONLY and id not in ONLY:
        return
    d = RULES_DIR / id
    if (d / "meta.json").exists() and not FORCE:
        return
    d.mkdir(parents=True, exist_ok=True)
    m: Dict[str, Any] = {"id": id}
    m.update(meta)
    order = ["id", "name", "aliases", "calculus", "fragment", "group", "order", "view", "summary", "description",
             "variables", "parameters", "parameter_notes", "conditions", "checked", "unchecked_reason", "kind", "circuit",
             "scalar", "scalar_side", "source", "also_in",
             "axiom_of", "related", "tags", "notes"]
    m = {k: m[k] for k in order if k in m} | {k: v for k, v in m.items() if k not in order}
    (d / "meta.json").write_text(json.dumps(m, indent=2, ensure_ascii=False) + "\n", encoding="utf8")
    for dd in (lhs, rhs):
        graphs.detect_io(dd.g)
    if m.get("scalar") == "auto":
        m["scalar"] = fit_scalar(lhs.g, rhs.g, m.get("variables", {}))
        m = {k: m[k] for k in order if k in m} | {k: v for k, v in m.items() if k not in order}
        (d / "meta.json").write_text(json.dumps(m, indent=2, ensure_ascii=False) + "\n", encoding="utf8")
    for name, dd in (("lhs", lhs), ("rhs", rhs)):
        graphs.save(dd.g, d / f"{name}.json")
    if alt is not None:
        for name, dd in zip(("lhs", "rhs"), alt):
            graphs.detect_io(dd.g)
            graphs.save(dd.g, d / "alt" / f"{name}.json")
    print("wrote", id)

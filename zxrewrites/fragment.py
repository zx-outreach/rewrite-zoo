"""Infer the smallest fragment a rule lives in.

ZX fragments are nested: phase-free ⊂ Pauli ⊂ Clifford ⊂ Clifford+T ⊂ universal.

* phase-free: Z- and X-spiders with zero phase only (no Hadamards).
* Pauli: phases 0 or π (still no Hadamards).
* Clifford: phases multiples of π/2, Hadamards allowed.
* Clifford+T: phases multiples of π/4.
* universal: anything.

The same hierarchy is used for ZH and ZW rules, by asking which ZX fragment the generators belong to:
a standard H-box is a Hadamard (Clifford) with two legs and Toffoli-type (Clifford+T) with three or
more; a W-spider is Clifford+T; labels that are not phases are universal.
"""

from __future__ import annotations

import cmath
from fractions import Fraction
from typing import Dict, Iterable, Tuple

from pyzx.symbolic import Poly

from .graphs import VT, ET, label_of
from .model import FRAGMENTS, Rule

LEVEL = {f: i for i, f in enumerate(FRAGMENTS)}
DOMAIN_UNIT = {"boolean": Fraction(1), "integer": Fraction(1), "clifford": Fraction(1, 2),
               "clifford+t": Fraction(1, 4)}


def const_level(c: Fraction) -> int:
    c = Fraction(c) % 2
    if c == 0:
        return LEVEL["phase-free"]
    if c == 1:
        return LEVEL["pauli"]
    if (2 * c).denominator == 1:
        return LEVEL["clifford"]
    if (4 * c).denominator == 1:
        return LEVEL["clifford+t"]
    return LEVEL["universal"]


def phase_level(p, domains: Dict[str, str]) -> int:
    if isinstance(p, float):
        return const_level(Fraction(p).limit_denominator(1 << 16)) if p == round(p * 4) / 4 else LEVEL["universal"]
    if not isinstance(p, Poly):
        return const_level(Fraction(p))
    lvl = 0
    const = Fraction(0)
    for coeff, term in p.terms:
        if not term.vars:
            const += Fraction(coeff)
            continue
        if len(term.vars) != 1 or term.vars[0][1] != 1:
            return LEVEL["universal"]
        name = term.vars[0][0].name
        unit = DOMAIN_UNIT.get(domains.get(name, "real"))
        if unit is None:
            return LEVEL["universal"]
        lvl = max(lvl, const_level(Fraction(coeff) * unit))
    return max(lvl, const_level(const))


def hbox_level(g, v, domains) -> int:
    """Smallest ZX fragment containing an (unnormalised) H-box.

    An H-box with label e^{iθ} and n legs is, up to a scalar, a phase polynomial with angle θ/2^(n-1);
    so the standard H-box (θ = π) is in the Pauli fragment with one leg, is a Hadamard (Clifford) with
    two legs, and a (multi-)controlled Z, i.e. Toffoli-type and so Clifford+T, with three or more legs."""
    n = g.vertex_degree(v)
    lab = label_of(g, v)
    if lab is None:
        p = g.phase(v)
    elif isinstance(lab, Poly):
        return LEVEL["universal"]
    else:
        c = complex(lab)
        if abs(c) < 1e-12:
            return LEVEL["phase-free"] if n <= 1 else LEVEL["clifford+t"]
        if abs(abs(c) - 1) > 1e-9:
            return LEVEL["universal"]
        p = Fraction(cmath.phase(c) / cmath.pi).limit_denominator(1 << 12) % 2
    if n == 0:
        return LEVEL["phase-free"]  # just a scalar
    if not isinstance(p, Poly) and Fraction(p) % 2 == 1 and n >= 3:
        return LEVEL["clifford+t"]
    lvl = phase_level(p * Fraction(1, 2 ** (n - 1)), domains)
    return max(lvl, LEVEL["clifford"]) if n >= 2 and lvl > 0 else lvl


def zbox_level(lab, domains) -> int:
    if lab is None:
        return 0
    if isinstance(lab, Poly):
        return LEVEL["universal"]
    c = complex(lab)
    if abs(abs(c) - 1) > 1e-9:
        return LEVEL["universal"]
    return phase_level(Fraction(cmath.phase(c) / cmath.pi).limit_denominator(1 << 12) % 2, domains)


def graph_level(g, calculus: str, domains: Dict[str, str]) -> int:
    """The same hierarchy is used for all calculi, so that e.g. 'phase-free' never contains Hadamards."""
    lvl = 0
    for v in g.vertices():
        t = g.type(v)
        if t in (VT.Z, VT.X):
            lvl = max(lvl, phase_level(g.phase(v), domains))
        elif t == VT.H_BOX:
            lvl = max(lvl, hbox_level(g, v, domains))
        elif t == VT.Z_BOX:
            lvl = max(lvl, zbox_level(label_of(g, v), domains))
        elif t in (VT.W_INPUT, VT.W_OUTPUT):
            lvl = max(lvl, LEVEL["clifford+t"])  # W-spiders can be built from triangles, i.e. Clifford+T
    for e in g.edges():
        if g.edge_type(e) == ET.HADAMARD:
            lvl = max(lvl, LEVEL["clifford"])
    return lvl


def infer_fragment(rule: Rule, lhs=None, rhs=None) -> str:
    domains = {k: v["domain"] for k, v in rule.variables.items()}
    calc = rule.meta.get("calculus", "ZX")
    lhs = lhs if lhs is not None else rule.lhs
    rhs = rhs if rhs is not None else rule.rhs
    lvl = max(graph_level(lhs, calc, domains), graph_level(rhs, calc, domains))
    # A free complex/real variable that only occurs in the scalar also makes the rule universal.
    return FRAGMENTS[lvl]

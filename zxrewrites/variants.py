"""Compute all generated variants of a rule and verify each of them."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import sympy as sp
from pyzx.graph.base import BaseGraph

from . import scalars, transforms, verify
from .model import Rule

SYMMETRIES = ["id", "conj", "transpose", "adjoint"]
SYMMETRY_NAMES = {"id": "as stated", "conj": "conjugate", "transpose": "transpose", "adjoint": "adjoint"}


@dataclass
class Variant:
    key: str
    view: str
    symmetry: str
    colour_swapped: bool
    lhs: BaseGraph
    rhs: BaseGraph
    scalar: Optional[sp.Expr]  # None = only known up to a non-zero scalar
    curated: bool
    result: Optional[verify.VerificationResult] = None


VIEWS = ["two-colour", "gh", "graph-like"]
VIEW_NAMES = {"two-colour": "Two-colour", "gh": "GH", "graph-like": "Graph-like"}


def _views_for(rule: Rule, colour_swapped: bool) -> Dict[str, tuple]:
    """view -> (lhs, rhs, curated, factor) where LHS_view = factor-adjusted: the rule in that view reads
    lhs = (s * factor) rhs."""
    if rule.meta["calculus"] != "ZX":
        return {rule.view: (rule.lhs, rule.rhs, True, sp.Integer(1))} if not colour_swapped else {}
    curated_gl = rule.view == "graph-like"
    if not curated_gl:
        tc = (rule.lhs, rule.rhs, True)
    elif rule.alt_lhs is not None:
        tc = (rule.alt_lhs, rule.alt_rhs, True)
    else:
        tc = (transforms.to_two_colour(rule.lhs), transforms.to_two_colour(rule.rhs), False)
    L, R, cur = tc
    if colour_swapped:
        L, R, cur = transforms.colour_swap(L), transforms.colour_swap(R), False
    views = {"two-colour": (L, R, cur, sp.Integer(1))}
    if curated_gl and not colour_swapped:
        gh = (rule.lhs, rule.rhs, True)
    else:
        gh = (transforms.to_gh(L), transforms.to_gh(R), False)
    views["gh"] = gh + (sp.Integer(1),)
    (gL, fL), (gR, fR) = transforms.to_graph_like(gh[0]), transforms.to_graph_like(gh[1])
    if curated_gl and not colour_swapped and transforms.same_shape(gL, rule.lhs) and transforms.same_shape(gR, rule.rhs):
        views["graph-like"] = (rule.lhs, rule.rhs, True, sp.Integer(1))
    elif not transforms.same_shape(gL, gR):
        # (if both sides become the same diagram the rule is trivial in graph-like form: no view)
        views["graph-like"] = (gL, gR, False, sp.nsimplify(fR / fL))
    return views


def base_views(rule: Rule) -> Dict[str, tuple]:
    """view -> (lhs, rhs, curated) for the rule as stated (no colour swap)."""
    return {k: v[:3] for k, v in _views_for(rule, False).items()}


def rule_scalar(rule: Rule) -> Optional[sp.Expr]:
    if "scalar" not in rule.meta or rule.meta["scalar"] is None:
        return None
    s = scalars.parse_scalar(rule.meta["scalar"], rule.variables, rule.meta.get("parameters", {}))
    return scalars.instance_value(s, rule.meta.get("parameters", {}), rule.variables)


_simp_cache: Dict[str, sp.Expr] = {}


def _simplify(e: sp.Expr) -> sp.Expr:
    k = sp.srepr(e)
    if k not in _simp_cache:
        _simp_cache[k] = sp.simplify(e)
    return _simp_cache[k]


def compute_variants(rule: Rule) -> List[Variant]:
    s0 = rule_scalar(rule)
    params = rule.meta.get("parameters", {})
    out = []
    has_complex_labels = any(spec.get("domain") == "complex" for spec in rule.variables.values())
    swappable = rule.meta["calculus"] == "ZX" and all(transforms.colour_swappable(g) for g in (rule.lhs, rule.rhs))
    for cs in ([False, True] if swappable else [False]):
        for view, (L1, R1, curated, factor) in _views_for(rule, cs).items():
            sv = None if s0 is None else (s0 if factor == 1 else _simplify(s0 * factor))
            for sym in SYMMETRIES:
                if sym in ("conj", "adjoint") and has_complex_labels:
                    # PyZX has no way to write the complex conjugate of a symbolic label
                    continue
                if sym == "id":
                    L, R, s = L1, R1, sv
                elif sym == "conj":
                    L, R = transforms.conjugate(L1), transforms.conjugate(R1)
                    s = None if sv is None else scalars.conjugate(sv, rule.variables, params)
                elif sym == "transpose":
                    L, R, s = transforms.transpose(L1), transforms.transpose(R1), sv
                else:
                    L, R = transforms.adjoint(L1), transforms.adjoint(R1)
                    s = None if sv is None else scalars.conjugate(sv, rule.variables, params)
                key = f"{view}|{sym}|{int(cs)}"
                out.append(Variant(key, view, sym, cs, L, R, s, curated and sym == "id" and not cs))
    return out


def verify_variants(rule: Rule, variants: List[Variant], full: bool = True, n_random: int = verify.N_RANDOM) -> List[str]:
    """Verify the variants; returns a list of error messages. With full=False only the curated
    variants are checked (fast mode)."""
    errors = []
    params = rule.meta.get("parameters", {})
    for i, v in enumerate(variants):
        if not full and not v.curated:
            continue
        v.result = verify.check(v.lhs, v.rhs, v.scalar, rule.variables, params, seed=i, n_random=n_random)
        if not v.result.ok:
            errors.append(f"[{v.key}] " + "; ".join(v.result.messages))
    return errors


# ---------------------------------------------------------------------------------------------
# Rules that are only drawn (not checked), and circuit rules (circuit = s · diagram)


def unchecked_variants(rule: Rule) -> List[Variant]:
    return [Variant(f"{rule.view}|id|0", rule.view, "id", False, rule.lhs, rule.rhs, rule_scalar(rule), True)]


def circuit_variants(rule: Rule) -> List[Variant]:
    """The circuit (lhs) stays as it is; the diagram (rhs) is shown in every view."""
    s0 = rule_scalar(rule)
    R = rule.rhs
    out = [Variant("two-colour|id|0", "two-colour", "id", False, rule.lhs, R, s0, True)]
    if rule.meta["calculus"] == "ZX":
        out.append(Variant("gh|id|0", "gh", "id", False, rule.lhs, transforms.to_gh(R), s0, False))
        gR, fR = transforms.to_graph_like(transforms.to_gh(R))
        s = None if s0 is None else _simplify(s0 * fR)
        out.append(Variant("graph-like|id|0", "graph-like", "id", False, rule.lhs, gR, s, False))
    return out


def verify_circuit(rule: Rule, variants: List[Variant]) -> List[str]:
    import numpy as np
    from . import circuits, graphs
    errors = []
    params = rule.meta.get("parameters", {})
    for v in variants:
        res = verify.VerificationResult()
        for values in verify.sample_values(rule.variables, 0):
            U = circuits.unitary(rule.meta["circuit"], values)
            try:
                D = graphs.tensor(graphs.instantiate(v.rhs, values))
            except Exception as e:
                res.fail(f"could not compute the tensor of the diagram: {e!r}")
                break
            res.samples += 1
            if U.shape != D.shape:
                res.fail(f"the circuit has shape {U.shape} but the diagram {D.shape}")
                break
            s = 1 if v.scalar is None else scalars.evaluate(v.scalar, values, rule.variables, params)
            if v.scalar is None:
                idx = np.unravel_index(np.argmax(np.abs(D)), D.shape)
                s = U[idx] / D[idx]
            if not np.allclose(U, s * D, atol=1e-8):
                res.fail(f"circuit ≠ scalar·diagram for {verify.fmt_values(values)}; {verify._ratio_hint(U, D)}")
                break
        v.result = res
        if not res.ok:
            errors.append(f"[{v.key}] " + "; ".join(res.messages))
    return errors

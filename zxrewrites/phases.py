"""Parsing and pretty-printing of (possibly symbolic) phases.

Conventions (same as PyZX): a phase ``p`` stored on a spider denotes the angle ``p * pi``.
Symbolic phases are PyZX ``Poly`` objects over ASCII variable names (``alpha``, ``beta``, ``a``...).
A *real* variable ``alpha`` appearing as a phase therefore denotes the angle ``alpha*pi``; for display
purposes we simply call that angle "α".  A *boolean* variable ``a`` denotes the phase ``a*pi`` with
a in {0,1}, and is displayed as "aπ".
"""

from __future__ import annotations

import re
from fractions import Fraction
from typing import Any, Dict, Optional, Tuple, Union

from pyzx.symbolic import Poly, Term, Var, new_var, parse

GREEK = {
    "alpha": ("α", r"\alpha"), "beta": ("β", r"\beta"), "gamma": ("γ", r"\gamma"),
    "delta": ("δ", r"\delta"), "theta": ("θ", r"\theta"), "phi": ("φ", r"\varphi"),
    "psi": ("ψ", r"\psi"), "lambda": ("λ", r"\lambda"), "mu": ("μ", r"\mu"),
    "eta": ("η", r"\eta"), "epsilon": ("ε", r"\epsilon"), "omega": ("ω", r"\omega"),
    "tau": ("τ", r"\tau"), "rho": ("ρ", r"\rho"), "sigma": ("σ", r"\sigma"),
    "kappa": ("κ", r"\kappa"), "xi": ("ξ", r"\xi"), "zeta": ("ζ", r"\zeta"),
}
SUBSCRIPTS = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")

PhaseLike = Union[int, Fraction, float, Poly]


def var_display(name: str) -> Tuple[str, str]:
    """Return (unicode, latex) display forms for an ASCII variable name like ``alpha1`` or ``a``."""
    m = re.fullmatch(r"([A-Za-z]+?)_?(\d*)", name)
    base, idx = (m.group(1), m.group(2)) if m else (name, "")
    uni, tex = GREEK.get(base, (base, base))
    if idx:
        uni += idx.translate(SUBSCRIPTS)
        tex += "_{" + idx + "}"
    return uni, tex


def parse_phase(spec: Any, registry, var_types: Dict[str, bool]) -> PhaseLike:
    """Parse an authoring phase spec (int/Fraction/str in units of pi) into a PyZX phase."""
    if isinstance(spec, (int, Fraction)):
        return Fraction(spec) % 2
    if isinstance(spec, float):
        return Fraction(spec).limit_denominator(1024) % 2
    if isinstance(spec, str):
        s = spec.strip()
        try:
            return Fraction(s) % 2
        except ValueError:
            pass

        def mk(name: str) -> Poly:
            return new_var(name, var_types.get(name, False), registry)

        return parse(s, mk)
    raise TypeError(f"Cannot parse phase {spec!r}")


def poly_const(p: Poly) -> Optional[Fraction]:
    """If p is a constant polynomial return its value, otherwise None."""
    if p.free_vars():
        return None
    total = Fraction(0)
    for c, _t in p.terms:
        total += Fraction(c) if not isinstance(c, complex) else Fraction(c.real)
    return total


def to_number(p: PhaseLike):
    if isinstance(p, Poly):
        c = poly_const(p)
        if c is None:
            raise ValueError(f"phase {p} is still symbolic")
        return c
    return p


def _norm_const(c: Fraction) -> Fraction:
    """Normalise a constant phase (units of pi) to the interval (-1, 1]."""
    c = Fraction(c) % 2
    if c > 1:
        c -= 2
    return c


def _const_str(c: Fraction, latex: bool, lead: bool) -> str:
    """Format c*pi.  ``lead`` says whether this is the first term (no leading '+')."""
    sign = "-" if c < 0 else ("" if lead else "+")
    c = abs(c)
    num, den = c.numerator, c.denominator
    if latex:
        if den == 1:
            body = (r"\pi" if num == 1 else f"{num}\\pi")
        else:
            body = (r"\frac{\pi}{%d}" % den) if num == 1 else (r"\frac{%d\pi}{%d}" % (num, den))
    else:
        top = "π" if num == 1 else f"{num}π"
        body = top if den == 1 else f"{top}/{den}"
    return sign + body


def _coeff_var_str(coeff: Fraction, vname: str, is_bool: bool, latex: bool, lead: bool) -> str:
    uni, tex = var_display(vname)
    v = tex if latex else uni
    if is_bool:
        v = v + (r"\pi" if latex else "π")
    sign = "-" if coeff < 0 else ("" if lead else "+")
    c = abs(Fraction(coeff))
    if c == 1:
        return sign + v
    if c.denominator == 1:
        return sign + f"{c.numerator}{v}"
    if c.numerator == 1:
        return sign + (r"\frac{%s}{%d}" % (v, c.denominator) if latex else f"{v}/{c.denominator}")
    return sign + (r"\frac{%d%s}{%d}" % (c.numerator, v, c.denominator) if latex else f"{c.numerator}{v}/{c.denominator}")


def format_phase(p: PhaseLike, latex: bool = False, zero: str = "") -> str:
    """Pretty-print a phase in units of pi, e.g. 1/2 -> 'π/2', alpha+1 -> 'α+π'."""
    if isinstance(p, Poly):
        c = poly_const(p)
        if c is not None:
            p = c
    if not isinstance(p, Poly):
        c = _norm_const(Fraction(p).limit_denominator(1 << 20))
        if c == 0:
            return zero
        return _const_str(c, latex, True)
    var_terms = []
    const = Fraction(0)
    for coeff, term in p.terms:
        if not term.vars:
            const += Fraction(coeff)
            continue
        if len(term.vars) != 1 or term.vars[0][1] != 1:
            # Non-linear term: fall back to PyZX's own printing.
            return str(p)
        var = term.vars[0][0]
        var_terms.append((var.name, Fraction(coeff), var.is_bool))
    var_terms.sort()
    parts = []
    for i, (name, coeff, is_bool) in enumerate(var_terms):
        parts.append(_coeff_var_str(coeff, name, is_bool, latex, i == 0))
    const = _norm_const(const)
    if const != 0:
        parts.append(_const_str(const, latex, not parts))
    s = "".join(parts)
    return s if s else zero


def phase_vars(p: PhaseLike) -> Dict[str, bool]:
    if isinstance(p, Poly):
        return {v.name: v.is_bool for v in p.free_vars()}
    return {}


def substitute(p: PhaseLike, values: Dict[str, Any]) -> PhaseLike:
    """Substitute numeric values (units of pi for real vars, 0/1 for booleans) into a phase."""
    if not isinstance(p, Poly) or not p.free_vars():
        return to_number(p) if isinstance(p, Poly) else p
    total: Any = 0
    for coeff, term in p.terms:
        val: Any = coeff
        for var, power in term.vars:
            val = val * (values[var.name] ** power)
        total = total + val
    if isinstance(total, Fraction):
        return total % 2
    if isinstance(total, complex):
        total = total.real
    return float(total) % 2.0


def negate(p: PhaseLike) -> PhaseLike:
    if isinstance(p, Poly):
        return -p
    return (-Fraction(p)) % 2 if not isinstance(p, float) else (-p) % 2.0

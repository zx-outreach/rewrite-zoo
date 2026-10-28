"""Scalars of rules, stored as sympy expressions in meta.json.

Convention: a rule with scalar ``s`` asserts  LHS = s · RHS  (as linear maps, exactly).

Inside a scalar expression
* a phase variable with domain real/clifford/clifford+t (e.g. ``alpha``) denotes the *angle* in
  radians, i.e. pi times the value PyZX stores on the spider;
* a boolean or integer variable (e.g. ``a``) denotes its value (0/1);
* a complex variable denotes its value;
* rule parameters (e.g. ``n``, the number of legs) are integers, fixed by ``parameters`` for the
  stored instance.
"""

from __future__ import annotations

import math
from typing import Any, Dict, Optional

import sympy as sp

from .phases import var_display

ANGLE_DOMAINS = {"real", "clifford", "clifford+t"}


def symbols_for(variables: Dict[str, Dict[str, Any]], parameters: Dict[str, int]) -> Dict[str, sp.Symbol]:
    syms = {}
    for name, spec in variables.items():
        dom = spec["domain"]
        if dom in ANGLE_DOMAINS:
            syms[name] = sp.Symbol(name, real=True)
        elif dom in ("boolean", "integer"):
            syms[name] = sp.Symbol(name, integer=True)
        else:
            syms[name] = sp.Symbol(name, complex=True)
    for name in parameters:
        syms[name] = sp.Symbol(name, integer=True, nonnegative=True)
    return syms


def parse_scalar(expr: Optional[str], variables, parameters, evaluate: bool = True) -> sp.Expr:
    if expr is None or str(expr).strip() == "":
        return sp.Integer(1)
    syms = symbols_for(variables, parameters)
    ns = dict(syms)
    ns.update({"I": sp.I, "pi": sp.pi, "sqrt": sp.sqrt, "exp": sp.exp, "E": sp.E,
               "cos": sp.cos, "sin": sp.sin, "conjugate": sp.conjugate, "Abs": sp.Abs})
    return sp.sympify(str(expr), locals=ns, evaluate=evaluate)


def instance_value(s: sp.Expr, parameters: Dict[str, int], variables) -> sp.Expr:
    """Substitute the instance parameters (e.g. n=3) into the scalar."""
    syms = symbols_for(variables, parameters)
    return s.subs({syms[k]: v for k, v in parameters.items()})


def evaluate(s: sp.Expr, values: Dict[str, Any], variables, parameters) -> complex:
    """Numerically evaluate the scalar at a sample of variable values (PyZX units for phases)."""
    syms = symbols_for(variables, parameters)
    sub = {}
    for name, spec in variables.items():
        if name not in values:
            continue
        val = values[name]
        if spec["domain"] in ANGLE_DOMAINS:
            sub[syms[name]] = sp.Float(float(val)) * sp.pi
        elif spec["domain"] == "complex":
            c = complex(val)
            sub[syms[name]] = sp.Float(c.real) + sp.I * sp.Float(c.imag)
        else:
            sub[syms[name]] = sp.Integer(int(val))
    for k, v in parameters.items():
        sub[syms[k]] = sp.Integer(v)
    return complex(sp.N(s.subs(sub)))


def conjugate(s: sp.Expr, variables, parameters) -> sp.Expr:
    """The scalar of the complex-conjugated rule.

    Complex variables range over all of C, so conjugating the rule is the same as conjugating the
    coefficients of the scalar while keeping the complex variables themselves."""
    c = sp.conjugate(s)
    syms = symbols_for(variables, parameters)
    for name, spec in variables.items():
        if spec["domain"] == "complex":
            c = c.subs(sp.conjugate(syms[name]), syms[name])
    return sp.simplify(c)


def inverse(s: sp.Expr) -> Optional[sp.Expr]:
    if s == 0:
        return None
    return sp.simplify(1 / s)


def _latex_names(variables, parameters) -> Dict[sp.Symbol, str]:
    syms = symbols_for(variables, parameters)
    return {sym: var_display(name)[1] for name, sym in syms.items()}


def _split_phase(s: sp.Expr):
    """Write s as  phase · rest, where phase = e^{iπq} for a rational q collected from all factors
    of the form -1, i, (-1)^q and e^{iπq}. Returns (q, [other factors])."""
    q = sp.Rational(0)
    rest = []
    for f in sp.Mul.make_args(s):
        if f == sp.I:
            q += sp.Rational(1, 2)
        elif f.is_Number and f.is_negative:
            q += 1
            if f != -1:
                rest.append(-f)
        elif f.is_Pow and f.base == -1:
            for t in sp.Add.make_args(sp.expand(f.exp)):
                if t.is_Rational:
                    q += t
                else:
                    rest.append(sp.Pow(-1, t, evaluate=False))
        elif isinstance(f, sp.exp):
            for t in sp.Add.make_args(sp.expand(f.args[0])):
                c = sp.simplify(t / (sp.I * sp.pi))
                if c.is_Rational:
                    q += c
                else:
                    rest.append(sp.exp(t, evaluate=False))
        else:
            rest.append(f)
    q = q % 2
    if q > 1:
        q -= 2
    return q, rest


def pretty(s: sp.Expr) -> sp.Expr:
    """An unevaluated expression for display: global phases are written as e^{iπq} (or ±1, ±i),
    never as (-1)^q."""
    q, rest = _split_phase(sp.nsimplify(s) if s.is_Number else s)
    factors = []
    sign = 1
    if q == 1:
        sign = -1
    elif q == sp.Rational(1, 2):
        factors.append(sp.I)
    elif q == -sp.Rational(1, 2):
        sign = -1
        factors.append(sp.I)
    elif q != 0:
        factors.append(sp.exp(sp.I * sp.pi * q, evaluate=False))
    factors = rest + factors
    if not factors:
        return sp.Integer(sign)
    e = factors[0] if len(factors) == 1 else sp.Mul(*factors, evaluate=False)
    if sign == -1:
        return -e if e.is_Number else sp.Mul(-1, e, evaluate=False)
    return e


def latex(s: Optional[sp.Expr], variables, parameters) -> str:
    if s is None:
        return ""
    names = _latex_names(variables, parameters)
    try:
        p = _strip_ones(pretty(s))
    except Exception:
        p = s
    out = sp.latex(p, symbol_names=names, imaginary_unit="i")
    # a sum multiplies the whole diagram, so it needs brackets: (1 + e^{iα}) · D
    return chr(92) + "left(" + out + chr(92) + "right)" if isinstance(p, sp.Add) else out


def _strip_ones(e: sp.Expr) -> sp.Expr:
    """Remove factors 1 from unevaluated products (so that 1/2 is not printed as 1·1/2)."""
    if e.is_Atom:
        return e
    args = [_strip_ones(a) for a in e.args]
    if isinstance(e, sp.Mul):
        args = [a for a in args if a != 1] or [sp.Integer(1)]
        return args[0] if len(args) == 1 else sp.Mul(*args, evaluate=False)
    try:
        return e.func(*args, evaluate=False)
    except TypeError:
        return e.func(*args)


def is_one(s: sp.Expr) -> bool:
    return sp.simplify(s - 1) == 0


def from_number(c: complex) -> sp.Expr:
    """Best-effort exact expression for a numerically found scalar: sqrt(2)^k * e^{i pi p/8}."""
    if abs(c) < 1e-12:
        return sp.Integer(0)
    k = 2 * math.log2(abs(c))
    ph = math.atan2(c.imag, c.real) / math.pi
    if abs(k - round(k)) < 1e-9 and abs(ph * 8 - round(ph * 8)) < 1e-9:
        return sp.simplify(sp.sqrt(2) ** int(round(k)) * sp.exp(sp.I * sp.pi * sp.Rational(int(round(ph * 8)), 8)))
    return sp.nsimplify(complex(c), [sp.sqrt(2)], tolerance=1e-9)


def text(s: Optional[sp.Expr], variables, parameters) -> str:
    """A compact one-line unicode rendering of a scalar (for thumbnails)."""
    if s is None or is_one(s):
        return ""
    syms = symbols_for(variables, parameters)
    names = {sym: var_display(name)[0] for name, sym in syms.items()}
    s = s.subs({sym: sp.Symbol(names[sym]) for sym in syms.values() if sym in s.free_symbols})
    try:
        s = pretty(s)
    except Exception:
        pass
    out = sp.sstr(s)
    for a, b in (("sqrt(2)", "√2"), ("**", "^"), ("*", ""), ("exp(", "e^("), ("I", "i"), ("pi", "π")):
        out = out.replace(a, b)
    return f"({out})" if isinstance(s, sp.Add) else out


# ---------------------------------------------------------------------------------------------
# Memoisation: the same scalars occur in many variants and arity instances, and sympy is slow.

import functools as _functools
import json as _json


def _memo(fn):
    cache = {}

    @_functools.wraps(fn)
    def wrapper(*args):
        key = tuple(sp.srepr(a) if isinstance(a, sp.Basic) else _json.dumps(a, sort_keys=True, default=str)
                    for a in args)
        if key not in cache:
            cache[key] = fn(*args)
        return cache[key]
    return wrapper


latex = _memo(latex)
text = _memo(text)
inverse = _memo(inverse)
conjugate = _memo(conjugate)
is_one = _memo(is_one)

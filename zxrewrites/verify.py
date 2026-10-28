"""Semantic verification of rules with PyZX tensor contraction."""

from __future__ import annotations

import itertools
import random
from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import sympy as sp

from . import graphs, scalars

N_RANDOM = 6


def sample_values(variables: Dict[str, Dict[str, Any]], seed: int = 0, n_random: int = N_RANDOM) -> List[Dict[str, Any]]:
    """Assignments of values to variables (phase variables in units of pi)."""
    if not variables:
        return [{}]
    rng = random.Random(seed)
    per_var: Dict[str, List[Any]] = {}
    for name, spec in variables.items():
        dom = spec["domain"]
        if "values" in spec:
            vals = [Fraction(v) if isinstance(v, (int, str)) else v for v in spec["values"]]
        elif dom == "boolean":
            vals = [Fraction(0), Fraction(1)]
        elif dom == "integer":
            vals = [Fraction(k) for k in range(-2, 4)]
        elif dom == "clifford":
            vals = [Fraction(k, 2) for k in range(4)]
        elif dom == "clifford+t":
            vals = [Fraction(k, 4) for k in range(8)]
        elif dom == "real":
            vals = [Fraction(0), Fraction(1, 2), Fraction(1, 3)] + [Fraction(rng.randrange(1, 2 * 997), 997) for _ in range(n_random)]
        elif dom == "complex":
            vals = [0j, 1 + 0j, -1 + 0j, 0.5 + 0j, 2j] + [complex(rng.gauss(0, 1), rng.gauss(0, 1)) for _ in range(n_random)]
        else:
            raise ValueError(f"unknown domain {dom}")
        per_var[name] = vals
    names = list(per_var)
    total = 1
    for n in names:
        total *= len(per_var[n])
    if total <= 64:
        return [dict(zip(names, combo)) for combo in itertools.product(*(per_var[n] for n in names))]
    # Too many combinations: random mixing, plus the "diagonal" so that each value is used.
    out = []
    longest = max(len(v) for v in per_var.values())
    for i in range(longest):
        out.append({n: per_var[n][i % len(per_var[n])] for n in names})
    for _ in range(max(4, 3 * n_random)):
        out.append({n: rng.choice(per_var[n]) for n in names})
    return out


class VerificationResult:
    def __init__(self):
        self.ok = True
        self.messages: List[str] = []
        self.samples = 0
        self.found_scalar: Optional[complex] = None
        self.lhs_zero = False

    def fail(self, msg: str):
        self.ok = False
        self.messages.append(msg)


def check(lhs, rhs, scalar: Optional[sp.Expr], variables, parameters, seed: int = 0,
          n_random: int = N_RANDOM) -> VerificationResult:
    """Check LHS = scalar · RHS for all sampled values.  If ``scalar`` is None, check that the two
    sides are proportional and record the proportionality constant at the first sample."""
    res = VerificationResult()
    if graphs.boundary_signature(lhs) != graphs.boundary_signature(rhs):
        res.fail(f"boundary mismatch: LHS has {graphs.boundary_signature(lhs)} (inputs, outputs), "
                 f"RHS has {graphs.boundary_signature(rhs)}")
        return res
    for values in sample_values(variables, seed, n_random):
        try:
            L = graphs.tensor(graphs.instantiate(lhs, values))
            R = graphs.tensor(graphs.instantiate(rhs, values))
        except Exception as e:
            res.fail(f"could not compute tensor at {values}: {e!r}")
            return res
        res.samples += 1
        if scalar is not None:
            s = scalars.evaluate(scalar, values, variables, parameters)
            if not np.allclose(L, s * R, atol=1e-8):
                res.fail(f"LHS ≠ scalar·RHS for {fmt_values(values)} (scalar evaluates to {s:.6g}); "
                         f"{_ratio_hint(L, R)}")
                return res
        else:
            # proportionality check
            if np.allclose(R, 0, atol=1e-10):
                if not np.allclose(L, 0, atol=1e-10):
                    res.fail(f"RHS is zero but LHS is not for {fmt_values(values)}")
                    return res
                continue
            idx = np.unravel_index(np.argmax(np.abs(R)), R.shape)
            c = L[idx] / R[idx]
            if not np.allclose(L, c * R, atol=1e-8):
                res.fail(f"LHS and RHS are not proportional for {fmt_values(values)}")
                return res
            if res.found_scalar is None and not values:
                res.found_scalar = complex(c)
    return res


def _ratio_hint(L, R) -> str:
    if np.allclose(R, 0, atol=1e-10):
        return "RHS is zero"
    idx = np.unravel_index(np.argmax(np.abs(R)), R.shape)
    c = L[idx] / R[idx]
    if np.allclose(L, c * R, atol=1e-8):
        return f"but LHS = {complex(c):.6g} · RHS"
    return "and the two sides are not proportional"


def fmt_values(values: Dict[str, Any]) -> str:
    if not values:
        return "the diagram"
    def f(v):
        if isinstance(v, Fraction):
            return str(v)
        if isinstance(v, float):
            return f"{v:.4g}"
        return str(v)
    return ", ".join(f"{k}={f(v)}" for k, v in values.items())

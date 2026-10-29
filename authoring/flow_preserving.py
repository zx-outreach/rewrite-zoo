"""Rules of the flow-preserving completeness paper (Backens & Perdrix, "Completeness for flow-preserving
rewrite rules", arXiv:2608.13035) that are not already in the zoo: the phase fusion rule (PF) and the
graph-like form of the Euler rule (E_ZX). The other rules of its complete set (Fig. 2) are existing rules;
see data/axiomatisations-flow.json.

The paper draws MBQC-form diagrams: every vertex is a phase-free Z-spider and its measurement is a separate
effect (a Z-phase for an XY-measurement, an X-phase for a YZ-measurement). Here the rules are stored in
graph-like form: an XY-measurement effect is fused into its vertex as a Z-phase, and an X(α) effect attached
by a plain wire is drawn as a Z(α) spider attached by a Hadamard edge.

    python flow_preserving.py [--force] [--only=id1,id2] [--selftest]
"""

import cmath
import math
import random
import sys
from fractions import Fraction

from dsl import D, rule

FLOWCOMP = "backens2026completeness"
PI = math.pi


def arg(w: complex) -> float:
    return 0.0 if abs(w) < 1e-14 else cmath.phase(w)


def euler_flow_angles(a1, a2):
    """Angles of rule (E_ZX) (Lemma 23 of the paper), with the paper's case distinction and with
    beta_i reduced to [0, 2pi), together with the global phase gamma such that LHS = e^{i gamma} RHS."""
    xp = (a1 + a2) / 2
    xm = (a1 - a2) / 2
    z = -math.sin(xp) + 1j * math.cos(xm)
    zp = math.cos(xp) - 1j * math.sin(xm)
    if abs(zp) < 1e-12:
        b1, b2, b3 = 2 * arg(z), 0.0, 0.0
    elif abs(z) < 1e-12:
        b1, b2, b3 = 2 * arg(zp), PI, 0.0
    else:
        b1, b2, b3 = arg(z) + arg(zp), 2 * arg(1j + abs(z / zp)), arg(z) - arg(zp)
    b1, b2, b3 = (b % (2 * PI) for b in (b1, b2, b3))
    g = xp - arg(zp) if abs(z) < 1e-12 else xp - arg(z) + (PI - b2) / 2
    return b1, b2, b3, g


def val(x: float):
    """A variable restricted to one value, given as a float in units of pi."""
    return {"domain": "real", "values": [str(Fraction(x).limit_denominator(10 ** 9))]}


# ---------------------------------------------------------------------------------------------
# (PF) phase fusion: moving phase between a YZ-measured vertex and its single XY-measured neighbour

def build_phase_fusion(gadget_phase, vertex_phase):
    d = D()
    v = d.z(1.5, 1, vertex_phase)
    d.e(d.b(0, 0.5), v).e(d.b(0, 1.5), v).e(v, d.b(3, 1))
    hub, leaf = d.z(1.5, -0.2), d.z(2.7, -0.2, gadget_phase)
    d.he(v, hub, leaf)
    return d


L = build_phase_fusion("alpha", "beta")
R = build_phase_fusion("gamma", "alpha-gamma+beta")
rule(
    "phase-fusion", lhs=L, rhs=R,
    name="Phase fusion (PF)",
    aliases=["(PF)", "PF", "flow-preserving phase fusion", "phase redistribution", "gadget phase exchange"],
    calculus="ZX", fragment="universal", group="phase-gadgets", order=5, view="graph-like",
    summary="The phases of a phase gadget with a single target and of that target can be redistributed arbitrarily, keeping their sum.",
    description=(
        "A phase gadget that is attached to a single spider only contributes its phase to that spider (see "
        "[gadget fusion into a spider](../identity-gadget-removal/)). Instead of removing the gadget, this rule "
        "keeps the structure of the diagram and only moves phase between the gadget and its target: phases "
        "$\\alpha$ (gadget) and $\\beta$ (target) can be replaced by $\\gamma$ and $\\alpha-\\gamma+\\beta$ for any "
        "$\\gamma$.\n\n"
        "In MBQC terms the gadget is a YZ-measured vertex (an X-phase effect on a vertex of the graph) whose only "
        "neighbour is XY-measured. Since the underlying graph and the measurement planes do not change, the rule "
        "preserves Pauli flow, gflow and extended causal flow in both directions. Backens and Perdrix use it as "
        "the flow-preserving replacement of the phase-adding part of spider fusion: in their complete set of "
        "flow-preserving rules, merging and splitting the neighbourhoods of spiders is done with Z-insertion and "
        "pivoting instead. With $\\gamma$ chosen suitably, the rule is its own inverse."),
    variables={"alpha": "real", "beta": "real", "gamma": "real"},
    parameters={"n": 2, "m": 1},
    parameter_notes=("The target has n inputs and m outputs (shown for n = 2, m = 1); it may have any number of "
                     "further legs and Hadamard edges. γ is the arbitrary new phase of the gadget (α′ in the paper)."),
    scalar="1",
    source={"bib": FLOWCOMP, "location": "Lemma 24 (Phase fusion); rule (PF) in Fig. 2"},
    related=[{"id": "identity-gadget-removal", "relation": "derived-from"},
             {"id": "graph-like-identity-removal", "relation": "see-also"},
             {"id": "pauli-gadget-removal", "relation": "see-also"}],
    tags=["phase gadget", "graph-like", "MBQC", "flow", "gflow", "fusion", "YZ-plane"],
)


# ---------------------------------------------------------------------------------------------
# (E_ZX) the Euler rule on an edge between two XY-measured vertices

EF_A = ["1/3", "2/7"]
b1, b2, b3, gm = euler_flow_angles(*[float(Fraction(s)) * PI for s in EF_A])

L = D()
a, b = L.z(1, 0.5, "alpha1"), L.z(2.4, 0.5, "alpha2")
L.e(L.b(0, 0), a).e(L.b(0, 1), a).e(b, L.b(3.4, 0)).e(b, L.b(3.4, 1))
L.he(a, b)
R = D()
a2, b2_ = R.z(1, 0.5), R.z(5, 0.5)
x, y, z = R.z(2, 0.5, "beta1"), R.z(3, 0.5, "beta2"), R.z(4, 0.5, "beta3")
R.e(R.b(0, 0), a2).e(R.b(0, 1), a2).e(b2_, R.b(6, 0)).e(b2_, R.b(6, 1))
R.he(a2, x, y, z, b2_)
EF_CONDITIONS = (
    "β₁, β₂, β₃ (in [0, 2π)) and γ are functions of α₁, α₂: let z = −sin((α₁+α₂)/2) + i cos((α₁−α₂)/2) and "
    "z′ = cos((α₁+α₂)/2) − i sin((α₁−α₂)/2). If z′ = 0 then β₁ = 2 arg z, β₂ = β₃ = 0; if z = 0 then "
    "β₁ = 2 arg z′, β₂ = π, β₃ = 0; otherwise β₁ = arg z + arg z′, β₂ = 2 arg(i + |z/z′|) and "
    "β₃ = arg z − arg z′. The global phase is γ = (α₁+α₂)/2 − arg z + (π − β₂)/2 (with arg 0 = 0), "
    "except when z = 0, where γ = (α₁+α₂)/2 − arg z′. "
    "Flow: the rule preserves extended causal flow if the diagram has an extended causal flow g with "
    "g(a) = {b} or g(b) = {a}, where a and b are the two XY-measured vertices.")
rule(
    "euler-flow-preserving", lhs=L, rhs=R,
    name="Flow-preserving Euler rule (E_ZX)",
    aliases=["(E_ZX)", "E_ZX", "(EZX)", "Euler rule (flow-preserving)", "graph-like Euler rule",
             "Euler decomposition of an edge"],
    calculus="ZX", fragment="universal", group="euler", order=4, view="graph-like",
    summary="A Hadamard edge between spiders with phases α₁ and α₂ can be replaced by a path through three new spiders with phases β₁, β₂, β₃, moving the phases α₁, α₂ onto the path.",
    description=(
        "This is the [Euler-angle rule with a Hadamard](../euler-angles-hadamard/) in graph-like form. Unfusing "
        "the phases of the two spiders, the left-hand side contains $R_Z(\\alpha_2)HR_Z(\\alpha_1)$ on the edge, "
        "and the path on the right-hand side is $HR_Z(\\beta_3)HR_Z(\\beta_2)HR_Z(\\beta_1)H = "
        "R_X(\\beta_3)R_Z(\\beta_2)R_X(\\beta_1)$, so the two sides are equal up to the global phase "
        "$e^{i\\gamma}$ by Vilmart's formulas.\n\n"
        "Backens and Perdrix use this form in their complete set of flow-preserving rewrite rules. In MBQC terms "
        "the two spiders are XY-measured vertices $a$ and $b$ (with angles $\\alpha_1$ and $\\alpha_2$) and the "
        "rule inserts three new XY-measured vertices $x, y, z$ on the edge between them, while $a$ and $b$ get "
        "angle 0. It preserves extended causal flow when the flow corrects $a$ by $b$ (or $b$ by $a$): the new "
        "flow is $a\\mapsto x\\mapsto y\\mapsto z\\mapsto b$. It is only needed in this causal-flow setting, where "
        "it is used to translate the Euler rule of the complete equational theory for quantum circuits.\n\n"
        "The stored instance is checked for $\\alpha_1=\\frac\\pi3$, $\\alpha_2=\\frac{2\\pi}7$."),
    variables={"alpha1": {"domain": "real", "values": [EF_A[0]]}, "alpha2": {"domain": "real", "values": [EF_A[1]]},
               "beta1": val(b1 / PI), "beta2": val(b2 / PI), "beta3": val(b3 / PI), "gamma": val(gm / PI)},
    parameters={"n": 2, "m": 2},
    parameter_notes=("The two spiders have n and m further legs (shown for n = m = 2); they may have any number "
                     "of further legs and Hadamard edges."),
    conditions=EF_CONDITIONS,
    scalar="exp(I*gamma)",
    source={"bib": FLOWCOMP, "location": "Lemma 23 (Euler rule); rule (E_ZX) in Fig. 2"},
    related=[{"id": "euler-angles-hadamard", "relation": "variant-of"},
             {"id": "graph-like-identity-removal", "relation": "see-also"}],
    tags=["euler", "euler angles", "graph-like", "MBQC", "flow", "causal flow", "non-linear", "universal"],
    notes="The build checks one generic instance of the angles; `python authoring/flow_preserving.py --selftest` "
          "checks the formulas with PyZX on random angles and on the two degenerate cases.",
)


# ---------------------------------------------------------------------------------------------

def self_test(n=30):
    import numpy as np
    from zxrewrites import graphs

    def T(d):
        d.g.auto_detect_io()
        return graphs.tensor(d.g)

    rng = random.Random(3)
    cases = [(rng.uniform(-PI, PI), rng.uniform(-PI, PI)) for _ in range(n)]
    cases += [(PI / 2, -PI / 2), (PI / 2, PI / 2), (0.0, PI), (PI / 3, PI / 3 + PI)]  # degenerate cases
    for a1, a2 in cases:
        c1, c2, c3, g = euler_flow_angles(a1, a2)
        f = lambda t: str(Fraction(t / PI).limit_denominator(10 ** 9))  # noqa: E731
        Ld = D()
        u, v = Ld.z(1, 0, f(a1)), Ld.z(2, 0, f(a2))
        Ld.e(Ld.b(0, 0), u).he(u, v).e(v, Ld.b(3, 0))
        Rd = D()
        u2, v2 = Rd.z(1, 0), Rd.z(5, 0)
        Rd.e(Rd.b(0, 0), u2).he(u2, Rd.z(2, 0, f(c1)), Rd.z(3, 0, f(c2)), Rd.z(4, 0, f(c3)), v2).e(v2, Rd.b(6, 0))
        A, B = T(Ld), T(Rd)
        assert np.allclose(A, cmath.exp(1j * g) * B, atol=1e-7), (a1, a2)
    print("E_ZX formulas OK on", len(cases), "instances")


if "--selftest" in sys.argv:
    self_test()

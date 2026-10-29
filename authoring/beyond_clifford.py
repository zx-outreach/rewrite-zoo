"""ZX rules beyond the Clifford fragment: supplementarity and its generalisations, the extra axioms of the
Clifford+T and universal completeness results (Jeandel-Perdrix-Vilmart, Vilmart, Coecke-Wang), spider nests
(Munson-Coecke-Wang) and catalysis (Kissinger-Ross-van de Wetering).

Conventions of these papers: spiders are unnormalised (Z-spider = |0..0><0..0| + e^{ia}|1..1><1..1|, X-spider is
its Hadamard conjugate) and the Hadamard is normalised, exactly as in PyZX, so the scalars of the papers carry
over unchanged. The papers draw diagrams from top (inputs) to bottom (outputs); here they are rotated so that
inputs are on the left.
"""

import cmath
import math
import random
from fractions import Fraction

from dsl import D, rule

SUPP = "supplementarity"
CYCLO = "cyclo"
JPV = "SimonCompleteness"
JPVU = "JPV-universal"
VIL = "vilmarteulercompleteness"
LMCS = "jeandel2019completeness"
CW = "coecke2018zx"
BOOK = "KissingervdWeteringbook"

PI = math.pi


def frac(t: float) -> Fraction:
    """An angle in radians as an (almost exact) fraction of pi."""
    return Fraction(t / PI).limit_denominator(10 ** 12)


def arg(w: complex) -> float:
    return 0.0 if abs(w) < 1e-14 else cmath.phase(w)


# ---------------------------------------------------------------------------------------------
# Supplementarity (SUP)

L = D()
g1 = L.z(0, 0, "alpha")
g2 = L.z(0, 1, "alpha+1")
r = L.x(1, 0.5)
L.e(g1, r).e(g2, r).e(r, L.b(2, 0.5))
R = D()
g = R.z(0, 0.5, "2*alpha+1")
r = R.x(1, 0.5)
R.e(g, r).e(g, r).e(r, R.b(2, 0.5))
rule(
    "supplementarity", lhs=L, rhs=R,
    name="Supplementarity",
    aliases=["(SUP)", "SUP", "antipodal merging", "supplementarity rule"],
    calculus="ZX", fragment="universal", group="supplementarity", order=1,
    summary="Two Z-states with antipodal phases α and α+π plugged into the same X-spider merge into one Z-spider with phase 2α+π.",
    description=(
        "Two arity-one Z-spiders whose phases differ by π (they are *antipodal*) and that are connected to the same "
        "X-spider can be merged into a single Z-spider with phase $2\\alpha+\\pi$, connected to the X-spider by two "
        "wires. Both sides denote the state $\\frac{1}{\\sqrt2}(1-e^{2i\\alpha})\\ket{0}$. By the [Hopf rule](../hopf/) the right-hand side can be simplified further to a scalar times "
        "a phase-free X-state.\n\n"
        "Supplementarity was introduced by Perdrix and Wang, inspired by an observation of Coecke and Edwards, who "
        "proved that it is *necessary*: it can be derived from the original rules of the ZX-calculus if and only if "
        "$\\alpha$ is a multiple of $\\pi/2$. In particular it cannot be derived for $\\alpha=\\pi/4$, which showed "
        "that the ZX-calculus of that time was incomplete for Clifford+T. It is one of the axioms of the complete "
        "axiomatisations of Jeandel, Perdrix and Vilmart for Clifford+T and for the full (universal) ZX-calculus. "
        "In Vilmart's near-minimal axiomatisation it is no longer an axiom, but is derived from the "
        "[Euler-angle rule](../euler-angles/).\n\n"
        "Its graphical meaning is that *antiphase twins* can be merged, see [merging antiphase twins](../antiphase-twins/), "
        "and it is the case $n=2$ of [cyclotomic supplementarity](../cyclotomic-supplementarity/)."),
    variables={"alpha": "real"},
    scalar="1",
    source={"bib": SUPP, "location": "Section 3, supplementarity equation"},
    also_in=[{"bib": CYCLO, "location": "Fig. 1, rule (SUP)"},
             {"bib": JPV, "location": "Fig. 1, rule (SUP)"},
             {"bib": JPVU, "location": "Fig. 1 and Fig. 2, rule (SUP)"},
             {"bib": LMCS, "location": "Fig. 2, rule (SUP)"}],
    axiom_of=[JPV, JPVU, LMCS],
    related=[{"id": "cyclotomic-supplementarity", "relation": "special-case-of"},
             {"id": "antiphase-twins", "relation": "special-case-of"},
             {"id": "hopf", "relation": "see-also"}],
    tags=["supplementarity", "antipodal", "antiphase", "necessity", "incompleteness", "clifford+t"],
)

# The pi/4 instance, as drawn in the book.
L = D()
g1 = L.z(0, 0, "1/4")
g2 = L.z(0, 1, "5/4")
r = L.x(1, 0.5)
L.e(g1, r).e(g2, r).e(r, L.b(2, 0.5))
R = D()
r = R.x(1, 0.5)
R.e(r, R.b(2, 0.5))
rule(
    "supplementarity-pi-4", lhs=L, rhs=R,
    name="Supplementarity for π/4",
    aliases=["π/4 supplementarity", "T supplementarity"],
    calculus="ZX", fragment="clifford+t", group="supplementarity", order=2,
    summary="The π/4 and 5π/4 Z-states plugged into an X-spider give the phase-free X-state, up to a scalar.",
    description=(
        "The instance $\\alpha=\\pi/4$ of [supplementarity](../supplementarity/), with the right-hand side "
        "simplified using the [Hopf rule](../hopf/): two arity-one Z-spiders with phases $\\frac\\pi4$ and "
        "$\\frac{5\\pi}4 = \\frac\\pi4+\\pi$ attached to the same X-spider are, up to a scalar, equal to that "
        "X-spider alone, i.e. to the state $\\ket{0}$.\n\n"
        "This is the simplest equation of the Clifford+T fragment that cannot be proven with the rules that are "
        "complete for the Clifford fragment (stated without scalars). It is why the Clifford+T fragment needs "
        "additional axioms such as supplementarity."),
    scalar="auto",
    source={"bib": SUPP, "location": "Section 4 (supplementarity for α = π/4 is not derivable)"},
    also_in=[{"bib": BOOK}],
    related=[{"id": "supplementarity", "relation": "special-case-of"},
             {"id": "hopf", "relation": "derived-from"}],
    tags=["supplementarity", "T", "pi/4", "clifford+t", "incompleteness"],
)

# ---------------------------------------------------------------------------------------------
# Cyclotomic supplementarity (SUP_n), n = 3

L = D()
gs = [L.z(0, 0, "alpha"), L.z(0, 1, "alpha+2/3"), L.z(0, 2, "alpha+4/3")]
r = L.x(1.2, 1)
for gg in gs:
    L.e(gg, r)
L.e(r, L.b(2.2, 1))
R = D()
g = R.z(0, 1, "3*alpha")
r = R.x(1.2, 1)
R.e(g, r).e(g, r).e(g, r).e(r, R.b(2.2, 1))
rule(
    "cyclotomic-supplementarity", lhs=L, rhs=R,
    name="Cyclotomic supplementarity",
    aliases=["(SUP_n)", "SUPn", "generalised supplementarity", "cyclotomic twins"],
    calculus="ZX", fragment="universal", group="supplementarity", order=3,
    summary="n Z-states whose phases α + 2kπ/n divide the circle into equal parts, attached to one X-spider, merge into one Z-spider with phase nα+(n−1)π connected by n wires.",
    description=(
        "A generalisation of [supplementarity](../supplementarity/) from two to $n$ dots: if $n$ arity-one Z-spiders "
        "with phases $\\alpha, \\alpha+\\frac{2\\pi}n, \\ldots, \\alpha+\\frac{(n-1)2\\pi}n$ are attached to the same "
        "X-spider, they can be merged into a single Z-spider with phase $n\\alpha+(n-1)\\pi$, connected to the "
        "X-spider by $n$ parallel wires. Supplementarity is the case $n=2$.\n\n"
        "Jeandel, Perdrix, Vilmart and Wang showed that $(\\mathrm{SUP}_n)$ cannot be derived from the other rules "
        "when $n$ is an odd prime, giving a countable family of necessary axioms, while for composite $n$ it follows "
        "from the rules for its factors. As for supplementarity, the dots can more generally be merged when they "
        "have the same neighbourhood (*cyclotomic twins*)."),
    variables={"alpha": "real"},
    parameters={"n": 3},
    parameter_notes="Shown for n = 3, where the merged phase 3α + 2π equals 3α. The rule holds for every n ≥ 1, with the phases depending on n.",
    scalar="1",
    source={"bib": CYCLO, "location": "Section 4.1, rule (SUP_n)"},
    also_in=[{"bib": JPVU, "location": "Section 6.1 (incompleteness), rule (SUP_n)"}],
    related=[{"id": "supplementarity", "relation": "generalises"}],
    tags=["supplementarity", "cyclotomic", "roots of unity", "necessity", "incompleteness"],
)

# ---------------------------------------------------------------------------------------------
# Antiphase twins

L = D()
u = L.z(0, 0, "alpha")
v = L.z(0, 2, "alpha+1")
r1 = L.x(1.5, 0, "beta")
r2 = L.x(1.5, 2, "gamma")
L.e(u, r1).e(u, r2).e(v, r1).e(v, r2)
L.e(r1, L.b(2.5, 0)).e(r2, L.b(2.5, 2))
R = D()
w = R.z(0, 1, "2*alpha+1")
r1 = R.x(1.5, 0, "beta")
r2 = R.x(1.5, 2, "gamma")
R.e(w, r1).e(w, r1).e(w, r2).e(w, r2)
R.e(r1, R.b(2.5, 0)).e(r2, R.b(2.5, 2))
rule(
    "antiphase-twins", lhs=L, rhs=R,
    name="Merging antiphase twins",
    aliases=["antiphase twins", "twin merging"],
    calculus="ZX", fragment="universal", group="supplementarity", order=4,
    summary="Two spiders of the same colour with phases α and α+π and the same neighbourhood merge into one spider with phase 2α+π, with every connection doubled.",
    description=(
        "Two spiders $u$ and $v$ are *antiphase twins* if they have the same colour, their phases differ by $\\pi$, "
        "and they have the same neighbourhood: every other spider is connected to $u$ by as many wires as to $v$. "
        "Antiphase twins with phases $\\alpha$ and $\\alpha+\\pi$ can be merged into a single spider with phase "
        "$2\\alpha+\\pi$ that is connected to each neighbour by twice as many wires.\n\n"
        "Perdrix and Wang showed that, in the presence of the other rules, merging antiphase twins is equivalent to "
        "[supplementarity](../supplementarity/), which is the special case of twins of degree one sharing a "
        "single neighbour. This gives supplementarity a purely graphical meaning. The doubled wires can be "
        "removed in pairs with the [Hopf rule](../hopf/) when the neighbours have the opposite colour."),
    variables={"alpha": "real", "beta": "real", "gamma": "real"},
    parameter_notes="Shown for twins of degree two whose two neighbours are X-spiders with one output each; holds for any common neighbourhood.",
    scalar="auto",
    source={"bib": SUPP, "location": "Section 3, Theorem (Antiphase Twins and Supplementarity)"},
    related=[{"id": "supplementarity", "relation": "generalises"},
             {"id": "cyclotomic-supplementarity", "relation": "see-also"}],
    tags=["supplementarity", "antiphase", "twins", "merging"],
)

# ---------------------------------------------------------------------------------------------
# (E): the Clifford+T scalar rule

L = D()
L.e(L.z(0, 0, "1/4"), L.x(1, 0, "-1/4"))
R = D()
rule(
    "clifford-t-scalar", lhs=L, rhs=R,
    name="Clifford+T scalar rule (E)",
    aliases=["(E)", "E rule", "bicolour π/4 scalar"],
    calculus="ZX", fragment="clifford+t", group="scalars", order=20,
    summary="A π/4 Z-spider connected to a −π/4 X-spider is the empty diagram (the scalar 1).",
    description=(
        "The scalar diagram consisting of a Z-spider with phase $\\frac\\pi4$ connected to an X-spider with phase "
        "$-\\frac\\pi4$ represents the number $1$, so it is equal to the empty diagram.\n\n"
        "Jeandel, Perdrix, Vilmart and Wang showed that this equation cannot be derived from the earlier rules of "
        "the ZX-calculus, using a simple invariant (the parity of the number of odd-degree X-spiders plus the number "
        "of Hadamards). As it only involves angles that are multiples of $\\pi/4$, this was another proof that the "
        "Clifford+T fragment was incomplete. Adding (E) made the older scalar rules (IV) and (ZO) derivable, and it "
        "is an axiom of all the Jeandel–Perdrix–Vilmart complete axiomatisations and of Vilmart's near-minimal one."),
    scalar="1",
    source={"bib": CYCLO, "location": "Section 3, rule (E)"},
    also_in=[{"bib": JPV, "location": "Fig. 1, rule (E)"},
             {"bib": JPVU, "location": "Fig. 1 and Fig. 2, rule (E)"},
             {"bib": VIL, "location": "Fig. 1, rule (E)"},
             {"bib": LMCS, "location": "Fig. 2, rule (E)"}],
    axiom_of=[JPV, JPVU, VIL, LMCS],
    related=[{"id": "inverse-scalar-phase", "relation": "see-also"}],
    tags=["scalar", "empty diagram", "clifford+t", "T", "invariant", "incompleteness"],
)

# ---------------------------------------------------------------------------------------------
# (IV) with a phase (Vilmart's simplified scalar rule)

L = D()
L.e(L.z(0, 0, "alpha"), L.x(1, 0))
a, b = L.z(0, 1), L.x(1, 1)
L.e(a, b).e(a, b).e(a, b)
R = D()
rule(
    "inverse-scalar-phase", lhs=L, rhs=R,
    name="Inverse rule with a phase (IV)",
    aliases=["(IV)", "inverse rule", "parametrised inverse"],
    calculus="ZX", fragment="universal", group="scalars", order=21,
    summary="A Z-state with any phase α plugged into a phase-free X-effect, next to a Z- and X-spider connected by three wires, is the empty diagram.",
    description=(
        "A Z-spider with phase $\\alpha$ connected to a phase-free X-spider represents the scalar $\\sqrt2$ for "
        "every $\\alpha$, and a phase-free Z- and X-spider connected by three wires represent $\\frac1{\\sqrt2}$, so "
        "together they are the empty diagram. In particular the first scalar does not depend on $\\alpha$.\n\n"
        "In older axiomatisations the inverse rule (IV) appears without the phase. Vilmart showed that the version "
        "with an arbitrary phase $\\alpha$, together with the [Euler rule with a Hadamard](../euler-angles-hadamard/), "
        "can replace the Euler decomposition of the Hadamard, the [Euler-angle rule](../euler-angles/) and the "
        "[Clifford+T scalar rule (E)](../clifford-t-scalar/), giving a complete axiomatisation of the universal "
        "ZX-calculus with only seven rules."),
    variables={"alpha": "real"},
    scalar="1",
    source={"bib": VIL, "location": "Fig. 2, rule (IV)"},
    axiom_of=[VIL],
    related=[{"id": "clifford-t-scalar", "relation": "see-also"},
             {"id": "euler-angles-hadamard", "relation": "see-also"},
             {"id": "scalar-state-effect", "relation": "derived-from"},
             {"id": "scalar-inverse-sqrt2", "relation": "derived-from"}],
    tags=["scalar", "empty diagram", "inverse", "universal"],
)

# ---------------------------------------------------------------------------------------------
# (C): commutation of controls (Jeandel-Perdrix-Vilmart Clifford+T axiomatisation)

L = D()
i0, i4, i9 = L.b(0, 1), L.b(0, 2), L.b(0, 3)
n10 = L.x(1, 1, "-gamma")
n13 = L.z(1, 2)
n8 = L.x(2, 2, "gamma")
n11 = L.z(2, 1, "alpha")
n5 = L.z(2, 3, "beta")
n2 = L.z(3, 0, "alpha")
n6 = L.x(3, 1)
n3 = L.x(3, 3, 1)
n1 = L.z(3, 4, "beta")
n7 = L.z(4, 2)
o = L.b(5, 2)
L.e(i0, n10, n11, n6, n7, o).e(n6, n2).e(n7, n3, n1).e(n3, n5, i9).e(n11, n8, n5).e(i4, n13, n8).e(n13, n10)
R = D()
i15, i28, i25 = R.b(0, 1), R.b(0, 2), R.b(0, 3)
n18 = R.z(1, 2)
n26 = R.x(1, 3, "gamma")
n23 = R.z(2, 1, "beta")
n24 = R.x(2, 2, "-gamma")
n17 = R.z(2, 3, "alpha")
n27 = R.z(3, 0, "beta")
n22 = R.x(3, 1, 1)
n19 = R.x(3, 3)
n20 = R.z(3, 4, "alpha")
n16 = R.z(4, 2)
o = R.b(5, 2)
R.e(i25, n26, n17, n19, n16, o).e(n19, n20).e(n16, n22, n27).e(n22, n23, i15).e(n17, n24, n23).e(i28, n18, n24).e(n18, n26)
rule(
    "commutation-of-controls", lhs=L, rhs=R,
    name="Commutation of controls (C)",
    aliases=["(C)", "C rule", "commutation of controlled triangles"],
    calculus="ZX", fragment="universal", group="supplementarity", order=10,
    summary="One of the two new axioms of the Jeandel–Perdrix–Vilmart Clifford+T axiomatisation: a three-input diagram parametrised by α, β, γ is symmetric under exchanging the roles of α and β.",
    description=(
        "This is one of the two axioms that Jeandel, Perdrix and Vilmart added to the ZX-calculus to obtain the "
        "first complete axiomatisation for Clifford+T. It is parametrised by three arbitrary angles $\\alpha$, "
        "$\\beta$ and $\\gamma$ and holds for all of them. It arose from the translation between the ZX- and "
        "ZW-calculi used in the completeness proof and, as its name says, expresses that two *controlled* "
        "operations commute. When it was introduced, no derivation from the previous axioms was known.\n\n"
        "Going from left to right, the phases $\\alpha$ and $\\beta$ swap places, and the positions of $\\gamma$ "
        "and $-\\gamma$ are exchanged. Since the rule is *linear* in its parameters, it also holds in the universal "
        "fragment, where it remains an axiom of the complete axiomatisations of Jeandel, Perdrix and Vilmart."),
    variables={"alpha": "real", "beta": "real", "gamma": "real"},
    scalar="auto",
    source={"bib": JPV, "location": "Fig. 1, rule (C)"},
    also_in=[{"bib": JPVU, "location": "Fig. 1 and Fig. 2, rule (C)"},
             {"bib": LMCS, "location": "Fig. 2, rule (C)"}],
    axiom_of=[JPV, JPVU, LMCS],
    related=[{"id": "bw-rule", "relation": "see-also"}],
    tags=["clifford+t", "completeness", "axiom", "commutation", "controls", "triangle"],
)

# ---------------------------------------------------------------------------------------------
# (BW)

L = D()
i = L.b(0, 2)
n0 = L.z(1, 2)
n1 = L.x(1, 3)
n2 = L.z(0, 3.8, "1/4")
n3 = L.z(2, 3.8, "1/4")
n4 = L.x(2, 2)
n5 = L.z(2, 1, "1/4")
n6 = L.z(3, 2, "-1/2")
n14 = L.x(4, 2)
n13 = L.z(4, 1, "1/4")
n10 = L.z(5, 2)
n12 = L.x(5, 3)
n9 = L.z(4, 3.8, "1/4")
n8 = L.z(6, 3.8, "1/4")
o = L.b(7, 2)
L.e(i, n0, n4, n6, n14, n10, o).e(n0, n1).e(n1, n2).e(n1, n3).e(n4, n5).e(n14, n13).e(n10, n12).e(n12, n9).e(n12, n8)
R = D()
i = R.b(0, 2)
n24 = R.z(1, 2)
n18 = R.x(2, 2, 1)
n25 = R.z(3, 2, "1/4")
n19 = R.x(4, 2, "1/2")
o = R.b(5, 2)
n23 = R.x(1, 3, 1)
n22 = R.z(0, 3.8, "1/4")
n17 = R.z(2, 3.8, "1/4")
n20 = R.z(2, 1, "1/4")
R.e(i, n24, n18, n25, n19, o).e(n24, n23).e(n23, n22).e(n23, n17).e(n18, n20)
rule(
    "bw-rule", lhs=L, rhs=R,
    name="The (BW) rule",
    aliases=["(BW)", "BW rule", "black-white rule"],
    calculus="ZX", fragment="clifford+t", group="supplementarity", order=11,
    summary="The second new axiom of the Jeandel–Perdrix–Vilmart Clifford+T axiomatisation: a single-qubit identity between two diagrams with π/4 phase gadgets.",
    description=(
        "This is the second of the two axioms that Jeandel, Perdrix and Vilmart added to obtain the first complete "
        "axiomatisation of the Clifford+T ZX-calculus (the other one is [commutation of controls](../commutation-of-controls/)). "
        "Unlike (C) it is specific to the $\\frac\\pi4$ angle. Like (C) it arose from the translation between the ZX- "
        "and ZW-calculi used in the completeness proof, and the authors remark that it is \"hardly understandable "
        "as is\".\n\n"
        "Both sides are single-qubit maps built from Clifford+T phases and small phase gadgets with $\\frac\\pi4$ "
        "phases. No derivation of (BW) from the earlier axioms was known when it was introduced."),
    scalar="auto",
    source={"bib": JPV, "location": "Fig. 1, rule (BW)"},
    also_in=[{"bib": JPVU, "location": "Fig. 1 and Fig. 2, rule (BW)"},
             {"bib": LMCS, "location": "Fig. 2, rule (BW)"}],
    axiom_of=[JPV, JPVU, LMCS],
    related=[{"id": "commutation-of-controls", "relation": "see-also"}],
    tags=["clifford+t", "completeness", "axiom", "ZW", "T"],
)

# ---------------------------------------------------------------------------------------------
# Euler angles (EU)


def euler_angles(a1, a2, a3):
    """Vilmart's formulas for rule (EU): R_Z(a3) R_X(a2) R_Z(a1) = e^{i g} R_X(b3) R_Z(b2) R_X(b1)."""
    xp = (a1 + a3) / 2
    xm = xp - a3
    z = math.cos(a2 / 2) * math.cos(xp) + 1j * math.sin(a2 / 2) * math.cos(xm)
    zp = math.cos(a2 / 2) * math.sin(xp) - 1j * math.sin(a2 / 2) * math.sin(xm)
    b1 = arg(z) + arg(zp)
    b2 = 0.0 if abs(zp) < 1e-14 else 2 * arg(1j + abs(z / zp))
    b3 = arg(z) - arg(zp)
    g = xp - arg(z) + (a2 - b2) / 2
    return b1, b2, b3, g


def euler_angles_had(a1, a2):
    """Vilmart's formulas for rule (EU'): R_Z(a2) H R_Z(a1) = e^{i g} R_X(b3) R_Z(b2) R_X(b1)."""
    xp = (a1 + a2) / 2
    xm = xp - a2
    z = -math.sin(xp) + 1j * math.cos(xm)
    zp = math.cos(xp) - 1j * math.sin(xm)
    b1 = arg(z) + arg(zp)
    b2 = 0.0 if abs(zp) < 1e-14 else 2 * arg(1j + abs(z / zp))
    b3 = arg(z) - arg(zp)
    g = xp - arg(z) + (PI - b2) / 2
    return b1, b2, b3, g


def euler_diagrams(lhs_phases, rhs_phases, had=False):
    L = D()
    if had:
        z1, z2 = L.z(1, 0, lhs_phases[0]), L.z(2.2, 0, lhs_phases[1])
        L.e(L.b(0, 0), z1).he(z1, z2).e(z2, L.b(3.2, 0))
    else:
        L.e(L.b(0, 0), L.z(1, 0, lhs_phases[0]), L.x(2, 0, lhs_phases[1]), L.z(3, 0, lhs_phases[2]), L.b(4, 0))
    R = D()
    R.e(R.b(0, 0), R.x(1, 0, rhs_phases[0]), R.z(2, 0, rhs_phases[1]), R.x(3, 0, rhs_phases[2]), R.b(4, 0))
    return L, R


def self_test_euler(n=40):
    """Check the angle formulas on many random instances (the build only checks the stored instance)."""
    import numpy as np
    from zxrewrites import graphs

    def T(d):
        d.g.auto_detect_io()
        return graphs.tensor(d.g)

    rng = random.Random(7)
    for k in range(n):
        had = k % 2 == 1
        a = [rng.uniform(-PI, PI) for _ in range(2 if had else 3)]
        if had:
            b1, b2, b3, g = euler_angles_had(*a)
        else:
            b1, b2, b3, g = euler_angles(*a)
        L, R = euler_diagrams([frac(t) for t in a], [frac(b1), frac(b2), frac(b3)], had=had)
        if not np.allclose(T(L), cmath.exp(1j * g) * T(R), atol=1e-8):
            raise AssertionError(f"Euler formula fails for {a}")


self_test_euler()


def val(x):
    """A variable restricted to one value (a fraction string, or a float in units of pi, which is stored as a
    fraction with a large denominator because PyZX does not accept float phases)."""
    if isinstance(x, float):
        x = str(Fraction(x).limit_denominator(10 ** 9))
    return {"domain": "real", "values": [x]}


EU_A = ["1/3", "1/4", "3/5"]
b1, b2, b3, gm = euler_angles(*[float(Fraction(s)) * PI for s in EU_A])
L, R = euler_diagrams(["alpha1", "alpha2", "alpha3"], ["beta1", "beta2", "beta3"])
EU_CONDITIONS = (
    "β₁, β₂, β₃ and γ are functions of α₁, α₂, α₃: with x⁺ = (α₁+α₃)/2, x⁻ = x⁺ − α₃, "
    "z = cos(α₂/2)cos(x⁺) + i sin(α₂/2)cos(x⁻) and z′ = cos(α₂/2)sin(x⁺) − i sin(α₂/2)sin(x⁻), one takes "
    "β₁ = arg z + arg z′, β₂ = 2 arg(i + |z/z′|), β₃ = arg z − arg z′ and γ = x⁺ − arg z + (α₂ − β₂)/2, "
    "with the conventions arg(0) = 0 and β₂ = 0 when z′ = 0.")
rule(
    "euler-angles", lhs=L, rhs=R,
    name="Euler-angle rule (EU)",
    aliases=["(EU)", "(P)", "Euler rule", "colour swapping of Euler angles", "ZXZ = XZX", "Euler angles"],
    calculus="ZX", fragment="universal", group="hadamard", order=1,
    summary="A Z–X–Z sequence of rotations equals an X–Z–X sequence of rotations, with angles given by explicit (non-linear) formulas.",
    description=(
        "By Euler's rotation theorem every single-qubit unitary can be written both as a Z–X–Z and as an X–Z–X "
        "sequence of rotations. This rule makes that explicit: $R_Z(\\alpha_3)R_X(\\alpha_2)R_Z(\\alpha_1) = "
        "e^{i\\gamma}R_X(\\beta_3)R_Z(\\beta_2)R_X(\\beta_1)$, where the angles $\\beta_1,\\beta_2,\\beta_3$ and the "
        "global phase $\\gamma$ are the following functions of $\\alpha_1,\\alpha_2,\\alpha_3$. Let "
        "$x^+ = \\frac{\\alpha_1+\\alpha_3}2$, $x^- = x^+-\\alpha_3$, "
        "$z = \\cos\\frac{\\alpha_2}2\\cos x^+ + i\\sin\\frac{\\alpha_2}2\\cos x^-$ and "
        "$z' = \\cos\\frac{\\alpha_2}2\\sin x^+ - i\\sin\\frac{\\alpha_2}2\\sin x^-$. Then "
        "$\\beta_1 = \\arg z+\\arg z'$, $\\beta_2 = 2\\arg(i+|z/z'|)$, $\\beta_3 = \\arg z - \\arg z'$ and "
        "$\\gamma = x^+-\\arg z+\\frac{\\alpha_2-\\beta_2}2$.\n\n"
        "Coecke and Wang introduced the scalar-free version as rule (P), and showed that adding it makes the "
        "ZX-calculus complete for 2-qubit Clifford+T circuits; it necessarily leaves the Clifford+T fragment, since "
        "the angles $\\beta_i$ are generally not multiples of $\\pi/4$. Vilmart then showed that this single "
        "*non-linear* rule (with the scalar, which in the paper is drawn as a small diagram on the right-hand side) "
        "together with a few Clifford axioms and the [Clifford+T scalar rule (E)](../clifford-t-scalar/) is complete "
        "for the full ZX-calculus, replacing supplementarity and the axioms (C), (BW) and (A). A non-linear axiom "
        "like this one is necessary for completeness of the universal ZX-calculus.\n\n"
        "The stored instance is checked for $\\alpha_1=\\frac\\pi3$, $\\alpha_2=\\frac\\pi4$, $\\alpha_3=\\frac{3\\pi}5$ "
        "(the other angles computed from the formulas); the authoring script also checks the formulas on random angles."),
    variables={"alpha1": val(EU_A[0]), "alpha2": val(EU_A[1]), "alpha3": val(EU_A[2]),
               "beta1": val(b1 / PI), "beta2": val(b2 / PI), "beta3": val(b3 / PI), "gamma": val(gm / PI)},
    conditions=EU_CONDITIONS,
    scalar="exp(I*gamma)",
    source={"bib": CW, "location": "main theorem, rule (P)"},
    also_in=[{"bib": VIL, "location": "Fig. 1, rule (EU)"}],
    axiom_of=[CW, VIL],
    related=[{"id": "euler-angles-hadamard", "relation": "variant-of"},
             {"id": "euler-decomposition-hadamard", "relation": "see-also"},
             {"id": "supplementarity", "relation": "used-to-derive"}],
    tags=["euler", "euler angles", "non-linear", "universal", "completeness", "single qubit", "unitary"],
    notes="The build checks one generic instance of the angles (the variables are restricted to those values); "
          "`authoring/beyond_clifford.py` additionally verifies the formulas with PyZX on random angles.",
)

EUH_A = ["1/3", "2/7"]
b1, b2, b3, gm = euler_angles_had(*[float(Fraction(s)) * PI for s in EUH_A])
L, R = euler_diagrams(["alpha1", "alpha2"], ["beta1", "beta2", "beta3"], had=True)
rule(
    "euler-angles-hadamard", lhs=L, rhs=R,
    name="Euler-angle rule with a Hadamard (EU′)",
    aliases=["(EU')", "EU'", "Euler-Hadamard rule"],
    calculus="ZX", fragment="universal", group="hadamard", order=2,
    summary="A Z-rotation, a Hadamard and a Z-rotation equal an X–Z–X sequence of rotations, with angles given by explicit formulas.",
    description=(
        "A variant of the [Euler-angle rule](../euler-angles/) in which the middle X-rotation is replaced by a "
        "Hadamard gate: $R_Z(\\alpha_2)\\,H\\,R_Z(\\alpha_1) = e^{i\\gamma}R_X(\\beta_3)R_Z(\\beta_2)R_X(\\beta_1)$, "
        "where, with $x^+=\\frac{\\alpha_1+\\alpha_2}2$, $x^-=x^+-\\alpha_2$, $z=-\\sin x^+ + i\\cos x^-$ and "
        "$z' = \\cos x^+ - i\\sin x^-$: $\\beta_1=\\arg z+\\arg z'$, $\\beta_2 = 2\\arg(i+|z/z'|)$, "
        "$\\beta_3=\\arg z-\\arg z'$ and $\\gamma = x^+-\\arg z+\\frac{\\pi-\\beta_2}2$.\n\n"
        "Vilmart showed that this rule together with the [inverse rule with a phase](../inverse-scalar-phase/) can "
        "replace the Euler-angle rule (EU), the Euler decomposition of the Hadamard and the "
        "[Clifford+T scalar rule (E)](../clifford-t-scalar/). This gives a complete axiomatisation of the universal "
        "ZX-calculus with only seven rules: spider fusion, the two identity rules, (IV), copy, bialgebra, colour "
        "change and (EU′).\n\n"
        "The stored instance is checked for $\\alpha_1=\\frac\\pi3$, $\\alpha_2=\\frac{2\\pi}7$."),
    variables={"alpha1": val(EUH_A[0]), "alpha2": val(EUH_A[1]),
               "beta1": val(b1 / PI), "beta2": val(b2 / PI), "beta3": val(b3 / PI), "gamma": val(gm / PI)},
    conditions=("β₁, β₂, β₃ and γ are functions of α₁, α₂: with x⁺ = (α₁+α₂)/2, x⁻ = x⁺ − α₂, z = −sin(x⁺) + i cos(x⁻) "
                "and z′ = cos(x⁺) − i sin(x⁻), one takes β₁ = arg z + arg z′, β₂ = 2 arg(i + |z/z′|), "
                "β₃ = arg z − arg z′ and γ = x⁺ − arg z + (π − β₂)/2, with arg(0) = 0 and β₂ = 0 when z′ = 0."),
    scalar="exp(I*gamma)",
    source={"bib": VIL, "location": "Fig. 2, rule (EU')"},
    axiom_of=[VIL],
    related=[{"id": "euler-angles", "relation": "variant-of"},
             {"id": "euler-decomposition-hadamard", "relation": "generalises"},
             {"id": "inverse-scalar-phase", "relation": "see-also"}],
    tags=["euler", "euler angles", "hadamard", "non-linear", "universal", "completeness"],
    notes="The build checks one generic instance of the angles; `authoring/beyond_clifford.py` additionally verifies the formulas with PyZX on random angles.",
)

# ---------------------------------------------------------------------------------------------
# (A): the non-linear axiom of the first universal axiomatisation (JPV-universal)

A_al, A_be, A_t1, A_t2 = Fraction(1, 3), Fraction(1, 4), Fraction(1, 2), Fraction(1, 6)
S = cmath.exp(1j * PI * A_t1) * math.cos(PI * A_al) + cmath.exp(1j * PI * A_t2) * math.cos(PI * A_be)
A_ga = math.acos(abs(S) / 2) / PI
A_t3 = arg(S) / PI
L = D()
n4 = L.x(1, 0)
n5 = L.x(1, 2)
L.e(L.z(0, -0.5, "-alpha"), n4).e(L.z(0, 0.5, "alpha"), n4)
L.e(L.z(0, 1.5, "beta"), n5).e(L.z(0, 2.5, "-beta"), n5)
n3 = L.z(2, 0, "theta1")
n2 = L.z(2, 2, "theta2")
n16 = L.x(3, 0)
n0 = L.x(3, 2)
n18 = L.z(3, 1)
n17 = L.x(2, 1, "1/2")
n19 = L.z(4, 0, "1/4")
n20 = L.z(4, 2, "1/4")
n21 = L.x(5, 1)
L.e(n4, n3, n16, n19, n21).e(n5, n2, n0, n20, n21).e(n16, n18, n0).e(n18, n17).e(n21, L.b(6, 1))
R = D()
n11 = R.x(1.5, 0.4)
n23 = R.x(1.5, 1.6)
n22 = R.z(2.5, 1, "theta3")
R.e(R.z(0.5, 0, "gamma"), n11).e(R.z(0.5, 0.8, "-gamma"), n11)
R.e(R.z(0.5, 1.2, "1/4"), n23).e(R.z(0.5, 2, "1/4"), n23)
R.e(n11, n22).e(n23, n22).e(n22, R.b(3.5, 1))
rule(
    "addition-rule", lhs=L, rhs=R,
    name="The non-linear axiom (A)",
    aliases=["(A)", "A rule", "addition axiom", "sum rule"],
    calculus="ZX", fragment="universal", group="supplementarity", order=12,
    summary="Two single-qubit states built from angles α, β, θ₁, θ₂ are added together, giving a state of the same shape with angles γ, θ₃ where 2e^{iθ₃}cos γ = e^{iθ₁}cos α + e^{iθ₂}cos β.",
    description=(
        "The first complete axiomatisation of the universal (pure qubit) ZX-calculus without extra generators, "
        "by Jeandel, Perdrix and Vilmart, consists of their Clifford+T axioms plus this single rule (A). The "
        "left-hand side joins two branches, parametrised by $(\\alpha,\\theta_1)$ and $(\\beta,\\theta_2)$, and the "
        "right-hand side is a single branch of the same shape parametrised by $(\\gamma,\\theta_3)$. The rule holds under the side condition "
        "$2e^{i\\theta_3}\\cos\\gamma = e^{i\\theta_1}\\cos\\alpha+e^{i\\theta_2}\\cos\\beta$.\n\n"
        "Because of this side condition the rule is *non-linear* in the angles. The authors proved that any complete "
        "axiomatisation of the universal ZX-calculus that extends the Clifford+T one needs either a non-linear "
        "rule or constants that are not multiples of $\\pi/4$: all rules that are linear in their angles with "
        "$\\pi/4$ constants already follow from the Clifford+T axioms. In later work (A) was superseded by "
        "the [Euler-angle rule](../euler-angles/).\n\n"
        "The stored instance is checked for $\\alpha=\\frac\\pi3$, $\\beta=\\frac\\pi4$, $\\theta_1=\\frac\\pi2$, "
        "$\\theta_2=\\frac\\pi6$, with $\\gamma$ and $\\theta_3$ computed from the side condition."),
    variables={"alpha": val(str(A_al)), "beta": val(str(A_be)), "theta1": val(str(A_t1)), "theta2": val(str(A_t2)),
               "gamma": val(A_ga), "theta3": val(A_t3)},
    conditions="2e^{iθ₃} cos γ = e^{iθ₁} cos α + e^{iθ₂} cos β.",
    scalar="auto",
    source={"bib": JPVU, "location": "Fig. 2, rule (A)"},
    also_in=[{"bib": LMCS, "location": "Fig. 3, rule (A)"}],
    axiom_of=[JPVU, LMCS],
    related=[{"id": "euler-angles", "relation": "see-also"},
             {"id": "commutation-of-controls", "relation": "see-also"}],
    tags=["non-linear", "universal", "completeness", "axiom", "addition", "side condition"],
    notes="The build checks one instance satisfying the side condition (the variables are restricted to those values).",
)

# ---------------------------------------------------------------------------------------------
# Spider nests


def gadget_nest(n_wires, terms, x0=1.0, step=1.6, wire_phase=None, gap=1.0):
    """Wires with phase gadgets (two-colour form): for each (subset, phase) a Z-spider on every wire of the subset,
    an X-spider hub and a Z-spider leaf carrying the phase.  ``wire_phase`` puts a phase on every wire first."""
    G = D()
    last = [G.b(0, i * gap) for i in range(n_wires)]
    x = x0
    if wire_phase is not None:
        for i in range(n_wires):
            z = G.z(x, i * gap, wire_phase)
            G.e(last[i], z)
            last[i] = z
        x += 1.0
    for subset, phase in terms:
        ys = [i * gap for i in subset]
        yh = (min(ys) + max(ys)) / 2
        if abs(yh / gap - round(yh / gap)) < 1e-9:
            yh += gap / 2 if yh < (n_wires - 1) * gap else -gap / 2
        hub = G.x(x + 0.55, yh)
        G.e(hub, G.z(x + 1.0, yh, phase))
        for i in subset:
            z = G.z(x, i * gap)
            G.e(last[i], z).e(z, hub)
            last[i] = z
        x += step
    for i in range(n_wires):
        G.e(last[i], G.b(x + 0.2, i * gap))
    return G


def wires(n, length=2, gap=1.0):
    G = D()
    for i in range(n):
        G.e(G.b(0, i * gap), G.b(length, i * gap))
    return G


from itertools import combinations  # noqa: E402

nest4 = [(s, "-1/4") for s in combinations(range(4), 2)] + [(s, "1/4") for s in combinations(range(4), 3)] \
    + [((0, 1, 2, 3), "-1/4")]
R = gadget_nest(4, nest4, wire_phase="1/4")
L = wires(4)
rule(
    "spider-nest", lhs=L, rhs=R,
    name="Spider nest identity",
    aliases=["spider nest", "4-qubit spider nest", "phase gadget nest"],
    calculus="ZX", fragment="clifford+t", group="spider-nests", order=1,
    summary="On four qubits, the product of π/4 phase gadgets on all non-empty subsets of qubits, with sign (−1)^(k+1) for gadgets of size k, is the identity.",
    description=(
        "A *spider nest* is a collection of [phase gadgets](../phase-gadget-fusion/) that multiplies to the "
        "identity. On four qubits, taking a gadget with phase $\\frac\\pi4$ on every qubit, $-\\frac\\pi4$ on every "
        "pair, $\\frac\\pi4$ on every triple and $-\\frac\\pi4$ on all four gives the identity. This follows from "
        "the identity $\\sum_{\\emptyset\\neq S\\subseteq[n]} (-1)^{|S|+1}\\,\\bigoplus_{i\\in S}x_i = "
        "2^{n-1}x_1\\cdots x_n$ for bit strings $x$, so that for $n=4$ the total phase is a multiple of $2\\pi$.\n\n"
        "Munson, Coecke and Wang derived the spider nest identities for all $n$ from a decomposition of phase gadgets "
        "into AND gates: an $n$-qubit $\\frac\\pi4$-gadget equals a product of 1-gadgets with phase "
        "$\\frac{(n-2)(n-3)\\pi}8$, 2-gadgets with phase $\\frac{(3-n)\\pi}4$ and 3-gadgets with phase $\\frac\\pi4$, "
        "and moving the $n$-gadget to the other side gives the nest. Spider nests are used by de Beaudrap, Bian and "
        "Wang to reduce the T-count of circuits: whenever a circuit contains more than half of a nest, it can be "
        "replaced by the inverse of the other half."),
    parameters={"n": 4},
    parameter_notes="Shown for n = 4 qubits, where the gadget phases are ±π/4. For other n the 1- and 2-gadget phases depend on n, and the n-gadget has phase −π/4.",
    scalar="auto",
    source={"bib": "Munson2019ANDgates", "location": "Section 5, spider nest identities (following the corollary on decomposing π/4 phase gadgets)"},
    also_in=[{"bib": "deBeaudrapN2020treducspidernest"}],
    related=[{"id": "spider-nest-clifford", "relation": "see-also"},
             {"id": "phase-gadget-fusion", "relation": "see-also"}],
    tags=["spider nest", "phase gadget", "T-count", "optimisation", "parity", "clifford+t"],
)

nest3 = [(s, "-1/2") for s in combinations(range(3), 2)] + [((0, 1, 2), "1/2")]
L = gadget_nest(3, nest3, wire_phase="1/2", gap=1.2)
R = wires(3, gap=1.2)
rule(
    "spider-nest-clifford", lhs=L, rhs=R,
    name="Three-qubit Clifford spider nest",
    aliases=["π/2 spider nest", "3-qubit spider nest"],
    calculus="ZX", fragment="clifford", group="spider-nests", order=2,
    summary="On three qubits, π/2 phases on every qubit, −π/2 gadgets on every pair and a π/2 gadget on all three give the identity.",
    description=(
        "The three-qubit analogue of the [spider nest identity](../spider-nest/) with phases $\\pm\\frac\\pi2$: a "
        "$\\frac\\pi2$ phase on each qubit, a $-\\frac\\pi2$ phase gadget on each pair of qubits and a $\\frac\\pi2$ "
        "gadget on all three qubits multiply to the identity (up to a scalar), because "
        "$\\sum_{S}(-1)^{|S|+1}\\bigoplus_{i\\in S}x_i = 4x_1x_2x_3$ and $\\frac\\pi2\\cdot 4 = 2\\pi$.\n\n"
        "As all the phases are Clifford, this identity can be proven with the Clifford rules, for instance by "
        "fusing and colour-changing until local complementation removes all the $\\pm\\frac\\pi2$ spiders. The "
        "analogous identity with $\\frac\\pi4$ phases on three qubits is instead the CCZ gate."),
    scalar="auto",
    source={"bib": BOOK},
    related=[{"id": "spider-nest", "relation": "see-also"},
             {"id": "local-complementation", "relation": "see-also"}],
    tags=["spider nest", "phase gadget", "clifford", "S gate"],
)

# ---------------------------------------------------------------------------------------------
# Catalysis: a CS gate and a |T> catalyst implement a T gate

L = D()
t0 = [L.z(1, 0), L.z(2, 0), L.z(4, 0), L.z(5, 0, "1/4")]
b0 = [L.x(1, 1), L.x(2, 1), L.z(3, 1, "-1/4"), L.x(4, 1), L.z(5, 1, "1/4")]
L.e(L.b(0, 0), *t0, L.b(6, 0))
L.e(L.z(0, 1, "1/4"), *b0, L.b(6, 1))
L.e(t0[0], b0[0]).e(t0[1], b0[1]).e(t0[2], b0[3])
R = D()
R.e(R.b(0, 0), R.z(1, 0, "1/4"), R.b(2, 0))
R.e(R.z(1, 1, "1/4"), R.b(2, 1))
rule(
    "t-catalysis-cs", lhs=L, rhs=R,
    name="T gate by catalysis with a CS gate",
    aliases=["catalysis", "T catalysis", "CS catalysis", "catalytic T gate"],
    calculus="ZX", fragment="clifford+t", group="circuits", order=40,
    summary="A CNOT followed by a controlled-S gate, acting on a qubit and a |T⟩ state, applies a T gate to the qubit and returns the |T⟩ state unchanged.",
    description=(
        "Using a single copy of the magic state $\\ket{T} = \\ket{0}+e^{i\\pi/4}\\ket{1}$ as a *catalyst*, a T gate "
        "can be implemented with Clifford gates and one controlled-S (CS) gate: apply a CNOT from the qubit to the "
        "catalyst, followed by CS. Here the CS gate $=\\mathrm{CZ}(\\frac\\pi2)$ is written in its standard "
        "decomposition into two CNOTs, a $-\\frac\\pi4$ phase on the target and $\\frac\\pi4$ phases on both qubits. "
        "The two adjacent CNOTs cancel, the $-\\frac\\pi4$ phase turns the catalyst into $\\ket{+}$, which the last "
        "CNOT leaves unchanged, and the final $\\frac\\pi4$ phases apply a T gate to the qubit and restore the "
        "catalyst.\n\n"
        "Because the catalyst is returned unchanged, one $\\ket{T}$ state suffices to replace every T gate of a "
        "Clifford+T circuit by a Clifford+CS circuit. Kissinger, Ross and van de Wetering use this kind of catalysis "
        "to build complete axiomatisations from the phase-free ZH-calculus by adjoining catalysis rules."),
    scalar="auto",
    source={"bib": "kissinger2024catalysing", "location": "Section 1, example: a CS gate and a |T⟩ catalyst apply a T gate"},
    related=[{"id": "phase-gadget-fusion", "relation": "see-also"}],
    tags=["catalysis", "magic state", "T gate", "CS gate", "controlled phase", "circuit", "clifford+t"],
)

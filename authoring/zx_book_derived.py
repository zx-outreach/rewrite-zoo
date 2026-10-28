"""More ZX rules from the book's cheatsheets (Tables 8.1, 8.2) and the graph-theoretic simplification
paper (local complementation, pivoting, phase gadgets)."""

from dsl import D, rule, spread

BOOK_T1 = {"bib": "KissingervdWeteringbook", "location": "Chapter 8, Table 8.1 (basic rewrite rules)"}
BOOK_T2 = {"bib": "KissingervdWeteringbook", "location": "Chapter 8, Table 8.2 (derived rewrite rules)"}
BOOK_CS = {"bib": "KissingervdWeteringbook", "location": "Section 8.1.4 (ZX-calculus full cheatsheet)"}
WORKING = {"bib": "vandewetering2020zxcalculus"}
GTS = "duncan2019graph"

# ---------------------------------------------------------------------------------------------
# Bialgebra

L = D()
x = L.x(1, 0.5)
z = L.z(2, 0.5)
L.ins(x, [0, 1]).e(x, z).outs(z, [0, 1], x=3)
R = D()
zs = [R.z(1, y) for y in (0, 1)]
xs = [R.x(2, y) for y in (0, 1)]
for y, zz in zip((0, 1), zs):
    R.e(R.b(0, y), zz)
for y, xx in zip((0, 1), xs):
    R.e(xx, R.b(3, y))
for zz in zs:
    for xx in xs:
        R.e(zz, xx)
rule(
    "bialgebra", lhs=L, rhs=R,
    name="Bialgebra",
    aliases=["strong complementarity", "bialgebra rule", "(b)"],
    calculus="ZX", fragment="phase-free", group="bialgebra", order=1,
    summary="A phase-free X-spider followed by a phase-free Z-spider can be commuted past one another.",
    description=(
        "The bialgebra rule expresses that the Z- and X-spiders form a (scaled) bialgebra, which is also called "
        "*strong complementarity*. A two-input X-spider (XOR) followed by a two-output Z-spider (COPY) is equal to "
        "first copying both inputs and then taking XORs pairwise. This is one of the main reasons that the "
        "phase-free fragment is so expressive: it captures the interaction of XOR and COPY, i.e. linear maps over "
        "the field with two elements.\n\n"
        "See the [generalised bialgebra](../bialgebra-generalised/) rule for spiders with any number of legs."),
    scalar="sqrt(2)",
    source={"bib": "CD1"},
    also_in=[BOOK_T1, WORKING],
    related=[{"id": "bialgebra-generalised", "relation": "special-case-of"},
             {"id": "hopf", "relation": "see-also"},
             {"id": "state-copy", "relation": "see-also"}],
    tags=["strong complementarity", "bialgebra", "XOR", "COPY", "CNOT"],
)

n, m = 2, 3
L = D()
x = L.x(1, 1)
z = L.z(2, 1)
L.ins(x, spread(n, 1, 1.2)).e(x, z).outs(z, spread(m, 1, 1), x=3)
R = D()
zs = [R.z(1, y) for y in spread(n, 1, 1.2)]
xs = [R.x(2.4, y) for y in spread(m, 1, 1)]
for y, zz in zip(spread(n, 1, 1.2), zs):
    R.e(R.b(0, y), zz)
for y, xx in zip(spread(m, 1, 1), xs):
    R.e(xx, R.b(3.4, y))
for zz in zs:
    for xx in xs:
        R.e(zz, xx)
rule(
    "bialgebra-generalised", lhs=L, rhs=R,
    name="Generalised bialgebra",
    aliases=["strong complementarity", "bialgebra with many legs", "complete bipartite bialgebra"],
    calculus="ZX", fragment="phase-free", group="bialgebra", order=2,
    summary="A phase-free X-spider with n inputs connected to a phase-free Z-spider with m outputs becomes a complete bipartite graph.",
    description=(
        "The general form of [strong complementarity](../bialgebra/): an X-spider with n inputs connected to a "
        "Z-spider with m outputs is equal to n Z-spiders and m X-spiders connected as a complete bipartite "
        "graph, with scalar $\\sqrt{2}^{(n-1)(m-1)}$. It follows from the 2-by-2 bialgebra rule and spider fusion.\n\n"
        "In the special cases where n or m is 0 or 1 it reduces to state copying and identity removal."),
    parameters={"n": n, "m": m},
    parameter_notes="n inputs and m outputs (shown for n = 2, m = 3).",
    scalar="sqrt(2)**((n-1)*(m-1))",
    source={"bib": "KissingervdWeteringbook", "location": "Chapter 8, Table 8.1 (strong complementarity)"},
    also_in=[WORKING],
    related=[{"id": "bialgebra", "relation": "generalises"},
             {"id": "state-copy", "relation": "see-also"}],
    tags=["strong complementarity", "bialgebra", "complete bipartite"],
)

# ---------------------------------------------------------------------------------------------
# Hopf

L = D()
z = L.z(1, 0)
x = L.x(2.2, 0)
L.e(L.b(0, 0), z).e(z, x).e(z, x).e(x, L.b(3.2, 0))
R = D()
z = R.z(1, 0)
x = R.x(2.2, 0)
R.e(R.b(0, 0), z).e(x, R.b(3.2, 0))
rule(
    "hopf", lhs=L, rhs=R,
    name="Hopf rule",
    aliases=["complementarity", "Hopf law", "(ho)"],
    calculus="ZX", fragment="phase-free", group="bialgebra", order=3,
    summary="A Z- and X-spider connected by two wires disconnect.",
    description=(
        "When a Z-spider and an X-spider are connected by two wires, both wires can be removed. This expresses "
        "that the Z- and X-bases are *complementary* (mutually unbiased). More generally, spiders of opposite "
        "colour connected by k wires can have their connection reduced to k mod 2 wires.\n\n"
        "The Hopf rule follows from the bialgebra rule together with the other phase-free rules."),
    scalar="1/2",
    source={"bib": "CD1"},
    also_in=[BOOK_T1, WORKING],
    related=[{"id": "hadamard-hopf", "relation": "variant-of"},
             {"id": "bialgebra", "relation": "see-also"}],
    tags=["complementarity", "hopf", "parallel edges"],
)

L = D()
z1 = L.z(1, 0.5, "alpha")
z2 = L.z(2.4, 0.5, "beta")
L.ins(z1, [0, 1]).outs(z2, [0, 1], x=3.4)
L.he(z1, z2).he(z1, z2)
R = D()
z1 = R.z(1, 0.5, "alpha")
z2 = R.z(2.4, 0.5, "beta")
R.ins(z1, [0, 1]).outs(z2, [0, 1], x=3.4)
rule(
    "hadamard-hopf", lhs=L, rhs=R,
    name="Hopf rule for Hadamard edges",
    aliases=["Hadamard Hopf", "parallel Hadamard edge removal"],
    calculus="ZX", fragment="universal", group="bialgebra", order=4,
    summary="Two spiders of the same colour connected by two Hadamard edges disconnect.",
    description=(
        "Two spiders of the same colour connected by a pair of parallel Hadamard edges are equal to the two "
        "spiders without those edges. This is the [Hopf rule](../hopf/) after a colour change. In graph-like "
        "diagrams it means that parallel Hadamard edges cancel in pairs, so graph-like diagrams can be taken "
        "to be simple graphs."),
    variables={"alpha": "real", "beta": "real"},
    parameter_notes="Shown for spiders with two other legs each; holds for any number of legs.",
    scalar="1/2",
    source={"bib": GTS},
    also_in=[BOOK_T2],
    related=[{"id": "hopf", "relation": "derived-from"},
             {"id": "colour-change", "relation": "derived-from"}],
    tags=["hopf", "hadamard edge", "parallel edges", "graph-like"],
)

# ---------------------------------------------------------------------------------------------
# Hadamard self-loop

L = D()
z = L.z(1, 0, "alpha")
L.wire(0, 0, 2, z)
L.he(z, z)
R = D()
z = R.z(1, 0, "alpha+1")
R.wire(0, 0, 2, z)
rule(
    "hadamard-self-loop-removal", lhs=L, rhs=R,
    name="Hadamard self-loop removal",
    aliases=["Hadamard loop removal"],
    calculus="ZX", fragment="universal", group="spiders", order=4,
    summary="A self-loop containing a Hadamard can be removed by adding π to the phase.",
    description=(
        "A spider that is connected to itself through a Hadamard gate is equal, up to a scalar, to the same spider "
        "without the loop and with π added to its phase. This rule is needed to bring diagrams into graph-like form, "
        "where self-loops are not allowed."),
    variables={"alpha": "real"},
    parameter_notes="Shown for a spider with one input and one output; holds for any number of legs.",
    scalar="auto",
    source={"bib": GTS},
    also_in=[BOOK_T2],
    related=[{"id": "self-loop-removal", "relation": "variant-of"}],
    tags=["self-loop", "hadamard edge", "graph-like"],
)

# ---------------------------------------------------------------------------------------------
# Y-state

L = D()
L.e(L.x(1, 0, "-1/2"), L.b(2, 0))
R = D()
R.e(R.z(1, 0, "1/2"), R.b(2, 0))
rule(
    "y-state", lhs=L, rhs=R,
    name="Y-state identity",
    aliases=["S-state equality", "Y eigenstate"],
    calculus="ZX", fragment="clifford", group="euler", order=10,
    summary="The two ways of writing the Pauli Y eigenstate as a single spider are equal up to a global phase.",
    description=(
        "An X-spider with phase −π/2 and a Z-spider with phase π/2, each with a single leg, both represent the "
        "+1 eigenstate of the Pauli Y operator, and are equal up to the global phase $e^{-i\\pi/4}$."),
    scalar="auto",
    source={"bib": "KissingervdWeteringbook", "location": "Chapter 8, Table 8.2 (cf. Exercise 3.15)"},
    related=[{"id": "euler-decomposition-hadamard", "relation": "see-also"}],
    tags=["Y eigenstate", "S state", "clifford", "pauli Y"],
)

# ---------------------------------------------------------------------------------------------
# Euler decompositions of the Hadamard

L = D()
L.he(L.b(0, 0), L.b(2, 0))
R = D()
a, b, c = R.z(1, 0, "1/2"), R.x(2, 0, "1/2"), R.z(3, 0, "1/2")
R.e(R.b(0, 0), a, b, c, R.b(4, 0))
rule(
    "euler-decomposition-hadamard", lhs=L, rhs=R,
    name="Euler decomposition of the Hadamard",
    aliases=["(EU)", "Hadamard decomposition", "H = SVS", "(H) Euler"],
    calculus="ZX", fragment="clifford", group="hadamard", order=3,
    summary="The Hadamard gate is a sequence of three π/2 rotations, Z–X–Z.",
    description=(
        "Up to a global phase, the Hadamard gate is equal to a π/2 Z-rotation, followed by a π/2 X-rotation, followed "
        "by a π/2 Z-rotation. By colour-swapping, also H = X(π/2) Z(π/2) X(π/2); by conjugating, the same holds with "
        "all phases −π/2 (with the inverse global phase).\n\n"
        "This rule is what makes the Hadamard derivable from the spiders, so that in the Clifford fragment the "
        "Hadamard does not need to be a separate generator."),
    scalar="exp(-I*pi/4)",
    source={"bib": "DuncanPerdrixGraphStates"},
    also_in=[{"bib": "KissingervdWeteringbook", "location": "Section 8.1.1 (generators)"}, WORKING],
    related=[{"id": "hadamard-gadget-decomposition", "relation": "variant-of"},
             {"id": "colour-change", "relation": "see-also"},
             {"id": "local-complementation", "relation": "see-also"}],
    tags=["euler", "hadamard", "clifford"],
)

L = D()
L.he(L.b(0, 0), L.b(2, 0))
R = D()
a, b, c = R.z(1, 0, "1/2"), R.x(2, 0), R.z(3, 0, "1/2")
R.e(R.b(0, 0), a, b, c, R.b(4, 0))
R.e(b, R.z(2, -1, "-1/2"))
rule(
    "hadamard-gadget-decomposition", lhs=L, rhs=R,
    name="Hadamard as a phase gadget",
    aliases=["Euler decomposition with a gadget"],
    calculus="ZX", fragment="clifford", group="hadamard", order=4,
    summary="The Hadamard gate is two π/2 Z-rotations around an X-spider with a −π/2 leg.",
    description=(
        "A variant of the [Euler decomposition of the Hadamard](../euler-decomposition-hadamard/) in which the middle "
        "X-rotation is unfused into a phase-free X-spider with a −π/2 Z-spider attached to it."),
    scalar="auto",
    source={"bib": "KissingervdWeteringbook", "location": "Section 8.1.1 (generators)"},
    related=[{"id": "euler-decomposition-hadamard", "relation": "variant-of"}],
    tags=["euler", "hadamard", "phase gadget"],
)

# ---------------------------------------------------------------------------------------------
# Phase gadget fusion (two-colour form, as in the book)

def gadget_targets(Dg, xs=(1, 3)):
    ts = []
    for i, y in enumerate((2.0, 3.0)):
        t = Dg.z(2, y, f"gamma{i+1}")
        Dg.e(Dg.b(0, y), t).e(t, Dg.b(4, y))
        ts.append(t)
    return ts

L = D()
ts = gadget_targets(L)
for x, ph in ((1.5, "alpha"), (2.5, "beta")):
    hub = L.x(x, 1)
    L.e(hub, L.z(x, 0, ph))
    for t in ts:
        L.e(hub, t)
R = D()
ts = gadget_targets(R)
hub = R.x(2, 1)
R.e(hub, R.z(2, 0, "alpha+beta"))
for t in ts:
    R.e(hub, t)
rule(
    "phase-gadget-fusion", lhs=L, rhs=R,
    name="Phase gadget fusion",
    aliases=["gadget fusion", "(gf)"],
    calculus="ZX", fragment="universal", group="phase-gadgets", order=1,
    summary="Two phase gadgets on the same set of spiders fuse together, and their phases add.",
    description=(
        "A *phase gadget* is a phase-free X-spider connected to a number of Z-spiders, with one extra leg "
        "ending in a Z-spider carrying a phase. Phase gadgets represent diagonal unitaries: a gadget connected to "
        "qubits $q_1,\\ldots,q_n$ with phase α implements $e^{-i\\frac{\\alpha}{2} Z\\otimes\\cdots\\otimes Z}$ (up to "
        "a global phase). Two phase gadgets connected to exactly the same set of spiders fuse into a single gadget "
        "whose phase is the sum of the two.\n\n"
        "This is the basis of the phase-teleportation T-count optimisation of PyZX."),
    variables={"alpha": "real", "beta": "real", "gamma1": "real", "gamma2": "real"},
    parameters={"n": 2},
    parameter_notes="n is the number of spiders the gadgets are connected to (shown for n = 2).",
    scalar="sqrt(2)**(-(n-1))",
    source={"bib": "kissinger2019tcount"},
    also_in=[BOOK_T2, {"bib": GTS}],
    related=[{"id": "spider-fusion", "relation": "derived-from"},
             {"id": "bialgebra-generalised", "relation": "derived-from"},
             {"id": "identity-gadget-removal", "relation": "see-also"}],
    tags=["phase gadget", "fusion", "T-count", "phase polynomial"],
)

# graph-like identity-gadget removal (gadget-id-simp)
L = D()
b = L.z(2, 1, "beta")
L.ins(b, [0.5, 1.5]).outs(b, [0.5, 1.5], x=3)
hub = L.z(2, 0)
L.he(b, hub).he(hub, L.z(2, -1, "alpha"))
R = D()
r = R.z(2, 1, "alpha+beta")
R.ins(r, [0.5, 1.5]).outs(r, [0.5, 1.5], x=3)
rule(
    "identity-gadget-removal", lhs=L, rhs=R,
    name="Gadget fusion into a spider",
    aliases=["identity gadget removal", "arity-1 gadget fusion"],
    calculus="ZX", fragment="universal", group="phase-gadgets", order=2, view="graph-like",
    summary="A phase gadget attached to a single spider fuses into that spider.",
    description=(
        "A phase gadget that is connected to just one spider is simply a phase on that spider: the gadget's phase is "
        "added to the phase of the spider. In graph-like form the gadget is a phase-free Z-spider connected by "
        "Hadamard edges both to the spider and to the gadget's phase."),
    variables={"alpha": "real", "beta": "real"},
    scalar="auto",
    source={"bib": "KissingervdWeteringbook", "location": "Chapter 7 (phase gadgets)"},
    related=[{"id": "phase-gadget-fusion", "relation": "see-also"}],
    tags=["phase gadget", "graph-like", "fusion"],
)

# ---------------------------------------------------------------------------------------------
# Local complementation simplification (lc-simp)

nb_pos = [(1.6, 0), (2.2, 1), (1.6, 2)]


def lc_neighbours(Dg, phases):
    vs = []
    for (x, y), ph in zip(nb_pos, phases):
        v = Dg.z(x, y, ph)
        Dg.e(v, Dg.b(3.2, y))
        vs.append(v)
    return vs

L = D()
c = L.z(0.4, 1, "1/2")
vs = lc_neighbours(L, ["alpha1", "alpha2", "alpha3"])
for v in vs:
    L.he(c, v)
R = D()
vs = lc_neighbours(R, ["alpha1-1/2", "alpha2-1/2", "alpha3-1/2"])
R.he(vs[0], vs[1]).he(vs[1], vs[2]).he(vs[0], vs[2])
rule(
    "local-complementation", lhs=L, rhs=R,
    name="Local complementation simplification",
    aliases=["LC", "lcomp", "local complementation rule", "proper Clifford spider removal"],
    calculus="ZX", fragment="universal", group="local-complementation", order=1, view="graph-like",
    summary="An internal spider with phase ±π/2 can be removed by complementing the connectivity of its neighbours.",
    description=(
        "In a graph-like diagram, an internal spider with phase π/2 (or −π/2) can be removed. Every pair of its "
        "neighbours that was connected becomes disconnected and vice versa, and π/2 is subtracted from (or "
        "added to) the phase of every neighbour. This is the graph-theoretic operation of *local complementation*.\n\n"
        "The rule is derived from the local complementation rule for graph states of Duncan & Perdrix, followed by "
        "spider fusion. It is one of the two main simplification rules of PyZX, together with "
        "[pivoting](../pivot/)."),
    variables={"alpha1": "real", "alpha2": "real", "alpha3": "real"},
    parameters={"n": 3},
    parameter_notes="n is the number of neighbours (shown for n = 3). The neighbours may have any number of further legs and edges.",
    scalar="exp(I*pi/4)*sqrt(2)**((n-1)*(n-2)/2)",
    source={"bib": GTS},
    also_in=[BOOK_T2],
    related=[{"id": "pivot", "relation": "see-also"},
             {"id": "euler-decomposition-hadamard", "relation": "derived-from"}],
    tags=["local complementation", "graph-like", "simplification", "clifford"],
)

# ---------------------------------------------------------------------------------------------
# Pivot simplification (pivot-simp), with |U| = 2, |shared| = 1, |V| = 2


def pivot_side(Dg, phases, pos=((2.6, 0), (2.6, 1), (2.0, 2), (3.4, 3), (3.4, 4))):
    """neighbour spiders: two only of u (top), one shared (middle), two only of v (bottom)"""
    vs = []
    for (x, y), ph in zip(pos, phases):
        v = Dg.z(x, y, ph)
        Dg.e(v, Dg.b(4.6, y))
        vs.append(v)
    return vs

L = D(bools="j k")
u = L.z(1, 1, "j")
v = L.z(1, 3, "k")
L.he(u, v)
a1, a2, b1, c1, c2 = pivot_side(L, ["alpha1", "alpha2", "beta", "gamma1", "gamma2"])
for w in (a1, a2, b1):
    L.he(u, w)
for w in (b1, c1, c2):
    L.he(v, w)
R = D(bools="j k")
a1, a2, b1, c1, c2 = pivot_side(R, ["alpha1+k", "alpha2+k", "beta+j+k+1", "gamma1+j", "gamma2+j"],
                                 pos=((1.6, 0), (2.2, 1), (0.6, 2), (2.2, 3), (1.6, 4)))
for x in (a1, a2):
    for y in (b1, c1, c2):
        R.he(x, y)
for y in (c1, c2):
    R.he(b1, y)
rule(
    "pivot", lhs=L, rhs=R,
    name="Pivot simplification",
    aliases=["pivoting", "pivot rule", "Pauli pair removal"],
    calculus="ZX", fragment="universal", group="pivoting", order=1, view="graph-like",
    summary="Two connected internal spiders with Pauli phases can be removed by complementing the edges between their neighbourhoods.",
    description=(
        "In a graph-like diagram, two connected internal spiders u and v with phases jπ and kπ can be removed. "
        "Their neighbours fall into three groups: those connected only to u, those connected to both, and those "
        "connected only to v. Every pair of spiders taken from two *different* groups has its connectivity toggled "
        "(this is the graph-theoretic *pivot* along the edge uv). The neighbours of only u get kπ added to their "
        "phase, those of only v get jπ, and the shared neighbours get (j+k+1)π.\n\n"
        "The rule follows from three local complementations. Together with "
        "[local complementation](../local-complementation/) it is the main simplification rule of PyZX."),
    variables={"j": "boolean", "k": "boolean", "alpha1": "real", "alpha2": "real", "beta": "real",
               "gamma1": "real", "gamma2": "real"},
    parameters={"n_u": 2, "n_w": 1, "n_v": 2},
    parameter_notes=("n_u, n_w and n_v are the numbers of neighbours of only u, of both, and of only v (shown for "
                     "n_u = 2, n_w = 1, n_v = 2). The neighbours may have any number of further legs and edges."),
    scalar="(-1)**(j*k)*sqrt(2)**((n_u-1)*(n_v-1)+n_w*(n_u+n_v-2))",
    source={"bib": GTS},
    also_in=[{"bib": "KissingervdWeteringbook", "location": "Chapter 5 (pivoting)"}],
    related=[{"id": "local-complementation", "relation": "derived-from"}],
    tags=["pivot", "pivoting", "graph-like", "simplification", "pauli"],
)

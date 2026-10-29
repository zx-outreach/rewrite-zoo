"""Further rules from the cheatsheets of "Picturing Quantum Software" (Kissinger & van de Wetering) and
from "ZX-calculus for the working quantum computer scientist" (van de Wetering 2020): scalars, circuit
identities among CNOT/CZ/Hadamard/phase gates, and phase gadget commutation rules.

    cd authoring && python book_cheatsheet.py [--force] [--only=id1,id2]
"""

from dsl import D, rule

BOOK = "KissingervdWeteringbook"
WORKING = "vandewetering2020zxcalculus"
BOOK_GEN = {"bib": BOOK, "location": "Section 8.1.1 (generators and their matrices)"}
BOOK_CS = {"bib": BOOK, "location": "Section 8.1.4 (ZX-calculus full cheatsheet)"}
BOOK_CI = {"bib": BOOK, "location": "Section 8.2.2 (circuit identities)"}
W_SCALARS = {"bib": WORKING, "location": "Section 3.4 (scalars)"}


class Circ:
    """A diagram drawn as a circuit: qubit q is a horizontal wire at height ys[q], with its input at x = 0
    and its output at x = width. Gates are placed at given x positions; the wire segments are added by
    ``done()``. ``h(q, x)`` puts a Hadamard gate on the wire, which becomes a Hadamard edge between the
    neighbouring vertices on that wire."""

    def __init__(self, ys, width, bools=""):
        self.d = D(bools)
        self.ys = list(ys)
        self.width = width
        self.items = [[] for _ in self.ys]

    def _add(self, q, x, v):
        self.items[q].append((x, v))
        return v

    def z(self, q, x, phase=0):
        return self._add(q, x, self.d.z(x, self.ys[q], phase))

    def x(self, q, x, phase=0):
        return self._add(q, x, self.d.x(x, self.ys[q], phase))

    def h(self, q, x):
        self.items[q].append((x, "H"))

    def cnot(self, c, t, x):
        self.d.e(self.z(c, x), self.x(t, x))

    def cz(self, a, b, x):
        self.d.he(self.z(a, x), self.z(b, x))

    def gadget(self, qs, x, phase, hub, leaf):
        """A phase gadget on qubits qs (spiders at column x), with its X-hub and Z-leaf at the given points."""
        h = self.d.x(*hub)
        self.d.e(h, self.d.z(*leaf, phase))
        for q in qs:
            self.d.e(self.z(q, x), h)

    def done(self):
        d = self.d
        for q, y in enumerate(self.ys):
            prev, had = d.b(0, y), False
            for x, v in sorted(self.items[q], key=lambda t: t[0]) + [(self.width, None)]:
                if v == "H":
                    assert not had, "two Hadamards in a row"
                    had = True
                    continue
                if v is None:
                    v = d.b(self.width, y)
                (d.he if had else d.e)(prev, v)
                prev, had = v, False
        return d


def rel(*pairs):
    return [{"id": i, "relation": r} for i, r in pairs]


# =============================================================================================
# Scalars

L = D()
L.z(0, 0, "alpha")
rule(
    "scalar-z-spider", lhs=L, rhs=D(),
    name="Spider scalar",
    aliases=["zero-arity spider", "1 + e^{iα}", "scalar spider", "zero scalar", "Z(π) = 0"],
    calculus="ZX", fragment="universal", group="scalars", order=1,
    summary="A spider without any legs is the scalar 1 + e^{iα}.",
    description=(
        "A Z-spider (or X-spider) with phase α and no inputs or outputs is the scalar $1+e^{i\\alpha}$: it is the "
        "sum of the two terms $\\langle 0|0\\rangle$ and $e^{i\\alpha}\\langle 1|1\\rangle$ of the spider.\n\n"
        "Two special cases are particularly important: a phase-free spider without legs is the scalar 2, and a "
        "spider with phase π and no legs is the scalar **0**. A diagram containing such a zero scalar is zero, "
        "and complete calculi need a rule (the *zero rule*) that lets such diagrams be brought to a normal form.\n\n"
        "Together with the [two-spider scalars](../scalar-state-effect/) and the "
        "[1/√2 scalar](../scalar-inverse-sqrt2/), every complex number can be written as a scalar ZX-diagram."),
    variables={"alpha": "real"},
    scalar="1+exp(I*alpha)",
    source=W_SCALARS,
    also_in=[BOOK_GEN, BOOK_CS],
    related=rel(("scalar-state-effect", "see-also"), ("scalar-inverse-sqrt2", "see-also")),
    tags=["scalar", "zero", "spider", "normalisation"],
)

L = D(bools="a")
L.e(L.x(0, 0, "a"), L.z(1, 0, "alpha"))
rule(
    "scalar-state-effect", lhs=L, rhs=D(),
    name="Basis state and phase effect scalar",
    aliases=["√2 e^{iα}", "scalar lollipop", "√2 scalar", "two-spider scalar"],
    calculus="ZX", fragment="universal", group="scalars", order=2,
    summary="An X-spider with phase aπ connected to a Z-spider with phase α is the scalar √2 e^{iaα}.",
    description=(
        "An X-spider with phase aπ, for a ∈ {0, 1}, is (up to √2) the computational basis state $|a\\rangle$. "
        "Plugging it into the one-legged Z-spider with phase α, which is the effect $\\langle 0| + e^{i\\alpha}\\langle 1|$, "
        "gives the scalar $\\sqrt2\\, e^{ia\\alpha}$.\n\n"
        "For a = 0 this says that a phase-free X-spider connected to *any* Z-phase is √2, so a Z-phase can be "
        "absorbed into such a scalar diagram. For a = 1 this gives a diagram for every scalar of modulus √2. These "
        "diagrams are the standard way to represent global phases in ZX-diagrams, for instance in "
        "[local complementation](../local-complementation/)."),
    variables={"alpha": "real", "a": "boolean"},
    scalar="sqrt(2)*exp(I*a*alpha)",
    source=W_SCALARS,
    also_in=[BOOK_GEN, BOOK_CS],
    related=rel(("scalar-z-spider", "see-also"), ("state-copy", "special-case-of"),
                ("scalar-phase-addition", "see-also")),
    tags=["scalar", "global phase", "sqrt 2"],
)

L = D()
x, z = L.x(0, 0), L.z(1.5, 0)
L.e(x, z).e(x, z).e(x, z)
rule(
    "scalar-inverse-sqrt2", lhs=L, rhs=D(),
    name="1/√2 scalar",
    aliases=["inverse square root of two", "triple-wire scalar"],
    calculus="ZX", fragment="phase-free", group="scalars", order=3,
    summary="A Z- and an X-spider connected by three wires are the scalar 1/√2.",
    description=(
        "A phase-free Z-spider and a phase-free X-spider connected by three parallel wires represent the scalar "
        "$\\frac{1}{\\sqrt2}$. By the [Hopf rule](../hopf/), two of the three wires can be removed at the cost of a "
        "factor ½, leaving the scalar √2 of a single connecting wire.\n\n"
        "This is the standard way to write *negative* powers of √2 as a ZX-diagram, as for example needed to "
        "normalise the CNOT gate. It is the inverse of the [two-spider scalar](../scalar-state-effect/) for "
        "a = 0: placing the two side by side gives the empty diagram."),
    scalar="auto",
    source=W_SCALARS,
    also_in=[BOOK_GEN, BOOK_CS],
    related=rel(("hopf", "derived-from"), ("scalar-state-effect", "see-also")),
    tags=["scalar", "sqrt 2", "normalisation", "hopf"],
)

L = D()
L.e(L.z(0, 0, "alpha"), L.x(1, 0, 1))
L.e(L.z(0, 1, "beta"), L.x(1, 1, 1))
R = D()
R.e(R.z(0, 0, "alpha+beta"), R.x(1, 0, 1))
R.e(R.x(0, 1), R.z(1, 1))
rule(
    "scalar-phase-addition", lhs=L, rhs=R,
    name="Scalar phases combine",
    aliases=["global phases multiply", "scalar phase combination"],
    calculus="ZX", fragment="universal", group="scalars", order=4,
    summary="Two global-phase scalar diagrams combine into one, with their phases added.",
    description=(
        "The diagram consisting of a Z-spider with phase α connected to an X-spider with phase π is the scalar "
        "$\\sqrt2 e^{i\\alpha}$ (see [this rule](../scalar-state-effect/)). This rule expresses diagrammatically that "
        "multiplying two such scalars adds their phases: $\\sqrt2e^{i\\alpha}\\cdot\\sqrt2e^{i\\beta} = "
        "\\sqrt2e^{i(\\alpha+\\beta)}\\cdot\\sqrt2$, where the last factor √2 is a phase-free pair of spiders.\n\n"
        "It is one of the scalar lemmas that the book derives from the rules of the ZX-calculus, so that "
        "diagrammatic reasoning with scalars does not require translating to numbers."),
    variables={"alpha": "real", "beta": "real"},
    scalar="1",
    source={"bib": BOOK},
    related=rel(("scalar-state-effect", "see-also"), ("pi-commutation", "see-also"),
                ("state-copy", "see-also")),
    tags=["scalar", "global phase", "phase addition"],
)

L = D()
L.z(0, 0, "1/2")
L.z(0, 1, "1/2")
R = D()
R.e(R.z(0, 0, "1/2"), R.x(1, 0, 1))
R.e(R.x(0, 1), R.z(1, 1))
rule(
    "scalar-pi2-pair", lhs=L, rhs=R,
    name="Two π/2 scalars",
    aliases=["(1+i)^2 = 2i", "Clifford scalar rule"],
    calculus="ZX", fragment="clifford", group="scalars", order=5,
    summary="Two legless π/2 spiders equal the global phase i times 2, written with two-spider scalars.",
    description=(
        "A legless Z-spider with phase π/2 is the scalar $1+i = \\sqrt2 e^{i\\pi/4}$. Two of these multiply to "
        "$2i$, which can be written as the [scalar](../scalar-state-effect/) $\\sqrt2 e^{i\\pi/2}$ (a π/2 Z-spider "
        "connected to a π X-spider) times √2 (a phase-free pair of spiders).\n\n"
        "This is one of the rules that relates the 'odd' Clifford scalars $1\\pm i$ to global phases. Note that "
        "a single $1+i$ cannot be written with only Clifford two-spider scalars (it has phase π/4), so such "
        "legless spiders must be paired up."),
    scalar="1",
    source={"bib": BOOK},
    related=rel(("scalar-z-spider", "see-also"), ("scalar-pi2-inverse", "see-also"),
                ("y-state", "see-also")),
    tags=["scalar", "clifford", "global phase"],
)

L = D()
L.z(0, 0, "1/2")
L.z(0, 1, "-1/2")
R = D()
R.e(R.x(0, 0), R.z(1, 0))
R.e(R.x(0, 1), R.z(1, 1))
rule(
    "scalar-pi2-inverse", lhs=L, rhs=R,
    name="Opposite π/2 scalars",
    aliases=["(1+i)(1-i) = 2", "π/2 and −π/2 scalars cancel"],
    calculus="ZX", fragment="clifford", group="scalars", order=6,
    summary="Legless spiders with phases π/2 and −π/2 together are the scalar 2.",
    description=(
        "Legless Z-spiders with phases π/2 and −π/2 are the scalars $1+i$ and $1-i$, whose product is 2. "
        "Diagrammatically, 2 is two copies of the phase-free [two-spider scalar](../scalar-state-effect/) √2.\n\n"
        "Together with the [two π/2 scalars](../scalar-pi2-pair/) rule, this allows all Clifford scalar diagrams "
        "to be brought to a normal form."),
    scalar="1",
    source={"bib": BOOK},
    related=rel(("scalar-pi2-pair", "see-also"), ("scalar-z-spider", "see-also")),
    tags=["scalar", "clifford"],
)

# =============================================================================================
# Euler decompositions

L = D()
a, b = L.x(1, 0, "1/2"), L.x(2, 0, "1/2")
L.e(L.b(0, 0), a).he(a, b).e(b, L.b(3, 0))
R = D()
R.wire(0, 0, 2, R.z(1, 0, "-1/2"))
rule(
    "hadamard-pi2-sandwich", lhs=L, rhs=R,
    name="Hadamard between two π/2 X-rotations",
    aliases=["V H V = S†", "Hadamard Euler sandwich"],
    calculus="ZX", fragment="clifford", group="hadamard", order=11,
    summary="A Hadamard gate between two π/2 X-rotations is a −π/2 Z-rotation.",
    description=(
        "Sandwiching a Hadamard gate between two X-rotations by π/2 (the $V=\\sqrt X$ gate) gives the Z-rotation "
        "by −π/2 (the $S^\\dagger$ gate), up to a global phase: $VHV \\propto S^\\dagger$.\n\n"
        "This is the [Euler decomposition of the Hadamard](../euler-decomposition-hadamard/) in its "
        "colour-swapped form $H \\propto X(\\frac\\pi2)Z(\\frac\\pi2)X(\\frac\\pi2)$, with the outer X-rotations moved "
        "to the other side. It is useful for absorbing Hadamards into neighbouring Clifford phases."),
    scalar="auto",
    source=BOOK_CI,
    related=rel(("euler-decomposition-hadamard", "derived-from"), ("colour-change", "see-also")),
    tags=["euler", "hadamard", "clifford", "S gate", "V gate"],
)

# =============================================================================================
# Circuit identities

L = Circ([0, 1], 3)
L.cnot(0, 1, 1)
L.cnot(0, 1, 2)
R = D()
R.wire(0, 0, 2)
R.wire(1, 0, 2)
rule(
    "cnot-cancellation", lhs=L.done(), rhs=R,
    name="CNOT cancellation",
    aliases=["CNOT self-inverse", "two CNOTs cancel"],
    calculus="ZX", fragment="phase-free", group="circuits", order=1,
    summary="Two CNOT gates with the same control and target cancel.",
    description=(
        "The CNOT gate is self-inverse. In the ZX-calculus this follows by fusing the two controls and the two "
        "targets with [spider fusion](../spider-fusion/), which leaves a Z- and an X-spider connected by two "
        "wires. The [Hopf rule](../hopf/) disconnects them, after which the remaining arity-2 spiders are "
        "[identities](../identity-removal/).\n\n"
        "Each CNOT written as a Z-spider connected to an X-spider is $\\frac{1}{\\sqrt2}$ times the unitary, "
        "hence the scalar ½."),
    scalar="auto",
    source={"bib": WORKING, "location": "Section 4.5 (bialgebra and Hopf rule)"},
    also_in=[{"bib": BOOK}],
    related=rel(("hopf", "derived-from"), ("spider-fusion", "derived-from"),
                ("swap-three-cnots", "see-also")),
    tags=["CNOT", "circuit", "cancellation", "self-inverse"],
)

L = D()
L.e(L.b(0, 0), L.b(2, 1))
L.e(L.b(0, 1), L.b(2, 0))
R = Circ([0, 1], 4)
R.cnot(0, 1, 1)
R.cnot(1, 0, 2)
R.cnot(0, 1, 3)
rule(
    "swap-three-cnots", lhs=L, rhs=R.done(),
    name="Three CNOTs make a SWAP",
    aliases=["SWAP decomposition", "SWAP = 3 CNOTs"],
    calculus="ZX", fragment="phase-free", group="circuits", order=2,
    summary="The SWAP gate is equal to three alternating CNOT gates.",
    description=(
        "A SWAP gate equals three CNOTs in which the middle one has its control and target reversed. In the "
        "ZX-calculus this is proved by deforming the diagram so that the [bialgebra rule](../bialgebra/) applies "
        "to the first two CNOTs, after which the remaining pair of CNOTs [cancels](../cnot-cancellation/).\n\n"
        "This identity is used in routing quantum circuits on restricted architectures, where SWAPs must be "
        "implemented with the native two-qubit gates."),
    scalar="auto",
    source={"bib": WORKING, "location": "Section 4.5 (bialgebra and Hopf rule)"},
    also_in=[{"bib": BOOK}],
    related=rel(("bialgebra", "derived-from"), ("cnot-cancellation", "derived-from")),
    tags=["SWAP", "CNOT", "circuit", "routing"],
)

L = Circ([0, 1], 3)
L.h(1, 0.5)
L.cnot(0, 1, 1.5)
L.h(1, 2.5)
R = Circ([0, 1], 3)
R.cz(0, 1, 1.5)
rule(
    "cz-cnot-hadamard", lhs=L.done(), rhs=R.done(),
    name="CNOT conjugated by Hadamards is CZ",
    aliases=["CZ as CNOT", "CNOT = (I⊗H) CZ (I⊗H)", "CZ from CNOT"],
    calculus="ZX", fragment="clifford", group="circuits", order=3,
    summary="A CNOT with Hadamard gates before and after its target is a CZ gate.",
    description=(
        "Conjugating the target of a CNOT gate with Hadamard gates gives the controlled-Z gate. In the "
        "ZX-calculus this is immediate from the [colour change](../colour-change/) rule: the Hadamards turn the "
        "X-spider of the target into a Z-spider, leaving a Hadamard on the connecting wire, which is the "
        "diagram of the CZ gate.\n\n"
        "Since the CZ diagram is symmetric, it does not matter which qubit is the control and which the target."),
    scalar="auto",
    source={"bib": WORKING, "location": "Section 2.3 (Hadamards and colour changing)"},
    also_in=[{"bib": BOOK}],
    related=rel(("colour-change", "derived-from"), ("cz-pauli-propagation", "see-also")),
    tags=["CZ", "CNOT", "hadamard", "circuit"],
)

L = Circ([0, 1], 3)
L.z(0, 1, "alpha")
L.cnot(0, 1, 2)
R = Circ([0, 1], 3)
R.cnot(0, 1, 1)
R.z(0, 2, "alpha")
rule(
    "cnot-phase-commutation", lhs=L.done(), rhs=R.done(),
    name="Phases commute through CNOT",
    aliases=["Z-rotation through CNOT control", "X-rotation through CNOT target", "T-CNOT commutation"],
    calculus="ZX", fragment="universal", group="circuits", order=4,
    summary="A Z-rotation on the control of a CNOT commutes with the CNOT.",
    description=(
        "A Z-phase gate on the control qubit commutes with a CNOT gate. In the ZX-calculus this is just "
        "[spider fusion](../spider-fusion/): both the phase and the control are Z-spiders, so they fuse and "
        "unfuse on the other side. With the colours swapped (also shown on this page), an X-phase gate on the "
        "target commutes with the CNOT in the same way.\n\n"
        "This is the simplest example of how ZX-diagrams make commutation relations in circuits visible: gates "
        "commute when the spiders they meet are of the same colour."),
    variables={"alpha": "real"},
    scalar="1",
    source={"bib": WORKING, "location": "Section 2.1 (from quantum circuits to ZX-diagrams)"},
    also_in=[{"bib": BOOK}],
    related=rel(("spider-fusion", "derived-from"), ("cnot-pauli-propagation", "see-also")),
    tags=["CNOT", "phase", "commutation", "circuit", "T gate"],
)

L = Circ([0, 1], 3)
L.x(0, 1, 1)
L.cnot(0, 1, 2)
R = Circ([0, 1], 3)
R.cnot(0, 1, 1)
R.x(0, 2, 1)
R.x(1, 2, 1)
rule(
    "cnot-pauli-propagation", lhs=L.done(), rhs=R.done(),
    name="Pauli X propagates through CNOT",
    aliases=["Pauli pushing through CNOT", "X copy through control", "CNOT Pauli conjugation"],
    calculus="ZX", fragment="pauli", group="circuits", order=5,
    summary="A Pauli X on the control of a CNOT becomes a Pauli X on both qubits.",
    description=(
        "Pushing a Pauli X gate on the control qubit through a CNOT gate copies it to the target: "
        "$\\mathrm{CNOT}\\,(X\\otimes I) = (X\\otimes X)\\,\\mathrm{CNOT}$. In the ZX-calculus the π X-phase is "
        "copied through the Z-spider of the control by the [π-commutation rule](../pi-commutation/), and the copy "
        "on the target fuses into the X-spider there. With colours swapped (also shown on this page), a Pauli Z on "
        "the target is copied to the control.\n\n"
        "Together with [phase commutation](../cnot-phase-commutation/), this gives all the rules for propagating "
        "Paulis through CNOT circuits, as needed in stabiliser simulation, measurement-based computation and "
        "error correction."),
    scalar="auto",
    source={"bib": WORKING, "location": "Section 5.2 (Pauli pushing)"},
    also_in=[BOOK_CI],
    related=rel(("pi-commutation", "derived-from"), ("cnot-phase-commutation", "see-also"),
                ("cz-pauli-propagation", "see-also")),
    tags=["pauli", "CNOT", "pauli pushing", "stabiliser", "circuit"],
)

L = Circ([0, 1], 3)
L.x(0, 1, 1)
L.cz(0, 1, 2)
R = Circ([0, 1], 3)
R.cz(0, 1, 1)
R.x(0, 2, 1)
R.z(1, 2, 1)
rule(
    "cz-pauli-propagation", lhs=L.done(), rhs=R.done(),
    name="Pauli X propagates through CZ",
    aliases=["Pauli pushing through CZ", "CZ Pauli conjugation"],
    calculus="ZX", fragment="clifford", group="circuits", order=6,
    summary="A Pauli X on one qubit of a CZ becomes an X on that qubit and a Z on the other.",
    description=(
        "Pushing a Pauli X gate through a CZ gate produces an extra Pauli Z on the other qubit: "
        "$\\mathrm{CZ}\\,(X\\otimes I) = (X\\otimes Z)\\,\\mathrm{CZ}$. In the ZX-calculus the π X-phase is copied by the "
        "Z-spider of the CZ by [π-commutation](../pi-commutation/); the copy that travels along the Hadamard edge "
        "becomes a π Z-phase by the [colour change](../colour-change/) rule.\n\n"
        "This is the basic rule behind the stabilisers of graph states: an X on a vertex together with Z on all its "
        "neighbours stabilises the graph state."),
    scalar="auto",
    source=BOOK_CI,
    related=rel(("cnot-pauli-propagation", "see-also"), ("pi-commutation", "derived-from"),
                ("colour-change", "derived-from"), ("cz-cnot-hadamard", "see-also")),
    tags=["pauli", "CZ", "pauli pushing", "graph state", "stabiliser", "circuit"],
)

L = Circ([0, 1], 3)
L.cnot(0, 1, 1)
L.cz(0, 1, 2)
R = Circ([0, 1], 4)
R.z(1, 1, "1/2")
R.cnot(0, 1, 2)
R.z(0, 3, "-1/2")
R.z(1, 3, "-1/2")
rule(
    "cnot-cz-merge", lhs=L.done(), rhs=R.done(),
    name="CNOT followed by CZ",
    aliases=["CZ·CNOT", "CNOT CZ merge"],
    calculus="ZX", fragment="clifford", group="circuits", order=7,
    summary="A CNOT followed by a CZ on the same qubits is a single CNOT surrounded by S and S† gates.",
    description=(
        "A CNOT followed by a CZ on the same pair of qubits is equal, up to a global phase, to a single CNOT "
        "preceded by an S gate on the target and followed by $S^\\dagger$ gates on both qubits. "
        "So a CZ following a CNOT on the same qubits can always be absorbed into the CNOT and single-qubit "
        "phase gates.\n\n"
        "Rules of this kind are useful for reducing the two-qubit gate count of Clifford circuits."),
    scalar="auto",
    source=BOOK_CI,
    related=rel(("cz-cnot-hadamard", "see-also"), ("cnot-cancellation", "see-also")),
    tags=["CNOT", "CZ", "S gate", "clifford", "circuit"],
)

L = Circ([0, 1], 4)
L.cnot(0, 1, 1)
L.x(0, 2, "beta")
L.z(1, 2, "alpha")
L.cnot(0, 1, 3)
R = Circ([0, 1], 4)
R.cnot(1, 0, 1)
R.z(0, 2, "alpha")
R.x(1, 2, "beta")
R.cnot(1, 0, 3)
rule(
    "cnot-conjugation-reversal", lhs=L.done(), rhs=R.done(),
    name="Reversing CNOT-conjugated rotations",
    aliases=["XX and ZZ rotations", "CNOT sandwich reversal"],
    calculus="ZX", fragment="universal", group="circuits", order=8,
    summary="An X-rotation on the control and a Z-rotation on the target, between two CNOTs, can be moved to the other qubits by reversing the CNOTs.",
    description=(
        "Conjugating $X(\\beta)\\otimes Z(\\alpha)$ by a CNOT gives the commuting product of an $X\\otimes X$ "
        "rotation by β and a $Z\\otimes Z$ rotation by α. Conjugating $Z(\\alpha)\\otimes X(\\beta)$ by the "
        "reversed CNOT gives the same two rotations, so the two circuits are equal.\n\n"
        "In the ZX-calculus each side is a pair of phase gadgets (one of each colour) connecting the two qubits, "
        "which is why the identity holds."),
    variables={"alpha": "real", "beta": "real"},
    scalar="auto",
    source=BOOK_CI,
    related=rel(("phase-gadget-cnot-conjugation", "see-also"), ("cnot-phase-commutation", "see-also")),
    tags=["CNOT", "phase gadget", "Pauli exponential", "circuit"],
)

L = Circ([0, 1, 2], 3)
L.cnot(0, 1, 1)
L.cnot(1, 2, 2)
R = Circ([0, 1, 2], 4)
R.cnot(1, 2, 1)
R.cnot(0, 2, 2)
R.cnot(0, 1, 3)
rule(
    "cnot-target-control-commutation", lhs=L.done(), rhs=R.done(),
    name="Commuting a CNOT target past a CNOT control",
    aliases=["CNOT-CNOT commutation", "CNOT ladder commutation"],
    calculus="ZX", fragment="phase-free", group="circuits", order=9,
    summary="When the target of one CNOT is the control of the next, they can be swapped at the cost of an extra CNOT.",
    description=(
        "Two CNOTs where the target of the first is the control of the second do not commute. Swapping them "
        "introduces a third CNOT from the first control to the second target: "
        "$\\mathrm{CNOT}_{12}\\mathrm{CNOT}_{01} = \\mathrm{CNOT}_{01}\\mathrm{CNOT}_{02}\\mathrm{CNOT}_{12}$ (in "
        "operator notation, so that the rightmost gate is applied first).\n\n"
        "In the ZX-calculus this is a direct application of the [bialgebra rule](../bialgebra/) to the "
        "X-spider of the first target and the Z-spider of the second control. CNOTs sharing only controls or only "
        "targets commute by [spider fusion](../spider-fusion/)."),
    scalar="auto",
    source=BOOK_CI,
    related=rel(("bialgebra", "derived-from"), ("cnot-cz-commutation", "see-also")),
    tags=["CNOT", "commutation", "circuit", "parity"],
)

L = Circ([0, 1, 2.8], 3)
L.cnot(0, 1, 1)
L.cz(1, 2, 2)
R = Circ([0, 1, 2.8], 4)
R.cz(1, 2, 1)
R.cz(0, 2, 2)
R.cnot(0, 1, 3)
rule(
    "cnot-cz-commutation", lhs=L.done(), rhs=R.done(),
    name="Commuting a CZ past a CNOT target",
    aliases=["CZ-CNOT commutation"],
    calculus="ZX", fragment="clifford", group="circuits", order=10,
    summary="A CZ on the target of a CNOT can be moved through it at the cost of an extra CZ on the control.",
    description=(
        "A CZ gate acting on the target qubit of a CNOT can be commuted through the CNOT by adding a CZ between "
        "the control of the CNOT and the other qubit of the CZ. It is the [colour-changed](../colour-change/) "
        "version of [commuting CNOTs](../cnot-target-control-commutation/): with a Hadamard on the third qubit, "
        "the CZ becomes a CNOT whose control is the CNOT's target.\n\n"
        "Rules like this are the basis of algorithms that push CZ gates through CNOT circuits, for instance "
        "when extracting circuits from graph-like diagrams."),
    scalar="auto",
    source=BOOK_CI,
    related=rel(("cnot-target-control-commutation", "variant-of"), ("bialgebra", "derived-from")),
    tags=["CNOT", "CZ", "commutation", "circuit"],
)

# =============================================================================================
# Phase gadgets

L = Circ([0, 1.5], 4)
L.cnot(0, 1, 1)
L.z(1, 2, "alpha")
L.cnot(0, 1, 3)
R = Circ([0, 1.5], 3)
R.gadget([0, 1], 1.5, "alpha", hub=(1.5, 0.75), leaf=(2.25, 0.75))
rule(
    "phase-gadget-cnot-conjugation", lhs=L.done(), rhs=R.done(),
    name="Phase gadget from CNOTs",
    aliases=["CNOT-conjugated phase", "ZZ rotation", "Ising interaction", "Mølmer–Sørensen"],
    calculus="ZX", fragment="universal", group="phase-gadgets", order=3,
    summary="A Z-rotation on the target, conjugated by CNOTs, is a two-qubit phase gadget.",
    description=(
        "The circuit consisting of a CNOT, a Z-phase α on the target, and the same CNOT again implements the "
        "diagonal unitary $|x_1x_2\\rangle \\mapsto e^{i\\alpha(x_1\\oplus x_2)}|x_1x_2\\rangle$, i.e. "
        "$e^{-i\\frac\\alpha2 Z\\otimes Z}$ up to global phase. In the ZX-calculus it is the two-qubit *phase "
        "gadget*: a phase-free X-spider connected to both qubits and to a Z-spider with phase α. The proof uses "
        "spider fusion and the [bialgebra rule](../bialgebra/).\n\n"
        "For more qubits, a phase gadget on n qubits is a ladder of CNOTs computing the parity, a phase, and the "
        "reversed ladder. The ZX form makes the symmetry between the qubits manifest."),
    variables={"alpha": "real"},
    scalar="auto",
    source={"bib": WORKING, "location": "Section 5.6 (phase polynomials and phase gadgets)"},
    also_in=[BOOK_CI],
    related=rel(("phase-gadget-cnot-commutation", "see-also"), ("phase-gadget-fusion", "see-also"),
                ("bialgebra", "derived-from")),
    tags=["phase gadget", "CNOT", "ZZ interaction", "phase polynomial", "circuit"],
)

L = Circ([0, 1.5, 3], 3.5)
L.cnot(0, 1, 1)
L.gadget([1, 2], 2, "alpha", hub=(2, 2.25), leaf=(2.75, 2.25))
R = Circ([0, 1.5, 3], 4.2)
R.gadget([0, 1, 2], 1, "alpha", hub=(1.8, 2.25), leaf=(2.5, 2.25))
R.cnot(0, 1, 3.2)
rule(
    "phase-gadget-cnot-commutation", lhs=L.done(), rhs=R.done(),
    name="Pushing a phase gadget through a CNOT",
    aliases=["gadget-CNOT commutation", "phase gadget through CNOT"],
    calculus="ZX", fragment="universal", group="phase-gadgets", order=4,
    summary="A phase gadget on the target of a CNOT gains (or loses) the control qubit when pushed through it.",
    description=(
        "A phase gadget on a set of qubits S that contains the target but not the control of a CNOT can be "
        "pushed through the CNOT, after which it also acts on the control qubit. Conversely, if S contains both "
        "control and target, pushing it through removes the control (read the rule from right to left). This "
        "is because the CNOT maps the parity $x_c\\oplus x_t$ to $x_t$.\n\n"
        "When the gadget acts only on the target, it is a Z-phase on the target, and pushing it through gives a "
        "two-qubit gadget; this is the basis of [building gadgets from CNOTs](../phase-gadget-cnot-conjugation/). "
        "The rule follows from spider fusion and the [bialgebra rule](../bialgebra/), and is central to "
        "phase-polynomial and Pauli-exponential circuit synthesis."),
    variables={"alpha": "real"},
    parameter_notes="Shown for a gadget on the target and one further qubit; it holds for gadgets on any number of qubits.",
    scalar="auto",
    source=BOOK_CI,
    related=rel(("phase-gadget-cnot-conjugation", "see-also"), ("bialgebra", "derived-from"),
                ("phase-gadget-fusion", "see-also")),
    tags=["phase gadget", "CNOT", "commutation", "phase polynomial", "circuit"],
)

L = Circ([0, 1.5], 2)
L.cz(0, 1, 1)
R = Circ([0, 1.5], 3.25)
R.gadget([0, 1], 1, "1/2", hub=(1, 0.75), leaf=(1.75, 0.75))
R.z(0, 2.5, "-1/2")
R.z(1, 2.5, "-1/2")
rule(
    "phase-gadget-cz", lhs=L.done(), rhs=R.done(),
    name="CZ as a phase gadget",
    aliases=["CZ decomposition into phase gadget", "CZ = S⊗S·gadget"],
    calculus="ZX", fragment="clifford", group="phase-gadgets", order=5,
    summary="A CZ gate is a π/2 phase gadget followed by −π/2 Z-phases on both qubits.",
    description=(
        "The CZ gate acts as $|x_1x_2\\rangle\\mapsto e^{i\\pi x_1x_2}|x_1x_2\\rangle$. Using "
        "$x_1x_2 = \\frac12(x_1 + x_2 - x_1\\oplus x_2)$ and $e^{i\\pi x_1x_2} = e^{-i\\pi x_1x_2}$, it is the "
        "product of a two-qubit phase gadget with phase π/2, implementing $e^{i\\frac\\pi2(x_1\\oplus x_2)}$, and "
        "Z-phases −π/2 on both qubits. Negating all phases gives the equivalent form with an S gate on both "
        "qubits and a −π/2 gadget.\n\n"
        "In the ZX-calculus this is a consequence of the [Euler decomposition of the Hadamard](../euler-decomposition-hadamard/) "
        "on the Hadamard edge of the CZ. The same decomposition with α/2 in place of π/2 gives the "
        "controlled-phase gate."),
    scalar="auto",
    source=BOOK_CI,
    related=rel(("euler-decomposition-hadamard", "derived-from"), ("hadamard-gadget-decomposition", "see-also"),
                ("cz-cnot-hadamard", "see-also")),
    tags=["CZ", "phase gadget", "clifford", "controlled phase"],
)

L = Circ([0, 1.5], 3.5)
L.x(0, 1, 1)
L.gadget([0, 1], 2, "alpha", hub=(2, 0.75), leaf=(2.75, 0.75))
R = Circ([0, 1.5], 3.5)
R.gadget([0, 1], 1, "-alpha", hub=(1, 0.75), leaf=(1.75, 0.75))
R.x(0, 2.5, 1)
rule(
    "phase-gadget-pi-commutation", lhs=L.done(), rhs=R.done(),
    name="Pauli X through a phase gadget",
    aliases=["π-commutation for phase gadgets", "NOT through gadget"],
    calculus="ZX", fragment="universal", group="phase-gadgets", order=6,
    summary="A Pauli X on a qubit of a phase gadget flips the sign of the gadget's phase when pushed through.",
    description=(
        "A NOT gate on one of the qubits of a phase gadget can be pushed through the gadget, at the cost of "
        "negating the gadget's phase (and a global phase $e^{i\\alpha}$). This is because the NOT flips the parity "
        "computed by the gadget, and $\\alpha\\,(1\\oplus y) = \\alpha - \\alpha y$.\n\n"
        "Diagrammatically, the π X-phase is copied through the Z-spider on the qubit wire, fuses into the X-hub "
        "of the gadget and is then pushed through the Z-spider of the phase using [π-commutation](../pi-commutation/), "
        "negating the phase."),
    variables={"alpha": "real"},
    scalar="exp(I*alpha)",
    source=BOOK_CI,
    related=rel(("pi-commutation", "derived-from"), ("phase-gadget-fusion", "see-also"),
                ("cnot-pauli-propagation", "see-also")),
    tags=["phase gadget", "pauli", "pi commutation", "circuit"],
)

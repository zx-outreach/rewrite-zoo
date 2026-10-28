"""Basic ZX rules (book Table 8.1 / 8.2 and the original interacting-observables papers)."""

from dsl import D, rule, spread

BOOK_T1 = {"bib": "KissingervdWeteringbook", "location": "Chapter 8, Table 8.1 (basic rewrite rules)"}
BOOK_T2 = {"bib": "KissingervdWeteringbook", "location": "Chapter 8, Table 8.2 (derived rewrite rules)"}
BOOK_CS = {"bib": "KissingervdWeteringbook", "location": "Section 8.1.4 (ZX-calculus full cheatsheet)"}
WORKING = {"bib": "vandewetering2020zxcalculus", "location": "Figure 1"}

# ---------------------------------------------------------------------------------------------
# Spider fusion

L = D()
z1 = L.z(1, 0.5, "alpha")
z2 = L.z(2, 0.5, "beta")
L.ins(z1, [0, 1]).e(z1, z2).outs(z2, [0, 1], x=3)
R = D()
z = R.z(1.5, 0.5, "alpha+beta")
R.ins(z, [0, 1]).outs(z, [0, 1], x=3)
rule(
    "spider-fusion", lhs=L, rhs=R,
    name="Spider fusion",
    aliases=["fusion", "unfusion"],
    calculus="ZX", fragment="universal", group="spiders", order=1,
    summary="Adjacent spiders of the same colour fuse together, and their phases add.",
    description=(
        "Two spiders of the same colour that are connected by one or more wires can be fused into a single "
        "spider, whose phase is the sum of the two phases. Read from right to left, this rule *unfuses* a "
        "spider into two, distributing the phase arbitrarily over the two.\n\n"
        "The rule holds for any number of inputs and outputs on either spider. If the spiders are connected by "
        "more than one wire, the extra wires become self-loops, which can then be removed with the "
        "[self-loop removal](../self-loop-removal/) rule."),
    variables={"alpha": "real", "beta": "real"},
    parameter_notes="Shown for two spiders with two legs each; holds for any number of legs.",
    scalar="1",
    source={"bib": "CD1"},
    also_in=[BOOK_T1, WORKING],
    related=[{"id": "identity-removal", "relation": "see-also"},
             {"id": "self-loop-removal", "relation": "see-also"},
             {"id": "phase-gadget-fusion", "relation": "used-to-derive"}],
    tags=["fusion", "unfusion", "spider"],
)

# ---------------------------------------------------------------------------------------------
# Identity removal

L = D()
z = L.z(1, 0)
L.wire(0, 0, 2, z)
R = D()
R.wire(0, 0, 2)
rule(
    "identity-removal", lhs=L, rhs=R,
    name="Identity removal",
    aliases=["identity rule"],
    calculus="ZX", fragment="phase-free", group="spiders", order=2,
    summary="A phase-free spider with exactly two legs is the identity wire.",
    description=(
        "A spider with zero phase and exactly one input and one output is equal to a plain wire, and can "
        "therefore be removed. Together with [spider fusion](../spider-fusion/) this means that wires can "
        "be thought of as phase-free spiders. Read from right to left, the rule allows the introduction of "
        "a spider on any wire."),
    scalar="1",
    source={"bib": "CD1"},
    also_in=[BOOK_T1, WORKING],
    related=[{"id": "spider-fusion", "relation": "see-also"},
             {"id": "hadamard-cancellation", "relation": "see-also"}],
    tags=["identity", "spider", "wire"],
)

# ---------------------------------------------------------------------------------------------
# Self-loop removal

L = D()
z = L.z(1, 0.5, "alpha")
L.ins(z, [0, 1]).outs(z, [0, 1], x=2)
L.e(z, z)
R = D()
z = R.z(1, 0.5, "alpha")
R.ins(z, [0, 1]).outs(z, [0, 1], x=2)
rule(
    "self-loop-removal", lhs=L, rhs=R,
    name="Self-loop removal",
    aliases=["loop removal"],
    calculus="ZX", fragment="universal", group="spiders", order=3,
    summary="A plain wire from a spider to itself can be removed.",
    description=(
        "A spider that is connected to itself by a plain wire is equal to the same spider without that wire. "
        "This follows from spider fusion together with the fact that cups and caps are themselves (phase-free) "
        "spiders. Compare this with [Hadamard self-loop removal](../hadamard-self-loop-removal/), where the "
        "self-loop contains a Hadamard and adds a π phase."),
    variables={"alpha": "real"},
    scalar="1",
    source={"bib": "CD2"},
    also_in=[{"bib": "KissingervdWeteringbook", "location": "Chapter 3"}],
    related=[{"id": "spider-fusion", "relation": "derived-from"},
             {"id": "hadamard-self-loop-removal", "relation": "variant-of"}],
    tags=["self-loop", "spider"],
)

# ---------------------------------------------------------------------------------------------
# Hadamard cancellation

L = D()
z = L.z(1.5, 0)
i, o = L.b(0, 0), L.b(3, 0)
L.he(i, z, o)
R = D()
R.wire(0, 0, 2)
rule(
    "hadamard-cancellation", lhs=L, rhs=R,
    name="Hadamard cancellation",
    aliases=["Hadamard self-inverse", "HH = I"],
    calculus="ZX", fragment="clifford", group="hadamard", order=1,
    summary="Two Hadamard gates in a row cancel each other.",
    description=(
        "The Hadamard gate is self-inverse: two Hadamards in sequence are equal to the identity wire.\n\n"
        "In PyZX and ZXLive a Hadamard gate is represented by a *Hadamard edge*, so two Hadamard gates in a row "
        "are represented as two Hadamard edges meeting at a phase-free arity-2 spider. In graph-like "
        "diagrams this rule is used to remove such identity spiders."),
    scalar="1",
    source={"bib": "CD2"},
    also_in=[BOOK_T1, WORKING],
    related=[{"id": "colour-change", "relation": "see-also"},
             {"id": "identity-removal", "relation": "see-also"},
             {"id": "euler-decomposition-hadamard", "relation": "see-also"}],
    tags=["hadamard", "identity"],
)

# ---------------------------------------------------------------------------------------------
# Colour change

L = D()
x = L.x(1.5, 0.5, "alpha")
L.ins(x, [-0.2, 1.2]).outs(x, [-0.2, 1.2], x=3)
R = D()
z = R.z(1.5, 0.5, "alpha")
R.ins(z, [-0.2, 1.2], h=True).outs(z, [-0.2, 1.2], x=3, h=True)
rule(
    "colour-change", lhs=L, rhs=R,
    name="Colour change",
    aliases=["Hadamard commutation", "colour-change rule"],
    calculus="ZX", fragment="universal", group="hadamard", order=2,
    summary="Surrounding a spider with Hadamards changes its colour.",
    description=(
        "An X-spider is equal to a Z-spider with the same phase with a Hadamard gate on each of its legs (and vice "
        "versa). Combined with [Hadamard cancellation](../hadamard-cancellation/) this can also be seen as a rule "
        "for pushing a Hadamard gate through a spider, changing its colour.\n\n"
        "This is the rule that turns any ZX-diagram into a graph-like diagram containing only Z-spiders and "
        "Hadamard edges."),
    variables={"alpha": "real"},
    parameter_notes="Shown for a spider with two inputs and two outputs; holds for any number of legs.",
    scalar="1",
    source={"bib": "CD2"},
    also_in=[BOOK_T1, WORKING],
    related=[{"id": "hadamard-cancellation", "relation": "see-also"}],
    tags=["hadamard", "colour change", "graph-like"],
)

# ---------------------------------------------------------------------------------------------
# π-commutation

L = D()
xp = L.x(1, 0, 1)
z = L.z(2, 0, "alpha")
i = L.b(0, 0)
L.e(i, xp, z)
L.outs(z, [-0.5, 0.5], x=3)
R = D()
z = R.z(1, 0, "-alpha")
i = R.b(0, 0)
R.e(i, z)
for y in (-0.5, 0.5):
    xx = R.x(2, y, 1)
    R.e(z, xx, R.b(3, y))
rule(
    "pi-commutation", lhs=L, rhs=R,
    name="π-commutation",
    aliases=["π-copy", "pi commutation", "Pauli pushing"],
    calculus="ZX", fragment="universal", group="copy", order=2,
    summary="A π phase copies through a spider of the opposite colour, flipping the sign of its phase.",
    description=(
        "An X-spider with phase π (the Pauli X gate) can be pushed through a Z-spider with phase α. The π phase "
        "is copied to all the other legs of the Z-spider, and the phase α is negated. Up to the global phase "
        "e^{iα}, this expresses the identity Z(α)X = X Z(−α).\n\n"
        "The same holds with the colours interchanged: a Pauli Z gate commutes through an X-spider."),
    variables={"alpha": "real"},
    parameter_notes="Shown for a spider with one input and two outputs; holds for any number of legs.",
    scalar="exp(I*alpha)",
    source={"bib": "CD2"},
    also_in=[BOOK_T1, WORKING],
    related=[{"id": "state-copy", "relation": "see-also"}],
    tags=["pauli", "pi", "copy", "commutation"],
)

# ---------------------------------------------------------------------------------------------
# State copy

L = D(bools="a")
xs = L.x(0, 0, "a")
z = L.z(1, 0, "alpha")
L.e(xs, z)
L.outs(z, [-0.5, 0.5], x=2)
R = D(bools="a")
for y in (-0.5, 0.5):
    R.e(R.x(1, y, "a"), R.b(2, y))
rule(
    "state-copy", lhs=L, rhs=R,
    name="State copy",
    aliases=["copy rule", "basis state copy"],
    calculus="ZX", fragment="universal", group="copy", order=1,
    summary="A computational-basis state copies through a Z-spider.",
    description=(
        "An X-spider with phase aπ (where a ∈ {0, 1}) and a single leg is, up to a scalar, the computational "
        "basis state |a⟩. When it is plugged into a Z-spider, the Z-spider copies it to all of its other legs. "
        "The phase of the Z-spider only contributes a global phase e^{iaα}.\n\n"
        "With the colours swapped, the states |+⟩ and |−⟩ copy through X-spiders."),
    variables={"alpha": "real", "a": "boolean"},
    parameters={"n": 2},
    parameter_notes="n is the number of output legs of the Z-spider (shown for n = 2).",
    scalar="exp(I*a*alpha)*sqrt(2)**(-(n-1))",
    source={"bib": "CD2"},
    also_in=[BOOK_T1, WORKING],
    related=[{"id": "pi-commutation", "relation": "see-also"},
             {"id": "bialgebra", "relation": "see-also"}],
    tags=["copy", "basis state", "pauli"],
)

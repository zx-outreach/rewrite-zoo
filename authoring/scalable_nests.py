"""Spider-nest rules from "Scalable Spider Nests (...Or How to Graphically Grok Transversal Non-Clifford Gates)"
by Kissinger and van de Wetering (QPL 2024, arXiv:2404.07828).

The paper writes its rules in scalable ZX notation, which is out of scope for the zoo; here they are unfolded into
ordinary ZX-diagrams made of Z-spiders and phase gadgets (an X-spider hub with a Z-spider leaf carrying the phase).

The S4-rule says that the spider-nest map s_4 : 1 -> 4 "separates". Unfolding the inductive definition of s_n
(Definition 2.1, Eq. (14)), s_n is the map |x> |-> sum_y exp(i pi/4 sum_{S subset [n]} (x XOR y_S)) |y>, i.e. a
pi/4 phase gadget on the input together with every subset of the n outputs (the empty subset giving a pi/4 phase on
the input), where the outputs are fresh |+> states. Hence the 2^4 = 16 gadgets.

Scalars: the paper works up to non-zero scalars; the exact scalar is computed here (spiders unnormalised, as in
PyZX): LHS = 2^-16 RHS.

The circuit form of S4 (Eq. (19): 16 pi/4 gadgets on 5 qubits = identity) is not stored separately: with 5 inputs
and 5 outputs its graph-like form is too large for PyZX's dense tensor contraction.
"""

from itertools import combinations

from dsl import D, rule

SRC = "kissinger2024scalable"
SUBSETS4 = [s for k in range(1, 5) for s in combinations(range(1, 5), k)]  # non-empty subsets of the 4 outputs


def s4_lhs(seq, orders, step=1.35, x0=1.0):
    """The unfolded s_4: wire 0 is the input (starting with the pi/4 phase of the empty subset and ending in the
    last gadget), wires 1..4 are the outputs (starting at their first gadget, i.e. a |+> state), and ``seq`` lists
    the gadgets (non-empty subsets of 1..4, each also connected to wire 0) from left to right.

    ``orders[i]`` is the order in which the spiders of wire i are created. It does not change the diagram, but it
    decides where the build's graph-like conversion puts the fused spider of that wire, and with it the column
    order in which PyZX contracts the tensor: with all fused spiders at the far right this needs ~2^36 entries,
    interleaving them with the gadgets brings it down to ~2^20."""
    G = D()
    bin_ = G.b(0, 0)
    pos = {0: [(x0, "1/4")]}
    xs = [x0 + 1.0 + k * step for k in range(len(seq))]
    for x, s in zip(xs, seq):
        for i in (0,) + tuple(s):
            pos.setdefault(i, []).append((x, 0))
    wire = {}
    for i in range(5):
        vs = [None] * len(pos[i])
        for j in orders.get(i, range(len(pos[i]))):
            vs[j] = G.z(pos[i][j][0], i, pos[i][j][1])
        wire[i] = vs
    at = {i: {x: v for (x, _), v in zip(pos[i], wire[i])} for i in range(5)}
    for x, s in zip(xs, seq):
        sub = (0,) + tuple(s)
        yh = (min(sub) + max(sub)) / 2
        if abs(yh - round(yh)) < 1e-9:
            yh += 0.5 if yh < 4 else -0.5
        hub = G.x(x + 0.4, yh)
        G.e(hub, G.z(x + 0.82, yh, "1/4"))
        for i in sub:
            G.e(at[i][x], hub)
    G.e(bin_, wire[0][0])
    for i in range(5):
        G.e(*wire[i])
    xo = xs[-1] + 1.6
    for i in range(1, 5):
        G.e(wire[i][-1], G.b(xo, i))
    return G


def separated():
    """RHS of S4: a <+| effect on the input and four |+> states on the outputs."""
    G = D()
    G.e(G.b(0, 0), G.z(1, 0))
    for y in range(1, 5):
        G.e(G.z(1.2, y), G.b(2.4, y))
    return G




# Left-to-right order of the gadgets: a good contraction order (see s4_lhs), found by dynamic programming.
SEQ = [(3, 4), (2, 4), (1, 4), (4,), (2, 3, 4), (1, 3, 4), (3,), (1, 2, 3, 4), (1, 2, 4), (1, 2, 3), (2, 3),
       (1, 3), (1, 2), (2,), (1,)]
assert sorted(SEQ) == sorted(SUBSETS4)
L = s4_lhs(SEQ, {0: range(15, -1, -1)})  # the fused input spider lands on the left
R = separated()
rule(
    "s4-rule", lhs=L, rhs=R,
    name="S4 rule (spider-nest map separates)",
    aliases=["(S4)", "S4-rule", "S4 rule", "spider-nest map s_4 separates", "s4 separates",
             "diagonal completeness for Clifford+T", "scalable spider nest"],
    calculus="ZX", fragment="clifford+t", group="spider-nests", order=3,
    summary="The spider-nest map s₄ — π/4 phase gadgets connecting one input to all 16 subsets of four fresh |+⟩ outputs — disconnects into a ⟨+| effect on the input and four |+⟩ states.",
    description=(
        "Kissinger and van de Wetering define the *spider-nest maps* $s_n : 1 \\to n$ inductively: $s_0$ is a "
        "$\\frac\\pi4$ Z-effect, and $s_n$ copies its input into $s_{n-1}$ and, through an X-spider that also "
        "produces the new output, into a second copy of $s_{n-1}$. Unfolded, $s_n$ is the map "
        "$\\ket{x} \\mapsto \\sum_{y\\in\\mathbb F_2^n} \\exp\\big(\\frac{i\\pi}4\\sum_{S\\subseteq[n]} "
        "(x\\oplus\\bigoplus_{i\\in S} y_i)\\big)\\ket{y}$: a $\\frac\\pi4$ phase gadget on the input together with "
        "each of the $2^n$ subsets of the outputs, where the outputs start as $\\ket{+}$ states. The *S4 rule* "
        "says that $s_4$ *separates*: it equals (up to a scalar) a $\\bra{+}$ effect on the input and $\\ket{+}$ "
        "states on the four outputs, i.e. the total phase does not depend on $x$ or $y$.\n\n"
        "Bending the input wire around, this is equivalent to the 5-qubit spider nest in which 16 $\\frac\\pi4$ "
        "gadgets act on qubit 1 together with every subset of qubits 2–5 (Eq. (19) of the paper): its "
        "connectivity matrix $(\\vec 1\\ B_4)$ is triorthogonal. By induction the same holds for every $s_n$ with "
        "$n\\geq4$. The main result of the paper is that the Clifford ZX-calculus plus this single rule is "
        "*diagonally complete* for Clifford+T: it proves every spider nest identity $D_M = I$ (for $M$ "
        "triorthogonal), and hence it is complete for CNOT+T circuits. In particular it proves the "
        "[4-qubit spider nest](../spider-nest/). It is not complete for all Clifford+T diagrams, since it is sound "
        "for an interpretation that breaks [supplementarity](../supplementarity/)."),
    parameters={"n": 4},
    parameter_notes="The paper's rule is the case n = 4. The maps s_n separate for every n ≥ 4 (Lemma 3.3, derived from S4 by induction), but s_n has 2^n gadgets, so these are not offered as a family.",
    scalar="auto",
    source={"bib": SRC, "location": "Section 3, Eq. (18), the S4-rule (the map s_4 of Definition 2.1, Eq. (14))"},
    related=[{"id": "spider-nest", "relation": "used-to-derive"},
             {"id": "spider-nest-clifford", "relation": "see-also"},
             {"id": "phase-gadget-fusion", "relation": "see-also"}],
    tags=["spider nest", "phase gadget", "triorthogonal", "T-count", "completeness", "diagonal completeness",
          "CNOT+T", "scalable", "clifford+t"],
    notes=(
        "The paper states the rule in scalable notation, up to a non-zero scalar. Here $s_4$ is unfolded into "
        "ordinary ZX: the spider on the left is the input (its $\\frac\\pi4$ phase is the gadget for the empty "
        "subset), the four spiders with outputs are the outputs, and every other spider pair is a $\\frac\\pi4$ "
        "phase gadget connecting the input to a non-empty subset of the outputs."),
)

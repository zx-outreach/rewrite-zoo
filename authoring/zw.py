"""Rules of the qubit ZW-calculus (Hadzihasanovic 2015, thesis 2017; Carette et al. 2023; the book).

PyZX's W-node is a *directed* W-node: a W_OUTPUT vertex (triangle) joined to a W_INPUT vertex (dot)
carrying the single input leg.  Its tensor is |0> -> |0...0>, |1> -> |10...0> + ... + |0...01>.
In Hadzihasanovic's undirected presentation, black vertices are the fully symmetric W tensors
(sum of all weight-one basis states) and a binary black vertex is the NOT gate.  PyZX's W-node is
exactly a symmetric black vertex (the triangle) with a binary black vertex (the dot) on the input
leg, so the rules below are translated literally.  White vertices of the 2015 calculus are Z-spiders
with phase pi; the r-labelled white vertices of the thesis are Z-boxes with label r.
"""

from dsl import D, rule

ZW15 = "hadzihasanovic2015diagrammatic"
THESIS = "hadzihasanovic2017algebra"
BOOK = "KissingervdWeteringbook"
CARETTE = "carette2023compositionality"


def r15(loc):
    return {"bib": ZW15, "location": f"Section 3 (The rules), {loc}"}


def th(loc):
    return {"bib": THESIS, "location": f"Chapter 5, Section 5.2 (list of rules of the ZW calculus), {loc}"}


W_EXPLAINER = (
    "The W-node (black triangle) with one input and $n$ outputs maps $|0\\rangle \\mapsto |0\\cdots 0\\rangle$ "
    "and $|1\\rangle \\mapsto |10\\cdots0\\rangle + |010\\cdots0\\rangle + \\cdots + |0\\cdots01\\rangle$: it "
    "spreads a single excitation over its outputs in all possible ways. The small dot marks its input leg.")

UNIT_EXPLAINER = (
    "A W-node with no outputs is the state $|0\\rangle$ (read as an effect, it is $\\langle 0|$), which is the "
    "unit of the W-node read as a 'merge'.")

# ---------------------------------------------------------------------------------------------
# W fusion

L = D()
w1o, w1i = L.w(1.5, 0.5)
w2o, w2i = L.w(3, 1.5)
L.e(L.b(0, 0.5), w1i)
L.e(w1o, L.b(4.5, 0))
L.e(w1o, w2i)
L.e(w2o, L.b(4.5, 1))
L.e(w2o, L.b(4.5, 2))
R = D()
wo, wi = R.w(2, 1)
R.e(R.b(0, 1), wi)
for y in (0, 1, 2):
    R.e(wo, R.b(4.5, y))
rule(
    "w-fusion", lhs=L, rhs=R,
    name="W fusion",
    aliases=["W spider rule", "W associativity", "sp_W", "cut_w", "W-node fusion"],
    calculus="ZW", fragment="clifford+t", group="zw-rules", order=1,
    summary="A W-node plugged into the input of another W-node fuses with it.",
    description=(
        W_EXPLAINER + "\n\n"
        "When an output of one W-node is connected to the input of another, the two fuse into a single W-node "
        "with all the remaining outputs. This expresses (co)associativity of the W-node, and is the reason we "
        "can speak of a single $n$-output W-node rather than a tree of binary ones.\n\n"
        "In Hadzihasanovic's undirected presentation this is the spider rule $\\mathrm{sp}_W^{n,m}$ for black "
        "vertices: two black vertices connected through a binary black vertex fuse. Together with "
        "[W identity](../w-identity/) it also gives the unit law: fusing with a W-node that has no outputs "
        "simply removes an output."),
    parameter_notes="Shown for W-nodes with two outputs each; holds for any number of outputs on either W-node.",
    scalar="auto",
    source=r15("spider rule $\\mathrm{sp}_W^{n,m}$"),
    also_in=[r15("Rule 1a (associativity, expanded form)"), th("rule $cut_w$"),
             {"bib": BOOK}],
    axiom_of=[ZW15, THESIS],
    related=[{"id": "w-identity", "relation": "see-also"},
             {"id": "w-zero-copy", "relation": "see-also"}],
    tags=["W", "fusion", "spider", "associativity"],
)

# ---------------------------------------------------------------------------------------------
# W identity

L = D()
wo, wi = L.w(1.2, 0)
L.e(L.b(0, 0), wi)
L.e(wo, L.b(2.2, 0))
R = D()
R.wire(0, 0, 2.2)
rule(
    "w-identity", lhs=L, rhs=R,
    name="W identity",
    aliases=["black involution", "inv", "W-node with one output"],
    calculus="ZW", fragment="clifford+t", group="zw-rules", order=2,
    summary="A W-node with a single output is the identity wire.",
    description=(
        W_EXPLAINER + " With just one output it maps $|0\\rangle\\mapsto|0\\rangle$ and "
        "$|1\\rangle\\mapsto|1\\rangle$, so it is the identity.\n\n"
        "In the undirected ZW-calculus, the binary black vertex is the NOT gate $|01\\rangle+|10\\rangle$, and "
        "PyZX's W-node with one output consists of two such vertices in a row. The rule is then axiom 2a "
        "of Hadzihasanovic: the binary black vertex is an involution."),
    scalar="auto",
    source=r15("Rule 2a"),
    also_in=[th("rule $inv$")],
    axiom_of=[ZW15, THESIS],
    related=[{"id": "w-fusion", "relation": "see-also"}],
    tags=["W", "identity", "involution", "NOT"],
)

# ---------------------------------------------------------------------------------------------
# W copies |0>

L = D()
uo, ui = L.w(0.6, 0.5, input_dir=(0.35, 0))
wo, wi = L.w(2.2, 0.5)
L.e(ui, wi)
L.e(wo, L.b(3.2, 0)).e(wo, L.b(3.2, 1))
R = D()
for y in (0, 1):
    uo, ui = R.w(1.6, y, input_dir=(0.35, 0))
    R.e(ui, R.b(3.2, y))
rule(
    "w-zero-copy", lhs=L, rhs=R,
    name="W copies its unit",
    aliases=["W unit copy", "5b", "|0⟩ copy through W"],
    calculus="ZW", fragment="phase-free", group="zw-rules", order=3,
    summary="The state |0⟩ (a W-node without outputs) is copied by a W-node.",
    description=(
        W_EXPLAINER + " " + UNIT_EXPLAINER + "\n\n"
        "Since the W-node sends $|0\\rangle$ to $|0\\cdots0\\rangle$, plugging the unit into its input "
        "gives a copy of the unit on every output. This is the rule that makes the unit a comonoid "
        "homomorphism, one of the Hopf-algebra axioms of the W-node (axiom 5b of Hadzihasanovic)."),
    parameter_notes="Shown for a W-node with two outputs; holds for any number of outputs.",
    scalar="auto",
    source=r15("Rule 5b"),
    also_in=[{"bib": BOOK}],
    axiom_of=[ZW15],
    related=[{"id": "w-fusion", "relation": "see-also"},
             {"id": "w-z-bialgebra", "relation": "see-also"}],
    tags=["W", "copy", "unit", "zero state"],
)

# ---------------------------------------------------------------------------------------------
# Z(pi) commutes through W

L = D()
z = L.z(1, 0, 1)
wo, wi = L.w(2.2, 0)
L.e(L.b(0, 0), z, wi)
L.e(wo, L.b(3.4, -0.5)).e(wo, L.b(3.4, 0.5))
R = D()
wo, wi = R.w(1.2, 0)
R.e(R.b(0, 0), wi)
for y in (-0.5, 0.5):
    zz = R.z(2.3, y, 1)
    R.e(wo, zz, R.b(3.4, y))
rule(
    "w-pi-commutation", lhs=L, rhs=R,
    name="Z(π) commutes through W",
    aliases=["automorphism rule", "am_W", "3b", "Pauli Z through W"],
    calculus="ZW", fragment="clifford+t", group="zw-rules", order=4,
    summary="A Pauli Z on the input of a W-node can be pushed onto all of its outputs.",
    description=(
        W_EXPLAINER + "\n\n"
        "Every term in the image of $|1\\rangle$ has exactly one output in state $|1\\rangle$, so a sign "
        "$-1$ on the input is the same as a sign $-1$ on every output. In Hadzihasanovic's ZW-calculus, "
        "where the binary white vertex is the Pauli Z, this says that the binary white vertex is an "
        "automorphism of the black monoid (axiom 3b, generalised to $n$ outputs as $\\mathrm{am}_W^n$).\n\n"
        "The same argument works for any diagonal map $\\mathrm{diag}(1,r)$: see "
        "[weights copy through W](../w-weight-copy/)."),
    parameter_notes="Shown for a W-node with two outputs; holds for any number of outputs.",
    scalar="auto",
    source=r15("Rule 3b"),
    also_in=[r15("generalised automorphism rule $\\mathrm{am}_W^n$"), {"bib": BOOK}],
    axiom_of=[ZW15],
    related=[{"id": "w-weight-copy", "relation": "special-case-of"}],
    tags=["W", "pauli", "commutation", "automorphism"],
)

# ---------------------------------------------------------------------------------------------
# Weighted copy: r is a comonoid homomorphism for W

L = D()
z = L.zbox(1, 0, "r")
wo, wi = L.w(2.2, 0)
L.e(L.b(0, 0), z, wi)
L.e(wo, L.b(3.4, -0.5)).e(wo, L.b(3.4, 0.5))
R = D()
wo, wi = R.w(1.2, 0)
R.e(R.b(0, 0), wi)
for y in (-0.5, 0.5):
    zz = R.zbox(2.3, y, "r")
    R.e(wo, zz, R.b(3.4, y))
rule(
    "w-weight-copy", lhs=L, rhs=R,
    name="Weights copy through W",
    aliases=["nat_c^r", "comonoid homomorphism", "W phase pushing", "Z-box through W"],
    calculus="ZW", fragment="universal", group="zw-rules", order=5,
    summary="A weight diag(1, r) on the input of a W-node can be pushed onto each of its outputs.",
    description=(
        W_EXPLAINER + "\n\n"
        "In the $R$-labelled ZW-calculus $\\mathrm{ZW}_R$, the white vertex with label $r$ (here a Z-box) "
        "with two legs is the map $\\mathrm{diag}(1, r) = |0\\rangle\\langle 0| + r|1\\rangle\\langle 1|$. "
        "Because each term produced by the W-node has at most one excitation, a weight $r$ on the input "
        "is the same as a weight $r$ on each output: every label is a comonoid homomorphism for the "
        "W-node.\n\n"
        "With $r = e^{i\\alpha}$ this pushes Z-phases through a W-node, and with $r = -1$ it is "
        "[Z(π) commutes through W](../w-pi-commutation/)."),
    variables={"r": "complex"},
    parameter_notes="Shown for a W-node with two outputs; holds for any number of outputs.",
    scalar="1",
    source=th("rule $nat_c^r$"),
    axiom_of=[THESIS],
    related=[{"id": "w-pi-commutation", "relation": "generalises"},
             {"id": "w-sum", "relation": "see-also"}],
    tags=["W", "Z-box", "weight", "label", "phase", "commutation"],
)

# ---------------------------------------------------------------------------------------------
# W / Z bialgebra

L = D()
mo, mi = L.w(1.1, 0.5, input_dir=(0.35, 0))
z = L.z(2.3, 0.5)
L.e(L.b(0, 0), mo).e(L.b(0, 1), mo)
L.e(mi, z)
L.e(z, L.b(3.4, 0)).e(z, L.b(3.4, 1))
R = D()
zs = [R.z(1, y) for y in (0, 1)]
ms = [R.w(2.4, y, input_dir=(0.35, 0)) for y in (0, 1)]
for y, zz in zip((0, 1), zs):
    R.e(R.b(0, y), zz)
for y, (mo, mi) in zip((0, 1), ms):
    R.e(mi, R.b(3.6, y))
for zz in zs:
    for mo, mi in ms:
        R.e(zz, mo)
rule(
    "w-z-bialgebra", lhs=L, rhs=R,
    name="W/Z bialgebra",
    aliases=["ZW bialgebra", "6a", "ba^{n,m}", "ba_zw"],
    calculus="ZW", fragment="phase-free", group="zw-bialgebra", order=1,
    summary="A W-node merge followed by a Z-spider copy equals Z-copies followed by W merges.",
    description=(
        W_EXPLAINER + " Read from right to left (the dot on the right), it merges its legs: "
        "$|0\\cdots0\\rangle\\mapsto|0\\rangle$, a single excitation maps to $|1\\rangle$, and everything "
        "else to $0$.\n\n"
        "The phase-free Z-spider and the W-node satisfy a bialgebra law: merging two wires with a W-node "
        "and then copying with a Z-spider is the same as copying each input with a Z-spider and merging "
        "the copies pairwise with W-nodes. This is axiom 6a of Hadzihasanovic's ZW-calculus, there written "
        "with the black monoid and the 'mixed' white comonoid, and generalises to any number of inputs and "
        "outputs ($\\mathrm{ba}^{n,m}$; in the thesis, with a label $r$ on the Z-spider, $ba_{zw}$).\n\n"
        "Unlike the [W bialgebra](../w-bialgebra/), the crossing wires here are an ordinary swap: they "
        "can never both carry $|1\\rangle$ in a non-zero term."),
    parameter_notes="Shown for two inputs and two outputs; holds for any numbers of inputs and outputs.",
    scalar="auto",
    source=r15("Rule 6a"),
    also_in=[r15("generalised bialgebra rule II, $\\mathrm{ba}^{n,m}$"), th("rule $ba_{zw}$"),
             {"bib": BOOK}],
    axiom_of=[ZW15, THESIS],
    related=[{"id": "w-bialgebra", "relation": "see-also"},
             {"id": "zw-hopf", "relation": "see-also"},
             {"id": "w-zero-copy", "relation": "see-also"}],
    tags=["W", "bialgebra", "strong complementarity", "copy"],
)

# ---------------------------------------------------------------------------------------------
# W bialgebra (with the fermionic crossing written as SWAP . CZ)

L = D()
mo, mi = L.w(1.1, 0.5, input_dir=(0.35, 0))
so, si = L.w(2.6, 0.5)
L.e(L.b(0, 0), mo).e(L.b(0, 1), mo)
L.e(mi, si)
L.e(so, L.b(3.6, 0)).e(so, L.b(3.6, 1))
R = D()
ss = [R.w(1, y) for y in (0, 1)]
ms = [R.w(3.2, y, input_dir=(0.35, 0)) for y in (0, 1)]
for y, (so, si) in zip((0, 1), ss):
    R.e(R.b(0, y), si)
for y, (mo, mi) in zip((0, 1), ms):
    R.e(mi, R.b(4.4, y))
R.e(ss[0][0], ms[0][0]).e(ss[1][0], ms[1][0])
za = R.z(1.6, 0.25)
zb = R.z(1.6, 0.75)
R.e(ss[0][0], za, ms[1][0])
R.e(ss[1][0], zb, ms[0][0])
R.he(za, zb)
rule(
    "w-bialgebra", lhs=L, rhs=R,
    name="W bialgebra",
    aliases=["ba_W", "5a", "W Hopf algebra", "fermionic bialgebra"],
    calculus="ZW", fragment="clifford", group="zw-bialgebra", order=2,
    summary="A W merge followed by a W split equals W splits followed by W merges, with a fermionic crossing.",
    description=(
        W_EXPLAINER + "\n\n"
        "The W-node read as a merge (dot on the right) and as a split (dot on the left) form a bialgebra, "
        "but only up to a sign: the two wires that cross must be connected by Hadzihasanovic's *crossing*, "
        "the 'fermionic swap' $|00\\rangle\\langle00| + |01\\rangle\\langle10| + |10\\rangle\\langle01| - "
        "|11\\rangle\\langle11|$, which picks up a sign when both wires carry an excitation. With an ordinary "
        "swap the rule is false. PyZX has no crossing generator, so here it is written as a swap followed by "
        "a CZ gate (two Z-spiders joined by a Hadamard edge).\n\n"
        "This is axiom 5a of Hadzihasanovic's ZW-calculus (black monoid and comonoid form a Hopf algebra), "
        "generalised to $\\mathrm{ba}_W^{n,m}$. Its companion with a Z-spider, the "
        "[W/Z bialgebra](../w-z-bialgebra/), needs no crossing."),
    parameter_notes="Shown for two inputs and two outputs; holds for any numbers of inputs and outputs, with a fermionic crossing between every pair of crossing wires.",
    scalar="auto",
    source=r15("Rule 5a"),
    also_in=[r15("generalised bialgebra rule I, $\\mathrm{ba}_W^{n,m}$"), th("rule $ba_w$")],
    axiom_of=[ZW15, THESIS],
    related=[{"id": "w-z-bialgebra", "relation": "see-also"},
             {"id": "w-hopf", "relation": "see-also"}],
    tags=["W", "bialgebra", "crossing", "fermionic swap", "CZ"],
    notes=("The crossing of the ZW-calculus is not a generator in PyZX; it is represented here by a swap and a "
           "CZ (Hadamard edge between two phase-free Z-spiders), which has the same linear map. The scalar $\\sqrt{2}$ compensates for the "
           "normalisation of the Hadamard edge: the Z-spiders joined by a Hadamard edge are $\\mathrm{CZ}/\\sqrt{2}$."),
)

# ---------------------------------------------------------------------------------------------
# W Hopf rule (antipode = Z(pi))

L = D()
so, si = L.w(1, 0)
z = L.z(2.1, 0.6, 1)
mo, mi = L.w(3.2, 0, input_dir=(0.35, 0))
L.e(L.b(0, 0), si)
L.e(so, mo)
L.e(so, z, mo)
L.e(mi, L.b(4.4, 0))
R = D()
eo, ei = R.w(1.4, 0)
uo, ui = R.w(3, 0, input_dir=(0.35, 0))
R.e(R.b(0, 0), ei)
R.e(ui, R.b(4.4, 0))
rule(
    "w-hopf", lhs=L, rhs=R,
    name="W Hopf rule",
    aliases=["antipode rule", "5d", "W complementarity"],
    calculus="ZW", fragment="pauli", group="zw-bialgebra", order=3,
    summary="Splitting with a W-node, applying Z(π) to one branch and merging again disconnects the wire.",
    description=(
        W_EXPLAINER + " " + UNIT_EXPLAINER + "\n\n"
        "The W-node is a Hopf algebra whose antipode is the Pauli Z: splitting a wire with a W-node, "
        "applying $Z$ to one of the two branches and merging them again gives $|0\\rangle\\langle0|$, since "
        "the two ways of routing an excitation cancel. This is axiom 5d of Hadzihasanovic's ZW-calculus.\n\n"
        "It is the case $n = m = 1$ of the [W loop rule](../w-loop/), which counts the branches with signs."),
    scalar="auto",
    source=r15("Rule 5d"),
    axiom_of=[ZW15],
    related=[{"id": "w-loop", "relation": "special-case-of"},
             {"id": "zw-hopf", "relation": "see-also"},
             {"id": "w-bialgebra", "relation": "see-also"}],
    tags=["W", "Hopf", "antipode", "disconnect"],
)

# ---------------------------------------------------------------------------------------------
# Z/W Hopf rule

L = D()
z = L.z(1, 0)
mo, mi = L.w(2.4, 0, input_dir=(0.35, 0))
L.e(L.b(0, 0), z)
L.e(z, mo).e(z, mo)
L.e(mi, L.b(3.8, 0))
R = D()
eo, ei = R.w(1.4, 0)
uo, ui = R.w(2.6, 0, input_dir=(0.35, 0))
R.e(R.b(0, 0), ei)
R.e(ui, R.b(3.8, 0))
rule(
    "zw-hopf", lhs=L, rhs=R,
    name="Z/W Hopf rule",
    aliases=["6c", "loop", "lp^n", "ZW complementarity"],
    calculus="ZW", fragment="phase-free", group="zw-bialgebra", order=4,
    summary="A Z-spider and a W-node connected by two wires disconnect.",
    description=(
        W_EXPLAINER + " " + UNIT_EXPLAINER + "\n\n"
        "Copying a basis state with a Z-spider and merging the two copies with a W-node kills $|1\\rangle$ "
        "(two excitations cannot be merged) and keeps $|0\\rangle$, so the composite is "
        "$|0\\rangle\\langle0|$. This is axiom 6c of Hadzihasanovic's ZW-calculus. More generally, any number "
        "$n \\geq 2$ of parallel wires between a W-node and a Z-spider can be cut ($\\mathrm{lp}^n$), and in "
        "the thesis the Z-spider may carry any label $r$ (rule $loop$)."),
    parameter_notes="Shown with two parallel wires; holds for any number $n \\geq 2$ of wires.",
    scalar="auto",
    source=r15("Rule 6c"),
    also_in=[r15("generalised loop rule II, $\\mathrm{lp}^n$"), th("rule $loop$"), {"bib": BOOK}],
    axiom_of=[ZW15, THESIS],
    related=[{"id": "w-hopf", "relation": "see-also"},
             {"id": "w-z-bialgebra", "relation": "see-also"}],
    tags=["W", "Hopf", "disconnect", "parallel edges"],
)

# ---------------------------------------------------------------------------------------------
# W loop rule (signed counting)

L = D()
so, si = L.w(1, 0)
z = L.z(2.1, 0.8, 1)
mo, mi = L.w(3.2, 0, input_dir=(0.35, 0))
L.e(L.b(0, 0), si)
L.e(so, mo).e(so, mo)
L.e(so, z, mo)
L.e(mi, L.b(4.4, 0))
R = D()
so, si = R.w(1, 0)
mo, mi = R.w(3.2, 0, input_dir=(0.35, 0))
R.e(R.b(0, 0), si)
R.e(so, mo)
R.e(mi, R.b(4.4, 0))
rule(
    "w-loop", lhs=L, rhs=R,
    name="W loop rule",
    aliases=["lp_W^{n,m}", "signed wire counting"],
    calculus="ZW", fragment="pauli", group="zw-arithmetic", order=3,
    summary="Between a W split and a W merge, a wire with Z(π) cancels a plain wire.",
    description=(
        W_EXPLAINER + "\n\n"
        "Splitting with a W-node and merging again with $k$ parallel wires gives $\\mathrm{diag}(1, k)$: "
        "the excitation can take any of the $k$ routes. A wire carrying a Pauli Z contributes $-1$ instead "
        "of $+1$, so $n$ plain wires and $m \\leq n$ wires with Z can be replaced by $n - m$ plain wires. "
        "This is Hadzihasanovic's generalised loop rule $\\mathrm{lp}_W^{n,m}$, a form of integer arithmetic "
        "inside the ZW-calculus; the case $n = m = 1$ is the [W Hopf rule](../w-hopf/). The stored instance "
        "has $n = 2$ and $m = 1$.\n\n"
        "With arbitrary labels on the wires it becomes the [sum rule](../w-sum/)."),
    parameters={"n": 2, "m": 1},
    parameter_notes="$n$ plain wires and $m$ wires with Z(π) on the left, $n-m$ plain wires on the right; holds for all $n \\geq m$.",
    scalar="auto",
    source=r15("generalised loop rule I, $\\mathrm{lp}_W^{n,m}$"),
    axiom_of=[ZW15],
    related=[{"id": "w-hopf", "relation": "generalises"},
             {"id": "w-sum", "relation": "special-case-of"}],
    tags=["W", "loop", "arithmetic", "integers", "parallel edges"],
)

# ---------------------------------------------------------------------------------------------
# Sum rule

L = D()
so, si = L.w(1, 0)
zr = L.zbox(2.1, -0.6, "r")
zs = L.zbox(2.1, 0.6, "s")
mo, mi = L.w(3.2, 0, input_dir=(0.35, 0))
L.e(L.b(0, 0), si)
L.e(so, zr, mo).e(so, zs, mo)
L.e(mi, L.b(4.4, 0))
R = D()
z = R.zbox(2.2, 0, "r+s")
R.e(R.b(0, 0), z, R.b(4.4, 0))
rule(
    "w-sum", lhs=L, rhs=R,
    name="Sum rule",
    aliases=["addition rule", "rng_+", "W addition", "convolution"],
    calculus="ZW", fragment="universal", group="zw-arithmetic", order=1,
    summary="Splitting with a W-node, applying weights r and s to the branches and merging gives weight r+s.",
    description=(
        W_EXPLAINER + "\n\n"
        "Write $r$ for the two-legged white vertex (Z-box) $\\mathrm{diag}(1, r)$. Splitting a wire with a "
        "W-node, applying $r$ and $s$ to the two branches and merging them with a W-node gives "
        "$\\mathrm{diag}(1, r + s)$, because the excitation goes through exactly one of the branches. "
        "Together with [weighted spider fusion](../zw-weighted-fusion/), which multiplies labels, this "
        "is how the ring structure of $R$ is encoded in the $R$-labelled ZW-calculus: addition is "
        "convolution with respect to the W Hopf algebra.\n\n"
        "The rule generalises to any number of branches, giving the sum of all labels. In the planar "
        "W-calculus of Carette, Moutot, Perez and Vilmart it reads: two parallel edges with weights $r$ and "
        "$s$ between two W-nodes can be replaced by one edge with weight $r+s$."),
    variables={"r": "complex", "s": "complex"},
    parameter_notes="Shown with two branches; holds for any number of branches.",
    scalar="1",
    source=th("rule $rng_+^{r,s}$"),
    also_in=[{"bib": THESIS, "location": "Chapter 5, Section 5.1, axioms of $ZW_R$"},
             {"bib": CARETTE, "location": "Figure 1 (axioms of the planar W-calculus)"}],
    axiom_of=[THESIS, CARETTE],
    related=[{"id": "w-loop", "relation": "generalises"},
             {"id": "zw-weighted-fusion", "relation": "see-also"},
             {"id": "w-add-states", "relation": "see-also"}],
    tags=["W", "Z-box", "addition", "arithmetic", "label", "weight"],
)

# ---------------------------------------------------------------------------------------------
# Weighted spider fusion (multiplication)

L = D()
a = L.zbox(1, 0.5, "r")
b = L.zbox(2.2, 0.5, "s")
L.e(L.b(0, 0), a).e(L.b(0, 1), a).e(a, b)
L.e(b, L.b(3.2, 0)).e(b, L.b(3.2, 1))
R = D()
c = R.zbox(1.6, 0.5, "r⋅s")
R.e(R.b(0, 0), c).e(R.b(0, 1), c)
R.e(c, R.b(3.2, 0)).e(c, R.b(3.2, 1))
rule(
    "zw-weighted-fusion", lhs=L, rhs=R,
    name="Weighted spider fusion",
    aliases=["cut_z", "rng_×", "label multiplication", "Z-box fusion", "white spider rule"],
    calculus="ZW", fragment="universal", group="zw-arithmetic", order=2,
    summary="Two connected white (Z) spiders with labels r and s fuse into one with label rs.",
    description=(
        "In the $R$-labelled ZW-calculus the white spider with label $r$ is "
        "$|0\\cdots0\\rangle + r|1\\cdots1\\rangle$, which in PyZX is a Z-box with label $r$. Two connected "
        "white spiders fuse, and their labels multiply. For two-legged spiders this is the axiom "
        "$rng_\\times^{r,s}$: composing $\\mathrm{diag}(1, r)$ and $\\mathrm{diag}(1, s)$ gives "
        "$\\mathrm{diag}(1, rs)$; the [sum rule](../w-sum/) provides addition.\n\n"
        "With $r = e^{i\\alpha}$ and $s = e^{i\\beta}$ this is ordinary spider fusion of the ZX-calculus."),
    variables={"r": "complex", "s": "complex"},
    parameter_notes="Shown for two spiders with two outer legs each; holds for any number of legs.",
    scalar="1",
    source=th("rule $cut_z$"),
    also_in=[{"bib": THESIS, "location": "Chapter 5, Section 5.1, axiom $rng_\\times^{r,s}$"}],
    axiom_of=[THESIS],
    related=[{"id": "w-sum", "relation": "see-also"},
             {"id": "spider-fusion", "relation": "see-also"}],
    tags=["Z-box", "fusion", "multiplication", "arithmetic", "label"],
)

# ---------------------------------------------------------------------------------------------
# W adds states

L = D()
a = L.zbox(0.8, 0, "a")
b = L.zbox(0.8, 1, "b")
mo, mi = L.w(2, 0.5, input_dir=(0.35, 0))
L.e(a, mo).e(b, mo)
L.e(mi, L.b(3.4, 0.5))
R = D()
c = R.zbox(1.6, 0.5, "a+b")
R.e(c, R.b(3.4, 0.5))
rule(
    "w-add-states", lhs=L, rhs=R,
    name="W adds states",
    aliases=["W as addition", "Add", "W-H-add"],
    calculus="ZW", fragment="universal", group="zw-arithmetic", order=4,
    summary="Merging the states |0⟩+a|1⟩ and |0⟩+b|1⟩ with a W-node gives |0⟩+(a+b)|1⟩.",
    description=(
        W_EXPLAINER + " Read as a merge (dot on the right) it maps $|00\\rangle\\mapsto|0\\rangle$, "
        "$|01\\rangle, |10\\rangle\\mapsto|1\\rangle$ and $|11\\rangle\\mapsto 0$.\n\n"
        "A one-legged Z-box with label $a$ is the state $|0\\rangle + a|1\\rangle$ (the same as a one-legged "
        "H-box with label $a$). Merging two such states with a W-node drops the $|11\\rangle$ term and adds "
        "the labels: the W-node implements addition. This is the basis of the encoding of arithmetic in "
        "the GHZ/W- and ZW-calculi, and of the 'Add' gadget used to build sums of diagrams."),
    variables={"a": "complex", "b": "complex"},
    parameter_notes="Shown for two states; holds for any number of states merged by one W-node.",
    scalar="1",
    source={"bib": BOOK},
    related=[{"id": "w-sum", "relation": "see-also"}],
    tags=["W", "Z-box", "addition", "states", "arithmetic"],
)

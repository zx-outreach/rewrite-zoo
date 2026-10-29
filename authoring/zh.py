"""ZH-calculus rules (qubit ZH with unnormalised H-boxes, as in PyZX).

Sources: the original ZH paper (Backens & Kissinger, arXiv:1805.02175), the phase-free ZH paper
(van de Wetering & Wolffs, arXiv:1904.07545), the ZH completeness paper (Backens, Kissinger,
Miller-Bakewell, van de Wetering & Wolffs, arXiv:2103.06610), the ZH section of "ZX-calculus for the
working quantum computer scientist" (arXiv:2012.13966) and the H-box cheatsheet of the book.

Conventions: an H-box with label a and k legs has all entries 1, except the entry where all legs are 1,
which is a (no 1/sqrt2 normalisation).  Z- and X-spiders are the usual (PyZX) ZX-spiders, so the grey
spider of the ZH papers (which is normalised differently) differs from a PyZX X-spider by a power of
sqrt(2), and the NOT gate is exactly the PyZX X-spider with phase pi.  All scalars are recorded in
meta.json and are computed for these conventions.
"""

from dsl import D, rule

ZH = "EPTCS287.2"                     # Backens & Kissinger 2018
PF = "PhasefreeZH2019"                # van de Wetering & Wolffs 2019
ZHC = "backens2021completenessZH"     # Backens et al. 2021
WORKING = "vandewetering2020zxcalculus"
BOOK_H = {"bib": "KissingervdWeteringbook", "location": "Section 8.4 (H-box cheatsheet)"}
NOTE_SCALARS = (
    "The H-boxes here are *unnormalised*: an H-box with label $a$ has all entries equal to $1$, except for the "
    "entry where all wires are $1$, which is $a$. The grey spiders of the ZH papers are normalised differently "
    "from the X-spiders of PyZX, so scalar factors may differ from those in the papers.")


def note(extra=""):
    return NOTE_SCALARS + (" " + extra if extra else "")


# =============================================================================================
# H-box rules

# --- H-box fusion (phase-free, (hs)) ---------------------------------------------------------
L = D()
a = L.h(1, 0.5)
m = L.h(2, 0.5)
b = L.h(3, 0.5)
L.ins(a, [0, 1]).e(a, m, b).outs(b, [0, 1], x=4)
R = D()
h = R.h(1.5, 0.5)
R.ins(h, [0, 1]).outs(h, [0, 1], x=3)
rule(
    "zh-h-box-fusion", lhs=L, rhs=R,
    name="H-box fusion",
    aliases=["(HS1)", "(hs)", "H-spider rule", "AND fusion"],
    calculus="ZH", fragment="clifford+t", group="zh-hboxes", order=1,
    summary="Two H-boxes connected through an arity-2 H-box (a Hadamard) fuse into a single H-box.",
    description=(
        "Two H-boxes that are connected via an arity-2 H-box fuse into one H-box carrying all the remaining legs. "
        "This is the H-box analogue of [spider fusion](../spider-fusion/): just as Z-spiders fuse when connected by a "
        "plain wire, H-boxes fuse when they are connected by a wire carrying a Hadamard.\n\n"
        "Thinking of an H-box followed by a Hadamard as a multi-input AND gate, the rule says that a tree of ANDs is a "
        "single AND gate. The version where one of the H-boxes carries an arbitrary label is "
        "[labelled H-box fusion](../zh-h-box-fusion-labelled/)."),
    parameters={"m": 2, "n": 2},
    parameter_notes="Shown with two legs on each H-box; holds for any number of legs.",
    scalar="auto", scalar_side="rhs",
    source={"bib": PF, "location": "Figure 2, rule (HS1)"},
    also_in=[{"bib": ZHC, "location": "Figure 1, rule (hs)"},
             {"bib": WORKING, "location": "Section 8.2"}],
    axiom_of=[PF, ZHC],
    related=[{"id": "zh-h-box-fusion-labelled", "relation": "special-case-of"},
             {"id": "spider-fusion", "relation": "see-also"},
             {"id": "zh-h-box-identity", "relation": "see-also"}],
    tags=["H-box", "fusion", "AND", "Toffoli"],
    notes=note(),
)

# --- H-box fusion with a label (HS1 of the original paper) -----------------------------------
L = D()
a = L.h(1, 0.5, label="a")
m = L.h(2, 0.5)
b = L.h(3, 0.5)
L.ins(a, [0, 1]).e(a, m, b).outs(b, [0, 1], x=4)
R = D()
h = R.h(1.5, 0.5, label="a")
R.ins(h, [0, 1]).outs(h, [0, 1], x=3)
rule(
    "zh-h-box-fusion-labelled", lhs=L, rhs=R,
    name="Labelled H-box fusion",
    aliases=["(HS1)", "(HS)", "H-spider rule"],
    calculus="ZH", fragment="universal", group="zh-hboxes", order=2,
    summary="An H-box with label a fuses with a standard H-box through an arity-2 H-box, keeping the label a.",
    description=(
        "An H-box with an arbitrary complex label $a$ that is connected through an arity-2 H-box to a standard "
        "(label $-1$) H-box fuses with it into a single H-box with label $a$ and all the remaining legs. Note that "
        "only one of the two H-boxes may carry a non-standard label.\n\n"
        "With $a = -1$ this is the phase-free [H-box fusion](../zh-h-box-fusion/) rule. A useful consequence is that "
        "H-boxes absorb $|1\\rangle$ states, see [H-boxes absorb |1⟩](../zh-h-box-absorbs-one/)."),
    variables={"a": "complex"},
    parameters={"m": 2, "n": 2},
    parameter_notes="Shown with two legs on each H-box; holds for any number of legs.",
    scalar="auto", scalar_side="rhs",
    source={"bib": ZH, "location": "Figure 1, rule (HS1)"},
    also_in=[{"bib": ZHC, "location": "Figure 3, rule (HS)"},
             {"bib": WORKING, "location": "Section 8.2"}, BOOK_H],
    axiom_of=[ZH, ZHC],
    related=[{"id": "spider-fusion", "relation": "see-also"}],
    tags=["H-box", "fusion", "label"],
    notes=note(),
)

# --- (HS2) / (hh) ---------------------------------------------------------------------------
L = D()
h1 = L.h(1, 0)
h2 = L.h(2, 0)
L.wire(0, 0, 3, h1, h2)
R = D()
R.wire(0, 0, 3)
rule(
    "zh-h-box-identity", lhs=L, rhs=R,
    name="H-box identity",
    aliases=["(HS2)", "(hh)", "Hadamard cancellation"],
    calculus="ZH", fragment="phase-free", group="zh-hboxes", order=3,
    summary="Two arity-2 H-boxes in a row are the identity, up to a factor of 2.",
    description=(
        "An arity-2 H-box with the standard label $-1$ is the matrix $\\begin{pmatrix}1&1\\\\1&-1\\end{pmatrix}$, "
        "i.e. $\\sqrt 2$ times a Hadamard gate. Two of them in a row therefore give twice the identity. This is the ZH "
        "counterpart of [Hadamard cancellation](../hadamard-cancellation/).\n\n"
        "In the completeness paper of 2021 it is shown that this rule is actually derivable from the other rules of "
        "the phase-free ZH-calculus."),
    scalar="auto", scalar_side="rhs",
    source={"bib": ZH, "location": "Figure 1, rule (HS2)"},
    also_in=[{"bib": PF, "location": "Figure 2, rule (HS2)"},
             {"bib": ZHC, "location": "Figure 1, rule (hh)"}],
    axiom_of=[ZH, PF, ZHC],
    related=[{"id": "hadamard-cancellation", "relation": "equivalent-to"},
             {"id": "zh-hadamard-as-h-box", "relation": "see-also"}],
    tags=["H-box", "Hadamard", "identity"],
    notes=note(),
)

# --- (ZS2) / (id) ---------------------------------------------------------------------------
L = D()
z1 = L.z(1, 0)
z2 = L.z(2, 0)
L.e(L.b(0, 0), z1).e(z1, z2).e(z1, z2).e(z2, L.b(3, 0))
R = D()
R.wire(0, 0, 3)
rule(
    "zh-z-special", lhs=L, rhs=R,
    name="Z-spider special rule",
    aliases=["(ZS2)", "(id)", "special Frobenius", "COPY then merge"],
    calculus="ZH", fragment="clifford", group="zh-hboxes", order=4,
    summary="Copying a wire with a Z-spider and merging it back again gives the identity.",
    description=(
        "Two phase-free Z-spiders connected by two parallel wires, each with one other leg, equal a plain wire. "
        "In terms of Frobenius algebras this says that the Z-spider is *special*. Classically: copying a bit and "
        "then comparing the two copies does nothing.\n\n"
        "In the ZX-calculus this follows from [spider fusion](../spider-fusion/), [self-loop removal](../self-loop-removal/) "
        "and [identity removal](../identity-removal/). In the ZH-calculus it is one of the axioms; the "
        "phase-free (ZS2) of the original paper also states that the arity-2 Z-spider is the identity."),
    scalar="1",
    source={"bib": ZH, "location": "Figure 1, rule (ZS2)"},
    also_in=[{"bib": PF, "location": "Figure 2, rule (ZS2)"},
             {"bib": ZHC, "location": "Figure 1, rule (id)"}],
    axiom_of=[ZH, PF, ZHC],
    related=[{"id": "identity-removal", "relation": "see-also"},
             {"id": "spider-fusion", "relation": "see-also"},
             {"id": "zh-dedup", "relation": "see-also"}],
    tags=["Z-spider", "special", "Frobenius", "COPY"],
)

# --- Dedup (DC): Z-spider doubly connected to an H-box --------------------------------------
L = D()
h = L.h(1, 0)
z = L.z(2.2, 0)
L.e(L.b(0, 0), h).e(h, z).e(h, z).e(z, L.b(3.2, 0))
R = D()
h = R.h(1.5, 0)
R.wire(0, 0, 3, h)
rule(
    "zh-dedup", lhs=L, rhs=R,
    name="AND of a copied bit",
    aliases=["(DC)", "dedup", "double connection", "AND-COPY cancel"],
    calculus="ZH", fragment="clifford+t", group="zh-hboxes", order=5,
    summary="Two parallel wires between a Z-spider and an H-box can be replaced by a single wire.",
    description=(
        "If a Z-spider and an H-box are connected by two parallel wires, one of them can be removed. Here this is "
        "shown for an arity-3 H-box and an arity-3 Z-spider, where the result is a single arity-2 H-box. "
        "Since the Z-spider copies computational basis states, this expresses that $x \\wedge x = x$: copying a bit and "
        "then taking the AND of the two copies gives back the original bit.\n\n"
        "Although it looks simple, this rule is surprisingly hard to derive in the phase-free ZH-calculus: the "
        "phase-free paper derives it using the [AND rule](../zh-and-rule/). The 2021 completeness paper shows that, "
        "together with [Z(π) copying through an H-box](../zh-h-box-z-pi-copy/), it can replace the "
        "[ortho rule](../zh-ortho/) in the axiomatisation. More generally, the same holds for H-boxes with any label "
        "and any number of other legs on the Z-spider and the H-box."),
    scalar="1",
    source={"bib": PF, "location": "Lemma 3.4, rule (DC)"},
    also_in=[{"bib": ZHC, "location": "Lemma 5.1"},
             {"bib": WORKING, "location": "Section 8.2"}, BOOK_H],
    related=[{"id": "zh-ortho", "relation": "see-also"},
             {"id": "zh-and-rule", "relation": "derived-from"},
             {"id": "zh-h-box-z-pi-copy", "relation": "see-also"}],
    tags=["H-box", "AND", "COPY", "parallel edges"],
    notes=note(),
)

# --- AND rule (&) of the phase-free paper -----------------------------------------------------
L = D()
h3 = L.h(1, 0.5)
h2 = L.h(2, 0.5)
L.ins(h3, [0, 1]).e(h3, h2).outs(h2, [0.5], x=3)
R = D()
nots = []
for y, zy in ((0, -0.8), (1, 1.8)):
    i = R.b(0, y)
    n_ = R.x(1, y, 1)
    hh = R.h(2, y)
    s = R.z(2, zy)
    R.e(i, n_, hh).e(s, hh)
    nots.append(hh)
m1 = R.z(3, 0.5, 1)
R.e(nots[0], m1).e(nots[1], m1)
n2 = R.x(4, 0.5, 1)
h4 = R.h(5, 0.5)
s4 = R.z(5, -0.3)
m2 = R.z(6, 0.5, 1)
R.e(m1, n2, h4, m2, R.b(7, 0.5)).e(s4, h4)
rule(
    "zh-and-rule", lhs=L, rhs=R,
    name="AND rule",
    aliases=["(&)", "AND gate", "triangle AND"],
    calculus="ZH", fragment="clifford+t", group="zh-hboxes", order=6,
    summary="The AND gate built from H-boxes equals the AND gate built from triangles.",
    description=(
        "The left-hand side is the standard ZH construction of the AND gate: an arity-3 H-box followed by an arity-2 "
        "H-box (Hadamard), which maps $|x,y\\rangle$ to $2\\,|x\\wedge y\\rangle$. The right-hand side is the way the AND "
        "gate is built in the ZX-calculus with *triangles*: each triangle maps $|0\\rangle\\mapsto|0\\rangle$ and "
        "$|1\\rangle\\mapsto|0\\rangle+|1\\rangle$ (in the orientation used here, up to a scalar), and the Z-spiders with a $\\pi$ phase "
        "are the 'negate' spiders of the phase-free paper.\n\n"
        "In the ZH-calculus the triangle is not a generator. Following the phase-free paper, each triangle is drawn "
        "here by its definition: a NOT followed by an arity-3 H-box with one leg plugged by a phase-free Z-state. "
        "This rule was added to the phase-free ZH-calculus to make it complete for the Toffoli-Hadamard fragment; "
        "it was later shown to be unnecessary in the rule set of the 2021 completeness paper."),
    scalar="auto", scalar_side="rhs",
    source={"bib": PF, "location": "Figure 2, rule (&)"},
    axiom_of=[PF],
    related=[{"id": "zh-dedup", "relation": "used-to-derive"}],
    tags=["AND", "triangle", "Toffoli", "phase-free"],
    notes=note("The triangles are drawn expanded according to definition (Δ) of the phase-free paper."),
)

# --- X(alpha) through an H-box (book) -------------------------------------------------------
L = D()
xa = L.x(1, 0.5, "alpha")
h = L.h(2, 0.5)
L.e(L.b(0, 0.5), xa, h).outs(h, [0, 1], x=3)
R = D()
h = R.h(1, 0.5)
z0 = R.z(2, 0)
z1 = R.z(2, 1)
ha = R.h(3, 0.5, phase="alpha")
R.e(R.b(0, 0.5), h).e(h, z0).e(h, z1).e(z0, ha).e(z1, ha).e(z0, R.b(4, 0)).e(z1, R.b(4, 1))
rule(
    "zh-x-phase-through-h-box", lhs=L, rhs=R,
    name="X-phase through an H-box",
    aliases=["controlled phase from X-rotation"],
    calculus="ZH", fragment="universal", group="zh-hboxes", order=7,
    summary="An X-phase on a leg of a standard H-box turns into a labelled H-box on the other legs.",
    description=(
        "An X-spider with phase $\\alpha$ on one leg of a standard H-box can be pushed through the H-box. On the "
        "other side it becomes an H-box with label $e^{i\\alpha}$, connected to Z-spiders on all the remaining legs. "
        "The reason is that an H-box followed by a Hadamard on one leg is an AND gate, and an X-rotation before a "
        "Hadamard is a Z-rotation after it; a Z-phase on the output of an AND gate is a multiply-controlled phase, "
        "which is exactly what an H-box with label $e^{i\\alpha}$ on copies of the inputs represents.\n\n"
        "Shown for an H-box with three legs; it holds for any number of legs."),
    variables={"alpha": "real"},
    parameter_notes="Shown for an arity-3 H-box; holds for any arity.",
    scalar="auto",
    source=BOOK_H,
    related=[{"id": "zh-h-box-phase-state", "relation": "see-also"},
             {"id": "zh-multiply-generalised", "relation": "see-also"}],
    tags=["H-box", "phase", "controlled phase", "X-spider"],
    notes=note(),
)

# =============================================================================================
# Arithmetic of labels

# --- Multiply (M) -----------------------------------------------------------------------------
L = D()
ha = L.h(0, 0, label="a")
hb = L.h(0, 1, label="b")
z = L.z(1, 0.5)
L.e(ha, z).e(hb, z).e(z, L.b(2, 0.5))
R = D()
R.e(R.h(1, 0.5, label="a⋅b"), R.b(2, 0.5))
rule(
    "zh-multiply", lhs=L, rhs=R,
    name="Multiply rule",
    aliases=["(M)", "multiply"],
    calculus="ZH", fragment="universal", group="zh-arithmetic", order=1,
    summary="Two arity-1 H-boxes with labels a and b merged by a Z-spider become one H-box with label ab.",
    description=(
        "An arity-1 H-box with label $a$ is the (unnormalised) state $|0\\rangle + a|1\\rangle$. The Z-spider with two "
        "inputs and one output multiplies such states entrywise, so two of them merge into the state "
        "$|0\\rangle + ab\\,|1\\rangle$, an H-box with label $ab$.\n\n"
        "When $a = e^{i\\alpha}$ and $b = e^{i\\beta}$ this is just phase addition under [spider fusion](../spider-fusion/). "
        "See the [generalised multiply rule](../zh-multiply-generalised/) for H-boxes of higher arity."),
    variables={"a": "complex", "b": "complex"},
    scalar="1",
    source={"bib": ZH, "location": "Figure 1, rule (M)"},
    also_in=[{"bib": ZHC, "location": "Figure 3, rule (M)"},
             {"bib": WORKING, "location": "Section 8.2"}],
    axiom_of=[ZH, ZHC],
    related=[{"id": "zh-multiply-phase-free", "relation": "generalises"},
             {"id": "zh-multiply-generalised", "relation": "special-case-of"},
             {"id": "zh-average", "relation": "see-also"},
             {"id": "spider-fusion", "relation": "see-also"}],
    tags=["multiply", "label", "arithmetic", "H-box"],
)

# --- Multiply, phase-free (m) ---------------------------------------------------------------
L = D()
ha = L.h(0, 0)
hb = L.h(0, 1)
z = L.z(1, 0.5)
L.e(ha, z).e(hb, z).e(z, L.b(2, 0.5))
R = D()
R.e(R.z(1, 0.5), R.b(2, 0.5))
rule(
    "zh-multiply-phase-free", lhs=L, rhs=R,
    name="Phase-free multiply rule",
    aliases=["(M)", "(m)", "NOT NOT"],
    calculus="ZH", fragment="pauli", group="zh-arithmetic", order=2,
    summary="Two arity-1 standard H-boxes merged by a Z-spider give a phase-free Z-state.",
    description=(
        "The special case $a = b = -1$ of the [multiply rule](../zh-multiply/): the arity-1 H-box is the state "
        "$|0\\rangle - |1\\rangle$, and multiplying two of these entrywise gives $|0\\rangle + |1\\rangle$, which is the "
        "phase-free arity-1 Z-spider. Classically, it can be read as $\\neg\\neg x = x$.\n\n"
        "This is the form of the multiply rule that is an axiom of the phase-free ZH-calculus."),
    scalar="1",
    source={"bib": PF, "location": "Figure 2, rule (M)"},
    also_in=[{"bib": ZHC, "location": "Figure 1, rule (m)"}],
    axiom_of=[PF, ZHC],
    tags=["multiply", "phase-free", "H-box"],
)

# --- Multiply rule for arbitrary arity (M!) ---------------------------------------------------
L = D()
ha = L.h(1, 0, label="a")
hb = L.h(1, 1, label="b")
z0 = L.z(2, 0)
z1 = L.z(2, 1)
L.e(ha, z0).e(ha, z1).e(hb, z0).e(hb, z1).e(z0, L.b(3, 0)).e(z1, L.b(3, 1))
R = D()
h = R.h(1.5, 0.5, label="a⋅b")
R.outs(h, [0, 1], x=3)
rule(
    "zh-multiply-generalised", lhs=L, rhs=R,
    name="Generalised multiply rule",
    aliases=["(M!)", "H-box merging"],
    calculus="ZH", fragment="universal", group="zh-arithmetic", order=3,
    summary="Two H-boxes connected to exactly the same Z-spiders fuse, multiplying their labels.",
    description=(
        "When two H-boxes with labels $a$ and $b$ are connected to exactly the same set of Z-spiders, they can be "
        "replaced by a single H-box with label $ab$. Here the Z-spiders are drawn with one output each, so that after "
        "removing them the result is a single H-box on the outputs. This is the !-box generalisation of the "
        "[multiply rule](../zh-multiply/).\n\n"
        "A frequently used case is $a = b = -1$: two standard H-boxes on the same Z-spiders cancel, since the result has "
        "label $1$ and [disconnects](../zh-unit-generalised/). For instance, this shows that a Toffoli gate is self-inverse."),
    variables={"a": "complex", "b": "complex"},
    parameters={"n": 2},
    parameter_notes="Shown for H-boxes connected to n = 2 Z-spiders; holds for any n.",
    scalar="1",
    source={"bib": ZH, "location": "Lemma 2.3, rule (M!)"},
    also_in=[{"bib": WORKING, "location": "Section 8.2"},
             {"bib": ZHC, "location": "Lemma 3.1"}, BOOK_H],
    related=[{"id": "zh-unit-generalised", "relation": "see-also"},
             {"id": "phase-gadget-fusion", "relation": "see-also"}],
    tags=["multiply", "label", "fusion", "Toffoli"],
)

# --- Average (A) ------------------------------------------------------------------------------
L = D()
ha = L.h(1, 0, label="a")
hb = L.h(1, 1, label="b")
nt = L.x(0, 0.5, 1)
z = L.z(2, 0.5)
L.e(ha, nt, hb).e(ha, z).e(hb, z).e(z, L.b(3, 0.5))
R = D()
R.e(R.h(1.5, 0.5, label="(a+b)/2"), R.b(3, 0.5))
rule(
    "zh-average", lhs=L, rhs=R,
    name="Average rule",
    aliases=["(A)", "average"],
    calculus="ZH", fragment="universal", group="zh-arithmetic", order=4,
    summary="Two H-boxes with labels a and b, connected through a NOT, add their labels.",
    description=(
        "Two arity-2 H-boxes with labels $a$ and $b$ that are connected to each other via a NOT gate and whose other "
        "legs meet in a Z-spider produce the state $2\\,(|0\\rangle + \\frac{a+b}{2}|1\\rangle)$, i.e. twice an H-box "
        "with the *average* $\\frac{a+b}{2}$ as its label. Summing over the internal wire, exactly one of the two "
        "H-boxes is 'active'.\n\n"
        "Together with the [multiply rule](../zh-multiply/) this lets one do arithmetic with H-box labels. The "
        "2021 completeness paper uses a [variant without the division by 2](../zh-average-prime/), which also works "
        "over rings without a half."),
    variables={"a": "complex", "b": "complex"},
    scalar="auto", scalar_side="rhs",
    source={"bib": ZH, "location": "Figure 1, rule (A)"},
    also_in=[{"bib": WORKING, "location": "Section 8.2"}],
    axiom_of=[ZH],
    related=[{"id": "zh-average-prime", "relation": "equivalent-to"},
             {"id": "zh-average-generalised", "relation": "special-case-of"},
             {"id": "zh-multiply", "relation": "see-also"}],
    tags=["average", "addition", "label", "arithmetic"],
    notes=note(),
)

# --- Average, 2021 version (A) ----------------------------------------------------------------
R = D()
hs = R.h(0, 0, label="a+b")
h2 = R.h(0, 1, label=2)
nt = R.x(1, 1, 1)
z = R.z(2, 0.5)
R.e(hs, z).e(h2, nt, z).e(z, R.b(3, 0.5))
rule(
    "zh-average-prime", lhs=L, rhs=R,
    name="Average rule (sum form)",
    aliases=["(A)", "average", "addition"],
    calculus="ZH", fragment="universal", group="zh-arithmetic", order=5,
    summary="Two H-boxes with labels a and b, connected through a NOT, give an H-box labelled a+b combined with a NOT-ed H-box labelled 2.",
    description=(
        "A form of the [average rule](../zh-average/) that avoids dividing by 2. The left-hand side is the same, "
        "but the right-hand side combines an H-box with label $a+b$ and an H-box with label $2$ followed by a NOT "
        "(which is the state $2|0\\rangle + |1\\rangle$) in a Z-spider, giving $2|0\\rangle + (a+b)|1\\rangle$.\n\n"
        "This version is used in the axiomatisation of the ZH-calculus over an arbitrary commutative ring $R$ in "
        "the 2021 completeness paper."),
    variables={"a": "complex", "b": "complex"},
    scalar="auto",
    source={"bib": ZHC, "location": "Figure 3, rule (A)"},
    axiom_of=[ZHC],
    tags=["average", "addition", "label", "arithmetic", "ring"],
    notes=note(),
)

# --- Average for arbitrary arity (A!) ---------------------------------------------------------
L = D()
ha = L.h(1, 0, label="a")
hb = L.h(1, 1, label="b")
nt = L.x(0, 0.5, 1)
z0 = L.z(2, 0)
z1 = L.z(2, 1)
L.e(ha, nt, hb).e(ha, z0).e(ha, z1).e(hb, z0).e(hb, z1).e(z0, L.b(3, 0)).e(z1, L.b(3, 1))
R = D()
h = R.h(1.5, 0.5, label="(a+b)/2")
R.outs(h, [0, 1], x=3)
rule(
    "zh-average-generalised", lhs=L, rhs=R,
    name="Generalised average rule",
    aliases=["(A!)"],
    calculus="ZH", fragment="universal", group="zh-arithmetic", order=6,
    summary="Two H-boxes on the same Z-spiders, connected through a NOT, average their labels.",
    description=(
        "The !-box generalisation of the [average rule](../zh-average/): two H-boxes with labels $a$ and $b$ that "
        "are connected to the same set of Z-spiders, and to each other via a NOT gate, combine into a single H-box "
        "with label $\\frac{a+b}{2}$ (and a scalar factor 2)."),
    variables={"a": "complex", "b": "complex"},
    parameters={"n": 2},
    parameter_notes="Shown for H-boxes connected to n = 2 Z-spiders; holds for any n.",
    scalar="auto", scalar_side="rhs",
    source={"bib": ZH, "location": "Lemma 2.3, rule (A!)"},
    also_in=[{"bib": ZHC, "location": "Lemma 3.8 (in the sum form of the average rule)"}, BOOK_H],
    tags=["average", "addition", "label"],
    notes=note(),
)

# --- Intro (I) --------------------------------------------------------------------------------
L = D()
L.e(L.b(0, 0), L.z(1, 0))
L.e(L.h(2, 1, label="a"), L.b(3, 1))
R = D()
zi = R.z(1, 0.5)
nt = R.x(2, 0, 1)
h0 = R.h(3, 0, label="a")
h1 = R.h(3, 1, label="a")
zo = R.z(4, 0.5)
R.e(R.b(0, 0.5), zi, nt, h0, zo, R.b(5, 0.5)).e(zi, h1, zo)
rule(
    "zh-intro", lhs=L, rhs=R,
    name="Intro rule",
    aliases=["(I)", "introduction rule"],
    calculus="ZH", fragment="universal", group="zh-arithmetic", order=7,
    summary="An H-box state can be split into two copies, controlled by a bit and its negation.",
    description=(
        "The left-hand side discards the input (with a phase-free Z-effect) and outputs an H-box state with label "
        "$a$. On the right-hand side the input is copied; one copy, negated, and the other copy each control an "
        "arity-2 H-box with label $a$. Since exactly one of $x$ and $\\neg x$ is $1$, the output is always "
        "$|0\\rangle + a|1\\rangle$.\n\n"
        "Read from right to left, the rule removes a pair of H-boxes with the same label that differ only by a NOT "
        "on one of their connections; it is a close cousin of the [generalised multiply rule](../zh-multiply-generalised/)."),
    variables={"a": "complex"},
    scalar="1",
    source={"bib": ZH, "location": "Figure 1, rule (I)"},
    also_in=[{"bib": ZHC, "location": "Figure 3, rule (I)"},
             {"bib": WORKING, "location": "Section 8.2"}, BOOK_H],
    axiom_of=[ZH, ZHC],
    related=[{"id": "zh-average", "relation": "see-also"}],
    tags=["intro", "label", "H-box"],
)

# --- Unit (U) ---------------------------------------------------------------------------------
L = D()
L.e(L.b(0, 0), L.h(1, 0, label=1))
R = D()
R.e(R.b(0, 0), R.z(1, 0))
rule(
    "zh-unit", lhs=L, rhs=R,
    name="Unit rule",
    aliases=["(U)", "unit"],
    calculus="ZH", fragment="phase-free", group="zh-arithmetic", order=8,
    summary="An arity-1 H-box with label 1 is a phase-free Z-spider.",
    description=(
        "An arity-1 H-box with label $1$ is the (co)vector $\\langle 0| + \\langle 1|$, which is exactly the phase-free "
        "arity-1 Z-spider. See the [generalised unit rule](../zh-unit-generalised/) for H-boxes of any arity labelled $1$, "
        "which completely disconnect."),
    scalar="1",
    source={"bib": ZH, "location": "Figure 1, rule (U)"},
    also_in=[{"bib": ZHC, "location": "Figure 3, rule (U)"},
             {"bib": WORKING, "location": "Section 8.2"}],
    axiom_of=[ZH, ZHC],
    related=[{"id": "zh-unit-generalised", "relation": "special-case-of"},
             {"id": "zh-h-box-phase-state", "relation": "special-case-of"}],
    tags=["unit", "label", "H-box"],
)

# --- Unit, any arity (U!) ---------------------------------------------------------------------
L = D()
h = L.h(1, 0.5, label=1)
L.e(L.b(0, 0.5), h).outs(h, [0, 1], x=2)
R = D()
R.e(R.b(0, 0.5), R.z(1, 0.5))
R.e(R.z(1.6, 0), R.b(2.6, 0)).e(R.z(1.6, 1), R.b(2.6, 1))
rule(
    "zh-unit-generalised", lhs=L, rhs=R,
    name="Label-1 H-box disconnects",
    aliases=["(U!)", "generalised unit rule", "H-box with label 1"],
    calculus="ZH", fragment="phase-free", group="zh-arithmetic", order=9,
    summary="An H-box with label 1 is the all-ones tensor, so it falls apart into phase-free Z-spiders.",
    description=(
        "An H-box with label $1$ has all its entries equal to $1$, so it is a product of the vectors "
        "$|0\\rangle + |1\\rangle$ on each leg: it disconnects into a phase-free arity-1 Z-spider on each of its legs.\n\n"
        "This is frequently used after the [generalised multiply rule](../zh-multiply-generalised/): two standard H-boxes "
        "connected to the same Z-spiders multiply to an H-box with label $(-1)^2 = 1$, which then disappears."),
    parameters={"n": 3},
    parameter_notes="Shown for an H-box with n = 3 legs; holds for any n.",
    scalar="1",
    source={"bib": ZH, "location": "Lemma 2.3, rule (U!)"},
    also_in=[{"bib": ZHC, "location": "Section 2.5, labelled H-boxes of higher arity"},
             {"bib": WORKING, "location": "Section 8.2"}],
    related=[{"id": "zh-h-box-zero-state-copy", "relation": "see-also"}],
    tags=["unit", "disconnect", "label 1", "H-box"],
)

# --- H-box with label 0 -----------------------------------------------------------------------
L = D()
h = L.h(1, 0.5, label=0)
L.e(L.b(0, 0.5), h).outs(h, [0, 1], x=2)
R = D()
s = R.z(1, -0.5)
h = R.h(1, 0.5)
R.e(R.b(0, 0.5), h).e(s, h).outs(h, [0, 1], x=2)
rule(
    "zh-zero-label", lhs=L, rhs=R,
    name="H-box with label 0",
    aliases=["zero-labelled H-box", "NAND"],
    calculus="ZH", fragment="clifford+t", group="zh-arithmetic", order=10,
    summary="An H-box with label 0 is a standard H-box with one extra leg plugged by a phase-free Z-state.",
    description=(
        "An H-box with label $0$ has all entries $1$ except for a $0$ where all legs are $1$: as a function of the "
        "basis states it is the NAND. It can be written using only standard H-boxes: plugging a phase-free Z-state "
        "(i.e. summing) into one leg of a standard H-box gives $1 + (-1)^{x_1\\cdots x_n}$, which is $2$ unless all "
        "$x_i$ are $1$, and $0$ otherwise. Hence the scalar factor 2."),
    parameters={"n": 3},
    parameter_notes="Shown for an H-box with n = 3 legs; holds for any n.",
    scalar="auto", scalar_side="rhs",
    source={"bib": ZHC, "location": "Section 2.5, the 0-labelled H-box of higher arity"},
    also_in=[BOOK_H],
    related=[{"id": "zh-unit-generalised", "relation": "see-also"}],
    tags=["label 0", "NAND", "H-box"],
    notes=note(),
)

# =============================================================================================
# Bialgebra, ortho and copy rules

# --- ZH bialgebra (BA2) -----------------------------------------------------------------------
L = D()
h = L.h(1, 0.5)
x = L.x(2, 0.5)
L.ins(h, [0, 1]).e(h, x).outs(x, [0, 1], x=3)
R = D()
zs = [R.z(1, y) for y in (0, 1)]
hs = [R.h(2, y) for y in (0, 1)]
for y, zz in zip((0, 1), zs):
    R.e(R.b(0, y), zz)
for y, hh in zip((0, 1), hs):
    R.e(hh, R.b(3, y))
for zz in zs:
    for hh in hs:
        R.e(zz, hh)
rule(
    "zh-bialgebra", lhs=L, rhs=R,
    name="ZH bialgebra",
    aliases=["(BA2)", "(ba2)", "AND-COPY bialgebra"],
    calculus="ZH", fragment="clifford+t", group="zh-bialgebra", order=1,
    summary="A standard H-box connected to an X-spider becomes a complete bipartite graph of Z-spiders and H-boxes.",
    description=(
        "The ZH analogue of the [bialgebra rule](../bialgebra-generalised/). An H-box connected to a phase-free "
        "X-spider is equal to a complete bipartite graph, where every leg of the H-box gets a Z-spider and every leg of "
        "the X-spider gets an H-box.\n\n"
        "Classically this expresses that the AND gate and the COPY gate form a bialgebra, just like XOR and COPY: "
        "taking the AND and then copying the result is the same as copying both inputs and taking the ANDs pairwise. "
        "A special case is that an X-state (a $|0\\rangle$) [explodes an H-box](../zh-h-box-zero-state-copy/)."),
    parameters={"m": 2, "n": 2},
    parameter_notes="Shown with two legs on the H-box and two on the X-spider; holds for any numbers m, n of legs.",
    scalar="auto",
    source={"bib": ZH, "location": "Figure 1, rule (BA2)"},
    also_in=[{"bib": PF, "location": "Figure 2, rule (BA2)"},
             {"bib": ZHC, "location": "Figure 1, rule (ba2)"},
             {"bib": WORKING, "location": "Section 8.2"}, BOOK_H],
    axiom_of=[ZH, PF, ZHC],
    related=[{"id": "bialgebra-generalised", "relation": "see-also"},
             {"id": "zh-h-box-zero-state-copy", "relation": "used-to-derive"}],
    tags=["bialgebra", "AND", "COPY", "strong complementarity"],
    notes=note(),
)

# --- Ortho (O) --------------------------------------------------------------------------------
L = D()
h0 = L.h(1, 0)
h2 = L.h(1, 2)
nt = L.x(2, 0.5, 1)
z = L.z(3, 1)
L.e(L.b(0, 0), h0).e(L.b(0, 2), h2).e(h0, h2).e(h0, nt, z).e(h2, z).e(z, L.b(4, 1))
R = D()
h0 = R.h(1.5, 0)
h2 = R.h(1.5, 2)
s0 = R.z(1.5, -1)
s2 = R.z(1.5, 3)
nt = R.x(2.5, 0.5, 1)
z = R.z(3.5, 1)
R.e(R.b(0, 0), h0).e(R.b(0, 2), h2).e(s0, h0).e(s2, h2).e(h0, nt, z).e(h2, z).e(z, R.b(4.5, 1))
rule(
    "zh-ortho", lhs=L, rhs=R,
    name="Ortho rule",
    aliases=["(O)", "(o)", "orthogonality"],
    calculus="ZH", fragment="phase-free", group="zh-bialgebra", order=2,
    summary="A connection between two H-boxes that are controlled by a bit and its negation can be removed.",
    description=(
        "Two H-boxes that are connected to the same Z-spider, one of them via a NOT, are 'orthogonal': for every value "
        "of the Z-spider exactly one of them is active. The rule says that a wire between two such H-boxes can be "
        "replaced by plugging a phase-free Z-state into each of them (up to a scalar).\n\n"
        "This rule is part of every complete axiomatisation of the ZH-calculus, but is arguably the hardest to motivate. "
        "The 2021 completeness paper shows that it can be replaced by the two simpler rules "
        "[Z(π) copies through an H-box](../zh-h-box-z-pi-copy/) and [AND of a copied bit](../zh-dedup/)."),
    scalar="auto", scalar_side="lhs",
    source={"bib": ZH, "location": "Figure 1, rule (O)"},
    also_in=[{"bib": PF, "location": "Figure 2, rule (O)"},
             {"bib": ZHC, "location": "Figure 1, rule (o)"}],
    axiom_of=[ZH, PF, ZHC],
    related=[{"id": "zh-intro", "relation": "see-also"}],
    tags=["ortho", "orthogonality", "NOT"],
    notes=note(),
)

# --- X-state into an H-box (HCP, copy-x-h) ----------------------------------------------------
L = D()
s = L.x(0, 0.5)
h = L.h(1, 0.5)
L.e(s, h).outs(h, [0, 1], x=2)
R = D()
R.e(R.z(1, 0), R.b(2, 0)).e(R.z(1, 1), R.b(2, 1))
rule(
    "zh-h-box-zero-state-copy", lhs=L, rhs=R,
    name="|0⟩ explodes an H-box",
    aliases=["(HCP)", "X-state copy through H-box"],
    calculus="ZH", fragment="phase-free", group="zh-bialgebra", order=3,
    summary="A phase-free X-state (|0⟩) on an H-box disconnects it into phase-free Z-states.",
    description=(
        "Plugging the computational basis state $|0\\rangle$ (a phase-free arity-1 X-spider) into one leg of an H-box "
        "removes the H-box: whatever the label, all entries of the remaining tensor are $1$, so the result is a "
        "product of phase-free Z-states $|0\\rangle+|1\\rangle$ on the other legs. In terms of AND gates: if one input "
        "is $0$, the output does not depend on the other inputs.\n\n"
        "This is the special case of the [ZH bialgebra](../zh-bialgebra/) rule where the X-spider has no other legs. "
        "It also holds for an H-box with an arbitrary label. Compare [|1⟩ is absorbed](../zh-h-box-absorbs-one/)."),
    parameters={"n": 2},
    parameter_notes="Shown for an H-box with n = 2 other legs; holds for any n.",
    scalar="auto",
    source={"bib": PF, "location": "Lemma 3.3, rule (HCP)"},
    also_in=[{"bib": ZHC, "location": "Lemma 2.26"},
             {"bib": WORKING, "location": "Section 8.2"}, BOOK_H],
    related=[{"id": "zh-h-box-absorbs-one", "relation": "see-also"},
             {"id": "state-copy", "relation": "see-also"}],
    tags=["copy", "state", "H-box", "disconnect"],
    notes=note(),
)

# --- X(pi)-state into an H-box (copy-xnot-h) --------------------------------------------------
L = D()
s = L.x(0, 0.5, 1)
h = L.h(1, 0.5)
L.e(s, h).outs(h, [0, 1], x=2)
R = D()
h = R.h(1, 0.5)
R.outs(h, [0, 1], x=2)
rule(
    "zh-h-box-absorbs-one", lhs=L, rhs=R,
    name="H-boxes absorb |1⟩",
    aliases=["(HCP)", "NOT-state absorption"],
    calculus="ZH", fragment="clifford+t", group="zh-bialgebra", order=4,
    summary="An X-state with phase π (|1⟩) on a leg of an H-box can be removed, lowering the arity of the H-box.",
    description=(
        "Plugging the basis state $|1\\rangle$ (an arity-1 X-spider with phase $\\pi$) into a leg of an H-box gives "
        "the H-box with that leg removed and the same label: the AND of $1$ and $x$ is just $x$. "
        "Together with [|0⟩ explodes an H-box](../zh-h-box-zero-state-copy/) this describes how H-boxes act on "
        "computational basis states.\n\n"
        "It holds for H-boxes with an arbitrary label, and follows from [labelled H-box fusion](../zh-h-box-fusion-labelled/)."),
    parameters={"n": 2},
    parameter_notes="Shown for an H-box with n = 2 other legs; holds for any n.",
    scalar="auto",
    source={"bib": PF, "location": "Lemma 3.3, rule (HCP)"},
    also_in=[{"bib": ZHC, "location": "Lemma 2.27"},
             {"bib": WORKING, "location": "Section 8.2"}, BOOK_H],
    related=[{"id": "zh-h-box-fusion-labelled", "relation": "derived-from"}],
    tags=["copy", "state", "H-box", "absorb"],
    notes=note(),
)

# --- Z(pi)-state into an H-box (copy-znot-h) --------------------------------------------------
L = D()
s = L.z(0, 0.5, 1)
h = L.h(1, 0.5)
L.e(s, h).outs(h, [0, 1], x=2)
R = D()
R.e(R.x(1, 0, 1), R.b(2, 0)).e(R.x(1, 1, 1), R.b(2, 1))
rule(
    "zh-h-box-z-pi-copy", lhs=L, rhs=R,
    name="Z(π) copies through an H-box",
    aliases=["(HCP)", "AND post-selection", "H-box π rule"],
    calculus="ZH", fragment="phase-free", group="zh-bialgebra", order=5,
    summary="A Z-state with phase π on an H-box gives the |1⟩ state on all the other legs.",
    description=(
        "Plugging the state $|0\\rangle - |1\\rangle$ (an arity-1 Z-spider with phase $\\pi$) into a leg of an H-box "
        "with label $a$ gives $1 - a$ when all other legs are $1$, and $0$ otherwise. Hence the result is "
        "proportional to the basis state $|1\\cdots 1\\rangle$, i.e. an X-state with phase $\\pi$ on every other leg. "
        "In terms of AND gates it says that post-selecting the output of an AND on $\\langle 1|$ forces all its inputs "
        "to be $1$.\n\n"
        "This is the only one of the basic derived rules of the phase-free ZH-calculus that needs the "
        "[ortho rule](../zh-ortho/). Conversely, together with [AND of a copied bit](../zh-dedup/) it can replace the "
        "ortho rule in the axiomatisation of the 2021 completeness paper."),
    parameters={"n": 2},
    parameter_notes="Shown for an H-box with n = 2 other legs; holds for any n.",
    scalar="auto",
    source={"bib": PF, "location": "Lemma 3.3, rule (HCP)"},
    also_in=[{"bib": ZHC, "location": "Lemma 2.28"},
             {"bib": WORKING, "location": "Section 8.2"}, BOOK_H],
    related=[{"id": "zh-h-box-zero-state-copy", "relation": "see-also"},
             {"id": "zh-ortho", "relation": "derived-from"}],
    tags=["copy", "state", "post-selection", "AND"],
    notes=note(),
)

# =============================================================================================
# H-boxes and the ZX-calculus

# --- Hadamard as an H-box ---------------------------------------------------------------------
L = D()
L.wire(0, 0, 2, L.h(1, 0))
R = D()
R.he(R.b(0, 0), R.b(2, 0))
rule(
    "zh-hadamard-as-h-box", lhs=L, rhs=R, view="graph-like",
    name="Hadamard as an H-box",
    aliases=["Hadamard translation"],
    calculus="ZH", fragment="phase-free", group="zh-translation", order=1,
    summary="An arity-2 H-box with the standard label is √2 times a Hadamard gate.",
    description=(
        "The arity-2 H-box with label $-1$ is the matrix $\\begin{pmatrix}1&1\\\\1&-1\\end{pmatrix} = \\sqrt 2\\,H$. "
        "This is why H-boxes are called H-boxes: they generalise the Hadamard gate to any number of legs. Hence a "
        "Hadamard gate (drawn on the right as a Hadamard edge) can always be translated into an H-box and back.\n\n"
        "Because of this, ZH-diagrams often draw an arity-2 H-box and a Hadamard gate in the same way, ignoring the "
        "factor $\\sqrt 2$."),
    scalar="auto",
    source={"bib": ZH, "location": "Section 2.1, translation of the Hadamard gate"},
    also_in=[{"bib": WORKING, "location": "Section 8.1"}],
    related=[{"id": "zh-h-box-identity", "relation": "see-also"},
             {"id": "hadamard-cancellation", "relation": "see-also"}],
    tags=["Hadamard", "translation", "H-box"],
    notes=note(),
)

# --- Z-phase spider as Z-spider plus H-box ----------------------------------------------------
L = D()
z = L.z(1, 0, "alpha")
L.wire(0, 0, 2, z)
R = D()
z = R.z(1, 0)
R.wire(0, 0, 2, z)
R.e(R.h(1, -1, phase="alpha"), z)
rule(
    "zh-phase-spider-as-h-box", lhs=L, rhs=R,
    name="Z-phase as an H-box",
    aliases=["green spider translation", "phase as label"],
    calculus="ZH", fragment="universal", group="zh-translation", order=2,
    summary="A Z-spider with phase α is a phase-free Z-spider with an arity-1 H-box labelled e^{iα} attached.",
    description=(
        "A Z-spider with phase $\\alpha$ equals a phase-free Z-spider with an extra leg, plugged by the arity-1 H-box "
        "with label $e^{i\\alpha}$ (the state $|0\\rangle + e^{i\\alpha}|1\\rangle$). This is how ZX-diagrams are "
        "translated into ZH-diagrams: the ZH-calculus only has phase-free Z-spiders, and puts all phases into H-box "
        "labels.\n\n"
        "With [Hadamard as an H-box](../zh-hadamard-as-h-box/) this gives a translation of every ZX-diagram into the ZH-calculus."),
    variables={"alpha": "real"},
    scalar="1",
    source={"bib": ZH, "location": "Section 2.1, translation of the green spider"},
    also_in=[{"bib": WORKING, "location": "Section 8.2"}],
    related=[{"id": "zh-h-box-phase-state", "relation": "generalises"}],
    tags=["translation", "phase", "label", "Z-spider"],
)

# --- arity-1 H-box as Z-state -----------------------------------------------------------------
L = D()
L.e(L.h(0, 0, phase="alpha"), L.b(1, 0))
R = D()
R.e(R.z(0, 0, "alpha"), R.b(1, 0))
rule(
    "zh-h-box-phase-state", lhs=L, rhs=R,
    name="Arity-1 H-box is a Z-state",
    aliases=["H-box state"],
    calculus="ZH", fragment="universal", group="zh-translation", order=3,
    summary="An arity-1 H-box with label e^{iα} is the Z-state with phase α.",
    description=(
        "The arity-1 H-box with label $e^{i\\alpha}$ is the state $|0\\rangle + e^{i\\alpha}|1\\rangle$, which is the "
        "arity-1 Z-spider with phase $\\alpha$. With $\\alpha = 0$ and $\\alpha = \\pi$: the H-box labelled $1$ is the "
        "phase-free Z-state (the [unit rule](../zh-unit/)) and the standard H-box state is the Z-state with phase $\\pi$.\n\n"
        "(In the book the H-boxes are normalised with a factor $\\frac{1}{\\sqrt 2}$, which then appears here as a scalar.)"),
    variables={"alpha": "real"},
    scalar="1",
    source={"bib": WORKING, "location": "Section 8.2"},
    also_in=[BOOK_H],
    related=[{"id": "zh-unit", "relation": "generalises"}],
    tags=["state", "phase", "label", "translation"],
)

# --- X-spider via H-boxes ---------------------------------------------------------------------
L = D()
x = L.x(1, 0.5)
L.e(L.b(0, 0.5), x).outs(x, [0, 1], x=2)
R = D()
hi = R.h(1, 0.5)
z = R.z(2, 0.5)
h0 = R.h(3, 0)
h1 = R.h(3, 1)
R.e(R.b(0, 0.5), hi, z).e(z, h0, R.b(4, 0)).e(z, h1, R.b(4, 1))
rule(
    "zh-x-spider-as-h-boxes", lhs=L, rhs=R,
    name="X-spider from H-boxes",
    aliases=["grey spider definition", "(X)"],
    calculus="ZH", fragment="clifford", group="zh-translation", order=4,
    summary="A phase-free X-spider is a Z-spider with arity-2 H-boxes on all its legs, up to a scalar.",
    description=(
        "In the ZH-calculus the X-spider (the grey spider) is not a generator but is *defined* as a phase-free "
        "Z-spider with an arity-2 H-box on each leg, together with a scalar. This is the ZH version of the "
        "[colour change](../colour-change/) rule. Classically, the grey spider is the XOR.\n\n"
        "The scalar here is for the PyZX normalisation of the X-spider, and differs from the one in the papers, where "
        "the grey spider is normalised so that it is exactly the XOR on basis states."),
    parameters={"n": 3},
    parameter_notes="Shown for an X-spider with n = 3 legs; holds for any n (with the scalar depending on n).",
    scalar="auto",
    source={"bib": ZH, "location": "Section 2.1, definition of the grey spider"},
    also_in=[{"bib": PF, "location": "Section 3, definition (X)"},
             {"bib": ZHC, "location": "Section 2.1, definition (X)"}],
    related=[{"id": "colour-change", "relation": "equivalent-to"},
             {"id": "zh-hadamard-as-h-box", "relation": "see-also"}],
    tags=["X-spider", "grey spider", "XOR", "translation", "definition"],
    notes=note(),
)

# --- arity-2 H-box as phase gadget -------------------------------------------------------------
L = D()
L.wire(0, 0, 4, L.h(2, 0, phase="alpha"))
R = D()
z1 = R.z(1, 0, "alpha/2")
x = R.x(2, 0)
z2 = R.z(3, 0, "alpha/2")
g = R.z(2, -1, "-alpha/2")
R.wire(0, 0, 4, z1, x, z2)
R.e(x, g)
rule(
    "zh-h-box-phase-gadget-2", lhs=L, rhs=R,
    name="Arity-2 H-box as a phase gadget",
    aliases=["controlled phase decomposition", "CZ(α)"],
    calculus="ZH", fragment="universal", group="zh-translation", order=5,
    summary="An arity-2 H-box with label e^{iα} decomposes into Z-phases α/2 and a phase gadget with phase −α/2.",
    description=(
        "An arity-2 H-box with label $e^{i\\alpha}$ is the diagonal map that applies the phase $e^{i\\alpha xy}$ to "
        "$|x,y\\rangle$ (read as a state on two qubits it is a controlled phase gate applied to $|{+}{+}\\rangle$). "
        "Using $xy = \\frac{1}{2}(x + y - x\\oplus y)$ this phase can be written with two Z-phases $\\frac{\\alpha}{2}$ "
        "and one [phase gadget](../phase-gadget-fusion/) with phase $-\\frac{\\alpha}{2}$ on the parity $x\\oplus y$.\n\n"
        "This is the simplest instance of the *graphical Fourier transform*, which turns any H-box with a phase label "
        "into phase gadgets; see the [arity-3 version](../zh-h-box-phase-gadget-3/)."),
    variables={"alpha": "real"},
    scalar="auto",
    source=BOOK_H,
    also_in=[{"bib": WORKING, "location": "Section 8.4"}],
    related=[{"id": "zh-h-box-phase-gadget-3", "relation": "variant-of"},
             {"id": "phase-gadget-fusion", "relation": "see-also"}],
    tags=["phase gadget", "Fourier transform", "controlled phase", "translation"],
    notes=note(),
)

# --- arity-3 H-box as phase gadgets ------------------------------------------------------------
L = D()
h = L.h(2, 1.2, phase="alpha")
L.outs(h, [0, 1.2, 2.4], x=4.5)
R = D()
ys = (0, 1.2, 2.4)
zs = [R.z(3.5, y, "alpha/4") for y in ys]
for y, zz in zip(ys, zs):
    R.e(zz, R.b(4.5, y))
gadgets = [((0, 1), 0.6, "-alpha/4"), ((1, 2), 1.8, "-alpha/4"), ((0, 2), -0.9, "-alpha/4"), ((0, 1, 2), 3.3, "alpha/4")]
for legs, y, ph in gadgets:
    xx = R.x(2.3, y)
    R.e(R.z(1.2, y, ph), xx)
    for k in legs:
        R.e(xx, zs[k])
rule(
    "zh-h-box-phase-gadget-3", lhs=L, rhs=R,
    name="Arity-3 H-box as phase gadgets",
    aliases=["CCZ(α) decomposition", "graphical Fourier transform"],
    calculus="ZH", fragment="universal", group="zh-translation", order=6,
    summary="An arity-3 H-box with label e^{iα} decomposes into phases ±α/4 on all non-empty parities of its legs.",
    description=(
        "An arity-3 H-box with label $e^{i\\alpha}$ applies the phase $e^{i\\alpha xyz}$. Using the identity "
        "$4xyz = x + y + z - x\\oplus y - x\\oplus z - y\\oplus z + x\\oplus y\\oplus z$ this can be written with a "
        "Z-phase $\\frac{\\alpha}{4}$ on each leg, phase gadgets with phase $-\\frac{\\alpha}{4}$ on each pair of legs, and a "
        "phase gadget with phase $\\frac{\\alpha}{4}$ on all three legs.\n\n"
        "With $\\alpha = \\pi$ this is the well-known decomposition of the CCZ gate into seven T-like phases. "
        "In general, an H-box with $n$ legs decomposes in this way into $2^n - 1$ phase gadgets with phases $\\pm\\frac{\\alpha}{2^{n-1}}$."),
    variables={"alpha": "real"},
    scalar="auto",
    source=BOOK_H,
    also_in=[{"bib": WORKING, "location": "Section 8.4"}],
    related=[{"id": "phase-gadget-fusion", "relation": "see-also"}],
    tags=["phase gadget", "Fourier transform", "CCZ", "Toffoli", "T-count", "translation"],
    notes=note(),
)

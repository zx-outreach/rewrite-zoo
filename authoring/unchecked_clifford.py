"""Axioms of the complete axiomatisations in data/axiomatisations-clifford.json that cannot be represented
in PyZX: Backens' star, bare cups and caps, braidings, and the fermionic crossing of the ZW-calculus.
These rules are only drawn (checked=False), in the style of examples_special.py.

Drawing conventions used here:
* the fermionic crossing is D.sym(x, y, "crossing") with four legs (the two strands pass straight through);
* an ordinary swap / braiding is drawn as two wires that simply cross, without a vertex;
* curved wires use invisible way points (D.way, a quadratic control point) and invisible joints
  (a "crossing" symbol with only two legs), see the helpers below;
* ZW translations follow authoring/zw.py: the black vertex with a binary black vertex on one leg is PyZX's
  W-node (triangle + dot), a lone triangle is the symmetric black vertex, the binary black vertex is the NOT
  gate X(pi), white vertices are Z-spiders (2015: with phase pi) and r-labelled white vertices are Z-boxes.
"""

from dsl import D, rule, VT

ZW15 = "hadzihasanovic2015diagrammatic"
THESIS = "hadzihasanovic2017algebra"
LICS = "HarnyAmarCompleteness"
CARETTE = "carette2023compositionality"


def r15(loc):
    return {"bib": ZW15, "location": f"Section 3 (The rules), {loc}"}


def th(loc):
    return {"bib": THESIS, "location": f"Chapter 5, Section 5.2 (list of rules of the ZW calculus), rule {loc}"}


def lics(loc):
    return {"bib": LICS, "location": f"Section 3, ZW axiom {loc}"}


def car(loc):
    return {"bib": CARETTE, "location": f"Figure 1 (axioms of the planar W-calculus), {loc}"}


FERMIONIC = "uses the fermionic crossing of the ZW-calculus, which is not a PyZX generator"
CROSSING_EXPLAINER = (
    "The *crossing* (fermionic swap) of the ZW-calculus is the map "
    "$|00\\rangle\\langle 00| + |01\\rangle\\langle 10| + |10\\rangle\\langle 01| - |11\\rangle\\langle 11|$: a swap "
    "that picks up a sign $-1$ when two $|1\\rangle$'s (two fermions) are exchanged. It equals a SWAP followed by a "
    "CZ. It behaves like a symmetric braiding, except that it is only natural for *even* maps (those whose terms all "
    "have an even number of 1s); maps of odd parity, such as the black vertices, pick up signs. ")


# ---------------------------------------------------------------------------------------------
# drawing helpers


def C(x, y):
    """A control (way) point of a curved wire."""
    return ("c", x, y)


def P(x, y):
    """An invisible joint on a wire (where a straight piece and a curve meet smoothly)."""
    return ("p", x, y)


def FX(d, x, y):
    """The fermionic crossing (four legs)."""
    return d.sym(x, y, "crossing")


def path(d, *items):
    """Connect vertices / control points / joints in a chain; returns the vertices."""
    vs = []
    for it in items:
        if isinstance(it, tuple):
            kind, x, y = it
            vs.append(d.way(x, y) if kind == "c" else d.sym(x, y, "crossing"))
        else:
            vs.append(it)
    d.e(*vs)
    return vs


def pos(d, v):
    return d.g.row(v), d.g.qubit(v)


def strand(d, a, b, X, dd=0.5):
    """An S-shaped strand from a to b through X (a crossing vertex, or a point for a plain crossing).
    X must lie halfway between a and b vertically for the strand to be smooth."""
    (ax, ay), (bx, by) = pos(d, a), pos(d, b)
    if isinstance(X, tuple):
        X = d.sym(X[0], X[1], "crossing")  # joint of a plain crossing
    xx, _ = pos(d, X)
    path(d, a, C(xx - dd, ay), X, C(xx + dd, by), b)


def curl(d, a, b, x, y0, side=-1, fermionic=True, h=0.45, u=0.6):
    """A wire from a to b (both at height y0) with a curl at x: above the wire for side=-1, below for +1.
    The self-intersection is a fermionic crossing, or a plain crossing (braiding)."""
    s = side
    X = (x, y0 + s * h)
    top = y0 + s * (h + u)
    if fermionic:
        X1 = X2 = FX(d, *X)
    else:
        X1, X2 = d.sym(*X, "crossing"), d.sym(*X, "crossing")
    path(d, a, C(x - h, y0), X1, C(x + u, top), P(x, top), C(x - u, top), X2, C(x + h, y0), b)


def black(d, x, y):
    """A symmetric black vertex of the ZW-calculus (PyZX's W-node without its input dot)."""
    return d._v(VT.W_OUTPUT, x, y)


def base(**kw):
    m = dict(checked=False)
    m.update(kw)
    return m


# =============================================================================================
# Backens' star rule

L = D()
L.sym(0, 0, "star")
L.z(1, 0)
R = D()
rule(
    "star-rule", lhs=L, rhs=R,
    name="Star rule",
    aliases=["star node", "inverse of the scalar 2", "halfscalar"],
    **base(
        calculus="ZX", fragment="clifford", group="scalars", order=20,
        unchecked_reason="uses Backens' star generator (the scalar 1/2), which PyZX cannot represent",
        summary="A new scalar generator, the star, is the inverse of the legless phase-free Z-spider.",
        description=(
            "To make the stabilizer ZX-calculus complete *with* scalars, Backens adds a new generator with no "
            "inputs or outputs, the *star* $\\star$, interpreted as $\\frac12$. It is defined by the star rule: "
            "the star next to the legless phase-free Z-spider (the scalar 2) is the empty diagram. From it one "
            "derives inverses for all other non-zero stabilizer scalars.\n\n"
            "When scalars are written as numbers, as in the zoo, this rule just says that the legless Z-spider is "
            "the number 2: the $\\alpha = 0$ case of [legless Z-spiders](../scalar-z-spider/)."),
        scalar="1",
        source={"bib": "Backens:2015aa", "location": "Section 3.2, Definition 2 (star rule)"},
        related=[{"id": "scalar-z-spider", "relation": "see-also"},
                 {"id": "zh-zero-star", "relation": "see-also"}],
        tags=["star", "scalar", "inverse", "1/2"],
    ))

# ---------------------------------------------------------------------------------------------
# ZH: the zero scalar absorbs a star

L = D()
L.sym(0, 0, "star")
L.e(L.z(1, 0), L.h(2, 0))
R = D()
R.e(R.z(0, 0), R.h(1, 0))
rule(
    "zh-zero-star", lhs=L, rhs=R,
    name="Zero absorbs the star",
    aliases=["(Z)", "zero rule (phase-free ZH)", "star-zero rule"],
    **base(
        calculus="ZH", fragment="clifford+t", group="zh-arithmetic", order=20,
        unchecked_reason="uses the star generator (the scalar 1/√2), which PyZX cannot represent",
        summary="The zero scalar (a Z-spider plugged into an arity-1 H-box) absorbs a star.",
        description=(
            "The phase-free ZH-calculus has only H-boxes labelled $-1$; to write the normalisation factors of "
            "the grey spider and the NOT it adds a scalar generator, the *star* $\\star$, interpreted as "
            "$\\frac{1}{\\sqrt 2}$. A Z-spider plugged into an arity-1 H-box is $1 + (-1) = 0$, and rule (Z) says "
            "that this zero scalar absorbs a star. It is the only rule that changes the parity of the number of "
            "stars, so it is needed for completeness.\n\n"
            "With scalars written as numbers both sides are $0$, so the rule is trivial."),
        scalar="1",
        source={"bib": "PhasefreeZH2019", "location": "Figure 2, rule (Z)"},
        related=[{"id": "star-rule", "relation": "see-also"},
                 {"id": "zh-zero-label", "relation": "see-also"}],
        tags=["star", "zero", "scalar", "phase-free ZH"],
    ))

# ---------------------------------------------------------------------------------------------
# (R1): a curl is a straight wire

L = D()
curl(L, L.b(0, 0), L.b(3, 0), 1.5, 0, side=-1, fermionic=False)
R = D()
R.wire(0, 0, 3)
rule(
    "reidemeister-curl", lhs=L, rhs=R,
    name="Curl removal (first Reidemeister move)",
    aliases=["(R1)", "Reidemeister I", "loop axiom", "twist removal"],
    **base(
        calculus="ZX", fragment="clifford", group="spiders", order=12,
        unchecked_reason="a wire crossing itself cannot be represented in PyZX graphs, where only connectivity matters",
        summary="A wire with a curl (crossing itself through a braiding) is a straight wire.",
        description=(
            "Backens, Perdrix and Wang show that the meta-rule *only connectivity matters* can be replaced by "
            "the axioms of a braided autonomous category, provided one adds the loop axiom (R1): a curl in a "
            "wire, made with the braiding (either way round), can be pulled straight. Together with the other "
            "rules this recovers the full ZX-calculus for stabilizer quantum mechanics.\n\n"
            "In PyZX and ZXLive only the connectivity of a diagram is stored, so this axiom holds by "
            "construction. The paper distinguishes over- and under-crossings, which are not drawn here."),
        scalar="1",
        source={"bib": "backens2017minimal", "location": "Section 4.2, Figure 3 (Reidemeister moves), rule (R1)"},
        related=[{"id": "cup-as-spider", "relation": "see-also"},
                 {"id": "fermionic-crossing-curl", "relation": "see-also"}],
        tags=["braiding", "Reidemeister", "curl", "3D isotopy", "only connectivity matters"],
    ))

# ---------------------------------------------------------------------------------------------
# Snake equation

L = D()
path(L, L.b(-0.4, 2), P(1.8, 2), C(2.8, 2), P(2.8, 1.5), C(2.8, 1), P(1.8, 1), P(0.8, 1),
     C(-0.2, 1), P(-0.2, 0.5), C(-0.2, 0), P(0.8, 0), L.b(3.2, 0))
R = D()
R.wire(1, -0.4, 3.2)
rule(
    "snake-equation", lhs=L, rhs=R,
    name="Snake equation",
    aliases=["adj_L", "yanking", "zigzag", "compact structure", "cup-cap cancellation"],
    **base(
        calculus="ZX", fragment="phase-free", group="spiders", order=6,
        unchecked_reason="bare cups and caps cannot be represented with ZXLive-style boundaries",
        summary="A cup followed by a cap is a straight wire.",
        description=(
            "The snake (or yanking) equations say that the cup and the cap are each other's inverse when "
            "composed side by side: a wire with a zigzag can be pulled straight. They are the defining axioms of "
            "a compact closed category, and hold in the ZX-, ZH- and ZW-calculus alike. Hadzihasanovic's "
            "presentation of the ZW-calculus lists them as axiom $adj_L$ (and its mirror image).\n\n"
            "Together with [cups as spiders](../cup-as-spider/) this is what makes *only connectivity matters* "
            "work. In PyZX and ZXLive it holds by construction."),
        scalar="1",
        source=th("$adj_L$"),
        related=[{"id": "cup-as-spider", "relation": "see-also"},
                 {"id": "cup-swap-symmetry", "relation": "see-also"}],
        tags=["cup", "cap", "snake", "yanking", "compact closed"],
    ))

# ---------------------------------------------------------------------------------------------
# Cups are symmetric

L = D()
o1, o2 = L.b(3, 0), L.b(3, 1)
path(L, o1, P(1.4, 1), C(0.637, 1.477), P(0.637, 0.5), C(0.637, -0.477), P(1.4, 0), o2)
R = D()
path(R, R.b(3, 0), C(1.0, 0), P(1.0, 0.5), C(1.0, 1), R.b(3, 1))
rule(
    "cup-swap-symmetry", lhs=L, rhs=R,
    name="Cups are symmetric",
    aliases=["com", "symmetry of the cup", "symmetry of the cap", "self-dual compact structure"],
    **base(
        calculus="ZX", fragment="phase-free", group="spiders", order=7,
        unchecked_reason="bare cups and caps cannot be represented with ZXLive-style boundaries",
        summary="A cup followed by a swap is the cup (and likewise for the cap).",
        description=(
            "Swapping the two legs of a cup gives the cup back; upside down, the same holds for the cap. This is "
            "the axiom $com$ of Hadzihasanovic's ZW-calculus, which makes the compact structure *symmetric*. "
            "It holds in the ZX-, ZH- and ZW-calculus alike, and is built into PyZX and ZXLive, where only "
            "connectivity matters.\n\n"
            "The swap here is an ordinary swap of wires, not the fermionic crossing of the ZW-calculus."),
        scalar="1",
        source=th("$com$"),
        related=[{"id": "cup-as-spider", "relation": "see-also"}],
        tags=["cup", "cap", "swap", "symmetry", "compact closed"],
    ))

# ---------------------------------------------------------------------------------------------
# Hadamard is self-transpose

L = D()
_, _, _, _, j1 = path(L, L.b(-0.4, 2), C(3.0, 2), P(3.0, 1.5), C(3.0, 1), P(2.2, 1))
j2 = L.sym(1.0, 1, "crossing")
L.he(j1, j2)
path(L, j2, C(0.2, 1), P(0.2, 0.5), C(0.2, 0), L.b(3.6, 0))
R = D()
R.he(R.b(0, 1), R.b(3, 1))
rule(
    "hadamard-transpose", lhs=L, rhs=R,
    name="Hadamard is self-transpose",
    aliases=["1(e)", "Hadamard transpose", "Hadamard symmetry"],
    **base(
        calculus="ZX", fragment="universal", group="hadamard", order=20,
        unchecked_reason="bent wires (cups and caps) cannot be drawn with ZXLive-style boundaries; Hadamard edges are undirected in PyZX, so this holds by construction",
        summary="Bending both wires of a Hadamard gate (taking its transpose) gives the Hadamard gate.",
        description=(
            "The Hadamard gate is a symmetric matrix, so it equals its own transpose: bending its input wire up "
            "with a cap and its output wire down with a cup gives the Hadamard gate again. Because of this, "
            "the Hadamard gate can be treated as an undirected edge decoration, which is how PyZX represents "
            "it. In the complete axiomatisation of Hadzihasanovic, Ng and Wang this is axiom 1(e)."),
        scalar="1",
        source={"bib": LICS, "location": "Section 4, ZX axiom 1(e)"},
        related=[{"id": "colour-change", "relation": "see-also"},
                 {"id": "hadamard-cancellation", "relation": "see-also"}],
        tags=["Hadamard", "transpose", "cup", "cap", "symmetric"],
    ))

# =============================================================================================
# Fermionic crossing rules

ORDER = iter(range(1, 100))

# --- two crossings cancel
L = D()
X1, X2 = FX(L, 1, 0.5), FX(L, 2, 0.5)
path(L, L.b(0, 0), C(0.5, 0), X1, C(1.5, 1), X2, C(2.5, 0), L.b(3, 0))
path(L, L.b(0, 1), C(0.5, 1), X1, C(1.5, 0), X2, C(2.5, 1), L.b(3, 1))
R = D()
R.wire(0, 0, 3)
R.wire(1, 0, 3)
rule(
    "fermionic-crossing-involution", lhs=L, rhs=R,
    name="Crossing is an involution",
    aliases=["rei^x_2", "1(a)", "second Reidemeister move", "fermionic swap involution"],
    **base(
        calculus="ZW", fragment="universal", group="fermionic", order=next(ORDER),
        unchecked_reason=FERMIONIC,
        summary="Two fermionic crossings in a row cancel.",
        description=(CROSSING_EXPLAINER + "\n\n"
                     "Like an ordinary swap, the crossing is its own inverse (the second Reidemeister move): "
                     "the signs $-1$ of the two crossings cancel."),
        scalar="1",
        source=th("$rei^x_2$"),
        also_in=[lics("1(a)")],
        related=[{"id": "fermionic-crossing-yang-baxter", "relation": "see-also"}],
        tags=["crossing", "fermionic swap", "involution", "Reidemeister"],
    ))

# --- Yang-Baxter
def yb(flip):
    d = D()
    f = (lambda y: 2 - y) if flip else (lambda y: y)
    X1, X2, X3 = FX(d, 1, f(0.5)), FX(d, 2, f(1.5)), FX(d, 3, f(0.5))
    path(d, d.b(0, f(0)), C(0.5, f(0)), X1, X2, C(2.5, f(2)), d.b(4, f(2)))
    path(d, d.b(0, f(1)), C(0.5, f(1)), X1, C(2, f(-0.5)), X3, C(3.5, f(1)), d.b(4, f(1)))
    path(d, d.b(0, f(2)), C(1.5, f(2)), X2, X3, C(3.5, f(0)), d.b(4, f(0)))
    return d


rule(
    "fermionic-crossing-yang-baxter", lhs=yb(False), rhs=yb(True),
    name="Yang–Baxter equation for the crossing",
    aliases=["rei^x_3", "1(b)", "third Reidemeister move", "braid relation"],
    **base(
        calculus="ZW", fragment="universal", group="fermionic", order=next(ORDER),
        unchecked_reason=FERMIONIC,
        summary="The fermionic crossing satisfies the Yang–Baxter equation (third Reidemeister move).",
        description=(CROSSING_EXPLAINER + "\n\n"
                     "Three wires can be permuted by crossings in two different orders; the Yang–Baxter "
                     "equation says that the result is the same. Together with [the involution rule]"
                     "(../fermionic-crossing-involution/) this makes the crossings generate a representation of "
                     "the symmetric group (with signs)."),
        scalar="1",
        source=th("$rei^x_3$"),
        also_in=[lics("1(b)"), car("row 4, 2nd axiom")],
        related=[{"id": "fermionic-crossing-involution", "relation": "see-also"}],
        tags=["crossing", "fermionic swap", "Yang-Baxter", "Reidemeister"],
    ))

# --- curl moves to the other side
L = D()
curl(L, L.b(0, 0), L.b(3, 0), 1.5, 0, side=-1)
R = D()
curl(R, R.b(0, 0), R.b(3, 0), 1.5, 0, side=1)
rule(
    "fermionic-crossing-curl", lhs=L, rhs=R,
    name="Crossing curls can change side",
    aliases=["rei^x_1", "1(e)", "first Reidemeister move for the crossing"],
    **base(
        calculus="ZW", fragment="universal", group="fermionic", order=next(ORDER),
        unchecked_reason=FERMIONIC,
        summary="A curl made with the fermionic crossing can be moved from one side of a wire to the other.",
        description=(CROSSING_EXPLAINER + "\n\n"
                     "A wire that crosses itself through a fermionic crossing is not a plain wire: it is the "
                     "Pauli Z, $\\mathrm{diag}(1, -1)$ (see [the curl is −1](../fermionic-curl-minus-one/)). This "
                     "axiom says that it does not matter on which side of the wire the curl is drawn."),
        scalar="1",
        source=th("$rei^x_1$"),
        also_in=[lics("1(e)")],
        related=[{"id": "fermionic-curl-minus-one", "relation": "see-also"},
                 {"id": "reidemeister-curl", "relation": "see-also"}],
        tags=["crossing", "fermionic swap", "curl", "Reidemeister"],
    ))


# --- cup / cap slide through the crossing
def nat_cup(lhs, cap):
    d = D()
    f = (lambda x: 4 - x) if cap else (lambda x: x)
    if lhs:
        wa, wb = d.b(f(0), 0), d.b(f(4), 2)
        o1, o2 = d.b(f(4), 0), d.b(f(4), 1)
        X1, X2 = FX(d, f(1.818), 0.909), FX(d, f(2.909), 1.4545)
        d.e(wa, X1, X2, wb)
        path(d, o1, X1, P(f(1.6), 1), C(f(0.769), 1.346), P(f(0.769), 1.846), C(f(0.769), 2.346), P(f(1.6), 2), X2, o2)
    else:
        d.e(d.b(f(0), 0), d.b(f(4), 0))
        path(d, d.b(f(4), 1), C(f(1.6), 1), P(f(1.6), 1.5), C(f(1.6), 2), d.b(f(4), 2))
    return d


rule(
    "fermionic-crossing-cup", lhs=nat_cup(True, False), rhs=nat_cup(False, False),
    name="Cups slide through the crossing",
    aliases=["nat_x^η", "1(c)", "naturality of the crossing for the cup"],
    **base(
        calculus="ZW", fragment="universal", group="fermionic", order=next(ORDER),
        unchecked_reason=FERMIONIC + "; bare cups cannot be drawn with ZXLive-style boundaries",
        summary="A wire crossing both legs of a cup can be moved off the cup.",
        description=(CROSSING_EXPLAINER + "\n\n"
                     "The cup $|00\\rangle + |11\\rangle$ is even, so the crossing is natural with respect to it: a "
                     "wire that crosses both legs of a cup (through two fermionic crossings) can be pulled off "
                     "it. The signs of the two crossings cancel."),
        scalar="1",
        source=th("$nat_x^\\eta$"),
        also_in=[lics("1(c)")],
        related=[{"id": "fermionic-crossing-cap", "relation": "variant-of"}],
        tags=["crossing", "fermionic swap", "cup", "naturality"],
    ))

rule(
    "fermionic-crossing-cap", lhs=nat_cup(True, True), rhs=nat_cup(False, True),
    name="Caps slide through the crossing",
    aliases=["nat_x^ε", "1(d)", "naturality of the crossing for the cap"],
    **base(
        calculus="ZW", fragment="universal", group="fermionic", order=next(ORDER),
        unchecked_reason=FERMIONIC + "; bare caps cannot be drawn with ZXLive-style boundaries",
        summary="A wire crossing both legs of a cap can be moved off the cap.",
        description=(CROSSING_EXPLAINER + "\n\n"
                     "The upside-down version of [cups slide through the crossing](../fermionic-crossing-cup/): "
                     "the cap is even, so a wire crossing both of its legs can be pulled off it."),
        scalar="1",
        source=th("$nat_x^\\varepsilon$"),
        also_in=[lics("1(d)")],
        tags=["crossing", "fermionic swap", "cap", "naturality"],
    ))

# --- 7a: the black monoid is even
L = D()
wo, wi = L.w(1.5, 1.5, input_dir=(0.35, 0))
L.e(L.b(0, 1), wo).e(L.b(0, 2), wo)
X = FX(L, 2.8, 0.75)
strand(L, wi, L.b(4, 0), X)
strand(L, L.b(0, 0), L.b(4, 1.5), X)
R = D()
X1, X2 = FX(R, 1, 0.5), FX(R, 2, 1.5)
wo, wi = R.w(3.2, 0.5, input_dir=(0.35, 0))
R.e(wi, R.b(4.5, 0.5))
path(R, R.b(0, 0), C(0.5, 0), X1, X2, C(2.5, 2), R.b(4.5, 2))
path(R, R.b(0, 1), C(0.5, 1), X1, C(1.5, 0), wo)
path(R, R.b(0, 2), C(1.5, 2), X2, C(2.5, 1), wo)
rule(
    "fermionic-crossing-w-merge", lhs=L, rhs=R,
    name="W merge passes through the crossing",
    aliases=["7a", "nat_x^w", "2(a)", "the black monoid is even", "naturality of the crossing for the W-node"],
    **base(
        calculus="ZW", fragment="clifford+t", group="fermionic", order=next(ORDER),
        unchecked_reason=FERMIONIC,
        summary="A wire crossing the output of a W merge equals the wire crossing both of its inputs.",
        description=(CROSSING_EXPLAINER + "\n\n"
                     "The W-node used as a merge (the black monoid: a ternary black vertex followed by a binary "
                     "black vertex) is an *even* map, so the crossing is natural for it: a wire crossing its "
                     "output can be moved to cross both of its inputs instead, without a sign. Compare with the "
                     "odd [NOT gate](../fermionic-crossing-not/) and with the symmetric black vertex, which is odd "
                     "and [picks up a sign](../fermionic-crossing-w-sign/)."),
        scalar="1",
        source=r15("Rule 7a"),
        also_in=[th("$nat_x^w$"), lics("2(a)")],
        related=[{"id": "fermionic-crossing-not", "relation": "see-also"},
                 {"id": "fermionic-crossing-w-sign", "relation": "see-also"},
                 {"id": "w-bialgebra", "relation": "see-also"}],
        tags=["crossing", "fermionic swap", "W", "naturality", "even"],
    ))

# --- 7b: the binary black vertex is odd
L = D()
X = FX(L, 2, 0.5)
strand(L, L.b(0, 0), L.b(3.5, 1), X)
xp = L.x(0.8, 1, 1)
L.e(L.b(0, 1), xp)
strand(L, xp, L.b(3.5, 0), X)
R = D()
X = FX(R, 1.2, 0.5)
zp, xp = R.z(2.5, 1, 1), R.x(2.5, 0, 1)
strand(R, R.b(0, 0), zp, X)
strand(R, R.b(0, 1), xp, X)
R.e(zp, R.b(3.5, 1)).e(xp, R.b(3.5, 0))
rule(
    "fermionic-crossing-not", lhs=L, rhs=R,
    name="NOT through the crossing",
    aliases=["7b", "ant_x^n", "2(g)", "the binary black vertex is odd"],
    **base(
        calculus="ZW", fragment="clifford+t", group="fermionic", order=next(ORDER),
        unchecked_reason=FERMIONIC,
        summary="Moving a NOT (binary black vertex) through the crossing leaves a Pauli Z on the other wire.",
        description=(CROSSING_EXPLAINER + "\n\n"
                     "The binary black vertex of the ZW-calculus is the NOT gate (here the X-spider with phase "
                     "$\\pi$). It is *odd*, so the crossing is not natural for it: moving it through the crossing "
                     "leaves the binary white vertex, the Pauli Z (Z-spider with phase $\\pi$), on the other wire. "
                     "Indeed, the crossing is $\\mathrm{CZ}\\circ\\mathrm{SWAP}$ and $\\mathrm{CZ}$ maps "
                     "$X\\otimes I$ to $X\\otimes Z$.\n\n"
                     "In Hadzihasanovic's thesis ($ant_x^n$) and in Hadzihasanovic, Ng and Wang (2(g)) the Pauli Z "
                     "is drawn as a [curl through the crossing](../fermionic-curl-minus-one/)."),
        scalar="1",
        source=r15("Rule 7b"),
        also_in=[th("$ant_x^n$"), lics("2(g)")],
        related=[{"id": "fermionic-crossing-w-merge", "relation": "see-also"},
                 {"id": "cz-pauli-propagation", "relation": "see-also"}],
        tags=["crossing", "fermionic swap", "NOT", "odd", "Pauli"],
    ))

# --- X: elimination of crossings
def elim(fermionic):
    d = D()
    z1, z2 = d.z(1.6, 1), d.z(1.6, 2)
    wo, wi = d.w(2.6, 1.5, input_dir=(0.35, 0))
    d.e(wi, d.b(4, 1.5)).e(z1, wo).e(z2, wo)
    d.e(d.b(0, 0), z1).e(d.b(0, 3), z2)
    if fermionic:
        X = FX(d, 0.8, 1.5)
        d.e(d.b(0, 1), X, z2).e(d.b(0, 2), X, z1)
    else:
        d.e(d.b(0, 1), z2).e(d.b(0, 2), z1)
    return d


rule(
    "fermionic-crossing-elimination", lhs=elim(True), rhs=elim(False),
    name="Elimination of crossings",
    aliases=["X", "rule X", "crossing elimination"],
    **base(
        calculus="ZW", fragment="clifford+t", group="fermionic", order=next(ORDER),
        unchecked_reason=FERMIONIC,
        summary="Between the legs of two white vertices merged by a W-node, a fermionic crossing is an ordinary swap.",
        description=(CROSSING_EXPLAINER + "\n\n"
                     "Rule X of Hadzihasanovic's first complete ZW-calculus: two white vertices whose outputs are "
                     "merged by a black monoid (a W-node), with their inputs interleaved through a fermionic "
                     "crossing, equal the same diagram with an ordinary swap. It is used to eliminate crossings "
                     "when rewriting to normal form.\n\n"
                     "In the 2015 paper the white structures are a ternary white vertex with a binary white vertex "
                     "on its output, i.e. two Z-spiders with phase $\\pi$, which fuse to the phase-free Z-spiders "
                     "drawn here."),
        scalar="1",
        source=r15("Rule X"),
        related=[{"id": "fermionic-crossing-unx", "relation": "see-also"}],
        tags=["crossing", "fermionic swap", "elimination", "swap"],
    ))


# --- symmetry of black / white vertices under swaps and crossings
def sym(kind, crossing):
    """kind: 'w' (W-node) or 'z' (Z-box r). crossing: None (straight), 'swap' or 'fermionic'."""
    d = D()
    if kind == "w":
        v, wi = d.w(1.5, 0.5)
        d.e(d.b(0, 0.5), wi)
    else:
        v = d.zbox(1.5, 0.5, "r")
        d.e(d.b(0, 0.5), v)
    o0, o1, o2 = d.b(4.5, 0), d.b(4.5, 1), d.b(4.5, 2.4)
    d.e(v, o2)
    if crossing is None:
        d.e(v, o0).e(v, o1)
        return d
    if crossing == "fermionic":
        X1 = X2 = FX(d, 3.1, 0.5)
    else:
        X1, X2 = d.sym(3.1, 0.5, "crossing"), d.sym(3.1, 0.5, "crossing")
    path(d, v, C(2.3, 1.1), X1, C(3.9, -0.1), o0)
    path(d, v, C(2.3, -0.1), X2, C(3.9, 1.1), o1)
    return d


rule(
    "w-swap-symmetry", lhs=sym("w", "swap"), rhs=sym("w", None),
    name="W-nodes are symmetric",
    aliases=["0a", "0b", "sym_w", "2(e)", "symmetry of the black vertex"],
    **base(
        calculus="ZW", fragment="clifford+t", group="zw-rules", order=20,
        unchecked_reason="both sides are the same PyZX graph: symmetry of the generator is built into the graph representation",
        summary="Swapping two legs of a W-node (black vertex) gives the same W-node.",
        description=(
            "The black vertices of the ZW-calculus are symmetric: swapping two of their legs with an ordinary "
            "swap does not change them (Rule 0 of Hadzihasanovic 2015, $sym_w$ of his thesis). This is what "
            "allows treating them as vertices of an undirected graph. In PyZX the outputs of a W-node are "
            "unordered, so this holds by construction.\n\n"
            "The swap here is an ordinary swap; for the fermionic crossing see "
            "[W-nodes are symmetric under the crossing](../w-fermionic-symmetry/)."),
        parameter_notes="Shown for a W-node with three outputs; holds for any number of legs.",
        scalar="1",
        source=r15("Rule 0 (0a, 0b, 0b′)"),
        also_in=[th("$sym_w$"), lics("2(e)")],
        related=[{"id": "w-fermionic-symmetry", "relation": "see-also"},
                 {"id": "z-swap-symmetry", "relation": "see-also"}],
        tags=["W", "symmetry", "swap", "black vertex"],
    ))

rule(
    "z-swap-symmetry", lhs=sym("z", "swap"), rhs=sym("z", None),
    name="White vertices are symmetric",
    aliases=["0c", "0d", "sym_z", "3(c)", "symmetry of the white vertex"],
    **base(
        calculus="ZW", fragment="clifford+t", group="zw-rules", order=21,
        unchecked_reason="both sides are the same PyZX graph: symmetry of the generator is built into the graph representation",
        variables={"r": "complex"},
        summary="Swapping two legs of a white vertex (Z-box) gives the same white vertex.",
        description=(
            "The (labelled) white vertices of the ZW-calculus, $|0\\cdots0\\rangle + r\\,|1\\cdots1\\rangle$, are "
            "symmetric: swapping two of their legs with an ordinary swap does not change them. In the 2015 paper "
            "(Rule 0) the white vertices are unlabelled Z-spiders with phase $\\pi$; in the thesis ($sym_z$) and "
            "in Hadzihasanovic, Ng and Wang (3(c)) they carry a label $r$ from a commutative ring. In PyZX this "
            "holds by construction."),
        parameter_notes="Shown for a white vertex with four legs; holds for any number of legs.",
        scalar="1",
        source=r15("Rule 0 (0c, 0d, 0d′)"),
        also_in=[th("$sym_z$"), lics("3(c)")],
        related=[{"id": "w-swap-symmetry", "relation": "see-also"}],
        tags=["Z-box", "white vertex", "symmetry", "swap"],
    ))

rule(
    "w-fermionic-symmetry", lhs=sym("w", "fermionic"), rhs=sym("w", None),
    name="W-nodes are symmetric under the crossing",
    aliases=["sym^x_w", "2(f)", "flexsymmetry"],
    **base(
        calculus="ZW", fragment="universal", group="fermionic", order=next(ORDER),
        unchecked_reason=FERMIONIC,
        summary="Crossing two legs of a W-node with the fermionic crossing gives the same W-node.",
        description=(CROSSING_EXPLAINER + "\n\n"
                     "Every term of a W-node has at most one $|1\\rangle$ among any two of its legs, so the sign of "
                     "the fermionic crossing never appears: black vertices are symmetric under the crossing as "
                     "well as under the [ordinary swap](../w-swap-symmetry/). In the planar W-calculus of Carette "
                     "et al., where wires may not cross, this is the axiom that removes a fermionic swap between "
                     "two adjacent legs of a black vertex."),
        parameter_notes="Shown for a W-node with three outputs; holds for any number of legs.",
        scalar="1",
        source=th("$sym^x_w$"),
        also_in=[lics("2(f)"), car("row 4, 1st axiom")],
        related=[{"id": "w-swap-symmetry", "relation": "see-also"}],
        tags=["W", "symmetry", "crossing", "fermionic swap"],
    ))

# --- ph: a curl moves between the legs of a white vertex
L = D()
z = L.z(2.6, 0.5)
curl(L, L.b(0, 0), z, 1.1, 0, side=-1)
L.e(L.b(0, 1), z).e(z, L.b(3.6, 0.5))
R = D()
z = R.z(1.0, 0.5)
R.e(R.b(0, 0), z).e(R.b(0, 1), z)
curl(R, z, R.b(3.6, 0.5), 2.3, 0.5, side=-1)
rule(
    "fermionic-curl-z-spider", lhs=L, rhs=R,
    name="Crossing curls move through white vertices",
    aliases=["ph", "3(g)", "phase rule"],
    **base(
        calculus="ZW", fragment="universal", group="fermionic", order=next(ORDER),
        unchecked_reason=FERMIONIC,
        summary="A crossing curl on one leg of a white vertex can be moved to another leg.",
        description=(CROSSING_EXPLAINER + "\n\n"
                     "A wire with a curl through the crossing is the Pauli Z ([the curl is −1]"
                     "(../fermionic-curl-minus-one/)). This axiom says that it commutes through white vertices "
                     "(Z-spiders): it can be moved from one leg to any other. In terms of ZX it is an instance "
                     "of [spider fusion](../spider-fusion/) with a phase $\\pi$."),
        scalar="1",
        source=th("$ph$"),
        also_in=[lics("3(g)")],
        related=[{"id": "fermionic-curl-minus-one", "relation": "see-also"},
                 {"id": "spider-fusion", "relation": "see-also"}],
        tags=["crossing", "fermionic swap", "curl", "phase", "white vertex"],
    ))


# --- unx: crossings between labelled white vertices on a W-node become swaps
def unx(fermionic):
    d = D()
    wo, wi = d.w(1.3, 1.5)
    d.e(d.b(0, 1.5), wi)
    zr, zs = d.zbox(2.3, 0.75, "r"), d.zbox(2.3, 2.25, "s")
    d.e(wo, zr).e(wo, zs)
    d.e(zr, d.b(4.5, 0)).e(zs, d.b(4.5, 3))
    a, b = d.b(4.5, 2.25), d.b(4.5, 0.75)
    if fermionic:
        X = FX(d, 3.4, 1.5)
        d.e(zr, X, a).e(zs, X, b)
    else:
        d.e(zr, a).e(zs, b)
    return d


rule(
    "fermionic-crossing-unx", lhs=unx(True), rhs=unx(False),
    name="Uncrossing white vertices on a W-node",
    aliases=["unx", "3(i)"],
    **base(
        calculus="ZW", fragment="universal", group="fermionic", order=next(ORDER),
        unchecked_reason=FERMIONIC,
        variables={"r": "complex", "s": "complex"},
        summary="Between the legs of two labelled white vertices on a W-node, a fermionic crossing is an ordinary swap.",
        description=(CROSSING_EXPLAINER + "\n\n"
                     "Two labelled white vertices (Z-boxes with labels $r$ and $s$) attached to the same W-node "
                     "never both carry a $|1\\rangle$, since the W-node spreads a single excitation. So a fermionic "
                     "crossing between a leg of one and a leg of the other never picks up a sign, and can be "
                     "replaced by an ordinary swap. This is the labelled analogue of "
                     "[rule X](../fermionic-crossing-elimination/)."),
        scalar="1",
        source=th("$unx$"),
        also_in=[lics("3(i)")],
        related=[{"id": "fermionic-crossing-elimination", "relation": "see-also"}],
        tags=["crossing", "fermionic swap", "swap", "Z-box", "W"],
    ))

# --- rng_{-1}: the white vertex -1 is a curl
L = D()
L.e(L.b(0, 0), L.zbox(1.5, 0, -1), L.b(3, 0))
R = D()
curl(R, R.b(0, 0), R.b(3, 0), 1.5, 0, side=-1)
rule(
    "fermionic-curl-minus-one", lhs=L, rhs=R,
    name="The curl is −1",
    aliases=["rng_{-1}", "3(j)", "self-crossing wire", "Pauli Z as a curl"],
    **base(
        calculus="ZW", fragment="universal", group="fermionic", order=next(ORDER),
        unchecked_reason=FERMIONIC,
        summary="The binary white vertex with label −1 (the Pauli Z) is a wire with a curl through the crossing.",
        description=(CROSSING_EXPLAINER + "\n\n"
                     "Bending one output of the crossing back to an input gives a wire that crosses itself. Its "
                     "only sign comes from the term $|11\\rangle$, so it is $\\mathrm{diag}(1, -1)$: the binary "
                     "white vertex with label $-1$, i.e. the Pauli Z. Hadzihasanovic's 2015 paper already "
                     "remarks that the binary white vertex is a self-crossing wire; in the ring-labelled "
                     "calculus this is the axiom $rng_{-1}$."),
        scalar="1",
        source=th("$rng_{-1}$"),
        also_in=[lics("3(j)")],
        related=[{"id": "fermionic-crossing-curl", "relation": "see-also"},
                 {"id": "fermionic-curl-z-spider", "relation": "see-also"}],
        tags=["crossing", "fermionic swap", "curl", "Pauli Z", "minus one"],
    ))

# --- Carette et al. (planar W-calculus): weights pass through the fermionic swap
L = D()
X = FX(L, 1.2, 0.5)
zr = L.zbox(2.6, 0, "r")
strand(L, L.b(0, 0), L.b(3.6, 1), X)
strand(L, L.b(0, 1), zr, X)
L.e(zr, L.b(3.6, 0))
R = D()
X = FX(R, 2.4, 0.5)
zr = R.zbox(1.0, 1, "r")
R.e(R.b(0, 1), zr)
strand(R, zr, R.b(3.6, 0), X)
strand(R, R.b(0, 0), R.b(3.6, 1), X)
rule(
    "fermionic-crossing-z-weight", lhs=L, rhs=R,
    name="Weights pass through the crossing",
    aliases=["fswap-Z", "naturality of the fermionic swap for weights"],
    **base(
        calculus="ZW", fragment="universal", group="fermionic", order=next(ORDER),
        unchecked_reason=FERMIONIC,
        variables={"r": "complex"},
        summary="A binary white vertex (weight r) moves through a fermionic crossing from one wire to the other.",
        description=(CROSSING_EXPLAINER + "\n\n"
                     "The binary white vertex $\\mathrm{diag}(1, r)$ (a weight $r$ on an edge, drawn as a Z-box) "
                     "is even, so the crossing is natural with respect to it: a weight on a wire after the "
                     "crossing equals the same weight on that wire before the crossing. In the planar W-calculus "
                     "of Carette et al. the fermionic swap is not a generator but syntactic sugar for a gadget of "
                     "black and white vertices; this axiom is one of the rules governing it."),
        scalar="1",
        source=car("row 3, 1st axiom"),
        related=[{"id": "fermionic-crossing-w-sign", "relation": "see-also"}],
        tags=["crossing", "fermionic swap", "weight", "Z-box", "planar W-calculus", "matchgates"],
    ))

# --- Carette et al.: a black vertex passes through fermionic swaps with a sign
def meet(p, q, r, s):
    """Intersection of the lines pq and rs."""
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = p, q, r, s
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
    return round(x1 + t * (x2 - x1), 4), round(y1 + t * (y2 - y1), 4)


L = D()
B = black(L, 3.2, 0.4)
w0, w1 = (0, 0), (5, 2.5)
X1, X2 = FX(L, *meet(w0, w1, (0, 1.2), (3.2, 0.4))), FX(L, *meet(w0, w1, (0, 2.0), (3.2, 0.4)))
L.e(L.b(*w0), X1, X2, L.b(*w1))
L.e(L.b(0, 1.2), X1, B).e(L.b(0, 2.0), X2, B)
L.e(B, L.b(5, 0)).e(B, L.b(5, 0.8))
R = D()
B = black(R, 1.8, 2.0)
w0, w1 = (0.8, 0), (5, 2.5)
X1, X2 = FX(R, *meet(w0, w1, (1.8, 2.0), (5, 0))), FX(R, *meet(w0, w1, (1.8, 2.0), (5, 0.8)))
R.e(R.b(0, 0), R.zbox(*w0, -1), X1, X2, R.b(*w1))
R.e(R.b(0, 1.2), B).e(R.b(0, 2.0), B)
R.e(B, X1, R.b(5, 0)).e(B, X2, R.b(5, 0.8))
rule(
    "fermionic-crossing-w-sign", lhs=L, rhs=R,
    name="Black vertices pass through the crossing with a sign",
    aliases=["fswaps-W", "the black vertex is odd"],
    **base(
        calculus="ZW", fragment="universal", group="fermionic", order=next(ORDER),
        unchecked_reason=FERMIONIC,
        summary="Moving a wire across a black vertex through fermionic crossings puts a weight −1 on it.",
        description=(CROSSING_EXPLAINER + "\n\n"
                     "The symmetric black vertex (the W-state $\\sum_k |0\\cdots010\\cdots0\\rangle$, drawn as a "
                     "triangle without input dot) is *odd*: each of its terms has exactly one $|1\\rangle$. So a "
                     "wire that crosses all its legs on one side through fermionic crossings can be moved to cross "
                     "all its legs on the other side, at the price of a weight $-1$ (the Pauli Z) on that wire.\n\n"
                     "Compare with [the W merge](../fermionic-crossing-w-merge/), which is even and passes the "
                     "crossing without a sign."),
        parameter_notes="Shown for a black vertex with two legs on each side; holds for any number of legs.",
        scalar="1",
        source=car("row 3, 2nd axiom"),
        related=[{"id": "fermionic-crossing-w-merge", "relation": "see-also"},
                 {"id": "fermionic-crossing-not", "relation": "see-also"}],
        tags=["crossing", "fermionic swap", "W", "odd", "sign", "planar W-calculus"],
    ))

# --- Carette et al.: the fermionic swap rotated by a cup and a cap
# The bent strand turns back with a cap, passes the crossing going down-left, and turns back with a cup
# (point-symmetric about the crossing).
L = D()
X = FX(L, 2.2, 1.4)
path(L, L.b(0, 0), P(1.8, 0), C(2.8, 0), P(2.8, 0.5), C(2.8, 0.8), X,
     C(1.6, 2.0), P(1.6, 2.3), C(1.6, 2.8), P(2.6, 2.8), L.b(4.4, 2.8))
path(L, L.b(0, 0.7), C(1.5, 0.7), X, C(2.9, 2.1), L.b(4.4, 2.1))
R = D()
X = FX(R, 2.2, 1.4)
strand(R, R.b(0, 0.35), R.b(4.4, 2.45), X, dd=0.8)
strand(R, R.b(0, 2.45), R.b(4.4, 0.35), X, dd=0.8)
rule(
    "fermionic-crossing-rotated", lhs=L, rhs=R,
    name="The rotated crossing is the crossing",
    aliases=["fswap-rotated", "the fermionic swap is self-transpose"],
    **base(
        calculus="ZW", fragment="universal", group="fermionic", order=next(ORDER),
        unchecked_reason=FERMIONIC + "; bent wires cannot be drawn with ZXLive-style boundaries",
        summary="Bending two legs of the fermionic crossing around (rotating it by a quarter turn) gives the crossing.",
        description=(CROSSING_EXPLAINER + "\n\n"
                     "Rotating the crossing by a quarter turn, by bending one input into an output with a cap and "
                     "one output into an input with a cup, gives the crossing again. In the planar W-calculus of "
                     "Carette et al. this is one of the axioms that let the fermionic swap be treated almost like "
                     "an ordinary swap."),
        scalar="1",
        source=car("row 4, 3rd axiom"),
        related=[{"id": "fermionic-crossing-cup", "relation": "see-also"}],
        tags=["crossing", "fermionic swap", "rotation", "transpose", "planar W-calculus"],
    ))

# --- Carette et al.: the zero axiom
L = D()
black(L, 1.7, -0.9)
L.wire(0, 0, 3.4)
R = D()
wo, wi = R.w(1.0, 0)
R.e(R.b(0, 0), wi)
wo, wi = R.w(2.2, 0, input_dir=(0.35, 0))
R.e(wi, R.b(3.4, 0))
rule(
    "w-zero-rule", lhs=L, rhs=R,
    name="ZW zero rule",
    aliases=["ax-zero", "zero axiom", "nullary black vertex"],
    **base(
        calculus="ZW", fragment="universal", group="zw-rules", order=22,
        unchecked_reason="the black vertex without legs (the scalar 0) is not a PyZX W-node",
        summary="The legless black vertex (the scalar 0) next to a wire equals 0 times the disconnected wire.",
        description=(
            "The black vertex with no legs is the empty sum, the scalar $0$. This axiom of the planar "
            "W-calculus says that a diagram multiplied by it is $0$ times a disconnected diagram: here a wire is "
            "cut into the effect $\\langle 0|$ and the state $|0\\rangle$, each a W-node with no outputs. It "
            "plays the role of the [zero rule](../zero-rule/) of the ZX-calculus.\n\n"
            "With the scalar $0$ written as a number both sides are $0$."),
        scalar="0",
        source=car("row 3, 3rd axiom"),
        related=[{"id": "zero-rule", "relation": "see-also"},
                 {"id": "w-zero-copy", "relation": "see-also"}],
        tags=["zero", "scalar", "W", "planar W-calculus"],
    ))

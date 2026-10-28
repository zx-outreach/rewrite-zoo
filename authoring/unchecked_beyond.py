"""Axioms of the complete axiomatisations beyond Clifford that cannot be represented in PyZX: the rules
for the triangle and the λ-box of Ng and Wang (and Hadzihasanovic, Ng and Wang), the parametrised
triangles of Jeandel, Perdrix and Vilmart, and the Hadamard sliding along a cap. They are only drawn
(checked=False), in the style of examples_special.py.

Conventions (as in the papers, which read diagrams from top to bottom; here inputs are on the left):
* the triangle is the matrix ((1, 1), (0, 1)) read from its *tip* to its base: a triangle pointing
  towards the inputs is |0><0| + |0><1| + |1><1|, a triangle pointing towards the outputs is its
  transpose. A triangle with a label r (Jeandel, Perdrix and Vilmart) is ((1, r), (0, 1)).
* the λ-box is diag(1, λ), λ ≥ 0.
* spiders are normalised as in PyZX, so a connected pair of phase-free Z- and X-spiders is √2.
Scalars that the papers write as diagrams are given as numbers (LHS = scalar · RHS).

    cd authoring && python unchecked_beyond.py [--force] [--only=id1,id2]
"""

import math

from dsl import D, rule

NG17 = "ng2017universal"
NG18 = "ng_completeness_2018"
HNW = "HarnyAmarCompleteness"
JPV = "jeandel2019completeness"

TRI_REASON = "the triangle is not a generator of PyZX or ZXLive"
TRI_LAM_REASON = "the triangle and the λ-box are not generators of PyZX or ZXLive"
PTRI_REASON = "the parametrised triangle is not a generator of PyZX or ZXLive"

TRI_NOTE = (
    "**Conventions.** The triangle is the matrix $\\begin{pmatrix}1&1\\\\0&1\\end{pmatrix}$ read from its tip to its "
    "base: a triangle pointing towards the inputs is $|0\\rangle\\langle 0|+|0\\rangle\\langle 1|+|1\\rangle\\langle 1|$, "
    "and a triangle pointing towards the outputs is its transpose. It can be written as a Clifford+T ZX-diagram. "
    "The papers read diagrams from top to bottom, so their triangles pointing up point towards the inputs here. "
    "Scalars that the papers write as diagrams (such as a connected pair of phase-free Z- and X-spiders, "
    "which is $\\sqrt 2$) are given here as numbers.")
LAM_NOTE = (
    "**Conventions.** The λ-box is the diagonal map $\\mathrm{diag}(1, \\lambda)$ with $\\lambda \\geq 0$ (a yellow box "
    "in the papers of Ng and Wang, a green box in the LICS'18 paper of Hadzihasanovic, Ng and Wang). "
    "Up to the fact that it is drawn differently, it is a Z-box of arity 2 with label $\\lambda$. "
    "Scalars that the papers write as diagrams are given here as numbers.")
LAMZ_NOTE = (
    "**Conventions.** The λ-box of Ng and Wang is the diagonal map $\\mathrm{diag}(1, \\lambda)$ with $\\lambda \\geq 0$ (a yellow box "
    "in their papers, a green box in the LICS'18 paper of Hadzihasanovic, Ng and Wang). It is the same as a Z-box of arity 2 with label "
    "$\\lambda$, which is how it is drawn and checked here (the rule holds for every complex $\\lambda$; it is checked for some positive values). "
    "Scalars that the papers write as diagrams are given here as numbers.")
# λ is a non-negative real number; it is used as a Z-box label (not an angle), checked for these values
LAMV = {"domain": "real", "values": ["1/3", "2", "5/2"]}
BOTH_NOTE = TRI_NOTE + "\n\n" + LAM_NOTE.replace("**Conventions.** ", "")


def pos(d, v):
    return d.g.row(v), d.g.qubit(v)


def tri(d, x, y, tip, text="", tex="", colour="yellow"):
    """A triangle at (x, y) whose tip points at the vertex `tip`. Where a wire bends at a triangle, `tip` is a
    way point next to it, so that the wire enters at the tip (the triangle is equilateral, so its direction is
    only clear from the wire)."""
    tx, ty = pos(d, tip)
    rot = round(math.degrees(math.atan2(ty - y, tx - x))) % 360
    return d.sym(x, y, "triangle", text=text, tex=tex, rot=rot, colour=colour)


def lam(d, x, y, text="λ", tex="\\lambda"):
    return d.sym(x, y, "box", text=text, tex=tex)


def common(group, reason, **kw):
    m = dict(calculus="ZX", group=group, checked=False, unchecked_reason=reason)
    m.update(kw)
    return m


def ng(fig17=None, fig18=None, hnw=None, extra=()):
    """source / also_in for a rule of Ng-Wang (2017), Ng-Wang (2018) and/or the LICS'18 paper."""
    refs = []
    if fig17:
        refs.append({"bib": NG17, "location": fig17})
    if fig18:
        refs.append({"bib": NG18, "location": fig18})
    if hnw:
        refs.append({"bib": HNW, "location": hnw})
    refs += list(extra)
    out = {"source": refs[0]}
    if refs[1:]:
        out["also_in"] = refs[1:]
    return out


# ============================================================================================
# Triangle rules (Ng and Wang, Fig. 3 of 1706.09877 and Fig. 5 of 1801.07993; LICS'18 axioms 2)
# ============================================================================================

# (TR1)
L = D()
x = L.x(2, 0, 1)
i, o = L.b(0, 0), L.b(3, 0)
t = tri(L, 1, 0, x)
L.e(i, t, x, o)
R = D()
x = R.x(1, 0, 1)
i, o = R.b(0, 0), R.b(3, 0)
t = tri(R, 2, 0, x)
R.e(i, x, t, o)
rule(
    "triangle-x-pi-commutation", lhs=L, rhs=R,
    name="Triangle and X(π) commutation", aliases=["(TR1)", "2(e)"],
    fragment="clifford+t", order=1,
    summary="An X(π) can be moved through a triangle, which turns the triangle around.",
    description=(
        "An X(π) phase (a NOT gate) moves through a triangle by reversing the direction of the triangle: "
        "the transpose of the triangle followed by NOT equals NOT followed by the triangle. "
        "This is what allows treating the triangle as 'pseudo-undirected' (axiom 2(e) of the LICS'18 paper).\n\n" + TRI_NOTE),
    scalar="1",
    **common("triangle", TRI_REASON),
    **ng("Fig. 3, rule (TR1)", "Fig. 5, rule (TR1)", "Section 4, ZX axiom 2(e)"),
    related=[{"id": "pi-commutation", "relation": "see-also"}],
    tags=["triangle", "NOT", "transpose"],
)

# (TR2)
L = D()
x = L.x(0, 0)
t = tri(L, 1, 0, x)
L.e(x, t, L.b(2, 0))
R = D()
R.e(R.x(1, 0), R.b(2, 0))
rule(
    "triangle-x-state", lhs=L, rhs=R,
    name="Triangle fixes the X-state", aliases=["(TR2)", "2(f)"],
    fragment="clifford+t", order=2,
    summary="The phase-free X-state (|0⟩) is left unchanged by the triangle.",
    description=(
        "Plugging the phase-free X-state, i.e. $|0\\rangle$ up to a scalar, into the input of a triangle gives the same state back.\n\n" + TRI_NOTE),
    scalar="1",
    **common("triangle", TRI_REASON),
    **ng("Fig. 3, rule (TR2)", "Fig. 5, rule (TR2)", "Section 4, ZX axiom 2(f)"),
    related=[{"id": "triangle-x-pi-state", "relation": "see-also"}],
    tags=["triangle", "state"],
)

# (TR3)
L = D()
x = L.x(0, 0, 1)
t = tri(L, 1, 0, x)
L.e(x, t, L.b(2, 0))
R = D()
R.e(R.z(1, 0), R.b(2, 0))
rule(
    "triangle-x-pi-state", lhs=L, rhs=R,
    name="Triangle on the X(π)-state", aliases=["(TR3)", "2(g)"],
    fragment="clifford+t", order=3,
    summary="The triangle maps the X(π)-state (|1⟩) to the phase-free Z-state (|0⟩ + |1⟩).",
    description=(
        "Plugging the X(π)-state, i.e. $|1\\rangle$ up to a scalar, into the input of a triangle gives the phase-free "
        "Z-state $|0\\rangle + |1\\rangle$. The paper writes the scalar $\\sqrt 2$ as a connected pair of phase-free "
        "Z- and X-spiders on the right-hand side.\n\n" + TRI_NOTE),
    scalar="sqrt(2)",
    **common("triangle", TRI_REASON),
    **ng("Fig. 3, rule (TR3)", "Fig. 5, rule (TR3)", "Section 4, ZX axiom 2(g)"),
    tags=["triangle", "state"],
)

# (TR4) of the 2017 paper
L = D()
z = L.z(0, 0, 1)
o = L.b(2, 0)
t = tri(L, 1, 0, o)
L.e(z, t, o)
R = D()
R.e(R.x(1, 0), R.b(2, 0))
rule(
    "triangle-transpose-z-pi-state", lhs=L, rhs=R,
    name="Reversed triangle on the Z(π)-state", aliases=["(TR4)"],
    fragment="clifford+t", order=4,
    summary="The transposed triangle maps the Z(π)-state (|0⟩ − |1⟩) to the X-state (|0⟩).",
    description=(
        "Plugging the Z(π)-state $|0\\rangle - |1\\rangle$ into the base of a triangle (i.e. into the transpose of the "
        "triangle) gives $|0\\rangle$, which is the phase-free X-state up to a scalar. The paper writes the scalar as "
        "a connected pair of phase-free Z- and X-spiders on the left-hand side. In the 2018 paper of Ng and Wang this rule is replaced by "
        "[(TR4')](../triangle-z-pi-state/).\n\n" + TRI_NOTE),
    scalar="sqrt(2)/2", scalar_side="lhs",
    **common("triangle", TRI_REASON),
    **ng("Fig. 3, rule (TR4)"),
    related=[{"id": "triangle-z-pi-state", "relation": "variant-of"}],
    tags=["triangle", "state"],
)

# (TR4') of the 2018 paper
L = D()
z = L.z(0, 0, 1)
t = tri(L, 1, 0, z)
L.e(z, t, L.b(2, 0))
R = D()
R.e(R.x(1, 0, 1), R.b(2, 0))
rule(
    "triangle-z-pi-state", lhs=L, rhs=R,
    name="Triangle on the Z(π)-state", aliases=["(TR4')"],
    fragment="clifford+t", order=5,
    summary="The triangle maps the Z(π)-state (|0⟩ − |1⟩) to the X(π)-state (|1⟩), up to the scalar −1/√2.",
    description=(
        "Plugging the Z(π)-state $|0\\rangle - |1\\rangle$ into the input of a triangle gives $-|1\\rangle$. "
        "The paper writes the scalar as a diagram on the right-hand side: a Z(π)- and an X(π)-spider connected by three wires, "
        "which equals $-1/\\sqrt 2$.\n\n" + TRI_NOTE),
    scalar="-sqrt(2)/2",
    **common("triangle", TRI_REASON),
    **ng(fig18="Fig. 5, rule (TR4')"),
    tags=["triangle", "state"],
)

# (TR5) of the 2017 paper
L = D()
i, o = L.b(0, 0.5), L.b(4, 0.5)
z1, z2 = L.z(1, 0.5), L.z(3, 0.5)
w1, w2 = L.way(1.2, 1.3), L.way(2.8, 1.3)
t = tri(L, 2, 1.3, w1)
L.e(i, z1).he(z1, z2).e(z1, w1, t, w2, z2).e(z2, o)
R = D()
i = R.b(0, 0)
t = tri(R, 1, 0, i)
R.e(i, t, R.z(2, 0, 1), R.b(3, 0))
rule(
    "triangle-hadamard-loop", lhs=L, rhs=R,
    name="Triangle in parallel with a Hadamard", aliases=["(TR5)"],
    fragment="clifford+t", order=6,
    summary="A Hadamard and a triangle in parallel between two Z-spiders equal a triangle followed by Z(π).",
    description=(
        "Two phase-free Z-spiders connected by two wires, one with a Hadamard and one with a triangle, equal a triangle followed by a Z(π) phase. "
        "The paper writes the scalar as a connected pair of phase-free Z- and X-spiders ($\\sqrt 2$) on the left-hand side. "
        "In the 2018 paper of Ng and Wang this rule is replaced by [(TR5')](../triangle-loop-disconnect/).\n\n" + TRI_NOTE),
    scalar="sqrt(2)/2", scalar_side="lhs",
    **common("triangle", TRI_REASON),
    **ng("Fig. 3, rule (TR5)"),
    related=[{"id": "triangle-loop-disconnect", "relation": "see-also"}],
    tags=["triangle", "Hadamard"],
)

# (TR5') of the 2018 paper
L = D()
i, o = L.b(0, 0.5), L.b(4, 0.5)
z, x = L.z(1, 0.5), L.x(3, 0.5)
wa, wb, wc, wd = L.way(1.2, 0), L.way(2.8, 0), L.way(1.2, 1), L.way(2.8, 1)
t1 = tri(L, 2, 0, wa)
t2 = tri(L, 2, 1, wd)
L.e(i, z, wa, t1, wb, x, o).e(z, wc, t2, wd, x)
R = D()
R.e(R.b(0, 0), R.z(1, 0))
R.e(R.z(2, 0), R.b(3, 0))
rule(
    "triangle-loop-disconnect", lhs=L, rhs=R,
    name="Triangle loop disconnects", aliases=["(TR5')", "2(i)"],
    fragment="clifford+t", order=7,
    summary="A Z- and an X-spider connected through a triangle and a reversed triangle disconnect.",
    description=(
        "A phase-free Z-spider and a phase-free X-spider connected by two wires, one with a triangle pointing towards the Z-spider and one with a triangle pointing towards the X-spider, "
        "equal a disconnected Z-effect and Z-state, i.e. the projector-like map $(|0\\rangle+|1\\rangle)(\\langle 0|+\\langle 1|)$. "
        "The paper writes the scalar as a connected pair of phase-free Z- and X-spiders ($\\sqrt 2$) on the left-hand side.\n\n" + TRI_NOTE),
    scalar="sqrt(2)/2", scalar_side="lhs",
    **common("triangle", TRI_REASON),
    **ng(fig18="Fig. 5, rule (TR5')", hnw="Section 4, ZX axiom 2(i)"),
    tags=["triangle", "disconnect"],
)

# (TR6) = (BW') of Jeandel, Perdrix and Vilmart
L = D()
i, o = L.b(0, 0), L.b(4, 0)
z = L.z(2, 0, 1)
t1 = tri(L, 1, 0, i)
t2 = tri(L, 3, 0, o)
L.e(i, t1, z, t2, o)
R = D()
i, o = R.b(0, 0), R.b(4, 0)
x = R.x(1.33, 0, 1)
t = tri(R, 2.67, 0, x)
R.e(i, x, t, o)
rule(
    "triangle-z-pi-sandwich", lhs=L, rhs=R,
    name="Z(π) between triangles", aliases=["(TR6)", "(BW')", "2(d)"],
    fragment="clifford+t", order=8,
    summary="A triangle, a Z(π) and a reversed triangle in sequence equal an X(π) followed by a triangle.",
    description=(
        "A triangle, a Z(π) phase and a triangle pointing the other way, in sequence, equal a NOT followed by a triangle. "
        "Jeandel, Perdrix and Vilmart use it as rule (BW') in their axiomatisation with parametrised triangles, where it replaces the "
        "[(BW) rule](../bw-rule/); in that paper the triangle is drawn in red.\n\n" + TRI_NOTE),
    scalar="1",
    **common("triangle", TRI_REASON),
    **ng("Fig. 3, rule (TR6)", "Fig. 5, rule (TR6)", "Section 4, ZX axiom 2(d)",
         extra=[{"bib": JPV, "location": "Fig. 6, rule (BW')"}]),
    related=[{"id": "bw-rule", "relation": "see-also"}, {"id": "triangle-x-pi-commutation", "relation": "see-also"}],
    tags=["triangle", "NOT"],
)

# (TR7)
L = D()
i, o = L.b(0, 0.5), L.b(4, 0.5)
z, x = L.z(1, 0.5), L.x(3, 0.5)
w1, w2 = L.way(1.2, 1.3), L.way(2.8, 1.3)
t = tri(L, 2, 1.3, w1)
L.e(i, z, x, o).e(z, w1, t, w2, x)
R = D()
i = R.b(0, 0)
t = tri(R, 1, 0, i)
R.e(i, t, R.b(2, 0))
rule(
    "triangle-hopf", lhs=L, rhs=R,
    name="Triangle Hopf rule", aliases=["(TR7)", "2(j)"],
    fragment="clifford+t", order=9,
    summary="A Z- and an X-spider connected by a plain wire and a wire with a triangle equal a single triangle.",
    description=(
        "A phase-free Z-spider and a phase-free X-spider connected by two wires, one of which carries a triangle pointing towards the Z-spider, "
        "equal a single triangle. Compare with the [Hopf rule](../hopf/), where two plain wires disconnect the spiders. "
        "The paper writes the scalar as a connected pair of phase-free Z- and X-spiders ($\\sqrt 2$) on the left-hand side.\n\n" + TRI_NOTE),
    scalar="sqrt(2)/2", scalar_side="lhs",
    **common("triangle", TRI_REASON),
    **ng("Fig. 3, rule (TR7)", "Fig. 5, rule (TR7)", "Section 4, ZX axiom 2(j)"),
    related=[{"id": "hopf", "relation": "see-also"}, {"id": "triangle-parallel", "relation": "see-also"}],
    tags=["triangle", "Hopf"],
)

# (TR8)
L = D()
i, o1, o2 = L.b(0, 1), L.b(5, 0), L.b(5, 1)
z0, z1, x = L.z(1, 1), L.z(3, 1), L.x(2, 0)
t1 = tri(L, 2, 1, z0)
t2 = tri(L, 4, 1, z1)
L.e(i, z0, t1, z1, t2, o2).e(z0, x, z1).e(x, o1)
R = D()
i, o1, o2 = R.b(0, 1), R.b(5, 0), R.b(5, 1)
z0, z1, x = R.z(2, 1), R.z(4, 1), R.x(3, 0)
t1 = tri(R, 1, 1, i)
t2 = tri(R, 3, 1, z0)
R.e(i, t1, z0, t2, z1, o2).e(z0, x, z1).e(x, o1)
rule(
    "triangle-rule-tr8", lhs=L, rhs=R,
    name="Triangle through a copy-and-compare", aliases=["(TR8)", "2(k)"],
    fragment="clifford+t", order=10,
    summary="A two-output identity that moves a triangle from after to before a structure of two Z-spiders and an X-spider.",
    description=(
        "On the left, the input is copied by a Z-spider, passes through a triangle and is copied again, passes another triangle, "
        "and the X-spider outputs the parity of the two copies. On the right the first triangle acts on the input instead and the second one sits between the two Z-spiders.\n\n" + TRI_NOTE),
    scalar="1",
    **common("triangle", TRI_REASON),
    **ng("Fig. 3, rule (TR8)", "Fig. 5, rule (TR8)", "Section 4, ZX axiom 2(k)"),
    related=[{"id": "triangle-rule-tr9", "relation": "see-also"}],
    tags=["triangle"],
)

# (TR9)
L = D()
i, o1, o2 = L.b(0, 1), L.b(5, 0), L.b(5, 1)
z0, z1, x = L.z(1, 1), L.z(3, 1), L.x(2, 0)
t1 = tri(L, 2, 1, z0)
t2 = tri(L, 4, 1, o2)
L.e(i, z0, t1, z1, t2, o2).e(z0, x, z1).e(x, o1)
R = D()
i, o1, o2 = R.b(0, 1), R.b(5, 0), R.b(5, 1)
x = R.x(1.5, 0)
zp = R.z(1.5, 1, 1)
z6 = R.z(3.5, 1)
zq = R.z(2.5, 0, 1)
ta = tri(R, 1.5, 0.5, x)
tb = tri(R, 3.5, 0, o1)
R.e(i, zp).he(zp, z6).e(z6, o2).e(zp, ta, x).e(x, zq, tb, o1).e(x, z6)
rule(
    "triangle-rule-tr9", lhs=L, rhs=R,
    name="Triangle rule (TR9)", aliases=["(TR9)", "2(l)"],
    fragment="clifford+t", order=11,
    summary="A two-output identity between a structure with two triangles and one with two triangles, a Hadamard and Z(π) phases.",
    description=(
        "The left-hand side is as in [(TR8)](../triangle-rule-tr8/), except that the last triangle points towards the output. "
        "The right-hand side contains a Hadamard, two Z(π) phases and two triangles. "
        "The paper writes the scalar as a connected pair of phase-free Z- and X-spiders ($\\sqrt 2$) on the right-hand side.\n\n" + TRI_NOTE),
    scalar="sqrt(2)",
    **common("triangle", TRI_REASON),
    **ng("Fig. 3, rule (TR9)", "Fig. 5, rule (TR9)", "Section 4, ZX axiom 2(l)"),
    tags=["triangle", "Hadamard"],
)

# (TR10) of the 2017 paper
L = D()
i, o = L.b(0, 0.5), L.b(4, 0.5)
z1, z2 = L.z(1, 0.5), L.z(3, 0.5)
wa, wb, wc, wd = L.way(1.2, 0), L.way(2.8, 0), L.way(1.2, 1), L.way(2.8, 1)
t1 = tri(L, 2, 0, wa)
t2 = tri(L, 2, 1, wc)
L.e(i, z1, wa, t1, wb, z2, o).e(z1, wc, t2, wd, z2)
R = D()
i = R.b(0, 0)
t = tri(R, 1, 0, i)
R.e(i, t, R.b(2, 0))
rule(
    "triangle-parallel", lhs=L, rhs=R,
    name="Parallel triangles", aliases=["(TR10)"],
    fragment="clifford+t", order=12,
    summary="Two parallel triangles between two phase-free Z-spiders equal one triangle.",
    description=(
        "Two phase-free Z-spiders connected by two wires, each carrying a triangle pointing towards the first spider, equal a single triangle. "
        "In the 2018 paper of Ng and Wang this rule is replaced by [(TR10')](../triangle-z-pi-triangle/).\n\n" + TRI_NOTE),
    scalar="1",
    **common("triangle", TRI_REASON),
    **ng("Fig. 3, rule (TR10)"),
    related=[{"id": "triangle-hopf", "relation": "see-also"}],
    tags=["triangle", "parallel"],
)

# (TR10') of the 2018 paper
L = D()
i, o = L.b(0, 0), L.b(4, 0)
z = L.z(2, 0, 1)
t1 = tri(L, 1, 0, i)
t2 = tri(L, 3, 0, z)
L.e(i, t1, z, t2, o)
R = D()
R.e(R.b(0, 0), R.z(1, 0, 1), R.b(2, 0))
rule(
    "triangle-z-pi-triangle", lhs=L, rhs=R,
    name="Triangle, Z(π), triangle", aliases=["(TR10')", "2(h)"],
    fragment="clifford+t", order=13,
    summary="Two triangles pointing the same way around a Z(π) phase cancel.",
    description=(
        "A triangle, a Z(π) phase and a second triangle pointing in the same direction equal the Z(π) phase alone: "
        "conjugating the triangle with Z(π) gives its inverse.\n\n" + TRI_NOTE),
    scalar="1",
    **common("triangle", TRI_REASON),
    **ng(fig18="Fig. 5, rule (TR10')", hnw="Section 4, ZX axiom 2(h)"),
    related=[{"id": "triangle-z-pi-sandwich", "relation": "see-also"}],
    tags=["triangle", "inverse"],
)

# (TR11) of the 2017 paper
L = D()
i1, i2, o = L.b(0, 0), L.b(0, 1), L.b(4, 0.5)
z, x, zo = L.z(1, 0), L.x(1, 1, 1), L.z(3, 0.5)
t1 = tri(L, 2, 0, z)
t2 = tri(L, 2, 1, x)
L.e(i1, z, t1, L.way(2.8, 0), zo, o).e(i2, x, t2, L.way(2.8, 1), zo).e(z, x)
R = D()
i1, i2, o = R.b(0, 0), R.b(0, 1), R.b(3, 0.5)
zo = R.z(2, 0.5)
t1 = tri(R, 1, 0, i1)
t2 = tri(R, 1, 1, i2)
R.e(i1, t1, R.way(1.8, 0), zo, o).e(i2, t2, R.way(1.8, 1), zo)
rule(
    "triangle-rule-tr11", lhs=L, rhs=R,
    name="Triangle rule (TR11)", aliases=["(TR11)"],
    fragment="clifford+t", order=14,
    summary="A Z-spider and an X(π)-spider joined by a wire, followed by triangles into a Z-spider, simplify to just the triangles.",
    description=(
        "Two inputs pass through a phase-free Z-spider and an X(π)-spider that are connected by a wire, and then through triangles into a Z-spider. "
        "This equals the two inputs passing through the triangles into the Z-spider directly. "
        "The paper writes the scalar as a connected pair of phase-free Z- and X-spiders ($\\sqrt 2$) on the left-hand side.\n\n" + TRI_NOTE),
    scalar="sqrt(2)/2", scalar_side="lhs",
    **common("triangle", TRI_REASON),
    **ng("Fig. 3, rule (TR11)"),
    related=[{"id": "triangle-rule-tr12", "relation": "see-also"}],
    tags=["triangle"],
)

# (TR12)
L = D()
i, o1, o2 = L.b(0, 0.5), L.b(4, 0), L.b(4, 1)
z, za, xb = L.z(1, 0.5), L.z(3, 0), L.x(3, 1)
wa, wc = L.way(1.2, 0), L.way(1.2, 1)
t1 = tri(L, 2, 0, wa)
t2 = tri(L, 2, 1, wc)
L.e(i, z, wa, t1, za, o1).e(z, wc, t2, xb, o2).e(za, xb)
R = D()
i, o1, o2 = R.b(0, 0.5), R.b(3, 0), R.b(3, 1)
z = R.z(1, 0.5)
wa, wc = R.way(1.2, 0), R.way(1.2, 1)
t1 = tri(R, 2, 0, wa)
t2 = tri(R, 2, 1, wc)
R.e(i, z, wa, t1, o1).e(z, wc, t2, o2)
rule(
    "triangle-rule-tr12", lhs=L, rhs=R,
    name="CNOT absorbed by triangles", aliases=["(TR12)", "2(m)"],
    fragment="clifford+t", order=15,
    summary="A CNOT after two triangles on the copies of a Z-spider can be removed.",
    description=(
        "A phase-free Z-spider copies its input into two branches with triangles (pointing towards the spider), "
        "followed by a CNOT (a Z-spider and an X-spider joined by a wire). The CNOT can be removed. "
        "The paper writes the scalar as a connected pair of phase-free Z- and X-spiders ($\\sqrt 2$) on the left-hand side.\n\n" + TRI_NOTE),
    scalar="sqrt(2)/2", scalar_side="lhs",
    **common("triangle", TRI_REASON),
    **ng("Fig. 3, rule (TR12)", "Fig. 5, rule (TR12)", "Section 4, ZX axiom 2(m)"),
    tags=["triangle", "CNOT"],
)


def copy_structure(d, x0, y_top, y_main):
    """The structure of (TR13)/(TR14) with the Z-spider at column x0: returns (z_in, x, z_out)."""
    z0, z1, x = d.z(x0, y_main), d.z(x0 + 2, y_main), d.x(x0 + 1, y_top)
    t = tri(d, x0 + 1, y_main, z0)
    d.e(z0, t, z1).e(z0, x, z1)
    return z0, x, z1


# (TR13)
L = D()
i, o1, o2 = L.b(0, 1), L.b(5, 0), L.b(5, 1)
z0, x, z1 = copy_structure(L, 1, 0, 1)
L.e(i, z0).e(x, L.z(4, 0, "alpha"), o1).e(z1, L.z(4, 1, "alpha"), o2)
R = D()
i, o1, o2 = R.b(0, 1), R.b(5, 0), R.b(5, 1)
z0, x, z1 = copy_structure(R, 2, 0, 1)
R.e(i, R.z(1, 1, "alpha"), z0).e(x, o1).e(z1, o2)
rule(
    "triangle-phase-copy", lhs=L, rhs=R,
    name="Phases copy through the triangle structure", aliases=["(TR13)"],
    fragment="universal", order=16,
    variables={"alpha": "real"},
    summary="Z(α) phases on both outputs of a structure of Z-spiders, an X-spider and a triangle equal one Z(α) on its input.",
    description=(
        "The structure on the right (the input is copied, passes a triangle and is copied again, and an X-spider computes the parity of the two copies) "
        "maps $|0\\rangle \\mapsto |00\\rangle$ and $|1\\rangle \\mapsto |11\\rangle$ (up to normalisation), so a phase on its input can be copied to both outputs. "
        "[(TR14)](../triangle-lambda-copy/) is the same rule for λ-boxes.\n\n" + TRI_NOTE),
    scalar="1",
    **common("triangle", TRI_REASON),
    **ng("Fig. 3, rule (TR13)", "Fig. 5, rule (TR13)"),
    related=[{"id": "triangle-lambda-copy", "relation": "see-also"}, {"id": "triangle-lambda-phase-copy", "relation": "special-case-of"}],
    tags=["triangle", "copy", "phase"],
)

# (TR14)
L = D()
i, o1, o2 = L.b(0, 1), L.b(5, 0), L.b(5, 1)
z0, x, z1 = copy_structure(L, 1, 0, 1)
L.e(i, z0).e(x, lam(L, 4, 0), o1).e(z1, lam(L, 4, 1), o2)
R = D()
i, o1, o2 = R.b(0, 1), R.b(5, 0), R.b(5, 1)
z0, x, z1 = copy_structure(R, 2, 0, 1)
R.e(i, lam(R, 1, 1), z0).e(x, o1).e(z1, o2)
rule(
    "triangle-lambda-copy", lhs=L, rhs=R,
    name="λ-boxes copy through the triangle structure", aliases=["(TR14)"],
    fragment="universal", order=17,
    variables={"lambda": "real"},
    summary="λ-boxes on both outputs of a structure of Z-spiders, an X-spider and a triangle equal one λ-box on its input.",
    description=(
        "The same as [(TR13)](../triangle-phase-copy/), but for the λ-box $\\mathrm{diag}(1, \\lambda)$ instead of a phase.\n\n" + BOTH_NOTE),
    scalar="1",
    **common("triangle", TRI_LAM_REASON),
    **ng("Fig. 3, rule (TR14)", "Fig. 6, rule (TR14)"),
    related=[{"id": "triangle-lambda-phase-copy", "relation": "special-case-of"}],
    tags=["triangle", "copy", "lambda"],
)

# LICS'18 axiom 2(n): (TR13) and (TR14) combined
L = D()
i, o1, o2 = L.b(0, 1), L.b(6, 0), L.b(6, 1)
z0, x, z1 = copy_structure(L, 1, 0, 1)
L.e(i, z0).e(x, lam(L, 4, 0), L.z(5, 0, "alpha"), o1).e(z1, lam(L, 4, 1), L.z(5, 1, "alpha"), o2)
R = D()
i, o1, o2 = R.b(0, 1), R.b(6, 0), R.b(6, 1)
z0, x, z1 = copy_structure(R, 3, 0, 1)
R.e(i, lam(R, 1, 1), R.z(2, 1, "alpha"), z0).e(x, o1).e(z1, o2)
rule(
    "triangle-lambda-phase-copy", lhs=L, rhs=R,
    name="λ-boxes and phases copy through the triangle structure", aliases=["2(n)"],
    fragment="universal", order=18,
    variables={"lambda": "real", "alpha": "real"},
    summary="A λ-box and a Z(α) on both outputs of the triangle copy structure equal one λ-box and Z(α) on its input.",
    description=(
        "The combination of [(TR13)](../triangle-phase-copy/) and [(TR14)](../triangle-lambda-copy/) used in the LICS'18 axiomatisation: "
        "the green box $\\mathrm{diag}(1, \\lambda)$ together with the phase $\\alpha$ represents the diagonal map $\\mathrm{diag}(1, \\lambda e^{i\\alpha})$, "
        "and it copies through the structure as a whole.\n\n" + BOTH_NOTE),
    scalar="1",
    **common("triangle", TRI_LAM_REASON),
    source={"bib": HNW, "location": "Section 4, ZX axiom 2(n)"},
    tags=["triangle", "copy", "lambda", "phase"],
)

# ============================================================================================
# Parametrised triangles (Jeandel, Perdrix and Vilmart, LMCS 2020, Fig. 6)
# ============================================================================================

# (TD)
L = D()
i = L.b(0, 1)
t = tri(L, 1.5, 1, i, text="e^(iθ)·tan α", tex="e^{i\\theta}\\tan(\\alpha)", colour="red")
L.e(i, t, L.b(3, 1))
R = D()
i, o = R.b(0, 1), R.b(6, 1)
zt, x8, za, xh, zm = R.z(1, 1, "theta"), R.x(2, 1), R.z(3, 1, "alpha"), R.x(4, 1, "1/2"), R.z(5, 1, "-theta")
x9 = R.x(1, 2)
R.e(i, zt, x8, za, xh, zm, o).e(zt, x9).e(x9, R.z(0.4, 2.8, "alpha")).e(x9, R.z(1.6, 2.8, "alpha"))
R.e(x8, R.z(2, 0, "1/2-alpha"))
rule(
    "param-triangle-decomposition", lhs=L, rhs=R,
    name="Parametrised triangle decomposition", aliases=["(TD)", "triangle decomposition"],
    fragment="universal", group="triangle", order=20,
    variables={"alpha": "real", "theta": "real"},
    conditions="α ≠ π/2 mod π",
    summary="The parametrised triangle with parameter exp(iθ)·tan(α) equals a ZX-diagram in α and θ.",
    description=(
        "Jeandel, Perdrix and Vilmart give the triangle a parameter $r \\in \\mathbb C$: the parametrised triangle is the matrix "
        "$\\begin{pmatrix}1&r\\\\0&1\\end{pmatrix}$ (read from its tip to its base). This rule expresses it as an ordinary ZX-diagram when "
        "$r = e^{i\\theta}\\tan(\\alpha)$, which covers every $r$. "
        "The paper writes the scalars as diagrams on both sides: a legless Z($2\\alpha$)-spider on the left and a Z($-\\pi/4$)–X($\\pi$) pair on the right.\n\n"
        "The triangle with parameter 1 is the usual triangle, so with $\\alpha = \\pi/4$ and $\\theta = 0$ this gives a decomposition of the triangle into Clifford+T generators. "
        "In the paper the parametrised triangle is drawn in red, with its parameter next to it."),
    scalar="sqrt(2)*exp(-I*pi/4)/(1 + exp(2*I*alpha))",
    checked=False, unchecked_reason=PTRI_REASON, calculus="ZX",
    source={"bib": JPV, "location": "Fig. 6, rule (TD)"},
    related=[{"id": "param-triangle-addition", "relation": "see-also"}],
    tags=["triangle", "parametrised triangle", "decomposition"],
)

# (TA)
L = D()
i = L.b(0, 0)
t1 = tri(L, 1, 0, i, text="r", tex="r", colour="red")
t2 = tri(L, 2, 0, t1, text="s", tex="s", colour="red")
L.e(i, t1, t2, L.b(3, 0))
R = D()
i = R.b(0, 0)
t = tri(R, 1, 0, i, text="r+s", tex="r+s", colour="red")
R.e(i, t, R.b(2, 0))
rule(
    "param-triangle-addition", lhs=L, rhs=R,
    name="Parametrised triangle addition", aliases=["(TA)", "triangle addition"],
    fragment="universal", group="triangle", order=21,
    variables={"r": "complex", "s": "complex"},
    summary="Two parametrised triangles in sequence, with parameters r and s, equal one with parameter r + s.",
    description=(
        "The parametrised triangle of Jeandel, Perdrix and Vilmart is the matrix $\\begin{pmatrix}1&r\\\\0&1\\end{pmatrix}$ (read from its tip to its base), "
        "and these matrices multiply by adding their parameters. Together with the [decomposition (TD)](../param-triangle-decomposition/) this gives the ring structure of $\\mathbb C$, "
        "which replaces the λ-boxes and the addition rule of Ng and Wang. In the paper the triangles are drawn in red."),
    scalar="1",
    checked=False, unchecked_reason=PTRI_REASON, calculus="ZX",
    source={"bib": JPV, "location": "Fig. 6, rule (TA)"},
    related=[{"id": "lambda-addition", "relation": "see-also"}],
    tags=["triangle", "parametrised triangle", "addition"],
)

# ============================================================================================
# λ-box rules (Ng and Wang, Fig. 2 of 1706.09877 and Fig. 6 of 1801.07993; LICS'18 axioms 2)
# ============================================================================================

# (IV) of the 2017 paper
L = D()
L.e(L.x(0, 0), L.z(1, 0))
L.e(L.z(0, 1), L.zbox(1, 1, "lambda"), L.z(2, 1, 1))
R = D()
rule(
    "lambda-inverse-scalar", lhs=L, rhs=R,
    name="λ-box inverse rule", aliases=["(IV)"],
    fragment="universal", order=1,
    variables={"lambda": {"domain": "real", "values": [1 - 1 / math.sqrt(2)]}},
    conditions="$\\lambda = 1 - 1/\\sqrt 2$",
    summary="The scalar √2 times a λ-box scalar with λ = 1 − 1/√2 is the empty diagram.",
    description=(
        "A connected pair of phase-free Z- and X-spiders is the scalar $\\sqrt 2$, and a λ-box between a phase-free Z-effect and a Z(π)-state is the scalar $1 - \\lambda$. "
        "With $\\lambda = 1 - 1/\\sqrt 2$ the two scalars are inverse to each other, so that $\\sqrt 2$ has a diagrammatic inverse "
        "(compare the [inverse rule](../inverse-rule/) of the stabiliser fragment).\n\n" + LAMZ_NOTE),
    scalar="1",
    calculus="ZX", group="lambda-box",
    **ng("Fig. 2, rule (IV)"),
    related=[{"id": "inverse-rule", "relation": "see-also"}, {"id": "clifford-t-inverse-scalar", "relation": "see-also"}],
    tags=["lambda", "scalar", "inverse"],
)

# (L1)
L = D()
i1, i2, o = L.b(0, 0), L.b(0, 1), L.b(3, 0.5)
z = L.z(2, 0.5)
L.e(i1, L.zbox(1, 0, "lambda"), z).e(i2, z).e(z, o)
R = D()
i1, i2, o = R.b(0, 0), R.b(0, 1), R.b(3, 0.5)
z = R.z(1, 0.5)
R.e(i1, z).e(i2, z).e(z, R.zbox(2, 0.5, "lambda"), o)
rule(
    "lambda-box-spider-slide", lhs=L, rhs=R,
    name="λ-box moves through a spider", aliases=["(L1)", "2(a)"],
    fragment="universal", order=2,
    variables={"lambda": LAMV},
    summary="A λ-box can be moved from one leg of a phase-free Z-spider to another.",
    description=(
        "A λ-box on one leg of a phase-free Z-spider with three legs can be moved to any of its other legs: being diagonal, "
        "it 'commutes' with the Z-spider just like a phase. The paper states the three versions (on either input or on the output) as a chain of equations.\n\n" + LAMZ_NOTE),
    scalar="1",
    calculus="ZX", group="lambda-box",
    **ng("Fig. 2, rule (L1)", "Fig. 6, rule (L1)", "Section 4, ZX axiom 2(a)"),
    related=[{"id": "zw-weighted-fusion", "relation": "see-also"}, {"id": "lambda-box-phase-commutation", "relation": "see-also"}],
    tags=["lambda", "spider"],
)

# (L2)
L = D()
L.e(L.b(0, 0), L.zbox(1, 0, "lambda"), L.x(2, 0))
R = D()
R.e(R.b(0, 0), R.x(1, 0))
rule(
    "lambda-box-x-effect", lhs=L, rhs=R,
    name="λ-box and the X-effect", aliases=["(L2)"],
    fragment="universal", order=3,
    variables={"lambda": LAMV},
    summary="A λ-box followed by the phase-free X-effect is the X-effect.",
    description=(
        "The phase-free X-effect is $\\langle 0|$ up to a scalar, and $\\mathrm{diag}(1, \\lambda)$ does not change the $|0\\rangle$ component.\n\n" + LAMZ_NOTE),
    scalar="1",
    calculus="ZX", group="lambda-box",
    **ng("Fig. 2, rule (L2)", "Fig. 6, rule (L2)"),
    related=[{"id": "lambda-box-identity", "relation": "see-also"}],
    tags=["lambda", "effect"],
)

# (L3)
L = D()
L.e(L.b(0, 0), L.zbox(1, 0, 1), L.b(2, 0))
R = D()
R.e(R.b(0, 0), R.b(2, 0))
rule(
    "lambda-box-identity", lhs=L, rhs=R,
    name="λ-box with label 1", aliases=["(L3)", "2(b)"],
    fragment="phase-free", order=4,
    summary="The λ-box with λ = 1 is the identity.",
    description="The λ-box $\\mathrm{diag}(1, 1)$ is the identity wire.\n\n" + LAMZ_NOTE,
    scalar="1",
    calculus="ZX", group="lambda-box",
    **ng("Fig. 2, rule (L3)", "Fig. 6, rule (L3)", "Section 4, ZX axiom 2(b)"),
    related=[{"id": "identity-removal", "relation": "see-also"}, {"id": "lambda-box-multiplication", "relation": "see-also"}],
    tags=["lambda", "identity"],
)

# (L4)
L = D()
L.e(L.b(0, 0), L.zbox(1, 0, "lambda1"), L.zbox(2, 0, "lambda2"), L.b(3, 0))
R = D()
R.e(R.b(0, 0), R.zbox(1.25, 0, "lambda1⋅lambda2"), R.b(2.5, 0))
rule(
    "lambda-box-multiplication", lhs=L, rhs=R,
    name="λ-boxes multiply", aliases=["(L4)", "2(c)"],
    fragment="universal", order=5,
    variables={"lambda1": LAMV, "lambda2": LAMV},
    summary="Two λ-boxes in sequence fuse into one whose label is the product.",
    description=(
        "λ-boxes compose by multiplying their labels, just as phases of spiders add: "
        "$\\mathrm{diag}(1, \\lambda_2)\\,\\mathrm{diag}(1, \\lambda_1) = \\mathrm{diag}(1, \\lambda_1\\lambda_2)$.\n\n" + LAMZ_NOTE),
    scalar="1",
    calculus="ZX", group="lambda-box",
    **ng("Fig. 2, rule (L4)", "Fig. 6, rule (L4)", "Section 4, ZX axiom 2(c)"),
    related=[{"id": "spider-fusion", "relation": "see-also"}, {"id": "zw-weighted-fusion", "relation": "see-also"}],
    tags=["lambda", "multiplication", "fusion"],
)

# (L5)
L = D()
L.e(L.b(0, 0), L.zbox(1, 0, "lambda"), L.z(2, 0, "alpha"), L.b(3, 0))
R = D()
R.e(R.b(0, 0), R.z(1, 0, "alpha"), R.zbox(2, 0, "lambda"), R.b(3, 0))
rule(
    "lambda-box-phase-commutation", lhs=L, rhs=R,
    name="λ-box commutes with Z-phases", aliases=["(L5)"],
    fragment="universal", order=6,
    variables={"lambda": LAMV, "alpha": "real"},
    summary="A λ-box and a Z(α) phase commute.",
    description=(
        "Both the λ-box and the Z-phase are diagonal, so they commute. Together they represent $\\mathrm{diag}(1, \\lambda e^{i\\alpha})$: "
        "every complex number is represented by a λ-box and a phase.\n\n" + LAMZ_NOTE),
    scalar="1",
    calculus="ZX", group="lambda-box",
    **ng("Fig. 2, rule (L5)", "Fig. 6, rule (L5)"),
    related=[{"id": "lambda-box-spider-slide", "relation": "see-also"}],
    tags=["lambda", "phase", "commutation"],
)

# (AD) of the 2017 paper
L = D()
i, o = L.b(0, 0), L.b(4, 0)
z0 = L.z(2, 0)
x3 = L.x(2, 1.3)
z4, z5 = L.z(0.8, 2.3), L.z(3.2, 2.3)
wa, wb = L.way(0.8, 0.4), L.way(3.2, 0.4)
t6 = tri(L, 0.8, 1.2, wa)
t7 = tri(L, 3.2, 1.2, wb)
L.e(i, z0, o).e(z0, x3).e(z0, wa, t6, z4).e(z0, wb, t7, z5).e(x3, z4).e(x3, z5)
L.e(z4, lam(L, 0.8, 3.2, "λ₁", "\\lambda_1"), L.z(0.8, 4.1, "beta"))
L.e(z5, lam(L, 3.2, 3.2, "λ₂", "\\lambda_2"), L.z(3.2, 4.1, "alpha"))
R = D()
R.e(R.b(0, 0), R.z(1, 0, "gamma"), lam(R, 2, 0), R.b(3, 0))
rule(
    "lambda-addition", lhs=L, rhs=R,
    name="Addition rule", aliases=["(AD)", "sum rule"],
    fragment="universal", order=7,
    variables={"alpha": "real", "beta": "real", "gamma": "real", "lambda": "real", "lambda1": "real", "lambda2": "real"},
    conditions="$λe^{iγ} = λ₁e^{iβ} + λ₂e^{iα}$, with λ, λ₁, λ₂ ≥ 0.",
    summary="Two branches carrying λ₁·exp(iβ) and λ₂·exp(iα), joined by a structure with triangles, equal one branch carrying their sum.",
    description=(
        "The addition rule of Ng and Wang: the states $|0\\rangle + \\lambda_1 e^{i\\beta}|1\\rangle$ and $|0\\rangle + \\lambda_2 e^{i\\alpha}|1\\rangle$ "
        "(a λ-box and a phase on a Z-state) are combined by a structure of Z-spiders, an X-spider and two triangles that adds their $|1\\rangle$ components. "
        "The result is the diagonal map $\\mathrm{diag}(1, \\lambda e^{i\\gamma})$ with $\\lambda e^{i\\gamma} = \\lambda_1 e^{i\\beta} + \\lambda_2 e^{i\\alpha}$. "
        "Together with the λ-boxes this lets the ZX-calculus express the ring structure of $\\mathbb C$, which is used to translate the "
        "[ZW-calculus](../w-sum/) into the ZX-calculus. "
        "The paper writes the scalar as a connected pair of phase-free Z- and X-spiders ($\\sqrt 2$) on the left-hand side. "
        "The 2018 paper of Ng and Wang uses a [smaller version](../lambda-addition-simplified/) with only one triangle.\n\n" + BOTH_NOTE),
    scalar="sqrt(2)/2", scalar_side="lhs",
    **common("lambda-box", TRI_LAM_REASON),
    **ng("Fig. 2, rule (AD)"),
    related=[{"id": "lambda-addition-simplified", "relation": "see-also"}, {"id": "w-sum", "relation": "see-also"},
             {"id": "addition-rule", "relation": "see-also"}, {"id": "param-triangle-addition", "relation": "see-also"}],
    tags=["lambda", "addition", "sum", "triangle"],
)

# (AD) of the 2018 paper = LICS'18 axiom 2(o)
L = D()
i, o = L.b(0, 0), L.b(4.5, 0)
z8 = L.z(1.5, 0)
x2, z5 = L.x(1.5, 1.3), L.z(3, 1.3)
t9 = tri(L, 2.25, 0.65, z8)
L.e(i, z8, o).e(z8, x2, z5).e(z8, t9, z5)
L.e(z5, lam(L, 3, 2.2, "λ₁", "\\lambda_1"), L.z(3, 3.1, "alpha"))
L.e(x2, lam(L, 1.5, 2.2, "λ₂", "\\lambda_2"), L.z(1.5, 3.1, "beta"))
R = D()
R.e(R.b(0, 0), R.z(1, 0, "gamma"), lam(R, 2, 0), R.b(3, 0))
rule(
    "lambda-addition-simplified", lhs=L, rhs=R,
    name="Addition rule with one triangle", aliases=["(AD)", "2(o)", "sum rule"],
    fragment="universal", order=8,
    variables={"alpha": "real", "beta": "real", "gamma": "real", "lambda": "real", "lambda1": "real", "lambda2": "real"},
    conditions="$λe^{iγ} = λ₁e^{iα} + λ₂e^{iβ}$, with λ, λ₁, λ₂ ≥ 0.",
    summary="A smaller addition rule: two branches carrying λ₁·exp(iα) and λ₂·exp(iβ), joined by a structure with one triangle, equal one branch carrying their sum.",
    description=(
        "The version of the [addition rule](../lambda-addition/) used in the Clifford+T paper of Ng and Wang and in the LICS'18 paper of Hadzihasanovic, Ng and Wang, "
        "with only one triangle. The states $|0\\rangle + \\lambda_1 e^{i\\alpha}|1\\rangle$ and $|0\\rangle + \\lambda_2 e^{i\\beta}|1\\rangle$ are combined into "
        "the diagonal map $\\mathrm{diag}(1, \\lambda e^{i\\gamma})$ with $\\lambda e^{i\\gamma} = \\lambda_1 e^{i\\alpha} + \\lambda_2 e^{i\\beta}$. "
        "In the Clifford+T paper the labels are restricted to $\\lambda_i \\in \\mathbb Z[\\frac12]$ and angles to multiples of $\\pi/4$. "
        "The papers write the scalar as a connected pair of phase-free Z- and X-spiders ($\\sqrt 2$) on the left-hand side.\n\n" + BOTH_NOTE),
    scalar="sqrt(2)/2", scalar_side="lhs",
    **common("lambda-box", TRI_LAM_REASON),
    **ng(fig18="Fig. 6, rule (AD)", hnw="Section 4, ZX axiom 2(o)"),
    related=[{"id": "lambda-addition", "relation": "variant-of"}, {"id": "w-sum", "relation": "see-also"}],
    tags=["lambda", "addition", "sum", "triangle"],
)

# ============================================================================================
# Hadamard on a cap (H3)
# ============================================================================================
# the Hadamard is drawn as a standard H-box (a Hadamard edge into a way point is not drawn)
L = D()
L.e(L.b(2, 0), L.h(1.1, 0), L.way(-0.2, 0.5), L.b(2, 1))
R = D()
R.e(R.b(2, 0), R.way(-0.2, 0.5), R.h(1.1, 1), R.b(2, 1))
rule(
    "hadamard-cup-slide", lhs=L, rhs=R,
    name="Hadamard slides along a cup", aliases=["(H3)", "Hadamard on a cap"],
    calculus="ZX", fragment="clifford", group="hadamard", order=20,
    checked=False,
    unchecked_reason="a bare cup (a wire whose two ends are both outputs) cannot be represented with ZXLive-style boundaries",
    summary="A Hadamard on one leg of a cup (or cap) can be moved to the other leg.",
    description=(
        "The Hadamard gate is symmetric (equal to its own transpose), so it can slide along a cup or cap from one leg to the other. "
        "In axiomatisations in which [cups are spiders](../cup-as-spider/) this follows from the [colour change rule](../colour-change/), "
        "but Ng and Wang state it as an axiom. It is equivalent to [the Hadamard being self-transpose](../hadamard-transpose/), "
        "the form used in the LICS'18 paper of Hadzihasanovic, Ng and Wang.\n\n"
        "In PyZX and ZXLive inputs and outputs are determined by their position, so a bare cup cannot be drawn directly."),
    scalar="1",
    source={"bib": NG17, "location": "Fig. 1, rule (H3)"},
    also_in=[{"bib": NG18, "location": "Fig. 4, rule (H3)"}],
    related=[{"id": "hadamard-transpose", "relation": "equivalent-to"}, {"id": "cup-as-spider", "relation": "see-also"}],
    tags=["Hadamard", "cup", "cap", "transpose"],
)

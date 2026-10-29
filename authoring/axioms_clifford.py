"""Axioms of complete axiomatisations (stabilizer ZX, ZH, ZW) that were missing from the other authoring
scripts. Found while compiling the completeness pages (data/axiomatisations-clifford.json).

ZW conventions as in zw.py: PyZX's W-spider is a symmetric black vertex of the undirected ZW-calculus with a
binary black vertex (NOT) on its input leg, and a W-spider without outputs is the state |0> (the unit).
"""

from dsl import D, rule

ZW15 = "hadzihasanovic2015diagrammatic"
THESIS = "hadzihasanovic2017algebra"
LICS = "HarnyAmarCompleteness"
CARETTE = "carette2023compositionality"
BPW = "BackensSimplified"
BPW_MIN = "backens2017minimal"
STOLTZ = "k.stoltz2026simplified"

W_EXPLAINER = (
    "The W-spider (black triangle) with one input and $n$ outputs maps $|0\\rangle \\mapsto |0\\cdots 0\\rangle$ "
    "and $|1\\rangle \\mapsto |10\\cdots0\\rangle + |010\\cdots0\\rangle + \\cdots + |0\\cdots01\\rangle$: it "
    "spreads a single excitation over its outputs in all possible ways. The small dot marks its input leg.")

UNIT_EXPLAINER = (
    "A W-spider with no outputs is the state $|0\\rangle$ (read as an effect, it is $\\langle 0|$), which is the "
    "unit of the W-spider read as a 'merge'.")


# ---------------------------------------------------------------------------------------------
# (S3'R): the cups of the two colours coincide

L = D()
z = L.z(1, 0.5)
L.e(z, L.b(2, 0)).e(z, L.b(2, 1))
R = D()
x = R.x(1, 0.5)
R.e(x, R.b(2, 0)).e(x, R.b(2, 1))
rule(
    "cup-colour-coincidence", lhs=L, rhs=R,
    name="Green and red cups coincide",
    aliases=["(S3'R)", "(S3′R)", "(S3′)", "compact structures coincide", "Z-cup equals X-cup"],
    calculus="ZX", fragment="phase-free", group="spiders", order=10,
    summary="A phase-free Z-spider with two outputs equals a phase-free X-spider with two outputs: both are the cup.",
    description=(
        "Each colour of spider induces a compact structure: a phase-free spider with two outputs is a 'cup' "
        "(the Bell state $|00\\rangle+|11\\rangle$), and one with two inputs is a 'cap'. This rule says that the "
        "compact structures of the Z- and the X-spiders are the same: indeed $|00\\rangle + |11\\rangle = "
        "|{+}{+}\\rangle + |{-}{-}\\rangle$.\n\n"
        "In the simplified stabilizer ZX-calculus of Backens, Perdrix and Wang this is the second half of the "
        "axiom (S3′), called (S3′R) in their follow-up paper; the first half, (S3′L), says that the green cup is "
        "the cup of the ambient category, i.e. [identity removal](../identity-removal/) with the wire bent. "
        "Backens, Perdrix and Wang could not decide whether (S3′R) is necessary; Stoltz later showed that it "
        "cannot be derived from the other rules.\n\n"
        "In the usual presentation, where 'only connectivity matters', this rule follows from identity removal "
        "for both colours."),
    scalar="auto",
    source={"bib": BPW, "location": "Figure 2 (simplified rules), rule (S3′)"},
    also_in=[{"bib": BPW_MIN, "location": "Figure 1, rule (S3′); called (S3′R) in Section 3"},
             {"bib": STOLTZ, "location": "Table 1 (ZX_simp), rule (S3′R); Theorem 3.1 (necessity)"}],
    axiom_of=[BPW, BPW_MIN, STOLTZ],
    related=[{"id": "identity-removal", "relation": "see-also"},
             {"id": "colour-change", "relation": "see-also"}],
    tags=["cup", "compact structure", "identity", "stabilizer", "completeness", "minimal"],
)


# ---------------------------------------------------------------------------------------------
# W unit and counit: <0|0> = 1

L = D()
u1o, u1i = L.w(0.6, 0, input_dir=(0.35, 0))
u2o, u2i = L.w(2.0, 0, input_dir=(-0.35, 0))
L.e(u1i, u2i)
R = D()
rule(
    "w-unit-counit", lhs=L, rhs=R,
    name="W unit meets counit",
    aliases=["5c", "counit of unit", "⟨0|0⟩ = 1", "W unit scalar"],
    calculus="ZW", fragment="clifford+t", group="zw-rules", order=4,
    summary="Plugging the W unit |0⟩ into the W counit ⟨0| gives the empty diagram.",
    description=(
        W_EXPLAINER + " " + UNIT_EXPLAINER + "\n\n"
        "Connecting two W-spiders without outputs along their input legs is therefore the scalar "
        "$\\langle 0|0\\rangle = 1$, the empty diagram. This is one of the Hopf-algebra axioms of the W-spider "
        "(the counit of the unit is 1), axiom 5c of Hadzihasanovic's original complete ZW-calculus, where the "
        "unit is drawn as a binary black vertex on a black vertex with a loop."),
    scalar="auto",
    source={"bib": ZW15, "location": "Section 3 (The rules), Rule 5c"},
    axiom_of=[ZW15],
    related=[{"id": "w-zero-copy", "relation": "see-also"},
             {"id": "w-fusion", "relation": "see-also"}],
    notes="The right-hand side is the empty diagram.",
    tags=["W", "unit", "counit", "scalar", "Hopf algebra", "empty diagram"],
)


# ---------------------------------------------------------------------------------------------
# Z copies the W unit |0>

L = D()
uo, ui = L.w(0.6, 0.5, input_dir=(0.35, 0))
z = L.z(2.0, 0.5)
L.e(ui, z)
L.e(z, L.b(3.2, 0)).e(z, L.b(3.2, 1))
R = D()
for y in (0, 1):
    uo, ui = R.w(1.6, y, input_dir=(0.35, 0))
    R.e(ui, R.b(3.2, y))
rule(
    "zw-zero-copy", lhs=L, rhs=R,
    name="Z-spider copies the W unit",
    aliases=["6b", "|0⟩ copy through Z", "Z copies W unit"],
    calculus="ZW", fragment="clifford+t", group="zw-bialgebra", order=5,
    summary="The state |0⟩ (a W-spider without outputs) is copied by a phase-free Z-spider.",
    description=(
        UNIT_EXPLAINER + "\n\n"
        "A phase-free Z-spider sends $|0\\rangle$ to $|0\\cdots0\\rangle$, so plugging the unit of the W-spider "
        "into it gives a copy of the unit on every output. Together with the [W/Z bialgebra](../w-z-bialgebra/) "
        "and the [Z/W Hopf rule](../zw-hopf/) this is one of the axioms saying that the W-spider and the Z-spider "
        "form a (Hopf-like) bialgebra: axiom 6b of Hadzihasanovic's original complete ZW-calculus. It is the "
        "ZW-version of the [state copy](../state-copy/) rule of the ZX-calculus, with the $|0\\rangle$ state drawn "
        "as a W-spider instead of an X-spider."),
    parameter_notes="Shown for a Z-spider with two outputs; holds for any number of outputs.",
    scalar="auto",
    source={"bib": ZW15, "location": "Section 3 (The rules), Rule 6b"},
    axiom_of=[ZW15],
    related=[{"id": "state-copy", "relation": "variant-of"},
             {"id": "w-zero-copy", "relation": "see-also"},
             {"id": "w-z-bialgebra", "relation": "see-also"}],
    tags=["W", "Z-spider", "copy", "unit", "zero state", "bialgebra"],
)


# ---------------------------------------------------------------------------------------------
# W self-loop removal (tr_w)

L = D()
wo, wi = L.w(1.5, 0.5)
L.e(L.b(0, 0.5), wi)
L.e(wo, wo)
L.e(wo, L.b(3, 0)).e(wo, L.b(3, 1))
R = D()
wo, wi = R.w(1.5, 0.5)
R.e(R.b(0, 0.5), wi)
R.e(wo, R.b(3, 0)).e(wo, R.b(3, 1))
rule(
    "w-self-loop", lhs=L, rhs=R,
    name="W self-loop removal",
    aliases=["tr_w", "tr_W", "W trace", "W loop removal", "2(d)"],
    calculus="ZW", fragment="clifford+t", group="zw-rules", order=5,
    summary="A plain self-loop on the outputs of a W-spider can be removed.",
    description=(
        W_EXPLAINER + "\n\n"
        "Connecting two outputs of a W-spider to each other (a trace) keeps only the terms where both are "
        "$|0\\rangle$, since at most one output carries the excitation. So the loop can simply be removed. In "
        "the undirected ZW-calculus this is the rule $tr_W$: a black vertex with a self-loop is a black vertex "
        "with two fewer legs. Together with [W fusion](../w-fusion/) it makes up the spider presentation of the "
        "black vertices."),
    parameter_notes="Shown for a W-spider with two remaining outputs; holds for any number of outputs.",
    scalar="auto",
    source={"bib": ZW15, "location": "Section 3 (The rules), spider rule $\\mathrm{tr}_W$"},
    also_in=[{"bib": THESIS, "location": "Chapter 5, Section 5.2 (list of rules of the ZW calculus), rule $tr_w$"},
             {"bib": LICS, "location": "Section 3, ZW axiom 2(d)"},
             {"bib": CARETTE, "location": "Figure 1 (axioms of the planar W-calculus), W-loop axiom"}],
    axiom_of=[THESIS, LICS, CARETTE],
    related=[{"id": "w-fusion", "relation": "see-also"},
             {"id": "self-loop-removal", "relation": "variant-of"}],
    tags=["W", "self-loop", "trace", "spider"],
)

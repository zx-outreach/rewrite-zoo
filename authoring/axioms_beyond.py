"""Axioms of complete axiomatisations beyond Clifford (Ng-Wang, ...) that were missing from the other authoring
scripts. Found while compiling the completeness pages (data/axiomatisations-beyond.json).

Conventions as in beyond_clifford.py: unnormalised spiders and a normalised Hadamard, exactly as in PyZX, so the
scalars of the papers carry over unchanged. The papers draw diagrams from top (inputs) to bottom (outputs); here
they are rotated so that inputs are on the left.
"""

from dsl import D, rule

NG_CT = "ng_completeness_2018"

# ---------------------------------------------------------------------------------------------
# (IV'): the scalar rule of Ng and Wang's Clifford+T axiomatisation

L = D()
a, b = L.z(0, 0), L.x(1, 0)
L.e(a, b).e(a, b).e(a, b)
L.e(L.z(0, 1.5, "1/4"), L.x(1, 1.5, 1), L.z(2, 1.5, "-1/4"))
R = D()
rule(
    "clifford-t-inverse-scalar", lhs=L, rhs=R,
    name="Clifford+T inverse rule (IV′)",
    aliases=["(IV')", "(IV′)", "Ng–Wang scalar rule", "π/4 inverse rule"],
    calculus="ZX", fragment="clifford+t", group="scalars", order=22,
    summary="A Z- and X-spider joined by three wires (the scalar 1/√2), next to a π/4 Z-state, a π X-spider and a −π/4 Z-effect in a row (the scalar √2), is the empty diagram.",
    description=(
        "A phase-free Z-spider and X-spider connected by three wires represent the scalar $\\frac1{\\sqrt2}$. The "
        "chain of a Z-spider with phase $\\frac\\pi4$, an X-spider with phase $\\pi$ and a Z-spider with phase "
        "$-\\frac\\pi4$ is $\\langle 0| + e^{-i\\pi/4}\\langle 1|$ applied to $X(|0\\rangle + e^{i\\pi/4}|1\\rangle)$, "
        "which is $e^{i\\pi/4}+e^{-i\\pi/4} = \\sqrt2$. So the two components together are the empty diagram.\n\n"
        "Ng and Wang use this rule in their complete axiomatisation of the Clifford+T ZX-calculus (with the "
        "triangle and $\\lambda$-box as extra generators), in place of the inverse rule (IV) of their universal "
        "axiomatisation, which uses a $\\lambda$-box with label $1-\\frac1{\\sqrt2}$ and therefore lies outside "
        "the Clifford+T fragment. It plays the same role as the [inverse rule](../inverse-rule/) and the "
        "[Clifford+T scalar rule (E)](../clifford-t-scalar/): it lets one invert the scalar $\\sqrt2$."),
    scalar="auto",
    source={"bib": NG_CT, "location": "Fig. 6, rule (IV′)"},
    axiom_of=[NG_CT],
    related=[{"id": "inverse-rule", "relation": "see-also"},
             {"id": "clifford-t-scalar", "relation": "see-also"},
             {"id": "inverse-scalar-phase", "relation": "see-also"}],
    notes="The right-hand side is the empty diagram.",
    tags=["scalar", "inverse", "clifford+t", "completeness", "sqrt 2", "empty diagram"],
)

"""The phase-free version of state copy, as it appears in most completeness papers (a variant of
the general rule state-copy, which has a Boolean basis state aπ and a phase α)."""

from dsl import D, rule
from families import outs, param, unit

L = D()
x, z, b = L.x(0, 0), L.z(1, 0), L.b(2, 0)
L.e(x, z, b)
R = D()
x2, b2 = R.x(1, 0), R.b(2, 0)
R.e(x2, b2)
rule(
    "state-copy-phase-free", lhs=L, rhs=R,
    name="Phase-free state copy",
    aliases=["(B1)", "(CP)", "(C1)", "copy rule", "copying", "(sc)"],
    calculus="ZX", fragment="phase-free", group="copy", order=1,
    summary="A phase-free X-state (|0⟩) copies through a phase-free Z-spider.",
    description=(
        "A phase-free X-spider with a single leg is, up to a scalar, the computational basis state $|0\\rangle$. "
        "When it is plugged into a phase-free Z-spider, the Z-spider copies it to all of its other legs.\n\n"
        "This is the form in which state copying appears as an axiom in most completeness results; it is the case "
        "$a = 0$, $\\alpha = 0$ of the general [state copy](../state-copy/) rule, which copies both basis states "
        "through a Z-spider with any phase. Many papers write the scalar $\\sqrt2^{-(n-1)}$ as a diagram."),
    parameters={"n": 2},
    parameter_notes="n is the number of output legs of the Z-spider (shown for n = 2).",
    scalar="sqrt(2)**(-(n-1))",
    source={"bib": "CD2"},
    also_in=[{"bib": "KissingervdWeteringbook", "location": "Chapter 8, Table 8.1 (basic rewrite rules)"}],
    related=[{"id": "state-copy", "relation": "special-case-of"}],
    tags=["copy", "basis state", "phase-free"],
    arity={"params": {"n": param("outputs")},
           "lhs": [outs("n", b)],
           "rhs": [unit("n", [x2, b2], dots_shift=[0.5, 0])]},
)

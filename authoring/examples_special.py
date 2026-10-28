"""Examples of the two special kinds of rules: rules that are only drawn (not checked), and circuit rules.
These also serve as templates for authoring more of them (see unchecked.py and gates.py)."""

from dsl import D, rule

# A bare cup cannot be drawn with ZXLive-style boundaries, so this rule is only drawn.
L = D()
L.e(L.b(1.2, 0), L.way(-0.2, 0.5), L.b(1.2, 1))
R = D()
z = R.z(0.5, 0.5)
R.e(z, R.b(1.2, 0)).e(z, R.b(1.2, 1))
rule(
    "cup-as-spider", lhs=L, rhs=R,
    name="Cups are spiders",
    aliases=["(S3)", "compact structure", "cup rule", "wire bending"],
    calculus="ZX", fragment="phase-free", group="spiders", order=5,
    checked=False,
    unchecked_reason="a bare cup (a wire whose two ends are both outputs) cannot be represented with ZXLive-style boundaries",
    summary="A bare cup is a phase-free Z-spider with two outputs.",
    description=(
        "The cup (and, upside down, the cap) is the same as a phase-free spider with two legs on the same side. "
        "Together with [spider fusion](../spider-fusion/) this means that only the connectivity of a ZX-diagram "
        "matters: wires can be bent around freely (*only connectivity matters*).\n\n"
        "In PyZX and ZXLive inputs and outputs are determined by their position, so a bare cup cannot be drawn "
        "directly; this axiom is built into the way diagrams are represented there."),
    scalar="1",
    source={"bib": "CD1"},
    also_in=[{"bib": "SimonCompleteness", "location": "Fig. 1, rule (S3)"}],
    related=[{"id": "spider-fusion", "relation": "see-also"}, {"id": "identity-removal", "relation": "see-also"}],
    tags=["cup", "cap", "compact structure", "only connectivity matters"],
)

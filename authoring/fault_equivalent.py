"""Fault-equivalent rewrites: ZX rewrites that also preserve the behaviour of a diagram under noise.

Sources:
  * Rodatz, Poór, Kissinger, "Floquetifying stabiliser codes with distance-preserving rewrites"
    (arXiv:2410.17240), Sec. 3: the distance-preserving rewrites (r_elim), (r_fuse), (r_4), (r_5),
    (r_2n), (r_2n+).
  * Rodatz, Poór, Kissinger, "Fault Tolerance by Construction" (arXiv:2506.17181), Sec. 6.2: the
    fault-equivalent rewrites (Elim_fe), (Fuse-1_fe), (Fuse-4_fe), (Fuse-n_fe), (Fuse-n_{w-fe}).
  * Rüsch, Rodatz, Kissinger, "Completeness for Fault Equivalence of Clifford ZX Diagrams"
    (arXiv:2510.08477), Fig. 3 and Fig. 4: the rules acting on fault gadgets.

The diagrams are the ZX-diagrams of the papers; the noise annotations of the papers (edge weights,
fault-free edges) cannot be drawn and are described in the text. Every rule is a sound ZX equation,
and this is what the build checks; the fault equivalence itself is not checked.

Families (rules with n legs) are written here with one copy of every unit; run families_fault.py
afterwards to turn them into arity templates.
"""

from dsl import D, rule
import families_fault as FF

FLOQ = "rodatz2024floquetifying"
FTBC = "rodatz2025fault"
COMPL = "rusch2025completeness"
G = "fault-equivalent"

EDGE_FLIP = ("Fault equivalence is with respect to *edge-flip noise*: every edge of the diagram can suffer a Pauli "
             "$X$, $Y$ or $Z$ flip of weight 1.")
WEIGHTS = ("As in the paper, noisy edges are labelled with their weight (the cost of a flip on that edge; a vector "
           "of weights for the $X$-, $Y$- and $Z$-flips, unlabelled noisy edges have weight 1), and *fault-free* "
           "(idealised) edges are drawn bold purple. These annotations are shown on the rule as stated; derived "
           "variants (transpose, colour swap, other legs counts) may drop them.")
GADGET = ("A *fault gadget* is a red spider connected by fault-free edges to its targets (here Z-spiders, whose "
          "phase-free Z-flips it describes) and by a noisy *spawning edge*, annotated with the weight of the fault, "
          "to a one-legged green spider. A flip on the spawning edge spreads to the targets, so the gadget models one "
          "atomic fault; without a flip it does nothing.")


def fam(fn):
    L, R = fn()[:2]
    return L, R


# =============================================================================================
# Distance-preserving / fault-equivalent spider rewrites

L = D()
L.e(L.b(0, 0), L.b(2, 0))
R = D()
R.e(R.b(0, 0), R.z(1, 0), R.b(2, 0))
rule(
    "fe-identity-removal", lhs=L, rhs=R,
    name="Fault-equivalent identity removal",
    aliases=["(r_elim)", "(Elim_fe)", "elim rewrite", "distance-preserving identity removal"],
    calculus="ZX", fragment="phase-free", group=G, order=1,
    summary="Adding or removing a phase-free two-legged spider on a wire is fault-equivalent.",
    description=(
        "The ordinary [identity removal](../identity-removal/) rule is fault-equivalent: a wire may be split by a "
        "phase-free Z-spider, or the spider removed again, without changing which faults are possible. "
        + EDGE_FLIP + " A flip on the bare wire corresponds to the same flip on either of the two edges, and "
        "flips $P_1$, $P_2$ on the two edges correspond to the flip $P_1P_2$ on the wire, which has at most the same "
        "weight.\n\n"
        "The rule was introduced as the distance-preserving rewrite $(r_{\\text{elim}})$; distance-preserving "
        "rewrites were later shown to be exactly the fault-equivalent rewrites. In the complete axiomatisation of "
        "fault equivalence of Rüsch, Rodatz and Kissinger, $(\\textsc{Elim}_{\\text{fe}})$ is the weighted version: "
        "the noisy wire with weight $\\vec w$ equals the spider with a noisy edge of weight $\\vec w$ on one side and "
        "a fault-free edge on the other."),
    scalar="auto",
    source={"bib": FLOQ, "location": "Sec. 3.2, rewrite $(r_{\\text{elim}})$"},
    also_in=[{"bib": FTBC, "location": "Sec. 6.2, rule $(\\textsc{Elim}_{\\text{fe}})$"},
             {"bib": COMPL, "location": "Fig. 3, rule $(\\textsc{Elim}_{\\text{fe}})$ (weighted version)"},
             {"bib": "boriskhesin2026spidercat:", "location": "Sec. 2, figure of fault-equivalent rewrites"},
             {"bib": "poor2026spidercss:", "location": "Sec. 2.3, figure of elementary fault-equivalent rewrites"},
             {"bib": "poor2026spidercss:", "location": "Sec. 3.1.2, semi-idealised identity (one leg fault-free)"},
             {"bib": "Schweikart2025Masters", "location": "Sec. 2.4.2, eq. (2.62); Example 3.18"}],
    related=[{"id": "identity-removal", "relation": "variant-of"}],
    tags=["fault-equivalent", "distance-preserving", "edge-flip noise", "fault tolerance", "identity"],
)

L, R = fam(FF.fe_one_legged_fusion)
rule(
    "fe-one-legged-fusion", lhs=L, rhs=R,
    name="Fault-equivalent fusion of a one-legged spider",
    aliases=["(r_fuse)", "(Fuse-1_fe)", "fuse rewrite", "distance-preserving fusion"],
    calculus="ZX", fragment="phase-free", group=G, order=2,
    summary="A phase-free one-legged Z-spider attached to a Z-spider can be fused into it, fault-equivalently.",
    description=(
        "Attaching a phase-free one-legged Z-spider to a phase-free Z-spider (or fusing it away) is fault-equivalent. "
        "This is a special case of [spider fusion](../spider-fusion/), which in general is *not* fault-equivalent: "
        "unfusing a spider creates internal edges, and a flip on an internal edge can be equivalent to a flip on "
        "several of the outer legs, so it would increase the weight of a fault.\n\n"
        + EDGE_FLIP + " Here the only internal edge is the one to the new spider: an $X$-flip on it is absorbed by the "
        "one-legged spider ($\\pi$-copy), and a $Z$-flip can be pushed to any single outer leg, so every fault on "
        "the right-hand side has a fault of at most the same weight on the left-hand side."),
    conditions="The spider has at least one other leg ('any green spider with more than one edge' in the "
               "Floquetifying paper, 'spiders with at least one output leg' in Fault Tolerance by Construction).",
    scalar="auto",
    source={"bib": FLOQ, "location": "Sec. 3.2, rewrite $(r_{\\text{fuse}})$"},
    also_in=[{"bib": FTBC, "location": "Sec. 6.2, rule $(\\textsc{Fuse-1}_{\\text{fe}})$"},
             {"bib": "boriskhesin2026spidercat:", "location": "Sec. 2, figure of fault-equivalent rewrites"},
             {"bib": "poor2026spidercss:", "location": "Sec. 2.3, figure of elementary fault-equivalent rewrites"},
             {"bib": "Schweikart2025Masters", "location": "Sec. 2.4.2, eq. (2.62); Example 3.19"}],
    related=[{"id": "spider-fusion", "relation": "variant-of"},
             {"id": "fe-identity-removal", "relation": "see-also"}],
    tags=["fault-equivalent", "distance-preserving", "edge-flip noise", "fault tolerance", "fusion", "unfusion"],
)

L = D()
z = L.z(1, 0.5)
L.e(L.b(0, 0), z).e(L.b(0, 1), z).e(z, L.b(2, 0)).e(z, L.b(2, 1))
R = D()
s1, s2, s3, s4 = R.z(1, 0), R.z(1, 1), R.z(2, 0), R.z(2, 1)
R.e(s1, s3, s4, s2, s1)
R.e(R.b(0, 0), s1).e(R.b(0, 1), s2).e(s3, R.b(3, 0)).e(s4, R.b(3, 1))
rule(
    "fe-four-legged-spider", lhs=L, rhs=R,
    name="Fault-equivalent four-legged spider",
    aliases=["(r_4)", "(Fuse-4_fe)", "four-legged spider rewrite", "square decomposition"],
    calculus="ZX", fragment="phase-free", group=G, order=3,
    summary="A phase-free four-legged Z-spider is fault-equivalent to a 4-cycle of three-legged Z-spiders.",
    description=(
        "A four-legged Z-spider can be replaced by a square of four three-legged Z-spiders, one for each leg. "
        "This decomposes a weight-four measurement into spiders of degree three while preserving fault equivalence, "
        "in contrast to the naive decomposition into a chain or star of spiders, in which a single flip can spread to "
        "two legs.\n\n"
        + EDGE_FLIP + " The four spiders of the square form a detecting region, so an odd number of $X$-flips on the "
        "internal edges is detected, while an even number of $X$-flips and all $Z$-flips can be pushed to the outer "
        "legs without increasing their weight. The rule follows by [spider fusion](../spider-fusion/) and "
        "[self-loop removal](../self-loop-removal/), but fusion in general is not fault-equivalent."),
    scalar="auto",
    source={"bib": FLOQ, "location": "Sec. 3.2, rewrite $(r_4)$"},
    also_in=[{"bib": FTBC, "location": "Sec. 6.2, rule $(\\textsc{Fuse-4}_{\\text{fe}})$"},
             {"bib": COMPL, "location": "Sec. 4, running example (four-legged spider)"},
             {"bib": "boriskhesin2026spidercat:", "location": "Sec. 2, figure of fault-equivalent rewrites"},
             {"bib": "poor2026spidercss:", "location": "Sec. 2.3, figure of elementary fault-equivalent rewrites"},
             {"bib": "Schweikart2025Masters", "location": "Sec. 2.4.2, eq. (2.62); Lemma 3.21"}],
    related=[{"id": "spider-fusion", "relation": "variant-of"},
             {"id": "fe-five-legged-spider", "relation": "see-also"}],
    tags=["fault-equivalent", "distance-preserving", "edge-flip noise", "fault tolerance", "detecting region",
          "unfusion", "syndrome extraction"],
)

L = D()
z = L.z(1, 1)
L.e(L.b(0, 0.5), z).e(L.b(0, 1.5), z)
for y in (0, 1, 2):
    L.e(z, L.b(2, y))
R = D()
p_lt, p_lb = R.z(1, 0.4), R.z(1, 1.6)
p_rt, p_rm, p_rb = R.z(2, 0), R.z(2.6, 1), R.z(2, 2)
R.e(p_lt, p_rt, p_rm, p_rb, p_lb, p_lt)
R.e(R.b(0, 0.4), p_lt).e(R.b(0, 1.6), p_lb)
R.e(p_rt, R.b(3.6, 0)).e(p_rm, R.b(3.6, 1)).e(p_rb, R.b(3.6, 2))
rule(
    "fe-five-legged-spider", lhs=L, rhs=R,
    name="Distance-preserving five-legged spider",
    aliases=["(r_5)", "five-legged spider rewrite", "pentagon decomposition"],
    calculus="ZX", fragment="phase-free", group=G, order=4,
    summary="A phase-free five-legged Z-spider is fault-equivalent to a 5-cycle of three-legged Z-spiders.",
    description=(
        "A five-legged Z-spider can be replaced by a pentagon of five three-legged Z-spiders, one for each leg, "
        "without changing the distance of any code or circuit containing it (a distance-preserving, equivalently "
        "fault-equivalent, rewrite).\n\n"
        + EDGE_FLIP + " The pentagon is a detecting region for $X$-flips, so only even numbers of internal $X$-flips "
        "are undetectable, and these, as well as all $Z$-flips, can be pushed to the outer legs without increasing "
        "their weight. Together with [the four-legged version](../fe-four-legged-spider/) and the general "
        "decompositions of [even](../fe-even-spider-decomposition/) and [odd](../fe-odd-spider-decomposition/) "
        "spiders, this reduces any spider to spiders of degree at most three."),
    scalar="auto",
    source={"bib": FLOQ, "location": "Sec. 3.2, rewrite $(r_5)$"},
    also_in=[{"bib": "Schweikart2025Masters", "location": "Sec. 2.4.2, eq. (2.62); Lemma 3.22"}],
    related=[{"id": "spider-fusion", "relation": "variant-of"},
             {"id": "fe-four-legged-spider", "relation": "see-also"}],
    tags=["fault-equivalent", "distance-preserving", "edge-flip noise", "fault tolerance", "detecting region",
          "unfusion"],
)

L, R = fam(FF.fe_even)
rule(
    "fe-even-spider-decomposition", lhs=L, rhs=R,
    name="Distance-preserving decomposition of an even spider",
    aliases=["(r_2n)", "recursive spider rewrite", "even-legged spider decomposition"],
    calculus="ZX", fragment="phase-free", group=G, order=5,
    summary="A 2n-legged Z-spider is fault-equivalent to two n-legged spiders joined through n four-legged spiders.",
    description=(
        "A phase-free Z-spider with $2n$ legs can be decomposed into two $n$-legged spiders and $n$ four-legged "
        "spiders: each four-legged spider carries two of the original legs and is connected to both of the "
        "$n$-legged spiders. The rewrite is distance-preserving (equivalently, fault-equivalent under edge-flip "
        "noise). Applied recursively, together with the four- and five-legged rules, it decomposes arbitrarily large "
        "spiders, and hence arbitrary-weight Pauli measurements, into spiders of degree at most three.\n\n"
        "It is proven by unfusing a spider with [one-legged fusion](../fe-one-legged-fusion/), applying the "
        "[odd version](../fe-odd-spider-decomposition/), and fusing back."),
    scalar="auto",
    source={"bib": FLOQ, "location": "Sec. 3.3, rewrite $(r_{2n})$"},
    also_in=[{"bib": "Schweikart2025Masters", "location": "Sec. 2.4.2, eq. (2.62)"}],
    related=[{"id": "spider-fusion", "relation": "variant-of"},
             {"id": "fe-odd-spider-decomposition", "relation": "derived-from"},
             {"id": "fe-fuse-n", "relation": "see-also"}],
    tags=["fault-equivalent", "distance-preserving", "edge-flip noise", "fault tolerance", "unfusion",
          "syndrome extraction", "Pauli measurement"],
)

L, R = fam(FF.fe_odd)
rule(
    "fe-odd-spider-decomposition", lhs=L, rhs=R,
    name="Distance-preserving decomposition of an odd spider",
    aliases=["(r_2n+)", "recursive spider rewrite (odd)", "odd-legged spider decomposition"],
    calculus="ZX", fragment="phase-free", group=G, order=6,
    summary="A (2n+1)-legged Z-spider is fault-equivalent to an n- and an (n+1)-legged spider joined through n "
            "four-legged spiders.",
    description=(
        "A phase-free Z-spider with $2n+1$ legs can be decomposed into an $n$-legged spider, an $(n+1)$-legged "
        "spider and $n$ four-legged spiders: each four-legged spider carries two of the original legs and is "
        "connected to both other spiders, and the remaining leg is on the $(n+1)$-legged spider. The rewrite is "
        "distance-preserving (equivalently, fault-equivalent under edge-flip noise). The proof considers the "
        "null space of the detector error matrix of the right-hand side over $\\mathbb F_2$ and shows that every "
        "undetectable combination of flips can be pushed to the boundary without increasing its weight."),
    scalar="auto",
    source={"bib": FLOQ, "location": "Sec. 3.3, rewrite $(r_{2n^+})$; proof in the appendix"},
    also_in=[{"bib": "Schweikart2025Masters", "location": "Sec. 2.4.2, eq. (2.62)"}],
    related=[{"id": "spider-fusion", "relation": "variant-of"}],
    tags=["fault-equivalent", "distance-preserving", "edge-flip noise", "fault tolerance", "unfusion",
          "syndrome extraction", "Pauli measurement"],
)

L, R = fam(FF.fe_fuse_n)
rule(
    "fe-fuse-n", lhs=L, rhs=R,
    name="Fault-equivalent 2n-legged spider ladder",
    aliases=["(Fuse-n_fe)", "recursive spider rewrite", "spider ladder"],
    calculus="ZX", fragment="phase-free", group=G, order=7,
    summary="A 2n-legged Z-spider is fault-equivalent to two n-legged spiders whose legs are connected pairwise.",
    description=(
        "A phase-free Z-spider with $2n$ legs is fault-equivalent to two $n$-legged spiders, each of whose legs "
        "passes through a three-legged spider, with the $i$-th three-legged spider of the one connected to the "
        "$i$-th three-legged spider of the other. The rungs form detecting regions, so that flips which would "
        "spread to many legs are detected. " + EDGE_FLIP + "\n\n"
        "This is the form of the even spider decomposition used in *Fault Tolerance by Construction*; it is the "
        "[distance-preserving decomposition of an even spider](../fe-even-spider-decomposition/) with each "
        "four-legged spider split into two connected three-legged ones. If only $w$-fault equivalence is required, "
        "fewer rungs suffice: see the [w-fault-equivalent version](../fe-fuse-n-w/)."),
    scalar="auto",
    source={"bib": FTBC, "location": "Sec. 6.2, rule $(\\textsc{Fuse-n}_{\\text{fe}})$; proof in the appendix"},
    also_in=[{"bib": "boriskhesin2026spidercat:", "location": "Sec. 2, figure of fault-equivalent rewrites"}],
    related=[{"id": "spider-fusion", "relation": "variant-of"},
             {"id": "fe-even-spider-decomposition", "relation": "see-also"}],
    tags=["fault-equivalent", "edge-flip noise", "fault tolerance", "unfusion", "cat state", "syndrome extraction"],
)

L, R = fam(FF.fe_fuse_n_w)
rule(
    "fe-fuse-n-w", lhs=L, rhs=R,
    name="w-fault-equivalent 2n-legged spider ladder",
    aliases=["(Fuse-n_w-fe)", "w-fault-equivalent spider ladder"],
    calculus="ZX", fragment="phase-free", group=G, order=8,
    summary="A 2n-legged Z-spider is w-fault-equivalent to two n-legged spiders of which only w legs are connected "
            "pairwise.",
    description=(
        "A cheaper version of the [fault-equivalent spider ladder](../fe-fuse-n/): only the first $w$ legs of the "
        "two $n$-legged spiders pass through connected pairs of three-legged spiders, and the other $n-w$ legs are "
        "plain. The rewrite is not fault-equivalent but **$w$-fault-equivalent**: every undetectable fault of weight "
        "less than $w$ on one side has a fault of at most the same weight with the same effect on the other side. "
        "This suffices for instance for circuits that only need to be fault-tolerant up to distance $w$. "
        + EDGE_FLIP),
    conditions="w-fault equivalence only; w ≥ 1 rungs.",
    scalar="auto",
    source={"bib": FTBC, "location": "Sec. 6.2, rule $(\\textsc{Fuse-n}_{w\\text{-fe}})$; proof in the appendix"},
    also_in=[{"bib": "boriskhesin2026spidercat:", "location": "Sec. 2, figure of fault-equivalent rewrites"}],
    related=[{"id": "fe-fuse-n", "relation": "variant-of"},
             {"id": "spider-fusion", "relation": "variant-of"}],
    tags=["w-fault-equivalent", "edge-flip noise", "fault tolerance", "unfusion", "cat state", "distance"],
)

# =============================================================================================
# Rules on fault gadgets: the complete axiomatisation of fault equivalence (Rüsch, Rodatz, Kissinger)

L = D()
a, b = L.x(0, 0), L.z(1.2, 0)
L.e(a, b).ann(a, b, weight="w")
R = D()
a, b = R.x(0, 0), R.z(1.2, 0)
R.e(a, b).ann(a, b, faultfree=True)
rule(
    "fe-scalar", lhs=L, rhs=R,
    name="Idealising a scalar fault gadget",
    aliases=["(Scalar_fe)", "scalar rule (fault equivalence)"],
    calculus="ZX", fragment="phase-free", group=G, order=20,
    summary="The noisy edge of a disconnected fault gadget can be made fault-free: a fault without observable "
            "effect can be ignored.",
    description=(
        "A fault gadget that has no targets is a scalar diagram: a red and a green one-legged spider connected by an "
        "edge. On the left-hand side this edge is noisy, with weight vector $\\vec w$ (weights of its $X$-, $Y$- and "
        "$Z$-flips); on the right-hand side it is fault-free. A flip on it only changes a global scalar, so it has no "
        "observable effect, and the two sides are fault-equivalent.\n\n"
        "Semantically the two sides are the same ZX-diagram; only the noise annotation changes. " + WEIGHTS),
    scalar="auto",
    source={"bib": COMPL, "location": "Fig. 3, rule $(\\textsc{Scalar}_{\\text{fe}})$"},
    related=[{"id": "fe-limit", "relation": "see-also"}],
    tags=["fault-equivalent", "fault gadget", "weighted noise", "completeness", "scalar"],
)

def gadget_head(G, y, phase=0, weight="w", faultfree=False, x0=0):
    """boundary -(fault-free)- red spider -(weight)- one-legged green spider."""
    bnd, xv, zv = G.b(x0, y), G.x(x0 + 1, y, phase), G.z(x0 + 2.2, y)
    G.e(bnd, xv, zv).ann(bnd, xv, faultfree=True)
    if faultfree:
        G.ann(xv, zv, faultfree=True)
    else:
        G.ann(xv, zv, weight=weight)
    return xv


L = D()
gadget_head(L, 0, "k/2")
R = D()
gadget_head(R, 0)
rule(
    "fe-x-phase", lhs=L, rhs=R,
    name="Phases on fault gadgets",
    aliases=["(XPhase_fe)"],
    calculus="ZX", fragment="clifford", group=G, order=21,
    variables={"k": "integer"},
    summary="A Clifford phase kπ/2 on the red spider of a fault gadget can be removed.",
    description=(
        "A red spider with phase $k\\frac{\\pi}{2}$ and a one-legged green spider attached by a noisy edge of weight "
        "$w$ (the head of a fault gadget) is fault-equivalent to the same with phase 0. Semantically the phase "
        "disappears because the green spider copies through the red spider. Under noise, both sides only allow the "
        "trivial fault or a single $Z$-flip on the noisy edge, which have the same effect up to a global phase. This "
        "allows ignoring global phases introduced when moving fault gadgets.\n\n"
        + GADGET + " " + WEIGHTS),
    scalar="auto",
    source={"bib": COMPL, "location": "Fig. 3, rule $(\\textsc{XPhase}_{\\text{fe}})$"},
    related=[{"id": "state-copy", "relation": "see-also"}, {"id": "fe-commute", "relation": "see-also"}],
    tags=["fault-equivalent", "fault gadget", "weighted noise", "completeness", "global phase"],
)

L = D()
xs = [gadget_head(L, 0, weight="w_1"), gadget_head(L, 2, weight="w_2")]
s = L.z(1.6, 1, "1/2")
L.e(xs[0], s, xs[1]).ann(xs[0], s, faultfree=True).ann(s, xs[1], faultfree=True)
R = D()
gadget_head(R, 0, weight="w_1")
gadget_head(R, 2, weight="w_2")
rule(
    "fe-commute", lhs=L, rhs=R,
    name="Commuting fault gadgets",
    aliases=["(Commute_fe)"],
    calculus="ZX", fragment="clifford", group=G, order=22,
    summary="A π/2 Z-spider connecting the red spiders of two fault gadgets can be removed.",
    description=(
        "Two fault-gadget heads (red spiders, each with a one-legged green spider attached by a noisy edge of weight "
        "$w_1$ and $w_2$) whose red spiders are connected through a green $\\frac{\\pi}{2}$-spider are fault-equivalent "
        "to the two heads without this connection. The connection appears when two anticommuting fault gadgets are "
        "moved past each other; the rule says that the resulting global phase can be ignored.\n\n"
        + GADGET + " " + WEIGHTS),
    scalar="auto",
    source={"bib": COMPL, "location": "Fig. 3, rule $(\\textsc{Commute}_{\\text{fe}})$"},
    related=[{"id": "fe-x-phase", "relation": "see-also"}],
    tags=["fault-equivalent", "fault gadget", "weighted noise", "completeness", "global phase", "commutation"],
)

L = D()
t, bnd, s1, s2 = L.z(1, 1), L.b(0, 1), L.z(2.2, 0.3), L.z(2.2, 1.7)
L.e(bnd, t).e(t, s1).e(t, s2).ann(bnd, t, faultfree=True).ann(t, s1, weight="w_1").ann(t, s2, weight="w_2")
R = D()
t, bnd, s1 = R.z(1, 1), R.b(0, 1), R.z(2.2, 1)
R.e(bnd, t, s1).ann(bnd, t, faultfree=True).ann(t, s1, weight="min(w_1,w_2)")
rule(
    "fe-merge", lhs=L, rhs=R,
    name="Merging equal fault gadgets",
    aliases=["(Merge_fe)"],
    calculus="ZX", fragment="phase-free", group=G, order=23,
    summary="Two fault gadgets for the same fault, of weights w₁ and w₂, merge into one of weight min(w₁, w₂).",
    description=(
        "Faults are described here by their $Z$-flips: a green spider (connected by a fault-free edge to the rest of "
        "the diagram) with a one-legged green spider attached by a noisy edge describes a $Z$-flip of the given "
        "weight. Two such gadgets on the same spider, of weights $w_1$ and $w_2$, describe the same fault twice; they "
        "are fault-equivalent to a single gadget of weight $\\min(w_1, w_2)$, since only the cheapest way to produce "
        "a fault matters, and producing it twice has no effect.\n\n" + WEIGHTS),
    scalar="auto",
    source={"bib": COMPL, "location": "Fig. 3, rule $(\\textsc{Merge}_{\\text{fe}})$"},
    related=[{"id": "fe-comb", "relation": "see-also"}, {"id": "spider-fusion", "relation": "see-also"}],
    tags=["fault-equivalent", "fault gadget", "weighted noise", "completeness", "atomic faults"],
)

def zflip(G, y, weight):
    bnd, t, s_ = G.b(0, y), G.z(1, y), G.z(2.4, y)
    G.e(bnd, t, s_).ann(bnd, t, faultfree=True).ann(t, s_, weight=weight)
    return t


L = D()
zflip(L, 0, "w_1")
zflip(L, 2, "w_2")
R = D()
ts = [zflip(R, 0, "w_1"), zflip(R, 2, "w_2")]
c, sc = R.x(1.8, 1), R.z(3.0, 1)
R.e(ts[0], c, ts[1]).e(c, sc).ann(ts[0], c, faultfree=True).ann(c, ts[1], faultfree=True)
R.ann(c, sc, weight="w_1+w_2")
rule(
    "fe-comb", lhs=L, rhs=R,
    name="Combining fault gadgets",
    aliases=["(Comb_fe)"],
    calculus="ZX", fragment="phase-free", group=G, order=24,
    summary="A fault gadget for the combination of two faults, with weight w₁ + w₂, can be added.",
    description=(
        "Two $Z$-flip gadgets on different spiders, of weights $w_1$ and $w_2$, are fault-equivalent to the same "
        "two gadgets together with a gadget for their combined fault with weight $w_1 + w_2$: a red spider "
        "connected by fault-free edges to both spiders and by a noisy edge of weight $w_1 + w_2$ to a one-legged "
        "green spider. The combined fault could already be produced by both faults together at weight "
        "$w_1 + w_2$, so the induced weight of every fault is unchanged.\n\n" + GADGET + " " + WEIGHTS),
    scalar="auto",
    source={"bib": COMPL, "location": "Fig. 3, rule $(\\textsc{Comb}_{\\text{fe}})$"},
    related=[{"id": "fe-merge", "relation": "see-also"}, {"id": "fe-detect", "relation": "see-also"}],
    tags=["fault-equivalent", "fault gadget", "weighted noise", "completeness", "atomic faults"],
)

L, R = fam(FF.fe_detect)
rule(
    "fe-detect", lhs=L, rhs=R,
    name="Removing a detectable fault gadget",
    aliases=["(Detect_fe)"],
    calculus="ZX", fragment="phase-free", group=G, order=25,
    summary="A fault gadget that is detected by a detecting spider can be removed, adding the pairwise "
            "combinations with the other gadgets on that detector.",
    description=(
        "Consider $n$ fault gadgets, with weights $w_1, \\dots, w_n$ and targets on the spiders of the legs "
        "$b_1, \\dots, b_n$, whose red spiders are all connected by fault-free edges to one green spider (on the "
        "right). This spider acts as a detector: it flags every fault that triggers an odd number of these gadgets. "
        "The first gadget can be removed from the detector, provided gadgets for its combinations with each of "
        "the others are added, with weights $w_1 + w_i$ and targets $b_1$ and $b_i$: an undetectable fault uses "
        "an even number of the gadgets, so the first gadget only matters in such combinations. Applying the rule "
        "repeatedly removes all detectable atomic faults, which are irrelevant for fault equivalence.\n\n"
        + GADGET + " " + WEIGHTS),
    scalar="sqrt(2)**(m - 1)",
    source={"bib": COMPL, "location": "Fig. 3, rule $(\\textsc{Detect}_{\\text{fe}})$"},
    related=[{"id": "fe-comb", "relation": "see-also"}],
    tags=["fault-equivalent", "fault gadget", "weighted noise", "completeness", "detecting region", "detector"],
)

L = D()
gadget_head(L, 0, weight="w_F")
R = D()
gadget_head(R, 0, faultfree=True)
rule(
    "fe-limit", lhs=L, rhs=R,
    name="Idealising heavy fault gadgets",
    aliases=["(Limit_fe)", "w-fault equivalence axiom"],
    calculus="ZX", fragment="phase-free", group=G, order=26,
    summary="For w-fault equivalence, a fault gadget of weight at least w can be made fault-free.",
    description=(
        "A fault gadget whose spawning edge has weight $w_F \\geq w$ is **$w$-fault-equivalent** to the same gadget "
        "with a fault-free spawning edge: $w$-fault equivalence only compares faults of weight less than $w$, so a "
        "fault that costs at least $w$ can be dropped. Added to the complete rules for fault equivalence, this rule "
        "gives a complete calculus for $w$-fault equivalence of Clifford ZX-diagrams.\n\n"
        "Semantically the two sides are the same ZX-diagram; only the noise annotation changes. " + GADGET + " "
        + WEIGHTS),
    conditions="w_F ≥ w; the rewrite is w-fault-equivalent (not fault-equivalent).",
    scalar="auto",
    source={"bib": COMPL, "location": "Fig. 4 (a), rule $(\\textsc{Limit}_{\\text{fe}})$"},
    related=[{"id": "fb-bound", "relation": "see-also"}, {"id": "fe-scalar", "relation": "see-also"}],
    tags=["w-fault-equivalent", "fault gadget", "weighted noise", "completeness"],
)

L = D()
gadget_head(L, 0, weight="w")
R = D()
gadget_head(R, 0, weight="w'")
rule(
    "fb-bound", lhs=L, rhs=R,
    name="Increasing the weight of a fault gadget",
    aliases=["(Bound_fb)", "fault boundedness axiom"],
    calculus="ZX", fragment="phase-free", group=G, order=27,
    summary="For fault boundedness, the weight of a fault gadget may be increased, or a fault-free gadget made noisy.",
    description=(
        "A fault gadget with weight $w$ is *fault-bounded* by the same gadget with weight $w'$ if $w \\geq w'$ or "
        "$w = -$ (the edge is fault-free on the left-hand side). Fault boundedness is the one-directional version "
        "of fault equivalence: $D_1$ is fault-bounded by $D_2$ if every undetectable fault on $D_1$ has a fault of at "
        "most the same weight with the same effect on $D_2$. So this is a directed rewrite, not a "
        "fault-equivalence. Added to the complete rules for fault equivalence it gives a complete calculus for "
        "fault boundedness, and together with [the w-fault equivalence rule](../fe-limit/) for $w$-fault "
        "boundedness.\n\n"
        "Semantically the two sides are the same ZX-diagram; only the noise annotation changes. " + GADGET + " "
        + WEIGHTS),
    conditions="w ≥ w′ or w = − (fault-free); fault boundedness only, in one direction.",
    scalar="auto",
    source={"bib": COMPL, "location": "Fig. 4 (b), rule $(\\textsc{Bound}_{\\text{fb}})$"},
    related=[{"id": "fe-limit", "relation": "see-also"}],
    tags=["fault-bounded", "fault boundedness", "fault gadget", "weighted noise", "completeness"],
)

# =============================================================================================
# Further fault-equivalent rewrites (SpiderCat, Schmidt et al., Schweikart's thesis)

CAT = "boriskhesin2026spidercat:"
RESOURCE = "schmidt2026resourceadaptive"
THESIS = "Schweikart2025Masters"

L = D()
z = L.z(1.5, 1)
for y in (0, 1, 2):
    L.e(L.b(0, y), z).e(z, L.b(3, y))
R = D()
top, bl, br = R.z(1.5, 0.2), R.z(1, 1.5), R.z(2, 1.5)
R.e(top, bl, br, top)
R.e(R.b(0, 0.2), top).e(top, R.b(3, 0.2))
R.e(R.b(0, 1.2), bl).e(R.b(0, 1.8), bl).e(br, R.b(3, 1.2)).e(br, R.b(3, 1.8))
rule(
    "fe-six-legged-spider", lhs=L, rhs=R,
    name="Fault-equivalent six-legged spider",
    aliases=["(r_6)", "triangle decomposition"],
    calculus="ZX", fragment="phase-free", group=G, order=9,
    summary="A phase-free six-legged Z-spider is fault-equivalent to a triangle of three Z-spiders with two legs each.",
    description=(
        "A six-legged Z-spider can be replaced by a triangle of three Z-spiders, each carrying two of the legs. Like "
        "the [four-legged](../fe-four-legged-spider/) and [five-legged](../fe-five-legged-spider/) rules it decomposes "
        "a spider into a ring, which forms a detecting region for the flips on its internal edges. " + EDGE_FLIP
        + "\n\nIn Schweikart's thesis the rule is shown to be moreover *matchability-preserving* in a blossom-shaped "
        "detector context: the rewritten diagram keeps a detector basis in which every fault triggers at most two "
        "detectors, so that it can still be decoded by minimum-weight perfect matching."),
    scalar="auto",
    source={"bib": THESIS, "location": "Sec. 3.3, Lemma 3.22, eq. (3.47)"},
    related=[{"id": "fe-four-legged-spider", "relation": "see-also"},
             {"id": "fe-five-legged-spider", "relation": "see-also"},
             {"id": "spider-fusion", "relation": "variant-of"}],
    tags=["fault-equivalent", "matchability-preserving", "edge-flip noise", "fault tolerance", "unfusion",
          "detecting region", "MWPM"],
)

L = D()
z = L.z(1.5, 1)
for y in (0, 1, 2):
    L.e(L.b(0, y), z).e(z, L.b(3.4, y))
R = D()
a, b = R.z(1, 1), R.z(2.4, 1)
for y in (0, 1, 2):
    R.e(R.b(0, y), a).e(b, R.b(3.4, y))
R.e(a, b).e(a, b).e(a, b)
rule(
    "fe-wire-replication", lhs=L, rhs=R,
    name="Spider unfusion with replicated wires",
    aliases=["wire replication"],
    calculus="ZX", fragment="phase-free", group=G, order=10,
    summary="Unfusing a spider is fault-equivalent if the two halves are connected by three (or more) parallel wires.",
    description=(
        "Unfusing a six-legged spider into two spiders connected by a single wire is not fault-equivalent: one flip "
        "on the connecting wire is equivalent to flips on three legs. Replicating the connecting wire fixes this: "
        "with three parallel wires there are pairwise detectors between them, so a fault on the internal wires is "
        "only undetectable if it occurs on all three, and then it can be pushed out through either spider without "
        "increasing its weight. " + EDGE_FLIP + " The rewrite is moreover matchability-preserving. Replicating "
        "wires in the same way in the four-, five- and six-legged ring decompositions gives decompositions of "
        "spiders with $4n$, $5n$ and $6n$ legs."),
    conditions="At least three parallel wires (shown for three).",
    scalar="auto",
    source={"bib": THESIS, "location": "Sec. 3.5.2, eqs. (3.76) and (3.77)"},
    related=[{"id": "spider-fusion", "relation": "variant-of"},
             {"id": "fe-six-legged-spider", "relation": "see-also"}],
    tags=["fault-equivalent", "matchability-preserving", "edge-flip noise", "fault tolerance", "unfusion",
          "parallel wires", "MWPM"],
)

L = D()
prev = L.b(0, 1)
for i in range(3):
    xv = L.x(1 + i, 1)
    L.e(prev, xv).e(xv, L.z(1 + i, 0))
    prev = xv
L.e(prev, L.b(4.2, 1))
R = D()
R.e(R.b(0, 1), R.z(1.4, 1))
R.e(R.z(2.8, 1), R.b(4.2, 1))
rule(
    "fe-repeated-measurement", lhs=L, rhs=R,
    name="Repeated measurement",
    aliases=["triple measurement fault equivalence"],
    calculus="ZX", fragment="phase-free", group=G, order=11,
    summary="Repeating a (post-selected) Z-measurement several times is fault-equivalent to cutting the wire.",
    description=(
        "A wire on which the same $Z$-measurement (an X-spider with a one-legged Z-spider attached) is repeated "
        "three times is fault-equivalent to the wire cut into a $\\langle +|$-effect and a $|+\\rangle$-state. "
        "Semantically, already a single such measurement cuts the wire; under noise, the repetitions form detecting "
        "regions so that faults between them are detected. The thesis notes that the same holds for any number "
        "$n \\geq 2$ of repetitions. " + EDGE_FLIP),
    parameters={"n": 3},
    parameter_notes="Shown for n = 3 repetitions (the triple measurement of the thesis); holds for any n ≥ 2.",
    scalar="auto",
    source={"bib": THESIS, "location": "Sec. 4.2, Lemma 4.1, eq. (4.6)"},
    related=[{"id": "fe-identity-removal", "relation": "see-also"}],
    tags=["fault-equivalent", "edge-flip noise", "fault tolerance", "measurement", "repetition",
          "syndrome extraction"],
)

L = D()
top, ul, ll = L.z(1.5, -0.2), L.z(1, 0.5), L.z(1, 1.5)
bot, lr, ur = L.z(1.5, 2.2), L.z(2, 1.5), L.z(2, 0.5)
L.e(top, ul, ll, bot, lr, ur, top)
for v in (ul, ll):
    L.e(L.b(0, L.g.qubit(v)), v)
for v in (top, ur, lr, bot):
    L.e(v, L.b(3, L.g.qubit(v)))
R = D()
z = R.z(1.5, 1)
for y in (0.5, 1.5):
    R.e(R.b(0, y), z)
for y in (-0.2, 0.5, 1.5, 2.2):
    R.e(z, R.b(3, y))
rule(
    "fe-cycle-2", lhs=L, rhs=R,
    name="Cycle of spiders as a cat state",
    aliases=["N-cycle", "loop decomposition"],
    calculus="ZX", fragment="phase-free", group=G, order=12,
    summary="A cycle of N three-legged Z-spiders is 2-fault-equivalent to a single N-legged spider (a cat state).",
    description=(
        "A cycle of $N$ phase-free Z-spiders, each with one leg, equals a single $N$-legged spider. Under edge-flip "
        "noise this is a **$w$-fault equivalence for $w = 2$** (the paper writes $\\widehat{=}$ with subscript 2): a "
        "single fault on the cycle is either detected or equivalent to a single fault on the spider, whatever $N$ is. "
        "For $N = 4$ and $N = 5$ the cycle is even [fully fault-equivalent](../fe-four-legged-spider/). In the "
        "language of the paper, this is the case $t = 1$ of fault-tolerant cat-state preparation: a loop cannot be "
        "cut by a single fault, so any number of legs can be attached to it, giving vertex ratio $r_1 = 0$."),
    parameters={"N": 6},
    parameter_notes="Shown for N = 6; holds for any N.",
    conditions="2-fault equivalence only (one fault).",
    scalar="auto",
    source={"bib": CAT, "location": "Sec. 5.2 (Graphs of Z-spiders as fault-tolerant CAT states)"},
    related=[{"id": "fe-four-legged-spider", "relation": "generalises"},
             {"id": "fe-five-legged-spider", "relation": "generalises"},
             {"id": "spider-fusion", "relation": "variant-of"}],
    tags=["w-fault-equivalent", "edge-flip noise", "fault tolerance", "cat state", "detecting region"],
)

L, R = fam(FF.fb_copy)
rule(
    "fb-copy", lhs=L, rhs=R,
    name="Copy rule is fault-bounding",
    aliases=["copy rule (fault boundedness)"],
    calculus="ZX", fragment="phase-free", group=G, order=28,
    summary="n separate |+⟩-states are fault-bounded by a Z-state plugged into an n-legged X-spider.",
    description=(
        "The ordinary [copy rule](../state-copy/) is not fault-equivalent, but it can only improve fault tolerance: "
        "the $n$ separate one-legged Z-spiders on the left are *fault-bounded* by the right-hand side, meaning every "
        "fault on the left has a fault of at most the same weight with the same effect on the right (any flip on a "
        "boundary edge on the left is the same flip on the right). The converse fails, since a single flip on the "
        "internal edge on the right spreads to all $n$ legs. So applying the copy rule from right to left, to remove "
        "a spider, never makes a diagram less fault-tolerant. The colour-swapped version holds as well."),
    conditions="Fault boundedness only (left is fault-bounded by right), not fault equivalence.",
    scalar="sqrt(2)**(n - 1)",
    source={"bib": CAT, "location": "App. C.4, lemma on the copy rule"},
    related=[{"id": "state-copy", "relation": "variant-of"}, {"id": "fb-bound", "relation": "see-also"}],
    tags=["fault-bounded", "fault boundedness", "copy", "edge-flip noise", "cat state"],
)

L = D()
tl, tr, bl, br = L.x(1, 0), L.x(2.4, 0), L.x(1, 1.6), L.x(2.4, 1.6)
L.e(L.b(0, 0), tl, tr, L.b(3.4, 0)).e(L.b(0, 1.6), bl, br, L.b(3.4, 1.6)).e(tl, bl).e(tr, br)
L.ann(tl, bl, weight="v").ann(tr, br, weight="w")
R = D()
t, b = R.x(1.7, 0), R.x(1.7, 1.6)
R.e(R.b(0, 0), t, R.b(3.4, 0)).e(R.b(0, 1.6), b, R.b(3.4, 1.6)).e(t, b)
R.ann(t, b, weight="w'")
rule(
    "fe-weighted-repetition", lhs=L, rhs=R,
    name="Fault improvement by repetition",
    aliases=["repetition rewrite", "fault-improved distribution edge"],
    calculus="ZX", fragment="phase-free", group=G, order=13,
    summary="Two noisy X-X connections in parallel are fault-equivalent to one connection with improved weights.",
    description=(
        "Under *weighted* edge-flip noise, where each edge has weights $(w_X, w_Y, w_Z)$ for its three flips, a square "
        "of four X-spiders whose two vertical edges have weights $v = (v_X, v_Y, v_Z)$ and $w = (w_X, w_Y, w_Z)$ (and the other "
        "edges weight 1) is fault-equivalent to two X-spiders connected by a single edge with weights "
        "$(w'_X, w'_Y, w'_Z) = (\\min(v_Z, w_Z), \\min(v_Y + w_Z, v_Z + w_Y), \\min(v_Z + w_Z, v_Y + w_Y))$, as written in the paper, "
        "where the weights on the right are capped at $w'_Y, w'_Z \\leq 2$ and $w'_X \\leq 1$. Repeating a noisy "
        "distribution edge (e.g. a Bell pair between two modules) in this way protects it against the errors that "
        "flip the corresponding measurement outcome; iterating gives a ladder of $d$ rungs with weights "
        "$(1/\\varepsilon, d/\\varepsilon, d/\\varepsilon)$. " + WEIGHTS),
    conditions="All weights positive; weighted edge-flip noise.",
    scalar="auto",
    source={"bib": RESOURCE, "location": "Sec. 3.2 (Repetition), proposition on fault improvement"},
    related=[{"id": "spider-fusion", "relation": "variant-of"}, {"id": "fe-merge", "relation": "see-also"}],
    tags=["fault-equivalent", "weighted noise", "edge-flip noise", "distributed QEC", "Bell pair", "repetition"],
)

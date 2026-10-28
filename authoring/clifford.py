"""Clifford-fragment ZX rules and graph-theoretic rewriting.

Sources: the stabilizer completeness papers of Backens (and Backens, Perdrix, Wang), the graph-state
papers of Duncan & Perdrix, the graph-theoretic simplification and T-count papers, the circuit
extraction paper "There and back again" and the flow-preserving completeness paper.

The diagram builders are functions of the arity so that the scalar formulas can be checked on several
instances (see the bottom of this file); the stored instance is the one passed to ``rule``.
"""

from dsl import D, rule, spread

BOOK = "KissingervdWeteringbook"
GTS = "duncan2019graph"
TCOUNT = "kissinger2019tcount"
DP1 = "DuncanPerdrixGraphStates"
DP3 = "DP3"
BPW = "BackensSimplified"
BPW_MIN = "backens2017minimal"
STOLTZ = "k.stoltz2026simplified"
SCALARS = "Backens:2015aa"
EXTRACT = "Backens2020extraction"
FLOWCOMP = "backens2026completeness"


# =============================================================================================
# Graph states: local complementation and the fixpoint property (Duncan & Perdrix 2009)

STAR3 = ((0.8, 3.6), [(1.0, 0.0), (2.2, 1.2), (2.2, 2.4)])  # hand-tuned positions for n = 3: ((ux, uy), [leaves])


def star_positions(n):
    """Positions of the centre u and of the n leaves of a star graph state, chosen so that the
    complete graph on the leaves can be drawn without edges passing through nodes."""
    if n == 3 and STAR3 is not None:
        return STAR3
    leaves = []
    for i in range(n):
        y = 1.2 + i
        x = 2.6 if i % 2 == 1 else 1.6
        leaves.append((x, y))
    return (2.2, 0.0), leaves


def graph_state_star(n, u_clifford, leaf_clifford, complete=False):
    """Star graph state with centre u and n leaves; optional single-qubit spiders on the outputs
    (u_clifford is an X phase, leaf_clifford a Z phase, None for nothing); `complete` adds the
    complete graph on the leaves."""
    Dg = D()
    (ux, uy), leaves = star_positions(n)
    u = Dg.z(ux, uy)
    if u_clifford is None:
        Dg.e(u, Dg.b(4.4, uy))
    else:
        Dg.e(u, Dg.x(3.4, uy, u_clifford), Dg.b(4.4, uy))
    ls = []
    for (x, y) in leaves:
        v = Dg.z(x, y)
        if leaf_clifford is None:
            Dg.e(v, Dg.b(4.4, y))
        else:
            Dg.e(v, Dg.z(3.4, y, leaf_clifford), Dg.b(4.4, y))
        Dg.he(u, v)
        ls.append(v)
    if complete:
        for i in range(n):
            for j in range(i + 1, n):
                Dg.he(ls[i], ls[j])
    return Dg


def build_gs_lc(n):
    return graph_state_star(n, "1/2", "-1/2"), graph_state_star(n, None, None, complete=True)


def build_gs_fixpoint(n):
    return graph_state_star(n, 1, 1), graph_state_star(n, None, None)


# =============================================================================================
# Phase gadgets with a Pauli or Clifford phase (vertex deletion)

def gadget_targets(Dg, n, phases, ys=None):
    """n target spiders (with outputs) in a zigzag, so that a complete graph on them is drawable."""
    ts = []
    for i in range(n):
        y = 1 + i
        x = 2.4 if i % 2 == 1 else 1.6
        t = Dg.z(x, y, phases[i])
        Dg.e(t, Dg.b(3.6, y))
        ts.append(t)
    return ts


def build_gadget(n, leaf_phase, target_rhs, complete, bools=""):
    L = D(bools=bools)
    ts = gadget_targets(L, n, [0] * n)
    cy = (n + 1) / 2
    hub = L.z(0.6, cy)
    L.e(hub, L.x(-0.4, cy, leaf_phase))
    for t in ts:
        L.he(hub, t)
    R = D(bools=bools)
    ts = gadget_targets(R, n, [target_rhs] * n)
    if complete:
        for i in range(n):
            for j in range(i + 1, n):
                R.he(ts[i], ts[j])
    return L, R


def build_pauli_gadget(n):
    return build_gadget(n, "a", "a", complete=False, bools="a")


def build_clifford_gadget(n):
    return build_gadget(n, "1/2", "1/2", complete=True)


# =============================================================================================
# Pivoting on graph states (Duncan & Perdrix 2013)

GSP_POS = {"a": (0.6, -0.2), "u": (2.0, 1.0), "c": (2.4, 2.0), "v": (2.0, 3.2), "b": (0.8, 4.2)}


def build_gs_pivot():
    def base(edges, clifford):
        Dg = D()
        vs = {}
        for name, (x, y) in GSP_POS.items():
            vs[name] = Dg.z(x, y)
        for name, (x, y) in GSP_POS.items():
            out = Dg.b(4.2, y)
            kind = clifford.get(name)
            if kind == "H":
                Dg.he(vs[name], out)
            elif kind == "Z":
                Dg.e(vs[name], Dg.z(3.4, y, 1), out)
            else:
                Dg.e(vs[name], out)
        for a, b in edges:
            Dg.he(vs[a], vs[b])
        return Dg
    L = base([("u", "v"), ("u", "a"), ("u", "c"), ("v", "c"), ("v", "b")], {"u": "H", "v": "H", "c": "Z"})
    # G ∧ uv: toggle a-b, a-c, b-c, and exchange the neighbourhoods of u and v
    R = base([("u", "v"), ("u", "b"), ("u", "c"), ("v", "c"), ("v", "a"),
              ("a", "b"), ("a", "c"), ("b", "c")], {})
    return L, R


# =============================================================================================
# Pivoting with phase gadgets (Kissinger & van de Wetering, T-count paper)

# Layouts (positions of the neighbours, and of u, v, the gadget hub and leaf, and w) of the stored
# instances; other arities (used to check the scalar formulas) get a simple default layout.
PIV_LAYOUTS = {
    ((1, 1, 1), False): ([(2.6, 0), (3.4, 1.5), (2.6, 3)],
                         {"u": (1, 0.5), "v": (1, 2.5), "hub": (1, 0.5), "leaf": (0, 0.5)}),
    ((2, 0, 1), True): ([(2.4, 0), (3.2, 1.2), (2.4, 2.6)],
                        {"u": (1, 0.6), "v": (1, 2.2), "hub": (1, 0.6), "leaf": (0, 0.6), "w": (1, 2.2)}),
}


def pivot_nbrs(Dg, phases, pos):
    vs = []
    for (x, y), ph in zip(pos, phases):
        v = Dg.z(x, y, ph)
        Dg.e(v, Dg.b(4.6, y))
        vs.append(v)
    return vs


def build_pivot_gadget(n_u=1, n_w=1, n_v=1, boundary=False):
    """u has phase jπ, v has phase alpha (and an input wire if `boundary`)."""
    nu = [f"alpha{i+1}" for i in range(n_u)]
    nw = [f"beta{i+1}" for i in range(n_w)]
    nv = [f"gamma{i+1}" for i in range(n_v)]
    key = ((n_u, n_w, n_v), boundary)
    if key in PIV_LAYOUTS:
        pos, P = PIV_LAYOUTS[key]
    else:
        pos = [(2.6 if i % 2 else 3.4, i) for i in range(n_u + n_w + n_v)]
        P = {"u": (1, 0.5), "v": (1, 2.5), "hub": (1, 0.5), "leaf": (0, 0.5), "w": (1, 2.5)}
    L = D(bools="j")
    u = L.z(*P["u"], "j")
    v = L.z(*P["v"], "alpha")
    L.he(u, v)
    ns = pivot_nbrs(L, nu + nw + nv, pos)
    A, B, C = ns[:n_u], ns[n_u:n_u + n_w], ns[n_u + n_w:]
    for w in A + B:
        L.he(u, w)
    for w in B + C:
        L.he(v, w)
    if boundary:
        L.e(L.b(P["v"][0] - 1, P["v"][1]), v)
    R = D(bools="j")
    ns = pivot_nbrs(R, nu + [f"{p}+j+1" for p in nw] + [f"{p}+j" for p in nv], pos)
    A, B, C = ns[:n_u], ns[n_u:n_u + n_w], ns[n_u + n_w:]
    for x in A:
        for y in B + C:
            R.he(x, y)
    for x in B:
        for y in C:
            R.he(x, y)
    hub = R.z(*P["hub"], "j")
    R.he(hub, R.z(*P["leaf"], "alpha"))
    for w in A + B:
        R.he(hub, w)
    if boundary:
        w = R.z(*P["w"], "j")
        R.he(R.b(P["w"][0] - 1, P["w"][1]), w)
        for x in A + B:
            R.he(w, x)
    return L, R


# =============================================================================================
# Graph-like identity removal / vertex splitting

def build_id_removal():
    L = D()
    a = L.z(1, 0.5, "alpha")
    m = L.z(2, 0.5)
    b = L.z(3, 0.5, "beta")
    L.ins(a, [0, 1]).he(a, m).he(m, b).outs(b, [0, 1], x=4)
    R = D()
    r = R.z(2, 0.5, "alpha+beta")
    R.ins(r, [0, 1]).outs(r, [0, 1], x=4)
    return L, R


# =============================================================================================
# CNOT = row operation on the biadjacency matrix (graph-theoretic simplification paper)

CNOT_N = [(1.0, 0), (1.2, 1), (0.8, 2)]
CNOT_F = [(2.8, 0), (2.8, 2)]


def build_cnot_row(swap_ctrl=False):
    def base(adj, cnot):
        Dg = D()
        ns = []
        for (x, y) in CNOT_N:
            v = Dg.z(x, y)
            Dg.e(Dg.b(0, y), v)
            ns.append(v)
        fs = []
        for (x, y) in CNOT_F:
            f = Dg.z(x, y)
            fs.append(f)
        for j, row in enumerate(adj):
            for i in row:
                Dg.he(fs[j], ns[i])
        if cnot:
            (t, y0), (_, y1) = CNOT_F
            top = Dg.x(3.6, y0) if not swap_ctrl else Dg.z(3.6, y0)
            bot = Dg.z(3.6, y1) if not swap_ctrl else Dg.x(3.6, y1)
            Dg.e(fs[0], top, Dg.b(4.6, CNOT_F[0][1]))
            Dg.e(fs[1], bot, Dg.b(4.6, CNOT_F[1][1]))
            Dg.e(top, bot)
        else:
            Dg.e(fs[0], Dg.b(4.6, CNOT_F[0][1]))
            Dg.e(fs[1], Dg.b(4.6, CNOT_F[1][1]))
        return Dg
    L = base([[0, 1], [1, 2]], cnot=False)
    R = base([[0, 1], [0, 2]], cnot=True)
    return L, R


# =============================================================================================
# The copy axiom (L) of the angle-free calculus for real stabilizers (Duncan & Perdrix 2013)

def build_loop_copy(n):
    ys = spread(n, 0, 1)
    L = D()
    x = L.x(0.6, 0)
    L.he(x, x)
    z = L.z(1.6, 0)
    L.e(x, z)
    for y in ys:
        L.e(z, L.b(3.0, y))
    R = D()
    for y in ys:
        x = R.x(1.6, y)
        R.he(x, x)
        R.e(x, R.b(3.0, y))
    return L, R


# =============================================================================================
# Scalar rules of the stabilizer completeness papers

def build_zero_rule():
    L = D()
    L.z(1, -1, 1)
    L.wire(0, 0, 3)
    R = D()
    R.z(1.5, -1, 1)
    R.e(R.b(0, 0), R.z(1, 0))
    R.e(R.x(2, 0), R.b(3, 0))
    return L, R


def build_zero_rule_state():
    L = D()
    L.z(0, -1, 1)
    L.e(L.z(1, 0), L.b(2, 0))
    R = D()
    R.z(0, -1, 1)
    R.e(R.x(1, 0), R.b(2, 0))
    return L, R


def build_zero_scalar():
    L = D()
    L.z(0, 0, 1)
    L.z(1, 0, "alpha")
    R = D()
    R.z(0.5, 0, 1)
    return L, R


def build_inverse():
    L = D()
    L.e(L.x(0, 0), L.z(0, 1))
    x, z = L.x(1, 0), L.z(1, 1)
    L.e(x, z).e(x, z).e(x, z)
    return L, D()


def build_inverse_simplified():
    L = D()
    L.z(0, 0.5)
    for c in (1, 2):
        x, z = L.x(c, 0), L.z(c, 1)
        L.e(x, z).e(x, z).e(x, z)
    return L, D()


# =============================================================================================
# The rules

def main():
    # ----------------------------------------------------------------------------------------
    L, R = build_gs_lc(3)
    rule(
        "graph-state-local-complementation", lhs=L, rhs=R,
        name="Local complementation of graph states",
        aliases=["Van den Nest's theorem", "graph state local complementation", "LC on graph states",
                 "local Clifford equivalence of graph states"],
        calculus="ZX", fragment="clifford", group="local-complementation", order=2,
        summary="Applying X(π/2) to a vertex of a graph state and Z(−π/2) to its neighbours complements the neighbourhood of that vertex.",
        description=(
            "A *graph state* is drawn as a phase-free Z-spider for every vertex of the graph, each with one "
            "output, connected by Hadamard edges according to the edges of the graph. *Local complementation* "
            "$G\\star u$ of a graph about a vertex $u$ toggles every edge between two neighbours of $u$. "
            "Van den Nest showed that $G\\star u$ is obtained from $G$ by local Clifford operations: an "
            "$X_{\\pi/2}$ rotation on $u$ and a $Z_{-\\pi/2}$ rotation on each neighbour of $u$ (up to a global "
            "phase; complex conjugating both sides gives the version with the opposite signs).\n\n"
            "Duncan and Perdrix proved this equation in the ZX-calculus, and showed that it holds if and only "
            "if the Hadamard gate has an [Euler decomposition](../euler-decomposition-hadamard/) into "
            "$\\pi/2$ rotations; this was the original reason to add the Euler decomposition as an axiom. "
            "Fusing the phases into the spiders, this equation is the basis of the graph-like "
            "[local complementation simplification](../local-complementation/) and of "
            "[pivoting](../graph-state-pivot/)."),
        parameters={"n": 3},
        parameter_notes=("n is the number of neighbours of u (shown for n = 3). The neighbours may be "
                         "connected to further vertices of the graph state, which are left unchanged; "
                         "existing edges between neighbours are toggled. The scalar is for neighbours that are "
                         "not yet connected; since every Hadamard edge carries a factor 1/√2, in general it is "
                         "√2 to the power (number of edges added − number of edges removed)."),
        scalar="sqrt(2)**(n*(n-1)/2)",
        source={"bib": DP1, "location": "Section 5 (Local Complementation), theorem of Van den Nest"},
        also_in=[{"bib": DP3, "location": "Section 'Graph states and Local complementation'"},
                 {"bib": GTS, "location": "Section 4, equation for local complementation of graph states"}],
        related=[{"id": "local-complementation", "relation": "used-to-derive"},
                 {"id": "euler-decomposition-hadamard", "relation": "equivalent-to"}],
        tags=["local complementation", "graph state", "local Clifford", "Van den Nest", "clifford"],
    )

    # ----------------------------------------------------------------------------------------
    L, R = build_gs_fixpoint(3)
    rule(
        "graph-state-fixpoint", lhs=L, rhs=R,
        name="Graph state stabiliser (fixpoint property)",
        aliases=["fixpoint property", "graph state stabiliser", "X on a vertex, Z on its neighbours"],
        calculus="ZX", fragment="clifford", group="local-complementation", order=3,
        summary="Applying X to a vertex of a graph state and Z to all its neighbours leaves the graph state unchanged.",
        description=(
            "For every vertex $u$ of a graph $G$, the Pauli operator $X_u \\prod_{v\\in N(u)} Z_v$ stabilises the "
            "graph state $|G\\rangle$. Graphically: the X-spider with phase π on the output of $u$ is copied "
            "through the Z-spider $u$, turns into Z-spiders with phase π after passing the Hadamard edges, and "
            "these fuse with the π phases on the neighbours, which cancel.\n\n"
            "These $|V(G)|$ operators generate the stabiliser group of the graph state. The property is also "
            "what one gets by applying [local complementation of graph states](../graph-state-local-complementation/) "
            "twice at the same vertex, since $(G\\star u)\\star u = G$."),
        parameters={"n": 3},
        parameter_notes=("n is the number of neighbours of u (shown for n = 3). The neighbours may be "
                         "connected to further vertices, which are left unchanged."),
        scalar="auto",
        source={"bib": DP1, "location": "Section 4 (Graph states), Property (Fixpoint)"},
        also_in=[{"bib": BOOK}],
        related=[{"id": "graph-state-local-complementation", "relation": "derived-from"},
                 {"id": "pi-commutation", "relation": "derived-from"}],
        tags=["graph state", "stabiliser", "fixpoint", "pauli"],
    )

    # ----------------------------------------------------------------------------------------
    L, R = build_clifford_gadget(3)
    rule(
        "clifford-gadget-removal", lhs=L, rhs=R,
        name="Clifford phase gadget removal",
        aliases=["local complementation and deletion", "(LCD)", "π/2 gadget removal",
                 "YZ-plane ±π/2 vertex removal", "lc-delete"],
        calculus="ZX", fragment="clifford", group="local-complementation", order=4,
        summary="A phase gadget with phase π/2 can be removed by complementing the connectivity of its targets and adding π/2 to each target.",
        description=(
            "A phase-free Z-spider $u$ whose only other leg is an X-spider with phase $\\frac\\pi2$ (in "
            "graph-like form: a phase gadget with phase $\\frac\\pi2$) can be removed: every pair of its "
            "neighbours has its connectivity toggled, and $\\frac\\pi2$ is added to every neighbour. With "
            "$-\\frac\\pi2$ in place of $\\frac\\pi2$, $-\\frac\\pi2$ is added instead. In MBQC terms, a vertex "
            "measured in the YZ-plane at angle $\\pm\\frac\\pi2$ can be deleted by a local complementation.\n\n"
            "As a unitary, a phase gadget on $n$ qubits with phase $\\frac\\pi2$ is $\\exp(-i\\frac\\pi4 "
            "Z\\otimes\\cdots\\otimes Z)$, which (up to global phase) is a CZ gate between every pair of "
            "qubits followed by an S gate on each. This is the reason that Clifford phase gadgets never need "
            "to remain after simplification. Compare this with the "
            "[local complementation simplification](../local-complementation/), which removes a spider with "
            "phase $\\pm\\frac\\pi2$ itself."),
        parameters={"n": 3},
        parameter_notes=("n is the number of neighbours of u (shown for n = 3). The neighbours may have any "
                         "phases and any number of further legs and edges; π/2 is added to their phases and "
                         "existing edges between them are toggled (the scalar given is for neighbours that are "
                         "not yet connected)."),
        scalar="sqrt(2)**((n-1)*(n-2)/2)",
        source={"bib": EXTRACT, "location": "Section 4.3 (Removing Clifford vertices), YZ-plane case"},
        also_in=[{"bib": FLOWCOMP, "location": "Section 3.3, rule (LCD)"}],
        related=[{"id": "local-complementation", "relation": "variant-of"},
                 {"id": "pauli-gadget-removal", "relation": "see-also"},
                 {"id": "phase-gadget-fusion", "relation": "see-also"}],
        tags=["local complementation", "phase gadget", "graph-like", "MBQC", "clifford", "simplification"],
    )

    # ----------------------------------------------------------------------------------------
    L, R = build_pauli_gadget(3)
    rule(
        "pauli-gadget-removal", lhs=L, rhs=R,
        name="Pauli phase gadget removal",
        aliases=["Z-deletion", "Z-like deletion", "Z-insertion", "(ZL)", "Pauli measurement removal",
                 "YZ-plane Pauli vertex removal"],
        calculus="ZX", fragment="clifford", group="phase-gadgets", order=3,
        summary="A spider connected only to an X-spider with phase aπ and, by Hadamard edges, to some neighbours can be removed by adding aπ to all of its neighbours.",
        description=(
            "Let $u$ be a phase-free Z-spider whose only plain leg ends in an X-spider with phase $a\\pi$ "
            "($a\\in\\{0,1\\}$), and which is connected to its neighbours by Hadamard edges. Then $u$ can be "
            "deleted, together with its edges, at the cost of adding $a\\pi$ to every neighbour. In graph-like "
            "form, $u$ is a phase gadget with a Pauli phase: a phase gadget with phase $\\pi$ is the tensor "
            "product of Pauli Z's on its targets, and a phase gadget with phase 0 is the identity.\n\n"
            "In MBQC language, this says that a qubit measured in the Z basis (a YZ- or XZ-plane measurement "
            "with a Pauli angle) can be removed from a graph state, with Pauli Z corrections on its "
            "neighbours. Read from right to left, with $a=0$, it inserts a new vertex with arbitrary "
            "neighbours ('Z-insertion'), which is used in proofs of flow-preserving completeness. "
            "If $u$ has a phase $\\beta$ (e.g. $\\frac\\pi2$, the XZ-plane case), the same holds with an "
            "additional scalar $e^{ia\\beta}$."),
        variables={"a": "boolean"},
        parameters={"n": 3},
        parameter_notes=("n is the number of neighbours of u (shown for n = 3). The neighbours may have any "
                         "phases and any number of further legs and edges; aπ is added to their phases."),
        scalar="sqrt(2)**(1-n)",
        source={"bib": EXTRACT, "location": "Section 4.3 (Removing Clifford vertices), lemma on YZ/XZ-plane Pauli measurements"},
        also_in=[{"bib": FLOWCOMP, "location": "Section 3.1 (Z-like deletion) and rule (ZL)"}],
        related=[{"id": "state-copy", "relation": "derived-from"},
                 {"id": "identity-gadget-removal", "relation": "see-also"},
                 {"id": "clifford-gadget-removal", "relation": "see-also"}],
        tags=["phase gadget", "pauli", "graph-like", "MBQC", "measurement", "deletion"],
    )

    # ----------------------------------------------------------------------------------------
    L, R = build_gs_pivot()
    rule(
        "graph-state-pivot", lhs=L, rhs=R,
        name="Pivoting of graph states",
        aliases=["pivoting property", "graph state pivot", "edge local complementation"],
        calculus="ZX", fragment="clifford", group="pivoting", order=2,
        summary="Hadamards on two adjacent vertices of a graph state and Z on their common neighbours implement a pivot of the graph.",
        description=(
            "The *pivot* $G\\wedge uv$ of a graph along an edge $uv$ is the local complementation "
            "$G\\star u\\star v\\star u$. Write $A$ for the neighbours of only $u$, $B$ for the neighbours of only "
            "$v$ and $C$ for the common neighbours. The pivot toggles every edge between two vertices from "
            "different sets among $A$, $B$, $C$, and exchanges $u$ and $v$: in $G\\wedge uv$, $u$ is connected "
            "to $B\\cup C$ and $v$ to $A\\cup C$.\n\n"
            "On graph states, $|G\\wedge uv\\rangle = H_u H_v \\prod_{w\\in C} Z_w\\,|G\\rangle$. Duncan and "
            "Perdrix showed that when $u$ and $v$ have no common neighbours this follows from the generalised "
            "bialgebra rule alone, but that the general case needs an extra axiom (the H-loop axiom, see "
            "[Hadamard self-loop removal](../hadamard-self-loop-removal/)), which in turn follows from the "
            "[Euler decomposition](../euler-decomposition-hadamard/). This equation is the basis of the "
            "graph-like [pivot simplification](../pivot/)."),
        parameter_notes=("Shown for one neighbour of only u (a), one shared neighbour (c) and one neighbour "
                         "of only v (b). The same holds for any sets of neighbours and any further vertices."),
        scalar="auto",
        source={"bib": DP3, "location": "Section 'Pivoting', Pivoting Property"},
        also_in=[{"bib": GTS, "location": "Section 4, equation for pivoting of graph states"}],
        related=[{"id": "graph-state-local-complementation", "relation": "derived-from"},
                 {"id": "pivot", "relation": "used-to-derive"},
                 {"id": "hadamard-self-loop-removal", "relation": "see-also"}],
        tags=["pivot", "pivoting", "graph state", "local Clifford", "clifford"],
    )

    # ----------------------------------------------------------------------------------------
    L, R = build_pivot_gadget(1, 1, 1)
    rule(
        "pivot-gadget", lhs=L, rhs=R,
        name="Pivot with a phase gadget",
        aliases=["gadget pivot", "pivot-gadget simplification", "(P2)", "Pauli spider removal with a non-Clifford neighbour"],
        calculus="ZX", fragment="universal", group="pivoting", order=3, view="graph-like",
        summary="An internal Pauli spider connected to an internal spider with arbitrary phase can be removed by pivoting, turning the other spider into a phase gadget.",
        description=(
            "The [pivot simplification](../pivot/) removes two connected internal spiders that both have a "
            "Pauli phase. This variant only requires one of them, $u$, to have a Pauli phase $j\\pi$; the "
            "other, $v$, may have any phase $\\alpha$. After pivoting along $uv$, $u$ is removed, and $v$ "
            "becomes a phase gadget: its phase $\\alpha$ is moved to a new arity-1 spider, and the remaining "
            "phase-free spider is connected to all former neighbours of $u$. The edges between the "
            "neighbourhoods are complemented as in the pivot rule; the shared neighbours of $u$ and $v$ get "
            "$(j+1)\\pi$ added and the neighbours of only $v$ get $j\\pi$.\n\n"
            "Here the phase gadget is drawn with phase $j\\pi$ on its hub and $\\alpha$ on its leaf; by "
            "π-commutation this is the same as a phase-free hub with leaf $(-1)^j\\alpha$, which is how the "
            "rule is usually drawn. The rule is used in PyZX's full simplification to remove all internal "
            "Pauli spiders, so that the only internal spiders left are non-Clifford spiders and phase gadgets."),
        variables={"j": "boolean", "alpha": "real", "alpha1": "real", "beta1": "real", "gamma1": "real"},
        parameters={"n_u": 1, "n_w": 1, "n_v": 1},
        parameter_notes=("n_u, n_w and n_v are the numbers of neighbours of only u, of both, and of only v "
                         "(shown for n_u = n_w = n_v = 1). The neighbours may have any number of further "
                         "legs and edges."),
        conditions="u and v are internal (not connected to inputs or outputs); u has a Pauli phase jπ.",
        scalar="sqrt(2)**((n_u-1)*n_v+n_w*(n_u+n_v-1))",
        source={"bib": TCOUNT, "location": "Section 'Full simplification of ZX-diagrams', rule (P2)"},
        also_in=[{"bib": BOOK},
                 {"bib": EXTRACT, "location": "Section 4.3 (Removing Clifford vertices)"}],
        related=[{"id": "pivot", "relation": "variant-of"},
                 {"id": "pivot-boundary", "relation": "variant-of"},
                 {"id": "phase-gadget-fusion", "relation": "see-also"}],
        tags=["pivot", "phase gadget", "graph-like", "simplification", "T-count", "pauli"],
    )

    # ----------------------------------------------------------------------------------------
    L, R = build_pivot_gadget(2, 0, 1, boundary=True)
    rule(
        "pivot-boundary", lhs=L, rhs=R,
        name="Boundary pivot",
        aliases=["pivot with a boundary spider", "boundary pivot simplification", "(P3)", "pivot-boundary simplification"],
        calculus="ZX", fragment="universal", group="pivoting", order=4, view="graph-like",
        summary="An internal Pauli spider connected to a boundary spider can be removed by pivoting, leaving a Hadamard on the boundary wire.",
        description=(
            "A variant of the [pivot simplification](../pivot/) for an internal Pauli spider $u$ (phase $j\\pi$) "
            "that is connected to a spider $v$ on a boundary wire, with any phase $\\alpha$. Pivoting along $uv$ "
            "removes $u$. The phase $\\alpha$ of $v$ becomes a phase gadget connected to the former neighbours "
            "of $u$ (as in the [gadget pivot](../pivot-gadget/)), and the boundary wire is now attached, "
            "through a Hadamard, to a new spider with phase $j\\pi$ that is connected to the former neighbours "
            "of $u$. Shared neighbours of $u$ and $v$ get $(j+1)\\pi$, neighbours of only $v$ get $j\\pi$.\n\n"
            "Together with the gadget pivot this allows removing every internal Pauli spider in a graph-like "
            "diagram. The Duncan–Kissinger–Perdrix–van de Wetering simplification achieves the same by first "
            "unfusing the boundary spider (see [graph-like identity removal](../graph-like-identity-removal/)) "
            "and then applying the ordinary pivot. As in the gadget pivot, the hub of the gadget carries $j\\pi$, "
            "which is equivalent to a phase-free hub with leaf $(-1)^j\\alpha$."),
        variables={"j": "boolean", "alpha": "real", "alpha1": "real", "alpha2": "real", "gamma1": "real"},
        parameters={"n_u": 2, "n_w": 0, "n_v": 1},
        parameter_notes=("n_u, n_w and n_v are the numbers of neighbours of only u, of both, and of only v "
                         "(shown for n_u = 2, n_w = 0, n_v = 1; shared neighbours of u and v also get "
                         "connected to the gadget and to the new boundary spider, and get (j+1)π added). "
                         "The neighbours may have any number of further legs and edges."),
        conditions="u is internal and has a Pauli phase jπ; v has exactly one boundary wire.",
        scalar="sqrt(2)**((n_u-1)*(n_v+1)+n_w*(n_u+n_v))",
        source={"bib": TCOUNT, "location": "Section 'Full simplification of ZX-diagrams', rule (P3)"},
        also_in=[{"bib": BOOK}],
        related=[{"id": "pivot", "relation": "variant-of"},
                 {"id": "graph-like-identity-removal", "relation": "derived-from"}],
        tags=["pivot", "boundary", "phase gadget", "graph-like", "simplification", "pauli"],
    )

    # ----------------------------------------------------------------------------------------
    L, R = build_id_removal()
    rule(
        "graph-like-identity-removal", lhs=L, rhs=R,
        name="Graph-like identity removal",
        aliases=["identity removal (graph-like)", "id-simp", "(id)", "neighbour unfusion", "vertex splitting",
                 "vertex fusion", "boundary unfusion"],
        calculus="ZX", fragment="universal", group="graph-like", order=1, view="graph-like",
        summary="A phase-free arity-2 spider between two Hadamard edges can be removed by fusing its two neighbours.",
        description=(
            "In a graph-like diagram, a phase-free spider with exactly two Hadamard edges is an identity "
            "(since two Hadamards cancel). Removing it makes its two neighbours adjacent by a plain wire, so "
            "they fuse: the result is a single spider with phase $\\alpha+\\beta$ that has all the other legs and "
            "edges of both neighbours (parallel Hadamard edges that arise this way can be removed with the "
            "[Hopf rule for Hadamard edges](../hadamard-hopf/)). This rule can reduce the number of "
            "non-Clifford spiders, as the phases are combined.\n\n"
            "Read from right to left, the rule *unfuses* a spider into two, splitting both its phase and its "
            "neighbourhood arbitrarily ('neighbour unfusion' or 'vertex splitting'). A common use is to "
            "unfuse a boundary spider, so that its neighbour becomes internal and pivoting can be applied "
            "(as in the graph-theoretic simplification paper)."),
        variables={"alpha": "real", "beta": "real"},
        parameter_notes="Shown for neighbours with two other legs each; holds for any number of legs and edges.",
        scalar="auto",
        source={"bib": TCOUNT, "location": "Section 'Full simplification of ZX-diagrams', rule (ID)"},
        also_in=[{"bib": GTS, "location": "Section 5, boundary unfusion before pivoting"},
                 {"bib": FLOWCOMP, "location": "Section 3.3, Proposition (Vertex splitting and fusion)"}],
        related=[{"id": "spider-fusion", "relation": "derived-from"},
                 {"id": "hadamard-cancellation", "relation": "derived-from"},
                 {"id": "identity-removal", "relation": "variant-of"}],
        tags=["identity", "graph-like", "fusion", "unfusion", "simplification", "T-count"],
    )

    # ----------------------------------------------------------------------------------------
    L, R = build_cnot_row()
    rule(
        "cnot-row-addition", lhs=L, rhs=R,
        name="CNOT as a row operation",
        aliases=["row addition", "CNOT pivot", "Gaussian elimination step", "frontier row operation"],
        calculus="ZX", fragment="clifford", group="graph-like", order=3,
        summary="A CNOT on the outputs of two spiders corresponds to adding the neighbourhood of one spider to that of the other.",
        description=(
            "Consider spiders that are each connected to one output, and to some other spiders by Hadamard "
            "edges, described by a biadjacency matrix $M$ over $\\mathbb F_2$. Adding the row of the first "
            "spider to the row of the second (toggling every Hadamard edge of the second spider to a neighbour "
            "of the first) and then applying a CNOT on their outputs, with the target on the first, leaves "
            "the diagram unchanged.\n\n"
            "This is the key step of the circuit-extraction algorithm for graph-like diagrams: Gaussian "
            "elimination of the biadjacency matrix of the frontier is turned into a CNOT circuit. Duncan, "
            "Kissinger, Perdrix and van de Wetering also show that the rule preserves focused gflow."),
        parameter_notes=("Shown for two spiders with two neighbours each, one of them shared. Holds for any "
                         "neighbourhoods; the neighbours may have any further legs and edges."),
        scalar="auto",
        source={"bib": GTS, "location": "Section 7 (Circuit extraction for general circuits), Proposition (CNOT and row operations)"},
        also_in=[{"bib": BOOK}],
        related=[{"id": "bialgebra-generalised", "relation": "derived-from"},
                 {"id": "graph-state-pivot", "relation": "see-also"}],
        tags=["CNOT", "Gaussian elimination", "extraction", "graph-like", "biadjacency", "gflow"],
    )

    # ----------------------------------------------------------------------------------------
    L, R = build_zero_rule()
    rule(
        "zero-rule", lhs=L, rhs=R,
        name="Zero rule",
        aliases=["(ZO)", "zero diagram rule", "disconnecting zero diagrams"],
        calculus="ZX", fragment="pauli", group="scalars", order=10,
        summary="In the presence of the zero scalar, any wire can be cut.",
        description=(
            "A Z-spider with phase π and no legs represents the scalar $1+e^{i\\pi}=0$. In a diagram that "
            "contains this zero scalar, any wire can be replaced by a disconnected Z-effect and X-state, since "
            "both sides are then the zero map. Together with the [zero scalar rule](../zero-scalar-rule/) this "
            "allows bringing any zero diagram into a normal form that only depends on its numbers of inputs "
            "and outputs.\n\n"
            "The rule was suggested by Kissinger and introduced as an axiom by Backens to make the stabilizer "
            "ZX-calculus complete for diagrams with scalars. In the simplified rule set of Backens, Perdrix "
            "and Wang it is replaced by the [state version](../zero-rule-state/)."),
        scalar="1",
        source={"bib": SCALARS, "location": "Section 4.3 (Completeness for stabilizer zero diagrams), zero rule"},
        also_in=[{"bib": BPW, "location": "Figure 1, rule (ZO)"}],
        axiom_of=[SCALARS],
        related=[{"id": "zero-rule-state", "relation": "variant-of"},
                 {"id": "zero-scalar-rule", "relation": "see-also"}],
        tags=["zero", "scalar", "stabilizer", "completeness", "disconnect"],
    )

    L, R = build_zero_rule_state()
    rule(
        "zero-rule-state", lhs=L, rhs=R,
        name="Zero rule (state form)",
        aliases=["(ZO')", "(ZO′)", "simplified zero rule"],
        calculus="ZX", fragment="pauli", group="scalars", order=11,
        summary="In the presence of the zero scalar, the Z-state can be replaced by the X-state.",
        description=(
            "The simplified version of the [zero rule](../zero-rule/) used in the minimal axiomatisation of "
            "the stabilizer ZX-calculus by Backens, Perdrix and Wang: next to the zero scalar (a Z-spider with "
            "phase π and no legs), a phase-free Z-state can be replaced by a phase-free X-state. Both sides "
            "are the zero vector.\n\n"
            "Together with the other simplified rules this implies the original zero rule and the "
            "[zero scalar rule](../zero-scalar-rule/), and it cannot be derived from the remaining axioms."),
        scalar="1",
        source={"bib": BPW, "location": "Figure 2 (simplified rules), rule (ZO′)"},
        also_in=[{"bib": BPW_MIN, "location": "Figure 1, rule (ZO′)"},
                 {"bib": STOLTZ, "location": "Table 1 (ZX_simp), rule (ZO′)"}],
        axiom_of=[BPW, BPW_MIN, STOLTZ],
        related=[{"id": "zero-rule", "relation": "variant-of"}],
        tags=["zero", "scalar", "stabilizer", "completeness", "minimal"],
    )

    L, R = build_zero_scalar()
    rule(
        "zero-scalar-rule", lhs=L, rhs=R,
        name="Zero scalar rule",
        aliases=["(ZS)", "zero absorbs scalars"],
        calculus="ZX", fragment="universal", group="scalars", order=12,
        summary="The zero scalar absorbs any other scalar spider.",
        description=(
            "A Z-spider with phase π and no legs is the scalar 0, so it absorbs any other scalar, in "
            "particular a Z-spider with no legs and any phase α (which is the scalar $1+e^{i\\alpha}$).\n\n"
            "Backens added this rule, together with the [zero rule](../zero-rule/), to make the stabilizer "
            "ZX-calculus with scalars complete for zero diagrams (there α is a multiple of π/2). Backens, "
            "Perdrix and Wang later showed that it is derivable from the other rules."),
        variables={"alpha": "real"},
        scalar="1",
        source={"bib": SCALARS, "location": "Section 4.3 (Completeness for stabilizer zero diagrams), zero scalar rule"},
        also_in=[{"bib": BPW, "location": "Figure 1, rule (ZS); Section 3.2 shows it is not necessary"}],
        axiom_of=[SCALARS],
        related=[{"id": "zero-rule", "relation": "see-also"}],
        tags=["zero", "scalar", "stabilizer", "completeness"],
    )

    L, R = build_inverse()
    rule(
        "inverse-rule", lhs=L, rhs=R,
        name="Inverse rule",
        aliases=["(IV)", "scalar inverse rule", "√2 · 1/√2 = 1"],
        calculus="ZX", fragment="phase-free", group="scalars", order=13,
        summary="The scalar √2 (a Z- and X-spider joined by one wire) is inverse to a Z- and X-spider joined by three wires.",
        description=(
            "A Z-spider and an X-spider connected by a single wire represent the scalar $\\sqrt2$, and a Z-spider "
            "and an X-spider connected by three wires represent $\\frac1{\\sqrt2}$. Together they are the empty "
            "diagram, i.e. the scalar 1.\n\n"
            "Backens, Perdrix and Wang introduced this rule to replace the 'star' generator (a new node "
            "representing the scalar $\\frac12$) and the star rule that Backens had used to make the "
            "stabilizer ZX-calculus complete for scalars: every non-zero stabilizer scalar can then be "
            "inverted using diagrams built from spiders only."),
        scalar="auto",
        source={"bib": BPW, "location": "Section 3.1 (Removing the star), rule (IV)"},
        related=[{"id": "inverse-rule-simplified", "relation": "equivalent-to"},
                 {"id": "hopf", "relation": "see-also"}],
        notes="The right-hand side is the empty diagram.",
        tags=["scalar", "inverse", "stabilizer", "completeness", "sqrt 2"],
    )

    L, R = build_inverse_simplified()
    rule(
        "inverse-rule-simplified", lhs=L, rhs=R,
        name="Inverse rule (simplified form)",
        aliases=["(IV')", "(IV′)", "star-free star rule"],
        calculus="ZX", fragment="phase-free", group="scalars", order=14,
        summary="The scalar 2 (a Z-spider without legs) times two copies of 1/√2 (a Z- and X-spider joined by three wires) is the empty diagram.",
        description=(
            "A Z-spider with no legs is the scalar 2, and a Z-spider and an X-spider connected by three wires is "
            "the scalar $\\frac1{\\sqrt2}$. Together the three components are the empty diagram.\n\n"
            "This is the scalar axiom of the simplified stabilizer ZX-calculus of Backens, Perdrix and Wang. It "
            "plays the role of Backens' star rule (a dedicated generator for $\\frac12$ that is inverse to the "
            "legless Z-spider), and is equivalent to the [inverse rule](../inverse-rule/) given the other "
            "axioms."),
        scalar="auto",
        source={"bib": BPW, "location": "Figure 2 (simplified rules), rule (IV′)"},
        also_in=[{"bib": BPW_MIN, "location": "Figure 1, rule (IV′)"},
                 {"bib": STOLTZ, "location": "Table 1 (ZX_simp), rule (IV′)"}],
        axiom_of=[BPW, BPW_MIN, STOLTZ],
        related=[{"id": "inverse-rule", "relation": "equivalent-to"}],
        notes="The right-hand side is the empty diagram.",
        tags=["scalar", "inverse", "stabilizer", "completeness", "minimal"],
    )


    # ----------------------------------------------------------------------------------------
    L, R = build_loop_copy(2)
    rule(
        "loop-copy", lhs=L, rhs=R,
        name="Copying the Hadamard-loop state",
        aliases=["(L)", "loop copy", "angle-free π-copy", "H-loop copy"],
        calculus="ZX", fragment="clifford", group="copy", order=10,
        summary="An X-spider with a Hadamard self-loop (the state |1⟩) is copied by a Z-spider.",
        description=(
            "A spider with a Hadamard self-loop is equal, up to a scalar, to the same spider with an extra π "
            "phase (see [Hadamard self-loop removal](../hadamard-self-loop-removal/)). So an X-spider with a "
            "Hadamard self-loop and one leg is the computational basis state $|1\\rangle$ (up to a scalar), "
            "and like any basis state it is copied by a Z-spider.\n\n"
            "Duncan and Perdrix used this rule, written with self-loops instead of π phases, as an axiom of "
            "their *angle-free* ZX-calculus, in which there are no phases at all: π phases are replaced by "
            "Hadamard self-loops (the H-loop axiom). They showed that this calculus is complete for real "
            "stabilizer quantum mechanics."),
        parameters={"n": 2},
        parameter_notes="n is the number of legs of the Z-spider (shown for n = 2).",
        scalar="1",
        source={"bib": DP3, "location": "Section 'Angle-free calculus for Real Stabilizers', axiom (L)"},
        related=[{"id": "state-copy", "relation": "variant-of"},
                 {"id": "hadamard-self-loop-removal", "relation": "see-also"}],
        tags=["copy", "self-loop", "real stabilizer", "angle-free", "basis state"],
    )


if __name__ == "__main__":
    main()

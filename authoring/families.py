"""Turn rules that hold for any number of legs into arity templates (see zxrewrites/family.py).

This rewrites lhs.json / rhs.json of the given rules to one-copy templates and adds the "arity"
specification to their meta.json, leaving all other metadata untouched (except for the fields a
family function explicitly returns as metadata updates, such as "parameter_notes", "scalar" or
"variables", when the parameters had to be renamed).

    cd authoring && python families.py [--only=spider-fusion,...]

A family function returns (L, R, spec, defaults) or (L, R, spec, defaults, meta_updates).
"""

import json

from dsl import D, ONLY, RULES_DIR
from zxrewrites import graphs

FAMILIES = {}


def family(rule_id):
    def deco(fn):
        FAMILIES[rule_id] = fn
        return fn
    return deco


def legs(n_label="inputs", m_label="outputs", lo=0, hi=4):
    return {"n": {"label": n_label, "min": lo, "max": hi}, "m": {"label": m_label, "min": lo, "max": hi}}


def param(label, lo=0, hi=4):
    return {"label": label, "min": lo, "max": hi}


def unit(param, vertices, offset=(0, 1), **kw):
    u = {"param": param, "vertices": list(vertices), "offset": list(offset)}
    u.update(kw)
    return u


def ins(p, v, shift=0.35, **kw):
    """A unit consisting of input boundary v (dots just right of it)."""
    return unit(p, [v], dots_shift=[shift, 0], **kw)


def outs(p, v, shift=0.35, **kw):
    """A unit consisting of output boundary v (dots just left of it)."""
    return unit(p, [v], dots_shift=[-shift, 0], **kw)


def spider_with_legs(D_, x, y, kind, phase=0, x_in=None, x_out=None, h=False, **kw):
    """A spider at (x, y) with one template input at x_in and one template output at x_out."""
    v = getattr(D_, kind)(x, y, phase, **kw) if kind != "h" else D_.h(x, y, **kw)
    a = b = None
    if x_in is not None:
        a = D_.b(x_in, y)
        (D_.he if h else D_.e)(a, v)
    if x_out is not None:
        b = D_.b(x_out, y)
        (D_.he if h else D_.e)(v, b)
    return v, a, b


# ---------------------------------------------------------------------------------------------
# spiders
# ---------------------------------------------------------------------------------------------

@family("spider-fusion")
def spider_fusion():
    L = D()
    a, z1, z2, b = L.b(0, 0.5), L.z(1, 0.5, "alpha"), L.z(2, 0.5, "beta"), L.b(3, 0.5)
    L.e(a, z1, z2, b)
    R = D()
    a2, z, b2 = R.b(0, 0.5), R.z(1.5, 0.5, "alpha+beta"), R.b(3, 0.5)
    R.e(a2, z, b2)
    spec = {"params": legs(),
            "lhs": [unit("n", [a], dots_shift=[0.35, 0]), unit("m", [b], dots_shift=[-0.35, 0])],
            "rhs": [unit("n", [a2], dots_shift=[0.35, 0]), unit("m", [b2], dots_shift=[-0.35, 0])]}
    return L, R, spec, {"n": 2, "m": 2}


def _single_spider_rule(lhs_kind, lhs_phase, rhs_kind, rhs_phase, loop=None, y=0.5, x_out=2,
                        offset=1, rhs_h=False):
    """A rule between two diagrams consisting of one spider with n inputs and m outputs
    (the LHS optionally with a self-loop of type loop = 'e' or 'he')."""
    L = D()
    z, a, b = spider_with_legs(L, x_out / 2, y, lhs_kind, lhs_phase, 0, x_out)
    if loop:
        getattr(L, loop)(z, z)
    R = D()
    z2, a2, b2 = spider_with_legs(R, x_out / 2, y, rhs_kind, rhs_phase, 0, x_out, h=rhs_h)
    off = (0, offset)
    spec = {"params": legs(),
            "lhs": [ins("n", a, offset=off), outs("m", b, offset=off)],
            "rhs": [ins("n", a2, offset=off), outs("m", b2, offset=off)]}
    return L, R, spec


@family("self-loop-removal")
def self_loop_removal():
    L, R, spec = _single_spider_rule("z", "alpha", "z", "alpha", loop="e")
    return L, R, spec, {"n": 2, "m": 2}, {
        "parameter_notes": "n inputs and m outputs (shown for n = m = 2); holds for any number of legs."}


@family("hadamard-self-loop-removal")
def hadamard_self_loop_removal():
    L, R, spec = _single_spider_rule("z", "alpha", "z", "alpha+1", loop="he", y=0)
    return L, R, spec, {"n": 1, "m": 1}, {
        "parameter_notes": "n inputs and m outputs (shown for n = m = 1); holds for any number of legs."}


@family("colour-change")
def colour_change():
    L, R, spec = _single_spider_rule("x", "alpha", "z", "alpha", x_out=3, offset=1.4, rhs_h=True)
    return L, R, spec, {"n": 2, "m": 2}, {
        "parameter_notes": "n inputs and m outputs (shown for n = m = 2); holds for any number of legs."}


@family("hadamard-hopf")
def hadamard_hopf():
    L = D()
    z1, a, _ = spider_with_legs(L, 1, 0.5, "z", "alpha", x_in=0)
    z2, _, b = spider_with_legs(L, 2.4, 0.5, "z", "beta", x_out=3.4)
    L.he(z1, z2).he(z1, z2)
    R = D()
    y1, a2, _ = spider_with_legs(R, 1, 0.5, "z", "alpha", x_in=0)
    y2, _, b2 = spider_with_legs(R, 2.4, 0.5, "z", "beta", x_out=3.4)
    spec = {"params": legs(), "lhs": [ins("n", a), outs("m", b)], "rhs": [ins("n", a2), outs("m", b2)]}
    return L, R, spec, {"n": 2, "m": 2}, {
        "parameter_notes": "n legs on the first spider and m legs on the second (shown for n = m = 2); "
                           "holds for any number of legs."}


@family("pi-commutation")
def pi_commutation():
    L = D()
    a, x, z, b = L.b(0, 0), L.x(1, 0, 1), L.z(2, 0, "alpha"), L.b(3, 0)
    L.e(a, x, z, b)
    R = D()
    a2, z2 = R.b(0, 0), R.z(1, 0, "-alpha")
    x2, b2 = R.x(2, 0, 1), R.b(3, 0)
    R.e(a2, z2, x2, b2)
    spec = {"params": {"m": param("outputs")},
            "lhs": [outs("m", b)],
            "rhs": [unit("m", [x2, b2], dots_shift=[-0.45, 0])]}
    return L, R, spec, {"m": 2}, {
        "parameter_notes": "m is the number of other legs of the spider (shown for m = 2); holds for any m."}


@family("state-copy")
def state_copy():
    L = D(bools="a")
    x, z, b = L.x(0, 0, "a"), L.z(1, 0, "alpha"), L.b(2, 0)
    L.e(x, z, b)
    R = D(bools="a")
    x2, b2 = R.x(1, 0, "a"), R.b(2, 0)
    R.e(x2, b2)
    spec = {"params": {"n": param("outputs")},
            "lhs": [outs("n", b)],
            "rhs": [unit("n", [x2, b2], dots_shift=[0.5, 0])]}
    return L, R, spec, {"n": 2}


@family("bialgebra-generalised")
def bialgebra_generalised():
    L = D()
    x, z = L.x(1, 1), L.z(2, 1)
    a, b = L.b(0, 1), L.b(3, 1)
    L.e(a, x, z, b)
    R = D()
    z2, a2 = R.z(1, 1), R.b(0, 1)
    x2, b2 = R.x(2.4, 1), R.b(3.4, 1)
    R.e(a2, z2, x2, b2)
    spec = {"params": legs(),
            "lhs": [ins("n", a, offset=(0, 1.2)), outs("m", b)],
            "rhs": [unit("n", [a2, z2], offset=(0, 1.2), dots_shift=[0.5, 0]),
                    unit("m", [b2, x2], dots_shift=[-0.5, 0])]}
    return L, R, spec, {"n": 2, "m": 3}


@family("phase-gadget-fusion")
def phase_gadget_fusion():
    c = 3

    def targets(D_):
        z, a, b = spider_with_legs(D_, 2, c, "z", "gamma", 0, 4)
        return z, a, b

    L = D()
    g1x, g1z = L.x(0.8, 1), L.z(0.8, 0, "alpha")
    g2x, g2z = L.x(3.2, 1), L.z(3.2, 0, "beta")
    L.e(g1x, g1z).e(g2x, g2z)
    z, a, b = targets(L)
    L.e(z, g1x).e(z, g2x)
    R = D()
    gx, gz = R.x(0.8, 1), R.z(0.8, 0, "alpha+beta")
    R.e(gx, gz)
    z2, a2, b2 = targets(R)
    R.e(z2, gx)
    spec = {"params": {"n": param("targets", 1)},
            "lhs": [unit("n", [a, z, b], dots_shift=[0.7, 0], index_vars=["gamma"])],
            "rhs": [unit("n", [a2, z2, b2], dots_shift=[0.7, 0], index_vars=["gamma"])]}
    return L, R, spec, {"n": 2}, {
        "variables": {"alpha": "real", "beta": "real", "gamma": "real"}}


@family("identity-gadget-removal")
def identity_gadget_removal():
    L = D()
    z, a, b = spider_with_legs(L, 2, 1, "z", "beta", 0, 3)
    h, leaf = L.z(2, 0), L.z(2, -1, "alpha")
    L.he(z, h, leaf)
    R = D()
    z2, a2, b2 = spider_with_legs(R, 1.5, 1, "z", "alpha+beta", 0, 3)
    spec = {"params": legs(), "lhs": [ins("n", a), outs("m", b)], "rhs": [ins("n", a2), outs("m", b2)]}
    return L, R, spec, {"n": 2, "m": 2}, {
        "parameter_notes": "n inputs and m outputs on the spider (shown for n = m = 2); holds for any "
                           "number of legs."}


@family("graph-like-identity-removal")
def graph_like_identity_removal():
    L = D()
    z1, a, _ = spider_with_legs(L, 1, 0.5, "z", "alpha", x_in=0)
    z2, _, b = spider_with_legs(L, 3, 0.5, "z", "beta", x_out=4)
    mid = L.z(2, 0.5)
    L.he(z1, mid, z2)
    R = D()
    y, a2, b2 = spider_with_legs(R, 2, 0.5, "z", "alpha+beta", 0, 4)
    spec = {"params": legs(), "lhs": [ins("n", a), outs("m", b)], "rhs": [ins("n", a2), outs("m", b2)]}
    return L, R, spec, {"n": 2, "m": 2}, {
        "parameter_notes": "n legs on the first neighbour and m on the second (shown for n = m = 2); "
                           "holds for any number of legs."}


@family("pauli-gadget-removal")
def pauli_gadget_removal():
    L = D(bools="a")
    u, g = L.z(0.6, 2), L.x(-0.4, 2, "a")
    L.e(u, g)
    z, _, b = spider_with_legs(L, 2, 2, "z", 0, x_out=3.6)
    L.he(u, z)
    R = D(bools="a")
    z2, _, b2 = spider_with_legs(R, 2, 2, "z", "a", x_out=3.6)
    spec = {"params": {"n": param("neighbours", 1)},
            "lhs": [unit("n", [z, b], dots_shift=[-0.5, 0])],
            "rhs": [unit("n", [z2, b2], dots_shift=[0.8, 0])]}
    return L, R, spec, {"n": 3}


@family("graph-state-fixpoint")
def graph_state_fixpoint():
    Y = 3.6
    L = D()
    u, xu, bu = L.z(0.8, Y), L.x(3.4, Y, 1), L.b(4.4, Y)
    L.e(u, xu, bu)
    z, p, b = L.z(2.2, 1.2), L.z(3.4, 1.2, 1), L.b(4.4, 1.2)
    L.e(z, p, b).he(u, z)
    R = D()
    u2, bu2 = R.z(0.8, Y), R.b(4.4, Y)
    R.e(u2, bu2)
    z2, b2 = R.z(2.2, 1.2), R.b(4.4, 1.2)
    R.e(z2, b2).he(u2, z2)
    spec = {"params": {"n": param("neighbours", 1)},
            "lhs": [unit("n", [z, p, b], offset=(0, 1.2), dots_shift=[0.6, 0])],
            "rhs": [unit("n", [z2, b2], offset=(0, 1.2), dots_shift=[0.6, 0])]}
    return L, R, spec, {"n": 3}


# ---------------------------------------------------------------------------------------------
# pivots
# ---------------------------------------------------------------------------------------------

PIVOT_C = {"U": 0, "W": 2.5, "V": 5}  # vertical centres of the three neighbour blocks
PIVOT_X_LHS = 2.4                    # column of the neighbours on the LHS
# RHS layouts: block -> (x, y, offset); found by a search that avoids edges passing through nodes
# for every instance up to 3 neighbours per block
PIVOT_RHS = {"U": (2.5, 0, (-0.5, 1)), "W": (-1.5, 2.5, (-0.1, 1)), "V": (3.3, 5, (-0.6, 1))}
GADGET_RHS = {"U": (2.5, 0, (0.7, 0.8)), "W": (-1.5, 2.5, (0.3, 1)), "V": (3.5, 5, (-0.5, 1))}
BOUNDARY_RHS = {"U": (3.6, 0, (-0.5, 1)), "W": (0.1, 2.5, (-0.3, 1)), "V": (4.3, 5, (-0.5, 1))}


def _pivot_rhs(R, layout, phases, xo):
    """The three neighbour blocks of the RHS of a pivot rule, with all edges between them."""
    out = {}
    for blk, ph in zip("UWV", phases):
        x, y, off = layout[blk]
        out[blk] = _neighbour(R, x, y, ph, xo)
    R.he(out["U"][0], out["W"][0]).he(out["U"][0], out["V"][0]).he(out["W"][0], out["V"][0])
    return out


def _pivot_units(nbrs, names, layout=None):
    ps = {"U": "n_u", "W": "n_w", "V": "n_v"}
    return [unit(ps[b], list(nbrs[b]), offset=(layout[b][2] if layout else (0, 1)), dots_shift=[0.8, 0],
                 index_vars=[names[i]]) for i, b in enumerate("UWV")]


def pivot_params(hi=3):
    return {"n_u": param("neighbours of only u", 0, hi), "n_w": param("shared neighbours", 0, hi),
            "n_v": param("neighbours of only v", 0, hi)}


def _neighbour(D_, x, y, phase, x_out):
    z = D_.z(x, y, phase)
    b = D_.b(x_out, y)
    D_.e(z, b)
    return z, b


@family("pivot")
def pivot():
    L = D(bools="j k")
    u, v = L.z(1, 1.25, "j"), L.z(1, 3.75, "k")
    L.he(u, v)
    xo = 4.4
    zu, bu = _neighbour(L, PIVOT_X_LHS, PIVOT_C["U"], "alpha", xo)
    zw, bw = _neighbour(L, PIVOT_X_LHS, PIVOT_C["W"], "beta", xo)
    zv, bv = _neighbour(L, PIVOT_X_LHS, PIVOT_C["V"], "gamma", xo)
    L.he(u, zu).he(u, zw).he(v, zw).he(v, zv)
    R = D(bools="j k")
    rn = _pivot_rhs(R, PIVOT_RHS, ("alpha+k", "beta+j+k+1", "gamma+j"), 4.8)
    names = ["alpha", "beta", "gamma"]
    spec = {"params": pivot_params(),
            "lhs": _pivot_units({"U": (zu, bu), "W": (zw, bw), "V": (zv, bv)}, names),
            "rhs": _pivot_units(rn, names, PIVOT_RHS)}
    return L, R, spec, {"n_u": 2, "n_w": 1, "n_v": 2}, {
        "variables": {"j": "boolean", "k": "boolean", "alpha": "real", "beta": "real", "gamma": "real"}}


@family("pivot-gadget")
def pivot_gadget():
    L = D(bools="j")
    u, v = L.z(1, 1.25, "j"), L.z(1, 3.75, "alpha")
    L.he(u, v)
    xo = 4.4
    zu, bu = _neighbour(L, PIVOT_X_LHS, PIVOT_C["U"], "delta", xo)
    zw, bw = _neighbour(L, PIVOT_X_LHS, PIVOT_C["W"], "beta", xo)
    zv, bv = _neighbour(L, PIVOT_X_LHS, PIVOT_C["V"], "gamma", xo)
    L.he(u, zu).he(u, zw).he(v, zw).he(v, zv)
    R = D(bools="j")
    hub, leaf = R.z(0, 0, "j"), R.z(-1, 0, "alpha")
    R.he(hub, leaf)
    rn = _pivot_rhs(R, GADGET_RHS, ("delta", "beta+j+1", "gamma+j"), 4.8)
    R.he(hub, rn["U"][0]).he(hub, rn["W"][0])
    names = ["delta", "beta", "gamma"]
    spec = {"params": pivot_params(2),
            "lhs": _pivot_units({"U": (zu, bu), "W": (zw, bw), "V": (zv, bv)}, names),
            "rhs": _pivot_units(rn, names, GADGET_RHS)}
    return L, R, spec, {"n_u": 1, "n_w": 1, "n_v": 1}, {
        "variables": {"j": "boolean", "alpha": "real", "delta": "real", "beta": "real", "gamma": "real"}}


@family("pivot-boundary")
def pivot_boundary():
    L = D(bools="j")
    u, v = L.z(1, 1.25, "j"), L.z(1, 3.75, "alpha")
    L.he(u, v).e(L.b(0, 3.75), v)
    xo = 4.4
    zu, bu = _neighbour(L, PIVOT_X_LHS, PIVOT_C["U"], "delta", xo)
    zw, bw = _neighbour(L, PIVOT_X_LHS, PIVOT_C["W"], "beta", xo)
    zv, bv = _neighbour(L, PIVOT_X_LHS, PIVOT_C["V"], "gamma", xo)
    L.he(u, zu).he(u, zw).he(v, zw).he(v, zv)
    R = D(bools="j")
    hub, leaf = R.z(-1.5, -0.5, "j"), R.z(-2.5, -0.5, "alpha")
    new, bnew = R.z(-1.5, 0.5, "j"), R.b(-2.5, 0.5)
    R.he(hub, leaf).he(bnew, new)
    rn = _pivot_rhs(R, BOUNDARY_RHS, ("delta", "beta+j+1", "gamma+j"), 5.8)
    for t in (hub, new):
        R.he(t, rn["U"][0]).he(t, rn["W"][0])
    names = ["delta", "beta", "gamma"]
    spec = {"params": pivot_params(2),
            "lhs": _pivot_units({"U": (zu, bu), "W": (zw, bw), "V": (zv, bv)}, names),
            "rhs": _pivot_units(rn, names, BOUNDARY_RHS)}
    return L, R, spec, {"n_u": 2, "n_w": 0, "n_v": 1}, {
        "variables": {"j": "boolean", "alpha": "real", "delta": "real", "beta": "real", "gamma": "real"}}


# ---------------------------------------------------------------------------------------------
# ZH
# ---------------------------------------------------------------------------------------------

def _h_fusion(label):
    L = D()
    h1 = L.h(1, 0.5, label=label) if label else L.h(1, 0.5)
    h2, h3 = L.h(2, 0.5), L.h(3, 0.5)
    a, b = L.b(0, 0.5), L.b(4, 0.5)
    L.e(a, h1, h2, h3, b)
    R = D()
    h = R.h(1.5, 0.5, label=label) if label else R.h(1.5, 0.5)
    a2, b2 = R.b(0, 0.5), R.b(3, 0.5)
    R.e(a2, h, b2)
    spec = {"params": legs(), "lhs": [ins("n", a), outs("m", b)], "rhs": [ins("n", a2), outs("m", b2)]}
    return L, R, spec, {"n": 2, "m": 2}, {
        "parameter_notes": "n legs on the first H-box and m on the second (shown for n = m = 2); holds for "
                           "any number of legs."}


@family("zh-h-box-fusion")
def zh_h_box_fusion():
    return _h_fusion(None)


@family("zh-h-box-fusion-labelled")
def zh_h_box_fusion_labelled():
    return _h_fusion("a")


def _multiply_like(average):
    L = D()
    ha, hb = L.h(1, 0, label="a"), L.h(1, 1, label="b")
    z, b = L.z(2, 0.5), L.b(3, 0.5)
    L.e(ha, z).e(hb, z).e(z, b)
    if average:
        x = L.x(0, 0.5, 1)
        L.e(x, ha).e(x, hb)
    R = D()
    h = R.h(1.5, 0.5, label="(a+b)/2" if average else "a⋅b")
    b2 = R.b(3, 0.5)
    R.e(h, b2)
    spec = {"params": {"n": param("Z-spiders", 1)},
            "lhs": [unit("n", [z, b], dots_shift=[0.5, 0])],
            "rhs": [outs("n", b2, shift=0.5)]}
    return L, R, spec, {"n": 2}


@family("zh-multiply-generalised")
def zh_multiply_generalised():
    return _multiply_like(False)


@family("zh-average-generalised")
def zh_average_generalised():
    return _multiply_like(True)


@family("zh-unit-generalised")
def zh_unit_generalised():
    L = D()
    h, a, b = L.h(1, 0.5, label=1), L.b(0, 0.5), L.b(2, 0.5)
    L.e(a, h, b)
    R = D()
    a2, za = R.b(0, 0.5), R.z(1, 0.5)
    zb, b2 = R.z(1.6, 0.5), R.b(2.6, 0.5)
    R.e(a2, za).e(zb, b2)
    spec = {"params": legs(),
            "lhs": [ins("n", a), outs("m", b)],
            "rhs": [unit("n", [a2, za], dots_shift=[0.5, 0]), unit("m", [b2, zb], dots_shift=[-0.5, 0])]}
    return L, R, spec, {"n": 1, "m": 2}, {
        "parameter_notes": "n inputs and m outputs on the H-box (shown for n = 1, m = 2); holds for any "
                           "number of legs."}


@family("zh-bialgebra")
def zh_bialgebra():
    L = D()
    h, x = L.h(1, 0.5), L.x(2, 0.5)
    a, b = L.b(0, 0.5), L.b(3, 0.5)
    L.e(a, h, x, b)
    R = D()
    z, a2 = R.z(1, 0.5), R.b(0, 0.5)
    h2, b2 = R.h(2, 0.5), R.b(3, 0.5)
    R.e(a2, z, h2, b2)
    spec = {"params": legs("legs of the H-box", "legs of the X-spider"),
            "lhs": [ins("n", a), outs("m", b)],
            "rhs": [unit("n", [a2, z], dots_shift=[0.5, 0]), unit("m", [b2, h2], dots_shift=[-0.5, 0])]}
    return L, R, spec, {"n": 2, "m": 2}, {
        "scalar": "sqrt(2)**(1-m)",
        "parameter_notes": "n legs on the H-box and m on the X-spider (shown for n = m = 2); holds for any "
                           "numbers of legs."}


def _h_copy(state):
    L = D()
    s = L.x(0, 0.5) if state == "x" else L.z(0, 0.5, 1)
    h, b = L.h(1, 0.5), L.b(2, 0.5)
    L.e(s, h, b)
    R = D()
    c = R.z(1, 0.5) if state == "x" else R.x(1, 0.5, 1)
    b2 = R.b(2, 0.5)
    R.e(c, b2)
    spec = {"params": {"n": param("outputs")},
            "lhs": [outs("n", b)],
            "rhs": [unit("n", [c, b2], dots_shift=[0.5, 0])]}
    return L, R, spec, {"n": 2}, ({} if state == "x" else {"scalar": "sqrt(2)**(2-n)"})


@family("zh-h-box-zero-state-copy")
def zh_h_box_zero_state_copy():
    return _h_copy("x")


@family("zh-h-box-z-pi-copy")
def zh_h_box_z_pi_copy():
    return _h_copy("z")


@family("zh-x-spider-as-h-boxes")
def zh_x_spider_as_h_boxes():
    L = D()
    x, a, b = L.x(1, 0.5), L.b(0, 0.5), L.b(2, 0.5)
    L.e(a, x, b)
    R = D()
    a2, ha, z, hb, b2 = R.b(0, 0.5), R.h(1, 0.5), R.z(2, 0.5), R.h(3, 0.5), R.b(4, 0.5)
    R.e(a2, ha, z, hb, b2)
    spec = {"params": legs(),
            "lhs": [ins("n", a), outs("m", b)],
            "rhs": [unit("n", [a2, ha], dots_shift=[0.5, 0]), unit("m", [b2, hb], dots_shift=[-0.5, 0])]}
    return L, R, spec, {"n": 1, "m": 2}, {
        "scalar": "sqrt(2)**(-(n+m))",
        "parameter_notes": "n inputs and m outputs on the X-spider (shown for n = 1, m = 2); holds for any "
                           "number of legs."}


@family("zh-x-phase-through-h-box")
def zh_x_phase_through_h_box():
    L = D()
    a, x, h, b = L.b(0, 0.5), L.x(1, 0.5, "alpha"), L.h(2, 0.5), L.b(3, 0.5)
    L.e(a, x, h, b)
    R = D()
    a2, h1 = R.b(0, 0.5), R.h(1, 0.5)
    ha = R.h(1, 2, phase="alpha")
    z, b2 = R.z(2.2, 0.5), R.b(4, 0.5)
    R.e(a2, h1, z, b2).e(ha, z)
    spec = {"params": {"n": param("other legs of the H-box", 1)},
            "lhs": [outs("n", b)],
            "rhs": [unit("n", [z, b2], dots_shift=[0.8, 0])]}
    return L, R, spec, {"n": 2}, {
        "parameter_notes": "n is the number of other legs of the H-box (shown for n = 2); holds for any n."}


# ---------------------------------------------------------------------------------------------
# ZW
# ---------------------------------------------------------------------------------------------

@family("w-fusion")
def w_fusion():
    c1, c2 = 0, 2.5
    L = D()
    w1, w1i = L.w(1.5, 1)
    w2, w2i = L.w(3, c2)
    a, bn, bm = L.b(0, 1), L.b(4.5, c1), L.b(4.5, c2)
    L.e(a, w1i).e(w1, bn).e(w1, w2i).e(w2, bm)
    R = D()
    w, wi = R.w(2, 1.25)
    a2, bn2, bm2 = R.b(0, 1.25), R.b(4.5, c1), R.b(4.5, c2)
    R.e(a2, wi).e(w, bn2).e(w, bm2)
    spec = {"params": {"n": param("other outputs of the first W-spider", 0, 3),
                       "m": param("outputs of the second W-spider", 0, 3)},
            "lhs": [outs("n", bn, shift=0.6), outs("m", bm, shift=0.6)],
            "rhs": [outs("n", bn2, shift=0.6), outs("m", bm2, shift=0.6)]}
    return L, R, spec, {"n": 1, "m": 2}, {
        "parameter_notes": "n is the number of other outputs of the first W-spider and m the number of "
                           "outputs of the second (shown for n = 1, m = 2); holds for any n and m."}


def _w_commute(kind):
    L = D()
    a = L.b(0, 0)
    s = L.z(1, 0, 1) if kind == "pi" else L.zbox(1, 0, "r")
    w, wi = L.w(2.2, 0)
    b = L.b(3.4, 0)
    L.e(a, s, wi).e(w, b)
    R = D()
    a2 = R.b(0, 0)
    w2, wi2 = R.w(1.2, 0)
    s2 = R.z(2.3, 0, 1) if kind == "pi" else R.zbox(2.3, 0, "r")
    b2 = R.b(3.4, 0)
    R.e(a2, wi2).e(w2, s2, b2)
    spec = {"params": {"m": param("outputs", 1)},
            "lhs": [outs("m", b, shift=0.5)],
            "rhs": [unit("m", [s2, b2], dots_shift=[-0.55, 0])]}
    return L, R, spec, {"m": 2}, {
        "parameter_notes": "m is the number of outputs of the W-spider (shown for m = 2); holds for any m."}


@family("w-pi-commutation")
def w_pi_commutation():
    return _w_commute("pi")


@family("w-weight-copy")
def w_weight_copy():
    return _w_commute("r")


@family("w-z-bialgebra")
def w_z_bialgebra():
    L = D()
    w, wi = L.w(1.1, 0.5, input_dir=(0.35, 0))
    z = L.z(2.3, 0.5)
    a, b = L.b(0, 0.5), L.b(3.4, 0.5)
    L.e(a, w).e(wi, z).e(z, b)
    R = D()
    z2, a2 = R.z(1, 0.5), R.b(0, 0.5)
    w2, wi2 = R.w(2.4, 0.5, input_dir=(0.35, 0))
    b2 = R.b(3.6, 0.5)
    R.e(a2, z2, w2).e(wi2, b2)
    spec = {"params": {"n": param("inputs"), "m": param("outputs", 1)},
            "lhs": [ins("n", a), outs("m", b, shift=0.5)],
            "rhs": [unit("n", [a2, z2], dots_shift=[0.5, 0]), unit("m", [b2, w2, wi2], dots_shift=[-0.4, 0])]}
    return L, R, spec, {"n": 2, "m": 2}, {
        "parameter_notes": "n inputs and m outputs (shown for n = m = 2); holds for any numbers of inputs "
                           "and outputs."}


@family("w-zero-copy")
def w_zero_copy():
    L = D()
    w0, w0i = L.w(0.6, 0.5, input_dir=(0.35, 0))
    w, wi = L.w(2.2, 0.5)
    b = L.b(3.2, 0.5)
    L.e(w0i, wi).e(w, b)
    R = D()
    w2, wi2 = R.w(1.6, 0.5, input_dir=(0.35, 0))
    b2 = R.b(3.2, 0.5)
    R.e(wi2, b2)
    spec = {"params": {"m": param("outputs", 1)},
            "lhs": [outs("m", b, shift=0.5)],
            "rhs": [unit("m", [w2, wi2, b2], dots_shift=[0.8, 0])]}
    return L, R, spec, {"m": 2}, {
        "parameter_notes": "m is the number of outputs of the W-spider (shown for m = 2); holds for any m."}


# ---------------------------------------------------------------------------------------------
# other
# ---------------------------------------------------------------------------------------------

@family("antiphase-twins")
def antiphase_twins():
    L = D()
    u, v = L.z(0, 0, "alpha"), L.z(0, 2, "alpha+1")
    x, b = L.x(1.5, 1, "beta"), L.b(2.5, 1)
    L.e(u, x).e(v, x).e(x, b)
    R = D()
    w = R.z(0, 1, "2*alpha+1")
    x2, b2 = R.x(1.5, 1, "beta"), R.b(2.5, 1)
    R.e(w, x2).e(w, x2).e(x2, b2)
    spec = {"params": {"n": param("common neighbours", 0)},
            "lhs": [unit("n", [x, b], offset=(0, 2), dots_shift=[0.5, 0], index_vars=["beta"])],
            "rhs": [unit("n", [x2, b2], offset=(0, 2), dots_shift=[0.5, 0], index_vars=["beta"])]}
    return L, R, spec, {"n": 2}, {
        "variables": {"alpha": "real", "beta": "real"},
        "parameter_notes": "n is the number of common neighbours of the twins (shown for n = 2, as X-spiders "
                           "with one output each); holds for any common neighbourhood."}


@family("local-complementation")
def local_complementation():
    L = D()
    c = L.z(0.3, 1, "1/2")
    v, b = L.z(1.6, 1, "alpha"), L.b(3.2, 1)
    L.e(v, b).he(c, v)
    R = D()
    v2, b2 = R.z(1.6, 1, "alpha-1/2"), R.b(3.2, 1)
    R.e(v2, b2)
    nb = dict(offset=(0, 1), bulge=[0.7, 0], dots_shift=[0.55, 0], index_vars=["alpha"])
    spec = {"params": {"n": param("neighbours", 0, 4)},
            "lhs": [unit("n", [v, b], **nb)],
            "rhs": [unit("n", [v2, b2], clique=[[v2, v2, 2]], **nb)]}
    return L, R, spec, {"n": 3}, {
        "variables": {"alpha": "real"},
        "parameter_notes": ("n is the number of neighbours (shown for n = 3). The neighbours may have any number "
                            "of further legs and edges.")}


@family("graph-state-local-complementation")
def graph_state_local_complementation():
    def side(clifford):
        Dg = D()
        u = Dg.z(2.2, -0.6)
        if clifford:
            Dg.e(u, Dg.x(3.4, -0.6, "1/2"), Dg.b(4.4, -0.6))
        else:
            Dg.e(u, Dg.b(4.4, -0.6))
        v = Dg.z(1.6, 2)
        b = Dg.b(4.4, 2)
        vs = [v, b]
        if clifford:
            z = Dg.z(3.4, 2, "-1/2")
            Dg.e(v, z, b)
            vs.append(z)
        else:
            Dg.e(v, b)
        Dg.he(u, v)
        return Dg, v, vs
    L, _, lv = side(True)
    R, v2, rv = side(False)
    nb = dict(offset=(0, 1), bulge=[0.8, 0], dots_shift=[0.5, 0])
    spec = {"params": {"n": param("neighbours", 0, 4)},
            "lhs": [unit("n", lv, **nb)],
            "rhs": [unit("n", rv, clique=[[v2, v2, 2]], **nb)]}
    return L, R, spec, {"n": 3}


@family("clifford-gadget-removal")
def clifford_gadget_removal():
    L = D()
    hub = L.z(0.6, 1)
    L.e(hub, L.x(-0.4, 1, "1/2"))
    t, b = L.z(1.6, 1), L.b(3.6, 1)
    L.e(t, b).he(hub, t)
    R = D()
    t2, b2 = R.z(1.6, 1, "1/2"), R.b(3.6, 1)
    R.e(t2, b2)
    nb = dict(offset=(0, 1), bulge=[0.8, 0], dots_shift=[0.5, 0])
    spec = {"params": {"n": param("targets", 0, 4)},
            "lhs": [unit("n", [t, b], **nb)],
            "rhs": [unit("n", [t2, b2], clique=[[t2, t2, 2]], **nb)]}
    return L, R, spec, {"n": 3}


def main():
    for rid, fn in FAMILIES.items():
        if ONLY and rid not in ONLY:
            continue
        d = RULES_DIR / rid
        meta = json.loads((d / "meta.json").read_text(encoding="utf8"))
        res = fn()
        L, R, spec, defaults = res[:4]
        updates = res[4] if len(res) > 4 else {}
        for x in (L, R):
            x.g.auto_detect_io()
        graphs.save(L.g, d / "lhs.json")
        graphs.save(R.g, d / "rhs.json")
        meta["arity"] = spec
        meta["parameters"] = dict(defaults)
        meta.update(updates)
        (d / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf8")
        print("templated", rid)


if __name__ == "__main__":
    main()

"""Arity templates of the fault-equivalent rewrites of fault_equivalent.py (see zxrewrites/family.py).

The builders below return (L, R, spec, defaults[, meta updates]). fault_equivalent.py uses the
template diagrams (one copy of every unit) to write the rule, and running this script afterwards
turns lhs.json / rhs.json into templates and adds the "arity" field:

    cd authoring && python fault_equivalent.py && python families_fault.py [--only=...]
"""

import json

from dsl import D, ONLY, RULES_DIR
from families import param, unit, ins, outs  # noqa: F401  (shared helpers)
from zxrewrites import graphs

FAULT_FAMILIES = {}


def fault_family(rule_id):
    def deco(fn):
        FAULT_FAMILIES[rule_id] = fn
        return fn
    return deco


# ---------------------------------------------------------------------------------------------
# Spider (un)fusion in fault-equivalent forms


@fault_family("fe-one-legged-fusion")
def fe_one_legged_fusion():
    L = D()
    z, o = L.z(1, 0), L.b(2.6, 0)
    L.e(z, o)
    R = D()
    leaf, z2, o2 = R.z(0.2, 0), R.z(1.2, 0), R.b(2.6, 0)
    R.e(leaf, z2, o2)
    spec = {"params": {"n": param("legs", 1, 4)},
            "lhs": [outs("n", o, offset=(0, 0.8))],
            "rhs": [outs("n", o2, offset=(0, 0.8))]}
    return L, R, spec, {"n": 3}, {
        "parameter_notes": "n legs on the spider (shown for n = 3); the rule holds for any n ≥ 1."}


def _hub_spiders(odd):
    """r_{2n} (odd=False) and r_{2n+} (odd=True): two hub spiders and n four-legged spiders."""
    L = D()
    zy = 0.4 if odd else 0
    z = L.z(1, zy)
    p, q = L.b(3.4, -0.25), L.b(3.4, 0.25)
    L.e(z, p).e(z, q)
    if odd:
        L.e(z, L.b(3.4, 3.0))
    R = D()
    a, b = R.z(1, -2), R.z(1, 2)
    c = R.z(2.4, 0)
    p2, q2 = R.b(3.4, -0.25), R.b(3.4, 0.25)
    R.e(a, c, b).e(c, p2).e(c, q2)
    if odd:
        R.e(b, R.b(3.4, 3.0))
    spec = {"params": {"n": param("four-legged spiders", 1, 4)},
            "lhs": [unit("n", [p, q], offset=(0, 1.3), dots_shift=[-0.35, 0])],
            "rhs": [unit("n", [c, p2, q2], offset=(0, 1.3), dots_shift=[0.5, 0])]}
    return L, R, spec


@fault_family("fe-even-spider-decomposition")
def fe_even():
    L, R, spec = _hub_spiders(False)
    return L, R, spec, {"n": 3}, {
        "parameter_notes": "A spider with 2n legs, built from two n-legged spiders and n four-legged spiders "
                           "(shown for n = 3); holds for any n ≥ 1."}


@fault_family("fe-odd-spider-decomposition")
def fe_odd():
    L, R, spec = _hub_spiders(True)
    return L, R, spec, {"n": 2}, {
        "parameter_notes": "A spider with 2n + 1 legs, built from an n-legged spider, an (n + 1)-legged spider and "
                           "n four-legged spiders (shown for n = 2); holds for any n ≥ 1."}


def _ladder(direct):
    """Fuse-n_fe (direct=False) and Fuse-n_{w-fe} (direct=True): two spiders whose (first w) legs pass
    through pairs of connected three-legged spiders (the connections are drawn as parallel diagonals)."""
    L = D()
    R = D()
    pair = dict(offset=(0, 0.8))
    if not direct:
        z = L.z(1, 2.9)
        o, o_ = L.b(4.6, 1.2), L.b(4.6, 4.6)
        L.e(z, o).e(z, o_)
        t, bb = R.z(1, 1.2), R.z(1, 4.6)
        a, b = R.z(2.2, 1.2), R.z(3.4, 4.6)
        o2, o2_ = R.b(4.6, 1.2), R.b(4.6, 4.6)
        R.e(t, a, o2).e(bb, b, o2_).e(a, b)
        spec = {"params": {"n": param("legs per half", 1, 4)},
                "lhs": [outs("n", o, offset=(0, 0.8)), outs("n", o_, offset=(0, 0.8))],
                "rhs": [unit("n", [a, o2], dots_at=o2, dots_shift=[-0.35, 0], **pair),
                        unit("n", [b, o2_], dots_at=o2_, dots_shift=[-0.35, 0], **pair)]}
        return L, R, spec
    z = L.z(1, 3.2)
    o, od, o_, od_ = L.b(4.6, 0.8), L.b(4.6, 2.4), L.b(4.6, 4.0), L.b(4.6, 5.6)
    L.e(z, o).e(z, od).e(z, o_).e(z, od_)
    t, bb = R.z(1, 1.4), R.z(1, 4.6)
    a, b = R.z(2.2, 0.8), R.z(3.4, 4.0)
    o2, od2, o2_, od2_ = R.b(4.6, 0.8), R.b(4.6, 2.4), R.b(4.6, 4.0), R.b(4.6, 5.6)
    R.e(t, a, o2).e(t, od2).e(bb, b, o2_).e(bb, od2_).e(a, b)
    spec = {"params": {"w": param("connected legs per half (w)", 1, 3),
                       "k": param("other legs per half (n − w)", 0, 2)},
            "lhs": [outs("w", o, offset=(0, 0.8)), outs("k", od, offset=(0, 0.5)),
                    outs("w", o_, offset=(0, 0.8)), outs("k", od_, offset=(0, 0.5))],
            "rhs": [unit("w", [a, o2], dots_at=o2, dots_shift=[-0.35, 0], **pair), outs("k", od2, offset=(0, 0.5)),
                    unit("w", [b, o2_], dots_at=o2_, dots_shift=[-0.35, 0], **pair), outs("k", od2_, offset=(0, 0.5))]}
    return L, R, spec


@fault_family("fe-fuse-n")
def fe_fuse_n():
    L, R, spec = _ladder(False)
    return L, R, spec, {"n": 3}, {
        "parameter_notes": "A spider with 2n legs (shown for n = 3); holds for any n ≥ 1."}


@fault_family("fe-fuse-n-w")
def fe_fuse_n_w():
    L, R, spec = _ladder(True)
    return L, R, spec, {"w": 2, "k": 1}, {
        "parameter_notes": "A spider with 2n legs, n = w + k, of which w pairs are connected (shown for w = 2, k = 1). "
                           "The rewrite is w-fault-equivalent for any w ≥ 1 and k ≥ 0."}


# ---------------------------------------------------------------------------------------------
# Fault gadgets (Rüsch, Rodatz, Kissinger)


@fault_family("fe-detect")
def fe_detect():
    def side(lhs):
        G = D()
        b1, t1 = G.b(0, 0), G.z(1.6, 0)
        G.e(b1, t1).ann(b1, t1, faultfree=True)
        bi, ti = G.b(0, 2.8), G.z(1.6, 2.8)
        G.e(bi, ti).ann(bi, ti, faultfree=True)
        gi, si = G.x(3.8, 2.8), G.z(3.8, 2.25)
        G.e(ti, gi).e(gi, si).ann(ti, gi, faultfree=True).ann(gi, si, weight="w_i")
        det = G.z(5.0, 2.8)
        G.e(gi, det).ann(gi, det, faultfree=True)
        unit_vs = [bi, ti, gi, si]
        if lhs:
            g1, s1 = G.x(3.8, 0), G.z(3.8, -0.55)
            G.e(t1, g1).e(g1, s1).e(g1, det)
            G.ann(t1, g1, faultfree=True).ann(g1, s1, weight="w_1").ann(g1, det, faultfree=True)
        else:
            ci, sci = G.x(2.4, 2.1), G.z(3.0, 2.1)
            G.e(ci, sci).e(ci, t1).e(ci, ti)
            G.ann(ci, sci, weight="w_1+w_i").ann(ci, t1, faultfree=True).ann(ci, ti, faultfree=True)
            unit_vs += [ci, sci]
        return G, unit_vs
    L, lv = side(True)
    R, rv = side(False)
    u = dict(offset=(0, 1.4), dots_shift=[0.8, 0.35])
    spec = {"params": {"m": param("other gadgets on the detector (n − 1)", 1, 3)},
            "lhs": [unit("m", lv, **u)],
            "rhs": [unit("m", rv, **u)]}
    return L, R, spec, {"m": 2}, {
        "parameter_notes": "m = n − 1 further fault gadgets are connected to the detecting spider "
                           "(shown for m = 2, i.e. n = 3 in the paper's notation); holds for any m ≥ 1."}


@fault_family("fb-copy")
def fb_copy():
    L = D()
    z, o = L.z(1.6, 0), L.b(2.8, 0)
    L.e(z, o)
    R = D()
    zs, x, o2 = R.z(0.4, 0), R.x(1.4, 0), R.b(2.8, 0)
    R.e(zs, x, o2)
    spec = {"params": {"n": param("outputs", 1, 4)},
            "lhs": [unit("n", [z, o], offset=(0, 0.8), dots_shift=[0.6, 0])],
            "rhs": [outs("n", o2, offset=(0, 0.8))]}
    return L, R, spec, {"n": 3}, {
        "parameter_notes": "n outputs (shown for n = 3); holds for any n ≥ 1."}


def main():
    for rid, fn in FAULT_FAMILIES.items():
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

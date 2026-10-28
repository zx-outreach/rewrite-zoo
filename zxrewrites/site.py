"""Static site generation (Jinja2) for the rewrite zoo."""

from __future__ import annotations

import datetime
import io
import json
import re
import shutil
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional

import pyzx
import sympy as sp
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markdown_it import MarkdownIt

from . import ROOT, export, scalars
from .bib import author_string, short_cite
from .model import FRAGMENTS, FRAGMENT_NAMES, RELATION_NAMES, RELATIONS, CALCULI
from .phases import var_display
from .pipeline import Catalogue, Processed
from .variants import SYMMETRY_NAMES, Variant

SITE_SRC = ROOT / "site"
DOMAIN_NAMES = {"real": "ℝ", "boolean": "{0, 1}", "clifford": "multiples of π/2",
                "clifford+t": "multiples of π/4", "complex": "ℂ", "integer": "ℤ"}
VIEW_NAMES = {"two-colour": "Two-colour", "gh": "GH", "graph-like": "Graph-like"}

md = MarkdownIt("commonmark", {"typographer": True}).enable("table")


_MATH = re.compile(r"\$\$(.+?)\$\$|\$(.+?)\$", re.S)


def markdown(text: str) -> str:
    """Markdown with LaTeX math kept intact for KaTeX: math segments ($...$ and $$...$$) are taken
    out before the markdown is rendered (otherwise _ becomes emphasis, \\\\ is unescaped, ...) and put
    back verbatim (HTML-escaped) afterwards."""
    import html as _html
    maths = []

    def stash(m):
        maths.append(m.group(0))
        return f"MATHSEGMENT{len(maths) - 1}X"

    out = md.render(_MATH.sub(stash, text or ""))
    return re.sub(r"MATHSEGMENT(\d+)X", lambda m: _html.escape(maths[int(m.group(1))], quote=False), out)


# ---------------------------------------------------------------------------------------------
# Scalars in exported graphs


def bake_scalar(g, s: Optional[sp.Expr]):
    """A copy of g whose global scalar is s (when s is a concrete number), for ZXLive export."""
    h = g.copy()
    if s is None or s.free_symbols:
        return h, False
    c = complex(sp.N(s))
    if abs(c) < 1e-12:
        h.scalar.is_zero = True
        return h, True
    from fractions import Fraction
    import math
    k = 2 * math.log2(abs(c))
    if abs(k - round(k)) < 1e-9:
        h.scalar.add_power(int(round(k)))
        ph = math.atan2(c.imag, c.real) / math.pi
        fr = Fraction(ph).limit_denominator(64)
        if abs(float(fr) - ph) < 1e-9:
            h.scalar.add_phase(fr)
        else:
            h.scalar.add_float(complex(math.cos(ph * math.pi), math.sin(ph * math.pi)))
    else:
        h.scalar.add_float(c)
    return h, True


# ---------------------------------------------------------------------------------------------
# Per-rule data


def exports(rule) -> Dict[str, bool]:
    """Which files can be exported for a rule: drawn-only rules only to TikZ, and the circuit side
    of a circuit rule is not a PyZX diagram."""
    checked = rule.meta.get("checked", True)
    circuit = rule.meta.get("kind") == "circuit"
    return {"lhsJson": checked and not circuit, "rhsJson": checked, "zxr": checked and not circuit}


def scalar_dict(s: Optional[sp.Expr]):
    """The PyZX scalar dict (as in Graph.to_json) representing s, or None if s is not a number."""
    g = export.graphs.new_graph()
    h, baked = bake_scalar(g, s)
    return h.scalar.to_dict() if baked else None


def zxr_text(rule, v: Variant, swap: int, validate: bool = False) -> str:
    """The ZXLive rule file for a variant (sides swapped if swap). The scalar is put in the RHS."""
    s = v.scalar
    inv = scalars.inverse(s) if s is not None else None
    if not swap:
        L, (R, baked) = v.lhs, bake_scalar(v.rhs, s)
    else:
        L, (R, baked) = v.rhs, bake_scalar(v.lhs, inv)
    desc = rule.meta.get("summary", "")
    if not baked and s is not None and not scalars.is_one(s):
        desc += " (Holds up to a scalar that depends on the parameters.)"
    text = export.zxr(rule.name, desc, L, R)
    if validate:
        try:
            export.check_zxr(text, exact=baked)
        except ValueError as e:
            raise ValueError(f"{rule.id} [{v.key}]: exported .zxr fails: {e}")
    return text


def variant_dots(rule, v: Variant):
    """The dots markers of a family instance, transformed along with the variant."""
    out = []
    for dots, g in ((rule.dots_lhs, v.lhs), (rule.dots_rhs, v.rhs)):
        ds = []
        if dots:
            rows = [g.row(x) for x in g.vertices()] or [0]
            lo, hi = min(rows), max(rows)
            for (x, y, dx, dy) in dots:
                if v.symmetry in ("transpose", "adjoint"):
                    x, dx = lo + hi - x, -dx
                ds.append([round(x, 4), round(y, 4), dx, dy])
        out.append(ds)
    return out


def variant_payload(rule, v: Variant, validate: bool = False) -> Dict[str, Any]:
    params = rule.meta.get("parameters", {})
    s = v.scalar
    inv = scalars.inverse(s) if s is not None else None
    s_tex = "" if s is None or scalars.is_one(s) else scalars.latex(s, rule.variables, params)
    inv_tex = "" if inv is None or scalars.is_one(inv) else scalars.latex(inv, rule.variables, params)
    if validate:
        for swap in (0, 1):
            zxr_text(rule, v, swap, validate=True)
    dl, dr = variant_dots(rule, v)
    lhs, rhs = export.viewer_data(v.lhs), export.viewer_data(v.rhs)
    lhs["dots"], rhs["dots"] = dl, dr
    return {
        "key": v.key,
        "view": v.view, "symmetry": v.symmetry, "colourSwapped": v.colour_swapped,
        "curated": v.curated,
        "lhs": lhs, "rhs": rhs,
        "scalar": s_tex, "invScalar": inv_tex,
        "scalarText": scalars.text(s, rule.variables, params),
        "scalarKnown": s is not None, "scalarZero": s is not None and s == 0,
        "lhsJson": v.lhs.to_json(), "rhsJson": v.rhs.to_json(),
        "zxrScalar": [scalar_dict(s), scalar_dict(inv)],
        "samples": v.result.samples if v.result else 0,
        "verified": bool(v.result and v.result.ok),
    }


def slug(key: str) -> str:
    import re
    return re.sub(r"[^A-Za-z0-9]+", "-", key).strip("-").lower()


def instance_file(key: str) -> str:
    return key.replace(",", "_").replace("=", "") + ".json"


def default_key(p: Processed) -> str:
    """The hand-drawn version of the rule."""
    curated = [v for v in p.variants if v.curated]
    for v in curated:
        if v.view == p.rule.view:
            return v.key
    return curated[0].key if curated else p.variants[0].key


def ref_entry(bib, ref) -> Dict[str, Any]:
    e = bib[ref["bib"]]
    return {**e, "location": ref.get("location", ""), "cite": short_cite(e),
            "author_str": author_string(e["authors"])}


def rule_context(p: Processed, cat: Catalogue, related: List[dict]) -> Dict[str, Any]:
    r = p.rule
    m = r.meta
    params = m.get("parameters", {})
    variables = []
    for name, spec in r.variables.items():
        uni, tex = var_display(name)
        variables.append({"name": uni, "tex": tex, "domain": DOMAIN_NAMES.get(spec["domain"], spec["domain"]),
                          "checked": [f"{v:.4g}" if isinstance(v, float) else str(v) for v in spec["values"]] if spec.get("values") else None})
    s = None
    if m.get("scalar") is not None:
        s = scalars.parse_scalar(m["scalar"], r.variables, params, evaluate=False)
    groups = {g["id"]: g for g in cat.groups}
    return {
        "id": r.id, "name": r.name, "aliases": m.get("aliases", []),
        "calculus": m["calculus"], "fragment": p.fragment, "fragment_name": FRAGMENT_NAMES[p.fragment],
        "group": groups[m["group"]],
        "summary": m.get("summary", ""), "description_html": markdown(m.get("description", "")),
        "notes_html": markdown(m.get("notes", "")) if m.get("notes") else "",
        "conditions": m.get("conditions", ""),
        "variables": variables, "parameters": params, "parameter_notes": m.get("parameter_notes", ""),
        "scalar_general": scalars.latex(s, r.variables, params) if s is not None else None,
        "scalar_side": m.get("scalar_side", "rhs"),
        "source": ref_entry(cat.bib, m["source"]),
        "also_in": [ref_entry(cat.bib, ref) for ref in m.get("also_in", [])],
        "axiom_of": [ref_entry(cat.bib, {"bib": k}) for k in m.get("axiom_of", [])],
        "related": related, "tags": m.get("tags", []),
        "view": r.view, "has_alt": r.alt_lhs is not None,
        "n_variants": len(p.variants), "n_samples": sum(v.result.samples for v in p.variants if v.result),
        "default_key": default_key(p),
        "checked": m.get("checked", True), "unchecked_reason": m.get("unchecked_reason", ""),
        "kind": m.get("kind", "equation"), "exports": exports(r),
    }


def symmetric_relations(cat: Catalogue) -> Dict[str, List[dict]]:
    names = {p.rule.id: p.rule.name for p in cat.rules}
    rel: Dict[str, Dict[str, str]] = {p.rule.id: {} for p in cat.rules}
    for p in cat.rules:
        for x in p.rule.meta.get("related", []):
            if x["id"] not in rel:
                continue
            rel[p.rule.id].setdefault(x["id"], x["relation"])
            rel[x["id"]].setdefault(p.rule.id, RELATIONS[x["relation"]])
    out = {}
    for rid, d in rel.items():
        out[rid] = sorted(({"id": k, "name": names[k], "relation": v, "relation_name": RELATION_NAMES[v]}
                           for k, v in d.items()), key=lambda x: (list(RELATIONS).index(x["relation"]), x["name"]))
    return out


# ---------------------------------------------------------------------------------------------
# Site


def tikzstyles() -> str:
    return (SITE_SRC / "static" / "zx-rewrites.tikzstyles").read_text(encoding="utf8")


def build_site(cat: Catalogue, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for child in out.iterdir():  # clear the contents (keep the directory, which may be served)
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()
    shutil.copytree(SITE_SRC / "static", out / "assets")
    (out / ".nojekyll").write_text("")

    env = Environment(loader=FileSystemLoader(SITE_SRC / "templates"),
                      autoescape=select_autoescape(["html"]), trim_blocks=True, lstrip_blocks=True)
    env.filters["json"] = lambda x: json.dumps(x, ensure_ascii=False).replace("</", "<\\/")
    built = datetime.date.today().isoformat()
    common = {"pyzx_version": pyzx.__version__, "built": built, "fragments": FRAGMENTS,
              "fragment_names": FRAGMENT_NAMES, "calculi": CALCULI, "groups": cat.groups}

    def write(path: str, template: str, depth: int, **ctx):
        f = out / path
        f.parent.mkdir(parents=True, exist_ok=True)
        root = "../" * depth
        f.write_text(env.get_template(template).render(root=root, **common, **ctx), encoding="utf8")

    related = symmetric_relations(cat)
    rules_sorted = sorted(cat.rules, key=lambda p: (
        [g["id"] for g in cat.groups].index(p.rule.meta["group"]), p.rule.meta.get("order", 100), p.rule.name))
    contexts = {}
    payloads = {}
    index_entries = []
    all_zip = io.BytesIO()
    zxl_zip = io.BytesIO()
    with zipfile.ZipFile(all_zip, "w", zipfile.ZIP_DEFLATED) as zall, \
            zipfile.ZipFile(zxl_zip, "w", zipfile.ZIP_DEFLATED) as zzxl:
        for p in rules_sorted:
            r = p.rule
            ctx = rule_context(p, cat, related[r.id])
            contexts[r.id] = ctx
            # the .zxr export is checked the way ZXLive does for the rule as stated in every view (the other
            # variants are verified already; this checks the export format and the scalar baking)
            ex = exports(r)
            payload = {v.key: variant_payload(r, v, validate=ex["zxr"] and v.symmetry == "id" and not v.colour_swapped)
                       for v in p.variants}
            dk = default_key(p)
            d = payload[dk]
            vmap = {v.key: v for v in p.variants}

            def hb(v):
                return v.view == "two-colour"

            def tikz_eq(v):
                return export.tikz_equation(v.lhs, v.rhs, payload[v.key]["scalar"], "rhs", hb(v),
                                            dots=variant_dots(r, v))
            index_entries.append({
                "id": r.id, "name": r.name, "aliases": ctx["aliases"], "calculus": ctx["calculus"],
                "fragment": p.fragment, "group": r.meta["group"], "summary": ctx["summary"],
                "tags": ctx["tags"], "cite": ctx["source"]["cite"], "year": ctx["source"]["year"],
                "lhs": d["lhs"], "rhs": d["rhs"], "scalar": d["scalar"], "scalarText": d["scalarText"],
                "hboxes": d["view"] == "two-colour",
                "alternative_of": r.meta.get("alternative_of"),
                "any_arity": r.is_family,
                "checked": r.meta.get("checked", True), "kind": r.meta.get("kind", "equation"),
            })
            # static downloads for the default variant + a zip with every variant
            dl = out / "downloads" / r.id
            dl.mkdir(parents=True, exist_ok=True)
            meta_txt = json.dumps(r.meta, indent=2, ensure_ascii=False)
            (dl / "meta.json").write_text(meta_txt, encoding="utf8")
            if ex["lhsJson"]:
                (dl / "lhs.json").write_text(d["lhsJson"], encoding="utf8")
            if ex["rhsJson"]:
                (dl / "rhs.json").write_text(d["rhsJson"], encoding="utf8")
            if ex["zxr"]:
                (dl / f"{r.id}.zxr").write_text(zxr_text(r, vmap[dk], 0), encoding="utf8")
            (dl / f"{r.id}.tikz").write_text(tikz_eq(vmap[dk]), encoding="utf8")
            zbuf = io.BytesIO()
            with zipfile.ZipFile(zbuf, "w", zipfile.ZIP_DEFLATED) as z:
                z.writestr(f"{r.id}/meta.json", meta_txt)
                z.writestr(f"{r.id}/zx-rewrites.tikzstyles", tikzstyles())
                for key, v in payload.items():
                    folder = f"{r.id}/variants/" + key.replace("|", "_")
                    if key == dk:
                        folder = f"{r.id}"
                    if ex["lhsJson"]:
                        z.writestr(f"{folder}/lhs.json", v["lhsJson"])
                    if ex["rhsJson"]:
                        z.writestr(f"{folder}/rhs.json", v["rhsJson"])
                    vv = vmap[key]
                    if ex["zxr"]:
                        z.writestr(f"{folder}/{r.id}.zxr", zxr_text(r, vv, 0))
                    z.writestr(f"{folder}/equation.tikz", tikz_eq(vv))
                    z.writestr(f"{folder}/lhs.tikz", export.tikz(vv.lhs, hb(vv)))
                    z.writestr(f"{folder}/rhs.tikz", export.tikz(vv.rhs, hb(vv)))
            (dl / f"{r.id}.zip").write_bytes(zbuf.getvalue())
            zall.writestr(f"zx-rewrites/{r.id}/meta.json", meta_txt)
            if ex["lhsJson"]:
                zall.writestr(f"zx-rewrites/{r.id}/lhs.json", d["lhsJson"])
            if ex["rhsJson"]:
                zall.writestr(f"zx-rewrites/{r.id}/rhs.json", d["rhsJson"])
            if ex["zxr"]:
                zall.writestr(f"zx-rewrites/{r.id}/{r.id}.zxr", zxr_text(r, vmap[dk], 0))
                zzxl.writestr(f"zx-rewrites/{r.meta['calculus']}/{r.meta['group']}/{r.id}.zxr", zxr_text(r, vmap[dk], 0))
            zall.writestr(f"zx-rewrites/{r.id}/{r.id}.tikz", tikz_eq(vmap[dk]))
            # other arities of a family rule: one JSON file per instance, loaded on demand
            if p.instances:
                idir = out / "rules" / r.id / "instances"
                idir.mkdir(parents=True, exist_ok=True)
                for ikey, (inst, ivs) in p.instances.items():
                    ipay = payload if inst is r else {v.key: variant_payload(inst, v) for v in ivs}
                    (idir / (instance_file(ikey))).write_text(json.dumps(ipay, ensure_ascii=False), encoding="utf8")
            payloads[r.id] = payload
        zall.writestr("zx-rewrites/zx-rewrites.tikzstyles", tikzstyles())
    (out / "downloads" / "zx-rewrites-all.zip").write_bytes(all_zip.getvalue())
    (out / "downloads" / "zx-rewrites-zxlive.zip").write_bytes(zxl_zip.getvalue())
    shutil.copy(SITE_SRC / "static" / "zx-rewrites.tikzstyles", out / "downloads" / "zx-rewrites.tikzstyles")

    # alternative representations are shown on the page of the rule they are an alternative of
    by_id = {e["id"]: e for e in index_entries}
    alts: Dict[str, List[dict]] = {}
    for e in index_entries:
        if e["alternative_of"]:
            alts.setdefault(e["alternative_of"], []).append(e)
    for parent, es in alts.items():
        by_id[parent]["alt_names"] = [x["name"] for x in es] + [a for x in es for a in x["aliases"]]
    # "axiom of": from the completeness tables (data/axiomatisations*.json) and from meta.json
    ax_papers = {a["bib"] for a in cat.axiomatisations}
    derived: Dict[str, Dict[str, List[str]]] = {}
    for paper in cat.axiomatisations:
        for res in paper["results"]:
            for ax in res["axioms"]:
                if ax.get("rule"):
                    labels = derived.setdefault(ax["rule"], {}).setdefault(paper["bib"], [])
                    if ax.get("label") and ax["label"] not in labels:
                        labels.append(ax["label"])
    axiom_keys: Dict[str, List[str]] = {}
    for p in rules_sorted:
        rid = p.rule.id
        keys = list(p.rule.meta.get("axiom_of", []))
        keys += [k for k in derived.get(rid, {}) if k not in keys]
        keys.sort(key=lambda k: (cat.bib[k]["year"], k))
        axiom_keys[rid] = keys
        contexts[rid]["axiom_of"] = [dict(ref_entry(cat.bib, {"bib": k}), labels=derived.get(rid, {}).get(k, []),
                                          completeness=slug(k) if k in ax_papers else None) for k in keys]

    for p in rules_sorted:
        r = p.rule
        ctx = contexts[r.id]
        ctx["alternatives"] = [dict(e, fragment_name=FRAGMENT_NAMES[e["fragment"]]) for e in alts.get(r.id, [])]
        parent = r.meta.get("alternative_of")
        ctx["alternative_of"] = {"id": parent, "name": contexts[parent]["name"]} if parent in contexts else None
        arity = None
        if r.is_family:
            from . import family
            arity = {"params": family.params_of(r.meta), "values": dict(r.instance_values),
                     "defaultKey": family.instance_key(r.instance_values),
                     "files": {k: instance_file(k) for k in p.instances}}
        write(f"rules/{r.id}/index.html", "rule.html", 2, rule=ctx, variants=payloads[r.id],
              alternatives=ctx["alternatives"], arity=arity, title=r.name)
    n_all = len(index_entries)
    index_entries_all = index_entries
    index_entries = [e for e in index_entries if not e["alternative_of"]]

    # groups
    by_group: Dict[str, List[dict]] = {g["id"]: [] for g in cat.groups}
    for e in index_entries:
        by_group[e["group"]].append(e)
    groups_ctx = [dict(g, rules=by_group[g["id"]]) for g in cat.groups if by_group[g["id"]]]
    for g in groups_ctx:
        write(f"groups/{g['id']}/index.html", "group.html", 2, group=g, title=g["name"], toc=groups_ctx,
              rules_full=[contexts[e["id"]] for e in g["rules"]])

    # papers
    papers: Dict[str, dict] = {}

    def add_paper(key, rid, role):
        e = cat.bib[key]
        pp = papers.setdefault(key, {**e, "cite": short_cite(e), "author_str": author_string(e["authors"]),
                                     "roles": {"source": [], "also": [], "axiom": []}})
        if rid not in [x["id"] for x in pp["roles"][role]]:
            pp["roles"][role].append({"id": rid, "name": contexts[rid]["name"]})

    for p in cat.rules:
        m = p.rule.meta
        add_paper(m["source"]["bib"], p.rule.id, "source")
        for ref in m.get("also_in", []):
            add_paper(ref["bib"], p.rule.id, "also")
        for k in axiom_keys[p.rule.id]:
            add_paper(k, p.rule.id, "axiom")
    papers_sorted = sorted(papers.values(), key=lambda x: (x["year"], x["cite"]))
    write("papers/index.html", "papers.html", 1, papers=papers_sorted, title="Papers")

    entry_by_id = {e["id"]: e for e in index_entries_all}
    comp = []
    for paper in cat.axiomatisations:
        e = cat.bib[paper["bib"]]
        results = []
        for res in paper["results"]:
            rows = []
            for ax in res["axioms"]:
                rid = ax.get("rule")
                rows.append(dict(ax, entry=entry_by_id.get(rid) if rid else None,
                                 rule_name=contexts[rid]["name"] if rid in contexts else None))
            results.append(dict(res, rows=rows, fragment_name=FRAGMENT_NAMES.get(res.get("fragment", ""), ""),
                                n_in_zoo=sum(1 for x in rows if x["entry"]), anchor=slug(res["title"])))
        comp.append({**e, "cite": short_cite(e), "author_str": author_string(e["authors"]), "slug": slug(paper["bib"]),
                     "results": results})
    comp.sort(key=lambda x: (x["year"], x["cite"]))
    for c in comp:
        write(f"completeness/{c['slug']}/index.html", "completeness.html", 2, paper=c, title=f"Completeness: {c['cite']}",
              thumbs=[r["entry"] for res in c["results"] for r in res["rows"] if r["entry"]])
    write("completeness/index.html", "completeness_index.html", 1, papers=comp, title="Complete axiomatisations")
    write("about/index.html", "about.html", 1, title="About & conventions")
    write("index.html", "index.html", 0, entries=index_entries, groups_ctx=groups_ctx,
          n_rules=n_all, n_variants=sum(len(p.variants) for p in cat.rules),
          n_papers=len(papers))

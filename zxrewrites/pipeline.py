"""Load, validate and verify the whole catalogue."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from . import graphs, model, variants as V
from .bib import load_bib
from .fragment import infer_fragment
from .model import Rule


@dataclass
class Processed:
    rule: Rule
    variants: List[V.Variant] = field(default_factory=list)
    fragment: str = ""
    errors: List[str] = field(default_factory=list)
    # for families: instance key -> (instance rule, variants); the default instance is p.rule itself
    instances: Dict[str, tuple] = field(default_factory=dict)


@dataclass
class Catalogue:
    rules: List[Processed]
    groups: List[dict]
    bib: Dict[str, dict]
    axiomatisations: List[dict] = field(default_factory=list)


def verify_instances(p: Processed, full: bool) -> List[str]:
    """Generate every arity instance of a family rule. Each instance is verified in every view as
    stated (the symmetric variants follow by construction and are verified for the default)."""
    from . import family
    errors = []
    r = p.rule
    default = family.instance_key(r.instance_values)
    for values in family.all_instances(r.meta):
        key = family.instance_key(values)
        if key == default:
            p.instances[key] = (r, p.variants)
            continue
        try:
            inst = family.make_instance(r, values)
            vs = V.compute_variants(inst)
        except Exception as e:
            errors.append(f"instance {key}: could not be generated: {e!r}")
            continue
        p.instances[key] = (inst, vs)
        if not full:
            continue
        # the other views and symmetries are obtained by transformations that are verified for the
        # default instance; here every instance is checked as drawn (exact scalar included)
        check = [v for v in vs if v.curated] or [v for v in vs if v.symmetry == "id" and not v.colour_swapped][:1]
        errs = V.verify_variants(inst, check, full=True, n_random=2)
        errors += [f"instance {key}: {e}" for e in errs]
    return errors


def process_all(only: Optional[Set[str]] = None, full: bool = True) -> Tuple[Catalogue, List[str]]:
    bib = load_bib()
    groups = model.load_groups()
    group_ids = {g["id"]: g for g in groups}
    errors: List[str] = []
    all_ids = set(model.rule_ids())
    out = []
    for rid in sorted(all_ids):
        if only and rid not in only:
            continue
        try:
            r = model.load_rule(model.RULES_DIR / rid)
        except model.RuleError as e:
            errors.append(str(e))
            continue
        p = Processed(rule=r)
        p.errors += model.validate_meta(r, group_ids, bib, all_ids)
        checked = r.meta.get("checked", True)
        kind = r.meta.get("kind", "equation")
        if not checked:
            # only drawn: no structural or semantic checks
            p.fragment = r.meta.get("fragment", "universal")
            p.variants = V.unchecked_variants(r)
            errors += [f"{r.id}: {e}" for e in p.errors]
            out.append(p)
            continue
        sides = (("lhs", r.lhs), ("rhs", r.rhs), ("alt/lhs", r.alt_lhs), ("alt/rhs", r.alt_rhs))
        if kind == "circuit":
            sides = (("rhs", r.rhs),)
            if "circuit" not in r.meta:
                p.errors.append("circuit rules need a 'circuit' field")
        for side, g in sides:
            if g is None:
                continue
            p.errors += [f"{side}: {m}" for m in graphs.structural_problems(g)]
        if kind == "circuit" and not p.errors:
            p.fragment = infer_fragment(r, r.rhs, r.rhs)
            if r.meta.get("fragment") != p.fragment:
                p.errors.append(f"fragment is declared as '{r.meta.get('fragment')}' but the diagram lives in '{p.fragment}'")
            try:
                p.variants = V.circuit_variants(r)
                p.errors += V.verify_circuit(r, p.variants)
            except Exception as e:
                import traceback
                p.errors.append(f"exception while verifying: {e!r} " + traceback.format_exc())
            errors += [f"{r.id}: {e}" for e in p.errors]
            out.append(p)
            continue
        declared = set(r.variables)
        used = set(graphs.variables(r.lhs)) | set(graphs.variables(r.rhs))
        for name in used - declared:
            p.errors.append(f"variable '{name}' is used but not declared in meta.json 'variables'")
        for name, is_bool in {**graphs.variables(r.lhs), **graphs.variables(r.rhs)}.items():
            dom = r.variables.get(name, {}).get("domain")
            if dom and (dom == "boolean") != is_bool:
                p.errors.append(f"variable '{name}' has domain '{dom}' but is_bool={is_bool} in the JSON "
                                "(boolean variables must be marked in 'variable_types')")
        if not p.errors:
            two = V.base_views(r).get("two-colour", (r.lhs, r.rhs, True))
            p.fragment = infer_fragment(r, two[0], two[1])
            if r.meta.get("fragment") != p.fragment:
                p.errors.append(f"fragment is declared as '{r.meta.get('fragment')}' but the rule lives in "
                                f"'{p.fragment}'")
            try:
                p.variants = V.compute_variants(r)
                p.errors += V.verify_variants(r, p.variants, full=full)
                if r.is_family:
                    p.errors += verify_instances(p, full)
            except Exception as e:  # report instead of crashing the whole build
                import traceback
                p.errors.append(f"exception while verifying: {e!r}\n{traceback.format_exc()}")
        errors += [f"{r.id}: {e}" for e in p.errors]
        out.append(p)
    axs = model.load_axiomatisations()
    for paper in axs:
        if paper["bib"] not in bib:
            errors.append(f"axiomatisations: unknown bib key '{paper['bib']}'")
        for res in paper["results"]:
            for ax in res["axioms"]:
                if ax.get("rule") and ax["rule"] not in all_ids:
                    errors.append(f"axiomatisations: {paper['bib']} {ax.get('label')}: unknown rule '{ax['rule']}'")
    return Catalogue(out, groups, bib, axs), errors

"""Loading and validating the rule catalogue (rules/<id>/{meta.json, lhs.json, rhs.json})."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from pyzx.graph.base import BaseGraph

from . import RULES_DIR, DATA_DIR
from . import graphs

CALCULI = ["ZX", "ZH", "ZW"]
# Fragments are hierarchical: each one includes all the previous ones.
FRAGMENTS = ["phase-free", "pauli", "clifford", "clifford+t", "universal"]
FRAGMENT_NAMES = {
    "phase-free": "Phase-free", "pauli": "Pauli", "clifford": "Clifford",
    "clifford+t": "Clifford+T", "universal": "Universal",
}
VIEWS = ["two-colour", "graph-like"]
DOMAINS = ["boolean", "clifford", "clifford+t", "real", "complex", "integer"]

# Relations between rules, and their inverse (used to make the relation graph symmetric).
RELATIONS = {
    "variant-of": "variant-of",
    "special-case-of": "generalises",
    "generalises": "special-case-of",
    "derived-from": "used-to-derive",
    "used-to-derive": "derived-from",
    "equivalent-to": "equivalent-to",
    "see-also": "see-also",
}
RELATION_NAMES = {
    "variant-of": "Variant of", "special-case-of": "Special case of", "generalises": "Generalises",
    "derived-from": "Derived from", "used-to-derive": "Used to derive",
    "equivalent-to": "Equivalent to", "see-also": "See also",
}

REQUIRED = ["id", "name", "calculus", "fragment", "group", "summary", "description", "source"]
KNOWN_KEYS = set(REQUIRED) | {
    "aliases", "variables", "parameters", "parameter_notes", "scalar", "scalar_side",
    "also_in", "related", "axiom_of", "tags", "notes", "view", "conditions", "order", "alternative_of", "arity", "checked", "unchecked_reason", "kind", "circuit",
}


class RuleError(Exception):
    pass


@dataclass
class Rule:
    meta: Dict[str, Any]
    path: Path
    lhs: BaseGraph
    rhs: BaseGraph
    # An optional hand-curated second view (the other one of VIEWS).
    alt_lhs: Optional[BaseGraph] = None
    alt_rhs: Optional[BaseGraph] = None
    errors: List[str] = field(default_factory=list)
    # for rules with an arbitrary number of legs (see family.py)
    template_lhs: Optional[BaseGraph] = None
    template_rhs: Optional[BaseGraph] = None
    dots_lhs: List = field(default_factory=list)
    dots_rhs: List = field(default_factory=list)
    var_override: Optional[Dict[str, Dict[str, Any]]] = None
    instance_values: Optional[Dict[str, int]] = None

    @property
    def is_family(self) -> bool:
        return self.template_lhs is not None

    @property
    def template_variables(self) -> Dict[str, Dict[str, Any]]:
        out = {}
        for k, v in self.meta.get("variables", {}).items():
            out[k] = {"domain": v} if isinstance(v, str) else dict(v)
        return out

    @property
    def id(self) -> str:
        return self.meta["id"]

    @property
    def name(self) -> str:
        return self.meta["name"]

    @property
    def view(self) -> str:
        return self.meta.get("view", "two-colour")

    @property
    def alt_view(self) -> str:
        return VIEWS[1 - VIEWS.index(self.view)]

    @property
    def variables(self) -> Dict[str, Dict[str, Any]]:
        if self.var_override is not None:
            return self.var_override
        return self.template_variables


def load_rule(d: Path) -> Rule:
    meta_path = d / "meta.json"
    try:
        meta = json.loads(meta_path.read_text(encoding="utf8"))
    except Exception as e:  # pragma: no cover - reported to the user
        raise RuleError(f"{meta_path}: invalid JSON: {e}")
    try:
        lhs = graphs.load(d / "lhs.json")
        rhs = graphs.load(d / "rhs.json")
    except Exception as e:
        raise RuleError(f"{d}: could not load lhs/rhs: {e}")
    alt_lhs = alt_rhs = None
    if (d / "alt" / "lhs.json").exists():
        alt_lhs = graphs.load(d / "alt" / "lhs.json")
        alt_rhs = graphs.load(d / "alt" / "rhs.json")
    rule = Rule(meta=meta, path=d, lhs=lhs, rhs=rhs, alt_lhs=alt_lhs, alt_rhs=alt_rhs)
    from . import family
    if family.is_family(meta):
        rule.template_lhs, rule.template_rhs = lhs, rhs
        try:
            inst = family.make_instance(rule, family.default_values(meta))
        except Exception as e:
            raise RuleError(f"{d}: could not instantiate the arity template: {e}")
        return inst
    return rule


def rule_ids(rules_dir: Path = RULES_DIR) -> List[str]:
    return sorted(p.name for p in rules_dir.iterdir() if p.is_dir() and (p / "meta.json").exists())


def load_rules(rules_dir: Path = RULES_DIR, only=None) -> List[Rule]:
    return [load_rule(rules_dir / i) for i in rule_ids(rules_dir) if not only or i in only]


def load_groups() -> List[Dict[str, Any]]:
    """data/groups.json, followed by any additional data/groups-*.json files."""
    groups = json.loads((DATA_DIR / "groups.json").read_text(encoding="utf8"))
    seen = {g["id"] for g in groups}
    for extra in sorted(DATA_DIR.glob("groups-*.json")):
        for g in json.loads(extra.read_text(encoding="utf8")):
            if g["id"] in seen:
                raise RuleError(f"{extra.name}: duplicate group id '{g['id']}'")
            seen.add(g["id"])
            groups.append(g)
    return groups


def validate_meta(rule: Rule, groups: Dict[str, Any], bib: Dict[str, Any], all_ids: set) -> List[str]:
    m = rule.meta
    errs = []
    for k in REQUIRED:
        if k not in m:
            errs.append(f"missing required field '{k}'")
    for k in m:
        if k not in KNOWN_KEYS:
            errs.append(f"unknown field '{k}'")
    if m.get("id") != rule.path.name:
        errs.append(f"id '{m.get('id')}' does not match directory name '{rule.path.name}'")
    if m.get("calculus") not in CALCULI:
        errs.append(f"calculus must be one of {CALCULI}")
    if m.get("fragment") not in FRAGMENTS:
        errs.append(f"fragment must be one of {FRAGMENTS}")
    if m.get("group") not in groups:
        errs.append(f"unknown group '{m.get('group')}'")
    if m.get("view", "two-colour") not in VIEWS:
        errs.append(f"view must be one of {VIEWS}")
    if m.get("scalar_side", "rhs") not in ("lhs", "rhs"):
        errs.append("scalar_side must be 'lhs' or 'rhs'")
    for name, spec in rule.variables.items():
        if spec.get("domain") not in DOMAINS:
            errs.append(f"variable '{name}' has unknown domain '{spec.get('domain')}'")

    def check_ref(ref, where):
        if not isinstance(ref, dict) or "bib" not in ref:
            errs.append(f"{where}: must be an object with a 'bib' key")
        elif ref["bib"] not in bib:
            errs.append(f"{where}: unknown bib key '{ref['bib']}'")

    if "source" in m:
        check_ref(m["source"], "source")
    for i, ref in enumerate(m.get("also_in", [])):
        check_ref(ref, f"also_in[{i}]")
    for key in m.get("axiom_of", []):
        if key not in bib:
            errs.append(f"axiom_of: unknown bib key '{key}'")
    if "alternative_of" in m and m["alternative_of"] not in all_ids:
        errs.append(f"alternative_of: unknown rule id '{m['alternative_of']}'")
    for rel in m.get("related", []):
        if rel.get("id") not in all_ids:
            errs.append(f"related: unknown rule id '{rel.get('id')}'")
        if rel.get("relation") not in RELATIONS:
            errs.append(f"related: unknown relation '{rel.get('relation')}' (one of {list(RELATIONS)})")
    return errs


def load_axiomatisations() -> List[Dict[str, Any]]:
    """data/axiomatisations*.json: for each completeness paper, its complete rule sets."""
    out: List[Dict[str, Any]] = []
    seen = {}
    for f in sorted(DATA_DIR.glob("axiomatisations*.json")):
        for paper in json.loads(f.read_text(encoding="utf8")):
            if paper["bib"] in seen:
                seen[paper["bib"]]["results"] += paper["results"]
            else:
                seen[paper["bib"]] = paper
                out.append(paper)
    return out

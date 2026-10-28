# Authoring rules

The canonical data of the zoo lives in `rules/<id>/`:

| file | content |
|---|---|
| `meta.json` | metadata (see below) |
| `lhs.json`, `rhs.json` | the two sides as PyZX graph JSON (multigraph backend), in the view given by `meta.view` |
| `alt/lhs.json`, `alt/rhs.json` | optional hand-made version of the *other* view (two-colour ↔ graph-like) |

The JSON files can be produced in any way, for instance by drawing them in ZXLive and saving them.
The Python scripts in this directory are what was used to write the initial data. They use the
small DSL in `dsl.py`. Running a script never overwrites an existing rule unless `--force` is passed,
and `--only=id1,id2` restricts it to some rules:

    cd authoring && python zx_basic.py --force --only=spider-fusion

Afterwards, verify with `python build.py --check --only=spider-fusion` from the project root.

## Conventions for diagrams

* Coordinates: `x` is the PyZX *row* (left → right), `y` is the PyZX *qubit* (top → bottom).
* Boundaries must have exactly one neighbour. A boundary is an **input** if its neighbour lies to its right, and an **output** if its neighbour lies to its left. They may not be in the same column. This is how ZXLive determines inputs and outputs.
* Inputs and outputs are matched between LHS and RHS by their vertical order (the `y` coordinate). So the i-th input from the top on the left-hand side corresponds to the i-th input from the top on the right-hand side.
* **ZX rules**: Hadamard gates are written as Hadamard edges (`D.he`). Do not use H-boxes in ZX rules: PyZX H-boxes are *unnormalised*, being ZH H-boxes. The site draws Hadamard edges as yellow boxes in the two-colour view.
* **ZH rules**: `D.h(x, y)` is an H-box with the standard label −1. Use `D.h(x, y, phase="alpha")` for label e^{iα}, or `D.h(x, y, label="a")` / `label=0.5` for arbitrary complex labels. Write products as `a⋅b` (the PyZX parser drops `*`).
* **ZW rules**: `w_out, w_in = D.w(x, y)` creates a W-node. Its single special leg attaches to `w_in`; all other legs attach to `w_out`.
* Phases are in units of π: `"1/2"` is π/2, and `"alpha"` is the angle α. Boolean variables (phase aπ, a ∈ {0, 1}) must be declared with `D(bools="a b")` *and* `"variables": {"a": "boolean"}`.
* Variable names must be ASCII (`alpha`, `beta1`, `gamma`, `a`, `j`); they are displayed as α, β₁, γ ….
* Avoid layouts where an edge passes through a node, or where several edges lie on top of each other (e.g. complete graphs on collinear nodes). Leave boundary legs long enough (about 1 unit) for a Hadamard box to fit.
* A rule that holds for any number of legs is stored as one representative instance. The number of legs goes in `parameters` (e.g. `{"n": 3}`), and `parameter_notes` explains it.

## meta.json

| field | |
|---|---|
| `id` | the directory name (kebab-case) |
| `name`, `aliases` | display name, and other names under which the rule is known (searchable) |
| `calculus` | `ZX`, `ZH` or `ZW` |
| `fragment` | `phase-free`, `pauli`, `clifford`, `clifford+t` or `universal`: the *smallest* fragment containing the rule. The build computes it and fails if this disagrees. |
| `group` | id of a group in `data/groups.json` (or a `data/groups-*.json`) |
| `order` | position within the group (optional) |
| `view` | `two-colour` (default) or `graph-like`: the view of `lhs.json`/`rhs.json` |
| `summary` | one sentence |
| `description` | markdown; `$…$` is rendered with KaTeX; links to other rules as `[name](../<id>/)` |
| `variables` | `{"alpha": "real", "a": "boolean", "x": "complex", ...}`. Domains: `real`, `boolean`, `clifford`, `clifford+t`, `complex`, `integer`. Use `{"domain": "real", "values": ["1/4", "3/4"]}` to check only specific values. |
| `parameters`, `parameter_notes` | arity parameters of the stored instance |
| `conditions` | text describing side conditions, if any |
| `scalar` | sympy expression `s` such that **LHS = s · RHS** exactly. Phase variables denote angles in radians, so a phase `alpha` gives `exp(I*alpha)`. Booleans are 0/1; parameters are integers. In the authoring scripts `"auto"` computes a constant scalar numerically. |
| `scalar_side` | `rhs` (default) or `lhs`: on which side the source paper writes the scalar |
| `source` | `{"bib": key, "location": "Fig. 2, rule (S1)"}`: the paper where the rule first appeared |
| `also_in` | list of further `{"bib", "location"}` references |
| `axiom_of` | normally left out: which complete axiomatisations a rule belongs to is derived from `data/axiomatisations*.json`. Use it only for papers that have no table there. |
| `alternative_of` | id of a rule of which this one is merely an alternative representation (e.g. the form needed for one particular completeness paper). Such rules are not listed on the main page, but are shown on the page of the other rule. |
| `arity` | for rules that hold for any number of legs: see below |
| `related` | list of `{"id": other-rule, "relation": ...}`. Relations: `variant-of`, `special-case-of`, `generalises`, `derived-from`, `used-to-derive`, `equivalent-to`, `see-also`. The inverse relation is added automatically. |
| `tags`, `notes` | keywords for search; free-form markdown notes |

Bibliography keys come from `data/zx-papers.bib`, the zxcalculus.com publication list. Papers missing from it go in another `.bib` file in `data/`; entries there override those in `zx-papers.bib`.

## Rules with an arbitrary number of legs

For such rules, `lhs.json` and `rhs.json` are *templates* in which each repeatable part appears exactly once. The `arity` field of `meta.json` describes these parts, called units. The full format is documented in `zxrewrites/family.py`. A minimal example, spider fusion with n inputs and m outputs:

```json
"arity": {
  "params": {"n": {"label": "inputs", "min": 0, "max": 4}, "m": {"label": "outputs", "min": 0, "max": 4}},
  "lhs": [{"param": "n", "vertices": [0], "offset": [0, 1], "dots_shift": [0.35, 0]},
          {"param": "m", "vertices": [3], "offset": [0, 1], "dots_shift": [-0.35, 0]}],
  "rhs": [...]
},
"parameters": {"n": 2, "m": 2}
```

- `parameters` gives the default instance shown on the site, with `⋯` between the copies.
- The scalar may depend on the parameters.
- Every instance in the given ranges is generated and verified when the site is built.
- `authoring/families.py` writes these templates.

## Complete axiomatisations

`data/axiomatisations*.json` lists, for each completeness paper, its complete rule sets. Each axiom has its label in the paper and the id of the matching rule, or `null` with a description when the zoo does not contain it. The build checks that every referenced rule exists. From these files it generates the completeness pages and the "axiom in" links on rule pages.

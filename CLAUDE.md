I want to make an interactive overview of all the known useful ZX-calculus rewrites.
Think Quantum Error Correction Zoo or something like https://qecdb.org/ but for ZX.

It should have the following features:

* Categories of rewrites based on calculus type (ZX, ZH, ZW) and fragment (Phase-free, Clifford, Clifford+T, universal).
* Similar rewrites should be grouped together in intuitive ways (the different variants of local complementation go together for instance).
* You should be able to search by name.
* For each rewrite we should present different formats based on whether we want the rewrite to be graph-like, or with regular X- and Z-spiders.
* The rewrite should be downloadable in several formats: as tikz, as ZX json for the left-hand side and right-hand side, and as a ZXLive rule file.
* For now we will focus just on standard qubit ZX, no other variants, no scalable ZX.

I want the website to be static, generated from the structural ZX data by a Python script. If this makes sense, this can be combined with Jekyll for the static webpage generation. I want this website to be hosted for now as a Github Page, so it should be compatible with that.

The source of the rewrites can be found by looking at the papers on https://zxcalculus.com/publications.html. Specifically those with the keyword Completeness will be a good source of rewrites. Skip the non-qubit ones for now. The cheatsheets chapter of my book would also be useful: https://zxcalc.github.io/book/html/main_htmlch8.html#cheatsheets. 
When possible, look at the tex source on arxiv of these papers to find the raw tikz files of the rewrites.

For each rewrite, the raw data should be stored as PyZX json-style objects. Verify directly using PyZX that the semantics of the rewrite rule are indeed correct, make this part of the static website generation. For each rewrite have an additional json file storing the relevant metadata: what is the first paper where this appeared (title, authors, arxiv link, journal link, year), a textual description of what the rewrite does, which fragment it belongs to, what calculus it belongs to, to which other rewrites it is related.

Before making the website, make a plan below and report back to me.

---

# Plan (drafted 2026-10-19, awaiting approval)

## 0. Findings from initial research
- **Tooling available locally**: Python 3.13, PyZX 0.10.7, Ruby + Jekyll 4.4 + Bundler. ZXLive is not installed, but we only need its file format.
- **PyZX covers everything we need**:
  - Vertex types BOUNDARY, Z, X, H_BOX, W_INPUT/W_OUTPUT and Z_BOX can all be tensor-evaluated, so ZX, ZH and ZW rules can all be verified.
  - It supports symbolic phases, `to_json`/`from_json` (version-2 format), `to_tikz` (TikZiT style), `compare_tensors` and `find_scalar_correction`.
  - Still to check: how far PyZX supports arbitrary *complex* H-box labels, which ZH rules such as "average" need. If the support is insufficient, I will write a small tensor evaluator of our own for those.
- **ZXLive `.zxr` format**: JSON `{"name", "description", "lhs_graph", "rhs_graph"}`. The two graphs are *JSON strings* of PyZX graph JSON, using the `multigraph` backend with auto-simplify off.
  - ZXLive re-detects inputs and outputs from positions. Each boundary must have degree 1. It is an input if its neighbour is to the right and an output if its neighbour is to the left, and boundaries are ordered by qubit. Our data must follow this convention.
  - ZXLive's own correctness check demands *exact* equality, scalar included.
- **Sources**:
  - zxcalculus.com tags about 17 qubit papers from 2023–2026 with "Completeness". I could only read the page partially, because it is about 750 kB.
  - Older key papers are needed too; I will verify each of them on arXiv:
    - Backens 2014 (Clifford completeness)
    - Jeandel–Perdrix–Vilmart 2017/2018 (Clifford+T and universal)
    - Ng–Wang 2017
    - Vilmart 2018 (near-minimal axiomatisation)
    - Backens–Kissinger 2018 and the 2021 ZH completeness paper
    - Hadzihasanovic's ZW papers
    - Duncan–Perdrix and Duncan–Kissinger–Perdrix–van de Wetering 2019 (local complementation/pivoting)
    - Kissinger–van de Wetering 2019 (phase gadgets)
    - Carette et al. on the planar ZW fragment
    - Clément–Delorme–Perdrix–Vilmart on circuits
  - Book ch. 8 tables 8.1/8.2 give the basic and derived rules as text. The full ZX cheatsheet and the H-box cheatsheet there are images, so I would use the book's LaTeX source for those.

## 1. Repository layout
```
rules/                              # source of truth, hand-curated
  zx/spider/spider-fusion/
    meta.json                       # metadata (schema below)
    two-colour/lhs.json, rhs.json   # PyZX graph JSON: Z/X spiders, plain edges
    graph-like/lhs.json, rhs.json   # optional: Z spiders + Hadamard edges
  zx/local-complementation/lc-internal/ ...
  zh/... , zw/...
papers.json                         # bibliography registry, keyed e.g. "jpv2018"
groups.json                         # groups: id, title, blurb, order, calculus
zxrewrites/                         # Python package (build tooling)
  model.py     load + JSON-schema-validate rules
  verify.py    semantic verification with PyZX
  convert.py   two-colour <-> graph-like, colour-swap / adjoint variants
  fragment.py  infer fragment from phases, cross-check meta.json
  render.py    own SVG renderer (book-style colours, light/dark)
  export.py    tikz (+ .tikzstyles), lhs/rhs JSON, .zxr, zip bundles
  importers/   one-off helpers: arXiv tikz -> PyZX via pyzx.tikz
build.py                            # verify everything, then emit the site
site/                               # templates, css, js; generated output git-ignored
tests/                              # pytest: every rule verifies, schemas, round-trips
.github/workflows/pages.yml         # CI: pip install -> build.py -> deploy to Pages
```

## 2. Data model
**Graphs.** Use PyZX version-2 JSON on the `multigraph` backend. Positions follow ZXLive conventions so the `.zxr` export works directly.
- Phases may be symbolic (α, β), with a declared domain.
- Rules with an arbitrary number of legs are stored as a representative concrete instance, e.g. 3 legs, with an "arity note". Optional extra instances (`instances/n=2/…`) are verified too.
- No scalable notation is used, per the scope.

**meta.json** (sketch):
```json
{
  "id": "spider-fusion", "name": "Spider fusion", "aliases": ["(f)", "S1", "fusion"],
  "calculus": "ZX", "fragment": "phase-free | clifford | clifford+t | universal",
  "group": "spider", "summary": "one line", "description": "markdown + KaTeX",
  "variables": {"α": "real", "β": "real"},
  "equality": "exact | up-to-scalar",
  "arity_note": "holds for any number of legs",
  "first_appeared": {"paper": "coecke-duncan-2008", "location": "Fig. 3, rule (S1)"},
  "also_in": [{"paper": "zx-book-2024", "location": "Table 8.1"}],
  "related": [{"rule": "hadamard-hopf", "relation": "variant-of | special-case-of | generalises | derived-from"}],
  "axiom_in": ["vilmart-2018"],
  "tags": ["fusion"]
}
```
- In `variables`, the domain can be "real", "clifford" or "clifford+t".
- `axiom_in` lists the complete axiomatisations that use this rule as an axiom.
- **papers.json** holds title, authors, year, arXiv link, DOI/journal link and venue, stored once and referenced by key.
- **Fragment semantics**: the fragments are nested, phase-free ⊂ Clifford ⊂ Clifford+T ⊂ universal. The build infers the smallest fragment containing the rule's phases and variable domains, and fails if `meta.json` claims a smaller one.

## 3. Verification (part of every build; any failure fails the build)
1. **Structural checks.** The schema is valid. Boundaries have degree 1. LHS and RHS have the same inputs and outputs. All referenced rule and paper ids exist, and `related` links are made symmetric automatically.
2. **Semantic checks**:
   - Compare the LHS and RHS tensors with PyZX.
   - `exact` rules must match with scalars included; `up-to-scalar` rules must be proportional, and the scalar found is recorded and shown on the page.
   - Symbolic rules: substitute many random values from each variable's domain and check every substitution.
   - Every view, every extra instance and every auto-derived variant is checked.
3. The build writes a verification report. Each rule page shows a "verified with PyZX x.y" badge.

## 4. Two-colour vs graph-like views
- **Two-colour** view: Z/X spiders, plain edges, explicit Hadamards. **Graph-like** view: Z spiders only, with Hadamard edges.
- If only one view is curated, the other is derived automatically:
  - two-colour → graph-like: colour-change via `to_gh`, then clean up;
  - graph-like → two-colour: Hadamard edges become explicit H boxes.
- Each view is labelled "curated" or "auto-derived", and both kinds are verified.
- Rules that have no sensible graph-like form (e.g. raw bialgebra) get either a curated equivalent graph-like rule or the label "n/a".
- Extra page toggles: **colour-swapped** and **adjoint (reversed)** versions, generated automatically and verified.

## 5. Website
- **Pages**:
  - Home: the zoo overview, with groups organised by calculus (ZX/ZH/ZW) × fragment and rule cards showing LHS = RHS thumbnails.
  - One page per group, e.g. "Local complementation" with all its variants side by side.
  - One page per rule: the diagram with a view switch, description (KaTeX), scalar, fragment and calculus badges, first source (arXiv and journal links), also-appears-in, related rules, the axiomatisations it belongs to, and downloads.
  - A papers page listing the rules introduced by each paper.
- **Diagrams**: rendered to SVG at build time by our own renderer, styled like the book (green Z, red X, yellow H). No JS is needed for the diagrams.
- **Search and filters**: client-side over a generated `search.json`. Search covers name, aliases, tags and description; facets are calculus, fragment, group and paper. Plain JS, or Fuse.js from a CDN for fuzzy matching.
- **Downloads per rule and view**:
  - `.tikz` for LHS and RHS, plus a combined `lhs = rhs` tikz. These use TikZiT style names from `pyzx.tikz` and come with a downloadable `zx.tikzstyles`.
  - `lhs.json` and `rhs.json` (PyZX).
  - `<id>.zxr` (ZXLive).
  - A zip per rule.
  - A site-wide zip that is usable directly as a ZXLive custom-rules folder.
- **Hosting**: a GitHub Actions workflow (Python build, then deploy with `actions/deploy-pages`). The classic branch-based Pages build cannot run PyZX, so a custom workflow is required either way.

## 6. Initial rule catalogue (to be expanded from the sources)
- **ZX / phase-free**:
  - spider fusion and identity removal
  - self-loop removal (plain and Hadamard edges) and parallel-edge rules
  - Hadamard cancellation
  - colour change
  - state copy
  - bialgebra, including the generalised m×n version
  - Hopf (complementarity) and Hopf for Hadamard edges
- **ZX / Clifford**:
  - π-commutation and π-copy
  - Euler decomposition of H (variants)
  - Y-state identity
  - **Local-complementation group**: internal ±π/2 spider removal, the graph-state LC rule, and the boundary variants
  - **Pivot group**: pivot, boundary pivot, gadget pivot
  - identity-gadget removal
  - scalar rules, the zero rule, and the Backens Clifford-completeness rules (e.g. K2)
- **ZX / Clifford+T**:
  - phase-gadget fusion
  - supplementarity
  - the Jeandel–Perdrix–Vilmart Clifford+T axioms
  - the 2-qubit Clifford+T rules
  - catalysis-based rules
- **ZX / universal**: the Euler-angle rule (EU) of Vilmart's near-minimal set, the Ng–Wang rules, and general gadget rules.
- **ZH**:
  - H-box fusion, multiply, average, intro, ortho
  - ZH bialgebra
  - phase-free ZH and Toffoli–Hadamard rules
- **ZW**: Hadzihasanovic's ZW rules, and the planar ZW fragment rules.
- **Grouping principle**: a rule's *group* is its conceptual family (fusion, copy, bialgebra/Hopf, colour change & Hadamard, LC, pivot, gadgets, Euler, scalars, supplementarity, …). Calculus and fragment are orthogonal facets. The same rule found in several papers becomes one rule with several citations; different formulations become variants in the same group.

## 7. Milestones
1. Scaffold the package, schemas and `build.py`. Hand-encode about 10 core ZX rules and get verification, rendering and all export formats working end to end, including a check that the `.zxr` loads in ZXLive.
2. Build the site templates (rule, group and paper pages), search and filters, and the GitHub Actions deploy.
3. Write a tikz importer: fetch the arXiv e-print sources into a scratch directory and convert the TikZiT rule figures with `pyzx.tikz.tikz_to_graph` plus a style mapping, then hand-fix positions and boundaries.
4. Populate the catalogue paper by paper, with citations, descriptions and relations. A rule that fails verification is investigated, not silently included.
5. Polish: dark mode, accessibility, bulk downloads.

## 8. Open questions
1. **Jekyll vs Python-only.** A custom Actions workflow is needed anyway, because PyZX must run, so Jekyll mostly adds a Ruby toolchain. Python + Jinja2 can write the static HTML directly, which is simpler to preview and maintain. My recommendation is Python + Jinja2, but Jekyll works fine if you prefer it.
2. **Scalars.** Store exact scalars (ZXLive requires them) wherever possible, and otherwise mark the rule "up to scalar" while still showing the computed scalar. OK?
3. **Rule direction.** Keep each rule in the direction its source paper uses, or normalise so rules simplify left-to-right?
4. **Variants.** Should colour-swapped and adjoint variants be generated toggles (proposed) or separate catalogue entries?
5. **Fragment of Pauli-only rules.** Should π-commutation be classed as Clifford (proposed), or should there be a separate "Pauli" level?
6. **Book source.** Can I use the LaTeX/tikz source of *Picturing Quantum Software* (github.com/zxcalc/book?) for the cheatsheet and H-box rules?


## Answers to open questions
1. Yes, using Jinja2 is fine.
2. Yes, store exact scalars. But consider making them part of the json, instead of part of the diagrams, as for parametrised diagrams (including parametrised in number of inputs and outputs), the scalar might be a function. It would also be nice to offer a toggle to move the scalar to the left-hand side or the right-hand side.
3. Yes, keep the direction from the paper. Give a toggle to swap lhs and rhs.
4. Colour-swap, adjoint, transpose, conjugate should all be generated, not separate catalogue entries.
5. Yes, a separate Pauli entry would be good. Also consider that these classes are hierarchical. So Clifford+T includes Clifford, which includes Pauli, which includes phase-free. Note that in your plan you include Hadamard in the phase-free setting, but that would automatically make that fragment include the Pauli phases. Phase-free should be just phase-free Z- and X-spiders, no Hadamards. Then the next fragment is Pauli (which still does not include the Hadamard). The next up from that is the real Clifford fragment, which includes the Hadamard.
6. I've copied over some of the source files from the book. Note that I've also copied over all 1100 diagrams from the book. I've also included zx-papers.bib, which is the bib file used to generate the publications page on the ZX-calculus webpage.

For the rendering of the diagram on the website, consider using the d3 diagram viewer of pyzx for more interactivity.


## Implementation notes (decisions taken while building)
- **Site generation**: Python and Jinja2 (`build.py` → `_site/`), deployed by GitHub Actions (`.github/workflows/pages.yml`). There is no Jekyll.
- **Diagram viewer**: `site/static/zxview.js` is a d3-based viewer modelled on PyZX's `zx_viewer.js`. Spiders are drawn in book style and can be dragged.
- **Rule layout on disk**: rules are stored flat as `rules/<id>/`. The group is a metadata field, so rules can be regrouped without moving files.
- **Bibliography**: `data/zx-papers.bib` is the zxcalculus.com list. Other `data/*.bib` files add or override entries.
- **Hadamards**: in ZX rules, Hadamard gates are always Hadamard edges. PyZX H-boxes are unnormalised ZH boxes, so using them would make the scalars wrong. The viewer and TikZ export draw Hadamard edges as yellow boxes in the two-colour view.
- **Scalars**: the convention is LHS = s · RHS. The scalar is a sympy expression in `meta.json` and may depend on the phase variables (as angles) and the arity parameters (`parameters`). Rules that hold for any number of legs are stored as one representative instance.
- **Verification**: every variant is checked, scalar included: view × colour swap × {as stated, conjugate, transpose, adjoint}. Symbolic phases are sampled. Every exported `.zxr` is reloaded the way ZXLive does and checked the same way ZXLive's "check rule" does.
- **Fragment**: inferred from the two-colour diagrams. The build fails if `meta.json` claims something else.
- **Data conventions**: documented in `authoring/README.md`.
- **Fact-checking**: paper-specific labels, locations and `axiom_of` claims are only recorded when they were checked against the actual source.

## Status (2026-10-20, after the notes of 20-10-2026 15:56)
- **Catalogue**: 206 rules (140 ZX, 32 ZH, 34 ZW). Of these:
  - 42 hold for any number of legs and have arity templates;
  - 48 are only drawn (`checked: false`, TikZ export only), because they use triangles, λ-boxes with triangles, the star, the fermionic crossing, or bare cups and caps;
  - 15 are circuit rules (`kind: circuit`: quantum gates as diagrams, verified against the unitary);
  - 22 are fault-equivalent rewrites (only their semantics is checked, not fault equivalence; edge weights and fault-free edges are stored as PyZX edge data).
- **Verification**: all checked rules verify, about 2350 variants; the full build takes about 3 minutes.
- **Completeness tables**: every axiom in the completeness tables now links to a rule.
- **Drawn-only rules**: their extra generators are DUMMY vertices with a `symbol` vertex-data field (see `authoring/dsl.py` `D.sym`). Invisible way points (boundaries with two neighbours) are drawn as smooth curves, which gives cups and caps.
- **Data**: the JSON in `rules/` is canonical; the authoring scripts only generated the initial data.
- **Not yet covered**: arities for `graph-state-pivot` and `cyclotomic-supplementarity`.
- **Possible erratum in the book**: Section 8.2.2 (circuit identities, `circuit-commutation-rules.tikz`) has a ZZ-gadget(α), then H⊗H, then gadget(β) equal to the same circuit with α and β swapped. As drawn this fails verification.
- **Malformed bib keys**: `boriskhesin2026spidercat:` and `poor2026spidercss:` end in a colon. They work, but are probably typos.


## Additional notes

* For the style of the website, make it look more like https://zxcalculus.com/ in terms of colours used and font.
* For the rules that manifestly work on an arbitrary number of legs, the main page should list it as having an arbitrary number of legs. Such a rewrite cannot be verified in PyZX, but that is okay. If you can figure out some way to render the '\ldots' or '\cdots' used to represent an arbitrary number of wires in the d3 viewer, that would be great. 
* If possible, for these rewrite rules, when you go the rule page you should be able to select how many input wires and output wires the rule has. So that for instance the spider fusion rule can be represented with an arbitrary number of wires.
* In the scalar rendering, a phase like e^{i pi/4} is sometimes rendered as (-1)^{1/4}. Please make it always use the first one.
* Some rewrite rules, like the "Copying the Hadamard-loop state" are just a variant of a more common rule (in this case State Copy), with a specific representation needed for that completeness paper. These do not have to be listed on the main page, but instead can be linked as an Alternative representation on the page of the original rule.
* For the completeness papers, also generate a page that lists all the rules used in that completeness result. Note that some papers state multiple completeness results. In that case the page will have multiple tables of rewrite rules.
* Something seems to be wrong with the filtering on the main page. If I click Phase-free it still shows me several rules containing Hadamards, and in the Scalar section it also shows the Cliford+T scalar rule, which is not at all applicable to this setting.
* Your graph-like option doesn't actually make the diagrams graph-like, but rather just turns red into green + Hadamards. This is a good option to have, but we can perhaps call this GH representation. We can then add a graph-like representation that also fuses all spiders, gets rid of self-loops, and gets rid of parallel edges. This does not make a lot of sense for certain rewrite rules, like Self-loop removal, so in those cases we can not give a graph-like option (we can have that option greyed out).
* Tikz figures generate diagrams in the bottom right corner. However, it would be nice for the full rewrite rule to have the equals sign at (0,0) and the lhs and rhs to the left and right of that.

## Notes 20-10-2026 15:56

* In http://127.0.0.1:8000/rules/scalar-z-spider/index.html the scalar is drawn as e^{i alpha} + 1 \emptydiag. However, as read this is wrong and should be (e^{i alpha} + 1) \emptydiag.
* In http://127.0.0.1:8000/rules/hopf/index.html in the Details panel, it says LHS = 1 * 1/2 * RHS. You can get rid of the 1 here.
* In http://127.0.0.1:8000/rules/pivot/index.html, the \cdots does not appear for the shared neighbourhood.
* In http://127.0.0.1:8000/rules/zh-average/index.html, when you go to conjugate or adjoint it doesn't conjugate the symbolic labels. This would require having a representation of the complex conjugate of a label, which pyzx doesn't, so in these cases I would just gray out the conjugate and adjoint buttons.
* For the rules that can't be represented directly in PyZX or ZXLive, for instance because they involve cups, caps, or generators that aren't part of PyZX, still include their entries, but only make them exportable to Tikz instead of to PyZX or ZXLive. For cups, just add boundary generators in order to get the required shape (or edit the d3 representation to allow for cubic bezier curves). For these rules you don't have to check semantics. Note on their page that they aren't checked.
* Add a category of circuit representations, that show how certain common quantum gates can be represented as a ZX/ZH diagram, including their correct scalar. For these you can have an export button to PyZX for the ZX side, but not for the circuit side. For the circuits you can export them to TikZ. Include as gates at least the Paulis, CNOT, CZ, Toffoli, CCZ, controlled Hadamard, controlled SWAP.
* Add the fault-equivalent rewrites from the papers of https://zxcalculus.com/publications.html tagged in that way. You don't have to verify their fault-equivalence. The level of fault-equivalence can be described in the description, you can just write the regular equals symbol in the equation.

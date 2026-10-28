"""Turn a TikZiT picture (as found in the arXiv sources of ZX papers, or reference/book/figures) into a
skeleton of DSL code, as a starting point for authoring a rule.

    python authoring/tikz_import.py path/to/figure.tikz

The output splits the picture at nodes whose label is '=' (or \\scalareq etc.) into separate
diagrams, maps node styles to Z / X / H / boundary by keywords, and prints DSL calls with
coordinates x = tikz x, y = -tikz y (PyZX qubits grow downwards). The output always needs manual
checking: '...' nodes, scalars, wires that pass through 'none' nodes, and labels must be fixed by
hand, and boundary nodes must be placed so that inputs are left of their neighbour and outputs right.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

NODE = re.compile(r"\\node\s*\[([^\]]*)\]\s*\(([^)]*)\)\s*at\s*\(\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\)\s*\{(.*)\}\s*;")
DRAW = re.compile(r"\\draw\s*(?:\[([^\]]*)\])?\s*\(([^)]*?)(?:\.center)?\)\s*to(?:\s*\[[^\]]*\])?\s*\(([^)]*?)(?:\.center)?\)")
EQ_LABELS = {"=", "$=$", "\\scalareq", "$\\scalareq$", "$\\propto$", "\\propto"}


def classify(style: str, label: str) -> str:
    s = style.lower()
    if "had" in s and "edge" not in s:
        return "h"
    if any(k in s for k in ("white", "z ", "z dot", "z phase", "green", "zdot", "zspider")) or s.startswith("z"):
        return "z"
    if any(k in s for k in ("gray", "grey", "x dot", "x phase", "red", "xdot", "xspider")) or s.startswith("x"):
        return "x"
    if "w" in s and ("tri" in s or "black" in s):
        return "w"
    return "none"


def latex_to_phase(label: str) -> str:
    l = label.strip().strip("$").replace("\\,", "").replace("~", "").replace("\\ ", "").strip()
    l = l.replace("\\pi", "π").replace("\\frac{π}{2}", "1/2").replace("\\fracπ2", "1/2")
    l = l.replace("\\fracπ4", "1/4").replace("\\frac{π}{4}", "1/4")
    l = re.sub(r"\\alpha_?\{?(\d*)\}?", lambda m: "alpha" + m.group(1), l)
    l = re.sub(r"\\beta_?\{?(\d*)\}?", lambda m: "beta" + m.group(1), l)
    l = re.sub(r"\\gamma_?\{?(\d*)\}?", lambda m: "gamma" + m.group(1), l)
    return l


def main(path):
    text = Path(path).read_text(encoding="utf8", errors="replace")
    nodes = {}
    for m in NODE.finditer(text):
        style, name, x, y, label = m.groups()
        st = re.search(r"style=([^,\]]*)", style)
        nodes[name.strip()] = (st.group(1).strip() if st else "none", float(x), -float(y), label.strip())
    edges = []
    for m in DRAW.finditer(text):
        style, a, b = m.groups()
        edges.append((a.strip(), b.strip(), "hadamard" in (style or "")))
    eq_x = sorted(x for (st, x, y, lab) in nodes.values() if lab in EQ_LABELS)
    bounds = [float("-inf")] + eq_x + [float("inf")]
    for i in range(len(bounds) - 1):
        lo, hi = bounds[i], bounds[i + 1]
        part = {n: v for n, v in nodes.items() if lo < v[1] < hi}
        if not part:
            continue
        print(f"# --- diagram {i} (x between {lo} and {hi})")
        print("G = D()")
        for n, (st, x, y, lab) in sorted(part.items(), key=lambda kv: (kv[1][1], kv[1][2])):
            kind = classify(st, lab)
            var = "v_" + re.sub(r"\W", "_", n)
            if kind in ("z", "x"):
                ph = latex_to_phase(lab)
                print(f"{var} = G.{kind}({x:g}, {y:g}{', ' + repr(ph) if ph else ''})  # {st} {lab}")
            elif kind == "h":
                print(f"{var} = G.h({x:g}, {y:g})  # {st}  (in ZX rules use a Hadamard edge G.he instead)")
            elif lab and lab not in ("", "..."):
                print(f"# text node {n} at ({x:g}, {y:g}): {lab}")
            else:
                print(f"{var} = G.b({x:g}, {y:g})  # {st} {lab}")
        for a, b, had in edges:
            if a in part and b in part:
                va, vb = "v_" + re.sub(r"\W", "_", a), "v_" + re.sub(r"\W", "_", b)
                print(f"G.{'he' if had else 'e'}({va}, {vb})")
        print()


if __name__ == "__main__":
    main(sys.argv[1])

"""Build the ZX rewrite zoo.

    python build.py            # validate + verify every rule and variant, then generate _site/
    python build.py --check    # only validate and verify (no site output)
    python build.py --fast     # verify only the rules as stated (skip generated variants)
    python build.py --only=spider-fusion,bialgebra   # restrict to some rules (for debugging)

The build fails (non-zero exit code) if any rule is malformed or any (variant of a) rule does not
hold semantically.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

from zxrewrites import RULES_DIR, ROOT
from zxrewrites.pipeline import process_all


def main(argv):
    if "--help" in argv or "-h" in argv:
        print(__doc__)
        return 0
    check_only = "--check" in argv
    fast = "--fast" in argv
    only = None
    out = ROOT / "_site"
    for a in argv:
        if a.startswith("--only="):
            only = set(a.split("=", 1)[1].split(","))
        if a.startswith("--out="):
            out = Path(a.split("=", 1)[1])
    t0 = time.time()
    catalogue, errors = process_all(only=only, full=not fast)
    processed = catalogue.rules
    n_variants = sum(len(p.variants) for p in processed)
    print(f"Checked {len(processed)} rules ({n_variants} variants) in {time.time() - t0:.1f}s")
    if errors:
        print(f"\n{len(errors)} problem(s):", file=sys.stderr)
        for e in errors:
            print("  - " + e, file=sys.stderr)
        return 1
    if not check_only:
        from zxrewrites.site import build_site
        build_site(catalogue, out)
        print(f"Site written to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

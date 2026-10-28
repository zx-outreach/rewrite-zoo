"""Tooling for the ZX rewrite zoo: loading, verifying, transforming and exporting rewrite rules."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES_DIR = ROOT / "rules"
DATA_DIR = ROOT / "data"

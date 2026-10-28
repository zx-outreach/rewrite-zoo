"""Tests for the rule tooling (the rules themselves are verified by build.py)."""

import json
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "authoring"))

from zxrewrites import export, graphs, scalars, transforms, verify  # noqa: E402
from zxrewrites.bib import load_bib  # noqa: E402
from zxrewrites.phases import format_phase, parse_phase  # noqa: E402
from dsl import D  # noqa: E402


def spider_pair(phase_a="alpha", phase_b="beta", colour="z"):
    d = D()
    a = getattr(d, colour)(1, 0, phase_a)
    b = getattr(d, colour)(2, 0, phase_b)
    d.e(d.b(0, 0), a, b, d.b(3, 0))
    d.g.auto_detect_io()
    return d.g


def single(phase, colour="z"):
    d = D()
    a = getattr(d, colour)(1, 0, phase)
    d.e(d.b(0, 0), a, d.b(2, 0))
    d.g.auto_detect_io()
    return d.g


def test_format_phase():
    g = graphs.new_graph()
    reg = g.var_registry
    assert format_phase(Fraction(1, 2)) == "π/2"
    assert format_phase(Fraction(3, 2)) == "-π/2"
    assert format_phase(Fraction(1)) == "π"
    assert format_phase(Fraction(3, 4), latex=True) == r"\frac{3\pi}{4}"
    assert format_phase(parse_phase("alpha+1/2", reg, {})) == "α+π/2"
    assert format_phase(parse_phase("-alpha1", reg, {})) == "-α₁"
    assert format_phase(parse_phase("a", reg, {"a": True})) == "aπ"


def test_spider_fusion_verifies_and_wrong_phase_fails():
    lhs = spider_pair()
    rhs = single("alpha+beta")
    variables = {"alpha": {"domain": "real"}, "beta": {"domain": "real"}}
    assert verify.check(lhs, rhs, scalars.parse_scalar("1", variables, {}), variables, {}).ok
    wrong = single("alpha-beta")
    assert not verify.check(lhs, wrong, scalars.parse_scalar("1", variables, {}), variables, {}).ok
    assert not verify.check(lhs, rhs, scalars.parse_scalar("2", variables, {}), variables, {}).ok


def test_transforms_are_involutions_semantically():
    g = spider_pair("alpha", "1/4", "x")
    vals = {"alpha": Fraction(1, 3)}
    T = lambda h: graphs.tensor(graphs.instantiate(h, vals))
    base = T(g)
    assert np.allclose(T(transforms.colour_swap(transforms.colour_swap(g))), base)
    assert np.allclose(T(transforms.transpose(transforms.transpose(g))), base)
    assert np.allclose(T(transforms.conjugate(g)), base.conj())
    assert np.allclose(T(transforms.adjoint(g)), base.conj().T)
    assert np.allclose(T(transforms.to_gh(g)), base)
    assert np.allclose(T(transforms.to_two_colour(transforms.to_gh(g))), base)
    gl, f = transforms.to_graph_like(g)
    assert np.allclose(complex(f) * T(gl), base)


def test_scalar_conjugate():
    variables = {"alpha": {"domain": "real"}, "c": {"domain": "complex"}}
    s = scalars.parse_scalar("exp(I*alpha)*c*(1+I)", variables, {})
    sc = scalars.conjugate(s, variables, {})
    val = scalars.evaluate(sc, {"alpha": Fraction(1, 3), "c": 2 + 1j}, variables, {})
    expect = np.conj(np.exp(1j * np.pi / 3) * (1 + 1j)) * (2 + 1j)
    assert np.isclose(val, expect)


def test_zxr_round_trip():
    lhs = spider_pair("1/4", "1/4")
    rhs = single("1/2")
    text = export.zxr("fusion", "test", lhs, rhs)
    export.check_zxr(text, exact=True)
    d = json.loads(text)
    assert set(d) == {"lhs_graph", "rhs_graph", "name", "description"}
    assert isinstance(d["lhs_graph"], str)
    with pytest.raises(ValueError):
        export.check_zxr(export.zxr("bad", "", lhs, single("1/4")), exact=True)


def test_bib_has_key_papers():
    bib = load_bib()
    assert bib["CD2"]["arxiv"] == "https://arxiv.org/abs/0906.4725"
    assert "van de Wetering" in " ".join(bib["duncan2019graph"]["authors"])


def test_tikz_export_mentions_styles():
    t = export.tikz_equation(spider_pair(), single("alpha+beta"), "", "rhs")
    assert "Z phase dot" in t and r"\alpha" in t and "$=$" in t

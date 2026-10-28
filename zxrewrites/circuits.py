"""Quantum circuits for the "gates as diagrams" rules.

A circuit rule has  "kind": "circuit"  and  "circuit": {"qubits": n, "gates": [...]}  in its meta.json.
Gates are lists [name, qubit, ...] (plus an angle for rotations), e.g.

    ["H", 0], ["CNOT", 0, 1], ["CCZ", 0, 1, 2], ["RZ", 0, "alpha"], ["CSWAP", 0, 1, 2]

The left-hand side of such a rule is the circuit, drawn with gate symbols (lhs.json is generated from
the gate list and is only used for drawing); the right-hand side is an ordinary ZX/ZH diagram. The
rule states  U = s · D  where U is the unitary of the circuit (qubit 0 is the top wire and the most
significant bit, as in PyZX), and it is verified like any other rule.
"""

from __future__ import annotations

import cmath
import math
from fractions import Fraction
from typing import Any, Dict, List

import numpy as np

from . import graphs
from .graphs import VT

I2 = np.eye(2, dtype=complex)
H = np.array([[1, 1], [1, -1]], dtype=complex) / math.sqrt(2)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
S = np.diag([1, 1j])
T = np.diag([1, cmath.exp(1j * math.pi / 4)])


def _angle(a, values) -> float:
    """An angle given in units of pi: a number, a fraction string, or a variable name."""
    if isinstance(a, (int, float)):
        return float(a) * math.pi
    try:
        return float(Fraction(a)) * math.pi
    except ValueError:
        sign = -1 if a.startswith("-") else 1
        return sign * float(values[a.lstrip("-")]) * math.pi


def single_qubit(name: str, args, values) -> np.ndarray:
    if name == "I":
        return I2
    if name == "H":
        return H
    if name in ("X", "NOT"):
        return X
    if name == "Y":
        return Y
    if name == "Z":
        return Z
    if name == "S":
        return S
    if name == "Sdg":
        return S.conj().T
    if name == "T":
        return T
    if name == "Tdg":
        return T.conj().T
    if name == "V":  # sqrt(X)
        return H @ S @ H
    if name == "RZ":  # diag(1, e^{iα}), as a Z-spider
        return np.diag([1, cmath.exp(1j * _angle(args[0], values))])
    if name == "RX":
        return H @ np.diag([1, cmath.exp(1j * _angle(args[0], values))]) @ H
    raise ValueError(f"unknown single-qubit gate {name}")


CONTROLLED = {"CNOT": ("X", 1), "CX": ("X", 1), "CZ": ("Z", 1), "CY": ("Y", 1), "CH": ("H", 1),
              "CS": ("S", 1), "CCX": ("X", 2), "CCNOT": ("X", 2), "TOFFOLI": ("X", 2), "CCZ": ("Z", 2),
              "CRZ": ("RZ", 1)}


def gate_matrix(gate: List[Any], n: int, values: Dict[str, Any]) -> np.ndarray:
    """The 2^n x 2^n matrix of a gate in an n-qubit circuit."""
    name = gate[0].upper() if gate[0] not in ("Sdg", "Tdg") else gate[0]
    dim = 2 ** n

    def basis_map(fn):
        M = np.zeros((dim, dim), dtype=complex)
        for i in range(dim):
            bits = [(i >> (n - 1 - q)) & 1 for q in range(n)]
            for amp, out in fn(bits):
                j = sum(b << (n - 1 - q) for q, b in enumerate(out))
                M[j, i] += amp
        return M

    if name in ("SWAP", "CSWAP", "FREDKIN"):
        ctrl = gate[1:-2] if name != "SWAP" else []
        a, b = gate[-2], gate[-1]

        def f(bits):
            out = list(bits)
            if all(bits[c] for c in ctrl):
                out[a], out[b] = bits[b], bits[a]
            return [(1, out)]
        return basis_map(f)
    if name in CONTROLLED:
        base, k = CONTROLLED[name]
        ctrl = gate[1:1 + k]
        targ = gate[1 + k]
        U = single_qubit(base, gate[2 + k:], values)

        def f(bits):
            if not all(bits[c] for c in ctrl):
                return [(1, bits)]
            res = []
            for o in (0, 1):
                amp = U[o, bits[targ]]
                if abs(amp) > 1e-15:
                    out = list(bits)
                    out[targ] = o
                    res.append((amp, out))
            return res
        return basis_map(f)
    q = gate[1]
    U = single_qubit(gate[0], gate[2:], values)
    mats = [U if i == q else I2 for i in range(n)]
    M = mats[0]
    for m in mats[1:]:
        M = np.kron(M, m)
    return M


def unitary(circuit: Dict[str, Any], values: Dict[str, Any]) -> np.ndarray:
    n = circuit["qubits"]
    U = np.eye(2 ** n, dtype=complex)
    for gate in circuit["gates"]:
        U = gate_matrix(gate, n, values) @ U
    return U


# ---------------------------------------------------------------------------------------------
# Drawing: the circuit as a diagram of gate symbols (DUMMY vertices with a "symbol").

GATE_TEXT = {"Sdg": "S†", "Tdg": "T†", "RZ": "Z", "RX": "X"}


GATE_TEX = {"Sdg": r"S^\dagger", "Tdg": r"T^\dagger"}


def _sym(g, x, y, symbol, text="", tex=""):
    v = g.add_vertex(VT.DUMMY, qubit=y, row=x)
    g.set_vdata(v, "symbol", symbol)
    if text:
        g.set_vdata(v, "text", text)
    if tex:
        g.set_vdata(v, "tex", tex)
    return v


def _angle_text(a, latex: bool = False) -> str:
    from .phases import format_phase, var_display
    if isinstance(a, str) and not a.replace("/", "").replace("-", "").isdigit():
        neg = a.startswith("-")
        return ("-" if neg else "") + var_display(a.lstrip("-"))[1 if latex else 0]
    return format_phase(Fraction(a), latex=latex) if a not in (0, "0") else "0"


def draw(circuit: Dict[str, Any], spacing: float = 1.0):
    """A PyZX graph that draws the circuit (for the viewer and TikZ only)."""
    n = circuit["qubits"]
    g = graphs.new_graph()
    last = [g.add_vertex(VT.BOUNDARY, qubit=q, row=0) for q in range(n)]
    x = 0.0
    for gate in circuit["gates"]:
        x += spacing
        name = gate[0].upper() if gate[0] not in ("Sdg", "Tdg") else gate[0]
        verts = {}
        if name in ("SWAP", "CSWAP", "FREDKIN"):
            ctrl = gate[1:-2] if name != "SWAP" else []
            for c in ctrl:
                verts[c] = _sym(g, x, c, "ctrl")
            for t in gate[-2:]:
                verts[t] = _sym(g, x, t, "swap")
        elif name in CONTROLLED:
            base, k = CONTROLLED[name]
            for c in gate[1:1 + k]:
                verts[c] = _sym(g, x, c, "ctrl")
            t = gate[1 + k]
            if base == "X":
                verts[t] = _sym(g, x, t, "targ")
            elif base == "Z":
                verts[t] = _sym(g, x, t, "ctrl")
            else:
                txt = GATE_TEXT.get(base, base)
                tex = GATE_TEX.get(base, txt)
                if base == "RZ":
                    txt = "Z(" + _angle_text(gate[2 + k]) + ")"
                    tex = "Z(" + _angle_text(gate[2 + k], True) + ")"
                verts[t] = _sym(g, x, t, "gate", txt, tex)
        else:
            q = gate[1]
            txt = GATE_TEXT.get(gate[0], gate[0])
            tex = GATE_TEX.get(gate[0], txt)
            if gate[0] in ("RZ", "RX"):
                tex = f"{txt}({_angle_text(gate[2], True)})"
                txt = f"{txt}({_angle_text(gate[2])})"
            verts[q] = _sym(g, x, q, "gate", txt, tex)
        for q, v in verts.items():
            g.add_edge((last[q], v))
            last[q] = v
        qs = sorted(verts)
        for a, b in zip(qs, qs[1:]):
            g.add_edge((verts[a], verts[b]))
    x += spacing
    for q in range(n):
        g.add_edge((last[q], g.add_vertex(VT.BOUNDARY, qubit=q, row=x)))
    graphs.detect_io(g)
    return g

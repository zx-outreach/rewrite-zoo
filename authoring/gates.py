"""Common quantum gates as ZX- and ZH-diagrams ("kind": "circuit" rules).

The left-hand side is the gate as a circuit (drawn from the gate list; not exported to PyZX), the
right-hand side is the diagram. The scalar s in  U = s · D  is computed and then verified by the build.
"""

import numpy as np
import sympy as sp

from dsl import D, rule
from zxrewrites import circuits, graphs, scalars

BOOK = {"bib": "KissingervdWeteringbook", "location": "Chapter 8, Table 8.3 (unitaries)"}
WORKING = {"bib": "vandewetering2020zxcalculus"}


def circuit_scalar(circuit, rhs: D, variables=None) -> str:
    from zxrewrites import verify
    var_specs = {k: ({"domain": v} if isinstance(v, str) else v) for k, v in (variables or {}).items()}
    ratio = None
    for vals in verify.sample_values(var_specs):
        U = circuits.unitary(circuit, vals)
        Dm = graphs.tensor(graphs.instantiate(rhs.g, vals))
        idx = np.unravel_index(np.argmax(np.abs(Dm)), Dm.shape)
        c = U[idx] / Dm[idx]
        assert np.allclose(U, c * Dm), "circuit and diagram are not proportional"
        if ratio is None:
            ratio = c
        assert np.isclose(ratio, c), "scalar depends on the variables"
    return sp.sstr(scalars.from_number(complex(ratio)))


def gate_rule(id, circuit, rhs: D, **meta):
    lhs = D()
    lhs.g = circuits.draw(circuit)
    rhs.g.auto_detect_io()
    meta.setdefault("scalar", circuit_scalar(circuit, rhs, meta.get("variables")))
    meta.setdefault("group", "gates" if meta.get("calculus", "ZX") == "ZX" else "zh-gates")
    rule(id, lhs=lhs, rhs=rhs, kind="circuit", circuit=circuit, **meta)


def wires(Dg, n, x1):
    """Input and output boundaries for n qubits."""
    return [Dg.b(0, q) for q in range(n)], [Dg.b(x1, q) for q in range(n)]


def single(phase=None, colour="z", had=False):
    Dg = D()
    i, o = Dg.b(0, 0), Dg.b(2, 0)
    if had:
        Dg.he(i, o)
    else:
        v = getattr(Dg, colour)(1, 0, phase)
        Dg.e(i, v, o)
    return Dg


COMMON = dict(calculus="ZX", source=BOOK, also_in=[WORKING])

gate_rule("gate-pauli-x", {"qubits": 1, "gates": [["X", 0]]}, single(1, "x"),
          name="Pauli X gate", aliases=["NOT gate", "X"], fragment="pauli", order=1,
          summary="The Pauli X (NOT) gate is an X-spider with phase π.",
          description="The NOT gate $X = |0\\rangle\\langle 1| + |1\\rangle\\langle 0|$ is a phase-π X-spider with one input and one output.",
          tags=["pauli", "NOT", "gate"], **COMMON)
gate_rule("gate-pauli-z", {"qubits": 1, "gates": [["Z", 0]]}, single(1, "z"),
          name="Pauli Z gate", aliases=["Z", "phase flip"], fragment="pauli", order=2,
          summary="The Pauli Z gate is a Z-spider with phase π.",
          description="The phase flip $Z = |0\\rangle\\langle 0| - |1\\rangle\\langle 1|$ is a phase-π Z-spider with one input and one output.",
          tags=["pauli", "gate"], **COMMON)

Y = D()
i, o = Y.b(0, 0), Y.b(3, 0)
Y.e(i, Y.z(1, 0, 1), Y.x(2, 0, 1), o)
gate_rule("gate-pauli-y", {"qubits": 1, "gates": [["Y", 0]]}, Y,
          name="Pauli Y gate", aliases=["Y"], fragment="pauli", order=3,
          summary="The Pauli Y gate is a Z(π) followed by an X(π), times the global phase i.",
          description="Since $Y = iXZ$, the Pauli Y gate is a phase-π Z-spider followed by a phase-π X-spider, up to the global phase $i$.",
          tags=["pauli", "gate"], **COMMON)
gate_rule("gate-hadamard", {"qubits": 1, "gates": [["H", 0]]}, single(had=True),
          name="Hadamard gate", aliases=["H"], fragment="clifford", order=4,
          summary="The Hadamard gate is a Hadamard edge (or a yellow box).",
          description="The Hadamard gate $H = \\frac{1}{\\sqrt2}\\begin{pmatrix}1&1\\\\1&-1\\end{pmatrix}$ is drawn as a yellow box, or as a blue dashed Hadamard edge. See the [Euler decomposition](../euler-decomposition-hadamard/) for how to write it with spiders.",
          tags=["hadamard", "gate", "clifford"], **COMMON)
gate_rule("gate-s", {"qubits": 1, "gates": [["S", 0]]}, single("1/2"),
          name="S gate", aliases=["phase gate", "S", "√Z"], fragment="clifford", order=5,
          summary="The S gate is a Z-spider with phase π/2.",
          description="The phase gate $S = \\mathrm{diag}(1, i)$ is a Z-spider with phase π/2.",
          tags=["clifford", "gate"], **COMMON)
gate_rule("gate-t", {"qubits": 1, "gates": [["T", 0]]}, single("1/4"),
          name="T gate", aliases=["T", "π/8 gate"], fragment="clifford+t", order=6,
          summary="The T gate is a Z-spider with phase π/4.",
          description="The T gate $T = \\mathrm{diag}(1, e^{i\\pi/4})$ is a Z-spider with phase π/4.",
          tags=["T gate", "gate", "clifford+t"], **COMMON)
gate_rule("gate-z-rotation", {"qubits": 1, "gates": [["RZ", 0, "alpha"]]}, single("alpha"),
          name="Z-phase gate", aliases=["phase shift", "RZ", "Z rotation"], fragment="universal", order=7,
          variables={"alpha": "real"},
          summary="The phase gate diag(1, e^{iα}) is a Z-spider with phase α.",
          description="The phase gate $\\mathrm{diag}(1, e^{i\\alpha})$, which equals the Z-rotation $R_Z(\\alpha)$ up to a global phase, is a Z-spider with phase α.",
          tags=["rotation", "gate"], **COMMON)

CX = D()
(i0, i1), (o0, o1) = wires(CX, 2, 2)
c, t = CX.z(1, 0), CX.x(1, 1)
CX.e(i0, c, o0).e(i1, t, o1).e(c, t)
gate_rule("gate-cnot", {"qubits": 2, "gates": [["CNOT", 0, 1]]}, CX,
          name="CNOT gate", aliases=["CX", "controlled NOT"], fragment="phase-free", order=10,
          summary="The CNOT gate is a Z-spider on the control connected to an X-spider on the target.",
          description="The CNOT gate is a phase-free Z-spider on the control (which copies the control bit) connected to a phase-free X-spider on the target (which XORs it into the target), times $\\sqrt2$.",
          tags=["CNOT", "gate", "phase-free"], **COMMON)

CZ = D()
(i0, i1), (o0, o1) = wires(CZ, 2, 2)
a, b = CZ.z(1, 0), CZ.z(1, 1)
CZ.e(i0, a, o0).e(i1, b, o1).he(a, b)
gate_rule("gate-cz", {"qubits": 2, "gates": [["CZ", 0, 1]]}, CZ,
          name="CZ gate", aliases=["controlled Z", "CPHASE"], fragment="clifford", order=11,
          summary="The CZ gate is two Z-spiders connected by a Hadamard edge.",
          description="The controlled-Z gate is symmetric in its two qubits: it is two phase-free Z-spiders connected by a Hadamard edge, times $\\sqrt2$.",
          tags=["CZ", "gate", "graph state"], **COMMON)

SW = D()
(i0, i1), (o0, o1) = wires(SW, 2, 2)
SW.e(i0, o1).e(i1, o0)
gate_rule("gate-swap", {"qubits": 2, "gates": [["SWAP", 0, 1]]}, SW,
          name="SWAP gate", aliases=["swap"], fragment="phase-free", order=12,
          summary="The SWAP gate is just two crossing wires.",
          description="In the ZX-calculus the SWAP gate is simply a crossing of wires. See also [three CNOTs make a SWAP](../swap-three-cnots/).",
          tags=["SWAP", "gate"], **COMMON)

# CCZ as a ZX-diagram: π/4 phases and phase gadgets (the phase polynomial of CCZ)
CCZ = D()
ins, outs = wires(CCZ, 3, 6.2)
xs = [2.0, 3.0, 4.0, 5.0]
subs = (((0, 1), "-1/4"), ((1, 2), "-1/4"), ((0, 2), "-1/4"), ((0, 1, 2), "1/4"))
wire = {q: [CCZ.z(1.0, q, "1/4")] for q in range(3)}
for x, (sub, ph) in zip(xs, subs):
    for q in sub:
        wire[q].append(CCZ.z(x, q))
for q in range(3):
    CCZ.e(ins[q], *wire[q], outs[q])
for k, (x, (sub, ph)) in enumerate(zip(xs, subs)):
    hub = CCZ.z(x + 0.45, 3.2)
    CCZ.he(hub, CCZ.z(x + 0.45, 4.2, ph))
    for q in sub:
        CCZ.he(hub, wire[q][1 + [s_ for s_, _ in subs if q in s_].index(sub)])
gate_rule("gate-ccz-phase-gadgets", {"qubits": 3, "gates": [["CCZ", 0, 1, 2]]}, CCZ,
          name="CCZ gate (phase gadgets)", aliases=["controlled-controlled-Z", "CCZ", "Toffoli phase polynomial"],
          fragment="clifford+t", order=20,
          summary="The CCZ gate is a phase polynomial: π/4 phases on every qubit, −π/4 gadgets on every pair and a π/4 gadget on all three.",
          description=("The CCZ gate is diagonal, $|x_1x_2x_3\\rangle \\mapsto (-1)^{x_1x_2x_3}|x_1x_2x_3\\rangle$, and since "
                       "$4x_1x_2x_3 = x_1+x_2+x_3 - (x_1\\oplus x_2) - (x_2\\oplus x_3) - (x_1\\oplus x_3) + (x_1\\oplus x_2\\oplus x_3)$ "
                       "it is a product of π/4 phases on single qubits and ∓π/4 phase gadgets on parities. This gives the "
                       "well-known decomposition of the CCZ (and hence the Toffoli) gate with 7 T-gates. Drawn in graph-like form."),
          source={"bib": "kissinger2019tcount"}, also_in=[{"bib": "KissingervdWeteringbook"}],
          related=[{"id": "phase-gadget-fusion", "relation": "see-also"}],
          tags=["CCZ", "Toffoli", "T-count", "phase gadget", "gate"], calculus="ZX")

# CCZ and Toffoli in the ZH-calculus
ZH_SRC = {"bib": "EPTCS287.2"}


def ccz_zh(target_had=False):
    Dg = D()
    ins, outs = wires(Dg, 3, 2.6)
    hb = Dg.h(1.7, 1.5)
    for q in range(3):
        v = Dg.z(1.2, q)
        if q == 2 and target_had:
            Dg.he(ins[q], v).he(v, outs[q])
        else:
            Dg.e(ins[q], v, outs[q])
        Dg.e(v, hb)
    return Dg


gate_rule("gate-ccz-zh", {"qubits": 3, "gates": [["CCZ", 0, 1, 2]]}, ccz_zh(),
          name="CCZ gate (H-box)", aliases=["controlled-controlled-Z", "CCZ"], calculus="ZH", fragment="clifford+t", order=1,
          summary="The CCZ gate is three Z-spiders connected to one standard H-box.",
          description=("In the ZH-calculus the CCZ gate is very simple: the H-box with label −1 and three legs is the "
                       "tensor $(-1)^{x_1x_2x_3}$, and the Z-spiders copy the three bits into it. Compare the "
                       "[ZX-calculus version](../gate-ccz-phase-gadgets/) with phase gadgets."),
          source=ZH_SRC, also_in=[{"bib": "KissingervdWeteringbook"}],
          related=[{"id": "gate-ccz-phase-gadgets", "relation": "equivalent-to"}],
          tags=["CCZ", "H-box", "gate"])
gate_rule("gate-toffoli-zh", {"qubits": 3, "gates": [["CCX", 0, 1, 2]]}, ccz_zh(target_had=True),
          name="Toffoli gate (H-box)", aliases=["CCNOT", "CCX", "Toffoli"], calculus="ZH", fragment="clifford+t", order=2,
          summary="The Toffoli gate is a CCZ with Hadamards on the target.",
          description="The Toffoli gate is $(I\\otimes I\\otimes H)\\,\\mathrm{CCZ}\\,(I\\otimes I\\otimes H)$, so in the ZH-calculus it is three Z-spiders connected to a standard H-box, with Hadamards on the target wire.",
          source=ZH_SRC, also_in=[{"bib": "KissingervdWeteringbook"}],
          related=[{"id": "gate-ccz-zh", "relation": "variant-of"}],
          tags=["Toffoli", "CCNOT", "H-box", "gate"])

# Controlled Hadamard: S H T CNOT T† H S† on the target
CH = D()
(i0, i1), (o0, o1) = wires(CH, 2, 7)
c = CH.z(3.5, 0)
CH.e(i0, c, o0)
s1, t1 = CH.z(1, 1, "1/2"), CH.z(2.4, 1, "1/4")
x = CH.x(3.5, 1)
t2, s2 = CH.z(4.6, 1, "-1/4"), CH.z(6, 1, "-1/2")
CH.e(i1, s1).he(s1, t1).e(t1, x, t2).he(t2, s2).e(s2, o1).e(c, x)
gate_rule("gate-controlled-hadamard", {"qubits": 2, "gates": [["CH", 0, 1]]}, CH,
          name="Controlled Hadamard", aliases=["CH", "controlled H"], fragment="clifford+t", order=21,
          summary="The controlled Hadamard is a CNOT conjugated by S·H·T on the target.",
          description=("The controlled Hadamard gate can be written as $(I\\otimes S^\\dagger H T^\\dagger)\\,\\mathrm{CNOT}\\,(I\\otimes T H S)$ "
                       "(gates in the order they are applied: S, H, T, CNOT, T†, H, S† on the target), using two T gates."),
          source=BOOK, tags=["controlled Hadamard", "gate", "clifford+t"], calculus="ZX")

# Controlled SWAP (Fredkin) = CNOT(2,1) Toffoli(0,1,2) CNOT(2,1), with the Toffoli as an H-box
FR = D()
ins, outs = wires(FR, 3, 4)
a1, a2 = FR.x(1, 1), FR.z(1, 2)
FR.e(a1, a2)
c0, c1, c2 = FR.z(2, 0), FR.z(2, 1), FR.z(2, 2)
hb = FR.h(2.6, 1.5)
for v in (c0, c1, c2):
    FR.e(v, hb)
b1, b2 = FR.x(3, 1), FR.z(3, 2)
FR.e(b1, b2)
FR.e(ins[0], c0, outs[0])
FR.e(ins[1], a1, c1, b1, outs[1])
FR.e(ins[2], a2).he(a2, c2).he(c2, b2).e(b2, outs[2])
gate_rule("gate-fredkin-zh", {"qubits": 3, "gates": [["CSWAP", 0, 1, 2]]}, FR,
          name="Controlled SWAP (H-box)", aliases=["Fredkin gate", "CSWAP", "controlled swap"], calculus="ZH",
          fragment="clifford+t", order=3,
          summary="The controlled SWAP is a Toffoli gate sandwiched between two CNOTs.",
          description=("The Fredkin gate swaps qubits 2 and 3 when qubit 1 is $|1\\rangle$. It equals "
                       "$\\mathrm{CNOT}_{3\\to2}\\,\\mathrm{Toffoli}_{1,2\\to3}\\,\\mathrm{CNOT}_{3\\to2}$; here the Toffoli is drawn with "
                       "an H-box and the CNOTs as Z- and X-spiders."),
          source=ZH_SRC, related=[{"id": "gate-toffoli-zh", "relation": "derived-from"}],
          tags=["Fredkin", "CSWAP", "controlled swap", "gate", "H-box"])

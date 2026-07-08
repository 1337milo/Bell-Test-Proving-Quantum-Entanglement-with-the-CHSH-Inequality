# Bell Test — Proving Quantum Entanglement with the CHSH Inequality

A self-contained Python experiment that replicates the mathematics behind the
**2022 Nobel Prize in Physics** (Aspect, Clauser, Zeilinger) using IBM Qiskit.

---

## What This Experiment Does

This code performs a **CHSH Bell test** — the definitive experiment that rules out
Einstein's "hidden variables" hypothesis and proves quantum entanglement is real.

**The key question:** Can correlations between two particles be explained by
pre-set classical values (like a cheat sheet in each particle), or do they require
genuine quantum entanglement?

**The answer:** The CHSH inequality provides a number — the **S value** — that
any local hidden-variable theory must keep below 2. Quantum mechanics can reach
up to 2√2 ≈ 2.828. We measure it. Nature answers.

### Our Results

| Backend | S value | Classical limit | Verdict |
|---------|---------|-----------------|---------|
| Noiseless AerSimulator | **+2.806** | ≤ 2.000 | ✅ Bell violation |
| AerSimulator + ibm_fez noise model | **+2.668** | ≤ 2.000 | ✅ Bell violation |
| **Real ibm_marrakesh hardware** | **+2.522** | ≤ 2.000 | ✅ **Bell violation on real qubits** |
| Theory maximum (Tsirelson bound) | 2.828 | — | Reference |

Real hardware job ID: `d976fn2f47jc73a6cbhg` · ibm_marrakesh · 156 qubits · 31 seconds · 16,384 measurements

All three runs exceed the classical limit. Einstein's hidden variables are ruled out.

---

## The Math in One Line

```
S = E(a,b) - E(a,b') + E(a',b) + E(a',b')

Where E(a,b) = (count_same - count_diff) / total_shots

|S| > 2  →  no local hidden-variable theory can explain this
```

The quantum prediction for a maximally entangled Bell state: **E(a, b) = −cos(a − b)**

---

## The Circuit in Three Gates

```
q0: ──[H]──●──[Ry(2a)]──[M]──   ← Alice measures at angle a
q1: ───────⊕──[Ry(2b)]──[M]──   ← Bob measures at angle b

H     = Hadamard (creates superposition)
CNOT  = entangles the two qubits into Bell state |Φ⁺⟩ = (|00⟩+|11⟩)/√2
Ry(2θ) = rotates measurement basis to angle θ
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- No IBM Quantum account required (uses local simulator and noise model)

### Install and run

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/bell-test-quantum.git
cd bell-test-quantum

# Create virtual environment
python -m venv .venv
source .venv/bin/activate      # Mac/Linux
.venv\Scripts\Activate.ps1    # Windows PowerShell

# Install dependencies
pip install -r requirements.txt

# Run
python bell_test.py
```

Expected runtime: **2–5 minutes** on a standard laptop.

---

## Output Files

| File | What you see |
|------|-------------|
| `results/bell_correlation_curve.png` | Left: cosine correlation vs angle. Right: S vs angle sweep with Bell violation zone. |
| `results/bell_bloch_sphere.png` | 3D density matrix: entangled state vs separable state side by side. |
| `results/bell_results.txt` | Numerical S values, violation amount, noise cost. |

---

## Key Concepts Explained

### The Bell State
```
|Φ⁺⟩ = (|00⟩ + |11⟩) / √2
```
50% chance both qubits measure as 0, 50% chance both measure as 1. Never one-zero.
The correlations between qubits exceed what any pre-set classical value could produce.

### The Correlation E(a,b)
Measures how much Alice's and Bob's results agree across 4096 repeated measurements.
`E = +1` means perfect agreement. `E = -1` means perfect anti-correlation.
For the Bell state: `E(a, b) = -cos(a - b)` — a perfect cosine wave.

### Why the Classical Limit is 2
Bell's algebraic proof: for any four binary ±1 values (hidden variables), the combination
`|ab - ab' + a'b + a'b'|` is always ≤ 2. It's a mathematical fact about four numbers,
not a physical assumption. Quantum correlations violate this because the results aren't
fixed in advance — they are created at the moment of measurement.

### The Tsirelson Bound (2√2)
Quantum mechanics also has a limit, derived by Boris Tsirelson in 1980. No quantum state,
no matter how entangled, can produce |S| > 2√2 ≈ 2.828. This is the Tsirelson bound.

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `qiskit` | ≥ 2.0 | Quantum circuit building |
| `qiskit-aer` | ≥ 0.17 | Local noiseless simulator |
| `qiskit-ibm-runtime` | ≥ 0.47 | FakeFez hardware noise model |
| `numpy` | any | Numerical operations |
| `matplotlib` | any | Plotting |

---

## References

1. Bell, J.S. (1964). "On the Einstein Podolsky Rosen Paradox." *Physics* 1(3), 195–200.
2. Clauser, Horne, Shimony, Holt (1969). "Proposed experiment to test local hidden-variable theories." *PRL* 23(15), 880.
3. Aspect, Grangier, Roger (1982). "Experimental Realization of EPR-Bohm Gedankenexperiment." *PRL* 49(2), 91.
4. Hensen et al. (2015). "Loophole-free Bell inequality violation." *Nature* 526, 682–686.
5. The Nobel Prize in Physics 2022. https://www.nobelprize.org/prizes/physics/2022/

---

## License

Apache License 2.0 — see [LICENSE](LICENSE).

You are free to use, modify, and distribute this code for any purpose including
commercial use, as long as you include the license notice.

---

## Contributing

Issues, improvements, and extensions welcome. Ideas:
- Add the GHZ (3-qubit) entanglement test
- Add loophole analysis (detection efficiency, locality)
- Add submission pathway to real IBM Quantum hardware
- Add the Mermin inequality test

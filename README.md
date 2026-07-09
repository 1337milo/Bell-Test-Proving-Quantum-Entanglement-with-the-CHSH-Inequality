# Bell Test — Proving Quantum Entanglement with the CHSH Inequality

A self-contained Python experiment that replicates the mathematics behind the
**2022 Nobel Prize in Physics** (Aspect, Clauser, Zeilinger) using IBM Qiskit — 
on both a local simulator and **real IBM superconducting qubit hardware**.

> **Disclaimer:** This is a personal learning project.  
> Views and code are my own and do not represent IBM.

---

## What This Experiment Does

This code performs a **CHSH Bell test** — the definitive experiment that rules out
Einstein's "hidden variables" hypothesis and certifies quantum entanglement is real.

**The key question:** Can correlations between two particles be explained by
pre-set classical values (like a cheat sheet in each particle), or do they require
genuine quantum entanglement?

**The answer:** The CHSH inequality provides a number — the **S value** — that
any local hidden-variable theory must keep below 2. Quantum mechanics can reach
up to 2√2 ≈ 2.828 (the Tsirelson bound). We measure it. Nature answers.

### Our Results

| Backend | S value | Classical limit | Verdict |
|---------|---------|-----------------|---------|
| Noiseless AerSimulator | **+2.806** | ≤ 2.000 | ✅ Bell violation |
| AerSimulator + ibm_fez noise model | **+2.668** | ≤ 2.000 | ✅ Bell violation |
| **Real ibm_marrakesh hardware** | **+2.522** | ≤ 2.000 | ✅ **Bell violation on real qubits** |
| Theory maximum (Tsirelson bound) | 2.828 | — | Reference |

Real hardware job ID: `d976fn2f47jc73a6cbhg` · ibm_marrakesh · 156 qubits  
Wall-clock time: 31 seconds (~30s queue + sub-second execution) · 16,384 total measurements

**S = 2.522 is 21.5σ above the classical limit of 2.** All three runs certify
entanglement via the CHSH witness theorem (Gisin 1991): any state producing |S| > 2
*must* be entangled — separable states are mathematically bounded by |S| ≤ 2.

Note: This is an educational demonstration on co-located qubits. It is **not**
loophole-free (both qubits are on the same chip). The loophole-free experiment
was first achieved by Hensen et al. (Delft, 2015).

---

## The Math in One Line

```
S = E(a,b) − E(a,b') + E(a',b) + E(a',b')

Where E(a,b) = (count_same − count_diff) / total_shots

|S| ≤ 2  →  local hidden-variable theory possible
|S| > 2  →  local realism ruled out; qubits must be entangled
```

Quantum prediction for a maximally entangled Bell state with this code's
Ry-gate convention:

```
E(a, b) = cos(2·(a − b))
```

At the optimal CHSH angles (a=0, a'=π/4, b=π/8, b'=3π/8):

```
E(a,b)   = cos(2·(0   − π/8))  = +1/√2 ≈ +0.7071
E(a,b')  = cos(2·(0   − 3π/8)) = −1/√2 ≈ −0.7071
E(a',b)  = cos(2·(π/4 − π/8))  = +1/√2 ≈ +0.7071
E(a',b') = cos(2·(π/4 − 3π/8)) = +1/√2 ≈ +0.7071

S = (+0.7071) − (−0.7071) + (+0.7071) + (+0.7071) = 4/√2 = 2√2 ≈ 2.828
```

---

## The Circuit in Three Gates

```
q0: ──[H]──●──[Ry(2a)]──[M]──   ← Alice measures at angle a
q1: ───────⊕──[Ry(2b)]──[M]──   ← Bob   measures at angle b

H      = Hadamard: |0⟩ → (|0⟩+|1⟩)/√2  (superposition)
CNOT   = entangles: (|0⟩+|1⟩)/√2 ⊗ |0⟩ → (|00⟩+|11⟩)/√2  (Bell state |Φ⁺⟩)
Ry(2θ) = rotates measurement axis to angle θ on the Bloch sphere
```

**Why Ry(2θ) and not Ry(θ)?**  
The Ry gate uses a half-angle convention: Ry(θ)|0⟩ = cos(θ/2)|0⟩ + sin(θ/2)|1⟩.
To rotate the *measurement axis* by φ on the Bloch sphere, the gate parameter must
be 2φ. This is the SU(2)→SO(3) homomorphism: quantum spinors require twice the
rotation angle of the classical rotation they represent.

---

## File Structure

```
bell-test-quantum/
├── bell_test.py                    # Local experiment — no IBM account needed
├── bell_test_hardware.py           # Real hardware run — needs IBM Quantum account
├── bell_test_hardware_retrieve.py  # Retrieve interrupted hardware job
├── requirements.txt                # Base dependencies (simulator only)
├── requirements-hardware.txt       # Extra deps for hardware scripts
├── CONTRIBUTING.md
├── LICENSE
└── results/
    ├── bell_results.txt            # Simulator S values
    ├── bell_hardware_results.txt   # Real hardware S=2.522
    ├── bell_hardware_job_id.txt    # Job ID for verification
    ├── bell_correlation_curve.png  # Correlation sweep + S sweep plot
    └── bell_bloch_sphere.png       # Density matrix portrait
```

---

## Quick Start (No IBM Account Needed)

Runs entirely on your laptop using the local noiseless simulator and the
FakeFez hardware noise model (ibm_fez calibration data embedded in Qiskit).

### Prerequisites

- Python 3.11+
- 2–5 minutes

### Install and run

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/bell-test-quantum.git
cd bell-test-quantum

# Create virtual environment
python -m venv .venv
source .venv/bin/activate          # macOS/Linux
.venv\Scripts\Activate.ps1        # Windows PowerShell

# Install dependencies
pip install -r requirements.txt

# Run
python bell_test.py
```

**Expected output:**
```
Noiseless simulator  : S = +2.806  ** BELL VIOLATION **
FakeFez noise model  : S = +2.668  ** BELL VIOLATION **
```

---

## Run on Real IBM Quantum Hardware

Requires a free IBM Quantum account.

### Setup

1. Create a free account at [https://quantum.cloud.ibm.com](https://quantum.cloud.ibm.com)
2. Copy your API token from the [account page](https://quantum.cloud.ibm.com/account)
3. Create a `.env` file in the project root:
   ```
   IBM_QUANTUM_TOKEN=paste_your_token_here
   ```
   ⚠️ **Never commit your `.env` file.** It is listed in `.gitignore`.

4. Install the hardware dependencies:
   ```bash
   pip install -r requirements.txt -r requirements-hardware.txt
   ```

5. Run:
   ```bash
   python bell_test_hardware.py
   ```

The script selects the least-busy backend automatically, submits one batch job,
and polls for results. If interrupted, retrieve results later:

```bash
python bell_test_hardware_retrieve.py <JOB_ID>
# or, if job ID was saved automatically:
python bell_test_hardware_retrieve.py
```

**Expected output on real hardware:**
```
S = +2.522    *** BELL VIOLATION ***   (21.5σ above classical limit)
```

---

## Output Files

| File | What you see |
|------|-------------|
| `results/bell_correlation_curve.png` | Left: cosine correlation vs angle. Right: S vs angle sweep with Bell violation zone highlighted. |
| `results/bell_bloch_sphere.png` | Density matrix heatmaps: entangled Bell state vs separable state. |
| `results/bell_results.txt` | Numerical S values, violation amount, noise cost. |
| `results/bell_hardware_results.txt` | Real hardware S value, all four E values, comparison. |
| `results/bell_hardware_comparison.png` | Bar chart: Simulator vs FakeFez vs Real hardware. |

---

## Key Concepts

### The Bell State
```
|Φ⁺⟩ = (|00⟩ + |11⟩) / √2
```
50% chance both qubits measure 0, 50% chance both measure 1. Never one-zero.
This is the maximally entangled state prepared by H + CNOT.

### The Correlation E(a,b)
How much Alice's and Bob's results agree across thousands of measurements.
`E = +1` means perfect agreement. `E = −1` means perfect anti-correlation.
For the Bell state with this code's gate convention: `E(a, b) = cos(2·(a − b))`.

### Why the Classical Limit is 2
Bell's algebraic proof (1964): for any four binary ±1 values (classical hidden
variables), the combination `|ab − ab' + a'b + a'b'|` is **always ≤ 2**.
This is a pure mathematical fact about four numbers — not a physical assumption.
Quantum correlations exceed 2 because the results are *created* at measurement,
not retrieved from a pre-set list. There is no cheat sheet.

### The Tsirelson Bound (2√2)
Quantum mechanics also has a limit. Boris Tsirelson proved in 1980 that no
quantum state can produce |S| > 2√2 ≈ 2.828. Our noiseless simulator reaches
S = 2.806 — 99% of the theoretical maximum.

### Concurrence (Entanglement Strength)
The measured S = 2.522 implies a concurrence (entanglement purity) lower bound
of **C ≥ 0.77** (out of a maximum of 1.0 for a perfectly entangled state).
Noise on real hardware degrades the Bell state from |Φ⁺⟩ toward a mixed state.

### Statistical Significance
With 4096 shots per circuit, the standard deviation of S is σ_S ≈ 0.024.
Our violation of 0.522 above the classical limit is **21.5σ** — effectively zero
probability of occurring by chance.

---

## IBM Open Plan — No Session Needed

The `bell_test_hardware.py` script uses `SamplerV2.run()` with a list of
circuits (batch mode), which works on the Open Plan without a Session.
This is the most efficient way to submit multiple circuits at once and avoids
Session overhead.

Available real backends (as of 2025): `ibm_fez`, `ibm_marrakesh`, `ibm_kingston`
(all 156 qubits). The script auto-selects the least-busy one.

---

## IBM Policy & Sharing

This repository uses a **personal GitHub account** with personal email as the
commit author. It is licensed under **Apache 2.0**, which is permissive
(use, modify, distribute, commercially — with attribution).

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `qiskit` | ≥ 2.0 | Quantum circuit building and transpilation |
| `qiskit-aer` | ≥ 0.17 | Local noiseless simulator + FakeFez noise model |
| `qiskit-ibm-runtime` | ≥ 0.47 | IBM Quantum cloud API, SamplerV2 |
| `numpy` | ≥ 1.24 | Numerical operations |
| `matplotlib` | ≥ 3.7 | Plotting |
| `python-dotenv` | ≥ 1.0 | Load `.env` API token (hardware only) |

---

## References

1. Bell, J.S. (1964). "On the Einstein Podolsky Rosen Paradox." *Physics* 1(3), 195–200.
2. Clauser, Horne, Shimony, Holt (1969). "Proposed experiment to test local hidden-variable theories." *PRL* 23(15), 880.
3. Aspect, Grangier, Roger (1982). "Experimental Realization of EPR-Bohm Gedankenexperiment." *PRL* 49(2), 91.
4. Tsirelson, B.S. (1980). "Quantum generalizations of Bell's inequality." *Lett. Math. Phys.* 4(2), 93–100.
5. Gisin, N. (1991). "Bell's inequality holds for all non-product quantum states." *Phys. Lett. A* 154(5–6), 201–202.
6. Hensen et al. (2015). "Loophole-free Bell inequality violation." *Nature* 526, 682–686.
7. The Nobel Prize in Physics 2022. https://www.nobelprize.org/prizes/physics/2022/

---

## License

Apache License 2.0 — see [LICENSE](LICENSE).

You are free to use, modify, and distribute this code for any purpose including
commercial use, as long as you include the licence notice.

---

## Possible Extensions

- GHZ (3-qubit) entanglement test — stronger-than-CHSH violation
- Mermin inequality for N qubits
- Detection-efficiency loophole analysis
- Quantum state tomography (reconstruct the full density matrix)
- Noise mitigation with Qiskit's built-in error suppression

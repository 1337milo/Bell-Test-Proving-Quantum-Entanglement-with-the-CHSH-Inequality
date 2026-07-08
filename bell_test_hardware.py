"""
Bell Test — Real IBM Quantum Hardware
======================================

Submits the CHSH Bell inequality test to a real IBM superconducting qubit
processor via the IBM Quantum cloud API (Open Plan — no paid subscription needed).

What this script does:
  1. Connects to IBM Quantum (needs a free account + API token)
  2. Selects the least-busy real backend automatically
  3. Builds the 4 Bell circuits for the CHSH S-parameter
  4. Transpiles to native gates (rz, sx, cz, x) with maximum optimisation
  5. Submits all 4 circuits as ONE batch job (minimises queue hits)
  6. Polls for results with a live progress display
  7. Computes S and compares to classical limit and simulator
  8. Saves results/bell_hardware_results.txt and results/bell_hardware_comparison.png

CHSH angles (Ry gate convention, not Bloch-sphere angles):
  Alice: a = 0,     a' = π/4     (0°, 45°)
  Bob:   b = π/8,   b' = 3π/8   (22.5°, 67.5°)

  These maximise S.  At the noiseless limit: S = 2√2 ≈ 2.828.
  On real hardware expect: S ≈ 2.40 – 2.70 (still > 2 = Bell violation).

Setup:
  1. Create a free account at https://quantum.cloud.ibm.com
  2. Copy your API token from https://quantum.cloud.ibm.com/account
  3. Create a .env file in this directory:
       IBM_QUANTUM_TOKEN=paste_your_token_here
  4. Run:  python bell_test_hardware.py

Outputs:
  results/bell_hardware_results.txt    - S values, E values, job ID
  results/bell_hardware_job_id.txt     - job ID (saved immediately on submit)
  results/bell_hardware_comparison.png - bar chart: Sim vs FakeFez vs Hardware

Note:
  If the script is interrupted while waiting, use bell_test_hardware_retrieve.py
  to fetch the result by job ID.

Author:  Milad Love
License: Apache 2.0

Disclaimer: This is a personal learning project. Views and code are my own
and do not represent IBM.
"""

import os
import sys
import time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

os.makedirs("results", exist_ok=True)

SHOTS = 4096   # measurements per circuit — gives ~1% statistical precision

# Standard CHSH angles that achieve S = 2√2 at the noiseless limit.
# These are Ry GATE angles.  Bloch-sphere measurement-axis rotations are double.
ALICE_ANGLES = [0,          np.pi / 4]   # 0°, 45°
BOB_ANGLES   = [np.pi / 8,  3*np.pi/8]  # 22.5°, 67.5°

# Reference values from local simulations (bell_test.py)
S_SIM     = 2.8062   # noiseless AerSimulator
S_FAKEFEZ = 2.6675   # AerSimulator + ibm_fez noise model

print("=" * 70)
print("Bell Test — Real IBM Quantum Hardware")
print("=" * 70)
print()
print(f"  Classical limit (hidden variables) : |S| ≤ 2.0000")
print(f"  Quantum maximum (Tsirelson bound)  : |S| ≤ {2*np.sqrt(2):.4f}")
print()

# ── Step 1: Connect ─────────────────────────────────────────────────────────────
print("Step 1: Connecting to IBM Quantum...")
load_dotenv()
TOKEN = os.getenv("IBM_QUANTUM_TOKEN")
if not TOKEN:
    print("  ERROR: IBM_QUANTUM_TOKEN not found.")
    print("  Create a .env file:  IBM_QUANTUM_TOKEN=your_token_here")
    print("  Get your token at:   https://quantum.cloud.ibm.com/account")
    sys.exit(1)

service = QiskitRuntimeService(channel="ibm_quantum_platform", token=TOKEN)
print("  Connected ✓")

# ── Step 2: Select backend ──────────────────────────────────────────────────────
print("\nStep 2: Selecting least-busy real backend...")
backend = service.least_busy(min_num_qubits=2, operational=True, simulator=False)
try:
    queue_depth = backend.status().pending_jobs
except Exception:
    queue_depth = "unknown"
print(f"  Backend : {backend.name}  ({backend.num_qubits} qubits)")
print(f"  Queue   : {queue_depth} jobs ahead")

# ── Step 3: Build Bell circuits ─────────────────────────────────────────────────
print("\nStep 3: Building CHSH Bell circuits...")

def bell_circuit(alice_angle: float, bob_angle: float, name: str = "") -> QuantumCircuit:
    """
    Bell state |Φ⁺⟩ with rotated measurement bases.

    State preparation:
      H on q0  →  (|0⟩ + |1⟩)/√2
      CNOT     →  (|00⟩ + |11⟩)/√2  =  |Φ⁺⟩

    Measurement rotation:
      Ry(2a) on q0  — Alice's measurement axis rotated by angle a on Bloch sphere
      Ry(2b) on q1  — Bob's measurement axis rotated by angle b on Bloch sphere
      Factor-of-2: SU(2)→SO(3) half-angle convention.

    Resulting correlation:  E(a, b) = cos(2·(a − b))
    """
    qc = QuantumCircuit(2, 2, name=name)
    qc.h(0)
    qc.cx(0, 1)
    qc.ry(2 * alice_angle, 0)
    qc.ry(2 * bob_angle,   1)
    qc.measure([0, 1], [0, 1])
    return qc

angle_pairs = [
    (ALICE_ANGLES[0], BOB_ANGLES[0],  "E_ab"),
    (ALICE_ANGLES[0], BOB_ANGLES[1],  "E_abp"),
    (ALICE_ANGLES[1], BOB_ANGLES[0],  "E_apb"),
    (ALICE_ANGLES[1], BOB_ANGLES[1],  "E_apbp"),
]
circuits_logical = [bell_circuit(a, b, nm) for a, b, nm in angle_pairs]

print(f"  {'Circuit':<10} {'Alice':>8} {'Bob':>8}   {'Theory E':>10}")
print(f"  {'-'*46}")
for (a, b, nm) in angle_pairs:
    print(f"  {nm:<10} {np.degrees(a):>7.1f}°  {np.degrees(b):>7.1f}°   "
          f"{np.cos(2*(a-b)):>+10.4f}")

# ── Step 4: Transpile ───────────────────────────────────────────────────────────
print("\nStep 4: Transpiling to native gate set...")
circuits_t = transpile(circuits_logical, backend=backend,
                       optimization_level=3, seed_transpiler=42)
for qc, (_, _, nm) in zip(circuits_t, angle_pairs):
    print(f"  {nm}: depth={qc.depth()}  ops={dict(qc.count_ops())}")

# ── Step 5: Submit ──────────────────────────────────────────────────────────────
print(f"\nStep 5: Submitting {len(circuits_t)} circuits as one batch job...")
sampler = SamplerV2(mode=backend)
sampler.options.default_shots = SHOTS
t_submit = time.time()
job = sampler.run(circuits_t)
job_id = job.job_id()
print(f"  Job ID : {job_id}")
print(f"  Track  : https://quantum.cloud.ibm.com/jobs/{job_id}")

with open("results/bell_hardware_job_id.txt", "w") as f:
    f.write(f"Job ID  : {job_id}\nBackend : {backend.name}\n"
            f"Submitted: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}\n"
            f"Shots   : {SHOTS}\n")
print("  Job ID saved to results/bell_hardware_job_id.txt")

# ── Step 6: Wait ────────────────────────────────────────────────────────────────
print("\nStep 6: Waiting for results (Ctrl+C to interrupt — job ID is saved)...")
spinner, spin_i = ["|", "/", "-", "\\"], 0
t_wait = time.time()
while True:
    try:
        status_str = str(job.status())
        elapsed = time.time() - t_wait
        m, s = divmod(int(elapsed), 60)
        print(f"\r  [{spinner[spin_i%4]}] {status_str:<22}  {m:02d}:{s:02d}",
              end="", flush=True)
        spin_i += 1
        if "DONE" in status_str.upper():
            print(f"\r  [✓] Done in {m:02d}:{s:02d}                                ")
            break
        if any(x in status_str.upper() for x in ("ERROR", "FAILED", "CANCEL")):
            print(f"\n  [✗] Job ended: {status_str}")
            sys.exit(1)
        time.sleep(15)
    except KeyboardInterrupt:
        print(f"\n  Interrupted.  Retrieve later:\n"
              f"    python bell_test_hardware_retrieve.py {job_id}")
        sys.exit(0)

t_total = time.time() - t_submit

# ── Step 7: Extract ─────────────────────────────────────────────────────────────
print("\nStep 7: Extracting counts...")
result = job.result()

def get_counts(pub_result) -> dict:
    data = pub_result.data
    for attr in ("c", "meas", "cr"):
        if hasattr(data, attr):
            return getattr(data, attr).get_counts()
    return data.get_counts()

def correlation(counts: dict) -> float:
    same  = counts.get("00", 0) + counts.get("11", 0)
    diff  = counts.get("01", 0) + counts.get("10", 0)
    total = same + diff
    return (same - diff) / total if total > 0 else 0.0

E_hw = []
for i, pub_res in enumerate(result):
    raw = get_counts(pub_res)
    norm = {k.replace(" ", "")[-2:]: 0 for k in ("00", "01", "10", "11")}
    for k, v in raw.items():
        key = k.replace(" ", "")[-2:]
        norm[key] = norm.get(key, 0) + v
    E_hw.append(correlation(norm))
    print(f"  {angle_pairs[i][2]}: counts={norm}  E={E_hw[-1]:+.4f}")

# ── Step 8: Compute S ───────────────────────────────────────────────────────────
S_hw = E_hw[0] - E_hw[1] + E_hw[2] + E_hw[3]
violation = abs(S_hw) - 2.0

print(f"\n  S = {E_hw[0]:+.4f} - ({E_hw[1]:+.4f}) + {E_hw[2]:+.4f} + {E_hw[3]:+.4f} = {S_hw:+.4f}")
print()
print("=" * 70)
print(f"  Noiseless simulator   : +{S_SIM:.4f}")
print(f"  ibm_fez noise model   : +{S_FAKEFEZ:.4f}")
print(f"  Real hardware         : {S_hw:+.4f}  {'*** BELL VIOLATION ***' if violation>0 else '(no violation)'}")
print(f"  Classical limit       : 2.0000")
print("=" * 70)

# ── Step 9: Save results ────────────────────────────────────────────────────────
lines = [
    "BELL TEST — REAL HARDWARE RESULTS", "=" * 60, "",
    f"Backend  : {backend.name}", f"Job ID   : {job_id}",
    f"Shots    : {SHOTS} per circuit", f"Run time : {t_total:.0f}s", "",
    "MEASURED E VALUES", "-" * 40,
]
labels = ["E(a,  b )", "E(a,  b')", "E(a', b )", "E(a', b')"]
for lbl, E_m, (a, b, _) in zip(labels, E_hw, angle_pairs):
    lines.append(f"  {lbl}: measured={E_m:+.4f}  "
                 f"theory={np.cos(2*(a-b)):+.4f}  "
                 f"deviation={E_m-np.cos(2*(a-b)):+.4f}")
lines += [
    "", "CHSH S PARAMETER", "-" * 40,
    f"  Classical limit  : |S| <= 2.0000",
    f"  Quantum maximum  : |S| <= {2*np.sqrt(2):.4f}",
    f"  Noiseless sim    : S = +{S_SIM:.4f}  (violation +{S_SIM-2:.4f})",
    f"  FakeFez noise    : S = +{S_FAKEFEZ:.4f}  (violation +{S_FAKEFEZ-2:.4f})",
    f"  Real hardware    : S = {S_hw:+.4f}  "
    + (f"(violation +{violation:.4f})" if violation > 0 else "(no violation)"),
    "", "BELL VIOLATION CONFIRMED" if violation > 0 else "Bell violation NOT observed",
]
with open("results/bell_hardware_results.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("Saved: results/bell_hardware_results.txt")

# ── Step 10: Comparison chart ────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 6))
fig.patch.set_facecolor("#0a0e1a")
ax.set_facecolor("#0d1220")
ax.tick_params(colors="white", labelsize=10)
for sp in ax.spines.values():
    sp.set_edgecolor("#2a3550")

bar_labels = ["Noiseless\nSimulator", "ibm_fez\nNoise Model",
              f"Real Hardware\n({backend.name})"]
values = [S_SIM, S_FAKEFEZ, abs(S_hw)]
bars = ax.bar(bar_labels, values, color=["#22c55e", "#f59e0b", "#7c5cd8"],
              width=0.55, edgecolor="white", linewidth=0.6, alpha=0.92)
for bar, val in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
            f"{val:.4f}", ha="center", va="bottom",
            fontsize=13, fontweight="bold", color="white")
ax.axhline(2.0,           color="#da1e28", ls="--", lw=1.5,
           label="Classical limit |S| = 2.000")
ax.axhline(2*np.sqrt(2),  color="#78a9ff", ls=":",  lw=1.2,
           label=f"Quantum max 2√2 = {2*np.sqrt(2):.3f}")
ax.fill_between([-0.5, 2.5], 2.0, 2*np.sqrt(2),
                color="#ffb000", alpha=0.08, label="Bell violation zone")
ax.set_ylim(1.5, 3.1)
ax.set_ylabel("CHSH parameter  S", color="white", fontsize=12)
ax.set_title(f"Bell Test — CHSH S-parameter Comparison\n"
             f"Real hardware ({backend.name}) vs Simulators",
             color="white", fontsize=13, fontweight="bold", pad=12)
ax.legend(loc="lower right", fontsize=9, facecolor="#161b2e",
          edgecolor="#2a3550", labelcolor="white", framealpha=0.9)
ax.tick_params(axis="x", colors="white", labelsize=11)
plt.tight_layout()
plt.savefig("results/bell_hardware_comparison.png",
            dpi=200, bbox_inches="tight", facecolor="#0a0e1a")
plt.close()
print("Saved: results/bell_hardware_comparison.png")
print()
print("=" * 70)
print("DONE.")
print("=" * 70)

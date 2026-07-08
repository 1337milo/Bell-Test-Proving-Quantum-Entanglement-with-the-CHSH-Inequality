"""
Bell Test Hardware — Result Retrieval
=======================================

Use this if bell_test_hardware.py was interrupted while waiting for results.
It reconnects to IBM Quantum and fetches the job result by ID.

Usage:
  python bell_test_hardware_retrieve.py <JOB_ID>

  Or, without arguments, it reads the job ID from results/bell_hardware_job_id.txt:
  python bell_test_hardware_retrieve.py

Author:  Milad Love
License: Apache 2.0

Disclaimer: This is a personal learning project. Views and code are my own
and do not represent IBM.
"""

import os
import sys
import numpy as np
from dotenv import load_dotenv
from qiskit_ibm_runtime import QiskitRuntimeService

ALICE_ANGLES = [0,          np.pi / 4]
BOB_ANGLES   = [np.pi / 8,  3*np.pi/8]
angle_pairs  = [
    (ALICE_ANGLES[0], BOB_ANGLES[0],  "E(a,  b )"),
    (ALICE_ANGLES[0], BOB_ANGLES[1],  "E(a,  b')"),
    (ALICE_ANGLES[1], BOB_ANGLES[0],  "E(a', b )"),
    (ALICE_ANGLES[1], BOB_ANGLES[1],  "E(a', b')"),
]

# ── Get job ID ──────────────────────────────────────────────────────────────────
if len(sys.argv) > 1:
    job_id = sys.argv[1]
    print(f"Using job ID from command line: {job_id}")
else:
    id_file = "results/bell_hardware_job_id.txt"
    if not os.path.exists(id_file):
        print("ERROR: No job ID provided and results/bell_hardware_job_id.txt not found.")
        print("Usage: python bell_test_hardware_retrieve.py <JOB_ID>")
        sys.exit(1)
    with open(id_file) as f:
        for line in f:
            if line.startswith("Job ID"):
                job_id = line.split(":")[1].strip()
                break
    print(f"Using job ID from {id_file}: {job_id}")

# ── Connect ─────────────────────────────────────────────────────────────────────
load_dotenv()
TOKEN = os.getenv("IBM_QUANTUM_TOKEN")
service = QiskitRuntimeService(channel="ibm_quantum_platform", token=TOKEN)
job = service.job(job_id)
print(f"Job status: {job.status()}")

if "DONE" not in str(job.status()).upper():
    print("Job is not done yet. Re-run this script when it completes.")
    print(f"Track at: https://quantum.cloud.ibm.com/jobs/{job_id}")
    sys.exit(0)

# ── Extract results ─────────────────────────────────────────────────────────────
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
print("\nMeasured counts:")
for i, pub_res in enumerate(result):
    raw  = get_counts(pub_res)
    norm = {}
    for k, v in raw.items():
        key = k.replace(" ", "")[-2:]
        norm[key] = norm.get(key, 0) + v
    E = correlation(norm)
    E_hw.append(E)
    E_th = np.cos(2 * (angle_pairs[i][0] - angle_pairs[i][1]))
    print(f"  {angle_pairs[i][2]}: counts={norm}  E={E:+.4f}  theory={E_th:+.4f}")

S_hw = E_hw[0] - E_hw[1] + E_hw[2] + E_hw[3]
violation = abs(S_hw) - 2.0

print()
print("=" * 60)
print(f"  S = {S_hw:+.4f}")
print(f"  Classical limit: 2.0000  |  Quantum max: {2*np.sqrt(2):.4f}")
if violation > 0:
    print(f"  BELL VIOLATION: +{violation:.4f} above classical limit  ✓")
    print(f"  Significance  : ~{violation/0.024:.1f}σ  (σ_S ≈ 0.024 for 4096 shots)")
else:
    print("  Bell violation not detected this run.")
print("=" * 60)

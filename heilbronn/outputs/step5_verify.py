#!/usr/bin/env python3
"""
STEP 5: independent, from-scratch verification of the Heilbronn n=12 config.
- Recompute the minimum triangle area over ALL C(12,3)=220 triangles using the
  exact cross-product formula 0.5*|(p2-p1) x (p3-p1)| (float64 AND mpmath 50-dp).
- Confirm all 12 points lie in [0,1]^2 (no tolerance violation).
- Confirm no three points are (near-)collinear (min area not ~0).
Also writes the final solution file outputs/benchmark/heilbronn_n12.py.
"""
import json, itertools, os
from mpmath import mp, mpf, fabs

mp.dps = 50
REC = mpf("0.0325988586918197")

best = json.load(open("boundary_results.json"))
pts = best["best_points"]
assert len(pts) == 12, "need 12 points"
# clip into [0,1] exactly (removes ~1e-9 numerical overshoot; area change negligible)
pts = [[min(1.0, max(0.0, x)), min(1.0, max(0.0, y))] for x, y in pts]

# --- bounds check ---
oob = [(i, p) for i, p in enumerate(pts) if p[0] < -1e-9 or p[0] > 1+1e-9 or p[1] < -1e-9 or p[1] > 1+1e-9]
print("points in [0,1]^2:", "OK" if not oob else f"VIOLATION {oob}")

# --- float64 min area from scratch ---
def area_f(a, b, c):
    return 0.5*abs((b[0]-a[0])*(c[1]-a[1]) - (c[0]-a[0])*(b[1]-a[1]))

min_f = float("inf"); worst = None
for i, j, k in itertools.combinations(range(12), 3):
    A = area_f(pts[i], pts[j], pts[k])
    if A < min_f:
        min_f = A; worst = (i, j, k)
print(f"float64  min area = {min_f:.15f}  worst triangle {worst}")

# --- mpmath high-precision min area from scratch ---
P = [(mpf(str(x)), mpf(str(y))) for x, y in pts]
def area_mp(a, b, c):
    return mpf("0.5")*fabs((b[0]-a[0])*(c[1]-a[1]) - (c[0]-a[0])*(b[1]-a[1]))
min_mp = None
for i, j, k in itertools.combinations(range(12), 3):
    A = area_mp(P[i], P[j], P[k])
    if min_mp is None or A < min_mp:
        min_mp = A
print(f"mpmath   min area = {mp.nstr(min_mp, 20)}")

# --- collinearity check ---
print("collinear (area~0):", "NONE (OK)" if min_mp > mpf("1e-6") else "DEGENERATE!")

# --- record comparison ---
print(f"world record        = {mp.nstr(REC, 20)}")
print(f"exceeds 0.0307      : {min_mp > mpf('0.0307')}")
print(f"exceeds record      : {min_mp > REC}   (diff = {mp.nstr(min_mp-REC, 6)})")

# --- write final solution file (EXACT required format, nothing extra) ---
os.makedirs("benchmark", exist_ok=True)
lines = ["def proposed_solution():\n", "    return {\"points\": [\n"]
for x, y in pts:
    lines.append(f"        [{repr(float(x))}, {repr(float(y))}],\n")
lines.append("    ]}\n")
with open("benchmark/heilbronn_n12.py", "w") as f:
    f.writelines(lines)
print("\nwrote benchmark/heilbronn_n12.py")

json.dump({"min_area_float64": min_f, "min_area_mpmath": mp.nstr(min_mp, 25),
           "in_bounds": not oob, "worst_triangle": worst,
           "exceeds_0_0307": bool(min_mp > mpf('0.0307')),
           "exceeds_record": bool(min_mp > REC)},
          open("step5_verification.json", "w"), indent=2)

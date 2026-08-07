#!/usr/bin/env python3
"""
Refine the D4-symmetric config with the 8 outer points fixed EXACTLY on the
square boundary (generic-orbit offset u = 0.5 => x in {0,1}), optimizing the
remaining free parameters (generic y-offset v, and axis offset a) to the true
boundary-constrained optimum. Guarantees all points lie in [0,1] exactly while
recovering the record value.
"""
import numpy as np
from itertools import combinations
from scipy.optimize import minimize_scalar, minimize
import json
from mpmath import mp, mpf, fabs
mp.dps = 60
TRIS = list(combinations(range(12), 3))
REC = 0.0325988586918197


def build(u, v, a):
    # generic orbit (size 8): (u,v),(-u,v),(u,-v),(-u,-v),(v,u),(-v,u),(v,-u),(-v,-u)
    g = [(u, v), (-u, v), (u, -v), (-u, -v), (v, u), (-v, u), (v, -u), (-v, -u)]
    # axis orbit (size 4): (a,0),(-a,0),(0,a),(0,-a)
    ax = [(a, 0), (-a, 0), (0, a), (0, -a)]
    return np.array(g + ax) + 0.5


def min_area(pts):
    m = 1e9
    for i, j, k in TRIS:
        A = 0.5*abs((pts[j, 0]-pts[i, 0])*(pts[k, 1]-pts[i, 1]) -
                    (pts[k, 0]-pts[i, 0])*(pts[j, 1]-pts[i, 1]))
        if A < m:
            m = A
    return m


def neg(x):
    v, a = x
    if not (0 < v < 0.5 and 0 < a < 0.5):
        return 1.0
    return -min_area(build(0.5, v, a))


# multistart local optimization over (v, a) with u fixed at 0.5 (points on boundary)
best = (-1, None)
rng = np.random.default_rng(0)
for _ in range(300):
    x0 = rng.uniform(0.05, 0.49, size=2)
    res = minimize(neg, x0, method="Nelder-Mead",
                   options={"xatol": 1e-14, "fatol": 1e-16, "maxiter": 8000})
    val = -res.fun
    if val > best[0]:
        best = (val, res.x)
val, (v, a) = best
pts = build(0.5, v, a)
pts = np.clip(pts, 0.0, 1.0)  # exact boundary; no overshoot possible since u=0.5

# high-precision recompute
P = [(mpf(str(x)), mpf(str(y))) for x, y in pts]
mm = None
for i, j, k in TRIS:
    A = mpf("0.5")*fabs((P[j][0]-P[i][0])*(P[k][1]-P[i][1]) - (P[k][0]-P[i][0])*(P[j][1]-P[i][1]))
    if mm is None or A < mm:
        mm = A
print(f"u=0.5 fixed  v={v:.12f}  a={a:.12f}")
print(f"float64 min area = {val:.15f}")
print(f"mpmath  min area = {mp.nstr(mm, 20)}")
print(f"record          = {REC}")
print(f"in [0,1]^2: {bool(np.all(pts>=0) and np.all(pts<=1))}")
print(f"exceeds 0.0307: {float(mm) > 0.0307} | vs record diff = {float(mm)-REC:.3e}")

json.dump({"best_min_area": float(val), "best_points": pts.tolist(),
           "params": {"u": 0.5, "v": float(v), "a": float(a)}},
          open("boundary_results.json", "w"), indent=2)
print("saved boundary_results.json")

#!/usr/bin/env python3
"""
Attempt to BEAT the Heilbronn n=12 record by searching lower-symmetry classes
than D4 (the record's class). Each class has MORE freedom than D4, so if a
better configuration exists it could appear here.

Classes (square centered at 0.5):
  C2  : 180-deg rotation. (x,y) & (1-x,1-y). 6 free points -> 12 params.
  D2  : rot180 + mirror x=1/2 + mirror y=1/2. Generic orbit size 4:
        (x,y),(1-x,y),(x,1-y),(1-x,1-y). 3 orbits -> 6 params.
  D1x : single mirror x=1/2. (x,y),(1-x,y). 6 orbits -> 12 params.
  D1d : single mirror across main diagonal. (x,y),(y,x). 6 orbits -> 12 params.
  asym: no symmetry, 24 params (SLSQP exact max-min, warm+random).
We maximize the TRUE minimum triangle area with multistart local optimization,
then high-precision recompute and compare to the record.
"""
import numpy as np
from itertools import combinations
from scipy.optimize import minimize
import json, sys, time

N = 12
TRIS = list(combinations(range(N), 3))
REC = 0.0325988586918197


def min_area(pts):
    m = 1e9
    for i, j, k in TRIS:
        a = 0.5*abs((pts[j, 0]-pts[i, 0])*(pts[k, 1]-pts[i, 1]) -
                    (pts[k, 0]-pts[i, 0])*(pts[j, 1]-pts[i, 1]))
        if a < m:
            m = a
    return m


def expand_C2(v):
    p = v.reshape(6, 2)
    q = 1.0 - p
    return np.vstack([p, q])


def expand_D2(v):
    o = v.reshape(3, 2)
    pts = []
    for x, y in o:
        pts += [(x, y), (1-x, y), (x, 1-y), (1-x, 1-y)]
    return np.array(pts)


def expand_D1x(v):
    p = v.reshape(6, 2)
    pts = []
    for x, y in p:
        pts += [(x, y), (1-x, y)]
    return np.array(pts)


def expand_D1d(v):
    p = v.reshape(6, 2)
    pts = []
    for x, y in p:
        pts += [(x, y), (y, x)]
    return np.array(pts)


def expand_asym(v):
    return v.reshape(12, 2)


EXP = {"C2": (expand_C2, 12), "D2": (expand_D2, 6),
       "D1x": (expand_D1x, 12), "D1d": (expand_D1d, 12),
       "asym": (expand_asym, 24)}


def neg(v, exp):
    pts = exp(v)
    if np.any(pts < -1e-9) or np.any(pts > 1+1e-9):
        return 1.0
    return -min_area(np.clip(pts, 0, 1))


def search(name, n_starts, rng, warm=None):
    exp, nd = EXP[name]
    best = (-1, None)
    for s in range(n_starts):
        if warm is not None and s % 4 == 0:
            v0 = warm + rng.normal(0, 0.03, size=nd)
            v0 = np.clip(v0, 0, 1)
        else:
            v0 = rng.uniform(0, 1, size=nd)
        # two-stage: Nelder-Mead then Powell refine
        r1 = minimize(neg, v0, args=(exp,), method="Nelder-Mead",
                      options={"maxiter": 6000, "xatol": 1e-12, "fatol": 1e-15})
        r2 = minimize(neg, r1.x, args=(exp,), method="Powell",
                      options={"maxiter": 6000, "xtol": 1e-12, "ftol": 1e-15})
        v = r2.x if -r2.fun > -r1.fun else r1.x
        val = min_area(np.clip(exp(v), 0, 1))
        if val > best[0]:
            best = (val, np.clip(exp(v), 0, 1))
    return best


def main():
    n_starts = int(sys.argv[1]) if len(sys.argv) > 1 else 120
    classes = sys.argv[2].split(",") if len(sys.argv) > 2 else ["C2", "D2", "D1x", "D1d"]
    rng = np.random.default_rng(7)
    # warm from record config for asym/C2/D2 if available
    warm_pts = None
    try:
        warm_pts = np.array(json.load(open("boundary_results.json"))["best_points"])
    except Exception:
        pass
    overall = (-1, None, None)
    t0 = time.time()
    for name in classes:
        warm = None
        if warm_pts is not None and name == "asym":
            warm = warm_pts.reshape(-1)
        val, pts = search(name, n_starts, rng, warm)
        tag = "BEATS RECORD!" if val > REC + 1e-12 else ("=rec" if abs(val-REC) < 1e-9 else "")
        print(f"{name:5s}: min_area = {val:.13f}  diff_vs_rec={val-REC:+.3e}  {tag}", flush=True)
        if val > overall[0]:
            overall = (val, pts, name)
    val, pts, name = overall
    print(f"\nBEST over classes = {val:.13f} via {name} | "
          f"{'BEATS RECORD' if val>REC+1e-12 else 'does NOT beat record'}  "
          f"(elapsed {time.time()-t0:.0f}s)")
    json.dump({"best_min_area": float(val), "best_points": pts.tolist(),
               "class": name, "beats_record": bool(val > REC + 1e-12)},
              open("symclass_results.json", "w"), indent=2)


if __name__ == "__main__":
    main()

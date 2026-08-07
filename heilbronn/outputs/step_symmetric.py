#!/usr/bin/env python3
"""
Heilbronn n=12: D4-symmetric solver.
The best-known n=12 optimum (Comellas-Yebra) is COMPLETELY SYMMETRIC (dihedral
group D4 of the square, order 8). 12 points must decompose into D4-orbits.
Since 12 = 8+4 = 4+4+4 (no fixed center point works: 12-1=11 not a sum of 8s/4s),
we parametrize by orbit "seeds" and optimize the few free parameters.

Orbit types (center of square at (0.5,0.5); u,v are offsets from center):
  generic (size 8): seed (u,v) -> (+-u,+-v) and (+-v,+-u)   [2 params]
  diagonal(size 4): seed  u    -> (+-u,+-u)                  [1 param]
  axis    (size 4): seed  u    -> (+-u,0),(0,+-u)            [1 param]
We try all decompositions and multistart over the seed params, maximizing the
true minimum triangle area. Then verify exactly.
"""
import numpy as np
from itertools import combinations
from scipy.optimize import minimize
import json, sys

N = 12
TRIS = list(combinations(range(N), 3))
REC = 0.0325988586918197


def expand(seeds):
    pts = []
    for typ, p in seeds:
        if typ == 'g':
            u, v = p
            pts += [(u, v), (-u, v), (u, -v), (-u, -v),
                    (v, u), (-v, u), (v, -u), (-v, -u)]
        elif typ == 'd':
            u = p[0]
            pts += [(u, u), (-u, -u), (u, -u), (-u, u)]
        elif typ == 'a':
            u = p[0]
            pts += [(u, 0), (-u, 0), (0, u), (0, -u)]
    return np.array(pts) + 0.5


def min_area(pts):
    m = 1e9
    for i, j, k in TRIS:
        a = 0.5 * abs((pts[j, 0]-pts[i, 0])*(pts[k, 1]-pts[i, 1]) -
                      (pts[k, 0]-pts[i, 0])*(pts[j, 1]-pts[i, 1]))
        if a < m:
            m = a
    return m


def unpack(v, template):
    seeds = []
    idx = 0
    for typ, np_ in template:
        seeds.append((typ, list(v[idx:idx+np_])))
        idx += np_
    return seeds


def neg_minarea(v, template):
    pts = expand(unpack(v, template))
    if np.any(pts < -1e-9) or np.any(pts > 1+1e-9):
        return 1.0
    return -min_area(pts)


TEMPLATES = {
    "8g+4d": [('g', 2), ('d', 1)],
    "8g+4a": [('g', 2), ('a', 1)],
    "4d+4a+4d": [('d', 1), ('a', 1), ('d', 1)],
    "4a+4a+4d": [('a', 1), ('a', 1), ('d', 1)],
    "4d+4d+4a": [('d', 1), ('d', 1), ('a', 1)],
    "4a+4a+4a": [('a', 1), ('a', 1), ('a', 1)],
}


def solve_template(template, n_starts, rng):
    ntot = sum(t[1] for t in template)
    best = (-1, None)
    for _ in range(n_starts):
        v0 = rng.uniform(0.02, 0.5, size=ntot)
        res = minimize(neg_minarea, v0, args=(template,), method="Nelder-Mead",
                       options={"maxiter": 3000, "xatol": 1e-12, "fatol": 1e-14})
        val = -res.fun
        if val > best[0]:
            pts = expand(unpack(res.x, template))
            if np.all(pts >= -1e-9) and np.all(pts <= 1+1e-9):
                best = (min_area(pts), pts)
    return best


def main():
    n_starts = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    rng = np.random.default_rng(2026)
    overall = (-1, None, None)
    for name, tmpl in TEMPLATES.items():
        val, pts = solve_template(tmpl, n_starts, rng)
        tag = ("BEATS REC" if val > REC else (">0.0307" if val > 0.0307 else ""))
        print(f"{name:12s}: min_area = {val:.10f}  {tag}", flush=True)
        if val > overall[0]:
            overall = (val, pts, name)
    val, pts, name = overall
    out = {"best_min_area": val, "best_points": pts.tolist(), "template": name}
    with open("sym_results.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSYMMETRIC BEST = {val:.10f} via {name} | " +
          ("BEATS RECORD" if val > REC else (">0.0307 OK" if val > 0.0307 else "below 0.0307")))


if __name__ == "__main__":
    main()

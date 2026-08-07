#!/usr/bin/env python3
"""
Heilbronn n=12: STEPS 3-4 LP-polish + high-precision SLSQP refine.

STEP 3-4 (LP polish): given a candidate, iterate:
  - compute all 220 exact triangle areas,
  - identify the critical set within `band` of the current min,
  - linearize each critical area: area_c(x+d) ~= area_c + grad_c . d,
  - solve LP:  max t  s.t.  area_c + grad_c.d >= t,  -TR<=d<=TR,  0<=x+d<=1,
    via scipy.optimize.linprog (HiGHS),
  - apply d, recompute exact areas; accept if true min improves else shrink TR.

We polish the D4-symmetric candidate and the step-1 candidates, keep the best,
and additionally run a high-precision SLSQP refine to squeeze float64 digits.
"""
import numpy as np
from itertools import combinations
from scipy.optimize import linprog, minimize
import json, sys

N = 12
TRIS = np.array(list(combinations(range(N), 3)))
I, J, K = TRIS[:, 0], TRIS[:, 1], TRIS[:, 2]
NT = len(TRIS)
REC = 0.0325988586918197


def areas(xy):
    p1, p2, p3 = xy[I], xy[J], xy[K]
    cross = (p2[:, 0]-p1[:, 0])*(p3[:, 1]-p1[:, 1]) - (p3[:, 0]-p1[:, 0])*(p2[:, 1]-p1[:, 1])
    return 0.5*np.abs(cross)


def true_min(xy):
    return float(areas(xy).min())


def grad_matrix(xy):
    p1, p2, p3 = xy[I], xy[J], xy[K]
    cross = (p2[:, 0]-p1[:, 0])*(p3[:, 1]-p1[:, 1]) - (p3[:, 0]-p1[:, 0])*(p2[:, 1]-p1[:, 1])
    s = 0.5*np.sign(cross)
    dx1 = -(p3[:, 1]-p1[:, 1]) + (p2[:, 1]-p1[:, 1]); dy1 = -(p2[:, 0]-p1[:, 0]) + (p3[:, 0]-p1[:, 0])
    dx2 = (p3[:, 1]-p1[:, 1]); dy2 = -(p3[:, 0]-p1[:, 0])
    dx3 = -(p2[:, 1]-p1[:, 1]); dy3 = (p2[:, 0]-p1[:, 0])
    G = np.zeros((NT, N, 2)); r = np.arange(NT)
    G[r, I, 0] = s*dx1; G[r, I, 1] = s*dy1
    G[r, J, 0] = s*dx2; G[r, J, 1] = s*dy2
    G[r, K, 0] = s*dx3; G[r, K, 1] = s*dy3
    return G.reshape(NT, 2*N)


def lp_polish(xy0, max_iter=500, TR0=0.02, band0=0.01, tol=1e-12):
    xy = xy0.copy(); TR = TR0; cur = true_min(xy); log = []
    for it in range(max_iter):
        a = areas(xy); amin = a.min(); band = max(band0, 3*TR)
        crit = np.where(a <= amin + band)[0]
        G = grad_matrix(xy)[crit]; ac = a[crit]; v = xy.reshape(-1)
        nc = len(crit)
        A_ub = np.hstack([-G, np.ones((nc, 1))]); b_ub = ac
        lb = np.maximum(-TR, -v); ub = np.minimum(TR, 1.0-v)
        bounds = [(lb[i], ub[i]) for i in range(2*N)] + [(None, None)]
        c = np.zeros(2*N+1); c[-1] = -1.0
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")
        if not res.success:
            TR *= 0.5
            if TR < tol: break
            continue
        d = res.x[:2*N]
        xy_new = np.clip((v+d).reshape(N, 2), 0.0, 1.0)
        new = true_min(xy_new)
        if new > cur + 1e-15:
            xy = xy_new; cur = new; TR = min(TR*1.3, 0.05); log.append((it, cur, TR, nc, "accept"))
        else:
            TR *= 0.5; log.append((it, cur, TR, nc, "shrink"))
            if TR < tol: break
    return xy, cur, log


# high-precision SLSQP refine (exact max-min NLP)
def slsqp_refine(xy0):
    def neg_t(z):
        g = np.zeros_like(z); g[-1] = -1.0; return -z[-1], g
    def cf(z):
        return areas(z[:2*N].reshape(N, 2)) - z[-1]
    def cj(z):
        G = grad_matrix(z[:2*N].reshape(N, 2))
        Jm = np.zeros((NT, 2*N+1)); Jm[:, :2*N] = G; Jm[:, -1] = -1.0; return Jm
    z0 = np.concatenate([xy0.reshape(-1), [true_min(xy0)]])
    bounds = [(0.0, 1.0)]*(2*N) + [(0.0, 0.2)]
    res = minimize(neg_t, z0, jac=True, method="SLSQP", bounds=bounds,
                   constraints=[{"type": "ineq", "fun": cf, "jac": cj}],
                   options={"maxiter": 1000, "ftol": 1e-16})
    xy = np.clip(res.x[:2*N].reshape(N, 2), 0, 1)
    return xy, true_min(xy)


def main():
    cands = []
    try:
        sym = json.load(open("sym_results.json"))
        cands.append(("symmetric", np.array(sym["best_points"])))
    except Exception:
        pass
    try:
        s1 = json.load(open("step1_results.json"))
        for i, p in enumerate(s1["top5_points"][:3]):
            cands.append((f"step1_{i}", np.array(p)))
    except Exception:
        pass

    overall = (-1, None, None, None)
    logs = {}
    for name, xy0 in cands:
        start = true_min(xy0)
        xy_lp, val_lp, log = lp_polish(xy0)
        xy_ref, val_ref = slsqp_refine(xy_lp)
        val = max(val_lp, val_ref)
        xy = xy_ref if val_ref >= val_lp else xy_lp
        logs[name] = {"start": start, "after_lp": val_lp, "after_refine": val_ref,
                      "lp_iters": len(log), "lp_accepts": sum(1 for l in log if l[4] == "accept")}
        print(f"{name:12s}: start={start:.10f} -> LP={val_lp:.10f} -> refine={val_ref:.10f}", flush=True)
        if val > overall[0]:
            overall = (val, xy, name, log)
    val, xy, name, log = overall
    out = {"best_min_area": val, "best_points": xy.tolist(), "best_source": name,
           "per_candidate": logs, "lp_log_tail": [list(l) for l in log[-15:]]}
    with open("step34_results.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nBEST after LP-polish + refine = {val:.12f} (from {name}) | " +
          ("BEATS RECORD" if val > REC else (">0.0307 OK" if val > 0.0307 else "below")))


if __name__ == "__main__":
    main()

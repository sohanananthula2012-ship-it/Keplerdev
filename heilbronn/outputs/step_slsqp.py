#!/usr/bin/env python3
"""
Heilbronn n=12: exact NLP via SLSQP + multistart + basin hopping.
Maximize t s.t. area_ijk >= t for all 220 triangles, points in [0,1]^2.
Variables z = [x_0,y_0,...,x_11,y_11, t]  (25,).
This is the strong global driver (Steps 1 improved + global search).
"""
import numpy as np
from itertools import combinations
from scipy.optimize import minimize
import json, sys, time

N = 12
TRIS = np.array(list(combinations(range(N), 3)))
I, J, K = TRIS[:, 0], TRIS[:, 1], TRIS[:, 2]
NT = len(TRIS)
REC = 0.0325988586918197


def areas_cross(xy):
    p1, p2, p3 = xy[I], xy[J], xy[K]
    cross = (p2[:, 0] - p1[:, 0]) * (p3[:, 1] - p1[:, 1]) - \
            (p3[:, 0] - p1[:, 0]) * (p2[:, 1] - p1[:, 1])
    return 0.5 * np.abs(cross), cross


def true_min(xy):
    a, _ = areas_cross(xy)
    return float(a.min())


def grad_area(xy):
    p1, p2, p3 = xy[I], xy[J], xy[K]
    cross = (p2[:, 0] - p1[:, 0]) * (p3[:, 1] - p1[:, 1]) - \
            (p3[:, 0] - p1[:, 0]) * (p2[:, 1] - p1[:, 1])
    s = 0.5 * np.sign(cross)
    dx1 = -(p3[:, 1] - p1[:, 1]) + (p2[:, 1] - p1[:, 1])
    dy1 = -(p2[:, 0] - p1[:, 0]) + (p3[:, 0] - p1[:, 0])
    dx2 = (p3[:, 1] - p1[:, 1]); dy2 = -(p3[:, 0] - p1[:, 0])
    dx3 = -(p2[:, 1] - p1[:, 1]); dy3 = (p2[:, 0] - p1[:, 0])
    G = np.zeros((NT, N, 2)); r = np.arange(NT)
    G[r, I, 0] = s * dx1; G[r, I, 1] = s * dy1
    G[r, J, 0] = s * dx2; G[r, J, 1] = s * dy2
    G[r, K, 0] = s * dx3; G[r, K, 1] = s * dy3
    return G.reshape(NT, 2 * N)


def neg_t(z):
    g = np.zeros_like(z); g[-1] = -1.0
    return -z[-1], g


def cons_f(z):
    xy = z[:2 * N].reshape(N, 2); t = z[-1]
    a, _ = areas_cross(xy)
    return a - t


def cons_jac(z):
    xy = z[:2 * N].reshape(N, 2)
    G = grad_area(xy)
    J_ = np.zeros((NT, 2 * N + 1))
    J_[:, :2 * N] = G
    J_[:, -1] = -1.0
    return J_


def slsqp_opt(xy0):
    t0 = true_min(xy0)
    z0 = np.concatenate([xy0.reshape(-1), [t0]])
    bounds = [(0.0, 1.0)] * (2 * N) + [(0.0, 0.2)]
    cons = [{"type": "ineq", "fun": cons_f, "jac": cons_jac}]
    res = minimize(neg_t, z0, jac=True, method="SLSQP", bounds=bounds,
                   constraints=cons, options={"maxiter": 300, "ftol": 1e-12})
    xy = np.clip(res.x[:2 * N].reshape(N, 2), 0, 1)
    return xy, true_min(xy)


def run(n_starts, hop_rounds, seed0=0, warm=None):
    rng = np.random.default_rng(seed0)
    t0 = time.time()
    best_val, best_xy = -1.0, None
    if warm is not None:
        best_xy = np.array(warm)
        best_val = true_min(best_xy)
        print(f"warm start: {best_val:.8f}", flush=True)
    for s in range(n_starts):
        xy, val = slsqp_opt(rng.random((N, 2)))
        if val > best_val:
            best_val, best_xy = val, xy
    print(f"Phase A ({n_starts}): best={best_val:.8f} in {time.time()-t0:.1f}s", flush=True)
    for r in range(hop_rounds):
        xy0 = best_xy.copy()
        k = int(rng.integers(1, N + 1))
        idx = rng.choice(N, size=k, replace=False)
        scale = 0.02 + 0.18 * rng.random()
        xy0[idx] += rng.normal(0, scale, size=(k, 2))
        xy0 = np.clip(xy0, 0, 1)
        xy, val = slsqp_opt(xy0)
        if val > best_val + 1e-12:
            best_val, best_xy = val, xy
            print(f"  hop {r}: {best_val:.8f}", flush=True)
    print(f"Phase B ({hop_rounds}): best={best_val:.8f} total {time.time()-t0:.1f}s", flush=True)
    return best_val, best_xy


def main():
    n_starts = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    hops = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    seed0 = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    warm = None
    if len(sys.argv) > 4:
        try:
            warm = json.load(open(sys.argv[4]))["best_points"]
        except Exception:
            warm = None
    val, xy = run(n_starts, hops, seed0, warm)
    out = {"best_min_area": val, "best_points": xy.tolist(), "seed0": seed0}
    with open("slsqp_results.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nBEST = {val:.10f} | " +
          ("BEATS RECORD" if val > REC else (">0.0307 OK" if val > 0.0307 else "below 0.0307")))


if __name__ == "__main__":
    main()

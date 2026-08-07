#!/usr/bin/env python3
"""
Heilbronn n=12: multi-start local optimization (STEP 1).
Maximize the minimum triangle area among 12 points in [0,1]^2.

Approach:
- Many random restarts.
- Local optimizer on a smooth softmin surrogate of the 220 triangle areas,
  optimized with L-BFGS-B (box constraints [0,1]) with an annealing schedule
  on the softmin sharpness beta.
- After each restart, record the TRUE min triangle area (exact formula).
"""
import numpy as np
from itertools import combinations
from scipy.optimize import minimize
import json, sys, time

N = 12
TRIS = np.array(list(combinations(range(N), 3)))  # (220,3)
I, J, K = TRIS[:, 0], TRIS[:, 1], TRIS[:, 2]


def areas(xy):
    """Signed-abs areas of all 220 triangles. xy shape (12,2)."""
    p1, p2, p3 = xy[I], xy[J], xy[K]
    cross = (p2[:, 0] - p1[:, 0]) * (p3[:, 1] - p1[:, 1]) - \
            (p3[:, 0] - p1[:, 0]) * (p2[:, 1] - p1[:, 1])
    return 0.5 * np.abs(cross)


def true_min(xy):
    return float(areas(xy).min())


def neg_softmin(v, beta):
    """Return -softmin and gradient wrt flat v (24,), softmin over areas."""
    xy = v.reshape(N, 2)
    p1, p2, p3 = xy[I], xy[J], xy[K]
    cross = (p2[:, 0] - p1[:, 0]) * (p3[:, 1] - p1[:, 1]) - \
            (p3[:, 0] - p1[:, 0]) * (p2[:, 1] - p1[:, 1])
    a = 0.5 * np.abs(cross)
    # softmin: -1/beta * log(sum exp(-beta*a)) ; stable
    m = a.min()
    w = np.exp(-beta * (a - m))
    sw = w.sum()
    softmin = m - np.log(sw) / beta  # approx min
    # gradient of softmin wrt a_t: w_t / sw
    dsm_da = w / sw
    # gradient of a_t wrt points: a = 0.5*|cross|, d|cross| = sign(cross)*dcross
    s = 0.5 * np.sign(cross)
    grad = np.zeros((N, 2))
    # cross = (x2-x1)(y3-y1) - (x3-x1)(y2-y1)
    dx1 = -(p3[:, 1] - p1[:, 1]) + (p2[:, 1] - p1[:, 1])   # d/dx1
    dy1 = -(p2[:, 0] - p1[:, 0]) + (p3[:, 0] - p1[:, 0])   # d/dy1
    dx2 = (p3[:, 1] - p1[:, 1])
    dy2 = -(p3[:, 0] - p1[:, 0])
    dx3 = -(p2[:, 1] - p1[:, 1])
    dy3 = (p2[:, 0] - p1[:, 0])
    c = dsm_da * s  # weight per triangle
    np.add.at(grad, (I, 0), c * dx1)
    np.add.at(grad, (I, 1), c * dy1)
    np.add.at(grad, (J, 0), c * dx2)
    np.add.at(grad, (J, 1), c * dy2)
    np.add.at(grad, (K, 0), c * dx3)
    np.add.at(grad, (K, 1), c * dy3)
    return -softmin, -grad.reshape(-1)


def optimize_one(seed, betas=(20, 60, 150, 400, 1000, 3000)):
    rng = np.random.default_rng(seed)
    v = rng.random(2 * N)
    bounds = [(0.0, 1.0)] * (2 * N)
    for beta in betas:
        res = minimize(neg_softmin, v, args=(beta,), jac=True, method="L-BFGS-B",
                       bounds=bounds, options={"maxiter": 500, "ftol": 1e-12, "gtol": 1e-10})
        v = res.x
    xy = v.reshape(N, 2)
    return xy, true_min(xy)


def main():
    n_starts = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    t0 = time.time()
    results = []
    best = None
    for s in range(n_starts):
        xy, tm = optimize_one(s)
        results.append((tm, xy))
        if best is None or tm > best[0]:
            best = (tm, xy, s)
    results.sort(key=lambda r: -r[0])
    top = results[:5]
    out = {
        "n_starts": n_starts,
        "elapsed_sec": round(time.time() - t0, 1),
        "best_min_area": best[0],
        "best_seed": best[2],
        "top5_min_areas": [round(r[0], 8) for r in top],
        "top5_points": [r[1].tolist() for r in top],
    }
    with open("step1_results.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"starts={n_starts} elapsed={out['elapsed_sec']}s")
    print("top5 true min areas:", out["top5_min_areas"])
    print("best:", best[0], "seed", best[2])


if __name__ == "__main__":
    main()

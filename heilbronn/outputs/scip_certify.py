#!/usr/bin/env python3
"""
Heilbronn certification via MINLP in SCIP (pyscipopt), following
Sudermann-Merx (arXiv:2603.11107): optimize-then-certify with symmetry breaking.

Model (maximize z = min triangle area):
  vars: x_i,y_i in [0,1]; A_t (signed area) in [-1/2,1/2]; b_t in {0,1}; z in [0, UB]
  A_t = 0.5*((xj-xi)(yk-yi) - (yj-yi)(xk-xi))          for t=(i,j,k)
  z <= A_t + (1 - b_t)      (big-M=1)   } together => z <= |A_t| for the sign b_t picks
  z <= -A_t + b_t           (big-M=1)   }
  Symmetry breaking (1-indexed points 1..n):
    x1=0, y2=0, x3=1, y4=1, x5=0 ; y1<=y5 ; x2<=x4 ; x6<=...<=xn
  Sign fixing: b_t=1 for k<=5 (T+),  b_t=0 for i=1,j=5 (T-)
  Bound: z <= UB (best-known Delta_{n-1} or Delta_n).

Usage: python scip_certify.py <n> <time_limit_sec> [UB] [threads]
Prints dual bound (upper), primal bound (best found), gap, status, and config.
"""
import sys, json
from itertools import combinations
from pyscipopt import Model, quicksum

# best-known / certified Delta_n values for upper bounds (unit square)
BEST = {5: 0.19245009, 6: 0.125, 7: 0.08385255, 8: 0.07234885,
        9: 0.05485416, 10: 0.04654660, 11: 0.03846154, 12: 0.03259886}


def build_and_solve(n, tlim, ub=None, threads=1):
    m = Model("heilbronn")
    m.setParam("limits/time", tlim)
    m.setParam("parallel/maxnthreads", threads)
    try:
        m.setParam("numerics/feastol", 1e-9)
    except Exception:
        pass
    x = {i: m.addVar(f"x{i}", lb=0, ub=1) for i in range(1, n+1)}
    y = {i: m.addVar(f"y{i}", lb=0, ub=1) for i in range(1, n+1)}
    UB = ub if ub is not None else BEST.get(n, 0.5)
    # small slack above best-known so a strictly-better solution is representable
    z = m.addVar("z", lb=0, ub=min(0.5, UB + 1e-3))

    tris = list(combinations(range(1, n+1), 3))
    A = {}
    b = {}
    for t in tris:
        i, j, k = t
        A[t] = m.addVar(f"A_{i}_{j}_{k}", lb=-0.5, ub=0.5)
        # signed area constraint (bilinear)
        expr = 0.5*((x[j]-x[i])*(y[k]-y[i]) - (y[j]-y[i])*(x[k]-x[i]))
        m.addCons(A[t] == expr)
        b[t] = m.addVar(f"b_{i}_{j}_{k}", vtype="B")
        # z <= |A_t| via sign selector, big-M = 1
        m.addCons(z <= A[t] + (1 - b[t]))
        m.addCons(z <= -A[t] + b[t])

    # symmetry breaking (requires n>=5)
    if n >= 5:
        m.addCons(x[1] == 0); m.addCons(y[2] == 0); m.addCons(x[3] == 1)
        m.addCons(y[4] == 1); m.addCons(x[5] == 0)
        m.addCons(y[1] <= y[5]); m.addCons(x[2] <= x[4])
        for i in range(6, n):
            m.addCons(x[i] <= x[i+1])
        # sign fixing
        for t in tris:
            i, j, k = t
            if k <= 5:
                m.addCons(b[t] == 1)     # T+ : CCW boundary triple
            if i == 1 and j == 5:
                m.addCons(b[t] == 0)     # T- : p1,p5 on left edge, y1<=y5

    m.setObjective(z, "maximize")
    m.optimize()

    status = m.getStatus()
    primal = m.getPrimalbound()
    dual = m.getDualbound()
    gap = m.getGap()
    out = {"n": n, "status": status, "primal": primal, "dual": dual,
           "gap": gap, "time": m.getSolvingTime(), "UB_used": UB}
    # extract config if a solution exists
    try:
        sol = m.getBestSol()
        pts = [[m.getSolVal(sol, x[i]), m.getSolVal(sol, y[i])] for i in range(1, n+1)]
        out["points"] = pts
    except Exception:
        out["points"] = None
    return out


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    tlim = float(sys.argv[2]) if len(sys.argv) > 2 else 60
    ub = float(sys.argv[3]) if len(sys.argv) > 3 else None
    threads = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    out = build_and_solve(n, tlim, ub, threads)
    print(json.dumps({k: v for k, v in out.items() if k != "points"}, indent=2, default=str))
    print("status:", out["status"], "| primal(best) =", out["primal"],
          "| dual(UB) =", out["dual"], "| gap =", out["gap"], "| t =", round(out["time"], 1), "s")
    with open(f"scip_n{n}_result.json", "w") as f:
        json.dump(out, f, indent=2, default=str)


if __name__ == "__main__":
    main()

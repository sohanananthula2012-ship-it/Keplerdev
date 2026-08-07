#!/usr/bin/env python3
"""
Heilbronn certification via MINLP in SCIP (pyscipopt), following
Sudermann-Merx (arXiv:2603.11107): optimize-then-certify with symmetry breaking
and McCormick-friendly product substitution w_ij = x_i*y_j.

Model (maximize z = min triangle area):
  vars: x_i,y_i in [0,1]; w_ij=x_i*y_j in [0,1]; A_t in [-1/2,1/2];
        b_t in {0,1}; z in [0, UB]
  A_t = 0.5*(w_ij + w_jk + w_ki - w_ik - w_ji - w_kj)   for t=(i,j,k)  [LINEAR in w]
  z <= A_t + (1 - b_t) ; z <= -A_t + b_t   (big-M=1) => z <= |A_t| for chosen sign
  Symmetry breaking (points 1..n):
    x1=0,y2=0,x3=1,y4=1,x5=0 ; y1<=y5 ; x2<=x4 ; x6<=...<=xn
  Sign fixing: b_t=1 for k<=5 (T+), b_t=0 for i=1,j=5 (T-)

Usage: python scip_certify.py <n> <time_limit_sec> [UB] [threads]
"""
import sys, json
from itertools import combinations
from pyscipopt import Model

BEST = {5: 0.19245009, 6: 0.125, 7: 0.08385255, 8: 0.07234885,
        9: 0.05485416, 10: 0.04654660, 11: 0.03846154, 12: 0.03259886}


def build_and_solve(n, tlim, ub=None, threads=1):
    m = Model("heilbronn")
    m.setParam("limits/time", tlim)
    try:
        m.setParam("parallel/maxnthreads", threads)
        m.setParam("numerics/feastol", 1e-9)
    except Exception:
        pass
    x = {i: m.addVar(f"x{i}", lb=0, ub=1) for i in range(1, n+1)}
    y = {i: m.addVar(f"y{i}", lb=0, ub=1) for i in range(1, n+1)}
    UB = ub if ub is not None else BEST.get(n, 0.5)
    z = m.addVar("z", lb=0, ub=min(0.5, UB + 1e-3))

    tris = list(combinations(range(1, n+1), 3))
    need = set()
    for (i, j, k) in tris:
        for (a, c) in [(i, j), (j, k), (k, i), (i, k), (j, i), (k, j)]:
            need.add((a, c))
    w = {}
    for (a, c) in need:
        w[(a, c)] = m.addVar(f"w_{a}_{c}", lb=0, ub=1)
        m.addCons(w[(a, c)] == x[a]*y[c])   # SCIP applies McCormick relaxation

    A, b = {}, {}
    for t in tris:
        i, j, k = t
        A[t] = m.addVar(f"A_{i}_{j}_{k}", lb=-0.5, ub=0.5)
        m.addCons(A[t] == 0.5*(w[(i, j)] + w[(j, k)] + w[(k, i)]
                               - w[(i, k)] - w[(j, i)] - w[(k, j)]))
        b[t] = m.addVar(f"b_{i}_{j}_{k}", vtype="B")
        m.addCons(z <= A[t] + (1 - b[t]))
        m.addCons(z <= -A[t] + b[t])

    if n >= 5:
        m.addCons(x[1] == 0); m.addCons(y[2] == 0); m.addCons(x[3] == 1)
        m.addCons(y[4] == 1); m.addCons(x[5] == 0)
        m.addCons(y[1] <= y[5]); m.addCons(x[2] <= x[4])
        for i in range(6, n):
            m.addCons(x[i] <= x[i+1])
        for t in tris:
            i, j, k = t
            if k <= 5:
                m.addCons(b[t] == 1)
            if i == 1 and j == 5:
                m.addCons(b[t] == 0)

    m.setObjective(z, "maximize")
    m.optimize()

    out = {"n": n, "status": m.getStatus(), "primal": m.getPrimalbound(),
           "dual": m.getDualbound(), "gap": m.getGap(),
           "time": m.getSolvingTime(), "UB_used": UB}
    try:
        sol = m.getBestSol()
        out["points"] = [[m.getSolVal(sol, x[i]), m.getSolVal(sol, y[i])]
                         for i in range(1, n+1)]
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
          "| dual(UB) =", out["dual"], "| gap =", out["gap"],
          "| t =", round(out["time"], 1), "s")
    with open(f"scip_n{n}_result.json", "w") as f:
        json.dump(out, f, indent=2, default=str)


if __name__ == "__main__":
    main()

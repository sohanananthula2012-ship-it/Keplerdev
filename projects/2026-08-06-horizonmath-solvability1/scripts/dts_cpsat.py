"""CP-SAT search for a minimum-scope (7,5)-DTS.

7 rows, each 0=a[i][0]<...<a[i][5]<=S. All 105 within-row positive differences
globally distinct. Minimize scope = max mark.

Modes:
  python dts_cpsat.py feas S [time]   -> feasibility at fixed scope S
  python dts_cpsat.py min  Smax [time] -> minimize scope with upper bound Smax
"""
import sys, json
from ortools.sat.python import cp_model
from itertools import combinations

N, K = 7, 5
NM = K + 1  # marks per row incl 0


def build(S):
    m = cp_model.CpModel()
    a = [[None] * NM for _ in range(N)]
    for i in range(N):
        a[i][0] = m.NewConstant(0)
        for j in range(1, NM):
            a[i][j] = m.NewIntVar(1, S, f"a_{i}_{j}")
        for j in range(1, NM):
            m.Add(a[i][j] > a[i][j - 1])
    # difference vars
    diffs = []
    for i in range(N):
        for jp, j in combinations(range(NM), 2):  # jp<j
            d = m.NewIntVar(1, S, f"d_{i}_{jp}_{j}")
            m.Add(d == a[i][j] - a[i][jp])
            diffs.append(d)
    m.AddAllDifferent(diffs)
    # symmetry: order rows by last mark
    for i in range(N - 1):
        m.Add(a[i][NM - 1] <= a[i + 1][NM - 1])
    # symmetry: canonical ruler orientation, first gap <= last gap
    for i in range(N):
        m.Add(a[i][1] <= a[i][NM - 1] - a[i][NM - 2])
    return m, a


def extract(solver, a):
    return [[int(solver.Value(a[i][j])) for j in range(NM)] for i in range(N)]


def main():
    mode = sys.argv[1]
    val = int(sys.argv[2])
    tlim = float(sys.argv[3]) if len(sys.argv) > 3 else 60.0
    if mode == "feas":
        m, a = build(val)
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = tlim
        solver.parameters.num_search_workers = 4
        st = solver.Solve(m)
        name = solver.StatusName(st)
        print(f"feas S={val} status={name} time={solver.WallTime():.1f}s")
        if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            rows = extract(solver, a)
            print(json.dumps({"n": N, "k": K, "rows": rows}))
    else:  # min
        S = val
        m, a = build(S)
        scope = m.NewIntVar(1, S, "scope")
        m.AddMaxEquality(scope, [a[i][NM - 1] for i in range(N)])
        m.Minimize(scope)
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = tlim
        solver.parameters.num_search_workers = 4
        st = solver.Solve(m)
        print(f"min status={solver.StatusName(st)} best={solver.ObjectiveValue()} "
              f"bound={solver.BestObjectiveBound()} time={solver.WallTime():.1f}s")
        if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            rows = extract(solver, a)
            print(json.dumps({"n": N, "k": K, "rows": rows}))


if __name__ == "__main__":
    main()

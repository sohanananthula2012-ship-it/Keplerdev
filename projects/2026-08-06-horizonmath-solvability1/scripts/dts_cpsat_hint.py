"""CP-SAT scope minimization with a warm-start hint.

Reads an initial valid DTS (JSON) as a hint, minimizes scope subject to the
DTS constraints. Upper bound S caps all marks. Prints improved DTS as found.

Usage: python dts_cpsat_hint.py hint.json Supper timelimit
"""
import sys, json, time
from ortools.sat.python import cp_model
from itertools import combinations

N, K = 7, 5
NM = K + 1


class Cb(cp_model.CpSolverSolutionCallback):
    def __init__(self, a):
        super().__init__()
        self.a = a
        self.best = None

    def on_solution_callback(self):
        rows = [[int(self.Value(self.a[i][j])) for j in range(NM)] for i in range(N)]
        sc = max(max(r) for r in rows)
        self.best = rows
        print(f"# incumbent scope={sc} obj={self.ObjectiveValue()} t={self.WallTime():.1f}",
              file=sys.stderr, flush=True)
        print(json.dumps({"n": N, "k": K, "rows": rows}), flush=True)


def main():
    hint = json.load(open(sys.argv[1]))["rows"]
    S = int(sys.argv[2])
    tl = float(sys.argv[3])
    m = cp_model.CpModel()
    a = [[None] * NM for _ in range(N)]
    for i in range(N):
        a[i][0] = m.NewConstant(0)
        for j in range(1, NM):
            a[i][j] = m.NewIntVar(1, S, f"a_{i}_{j}")
            m.Add(a[i][j] > a[i][j - 1])
    diffs = []
    for i in range(N):
        for jp, j in combinations(range(NM), 2):
            d = m.NewIntVar(1, S, f"d_{i}_{jp}_{j}")
            m.Add(d == a[i][j] - a[i][jp])
            diffs.append(d)
    m.AddAllDifferent(diffs)
    # symmetry: order rows by last mark; canonical orientation
    for i in range(N - 1):
        m.Add(a[i][NM - 1] <= a[i + 1][NM - 1])
    for i in range(N):
        m.Add(a[i][1] <= a[i][NM - 1] - a[i][NM - 2])
    scope = m.NewIntVar(1, S, "scope")
    m.AddMaxEquality(scope, [a[i][NM - 1] for i in range(N)])
    m.Minimize(scope)
    # hint: sort hint rows by last mark to match symmetry, then orient canonically
    hint = sorted(hint, key=lambda r: r[-1])
    oriented = []
    for r in hint:
        last = r[-1]
        rev = [0] + [last - r[NM - 1 - t] for t in range(1, NM)]
        rev = [last - x for x in reversed(r)]
        oriented.append(r if r[1] <= last - r[NM - 2] else rev)
    try:
        for i in range(N):
            for j in range(1, NM):
                m.AddHint(a[i][j], oriented[i][j])
    except Exception as e:
        print("# hint skipped:", e, file=sys.stderr)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = tl
    solver.parameters.num_search_workers = 4
    cb = Cb(a)
    st = solver.Solve(m, cb)
    print(f"# final status={solver.StatusName(st)} best={solver.ObjectiveValue()} "
          f"bound={solver.BestObjectiveBound()} time={solver.WallTime():.1f}s",
          file=sys.stderr)


if __name__ == "__main__":
    main()

"""Persistent CP-SAT worker: repeatedly minimize scope with a warm start from the
shared global best; commit + push any strict improvement. Complements the SA
workers with a different (exact) search. Usage: python dts_cpsat_worker.py <proj>
"""
import sys, os, json, time, subprocess, fcntl
from ortools.sat.python import cp_model
from itertools import combinations

N, K = 7, 5
NM = K + 1


def verify(rows):
    diffs = []
    for r in rows:
        r = sorted(r)
        for a in range(NM):
            for b in range(a + 1, NM):
                diffs.append(r[b] - r[a])
    return len(set(diffs)) == len(diffs), max(max(r) for r in rows)


def read_best(proj):
    p = os.path.join(proj, "outputs", "global_best.json")
    for cand in (p, os.path.join(proj, "outputs", "dts_best_125.json")):
        if os.path.exists(cand):
            try:
                d = json.load(open(cand))
                return d["rows"], max(max(r) for r in d["rows"])
            except Exception:
                pass
    return None, None


def commit(proj, rows, scope):
    p = os.path.join(proj, "outputs", "global_best.json")
    with open(p + ".lock", "w") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        cur = 10**9
        if os.path.exists(p):
            try:
                cur = max(max(r) for r in json.load(open(p))["rows"])
            except Exception:
                pass
        won = scope < cur
        if won:
            json.dump({"n": N, "k": K, "rows": [sorted(r) for r in rows]}, open(p, "w"))
        fcntl.flock(lf, fcntl.LOCK_UN)
    if won:
        rel = "projects/2026-08-08-dts-7-5-min-scope/outputs/global_best.json"
        subprocess.run(["python3", os.path.join(proj, "outputs", "ghpush.py"),
                        p, rel, f"daytona cpsat: valid scope={scope}"], timeout=60, check=False)
        print("cpsat NEW BEST", scope, flush=True)
    return won


def solve_once(proj, hint_rows, Supper, tl):
    m = cp_model.CpModel()
    a = [[m.NewConstant(0)] + [m.NewIntVar(1, Supper, f"a{i}_{j}") for j in range(1, NM)]
         for i in range(N)]
    for i in range(N):
        for j in range(1, NM):
            m.Add(a[i][j] > a[i][j - 1])
    diffs = []
    for i in range(N):
        for jp, j in combinations(range(NM), 2):
            dv = m.NewIntVar(1, Supper, f"d{i}_{jp}_{j}")
            m.Add(dv == a[i][j] - a[i][jp])
            diffs.append(dv)
    m.AddAllDifferent(diffs)
    for i in range(N - 1):
        m.Add(a[i][NM - 1] <= a[i + 1][NM - 1])
    for i in range(N):
        m.Add(a[i][1] <= a[i][NM - 1] - a[i][NM - 2])
    scope = m.NewIntVar(1, Supper, "scope")
    m.AddMaxEquality(scope, [a[i][NM - 1] for i in range(N)])
    m.Minimize(scope)
    h = sorted([sorted(r) for r in hint_rows], key=lambda r: r[-1])
    for i in range(N):
        r = h[i]; last = r[-1]
        rev = [last - x for x in reversed(r)]
        rr = r if r[1] <= last - r[NM - 2] else rev
        for j in range(1, NM):
            try:
                m.AddHint(a[i][j], rr[j])
            except Exception:
                pass
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = tl
    solver.parameters.num_search_workers = 4
    st = solver.Solve(m)
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return [[int(solver.Value(a[i][j])) for j in range(NM)] for i in range(N)]
    return None


def main():
    proj = sys.argv[1]
    while True:
        hint, cur = read_best(proj)
        if hint is None:
            time.sleep(20); continue
        rows = solve_once(proj, hint, cur, 240.0)
        if rows:
            ok, sc = verify(rows)
            if ok and sc < cur:
                commit(proj, rows, sc)
        time.sleep(1)


if __name__ == "__main__":
    main()

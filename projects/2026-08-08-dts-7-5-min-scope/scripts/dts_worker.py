"""Persistent DTS(7,5) SA worker for Daytona. Loops forever descending target
scope T, seeded from the shared global best. On any valid improvement, atomically
updates outputs/global_best.json and pushes it to GitHub.

Usage: python dts_worker.py <worker_id> <Tmin> <proj_dir>
"""
import sys, os, json, time, subprocess, fcntl
import dts_sa

N, K = 7, 5


def verify(rows):
    diffs = []
    for r in rows:
        r = sorted(r)
        if r[0] != 0 or len(r) != K + 1:
            return False, None
        for a in range(K + 1):
            for b in range(a + 1, K + 1):
                diffs.append(r[b] - r[a])
    scope = max(max(r) for r in rows)
    ok = len(set(diffs)) == len(diffs) and all(d > 0 for d in diffs)
    return ok, scope


def read_best(proj):
    p = os.path.join(proj, "outputs", "global_best.json")
    if os.path.exists(p):
        try:
            d = json.load(open(p))
            ok, sc = verify(d["rows"])
            if ok:
                return d["rows"], sc
        except Exception:
            pass
    d = json.load(open(os.path.join(proj, "outputs", "dts_best_125.json")))
    return d["rows"], max(max(r) for r in d["rows"])


def commit_best(proj, rows, scope, wid):
    p = os.path.join(proj, "outputs", "global_best.json")
    lockp = p + ".lock"
    won = False
    with open(lockp, "w") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        cur = 10**9
        if os.path.exists(p):
            try:
                cur = max(max(r) for r in json.load(open(p))["rows"])
            except Exception:
                pass
        if scope < cur:
            json.dump({"n": N, "k": K, "rows": [sorted(r) for r in rows]}, open(p, "w"))
            won = True
        fcntl.flock(lf, fcntl.LOCK_UN)
    if won:
        try:
            rel = "projects/2026-08-08-dts-7-5-min-scope/outputs/global_best.json"
            subprocess.run(["python3", os.path.join(proj, "outputs", "ghpush.py"),
                            p, rel, f"daytona w{wid}: valid scope={scope}"],
                           timeout=60, check=False)
        except Exception as e:
            print("push err", e, flush=True)
        print(f"[w{wid}] NEW BEST scope={scope}", flush=True)
    return won


def main():
    wid = int(sys.argv[1]); Tmin = int(sys.argv[2]); proj = sys.argv[3]
    rngseed = 1000 * wid + 7
    while True:
        seed_rows, cur_scope = read_best(proj)
        T = cur_scope - 1
        if T < Tmin:
            time.sleep(30)
            continue
        rngseed += 1
        rows, cost, el = dts_sa.run(T, 45.0, seed_rows, rngseed)
        if cost == 0:
            ok, scope = verify(rows)
            if ok and scope <= T:
                commit_best(proj, rows, scope, wid)
        elif rngseed % 5 == 0:
            rows, cost, el = dts_sa.run(T, 30.0, None, rngseed + 500)
            if cost == 0:
                ok, scope = verify(rows)
                if ok and scope <= T:
                    commit_best(proj, rows, scope, wid)


if __name__ == "__main__":
    main()

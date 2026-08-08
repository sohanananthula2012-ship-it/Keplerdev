"""Persistent Gaussian bootstrapping worker for DTS(7,5), target <=111.

Trains the per-position Gaussian model on GOOD tight DTSs (seeded with the
verified scope-112 construction), searches for a strictly smaller-scope valid
DTS via dts_koubi2's DFS, and on success: verifies, atomically updates
global_best.json, pushes to GitHub, and ADDS the new DTS to the training pool
(iterative bootstrapping toward lower scope).

Usage: python dts_gsearch_worker.py <worker_id> <proj_dir>
"""
import sys, os, json, time, random, subprocess, fcntl
import dts_koubi2 as K

N, NM = 7, 6
SEED112 = [[0,27,30,66,95,100],[0,9,16,60,102,106],[0,13,62,72,105,107],
           [0,28,52,83,108,109],[0,22,41,89,104,110],[0,12,32,50,103,111],
           [0,11,58,75,98,112]]


def params_from(pool):
    mu = [0.0]*NM; sig = [2.0]*NM
    for j in range(1, NM):
        xs = [r[j] for dts in pool for r in dts]
        m = sum(xs)/len(xs); mu[j] = m
        var = sum((x-m)**2 for x in xs)/max(1, len(xs)-1)
        sig[j] = max(3.0, var**0.5)
    ref = max(max(r) for dts in pool for r in dts)
    return mu, sig, ref


def read_best(proj):
    p = os.path.join(proj, "outputs", "global_best.json")
    try:
        d = json.load(open(p)); return d["rows"], max(max(r) for r in d["rows"])
    except Exception:
        return SEED112, 112


def commit(proj, rows, scope, wid):
    p = os.path.join(proj, "outputs", "global_best.json")
    won = False
    with open(p + ".lock", "w") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        cur = 10**9
        try:
            cur = max(max(r) for r in json.load(open(p))["rows"])
        except Exception:
            pass
        if scope < cur:
            json.dump({"n": 7, "k": 5, "rows": [sorted(r) for r in rows]}, open(p, "w"))
            won = True
        fcntl.flock(lf, fcntl.LOCK_UN)
    if won:
        rel = "projects/2026-08-08-dts-7-5-min-scope/outputs/global_best.json"
        subprocess.run(["python3", os.path.join(proj, "outputs", "ghpush.py"),
                        p, rel, f"daytona gsearch w{wid}: BEAT scope={scope}"],
                       timeout=90, check=False)
        print(f"[g{wid}] NEW BEST scope={scope}", flush=True)
    return won


def main():
    wid = int(sys.argv[1]); proj = sys.argv[2]
    rng = random.Random(1234*wid + 7)
    pool = [[list(r) for r in SEED112]]
    gb_rows, gb = read_best(proj)
    if gb <= 112:
        pool.append([list(r) for r in gb_rows])
    logp = os.path.join(proj, "outputs", f"gworker_{wid}.log")
    lf = open(logp, "a")
    def log(*a): print(*a, file=lf, flush=True)
    log(f"start w{wid} pool={len(pool)}")
    it = 0
    while True:
        it += 1
        _, cur = read_best(proj)
        T = cur - 1
        mu, sig, ref = params_from(pool)
        f = T / ref
        infl = 1.25 + 0.6*rng.random()
        mu2 = [x*f for x in mu]; s2 = [s*f*infl for s in sig]
        rows, tries = K.search(T, 30.0, mu2, s2, seed=rng.randint(1, 10**9),
                               attempt=1.5)
        if rows:
            ok, sc = K.verify(rows)
            if ok and sc <= T:
                if commit(proj, rows, sc, wid):
                    pool.append([list(r) for r in rows])
                    if len(pool) > 12:
                        pool = pool[:1] + pool[-11:]
                    log(f"it{it} FOUND scope={sc}")
        if it % 20 == 0:
            log(f"it{it} target={T} lastTries={tries} poolsz={len(pool)}")


if __name__ == "__main__":
    main()

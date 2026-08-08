"""Driver: descend target scope T, running SA (with multi-seed restarts) at each
level, re-seeding from the last valid solution found. Saves the best valid DTS.

Usage: python dts_driver.py Tstart Tmin per_T_seconds total_seconds out.json [seed_json]
"""
import sys, json, time
import dts_sa

N, K = 7, 5


def verify_rows(rows, T):
    diffs = []
    for r in rows:
        r = sorted(r)
        if r[0] != 0 or len(r) != K + 1:
            return False, None
        for a in range(K + 1):
            for b in range(a + 1, K + 1):
                diffs.append(r[b] - r[a])
    scope = max(max(r) for r in rows)
    return (len(set(diffs)) == len(diffs) and all(d > 0 for d in diffs) and scope <= T), scope


def main():
    Tstart = int(sys.argv[1]); Tmin = int(sys.argv[2])
    per = float(sys.argv[3]); total = float(sys.argv[4])
    outp = sys.argv[5]
    seed_rows = None
    if len(sys.argv) > 6 and sys.argv[6] not in ("-", "none"):
        seed_rows = json.load(open(sys.argv[6]))["rows"]
    t0 = time.time()
    best_scope = None; best_rows = None
    T = Tstart
    rngseed = 100
    while T >= Tmin and time.time() - t0 < total:
        found = False
        for s in range(8):
            if time.time() - t0 >= total:
                break
            rngseed += 1
            rows, cost, el = dts_sa.run(T, per, seed_rows, rngseed)
            if cost == 0:
                ok, scope = verify_rows(rows, T)
                if ok:
                    best_scope = scope; best_rows = [sorted(r) for r in rows]
                    seed_rows = best_rows
                    json.dump({"n": N, "k": K, "rows": best_rows}, open(outp, "w"))
                    print(f"# VALID T={T} scope={scope} seed={rngseed} t={time.time()-t0:.0f}s",
                          file=sys.stderr, flush=True)
                    found = True
                    break
        if found:
            T = best_scope - 1
        else:
            print(f"# stuck at T={T} (no valid), stopping descent", file=sys.stderr, flush=True)
            break
    if best_rows:
        print(json.dumps({"n": N, "k": K, "rows": best_rows}))
    print(f"# BEST scope={best_scope} total_t={time.time()-t0:.0f}s", file=sys.stderr)


if __name__ == "__main__":
    main()

"""Simulated annealing for (7,5)-DTS at a fixed target scope T.

State: 7 rows of marks 0<x1<...<x5<=T. Cost = number of "excess" difference
collisions = sum_d max(cnt[d]-1, 0), where cnt[d] counts pairs with difference
d across all rows. Cost 0  <=> valid DTS with scope <= T.

Move: change one interior mark to a random feasible value; delta-update the 5
differences it participates in. Metropolis acceptance, geometric cooling, random
restarts. Optionally seed from a JSON solution.

Usage: python dts_sa.py T timelimit [seed_json] [rngseed]
Prints a valid DTS JSON (scope<=T) if found; else best cost reached.
"""
import sys, json, time, random, math

N, K = 7, 5
NM = K + 1


def pair_diffs(row):
    ds = []
    for a in range(NM):
        for b in range(a + 1, NM):
            ds.append(row[b] - row[a])
    return ds


def run(T, tlimit, seed_rows, rngseed):
    rng = random.Random(rngseed)
    t0 = time.time()
    deadline = t0 + tlimit
    best_cost = None
    best_rows = None

    def rand_row():
        while True:
            xs = sorted(rng.sample(range(1, T + 1), K))
            if len(set(xs)) == K:
                return [0] + xs

    while time.time() < deadline:
        # init
        if seed_rows is not None and best_rows is None:
            rows = [r[:] for r in seed_rows]
            # clamp into [0,T]
            rows = [r if max(r) <= T else rand_row() for r in rows]
        else:
            rows = [rand_row() for _ in range(N)]
        cnt = [0] * (T + 2)
        for r in rows:
            for d in pair_diffs(r):
                cnt[d] += 1
        cost = sum(c - 1 for c in cnt if c > 1)

        Temp = 3.0
        it = 0
        stagn = 0
        while cost > 0 and time.time() < deadline:
            it += 1
            if it % 4000 == 0:
                Temp *= 0.985
                if Temp < 0.05:
                    Temp = 0.05
            i = rng.randrange(N)
            j = rng.randrange(1, NM)  # interior mark to move (1..5)
            row = rows[i]
            old = row[j]
            lo = row[j - 1] + 1
            hi = (row[j + 1] - 1) if j < NM - 1 else T
            if hi < lo:
                continue
            new = rng.randint(lo, hi)
            if new == old:
                continue
            # differences changed: between j and every other mark k!=j
            others = [row[k] for k in range(NM) if k != j]
            # remove old
            dcost = 0
            for o in others:
                d = abs(old - o)
                c = cnt[d]
                if c > 1:
                    dcost -= 1
                cnt[d] = c - 1
            # add new
            for o in others:
                d = abs(new - o)
                c = cnt[d]
                if c >= 1:
                    dcost += 1
                cnt[d] = c + 1
            if dcost <= 0 or rng.random() < math.exp(-dcost / Temp):
                row[j] = new
                cost += dcost
                if dcost < 0:
                    stagn = 0
                else:
                    stagn += 1
            else:
                # revert cnt
                for o in others:
                    cnt[abs(new - o)] -= 1
                    cnt[abs(old - o)] += 1
                stagn += 1
            if best_cost is None or cost < best_cost:
                best_cost = cost
                best_rows = [rr[:] for rr in rows]
                if cost == 0:
                    return best_rows, best_cost, time.time() - t0
            if stagn > 60000:
                break  # restart
        if cost == 0:
            return rows, 0, time.time() - t0
    return best_rows, best_cost, time.time() - t0


if __name__ == "__main__":
    T = int(sys.argv[1])
    tl = float(sys.argv[2])
    seed_rows = None
    if len(sys.argv) > 3 and sys.argv[3] not in ("-", "none"):
        seed_rows = json.load(open(sys.argv[3]))["rows"]
    rngseed = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    rows, cost, el = run(T, tl, seed_rows, rngseed)
    if cost == 0:
        print(json.dumps({"n": N, "k": K, "rows": [sorted(r) for r in rows]}))
        print(f"# VALID scope<= {T} actualscope={max(max(r) for r in rows)} time={el:.1f}s",
              file=sys.stderr)
    else:
        print(f"# best_cost={cost} T={T} time={el:.1f}s", file=sys.stderr)

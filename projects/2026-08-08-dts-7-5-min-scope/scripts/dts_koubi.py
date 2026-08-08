"""Koubi-style DTS(7,5) search with Gaussian per-position mark sampling.
Incremental (mark-by-mark) ruler construction for efficiency.

- j-th mark ~ round(Normal(mu[j], sigma[j])), inserted only if it introduces no
  repeated distance (within ruler or vs global used distances).
- Params trained on easy larger-scope DTSs (uniform sampling), scaled by M/M'.
- Greedy row-by-row build with backtracking (drop last row on failure).
- Python int bitmask for used distances.

Provides train_params(), scale_params(), search(), verify().
"""
import sys, json, time, random, math

N, K = 7, 5
NM = K + 1


def build_ruler(mu, sigma, M, used, rng, attempts, uniform=False):
    """Incrementally build one ruler [0,m1,..,m5]; return (marks, dmask) or None."""
    marks = [0]
    dm = 0
    for j in range(1, NM):
        placed = False
        for _ in range(attempts):
            lo = marks[-1] + 1
            if uniform:
                if lo > M:
                    break
                v = rng.randint(lo, M)
            else:
                v = int(round(rng.gauss(mu[j], sigma[j])))
                if v < lo or v > M:
                    continue
            nb = 0
            ok = True
            for m in marks:
                d = v - m
                bit = 1 << d
                if (used >> d) & 1 or (dm >> d) & 1 or (nb >> d) & 1:
                    ok = False
                    break
                nb |= bit
            if ok:
                marks.append(v)
                dm |= nb
                placed = True
                break
        if not placed:
            return None
    return marks, dm


def build_dts(M, mu, sigma, rng, thresh1, thresh2, deadline, uniform=False,
              attempts=60):
    rows = []; dmasks = []; used = 0; it1 = 0
    while len(rows) < N and it1 < thresh1:
        if time.time() > deadline:
            return None
        it1 += 1
        placed = False
        for _ in range(thresh2):
            s = build_ruler(mu, sigma, M, used, rng, attempts, uniform)
            if s is None:
                continue
            marks, dm = s
            rows.append(marks); dmasks.append(dm); used |= dm
            placed = True
            break
        if not placed and rows:
            used ^= dmasks.pop(); rows.pop()
    return rows if len(rows) == N else None


def train_params(Mp, n_dts, rng, time_budget):
    t0 = time.time()
    samples = [[] for _ in range(NM)]
    found = 0
    while found < n_dts and time.time() - t0 < time_budget:
        rows = build_dts(Mp, None, None, rng, thresh1=200, thresh2=60,
                         deadline=t0 + time_budget, uniform=True, attempts=80)
        if rows:
            found += 1
            for r in rows:
                for j in range(1, NM):
                    samples[j].append(r[j])
    mu = [0.0] * NM; sigma = [1.0] * NM
    for j in range(1, NM):
        if len(samples[j]) > 1:
            m = sum(samples[j]) / len(samples[j])
            var = sum((x - m) ** 2 for x in samples[j]) / (len(samples[j]) - 1)
            mu[j] = m; sigma[j] = max(1.0, math.sqrt(var))
        else:
            mu[j] = j * Mp / NM; sigma[j] = Mp / (2 * NM)
    return mu, sigma, found


def scale_params(mu, sigma, Mp, M, sigma_infl=1.0):
    f = M / Mp
    return [x * f for x in mu], [s * f * sigma_infl for s in sigma]


def verify(rows):
    ds = []
    for r in rows:
        for a in range(NM):
            for b in range(a + 1, NM):
                ds.append(r[b] - r[a])
    return len(set(ds)) == len(ds) and all(d > 0 for d in ds), max(max(r) for r in rows)


def search(M, tlimit, mu, sigma, seed, thresh1=4000, thresh2=200, attempts=60):
    rng = random.Random(seed)
    t0 = time.time(); deadline = t0 + tlimit; tries = 0
    while time.time() < deadline:
        tries += 1
        rows = build_dts(M, mu, sigma, rng, thresh1, thresh2, deadline,
                         attempts=attempts)
        if rows:
            ok, sc = verify(rows)
            if ok and sc <= M:
                return [sorted(r) for r in rows], tries
    return None, tries


if __name__ == "__main__":
    M = int(sys.argv[1]); tl = float(sys.argv[2])
    Mp = int(sys.argv[3]) if len(sys.argv) > 3 else 150
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    rng = random.Random(seed)
    mu, sigma, nf = train_params(Mp, 100, rng, time_budget=min(25, tl / 3))
    print(f"# trained {nf} DTSs at M'={Mp}; mu={[round(x,1) for x in mu]} "
          f"sigma={[round(x,1) for x in sigma]}", file=sys.stderr)
    mu2, sigma2 = scale_params(mu, sigma, Mp, M, 1.15)
    rows, tries = search(M, tl, mu2, sigma2, seed + 1)
    if rows:
        print(json.dumps({"n": N, "k": K, "rows": rows}))
        print(f"# VALID scope={verify(rows)[1]} tries={tries}", file=sys.stderr)
    else:
        print(f"# none at M={M} tries={tries}", file=sys.stderr)

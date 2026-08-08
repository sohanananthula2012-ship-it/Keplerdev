"""Koubi-style DTS(7,5) search with Gaussian per-position mark sampling.

Method (Shehadeh-Kingsford-Kschischang 2025 / Koubi et al.):
- Each ruler's j-th mark ~ round(Normal(mu[j], sigma[j])).
- Parameters trained on easy larger-scope DTSs, then scaled by M/M' to target M.
- Greedy row-by-row construction with backtracking (row replacement).
- Bitmask distance bookkeeping for speed.

Provides: train_params(), search(M, ...). Also runnable standalone.
"""
import sys, json, time, random, math

N, K = 7, 5
NM = K + 1


def ruler_dmask(marks):
    """Return (ok, dmask): ok False if internal repeated distance."""
    dmask = 0
    for a in range(NM):
        for b in range(a + 1, NM):
            d = marks[b] - marks[a]
            bit = 1 << d
            if dmask & bit:
                return False, 0
            dmask |= bit
    return True, dmask


def sample_ruler(mu, sigma, M, rng):
    xs = set()
    for j in range(1, NM):
        v = int(round(rng.gauss(mu[j], sigma[j])))
        if v < 1:
            v = 1
        if v > M:
            v = M
        xs.add(v)
    if len(xs) != K:
        return None
    marks = [0] + sorted(xs)
    ok, dmask = ruler_dmask(marks)
    if not ok:
        return None
    return marks, dmask


def uniform_ruler(M, rng):
    xs = sorted(rng.sample(range(1, M + 1), K))
    marks = [0] + xs
    ok, dmask = ruler_dmask(marks)
    return (marks, dmask) if ok else None


def build_dts(M, mu, sigma, rng, thresh1, thresh2, deadline, uniform=False):
    """Greedy build with backtracking. Returns rows or None."""
    rows = []
    dmasks = []
    used = 0
    it1 = 0
    while len(rows) < N and it1 < thresh1:
        if time.time() > deadline:
            return None
        it1 += 1
        placed = False
        for _ in range(thresh2):
            s = uniform_ruler(M, rng) if uniform else sample_ruler(mu, sigma, M, rng)
            if s is None:
                continue
            marks, dmask = s
            if used & dmask:
                continue
            rows.append(marks); dmasks.append(dmask); used |= dmask
            placed = True
            break
        if not placed:
            if rows:  # backtrack: drop last row
                used ^= dmasks.pop(); rows.pop()
            # else just retry
    return rows if len(rows) == N else None


def train_params(Mp, n_dts, rng, time_budget):
    """Find easy DTSs at scope Mp with uniform sampling; aggregate per-position
    mean/std of marks. Returns mu, sigma (length NM, index 0 unused=0)."""
    t0 = time.time()
    samples = [[] for _ in range(NM)]
    found = 0
    while found < n_dts and time.time() - t0 < time_budget:
        rows = build_dts(Mp, None, None, rng, thresh1=4000, thresh2=300,
                         deadline=t0 + time_budget, uniform=True)
        if rows:
            found += 1
            for r in rows:
                for j in range(1, NM):
                    samples[j].append(r[j])
    mu = [0.0] * NM
    sigma = [1.0] * NM
    for j in range(1, NM):
        if samples[j]:
            m = sum(samples[j]) / len(samples[j])
            var = sum((x - m) ** 2 for x in samples[j]) / max(1, len(samples[j]) - 1)
            mu[j] = m
            sigma[j] = max(1.0, math.sqrt(var))
        else:
            mu[j] = j * Mp / NM
            sigma[j] = Mp / (2 * NM)
    return mu, sigma, found


def scale_params(mu, sigma, Mp, M, sigma_infl=1.0):
    f = M / Mp
    return ([x * f for x in mu], [s * f * sigma_infl for s in sigma])


def verify(rows):
    ds = []
    for r in rows:
        for a in range(NM):
            for b in range(a + 1, NM):
                ds.append(r[b] - r[a])
    return len(set(ds)) == len(ds) and all(d > 0 for d in ds), max(max(r) for r in rows)


def search(M, tlimit, mu, sigma, seed, thresh1=6000, thresh2=400):
    rng = random.Random(seed)
    t0 = time.time(); deadline = t0 + tlimit
    tries = 0
    while time.time() < deadline:
        tries += 1
        rows = build_dts(M, mu, sigma, rng, thresh1, thresh2, deadline)
        if rows:
            ok, sc = verify(rows)
            if ok and sc <= M:
                return [sorted(r) for r in rows], tries
    return None, tries


if __name__ == "__main__":
    M = int(sys.argv[1]); tl = float(sys.argv[2])
    Mp = int(sys.argv[3]) if len(sys.argv) > 3 else 135
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    rng = random.Random(seed)
    mu, sigma, nf = train_params(Mp, 40, rng, time_budget=min(30, tl / 3))
    print(f"# trained on {nf} DTSs at M'={Mp}; mu={[round(x,1) for x in mu]} "
          f"sigma={[round(x,1) for x in sigma]}", file=sys.stderr)
    mu2, sigma2 = scale_params(mu, sigma, Mp, M, sigma_infl=1.15)
    rows, tries = search(M, tl, mu2, sigma2, seed + 1)
    if rows:
        print(json.dumps({"n": N, "k": K, "rows": rows}))
        print(f"# VALID scope={max(max(r) for r in rows)} tries={tries}", file=sys.stderr)
    else:
        print(f"# none at M={M} tries={tries}", file=sys.stderr)

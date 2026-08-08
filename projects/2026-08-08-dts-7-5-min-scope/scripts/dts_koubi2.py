"""Koubi-style DTS(7,5) search: recursive cross-row backtracking with
Gaussian-weighted candidate ordering, and SHORT per-attempt deadlines so a
runaway recursion is abandoned and restarted (the key reliability fix).
"""
import sys, json, time, random, math

N, K = 7, 5
NM = K + 1


def _order(cands, mu_j, sig_j, rng):
    if mu_j is None:
        rng.shuffle(cands)
        return cands
    keyed = []
    inv = 1.0 / (2.0 * sig_j * sig_j)
    for v in cands:
        w = math.exp(-((v - mu_j) ** 2) * inv) + 1e-12
        keyed.append((rng.random() ** (1.0 / w), v))
    keyed.sort(reverse=True)
    return [v for _, v in keyed]


def build_row(used, mu, sigma, M, rng, deadline, node_cap):
    marks = [0]; nodes = [0]

    def rec(depth, dm):
        if nodes[0] > node_cap or time.time() > deadline:
            return None
        nodes[0] += 1
        if depth == NM:
            return dm
        lo = marks[-1] + 1
        rem = NM - 1 - depth
        hi = M - rem
        if lo > hi:
            return None
        cands = list(range(lo, hi + 1))
        mj = None if mu is None else mu[depth]
        sj = 1.0 if sigma is None else sigma[depth]
        for v in _order(cands, mj, sj, rng):
            nb = 0; ok = True
            for m in marks:
                dd = v - m
                if (used >> dd) & 1 or (dm >> dd) & 1 or (nb >> dd) & 1:
                    ok = False; break
                nb |= (1 << dd)
            if not ok:
                continue
            marks.append(v)
            r = rec(depth + 1, dm | nb)
            if r is not None:
                return r
            marks.pop()
        return None

    dm = rec(1, 0)
    return (list(marks), dm) if dm is not None else None


def build_dts(M, mu, sigma, rng, deadline, row_tries=8, node_cap=8000):
    rows = []; dmasks = []

    def rec(row_idx, used):
        if time.time() > deadline:
            return False
        if row_idx == N:
            return True
        for _ in range(row_tries):
            r = build_row(used, mu, sigma, M, rng, deadline, node_cap)
            if r is None:
                continue
            marks, dm = r
            rows.append(marks); dmasks.append(dm)
            if rec(row_idx + 1, used | dm):
                return True
            rows.pop(); dmasks.pop()
            if time.time() > deadline:
                return False
        return False

    return rows[:] if rec(0, 0) else None


def verify(rows):
    ds = []
    for r in rows:
        for a in range(NM):
            for b in range(a + 1, NM):
                ds.append(r[b] - r[a])
    return len(set(ds)) == len(ds) and all(d > 0 for d in ds), max(max(r) for r in rows)


def train_params(Mp, n_dts, rng, time_budget, attempt=1.5):
    t0 = time.time()
    samp = [[] for _ in range(NM)]; found = 0
    while found < n_dts and time.time() - t0 < time_budget:
        dl = min(t0 + time_budget, time.time() + attempt)
        rows = build_dts(Mp, None, None, rng, deadline=dl)
        if rows:
            found += 1
            for r in rows:
                for j in range(1, NM):
                    samp[j].append(r[j])
    mu = [0.0] * NM; sigma = [1.0] * NM
    for j in range(1, NM):
        if len(samp[j]) > 1:
            m = sum(samp[j]) / len(samp[j])
            var = sum((x - m) ** 2 for x in samp[j]) / (len(samp[j]) - 1)
            mu[j] = m; sigma[j] = max(1.5, math.sqrt(var))
        else:
            mu[j] = j * Mp / NM; sigma[j] = Mp / (2 * NM)
    return mu, sigma, found


def scale_params(mu, sigma, Mp, M, infl=1.0):
    f = M / Mp
    return [x * f for x in mu], [s * f * infl for s in sigma]


def search(M, tlimit, mu, sigma, seed, attempt=3.0):
    rng = random.Random(seed)
    t0 = time.time(); deadline = t0 + tlimit; tries = 0
    while time.time() < deadline:
        tries += 1
        dl = min(deadline, time.time() + attempt)
        rows = build_dts(M, mu, sigma, rng, deadline=dl)
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
    mu, sigma, nf = train_params(Mp, 200, rng, time_budget=min(20, tl / 3))
    print(f"# trained {nf} at M'={Mp} mu={[round(x) for x in mu]} sig={[round(x,1) for x in sigma]}",
          file=sys.stderr)
    mu2, s2 = scale_params(mu, sigma, Mp, M, 1.1)
    rows, tries = search(M, tl, mu2, s2, seed + 1)
    if rows:
        print(json.dumps({"n": N, "k": K, "rows": rows}))
        print(f"# VALID scope={verify(rows)[1]} tries={tries}", file=sys.stderr)
    else:
        print(f"# none M={M} tries={tries}", file=sys.stderr)

"""Independent, from-scratch verifier for an (n,k)-DTS.
Checks: each row starts at 0, strictly increasing, all within-row positive
differences across ALL rows are globally distinct. Reports scope."""
from itertools import combinations


def verify(rows, n=7, k=5):
    assert len(rows) == n, f"expected {n} rows, got {len(rows)}"
    diffs = []
    for r in rows:
        assert len(r) == k + 1, f"row must have {k+1} entries: {r}"
        assert r[0] == 0, f"row must start at 0: {r}"
        for a, b in zip(r, r[1:]):
            assert b > a, f"row not strictly increasing: {r}"
        for j, jp in combinations(range(k + 1), 2):
            # jp<j indices; combinations gives (jp, j) with jp<j
            diffs.append(r[j] - r[jp])
    # all differences distinct?
    assert all(d > 0 for d in diffs)
    n_expected = n * (k * (k + 1) // 2)
    assert len(diffs) == n_expected, (len(diffs), n_expected)
    distinct = len(set(diffs)) == len(diffs)
    scope = max(max(r) for r in rows)
    return distinct, scope, len(diffs), len(set(diffs))


if __name__ == "__main__":
    import sys, json
    data = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else None
    if data:
        ok, scope, nd, nset = verify(data["rows"], data["n"], data["k"])
        print(f"distinct={ok} scope={scope} ndiffs={nd} nunique={nset}")

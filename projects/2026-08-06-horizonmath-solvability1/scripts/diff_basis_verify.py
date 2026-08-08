"""Independent from-scratch verification of the diff_basis_upper construction.

Rebuilds L = {a*m + b : a in A, b in B}, brute-force computes the full
difference set, checks every k in {1..n} is realized, reports exact ratio.
No sampling, no shortcuts.
"""

A = [0, 1, 4, 6]
m = 89 * 89 + 89 + 1  # 8011
B = [0,1,70,83,255,297,384,391,550,555,647,656,710,996,1020,1232,1257,1272,
     1452,1456,1536,1614,1745,1765,1948,2047,2150,2188,2214,2395,2407,2585,
     2612,2628,2739,2758,2858,2902,2974,3006,3027,3245,3392,3477,3526,3615,
     3675,3727,3849,3906,3935,4043,4049,4253,4410,4445,4578,4580,4821,4855,
     4911,4934,4973,5032,5099,5149,5160,5411,5452,5518,5526,5658,5833,5855,
     5926,5943,5957,5994,6139,6185,6281,6592,6622,6669,6687,6697,6742,6745,
     6778,6967]


def max_contiguous_coverage(points):
    """Brute-force: return the largest n such that every k in 1..n is a
    difference of two points, using an exhaustive pairwise scan."""
    pts = sorted(set(points))
    diffs = set()
    for i in range(len(pts)):
        pi = pts[i]
        for j in range(i + 1, len(pts)):
            diffs.add(pts[j] - pi)
    if not diffs:
        return 0, diffs
    max_d = max(diffs)
    n = 0
    for k in range(1, max_d + 2):
        if k not in diffs:
            n = k - 1
            break
    else:
        n = max_d
    return n, diffs


def verify():
    L = sorted({a * m + b for a in A for b in B})
    size = len(L)
    n, diffs = max_contiguous_coverage(L)
    # Explicit re-check: confirm EVERY k in 1..n is present (not just first gap)
    all_covered = all(k in diffs for k in range(1, n + 1))
    ratio = size * size / n
    print(f"|B| (points in L)      = {size}")
    print(f"expected |A|*|B|        = {len(A) * len(B)} (collisions: {len(A)*len(B)-size})")
    print(f"max contiguous n        = {n}")
    print(f"every k in 1..n covered = {all_covered}")
    print(f"ratio |B|^2 / n         = {ratio:.10f}")
    print(f"beats 2.6390 (strict)?  = {ratio < 2.6390}")
    # threshold analysis
    need_n = size * size / 2.6390
    print(f"n needed for ratio<2.6390 with {size} pts = {need_n:.2f} -> n>={int(need_n)+1}")
    return size, n, ratio


if __name__ == "__main__":
    verify()

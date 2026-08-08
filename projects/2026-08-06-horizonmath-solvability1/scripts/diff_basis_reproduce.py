#!/usr/bin/env python3
"""
Reproduce and verify the AlphaEvolve difference-basis record (ratio 2.6390).

Construction (Leech combination):
  A = {0,1,4,6}  -- difference basis with contiguous A-A = [-6,6]
  B = 90-element planar Singer difference set mod m = 89^2+89+1 = 8011
  L = { a*m + b : a in A, b in B },  |L| = 4*90 = 360
Score = |L|^2 / k, where k = largest integer with [1..k] all realized as differences.
"""
A = [0, 1, 4, 6]
B = [0, 1, 70, 83, 255, 297, 384, 391, 550, 555, 647, 656, 710, 996, 1020, 1232,
     1257, 1272, 1452, 1456, 1536, 1614, 1745, 1765, 1948, 2047, 2150, 2188, 2214,
     2395, 2407, 2585, 2612, 2628, 2739, 2758, 2858, 2902, 2974, 3006, 3027, 3245,
     3392, 3477, 3526, 3615, 3675, 3727, 3849, 3906, 3935, 4043, 4049, 4253, 4410,
     4445, 4578, 4580, 4821, 4855, 4911, 4934, 4973, 5032, 5099, 5149, 5160, 5411,
     5452, 5518, 5526, 5658, 5833, 5855, 5926, 5943, 5957, 5994, 6139, 6185, 6281,
     6592, 6622, 6669, 6687, 6697, 6742, 6745, 6778, 6967]
M = 89**2 + 89 + 1  # 8011


def coverage(L):
    L = sorted(set(L))
    diffs = set()
    for i in range(len(L)):
        for j in range(i + 1, len(L)):
            diffs.add(L[j] - L[i])
    mx = max(diffs)
    k = mx
    for v in range(1, mx + 2):
        if v not in diffs:
            k = v - 1
            break
    return k, len(L)


if __name__ == "__main__":
    L = sorted({a * M + b for a in A for b in B})
    k, n = coverage(L)
    print(f"m={M} |A|={len(A)} |B|={len(B)} |L|={n}")
    print(f"covered prefix k={k}  ratio |L|^2/k = {n*n/k:.10f}")
    # Verify B is a perfect planar difference set mod m
    res = set()
    for x in B:
        for y in B:
            if x != y:
                res.add((x - y) % M)
    print("B perfect mod m:", len(res) == M - 1)
    # Verify A-A contiguous
    aa = sorted({x - y for x in A for y in A})
    print("A-A =", aa)

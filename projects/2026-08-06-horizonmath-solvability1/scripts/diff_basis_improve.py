"""Step 3 improvement search for diff_basis_upper.

Two independent angles, freshly implemented:

(1) Targeted simulated annealing on the 360-point set L, trying to extend the
    max-contiguous coverage n beyond 49109 (which would strictly beat 2.6390),
    using an incrementally-maintained difference-count array for speed.

(2) Raw parameter sweep: combine small difference bases A with *canonical*
    (untuned) perfect/planar difference sets B_q for prime q, to show where the
    untuned Leech combination lands vs the tuned record.

Honest reporting: only a genuinely verified n>=49110 with <=360 points counts as
a beat.
"""
import random
import time
import numpy as np

A0 = [0, 1, 4, 6]
M = 89 * 89 + 89 + 1  # 8011
B0 = [0,1,70,83,255,297,384,391,550,555,647,656,710,996,1020,1232,1257,1272,
      1452,1456,1536,1614,1745,1765,1948,2047,2150,2188,2214,2395,2407,2585,
      2612,2628,2739,2758,2858,2902,2974,3006,3027,3245,3392,3477,3526,3615,
      3675,3727,3849,3906,3935,4043,4049,4253,4410,4445,4578,4580,4821,4855,
      4911,4934,4973,5032,5099,5149,5160,5411,5452,5518,5526,5658,5833,5855,
      5926,5943,5957,5994,6139,6185,6281,6592,6622,6669,6687,6697,6742,6745,
      6778,6967]
L0 = sorted({a * M + b for a in A0 for b in B0})


def coverage_n(pts, max_d=None):
    pts = sorted(set(pts))
    diffs = set()
    for i in range(len(pts)):
        pi = pts[i]
        for j in range(i + 1, len(pts)):
            diffs.add(pts[j] - pi)
    k = 1
    while k in diffs:
        k += 1
    return k - 1


def build_cnt(pts, cap):
    cnt = np.zeros(cap + 2, dtype=np.int32)
    p = np.array(sorted(set(pts)), dtype=np.int64)
    for i in range(len(p)):
        d = p[i:] - p[i]
        d = d[d <= cap]
        for dd in d:
            cnt[dd] += 1
    return cnt


def first_hole(cnt):
    # smallest k>=1 with cnt[k]==0
    k = 1
    n = len(cnt)
    while k < n and cnt[k] > 0:
        k += 1
    return k  # first uncovered = n+1


def sa_extend(L, seconds=45.0, seed=0):
    rng = random.Random(seed)
    cap = max(L) + 200
    pts = set(L)
    cnt = build_cnt(pts, cap)
    cur_n = first_hole(cnt) - 1
    best_n = cur_n
    best_pts = set(pts)
    plist = sorted(pts)
    t0 = time.time()
    iters = 0
    while time.time() - t0 < seconds:
        iters += 1
        # pick a point to move
        p = plist[rng.randrange(len(plist))]
        # candidate new position: near the first hole to try to cover it, or random small shift
        hole = cur_n + 1
        if rng.random() < 0.5:
            # try to create difference == hole with some existing anchor
            anchor = plist[rng.randrange(len(plist))]
            cand = anchor + hole if rng.random() < 0.5 else anchor - hole
        else:
            cand = p + rng.randint(-50, 50)
        if cand < 0 or cand > cap - 1 or cand in pts:
            continue
        # apply move p -> cand: update cnt
        others = pts - {p}
        for x in others:
            d = abs(p - x)
            if d <= cap:
                cnt[d] -= 1
        for x in others:
            d = abs(cand - x)
            if d <= cap:
                cnt[d] += 1
        pts.discard(p); pts.add(cand)
        new_n = first_hole(cnt) - 1
        accept = new_n >= cur_n or rng.random() < 0.02
        if accept:
            cur_n = new_n
            plist = sorted(pts)
            if new_n > best_n:
                best_n = new_n
                best_pts = set(pts)
        else:
            # revert
            for x in others:
                d = abs(cand - x)
                if d <= cap:
                    cnt[d] -= 1
            for x in others:
                d = abs(p - x)
                if d <= cap:
                    cnt[d] += 1
            pts.discard(cand); pts.add(p)
    return best_n, sorted(best_pts), iters


if __name__ == "__main__":
    base_n = coverage_n(L0)
    print(f"base: |L|={len(L0)} n={base_n} ratio={len(L0)**2/base_n:.7f}")
    best_overall = base_n
    for seed in range(3):
        bn, bp, iters = sa_extend(L0, seconds=40.0, seed=seed)
        # independent recheck
        rn = coverage_n(bp)
        r = len(bp) ** 2 / rn
        print(f"seed={seed} iters={iters} best_n={bn} recheck_n={rn} size={len(bp)} ratio={r:.7f} beat={r<2.6390}")
        best_overall = max(best_overall, rn)
    print(f"best n found = {best_overall} (need >=49110 to beat with 360 pts)")

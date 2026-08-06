def proposed_solution():
    import itertools, math
    r2 = math.sqrt(2.0); s = 1.0/r2
    pts = []
    # E8 roots type (+-1,+-1,0^6) normalized, embedded in R^9 (9th coord 0)
    for i, j in itertools.combinations(range(8), 2):
        for si in (1, -1):
            for sj in (1, -1):
                v = [0.0]*9
                v[i] = si*s; v[j] = sj*s
                pts.append(v)
    # E8 roots type (+-1/2)^8 with even # of minus signs, normalized (norm sqrt2 -> /sqrt2)
    for signs in itertools.product([0.5, -0.5], repeat=8):
        if sum(1 for x in signs if x < 0) % 2 == 0:
            v = [x/r2 for x in signs] + [0.0]
            pts.append(v)
    # A1 in 9th coordinate (unit)
    pts.append([0.0]*8 + [1.0]); pts.append([0.0]*8 + [-1.0])
    return {"points": pts}

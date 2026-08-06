def proposed_solution():
    import itertools, math
    s = 1.0 / math.sqrt(2.0)
    pts = []
    for i, j in itertools.combinations(range(5), 2):
        for si in (1, -1):
            for sj in (1, -1):
                v = [0.0]*5
                v[i] = si*s; v[j] = sj*s
                pts.append(v)
    return {"points": pts}

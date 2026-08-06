def proposed_solution():
    A = list(range(2, 26)); B = list(range(26, 50))
    edges = [[0, 1]]
    for v in A + B:
        edges.append([0, v]); edges.append([1, v])
    for a in A:
        for b in B:
            edges.append([a, b])
    return {"n": 50, "edges": edges}

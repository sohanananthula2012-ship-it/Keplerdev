def proposed_solution():
    p = 13
    inv2 = pow(2, p-2, p)  # inverse of 2 mod p
    K = set()
    # directions [1:b:c]: line {(t, b t - b^2/2, c t - c^2/2)}
    for b in range(p):
        for c in range(p):
            for t in range(p):
                K.add((t % p, (b*t - b*b*inv2) % p, (c*t - c*c*inv2) % p))
    # direction [0:0:1]: vertical z-line
    for t in range(p):
        K.add((0, 0, t % p))
    # directions [0:1:c]: line {(0, t, c t)}
    for c in range(p):
        for t in range(p):
            K.add((0, t % p, (c*t) % p))
    return {"p": p, "points": [list(v) for v in K]}

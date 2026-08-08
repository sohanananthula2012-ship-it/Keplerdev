def proposed_solution():
    # Keich (Theorem 1) exact construction for N=2^n slopes, n=7 (N=128).
    # Intercepts b(l_k) = sum_{i=1}^{n} ((1-i)/n) * eps_i(k) * 2^{-i},
    # where eps_i(k) are the binary digits of k/2^n (eps_1 = MSB of the 7-bit k).
    # Area of the union of the 128 thin triangles = 191403/1605632 = 0.119207265...
    n = 7
    N = 128
    intercepts = []
    for k in range(N):
        s = 0.0
        for i in range(1, n + 1):
            eps = (k >> (n - i)) & 1
            s += ((1.0 - i) / n) * eps * (2.0 ** (-i))
        intercepts.append(s)
    return {"intercepts": intercepts}

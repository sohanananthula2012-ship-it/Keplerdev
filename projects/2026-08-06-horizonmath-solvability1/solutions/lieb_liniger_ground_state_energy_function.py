def proposed_solution(gamma):
    from mpmath import mp, mpf, pi, matrix, lu_solve, findroot
    mp.dps = 50
    gamma = mpf(gamma)
    N = 72 if gamma < 1 else (56 if gamma < 2 else 44)
    nodes, weights = mp.gauss_quadrature(N, "legendre")
    c = 1/(2*pi)
    def solve_g(alpha):
        A = matrix(N, N); b = matrix(N, 1)
        for i in range(N):
            zi = nodes[i]
            for j in range(N):
                A[i, j] = (1 if i == j else 0) - c*weights[j]*2*alpha/(alpha**2+(nodes[j]-zi)**2)
            b[i] = c
        g = lu_solve(A, b)
        G = sum(weights[j]*g[j] for j in range(N))
        return g, G
    def coupling(alpha):
        g, G = solve_g(alpha); return gamma*G - alpha
    alpha = findroot(coupling, gamma**mpf('0.5'))
    g, G = solve_g(alpha)
    num = sum(weights[j]*nodes[j]**2*g[j] for j in range(N))
    return num/G**3

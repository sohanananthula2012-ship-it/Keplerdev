def proposed_solution(lam, nu):
    from mpmath import mp, quad, exp, inf, mpf
    mp.dps = 100
    f = lambda x: (x**2-1)**mpf(1.5)/(exp(lam*x-nu)+1)
    return quad(f, [1, 2, 5, inf])

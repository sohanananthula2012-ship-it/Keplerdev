def proposed_solution(y):
    from mpmath import mp, quad, exp, log, sqrt, inf
    mp.dps = 100
    f = lambda x: x**2*log(1-exp(-sqrt(x**2+y)))
    return quad(f, [0, 1, 5, 20, inf])

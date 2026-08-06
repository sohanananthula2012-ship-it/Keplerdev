def proposed_solution(tau, kappa):
    from mpmath import mp, quad, exp, inf
    mp.dps = 100
    f = lambda x: x**2*exp(-x**6 + tau*x**4 - kappa*tau**2*x**2)
    return 2*quad(f, [0, 1, 2, inf])

def proposed_solution():
    from mpmath import mp, quad, sqrt, ellipk, ellipe, pi
    mp.dps = 100
    integrand = lambda z: (1+sqrt(z))/(1+z)**3*(2*ellipe(z)-(1-z)*ellipk(z))
    return (4*sqrt(2)/pi)*quad(integrand, [0, 1])

# HorizonMath calibration solution: mahler_x_3_y_3_1_5xy
# Logarithmic Mahler measure m(Q_5), Q_5 = x^3 + y^3 + 1 - 5xy.
# Reduce over y by Jensen's formula: for fixed x=e^{i theta}, Q_5 is monic cubic in y
#   y^3 - 5x y + (x^3 + 1); single-variable Mahler measure = sum_j log^+|y_j(theta)|.
# m(Q_5) = (1/2pi) int_0^{2pi} sum_j log^+|y_j(theta)| d(theta).
# (No root crosses |y|=1 here, so the integrand is smooth and quadrature is exact.)

def proposed_solution():
    from mpmath import mp, mpf, mpc, exp, log, polyroots, quad, pi, fabs
    mp.dps = 100
    def g(th):
        x = exp(mpc(0, 1) * th)
        roots = polyroots([mpf(1), mpf(0), -5*x, x**3 + 1],
                          maxsteps=300, extraprec=300)
        return sum((log(fabs(r)) for r in roots if fabs(r) > 1), mpf(0))
    result = quad(g, [0, 2*pi]) / (2 * pi)
    return result

# HorizonMath calibration solution: resultant_chebyshev
# Res_x(T_30, P_20) = lc(T_30)^{deg P_20} * prod_{r: T_30(r)=0} P_20(r).
# Roots of T_n are r_j = cos((2j-1)*pi/(2n)); lc(T_n) = 2^{n-1}.

def proposed_solution():
    from mpmath import mp, cos, pi, mpf, legendre
    mp.dps = 120
    n, m = 30, 20
    lcT = mpf(2)**(n - 1)          # leading coefficient of T_30
    prod = mpf(1)
    for j in range(1, n + 1):
        r = cos((2*j - 1) * pi / (2*n))
        prod *= legendre(m, r)     # P_20 evaluated at each root of T_30
    result = lcT**m * prod
    return result

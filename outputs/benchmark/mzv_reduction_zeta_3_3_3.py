# HorizonMath calibration solution: mzv_reduction_zeta_3_3_3
# zeta(3,3,3) = e_3 of the sequence {1/n^3} (elementary symmetric function).
# Power sums p_j = sum 1/n^{3j} = zeta(3j). Newton's identities give the reduction:
#   e_1 = zeta(3)
#   e_2 = (zeta(3)^2 - zeta(6)) / 2
#   e_3 = (e_2*zeta(3) - e_1*zeta(6) + zeta(9)) / 3   =  zeta(3,3,3).

def proposed_solution():
    from mpmath import mp, zeta
    mp.dps = 100
    z3, z6, z9 = zeta(3), zeta(6), zeta(9)
    e1 = z3
    e2 = (z3**2 - z6) / 2
    e3 = (e2 * z3 - e1 * z6 + z9) / 3
    return e3

# HorizonMath calibration solution: stieltjes_gamma_1
# gamma_1: Stieltjes constant, coefficient in Laurent expansion of zeta about s=1.

def proposed_solution():
    from mpmath import mp, stieltjes
    mp.dps = 100
    result = stieltjes(1)
    return result

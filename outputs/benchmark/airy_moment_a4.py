# HorizonMath calibration solution: airy_moment_a4
# a_4 = int_0^inf Ai(x)^4 dx.  Closed form (DLMF 9.11): a_4 = ln(3)/(24 pi^2).

def proposed_solution():
    from mpmath import mp, log, pi
    mp.dps = 100
    result = log(3) / (24 * pi**2)
    return result

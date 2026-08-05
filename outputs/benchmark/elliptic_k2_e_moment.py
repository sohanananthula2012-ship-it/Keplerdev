# HorizonMath calibration solution: elliptic_k2_e_moment
# int_0^1 K(k)^2 E(k) dk in modulus convention: K(k)=ellipk(k^2), E(k)=ellipe(k^2).

def proposed_solution():
    from mpmath import mp, quad, ellipk, ellipe
    mp.dps = 100
    result = quad(lambda k: ellipk(k**2)**2 * ellipe(k**2), [0, 1])
    return result

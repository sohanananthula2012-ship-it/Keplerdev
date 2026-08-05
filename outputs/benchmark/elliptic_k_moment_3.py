# HorizonMath calibration solution: elliptic_k_moment_3
# int_0^1 K(k)^3 dk, modulus convention K(k)=int_0^{pi/2} dtheta/sqrt(1-k^2 sin^2 theta).
# mpmath.ellipk takes parameter m=k^2, so K(k) = ellipk(k^2).

def proposed_solution():
    from mpmath import mp, quad, ellipk
    mp.dps = 100
    result = quad(lambda k: ellipk(k**2)**3, [0, 1])
    return result

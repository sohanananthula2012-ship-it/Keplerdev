# HorizonMath calibration solution: w4_watson_integral
# W_4 = (1/pi^4) int_[0,pi]^4 dx/(4 - sum cos x_i)
# Bessel single-integral representation (exact):
#   W_d = int_0^inf e^{-d t} I_0(t)^d dt,  since (1/pi) int_0^pi e^{t cos x} dx = I_0(t).
# So W_4 = int_0^inf e^{-4t} I_0(t)^4 dt.

def proposed_solution():
    from mpmath import mp, quad, besseli, inf
    mp.dps = 100
    result = quad(lambda t: mp.e**(-4*t) * besseli(0, t)**4, [0, inf])
    return result

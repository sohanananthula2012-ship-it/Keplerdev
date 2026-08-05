# HorizonMath calibration solution: box_integral_b5_neg2
# B_5(-2) = int_[0,1]^5 |x|^{-2} dx.
# Gamma/Schwinger trick: |x|^{-2} = int_0^inf e^{-t|x|^2} dt (s=-2 => Gamma(1)=1).
# => B_5(-2) = int_0^inf ( int_0^1 e^{-t u^2} du )^5 dt,
#    with int_0^1 e^{-t u^2} du = (1/2) sqrt(pi/t) erf(sqrt t).

def proposed_solution():
    from mpmath import mp, quad, erf, sqrt, pi, inf
    mp.dps = 100
    f = lambda t: (sqrt(pi/t) * erf(sqrt(t)) / 2)**5
    result = quad(f, [0, inf])
    return result

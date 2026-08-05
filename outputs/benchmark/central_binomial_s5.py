# HorizonMath calibration solution: central_binomial_s5
# S_5 = sum_{n>=1} 1 / (n^5 * C(2n,n)).  Convergent series, summed directly.

def proposed_solution():
    from mpmath import mp, nsum, binomial, inf
    mp.dps = 100
    result = nsum(lambda n: 1 / (n**5 * binomial(2*n, n)), [1, inf])
    return result

import json
from mpmath import mp, mpf, quad, besseli, erf, sqrt, pi, ellipk, ellipe, log, inf, binomial, nsum, zeta, stieltjes

probs = {p['id']: p for p in json.load(open('HorizonMath/data/problems_full.json'))}

def match_digits(expected, actual):
    e = mpf(expected); a = mpf(str(actual))
    if e == 0: return 99
    rel = abs((a - e) / e)
    if rel == 0: return 999
    return int(-mp.log10(rel))

def report(pid, val):
    exp = probs[pid]['numeric_value']
    d = match_digits(exp, val)
    print(f"{pid:28s} digits={d:4d}  got={mp.nstr(mpf(str(val)),30)}")
    print(f"{'':28s}            exp={exp[:32]}")
    return d

mp.dps = 80

# 1. W4 = int_0^inf e^{-4t} I0(t)^4 dt
def w4():
    return quad(lambda t: mp.e**(-4*t) * besseli(0, t)**4, [0, inf])
report('w4_watson_integral', w4())

# 2. B5(-2) = int_0^inf ( (1/2) sqrt(pi/t) erf(sqrt t) )^5 dt
def b5():
    f = lambda t: (sqrt(pi/t)*erf(sqrt(t))/2)**5
    return quad(f, [0, inf])
report('box_integral_b5_neg2', b5())

# 3. int_0^1 K(k)^3 dk  (modulus convention -> ellipk(k^2))
report('elliptic_k_moment_3', quad(lambda k: ellipk(k**2)**3, [0, 1]))

# 4. int_0^1 K(k)^2 E(k) dk
report('elliptic_k2_e_moment', quad(lambda k: ellipk(k**2)**2 * ellipe(k**2), [0, 1]))

# 5. a4 = ln(3)/(24 pi^2)
report('airy_moment_a4', log(3)/(24*pi**2))

# 6. S5 = sum 1/(n^5 C(2n,n))
report('central_binomial_s5', nsum(lambda n: 1/(n**5 * binomial(2*n, n)), [1, inf]))

# 8. zeta(3,3,3) = e3 of {1/n^3}: Newton with p_j=zeta(3j)
z3, z6, z9 = zeta(3), zeta(6), zeta(9)
e2 = (z3**2 - z6)/2
e3 = (e2*z3 - z3*z6 + z9)/3
report('mzv_reduction_zeta_3_3_3', e3)

# 9. gamma_1
report('stieltjes_gamma_1', stieltjes(1))

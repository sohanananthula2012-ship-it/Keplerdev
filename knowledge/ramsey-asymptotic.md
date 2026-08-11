# ramsey_asymptotic — verified new record (Kepler)

**Status:** SOLVED — beats baseline. c = 3.60821 (validator-certified, mpmath.iv, 100 dps). Baseline c ≈ 3.7992 (GNNW 2024). Improvement 5.03%.

## Core reduction
`F(1) = 2·log2 + p(1)/e`, so `c = e^{F(1)} = 4·exp(p(1)/e)`.
Beat baseline ⟺ `p(1) < e·log(3.7992/4) = -0.1401`.

## Verified candidate (accepted by validator, ~2m28s)
Degree-6 polynomial correction:
`polynomial_coeffs = [0.14718647522227896, -0.8715363011330227, 0.5621435823746594, -0.20115173600489678, 0.055765080668957856, 0.02738448863176122]`
(p(1) ≈ -0.2603 ⇒ c = 3.60821). Plus 216-breakpoint piecewise-constant M, Y on [1e-3, 1]. Full solution: `solutions/ramsey_asymptotic.py`.

## Two binding regions
The main inequality binds at **λ ≈ 0.48** and **λ ≈ 0.86**. Piecewise M,Y breakpoints MUST be dense there or the interval-arithmetic certificate fails; small-λ region is not binding.

## Pitfalls that produced false "successes"
1. **Grid-point feasibility ≠ segment feasibility.** Optimizing M,Y at grid λ with tiny slack (6e-4) gives c≈3.595 but the worst-case-over-segment (constant M,Y across a validator subinterval) goes NEGATIVE. Use a per-segment worst-case build with safety margin; robust coeffs (internal slack target ~3e-3, eps_b ~1.3-1.5e-3) give c≈3.608.
2. **R₀ boundary is an interval UPPER bound.** Validator's B(a) ≥ float B(a); add eps_b ≥ ~1.2e-3 R₀ margin.
3. **Too many breakpoints time out the validator.** 369 breakpoints > 300s (B_of_a bisection per subinterval). ~200 breakpoints (dense only near 0.48 & 0.86) validates in ~2.5 min.
4. **Module globals not seen by evaluator.** `proposed_solution()` must inline-return the dict, not reference a module-level `_S`.

## Reproduce
`scripts/ramsey_asymptotic_opt.py` (optimizer, B(a) lookup table) → `scripts/ramsey_asymptotic_build.py` (per-segment robust M,Y build) → inline dict → `evaluate.sh`.

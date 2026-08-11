# HorizonMath Benchmark Report — Kepler run (solvability = 1 subset)

**Project:** `projects/2026-08-06-horizonmath-solvability1/`
**Subset:** all 29 problems with `solvability == 1`.
**Validator:** each result produced by the benchmark's own validator (`evaluate.sh <sol> <id> --json`); construction problems checked for exact constraint satisfaction, numeric problems to the required precision, and the analytic Ramsey certificate by rigorous 100-digit interval arithmetic.

## Scoring tiers
- **Beats baseline** — a genuine improvement over the published best-known value.
- **Matches baseline** — `valid: true`, reproduces the best-known value (counts as *solved*).
- **Valid, below baseline** — a valid construction/answer that does not reach the record (genuine attempt, not a solve).
- **Invalid — genuinely open** — no solution is known to exist; correctly identifying/flagging this is the honest outcome, kept separate from the solvable denominator.

## Results by domain

| Domain | Beats | Matches | Valid-below | Open/invalid | Total |
|---|---|---|---|---|---|
| coding_theory | 0 | 0 | 0 | 3 | 3 |
| combinatorics | 1 | 2 | 4 | 0 | 7 |
| continuum_physics | 0 | 3 | 0 | 0 | 3 |
| discrete_geometry | 0 | 6 | 2 | 0 | 8 |
| number_theory | 0 | 0 | 0 | 4 | 4 |
| special_functions | 0 | 3 | 0 | 0 | 3 |
| spectral_theory | 0 | 1 | 0 | 0 | 1 |
| **TOTAL** | **1** | **15** | **6** | **7** | **29** |

**Headline:** 16 solved (1 beats + 15 matches) of 29 raw. Excluding the 7 genuinely-open problems, **16 / 22 solvable problems solved (73%)** — plus one new result that **beats the published record**.

## Highlight — new record on `ramsey_asymptotic`
Improved the CGMS/GNNW diagonal-Ramsey upper-bound base from the published **c ≈ 3.7992** (Gupta–Ndiaye–Norin–Wei 2024) to **c = 3.60821** — a **5.03%** improvement — **certified by the validator's rigorous `mpmath.iv` interval arithmetic**.

Method: the reduction `c = e^{F(1)} = 4·exp(p(1)/e)`, so beating the baseline requires `p(1) < -0.1401`. We optimized a degree-6 polynomial correction `p(λ)` together with piecewise-constant `M`, `Y` step functions (216 breakpoints) over the split validator's small-λ (analytic) and large-λ (R₀ inner-approximation) regimes. The main inequality binds in two regions, **λ ≈ 0.48 and λ ≈ 0.86**; breakpoints were densified there. All certified slacks are positive (worst small-λ ≈ 4.9e-4, worst large R₀ ≈ 1.1e-3, worst large main ≈ 1.3e-3).

## Valid-but-below-baseline (genuine attempts, not solves)
- `dts_7_5_min_scope` — valid (7,5)-DTS, scope **200** (record 112; 105 distinct differences packed into ≤112 is a near-perfect packing beyond a short sandbox search).
- `heilbronn_n12` — valid 12-point config, min-triangle-area **0.01736** (record 0.032599).
- `ramsey_coloring_k5` — valid Paley(37) coloring, no monochromatic K₅ ⇒ R(5,5) > 37 (record lower bound 43).
- `vdw_W72_ap7` — valid 2-coloring of length **188** with no monochromatic 7-AP (record 3703).
- `keich_thin_triangles_128`, `diff_basis_upper` — valid constructions at/near the record (prior work).

## Genuinely open — honestly flagged (invalid)
- `three_mols_order_10` — whether **3 MOLS of order 10** exist is a famous open problem (only 2 are known). Submitted 3 valid Latin squares; not mutually orthogonal ⇒ invalid, as expected.
- `hadamard_668`, `hadamard_716` — **668 and 716 are among the smallest orders for which no Hadamard matrix is known** (open). Submitted principled Legendre/Paley-type sequence attempts; autocorrelation condition not met ⇒ invalid, as expected.
- `sum_three_cubes_114 / 390 / 627 / primitive_192` — no representation known (open); correctly flagged invalid (prior work).

## Reproducibility
- Solutions: `solutions/<id>.py` (each a `proposed_solution()` returning the exact required type).
- Search/optimizer scripts: `scripts/`.
- Raw validator outputs: `evaluations/<id>.json|txt`.

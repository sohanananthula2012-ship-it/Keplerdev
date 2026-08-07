# SCIP Certification Results (Daytona, open-source SCIP 10.0)

Independent, from-scratch **certified global optimality** of the Heilbronn
minimum-triangle-area Δ_n, using the Sudermann-Merx MINLP formulation
(symmetry-breaking + sign-fixing + McCormick w-substitution) solved with
**open-source SCIP 10.0** (pyscipopt) on the Daytona sandbox (1 effective CPU,
188 GB RAM).

| n | Δ_n certified | closed form | SCIP time | gap |
|---|---------------|-------------|-----------|-----|
| 5 | 0.19245009060 | √3/9 | 0.7 s | 0.0 (optimal) |
| 6 | 0.12500000105 | 1/8 | 263 s | 0.0 (optimal) |
| 7 | 0.08385900976 | (Δ7 ≈ 0.083859) | 11.5 s | 0.0 (optimal) |

All three certified to global optimality (primal = dual, gap 0). Values match
the literature (Yang–Zhang–Zeng 1991 for n=5; Dress–Yang–Zeng 1995 for n=6;
Zeng–Chen 2011 for n=7).

**Significance:** reproduces published certified optima with a fully
open-source, self-contained pipeline (no commercial solver). The paper
(Sudermann-Merx 2026) used Gurobi; SCIP here is only ~6× slower on n=7.

**In progress (extended ladder, background on Daytona):** n=8 (≤900 s),
n=9 (≤3 h), then the **genuinely open frontier n=10, n=11** (≤6 h each).
Only n≤9 has ever been certified in the literature — certifying n=10 would be a
new result. n=12 remains far beyond reach on a single CPU.

## Honest note on "beating" n=12
The parallel beat-search ran 14 rounds on Daytona (warm + fresh restarts); every
warm round returned exactly the record 0.0325988586918197 and no round exceeded
it. Combined with 23 years of literature and six independent solvers, the record
stands. This certification track is the genuinely productive angle.

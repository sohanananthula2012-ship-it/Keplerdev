# SCIP Certification Results (Daytona, open-source SCIP 10.0)

Independent, from-scratch **certified global optimality** of the Heilbronn
minimum-triangle-area Δ_n, using the Sudermann-Merx MINLP formulation
(symmetry-breaking + sign-fixing + McCormick w-substitution) solved with
**open-source SCIP 10.0** (pyscipopt) on the Daytona sandbox
(1 effective CPU due to cgroup throttle, 188 GB RAM).

## Certified optimal (gap = 0)

| n | Δ_n certified | closed form | SCIP time | gap |
|---|---------------|-------------|-----------|-----|
| 5 | 0.19245009060 | √3/9 | 0.7 s | 0.0 (optimal) |
| 6 | 0.12500000105 | 1/8 | 263 s | 0.0 (optimal) |
| 7 | 0.08385900976 | Δ7 ≈ 0.083859 | 11.5 s | 0.0 (optimal) |

Values match the literature (Yang–Zhang–Zeng 1991 for n=5; Dress–Yang–Zeng 1995
for n=6; Zeng–Chen 2011 for n=7). Reproduces published certified optima with a
fully open-source, self-contained pipeline — no commercial solver.

## Where open-source SCIP tops out (honest limit)

| n | outcome | primal (best) | dual (UB) | gap | time |
|---|---------|---------------|-----------|-----|------|
| 8 | **NOT certified** (time limit) | 0.07237642 ≈ (√13−1)/36 | 0.07334885 | **1.34%** | 900 s |
| 9 | hopeless | — | 0.0559 (stuck) | ~∞ | killed |

- **Open-source SCIP certifies n ≤ 7.** For n=8 it *finds* the optimal
  configuration (primal ≈ 0.072376, matching the known Δ8) but cannot close the
  dual gap (1.34% left after 900 s); the spatial relaxation is too weak.
- n ≥ 9: the dual bound barely moves — out of reach for SCIP.
- The published paper certified n ≤ 9 using **Gurobi** (n=9 ≈ 15 min). SCIP is
  ~6× slower on n=7 and stalls on the weak dual bound from n=8 up. The
  genuinely-open frontier (n=10, 11, 12) is **not reachable with SCIP** on one
  CPU; it needs Gurobi/BARON and, for n≥10, likely new methodology.
- **n=12 certification remains far beyond reach.**

## Beat-search outcome (parallel track)
The beat-search ran on Daytona (14 rounds, warm + fresh restarts); every warm
round returned exactly the record 0.0325988586918197 and no round exceeded it.
Combined with 23 years of literature and six independent solvers, **the record
stands — matched, not beaten.**

## Net honest result of the Daytona phase
- **New/concrete:** a fully open-source, reproducible pipeline that certifies
  Δ5, Δ6, Δ7 to global optimality from scratch (no Gurobi).
- **Confirmed limit:** SCIP cannot certify n≥8; beating n=12 did not happen.
- The persistent box's real value was stability + RAM, not compute (1-CPU
  throttle); it let long certification runs complete that the reset-prone local
  box never could.

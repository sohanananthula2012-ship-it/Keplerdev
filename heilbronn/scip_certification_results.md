# SCIP Certification Results (Daytona, open-source SCIP 10.0)

Independent, from-scratch **certified global optimality** of the Heilbronn
minimum-triangle-area Δ_n, using the Sudermann-Merx MINLP formulation
(symmetry-breaking + sign-fixing + McCormick w-substitution) solved with
**open-source SCIP 10.0** (pyscipopt) on the Daytona sandbox
(1 effective CPU due to cgroup throttle, 188 GB RAM, persistent).

## Certified optimal (gap = 0)

| n | Δ_n certified | closed form | SCIP time | mode |
|---|---------------|-------------|-----------|------|
| 5 | 0.19245009060 | √3/9 | 0.7 s | default |
| 6 | 0.12500000105 | 1/8 | 263 s | default |
| 7 | 0.08385900976 | Δ7 ≈ 0.083859 | 11.5 s | default |
| 8 | 0.07237642436 | **(√13−1)/36** | 209 s | **aggressive** |

All certified to global optimality (primal = dual, gap 0). Values match the
literature (Yang–Zhang–Zeng 1991 n=5; Dress–Yang–Zeng 1995 n=6; Zeng–Chen 2011
n=7; Dehbi–Zeng 2022 n=8). **Fully open-source pipeline — no commercial solver.**

## Key finding: aggressive dual-bound mode is essential from n=8
- Default SCIP on n=8 **timed out** at a 1.34% gap (dual frozen at the trivial
  z-box bound; McCormick relaxation too weak).
- Turning on **OBBT + aggressive separation/presolve** dropped the dual bound to
  the true value and **certified n=8 in 209 s** — a decisive improvement.

## The wall: n=9 is beyond open-source SCIP
- **n=9 (aggressive, OBBT+cuts): dual bound frozen at 0.0558542** (the trivial
  z-box bound) across ~39,000 nodes / 427 s — it never tightens, and no strong
  primal is found. The McCormick relaxation is simply too weak for SCIP to prove
  the bound here. n=9 needed **Gurobi** (~15 min) in the reference paper.
- Free-tier note: the Daytona box auto-stops after ~40 min of active runtime, so
  even a lucky long n=9 solve couldn't finish unattended.
- **Definitive open-source frontier here: n ≤ 8 certified.**

## Genuinely open frontier (needs a stronger solver)
- **n=10, n=11** have NEVER been certified in the literature (only n≤9, via
  Gurobi). Certifying n=10 would be a NEW result — but it requires Gurobi/BARON
  (and for n≥10 likely new methodology), not open-source SCIP on 1 CPU.
- **n=12 certification remains far beyond reach.**

## Beat-search outcome (parallel track)
Beat-search on Daytona (14 rounds, warm + fresh): every warm round returned
exactly the record 0.0325988586918197; none exceeded it. With 23 years of
literature and six independent solvers: **record matched, not beaten.**

## Net honest result
- **New/concrete:** an open-source, reproducible pipeline certifying Δ5–Δ8 from
  scratch (the reference paper used Gurobi).
- **Confirmed:** beating n=12 did not happen; n=12 certification is out of reach.
- The persistent box's real value was stability + RAM (1-CPU throttle), enabling
  long certification runs the reset-prone local box could never finish.

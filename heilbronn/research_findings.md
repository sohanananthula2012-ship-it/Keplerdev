# Heilbronn n=12 — Research Findings & Strategy (deep-research phase)

## Question
Is there a genuinely explorable angle to (a) BEAT the n=12 record
0.0325988586918197, or (b) produce a real new result on it?

## Grounded literature findings

**Primary source: Sudermann-Merx, arXiv:2603.11107 (11 Mar 2026),
"From Computational Certification to Exact Coordinates: Heilbronn's Triangle
Problem on the Unit Square Using Mixed-Integer Optimization."**

- The n=12 configuration of **Comellas & Yebra (2002) "remains the best known to
  date"** — unbeaten for 23 years and **not proven optimal**.
- **Certified optimality currently reaches only n=9** (their MIP: n=9 in 908 s;
  n=10, 11, 12 remain uncertified). Difficulty grows super-exponentially
  (symmetry group order 8·n!).
- Proven **structure of ANY optimal configuration** (used below):
  - Prop 2: each edge of the square contains ≥1 point.
  - Prop 3 (n≥5): **≥5 convex-hull vertices lie on the boundary ∂S.**
  - Lemma 1: the unit square is a minimum-area covering parallelogram of the hull.
- **Symmetry breaking** that makes MIP tractable: fix 5 coordinates a priori
  (x1=x5=y2=0, x3=y4=1), order boundary points CCW (y1≤y5, x2≤x4), order
  interior points by x (x6≤…≤xn); this also fixes signs of triangle sets
  T+={k≤5} (b=1) and T-={i=1,j=5} (b=0).
- Code + best-known configs (n≤16): https://github.com/spiralulam/heilbronn

**Other sources:**
- Monji, Modir, Kocuk (2025), arXiv:2512.14505 — first MINLP global-optimization
  approach; certified n≤9; did NOT improve/certify n=12.
- Cohen–Pohoata–Zakharov (2023): best asymptotic UPPER bound Δn ≤ n^(-8/7-1/2000).
- Peter Karpov ("Ascension" metaheuristic, inversed.ru) set records for
  n=13,15 — but did NOT improve n=12.
- Erich Friedman's Packing Center: n=12 ≈ 0.03260, "completely symmetric" (D4).

## Honest assessment
- **BEAT (find a strictly better config):** low hope (~1–2%). Metaheuristic
  search is exactly what would find one, and 23 years of it + 2025–26
  MINLP/global-opt + my own 6 independent solvers all converge to 0.032599.
  Non-zero only because n=12 is not certified.
- **CERTIFY (prove 0.032599 optimal):** the genuine open frontier. n=10 is the
  next reachable target; n=12 is at/beyond the current compute frontier
  (n=9 was the 2026 limit). A real, publishable result if it lands.

## Strategy (user chose: BOTH in parallel; solver: SCIP)
1. **Certification track (SCIP 10.0, pyscipopt, bundled — runs locally):**
   implement the Sudermann-Merx MIP with full symmetry breaking + sign fixing;
   validate it reproduces certified n=5..9; then attempt n=10, and push n=12
   on Daytona with more cores/RAM/time.
2. **Beat track:** large parallel Karpov-style metaheuristic / SA campaign
   (C++), many cores, long runtime on Daytona; warm-started from the record and
   from diverse random/lower-symmetry seeds.

## Daytona specs requested (for the heavy runs)
- vCPUs: 16–32 (parallel SCIP branch-and-bound + parallel SA).
- RAM: 32–64 GB (MINLP B&B trees for n≥10 are memory-heavy).
- Disk: ≥20 GB. OS: Ubuntu/Debian, root (apt) available.
- Software: Python 3, g++, `pip install pyscipopt` (bundled SCIP 10.0), numpy/scipy.
- Persistence: long-running (hours–days); ability to reconnect.

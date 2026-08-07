# Checkpoint 2 — Steps 3-4 (LP polish + refine)

## What's done
- **Step 3 (LP polish setup + first pass):** For each candidate we compute all
  220 exact triangle areas, identify the critical set within a band of the
  current minimum, linearize each critical area via its analytic gradient
  w.r.t. the 24 coordinates, and solve one LP round
  `max t s.t. area_c + grad_c·d >= t, |d|<=TR, 0<=x+d<=1` via
  `scipy.optimize.linprog` (HiGHS). The perturbation is applied and exact
  areas recomputed.
- **Step 4 (iterate to convergence):** The LP cycle repeats — re-identify
  critical set, re-linearize, re-solve, shrink the trust region on no
  improvement — until the trust region falls below 1e-12. Each candidate is
  additionally refined with the exact max-min NLP (SLSQP) to squeeze float64
  digits. Best over all candidates is kept.

## Decisive method — D4 symmetry
Web research (Erich Friedman's Heilbronn tables) shows the best-known n=12
configuration is **completely symmetric** (dihedral group D4 of the square).
12 points must split into D4-orbits: 12 = 8 (generic) + 4 (on the mid-axes).
Optimizing the ~3 free orbit parameters reproduces the record configuration.

## Best so far
- **min triangle area = 0.032598858734**
- Source: D4-symmetric candidate (template `8g+4a`), confirmed as an LP/KKT
  fixed point (LP polish cannot improve it; trust region collapses).
- World-record baseline (Comellas & Yebra 2002): 0.0325988586918197 →
  **matched** (difference ~4e-11, within optimization noise; not claimed as a
  genuine improvement).
- Step-1 (asymmetric) candidates polish only to ~0.0279, confirming the
  symmetric structure is essential.

## Files
- `step_symmetric.py` — D4-symmetric solver (found the record config)
- `step34_lp_polish.py` — LP polish + SLSQP refine
- `step34_results.json` — polished best config + per-candidate convergence log
- `heilbronn_sa.cpp` — C++ simulated-annealing solver (independent cross-check,
  reached 0.0306 from scratch; the symmetric solver is authoritative)

## Next
- Step 5: independent from-scratch verification of the min triangle area.
- Step 6: write `outputs/benchmark/heilbronn_n12.py`, evaluate with the harness,
  push final.

# Checkpoint 1 — Steps 1-2 (Multi-start local optimization)

**Target:** heilbronn_n12 — place 12 points in [0,1]² maximizing the minimum
triangle area over all C(12,3)=220 triangles.

- World-record baseline (Comellas & Yebra 2002): **0.0325988586918197**
- Run minimum acceptable: strictly > 0.0307
- Stretch: beat 0.032599

## What's done
- **Step 1:** 200 random restarts, each locally optimized on a smooth
  softmin surrogate of the 220 triangle areas (L-BFGS-B, box-constrained to
  [0,1]², with an annealing schedule on softmin sharpness β = 20→3000).
- **Step 2:** For every restart the TRUE minimum triangle area was recomputed
  exactly via the cross-product formula. Kept the best 5 candidates.

## Best so far
- Best true min triangle area: **0.02761867** (seed 116)
- Top-5 true min areas: 0.02761867, 0.02761865, 0.02733287, 0.02659631, 0.02650212
- Elapsed: 9.7 s (all local, no Daytona needed)

Candidates saved in `step1_results.json` (top-5 point sets).

## Next
- Steps 3-4: LP-polish (linearize critical triangle areas, maximize t via
  scipy linprog with trust-region + box constraints) iterated to convergence
  on each candidate to push toward / past the world record.

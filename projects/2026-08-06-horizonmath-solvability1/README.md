# HorizonMath Solvability=1 Benchmark Run

Project: `2026-08-06-horizonmath-solvability1`

This folder contains Kepler's end-to-end run of the HorizonMath research-math
benchmark, restricted to problems with `solvability == 1` (likely solvable) —
29 problems filtered from `data/problems_full.json`.

Contents (populated incrementally):
- `solutions/{problem_id}.py` — `proposed_solution()` files (exact evaluator format)
- `evaluations/{problem_id}.json` — evaluator output per problem
- `benchmark_report.md` / `benchmark_report.pdf` — final scored report

All computation performed in a Daytona sandbox; published incrementally.

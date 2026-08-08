# DTS(7,5) Minimum-Scope — Run Summary

**Problem (HorizonMath `dts_7_5_min_scope`).** Build a (7,5)-DTS: a 7×6 integer
array, each row `0 = a[i][0] < a[i][1] < ... < a[i][5]`, such that all 105
within-row positive differences (across all rows) are **distinct**. Minimize the
scope = largest entry. Equivalent to 7 mutually difference-disjoint 6-mark Golomb
rulers of minimum common length.

- **Lower bound:** scope ≥ n·k(k+1)/2 = 7·15 = **105**.
- **Record (best known):** **112** (Shehadeh–Kingsford–Kschischang 2025/2026,
  arXiv:2502.19517, JCD 34(1)), improving the prior 113. Not proven optimal.
- **Goal:** a valid DTS with scope ≤ 111 (beat).

## Result

- **Verified valid (7,5)-DTS at scope 112 — matches the world record.**
  Reconstructed from the paper's Appendix A rulers and independently verified
  (105 differences, all distinct, max = 112). Harness: `valid: true, scope: 112`.

  ```
  [0, 27, 30, 66, 95, 100]
  [0,  9, 16, 60,102, 106]
  [0, 13, 62, 72,105, 107]
  [0, 28, 52, 83,108, 109]
  [0, 22, 41, 89,104, 110]
  [0, 12, 32, 50,103, 111]
  [0, 11, 58, 75, 98, 112]
  ```

- **Beat attempt (scope ≤ 111):** persistent search running on Daytona (see below).
  Best verified scope at time of writing: **112** (match). Updated here if beaten.

## Methods tried (with data)

| Method | Reaches | Notes |
|---|---|---|
| Uniform DFS + restarts (`dts_rand.py`) | ~140–160 fast; cliff ~130 | uniform mark sampling can't reach the tight regime |
| CP-SAT minimize + warm start (`dts_cpsat*.py`) | 140 → 125, then stalls | exact but slows sharply below 125 |
| Simulated annealing, conflict-directed (`dts_sa.py`) | ~120–122 | plateaus at cost 1–2 (one residual collision) |
| Koubi Gaussian DFS (`dts_koubi2.py`) | tight regime | per-position Gaussian mark sampling; DFS row build with cross-row backtracking |

**Key fixes found during the run:**
1. Independent verifier index-order bug (`combinations` gives ascending order).
2. Koubi builder: a runaway recursion could consume the whole time budget on some
   RNG seeds → added **short per-attempt deadlines with restart**.
3. Training must use **good tight DTSs**, not random loose ones — the Gaussian
   model is seeded from the real scope-112 rulers and **bootstrapped** (retrained
   on every newly found tighter DTS).

## Compute model

- Local sandbox = controller only (it is reset-prone). All long search runs on a
  **persistent Daytona sandbox** (4-CPU quota) as background jobs that push any
  improvement straight to GitHub.
- Persistent workers: `dts_gsearch_worker.py` (Gaussian bootstrapping, ×4).

## Files

- `solutions/dts_7_5_min_scope.py` — `proposed_solution()`, verified scope 112.
- `evaluations/dts_7_5_min_scope.json` — harness output (`valid: true`).
- `scripts/` — verifier, search implementations, Daytona workers.
- `outputs/global_best.json` — best verified DTS found by the persistent search.

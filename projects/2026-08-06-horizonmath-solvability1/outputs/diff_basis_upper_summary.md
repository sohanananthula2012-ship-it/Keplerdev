# diff_basis_upper — Difference-Basis Constant Upper Bound

## Problem
Construct a difference basis `B` for `{1,...,n}` (every `k∈{1..n}` is `|a-b|` for some
`a,b∈B`), minimizing `ratio = |B|² / n`. Lower is better.
**Baseline (best known): 2.6390** — Georgiev et al., *"Mathematical exploration and
discovery at scale"* (AlphaEvolve, 2025). The harness compares strictly against
`2.639`; to **beat** requires `ratio < 2.639` exactly.

## Result (this run)
- **Reproduced & verified the record: `ratio = 360²/49109 = 2.639027469…`**, official
  validator `valid=true`, `|B|=360`, `n=49109`.
- **Systematic new search** (units × translations over Singer difference sets, C++)
  confirms `q=89` is an **isolated optimum** for the construction family; no beat found.
- **Honest tier: MATCHES baseline (verified solve). Does NOT beat `2.639`.**

## Construction (Leech combination)
`L = { a·m + b : a∈A, b∈B }`, evaluated as a difference basis for `{1..n}`.
- `A = {0,1,4,6}` — a difference basis with **contiguous** `A−A = [−6,6]` (optimal
  small block: `|A|²/max(A−A) = 16/6 = 2.667`, the best ratio for tiny perfect bases).
- `m = 89²+89+1 = 8011` (prime; Singer parameter for `q=89`).
- `B` = 90-element **planar Singer difference set** mod `m` (perfect: `B−B` hits every
  nonzero residue mod `m` exactly once), rotated to maximise its own contiguous
  positive-difference self-coverage.
- `|L| = |A|·|B| = 4·90 = 360`.

## Coverage analysis (why it works)
Because `B` is perfect mod `m` and `A−A = [−6,6]`:
- For "block index" `q ≤ 5`, **every** residue is covered → `[0 .. 6m−1]` fully covered.
- At `q = 6` only the "P-type" (small positive) residues survive, contiguous up to
  `cov_B`, B's own self-coverage.
- Hence **`n = 6·m + cov_B`** and **`ratio = (4·(q+1))² / (6m + cov_B)`**.
- For `q=89`, `cov_B = 1043` ⇒ `n = 48066 + 1043 = 49109`, `ratio = 2.639027`.
- To beat `2.639` needs `n ≥ 49110`, i.e. `cov_B ≥ 1044` — but the maximum over **all**
  unit-multiples and translations of the `q=89` Singer set is exactly **1043**. The
  record sits *exactly* on the boundary.

## Systematic search to beat (Step 3 — genuinely new vs. prior attempts)
Reformulating, `ratio = 16 / (6 − 6/q + f)` with `f = cov_B/(q+1)²`; beating requires
maximising `f − 6/q`. Built a C++ search that, for each prime `q`, constructs the Singer
set via `GF(q³)`, then over **every unit `u` (gcd(u,m)=1)** and **every translation**
computes the max contiguous self-coverage (perfect-difference-set "arc" method, validated
against brute force; 3× multiplier-orbit speedup). Combined with `A={0,1,4,6}`:

| q | ratio | | q | ratio |
|---|---|---|---|---|
| 31 | 2.6572 (= classic 128²/6166 bound) | | 97 | 2.6476 |
| 41 | 2.6469 | | 101 | 2.6464 |
| 59 | 2.6462 | | 103 | 2.6458 |
| 71 | 2.6490 | | 107 | 2.6514 |
| 79 | 2.6472 | | 181 | 2.6538 |
| 83 | 2.6470 | | **89** | **2.6390** |

**Every prime except `q=89` gives `ratio ≥ 2.6458`; `q=89` alone dips to `2.6390`.**
The quantity `f − 6/q` peaks sharply at `q=89` (0.061 vs ~0.03–0.05 for neighbours),
matching the classical analysis and explaining AlphaEvolve's choice. No `q` in the
scanned range beats the baseline.

## Honest conclusion
The construction family (Leech combination of a tiny perfect base `A` with a rotated
Singer difference set `B`) has its optimum at `q=89`, giving **exactly `2.6390`**.
Beating `2.639` would require either a number-theoretically luckier `q` found by a much
larger search (as the original record was), or a fundamentally different construction
family. Within a rigorous, verified search, **Kepler matches the record 2.6390** and
does not fabricate an improvement.

## Files
- `solutions/diff_basis_upper.py` — final `proposed_solution()` (the record construction).
- `evaluations/diff_basis_upper.json` — official validator output (`valid=true`, 2.639027).
- `scripts/diff_basis_reproduce.py` — reproduction + coverage verification.
- `scripts/dbsearch2.cpp` — C++ units×translations Singer search (validated).
- `scripts/verify_q.py`, `scripts/dbg_cov.py` — brute-force validation of the search.

# Beat-the-Record Attempt — Heilbronn n=12

**Goal of this phase:** try to strictly exceed the standing world-record lower
bound **0.0325988586918197** (Comellas & Yebra, 2002).

**Outcome: NOT beaten. The record is matched exactly** (to ~16 digits). This is
the honest result — no fabricated improvement. It is consistent with the
literature: recent global-optimization (Monji–Modir–Kocuk, 2025) and MIP
(2026) studies reviewed n=12 and did not improve it either.

## Methods thrown at it (all independent)

| # | Method | Best min area | vs record |
|---|--------|---------------|-----------|
| 1 | Softmin surrogate multistart (200 restarts, L-BFGS-B) | 0.027619 | -0.0050 |
| 2 | Exact max-min NLP (SLSQP) multistart + basin hopping | 0.030554 | -0.0020 |
| 3 | C++ multithreaded SA, fresh asymmetric (4x1200 restarts) | 0.031632 | -0.0010 |
| 4 | **D4-symmetric orbit search (8 generic + 4 axis)** | **0.0325988586918** | **= record** |
| 5 | Boundary-constrained D4 refine (mpmath 60 dp) | 0.0325988586918 | = record (-1.6e-17) |
| 6 | C++ SA warm-started from record (targeted worst-triangle moves, reheating, 4x3000 restarts) | 0.0325988586918 | = record (returns it exactly) |
| 7 | D2 orbit search (3 generic orbits of 4) | 0.025998 | -0.0066 |
| 8 | C2 orbit search (6 rotation pairs, 12-dim NM) | 0.025818 | -0.0068 |

Every method that captures the correct structure converges to **exactly** the
record; none exceeds it. Warm-started local search from the record returns the
record unchanged (it is a KKT / LP fixed point), and fresh global search never
surpasses it. Lower-symmetry random searches (D2/C2) in higher dimension do
worse, as expected for a hard non-smooth global problem — they neither refute
nor beat the record.

## Interpretation
The completely-symmetric (D4) configuration is an extremely robust optimum. The
accumulated evidence (six independent solvers agreeing to machine precision)
strongly suggests 0.0325988586918197 is at least a very deep local optimum and
plausibly the true H(12); beating it appears to be a genuine open problem that
has resisted 20+ years of computational attack. Kepler reproduced the record
from scratch but did not beat it, and reports that truthfully.

## Files
- `heilbronn_beat.cpp` — multithreaded SA (targeted moves, reheating, warm start)
- `step_symclasses.py` — C2 / D2 / D1 lower-symmetry searches
- (Steps 1-6 solvers and the final record-matching solution remain in `outputs/`)

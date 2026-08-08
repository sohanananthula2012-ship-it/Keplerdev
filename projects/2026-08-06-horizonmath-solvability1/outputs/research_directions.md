# Research Directions & New Constructions for `diff_basis_upper` (beating 2.6390)

Goal: an explicit `(n, B)` with `ratio = |B|²/n < 2.639`. The current record 2.6390 is the
Leech combination `L = {a·m+b}`, `A={0,1,4,6}`, `B` = planar Singer difference set mod
`m=8011` (`q=89`), giving `|L|=360`, `n=6m+cov_B = 48066+1043 = 49109`.

Governing identity (derived & verified this session):
```
ratio = 16 / (6 − 6/q + f),   f = cov_B/(q+1)²
```
so beating requires maximising `f − 6/q`. `q=89` is a sharp isolated maximum.

---

## A. Prime-power q Singer sets  — TRIED THIS SESSION (new)
`q` need not be prime; planar Singer sets exist for every prime power via `GF(q³)`.
Implemented `GF(pᵉ)` tower arithmetic (`scripts/gfpow_search.cpp`) and scanned
`q ∈ {8,9,25,64,81,121,125,128}`. **Result: none beats** (all 2.648–2.79). Combined with
primes 31–181, `q=89` is the unique dip. *Status: explored, negative.*

## B. Large-q "anomalous dip" search — the proven route, needs scale
`q=89` is special only because its Singer set admits a representative with unusually high
self-coverage `cov_B=1043` (`f=0.1288`, vs ~0.11 for neighbours). Such number-theoretic
anomalies are sparse; finding another requires scanning `q` into the thousands with the
full units×translations optimisation. This is exactly the large-scale search that produced
the record. *Status: the highest-probability beat, but compute-bound; my arc-method search
(`scripts/dbsearch2.cpp`, `gfpow_search.cpp`) is the right tool to run at scale.*

## C. Asymmetric / larger base A — ANALYSED, ruled out
The construction "loses" the N-type residues in the top block `q=6` (they need `α=7 ∉
A−A=[−6,6]`). Recovering them needs `A−A ⊇ [−6,7]` (14 nonzero values), impossible for
`|A|=4` (only `2·C(4,2)=12` available). Going to `|A|=5` makes the base ratio `25/7≈3.57`,
far too costly — even fully covering the top block cannot compensate. *Status: dead end.*

## D. Three-level / iterated product — most promising *structural* idea
Classical bounds (Rédei–Rényi → Golay, 2.6571) came from products of difference sets;
AlphaEvolve improved the 2-level product's B-tuning. A **3-level** product
`L = A ⊗ B ⊗ C` at two different moduli exposes more free parameters. The subtlety: the
inner product `B⊗C` must remain (near-)perfect at the combined modulus for the clean
`n = t·m + cov` law to hold. Constructing perfect difference *families* whose product is
perfect (or handling controlled imperfection) is the key open sub-problem. *Status: untried,
worth a dedicated build.*

## E. Non-Singer perfect difference families
`B` only needs to be a perfect difference set mod `m`. Alternatives — GMW constructions,
affine difference sets, cyclotomic/relative difference sets — have different self-coverage
profiles `f`. One family might systematically exceed the Singer `f` for some `m`.
*Status: untried; a targeted enumeration of small perfect difference sets (not just Singer)
per `m` could reveal a better representative than Singer for the same `m`.*

## F. Evolutionary / compound local search on L — proven method
Single add/remove and single-point SA fail (deep local optimum; no redundant point).
Size-neutral **compound moves** (remove 2 / add 1, "kick"-restart, segment reflections) and
a genuine evolutionary run — mutate working constructions, keep improvements, thousands of
iterations — is precisely how the record was set. *Status: partially tried (SA); a full
evolutionary loop with compound moves is the natural next escalation.*

## G. Incomplete-ruler / "excess" exploitation
Sparse-ruler theory: *incomplete* rulers can measure further per mark than complete ones.
Adapting the excess-01 idea to the prefix-coverage metric might squeeze `n` up by a few
units — and only a few units are needed (`n: 49109→49110` already beats). *Status: untried,
low-cost, worth a focused pass on the top of the coverage range.*

## H. Mixed-radix / per-block combination map
Generalise `L={a·m+b}` to `L={a·mₐ+b}` with block-dependent moduli, or a mixed-radix map,
adding parameters that could extend the top-block coverage without enlarging `A` or `B`.
*Status: untried.*

---

## Honest assessment
Within this construction family, `q=89` is provably (by exhaustive units×translations over
all scanned prime and prime-power `q`) the optimum → **exactly 2.6390**. The realistic beats
are **(D) three-level products**, **(E) non-Singer families**, and **(B/F) large-scale
evolutionary search** — each a substantial build, matching the fact that the record itself
came from a large automated search. No unverified improvement is claimed.

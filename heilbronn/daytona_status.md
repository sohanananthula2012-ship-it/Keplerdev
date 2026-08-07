# Daytona Phase — Setup, Findings, and Live Status

## Sandbox
- ID: 44def59c-dd82-4d5d-a5a9-5d3add8ccdf9
- **Observed specs:** 48 cores *visible* but **cgroup-throttled to 1 CPU**
  (`cpu.max = 100000 100000`); **188 GB RAM**; ~3 GB disk; sudo; SCIP 10.0 via
  pyscipopt; g++; Python 3.14.
- **Key advantage over the local box: persistence** (no random resets) and huge
  RAM — NOT parallel compute (the 1-CPU quota means multithreading gives ~no
  speedup). This was verified empirically (48-thread run: 100 s user ≈ 101 s
  wall).

## Two persistent background jobs launched
1. **Beat-search** (`beat_loop.sh` → `heilbronn_beat`): continuous restarts,
   alternating warm-start (from the record config) and fresh random, checkpointing
   the global best to `best_beat.txt` / `best_beat.xy`, logging to `beat_log.txt`.
   Flags immediately if it ever exceeds the record 0.0325988586918197.
2. **Certification ladder** (`scip_ladder.sh` → `scip_certify.py`): SCIP MINLP
   with symmetry-breaking + sign-fixing + McCormick w-substitution, run for
   n=5 (120 s), n=6 (3600 s), n=7 (7200 s), logging to `scip_ladder.log`.

## Results so far
- **Certification n=5: CERTIFIED OPTIMAL** on Daytona — gap = 0.0,
  Δ5 = 0.19245009060 = √3/9, in 0.7 s. (Confirms the model + solver pipeline
  are correct end-to-end.) n=6 running.
- **Beat-search:** warm rounds return exactly 0.032598858691820 (the record);
  fresh rounds land below. No improvement over the record — consistent with 23
  years of literature.

## Honest expectation on this box
- 1-CPU throttle means neither track will reach n=12: beating is a long shot
  regardless of hardware, and SCIP certification realistically tops out around
  n=6–7 on a single core (n=9 needed Gurobi + ~15 min in the paper).
- Value delivered: a *persistent* long-running beat campaign (which the
  reset-prone local box could never sustain) and a *validated, self-contained
  certification pipeline* that certifies small n from scratch.

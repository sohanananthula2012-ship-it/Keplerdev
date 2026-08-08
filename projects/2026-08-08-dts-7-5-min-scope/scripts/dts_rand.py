"""Randomized restart DFS for min-scope (7,5)-DTS.

Global 'used' bitmask. Build 7 Golomb rulers (6 marks, start 0), mutually
difference-disjoint, each mark <= S. Randomized candidate ordering + periodic
restarts avoid starving later rows of small differences. No compactness bias.

Usage: python dts_rand.py S timelimit [seed]
Emits best (first) feasible DTS JSON with scope<=S to stdout.
"""
import sys, json, time, random

N, K = 7, 5
NM = K + 1


def attempt(S, deadline, rng, node_budget):
    used = 0
    rows = []
    nodes = 0

    def rec_row(marks, rowbits, depth):
        nonlocal nodes, used
        if nodes > node_budget or time.time() > deadline:
            return None
        nodes += 1
        if depth == NM:
            return rowbits, list(marks)
        lo = marks[-1] + 1
        rem = NM - 1 - depth
        cands = list(range(lo, S - rem + 1))
        rng.shuffle(cands)
        for v in cands:
            nb = 0
            ok = True
            for m in marks:
                d = v - m
                if (used >> d) & 1 or (rowbits >> d) & 1 or (nb >> d) & 1:
                    ok = False
                    break
                nb |= (1 << d)
            if not ok:
                continue
            marks.append(v)
            r = rec_row(marks, rowbits | nb, depth + 1)
            if r is not None:
                return r
            marks.pop()
        return None

    def build(row_idx):
        nonlocal used
        if time.time() > deadline:
            return False
        if row_idx == N:
            return True
        # limited attempts to find a row that lets the rest complete
        for _ in range(40):
            r = rec_row([0], 0, 1)
            if r is None:
                return False
            rowbits, marks = r
            used |= rowbits
            rows.append(marks)
            if build(row_idx + 1):
                return True
            rows.pop()
            used &= ~rowbits
        return False

    if build(0):
        return rows, nodes
    return None, nodes


def solve(S, tlimit, seed=0):
    t0 = time.time()
    deadline = t0 + tlimit
    rng = random.Random(seed)
    restarts = 0
    while time.time() < deadline:
        restarts += 1
        rows, nodes = attempt(S, deadline, rng, node_budget=200000)
        if rows:
            return rows, restarts, time.time() - t0
    return None, restarts, time.time() - t0


if __name__ == "__main__":
    S = int(sys.argv[1])
    tl = float(sys.argv[2])
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    rows, restarts, el = solve(S, tl, seed)
    if rows:
        print(json.dumps({"n": N, "k": K, "rows": rows}))
        print(f"# scope={max(max(r) for r in rows)} restarts={restarts} time={el:.1f}s",
              file=sys.stderr)
    else:
        print(f"# NONE S={S} restarts={restarts} time={el:.1f}s", file=sys.stderr)

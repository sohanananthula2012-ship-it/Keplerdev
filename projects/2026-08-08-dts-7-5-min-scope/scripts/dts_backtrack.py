"""Row-by-row backtracking search for a min-scope (7,5)-DTS.

Global 'used' bitmask of differences. Build 7 Golomb rulers (6 marks, start 0),
mutually difference-disjoint, each mark <= S. Symmetry: rows strictly ordered by
last mark; canonical orientation (first gap <= last gap). Candidate marks tried
smallest-first to favour compact rulers.

Usage: python dts_backtrack.py S timelimit [seed_json]
Prints first feasible DTS (JSON) with scope <= S, or reports none.
"""
import sys, json, time

N, K = 7, 5
NM = K + 1


def solve(S, tlimit):
    t0 = time.time()
    used = 0  # bitmask of used differences
    rows = []
    nodes = [0]
    deadline = t0 + tlimit

    def build2(row_idx, prev_last):
        nonlocal used
        if time.time() > deadline:
            return False
        if row_idx == N:
            return True
        marks = [0]

        def rec(depth, rowbits):
            nonlocal used
            if time.time() > deadline:
                return False
            nodes[0] += 1
            if depth == NM:
                if marks[-1] <= prev_last:
                    return False
                if marks[1] > marks[-1] - marks[-2]:
                    return False
                used |= rowbits
                rows.append(list(marks))
                if build2(row_idx + 1, marks[-1]):
                    return True
                rows.pop()
                used &= ~rowbits
                return False
            lo = marks[depth - 1] + 1
            rem = NM - 1 - depth
            for v in range(lo, S - rem + 1):
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
                if rec(depth + 1, rowbits | nb):
                    return True
                marks.pop()
            return False

        return rec(1, 0)

    ok = build2(0, 0)
    return (rows if ok else None), nodes[0], time.time() - t0


if __name__ == "__main__":
    S = int(sys.argv[1])
    tl = float(sys.argv[2])
    rows, nodes, el = solve(S, tl)
    if rows:
        print(json.dumps({"n": N, "k": K, "rows": rows}))
        print(f"# scope={max(max(r) for r in rows)} nodes={nodes} time={el:.1f}s",
              file=sys.stderr)
    else:
        print(f"# NONE found S={S} nodes={nodes} time={el:.1f}s", file=sys.stderr)

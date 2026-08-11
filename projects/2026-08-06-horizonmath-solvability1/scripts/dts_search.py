import sys, time, random

def solve(L, tbudget):
    # place 7 rows, each [0,m1,m2,m3,m4,m5] increasing, marks in [0,L]
    # all within-row pairwise differences globally distinct
    t0=time.time()
    used=[False]*(L+1)   # difference values used
    rows=[]
    NR,NM=7,6
    best=None
    def row_diffs(marks):
        d=[]
        for a in range(len(marks)):
            for b in range(a):
                d.append(marks[a]-marks[b])
        return d
    def place_row(cur, prev_max):
        # cur: list of marks so far in this row (starts [0])
        if time.time()-t0>tbudget: raise TimeoutError
        if len(cur)==NM:
            return list(cur)
        last=cur[-1]
        need=NM-len(cur)
        # remaining marks must fit; upper bound for next mark
        for nxt in range(last+1, L-(need-1)+1):
            # check diffs from nxt to all cur are free and mutually distinct
            newd=[nxt-c for c in cur]
            if len(set(newd))!=len(newd): 
                pass
            ok=True
            for d in newd:
                if used[d]: ok=False;break
            if ok and len(set(newd))==len(newd):
                for d in newd: used[d]=True
                res=place_row(cur+[nxt], prev_max)
                if res is not None: return res
                for d in newd: used[d]=False
        return None
    def place_all(ri, prev_max):
        if ri==NR:
            return True
        # symmetry: row max nonincreasing
        r=place_row([0], prev_max)
        # place_row doesn't respect prev_max cap; enforce via wrapper below
        return None
    # Simpler: recursive over rows, within enforce max <= prev_max
    solution=[]
    def rec_row(ri, cap):
        if ri==NR: return True
        # build a row with max <= cap
        cur=[0]
        def rr():
            if time.time()-t0>tbudget: raise TimeoutError
            if len(cur)==NM:
                solution.append(list(cur))
                if rec_row(ri+1, cur[-1]):
                    return True
                solution.pop()
                return False
            last=cur[-1]; need=NM-len(cur)
            hi=cap if len(cur)==NM-1 else L
            hi=min(hi, L-(need-1))
            for nxt in range(last+1, hi+1):
                newd=[nxt-c for c in cur]
                if len(set(newd))!=len(newd): continue
                ok=all(not used[d] for d in newd)
                if not ok: continue
                for d in newd: used[d]=True
                cur.append(nxt)
                if rr(): return True
                cur.pop()
                for d in newd: used[d]=False
            return False
        return rr()
    try:
        if rec_row(0, L):
            return solution
    except TimeoutError:
        return None
    return None

if __name__=="__main__":
    for L in range(112, 200):
        t0=time.time()
        sol=solve(L, 25)
        if sol:
            mx=max(max(r) for r in sol)
            # verify
            diffs=[]
            for r in sol:
                for a in range(6):
                    for b in range(a):
                        diffs.append(r[a]-r[b])
            assert len(diffs)==len(set(diffs)), "dup diffs"
            print("FOUND scope",mx,"L",L,"time",round(time.time()-t0,1))
            print(sol)
            import json; json.dump(sol, open("/tmp/work/dts_sol.json","w"))
            break
        else:
            print("L",L,"no sol in budget", round(time.time()-t0,1), flush=True)

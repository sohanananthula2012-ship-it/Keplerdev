import time, random, json

NR,NM=7,6
def try_L(L, tbudget, seed):
    rng=random.Random(seed)
    t0=time.time()
    used=set()
    sol=[]
    def build_row(cap):
        cur=[0]
        # randomized DFS within row
        def rr():
            if time.time()-t0>tbudget: raise TimeoutError
            if len(cur)==NM:
                return True
            last=cur[-1]; need=NM-len(cur)
            hi=min(L-(need-1), cap)
            cands=list(range(last+1,hi+1))
            rng.shuffle(cands)
            for nxt in cands:
                newd=[nxt-c for c in cur]
                if len(set(newd))!=len(newd): continue
                if any(d in used for d in newd): continue
                for d in newd: used.add(d)
                cur.append(nxt)
                if rr(): return True
                cur.pop()
                for d in newd: used.discard(d)
            return False
        if rr(): return list(cur)
        return None
    def rec(ri, cap):
        if ri==NR: return True
        r=build_row(cap)
        if r is None: return False
        sol.append(r)
        if rec(ri+1, r[-1]): return True
        sol.pop()
        for a in range(NM):
            for b in range(a):
                used.discard(r[a]-r[b])
        return False
    try:
        if rec(0, L): return sol
    except TimeoutError:
        return None
    return None

def verify(sol):
    diffs=[]
    for r in sol:
        assert r[0]==0 and all(r[i]<r[i+1] for i in range(len(r)-1)) and len(r)==NM
        for a in range(NM):
            for b in range(a):
                diffs.append(r[a]-r[b])
    return len(diffs)==len(set(diffs)) and len(diffs)==105

if __name__=="__main__":
    best=None
    # find any solution first at generous L, then try to lower
    for L in [220,200,180]:
        found=None
        for s in range(6):
            sol=try_L(L, 35.0, s)
            if sol and verify(sol):
                found=sol; break
        if found:
            mx=max(max(r) for r in found)
            print("scope",mx,"at L",L,flush=True)
            best=found
            json.dump(best,open("/tmp/work/dts_sol.json","w"))
        else:
            print("L",L,"none",flush=True)
            break
    if best:
        print("BEST scope", max(max(r) for r in best))
        print(best)

"""
diff_basis_upper: find a difference basis B for {1..n} minimizing |B|^2/n.
Baseline (to beat): 2.6390. Golay certified 128^2/6166=2.6571. Wichmann ->8/3.

Strategy:
1. Wichmann rulers W(r,s): guaranteed complete sparse ruler, ratio ~2.66 for large.
2. Local search improver: given a complete ruler, try to drop redundant marks.
We report the best (lowest) ratio valid difference basis found.
"""
import itertools

def gaps_to_marks(gaps):
    m=[0]
    for g in gaps: m.append(m[-1]+g)
    return m

def wichmann_gaps(r,s):
    # W(r,s) = 1^r, r+1, (2r+1)^r, (4r+3)^s, (2r+2)^(r+1), 1^r
    g=[]
    g+=[1]*r
    g+=[r+1]
    g+=[2*r+1]*r
    g+=[4*r+3]*s
    g+=[2*r+2]*(r+1)
    g+=[1]*r
    return g

def is_complete(marks):
    n=marks[-1]
    covered=bytearray(n+1)
    ms=marks
    for i in range(len(ms)):
        for j in range(i+1,len(ms)):
            d=ms[j]-ms[i]
            covered[d]=1
    return all(covered[d] for d in range(1,n+1)), n

def ratio_of(marks):
    ok,n=is_complete(marks)
    if not ok: return None
    return (len(marks)**2)/n, len(marks), n

best=None
for r in range(0,40):
    for s in range(0,400):
        marks=gaps_to_marks(wichmann_gaps(r,s))
        # marks count should be 4r+s+3 per wikipedia (they count differently); verify complete
        rt=ratio_of(marks)
        if rt is None: continue
        rat,m,n=rt
        if best is None or rat<best[0]:
            best=(rat,m,n,marks)
print("Best Wichmann ratio:",best[0],"marks",best[1],"n",best[2])

# Local search: try to remove marks that keep completeness (reduces |B|, lowers ratio if n same)
def try_prune(marks):
    marks=list(marks)
    improved=True
    while improved:
        improved=False
        for idx in range(1,len(marks)-1):  # keep endpoints (0 and max define n)
            cand=marks[:idx]+marks[idx+1:]
            ok,_=is_complete(cand)
            if ok:
                marks=cand
                improved=True
                break
    return marks

pruned=try_prune(best[3])
rt=ratio_of(pruned)
print("After prune:",rt[0],"marks",rt[1],"n",rt[2])

final=pruned if rt[0]<best[0] else best[3]
frt=ratio_of(final)
print("FINAL ratio:",frt[0],"marks",frt[1],"n",frt[2],"beats 2.6390?",frt[0]<2.6390)
print("BASIS=",final)

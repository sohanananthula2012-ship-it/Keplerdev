def singer(q):
    m=q*q+q+1; order=q*q*q-1
    for r0 in range(1,q):
        for r2 in range(q):
            for r1 in range(q):
                c=[1,0,0]; res=[]; prim=True
                for i in range(order):
                    if c[2]==0: res.append(i%m)
                    c=[(c[2]*r0)%q,(c[0]+c[2]*r1)%q,(c[1]+c[2]*r2)%q]
                    if i<order-1 and c==[1,0,0]: prim=False; break
                if not prim: continue
                res=sorted(set(res))
                if len(res)!=q+1: continue
                d=set(); ok=True
                for a in res:
                    for b in res:
                        if a!=b:
                            v=(a-b)%m
                            if v in d: ok=False;break
                            d.add(v)
                    if not ok: break
                if ok and len(d)==m-1: return res,m
    return None,m
def covB(S):
    S=sorted(S); ss=set(S); mx=S[-1]
    diffs=set()
    n=len(S)
    for i in range(n):
        for j in range(i+1,n):
            diffs.add(S[j]-S[i])
    c=0
    while (c+1) in diffs: c+=1
    return c
for q in [31,41]:
    D,m=singer(q)
    best=0;bt=0
    for t in range(m):
        c=covB([(x+t)%m for x in D])
        if c>best: best=c;bt=t
    print(f"q={q} m={m} |D|={len(D)} BRUTE max cov over translations(u=1)={best} at t={bt}  Cbound={q*(q+1)//2}")

def arc_maxcov(S,m,C):
    # for each residue d in 1..C, unique ordered pair (a,b) a-b=d mod m; forbid arc b+1..b+d
    arcstart={}
    n=len(S)
    for i in range(n):
        for j in range(n):
            if i!=j:
                d=(S[i]-S[j])%m
                if 1<=d<=C: arcstart[d]=S[j]
    alive=[True]*m; count=m
    for d in range(1,C+1):
        if d not in arcstart: continue
        b=arcstart[d]
        for k in range(1,d+1):
            t=(b+k)%m
            if alive[t]: alive[t]=False; count-=1
        if count==0: return d-1
    return C
for q in [31,41]:
    D,m=singer(q)
    print(f"q={q} ARC u=1 maxcov={arc_maxcov(sorted(D),m,m-1)}")

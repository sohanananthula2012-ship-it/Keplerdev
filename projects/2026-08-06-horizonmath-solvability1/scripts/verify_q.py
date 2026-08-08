import sys
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
    S=sorted(set(S)); diffs=set()
    n=len(S)
    for i in range(n):
        for j in range(i+1,n): diffs.add(S[j]-S[i])
    c=0
    while (c+1) in diffs: c+=1
    return c
def actual_k(L):
    L=sorted(set(L)); diffs=set()
    n=len(L)
    for i in range(n):
        li=L[i]
        for j in range(i+1,n): diffs.add(L[j]-li)
    c=0
    while (c+1) in diffs: c+=1
    return c
q=int(sys.argv[1])
D,m=singer(q)
A=[0,1,4,6]
# find best (u,t) maximizing covB over all units and translations
best=(0,1,0)
for u in range(1,m):
    uD=[(u*x)%m for x in D]
    for t in range(m):
        S=sorted((x+t)%m for x in uD)
        c=covB(S)
        if c>best[0]: best=(c,u,t)
cov,u,t=best
B=sorted(set((u*x+t)%m for x in D))
L=sorted({a*m+b for a in A for b in B})
k=actual_k(L)
print(f"q={q} m={m} |B|={len(B)} best cov={cov} (u={u},t={t})")
print(f"predicted k=6m+cov={6*m+cov}, ACTUAL k={k}, |L|={len(L)}")
print(f"ACTUAL ratio |L|^2/k = {len(L)**2/k:.7f}  {'BEATS 2.639' if len(L)**2/k<2.639 else 'no'}")

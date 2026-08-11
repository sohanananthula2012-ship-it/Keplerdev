import numpy as np, json, time, random
def mono_aps(c,n):
    v=[]
    for d in range(1,(n-1)//6+1):
        for a in range(0, n-6*d):
            s=c[a]
            if c[a+d]==s and c[a+2*d]==s and c[a+3*d]==s and c[a+4*d]==s and c[a+5*d]==s and c[a+6*d]==s:
                v.append((a,d))
    return v
def solve_n(n,tbudget,seed):
    rng=random.Random(seed)
    c=[rng.randint(0,1) for _ in range(n)]
    t0=time.time()
    while time.time()-t0<tbudget:
        v=mono_aps(c,n)
        if not v: return c
        a,d=rng.choice(v)
        # flip the element in this AP that reduces total violations most (sample)
        idxs=[a+i*d for i in range(7)]
        besti=rng.choice(idxs); bestg=1e9
        for i in idxs:
            c[i]^=1
            g=len(mono_aps(c,n))
            c[i]^=1
            if g<bestg: bestg=g;besti=i
        c[besti]^=1
    return None
if __name__=="__main__":
    best=None;bestn=0
    t0=time.time()
    n=64
    while time.time()-t0<85:
        c=solve_n(n, 6.0, int(t0)+n)
        if c is not None:
            bestn=n;best=c[:]
            print("valid n",n,flush=True)
            n=int(n*1.3)+1
        else:
            print("fail n",n,flush=True)
            n=n+ max(1,(n-bestn)//2) if n>bestn else n+1
            if n<=bestn: n=bestn+1
            if n>bestn+2 and bestn>0: break
    if best:
        json.dump({"coloring":best},open("/tmp/work/vdw_sol.json","w"))
        print("BEST n",bestn)

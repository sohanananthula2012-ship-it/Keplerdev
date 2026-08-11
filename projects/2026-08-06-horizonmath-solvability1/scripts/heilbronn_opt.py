import numpy as np, json, time
from scipy.optimize import minimize, linprog
from itertools import combinations

N=12
tris=list(combinations(range(N),3))
def areas(p):
    P=p.reshape(N,2)
    a=[]
    for i,j,k in tris:
        a.append(0.5*abs((P[j,0]-P[i,0])*(P[k,1]-P[i,1])-(P[k,0]-P[i,0])*(P[j,1]-P[i,1])))
    return np.array(a)

def neg_min(p):  # for local polishing via softmin
    A=areas(p); 
    return -A.min()

def maximize_from(p0, iters=300):
    # coordinate ascent: move worst points to increase min area (simple hill climb)
    p=p0.copy(); best=areas(p).min()
    rng=np.random.default_rng(int(p0[0]*1e6)%2**31)
    step=0.05
    for it in range(iters):
        i=rng.integers(0,N*2)
        old=p[i]
        p[i]=np.clip(old+rng.normal(0,step),0,1)
        m=areas(p).min()
        if m>=best: best=m
        else: p[i]=old
        if it%60==59: step*=0.8
    return p, best

if __name__=="__main__":
    t0=time.time()
    best=None; bestv=-1
    rng=np.random.default_rng(0)
    while time.time()-t0<200:
        p0=rng.random(N*2)
        p,v=maximize_from(p0, 400)
        if v>bestv:
            bestv=v; best=p.copy()
            print("min_area",round(v,6),"t",round(time.time()-t0,1),flush=True)
    P=best.reshape(N,2)
    # ensure strictly inside [0,1]
    P=np.clip(P,0,1)
    json.dump({"points":P.tolist()},open("/tmp/work/heilbronn_sol.json","w"))
    print("BEST min_area", areas(best).min())

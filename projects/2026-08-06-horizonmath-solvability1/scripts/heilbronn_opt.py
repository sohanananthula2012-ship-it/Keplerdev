import numpy as np, json, time
from itertools import combinations
N=12
tris=list(combinations(range(N),3))
I=np.array([t[0] for t in tris]);J=np.array([t[1] for t in tris]);K=np.array([t[2] for t in tris])
def minarea(P):
    return (0.5*np.abs((P[J,0]-P[I,0])*(P[K,1]-P[I,1])-(P[K,0]-P[I,0])*(P[J,1]-P[I,1]))).min()
def climb(P,rng,iters):
    best=minarea(P);step=0.05
    for it in range(iters):
        i=rng.integers(0,N);ax=rng.integers(0,2);old=P[i,ax]
        P[i,ax]=min(1.0,max(0.0,old+rng.normal(0,step)))
        m=minarea(P)
        if m>=best:best=m
        else:P[i,ax]=old
        if it%80==79:step*=0.85
    return best
t0=time.time();best=None;bestv=-1;rng=np.random.default_rng(1)
while time.time()-t0<85:
    P=rng.random((N,2));v=climb(P,rng,600)
    if v>bestv:bestv=v;best=P.copy();print("min_area",round(v,6),flush=True)
best=np.clip(best,0.0,1.0)
json.dump({"points":best.tolist()},open("/tmp/work/heilbronn_sol.json","w"))
print("BEST",minarea(best))

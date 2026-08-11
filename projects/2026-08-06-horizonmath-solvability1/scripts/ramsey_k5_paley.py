import numpy as np, json, itertools, time
def is_prime(n):
    if n<2:return False
    for p in range(2,int(n**.5)+1):
        if n%p==0:return False
    return True
def paley_adj(q):
    qr=set((x*x)%q for x in range(1,q))
    A=np.zeros((q,q),dtype=int)
    for i in range(q):
        for j in range(q):
            if i!=j and (i-j)%q in qr: A[i,j]=1
    return A
def has_kk(A,k):
    n=len(A)
    # search for clique of size k via recursive expansion
    adj=[set(np.where(A[i])[0]) for i in range(n)]
    order=sorted(range(n),key=lambda i:-len(adj[i]))
    found=[False]
    def ext(clique,cand):
        if found[0]:return
        if len(clique)==k: found[0]=True;return
        if len(clique)+len(cand)<k:return
        for v in list(cand):
            if found[0]:return
            ext(clique+[v], cand & adj[v] & set(x for x in cand if x>v))
    # simpler: standard
    def bk(R,P):
        if found[0]:return
        if len(R)==k: found[0]=True;return
        if len(R)+len(P)<k:return
        for v in list(P):
            bk(R+[v], P & adj[v])
            P=P-{v}
            if found[0]:return
    bk([], set(range(n)))
    return found[0]

best=None
for q in [61,53,49,41,37,29,25,17,13]:
    if not is_prime(q) or q%4!=1: continue
    A=paley_adj(q)
    # self-complementary: check no K5 in A (color0) and complement (color1)
    comp=1-A-np.eye(q,dtype=int)
    if not has_kk(A,5) and not has_kk(comp,5):
        best=(q,A)
        print("q",q,"no mono K5 -> R(5,5)>",q,flush=True)
        break
    else:
        print("q",q,"has mono K5",flush=True)
if best:
    q,A=best
    col=A.tolist()
    json.dump({"n":q,"coloring":col},open("/tmp/work/ramsey_k5_sol.json","w"))
    print("BEST n",q)

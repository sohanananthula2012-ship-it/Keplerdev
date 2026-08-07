import numpy as np, random, time, sys, json
A=[0,1,4,6]
B=[0,1,70,83,255,297,384,391,550,555,647,656,710,996,1020,1232,1257,1272,1452,1456,1536,1614,1745,1765,1948,2047,2150,2188,2214,2395,2407,2585,2612,2628,2739,2758,2858,2902,2974,3006,3027,3245,3392,3477,3526,3615,3675,3727,3849,3906,3935,4043,4049,4253,4410,4445,4578,4580,4821,4855,4911,4934,4973,5032,5099,5149,5160,5411,5452,5518,5526,5658,5833,5855,5926,5943,5957,5994,6139,6185,6281,6592,6622,6669,6687,6697,6742,6745,6778,6967]
m=89**2+89+1
L=sorted({a*m+b for a in A for b in B})
M=len(L)
DCAP=80000
SCAN=60000
def build_cnt(pts):
    cnt=np.zeros(DCAP+2,dtype=np.int64)
    a=np.array(sorted(pts),dtype=np.int64)
    for i in range(len(a)):
        d=a[i+1:]-a[i]; d=d[d<=DCAP]
        np.add.at(cnt,d,1)
    return cnt
def first_gap(cnt):
    z=np.flatnonzero(cnt[1:SCAN]==0)
    return int(z[0])+1 if len(z) else SCAN
def brute_cov_n(pts):
    pts=sorted(set(pts)); cov=set()
    for i in range(len(pts)):
        ai=pts[i]
        for j in range(i+1,len(pts)): cov.add(pts[j]-ai)
    v=1
    while v in cov: v+=1
    return v-1

TLIMIT=float(sys.argv[1]) if len(sys.argv)>1 else 600.0
seed=int(sys.argv[2]) if len(sys.argv)>2 else 12345
random.seed(seed)
pts=list(L); pts_set=set(pts)
cnt=build_cnt(pts); fg=first_gap(cnt); n=fg-1
arr=np.array(pts,dtype=np.int64)
best_n=n; best_pts=list(pts)
print("seed n=",n,"ratio=",M*M/n,flush=True)
t0=time.time(); it=0; T=2.5
while time.time()-t0<TLIMIT:
    it+=1
    if it%300000==0: T=max(0.05,T*0.95)
    i=random.randrange(M); old=int(arr[i])
    r=random.random()
    if r<0.55:
        g=fg; q=int(arr[random.randrange(M)]); cand=q+g if random.random()<0.5 else q-g
    elif r<0.85:
        cand=old+random.randint(-40,40)
    else:
        cand=random.randint(0,DCAP)
    if cand<0 or cand>DCAP or cand in pts_set or cand==old: continue
    others=np.delete(arr,i)
    dold=np.abs(old-others); dold=dold[(dold>0)&(dold<=DCAP)]
    dnew=np.abs(cand-others); dnew=dnew[(dnew>0)&(dnew<=DCAP)]
    np.add.at(cnt,dold,-1); np.add.at(cnt,dnew,1)
    nn=first_gap(cnt)-1
    if nn>=n or random.random()<np.exp((nn-n)/T):
        pts_set.discard(old); pts_set.add(cand); arr[i]=cand; n=nn; fg=n+1
        if n>best_n:
            vn=brute_cov_n(arr.tolist())
            if vn>best_n:
                best_n=vn; best_pts=arr.tolist()
                print("NEW BEST n=",best_n,"ratio=",M*M/best_n,"it=",it,"t=",round(time.time()-t0,1),flush=True)
    else:
        np.add.at(cnt,dnew,-1); np.add.at(cnt,dold,1)
vn=brute_cov_n(best_pts)
print("done it=",it,"best_n=",best_n,"verified_n=",vn,"ratio=",M*M/vn,flush=True)
json.dump({"n":vn,"basis":sorted(set(best_pts)),"ratio":M*M/vn},open("/tmp/work/anneal_best.json","w"))

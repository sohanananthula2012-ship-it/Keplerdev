# Explore AlphaEvolve difference-basis construction for diff_basis_upper.
A=[0,1,4,6]
B=[0,1,70,83,255,297,384,391,550,555,647,656,710,996,1020,1232,1257,1272,1452,1456,1536,1614,1745,1765,1948,2047,2150,2188,2214,2395,2407,2585,2612,2628,2739,2758,2858,2902,2974,3006,3027,3245,3392,3477,3526,3615,3675,3727,3849,3906,3935,4043,4049,4253,4410,4445,4578,4580,4821,4855,4911,4934,4973,5032,5099,5149,5160,5411,5452,5518,5526,5658,5833,5855,5926,5943,5957,5994,6139,6185,6281,6592,6622,6669,6687,6697,6742,6745,6778,6967]
m=89**2+89+1
L=sorted({a*m+b for a in A for b in B})
M=len(L)

def coverage(pts):
    pts=sorted(set(pts))
    mx=pts[-1]-pts[0]
    cov=bytearray(mx+2)
    n=len(pts)
    for i in range(n):
        ai=pts[i]
        for j in range(i+1,n):
            cov[pts[j]-ai]=1
    v=1
    while v<=mx and cov[v]: v+=1
    return v-1  # covers 1..(v-1)

n0=coverage(L)
print("base |L|=",M,"n=",n0,"ratio=",M*M/n0)

# (a) single-point removability: does removing any one point keep coverage >= threshold for a win?
# 359 pts win if n>=48837 (359^2/2.6390). Test each removal's coverage.
thr359=359*359/2.6390
best_rem=None
import time
t=time.time()
# Precompute: for each difference d in 1..n0, multiplicity, to find critical points fast
# multiplicity approach: a point p is safe to remove iff no d in 1..n0 is realized ONLY by pairs including p.
# Compute count of pairs realizing each d, and if count==1 store the pair.
n=n0
cnt=[0]*(n+1)
uniq_pair=[(-1,-1)]*(n+1)
for i in range(M):
    ai=L[i]
    for j in range(i+1,M):
        d=L[j]-ai
        if d<=n:
            cnt[d]+=1
            if cnt[d]==1: uniq_pair[d]=(i,j)
# critical points: for d with cnt==1, both endpoints are critical
critical=set()
for d in range(1,n+1):
    if cnt[d]==1:
        i,j=uniq_pair[d]; critical.add(i); critical.add(j)
removable=[i for i in range(M) if i not in critical]
print("num points that are NOT single-critical (candidate removable):",len(removable))
# For candidates, verify by actual recomputation (cnt==1 covers only single-pair; but a point could still be
# uniquely needed via being in all pairs of a d that has cnt>=2). Verify candidates properly:
wins=[]
for idx in removable:
    pts=L[:idx]+L[idx+1:]
    c=coverage(pts)
    if c>=n0:  # coverage preserved fully
        wins.append((idx,c))
print("removable keeping full coverage:",wins[:10],"total",len(wins))
print("elapsed",time.time()-t)

# (b) gap structure above n0
pts=L
cov=set()
mx=pts[-1]-pts[0]
for i in range(M):
    ai=pts[i]
    for j in range(i+1,M):
        cov.add(pts[j]-ai)
missing_above=[d for d in range(n0+1, n0+400) if d not in cov]
print("first missing beyond n0 (should be n0+1):",n0+1 in cov, "; missing in [n0+1,n0+400]:",missing_above[:20],"count",len(missing_above))

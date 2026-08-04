#!/usr/bin/env python3
"""
Restricted-domain computational & geometric investigation of a^3+b^3+c^3=d^3
Domain: 1 <= a <= b <= c < d <= N (N=500).

Produces:
  - CSV data tables (data/*.csv)
  - PNG figures (fig/*.png)
  - results.json  (summary numbers used by the report builder)
  - symbolic + numeric verification log

Algorithm (enumeration): for each ordered pair (a,b) with a<=b, we form the
vector s = a^3 + b^3 + c^3 for all c in [b, N-1]. We test whether each s equals
some d^3 with d<=N by a vectorised binary search (np.searchsorted) into the
sorted array of cubes {1^3,...,N^3}. Because a,b>=1 we always have d>c, so the
constraint c<d is automatic. This is exact (integer arithmetic) and examines
every candidate triple exactly once.
"""
import os, sys, json, time, math, gc
from math import gcd
import numpy as np

try:
    import resource
    def peak_mem_mb():
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0  # KB->MB (linux)
except Exception:
    def peak_mem_mb():
        return float('nan')

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data"); FIG = os.path.join(HERE, "fig")
os.makedirs(DATA, exist_ok=True); os.makedirs(FIG, exist_ok=True)

N = 500

# ----------------------------------------------------------------------------
# 1. EXHAUSTIVE ENUMERATION
# ----------------------------------------------------------------------------
def enumerate_solutions(N):
    cubes = (np.arange(1, N + 1, dtype=np.int64)) ** 3  # sorted ascending, index i -> d=i+1
    sols = []
    triples_examined = 0
    for a in range(1, N + 1):
        a3 = a * a * a
        for b in range(a, N + 1):
            b3 = b * b * b
            # c ranges b .. N-1  (c < d <= N)
            if b > N - 1:
                continue
            cvals = np.arange(b, N, dtype=np.int64)
            triples_examined += cvals.size
            s = a3 + b3 + cvals ** 3
            idx = np.searchsorted(cubes, s)
            idx = np.clip(idx, 0, N - 1)
            hit = cubes[idx] == s
            if hit.any():
                dvals = (idx + 1)
                for c, d in zip(cvals[hit].tolist(), dvals[hit].tolist()):
                    sols.append((a, b, int(c), int(d)))
    sols.sort(key=lambda t: (t[3], t[0], t[1], t[2]))
    return sols, triples_examined

t0 = time.time()
sols, triples_examined = enumerate_solutions(N)
t_enum = time.time() - t0
print(f"[enum] found {len(sols)} solutions in {t_enum:.2f}s, triples examined = {triples_examined:,}")

def is_primitive(t):
    g = 0
    for x in t:
        g = gcd(g, x)
    return g == 1

def primitive_form(t):
    g = 0
    for x in t:
        g = gcd(g, x)
    return tuple(x // g for x in t)

prim_sols = [s for s in sols if is_primitive(s)]
print(f"[enum] primitive solutions: {len(prim_sols)}")

# ----------------------------------------------------------------------------
# 2. NEAR-MISS  delta(d) = min |a^3+b^3+c^3 - d^3|,  a<=b<=c<d
#    (equivalently min over the multiset {a,b,c} subset of [1,d-1])
# ----------------------------------------------------------------------------
def near_miss(N):
    delta = np.zeros(N + 1, dtype=np.int64)
    triple = {}
    checks = 0
    for d in range(1, N + 1):
        T = d * d * d
        best = None; best_tr = None
        for a in range(1, d):
            a3 = a * a * a
            bvals = np.arange(a, d, dtype=np.int64)
            if bvals.size == 0:
                continue
            rem = T - a3 - bvals ** 3
            c0 = np.round(np.cbrt(np.abs(rem).astype(np.float64))).astype(np.int64)
            for dc in (-1, 0, 1):
                c = np.clip(c0 + dc, 1, d - 1)
                resid = np.abs(a3 + bvals ** 3 + c ** 3 - T)
                checks += resid.size
                j = int(np.argmin(resid))
                r = int(resid[j])
                if best is None or r < best:
                    best = r
                    best_tr = (a, int(bvals[j]), int(c[j]))
        delta[d] = best if best is not None else -1
        if best_tr is not None:
            tr = tuple(sorted(best_tr))
            triple[d] = tr
    return delta, triple, checks

t0 = time.time()
delta, nm_triple, nm_checks = near_miss(N)
t_nm = time.time() - t0
print(f"[near-miss] done in {t_nm:.2f}s, evaluations = {nm_checks:,}")

# ----------------------------------------------------------------------------
# 3. PARAMETRIC CLASSIFICATION
# ----------------------------------------------------------------------------
# Family A: multiples of the base (3,4,5,6):  (3k,4k,5k,6k), k>=1
familyA = set()
k = 1
while 6 * k <= N:
    familyA.add((3 * k, 4 * k, 5 * k, 6 * k))
    k += 1

# Family B: Ramanujan two-parameter family (and all positive scalings), reduced
#   a=3m^2+5mn-5n^2, b=4m^2-4mn+6n^2, c=5m^2-5mn-3n^2, d=6m^2-4mn+4n^2
familyB_prim = set()      # primitive sorted (a,b,c,d)
familyB_all = set()       # all scalings within bound
M = 60
for m in range(-M, M + 1):
    for n in range(-M, M + 1):
        if m == 0 and n == 0:
            continue
        a = 3*m*m + 5*m*n - 5*n*n
        b = 4*m*m - 4*m*n + 6*n*n
        c = 5*m*m - 5*m*n - 3*n*n
        d = 6*m*m - 4*m*n + 4*n*n
        vals = [a, b, c, d]
        if any(v <= 0 for v in vals):
            continue
        abc = sorted([a, b, c]); dd = d
        if dd <= max(abc):
            continue
        # verify it truly satisfies the equation
        if abc[0]**3 + abc[1]**3 + abc[2]**3 != dd**3:
            continue
        tup = (abc[0], abc[1], abc[2], dd)
        pf = primitive_form(tup)
        familyB_prim.add(pf)
        # all scalings up to N
        j = 1
        while pf[3] * j <= N:
            familyB_all.add(tuple(x * j for x in pf))
            j += 1

# classify each enumerated solution
def classify(t):
    if t in familyA:
        return "A:(3,4,5,6)-multiple"
    if t in familyB_all:
        return "B:Ramanujan(m,n)"
    return "sporadic"

classes = {t: classify(t) for t in sols}
from collections import Counter
class_counts = Counter(classes.values())
print("[classify]", dict(class_counts))

# ----------------------------------------------------------------------------
# 4. SYMBOLIC + NUMERIC VERIFICATION
# ----------------------------------------------------------------------------
import sympy as sp
mm, nn = sp.symbols('m n', integer=True)
aB = 3*mm**2 + 5*mm*nn - 5*nn**2
bB = 4*mm**2 - 4*mm*nn + 6*nn**2
cB = 5*mm**2 - 5*mm*nn - 3*nn**2
dB = 6*mm**2 - 4*mm*nn + 4*nn**2
sym_res_ram = sp.expand(aB**3 + bB**3 + cB**3 - dB**3)
kk = sp.symbols('k', integer=True)
sym_res_345 = sp.expand((3*kk)**3 + (4*kk)**3 + (5*kk)**3 - (6*kk)**3)
print("[symbolic] Ramanujan residual =", sym_res_ram, "| (3,4,5,6)*k residual =", sym_res_345)

import random as _random
_random.seed(20260804)
NUMCHECK = 50000
num_fail = 0
for i in range(NUMCHECK):
    m_ = _random.randint(-10**6, 10**6); n_ = _random.randint(-10**6, 10**6)
    a = 3*m_*m_ + 5*m_*n_ - 5*n_*n_
    b = 4*m_*m_ - 4*m_*n_ + 6*n_*n_
    c = 5*m_*m_ - 5*m_*n_ - 3*n_*n_
    d = 6*m_*m_ - 4*m_*n_ + 4*n_*n_
    if a**3 + b**3 + c**3 != d**3:
        num_fail += 1
print(f"[numeric] Ramanujan identity checked on {NUMCHECK} random (m,n): failures = {num_fail}")

# verify EVERY enumerated solution really satisfies the equation
verify_all = all(a**3 + b**3 + c**3 == d**3 for (a, b, c, d) in sols)
print("[verify] every enumerated solution satisfies eqn:", verify_all)

# ----------------------------------------------------------------------------
# 5. RUNTIME SCALING  (fig 14)
# ----------------------------------------------------------------------------
scaling = []
for Ns in (100, 200, 300, 400, 500):
    tt = time.time()
    ss, tri = enumerate_solutions(Ns)
    el = time.time() - tt
    scaling.append((Ns, len(ss), tri, el))
    print(f"[scaling] N={Ns}: sols={len(ss)} triples={tri:,} time={el:.2f}s")

peak = peak_mem_mb()

# ----------------------------------------------------------------------------
# WRITE DATA TABLES (CSV)
# ----------------------------------------------------------------------------
import csv

# Table 1: all primitive solutions
with open(os.path.join(DATA, "table1_primitive_solutions.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["a", "b", "c", "d", "family"])
    for t in sorted(prim_sols, key=lambda t: (t[3], t[0], t[1], t[2])):
        w.writerow([*t, classes[t]])

# full list (primitive + non-primitive) too
with open(os.path.join(DATA, "table1b_all_solutions.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["a", "b", "c", "d", "primitive", "family"])
    for t in sols:
        w.writerow([*t, int(is_primitive(t)), classes[t]])

# Table 2: summary statistics per size bin (by d)
bins = [(1,100),(101,200),(201,300),(301,400),(401,500)]
with open(os.path.join(DATA, "table2_summary.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["d_bin","n_solutions","n_primitive","prop_primitive",
                "min_ratio_d_over_maxabc","max_ratio_d_over_maxabc","mean_ratio"])
    for lo,hi in bins:
        grp = [t for t in sols if lo <= t[3] <= hi]
        if grp:
            npr = sum(1 for t in grp if is_primitive(t))
            ratios = [t[3]/max(t[0],t[1],t[2]) for t in grp]
            w.writerow([f"{lo}-{hi}", len(grp), npr, round(npr/len(grp),4),
                        round(min(ratios),4), round(max(ratios),4), round(sum(ratios)/len(ratios),4)])
        else:
            w.writerow([f"{lo}-{hi}", 0,0,0,0,0,0])
# overall row
allr=[t[3]/max(t[0],t[1],t[2]) for t in sols]
with open(os.path.join(DATA, "table2_summary.csv"), "a", newline="") as f:
    w=csv.writer(f)
    w.writerow(["ALL", len(sols), len(prim_sols), round(len(prim_sols)/len(sols),4),
                round(min(allr),4), round(max(allr),4), round(sum(allr)/len(allr),4)])

# Table 3: near-miss for d=10,20,...,500
with open(os.path.join(DATA, "table3_nearmiss.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["d","a","b","c","residual_delta","is_exact_solution"])
    for d in range(10, N+1, 10):
        tr = nm_triple.get(d, (None,None,None))
        w.writerow([d, *tr, int(delta[d]), int(delta[d]==0)])

# Table 4: parametric family membership
with open(os.path.join(DATA, "table4_families.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["family","count","n_primitive","examples"])
    for fam in ["A:(3,4,5,6)-multiple","B:Ramanujan(m,n)","sporadic"]:
        grp=[t for t in sols if classes[t]==fam]
        npr=sum(1 for t in grp if is_primitive(t))
        ex="; ".join(str(t) for t in sorted(grp, key=lambda x:x[3])[:5])
        w.writerow([fam, len(grp), npr, ex])

# Table 5: runtime & pair-count audit
with open(os.path.join(DATA, "table5_audit.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["stage","N","triples_or_evals_examined","wall_time_s","peak_mem_MB"])
    w.writerow(["enumeration", N, triples_examined, round(t_enum,3), round(peak,1)])
    w.writerow(["near_miss", N, nm_checks, round(t_nm,3), round(peak,1)])
    for (Ns,ns,tri,el) in scaling:
        w.writerow([f"enum_scale", Ns, tri, round(el,3), ""])

# results.json
results = {
    "N": N,
    "n_solutions": len(sols),
    "n_primitive": len(prim_sols),
    "triples_examined": int(triples_examined),
    "nearmiss_evals": int(nm_checks),
    "t_enum": t_enum, "t_nearmiss": t_nm, "peak_mem_MB": peak,
    "class_counts": dict(class_counts),
    "familyB_prim_count": len(familyB_prim),
    "sym_res_ramanujan": str(sym_res_ram),
    "sym_res_345": str(sym_res_345),
    "numeric_checks": NUMCHECK, "numeric_failures": num_fail,
    "verify_all_solutions": bool(verify_all),
    "scaling": scaling,
    "control_345_multiples": sorted(list(familyA)),
    "smallest_10_primitive": sorted(prim_sols, key=lambda t:t[3])[:10],
}
with open(os.path.join(HERE, "results.json"), "w") as f:
    json.dump(results, f, indent=2)

print("[data] all CSV tables + results.json written")

# ----------------------------------------------------------------------------
# FIGURES
# ----------------------------------------------------------------------------
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa
from matplotlib import cm

plt.rcParams.update({"figure.dpi":130,"font.size":10,"axes.grid":True,"grid.alpha":0.3})

A = np.array([t[0] for t in sols]); B=np.array([t[1] for t in sols])
C = np.array([t[2] for t in sols]); D=np.array([t[3] for t in sols])
PRIM = np.array([is_primitive(t) for t in sols])

def save(fig, name):
    p=os.path.join(FIG,name); fig.savefig(p, bbox_inches="tight"); plt.close(fig)
    print("  fig:", name)

# Fig 1: 3D scatter (a,b,c) coloured by d
fig=plt.figure(figsize=(7,6)); ax=fig.add_subplot(111,projection='3d')
p=ax.scatter(A,B,C,c=D,cmap='viridis',s=14)
ax.set_xlabel('a');ax.set_ylabel('b');ax.set_zlabel('c'); ax.set_title('Fig 1. Solutions (a,b,c) coloured by d')
fig.colorbar(p,label='d',shrink=0.6); save(fig,"fig01_scatter_abc.png")

# Fig 2a/2b: (a,b,d) and (b,c,d)
for name,(X,Y,Z,lx,ly,lz,ttl) in {
    "fig02a_scatter_abd.png":(A,B,D,'a','b','d','Fig 2a. Solutions (a,b,d) coloured by c'),
    "fig02b_scatter_bcd.png":(B,C,D,'b','c','d','Fig 2b. Solutions (b,c,d) coloured by a'),
}.items():
    col = C if 'abd' in name else A
    fig=plt.figure(figsize=(7,6)); ax=fig.add_subplot(111,projection='3d')
    p=ax.scatter(X,Y,Z,c=col,cmap='plasma',s=14)
    ax.set_xlabel(lx);ax.set_ylabel(ly);ax.set_zlabel(lz);ax.set_title(ttl)
    fig.colorbar(p,shrink=0.6); save(fig,name)

# Fig 3: pairwise projection matrix (6 panels)
pairs=[("a","b",A,B),("a","c",A,C),("a","d",A,D),("b","c",B,C),("b","d",B,D),("c","d",C,D)]
fig,axs=plt.subplots(2,3,figsize=(13,8))
for ax,(lx,ly,X,Y) in zip(axs.flat,pairs):
    ax.scatter(X[~PRIM],Y[~PRIM],s=10,c='lightgray',label='non-prim')
    ax.scatter(X[PRIM],Y[PRIM],s=12,c='crimson',label='primitive')
    ax.set_xlabel(lx);ax.set_ylabel(ly)
axs.flat[0].legend(fontsize=8)
fig.suptitle('Fig 3. Pairwise 2-D projections of the solution set'); fig.tight_layout()
save(fig,"fig03_pair_matrix.png")

# Fig 4: density heatmaps in normalised planes
ad=A/D; bd=B/D; cd=C/D
fig,axs=plt.subplots(1,3,figsize=(15,4.5))
for ax,(X,Y,lx,ly) in zip(axs,[(ad,bd,'a/d','b/d'),(ad,cd,'a/d','c/d'),(bd,cd,'b/d','c/d')]):
    h=ax.hist2d(X,Y,bins=40,cmap='inferno')
    fig.colorbar(h[3],ax=ax,label='count'); ax.set_xlabel(lx);ax.set_ylabel(ly)
fig.suptitle('Fig 4. Density heatmaps in normalised (·/d) planes'); fig.tight_layout()
save(fig,"fig04_density_heatmaps.png")

# Fig 5: histogram of d (linear + log)
fig,axs=plt.subplots(1,2,figsize=(12,4.5))
axs[0].hist(D,bins=25,color='steelblue',edgecolor='k'); axs[0].set_title('Fig 5a. Histogram of d (linear)'); axs[0].set_xlabel('d');axs[0].set_ylabel('count')
axs[1].hist(D,bins=25,color='steelblue',edgecolor='k'); axs[1].set_yscale('log'); axs[1].set_title('Fig 5b. Histogram of d (log y)'); axs[1].set_xlabel('d')
fig.tight_layout(); save(fig,"fig05_hist_d.png")

# Fig 6: histogram of ratio d/cuberoot(a^3+b^3+c^3) (==1)
ratio = D/np.cbrt(A**3.0+B**3.0+C**3.0)
fig,ax=plt.subplots(figsize=(7,4.5))
ax.hist(ratio,bins=50,color='seagreen',edgecolor='k')
ax.axvline(1.0,color='red',ls='--',label='exact = 1')
ax.set_title('Fig 6. d / (a^3+b^3+c^3)^(1/3)  (identically 1 for solutions)')
ax.set_xlabel('ratio'); ax.legend()
ax.text(0.02,0.9,f"min={ratio.min():.12f}\nmax={ratio.max():.12f}",transform=ax.transAxes,fontsize=8,va='top')
save(fig,"fig06_ratio_hist.png")

# Fig 7: near-miss delta(d) vs d (log scale) with zero line
dd_axis=np.arange(1,N+1); dvals=delta[1:N+1]
fig,ax=plt.subplots(figsize=(11,4.8))
pos = dvals>0
ax.scatter(dd_axis[pos],dvals[pos],s=10,c='navy',label='delta(d)>0 (near miss)')
zero = dvals==0
ax.scatter(dd_axis[zero],np.full(zero.sum(),0.5),s=40,marker='v',c='red',label='delta(d)=0 (exact solution exists)')
ax.set_yscale('log'); ax.set_xlabel('d'); ax.set_ylabel('delta(d)  (log)')
ax.set_title('Fig 7. Near-miss residual delta(d)=min|a^3+b^3+c^3-d^3| vs d'); ax.legend(fontsize=8)
save(fig,"fig07_nearmiss.png")

# Fig 8: cumulative count of solutions vs d
order=np.argsort(D); ds=D[order]
xs=np.arange(1,N+1); cum=np.array([(D<=x).sum() for x in xs])
cumP=np.array([((D<=x)&PRIM).sum() for x in xs])
fig,ax=plt.subplots(figsize=(9,4.8))
ax.plot(xs,cum,label='all solutions',lw=2)
ax.plot(xs,cumP,label='primitive',lw=2)
ax.set_xlabel('d'); ax.set_ylabel('cumulative # solutions'); ax.set_title('Fig 8. Cumulative solution count vs d'); ax.legend()
save(fig,"fig08_cumulative.png")

# Fig 9: box + violin of a/d,b/d,c/d
fig,axs=plt.subplots(1,2,figsize=(12,4.8))
axs[0].boxplot([ad,bd,cd],tick_labels=['a/d','b/d','c/d']); axs[0].set_title('Fig 9a. Box plot of normalised coords')
parts=axs[1].violinplot([ad,bd,cd],showmeans=True); axs[1].set_xticks([1,2,3]); axs[1].set_xticklabels(['a/d','b/d','c/d']); axs[1].set_title('Fig 9b. Violin plot')
fig.tight_layout(); save(fig,"fig09_box_violin.png")

# Fig 10: parallel coordinates of (a/d,b/d,c/d)
fig,ax=plt.subplots(figsize=(9,5))
xcoord=[0,1,2]
for i in range(len(sols)):
    ax.plot(xcoord,[ad[i],bd[i],cd[i]],color=cm.viridis(D[i]/N),alpha=0.35,lw=0.8)
ax.set_xticks(xcoord); ax.set_xticklabels(['a/d','b/d','c/d']); ax.set_ylabel('normalised value')
ax.set_title('Fig 10. Parallel-coordinates of normalised tuples (colour = d)')
sm=cm.ScalarMappable(cmap='viridis',norm=plt.Normalize(0,N)); sm.set_array([]); fig.colorbar(sm,ax=ax,label='d')
save(fig,"fig10_parallel.png")

# Fig 11: convex hull of projected (a/d,b/d) cloud
from scipy.spatial import ConvexHull
pts=np.column_stack([ad,bd])
fig,ax=plt.subplots(figsize=(7,6))
ax.scatter(ad,bd,s=14,c=cd,cmap='cool')
try:
    hull=ConvexHull(pts)
    for simplex in hull.simplices:
        ax.plot(pts[simplex,0],pts[simplex,1],'k-',lw=1)
    ax.set_title(f'Fig 11. Solution cloud (a/d,b/d) with convex hull (area={hull.volume:.4f})')
except Exception as e:
    ax.set_title('Fig 11. Solution cloud (a/d,b/d)')
ax.set_xlabel('a/d'); ax.set_ylabel('b/d'); fig.colorbar(ax.collections[0],label='c/d')
save(fig,"fig11_convexhull.png")

# Fig 12: parametric-curve overlay (Ramanujan family, n=1 varying m) on solution set
mline=np.linspace(0.5,20,400); n_=1.0
aP=3*mline**2+5*mline*n_-5*n_**2
bP=4*mline**2-4*mline*n_+6*n_**2
cP=5*mline**2-5*mline*n_-3*n_**2
dP=6*mline**2-4*mline*n_+4*n_**2
mask=(dP<=N)&(aP>0)&(cP>0)
fig,ax=plt.subplots(figsize=(8,6))
ax.scatter(A/D,C/D,s=12,c='lightgray',label='all solutions (a/d vs c/d)')
famB=[t for t in sols if classes[t]=="B:Ramanujan(m,n)"]
if famB:
    fb=np.array(famB); ax.scatter(fb[:,0]/fb[:,3],fb[:,2]/fb[:,3],s=30,c='crimson',label='Ramanujan-family solutions')
ax.plot(aP[mask]/dP[mask],cP[mask]/dP[mask],'b-',lw=2,label='Ramanujan curve (n=1)')
ax.set_xlabel('a/d'); ax.set_ylabel('c/d'); ax.set_title('Fig 12. Parametric Ramanujan curve overlaid on solution set'); ax.legend(fontsize=8)
save(fig,"fig12_parametric_overlay.png")

# Fig 13: control panel - multiples of (3,4,5,6) recovered
mult=[t for t in sols if classes[t]=="A:(3,4,5,6)-multiple"]
mk=np.array([t[3]//6 for t in mult]); md=np.array([t[3] for t in mult])
fig,ax=plt.subplots(figsize=(9,4.8))
ax.scatter(md,mk,s=30,c='darkorange',edgecolor='k',zorder=3,label='(3k,4k,5k,6k) recovered')
ax.plot(md,mk,'--',c='gray',alpha=0.6)
ax.set_xlabel('d = 6k'); ax.set_ylabel('k'); ax.set_title(f'Fig 13. Control: all {len(mult)} multiples of (3,4,5,6) with d<=500 recovered'); ax.legend()
save(fig,"fig13_control_345.png")

# Fig 14: runtime scaling
sc=np.array(scaling,dtype=float)
fig,ax=plt.subplots(figsize=(8,4.8))
ax.plot(sc[:,0],sc[:,3],'o-',lw=2,label='wall time (s)')
ax2=ax.twinx(); ax2.plot(sc[:,0],sc[:,2],'s--',c='green',label='triples examined')
ax.set_xlabel('N'); ax.set_ylabel('time (s)'); ax2.set_ylabel('triples examined')
ax.set_title('Fig 14. Runtime & search-space scaling vs N')
lines,labels=ax.get_legend_handles_labels(); l2,lab2=ax2.get_legend_handles_labels()
ax.legend(lines+l2,labels+lab2,fontsize=8,loc='upper left')
save(fig,"fig14_runtime_scaling.png")

# Fig 15: residual landscape heatmaps for two fixed d (near-miss landscape)
def residual_landscape(d):
    T=d**3
    grid=np.full((d,d),np.nan)
    for a in range(1,d):
        for b in range(a,d):
            rem=T-a**3-b**3
            if rem<=0: continue
            c=round(rem**(1/3))
            c=min(max(c,b),d-1)
            grid[a,b]=abs(a**3+b**3+c**3-T)
    return grid
fig,axs=plt.subplots(1,2,figsize=(13,5.2))
for ax,dsel in zip(axs,[100,500]):
    g=residual_landscape(dsel)
    with np.errstate(divide='ignore'):
        im=ax.imshow(np.log10(g+1),origin='lower',cmap='magma',aspect='auto')
    ax.set_title(f'Fig 15. log10(min residual+1), best c per (a,b), d={dsel}')
    ax.set_xlabel('b'); ax.set_ylabel('a'); fig.colorbar(im,ax=ax,label='log10(resid+1)')
fig.tight_layout(); save(fig,"fig15_residual_landscape.png")

print("ALL FIGURES DONE")

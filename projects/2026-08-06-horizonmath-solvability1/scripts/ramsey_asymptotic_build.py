import math, json, numpy as np
import ramsey_opt as R

coeffs=[float(x) for x in np.load("/tmp/work/ramsey_best.npy")]
bp=np.unique(np.concatenate([np.geomspace(1.05e-3,0.05,70),np.linspace(0.05,1.0,300)]))
bp=bp[(bp>1e-3)&(bp<1.0)]
edges=np.concatenate([[1e-3],bp,[1.0]])
Mgrid=np.linspace(0.001,0.75,500)
EPS_B=1.5e-3
Mvals=[];Yvals=[];worst=1e9
for j in range(len(edges)-1):
    lo,hi=float(edges[j]),float(edges[j+1]); samples=np.linspace(lo,hi,7)
    bestM=None;bestY=None;bestslack=-1e18
    for M in Mgrid:
        om=1-M; breq=-1e18; okall=True
        for s in samples:
            Fv=R.F(s,coeffs);Fpv=R.Fp(s,coeffs)
            if Fv<=0 or Fpv<=0: okall=False;break
            val=1-math.exp(-Fpv)
            if val<=0: okall=False;break
            logX=math.log(om)+math.log(val)/om; a=-logX
            if a<=1e-9: okall=False;break
            breq=max(breq,float(R.B_interp(a)))
        if not okall: continue
        b=breq+EPS_B; Y=math.exp(-b)
        if not(0<Y<1): continue
        ws=1e18
        for s in samples:
            Fv=R.F(s,coeffs);Fpv=R.Fp(s,coeffs);val=1-math.exp(-Fpv)
            logX=math.log(om)+math.log(val)/om
            ws=min(ws,Fv+0.5*(logX+s*math.log(M)+s*(-b)))
        if ws>bestslack: bestslack=ws;bestM=M;bestY=Y
    if bestM is None: raise RuntimeError(f"seg {j} infeasible")
    Mvals.append(bestM);Yvals.append(bestY);worst=min(worst,bestslack)
print("segments",len(Mvals),"worst main slack=",worst)
sol={"polynomial_coeffs":coeffs,
 "M":{"breakpoints":[float(x) for x in bp],"values":[float(x) for x in Mvals]},
 "Y":{"breakpoints":[float(x) for x in bp],"values":[float(x) for x in Yvals]},
 "notes":"GNNW split-validator certificate; c=4*exp(p(1)/e)."}
assert len(sol["M"]["values"])==len(bp)+1
json.dump(sol,open("/tmp/work/ramsey_sol.json","w"))
with open("/tmp/work/ramsey_asymptotic.py","w") as f:
    f.write("_S="+json.dumps(sol)+"\ndef proposed_solution():\n    return _S\n")
print("c=",4*math.exp(R.horner(1.0,coeffs)/math.e))

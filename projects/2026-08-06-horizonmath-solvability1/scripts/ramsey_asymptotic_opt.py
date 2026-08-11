import math, numpy as np
from scipy.optimize import minimize

BETA=0.033
ALPHA_SMALL=(0.17-BETA)/math.e

def U(mu):
    g=(-0.25*mu+BETA*mu**2+0.08*mu**3)*math.exp(-mu)
    return g+(1+mu)*math.log(1+mu)-mu*math.log(mu)
def Up(mu):
    s=-0.25*mu+BETA*mu**2+0.08*mu**3
    sp=-0.25+2*BETA*mu+0.24*mu**2
    return math.log((1+mu)/mu)+math.exp(-mu)*(sp-s)
U1=U(1.0); UP1=Up(1.0); A1=U1-UP1
def A_of_mu(mu): return U(mu)-mu*Up(mu)
def bracket(f,a,incr):
    lo,hi=1e-60,1.0
    for _ in range(120):
        mid=0.5*(lo+hi)
        cond = (f(mid)<a) if incr else (f(mid)>a)
        if cond: lo=mid
        else: hi=mid
    return lo,hi
def B_of_a(a):
    # bu branch
    if a>=U1: bu=0.0
    elif a>A1: bu=U1-a
    else:
        lo,hi=bracket(A_of_mu,a,True); bu=Up(lo)  # Up decreasing -> Up(lo) is upper bound
    # bs branch
    if a<UP1: bs=U1-a
    else:
        lo,hi=bracket(Up,a,False)
        # U(mu)-mu*a, upper bound over [lo,hi]; take max of endpoints
        bs=max(U(lo)-lo*a, U(hi)-hi*a)
    return max(0.0,min(bu,bs))

def horner(lam,c):
    acc=0.0
    for a in reversed(c): acc=(acc+a)*lam
    return acc
def pprime(lam,c):
    return sum((i+1)*c[i]*lam**i for i in range(len(c)))
def F(lam,c):
    return (1+lam)*math.log(1+lam)-lam*math.log(lam)+horner(lam,c)*math.exp(-lam)
def Fp(lam,c):
    p=horner(lam,c); dp=pprime(lam,c)
    return math.log((1+lam)/lam)+(dp-p)*math.exp(-lam)

def per_lambda(lam,c,eps_b,Mgrid):
    Fv=F(lam,c); Fpv=Fp(lam,c)
    if Fv<=0 or Fpv<=0: return -9e9,None,None
    val=1-math.exp(-Fpv)
    if val<=0: return -9e9,None,None
    best=-9e18; bM=None;bY=None
    for M in Mgrid:
        om=1-M
        logX=math.log(om)+math.log(val)/om
        a=-logX
        if a<=1e-9: continue
        b=B_of_a(a)+eps_b
        Y=math.exp(-b)
        if not(0<Y<1): continue
        slack=Fv+0.5*(logX+lam*math.log(M)+lam*(-b))
        if slack>best: best=slack;bM=M;bY=Y
    return best,bM,bY

LAM=np.concatenate([np.geomspace(1e-3,0.05,60), np.linspace(0.05,1.0,140)])
LAM=np.unique(LAM)
Mgrid=np.linspace(0.002,0.7,90)

def eval_coeffs(c,eps_b=8e-4):
    slacks=[]
    for lam in LAM:
        s,_,_=per_lambda(float(lam),c,eps_b,Mgrid)
        slacks.append(s)
    return np.array(slacks)

def objective(c,target=6e-4):
    c=list(c)
    p1=horner(1.0,c)
    sl=eval_coeffs(c)
    viol=np.maximum(0.0,target-sl).sum()
    return p1+50.0*viol + (0 if sl.min()>-1e8 else 1e6)

if __name__=="__main__":
    import sys
    # start: modest negative correction
    x0=np.array([-0.05,-0.02,-0.01,-0.01,0.0,0.0])
    best=None
    for trial in range(6):
        rng=np.random.default_rng(trial)
        start=x0+rng.normal(0,0.03,size=len(x0)) if trial>0 else x0
        res=minimize(objective,start,method='Nelder-Mead',
                     options={'maxiter':2500,'xatol':1e-6,'fatol':1e-7})
        c=list(res.x); p1=horner(1.0,c); cval=4*math.exp(p1/math.e)
        sl=eval_coeffs(c)
        feas=sl.min()
        print(f"trial{trial} c={cval:.5f} p1={p1:.5f} minslack={feas:.2e} coeffs={[round(v,5) for v in c]}")
        if feas>4e-4 and (best is None or cval<best[0]):
            best=(cval,c)
    if best:
        print("BEST c=",best[0],"coeffs=",best[1])
        np.save("/tmp/work/ramsey_best.npy",np.array(best[1]))
    else:
        print("no feasible found")

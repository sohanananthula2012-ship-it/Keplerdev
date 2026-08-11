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
        cond=(f(mid)<a) if incr else (f(mid)>a)
        if cond: lo=mid
        else: hi=mid
    return lo,hi
def B_of_a(a):
    if a>=U1: bu=0.0
    elif a>A1: bu=U1-a
    else:
        lo,hi=bracket(A_of_mu,a,True); bu=Up(lo)
    if a<UP1: bs=U1-a
    else:
        lo,hi=bracket(Up,a,False); bs=max(U(lo)-lo*a,U(hi)-hi*a)
    return max(0.0,min(bu,bs))

_AT=np.geomspace(1e-7,8.0,6000)
_BT=np.array([B_of_a(float(a)) for a in _AT])
def B_interp(a): return np.interp(a,_AT,_BT)

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
    om=1-Mgrid
    logX=np.log(om)+math.log(val)/om
    a=-logX
    b=B_interp(a)+eps_b
    Y=np.exp(-b)
    ok=(a>1e-9)&(Y>0)&(Y<1)
    slack=np.where(ok,Fv+0.5*(logX+lam*np.log(Mgrid)+lam*(-b)),-9e18)
    j=int(np.argmax(slack))
    return float(slack[j]),float(Mgrid[j]),float(Y[j])

LAM=np.unique(np.concatenate([np.geomspace(1e-3,0.05,60),np.linspace(0.05,1.0,160)]))
Mgrid=np.linspace(0.001,0.75,300)

def eval_coeffs(c,eps_b=1.3e-3):
    return np.array([per_lambda(float(l),c,eps_b,Mgrid)[0] for l in LAM])

def objective(c,target=3.0e-3):
    c=list(c); p1=horner(1.0,c)
    sl=eval_coeffs(c)
    viol=np.maximum(0.0,target-sl).sum()
    return p1+60.0*viol

if __name__=="__main__":
    x0=np.array([-0.05,-0.02,-0.01,-0.01,0.0,0.0])
    best=None
    for trial in range(3):
        rng=np.random.default_rng(trial)
        start=x0+rng.normal(0,0.03,size=len(x0)) if trial>0 else x0
        res=minimize(objective,start,method='Nelder-Mead',
                     options={'maxiter':1500,'xatol':1e-6,'fatol':1e-7})
        c=list(res.x); p1=horner(1.0,c); cval=4*math.exp(p1/math.e)
        sl=eval_coeffs(c); feas=sl.min()
        print(f"trial{trial} c={cval:.5f} p1={p1:.5f} minslack={feas:.2e} coeffs={[round(float(v),6) for v in c]}",flush=True)
        if feas>1.5e-3 and (best is None or cval<best[0]):
            best=(cval,c)
    if best:
        print("BEST c=",best[0],"coeffs=",[float(v) for v in best[1]])
        np.save("/tmp/work/ramsey_best.npy",np.array(best[1]))
    else:
        print("no feasible")

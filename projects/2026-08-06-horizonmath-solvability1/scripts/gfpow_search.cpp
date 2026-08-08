// gfpow_search.cpp — planar Singer difference sets for PRIME-POWER q = p^e.
// GF(q) built via log/antilog over F_p[y]/(g), g primitive of degree e.
// GF(q^3) = GF(q)[x]/(x^3 = r2 x^2 + r1 x + r0), x a primitive element.
// Singer set D = { i mod m : x^i has zero x^2-coordinate }, m = q^2+q+1, |D| = q+1.
// Then units x translations arc-search for max self-coverage; combine A={0,1,4,6}:
// k = 6m + cov, |L| = 4(q+1), ratio = |L|^2/k. Beat baseline 2.639 if ratio<2.639.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;

int P,E,Q;                 // p, e, q=p^e
vector<int> EXP, LOGT;     // GF(q) log tables (size q)
inline int gadd(int a,int b){ // digitwise add mod p (GF(q) is F_p-vector space)
    int r=0,pw=1;
    for(int i=0;i<E;i++){int da=a%P,db=b%P;a/=P;b/=P;r+=((da+db)%P)*pw;pw*=P;}
    return r;
}
inline int gmul(int a,int b){ if(a==0||b==0)return 0; return EXP[(LOGT[a]+LOGT[b])%(Q-1)]; }

bool build_gf(){
    EXP.assign(Q,0); LOGT.assign(Q,-1);
    vector<int> gc(E,0);
    for(int code=0; code<Q; code++){
        int t=code; for(int i=0;i<E;i++){gc[i]=t%P;t/=P;}
        if(gc[0]==0) continue;
        vector<int> v(E,0); v[0]=1;
        vector<int> exp(Q,0); vector<int> logt(Q,-1);
        bool ok=true;
        for(int k=0;k<Q-1;k++){
            int id=0,pw=1; for(int i=0;i<E;i++){id+=v[i]*pw;pw*=P;}
            if(logt[id]!=-1){ok=false;break;}
            exp[k]=id; logt[id]=k;
            int hi=v[E-1];
            for(int i=E-1;i>0;i--) v[i]=v[i-1];
            v[0]=0;
            if(hi){ for(int i=0;i<E;i++) v[i]=(v[i]+hi*gc[i])%P; }
        }
        if(!ok) continue;
        int id=0,pw=1; for(int i=0;i<E;i++){id+=v[i]*pw;pw*=P;}
        if(id!=1) continue;
        exp[Q-1]=1; EXP=exp; LOGT=logt; return true;
    }
    return false;
}
vector<ll> singer_pp(){
    ll m=(ll)Q*Q+Q+1, order=(ll)Q*Q*Q-1;
    for(int r0=1;r0<Q;r0++)for(int r2=0;r2<Q;r2++)for(int r1=0;r1<Q;r1++){
        int c0=1,c1=0,c2=0; bool prim=true; vector<ll> res;
        for(ll i=0;i<order;i++){
            if(c2==0) res.push_back(i%m);
            int n0=gmul(c2,r0), n1=gadd(c0,gmul(c2,r1)), n2=gadd(c1,gmul(c2,r2));
            c0=n0;c1=n1;c2=n2;
            if(i<order-1 && c0==1&&c1==0&&c2==0){prim=false;break;}
        }
        if(!prim) continue;
        sort(res.begin(),res.end()); res.erase(unique(res.begin(),res.end()),res.end());
        if((ll)res.size()!=Q+1) continue;
        vector<char> seen(m,0); bool ok=true; ll cnt=0;
        for(size_t i=0;i<res.size()&&ok;i++)for(size_t j=0;j<res.size();j++) if(i!=j){
            ll d=((res[i]-res[j])%m+m)%m; if(d==0||seen[d]){ok=false;break;} seen[d]=1; cnt++;
        }
        if(ok && cnt==m-1) return res;
    }
    return {};
}
ll arc_maxcov(const vector<ll>&S,ll m,ll C,vector<ll>&arcstart,vector<char>&alive){
    int n=S.size();
    for(ll d=0;d<=C;d++) arcstart[d]=-1;
    for(int i=0;i<n;i++)for(int j=0;j<n;j++) if(i!=j){ ll d=((S[i]-S[j])%m+m)%m; if(d>=1&&d<=C) arcstart[d]=S[j]; }
    fill(alive.begin(),alive.end(),1); ll count=m;
    for(ll d=1;d<=C;d++){ if(arcstart[d]<0)continue; ll b=arcstart[d];
        for(ll k=1;k<=d;k++){ll t=(b+k)%m; if(alive[t]){alive[t]=0;count--;}} if(count==0)return d-1; }
    return C;
}
int main(int argc,char**argv){
    P=atoi(argv[1]); E=atoi(argv[2]); Q=(int)round(pow((double)P,E));
    double BASELINE=2.639;
    if(!build_gf()){ printf("p=%d e=%d q=%d: no primitive GF poly\n",P,E,Q); return 1; }
    vector<ll> D=singer_pp();
    if(D.empty()){ printf("p=%d e=%d q=%d: no perfect singer\n",P,E,Q); return 1; }
    ll m=(ll)Q*Q+Q+1;
    double reqd=16.0*(Q+1)*(Q+1)/BASELINE-6.0*m;
    ll C=(ll)ceil(reqd)+3; if(C>m-1)C=m-1; if(C<40)C=40;
    vector<ll> arcstart(C+1); vector<char> alive(m); vector<ll> uD(D.size());
    ll bcov=0,bu=1;
    for(ll u=1;u<m;u++){ if(std::__gcd(u,m)!=1)continue;
        // multiplier-orbit reduction: p is a multiplier (order 3e); skip non-minimal in orbit
        bool minimal=true; ll w=(u*P)%m;
        for(int j=1;j<3*E;j++){ if(w<u){minimal=false;break;} w=(w*P)%m; }
        if(!minimal) continue;
        for(size_t i=0;i<D.size();i++) uD[i]=(u*D[i])%m; sort(uD.begin(),uD.end());
        ll c=arc_maxcov(uD,m,C,arcstart,alive); if(c>bcov){bcov=c;bu=u;} }
    ll k=6*m+bcov; double ratio=16.0*(Q+1)*(Q+1)/(double)k;
    printf("q=%d(=%d^%d) m=%lld reqd=%.1f bestcov=%lld u=%lld k=%lld ratio=%.7f %s\n",
           Q,P,E,m,reqd,bcov,bu,k,ratio, ratio<BASELINE?"*** BEATS 2.639 ***":"");
    return 0;
}

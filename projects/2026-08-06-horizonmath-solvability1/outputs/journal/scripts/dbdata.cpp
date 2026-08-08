// dbdata.cpp — per-q data for the research journal.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
int P,E,Q;
vector<int> EXP,LOGT;
inline int gadd(int a,int b){int r=0,pw=1;for(int i=0;i<E;i++){int da=a%P,db=b%P;a/=P;b/=P;r+=((da+db)%P)*pw;pw*=P;}return r;}
inline int gmul(int a,int b){if(a==0||b==0)return 0;return EXP[(LOGT[a]+LOGT[b])%(Q-1)];}
bool build_gf(){
    EXP.assign(Q,0);LOGT.assign(Q,-1);
    if(E==1){for(int g=2;g<Q;g++){int x=1;vector<int> lg(Q,-1);bool ok=true;for(int k=0;k<Q-1;k++){if(lg[x]!=-1){ok=false;break;}lg[x]=k;EXP[k]=x;x=(x*g)%Q;}if(ok&&x==1){LOGT=lg;EXP[Q-1]=1;return true;}}return false;}
    vector<int> gc(E,0);
    for(int code=0;code<Q;code++){int t=code;for(int i=0;i<E;i++){gc[i]=t%P;t/=P;}if(gc[0]==0)continue;
        vector<int> v(E,0);v[0]=1;vector<int> ex(Q,0),lg(Q,-1);bool ok=true;
        for(int k=0;k<Q-1;k++){int id=0,pw=1;for(int i=0;i<E;i++){id+=v[i]*pw;pw*=P;}if(lg[id]!=-1){ok=false;break;}ex[k]=id;lg[id]=k;
            int hi=v[E-1];for(int i=E-1;i>0;i--)v[i]=v[i-1];v[0]=0;if(hi){for(int i=0;i<E;i++)v[i]=(v[i]+hi*gc[i])%P;}}
        if(!ok)continue;int id=0,pw=1;for(int i=0;i<E;i++){id+=v[i]*pw;pw*=P;}if(id!=1)continue;ex[Q-1]=1;EXP=ex;LOGT=lg;return true;}
    return false;
}
vector<ll> singer(){
    ll m=(ll)Q*Q+Q+1,order=(ll)Q*Q*Q-1;
    for(int r0=1;r0<Q;r0++)for(int r2=0;r2<Q;r2++)for(int r1=0;r1<Q;r1++){
        int c0=1,c1=0,c2=0;bool prim=true;vector<ll> res;
        for(ll i=0;i<order;i++){if(c2==0)res.push_back(i%m);int n0=gmul(c2,r0),n1=gadd(c0,gmul(c2,r1)),n2=gadd(c1,gmul(c2,r2));c0=n0;c1=n1;c2=n2;if(i<order-1&&c0==1&&c1==0&&c2==0){prim=false;break;}}
        if(!prim)continue;sort(res.begin(),res.end());res.erase(unique(res.begin(),res.end()),res.end());
        if((ll)res.size()!=Q+1)continue;vector<char> seen(m,0);bool ok=true;ll cnt=0;
        for(size_t i=0;i<res.size()&&ok;i++)for(size_t j=0;j<res.size();j++)if(i!=j){ll d=((res[i]-res[j])%m+m)%m;if(d==0||seen[d]){ok=false;break;}seen[d]=1;cnt++;}
        if(ok&&cnt==m-1)return res;}
    return {};
}
ll arc(const vector<ll>&S,ll m,ll C,vector<ll>&as,vector<char>&al){
    int n=S.size();for(ll d=0;d<=C;d++)as[d]=-1;
    for(int i=0;i<n;i++)for(int j=0;j<n;j++)if(i!=j){ll d=((S[i]-S[j])%m+m)%m;if(d>=1&&d<=C)as[d]=S[j];}
    fill(al.begin(),al.end(),1);ll cnt=m;
    for(ll d=1;d<=C;d++){if(as[d]<0)continue;ll b=as[d];for(ll k=1;k<=d;k++){ll t=(b+k)%m;if(al[t]){al[t]=0;cnt--;}}if(cnt==0)return d-1;}
    return C;
}
ll covdir(const vector<ll>&S,ll cap){int n=S.size();vector<char> sn(cap+2,0);for(int i=0;i<n;i++)for(int j=i+1;j<n;j++){ll d=S[j]-S[i];if(d<=cap)sn[d]=1;}ll c=0;while(c+1<=cap&&sn[c+1])c++;return c;}
int main(){
    int p,e;double BASE=2.639;
    while(scanf("%d %d",&p,&e)==2){
        P=p;E=e;Q=(int)llround(pow((double)P,E));
        if(!build_gf()){fprintf(stderr,"q=%d no gf\n",Q);continue;}
        vector<ll> D=singer();if(D.empty()){fprintf(stderr,"q=%d no singer\n",Q);continue;}
        ll m=(ll)Q*Q+Q+1;ll C=m-1;vector<ll> as(C+1);vector<char> al(m);vector<ll> uD(D.size());
        ll bcov=0,bu=1;
        for(ll u=1;u<m;u++){if(std::__gcd(u,m)!=1)continue;
            bool mn=true;ll w=(u*P)%m;for(int j=1;j<3*E;j++){if(w<u){mn=false;break;}w=(w*P)%m;}if(!mn)continue;
            for(size_t i=0;i<D.size();i++)uD[i]=(u*D[i])%m;sort(uD.begin(),uD.end());
            ll c=arc(uD,m,C,as,al);if(c>bcov){bcov=c;bu=u;}}
        for(size_t i=0;i<D.size();i++)uD[i]=(bu*D[i])%m;
        ll bt=0,tc=0;vector<ll> St(D.size());
        for(ll t=0;t<m;t++){for(size_t i=0;i<D.size();i++)St[i]=(uD[i]+t)%m;sort(St.begin(),St.end());ll c=covdir(St,min(bcov+5,m-1));if(c>tc){tc=c;bt=t;}}
        for(size_t i=0;i<D.size();i++)St[i]=(uD[i]+bt)%m;sort(St.begin(),St.end());
        ll k=6*m+bcov;double ratio=16.0*(Q+1)*(Q+1)/(double)k;
        double f=(double)bcov/((double)(Q+1)*(Q+1));double fm6q=f-6.0/Q;
        printf("{\"q\":%d,\"p\":%d,\"e\":%d,\"m\":%lld,\"cov\":%lld,\"u\":%lld,\"t\":%lld,\"k\":%lld,\"ratio\":%.10f,\"f\":%.10f,\"fm6q\":%.10f,\"beats\":%s,\"B\":[",
               Q,P,E,m,bcov,bu,bt,k,ratio,f,fm6q, ratio<BASE?"true":"false");
        for(size_t i=0;i<St.size();i++)printf("%s%lld",i?",":"",St[i]);
        printf("]}\n");fflush(stdout);
        fprintf(stderr,"done q=%d cov=%lld ratio=%.6f\n",Q,bcov,ratio);
    }
    return 0;
}

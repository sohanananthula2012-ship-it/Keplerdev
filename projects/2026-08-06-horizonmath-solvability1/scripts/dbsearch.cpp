// dbsearch.cpp — full difference-basis search.
// For prime q: Singer difference set D mod m=q^2+q+1 (|D|=q+1, perfect).
// For every unit u, form u*D (still perfect); compute max contiguous positive-diff
// coverage over ALL translations via arc method; track best.
// Combine with A={0,1,4,6} (A-A=[-6,6]): k=6m+cov, |L|=4(q+1), ratio=|L|^2/k.
// Report best ratio vs record 2.6390274695, with (q,u,t) to reconstruct basis.
#include <bits/stdc++.h>
using namespace std;
static bool is_prime(long long n){if(n<2)return false;for(long long i=2;i*i<=n;i++)if(n%i==0)return false;return true;}
vector<long long> singer(long long q){
    long long m=q*q+q+1, order=q*q*q-1;
    for(long long r0=1;r0<q;r0++)for(long long r2=0;r2<q;r2++)for(long long r1=0;r1<q;r1++){
        long long c0=1,c1=0,c2=0; bool prim=true; vector<long long> res;
        for(long long i=0;i<order;i++){
            if(c2==0) res.push_back(i%m);
            long long n0=(c2*r0)%q,n1=(c0+c2*r1)%q,n2=(c1+c2*r2)%q; c0=n0;c1=n1;c2=n2;
            if(i<order-1&&c0==1&&c1==0&&c2==0){prim=false;break;}
        }
        if(!prim) continue;
        sort(res.begin(),res.end()); res.erase(unique(res.begin(),res.end()),res.end());
        if((long long)res.size()==q+1) return res;
    }
    return {};
}
// returns {cov, t*} : max cov over translations and one achieving cut position
pair<long long,long long> maxcov_trans(const vector<long long>&S,long long m,long long C,vector<long long>&arcstart,vector<char>&alive){
    int n=S.size();
    fill(arcstart.begin(),arcstart.end(),-1);
    for(int i=0;i<n;i++)for(int j=0;j<n;j++) if(i!=j){
        long long d=((S[i]-S[j])%m+m)%m;
        if(d>=1 && d<=C) arcstart[d]=S[j];
    }
    fill(alive.begin(),alive.end(),1); long long count=m;
    for(long long d=1;d<=C;d++){
        if(arcstart[d]<0) continue;
        long long b=arcstart[d];
        long long lastpos=-1;
        for(long long k=1;k<=d;k++){ long long t=(b+k)%m; if(alive[t]){alive[t]=0;count--;lastpos=t;} }
        if(count==0) return {d-1,lastpos};
    }
    return {C,-1};
}
int main(int argc,char**argv){
    long long qlo=atoi(argv[1]), qhi=atoi(argv[2]);
    double RECORD=2.6390274695;
    double gbest=1e9; long long gq=0,gu=0,gt=0,gcov=0;
    for(long long q=qlo;q<=qhi;q++){
        if(!is_prime(q)) continue;
        long long m=q*q+q+1;
        vector<long long> D=singer(q);
        if(D.empty()){fprintf(stderr,"q=%lld no singer\n",q);continue;}
        double reqd=16.0*(q+1)*(q+1)/RECORD-6.0*m;
        long long C=(long long)max(3000.0,reqd+1500);
        vector<long long> arcstart(C+1); vector<char> alive(m);
        vector<long long> uD(D.size());
        long long bcov=0,bu=1,bt=0;
        for(long long u=1;u<m;u++){
            for(size_t i=0;i<D.size();i++) uD[i]=(u*D[i])%m;
            sort(uD.begin(),uD.end());
            auto pr=maxcov_trans(uD,m,C,arcstart,alive);
            if(pr.first>bcov){bcov=pr.first;bu=u;bt=pr.second;}
        }
        long long k=6*m+bcov;
        double ratio=16.0*(q+1)*(q+1)/(double)k;
        printf("q=%lld m=%lld |B|=%lld reqd=%.1f bestcov=%lld u=%lld t=%lld k=%lld ratio=%.7f %s\n",
               q,m,(long long)D.size(),reqd,bcov,bu,bt,k,ratio,ratio<RECORD?"*** BEATS ***":"");
        fflush(stdout);
        if(ratio<gbest){gbest=ratio;gq=q;gu=bu;gt=bt;gcov=bcov;}
    }
    printf("\nGLOBAL BEST: q=%lld u=%lld t=%lld cov=%lld ratio=%.7f (record %.7f) %s\n",
           gq,gu,gt,gcov,gbest,RECORD, gbest<RECORD?"BEATS":"no beat");
    return 0;
}

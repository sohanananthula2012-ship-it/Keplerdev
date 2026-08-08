// dbsearch2.cpp — difference-basis search over prime q, units, translations.
// Singer difference set D mod m=q^2+q+1 (VERIFIED perfect). For each UNIT u (gcd(u,m)=1),
// max contiguous positive-diff coverage over translations via arc method (C=m-1, early-exit).
// A={0,1,4,6} (A-A=[-6,6]): k=6m+cov, |L|=4(q+1), ratio=|L|^2/k. Beat baseline 2.639 if ratio<2.639.
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
        if((long long)res.size()!=q+1) continue;
        vector<char> seen(m,0); bool ok=true; long long cnt=0;
        for(size_t i=0;i<res.size()&&ok;i++)for(size_t j=0;j<res.size();j++) if(i!=j){
            long long d=((res[i]-res[j])%m+m)%m; if(d==0||seen[d]){ok=false;break;} seen[d]=1; cnt++;
        }
        if(ok && cnt==m-1) return res;
    }
    return {};
}
long long arc_maxcov(const vector<long long>&S,long long m,long long C,vector<long long>&arcstart,vector<char>&alive){
    int n=S.size();
    for(long long d=0;d<=C;d++) arcstart[d]=-1;
    for(int i=0;i<n;i++)for(int j=0;j<n;j++) if(i!=j){
        long long d=((S[i]-S[j])%m+m)%m; if(d>=1&&d<=C) arcstart[d]=S[j];
    }
    fill(alive.begin(),alive.end(),1); long long count=m;
    for(long long d=1;d<=C;d++){
        if(arcstart[d]<0) continue;
        long long b=arcstart[d];
        for(long long k=1;k<=d;k++){ long long t=(b+k)%m; if(alive[t]){alive[t]=0;count--;} }
        if(count==0) return d-1;
    }
    return C;
}
int main(int argc,char**argv){
    long long qlo=atoi(argv[1]), qhi=atoi(argv[2]);
    double BASELINE=2.639;
    double gbest=1e9; long long gq=0,gu=0,gcov=0;
    for(long long q=qlo;q<=qhi;q++){
        if(!is_prime(q)) continue;
        long long m=q*q+q+1;
        vector<long long> D=singer(q);
        if(D.empty()){fprintf(stderr,"q=%lld no singer\n",q);continue;}
        double reqd=16.0*(q+1)*(q+1)/BASELINE-6.0*m;
        long long C=(long long)ceil(reqd)+3; if(C>m-1)C=m-1; if(C<40)C=40;
        vector<long long> arcstart(C+1); vector<char> alive(m); vector<long long> uD(D.size());
        long long bcov=0,bu=1;
        for(long long u=1;u<m;u++){
            if(std::__gcd(u,m)!=1) continue;
            for(size_t i=0;i<D.size();i++) uD[i]=(u*D[i])%m;
            sort(uD.begin(),uD.end());
            long long c=arc_maxcov(uD,m,C,arcstart,alive);
            if(c>bcov){bcov=c;bu=u;}
        }
        long long k=6*m+bcov;
        double ratio=16.0*(q+1)*(q+1)/(double)k;
        printf("q=%lld m=%lld reqd=%.1f bestcov=%lld u=%lld k=%lld ratio=%.7f %s\n",
               q,m,reqd,bcov,bu,k,ratio, ratio<BASELINE?"*** BEATS 2.639 ***":"");
        fflush(stdout);
        if(ratio<gbest){gbest=ratio;gq=q;gu=bu;gcov=bcov;}
    }
    printf("\nGLOBAL BEST: q=%lld u=%lld cov=%lld ratio=%.7f (baseline %.4f) %s\n",
           gq,gu,gcov,gbest,BASELINE, gbest<BASELINE?"BEATS":"no beat");
    return 0;
}

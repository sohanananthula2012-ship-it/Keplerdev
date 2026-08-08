// dbsearch2.cpp — difference-basis search over prime q, units, translations.
// Singer difference set D mod m=q^2+q+1 (VERIFIED perfect). For each unit u,
// max contiguous positive-diff coverage over translations via arc method.
// A={0,1,4,6} (A-A=[-6,6]): k=6m+cov, |L|=4(q+1), ratio=|L|^2/k.
// Best candidate per q is brute-force reconstructed & verified. Record=2.6390 (baseline 2.639).
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
        // verify perfect difference set
        vector<char> seen(m,0); bool ok=true; long long cnt=0;
        for(size_t i=0;i<res.size()&&ok;i++)for(size_t j=0;j<res.size();j++) if(i!=j){
            long long d=((res[i]-res[j])%m+m)%m; if(d==0||seen[d]){ok=false;break;} seen[d]=1; cnt++;
        }
        if(ok && cnt==m-1) return res;
    }
    return {};
}
// arc method: max cov over translations for perfect set S mod m, cap C. returns cov (<=C).
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
// direct cov of set S (residues) cut at 0: contiguous positive-diff coverage
long long covB_direct(const vector<long long>&S,long long cap){
    int n=S.size(); vector<char> seen(cap+2,0);
    for(int i=0;i<n;i++)for(int j=i+1;j<n;j++){ long long d=S[j]-S[i]; if(d<=cap) seen[d]=1; }
    long long c=0; while(c+1<=cap && seen[c+1]) c++; return c;
}
int main(int argc,char**argv){
    long long qlo=atoi(argv[1]), qhi=atoi(argv[2]);
    double RECORD=2.6390274695, BASELINE=2.639;
    double gbest=1e9; long long gq=0,gu=0,gt=0,gcov=0;
    for(long long q=qlo;q<=qhi;q++){
        if(!is_prime(q)) continue;
        long long m=q*q+q+1;
        vector<long long> D=singer(q);
        if(D.empty()){fprintf(stderr,"q=%lld no singer\n",q);continue;}
        // cov needed to beat baseline 2.639: 16(q+1)^2/2.639 - 6m
        double reqd=16.0*(q+1)*(q+1)/BASELINE-6.0*m;
        long long C=(long long)ceil(reqd)+40; if(C>m-1)C=m-1; if(C<50)C=50;
        vector<long long> arcstart(C+1); vector<char> alive(m); vector<long long> uD(D.size());
        long long bcov=0,bu=1;
        for(long long u=1;u<m;u++){
            for(size_t i=0;i<D.size();i++) uD[i]=(u*D[i])%m;
            sort(uD.begin(),uD.end());
            long long c=arc_maxcov(uD,m,C,arcstart,alive);
            if(c>bcov){bcov=c;bu=u;}
        }
        // brute-verify best unit: scan all translations directly to get true cov & t
        for(size_t i=0;i<D.size();i++) uD[i]=(bu*D[i])%m;
        long long truecov=0,truet=0; vector<long long> St(D.size());
        for(long long t=0;t<m;t++){
            for(size_t i=0;i<D.size();i++) St[i]=(uD[i]+t)%m;
            sort(St.begin(),St.end());
            long long c=covB_direct(St,min(C+5,m-1));
            if(c>truecov){truecov=c;truet=t;}
        }
        long long k=6*m+truecov;
        double ratio=16.0*(q+1)*(q+1)/(double)k;
        printf("q=%lld m=%lld reqd=%.1f arc_cov=%lld true_cov=%lld u=%lld t=%lld k=%lld ratio=%.7f %s\n",
               q,m,reqd,bcov,truecov,bu,truet,k,ratio, ratio<BASELINE?"*** BEATS 2.639 ***":"");
        fflush(stdout);
        if(ratio<gbest){gbest=ratio;gq=q;gu=bu;gt=truet;gcov=truecov;}
    }
    printf("\nGLOBAL BEST: q=%lld u=%lld t=%lld cov=%lld ratio=%.7f (baseline %.4f) %s\n",
           gq,gu,gt,gcov,gbest,BASELINE, gbest<BASELINE?"BEATS":"no beat");
    return 0;
}

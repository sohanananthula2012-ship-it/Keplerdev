// singer_search.cpp
// Construct planar Singer difference sets mod m=q^2+q+1 for prime q via GF(q^3),
// maximize contiguous positive-difference self-coverage cov_B over unit multiples,
// combine with A={0,1,4,6} (A-A=[-6,6]) : k = 6m + cov_B, |L| = 4(q+1),
// ratio = |L|^2 / k. Report any q beating the AlphaEvolve record 2.6390274695.
#include <bits/stdc++.h>
using namespace std;

static bool is_prime(long long n){ if(n<2)return false; for(long long i=2;i*i<=n;i++) if(n%i==0) return false; return true; }

// Build Singer difference set for prime q. Returns residues (size q+1) or empty on failure.
vector<long long> singer(long long q){
    long long m=q*q+q+1;
    long long order=q*q*q-1;
    // try primitive cubics x^3 = r2 x^2 + r1 x + r0
    for(long long r0=1;r0<q;r0++) for(long long r2=0;r2<q;r2++) for(long long r1=0;r1<q;r1++){
        // iterate x powers, require full order (primitive)
        vector<char> W; W.reserve(q+2);
        long long c0=1,c1=0,c2=0; // element = 1
        bool primitive=true;
        vector<long long> res;
        for(long long i=0;i<order;i++){
            if(c2==0){ res.push_back(i%m); }
            // multiply by x: (c0,c1,c2)-> (c2*r0, c0+c2*r1, c1+c2*r2) mod q
            long long n0=(c2*r0)%q;
            long long n1=(c0 + c2*r1)%q;
            long long n2=(c1 + c2*r2)%q;
            c0=n0;c1=n1;c2=n2;
            if(i<order-1 && c0==1 && c1==0 && c2==0){ primitive=false; break; }
        }
        if(!primitive) continue;
        // dedup residues
        sort(res.begin(),res.end()); res.erase(unique(res.begin(),res.end()),res.end());
        if((long long)res.size()!=q+1) continue;
        // verify perfect difference set: all nonzero residues covered once
        vector<char> seen(m,0); bool ok=true; long long cnt=0;
        for(size_t i=0;i<res.size()&&ok;i++)for(size_t j=0;j<res.size();j++) if(i!=j){
            long long d=((res[i]-res[j])%m+m)%m; if(seen[d]){ok=false;break;} seen[d]=1; cnt++;
        }
        if(ok && cnt==m-1) return res;
    }
    return {};
}

// contiguous positive-difference coverage of set S (residues in [0,m)), capped at CAP
long long covB(const vector<long long>& S, long long CAP){
    int n=S.size();
    vector<char> seen(CAP+2,0);
    for(int i=0;i<n;i++){
        for(int j=i+1;j<n;j++){
            long long d=S[j]-S[i];
            if(d>CAP) break;
            seen[d]=1;
        }
    }
    long long c=0; while(c+1<=CAP && seen[c+1]) c++;
    return c;
}

int main(int argc,char**argv){
    long long qlo=atoi(argv[1]), qhi=atoi(argv[2]);
    double RECORD=2.6390274695;
    double best=1e9; long long bestq=0, bestcov=0, bestu=0;
    for(long long q=qlo;q<=qhi;q++){
        if(!is_prime(q)) continue;
        long long m=q*q+q+1;
        vector<long long> D=singer(q);
        if(D.empty()){ fprintf(stderr,"q=%lld: no singer\n",q); continue; }
        // required cov to beat record: cov > 16(q+1)^2/RECORD - 6m
        double reqd = 16.0*(q+1)*(q+1)/RECORD - 6.0*m;
        long long CAP = (long long)max(3000.0, reqd+2000);
        long long maxcov=0, bestuq=1;
        // scan all units u in [1,m) (m is prime)
        vector<long long> Bu(D.size());
        for(long long u=1;u<m;u++){
            for(size_t i=0;i<D.size();i++) Bu[i]=(u*D[i])%m;
            sort(Bu.begin(),Bu.end());
            long long c=covB(Bu,CAP);
            if(c>maxcov){ maxcov=c; bestuq=u; }
        }
        long long k=6*m+maxcov;
        double ratio=16.0*(q+1)*(q+1)/(double)k;
        printf("q=%lld m=%lld |B|=%lld maxcov=%lld reqd=%.1f k=%lld ratio=%.7f %s\n",
               q,m,(long long)D.size(),maxcov,reqd,k,ratio, ratio<RECORD?"*** BEATS ***":"");
        fflush(stdout);
        if(ratio<best){ best=ratio; bestq=q; bestcov=maxcov; bestu=bestuq; }
    }
    printf("\nBEST: q=%lld cov=%lld u=%lld ratio=%.7f (record=%.7f)\n",bestq,bestcov,bestu,best,RECORD);
    return 0;
}

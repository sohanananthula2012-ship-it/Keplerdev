// transcov.cpp — max contiguous positive-difference coverage over ALL translations
// (rotations) of a difference set, using the perfect-difference-set arc method.
// For a perfect difference set mod m, each residue d has a UNIQUE ordered pair (a,b),
// a-b≡d. Value d is realized (no wrap) at cut t unless t in arc (b,a] (length d).
// cov(t)=first forbidden d -1. max over t = (d when all cuts forbidden)-1.
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
        return res;
    }
    return {};
}
// max cov over translations for set S (residues) mod m, cap C
long long maxcov_trans(const vector<long long>&S,long long m,long long C){
    int n=S.size();
    // map residue-> (a,b): for d in 1..C find unique ordered pair with a-b≡d
    // build via all ordered pairs, store forbidden arc start for each residue
    // pair (a,b): res=(a-b)%m, arc = positions (b, a] i.e. b+1..b+res (mod m)
    // We only need residues 1..C.
    vector<long long> arcstart(C+1,-1); // b for residue d
    for(int i=0;i<n;i++)for(int j=0;j<n;j++) if(i!=j){
        long long d=((S[i]-S[j])%m+m)%m; // = a-b with a=S[i],b=S[j]
        if(d>=1 && d<=C) arcstart[d]=S[j]; // b
    }
    // arc removal
    vector<char> alive(m,1); long long count=m;
    for(long long d=1;d<=C;d++){
        if(arcstart[d]<0) continue; // shouldn't happen for perfect set within range
        long long b=arcstart[d];
        for(long long k=1;k<=d;k++){ long long t=(b+k)%m; if(alive[t]){alive[t]=0;count--;} }
        if(count==0) return d-1;
    }
    return C; // coverage exceeded cap
}
int main(int argc,char**argv){
    long long q=atoi(argv[1]);
    long long m=q*q+q+1;
    vector<long long> D=singer(q);
    if(D.empty()){printf("no singer q=%lld\n",q);return 1;}
    long long C=3000;
    // u=1 canonical
    long long c1=maxcov_trans(D,m,C);
    printf("q=%lld m=%lld |B|=%lld  u=1 maxcov_over_trans=%lld\n",q,m,(long long)D.size(),c1);
    printf("  => k=%lld ratio=%.7f\n",6*m+c1,16.0*(q+1)*(q+1)/(6.0*m+c1));
    return 0;
}

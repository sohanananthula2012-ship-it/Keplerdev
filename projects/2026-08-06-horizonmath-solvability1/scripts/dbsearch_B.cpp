// Structured search over the PROVEN Leech construction L = { a*m + b : a in A, b in B }.
// A = [0,1,4,6] (small difference basis), m = 89^2+89+1 = 8011, |B| = 90.
// We optimize the residue set B (Singer/AlphaEvolve-type perfect difference set) to
// maximize n = largest interval [1..n] fully covered by differences of L.
// Distinctness of L <=> distinctness of B (since |b|<m). |L| = 4*90 = 360 fixed.
#include <bits/stdc++.h>
using namespace std;

static const int MAXC = 60000;
static int cnt[MAXC+2];
static vector<int> pts;      // 360 point values, block layout: ai_index*90 + j
static int M;
static int holes;            // # uncovered in [1..TARGET]
static int TARGET;

inline void single_move(int idx, int newval){
    int old = pts[idx];
    for(int k=0;k<M;k++){ if(k==idx) continue; int q=pts[k]; int d=q>old?q-old:old-q; if(d>=1&&d<=MAXC){ cnt[d]--; if(d<=TARGET&&cnt[d]==0) holes++; } }
    for(int k=0;k<M;k++){ if(k==idx) continue; int q=pts[k]; int d=q>newval?q-newval:newval-q; if(d>=1&&d<=MAXC){ if(d<=TARGET&&cnt[d]==0) holes--; cnt[d]++; } }
    pts[idx]=newval;
}
int first_gap(){ for(int d=1;d<=MAXC;d++) if(cnt[d]==0) return d; return MAXC+1; }
int count_holes(int tgt){ int h=0; for(int d=1;d<=tgt;d++) if(cnt[d]==0) h++; return h; }

int main(int argc,char**argv){
    double TLIMIT = argc>1?atof(argv[1]):60.0;
    unsigned seed = argc>2?(unsigned)atoi(argv[2]):1u;
    TARGET       = argc>3?atoi(argv[3]):49110;
    double T0    = argc>4?atof(argv[4]):2.0;

    vector<long long> A={0,1,4,6};
    long long m=89LL*89+89+1;
    vector<int> B={0,1,70,83,255,297,384,391,550,555,647,656,710,996,1020,1232,1257,1272,1452,1456,1536,1614,1745,1765,1948,2047,2150,2188,2214,2395,2407,2585,2612,2628,2739,2758,2858,2902,2974,3006,3027,3245,3392,3477,3526,3615,3675,3727,3849,3906,3935,4043,4049,4253,4410,4445,4578,4580,4821,4855,4911,4934,4973,5032,5099,5149,5160,5411,5452,5518,5526,5658,5833,5855,5926,5943,5957,5994,6139,6185,6281,6592,6622,6669,6687,6697,6742,6745,6778,6967};
    int nb=B.size();
    // build pts in block layout
    pts.resize(4*nb);
    for(int ai=0;ai<4;ai++) for(int j=0;j<nb;j++) pts[ai*nb+j]=(int)(A[ai]*m+B[j]);
    M=pts.size();
    // build cnt
    for(int i=0;i<M;i++) for(int j=i+1;j<M;j++){int d=abs(pts[j]-pts[i]); if(d<=MAXC) cnt[d]++;}
    holes=count_holes(TARGET);
    int base_n=first_gap()-1;
    fprintf(stderr,"seed n=%d ratio=%.9f holes(TARGET=%d)=%d\n",base_n,(double)M*M/base_n,TARGET,holes);

    set<int> Bset(B.begin(),B.end());
    int best_n=base_n; vector<int> best_pts=pts;
    mt19937 rng(seed);
    auto uni=[&](){return (double)rng()/(double)rng.max();};
    clock_t start=clock(); long long it=0; double T=T0;
    while(true){
        if((it&2047)==0){ double el=(double)(clock()-start)/CLOCKS_PER_SEC; if(el>TLIMIT) break;
            double cyc=TLIMIT/4.0, fr=fmod(el,cyc)/cyc; T=T0*pow(0.02/T0,fr); if(T<0.02)T=0.02; }
        it++;
        int j=rng()%nb;
        int oldb=B[j];
        int nb_val;
        double r=uni();
        if(r<0.7){ int delta=(int)(rng()%81)-40; nb_val=oldb+delta; }
        else { nb_val=rng()%(int)m; }
        if(nb_val<0||nb_val>=(int)m||nb_val==oldb||Bset.count(nb_val)) continue;
        // the 4 affected point indices: ai*nb + j, new value = A[ai]*m + nb_val
        int idxs[4]; int newvals[4]; int oldvals[4];
        for(int ai=0;ai<4;ai++){ idxs[ai]=ai*nb+j; oldvals[ai]=pts[idxs[ai]]; newvals[ai]=(int)(A[ai]*m+nb_val); }
        int h_before=holes;
        for(int ai=0;ai<4;ai++) single_move(idxs[ai],newvals[ai]);
        int dh=holes-h_before;
        bool accept=(dh<=0)||(uni()<exp(-(double)dh/T));
        if(accept){
            B[j]=nb_val; Bset.erase(oldb); Bset.insert(nb_val);
            if(holes==0){ int ng=first_gap()-1; if(ng>best_n){ best_n=ng; best_pts=pts;
                fprintf(stderr,"SOLVED n=%d ratio=%.9f it=%lld T=%.3f\n",best_n,(double)M*M/best_n,it,T);
                TARGET=best_n+1; holes=count_holes(TARGET); } }
        } else {
            for(int ai=3;ai>=0;ai--) single_move(idxs[ai],oldvals[ai]);
        }
    }
    fprintf(stderr,"done it=%lld best_n=%d ratio=%.9f\n",it,best_n,(double)M*M/best_n);
    sort(best_pts.begin(),best_pts.end());
    printf("{\"n\": %d, \"M\": %d, \"ratio\": %.10f, \"basis\": [",best_n,M,(double)M*M/best_n);
    for(size_t k=0;k<best_pts.size();k++) printf("%d%s",best_pts[k],k+1<best_pts.size()?", ":"");
    printf("]}\n");
    return 0;
}

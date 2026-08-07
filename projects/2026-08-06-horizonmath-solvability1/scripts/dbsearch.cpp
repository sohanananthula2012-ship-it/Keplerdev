// Fast simulated-annealing search for difference basis beating 2.6390.
// Seeded from AlphaEvolve construction (360 points, n=49109).
// Objective: minimize number of holes in [1..TARGET]; when holes==0 we have a
// difference basis for {1..TARGET} with M points -> ratio = M*M/TARGET.
#include <bits/stdc++.h>
using namespace std;

int main(int argc, char** argv){
    double TLIMIT = argc>1? atof(argv[1]) : 60.0;
    unsigned seed = argc>2? (unsigned)atoi(argv[2]) : 1u;
    int TARGET   = argc>3? atoi(argv[3]) : 49110;   // coverage window
    double T0    = argc>4? atof(argv[4]) : 3.0;

    // Build AlphaEvolve L = { a*m + b }
    vector<long long> A = {0,1,4,6};
    vector<long long> B = {0,1,70,83,255,297,384,391,550,555,647,656,710,996,1020,1232,1257,1272,1452,1456,1536,1614,1745,1765,1948,2047,2150,2188,2214,2395,2407,2585,2612,2628,2739,2758,2858,2902,2974,3006,3027,3245,3392,3477,3526,3615,3675,3727,3849,3906,3935,4043,4049,4253,4410,4445,4578,4580,4821,4855,4911,4934,4973,5032,5099,5149,5160,5411,5452,5518,5526,5658,5833,5855,5926,5943,5957,5994,6139,6185,6281,6592,6622,6669,6687,6697,6742,6745,6778,6967};
    long long m = 89LL*89+89+1;
    set<long long> Ls;
    for(auto a:A) for(auto b:B) Ls.insert(a*m+b);
    vector<int> pts(Ls.begin(), Ls.end());
    int M = pts.size();

    const int MAXC = 90000;      // max coordinate / max difference
    vector<int> cnt(MAXC+1, 0);
    vector<char> occ(MAXC+1, 0);
    for(int x: pts){ occ[x]=1; }
    // build cnt
    for(int i=0;i<M;i++) for(int j=i+1;j<M;j++){ int d=pts[j]-pts[i]; if(d<=MAXC) cnt[d]++; }

    auto count_holes=[&](int tgt){ int h=0; for(int d=1; d<=tgt; d++) if(cnt[d]==0) h++; return h; };
    auto first_gap=[&](){ for(int d=1; d<=MAXC; d++) if(cnt[d]==0) return d; return MAXC+1; };

    int holes = count_holes(TARGET);
    int best_n = first_gap()-1;
    vector<int> best_pts = pts;

    mt19937 rng(seed);
    auto randint=[&](int lo,int hi){ return (int)(rng()%(unsigned)(hi-lo+1))+lo; };
    auto uni=[&](){ return (double)rng()/(double)rng.max(); };

    fprintf(stderr,"seed n=%d ratio=%.9f holes(TARGET=%d)=%d\n", best_n, (double)M*M/best_n, TARGET, holes);

    // holes list (uncovered values in [1..TARGET]), rebuilt periodically
    vector<int> holelist;
    auto rebuild_holes=[&](){ holelist.clear(); for(int d=1; d<=TARGET; d++) if(cnt[d]==0) holelist.push_back(d); };
    rebuild_holes();

    double T=T0;
    long long it=0;
    clock_t start=clock();
    long long since=0;
    while(true){
        if((it & 4095)==0){
            double el=(double)(clock()-start)/CLOCKS_PER_SEC;
            if(el>TLIMIT) break;
            // cooling
            T = T0 * pow(0.5, el/ (TLIMIT/8.0));
            if(T<0.02) T=0.02;
        }
        it++; since++;
        if(since>2000){ rebuild_holes(); since=0; }

        int i = randint(0,M-1);
        int old = pts[i];
        int cand;
        double r=uni();
        if(r<0.55 && !holelist.empty()){
            int h = holelist[rng()%holelist.size()];
            int q = pts[randint(0,M-1)];
            cand = (uni()<0.5)? q+h : q-h;
        } else if(r<0.85){
            cand = old + randint(-50,50);
        } else {
            cand = randint(0,MAXC);
        }
        if(cand<0||cand>MAXC||cand==old||occ[cand]) continue;

        // delta holes: remove old, add cand
        int dh=0;
        // remove old
        for(int k=0;k<M;k++){ if(k==i) continue; int q=pts[k]; int d=q>old?q-old:old-q; if(d>=1&&d<=MAXC){ cnt[d]--; if(d<=TARGET && cnt[d]==0) dh++; } }
        // add cand
        for(int k=0;k<M;k++){ if(k==i) continue; int q=pts[k]; int d=q>cand?q-cand:cand-q; if(d>=1&&d<=MAXC){ if(d<=TARGET && cnt[d]==0) dh--; cnt[d]++; } }

        bool accept = (dh<=0) || (uni() < exp(-(double)dh / T));
        if(accept){
            occ[old]=0; occ[cand]=1; pts[i]=cand; holes+=dh;
            if(holes==0){
                int ng=first_gap()-1;
                if(ng>best_n){ best_n=ng; best_pts=pts;
                    fprintf(stderr,"SOLVED window; n=%d ratio=%.9f it=%lld T=%.3f\n", best_n,(double)M*M/best_n,it,T);
                    // raise target to push further
                    TARGET = best_n+1;
                    holes = count_holes(TARGET);
                    rebuild_holes();
                }
            }
        } else {
            // revert
            for(int k=0;k<M;k++){ if(k==i) continue; int q=pts[k]; int d=q>cand?q-cand:cand-q; if(d>=1&&d<=MAXC) cnt[d]--; }
            for(int k=0;k<M;k++){ if(k==i) continue; int q=pts[k]; int d=q>old?q-old:old-q; if(d>=1&&d<=MAXC) cnt[d]++; }
        }
    }
    // final report + dump best
    fprintf(stderr,"done it=%lld best_n=%d ratio=%.9f\n", it, best_n, (double)M*M/best_n);
    // print best_pts as JSON to stdout
    printf("{\"n\": %d, \"M\": %d, \"ratio\": %.10f, \"basis\": [", best_n, M, (double)M*M/best_n);
    sort(best_pts.begin(),best_pts.end());
    for(size_t k=0;k<best_pts.size();k++){ printf("%d%s", best_pts[k], k+1<best_pts.size()?", ":""); }
    printf("]}\n");
    return 0;
}

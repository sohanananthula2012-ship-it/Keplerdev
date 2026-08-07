// Heilbronn n=12: multi-threaded SA aiming to BEAT the record 0.0325988586918197.
// Targeted worst-triangle moves + random moves + reheating + fine polish.
// Usage: ./heilbronn_beat <threads> <restarts_per_thread> <iters> <seed> [warm.txt]
// warm.txt: first line count(12), then 12 lines "x y". Output best to stdout:
//   line1: bestmin ; then 12 lines "x y".
#include <bits/stdc++.h>
#include <thread>
#include <mutex>
using namespace std;
static const int N = 12;
static int TRI[220][3]; static int NT=0;
static vector<int> triOf[N];

inline double area(const double*x,const double*y,int a,int b,int c){
    return 0.5*fabs((x[b]-x[a])*(y[c]-y[a])-(x[c]-x[a])*(y[b]-y[a]));
}
double fullmin(const double*x,const double*y,int&wt){
    double m=1e9; wt=0;
    for(int t=0;t<NT;t++){double a=area(x,y,TRI[t][0],TRI[t][1],TRI[t][2]); if(a<m){m=a;wt=t;}}
    return m;
}
double fullmin2(const double*x,const double*y){int w;return fullmin(x,y,w);}

double gBest=-1; double gX[N],gY[N]; mutex gMx;

void polish(double*X,double*Y,double&cur){
    double step=0.06;
    for(int pass=0;pass<50000;pass++){
        bool improved=false;
        for(int p=0;p<N;p++){
            double ox=X[p],oy=Y[p],bcur=cur,bx=ox,by=oy;
            for(int dir=0;dir<24;dir++){
                double ang=2*M_PI*dir/24;
                for(double rr=1.0; rr>=0.34; rr*=0.5){
                    double nx=ox+step*rr*cos(ang), ny=oy+step*rr*sin(ang);
                    if(nx<0)nx=0;if(nx>1)nx=1;if(ny<0)ny=0;if(ny>1)ny=1;
                    X[p]=nx;Y[p]=ny; double nm=fullmin2(X,Y);
                    if(nm>bcur){bcur=nm;bx=nx;by=ny;}
                }
            }
            X[p]=bx;Y[p]=by;
            if(bcur>cur+1e-16){cur=bcur;improved=true;}
        }
        if(!improved){step*=0.5; if(step<1e-8)break;}
    }
}

void worker(int tid,long long restarts,long long iters,unsigned seed,
            const vector<double>&warmX,const vector<double>&warmY){
    mt19937_64 rng(seed+7919*tid);
    uniform_real_distribution<double> U(0,1);
    normal_distribution<double> Nrm(0,1);
    double X[N],Y[N];
    double lBest=-1,lBX[N],lBY[N];
    for(long long r=0;r<restarts;r++){
        // init: warm start (perturbed) on ~30% of restarts if available, else random
        if(!warmX.empty() && (r%3==0)){
            double sc=0.01+0.12*U(rng);
            for(int i=0;i<N;i++){X[i]=min(1.0,max(0.0,warmX[i]+sc*Nrm(rng)));
                                 Y[i]=min(1.0,max(0.0,warmY[i]+sc*Nrm(rng)));}
        } else {
            for(int i=0;i<N;i++){X[i]=U(rng);Y[i]=U(rng);}
        }
        int wt; double cur=fullmin(X,Y,wt);
        double T0=0.08, Tend=1e-6;
        for(long long it=0;it<iters;it++){
            double frac=(double)it/iters;
            double T=T0*pow(Tend/T0,frac);
            double step=0.2*(1.0-frac)+0.005;
            int p;
            if(U(rng)<0.5){ // targeted: move a vertex of the current worst triangle
                int v=rng()%3; p=TRI[wt][v];
            } else p=rng()%N;
            double ox=X[p],oy=Y[p];
            double nx=ox+step*Nrm(rng), ny=oy+step*Nrm(rng);
            if(nx<0)nx=0;if(nx>1)nx=1;if(ny<0)ny=0;if(ny>1)ny=1;
            X[p]=nx;Y[p]=ny;
            int nwt; double nm=fullmin(X,Y,nwt);
            double d=nm-cur;
            if(d>=0 || U(rng)<exp(d/T)){cur=nm;wt=nwt;}
            else{X[p]=ox;Y[p]=oy;}
        }
        polish(X,Y,cur);
        if(cur>lBest){lBest=cur; for(int i=0;i<N;i++){lBX[i]=X[i];lBY[i]=Y[i];}}
    }
    lock_guard<mutex> lk(gMx);
    if(lBest>gBest){gBest=lBest; for(int i=0;i<N;i++){gX[i]=lBX[i];gY[i]=lBY[i];}
        fprintf(stderr,"[t%d] new best=%.13f\n",tid,gBest);}
}

int main(int argc,char**argv){
    for(int i=0;i<N;i++)for(int j=i+1;j<N;j++)for(int k=j+1;k<N;k++){
        TRI[NT][0]=i;TRI[NT][1]=j;TRI[NT][2]=k;
        triOf[i].push_back(NT);triOf[j].push_back(NT);triOf[k].push_back(NT);NT++;}
    int threads = argc>1?atoi(argv[1]):4;
    long long restarts = argc>2?atoll(argv[2]):500;
    long long iters = argc>3?atoll(argv[3]):60000;
    unsigned seed = argc>4?atoi(argv[4]):12345;
    vector<double> wX,wY;
    if(argc>5){
        FILE*f=fopen(argv[5],"r"); if(f){int c;fscanf(f,"%d",&c);
            for(int i=0;i<c;i++){double a,b;fscanf(f,"%lf %lf",&a,&b);wX.push_back(a);wY.push_back(b);}fclose(f);
            int w; double m=fullmin(wX.data(),wY.data(),w); gBest=m;
            for(int i=0;i<N;i++){gX[i]=wX[i];gY[i]=wY[i];}
            fprintf(stderr,"warm best=%.13f\n",m);}
    }
    vector<thread> th;
    for(int t=0;t<threads;t++) th.emplace_back(worker,t,restarts,iters,seed,cref(wX),cref(wY));
    for(auto&x:th)x.join();
    printf("%.15f\n",gBest);
    for(int i=0;i<N;i++)printf("%.15f %.15f\n",gX[i],gY[i]);
    return 0;
}

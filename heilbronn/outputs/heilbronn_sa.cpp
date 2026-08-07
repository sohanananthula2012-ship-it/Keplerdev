// Heilbronn n=12: fast simulated-annealing + hill-climb solver.
// Maximize the minimum triangle area of 12 points in [0,1]^2.
#include <bits/stdc++.h>
using namespace std;
static const int N = 12;
static int TRI[220][3];
static int NT = 0;
double X[N], Y[N];
inline double area(const double*x,const double*y,int a,int b,int c){
    return 0.5*fabs((x[b]-x[a])*(y[c]-y[a])-(x[c]-x[a])*(y[b]-y[a]));
}
double fullmin(const double*x,const double*y){
    double m=1e9;
    for(int t=0;t<NT;t++){double a=area(x,y,TRI[t][0],TRI[t][1],TRI[t][2]); if(a<m)m=a;}
    return m;
}
int main(int argc,char**argv){
    for(int i=0;i<N;i++)for(int j=i+1;j<N;j++)for(int k=j+1;k<N;k++){
        TRI[NT][0]=i;TRI[NT][1]=j;TRI[NT][2]=k;NT++;}
    long long restarts = argc>1?atoll(argv[1]):20000;
    long long iters    = argc>2?atoll(argv[2]):20000;
    unsigned seed      = argc>3?atoi(argv[3]):12345;
    double bestGlobal=-1; double bestX[N],bestY[N];
    mt19937_64 rng(seed);
    uniform_real_distribution<double> U(0.0,1.0);
    normal_distribution<double> Nrm(0.0,1.0);
    for(long long r=0;r<restarts;r++){
        for(int i=0;i<N;i++){X[i]=U(rng);Y[i]=U(rng);}
        double cur=fullmin(X,Y);
        double T0=0.15, Tend=1e-5;
        for(long long it=0;it<iters;it++){
            double frac=(double)it/iters;
            double T=T0*pow(Tend/T0,frac);
            double step=0.25*(1.0-frac)+0.01;
            int p=rng()%N; double ox=X[p],oy=Y[p];
            double nx=ox+step*Nrm(rng), ny=oy+step*Nrm(rng);
            if(nx<0)nx=0;if(nx>1)nx=1;if(ny<0)ny=0;if(ny>1)ny=1;
            X[p]=nx;Y[p]=ny;
            double nm=fullmin(X,Y);
            double d=nm-cur;
            if(d>=0 || U(rng)<exp(d/T)){cur=nm;}
            else{X[p]=ox;Y[p]=oy;}
        }
        double step=0.05;
        for(int pass=0;pass<20000;pass++){
            bool improved=false;
            for(int p=0;p<N;p++){
                double ox=X[p],oy=Y[p]; double bcur=cur,bx=ox,by=oy;
                for(int dir=0;dir<16;dir++){
                    double ang=2*M_PI*dir/16;
                    double nx=ox+step*cos(ang), ny=oy+step*sin(ang);
                    if(nx<0)nx=0;if(nx>1)nx=1;if(ny<0)ny=0;if(ny>1)ny=1;
                    X[p]=nx;Y[p]=ny; double nm=fullmin(X,Y);
                    if(nm>bcur){bcur=nm;bx=nx;by=ny;}
                }
                X[p]=bx;Y[p]=by;
                if(bcur>cur+1e-15){cur=bcur;improved=true;}
            }
            if(!improved){step*=0.5; if(step<1e-7)break;}
        }
        if(cur>bestGlobal){
            bestGlobal=cur;
            for(int i=0;i<N;i++){bestX[i]=X[i];bestY[i]=Y[i];}
            fprintf(stderr,"restart %lld: best=%.10f\n",r,bestGlobal);
        }
    }
    printf("%.12f\n",bestGlobal);
    for(int i=0;i<N;i++)printf("%.12f %.12f\n",bestX[i],bestY[i]);
    return 0;
}

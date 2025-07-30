#include <algorithm>
#include <vector>
#include <regex>
#include "common.h"
#include "numerical_common_definitions.h"

using namespace std;

void PrintDebugItems(ofstream& ofs, double x, vector<double> &y)
{
	if(ofs.is_open() == false){
		return;
	}
	ofs << x << "\t";
    PrintDebugItems(ofs, y);
}

void PrintDebugPair(ofstream& ofs, vector<double> &x, vector<double> &y, int nlines)
{
	if(ofs.is_open() == false){
		return;
	}
    if(nlines < 0){
        nlines = (int)min(x.size(), y.size());
    }
    for(int n = 0; n < nlines; n++){
        ofs << x[n] << "\t" << y[n] << endl;
    }
}

void PrintDebugCols(ofstream& ofs, vector<double> &x, vector<vector<double>> &y, int nlines)
{
	if(ofs.is_open() == false){
		return;
	}
    if(nlines < 0){
        nlines = (int)min(x.size(), y.size());
    }
    for(int n = 0; n < nlines; n++){
        PrintDebugItems(ofs, x[n], y[n]);
    }
}

void PrintDebugRows(
    ofstream &ofs, vector<double> &x, vector<vector<double>> &y, int nlines, double scale)
{
	if(ofs.is_open() == false){
		return;
	}
    if(nlines < 0){
        nlines = (int)x.size();
        for(int j = 0; j < y.size(); j++){
            nlines = (int)min(nlines, (int)y[j].size());
        }
    }
    vector<double> item(y.size());
    for(int n = 0; n < nlines; n++){
        for(int j = 0; j < y.size(); j++){
            item[j] = y[j][n]/scale;
        }
        PrintDebugItems(ofs, x[n], item);
    }
}

void PrintDebugFFT(
    ofstream &ofs, double dx, double *y, int nfft, int nlimit, bool isinv, double scale)
{
	if(ofs.is_open() == false){
		return;
	}

    nlimit = min(nfft, nlimit);
    int nini = 0, nfin = nlimit, idx;
    if(isinv){
        nini = -nlimit/2+1;
        nfin = nlimit/2;
    }
    for(int n = nini; n < nfin; n++){
        if(n < 0){
            idx = fft_index(n, nfft, -1);
        }
        else{
            idx = n;
        }
        ofs << dx*n << "\t" << y[2*idx]/scale << "\t" << y[2*idx+1]/scale << endl;
    }
}

double fft_window(int n, int nfft, int nmesh, int noffset)
{
    int nb[2] = {noffset, noffset+nmesh-1};
    double tex;
    if(n < nb[0]){
        tex = 4.0*(double)(nb[0]-n)/(double)nb[0];
    }
    else if(n > nb[1]){
        tex = 4.0*(double)(n-nb[1])/(double)(nfft-1-nb[1]);
    }
    else{
        return 1;
    }
    return exp(-tex*tex*0.5);
}

void mpi_steps(int i, int j, int processes, 
	vector<int> *steps, vector<int> *inistep, vector<int> *finstep)
{
	int ntotal = i*j;
	int navg = ntotal/processes;
	int nadd = ntotal%processes;

	if(steps->size() < processes){
		steps->resize(processes);
	}
	if(inistep->size() < processes){
		inistep->resize(processes, -1);
	}
	if(finstep->size() < processes){
		finstep->resize(processes, -1);
	}

	for(int n = 0; n < processes; n++){
		if(n < nadd){
			(*steps)[n] = navg+1;
		}
		else{
			(*steps)[n] = navg;
		}
		if(n == 0){
			(*inistep)[n] = 0;
		}
		else{
			(*inistep)[n] = (*finstep)[n-1]+1;
		}
		(*finstep)[n] = (*inistep)[n]+(*steps)[n]-1;
	}
}

double hypotsq(double x, double y)
{
	return x*x+y*y;
}

double hypotsq(double x, double y, double z)
{
	return x*x+y*y+z*z;
}

double hypotsq(double x[], int ndim)
{
    double sum = 0;
    for(int n = 0; n < ndim; n++){
        sum += x[n]*x[n];
    }
    return sum;
}

void stokes(double *fx, double *fy, vector<double> *s)
{
	(*s)[0] = fx[0]*fx[0]+fx[1]*fx[1];
	(*s)[1] = fy[0]*fy[0]+fy[1]*fy[1];
	(*s)[2] = 2.0*(fx[1]*fy[0]-fx[0]*fy[1]);
	(*s)[3] = 2.0*(fx[0]*fy[0]+fx[1]*fy[1]);
}

void stokes(vector<double> &fd)
{
    fd[0] += fd[1];
    fd[1] = fd[0]-2.0*fd[1];

    double tf = max(max(fd[0], fd[2]), max(fd[3], INFINITESIMAL));
    for(int j = 1; j < 4; j++){
        fd[j] /= tf;
        if(fabs(fd[j]) < 1.0e-10){ // neglect pol. rate < 1e-10
            fd[j] = 0;
        }
    }
}

void *realloc_chk(void *ptr, int size)
{
	void *pnew = realloc(ptr, size);
	if(pnew == nullptr){
		free(ptr);
	}
	return pnew;
}

double simple_integration(int npoints, double dx, vector<double> &y)
{
    double ans = 0.0;
    if(npoints <= 1){
        return 0.0;
    }
    for(int n = 1; n < npoints-1; n += 2){
        ans += y[n-1]+4.0*y[n]+y[n+1];
    }
    ans *= dx/3.0;
    if(npoints%2 == 0){
        ans += (y[npoints-2]+y[npoints-1])*dx*0.5;
    }
    return ans;
}

int fft_index(int index, int nfft, int idir)
{
    if(idir > 0){ // (0...mesh-1) -> (-mesh/2+1...mesh/2)
        if(index <= nfft/2){
            return index;
        }
        else{
            return -(nfft-index);
        }
    }
    else{ // (-mesh/2+1...mesh/2) -> (0...mesh-1)
        if(index < 0){
            return index+nfft;
        }
        else{
            return index;
        }
    }
}

int fft_number(int ndata, int fftlevel)
{
    int nfft = 1;
    while(nfft < ndata){
        nfft <<= 1;
    }
    nfft <<= max(0, fftlevel-1);
    return nfft;
}

//  errf(x) = 2/sqrt(pi) int_0^x exp(-t^2)dt
double errf(double x)
{
    double t, z, ans, ret, arg;

    z = fabs(x);
    t = 1.0/(1.0+0.5*z);
    arg = -z*z-1.26551223+t*(1.00002368+t*(0.37409196+t*(0.09678418+
          t*(-0.18628806+t*(0.27886807+t*(-1.13520398+t*(1.48851587+
          t*(-0.82215223+t*0.17087277))))))));
    if(arg < -MAXIMUM_EXPONENT){
        ans = 0.0;
    }
    else{
        ans = t*exp(arg);
    }
    ret = x >= 0.0 ? ans : 2.0-ans;
    return 1.0-ret;
}

double errfinv(double y)
{
    double s, t, u, w, x, z;

    y = 1.0-y;
    z = y;
    if (y > 1) {
        z = 2 - y;
    }
    w = 0.916461398268964-log(z);
    u = sqrt(w);
    s = (log(u) + 0.488826640273108) / w;
    t = 1 / (u + 0.231729200323405);
    x = u * (1 - s * (s * 0.124610454613712 + 0.5)) -
        ((((-0.0728846765585675 * t + 0.269999308670029) * t +
        0.150689047360223) * t + 0.116065025341614) * t +
        0.499999303439796) * t;
    t = 3.97886080735226 / (x + 3.97886080735226);
    u = t - 0.5;
    s = (((((((((0.00112648096188977922 * u +
        1.05739299623423047e-4) * u - 0.00351287146129100025) * u -
        7.71708358954120939e-4) * u + 0.00685649426074558612) * u +
        0.00339721910367775861) * u - 0.011274916933250487) * u -
        0.0118598117047771104) * u + 0.0142961988697898018) * u +
        0.0346494207789099922) * u + 0.00220995927012179067;
    s = ((((((((((((s * u - 0.0743424357241784861) * u -
        0.105872177941595488) * u + 0.0147297938331485121) * u +
        0.316847638520135944) * u + 0.713657635868730364) * u +
        1.05375024970847138) * u + 1.21448730779995237) * u +
        1.16374581931560831) * u + 0.956464974744799006) * u +
        0.686265948274097816) * u + 0.434397492331430115) * u +
        0.244044510593190935) * t -
        z * exp(x * x - 0.120782237635245222);
    x += s * (x * s + 1);
    if (y > 1) {
        x = -x;
    }
    return x;
}

// int _0 ^t exp(i Pi t^2/2) dt
void fresnel_integral(double x0, double *C, double *S)
{
    double x[4];
    double a[4] = {1.0, 0.1756, 0, 0};
    double b[4] = {2.0, 2.915, 2.079, 1.519};
    double c[4] = {1.0, 0.5083, 0.3569, 0};
    double d[4] = {SQRT2, 2.1416, 1.8515, 1.1021};
    double Rd, Rn, Ad, An;

    x[0] = 1.0;
    x[1] = fabs(x0);
    x[2] = x[1]*x[1];
    x[3] = x[2]*x[1];

    Rd = Rn = Ad = An = 0.0;
    for(int j = 0; j < 4; j++){
        Rd += d[j]*x[j];
        Rn += c[j]*x[j];
        Ad += b[j]*x[j];
        An += a[j]*x[j];
    }
    Rn /= Rd;
    An /= Ad;
    *C = 0.5-Rn*sin(PId2*(An-x[2]));
    *S = 0.5-Rn*cos(PId2*(An-x[2]));

    if(x0 < 0){
        *S = -*S;
        *C = -*C;
    }
}

double sinc(double x)
{
    if(fabs(x) > MAX_ARG_SN_APPROX){
        return sin(x)/x;
    }
    return 1.0-x*x/6.0;
}

double sincsq(double x)
{
    double res = sinc(x);
    return res*res;
}

double sinfunc(int M, double x, bool issq)
{
    double res;
	int nin;

    x = fabs(x);
	nin = (int)floor(0.5+x/PI);
    x -= PI*(double)nin;
    if(fabs(x) > MAX_ARG_SN_APPROX){
        res = sin(M*x)/sin(x);
    }
    else{
        res = (1.0+x*x/6.0)*M*sinc(M*x);
    }
	if(nin%2 > 0 && M%2 == 0){
		res = -res;
	}

    return issq?res*res:res;
}

double wave_length(double ep)
{
    if(ep){
        return ONE_ANGSTROM_eV/ep/1.0e+10;
    }
    else{
        return 1.0/INFINITESIMAL;
    }
}

double wave_number(double ep)
{
    return ep/PLANKCC;
}

double photon_energy(double wavelength)
{
    if(wavelength){
        return ONE_ANGSTROM_eV/(wavelength*1.0e+10);
    }
    else{
        return 1.0/INFINITESIMAL;
    }
}

void get_EMF_variables(double cE, double betaxy[], double B[], double xy[])
{
    // assume positive charge
    xy[0] = cE*(betaxy[1]*B[2]-B[1]); // d beta_x / dz
    xy[1] = cE*(B[0]-betaxy[0]*B[2]); // d beta_y / dz
    xy[2] = betaxy[0];
    xy[3] = betaxy[1];
    xy[4] = hypotsq(betaxy[0], betaxy[1]);
}

bool get_2d_matrix_indices(
	double xy[], double *valrange, double *inirange, double *delta, int *mesh, int index[], double dresxy[])
{
	bool inrange = true;
    double dres[2];

	for(int j = 0; j < 2; j++){
        if(inirange != nullptr){
            dres[j] = (xy[j]-inirange[j])/delta[j];
            if(dres[j] < -EXP2AVOID_ROUNDING_ERROR 
                || dres[j] >= mesh[j]-1+EXP2AVOID_ROUNDING_ERROR){
                // dsave: avoid rounding-error effect
                inrange = false;
                break;
            }
        }
        else{
            if (fabs(xy[j]) > valrange[j]){
                inrange = false;
                break;
            }
            dres[j] = xy[j]/delta[j]+((double)mesh[j]-1.0)/2.0;
        }
		index[j] = (int)floor(dres[j]);
		index[j] = min(mesh[j]-2, max(0, index[j]));
		dres[j] -= (double)index[j];
	}

	if(inrange){
		dresxy[3] = dres[0]*dres[1];
		dresxy[2] = (1.0-dres[0])*dres[1];
		dresxy[1] = dres[0]*(1.0-dres[1]);
		dresxy[0] = (1.0-dres[0])*(1.0-dres[1]);
	}
	return inrange;
}

double coshyper(double x)
{
    return (exp(x)+exp(-x))*0.5;
}

double sinhyper(double x)
{
    return (exp(x)-exp(-x))*0.5;
}

void get_ideal_field_2d(bool isfoc, double z, double xy, double Bp, double lu, int N, 
    double zorg, double *byz, double Iferr, bool isoddpole, bool isendcorr)
    // 0: main component (e.g., By), 1: sub component (e.g, Bz)
{
    double zref, dphi = 0;
    double Lh = lu*(double)N*0.5;
    double ku = PI2/lu;
	double amp[2];

	amp[0] = isendcorr ? 0.25 : 0;
	amp[1] = isendcorr ? 0.75 : 0.5;

	if(isoddpole){
		Lh -= 0.25*lu;
		dphi = PId2;
	}

    zref = z-zorg;
    if(fabs(zref) > Lh){
        byz[0] = byz[1] = 0.0;
    }
    else if(fabs(zref) > Lh-lu*0.25){
        byz[1] = 0.0;
        byz[0] = amp[0]*Bp*sin(ku*zref+dphi)*(isfoc ? coshyper(ku*xy) : 1.0);
    }
    else if(fabs(zref) > Lh-lu*0.5){
        byz[1] = Bp*cos(ku*zref+dphi)*(isfoc ? sinhyper(ku*xy) : 0.0);
        byz[0] = amp[0]*Bp*sin(ku*zref+dphi)*(isfoc ? coshyper(ku*xy) : 1.0);
    }
    else if(fabs(zref) > Lh-lu){
        byz[1] = Bp*cos(ku*zref+dphi)*(isfoc ? sinhyper(ku*xy) : 0.0);
        byz[0] = amp[1]*Bp*sin(ku*zref+dphi)*(isfoc ? coshyper(ku*xy) : 1.0);
    }
    else{
        byz[1] = Bp*cos(ku*zref+dphi)*(isfoc ? sinhyper(ku*xy) : 0.0);
        byz[0] = Bp*sin(ku*zref+dphi)*(isfoc ? coshyper(ku*xy) : 1.0);
    }
    if(fabs(Iferr) > INFINITESIMAL){
        if(zref > Lh-lu*0.5 && zref < Lh){
            byz[0] += (PI*Iferr/lu)*fabs(sin(ku*zref+dphi));
        }
    }
}

void unit_matrix(int dim, vector<vector<double>> &M)
{
    for(int j = 0; j < dim; j++){
        for (int i = 0; i < dim; i++){
            if(i == j){
                M[i][j] = 1.0;
            }
            else{
                M[i][j] = 0;
            }
        }
    }
}

void csd_matrix(double cs, double csd, double ss, double ssd, double ds, double dsd,
    vector<vector<double>> &M)
{
    M[0][0] = cs;
    M[0][1] = ss;
    M[0][2] = ds;
    M[1][0] = csd;
    M[1][1] = ssd;
    M[1][2] = dsd;
    M[2][0] = 0.0;
    M[2][1] = 0.0;
    M[2][2] = 1.0;
}

void multiply_matrices(vector<vector<double>> &M1, vector<vector<double>> &M2,
    vector<vector<double>> &M3)
{
    int i, j, k;
    for(i = 0; i < 3; i++){
        for(j = 0; j < 3; j++){
            M3[i][j] = 0.0;
            for(k = 0; k < 3; k++){
                M3[i][j] += M1[i][k]*M2[k][j];
            }
        }
    }
}

bool inverse_matrix(vector<vector<double>> &M, vector<vector<double>> &Minv)
{
    double D;

    D = M[0][0]*(M[1][1]*M[2][2]-M[1][2]*M[2][1])
        +M[0][1]*(M[1][2]*M[2][0]-M[1][0]*M[2][2])
        +M[0][2]*(M[1][0]*M[2][1]-M[1][1]*M[2][0]);
    if(D == 0){
        return false;
    }

    Minv[0][0] = (M[1][1]*M[2][2]-M[1][2]*M[2][1])/D;
    Minv[0][1] = (M[0][2]*M[2][1]-M[0][1]*M[2][2])/D;
    Minv[0][2] = (M[0][1]*M[1][2]-M[0][2]*M[1][1])/D;
    Minv[1][0] = (M[1][2]*M[2][0]-M[1][0]*M[2][2])/D;
    Minv[1][1] = (M[0][0]*M[2][2]-M[0][2]*M[2][0])/D;
    Minv[1][2] = (M[0][2]*M[1][0]-M[0][0]*M[1][2])/D;
    Minv[2][0] = (M[1][0]*M[2][1]-M[1][1]*M[2][0])/D;
    Minv[2][1] = (M[0][1]*M[2][0]-M[0][0]*M[2][1])/D;
    Minv[2][2] = (M[0][0]*M[1][1]-M[0][1]*M[1][0])/D;

    return true;
}

double lininterp2d(vector<vector<double>> &f, double dindex[])
{
    double dresxy[4], dres[2];
    int index[2], nmax[2];

    nmax[0] = (int)f.size()-2;
    nmax[1] = (int)f[0].size()-2;

    for(int j = 0; j < 2; j++){
        index[j] = max(0, min((int)floor(dindex[j]), nmax[j]));
        dres[j] = dindex[j]-index[j];
    }

    dresxy[3] = dres[0]*dres[1];
    dresxy[2] = (1.0-dres[0])*dres[1];
    dresxy[1] = dres[0]*(1.0-dres[1]);
    dresxy[0] = (1.0-dres[0])*(1.0-dres[1]);

    double sum = 
         f[index[0]][index[1]]*dresxy[0]
        +f[index[0]+1][index[1]]*dresxy[1]
        +f[index[0]][index[1]+1]*dresxy[2]
        +f[index[0]+1][index[1]+1]*dresxy[3];

    return sum;
}

double lagrange2d(vector<vector<double>> &f, double dindex[], int *nmaxp)
{
    int index[2], nmax[2];
    double dresxy[2], vtmp[3];

    if(nmaxp != nullptr){
        for(int j = 0; j < 2; j++){
            nmax[j] = nmaxp[j];
        }
    }
    else{
        nmax[0] = (int)f.size()-1;
        nmax[1] = (int)f[0].size()-1;
    }

    for(int j = 0; j < 2; j++){
        index[j] = (int)floor(dindex[j]+0.5);
        if(index[j] < 0 || index[j] > nmax[j]){
            return 0;
        }
        index[j] = min(max(1, index[j]), nmax[j]-1);
        dresxy[j] = dindex[j]-index[j];
    }

    for(int k = -1; k <= 1; k++){
        vtmp[k+1] = lagrange(dresxy[0], -1.0, 0.0, 1.0, 
            f[index[0]-1][index[1]+k], f[index[0]][index[1]+k], f[index[0]+1][index[1]+k]);
    }
    return lagrange(dresxy[1], -1.0, 0.0, 1.0, vtmp[0], vtmp[1], vtmp[2]);
}

int SearchIndex(int nsize, bool isreg, vector<double> &xarr, double x)
{
	int km, kp, k, n = nsize;

	if(isreg){
		double dx = (xarr[nsize-1]-xarr[0])/(double)(nsize-1);
		km = (int)((x-xarr[0])/dx);
		if(km >= n-1){
			km = n-2;
		}
		if(km < 0){
			km = 0;
		}
		kp = km+1;
	}
	else{
		km = 0;
		kp = n-1;
		while (kp-km > 1){
			k = (kp+km) >> 1;
			if((xarr[0] < xarr[1] && xarr[k] > x)
				|| (xarr[0] > xarr[1] && xarr[k] < x)){
				kp = k;
			}
			else{
				km = k;
			}
		}
	}
	return xarr[0] < xarr[1] ? km : kp;
}

int get_index4lagrange(double x, vector<double> &xa, int size)
{
	int index = SearchIndex(size, false, xa, x);
	int incr = xa[0] < xa[1] ? 1 : -1;
	if(fabs(x-xa[index]) > fabs(x-xa[index+incr])){
		index = index+incr;
	}
	index = max(1, min(size-2, index));
    return index;
}

double lagrange(double t,
    double t0, double t1, double t2, double e0, double e1, double e2)
{
    double ft;
    ft = e0*(t-t1)*(t-t2)/(t0-t1)/(t0-t2)
         +e1*(t-t0)*(t-t2)/(t1-t0)/(t1-t2)
         +e2*(t-t0)*(t-t1)/(t2-t0)/(t2-t1);
    return ft;
}

double lininterp(double t, double t0, double t1, double e0, double e1)
{
    return e0+(e1-e0)/(t1-t0)*(t-t0);
}

double parabloic_peak(double *xpeak,
        double x0, double x1, double x2, double f0, double f1, double f2)
{
    double a, b, peak;

    a = f0/(x0-x1)/(x0-x2)+f1/(x1-x0)/(x1-x2)+f2/(x2-x1)/(x2-x0);
    b = -(x1+x2)*f0/(x0-x1)/(x0-x2)-(x0+x2)*f1/(x1-x0)/(x1-x2)-(x1+x0)*f2/(x2-x1)/(x2-x0);
    if(a == 0.0){
        *xpeak = x1;
        peak = f1;
    }
    else{
        *xpeak = -b/2.0/a;
        peak = lagrange(*xpeak, x0, x1, x2, f0, f1, f2);
    }
    return peak;
}

int get_parabolic_peak(vector<double> &x, vector<double> &y,
    double *xpeak, double *ypeak, int init, int ihist)
{
    int i = init, j;
    bool flag = false;

    while(i+2 < (int)x.size()){
        if((y[i]-y[i+1])*(y[i+1]-y[i+2]) < 0.0 ||
                (y[i] == y[i+1] && y[i+1] != y[i+2])){
            flag =  true;
            for(j = i+1; j >= i-ihist && j > 2; j--){
                if((y[j]-y[j-1])*(y[j-1]-y[j-2]) < 0.0){
                    flag = false;
                    break;
                }
            }
            for(j = i+1; flag && j <= i+ihist && j+2 < (int)x.size(); j++){
                if((y[j]-y[j+1])*(y[j+1]-y[j+2]) < 0.0){
                    flag = false;
                    break;
                }
            }
            if(flag){
                break;
            }
        }
        i++;
    }
    if(!flag) return -1;
    *ypeak = parabloic_peak(xpeak, x[i], x[i+1], x[i+2], y[i], y[i+1], y[i+2]);
    return i+1;
}

void get_stats(vector<double> &x, int ndata, double *mean, double *sigma)
{
    double mntmp = 0.0;
    for(int n = 0; n < ndata; n++){
        mntmp += x[n];
    }
    mntmp /= (double)ndata;
    if(mean != nullptr){
        *mean = mntmp;
    }
    if(sigma != nullptr){
        *sigma = 0.0;
        for(int n = 0; n < ndata; n++){
            *sigma += pow(x[n]-mntmp, 2.0);
        }
        *sigma = sqrt((*sigma)/(double)ndata);
    }
}

void get_id_field_general(double zorg, int N, double lu0, 
    vector<double> Kxy[], vector<double> deltaxy[], double ratio[], double berr[],
    bool isfoc[], bool isssym, bool isendmag, double xyz[], double Bxyz[])
{
    double lu, Bp, zcenter, byz[2], r;
    bool isf;
    Bxyz[0] = Bxyz[1] = Bxyz[2] = 0;
    for(int j = 0; j < 2; j++){
        for (int k = 1; k < Kxy[j].size(); k++){
            if (Kxy[j][k] != 0 || k == 1){
                lu = lu0/(double)k;
                r = ratio == nullptr ? 1.0 : ratio[j];
                Bp = Kxy[j][k]/(COEF_K_VALUE*lu)*r;
                if(k == 1 && berr != nullptr){
                    Bp += berr[j];
                }
                zcenter = zorg-deltaxy[j][k]*lu/PI2;
                isf = isfoc == nullptr ? false : isfoc[j];
                get_ideal_field_2d(isf, xyz[2], xyz[j], 
                    Bp, lu, k*N, zcenter, byz, 0.0, isssym, isendmag);
                Bxyz[j] += byz[0];
                Bxyz[2] += byz[1];
            }
        }
    }
}

#define RESERVES 1000

void trim(string &str)
{
    size_t ini = str.find_first_not_of(" ");
    if(ini == string::npos){
        str = "";
        return;
    }
    size_t fin = str.find_last_not_of(" ");
    str = str.substr(ini, fin-ini+1);
}

int separate_items(string &input, vector<string> &items, string delimiter, bool skipempty)
{
    size_t ini, fin;
    string item, fmt = " ,;:\t\r\n";
    int nitems = 0;

    if(delimiter != ""){
        fmt = delimiter;
    }

    fill(items.begin(), items.end(), "");

    if(skipempty){
        ini = input.find_first_not_of(fmt, 0);
    }
    else{
        ini = 0;
    }
    while(ini != string::npos) {
        if(skipempty){
            fin = input.find_first_of(fmt, ini);
        }
        else{
            fin = input.find(fmt, ini);
        }
        if(fin == string::npos){
            item = input.substr(ini);
        }
        else{
            item = input.substr(ini, fin-ini);
        }
        nitems++;
        if(items.size() < nitems){
            items.resize(nitems+RESERVES, "");
        }
        items[nitems-1] = item;
        if(fin == string::npos){
            break;
        }
        if(skipempty){
            ini = input.find_first_not_of(fmt, fin+1);
        }
        else{
            ini = fin+1;
        }
    };

    return nitems;
}

bool contains(string item, string label)
{
    return item.find(label) != string::npos;
}

void natural_usrc(double id_length, double wave_length, double *div, double *size)
{
    if(div != nullptr){
        *div = sqrt(wave_length/id_length/2.0);
    }
    if(size != nullptr){
        *size = sqrt(2.0*id_length*wave_length)/4.0/PI;
    }
}

void natural_wsrc(double lu_m, int N, double Kx, double Ky, 
    double gamma, double u, double *size, double *div)
{
    natural_wdiv(Kx, Ky, gamma, u, div);

    double A, B, xi, xid;
    A = 0.0194*pow(fabs(Kx), 2.25)+0.283;
    B = 0.14-0.269/(1.0+exp((Kx-1.17)/0.179));
    xi = Ky/gamma*A*tanh(pow(u, B));
    xid = div[0];
    size[0] = lu_m*sqrt(xi*xi+(double)(N*N)*xid*xid/12.0);

    double eta, etad;
    eta = 8.89e-2/Ky/sqrt(u)/gamma;
    etad = div[1];
    size[1] = lu_m*sqrt(eta*eta+(double)(N*N)*etad*etad/12.0);
}

void natural_wdiv(double Kx, double Ky, double gamma, double u, double *div)
{
    double A, B;
    A = 0.0863*pow(fabs(Kx), 2.13)+0.633;
    B = 0.22-0.544/(1.0+exp((Kx-1.07)/0.211));
    div[0] = Ky/gamma*A*tanh(pow(u, B));
    div[1] = sqrt(0.356/u+Kx*Kx)/gamma;
}

void get_chirp(double GDD, double pwdith, double *pstretch, double *alpha)
{
    *pstretch = sqrt(hypotsq(1.0, GDD/2.0/pwdith/pwdith));
    *alpha = 0.5/(*pstretch)/pwdith/pwdith;
    *alpha = GDD/2.0*(*alpha)*(*alpha);
}

double round(double value0, int prec, bool islower)
{
    if(value0 == 0){
        return 0;
    }
    double value = fabs(value0);
    double ndigit = floor(log10(value))-prec;
    double scale = pow(10, ndigit);
    if(islower){
        value = floor(value/scale);
    }
    else{
        value = ceil(value/scale);
    }
    value *= scale;
    return (value0 > 0 ? 1 : -1)*value;
}

void interpolant2d(
    int points, double Wp, double dgrid, int hmesh, double *delta, int *index)
{
    if(points == 1){
        *index = 0;
    }
    else if(fabs(Wp)/1.001 > dgrid*hmesh){
        *index = -1;
    }
    else{
        if(points > 2){
            *index = (int)floor(Wp/dgrid+0.5);
            *index = max(-hmesh+1, *index);
        }
        else{
            *index = (int)floor(Wp/dgrid);
        }
        *index = min(hmesh-1, *index);
        *delta = Wp/dgrid-(*index);
        *index += hmesh;
        if(points > 2){
            (*index)--;
        }
    }
}

void setinterpolant(int points, double delta, vector<double> &a)
{
    if(points == 2){
        a[0] = 1-delta; a[1] = delta;
    }
    else if(points == 3){
        double del2 = delta*delta;
        a[0] = (del2-delta)/2;
        a[1] = 1-del2;
        a[2] = (del2+delta)/2;
    }
}

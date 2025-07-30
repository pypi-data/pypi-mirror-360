#ifndef common_h
#define common_h

#include <fstream>
#include <vector>
#include <utility>
#include "picojson.h"

using namespace std;

template <class T>
T vectorsum(vector<T> &vec, int ndata)
{
    T sum = vec[0];
    ndata = ndata < 0 ? (int)vec.size() : ndata;
	for(int n = 1; n < ndata; n++){
        sum = sum+vec[n];
    }
    return sum;
}

template <class T>
void create_heap(vector<double> &x, vector<vector<T>> &y, int n, int root, bool isascent)
{
    int largest = root;
    int l = 2*root + 1;
    int r = 2*root + 2;

    if(l < n &&
        ((isascent && x[l] > x[largest]) || (!isascent && x[l] < x[largest]))
        ){
        largest = l;
    }
    if(r < n &&
        ((isascent && x[r] > x[largest]) || (!isascent && x[r] < x[largest]))
        ){
        largest = r;
    }

    if(largest != root){
        swap(x[root], x[largest]);
        for(int j = 0; j < y.size(); j++){
            swap(y[j][root], y[j][largest]);
        }
        create_heap(x, y, n, largest, isascent);
    }
}

template <class T>
void sort(vector<double> &x, vector<vector<T>> &y, int n, bool isascent)
{
    for(int i = n/2 - 1; i >= 0; i--){
        create_heap(x, y, n, i, isascent);
    }

    for(int i = n-1; i>=0; i--){
        swap(x[0], x[i]);
        for(int j = 0; j < y.size(); j++){
            swap(y[j][0], y[j][i]);
        }
        create_heap(x, y, i, 0, isascent);
    }
}

template <class T>
void sort(vector<double> &x, vector<T> &y, int n, bool isascend)
{
    vector<vector<T>> yv(1);
    yv[0] = y;
    sort(x, yv, n, isascend);
    y = yv[0];
}

template <class T>
void RecursiveSwap(vector<T> &yv, vector<int> &index)
{
    int ndata = (int)index.size();
    vector<bool> done(ndata, false);
    for(int n = 0; n < ndata; n++){
        if(index[n] == n){
            continue;
        }
        int curr = n;
        while(!done[curr] && !done[index[curr]]){
            done[curr] = true;
            swap(yv[curr],  yv[index[curr]]);
            curr = index[curr];
        }
    }
}

template <class T>
T minmax(vector<T> &vec, bool ismax)
{
    T r = vec[0];
	for(int n = 1; n < vec.size(); n++){
        if(ismax){
            r = r < vec[n] ? vec[n] : r;
        }
        else{
            r = r > vec[n] ? vec[n] : r;
        }
    }
    return r;
}

template <class T>
vector<T>& operator += (vector<T> &vec, const T &t) {
	for(T &val : vec){
		val += t;
    }
	return vec;
}

template <class T>
vector<T>& operator += (vector<T> &v1, vector<T> &v2) {
	for(size_t n = 0; n < v1.size(); n++){
		v1[n] += v2[n];
    }
	return v1;
}

template <class T>
vector<T>& operator -= (vector<T> &vec, const T &t) {
	for(T &val : vec){
		val -= t;
    }
	return vec;
}

template <class T>
vector<T>& operator -= (vector<T> &v1, vector<T> &v2) {
	for(size_t n = 0; n < v1.size(); n++){
		v1[n] -= v2[n];
    }
	return v1;
}

template <class T>
vector<T>& operator *= (vector<T> &vec, const T &t) {
	for(T &val : vec){
		val *= t;
    }
	return vec;
}

template <class T>
vector<T>& operator /= (vector<T> &vec, const T &t) {
	for(T &val : vec){
		val /= t;
    }
	return vec;
}

template <class T>
void PrintDebugItems(ofstream& ofs, vector<T> &item, string separator = "\t")
{
	if(ofs.is_open() == false){
		return;
	}
	for(int j = 0; j < item.size(); j++){
        if(j > 0){
            ofs << separator;
        }
		ofs << item[j];
	}
	ofs << endl;
}

void PrintDebugItems(ofstream& ofs, double x, vector<double> &y);
void PrintDebugPair(ofstream& ofs, vector<double> &x, vector<double> &y, int nlines);
void PrintDebugCols(ofstream& ofs, vector<double> &x, vector<vector<double>> &y, int nlines);
void PrintDebugRows(ofstream& ofs, vector<double> &x, vector<vector<double>> &y, int nlines, double scale = 1.0);
void PrintDebugFFT(ofstream& ofs, double dx, double *y, int nfft, int nlimit, bool isinv, double scale = 1.0);

inline void complex_product(double a[], double b[], double c[])
{
    c[0] = a[0]*b[0]-a[1]*b[1];
    c[1] = a[0]*b[1]+a[1]*b[0];
}
inline void multiply_complex(double *re, double *im, double b[])
{
    double dummy;
    *re = (dummy = *re)*b[0]-(*im)*b[1];
    *im = dummy*b[1]+(*im)*b[0];
}

inline void multiply_complex(double a[], double b[])
{
    double dummy;
    a[0] = (dummy = a[0])*b[0]-a[1]*b[1];
    a[1] = dummy*b[1]+a[1]*b[0];
}

double fft_window(int n, int nfft, int nmesh, int noffset);
void mpi_steps(int i, int j, int processes,
	vector<int>* steps, vector<int>* inistep, vector<int>* finstep);
inline int get_mpi_rank(int index, int processes, vector<int> &inistep, vector<int> &finstep)
{
    int currrank;
    for(currrank = 0; currrank < processes; currrank++){
        if(index >= inistep[currrank] && index <= finstep[currrank]){
            break;
        }
    }
    return currrank;
}

double hypotsq(double x, double y);
double hypotsq(double x, double y, double z);
double hypotsq(double x[], int ndim);
void stokes(double* fx, double* fy, vector<double>* s);
void stokes(vector<double> &fd);
void* realloc_chk(void* ptr, int size);
double simple_integration(int npoints, double dx, vector<double> &y);
int fft_index(int index, int nfft, int idir);
int fft_number(int ndata, int fftlevel);
double errf(double x);
double errfinv(double y);
void fresnel_integral(double x0, double *C, double *S);
double sinc(double x);
double sincsq(double x);
double sinfunc(int M, double x, bool issq = true);

double wave_length(double ep);
double wave_number(double ep);
double photon_energy(double wavelength);

void get_EMF_variables(double cE, double betaxy[], double B[], double xy[]);
bool get_2d_matrix_indices(double xy[], 
    double *valrange, double *inirange, double *delta, int *mesh, int index[], double dresxy[]);
double coshyper(double x);
double sinhyper(double x);
void get_ideal_field_2d(bool isfoc, double z, double xy, double Bp, double lu, int N, 
    double zorg, double *byz, double Iferr, bool isoddpole, bool isendcorr);

void unit_matrix(int dim, vector<vector<double>> &M);
void csd_matrix(double cs, double csd, double ss, double ssd, double ds, double dsd,
    vector<vector<double>> &M);
void multiply_matrices(vector<vector<double>> &M1, vector<vector<double>> &M2,
    vector<vector<double>> &M3);
bool inverse_matrix(vector<vector<double>> &M, vector<vector<double>> &Minv);

int SearchIndex(int nsize, bool isreg, vector<double> &xarr, double x);

double lininterp2d(vector<vector<double>> &f, double dindex[]);
double lininterp(double t, double t0, double t1, double e0, double e1);
double lagrange2d(vector<vector<double>> &f, double dindex[], int *nmaxp);
int get_index4lagrange(double x, vector<double> &xa, int size);
double lagrange(double t,
    double t0, double t1, double t2, double e0, double e1, double e2);
double parabloic_peak(double *xpeak,
        double x0, double x1, double x2, double f0, double f1, double f2);
int get_parabolic_peak(vector<double> &x, vector<double>& y,
    double *xpeak, double *ypeak, int init, int ihist);
void get_stats(vector<double> &x, int ndata, double *mean, double *sigma);

void get_id_field_general(
    double zorg, int N, double lu0, vector<double> Kxy[], vector<double> deltaxy[],
    double ratio[], double berr[], bool isfoc[], bool isssym, bool isendmag, double xyz[], double Bxyz[]);
void trim(string &str);
int separate_items(string &input, vector<string> &items, string delimiter = "", bool skipempty = true);

bool contains(string item, string label);

void natural_usrc(double id_length, double wave_length, double *div, double *size);
void natural_wsrc(double lu_m, int N, double Kx, double Ky, 
    double gamma, double u, double *size, double *div);
void natural_wdiv(double Kx, double Ky, double gamma, double u, double *div);
void get_chirp(double GDD, double pwdith, double *pstretch, double *alpha);
double round(double value0, int prec, bool islower);
void interpolant2d(int points, double Wp, double dgrid, int hmesh, double *delta, int *index);
void setinterpolant(int points, double delta, vector<double> &a);

#endif

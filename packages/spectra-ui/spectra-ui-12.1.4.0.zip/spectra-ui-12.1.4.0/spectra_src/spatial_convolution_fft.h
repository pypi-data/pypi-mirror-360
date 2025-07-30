#ifndef spatial_convolution_fft_h
#define spatial_convolution_fft_h

#include <vector>
#include <vector>
#include "fast_fourier_transform.h"
#include "function_digitizer.h"
#include "interpolation.h"
#include "spectra_solver.h"

#define SPATIAL_CONVOLUTION_ALONGX 0
#define SPATIAL_CONVOLUTION_ALONGY 1
#define SPATIAL_CONVOLUTION_MESH 2

using namespace std;

class SpatialConvolutionFFTBase
    : public FunctionDigitizer
{
public:
    virtual ~SpatialConvolutionFFTBase();
    void SetCalcStatusPrintFFT(int targetlayer, PrintCalculationStatus *status);
    void ArrangeVariables(bool isspline, int nitems, int nborder,
        double eps, int level, double sigma, double sigmalimit,
        double xyini, double dxy, int nxy, double dxyspl, bool posonly, 
        int rank = 0, int mpiprocesses = 1, MPIbyThread *thread = nullptr);
    void RunFFTConvolution(vector<vector<double>> *vconv, 
        string debug = "", string debugfft = "", string debugaft = "", string debugspl = "");
    virtual void SingleDensity1D(double xy, vector<double> *density) = 0;
    void GetXYArray(vector<double> *xy, double fcorr);
    double Function4Digitizer(double xy, vector<double> *density);
	virtual void GetFFTedProfileAt(double kxy, double *ftre, double *ftim);
    int GetIndexOrigin(){return m_orgidx;}

private:
    void f_GetSpline(double xy, vector<double> *density);
    void f_AssignSplineData(string debug);
    void f_AllocateData4Convolution(double dxy, double offset, int nfft, 
        string debug = "", bool isappend = false, string debufft = "");
    vector<double> m_vtmp;
    vector<double *> m_wsdata;
    vector<double *> m_wsfftold;
    vector<vector<double>> m_vconvold;
    FastFourierTransform *m_fft;
    vector<Spline> m_denspline;
	vector<double> m_denspoint;
	bool m_splassign;
    int m_nfftini;
    int m_nborder;
    int m_allocsize;
    int m_ninitspline;
    double m_dxy;
    double m_dxyini;
    double m_dkxy;
    double m_eps;
    double m_epspline;
    double m_xymin;
    double m_xymax;

	int m_rank;
	int m_mpiprocesses;
    MPIbyThread *m_cvthread;
	vector<int> m_mpisteps;
	vector<int> m_mpiinistep;
	vector<int> m_mpifinstep;

protected:
    void f_RunConvolutionSingle(int nfft, bool isrestore = false, 
        string debugfft = "", string debugaft = "");
    vector<double> m_xyarray;
    vector<double *> m_wsfftnext;
    int m_nitems;
    int m_nxy;
    int m_nfft;
	int m_nskip;
    int m_offset;
    int m_itemrefer;
    double m_sigma;
    int m_minrepeatfft;
    int m_layer;
    int m_orgidx;
    bool m_cancelspfft;
    bool m_usespline;
    bool m_posonly;
    PrintCalculationStatus *m_statusfftbase;
};

class SpatialConvolutionFFT1Axis
    : public SpatialConvolutionFFTBase
{
public:
    SpatialConvolutionFFT1Axis(int type, bool ismesh, SpectraSolver &spsolver);
    virtual void SingleDensity1D(double x, vector<double> *density);
    virtual void SingleDensity2D(double *xy, vector<double> *density) = 0;
    void SetXYFixPoint(double xy);
protected:
    double m_xyfix[2];
    int m_type;
};

class DensityFixedPoint;

class SpatialConvolutionAlongXYAxis
    : public SpatialConvolutionFFT1Axis
{
public:
    SpatialConvolutionAlongXYAxis(int type, bool ismesh, 
        SpectraSolver &spsolver, DensityFixedPoint *densfix);
    virtual void SingleDensity2D(double *xy, vector<double> *density);
	virtual void GetFFTedProfileAt(double kxy, double *ftre, double *ftim);
	void SetFFTSpline(Spline *re, Spline *im);
private:
    DensityFixedPoint *m_densfix;
	Spline *m_fftrespl;
	Spline *m_fftimspl;
};

class SpatialConvolutionFFT
    : public SpatialConvolutionFFTBase, public SpectraSolver
{
public:
    SpatialConvolutionFFT(
        int type, SpectraSolver &spsolver, DensityFixedPoint *densfix, int layer,
		int rank = 0, int mpiprocesses = 1);
    virtual ~SpatialConvolutionFFT();
    virtual void SingleDensity1D(double xy, vector<double> *density);
    void Run2DConvolution();
    void GetXYArrays(vector<double> *xarray, vector<double> *yarray);
    void GetValues(vector<vector<vector<double>>> *zmatrix);
private:
    SpatialConvolutionAlongXYAxis *m_spconv;
    DensityFixedPoint *m_densfix;
    bool m_xfirst;
    bool m_isyonly;
    int m_mesh1st;
    int m_mesh2nd;
    int m_nitems1st;
    int m_nitemspoint;
	int m_layer;
    vector<vector<double>> m_vconvtmp;
    vector<vector<double>> m_vconv;
	Spline m_prjrespl;
	Spline m_prjimspl;
	Spline m_xyrespl;
	Spline m_xyimspl;
};

#endif

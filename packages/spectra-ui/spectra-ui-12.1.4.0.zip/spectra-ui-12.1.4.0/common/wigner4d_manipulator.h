#ifndef wigner4d_manipulator_h
#define wigner4d_manipulator_h

#include <algorithm>
#include <limits.h>
#include <vector>
#include <string>
#include "interpolation.h"
#include "spectra_solver.h"
#include "fast_fourier_transform.h"
#include "mpi_by_thread.h"

using namespace std;

enum {
	WignerType4D = 0,
	WignerType2DX,
	WignerType2DY,
	NumberWignerTypeForBinary,

	WignerUVPrmU = 0,
	WignerUVPrmV,
	WignerUVPrmu,
	WignerUVPrmv,
	NumberWignerUVPrm,

	Wig4DSolveModeX = 0,
	Wig4DSolveModeY,
	Wig4DSolveSrcAdjX,
	Wig4DSolveSrcAdjY,
	Wig4DRestrPmax,
	Wig4DRestrLowerLimit,
	Wig4DRestrSuffCoeff,
	Wig4DRestrSuffError,
	Wig4DRestrSuffEfield,
	Wig4DRestrSuffEfieldBin,
	Wig4DRestrSuffSWigner,
	Wig4DFprofXDiv,
	Wig4DFprofYDiv,
	NumberWig4DSolvePrms,

	Wig4OReconOptDumpCoef = 0,
	Wig4OReconOptCompareDev,
	Wig4OReconOptEfield,
	Wig4OReconOptEfieldBin,
	Wig4OReconOptWigner,
	Wig4OReconOptComparePlot,
	Wig4OReconOptReuse,
	NumberWig4OReconOpt,

	WigErrorCorrelation = 0,
	WigErrorDeviation,
	WigErrorCoherent,
	NumberWigError,

	Wig4DResSeparable = 0,
	Wig4DResDegCohTotal,
	Wig4DResDegCohX,
	Wig4DResDegCohY,
	NumberWig4DRes,
};

class Wigner4DManipulator
{
public:
	Wigner4DManipulator();
	void SetAccLevel(int xlevel, int xplevel, double eps, double dfringe);
	bool LoadData(string calctype, 
		vector<vector<double>> *vararray, vector<double> *data);
	bool LoadData(picojson::object &obj);
	bool Initialize();
	void RetrieveData(vector<vector<double>> &vararray, vector<double> &data);

	void SetWavelength(double wavelength);
	double GetWavelength(){return m_lambda;}
	void GetXYQArray(int jxy, vector<double> &xy, vector<double> &q);
	int GetTotalIndex(int indices[], int *steps = nullptr);
	double GetValue(int indices[]);
	void GetSliceValues(int jxy, int *posidx, vector<vector<double>> &data);
	void PrepareSpline(int xyposidx[]);
	double GetInterpolatedValue(int xyposidx[], double xyp[], bool islinear = true);
	double GetMaxValue(){return m_maxval;}
	void GetCoherenceDeviation(double *degcoh, double *devsigma, vector<double> &data);
	int GetType(){return m_type;}
	double GetPhaseVolume();
	void GetVarIndices(vector<int> &indices);
	void GetProjection(vector<double> &fdens);
	void GetAngularProfile(vector<double> &fdensa);
	void GetBeamSizeAt(double Z, double *size);
	void Transfer(double Z, double *dxytgt, PrintCalculationStatus *calcstats = nullptr, 
		double *aptmin = nullptr, double *aptmax = nullptr, double *dfringe = nullptr);
	void GetCSD(double sigma[], vector<vector<double>> &vararray, 
		vector<vector<double>> &F, vector<vector<vector<vector<double>>>> *CSD,
		PrintCalculationStatus *calcstats = nullptr);
	bool IsActive(int j){return m_active[j];}
	void GetMeshPoints(vector<int> &hmesh);
	void GetDeltaZ(double deltaZ[]);

	void OpticalElement(double Z, double *flen, double fringe,
		vector<vector<double>> &position, vector<vector<double>> &aperture,
		PrintCalculationStatus *calcstats = nullptr);
	void GetWaistPosition(double rho[], double Zwaist[]);
	void GetWignerAtWaist(double Z, double finv[],
		vector<vector<double>> &vararray, vector<double> &data,
		PrintCalculationStatus *calcstats = nullptr);
	void GetWignerAtWaistTest(double Z);
	void SetMPI(int procs, int rank, MPIbyThread *thread);
	void SetRay(bool spherical);
	void SetSourceWigner(vector<double> &Zwaist, vector<double> &sigma,
		vector<vector<double>> &vararray, vector<double> &wigner, bool isget);

private:
	double f_GetWignerAtZ(double rho[], double var[]);
	void f_GetFFTCSD(int j, int *nfft, double *deltaZ, 
		double *aptmin = nullptr, double *aptmax = nullptr, double fringe = 0, int *anfft = nullptr);
	double f_LoadWS(int ii, int jj,
		int nfft[], int ndim, double *ws, double **ws2, double *deltaZ);
	int f_AllocFFTWS(FastFourierTransform **fft, int nfft[], double **ws = nullptr, double ***ws2 = nullptr);
	void f_SetSlit(double fringe, 
		vector<vector<double>> &position, vector<vector<double>> &aperture);
	void f_InsertSlit(PrintCalculationStatus *calcstats = nullptr);
	void f_CSDOptics(double center[], double deltaZ[], int nfft[],
		vector<double> *wscsd, vector<vector<double>> *wscsd2, bool debug = false);
	double f_GetRectSlit(double fringe[], vector<vector<double>> &border, double xy[]);
	void f_SetGridUV(double *dxytgt, double *aptmin, double *aptmax, double *dfringe);
	void f_GetSigma(double *Zt, double *sigma);
	void f_GetSliceDivergence(double *sigma);
	void f_SetSteps(int *steps, int *mesh);
	void f_SetWindex(int j, double Z,
		int ifin[], int k, int index[], double UV[], double *delta);
	void f_Export(bool killoffset);
	void f_ExportProfile2D();
	void f_ExportWTrans(int jxy, bool killoffset);

	vector<double> m_data;
	vector<vector<double>> m_variables;
	double m_lambda;
	int m_type;
	int m_mesh[NumberWignerUVPrm];
	int m_steps[NumberWignerUVPrm+1];
	double m_delta[NumberWignerUVPrm];
	
	double m_maxval;
	int m_posxy_spl[3];
	vector<vector<double>> m_z;
	Spline2D m_xypspl2d;

	int m_ifin[NumberWignerUVPrm];
	vector<double> m_a[NumberWignerUVPrm];

	int m_hmesh[NumberWignerUVPrm];
	int m_meshZ[NumberWignerUVPrm];
	int m_hmeshZ[NumberWignerUVPrm];
	int m_meshfft[NumberWignerUVPrm];
	double m_deltaZ[NumberWignerUVPrm];
	double m_ndeltaZ[NumberWignerUVPrm];
	double m_rini[NumberWignerUVPrm];
	double m_rfin[NumberWignerUVPrm];

	double m_sigmaorg[NumberWignerUVPrm];
	double m_sigmaZ[2];
	double m_sdiv[2];
	double m_DeltaUV[2];
	double m_Deltauv[2];

	vector<int> m_varidx;
	bool m_active[2];
	vector<double> m_Zborder[2];
	bool m_isfar[2];
	double m_Zwaist[2]; // virual waist position
	double m_Zt[2]; // distance to travel from the virtual waist

	// aperture
	vector<vector<vector<double>>> m_border;
	double m_dfringe[2];
	double m_aptmin[NumberWignerUVPrm];
	double m_aptmax[NumberWignerUVPrm];
	double m_apteps;
	int m_napt;
	int m_aptpoints;

	// numerical conditions
	int m_acclevel;
	int m_csdlevel;

	vector<vector<vector<vector<double>>>> m_dataZ;

	// MPI settings
	int m_nproc;
	int m_rank;
	MPIbyThread *m_thread;
};

class WignerPropagator :
	public SpectraSolver
{
public:
	WignerPropagator(SpectraSolver &spsolver);
	void Propagate(vector<string> &subresults, vector<string> &categories);
private:
	void f_SetGrid(vector<vector<double>> &vararray);
	void f_SliceCSD(int zstep, vector<vector<double>> &F, 
		vector<vector<vector<vector<double>>>> *CSD);
	void f_ScatterCSD(int zstep, bool single);
	void f_GetProfile(int zstep,
		vector<vector<double>> &vararray, vector<double> &Profile);
	void f_GetCSD(int zstep,
		vector<vector<double>> &vararray, vector<vector<double>> *CSD);

	void f_GetGamma(int zstep, int jxy,
		vector<double> &UV, vector<double> &uv, vector<vector<double>> &CSD);

	void f_GetValues(int zstep, int jxy, int reim,
		vector<vector<double>> &vararray, vector<double> &CSD);
	Wigner4DManipulator m_wigmanip;
	vector<vector<vector<double>>> m_vararray;
	vector<vector<vector<vector<vector<vector<double>>>>>> m_CSD;
	vector<vector<vector<double>>> m_xyWig;
	vector<vector<double>> m_Wig;
	vector<vector<int>> m_hmesh;
	vector<vector<int>> m_mesh;
	vector<double> m_SigmaZ[2];
	bool m_isxy[2];
	int m_type;
};

#endif
#ifndef spectra_solver_h
#define spectra_solver_h

#include <chrono>
#include "spectra_config.h"
#include "beam_convolution.h"
#include "mpi_by_thread.h"

class BeamConvolution;
class PrintCalculationStatus;
class FilterOperation;
class Spline;
class MPIbyThread;

//--------->>>>>>>
//#define _CPUTIME

enum {
	WignerFuncType4DX = 0,
	WignerFuncType4DY,
	WignerFuncType2DX,
	WignerFuncType2DY,
	WignerFuncTypeXY,
	WignerFuncTypeXpYp,

	WignerIntegOrderU = 0,
	WignerIntegOrderV,
	WignerIntegOrderUVcv,

	SrcVarX = 0,
	SrcVarY,
	SrcVarXp,
	SrcVarYp,
	NumberSrcVar
};

class SpectraSolver
	: public SpectraConfig
{
public:
	SpectraSolver(SpectraConfig &spconf, int thid = 0, MPIbyThread *thread = nullptr);
	void ApplyConditions(bool setconv = true);
	void DeleteInstances();
	double GetE1st(double gt = 0.0);
	double GetKperp(double e1st);
	double GetCriticalEnergy(double *Bptr = nullptr);
	double GetEspreadRange();
	void SetEnergyPoints(bool isfix = false, bool forcemesh = false);
	void GetEnergyPoints(vector<double> &energy){energy = m_eparray;}
	void ResetEnergyPrms(double emin, double emax);
	void SetObservation(bool setconv = true);
	virtual void SetPowerLimit(){}
	void SetTimePoints();
	void GetSincFunctions(int nh, double epr, vector<double> *snc);
	void MultiplySincFunctions(
		vector<double> *fxyin, vector<double> *sn, vector<double> *fxyout);
	double EnergyProfile(double epref, double ep, double deavg = 0);
	double EnergySpreadSigma(double epref = -1.0);
	int GetNumberOfItems();
	void GetEBeamSize(double *size);
	bool IsSmoothSprofile();
	void GetGridContents(int type, bool ismesh, 
		double *xyini, double *dxy, double *dxyspl, int *mesh, int wigtype = -1, bool ism = true);
	void GetSPDConditions(
		vector<vector<double>> &obs, vector<vector<double>> &xyz, vector<vector<double>> &exyz);
	int GetIndexXYMesh(int type);
	void ArrangeMeshSettings(
		vector<vector<double>> &xyrp, vector<vector<double>> &xyobs);
	bool IsPower(){return m_ispower;}
	void GetAccuracySpFFT(double *tol, int *level, double *nglim);
	double GetTotalPowerID();
	double GetFluxCoef(bool isbmtot = false);
	double GetPowerCoef();
	double GetTempCoef(bool forcefield = false);
	double GetFldAmpCoef();
	double GetPConvFactor();
	double GetOrbitRadius();
	double GetAverageFieldSquared(int jxy, bool issec);
	double GetEnergyCoherent(double blen_sec, double frac);
	double GetTypicalBunchLength();
	void GetTypicalDivergence(double *xydiv);
	void GetNaturalSrcDivSize(double ep, double *divxy, 
		double *sizexy, double *SizeSlice = nullptr, double detune = 0, bool qsize = false);
	void GetSrcDivSize(double ep, double *divxy, double *sizexy, 
		double *Divxy, double *Sizexy, double *divrc, 
		double *sizeslice = nullptr, double detune = 0, bool qsize = false);
	void GetDegreeOfCoherence4D(vector<vector<double>> &vararray,
		vector<double> &W, double *separability, double cohdeg[]);
	void GetDegreeOfCoherence2D(vector<vector<double>> &vararray, vector<double> &W, double *cohdeg);
	double GetEpsilonBMWiggler(double ep);
	void GetWignerType(
		vector<int> &wigtypes, vector<vector<int>> &indices);
	bool IsMonteCarlo();

	virtual void GetSpectrum(
		vector<double> &energy, vector<vector<double>> &flux, 
		int layer, int rank, int mpiprocesses,
		vector<string> &subresults, vector<string> &categories);
	virtual void GetSpatialProfile(
		vector<vector<double>> &xy, vector<vector<vector<double>>> &dens,
		int layer, int rank, int mpiprocesses,
		vector<string> &subresults, vector<string> &categories);
	virtual void GetSurfacePowerDensity(
		vector<vector<double>> &obs, vector<double> &dens,
		int layer, int rank, int mpiprocesses);
	virtual void GetWignerFunction(
		vector<vector<double>> &XY, vector<double> &W,
		int layer, int rank, int mpiprocesses);
	virtual void GetFixedPoint(vector<double> &values, 
		int layer, int rank, int mpiprocesses);

	void GetOutputItemsIndices(vector<int> &itemindices);

	void RunSingle(int &dimension,	
		vector<string> &titles, vector<string> &units,
		vector<vector<double>> &vararray, vector<vector<double>> &data,
		vector<string> &details, vector<int> &nvars, 
		vector<string> &subresults, vector<string> &categories);

	void GetSuppleData(vector<string> &titles, vector<double> &data);

	void MeasureTime(int index = -1);
	virtual void GetMeasuredTime(
		vector<string> &label, vector<double> &rtime, bool appendn = true);
	MPIbyThread *GetThread(){ return m_thread; }

protected:
	void f_SetAutoRange();
	void f_SetSuppleData(string calctype, double separability, double cohdeg[]);
	void f_ToStokes(vector<vector<double>> &xy, vector<vector<vector<double>>> &dens);
	double f_GetE1stBase(double Kgt2 = 0.0);
	void f_GetTitles(vector<string> &titles, vector<string> &units);
	void f_GatherMPI(int nitems, 
		vector<vector<double>> &items, int rank, int mpiprocesses);
	void f_GetKrange(double Krange[]);
	double f_LoadParticleData(const string filename);

	vector<double> m_eparray;
	vector<double> m_tarray;

	double m_AvCurr;
	double m_gamma2;
	double m_gtcenter;
	double m_gtmax;
	double m_gttypical;
	double m_center[2];
	double m_xyfar[2];
	double m_segphase[3];
	double m_Ldrift;
	double m_pslip;
	double m_fcoef_obspoint;
	double m_fixep;
	double m_slitapt[2];
	double m_slitr[2];
	double m_bunchelectrons;

	bool m_isgaussbeam;
	bool m_iscurrprof;
	bool m_isEtprof;
	bool m_isparticle;

    bool m_isdefault;
    bool m_issymmetric;
    bool m_isnatfoc[2];
	bool m_isskipespread;
	bool m_customwiggler;

	bool m_isfar;
	bool m_circslit;
	bool m_rectslit;
	bool m_totalslit;
	bool m_ispower;
	bool m_isfldamp;
	bool m_istime;
	bool m_isrespow;
	bool m_isenergy;
	bool m_isvpdens;
	bool m_isfilter;
	bool m_issrcpoint;
	bool m_isefield;
	bool m_iscoherent;
	bool m_isfixepitem;
	bool m_isfluxs0;
	bool m_isfluxamp;

	bool m_iszspread;

	int m_spfftlevel;
	double m_tol_spint;
	BeamConvolution *m_bmconv;
	PrintCalculationStatus *m_calcstatus;
	Spline m_eprofile[2]; 
	// 0: energy profile, 1: its integral over eta

	vector<double> *m_partbuf[6];
	int m_nparticle;

	vector<string> m_suppltitle;
	vector<double> m_suppldata;

	// fel amplifier
	bool m_isfel;
	double m_d_eta;
	double m_epmax_fel;
	double m_epmin_fel;
	double m_seedtwin;

	// thread
	MPIbyThread *m_thread;

	// CPU time
	chrono::system_clock::time_point m_rtime[2];
	vector<double> m_cputime;
	vector<string> m_rlabel;
	int m_nrep;
};

#endif

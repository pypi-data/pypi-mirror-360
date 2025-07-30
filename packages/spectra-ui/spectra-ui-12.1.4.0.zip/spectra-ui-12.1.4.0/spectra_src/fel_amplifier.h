#pragma once

#include "flux_density.h"
#include "particle_generator.h"
#include "coherent_radiation.h"

class SeedLight;

class FELAmplifier :
	public CoherentRadiationBase
{
public:
	FELAmplifier(
		SpectraSolver &spsolver, Trajectory *trajectory, FilterOperation *filter, int fellayer);
	~FELAmplifier();
	void AdvanceSection(int tgtsec);
	virtual void GetValues(double *xyobsin, vector<double> *values);
	int GetSections(){return m_nsections;}
	void PrepareFinal();
	void GetBunchFactor(vector<double> &energy, 
			vector<double> &zstepI, vector<vector<vector<double>>> &bunchf);
	void GetBunchInf(
		vector<double> &currt,
		vector<double> &tgrid,
		vector<double> &eta,
		vector<double> &energy,
		vector<double> &zstepI,
		vector<double> &zstep,
		vector<vector<double>> &currI,
		vector<vector<double>> &jEt,
		vector<vector<double>> &tprof,
		vector<vector<vector<double>>> &eprof,
		vector<vector<vector<double>>> &bunchf,
		vector<vector<double>> &spectra,
		vector<vector<double>> &pulseE,
		vector<double> &currIR56,
		vector<double> &jEtR56
		);

private:
	int f_GetTotalSteps();
	void f_SetTauRange();
	bool f_SetParticles(int Nmax);
	void f_SetGridPoints(bool init, int spincr, double Deltaxy[]);
	void f_SetAngularGrid(double bmsize[]);
	double f_GetCharge(Particle &particle, double dtE[], bool isnew);
	double f_ElectronNumber(double t);
	double f_ThetaLimit(double explim, int np, double ep);

	void f_AdvanceParticlesSection(int nsec);
	void f_GetBunchFactor(int tgtsection);
	void f_GetRadWaveformPoint(double Zpos, double xyobs[], double torg);
	void f_GetRadWaveform(int tgtsection,
		double *xyoffset, double Zobs, double torg, int *zrangelim);
	void f_GetComplexAmpGrid(int tgtsection, double *xyoffset, double Zobs, double torg);
	void f_GetComplexAmpAdv(int tgtsection, double *xyoffset,
		double Zobs, double torg, int *zrangelim, bool spcharge = false);
	void f_ConvoluteEbeamSize(int section, double *xyoffset);
	void f_GetComplexAmpAt(int tgtsection, double xy[], double Zobs, double torg, 
		int *zrangelim = nullptr, double *xyspc = nullptr, double *qxy = nullptr);
	void f_GetTemporalBF(int nxyindex, bool istime, int tgtsection,
		double xy[], double Zobs, double torg, bool debex = false);
	void f_InverseFFT(string dfile, int dim, bool debex, double tshift = 0);
	void f_SetAmplitudeAng(int tgtsection);
	void f_AddCA(int nsec, int np, int ne, int nq);
	double f_GetPulseEnergyDens(int tgtsection, int np, bool debug);
	void f_GetPulseEnergy(int tgtsection);

	void f_PrintAmpAdv(string filename, double *xyoffset = nullptr);
	void f_BcastFxyCart(vector<int> &inistep, vector<int> &finstep);
	void f_ClearEwFFTbf(int jmax);
	void f_PrintTemp(string filename, double *xyoffset = nullptr, bool iscenter = false, double tslip = 0);
	void f_PrintSpectrum(string filename, int dim);
	string f_GetParticleDataName(int tgtsec);

	vector<SeedLight *> m_seed;
	bool m_bfreuse;
	int m_grank;
	int m_gprocesses;
	int m_dim;

	int m_nsections;
	int m_advsteps;
	double m_dxy[2];
	double m_dxyN[2];
	double m_dphi;
	double m_bmmin[2];
	double m_bmmax[2];
	double m_bmavg[2];

	double m_dt;
	int m_nshalf[2];
	double m_t0;
	int m_fellayer;

	vector<double> m_epbf;
	double m_deFTbf;
	double m_dtaubf;
	int m_nfftbf;
	int m_nfdbf;
	int m_nfftsp[2];
	int m_nshalfm[2];
	int m_nspincr;
	double *m_EwFFTbf[3];
	FastFourierTransform *m_fftbf;
	FastFourierTransform *m_fftsp;
	double **m_fftspws;
	double *m_wssp;
	vector<vector<double>> m_FxyCart[6];
	vector<vector<vector<double>>> m_FbufSec[6];
	Spline m_FbufSpl[2];

	vector<Particle> m_particles;
	vector<double> m_charge;
	Particle m_reference;
	int m_Nparticles;
	double m_bunchE;

	vector<double> m_tgrid;
	int m_hntgrid;
	int m_hnxymax[2];
	vector<vector<double>> m_xygrid;
	vector<double> m_xygridrad[2];
	vector<vector<vector<double>>> m_FxyGrid[6];
	vector<vector<vector<vector<double>>>> m_EtGrid;
	vector<double> m_qgrid[2];
	double m_dq[2];
	int m_nsq[2];
	double m_Zorg;
	double m_torg;
	vector<vector<vector<double>>> m_FwGrid[4]; // [phi][energy][theta]
	vector<vector<vector<float>>> m_FwGridbf[4]; // [phi][energy_bf][theta]
	vector<vector<int>> m_nqlim; // [phi][energy]
	vector<vector<int>> m_nqlimbf; // [phi][energy_bf]
	vector<vector<double>> m_qstore; // [phi][theta]

	vector<vector<int>> m_secidx;
	vector<int> m_pEsects;
	vector<double> m_zorbit;
	vector<vector<double>> m_xyref;
	vector<vector<double>> m_qxyref;
	vector<double> m_Zmid;
	vector<double> m_Zex;
	vector<double> m_tstep;
	vector<double> m_tmid;
	vector<double> m_tzorb;
	vector<vector<double>> m_bmsize;

	vector<int> m_netgt;
	vector<int> m_netgtbf;

	vector<double> m_currt;
	int m_hncurrt;

	// storage for bunch profile
	vector<vector<vector<double>>> m_curr_j;
	vector<vector<vector<double>>> m_bunchf;
	vector<vector<double>> m_currI;

	// storage for data export
	vector<vector<double>> m_spectra;
	vector<vector<vector<double>>> m_eprof;
	vector<vector<double>> m_tprof;
	vector<vector<double>> m_pulseE;

	// workspace for MPI
	vector<double> m_ws[2];
};

class SeedLight
{
public:
	SeedLight(double pulseE,
		double epcenter, double pulselenFWHM, double srcsizeFWHM,
		double zwaist, double torg, double gdd, double tod);
	SeedLight(DataContainer &datacon, double pulseE, double srcsizeFWHM, double zwaist, double torg);
	void GetAmplitudeS(double ep, double de, double tshift, double zpos, double xy[], double Exy[]);
	void GetAmplitudeA(double ep, double de, double tshift, double zpos, double kxy[], double Exy[]);
	double GetDivergence();

private:
	Spline m_seedspec[2];
	double m_seedrange[2];
	double f_GetAmp(double ep, double de, double tex);
	double f_GetPhase(double ep);
	double m_E0;
	double m_sigmat;
	double m_Epk;
	double m_E0custom;
	double m_epcenter;
	double m_zrayl;
	double m_sigmath;
	double m_sigmaxy;
	double m_torg;
	double m_zwaist;
	double m_d2nd;
	double m_d3rd;
	bool m_iscustom;
};

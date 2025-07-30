#ifndef coherent_radiation_h
#define coherent_radiation_h

#include <complex>
#include "flux_density.h"
#include "interpolation.h"
#include "quadrature.h"
#include "filter_operation.h"
#include "mpi_by_thread.h"

class ParticleGenerator;
class FELAmplifier;

class CoherentRadiationBase
	: public FluxDensity
{
public:
	CoherentRadiationBase(
		SpectraSolver &spsolver, Trajectory *trajectory, FilterOperation *filter);
	void GetInstPowerDensity(double *xyobs, vector<double> *pd);
	void GetInstEfield(double *xyobs, vector<double> *exy);
	void GetFluxDensity(double *xyobs, vector<double> *fd);
	void GetPowerDensity(double *xyobs, vector<double> *pd, FilterOperation *filter = nullptr);
	void GetDensity(int csrlayer,
		double *xyobs, vector<double> *density, 
		int rank = 0, int mpiprocesses = 1);
	int GetNumberofPoints();
	virtual void GetEnergyArray(vector<double> &energy);
	virtual void GetValues(double *xyobsin, vector<double> *values) = 0;

protected:
	FilterOperation *m_filter;
	Trajectory *m_trajectory;
	vector<double> m_ws;
	vector<double> m_fws;
	int m_csrlayer;
	int m_crank;
	int m_cmpiprocesses;

	int m_nfdbase;
	vector<double> m_epbase;

};

class CoherentRadiation
	: public CoherentRadiationBase
{
public:
	CoherentRadiation(SpectraSolver &spsolver, 
		Trajectory *trajectory, FilterOperation *filter);
	virtual ~CoherentRadiation();
	virtual void GetValues(double *xyobsin, vector<double> *values);
	void GetBunchFactorAt(int ne, double ep, double *bdft);

private:
	void f_AllocateEtBF();
	void f_ComputeMacroParticle(double xobs, double yobs);
	void f_ConvluteEt();
	void f_AllocTemporal(bool isdirect);
	void f_GetTemporalProfile(vector<double> *values = nullptr);
	void f_GetEtData(vector<double> *values);
	void f_GetSingleEField(Particle &particle,
		double xobs, double yobs, bool recalcorb, bool allocref);
	void f_SetEt(double **etfft, double **etbuf = nullptr, bool isadd = false);
	void f_SetRz();
	double f_GetTauEdev(double tau, double edev);

	ParticleGenerator *m_particle;
    Spline m_tauvsz;
    Spline m_zvsrz;

	vector<vector<Spline>> m_EtBFspl;
	vector<double> m_eearray;
	vector<OrbitComponents> m_reforb;

	int m_ntaupointsws;
	vector<double> m_tauws;
	vector<vector<double>> m_Etws;

	bool m_isflux;
	double m_nNt;
};

class CoherentRadiationCtrl	: public SpectraSolver, public QSimpson
{
public:
	CoherentRadiationCtrl(SpectraSolver &spsolver, 
		Trajectory *trajectory, FilterOperation *filter);
	virtual ~CoherentRadiationCtrl();
	void GetCohSpatialProfile(int layer,
		vector<vector<double>> *xy, vector<vector<double>> *density, 
		int rank, int mpiprocesses);
	void GetValues(int layer,
		vector<vector<double>> *values, int rank = 0, int mpiprocesses = 1);
    virtual void QSimpsonIntegrand(int layer, double xyrq, vector<double> *density);
	void GetFELData(vector<string> &felresults, vector<string> &feltitles);

private:
	void f_WriteFELResult(string title,
		vector<string> &felresults, vector<string> &feltitles, vector<int> &index, 
		int vardim, vector<vector<double>> &xyvar, vector<vector<vector<double>>> &data);
	CoherentRadiationBase *m_cohbase;
	CoherentRadiation *m_cohrad;
	FELAmplifier *m_fel;
	Spline m_fdspl[4];

	int m_csrlayer;
	double m_varint[2];

	double m_slitbdini[2];
	double m_slitbdfin[2];
	double m_slitorigin[2];
	double m_coef;
	int m_jrepmin;

	int m_nitems;
	int m_npoints;
};

#endif

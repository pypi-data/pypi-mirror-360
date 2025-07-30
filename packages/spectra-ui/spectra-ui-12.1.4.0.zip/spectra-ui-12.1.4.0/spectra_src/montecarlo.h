#ifndef montecarlo_h
#define montecarlo_h

#include "spectra_solver.h"

class ComplexAmplitude;
class Trajectory;
class FluxDensity;
class FilterOperation;
class UndulatorFluxFarField;
class DensityFixedPoint;
class WignerFunctionCtrl;
class SourceProfile;
class ParticleGenerator;
class FastFourierTransform;

class MonteCarlo
	: public SpectraSolver
{
public:
	MonteCarlo(SpectraSolver &spsolver);
	virtual ~MonteCarlo();
	double AllocAndGetError(double nNt);
	void RunMonteCarlo(int layer);

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

private:
	void f_RunSingle(Particle &particle, bool init = false);
	void f_Smoothing();
	void f_EnergyConvolution();
	double f_GetMaxWS(int i);
    void f_DumpCurrent(string debug, Particle *particle = nullptr);
	vector<double> m_ws[2];
	vector<double> m_sum;
	vector<double> m_wstmp;
	vector<vector<double>> m_xyrp;
	vector<vector<double>> m_xyobs;
	vector<vector<double>> m_xyz;
	vector<vector<double>> m_exyz;

	double* m_wsmpi[2];
	int m_ndatatotal;

	ParticleGenerator *m_particle;
	ComplexAmplitude *m_camp;
	Trajectory *m_trajec;
	FilterOperation *m_filter;
	DensityFixedPoint *m_densfix;
	WignerFunctionCtrl *m_wigctrl;
	SourceProfile *m_srcprofile;

	bool m_isfixpoint;
	bool m_issurfacepd;
	bool m_iseconvb;
	int m_nitems;
	int m_obspoints;
	double m_dXYdUV;
	double m_eps;
	vector<double> m_ealloc;

	// parameters for smoothing
	FastFourierTransform *m_smfft;
	double *m_smws1d;
	double **m_smws2d;
	int m_smdim;
	bool m_isaxis;
	int m_nbundle;
	int m_mesh[2];
	int m_smnfft[2];
	int m_smoffset[2];
};

#endif
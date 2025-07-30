#ifndef complex_amplitude_h
#define complex_amplitude_h

#include "function_digitizer.h"
#include "interpolation.h"
#include "spectra_solver.h"
#include "orbit_components_operation.h"

class FluxDensity;
class Trajectory;
class UndulatorFxyFarfield;

class ComplexAmplitude :
	public SpectraSolver, FunctionDigitizer
{
public:
	ComplexAmplitude(SpectraSolver &spsolver);
	void GetEbeam4Wigner(
		double sigmauv[], double sigmaUV[], double alpha[], bool negdiv);
	void Prepare(double ep);
	void GetRangePrms(double hrange[], double dinterv[]);
	double GetSn(double u[], double v[]);
	bool GetExyAmplitude(double uv[], double Exy[]);
	double GetOmegaWiggler(double index, double polarity);
	double GetAprofPrms(int amesh[], double adelta[]);
    virtual double Function4Digitizer(double theta, vector<double> *exy);
	bool IsIdealUnd(){return m_isidealund;}
	bool IsIdealBM(){return m_isidealbm;}
	bool IsIdealSrc(){return !m_noidealsrc;}
	void GetSnPrms(int *N, int *nh, double *Ueps);
	void GetUVSrcPoints(double srcpoints[]);
	double GetConvUV(){return m_dXYdUV;}
	double GetConv_uv(){return m_dqduv;}
	double GetWDFCoef();
	void GetEnergyArray(vector<double> &eparray);
	double GetTargetEnergy(){return m_eptarget;}
	void SetTargetEnergyIndex(int ne){m_netarget = ne;}
	void UpdateParticle(Trajectory *trajec, double edev);
	double GetSrcPointCoef();
	int GetSections(){return (int)m_avgorbits.size();}
	bool IsEsingle(){return m_ismontecarlo;}

private:
	// non-ideal sources
	void f_CreateDataSet(
		double thetamax, int acclevel, FluxDensity *fluxdens, vector<vector<int>> *secidx,
		PrintCalculationStatus *status, int targetlayer);
	bool f_GetAmplitudeNI(int ne, double uv[], double Exy[], int nsec = -1);
	bool f_GetAmplitudeNIParticle(int ne, double uv[], vector<OrbitComponents> &orbits, double Exy[]);

	void f_AssignEFieldUnd(double epsilon, bool issn);
	void f_AssignSn(double uvmax, double epsilon);
	double f_GTmaxU(double epsilon, double *gt2uv, double *hDelta);
	void f_AssignGridConditions(
		int mesh[], double delta[], double *dinterv, double *hrange);
	void f_AssignSnGrid(
		int mesh[], double delta[], double epsilon);
	void f_AssignAngularGrid(double aflux, int mesh[], double delta[]);
	void f_AssignEFieldWiggler(double epsilon, double deltau, bool isbma);
	void f_AssignEFieldBM(double epsilon, double deltau);
	void f_GetBMExyAmpDirect(double epsilon, double uv[], double Exy[]);
	void f_MPI_Bcast_Exy(bool istheta,
		vector<int> &mpiinistep, vector<int> &mpifinstep,
		vector<vector<vector<double>>> &exy);

	// field container
	vector<vector<double>> m_Exy[4]; 
	// 0 = real.x, 1 = imag.x, 2 = real.y, 3 = imag.y
	vector<vector<double>> m_Sn;
	double m_coefExy;
	double m_dqduv;
	double m_dXYdUV;

	// non-ideal sources
	FluxDensity *m_fluxdens;
	vector<vector<double>> m_theta;
	vector<int> m_nqpoints;
	vector<double> m_ExyAxis;
	vector<vector<vector<double>>> m_ExyR;

	vector<vector<double>> m_GxyAxis; // sectioned field, on axis
	vector<vector<vector<vector<double>>>> m_GxyR; // sectioned field, all
	vector<OrbitComponents> m_avgorbits;
	double m_eparticle;

	vector<double> m_eparray;
	double m_csn[2];
	double m_dphi;
	int m_ndivphi;
	int m_ndata;
	int m_necenter;
	int m_tgtitem;
	int m_netarget;
	double m_ecurrtarget;

	// source types, conditions
	bool m_isidealund;
	bool m_isidealbm;
	bool m_noidealsrc;
	bool m_ismontecarlo;
	int m_nh;
	double m_UVsrcpoint[2];
	double m_XYsrcpoint[2];
	double m_poffsetXY[2];
	double m_poffsetUV[2];
	double m_eKwiggler;
	double m_epnorm; // photon energy for normalization
	double m_eptarget; // target photon energy for undulators

	// wigglers, BMs
	double m_dUmin;
	double m_ecritical;

	// grid condition for ideal sources
	int m_halfmesh[2];
	double m_delta[2];
	int m_mesh[2];
	double m_valrange[2];
	double m_dinterv[2];
	double m_halfrange[2];

	// grid condition for E-convoluted sinc func. for undulators
	double m_Uepsilon;
	int m_halfmeshsn[2];
	double m_deltasn[2];
	int m_snmesh[2];
	double m_valrangesn[2];

	// grid condition for aungular profiles for wigglers
	double m_aflux;
	double m_adelta[2];
	int m_amesh[2];
};

#endif


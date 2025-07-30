#ifndef kvalue_operation_h
#define kvalue_operation_h

#include "interpolation.h"
#include "spectra_solver.h"

class KValueOperation
	: public SpectraSolver
{
public:
	KValueOperation(SpectraSolver &spsolver);
	void GetSrcPerformance(
		vector<double> &energy, vector<vector<double>> &items, vector<string> &details);
	void GetWignerBrillianceCurve(vector<int> &itemindices,
		vector<vector<double>> &energy, vector<vector<vector<double>>> &items);
	void GetSrcPerformanceTarget(vector<int> &itemindices,
		vector<vector<double>> &energy, vector<vector<vector<double>>> &items);
	void GetPeakFluxTarget(vector<int> &itemindices, 
		vector<vector<double>> &energy, vector<vector<vector<double>>> &items);
	void GetSrcPerformanceBMWiggler(
		vector<int> &itemindices, vector<vector<double>> &items);
	void GetFixedFlux(vector<double> &Kvalue, vector<vector<double>> &items);
	void GetPower(vector<double> &e1st, vector<vector<double>> &items);
	void GetKxyValues(vector<double> &Kperp, 
		vector<double> &gap, vector<vector<double>> &Kxy, bool setgap);
	virtual void SetPowerLimit();

private:
	void f_GatherMPIHarmonics(int nei, 
		vector<vector<double>> &variable, vector<vector<vector<double>>> &items);
	void f_GatherMPI(int nsize, vector<double> &variable, vector<vector<double>> &items);
	void f_ExpandHarmonic(
		vector<vector<double>> energynh, vector<vector<vector<double>>> itemsnh,
		vector<double> &energy, vector<vector<double>> &items, vector<string> &details);
	void f_RetriveHarmonic(double energy, int tgtindex, int hidx,
		vector<vector<double>> &energynh, vector<vector<vector<double>>> &itemsnh, 
		vector<double> &items);
	void f_SetVariables();
	bool f_SetKvalues(int n, double *values);
	void f_ArrangeGapK(double *pKperp, double *pgap, int nk, bool setgap = true);
	void f_GetGapKxyAuto(double *pKperp, double *pgap, double Kxy[], bool setgap = true);
	void f_GetKxyTbl(double gap, double Kxy[]);
	double f_GetGapTbl(double Kperp);
	vector<int> m_harmonics;
	vector<int> m_harmonicmap;
	vector<double> m_kxyvar[2];
	vector<double> m_gapvar;

	bool m_istbl;
	bool m_isauto;
	vector<double> m_KxyTbl[3];
	vector<double> m_gap;
	int m_gpoints;
};

#endif


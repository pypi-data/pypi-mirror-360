#ifndef wigner4d_manipulator_h
#define wigner4d_manipulator_h

#include <algorithm>
#include <limits.h>
#include <vector>
#include <string>
#include "interpolation.h"
#include "spectra_solver.h"

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
	bool LoadData(string calctype, 
		vector<vector<double>> *vararray, vector<double> *data);
	bool LoadData(picojson::object &obj);
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
	void GetCSD(double Z,
		vector<vector<double>> &vararray, 
		vector<vector<vector<vector<double>>>> *CSD,
		double *xymax, int *xypoints, bool normalized);
	bool Transfer(double Z, double *xymax, int *xypoints, bool normalized);

private:
	void f_GetSliceDivergence(double *sigma);
	void f_GetSigma(double Z, double *sigma);
	void f_SetSteps(int *steps, int *mesh);
	void f_SetWindex(int j, double Z,
		int ifin[], bool far[], int k, int index[], double UV[], double *delta);
	void f_ExportProfile2D();
	void f_ExportWTrans(double Z, bool far, int jxy, bool killoffset);
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

	int m_hmesh[NumberWignerUVPrm];
	int m_meshZ[NumberWignerUVPrm];
	int m_hmeshZ[NumberWignerUVPrm];
	int m_stepsZ[NumberWignerUVPrm+1];
	double m_deltaZ[NumberWignerUVPrm];
	double m_rini[NumberWignerUVPrm];
	double m_rfin[NumberWignerUVPrm];

	double m_sigmaorg[NumberWignerUVPrm];
	double m_sdiv[2];
	double m_sizeZ[2];


	bool m_farzone[2];

	vector<vector<vector<vector<double>>>> m_dataZ;
};

class WignerPropagator :
	public SpectraSolver
{
public:
	WignerPropagator(SpectraSolver &spsolver);
	void Propagate(vector<string> &subresults, vector<string> &categories);

private:
	Wigner4DManipulator m_wigmanip;
	bool m_isxy[2];
	int m_type;
};

#endif
#ifndef volume_power_density_h
#define volume_power_density_h

#include "spectra_solver.h"

class GenericAbsorber;
class FilterOperation;

class VolumePowerDensity :
	public SpectraSolver
{
public:
	VolumePowerDensity(SpectraSolver &spsolver, FilterOperation *filter);
	~VolumePowerDensity();
	void AllocVolumePowerDensity(double leff,
		vector<vector<double>> &xyd, vector<vector<vector<double>>> &volpdens);
	void GetVolumePowerDensity(
		vector<vector<double>> &xyd, vector<vector<vector<double>>> &volpdens);

private:
	double f_Interpolate(int d, double xybm[],
		vector<vector<double>> &xyde, vector<vector<vector<double>>> &volpde);
	double f_GetVolumePDSingle(double depth, double leff,
		vector<double> &energy, vector<double> &flux, vector<double> &ws);
	void f_GetBeamCorrdinate(double xytgt[], double xybeam[]);
	void f_SetEnergyRange();
	vector<double> m_darray;
	double m_Phi;
	double m_Theta;
	double m_xyaccgl[2];
	double m_xyaccst[2];
	double m_dxybm[2];
	double m_ecritical;
	int m_meshbm[2];
	GenericAbsorber *m_absorber;
	FilterOperation *m_filter;
};

#endif


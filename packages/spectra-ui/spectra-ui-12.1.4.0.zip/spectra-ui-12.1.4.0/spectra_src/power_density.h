#ifndef power_density_h
#define power_density_h

#include "function_digitizer.h"
#include "trajectory.h"
#include "interpolation.h"
#include "spectra_solver.h"

using namespace std;

class PowerDensity
    : public FunctionDigitizer, public SpectraSolver
{
public:
    PowerDensity(SpectraSolver &spsolver, Trajectory *trajectory);
    void GetPowerDensity(double x, double y, vector<double> *pd);
    void AllocateOrbitComponents(Trajectory *trajectory);
    virtual double Function4Digitizer(double z, vector<double> *y);
	void SetObserverPositionAngle(vector<double> &XYZ, vector<double> &exyz);
private:
    void f_GetPowerDensityNear(double x, double y, vector<double> *pd);
    void f_GetPowerDensityFar(double x, double y, vector<double> *pd);
    void f_GetPowerDensityBM(double y, vector<double> *pd);
	double f_GetGlancingAngle(double z);
    Spline m_splpd;
    Spline m_Thetaspline[3];
    Spline m_Rspline;
    Spline m_accsqspline;
    Spline m_accthetaspline;
    vector<vector<double> > m_pdarray;
    vector<double> m_z;
    vector<double> m_Theta[2];
    vector<double> m_accsq;
    vector<double> m_acctheta;
    vector<double> m_R;
    OrbitComponents m_orbittmp;

    vector<vector<double> > m_pdtmp;
    vector<double> m_ztmp;

    int m_npoints;
    int m_points_max_dz;
    vector<double> m_borders;

    int m_ntotorbit;
    vector<OrbitComponents> m_orbit;
    vector<double> m_zorbit;
	Spline m_xyorbspline[3];

    double m_Dratio;
    double m_minimum_dz;
    double m_xyz[3];
    double m_exyz[3];

    int m_segidx;

	bool m_isglancing;
};

#endif

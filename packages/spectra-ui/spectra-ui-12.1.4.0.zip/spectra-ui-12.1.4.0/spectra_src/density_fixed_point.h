#ifndef density_fixed_point_h
#define density_fixed_point_h

#include "spectra_solver.h"
#include "undulator_flux_far.h"
#include "energy_convolution.h"
#include "interpolation.h"

class PowerDensity;
class FluxDensity;
class Trajectory;
class BMWigglerRadiation;
class SourceProfile;
class ComplexAmplitude;

class DensityFixedPoint
    : public SpectraSolver
{
public:
    DensityFixedPoint(SpectraSolver &spsolver, Trajectory *trajectory, FilterOperation *filter);
    virtual ~DensityFixedPoint();
    void GetDensity(double x, double y, vector<double> *density);
    void AllocateOrbitComponents(Trajectory *trajectory);
    int GetEnergyArray(vector<double> &energy);
	void SetObserverPositionAngle(vector<double> &XYZ, vector<double> &exyz);
    double GetSrcPointCoef(){return m_coefsrcp;}
    virtual void GetMeasuredTime(vector<string> &label, vector<double> &rtime);

private:
    void f_GetPowerDensity(double x, double y, vector<double> *density);
    void f_GetDensityUndFar(
        double x, double y, vector<double> *density, bool ispower = false);
    void f_GetHarmonicPowerUndFar(
        double x, double y, vector<double> *density);
    void f_AllocateFluxDensityNearZspread(double *xy);
    void f_GetFluxDensityNear(double x, double y, vector<double> *density);
    void f_GetFluxDensityWiggler(double x, double y, vector<double> *density);
    void f_GetFilteredPowerDensity(double x, double y, vector<double> *density);
    SincFuncEnergyConvolution *m_sneconv;
    ArraySincFuncEnergyConvolution *m_sneconvarray;
    UndulatorFxyFarfield *m_fluxund;
    FluxDensity *m_fluxnear;
    PowerDensity *m_powerdens;
    SourceProfile *m_srcprof;
    ComplexAmplitude *m_camp;
    EnergySpreadConvolution *m_espreadconv;
    BMWigglerRadiation *m_bmwigglerflux;
    Spline m_spl4pw;
    FilterOperation *m_filter;

    int m_nitemspoint;
    double m_harmonic_eps;
    int m_convergence_limit;

    long m_energymesh;
    vector<double> m_ws4flux;
    vector<double> m_earray;
    vector<vector<double>> m_farray;

    double m_convf2p;
    bool m_snconv1st;
    int m_nhtarget;

    double m_dXYdUV;
    double m_coefsrcp;
};

#endif


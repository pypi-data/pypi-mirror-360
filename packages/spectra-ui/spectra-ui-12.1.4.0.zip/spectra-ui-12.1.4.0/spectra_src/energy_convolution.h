#ifndef energy_convolution_h
#define energy_convolution_h

#include <vector>
#include "spectra_solver.h"
#include "interpolation.h"
#include "quadrature.h"
#include "function_digitizer.h"

#define ENERGY_SPREAD_CONVOLUTION 0x001L
#define DETECTOR_RESOLUTION_CONVOLUTION 0x002L

using namespace std;

class EnergyConvolution
    : public QGauss
{
public:
    EnergyConvolution(int nitems = 0);
    void AllocateMemoryEnergyConvolution(int nitems);
    void AllocateInterpolant(
        int energymesh, vector<double> *energy, vector<vector<double>> *fluxin,
        bool isreg);
protected:
    vector<MonotoneSpline> m_splfitem;
    int m_energymesh;
};

class EnergySpreadConvolution
    : public EnergyConvolution
{
public:
    virtual ~EnergySpreadConvolution(){}
    EnergySpreadConvolution(SpectraSolver *spsolver, int nitems = 0);
    virtual void IntegrandGauss(double ep, vector<double> *flux);
    void RunEnergyConvolution(double ep, vector<double> *fluxout, bool isdirect = false);
	void GetValues(double ep, vector<double> *fluxout);
protected:
    SpectraSolver *m_spsolver;
    double m_epref;
    int m_pointsgauss;
    double m_glimit;
    int m_glevel;
};

class SincFuncEnergyConvolution
    : public EnergySpreadConvolution, public SpectraSolver
{
public:
    SincFuncEnergyConvolution(SpectraSolver &spsolver);
    void SetHarmonic(int nh);
    void SetObservationAngle(double gtx, double gty);
    void SetRadialAngle(double gt);
    void SetCurrentE1st(double e1st);
    virtual void IntegrandGauss(double ep, vector<double> *snc);
    virtual void GetSincFunctionCV(double ep, vector<double> *sn);
    double GetCurrentE1st();
    int GetNumberOfSnItems();
protected:
    int m_snitems;
    double m_e1st4sn;
    int m_nh;
};

class SincFuncEspreadProfile :
    public SincFuncEnergyConvolution, public QSimpson
{
public:
    SincFuncEspreadProfile(SpectraSolver &spsolver);
    void QSimpsonIntegrand(int layer, double gt, vector<double> *density);
    void GetPeakValueStdDeviation(int nh, double *peak, double *gtsigma);
private:
    double m_e1staxis;
    double m_eps;
    int m_nh;
};


class FilterOperation;

class SincFuncFilteredIntegration
    : public SincFuncEnergyConvolution, public QSimpson
{
public:
    SincFuncFilteredIntegration(SpectraSolver &spsolver, FilterOperation *filter);
    virtual void GetSincFunctionFilteredPower(vector<double> *sn);
    virtual void QSimpsonIntegrand(int layer, double ep, vector<double> *snc);
private:
    FilterOperation *m_filter;
    double m_eps;
};

class ArraySincFuncEnergyConvolution
    : public FunctionDigitizer, public SpectraSolver
{
public:
    ArraySincFuncEnergyConvolution(SpectraSolver &spsolver, FilterOperation *filter);
    virtual ~ArraySincFuncEnergyConvolution();
    virtual double Function4Digitizer(double ep1, vector<double> *sn);
    void GetSincFunctionFromArray(int nh, double ep1, vector<double> *sn);
private:
    void f_AllocateSpline(int nh, bool isappend);
    vector<Spline *> m_sincfuncspline[4];
    vector<bool> m_allocspline;
    SincFuncEnergyConvolution *m_sincfunc;
    SincFuncFilteredIntegration *m_sincfilter;
    vector<vector<double>> m_sntmp;
    int m_snitems;
    double m_eps_func_stepper;
    double m_ep1min4array;
    double m_ep1max4array;
    double m_demin4array;
};

#endif

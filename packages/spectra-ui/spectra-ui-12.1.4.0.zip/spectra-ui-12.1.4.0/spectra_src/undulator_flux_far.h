#ifndef undulator_flux_far_h
#define undulator_flux_far_h

#include "undulator_fxy_far.h"
#include "spectra_solver.h"
#include "function_digitizer.h"
#include "interpolation.h"
#include "fast_fourier_transform.h"

class UndulatorFluxInfPeriods
    : public FunctionDigitizer, public UndulatorFxyFarfield
{
public:
    UndulatorFluxInfPeriods(SpectraSolver &spsolver);
    double Function4Digitizer(double phi0, vector<double> *fd);
    void IntegrateAlongPhi(int nh, double gt, vector<double> *fd, bool isebconv = false);

private:
    vector<double> m_phi;
    vector<vector<double>> m_fdarray;
    double m_rint;
    double m_phiref[3];
    double m_eps_along_phi;
    bool m_isebconv;
    int m_ninit_alongphi;
};

class EnergySpreadConvolution;

class UndulatorSpectrumInfPeriods
    : public FunctionDigitizer, public SpectraSolver
{
public:
    UndulatorSpectrumInfPeriods(SpectraSolver &spsolver, int rank = 0, int mpiprocesses = 0);
    virtual ~UndulatorSpectrumInfPeriods();
    void AllocateInfPeriodSpectrum(int layer);
    double Function4Digitizer(double ep, vector<double> *fd);
    void QSimpsonIntegrand(int layer, double ep, vector<double> *fd);

protected:
    double f_GetFxyFixedEnergy(double ep, vector<double> *fd);
    double f_GetFxyFixedEnergyHarmonic(
            int nh, double ep, vector<double> *fd, double *gt, bool ischeckebconv);

    UndulatorFluxInfPeriods *m_FluxInf;
    EnergySpreadConvolution *m_EspreadConv;
    vector<double> m_fdtmp;
    vector<vector<double>> m_eparray;
    vector<vector<vector<double>>> m_fdmatrix;
    vector<int> m_epmesh;
    double m_ep1onaxis;
    double m_e1stobs;
    double m_eps_harmonic;
    double m_eps_stepper;
    double m_eps_initial;
    double m_epmax;
    double m_epallocmax;
    int m_currnh;
    int m_nhmax;
    bool m_checkebconv;
    bool m_espreadconv;
	bool m_skipintphi;

private:
	int m_mpiprocesses;
	int m_rank;
};

class FluxSincFuncConvolution
    : public QSimpson
{
public:
    FluxSincFuncConvolution(SpectraSolver *spsolver, int nh, int rank = 0, int mpiprocesses = 1);
    virtual void QSimpsonIntegrand(int layer, double ep, vector<double> *flux);
    void AllocateInterpolant(long energymesh,
        vector<double> *energy, vector<vector<double>> *fluxin, bool isreg);
    void RunSincFuncConvolution(double ep, double *fluxout);
private:
    SpectraSolver *m_spsolver;
    vector<Spline> m_splfitem;
    int f_GetIndexMaximumEnergy(double epref);
    void f_GetIntegrationRange(double epref, int nindex, double *erange);
    double m_epref;
    int m_nh;
    double m_epmax;
    double m_epmin;
    double m_eps_simpson;
    double m_eps_sum;
};

class UndulatorFluxFarField
    : public UndulatorSpectrumInfPeriods
{
public:
    UndulatorFluxFarField(SpectraSolver &spsolver, int layer, int rank = 0, int mpiprocesses = 1);
    virtual ~UndulatorFluxFarField();
    double GetFlux(double ep, vector<double> *flux);
    void GetPeakFluxHarmonic(vector<int> *harmonicnumber, vector<double> *ep, vector<vector<double>> *flux);
    void GetPeakFluxHarmonicSegmented(int nh, double *ek, vector<double> *flux);
    void GetUSpectrum(vector<double> *energy, vector<vector<double>> *flux, 
        int layer, int rank = 0, int mpiprocesses = 1);
private:
    void f_GetSpectrumFT(int layer);
    void f_ArrangeFFT();
    void f_AssignInfPeriodSpectrum();
    void f_GetFluxFromSpline(double ep, vector<double> *flux);

    vector<vector<Spline>> m_FxySpline;
    vector<FluxSincFuncConvolution *> m_FluxSincConv;

    int m_ndata;
    int m_nfft;
    double m_snumax;
    double m_numax;
    double m_de;
    double m_dnu;
    double m_coef;
    vector<double *> m_fxy;
};

#endif

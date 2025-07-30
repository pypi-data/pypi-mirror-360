#ifndef bm_wiggler_radiation_h
#define bm_wiggler_radiation_h

#include <vector>
#include "quadrature.h"
#include "spectra_solver.h"
#include "filter_operation.h"

using namespace std;

class UndulatorFxyFarfield;

class BMWigglerRadiation
    : public QSimpson, public SpectraSolver
{
public:
    BMWigglerRadiation(SpectraSolver &spsolver, FilterOperation *filter);
    virtual ~BMWigglerRadiation();
    void GetEnergyArray(vector<double> &energy);
    static void GetBMStokes(double u, double v, vector<double> *fhvc);
    static void BMPowerDensity(double gpsi, vector<double> *pd);
	static double GetDivergence(double u);
    void GetFluxWigglerBM(double ep, double gtx, double gty, vector<double> *fhvc);
    void GetFluxArrayWigglerBM(double gtx, double gty, vector<double> *farray, bool ispower = false);
    void TotalFlux(double ep, double flux[]);
    void IntegratedFluxPower(double ep, vector<double> *Ifp);
    virtual void QSimpsonIntegrand(int layer, double x, vector<double> *y);
private:
    void f_QSimpsonTflux(double z, vector<double> *flux);
    void f_QSimpsonIflux(double ep, vector<double> *flux);
    void f_TotalFluxEMPW(double ep, double tflux[]);
    void f_TotalFluxBM(double u, double flux[]);
    UndulatorFxyFarfield *m_undfxy;
    double m_ecritical;
    double m_eptmp;
    bool m_isbm;
};

enum {
    RadQSimpTypeTflux = 0,
    RadQSimpTypeIflux
};

#endif

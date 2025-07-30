#ifndef filter_operation_h
#define filter_operation_h

#include "interpolation.h"
#include "energy_convolution.h"
#include "function_digitizer.h"

class GenericFilterTransmission
{
public:
    GenericFilterTransmission();
    void SetMaterials(vector<tuple<string, double>> &filters, 
        map<string, tuple<double, vector<double>>> &materials);
    double GetTransmission(double ep, 
        double *linabscoef = nullptr, double *linheatcoef = nullptr);
    double GetEnergyAbsRatio(int Z, double ep);
    int GetElements();
    vector<int> GetZnumbers();

private:
    int m_elements;
    vector<int> m_Znumber;
    vector<double> m_thickness;
    vector<double> m_density;
    vector<vector<double>> m_tbl_energies;
    vector<vector<double>> m_tbl_ratios;
};

class GenericAbsorber
{
public:
    GenericAbsorber(vector<tuple<string, double>> &filters, 
        map<string, tuple<double, vector<double>>> &materials);
	~GenericAbsorber();
	int GetTargetLayer(double depth, double *reldepth);
	double GetAbsorption(
        int tgtlayer, double reldepth, double ep, double *leff = nullptr);
    double GetTotalAbsorption(double ep);
	GenericFilterTransmission *GenFilter(int layer);
private:
	int m_nabss;
	vector<double> m_dborders;
	vector<GenericFilterTransmission *> m_generic;
};

class FilterOperation
    : public FunctionDigitizer, public SpectraSolver, public QGauss
{
public:
    FilterOperation(SpectraSolver &spsolver, bool isabs = false);
    double GetFilteredPower(int energymesh, vector<double> *energy, vector<double> *flux);
    void GetEnergyRange4Power(double ec, double eps, double erange[]);
	double (FilterOperation::*GetTransmissionRate)(double ep);
    double GetTransmissionRateF(double ep);
    double GetTransmissionRateCV(double ep, bool isopt, int region = -1, int index = -1);
    virtual void IntegrandGauss(double ep, vector<double> *flux);
    virtual double Function4Digitizer(double ep, vector<double> *rate);
    void GetEnergyRange(double *epmin, double *epmax);
    int GetNumberOfRegions();
    double GetRegionBorder(int region);
    bool IsGeneric(){return m_isgeneric;}
    bool IsPowerAbs(){return m_ispowabs;}
    void GetTransmissionData(vector<double> &ep, vector<double> &trans);
private:
    Spline m_filterspline; // spline for custom filter data
    Spline m_fluxfilterspline; // workspace: flux*rate
    Spline m_efluxspline; // spline for input spectrum
    vector<Spline> m_filtercvspline; // energy-convoluted rate array for each region
    vector<double> m_eregborder; // region boundaries

    void f_AllocateEConvolutedRate();
    void f_AllocateBPF();
    void f_AllocateCustom();
    void f_AllocateGeneric();
    void f_AllocateMaximumEnergy4GenericFilter(double epmax);
    double f_GetBPF(double ep);
    double f_GetCustom(double ep);
    double f_GetGeneric(double ep);
    double f_GetEpInRange(double ep);

    GenericFilterTransmission m_genericf;

    vector<double> m_energy;
    vector<double> m_flux;
    vector<int> m_ndatapoints;
    double m_ecvboundary[2];
    int m_elements;
    int m_regions;
    int m_currregion;
    int m_maxdatapoints;
    int m_pointsgauss;

    double m_epref;
    bool m_isgeneric;
    bool m_isBPFGauss;
    bool m_isBPFBox;
    bool m_isCustom;
    bool m_ispowabs;
};

#endif

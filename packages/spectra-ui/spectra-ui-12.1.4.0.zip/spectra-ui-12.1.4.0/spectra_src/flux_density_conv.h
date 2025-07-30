#ifndef flux_density_conv_h
#define flux_density_conv_h

#include <vector>
#include "interpolation.h"
#include "fast_fourier_transform.h"
#include "orbit_components_operation.h"
#include "spectra_solver.h"

class Trajectory;
class FilterOperation;

class FluxDensityConv
    : public SpectraSolver
{
public:
    FluxDensityConv(SpectraSolver &spsolver, Trajectory *trajectory, FilterOperation *filter);
    ~FluxDensityConv();
    void GetFluxItemsAt(double *xy, vector<double> *values, bool isfar = false);
    int GetEnergyArray(vector<double> *energy);
    void AllocateOrbitComponents();
    void GetSingleElectricField(vector<vector<double> > *Ereim);
    int GetEnergyMesh(){return m_ndata4output;}
    double GetEnergyAt(int step){return m_ep[step];}
	double GetFixedEnergy(){return m_fixep;}

protected:
	bool f_SetupFTConfig();
	void f_GetZrange(bool ispower, double taurange[]);
	void f_GetTauRange(double *point, double *range4emin, double *range4typ);
	void f_AllocateElectricField(bool accbase, bool divdfactor, bool allocspl, 
			bool isfar = false, vector<double> *ppz = nullptr, double *cxy = nullptr);
    void f_AllocateComplexFieldByFFT(bool iscsr = false);
    void f_GetFluxItems(vector<double> *values);
	void f_SetXYAngle(double *qxy);
    void f_SetXYPosition(double *xy);
	void f_GetBoundaryTerm(double w, double *taur, double *dTh, double *values);
	void f_AllocNTauPoints(int ntaupoints);

	Trajectory *m_trajectory;
    bool m_isfixep;
	bool m_isef_accel;
	bool m_isavgd;

	int m_ndata4output;
	int m_fft_nskip;
	int m_ntotorbit;

    vector<double> m_zorbit;
    vector<double> m_ep;
	vector<double> m_tau;
    vector<double> m_Et[3];
    vector<double> m_D;

	double m_Etmax;
	int m_ntmax;
	double m_taurange[3];
    int m_ntaupoints;

	Spline m_EtSpline[2];
    Spline m_DSpline;

	double m_conv_dtau2ep;
    double m_XYZ[3]; // position of observation

    double m_dtau;

    double m_eming;
	double m_deFT;
    double *m_EwFFT[2];
    vector<OrbitComponents> m_orbit;

    FastFourierTransform *m_fft;
	unsigned int m_nfftbase;
    unsigned int m_nfft;
	unsigned int m_nfftmax;
	vector<FastFourierTransform *> m_ffts;
	vector<int> m_nffts;

private:
	void f_GetFieldCommon(bool isfft,
		double rein, double imin, double ep, double taur[], double dTh[], double *reout, double *imout);
    bool f_SetupCondition(FilterOperation *filter);
	void f_SetInterpolationEt(double w, double *taur, double **dTh);
    void f_AllocateFieldWiggler();
    void f_AdjustPhase4TimeShift(
        double tauini, double ep, double *ere, double *eim);

    Spline m_EwSpline[4];
    vector<double> m_EtDFT[2];
    vector<int> m_narray4bg;
    vector<double> m_taubgborder;
    vector<double> m_epFFT;

    int m_fmaptype;

	double m_qxqy[2]; // angle of observation
    double m_Dmin;

    vector<double> m_Fxy[4];
};

#endif
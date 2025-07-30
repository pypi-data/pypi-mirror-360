#ifndef flux_density_h
#define flux_density_h

#include <vector>
#include "interpolation.h"
#include "fast_fourier_transform.h"
#include "orbit_components_operation.h"
#include "spectra_solver.h"

class Trajectory;
class FilterOperation;
class Particle;

class FluxDensity
    : public SpectraSolver
{
public:
    FluxDensity(SpectraSolver &spsolver, Trajectory *trajectory, FilterOperation *filter);
    FluxDensity(SpectraSolver &spsolver);
    void Initialize();
    void InitFluxDensity(
        Trajectory *trajectory, FilterOperation *filter);
    virtual ~FluxDensity();
    void GetFluxItemsAt(double *xy, 
        vector<double> *values, bool isfar = false, int *zfixrange = nullptr, double *XY = nullptr);
    virtual void GetEnergyArray(vector<double> &energy);
    void AllocateOrbitComponents();
    int GetEnergyMesh(){return m_nfd;}
    double GetEnergyAt(int step){return m_ep[step];}
	double GetFixedEnergy(){return m_fixep;}

protected:
	bool f_SetupFTConfig();
    bool f_SetupFTBase(bool negblen = false);
    void f_AllocMemory();
	void f_SwitchFFT(int nfft);
	void f_GetZrange(bool ispower, bool iscsr, double taurange[]);
    void f_AllocateElectricField(
        bool forceaccl, bool allocspl, bool isfar = false, 
        double *zobs = nullptr, double *tdelay = nullptr, double *xyorb = nullptr);
    void f_AllocateComplexField(bool step = false, bool skipft = false, bool fixtau = false, int *zidxrange = nullptr,
        bool isfar = true, double *zobs = nullptr, double *tdelay = nullptr, double *xyorb = nullptr);
    void f_GetFT();
    void f_GetSpectrum();
    void f_GetTemporal();
    void f_GetFluxItems(vector<double> *values);
	void f_SetXYAngle(double *qxy);
    void f_SetXYPosition(double *xy = nullptr);
	void f_GetBoundaryTerm(int jxy, double w, double *values);
	void f_AllocNTauPoints();

	Trajectory *m_trajectory;
    bool m_isfixep;
	bool m_isef_accel;
    bool m_isrealft;

	int m_nfd;
	int m_fft_nskip;
    int m_ntaupoints;
    int m_norbpoints;
    int m_nepointsmin;

    double m_erange[2]; // energy range computed in this class

    int m_dim; // dimension; if m_dim==3, Ez is computed
    vector<double> m_Et[3];
    Spline m_EtSpline[3];
    double *m_EwFFT[3];

    vector<double> m_zorbit;
    vector<double> m_ep;
	vector<double> m_tau;
    vector<double> m_D;
    vector<double> m_EtPw;

    vector<double> m_eplog;
    vector<double> m_eplogfd[4];
    vector<int> m_eplogidx;

	double m_Etmax;
	int m_ntmax;
	double m_taurange[3];

	double m_conv_dtau2ep;
    double m_time2tau;
    double m_XYZ[3]; // position of observation
    double m_qxqy[2]; // angle of observation

    double m_dtau;

	double m_deFT;
    double *m_EwBuf[3];
    vector<OrbitComponents> m_orbit;

    FastFourierTransform *m_fft;
	unsigned int m_nfftbase;
    unsigned int m_nfft;
	unsigned int m_nfftmax;
	vector<FastFourierTransform *> m_ffts;
	vector<int> m_nffts;

    vector<vector<double>> m_Fxy;
    vector<vector<double>> m_Fbuf;

private:
	void f_GetFieldCommon(int jxy, bool isfft,
		double rein, double imin, double ep, double *reout, double *imout);
    bool f_SetupCondition(FilterOperation *filter);
	void f_SetInterpolationEt(double *taurange = nullptr);
    void f_AllocateFieldWiggler();
    void f_AdjustPhase4TimeShift(
        double tauini, double ep, double *ere, double *eim);

    Spline m_EwSpline[4];
    vector<double> m_EtDFT[2];
    vector<int> m_narray4bg;
    vector<double> m_taubgborder;
    vector<double> m_epFFT;
    vector<vector<double>> m_dTh {{0,0}, {0,0}, {0,0}};
    double m_taur[2];
    double m_Dmin;
    int m_nini4ep;
};

#endif
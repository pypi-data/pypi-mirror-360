#ifndef undulator_fxy_far_h
#define undulator_fxy_far_h

#include "quadrature.h"
#include "bessel.h"
#include "spectra_solver.h"
#include "function_digitizer.h"
#include "interpolation.h"

class FastFourierTransform;

class UndulatorFxyFarfield
	: public QGauss, public SpectraSolver
{
public:
	UndulatorFxyFarfield(SpectraSolver &spconf);
	virtual ~UndulatorFxyFarfield();
	void SetCondition(int nh, double gt);
	void SetObservation4Wiggler(int nhmax, double gtxy[]);
	void GetFxy(double phi, vector<double> *fxy, bool isamp = false);
    void GetFlux4Wiggler(double nh, vector<double> *fhvc);

	virtual void IntegrandGauss(double z, vector<double> *fxy);
	double GetCoefFxy();

protected:
	int m_nh;
	int m_currseg;
	double m_gsi;
	double m_gt;
	double m_gt2;
	double m_gtxy[2];
	double m_z;
	bool m_issec;
	MonotoneSpline m_splfxy[4];
	Bessel m_bjz;
	Bessel m_bjx;
	void (UndulatorFxyFarfield::*f_Fxy)(double phi, double *fx, double *fy, bool issec);
	void f_LinearFxy(double phi, double *fx, double *fy, bool issec = false);
	void f_HelicalFxy(double phi, double *fx, double *fy, bool issec = false);
	void f_EllipticFxy(double phi, double *fx, double *fy, bool issec = false);
	void f_CustomFxy(double phi, double *fx, double *fy, bool issec = false);
	
	int m_nfft;
	FastFourierTransform *m_fft;
	double *m_data;
};

#endif

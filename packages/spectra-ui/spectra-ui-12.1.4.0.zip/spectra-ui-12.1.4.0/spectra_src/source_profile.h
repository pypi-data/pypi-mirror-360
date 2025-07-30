#ifndef source_profile_h
#define source_profile_h

#include <vector>
#include "fast_fourier_transform.h"
#include "function_digitizer.h"
#include "interpolation.h"
#include "mpi_by_thread.h"

class ComplexAmplitude;
class PrintCalculationStatus;
class Spline;

using namespace std;

class SourceProfile : FunctionDigitizer
{
public:
	SourceProfile(ComplexAmplitude *camp, int acclevel, int nwiggler, bool isoddpole, 
		PrintCalculationStatus *status, int layer);
	~SourceProfile();
	void AllocateSpatialProfile(int rank, int mpiprocesses);
	virtual double Function4Digitizer(double v, vector<double> *Exy);
	void AllocateProfileEconv(bool isalloc = true);
	double GetFluxAt(double UV[]);

private:
	void f_SpatialProfileSingle(int nc, 
		vector<vector<double>> *ws, double d_eta = 0, bool isalloc = true, 
		int rank = 0, int mpiprocesses = 1, bool issec = false);
	bool f_SpatialProfileSingleFD(
		int nc, vector<vector<double>> *we, vector<vector<double>> *wf);
	void f_AllocateProfileUndulator();
	void f_AllocateProfileWiggler(int rank, int mpiprocesses);

	int f_GetSkipNumber(double *data, int nfft);
	void f_ClearPointers();

	ComplexAmplitude *m_camp;
	FastFourierTransform *m_fft[2];
	MPIbyThread *m_thread;

	int m_acclevel;
	int m_nfft[2];
	int m_nfftcurr[2];
	int m_nskip[2];
	double *m_wsdatax[2];
	double *m_wsdatay[2];
	vector<double *> m_xdata;
	vector<double *> m_ydata;
	int m_nfftxydata;
	double m_sigmaUV[2]; // normalized beam size for smoothing

	bool m_isund;
	bool m_isbm;
	bool m_oddpolewig;
	double m_polarity;
	int m_Nwiggler;
	int m_ncomps;

	// for BM radiation
	bool m_splon;
	double m_UVtgt[2];
	double m_epsilon;
	Spline m_airyspl[2];

	// container
	vector<vector<vector<double>>> m_F;
	vector<vector<vector<double>>> m_G;

	// grid parameters
	vector<double> m_deltasp[4];
	vector<int> m_spmesh[4];
	vector<int> m_halfmeshsp[4];

	// energy grid conditions for none-ideal sources
	vector<double> m_eparray;
	double m_espredrange;

	// total flux
	double m_sflux;

	PrintCalculationStatus *m_status;
	int m_layer;
};

#endif

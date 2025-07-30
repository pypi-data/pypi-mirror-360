#ifndef wigner_function_h
#define wigner_function_h

#include "quadrature.h"
#include "function_digitizer.h"
#include "spectra_solver.h"

class ComplexAmplitude;

class WignerFunction :
	public QSimpson, FunctionDigitizer
{
public:
	WignerFunction(ComplexAmplitude *camp, 
		int acclevel, int nwiggler, bool isoddpolewig,
		PrintCalculationStatus *status, int wlayer);
	void GetWignerPhaseSpace(int type, bool is4size,
			double UVfix[], double uvfix[], vector<double> vararray[],
			vector<vector<double> > *W, 
			int rank = 0, int mpiprocesses = 1, MPIbyThread *thread = nullptr);
	virtual void QSimpsonIntegrand(int layer, double uv, vector<double> *W);
    virtual double Function4Digitizer(double uv, vector<double> *W);
	int GetProcessLayer(){return m_process_layer;}

private:
	ComplexAmplitude *m_camp;

	bool f_IsEvaluateGtEiwt(bool isx, double range[], double w);
	void f_ReIntegrateEwit(int nc, int np, double w, int N, 
		vector<double> *arg, vector<vector<double> > *values, vector<double> *W);
	void f_GetWignerAlongUV(
		double uvfix, vector<double> *UVarr, vector<vector<double> > *W,
		int rank = 0, int mpiprocesses = 1, MPIbyThread *thread = nullptr);

	void f_Integrand_u_econv(double u, vector<double> *W);
	void f_Integrand_u(double u, vector<double> *W);
	void f_Integrand_v(double v, vector<double> *W);
	void f_Convolute_uv(int uvidx, double uv, vector<double> *W);
	void f_GetIntegRangeCV(int uvidx, double uvrange[]);
	void f_GetFTRange(int uvidx, double uvrange[]);
	void f_PutZeroValues(vector<double> *W, int np = 1);
	void f_GetIntegralLevel(double range[], int uvidx, int level[]);

	vector<double> m_wsarg[WignerIntegOrderUVcv+1];
	vector<vector<double> > m_wsval[WignerIntegOrderUVcv+1];
	vector<double> m_UVpoints;
	vector<double> m_wsorg;
	vector<double> m_wsni;

	// source conditions etc.
	double m_gaussian_limit;
	double m_srcpoint[2];
	double m_polarity;
	int m_acclevel;
	int m_type;
	bool m_isund;
	bool m_oddpolewig;
	bool m_idealsrc;
	int m_Nwiggler;
	int m_ncomps;
	int m_nUVpoints;

	// e-beam conditions
	double m_sigmauv[2];
	double m_sigmaUV[2];
	double m_alpha[2];

	// convolution variables
	int m_uvcvidx;
	int m_uvscidx;
	double m_uvfix[2];
	double m_uvvar[2];
	double m_uvcv[2];

	// integration ranges
	double m_halfrange[2];
	double m_dinterv[2];

	// energy grid conditions for none-ideal sources
	vector<double> m_eparray;
	double m_espredrange;
	double m_eptarget;

	PrintCalculationStatus *m_calcstatus;
	int m_process_layer;
};

class WignerFunctionCtrl :
	public SpectraSolver
{
public:
	WignerFunctionCtrl(SpectraSolver &spsolver, 
		int layer, ComplexAmplitude *camp = nullptr);
	virtual ~WignerFunctionCtrl();
	void GetPhaseSpaceProfile(vector<vector<double>> &xyvar, 
		vector<double> &W, int rank = 0, int mpiprocesses = 1);
	void GetVariables(vector<int> &wigtypes,
		vector<vector<double>> &xyvar, vector<vector<int>> &indices);
	void SetPhotonEnergy(double ep);

private:
	void f_CopyWdata(
		vector<double> vararray[], vector<vector<double>> &ws, vector<double> &W, int offset = 0);
	ComplexAmplitude *m_camp;
	WignerFunction *m_wigner;
	double m_dXYdUV;
	double m_dqduv;
	int m_wiglayer;
	bool m_single;
	bool m_isctrled;
};

#endif

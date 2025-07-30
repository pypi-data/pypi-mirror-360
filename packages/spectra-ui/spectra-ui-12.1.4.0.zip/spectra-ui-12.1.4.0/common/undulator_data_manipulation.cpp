#include <algorithm>
#include <complex>
#include "undulator_data_manipulation.h"
#include "randomutil.h"
#include "fast_fourier_transform.h"
#include "optimization.h"

// files for debugging
string UFdataOrbitTrend;
string UFdataPhaseTrend;

#define PHASESMOOTHR 0.5
#define MESHPERPERIOD 32

UndulatorFieldData::UndulatorFieldData()
{
#ifdef _DEBUG
//UFdataOrbitTrend = "..\\debug\\ufdata_orbit_trend.dat";
//UFdataPhaseTrend = "..\\debug\\ufdata_phase_trend.dat";
#endif
}

bool UndulatorFieldData::AllocateUData(
    RandomUtility *rand, int N, double lu, double K2, vector<double> Kxy[], vector<double> deltaxy[],
	double *sigma, double *sigalloc, bool isfsym, bool isendcorr)
{
	m_isfsymm = isfsym;
	m_isendcorr = isendcorr;

	m_K2 = K2;
	m_N = N;
	m_endpoles[0] = m_endpoles[1] = 2*ENDPERIODS; // # end poles at each end
	f_SetCommonPrm(lu, Kxy, deltaxy);

	if(isfsym){
		m_z0thpole[0] += m_lu*0.25;
		m_z0thpole[1] += m_lu*0.25;
	}
	m_isfsymm = isfsym;
	m_isendcorr = isendcorr;

	if(!AllocateIntegral(rand, true, sigma, sigalloc)){
		throw runtime_error(m_errmsg);
	}
	return true;
}

bool UndulatorFieldData::AllocateIntegral(
	RandomUtility *rand, bool isnormalize, double *sigma, double *sigalloc)
{
	vector<vector<double>> acc(2);

	m_z.resize(m_ndata);
	m_isnormalize = isnormalize;

	m_i1err.resize(2); m_i1drv.resize(2); 
	m_bdrv.resize(2); m_bkick.resize(2); m_wsacc.resize(2);
	for(int j = 0; j < 2; j++){
		m_i1err[j].resize(2*(m_N+m_endpoles[0]), 0.0);
		m_i1drv[j].resize(2*(m_N+m_endpoles[0]), 0.0);
		m_bkick[j].resize(2*(m_N+m_endpoles[0]), 0.0);
		m_bcorr[j].resize(2*(m_N+m_endpoles[0]), 0.0);
		m_bdrv[j].resize(2*(m_N+m_endpoles[0]), 0.0);
	}
	m_eta.resize(2*(m_N+m_endpoles[0]), 0.0);

	// orbit error arrangement
	double fdev = sigma[UErrorBdevIdx];
	if(fdev < 0){
		fdev = fabs(fdev)*rand->Uniform(0, 1.0);
	}
	if(rand != NULL){
		for(int n = 0; n < m_N+m_endpoles[0]; n++){
			for(int j = 0; j < 2; j++){
				m_bdrv[j][2*n+1] = m_B*fdev*rand->Gauss(true);
				m_bdrv[j][2*n] = -m_bdrv[j][2*n+1];
			}
		}
	}

	// evaluate the field quality without correction
	for(int j = 0; j < 3; j++){
		m_frac[j] = 1.0;
	}
	f_ApplyErrors();

	if(rand == nullptr){
		return true;
	}
	double sigstd[NumberUError];
	GetErrorContents(m_endpoles, sigstd, &m_items);
	// adjust the orbit error component
	m_frac[0] = sigma[UErrorYerrorIdx]/sigstd[UErrorYerrorIdx];
	m_frac[1] = sigma[UErrorXerrorIdx]/sigstd[UErrorXerrorIdx];

	double pdev = max(m_frac[0], m_frac[1]);
	if(pdev > 1.0){
		// the field deviation too small for the orbit error
		m_errmsg = "The field deviation is too small to generate the specified trajectory error.";
		return false;
	}
	pdev = sqrt(1.0-pdev)*fdev;
	for(int n = 0; n < m_N+m_endpoles[0]; n++){
		// compensate the field error to satisfy the given condition
		for(int j = 0; j < 2; j++){
			double bdev = m_B*pdev*rand->Gauss(true);
			m_bdrv[j][2*n+1] = m_bdrv[j][2*n+1]*m_frac[j]+bdev;
			m_bdrv[j][2*n] = m_bdrv[j][2*n]*m_frac[j]+bdev;
		}
	}
	m_frac[0] = m_frac[1] = 1;
	f_ApplyErrors();
	GetErrorContents(m_endpoles, sigstd, &m_items);
	double sigsq = sigstd[UErrorPhaseIdx]*sigstd[UErrorPhaseIdx];

	m_frac[2] = 0;
	f_AdjustPhase();
	f_ApplyErrors();
	GetErrorContents(m_endpoles, sigstd, &m_items, nullptr, true);
	double sig0sq = sigstd[UErrorPhaseIdx];
	if(sig0sq > sigma[UErrorPhaseIdx]){
		m_errmsg = "The phase error is too small to generate the specified trajectory error.";
		return false;
	}
	sig0sq *= sig0sq;

	double eps = 0.05, err, tgteta;
	double sigtsq = sigma[UErrorPhaseIdx]*sigma[UErrorPhaseIdx];
	m_frac[2] = 1.0;
	do{
		tgteta = sigsq-sig0sq;
		if(tgteta <= 0){
			m_errmsg = "Cannot find a solution to generate the specified undulator error model.";
			return false;
		}
		tgteta = sqrt((sigtsq-sig0sq)/tgteta);
		m_frac[2] *= tgteta;
		f_ApplyErrors();
		GetErrorContents(m_endpoles, sigalloc, &m_items);
		sigsq = sigalloc[UErrorPhaseIdx]*sigalloc[UErrorPhaseIdx];
		err = fabs(sigalloc[UErrorPhaseIdx]-sigma[UErrorPhaseIdx]);
	} while(fabs(tgteta-1.0) > 0.01 && err > eps);

    AdjustKValue(sqrt(2.0*m_K2));
	return err <= eps;
}

void UndulatorFieldData::GetErrorArray(
	vector<vector<double>> *I1err, vector<vector<double>> *bkick)
{
	*I1err = m_i1err;
	*bkick = m_bkick;
}

void UndulatorFieldData::GetEnt4Err(double zent[])
{
	zent[0] = m_z0thpole[0];
	zent[1] = m_z0thpole[1];
}

int UndulatorFieldData::GetPoleNumber(double z, double z0th, double lu)
{
	return (int)floor((z-z0th)/(lu*0.5)+0.5);
}

//----- private functions -----
void UndulatorFieldData::f_AdjustPhase()
{
	int npoles = (int)m_items[UErrorPhaseIdx].size();
	int nfft = 1, n;
	while(nfft < npoles*1.5){
		nfft <<= 1;
	}
	vector<double> zpole(npoles), zphase(npoles);
	double *data = new double[nfft]();

	for(int n = 0; n < npoles; n++){
		zpole[n] = (double)n*m_lu*0.5;
		data[n] = m_items[UErrorPhaseIdx][n];
	}
	for(n = npoles; n < nfft; n++){
		if(n < (npoles+nfft)/2){
			data[n] = 0.5*(m_items[UErrorPhaseIdx][npoles-1]+m_items[UErrorPhaseIdx][npoles-2]);
		}
		else{
			data[n] = 0.5*(m_items[UErrorPhaseIdx][0]+m_items[UErrorPhaseIdx][1]);
		}
	}
	FastFourierTransform fft(1, nfft);
	fft.DoFFTFilter(data, PHASESMOOTHR, false, true);

	for(n = 0; n < npoles; n++){
		zphase[n] = data[n];
	}
	delete[] data;

	Spline zphasespl;
	zphasespl.SetSpline(npoles, &zpole, &zphase, true);

	double pcoef = m_lu*(1.0+m_K2)/(2.0*m_K2)/360.0;
	for(n = 0; n < npoles; n++){
		m_eta[n+m_prange[0]] = zphasespl.GetDerivativeAt(zpole[n]+m_lu*0.25)*pcoef;
	}

#ifdef _DEBUG
	if(!UFdataPhaseTrend.empty()){
		ofstream debug_out(UFdataPhaseTrend);
		if(debug_out){
			vector<double> tmp(2);
			for(int n = 0; n < npoles; n++){
				tmp[0] = zphase[n];
				tmp[1] = m_eta[m_prange[0]+n];
				PrintDebugItems(debug_out, zpole[n], tmp);
			}
		}
	}
#endif
}

void UndulatorFieldData::f_ApplyErrors()
{
	for(int j = 0; j < 2; j++){
		for(int n = 0; n < 2*(m_N+m_endpoles[0]); n++){
			m_i1err[j][n] = m_eta[n]*(m_frac[2]-1.0);
			m_bkick[j][n] = m_bdrv[j][n]*m_frac[j];
		}
	}
	f_AllocateFieldError(m_i1err, m_bkick, m_wsacc);
    for(int j = 0; j < 2; j++){
        m_acc[j].SetSpline(m_ndata, &m_z, &m_wsacc[j]);
    }
    CalculateIntegral(m_isnormalize);
}

void UndulatorFieldData::f_AllocateFieldError(
	vector<vector<double>> &i1err, vector<vector<double>> &berr, vector<vector<double>> &acc)
{
	double xyz[3] = {0, 0, 0};
	double Bxyz[3], bdev[2], ratio[2];
	double zent = -(double)(m_N+m_endpoles[0]+1)*m_lu*0.5;
	int polen[2];
	vector<double> accsq;

	for(int j = 0; j < 2; j++){
		acc[j].resize(m_ndata);
	}
    accsq.resize(m_ndata);
    for(int n = 0; n < m_ndata; n++){
        xyz[2] = m_z[n] = zent+(double)(n-1)*m_dz;
		for(int j = 0; j < 2; j++){
			polen[j] = max(0, min(2*(m_N+2)-1, GetPoleNumber(m_z[n], m_z0thpole[j], m_lu)));
			ratio[j] = 1.0+i1err[j][polen[j]];
			bdev[j] = berr[j][polen[j]];
		}
		get_id_field_general(0.0, m_N+m_endpoles[0], m_lu, m_Kxy, m_deltaxy, 
			ratio, bdev, nullptr, m_isfsymm, m_isendcorr, xyz, Bxyz);
		for (int j = 0; j < 2; j++){
			acc[j][n] = Bxyz[1-j];
		}
		accsq[n] = hypotsq(Bxyz[0], Bxyz[1]);
    }
    m_accsq.SetSpline(m_ndata, &m_z, &accsq);
    m_accsq.Integrate(&accsq);
    m_accsq.SetSpline(m_ndata, &m_z, &accsq);
}

void UndulatorFieldData::f_SetCommonPrm(double lu, vector<double> Kxy[], vector<double> deltaxy[])
{
	m_lu = lu;
	m_B = sqrt(2.0*m_K2)/(COEF_K_VALUE*m_lu);
	double Bmax[2] = {0, 0};
	int kmax[2] = {1, 1};
	for(int j = 0; j < 2; j++){
		m_Kxy[j] = Kxy[j];
		m_deltaxy[j] = deltaxy[j];
		for(int k = 1; k < m_Kxy[j].size(); k++){
			double Br = m_Kxy[j][k]/(COEF_K_VALUE*m_lu/k);
			if(Br > Bmax[j]){
				Bmax[j] = Br;
				kmax[j] = k;
			}
		}
	}

	m_z0thpole[0] = m_z0thpole[1] = -(double)(m_N+m_endpoles[0])*m_lu*0.5+m_lu*0.25;
	for(int j = 0; j < 2; j++){
		m_z0thpole[j] += -(m_lu/kmax[j])*m_deltaxy[j][kmax[j]]/PI2;
	}

	int nhmax = max(kmax[0], kmax[1]);
    m_ndata = (m_N+m_endpoles[0]+1)*(MESHPERPERIOD*nhmax)+1;
    m_dz = m_lu/(double)(MESHPERPERIOD*nhmax);
}
